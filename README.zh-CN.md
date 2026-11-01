# Archive Bridge

[English](README.md) · [Simplified Chinese](README.zh-CN.md) · [Japanese](README.ja.md) · [Korean](README.ko.md)

[Archive Lens](https://github.com/Nagisa0803/archive-lens) 的本地帐号采集端：运行原生程序，按浏览器向导生成本机 ZIP，再在查看器中本地导入。公开网站不接收帐号数据。

**[下载版本](https://github.com/Nagisa0803/archive-bridge/releases)** · **[在线查看器](https://archive-lens.chiyoda-site.workers.dev/)** · **[导出与导入指南](https://archive-lens.chiyoda-site.workers.dev/guide/?lang=zh)**


### 图片链接（v0.3.0）

本机向导默认勾选“包含图片链接”，可取消以跳过额外照片请求。明确同意采集后，仅查询帐号已存在照片的资源ID，每批最多50个；卡面使用已知通用预览地址，不猜测缺失链接，不下载图片文件。

ZIP新增 `image-links.json`、`image-links.csv`、`image-links.txt`、`photo-links.json`，并在 `account.json` 中保存对应关系，可直接导入Lens。照片链接可能过期或携带访问参数，请保持私密。覆盖信息分别记录缺失项；获得链接不等于已备份图片。新版整合采用合成数据回归，未重新进行真实帐号认证测试。



每次采集只保留**一个ZIP**：进行中的检查点不显示为可下载成品，结束后原子更新为最终结果；最终写入失败时保留恢复包。照片补采失败会显示警示及安全的HTTP/gRPC状态码，不把流程结束当成照片全部备份。仅瞬时照片读取错误允许一次重试及有界缩批，不重试引继认证。


## 下载和使用

每个版本在全部检查通过后发布六个原生包：Windows、macOS、Linux 各有 x64 和 ARM64。选择与系统及 CPU 同时匹配的文件，完整解压目录（保留 `_internal`）。无需安装 Python、ADB、Root、注入或改包。

| 平台 | x64 | ARM64 |
| --- | --- | --- |
| Windows | `windows-x64.zip`，面向 Windows 10/11 | `windows-arm64.zip`，Windows 11 ARM |
| Linux | `linux-x64.tar.gz`，Ubuntu 22.04 / glibc 2.35+ | `linux-arm64.tar.gz`，Ubuntu 24.04 / glibc 2.39+ |
| macOS | `macos-x64.tar.gz`，macOS 15 Intel 验证 | `macos-arm64.tar.gz`，macOS 15 Apple Silicon 验证 |

1. Windows 运行 `archive-bridge.exe`；Linux/macOS 运行 `./archive-bridge`。浏览器将自动打开本地向导；未自动打开时，使用终端显示的完整地址。
2. 选择自己的未修改 **日服安卓原版 APK/XAPK**（最大 512 MiB）。仅在本机提取公开认证项目配置，处理后删除临时包；重新启动后需再次配置。安装包不上传互联网，也不会修改游戏。
3. 在游戏中设置引继密码，在本地向导输入游戏引继 ID 和引继密码。不是 Google 或 Apple 密码，切勿发到聊天或 Issue。
4. 勾选本人帐号和明确授权后，点击“验证并导出 ZIP”。引继认证可能影响另一设备上的游戏会话。不会自动重试引继执行。
5. 查看进度。基础快照先原子保存，再读取补充引继记录；后续失败或取消都保留已完成 ZIP。取消在请求边界生效，进行中的请求可能等到超时。
6. 下载 ZIP，在 [Archive Lens](https://archive-lens.chiyoda-site.workers.dev/?lang=zh) 本地导入。采集端、查看器和指南均支持中英日韩，默认英语。

默认导出目录为可执行程序旁 `ArchiveBridgeData/exports`，向导显示实际路径。可用 `--data-dir "F:\PrivateArchive"` 指定目录，`--port 8794` 指定端口，`--no-browser` 关闭自动打开。网络高级设置可填 `http://host:port` 代理，留空直连；TLS 证书校验保持开启。

## 保存范围和隐私

ZIP 包含完整 `User/Get` JSON、原始 `raw/user.pb`、Master 响应、成功取得的引继列表、无凭据的采集记录和 SHA-256 清单，可直接导入 Lens。原始 protobuf 保留当前描述未解析的字段。

不包含密码、认证/刷新令牌、TLS 密钥、APK、设备恢复包、卡面、照片原图，也不保证独立消息/电话历史完整。每包声明真实覆盖，不能视为所有内容的完整备份。ZIP 本身包含私人帐号信息，请谨慎分享。

仅监听 127.0.0.1，启动票据、Host/Origin 校验及单任务互斥；凭据仅在进程内存，不承诺取证级内存擦除。无统计、后台采集、自动更新、证书安装、玩法修改、消费或任意接口控制台。支持的 APK 不代表自动兼容其他版本。

当前正式版为 **[v0.2.1](https://github.com/Nagisa0803/archive-bridge/releases/latest)**。每次登录前从官方日服 Google Play 获取最新版本并设置请求头，获取失败不沿用旧版本，不降级；跨协议大版本先停止认证。同一大版本也可能改变协议，仍保留响应校验。二进制未签名、未经过 Apple 公证；SHA256SUMS 只验证下载完整性，不证明发布者身份。不要关闭系统全局保护。

## 排错与开发

`UNSUPPORTED_APK`：选择正确原版包；`TRANSFER_REJECTED`：核对已保存的游戏引继配置；`IDENTITY_MISMATCH`：停止，目标身份不符且帐号读取被阻止；`PROXY_FAILED/NETWORK_TIMEOUT`：检查本机网络/代理，重试前先检查已保存包。访问拒绝时重开当前程序输出的完整本地地址。保存失败时指定可写目录。

详细错误表、开发命令和发布规则见 [English README](README.md)。GitHub Actions 对六平台运行离线测试、源码隐私检查和编译后二进制自测；全部成功后才发布版本和校验清单。CI 不使用游戏帐号或真实凭据。

[产品设计](docs/PRODUCT.md) · [更新记录](CHANGELOG.md) · [安全说明](SECURITY.md) · [第三方说明](THIRD_PARTY_NOTICES.md)

许可证：AGPL-3.0-only。非游戏官方项目，不分发游戏安装包或资源。提交 Issue 仅提供版本、系统/架构、安全错误码，不附帐号包或私密资料。
