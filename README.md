# Archive Bridge

[English](README.md) · [Simplified Chinese](README.zh-CN.md) · [Japanese](README.ja.md) · [Korean](README.ko.md)

A local account exporter for **[Archive Lens](https://github.com/Nagisa0803/archive-lens)**. Run a native application, follow the browser wizard, and save a portable ZIP on your own computer. Open the ZIP locally in the viewer; the public website does not receive account data.

**[Downloads](https://github.com/Nagisa0803/archive-bridge/releases)** · **[Live viewer](https://archive-lens.chiyoda-site.workers.dev/)** · **[Export/import handbook](https://archive-lens.chiyoda-site.workers.dev/guide/)**

**Current stable release: [v0.2.1](https://github.com/Nagisa0803/archive-bridge/releases/latest).** Before every sign-in, Bridge reads the latest official Japanese Android version. CI uses synthetic accounts, never real credentials.


### Image links (v0.3.0)

The local wizard enables **Include image links** by default; clear it to skip extra photo reads. After your explicit collection consent, Bridge records known generic card-preview URLs and queries only asset IDs already in your account photo records (batches of at most 50). It never guesses missing URLs or downloads image files.

The ZIP adds `image-links.json`, `image-links.csv`, `image-links.txt`, and a Lens-compatible `photo-links.json`; card/photo mappings are also attached to `account.json`. Photo links may expire or contain access parameters. Keep the entire archive and its links private. Missing card previews and photo URLs are counted in coverage; a returned URL is not proof that an image was backed up. No new live account authentication was used to validate this release; the integration is covered by synthetic tests.


## Download the right build

Each version publishes six native packages, after all six jobs pass tests and compiled-program self-tests.

| Operating system | CPU | Package suffix | Tested runner baseline |
| --- | --- | --- | --- |
| Windows | Intel/AMD x64 | `windows-x64.zip` | Windows Server 2025; Windows 10/11 x64 targeted |
| Windows | ARM64 | `windows-arm64.zip` | Windows 11 ARM |
| Linux | x64 | `linux-x64.tar.gz` | Ubuntu 22.04, glibc 2.35+ |
| Linux | ARM64 / aarch64 | `linux-arm64.tar.gz` | Ubuntu 24.04, glibc 2.39+ |
| macOS | Intel x64 | `macos-x64.tar.gz` | macOS 15 Intel |
| macOS | Apple Silicon | `macos-arm64.tar.gz` | macOS 15 ARM64 |

You do not need Python, ADB, root, injection or a modified APK. Download the package matching both your OS and CPU, then extract the **whole directory**, including `_internal`. Initial binaries are unsigned and not Apple-notarized. `SHA256SUMS` verifies download integrity, not publisher identity; do not disable system-wide security protections.

## First export

1. Run `archive-bridge.exe` on Windows, or `./archive-bridge` on Linux/macOS. The local wizard opens automatically. If it does not, restart with `--no-browser` to obtain a private manual link. Do not share that active link; its token is removed from the address bar after use. Refreshing requires reopening the original private link.
2. Choose your own **original Japanese Android APK or XAPK**, up to 512 MiB. Bridge reads only the public authentication project configuration locally and deletes its temporary upload. No APK or account data is uploaded to the Internet. This configuration stays in memory, so select it again after restarting Bridge.
3. Set the game's account transfer password in the game. Enter your transfer ID and password **only in the local wizard**. This is the game transfer password, not your Google/Apple password.
4. Confirm that it is your account and explicitly authorize authentication and necessary reads. Authentication can affect an active session on another device. Click **Authenticate and export ZIP** once; migration execution is never automatically retried.
5. Watch progress. Bridge commits the essential account snapshot before supplementary reads. A later error or cancellation keeps previously completed ZIPs. Cancellation takes effect at request boundaries; an in-flight request can take up to its timeout.
6. Download the completed ZIP. Open **[Archive Lens](https://archive-lens.chiyoda-site.workers.dev/)** and import it locally. Its viewer and guide support English, Chinese, Japanese and Korean; English is the default.

The wizard shows the actual export folder. By default it is `ArchiveBridgeData/exports` beside the portable executable. Keep the directory writable. To choose another location or a fixed port:

```sh
archive-bridge --data-dir /path/to/private-data --port 8794
archive-bridge --no-browser
archive-bridge --version
archive-bridge --self-test --data-dir /path/to/offline-test
```

On Windows, quote paths containing spaces and use `archive-bridge.exe`. The optional HTTP proxy setting accepts `http://host:port`; blank means a direct connection. HTTPS certificate verification stays enabled.

## What a ZIP contains

- `account.json`: the complete decoded `User/Get` response and explicit coverage metadata.
- `raw/user.pb`: the original response protobuf, including fields not understood by the current descriptor.
- `raw/master.pb` and `decoded/master.json`: the corresponding master information response.
- `raw/rpc/`: successfully obtained migration-list metadata, when available.
- `collection.json`: method names, timings and response sizes; no request bodies or authentication headers.
- `manifest.json`: format version, SHA-256 file checksums and coverage; compatible with Archive Lens ZIP import.

**Not intentionally recorded:** entered passwords or authentication responses. Credential presence in unknown raw account fields is not fully assessed; manifests mark it unknown. These complete backups are private, not anonymized. Also excluded: captured TLS secrets, APK files, device restore archives, card artwork, photo originals, or a proven complete independent message/phone history. This release does not claim complete account/media coverage. The ZIP contains private account information and is not anonymized. Keep it private; do not equate absence of recorded login credentials with safe public sharing.

## Product boundaries

The application binds only to `127.0.0.1`, uses a per-launch local access token, validates Host/Origin, and runs one collection at a time. Credentials remain in process memory; it does not promise forensic memory erasure. There is no analytics, updater, background collection, certificate installation, APK patching, gameplay operation, purchase, arbitrary RPC console or endpoint enumeration.

APK package/version are detected from its manifest. Before every collection, Bridge fetches the current version from the official Japanese Google Play listing and applies it to all `x-app-version` headers. No cached/old fallback is used when lookup fails, and no downgrade is allowed. A new protocol major stops before authentication. Same-major updates can still change schemas; response validation remains enabled and unsupported replies stop the workflow. The wizard and ZIP coverage show request/APK versions and the check source/time.

## Troubleshooting

| Code / symptom | Action |
| --- | --- |
| `PROFILE_REQUIRED` / `UNSUPPORTED_APK` | Select the original supported base APK or matching XAPK; do not rename an unrelated client. |
| `TRANSFER_REJECTED` | Check that the game transfer settings are saved and the ID/password are correct. No automatic retry occurs. |
| `IDENTITY_MISMATCH` | Stop. The authenticated target differs from the requested account; account reads are blocked. |
| `PROXY_FAILED` / `NETWORK_TIMEOUT` | Check your local proxy or direct network connection; review completed ZIPs before starting a new session. |
| Local access denied | Reopen the full local URL printed by the currently running process, including its fragment. |
| Cannot save output | Choose a writable `--data-dir`; existing completed exports are retained. |
| Browser closed | The native application keeps running. Reopen its local URL, or stop it with Ctrl+C. |

Report the version, OS/architecture and safe error code in an issue. Never attach real account ZIPs, passwords, tokens, private photo links or raw network captures. See [SECURITY.md](SECURITY.md).

## Development and cloud releases

```sh
python -m venv .venv
# Activate the environment for your operating system.
python -m pip install -e . -r requirements-build.txt -r requirements-dev.txt
python -m ruff format --check .
python -m ruff check --select E9,F63,F7,F82 .
python scripts/check_public.py
python -m unittest discover -s tests -v
python -m archive_bridge --self-test --data-dir .ci-self-test
```

GitHub Actions builds on native Windows/macOS/Linux runners for both architectures. Every build runs offline tests, the public-source gate and a compiled-executable self-test. Version tags such as `v0.2.1` publish all six packages and `SHA256SUMS` only after the complete matrix succeeds. Builds include dependency notices and `build-info.json`. CI never authenticates to the game and needs no account secrets. A separate source-quality workflow enforces readable Python/frontend formatting and static checks on main and pull requests.

[Product design and upstream references](docs/PRODUCT.md) · [Changelog](CHANGELOG.md) · [Third-party notices](THIRD_PARTY_NOTICES.md)

Application/source distribution: **AGPL-3.0-only**. Public protocol reference and descriptor attribution are recorded in the notices. Not affiliated with the game publisher; no game APK or game assets are distributed.
