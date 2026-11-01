"""Package native builds, source notices and dependency manifest with reproducible naming."""

import argparse, importlib.metadata, json, os, platform, shutil, subprocess, sys, tarfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--platform", required=True, choices=["windows", "linux", "macos"])
parser.add_argument("--arch", required=True, choices=["x64", "arm64"])
parser.add_argument("--version", required=True)
args = parser.parse_args()
subprocess.run(
    [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--specpath",
        "build",
        "--name",
        "archive-bridge",
        "--collect-data",
        "archive_bridge",
        str(ROOT / "launcher.py"),
    ],
    cwd=ROOT,
    check=True,
)
folder = ROOT / "dist/archive-bridge"
for name in [
    "LICENSE",
    "README.md",
    "README.zh-CN.md",
    "README.ja.md",
    "README.ko.md",
    "THIRD_PARTY_NOTICES.md",
    "CHANGELOG.md",
]:
    shutil.copyfile(ROOT / name, folder / name)
licenses = folder / "dependency-licenses"
licenses.mkdir(exist_ok=True)
dependencies = []
for name in [
    "cryptography",
    "h2",
    "hpack",
    "hyperframe",
    "protobuf",
    "cffi",
    "pycparser",
]:
    try:
        dist = importlib.metadata.distribution(name)
    except importlib.metadata.PackageNotFoundError:
        continue
    dependencies.append(
        {
            "name": dist.metadata["Name"],
            "version": dist.version,
            "license": dist.metadata.get("License-Expression")
            or dist.metadata.get("License", "See bundled notices"),
        }
    )
    for file in dist.files or []:
        if any(
            word in str(file).lower() for word in ["license", "copying", "notice"]
        ) and ".dist-info/" in str(file):
            source = dist.locate_file(file)
            if source.is_file():
                target = licenses / (name + "-" + Path(str(file)).name)
                target.write_bytes(source.read_bytes())
info = {
    "version": args.version,
    "os": args.platform,
    "arch": args.arch,
    "python": platform.python_version(),
    "machine": platform.machine(),
    "dependencies": dependencies,
    "signing": "not signed/not notarized",
    "tests": "offline unit tests and native binary self-test required by workflow",
}
(folder / "build-info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
release = ROOT / "release"
release.mkdir(exist_ok=True)
base = "archive-bridge-" + args.version + "-" + args.platform + "-" + args.arch
if args.platform == "windows":
    with zipfile.ZipFile(
        release / (base + ".zip"), "w", zipfile.ZIP_DEFLATED, compresslevel=6
    ) as archive:
        for file in folder.rglob("*"):
            if file.is_file():
                archive.write(file, Path("archive-bridge") / file.relative_to(folder))
else:
    with tarfile.open(release / (base + ".tar.gz"), "w:gz") as archive:
        archive.add(folder, arcname="archive-bridge")
print("Created " + base)
