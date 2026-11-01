"""Single-user loopback UI with origin, host and per-launch token checks."""

import json, mimetypes, re, secrets, threading, zipfile
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit
from . import __version__
from .errors import BridgeError
from .profile import read_profile, MAX_APK
from .transport import Transport
from .collector import collect

WEB = Path(__file__).parent / "web"
CSP = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' blob: data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"


class Application:
    def __init__(self, data, transport_factory=Transport):
        self.data = Path(data).resolve()
        self.output = self.data / "exports"
        self.output.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.factory = transport_factory
        self.token = secrets.token_urlsafe(32)
        self.project = None
        self.apk_version = None
        self.lock = threading.Lock()
        self.cancel = threading.Event()
        self.state = {"status": "idle", "stage": "idle", "percent": 0}
        self.thread = None

    def progress(self, **values):
        with self.lock:
            self.state.update(values)

    def list_backups(self):
        result = []
        for path in sorted(self.output.glob("archive-*.zip"), reverse=True)[:100]:
            try:
                with zipfile.ZipFile(path) as z:
                    if z.getinfo("manifest.json").file_size > 1024 * 1024:
                        continue
                    manifest = json.loads(z.read("manifest.json"))
                result.append(
                    {
                        "filename": path.name,
                        "bytes": path.stat().st_size,
                        "createdAt": manifest.get("createdAt"),
                        "coverage": manifest.get("coverage", {}),
                    }
                )
            except (OSError, ValueError, zipfile.BadZipFile, KeyError):
                continue
        return result

    def snapshot(self):
        with self.lock:
            state = dict(self.state)
        return {
            "version": __version__,
            "profileReady": bool(self.project),
            "compatibility": "Japanese Android · automatic official version",
            "apkVersion": self.apk_version,
            "outputDirectory": str(self.output),
            "job": state,
            "backups": self.list_backups(),
        }

    def start(self, values):
        with self.lock:
            if self.state["status"] in ("running", "configuring"):
                raise BridgeError(
                    "BUSY", "One collection is already running. Wait or cancel it."
                )
            if not self.project:
                raise BridgeError(
                    "PROFILE_REQUIRED",
                    "Choose the supported original APK before collecting.",
                )
            if values.get("confirm") is not True:
                raise BridgeError(
                    "CONSENT_REQUIRED",
                    "Confirm that this is your own account and you want to authenticate and read its data.",
                )
            if not isinstance(values.get("transferId"), str) or not isinstance(
                values.get("password"), str
            ):
                raise BridgeError(
                    "INVALID_CREDENTIALS", "Transfer ID and password are required."
                )
            self.cancel.clear()
            self.state = {"status": "running", "stage": "verify", "percent": 0}
            self.thread = threading.Thread(target=self.run, args=(values,), daemon=True)
            self.thread.start()

    def run(self, values):
        password = values.pop("password")
        try:
            transport = self.factory(
                self.project, values.get("proxy") or None, self.cancel
            )
            transport.apk_version = self.apk_version
            collect(
                transport,
                values.get("transferId", ""),
                password,
                self.output,
                self.progress,
                include_image_links=values.get("includeImageLinks") is True,
            )
            self.progress(status="complete")
        except BridgeError as e:
            self.progress(
                status="cancelled" if e.code == "CANCELLED" else "failed",
                error={"code": e.code, "message": e.message},
            )
        except Exception:
            self.progress(
                status="failed",
                error={
                    "code": "OPERATION_FAILED",
                    "message": "A network or filesystem operation failed. Check connectivity, proxy configuration and write access. Transfer execution is never automatically retried.",
                },
            )
        finally:
            password = None
            values.clear()


