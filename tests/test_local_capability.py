import contextlib, io, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from archive_bridge.cli import main


class LocalCapabilityTests(unittest.TestCase):
    def run_cli(self, manual):
        with tempfile.TemporaryDirectory() as folder:
            app = MagicMock()
            app.output = Path(folder) / "exports"
            app.token = "SYNTHETIC_LOCAL_CAPABILITY"
            server = MagicMock()
            server.server_port = 12345
            server.serve_forever.side_effect = KeyboardInterrupt
            buffer = io.StringIO()
            args = ["archive-bridge", "--data-dir", folder] + (
                ["--no-browser"] if manual else []
            )
            with (
                patch.object(sys, "argv", args),
                patch("archive_bridge.server.Application", return_value=app),
                patch("archive_bridge.server.create_server", return_value=server),
                patch(
                    "archive_bridge.cli.webbrowser.open", return_value=True
                ) as browser,
                contextlib.redirect_stdout(buffer),
            ):
                main()
            return buffer.getvalue(), browser

    def test_normal_launch_does_not_print_capability(self):
        text, browser = self.run_cli(False)
        self.assertNotIn("SYNTHETIC_LOCAL_CAPABILITY", text)
        browser.assert_called_once()

    def test_manual_mode_is_explicit_and_warns(self):
        text, browser = self.run_cli(True)
        self.assertIn("do not share", text)
        self.assertIn("SYNTHETIC_LOCAL_CAPABILITY", text)
        browser.assert_not_called()
