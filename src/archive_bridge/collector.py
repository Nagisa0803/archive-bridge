"""One explicit transfer and bounded necessary reads. No discovery or gameplay calls."""

import re
from .archive import write_archive, json_bytes, fingerprint
from .errors import BridgeError


def collect(transport, uid, password, output, progress=lambda **kw: None):
    uid = uid.strip()
    if not re.fullmatch(r"[A-Za-z0-9]{4,64}", uid) or not re.fullmatch(
        r"[A-Za-z0-9]{8,16}", password
    ):
        raise BridgeError(
            "INVALID_CREDENTIALS",
            "Use the game transfer ID and its 8–16 letter/digit password.",
        )
    progress(stage="version", percent=3)
    version_info = transport.prepare_version()
    progress(stage="version", percent=5, versionInfo=version_info)
    calls = []

    def rpc(path, values=None, token=None, version=None):
        response, raw, meta = transport.rpc(path, values, token, version)
        calls.append(meta)
        return response, raw

    progress(stage="verify", percent=10)
    result, _ = rpc(
        "/api.Migration/MigratePassword", {"userId": uid, "password": password}
    )
    password = None
    if not result.get("onetimeToken") or str(result.get("linkedUserId", "")) != uid:
        raise BridgeError(
            "TRANSFER_REJECTED",
            "No usable one-time token or matching target was returned. Transfer was not executed.",
        )
    progress(stage="transfer", percent=20)
    execute, _ = rpc("/api.Migration/Execute", {"onetimeToken": result["onetimeToken"]})
    result.clear()
    if not execute.get("token"):
        raise BridgeError(
            "TRANSFER_REJECTED",
            "Official transfer did not return an authentication token.",
        )
    identity = transport.firebase(execute["token"])
    execute.clear()
    progress(stage="login", percent=30)
    login, _ = rpc("/api.Auth/Login", {"firebaseIDToken": identity})
    identity = None
    public = login.get("userPublic", {})
    if uid not in {
        str(public.get("serverUserId", "")),
        str(public.get("publicUserId", "")),
    }:
        raise BridgeError(
            "IDENTITY_MISMATCH",
            "Authenticated account differs from the requested transfer ID. Account data was not read.",
        )
    token = login.get("gameAuthToken")
    if not token:
        raise BridgeError(
            "AUTH_FAILED", "The login response has no game session token."
        )
    expected = fingerprint({"userPublic": public})
    login.clear()
    progress(stage="master", percent=40)
    master, master_raw = rpc("/api.Master/Get", token=token)
    version = master.get("masterTag", {}).get("version")
    if not version:
        raise BridgeError(
            "PROTOCOL_CHANGED", "Master data has no version. Account reading stopped."
        )
    progress(stage="account", percent=55)
    user, raw = rpc("/api.User/Get", token=token, version=version)
    if fingerprint(user) != expected:
        raise BridgeError(
            "IDENTITY_MISMATCH",
            "Returned account does not match the authenticated account.",
        )
    coverage = {
        "clientVersionInfo": version_info,
        "userGet": "complete_response_preserved",
        "allAccountDomainsComplete": False,
        "photoOriginalsDownloaded": False,
        "completeMessageHistory": False,
        "standaloneDomainsPending": True,
        "note": "Full User/Get and original protobuf preserved. Independent history, photo media, and global completeness remain unproven.",
    }
    progress(stage="save", percent=70)
    base = write_archive(output, user, raw, master, master_raw, calls, dict(coverage))
    progress(stage="supplemental", percent=80, backup=base)
    extra = {}
    supplemental = []
    failures = []
    try:
        response, body = rpc("/api.Migration/List", token=token, version=version)
        extra["raw/rpc/migration_list.pb"] = body
        extra["raw/rpc/migration_list.json"] = json_bytes(response)
        supplemental.append(
            {
                "method": "/api.Migration/List",
                "record": "migration_list",
                "response": response,
                "protobufFile": "raw/rpc/migration_list.pb",
            }
        )
    except Exception as e:
        failures.append(
            {
                "domain": "migration-list",
                "errorCode": e.code if isinstance(e, BridgeError) else "READ_FAILED",
            }
        )
    coverage["supplementalFailures"] = failures
    transport.check()
    progress(stage="save", percent=95, backup=base)
    result = write_archive(
        output, user, raw, master, master_raw, calls, coverage, extra, supplemental
    )
    progress(stage="done", percent=100, backup=result)
    token = None
    return result
