"""Synthetic offline checks also run against every compiled native executable."""

import tempfile, zipfile, json
from pathlib import Path
from . import codec
from .archive import write_archive


def run(data):
    payload = b"archive-bridge-offline-self-test"
    wire = codec.pack(payload)
    decoded = codec.frames(b"\0" + len(wire).to_bytes(4, "big") + wire, "identity")[0][
        1
    ]
    if decoded != payload:
        raise RuntimeError("Codec round-trip failed")
    user = {
        "userPublic": {"serverUserId": "DEMO0001"},
        "user": {"name": "Synthetic demo"},
        "cards": [{"cardId": "card-demo-001"}],
    }
    with tempfile.TemporaryDirectory(dir=data, prefix="offline-selftest-") as directory:
        archive = write_archive(
            directory,
            user,
            b"synthetic-protobuf",
            {},
            b"",
            [],
            {"allAccountDomainsComplete": False},
        )
        with zipfile.ZipFile(Path(directory) / archive["filename"]) as z:
            if (
                json.loads(z.read("account.json"))["userData"] != user
                or z.read("raw/user.pb") != b"synthetic-protobuf"
            ):
                raise RuntimeError("Archive round-trip failed")
    return {
        "ok": True,
        "networkRequests": 0,
        "codecRoundTrip": True,
        "archiveRoundTrip": True,
        "profileVersion": "Japanese Android / schema baseline 6.1.0 / automatic official request version",
    }
