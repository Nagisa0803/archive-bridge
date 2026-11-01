# Changelog

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
