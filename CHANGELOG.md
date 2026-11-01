# Changelog

## 0.3.2

- Keep one archive per collection: atomically update the initial checkpoint with final supplemental data. Interrupted writes preserve the recovery copy.
- Hide the active checkpoint from downloads; distinguish final, recovery and historical archives.
- Show optional photo-read failures and credential-free HTTP/gRPC status codes instead of implying complete coverage.


## 0.3.1

- Add an original Archive Bridge app icon at 16–256 pixel sizes in Windows executables.
- Match the local wizard brand and browser favicon to the executable icon.


## 0.3.0

- Add an explicit image-link option: known generic card previews and bounded read-only URL lookups for owned photo assets.
- Export private JSON/CSV/TXT link files and Lens-compatible embedded photo mappings; originals are not downloaded.
- Preserve the primary account ZIP if optional URL reads fail; report missing URLs without guessing.
- Add synthetic scope, opt-out, empty-account, partial-failure and unsafe-URL regression checks.


## 0.2.1

- Remove the local access capability from the address bar immediately after reading it.
- Do not print the private startup URL during normal automatic browser launch; show it only in explicit --no-browser mode with a warning.
- Keep full account ZIPs private: preserving raw account data is not anonymization; credential presence in unknown raw fields is marked unassessed.


## 0.2.0

- Stable release with six native packages and explicit GitHub Latest publication after all assets upload.
- Read original APK versionName and check fresh official Japanese Android Google Play metadata before every collection.
- Apply the discovered version to all game requests; stop before authentication on discovery failure, downgrade, or unsupported protocol major. Never silently reuse an old version.
- Show current request/APK versions in the four-language local wizard and preserve public version provenance in exported coverage.
- Strengthen source privacy checks and use GitHub-associated noreply commit identities.


## 0.1.0-rc.1

- Independent portable collector with English, Chinese, Japanese and Korean local wizard.
- Explicit one-time transfer consent, exact target checks and bounded necessary reads.
- Local original APK/XAPK configuration, verified TLS and optional HTTP CONNECT proxy.
- Atomic compatible User/Get JSON/protobuf ZIPs with honest coverage and retained primary snapshots.
- Local access tickets, Host/Origin checks, single job, cancellation and saved-archive downloads.
- Six native Windows/macOS/Linux x64/ARM64 builds, offline fixture tests, binary self-tests and all-green-only publication.
- First release candidate: unsigned/not notarized; photo originals, artwork, independent histories and other client versions remain outside this release.
