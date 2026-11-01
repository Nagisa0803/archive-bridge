# Product design

Archive Bridge is a small, explicit exporter, with the same local ZIP contract consumed by [Archive Lens](https://github.com/Nagisa0803/archive-lens).

## What we studied

- [yt-dlp installation](https://github.com/yt-dlp/yt-dlp/wiki/Installation) and [releases](https://github.com/yt-dlp/yt-dlp/releases): recognizable platform/architecture packages, versioned downloads, checksums and a source-install alternative.
- [rclone configuration and progress](https://rclone.org/docs/) and [flags](https://rclone.org/flags/): visible progress, explicit network/output configuration and separation of normal operation from advanced options.
- [restic release verification](https://restic.readthedocs.io/en/v0.17.0/developer_information.html): release integrity and testing the binary users receive, rather than trusting source tests alone.
- [PyInstaller manual](https://pyinstaller.org/en/latest/): build on each native operating system; a Windows build is not a cross-compiler for macOS or Linux.

These are design references, not dependencies or claims of equivalent maturity.

## User journey

Download the matching native archive → extract all files → launch → select the original supported APK → enter own transfer credentials locally → explicitly consent → observe stages/cancel → keep ZIP → import locally into Lens.

The public viewer never receives credentials and never calls a user's loopback collector. There is no hidden server-to-server transfer of account data. Local configuration is deliberately minimal: public project information is extracted from the user's APK and held in memory; credentials are not saved.

## State and durability

The workflow is finite: validate target → execute transfer once → authenticate → match identity → get master version → get account → commit primary ZIP → attempt known migration-list metadata → commit enriched ZIP. Each ZIP is immutable and atomically renamed after verification. A supplementary failure never invalidates the primary archive. Cancellation is cooperative at request boundaries.

Coverage is a first-class field, not a success badge implying all game content was retrieved. Photo originals, artwork and independent histories remain outside this release.

## Release quality gate

Native x64 and ARM64 runners for Windows, macOS and Linux run offline identity/serialization/failure/security tests, optimized-Python tests, source scanning and packaged-executable self-tests. The release job depends on the entire matrix and requires exactly six package assets. Packages include dependency versions/notices, upstream license and a checksum manifest.

Version 0.3.0 adds explicitly selectable card-preview and owned-photo URL export; it does not download photo originals. Before any authentication, each collection reads the current official Japanese Android version. Same-major header updates do not guarantee unchanged schemas: response validation remains enabled and unsupported new protocol majors stop before authentication. Signed/notarized installers, broader game-version profiles and separately consented media/history modules are future work, not implemented features.
