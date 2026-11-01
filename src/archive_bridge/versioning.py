"""Discover the official Japanese Android release before any account request."""

import datetime, json, re, urllib.request, urllib.parse, urllib.error
from .errors import BridgeError

PACKAGE = "game.qualiarts.idolypride"
SOURCE = "https://play.google.com/store/apps/details?id=" + PACKAGE + "&hl=en&gl=JP"
SCHEMA_BASELINE = "6.1.0"
MAX_METADATA = 6 * 1024 * 1024


def version_tuple(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[1-9]\d{0,3}\.\d{1,4}\.\d{1,4}(?:\.\d{1,4})?", value
    ):
        raise BridgeError(
            "VERSION_METADATA_INVALID",
            "The official client version is missing or malformed. Authentication was not started.",
        )
    parts = tuple(int(x) for x in value.split("."))
    return parts + (0,) * (4 - len(parts))


def parse_play_version(html):
    # Parse structured application details, never guess from release notes or arbitrary version-like text.
    blocks = re.findall(
        r"AF_initDataCallback\(\{key:\s*['\"](ds:\d+)['\"].*?data:\s*(.*?),\s*sideChannel:",
        html,
        re.S,
    )
    versions = []
    for key, body in blocks:
        if key != "ds:5":
            continue
        try:
            data = json.loads(body)
            for index in [1, 2, 140, 0, 0, 0]:
                data = data[index]
            version_tuple(data)
            versions.append(data)
        except (ValueError, TypeError, IndexError, BridgeError):
            continue
    if len(set(versions)) != 1:
        raise BridgeError(
            "VERSION_METADATA_INVALID",
            "Google Play metadata could not identify one current Android version. Update Bridge or retry later; no account request was sent.",
        )
    return versions[0]


class OfficialRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        target = urllib.parse.urlsplit(newurl)
        if (
            target.scheme != "https"
            or target.hostname != "play.google.com"
            or target.username
            or target.password
        ):
            raise BridgeError(
                "VERSION_SOURCE_CHANGED",
                "The official version source redirected outside Google Play. Authentication was not started.",
            )
        return super().redirect_request(request, fp, code, message, headers, newurl)


def discover_version(apk_version, proxy=None, cancel=None, fetch=None):
    apk = version_tuple(apk_version)
    if cancel and cancel.is_set():
        raise BridgeError("CANCELLED", "Collection cancelled before version discovery.")
    if fetch is None:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({"https": proxy} if proxy else {}),
            OfficialRedirects(),
        )
        request = urllib.request.Request(
            SOURCE,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; ArchiveBridge public-version-check)",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
            },
        )
        try:
            with opener.open(request, timeout=25) as response:
                raw = response.read(MAX_METADATA + 1)
                if len(raw) > MAX_METADATA:
                    raise BridgeError(
                        "VERSION_METADATA_INVALID",
                        "Official version metadata exceeded its size limit.",
                    )
                html = raw.decode("utf-8")
        except (urllib.error.URLError, TimeoutError, UnicodeError):
            raise BridgeError(
                "VERSION_CHECK_FAILED",
                "Cannot read current official Google Play version. Check the network/proxy and retry; no fallback to an old version or account request occurred.",
            ) from None
    else:
        html = fetch()
    latest = parse_play_version(html)
    current = version_tuple(latest)
    if current < apk:
        raise BridgeError(
            "VERSION_SOURCE_STALE",
            "Google Play reports an older release than the supplied APK. No version downgrade or authentication was attempted; retry after the regional store updates.",
        )
    if current[0] != version_tuple(SCHEMA_BASELINE)[0]:
        raise BridgeError(
            "PROTOCOL_UPDATE_REQUIRED",
            "Latest Android release "
            + latest
            + " changes the supported protocol major version. Update Bridge before signing in.",
        )
    if cancel and cancel.is_set():
        raise BridgeError("CANCELLED", "Collection cancelled before authentication.")
    return {
        "appVersion": latest,
        "apkVersion": apk_version,
        "schemaBaseline": SCHEMA_BASELINE,
        "source": SOURCE,
        "checkedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "policy": "fresh-per-collection; same-major compatibility; no stale fallback",
    }
