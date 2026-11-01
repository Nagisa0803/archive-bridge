"""Extract public project configuration from a user-supplied original APK, locally."""

import re, zipfile
from .errors import BridgeError
from .manifest import read_manifest
from .versioning import PACKAGE, version_tuple

MAX_APK = 512 * 1024 * 1024


def read_profile(path):
    def read_base(z):
        for name, limit in [
            ("resources.arsc", 64 * 1024 * 1024),
            ("AndroidManifest.xml", 4 * 1024 * 1024),
        ]:
            if name not in z.namelist() or z.getinfo(name).file_size > limit:
                raise BridgeError(
                    "UNSUPPORTED_APK",
                    "Select the supported original game APK or XAPK (Japanese Android).",
                )
        package, version = read_manifest(z.read("AndroidManifest.xml"))
        if package != PACKAGE:
            raise BridgeError(
                "UNSUPPORTED_APK",
                "Select the original Japanese IDOLY PRIDE package, not another region or application.",
            )
        version_tuple(version)
        keys = set(re.findall(rb"AIza[0-9A-Za-z_-]{35}", z.read("resources.arsc")))
        if len(keys) != 1:
            raise BridgeError(
                "UNSUPPORTED_APK",
                "A unique public authentication project could not be identified.",
            )
        return {
            "project": next(iter(keys)).decode("ascii"),
            "apkVersion": version,
            "package": package,
        }

    try:
        with zipfile.ZipFile(path) as z:
            if len(z.infolist()) > 50000:
                raise BridgeError("UNSUPPORTED_APK", "Too many APK entries.")
            if "resources.arsc" in z.namelist():
                return read_base(z)
            candidates = [
                n
                for n in z.namelist()
                if n.endswith(".apk")
                and ("game.qualiarts.idolypride" in n or n.endswith("base.apk"))
            ]
            if len(candidates) != 1 or z.getinfo(candidates[0]).file_size > MAX_APK:
                raise BridgeError(
                    "UNSUPPORTED_APK", "Choose the base game APK inside this package."
                )
            with z.open(candidates[0]) as stream:
                with zipfile.ZipFile(stream) as base:
                    return read_base(base)
    except (zipfile.BadZipFile, KeyError, RuntimeError, OSError):
        raise BridgeError(
            "UNSUPPORTED_APK",
            "Could not read this package. Choose an unmodified local APK/XAPK.",
        ) from None


def extract_project(path):
    return read_profile(path)["project"]
