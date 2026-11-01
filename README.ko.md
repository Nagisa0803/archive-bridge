# Archive Bridge

[English](README.md) · [Simplified Chinese](README.zh-CN.md) · [Japanese](README.ja.md) · [Korean](README.ko.md)

[Archive Lens](https://github.com/Nagisa0803/archive-lens)의 로컬 계정 수집 도구입니다. 네이티브 앱의 브라우저 안내를 따라 이 컴퓨터에 ZIP을 저장하고, 뷰어에서 로컬로 가져옵니다. 공개 웹사이트로 계정 데이터를 전송하지 않습니다.

**[다운로드](https://github.com/Nagisa0803/archive-bridge/releases)** · **[온라인 뷰어](https://archive-lens.chiyoda-site.workers.dev/)** · **[사용 가이드](https://archive-lens.chiyoda-site.workers.dev/guide/?lang=ko)**


### 이미지 링크(v0.3.0)

로컬 화면의 이미지 링크 옵션은 기본 켜짐이며 끄면 추가 사진 요청을 건너뜁니다. 동의 후 계정에 이미 존재하는 사진 리소스 ID만 최대 50개씩 조회합니다. 카드는 알려진 공통 미리보기 URL을 사용합니다. 누락 URL을 추측하거나 이미지 파일을 내려받지 않습니다.

ZIP에 `image-links.json`, `image-links.csv`, `image-links.txt`, `photo-links.json` 및 `account.json`의 매핑이 추가됩니다. URL은 만료되거나 접근 매개변수를 포함할 수 있으므로 비공개로 보관하세요. URL 확보는 이미지 백업 완료를 뜻하지 않습니다. 새 통합은 합성 데이터로 검증했으며 실제 계정을 다시 인증하지 않았습니다.


## 다운로드와 첫 사용

Windows, macOS, Linux 각각 x64와 ARM64 네이티브 패키지를 제공합니다. OS와 CPU가 모두 맞는 파일을 선택하고 `_internal`을 포함한 폴더 전체를 압축 해제하세요. Python, ADB, root, 주입, APK 수정이 필요하지 않습니다.

| 운영체제 | x64 | ARM64 |
| --- | --- | --- |
| Windows | `windows-x64.zip`, Windows 10/11 대상 | `windows-arm64.zip`, Windows 11 ARM |
| Linux | `linux-x64.tar.gz`, Ubuntu 22.04 / glibc 2.35+ | `linux-arm64.tar.gz`, Ubuntu 24.04 / glibc 2.39+ |
| macOS | `macos-x64.tar.gz`, macOS 15 Intel 검증 | `macos-arm64.tar.gz`, macOS 15 Apple Silicon 검증 |

1. Windows에서는 `archive-bridge.exe`, Linux/macOS에서는 `./archive-bridge`를 실행합니다. 로컬 안내 화면이 자동으로 열립니다. 열리지 않으면 터미널에 표시된 전체 로컬 URL을 여세요.
2. 본인의 수정하지 않은 **일본판 원본 Android APK/XAPK**(최대 512 MiB)를 선택하세요. 공개 인증 프로젝트 설정만 로컬에서 읽고 임시 파일을 삭제합니다. 재시작하면 다시 설정해야 하며 APK를 인터넷에 올리거나 게임을 수정하지 않습니다.
3. 게임에서 연동 비밀번호를 설정하고 로컬 화면에 게임 연동 ID와 비밀번호를 입력하세요. Google/Apple 비밀번호가 아닙니다. 채팅이나 Issue에 보내지 마세요.
4. 본인 계정과 인증·필요한 읽기를 명시적으로 허용한 후 인증 및 ZIP 내보내기를 한 번 실행하세요. 다른 기기의 게임 세션에 영향을 줄 수 있습니다. 연동 실행을 자동 재시도하지 않습니다.
5. 진행 상황을 확인하세요. 기본 스냅샷을 먼저 저장하므로 이후 실패나 취소가 발생해도 완성된 ZIP은 유지됩니다. 취소는 요청 경계에서 적용되며 진행 중인 요청은 시간 초과까지 걸릴 수 있습니다.
6. ZIP을 다운로드하고 [Archive Lens](https://archive-lens.chiyoda-site.workers.dev/?lang=ko)에서 로컬로 가져오세요. 수집 도구, 뷰어, 가이드는 영어·중국어·일본어·한국어를 지원하며 기본 언어는 영어입니다.

기본 저장 위치는 실행 파일 옆의 `ArchiveBridgeData/exports`이며 화면에서 실제 경로를 확인할 수 있습니다. `--data-dir /private/path`, `--port 8794`, `--no-browser` 옵션을 사용할 수 있습니다. HTTP 프록시는 `http://host:port` 형식이며 비워 두면 직접 연결합니다. TLS 인증서 검증을 유지합니다.

## 보존 범위와 개인정보

ZIP에는 User/Get 전체 JSON과 원본 protobuf, Master 응답, 성공적으로 가져온 연동 목록, 인증 정보 없는 수집 기록, SHA-256 파일 목록이 들어갑니다. 원본 protobuf는 현재 해석하지 못하는 필드도 보존하며 Lens로 직접 가져올 수 있습니다.

비밀번호, 인증·갱신 토큰, TLS 비밀 정보, APK, 기기 복원 자료, 카드 이미지, 사진 원본은 포함하지 않습니다. 별도 메시지·전화 기록의 완전성도 보장하지 않습니다. ZIP마다 실제 수집 범위를 기록하며 모든 콘텐츠의 완전한 백업이라고 주장하지 않습니다. ZIP 자체에는 개인 계정 정보가 있으므로 신중하게 공유하세요.

127.0.0.1만 사용하며 실행별 접근 토큰, Host/Origin 확인, 단일 작업 제어를 적용합니다. 인증 정보는 프로세스 메모리에만 유지하며 포렌식 수준의 메모리 삭제를 보장하지 않습니다. 추적 분석, 백그라운드 수집, 자동 업데이트, 인증서 변경, 게임 플레이·구매, 임의 RPC 기능이 없습니다.

정식 버전은 **[v0.2.1](https://github.com/Nagisa0803/archive-bridge/releases/latest)**입니다. 매 로그인 전에 공식 일본 Google Play 최신 버전을 조회해 요청에 적용하며 실패 시 이전 버전을 재사용하지 않습니다. 다운그레이드나 새 프로토콜 메이저에서는 인증 전 중단하고 같은 메이저에서도 응답 검증을 유지합니다. 바이너리는 서명 및 Apple 공증이 없습니다. SHA256SUMS는 다운로드 무결성을 확인할 뿐 발행자 신원을 증명하지 않습니다. 시스템 전체 보안 기능을 끄지 마세요.

## 문제 해결과 개발

`UNSUPPORTED_APK`는 원본 지원 APK를 확인하세요. `TRANSFER_REJECTED`는 게임에 저장된 연동 설정을 확인하세요. `IDENTITY_MISMATCH`는 대상 계정이 일치하지 않아 읽기를 중단한 것이므로 멈추세요. `PROXY_FAILED/NETWORK_TIMEOUT`은 연결을 점검하고 새 인증 전에 저장된 ZIP부터 확인하세요. 로컬 접근이 거부되면 현재 실행 프로그램이 표시한 전체 URL을 다시 여세요.

자세한 오류표와 개발 명령은 [English README](README.md)를 참고하세요. Actions는 6개 네이티브 환경에서 오프라인 테스트, 공개 소스 검사, 컴파일된 실행 파일 자체 검사를 진행합니다. 전체 성공 후에만 버전과 체크섬을 게시하며 CI는 게임 계정으로 인증하지 않습니다.

[설계](docs/PRODUCT.md) · [변경 기록](CHANGELOG.md) · [안전한 보고](SECURITY.md) · [타사 고지](THIRD_PARTY_NOTICES.md)

AGPL-3.0-only. 게임 공식 프로젝트와 무관하며 APK나 게임 리소스를 배포하지 않습니다. Issue에는 버전, OS/CPU, 안전한 오류 코드만 기록하고 개인 ZIP이나 인증 정보는 첨부하지 마세요.
