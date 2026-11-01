"""Finite HTTP/2 transport, verified TLS, optional explicit HTTP CONNECT proxy."""

import json, socket, ssl, time, urllib.parse, urllib.request, urllib.error
from h2.connection import H2Connection
from h2.config import H2Configuration
from h2.events import (
    ResponseReceived,
    TrailersReceived,
    DataReceived,
    StreamEnded,
    StreamReset,
)
from . import codec
from .errors import BridgeError
from .versioning import discover_version

HOST = "api.game-idolypride.jp"
ALLOWED = frozenset(
    [
        "/api.Migration/MigratePassword",
        "/api.Migration/Execute",
        "/api.Auth/Login",
        "/api.Master/Get",
        "/api.User/Get",
        "/api.Migration/List",
    ]
)


class Transport:
    def __init__(self, project, proxy=None, cancel=None):
        self.project = project
        self.proxy = proxy
        self.cancel = cancel
        self.apk_version = None
        self.app_version = None
        self.version_info = None
        if proxy:
            u = urllib.parse.urlsplit(proxy)
            if (
                u.scheme != "http"
                or not u.hostname
                or u.username
                or u.password
                or u.path not in ("", "/")
                or u.query
                or u.fragment
            ):
                raise BridgeError(
                    "INVALID_PROXY",
                    "Use an HTTP proxy URL without credentials, for example http://127.0.0.1:7892.",
                )

    def prepare_version(self):
        self.version_info = discover_version(self.apk_version, self.proxy, self.cancel)
        self.app_version = self.version_info["appVersion"]
        return self.version_info

    def check(self):
        if self.cancel and self.cancel.is_set():
            raise BridgeError(
                "CANCELLED",
                "Collection cancelled. Previously completed backups remain available.",
            )

    def connect(self):
        self.check()
        u = urllib.parse.urlsplit(self.proxy) if self.proxy else None
        raw = socket.create_connection(
            (u.hostname, u.port or 80) if u else (HOST, 443), timeout=20
        )
        try:
            if u:
                raw.sendall(
                    f"CONNECT {HOST}:443 HTTP/1.1\r\nHost: {HOST}:443\r\n\r\n".encode()
                )
                headers = bytearray()
                while not headers.endswith(b"\r\n\r\n"):
                    b = raw.recv(1)
                    if not b or len(headers) > 8192:
                        raise BridgeError(
                            "PROXY_FAILED",
                            "The proxy did not establish a secure tunnel.",
                        )
                    headers.extend(b)
                if b" 200 " not in headers.split(b"\r\n")[0]:
                    raise BridgeError("PROXY_FAILED", "The proxy rejected the tunnel.")
            context = ssl.create_default_context()
            context.set_alpn_protocols(["h2"])
            tls = context.wrap_socket(raw, server_hostname=HOST)
            tls.settimeout(25)
            if tls.selected_alpn_protocol() != "h2":
                raise BridgeError(
                    "NETWORK_FAILED", "The server did not negotiate HTTP/2."
                )
            return tls
        except BaseException:
            raw.close()
            raise

    def rpc(self, path, values=None, token=None, master_version=None):
        if path not in ALLOWED:
            raise BridgeError(
                "METHOD_BLOCKED", "This operation is not part of the account exporter."
            )
        self.check()
        if not self.app_version:
            raise BridgeError(
                "VERSION_NOT_READY",
                "Read the latest official client version before any account request.",
            )
        desc = codec.descriptor(path)
        body = codec.pack(codec.encode(desc.input_type, values or {}))
        frame = b"\0" + len(body).to_bytes(4, "big") + body
        start = time.monotonic()
        with self.connect() as tls:
            h = H2Connection(H2Configuration(client_side=True, header_encoding="utf-8"))
            h.initiate_connection()
            tls.sendall(h.data_to_send())
            sid = h.get_next_available_stream_id()
            headers = [
                (":method", "POST"),
                (":scheme", "https"),
                (":authority", HOST),
                (":path", path),
                ("content-type", "application/grpc"),
                ("te", "trailers"),
                ("x-app-version", self.app_version),
                ("x-platform", "Android"),
            ]
            if token:
                headers.append(("x-auth-token", token))
            if master_version:
                headers.append(("x-master-version", master_version))
            h.send_headers(sid, headers)
            h.send_data(sid, frame, end_stream=True)
            tls.sendall(h.data_to_send())
            chunks = []
            size = 0
            returned = {}
            done = False
            while not done:
                self.check()
                if time.monotonic() - start > 75:
                    raise BridgeError(
                        "NETWORK_TIMEOUT",
                        "The request timed out. Transfer execution is never retried automatically.",
                    )
                packet = tls.recv(65536)
                if not packet:
                    raise BridgeError(
                        "NETWORK_FAILED", "The server closed an incomplete response."
                    )
                for ev in h.receive_data(packet):
                    if isinstance(ev, (ResponseReceived, TrailersReceived)):
                        returned.update(dict(ev.headers))
                    elif isinstance(ev, DataReceived):
                        size += len(ev.data)
                        if size > 128 * 1024 * 1024:
                            raise BridgeError(
                                "RESPONSE_TOO_LARGE",
                                "The response exceeded this release limit.",
                            )
                        chunks.append(ev.data)
                        h.acknowledge_received_data(ev.flow_controlled_length, sid)
                    elif isinstance(ev, StreamReset):
                        raise BridgeError(
                            "NETWORK_FAILED", "The HTTP/2 stream was reset."
                        )
                    elif isinstance(ev, StreamEnded):
                        done = True
                outgoing = h.data_to_send()
                if outgoing:
                    tls.sendall(outgoing)
            if returned.get(":status") != "200" or returned.get("grpc-status") != "0":
                raise BridgeError(
                    "RPC_FAILED",
                    f"Server rejected {path} (HTTP {returned.get(':status', '?')}, gRPC {returned.get('grpc-status', '?')}). No transfer retry was performed.",
                )
            try:
                frames = codec.frames(
                    b"".join(chunks), returned.get("grpc-encoding", "identity")
                )
                if len(frames) != 1:
                    raise ValueError("Frame count")
                plain = frames[0][1]
                response = codec.decode(desc.output_type, plain)
            except Exception:
                raise BridgeError(
                    "PROTOCOL_CHANGED",
                    "The response differs from the supported protocol. Check for a compatible release.",
                ) from None
            return (
                response,
                plain,
                {
                    "method": path,
                    "appVersion": self.app_version,
                    "status": "0",
                    "responseBytes": len(plain),
                    "milliseconds": round((time.monotonic() - start) * 1000),
                },
            )

    def firebase(self, custom_token):
        self.check()
        url = (
            "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key="
            + self.project
        )
        request = urllib.request.Request(
            url,
            data=json.dumps(
                {"token": custom_token, "returnSecureToken": True}
            ).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({"https": self.proxy} if self.proxy else {})
        )
        try:
            with opener.open(request, timeout=25) as r:
                data = r.read(1024 * 1024)
                if len(data) >= 1024 * 1024:
                    raise BridgeError(
                        "AUTH_FAILED", "Authentication response exceeded its limit."
                    )
                return json.loads(data)["idToken"]
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            KeyError,
            ValueError,
            TimeoutError,
        ):
            raise BridgeError(
                "AUTH_FAILED",
                "Official authentication failed. Check transfer settings and network. Credentials were not saved.",
            ) from None
