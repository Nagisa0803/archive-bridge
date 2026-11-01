import json, threading, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from archive_bridge.versioning import (
    parse_play_version,
    discover_version,
    version_tuple,
)
from archive_bridge.errors import BridgeError
from archive_bridge.transport import Transport
from archive_bridge.collector import collect
from test_product import FakeTransport, UID, PASSWORD


def page(version):
    row = [None] * 141
    row[140] = [[[version]]]
    data = [None, [None, None, row]]
    return (
        "AF_initDataCallback({key: 'ds:5', hash: 'x', data: "
        + json.dumps(data)
        + ", sideChannel: {}});"
    )


class VersionTests(unittest.TestCase):
    def test_latest_patch_and_minor_are_used(self):
        for version in ["6.1.7", "6.2.0"]:
            result = discover_version("6.1.0", fetch=lambda: page(version))
            self.assertEqual(result["appVersion"], version)

    def test_reject_missing_or_conflicting_metadata(self):
        for text in [
            "Version 999.0.0",
            page("6.1.0") + page("6.2.0"),
            page("Varies with device"),
        ]:
            with self.assertRaises(BridgeError):
                parse_play_version(text)

    def test_never_downgrade_to_stale_store_version(self):
        with self.assertRaises(BridgeError) as error:
            discover_version("6.1.0", fetch=lambda: page("6.0.2"))
        self.assertEqual(error.exception.code, "VERSION_SOURCE_STALE")

    def test_new_protocol_major_stops_before_auth(self):
        with self.assertRaises(BridgeError) as error:
            discover_version("6.1.0", fetch=lambda: page("7.0.0"))
        self.assertEqual(error.exception.code, "PROTOCOL_UPDATE_REQUIRED")

    def test_invalid_versions_cannot_enter_header(self):
        for value in ["6.1.0\r\nx-auth-token: x", "v6.1.0", "unknown", None]:
            with self.assertRaises(BridgeError):
                version_tuple(value)

    def test_failure_stops_all_account_calls(self):
        transport = FakeTransport()
        transport.prepare_version = lambda: (_ for _ in ()).throw(
            BridgeError("VERSION_CHECK_FAILED", "Synthetic failure")
        )
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(BridgeError):
                collect(transport, UID, PASSWORD, Path(directory))
        self.assertEqual(transport.calls, [])

    def test_unprepared_transport_never_connects(self):
        transport = Transport("synthetic")
        with patch.object(transport, "connect") as connection:
            with self.assertRaises(BridgeError):
                transport.rpc("/api.Auth/Login", {})
            connection.assert_not_called()

    def test_metadata_network_failure_does_not_fallback(self):
        import urllib.error

        with patch("archive_bridge.versioning.urllib.request.build_opener") as build:
            build.return_value.open.side_effect = urllib.error.URLError(
                "Synthetic outage"
            )
            with self.assertRaises(BridgeError) as error:
                discover_version("6.1.0")
        self.assertEqual(error.exception.code, "VERSION_CHECK_FAILED")

    def test_official_source_redirect_is_restricted(self):
        from archive_bridge.versioning import OfficialRedirects

        with self.assertRaises(BridgeError):
            OfficialRedirects().redirect_request(
                None, None, 302, "redirect", {}, "https://untrusted.invalid/metadata"
            )

    def test_discovered_version_is_sent_in_real_rpc_headers(self):
        from unittest.mock import MagicMock
        from h2.events import ResponseReceived, DataReceived, StreamEnded

        transport = Transport("synthetic")
        transport.apk_version = "6.1.0"
        with patch(
            "archive_bridge.transport.discover_version",
            return_value={"appVersion": "6.2.7"},
        ):
            transport.prepare_version()
        h = MagicMock()
        h.get_next_available_stream_id.return_value = 1
        h.data_to_send.return_value = b""
        response = ResponseReceived(
            stream_id=1, headers=[(":status", "200"), ("grpc-status", "0")]
        )
        data = DataReceived(stream_id=1, data=bytes(5), flow_controlled_length=5)
        h.receive_data.return_value = [response, data, StreamEnded(stream_id=1)]
        tls = MagicMock()
        tls.__enter__.return_value = tls
        tls.recv.return_value = b"synthetic-packet"
        with (
            patch.object(transport, "connect", return_value=tls),
            patch("archive_bridge.transport.H2Connection", return_value=h),
        ):
            transport.rpc("/api.Master/Get")
        headers = dict(h.send_headers.call_args.args[1])
        self.assertEqual(headers["x-app-version"], "6.2.7")

    def test_cancel_before_version_discovery(self):
        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(BridgeError):
            discover_version(
                "6.1.0", cancel=cancel, fetch=lambda: self.fail("Should not fetch")
            )