def create_server(app, port=0):
    class Handler(BaseHTTPRequestHandler):
        server_version = "ArchiveBridge"
        sys_version = ""
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def send(
            self, status, body, kind="application/json; charset=utf-8", headers=None
        ):
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)

        def result(self, value, status=200):
            self.send(status, json.dumps(value, ensure_ascii=False).encode("utf-8"))

        def authorized(self):
            expected = "127.0.0.1:" + str(self.server.server_port)
            if (
                self.headers.get("Host") != expected
                or self.headers.get("Origin") not in (None, "http://" + expected)
                or self.headers.get("Sec-Fetch-Site") == "cross-site"
            ):
                return False
            return secrets.compare_digest(
                self.headers.get("X-Bridge-Token", ""), app.token
            )

        def do_GET(self):
            path = urlsplit(self.path).path
            if self.headers.get("Host") != "127.0.0.1:" + str(self.server.server_port):
                self.result({"error": "Invalid host"}, 403)
                return
            if path.startswith("/api/"):
                if not self.authorized():
                    self.result(
                        {
                            "error": "Open the local URL printed by this running application."
                        },
                        403,
                    )
                    return
                if path == "/api/state":
                    self.result(app.snapshot())
                    return
                if re.fullmatch(r"/api/export/archive-[A-Za-z0-9-]+\.zip", path):
                    file = app.output / Path(path).name
                    if file.is_file():
                        self.send(
                            200,
                            file.read_bytes(),
                            "application/zip",
                            {
                                "Content-Disposition": 'attachment; filename="'
                                + file.name
                                + '"'
                            },
                        )
                        return
                self.result({"error": "Not found"}, 404)
                return
            file = WEB / (
                {
                    "/": "index.html",
                    "/app.js": "app.js",
                    "/style.css": "style.css",
                    "/icon.svg": "icon.svg",
                    "/icon.png": "icon.png",
                    "/icon.ico": "icon.ico",
                    "/favicon.ico": "icon.ico",
                }.get(path, "__missing__")
            )
            if file.is_file():
                self.send(
                    200,
                    file.read_bytes(),
                    {
                        ".html": "text/html; charset=utf-8",
                        ".js": "text/javascript; charset=utf-8",
                        ".css": "text/css; charset=utf-8",
                        ".svg": "image/svg+xml",
                        ".png": "image/png",
                        ".ico": "image/x-icon",
                    }[file.suffix],
                )
                return
            self.result({"error": "Not found"}, 404)

        def do_POST(self):
            if not self.authorized():
                self.close_connection = True
                self.result({"error": "Invalid local request"}, 403)
                return
            path = urlsplit(self.path).path
            try:
                length = int(self.headers.get("Content-Length", "-1"))
                if length < 0 or length > (
                    MAX_APK if path == "/api/profile" else 16384
                ):
                    self.close_connection = True
                    raise BridgeError(
                        "REQUEST_TOO_LARGE", "The input exceeds this release limit."
                    )
                if path == "/api/profile":
                    with app.lock:
                        if app.state["status"] in ("running", "configuring"):
                            raise BridgeError(
                                "BUSY",
                                "Wait for the current collection before changing APK configuration.",
                            )
                        app.state = {
                            "status": "configuring",
                            "stage": "configure",
                            "percent": 0,
                        }
                    file = app.data / ("upload-" + secrets.token_hex(12) + ".tmp")
                    try:
                        with file.open("xb") as out:
                            remaining = length
                            while remaining:
                                block = self.rfile.read(min(1024 * 1024, remaining))
                                if not block:
                                    raise BridgeError(
                                        "UPLOAD_INCOMPLETE",
                                        "The APK upload was interrupted.",
                                    )
                                out.write(block)
                                remaining -= len(block)
                        profile = read_profile(file)
                        with app.lock:
                            app.project = profile["project"]
                            app.apk_version = profile["apkVersion"]
                            app.state = {
                                "status": "idle",
                                "stage": "idle",
                                "percent": 0,
                            }
                    finally:
                        file.unlink(missing_ok=True)
                        with app.lock:
                            if app.state["status"] == "configuring":
                                app.state = {
                                    "status": "idle",
                                    "stage": "idle",
                                    "percent": 0,
                                }
                    self.result({"ready": True})
                    return
                body = self.rfile.read(length)
                if len(body) != length:
                    raise BridgeError(
                        "UPLOAD_INCOMPLETE", "The request was interrupted."
                    )
                values = json.loads(body) if body else {}
                if not isinstance(values, dict):
                    raise BridgeError("INVALID_INPUT", "Expected a JSON object.")
                if path == "/api/collect":
                    app.start(values)
                    self.result({"started": True}, 202)
                    return
                if path == "/api/cancel":
                    app.cancel.set()
                    self.result({"requested": True})
                    return
                self.result({"error": "Not found"}, 404)
            except BridgeError as e:
                self.result({"error": {"code": e.code, "message": e.message}}, 400)
            except (ValueError, UnicodeError):
                self.result(
                    {
                        "error": {
                            "code": "INVALID_INPUT",
                            "message": "The request format is invalid.",
                        }
                    },
                    400,
                )
            except Exception:
                self.result(
                    {
                        "error": {
                            "code": "LOCAL_IO_FAILED",
                            "message": "Local processing failed. Check that the output directory is writable and the selected file is valid.",
                        }
                    },
                    500,
                )

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    return server
