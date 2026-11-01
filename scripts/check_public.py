"""Public tree gate: no account archives, runtime state, APKs, tokens or private media."""

import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {
    ".git",
    ".ruff_cache",
    ".venv",
    "build",
    "dist",
    "release",
    "__pycache__",
    ".ci-self-test",
    ".ci-native-test",
}
patterns = [
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(rb"AIza[0-9A-Za-z_-]{35}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(
        rb"(?:CLIENT_RANDOM|CLIENT_HANDSHAKE_TRAFFIC_SECRET|SERVER_TRAFFIC_SECRET_0) [0-9a-fA-F]{64} [0-9a-fA-F]{32,}"
    ),
    re.compile(
        rb"(?i)[A-Z]:[\\/]Users[\\/](?!Public[\\/]|Default[\\/])[^\\/\s\"]+[\\/]"
    ),
    re.compile(rb"(?i)[A-Z]:[\\/](?:VibCoding|IDOLY_PRIDE_backups)[\\/]"),
    re.compile(rb"https://[a-z0-9]+\.cloudfront\.net/(?:Photo|photo)/"),
]
fail = []
count = 0
for path in ROOT.rglob("*"):
    rel = path.relative_to(ROOT)
    if not path.is_file() or any(
        part in SKIP or part.endswith(".egg-info") for part in rel.parts
    ):
        continue
    count += 1
    if (
        path.suffix.lower()
        in {
            ".apk",
            ".xapk",
            ".zip",
            ".tar",
            ".sqlite",
            ".db",
            ".pcap",
            ".pem",
            ".key",
            ".log",
        }
        or path.name in {"account.json", "photo-links.json", "test_identity.json"}
        or path.name.startswith(".env")
    ):
        fail.append(str(rel) + ": runtime/secret file")
    if (
        path.suffix == ".pb"
        and rel.as_posix() != "src/archive_bridge/resources/schema.pb"
    ):
        fail.append(str(rel) + ": unknown protobuf blob")
    body = path.read_bytes()
    if any(pattern.search(body) for pattern in patterns):
        fail.append(str(rel) + ": credential/private-media pattern")
if fail:
    raise SystemExit("Public source rejected:\n" + "\n".join(fail))
print(
    f"Public source passed: {count} files; no account archives, APKs, authentication literals or TLS keylogs."
)
