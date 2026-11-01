import gzip, hashlib, http.client, json, os, tempfile, threading, unittest, zipfile
from pathlib import Path
from archive_bridge import codec
from archive_bridge.archive import write_archive
from archive_bridge.collector import collect
from archive_bridge.errors import BridgeError
from archive_bridge.profile import extract_project
from archive_bridge.server import Application, create_server
from archive_bridge.transport import Transport

UID = "DEMO0001"
PASSWORD = "DemoPassword01"


class FakeTransport:
    def __init__(self, fail=None, identity=UID, linked=UID):
        self.fail = fail
        self.identity = identity
        self.linked = linked
        self.calls = []

    def prepare_version(self):
        return {
            "appVersion": "6.1.0",
            "apkVersion": "6.1.0",
            "source": "synthetic-official-metadata",
        }

    def check(self):
        pass

    def firebase(self, token):
        return "synthetic-firebase-session"

    def rpc(self, path, values=None, token=None, master_version=None):
        self.calls.append(path)
        if self.fail == path:
            raise BridgeError("SYNTHETIC_FAILURE", "Synthetic failure")
        data = {
            "/api.Migration/MigratePassword": {
                "success": False,
                "onetimeToken": "synthetic-one-time",
                "linkedUserId": self.linked,
            },
            "/api.Migration/Execute": {"token": "synthetic-custom-session"},
            "/api.Auth/Login": {
                "gameAuthToken": "synthetic-game-session",
                "userPublic": {"serverUserId": self.identity},
            },
            "/api.Master/Get": {"masterTag": {"version": "synthetic-master"}},
            "/api.User/Get": {
                "userPublic": {"serverUserId": self.identity},
                "user": {"name": "Synthetic demo"},
                "cards": [{"cardId": "card-demo-001"}],
                "characters": [],
                "decks": [],
            },
            "/api.Migration/List": {},
        }[path]
        raw = codec.encode(codec.descriptor(path).output_type, data)
        return (
            codec.decode(codec.descriptor(path).output_type, raw),
            raw,
            {"method": path, "status": "0", "responseBytes": len(raw)},
        )


class ProductTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_supported_schema_methods(self):
        for path in [
            "/api.Migration/MigratePassword",
            "/api.Migration/Execute",
            "/api.Auth/Login",
            "/api.Master/Get",
            "/api.User/Get",
            "/api.Migration/List",
        ]:
            self.assertIsNotNone(codec.descriptor(path))

    def test_codec_frames_roundtrip_and_compression(self):
        data = b"public synthetic payload"
        wrapped = codec.pack(data)
        frame = b"\0" + len(wrapped).to_bytes(4, "big") + wrapped
        self.assertEqual(codec.frames(frame, "identity")[0][1], data)
        zipped = gzip.compress(wrapped)
        self.assertEqual(
            codec.frames(b"\1" + len(zipped).to_bytes(4, "big") + zipped, "gzip")[0][1],
            data,
        )

    def test_truncated_and_untrusted_frames_rejected(self):
        for data in [b"\0", b"\2\0\0\0\0", b"\0\0\0\0\4tiny"]:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    codec.frames(data, "identity")

    def test_gameplay_rejected_before_network(self):
        with self.assertRaises(BridgeError) as error:
            Transport("synthetic").rpc("/api.Gacha/Draw")
        self.assertEqual(error.exception.code, "METHOD_BLOCKED")

    def test_invalid_proxy_rejected(self):
        for value in [
            "socks5://localhost:9999",
            "http://user:password@localhost:9",
            "https://localhost:9",
            "http://localhost:9/private",
        ]:
            with self.assertRaises(BridgeError):
                Transport("synthetic", value)

    def test_transfer_false_flag_with_matching_token_is_valid(self):
        transport = FakeTransport()
        result = collect(transport, UID, PASSWORD, self.folder)
        self.assertTrue((self.folder / result["filename"]).is_file())
        self.assertEqual(transport.calls.count("/api.Migration/Execute"), 1)
        with zipfile.ZipFile(self.folder / result["filename"]) as z:
            snap = json.loads(z.read("account.json"))
            manifest = json.loads(z.read("manifest.json"))
            self.assertEqual(len(snap["userData"]["cards"]), 1)
            self.assertIsNone(manifest["credentialsIncluded"])
            self.assertFalse(manifest["authenticationArtifactsWritten"])
            self.assertFalse(manifest["safeToShare"])
            self.assertFalse(snap["coverage"]["allAccountDomainsComplete"])
            for name, digest in manifest["files"].items():
                self.assertEqual(hashlib.sha256(z.read(name)).hexdigest(), digest)
            for name in z.namelist():
                for forbidden in [
                    PASSWORD,
                    "synthetic-firebase-session",
                    "synthetic-game-session",
                    "synthetic-one-time",
                    "synthetic-custom-session",
                ]:
                    self.assertNotIn(forbidden.encode(), z.read(name))
            self.assertEqual(
                codec.decode(
                    codec.descriptor("/api.User/Get").output_type, z.read("raw/user.pb")
                ),
                snap["userData"],
            )

    def test_mismatched_transfer_stops_before_execute(self):
        transport = FakeTransport(linked="DEMO9999")
        with self.assertRaises(BridgeError):
            collect(transport, UID, PASSWORD, self.folder)
        self.assertNotIn("/api.Migration/Execute", transport.calls)
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_mismatched_authenticated_identity_stops_before_reads(self):
        transport = FakeTransport(identity="DEMO9999")
        with self.assertRaises(BridgeError):
            collect(transport, UID, PASSWORD, self.folder)
        self.assertNotIn("/api.User/Get", transport.calls)
        self.assertNotIn("/api.Master/Get", transport.calls)

    def test_execute_failure_never_retried(self):
        transport = FakeTransport(fail="/api.Migration/Execute")
        with self.assertRaises(BridgeError):
            collect(transport, UID, PASSWORD, self.folder)
        self.assertEqual(transport.calls.count("/api.Migration/Execute"), 1)

    def test_optional_failure_keeps_primary_backup(self):
        result = collect(
            FakeTransport(fail="/api.Migration/List"), UID, PASSWORD, self.folder
        )
        self.assertGreaterEqual(len(list(self.folder.glob("*.zip"))), 1)
        self.assertEqual(
            result["coverage"]["supplementalFailures"][0]["domain"], "migration-list"
        )

    def test_snapshot_is_committed_before_supplemental(self):
        stages = []

        def progress(**values):
            stages.append(values["stage"])
            if values["stage"] == "supplemental":
                self.assertGreater(len(list(self.folder.glob("*.zip"))), 0)

        collect(FakeTransport(), UID, PASSWORD, self.folder, progress)
        self.assertEqual(stages[-1], "done")
        self.assertFalse(list(self.folder.glob("*.partial")))

    def test_apk_configuration_and_cleanup_inputs(self):
        path = self.folder / "synthetic.apk"
        with zipfile.ZipFile(path, "w") as z:
            z.writestr(
                "AndroidManifest.xml",
                '<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="game.qualiarts.idolypride" android:versionName="6.1.0"/>',
            )
            z.writestr("resources.arsc", ("AI" + "za" + "0" * 35).encode())
        self.assertEqual(len(extract_project(path)), 39)
        with zipfile.ZipFile(self.folder / "synthetic.xapk", "w") as z:
            z.writestr("base.apk", path.read_bytes())
        self.assertEqual(
            extract_project(path), extract_project(self.folder / "synthetic.xapk")
        )

    def test_wrong_apk_package_is_rejected(self):
        path = self.folder / "wrong.apk"
        with zipfile.ZipFile(path, "w") as z:
            z.writestr(
                "AndroidManifest.xml",
                '<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="unrelated.application" android:versionName="9.9.9"/>',
            )
            z.writestr("resources.arsc", b"no project")
        with self.assertRaises(BridgeError):
            extract_project(path)

    def test_local_api_security(self):
        app = Application(self.folder)
        server = create_server(app)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        port = server.server_port

        def request(path, headers=None, method="GET", body=None):
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            status = response.status
            data = response.read()
            connection.close()
            return status, data

        try:
            self.assertEqual(request("/")[0], 200)
            self.assertEqual(request("/api/state")[0], 403)
            self.assertEqual(
                request("/api/state", {"X-Bridge-Token": app.token})[0], 200
            )
            self.assertEqual(
                request(
                    "/api/state",
                    {
                        "X-Bridge-Token": app.token,
                        "Origin": "https://untrusted.invalid",
                    },
                )[0],
                403,
            )
            self.assertEqual(
                request(
                    "/api/state",
                    {"X-Bridge-Token": app.token, "Host": "untrusted.invalid"},
                )[0],
                403,
            )
            self.assertEqual(request("/../LICENSE")[0], 404)
            code, body = request(
                "/api/collect",
                {"X-Bridge-Token": app.token, "Content-Type": "application/json"},
                "POST",
                b'{"confirm":true}',
            )
            self.assertEqual(code, 400)
            self.assertNotIn(PASSWORD.encode(), body)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
