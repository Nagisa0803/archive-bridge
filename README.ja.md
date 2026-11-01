# Archive Bridge

[English](README.md) · [Simplified Chinese](README.zh-CN.md) · [Japanese](README.ja.md) · [Korean](README.ko.md)

[Archive Lens](https://github.com/Nagisa0803/archive-lens) 用のローカルアカウント取得ツールです。ネイティブアプリとブラウザーの手順に従ってPCにZIPを保存し、閲覧サイトではローカルに読み込みます。公開サイトへアカウントデータを送信しません。

**[ダウンロード](https://github.com/Nagisa0803/archive-bridge/releases)** · **[閲覧サイト](https://archive-lens.chiyoda-site.workers.dev/)** · **[利用ガイド](https://archive-lens.chiyoda-site.workers.dev/guide/?lang=ja)**

## ダウンロードと初回利用

Windows・macOS・Linuxそれぞれにx64とARM64のネイティブ版を公開します。OSとCPUの両方に合うファイルを選び、`_internal` を含むディレクトリ全体を展開してください。Python、ADB、root、注入、APK改変は不要です。

| OS | x64 | ARM64 |
| --- | --- | --- |
| Windows | `windows-x64.zip`、Windows 10/11向け | `windows-arm64.zip`、Windows 11 ARM |
| Linux | `linux-x64.tar.gz`、Ubuntu 22.04 / glibc 2.35+ | `linux-arm64.tar.gz`、Ubuntu 24.04 / glibc 2.39+ |
| macOS | `macos-x64.tar.gz`、macOS 15 Intelで確認 | `macos-arm64.tar.gz`、macOS 15 Apple Siliconで確認 |

1. Windowsでは `archive-bridge.exe`、Linux/macOSでは `./archive-bridge` を起動します。ローカルの案内画面が自動で開きます。開かない場合は端末に表示された完全なURLを使用します。
2. 自分の未改変 **日本版Androidの元のAPK/XAPK**（最大512 MiB）を選択します。公開認証プロジェクト設定のみローカルで読み取り、一時ファイルは削除します。再起動時は再設定が必要です。APKをインターネットへ送信せず、ゲームも変更しません。
3. ゲームで連携パスワードを設定し、ユーザーIDと連携パスワードをローカル画面に入力します。Google/Appleのパスワードではありません。チャットやIssueへ投稿しないでください。
4. 自分のアカウントであることと認証・必要な読み取りを許可し、認証・ZIP作成を1回実行します。他端末のゲームセッションに影響する場合があります。連携実行を自動再試行しません。
5. 進行状況を確認します。基本スナップショットを先に保存してから補足情報を読み取るため、後続の失敗やキャンセルでも完成済みZIPは残ります。キャンセルはリクエストの境界で反映されます。
6. ZIPをダウンロードし、[Archive Lens](https://archive-lens.chiyoda-site.workers.dev/?lang=ja) にローカルで読み込みます。ツール・閲覧画面・ガイドは英中日韓対応、初期言語は英語です。

保存先は通常、実行ファイル横の `ArchiveBridgeData/exports` です。実際のパスを画面に表示します。`--data-dir /private/path`、`--port 8794`、`--no-browser` で変更できます。任意のHTTPプロキシは `http://host:port`、空欄は直接接続です。TLS証明書検証を維持します。

## 保存範囲とプライバシー

ZIPにはUser/Get全JSONと元のprotobuf、Master応答、取得できた連携一覧、認証情報を含まない取得記録、SHA-256一覧を保存します。元のprotobufは現在未解釈のフィールドも保持し、Lensに直接インポートできます。

パスワード、認証・更新トークン、TLS秘密情報、APK、端末復元データ、カード画像、写真原本は含みません。独立したメッセージ・通話履歴の完全性も未保証です。ZIPごとに取得範囲を明記し、全内容の完全バックアップとは称しません。ZIP自体は個人情報を含みます。

127.0.0.1のみで待ち受け、起動ごとのアクセス票、Host/Origin確認、単一ジョブ制御を使用します。認証情報はプロセスメモリ内のみで、取証レベルの消去は保証しません。解析送信、バックグラウンド取得、自動更新、証明書変更、ゲーム操作・購入、任意RPC呼び出しはありません。

正式版は **[v0.2.1](https://github.com/Nagisa0803/archive-bridge/releases/latest)**。ログイン前に毎回公式日本版Google Playの最新版を取得し、リクエストへ適用します。取得失敗時に旧版へフォールバックせず、ダウングレードや新しいプロトコルメジャーでは認証前に停止します。同一メジャーでも応答検証を維持します。バイナリは未署名・Apple未公証です。SHA256SUMSは完全性確認であり発行元の証明ではありません。システム全体の保護を無効にしないでください。

## 問題解決と開発

`UNSUPPORTED_APK` は元の対応APKを確認、`TRANSFER_REJECTED` は保存済みの連携設定を確認します。`IDENTITY_MISMATCH` は停止してください。アカウント読取前に不一致を検出しています。`PROXY_FAILED/NETWORK_TIMEOUT` は接続を確認し、新しい認証の前に既存ZIPを確認します。ローカルアクセス拒否時は今回の完全URLを開き直します。

開発手順と詳細は [English README](README.md) を参照してください。Actionsは6種類のネイティブ環境でオフライン試験・公開ソース検査・ビルド後セルフテストを行い、すべて合格したタグのみ公開します。CIでゲームへ認証しません。

[設計](docs/PRODUCT.md) · [変更履歴](CHANGELOG.md) · [安全な報告](SECURITY.md) · [第三者表記](THIRD_PARTY_NOTICES.md)

AGPL-3.0-only。ゲーム公式とは無関係で、APKやゲーム素材は配布しません。Issueにはバージョン、OS/CPU、安全なエラーコードのみを添え、個人アーカイブや認証情報は含めないでください。
