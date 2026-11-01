"""Explicitly selected links only: bundled generic card catalog and owned-photo RPC."""

import csv
import io
import json
from pathlib import Path
from urllib.parse import urlsplit
from .archive import fingerprint, json_bytes, now
from .errors import BridgeError

VIEWER = "https://archive-lens.chiyoda-site.workers.dev/"


def validate_url(value):
    if not isinstance(value, str) or len(value) > 8192:
        raise BridgeError("PHOTO_URL_INVALID", "Unsupported photo URL.")
    u = urlsplit(value)
    allowed = u.hostname in {
        "d2ilil7yh5oi1v.cloudfront.net",
        "storage.googleapis.com",
        "firebasestorage.googleapis.com",
        "storage.cloud.google.com",
    } or (u.hostname or "").endswith(".storage.googleapis.com")
    if (
        u.scheme != "https"
        or u.username
        or u.password
        or u.port not in (None, 443)
        or not allowed
    ):
        raise BridgeError("PHOTO_URL_INVALID", "Unsupported photo URL.")
    return value


def collect_image_links(user, rpc, token, version, extra, failures, check, progress):
    catalog = json.loads(
        (Path(__file__).parent / "resources/card-previews.json").read_text(
            encoding="utf-8"
        )
    )["cards"]
    cards = {}
    for card in user.get("cards", []):
        cid = card.get("cardId")
        image = catalog.get(cid, {})
        if image.get("file"):
            cards[cid] = {
                "cardId": cid,
                "name": image.get("name", ""),
                "previewUrl": VIEWER + image["file"],
                "kind": "generic-card-preview",
            }
    assets = list(
        dict.fromkeys(
            p.get("assetId")
            for p in user.get("photos", [])
            if isinstance(p.get("assetId"), str) and p["assetId"]
        )
    )
    links = {}
    completed = 0
    if len(assets) > 20000:
        failures.append({"domain": "photo-links", "errorCode": "PHOTO_LIMIT"})
    else:
        for start in range(0, len(assets), 50):
            check()
            batch = assets[start : start + 50]
            progress(
                stage="photo_links", percent=82 + int(10 * start / max(1, len(assets)))
            )
            try:
                response, raw = rpc(
                    "/api.Photo/GetImageURL",
                    {"type": 3, "assetIds": batch},
                    token=token,
                    version=version,
                )
                rows = response.get("urlList", [])
                if not isinstance(rows, list) or any(
                    row.get("assetId") not in batch for row in rows
                ):
                    raise BridgeError(
                        "PHOTO_SCOPE_MISMATCH",
                        "Photo response contains an unrequested asset.",
                    )
                validated = {}
                for row in rows:
                    asset = row["assetId"]
                    out = {"assetId": asset}
                    for key in ("origUrl", "tmbUrl"):
                        if row.get(key):
                            out[key] = validate_url(row[key])
                    if out.get("origUrl") or out.get("tmbUrl"):
                        validated[asset] = out
                links.update(validated)
                extra[f"raw/rpc/photo_get_image_url_{start // 50:04}.pb"] = raw
                extra[f"raw/rpc/photo_get_image_url_{start // 50:04}.json"] = (
                    json_bytes(response)
                )
                completed += len(batch)
            except Exception as e:
                failures.append(
                    {
                        "domain": "photo-links",
                        "errorCode": e.code
                        if isinstance(e, BridgeError)
                        else "READ_FAILED",
                    }
                )
                break
    bundle = {
        "format": "idoly-image-links/v1",
        "createdAt": now(),
        "accountFingerprint": fingerprint(user),
        "cardImageLinks": cards,
        "photoLinks": links,
        "urlsMayExpire": True,
        "imagesDownloaded": False,
    }
    extra["image-links.json"] = json_bytes(bundle)
    photo_bundle = {
        "format": "idoly-photo-links/v1",
        "createdAt": bundle["createdAt"],
        "accountFingerprint": bundle["accountFingerprint"],
        "photoLinks": links,
        "source": "Official Photo/GetImageURL; only owned records",
    }
    extra["photo-links.json"] = json_bytes(photo_bundle)
    records = [("card-preview", cid, x["previewUrl"]) for cid, x in cards.items()]
    records += [
        (kind, asset, row[key])
        for asset, row in links.items()
        for key, kind in [("origUrl", "photo-original"), ("tmbUrl", "photo-thumbnail")]
        if row.get(key)
    ]
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["kind", "id", "url"])
    for row in records:
        writer.writerow(
            [
                "'" + value
                if value.startswith(("=", "+", "-", "@", "\t", "\r"))
                else value
                for value in row
            ]
        )
    extra["image-links.csv"] = stream.getvalue().encode("utf-8-sig")
    extra["image-links.txt"] = (
        "\n".join(dict.fromkeys(row[2] for row in records)) + "\n"
    ).encode("utf-8")
    coverage = {
        "requested": True,
        "cardRecords": len(user.get("cards", [])),
        "cardPreviewLinks": len(cards),
        "photoAssets": len(assets),
        "photoAssetsQueried": completed,
        "photoAssetsWithURLs": len(links),
        "photoAssetsWithoutURLs": len(assets) - len(links),
        "photoURLReadsComplete": completed == len(assets),
        "imagesDownloaded": False,
        "allURLsDownloadTested": False,
    }
    return bundle, coverage
