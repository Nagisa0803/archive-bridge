# Third-party notices

- Public protocol reference: [vertesan/solis-server](https://github.com/vertesan/solis-server), AGPL-3.0. `src/archive_bridge/resources/public-solis-marshaler.go` is the public reference implementation. Its fixed application-protocol parameters are publicly distributed compatibility constants, not captured TLS session keys or account credentials. The bundled descriptor set describes the public API interface; it contains no captured account messages. This application is distributed under AGPL-3.0-only; see LICENSE.
- Runtime: cryptography (Apache-2.0/BSD), h2/hpack/hyperframe (MIT), protobuf (BSD-3-Clause), and platform-dependent cffi/pycparser. Native packages include their dependency version manifest and available license files.
- PyInstaller builds native packages; its bootloader exception permits distribution of bundled applications. See the upstream PyInstaller licensing documentation and your package's build information.
- The game's names, trademarks, APKs and assets belong to their respective right holders. No APK, personal snapshot, owned-card collection, private photo URL or game asset collection is included in this repository.

Generic card title mappings: INFO PRIDE CCID table, https://github.com/outloudvi/info-pride/blob/master/data/ccid/ccid.json ; dataset CC BY-NC-SA 3.0 as documented by INFO PRIDE. Card preview URLs refer to Archive Lens generic game artwork; no ownership is included in this source catalog.
