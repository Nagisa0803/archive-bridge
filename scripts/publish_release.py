"""Publish only completed matrix artifacts with SHA-256 integrity and visible scope."""

import hashlib, json, os, re, urllib.request
from pathlib import Path

folder = Path("release")
repo = os.environ["GITHUB_REPOSITORY"]
tag = os.environ["GITHUB_REF_NAME"]
token = os.environ["GITHUB_TOKEN"]
files = sorted([*folder.glob("*.zip"), *folder.glob("*.tar.gz")])
if len(files) != 6:
    raise SystemExit("Expected exactly six platform archives before publishing.")
for system in ["windows", "linux", "macos"]:
    for arch in ["x64", "arm64"]:
        if len([p for p in files if "-" + system + "-" + arch + "." in p.name]) != 1:
            raise SystemExit("Incomplete platform matrix.")
checksum = folder / "SHA256SUMS"
checksum.write_text(
    "".join(
        hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name + "\n" for p in files
    ),
    encoding="utf-8",
)
files.append(checksum)


def request(url, data=None, content="application/json", method=None):
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "archive-bridge-release",
            "Content-Type": content,
        },
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        return json.load(response)


body = f"""## Archive Bridge {tag}

Local-only account export companion for [Archive Lens](https://archive-lens.chiyoda-site.workers.dev/).

- Native Windows, macOS and Linux packages, each in x64 and ARM64.
- English, Chinese, Japanese and Korean local UI.
- Original Japanese Android APK/XAPK is read locally for package/version and public project configuration.
- Before every sign-in, fetch the current official Google Play Android version and apply it to all request headers. No stale fallback or automatic transfer retry; new protocol majors stop before authentication.
- Preserves User/Get JSON and raw protobuf with explicit coverage; photo originals and complete independent histories are not included.
- Every native binary passes offline protocol/ZIP self-tests; no account data or game authentication is used in CI.
- Initial packages are unsigned/not notarized. `SHA256SUMS` checks download integrity, not publisher identity.

Download the package matching your operating system AND CPU architecture. Extract it, run `archive-bridge`, then follow the local browser wizard. Read the bundled README for setup, platform baselines and troubleshooting.
"""
release = request(
    "https://api.github.com/repos/" + repo + "/releases",
    json.dumps(
        {
            "tag_name": tag,
            "name": "Archive Bridge " + tag,
            "body": body,
            "draft": True,
            "prerelease": "-" in tag,
            "make_latest": "false",
        }
    ).encode(),
)
for file in files:
    request(
        release["upload_url"].split("{")[0] + "?name=" + file.name,
        file.read_bytes(),
        "application/octet-stream",
    )
# Make the complete release public only after every asset is uploaded.
request(
    "https://api.github.com/repos/" + repo + "/releases/" + str(release["id"]),
    json.dumps(
        {
            "draft": False,
            "prerelease": "-" in tag,
            "make_latest": "false" if "-" in tag else "true",
        }
    ).encode(),
    method="PATCH",
)
print("Published " + release["html_url"])
