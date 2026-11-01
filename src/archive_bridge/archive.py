"""Atomic per-collection ZIPs with original protobuf and portable Archive Lens metadata."""

import datetime, hashlib, json, os, re, uuid, zipfile
from pathlib import Path
from .errors import BridgeError


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def fingerprint(user):
    public = user.get("userPublic", {})
    value = public.get("serverUserId") or public.get("publicUserId")
    if not value:
        raise BridgeError(
            "INVALID_ACCOUNT", "The account has no authenticated identifier."
        )
    return hashlib.sha256(str(value).encode()).hexdigest()


def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")


def write_archive(
    folder,
    user,
    raw,
    master,
    master_raw,
    calls,
    coverage,
    extra=None,
    supplemental=None,
    image_links=None,
    replace_filename=None,
):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    snapshot = {
        "format": "idoly-account-snapshot/v1",
        "createdAt": now(),
        "scope": "Account",
        "source": {
            "kind": "official-readonly-rpc",
            "collector": "archive-bridge",
            "methods": [c["method"] for c in calls],
        },
        "accountFingerprint": fingerprint(user),
        "userData": user,
        "coverage": coverage,
        "supplemental": supplemental or [],
    }
    if image_links is not None:
        snapshot["cardImageLinks"] = image_links["cardImageLinks"]
        snapshot["photoLinks"] = image_links["photoLinks"]
    files = {
        "account.json": json_bytes(snapshot),
        "raw/user.pb": raw,
        "decoded/master.json": json_bytes(master),
        "raw/master.pb": master_raw,
        "collection.json": json_bytes({"requests": calls, "credentialsWritten": False}),
    }
    files.update(extra or {})
    manifest = {
        "format": "idoly-account-backup/v1",
        "createdAt": now(),
        "accountFingerprint": snapshot["accountFingerprint"],
        "files": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()},
        "credentialsIncluded": None,
        "credentialAssessment": "authentication-artifacts-excluded; raw-account-fields-not-fully-assessed",
        "authenticationArtifactsWritten": False,
        "containsPersonalData": True,
        "safeToShare": False,
        "coverage": coverage,
    }
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = replace_filename or f"archive-{stamp}-{uuid.uuid4().hex[:8]}.zip"
    if not re.fullmatch(r"archive-\d{8}T\d{6}Z-[a-f0-9]{8}\.zip", name):
        raise BridgeError("ARCHIVE_FAILED", "Invalid collection archive name.")
    target = folder / name
    if replace_filename is not None:
        with zipfile.ZipFile(target) as existing:
            previous = json.loads(existing.read("manifest.json"))
        if previous.get("accountFingerprint") != snapshot["accountFingerprint"]:
            raise BridgeError("ARCHIVE_FAILED", "Collection archive identity changed.")
    temporary = folder / (name + ".partial")
    try:
        with open(temporary, "xb") as stream:
            if os.name != "nt":
                os.chmod(temporary, 0o600)
            with zipfile.ZipFile(
                stream, "w", zipfile.ZIP_DEFLATED, compresslevel=6
            ) as z:
                for path, body in files.items():
                    z.writestr(path, body)
                z.writestr("manifest.json", json_bytes(manifest))
            stream.flush()
            os.fsync(stream.fileno())
        with zipfile.ZipFile(temporary) as z:
            if z.testzip():
                raise BridgeError(
                    "ARCHIVE_FAILED", "The completed archive could not be verified."
                )
            for path, digest in manifest["files"].items():
                if hashlib.sha256(z.read(path)).hexdigest() != digest:
                    raise BridgeError(
                        "ARCHIVE_FAILED", "Archive round-trip verification failed."
                    )
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return {
        "filename": name,
        "bytes": target.stat().st_size,
        "counts": {k: len(v) for k, v in user.items() if isinstance(v, list)},
        "coverage": coverage,
    }
