import json
import tempfile
from pathlib import Path
import unittest
import zipfile
from test_product import FakeTransport, UID, PASSWORD
from archive_bridge import codec
from archive_bridge.collector import collect
from archive_bridge.errors import BridgeError
from archive_bridge.image_links import validate_url


class PhotoTransport(FakeTransport):
    def __init__(self, count=51, mode="ok"):
        super().__init__()
        self.count = count
        self.mode = mode
        self.photo_batches = []

    def rpc(self, path, values=None, token=None, version=None):
        if path == "/api.Photo/GetImageURL":
            self.calls.append(path)
            self.photo_batches.append(values)
            if self.mode == "failure":
                raise BridgeError("SYNTHETIC_FAILURE", "Synthetic failure")
            assets = values["assetIds"]
            rows = [
                {
                    "assetId": asset,
                    "origUrl": "https://storage.googleapis.com/synthetic-demo/"
                    + asset
                    + ".png",
                    "tmbUrl": "https://storage.googleapis.com/synthetic-demo/"
                    + asset
                    + "-thumb.png",
                }
                for asset in assets[:-1]
            ]
            if self.mode == "foreign":
                rows = [
                    {
                        "assetId": "NOT-OWNED",
                        "origUrl": "https://storage.googleapis.com/synthetic-demo/foreign.png",
                    }
                ]
            if self.mode == "invalid":
                rows = [{"assetId": assets[0], "origUrl": "http://127.0.0.1/private"}]
            data = {"urlList": rows}
            raw = codec.encode(codec.descriptor(path).output_type, data)
            return (
                codec.decode(codec.descriptor(path).output_type, raw),
                raw,
                {"method": path, "status": "0", "responseBytes": len(raw)},
            )
        data, raw, meta = super().rpc(path, values, token, version)
        if path == "/api.User/Get":
            data["cards"] = [{"cardId": "card-ai-02-eve-00"}]
            data["photos"] = [
                {
                    "photoId": "synthetic-photo-" + str(i),
                    "assetId": "synthetic-asset-" + str(i),
                }
                for i in range(self.count)
            ]
            raw = codec.encode(codec.descriptor(path).output_type, data)
        return data, raw, meta


class ImageLinkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_collection(self, transport, enabled=True):
        result = collect(
            transport, UID, PASSWORD, self.folder, include_image_links=enabled
        )
        with zipfile.ZipFile(self.folder / result["filename"]) as z:
            return result, {name: z.read(name) for name in z.namelist()}

    def test_links_are_bounded_owned_only_and_portable(self):
        transport = PhotoTransport()
        result, files = self.run_collection(transport)
        self.assertEqual([len(x["assetIds"]) for x in transport.photo_batches], [50, 1])
        self.assertTrue(all(x["type"] == 3 for x in transport.photo_batches))
        snapshot = json.loads(files["account.json"])
        self.assertEqual(len(snapshot["photoLinks"]), 49)
        card = snapshot["cardImageLinks"]["card-ai-02-eve-00"]
        self.assertTrue(
            card["previewUrl"].startswith(
                "https://archive-lens.chiyoda-site.workers.dev/cards/images/"
            )
        )
        self.assertTrue(card["name"])
        self.assertIn(card["previewUrl"].encode(), files["image-links.txt"])
        for name in [
            "image-links.json",
            "image-links.csv",
            "photo-links.json",
            "raw/rpc/photo_get_image_url_0000.pb",
        ]:
            self.assertIn(name, files)
        self.assertEqual(result["coverage"]["imageLinks"]["photoAssetsWithoutURLs"], 2)
        self.assertFalse(result["coverage"]["imageLinks"]["allURLsDownloadTested"])
        self.assertFalse(result["coverage"]["photoOriginalsDownloaded"])

    def test_disabled_means_no_photo_requests(self):
        transport = PhotoTransport()
        result, files = self.run_collection(transport, False)
        self.assertEqual(transport.photo_batches, [])
        self.assertNotIn("image-links.json", files)
        self.assertFalse(result["coverage"]["imageLinks"]["requested"])

    def test_no_photos_does_not_send_empty_request(self):
        transport = PhotoTransport(count=0)
        result, files = self.run_collection(transport)
        self.assertEqual(transport.photo_batches, [])
        self.assertEqual(json.loads(files["account.json"])["photoLinks"], {})
        self.assertFalse(result["coverage"]["imageLinks"]["allURLsDownloadTested"])

    def test_optional_failure_preserves_account_backup(self):
        result, files = self.run_collection(PhotoTransport(mode="failure"))
        self.assertIn("raw/user.pb", files)
        self.assertEqual(
            result["coverage"]["supplementalFailures"][0]["domain"], "photo-links"
        )
        self.assertFalse(result["coverage"]["imageLinks"]["photoURLReadsComplete"])

    def test_foreign_assets_or_invalid_urls_are_not_saved(self):
        for mode in ["foreign", "invalid"]:
            with self.subTest(mode=mode):
                result, files = self.run_collection(PhotoTransport(mode=mode))
                self.assertEqual(json.loads(files["account.json"])["photoLinks"], {})
                self.assertNotIn("raw/rpc/photo_get_image_url_0000.pb", files)
                self.assertTrue(result["coverage"]["supplementalFailures"])

    def test_photo_url_allowlist(self):
        for url in [
            "file:///private",
            "https://example.invalid/a",
            "https://user:password@storage.googleapis.com/a",
            "https://storage.googleapis.com:444/a",
        ]:
            with self.subTest(url=url):
                with self.assertRaises((BridgeError, ValueError)):
                    validate_url(url)


class TransientPhotoTransport(PhotoTransport):
    def __init__(self, large_batches_fail=False):
        super().__init__(count=21)
        self.photo_attempts = 0
        self.large_batches_fail = large_batches_fail

    def rpc(self, path, values=None, token=None, version=None):
        if path == "/api.Photo/GetImageURL":
            self.photo_attempts += 1
            if self.photo_attempts == 1 or (
                self.large_batches_fail and len(values["assetIds"]) > 10
            ):
                raise BridgeError(
                    "RPC_FAILED",
                    "Synthetic transient photo error",
                    details={"httpStatus": "200", "grpcStatus": "13"},
                )
        return super().rpc(path, values, token, version)


class PhotoRecoveryTests(unittest.TestCase):
    def test_read_only_transient_retry_does_not_repeat_authentication(self):
        with tempfile.TemporaryDirectory() as folder:
            transport = TransientPhotoTransport()
            result = collect(transport, UID, PASSWORD, folder, include_image_links=True)
            self.assertEqual(transport.calls.count("/api.Migration/Execute"), 1)
            self.assertEqual(result["coverage"]["imageLinks"]["photoReadRetryCount"], 1)
            self.assertTrue(result["coverage"]["imageLinks"]["photoURLReadsComplete"])

    def test_rejected_large_batches_fall_back_once_without_guessing_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            transport = TransientPhotoTransport(large_batches_fail=True)
            result = collect(transport, UID, PASSWORD, folder, include_image_links=True)
            self.assertEqual(
                [len(x["assetIds"]) for x in transport.photo_batches], [10, 10, 1]
            )
            self.assertTrue(result["coverage"]["imageLinks"]["smallerPhotoBatchesUsed"])
            self.assertEqual(result["coverage"]["imageLinks"]["photoAssetsQueried"], 21)
            self.assertEqual(transport.photo_attempts, 5)
