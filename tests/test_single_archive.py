import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from archive_bridge.collector import collect
from archive_bridge.server import Application
from test_product import FakeTransport, UID, PASSWORD
from test_image_links import PhotoTransport


class SingleArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_one_final_archive_and_checkpoint_hidden_until_finished(self):
        app = Application(self.root)
        app.state = {"status": "running"}
        checkpoints = []

        def progress(**values):
            app.progress(**values)
            if values["stage"] == "supplemental":
                checkpoints.append(values["backup"]["filename"])
                self.assertEqual(len(list(app.output.glob("*.zip"))), 1)
                self.assertEqual(app.list_backups(), [])

        result = collect(
            PhotoTransport(count=3),
            UID,
            PASSWORD,
            app.output,
            progress,
            include_image_links=True,
        )
        app.progress(status="complete", backup=result)
        self.assertEqual(checkpoints, [result["filename"]])
        self.assertEqual(len(list(app.output.glob("*.zip"))), 1)
        self.assertEqual(app.list_backups()[0]["archiveState"], "final")
        with zipfile.ZipFile(app.output / result["filename"]) as z:
            self.assertIn("photo-links.json", z.namelist())
            self.assertEqual(len(json.loads(z.read("account.json"))["photoLinks"]), 2)

    def test_failed_final_replace_preserves_valid_recovery_zip(self):
        replacement = None

        def progress(**values):
            nonlocal replacement
            if values["stage"] == "supplemental":
                replacement = patch(
                    "archive_bridge.archive.os.replace",
                    side_effect=OSError("synthetic replace failure"),
                )
                replacement.start()

        try:
            with self.assertRaises(OSError):
                collect(FakeTransport(), UID, PASSWORD, self.root, progress)
        finally:
            if replacement:
                replacement.stop()
        files = list(self.root.glob("*.zip"))
        self.assertEqual(len(files), 1)
        self.assertFalse(list(self.root.glob("*.partial")))
        with zipfile.ZipFile(files[0]) as z:
            self.assertIsNone(z.testzip())
            self.assertIn("raw/user.pb", z.namelist())
            self.assertEqual(
                json.loads(z.read("account.json"))["coverage"]["collectionState"],
                "collecting_supplemental",
            )

    def test_optional_photo_failure_is_one_explicitly_partial_archive(self):
        app = Application(self.root)
        result = collect(
            PhotoTransport(mode="failure"),
            UID,
            PASSWORD,
            app.output,
            include_image_links=True,
        )
        app.progress(status="complete", backup=result)
        self.assertEqual(len(app.list_backups()), 1)
        self.assertEqual(app.list_backups()[0]["archiveState"], "partial")
        self.assertEqual(
            result["coverage"]["collectionState"], "finished_with_warnings"
        )
