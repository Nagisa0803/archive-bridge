const COPY = {
  photo_links: [
    "Reading owned photo URLs",
    "正在读取已有照片链接",
    "所持写真URLを取得中",
    "보유 사진 URL 읽는 중",
  ],
  imageLinks: [
    "Include card-preview links and owned photo original/thumbnail URLs. Adds read-only photo URL requests; does not download image files. Links are private and may expire.",
    "包含卡面预览和已有照片原图/缩略图链接。会增加只读照片链接请求，不下载图片文件。链接属于私密数据，可能失效。",
    "カードプレビューと所持写真の原本・サムネイルURLを含めます。写真URLの読み取りのみを追加し、画像本体はダウンロードしません。URLは非公開情報で、期限切れになる場合があります。",
    "카드 미리보기와 보유 사진 원본/썸네일 URL을 포함합니다. 읽기 전용 사진 URL 요청만 추가하며 이미지 파일은 받지 않습니다. 링크는 비공개 정보이며 만료될 수 있습니다.",
  ],
  title: [
    "Your account, in your own archive.",
    "把帐号，保存在自己手中。",
    "アカウントを、自分のアーカイブへ。",
    "내 계정을 나만의 아카이브로.",
  ],
  lead: [
    "Create a portable account ZIP on this computer, then explore it privately in Archive Lens. Nothing is sent to the viewer website.",
    "在本机生成可携带的帐号 ZIP，再用 Archive Lens 私密查看。帐号数据不会发送到查看器网站。",
    "このPCで持ち運べるアカウントZIPを作成し、Archive Lensでローカル閲覧できます。閲覧サイトへアカウントデータは送信されません。",
    "이 컴퓨터에서 계정 ZIP을 만들고 Archive Lens에서 비공개로 확인하세요. 뷰어 웹사이트로 계정 데이터를 전송하지 않습니다.",
  ],
  step1: [
    "1 · Choose original APK",
    "1 · 选择原版安装包",
    "1 · 元のAPKを選択",
    "1 · 원본 APK 선택",
  ],
  step2: [
    "2 · Authenticate your account",
    "2 · 验证自己的帐号",
    "2 · 自分のアカウントを認証",
    "2 · 본인 계정 인증",
  ],
  step3: [
    "3 · Save ZIP and open Lens",
    "3 · 保存 ZIP 并打开 Lens",
    "3 · ZIPを保存してLensを開く",
    "3 · ZIP 저장 후 Lens 열기",
  ],
  setup: ["Compatibility setup", "兼容性设置", "互換性設定", "호환성 설정"],
  apkHint: [
    "Choose your own unmodified Japanese Android 6.1.0 APK or XAPK (up to 512 MiB). Only its public authentication project configuration is read. The uploaded package is deleted after processing; setup is required again after restarting Bridge.",
    "选择自己的未修改日服安卓 6.1.0 APK 或 XAPK（最大 512 MiB）。仅提取公开认证项目配置，处理后删除临时安装包；重新启动采集端后需再次设置。",
    "未改変の日本版Android 6.1.0 APK/XAPK（最大512 MiB）を選択してください。公開認証プロジェクト設定のみ読み取り、一時パッケージは処理後に削除します。再起動時は再設定が必要です。",
    "수정하지 않은 일본판 Android 6.1.0 APK/XAPK(최대 512 MiB)를 선택하세요. 공개 인증 프로젝트 설정만 읽으며 처리 후 임시 패키지를 삭제합니다. 재시작하면 다시 설정해야 합니다.",
  ],
  choose: [
    "Choose APK / XAPK",
    "选择 APK / XAPK",
    "APK / XAPKを選択",
    "APK / XAPK 선택",
  ],
  ready: [
    "✓ Supported package configured",
    "✓ 支持的安装包已配置",
    "✓ 対応パッケージを設定済み",
    "✓ 지원 패키지 설정 완료",
  ],
  notReady: [
    "No package configured yet",
    "尚未配置安装包",
    "パッケージ未設定",
    "아직 패키지를 설정하지 않았습니다",
  ],
  uploading: [
    "Reading package locally…",
    "正在本机读取安装包…",
    "パッケージをローカルで読み取り中…",
    "로컬에서 패키지를 읽는 중…",
  ],
  account: [
    "Account transfer login",
    "帐号引继登录",
    "アカウント連携ログイン",
    "계정 연동 로그인",
  ],
  id: ["Game transfer ID", "游戏引继 ID", "ゲームのユーザーID", "게임 연동 ID"],
  password: [
    "Game transfer password",
    "游戏引继密码",
    "ゲームの連携パスワード",
    "게임 연동 비밀번호",
  ],
  advanced: [
    "Advanced network settings",
    "高级网络设置",
    "ネットワーク詳細設定",
    "고급 네트워크 설정",
  ],
  proxy: [
    "Optional HTTP proxy (blank = direct connection)",
    "可选 HTTP 代理（留空则直连）",
    "HTTPプロキシ（空欄は直接接続）",
    "HTTP 프록시(비워 두면 직접 연결)",
  ],
  consent: [
    "This is my account. I explicitly authorize one official transfer authentication and necessary read-only data requests. Signing in can affect the game session on another device.",
    "这是我的帐号。我明确允许进行一次官方引继认证及必要只读请求。登录可能影响其他设备上的游戏会话。",
    "これは自分のアカウントです。公式の連携認証1回と必要な読み取りリクエストを許可します。他の端末のゲームセッションに影響する場合があります。",
    "본인 계정이며 공식 연동 인증 1회와 필요한 읽기 요청을 명시적으로 허용합니다. 다른 기기의 게임 세션에 영향을 줄 수 있습니다.",
  ],
  collect: [
    "Authenticate and export ZIP",
    "验证并导出 ZIP",
    "認証してZIPを作成",
    "인증 후 ZIP 내보내기",
  ],
  progress: [
    "Collection progress",
    "采集进度",
    "取得の進行状況",
    "수집 진행 상황",
  ],
  saved: [
    "Saved on this computer",
    "已保存在本机",
    "このPCに保存済み",
    "이 컴퓨터에 저장됨",
  ],
  cancel: [
    "Cancel remaining reads",
    "取消后续读取",
    "残りの取得をキャンセル",
    "남은 읽기 취소",
  ],
  privacyTitle: [
    "Private by design",
    "隐私边界清晰",
    "プライバシーを重視",
    "개인정보 보호 설계",
  ],
  privacy: [
    "Entered transfer passwords and authentication responses are excluded from archives and logs. Complete account responses may contain personal or unknown fields. Backups are private, not anonymized.",
    "输入的引继密码和认证响应不写入档案或日志。完整帐号响应可能含个人资料及未知字段；备份是私密数据，并未匿名化。",
    "入力した連携パスワードや認証応答はアーカイブやログへ保存しません。完全なアカウント応答には個人情報や未知フィールドが含まれ得ます。非公開バックアップであり匿名化ではありません。",
    "입력한 연동 비밀번호와 인증 응답은 아카이브나 로그에 저장하지 않습니다. 전체 계정 응답에는 개인정보나 알 수 없는 필드가 있을 수 있습니다. 비공개 백업이며 익명화하지 않았습니다。",
  ],
  coverage: [
    "This release preserves the complete User/Get response and original protobuf. Photo originals and independent message/phone histories are not a proven complete backup. Each ZIP states its actual coverage.",
    "此版本保存完整 User/Get 返回与原始 protobuf。照片原图及独立消息、电话历史尚未证明完整备份。每个 ZIP 都声明实际覆盖范围。",
    "User/Get全応答と元のprotobufを保存します。写真原本や独立したメッセージ・通話履歴の完全取得は未保証です。ZIPに実際の取得範囲を明記します。",
    "User/Get 전체 응답과 원본 protobuf를 보존합니다. 사진 원본 및 별도 메시지·전화 기록의 완전한 백업은 보장되지 않습니다. ZIP마다 실제 범위를 기록합니다.",
  ],
  viewer: [
    "Open Archive Lens ↗",
    "打开 Archive Lens ↗",
    "Archive Lensを開く ↗",
    "Archive Lens 열기 ↗",
  ],
  guide: [
    "Read the export and import guide ↗",
    "查看导出和导入指南 ↗",
    "エクスポート・インポートガイド ↗",
    "내보내기 및 가져오기 가이드 ↗",
  ],
  download: ["Download ZIP", "下载 ZIP", "ZIPをダウンロード", "ZIP 다운로드"],
  none: [
    "No saved archives yet.",
    "还没有保存的档案。",
    "保存済みアーカイブはありません。",
    "저장된 아카이브가 없습니다.",
  ],
  idle: [
    "Ready when you are",
    "准备就绪，等待操作",
    "操作をお待ちしています",
    "준비되었습니다",
  ],
  configure: [
    "Configuring compatibility",
    "正在配置兼容性",
    "互換性を設定中",
    "호환성 설정 중",
  ],
  verify: [
    "Verifying transfer target",
    "正在核对引继目标",
    "連携先を確認中",
    "연동 대상 확인 중",
  ],
  transfer: [
    "Executing authorized transfer once",
    "正在执行一次已授权引继",
    "許可された連携を1回実行中",
    "허용된 연동 1회 실행 중",
  ],
  login: [
    "Verifying authenticated account identity",
    "正在核对认证身份",
    "認証アカウントを照合中",
    "인증 계정 확인 중",
  ],
  master: [
    "Reading compatible master information",
    "正在读取主数据版本",
    "マスターバージョンを取得中",
    "마스터 버전 읽는 중",
  ],
  readAccount: [
    "Reading account snapshot",
    "正在读取帐号快照",
    "アカウントスナップショットを取得中",
    "계정 스냅샷 읽는 중",
  ],
  save: [
    "Saving and verifying ZIP",
    "正在保存并验证 ZIP",
    "ZIPを保存・検証中",
    "ZIP 저장 및 검증 중",
  ],
  supplemental: [
    "Core snapshot saved; reading migration metadata",
    "基础快照已保存，正在读取引继记录",
    "基本スナップショット保存済み・連携情報を取得中",
    "기본 스냅샷 저장 완료, 연동 정보 읽는 중",
  ],
  done: ["Export complete", "导出完成", "エクスポート完了", "내보내기 완료"],
  completeNote: [
    "Archive saved. Open Lens and import the downloaded ZIP locally.",
    "档案已保存。请打开 Lens，在本地导入下载的 ZIP。",
    "保存しました。Lensを開き、ダウンロードしたZIPをローカルで読み込んでください。",
    "아카이브를 저장했습니다. Lens에서 다운로드한 ZIP을 로컬로 가져오세요.",
  ],
  requestFailed: [
    "Local request failed. Reopen the application URL and try again.",
    "本地请求失败，请重新打开本次启动显示的地址。",
    "ローカルリクエストに失敗しました。起動時に表示されたURLを開き直してください。",
    "로컬 요청에 실패했습니다. 실행 시 표시된 URL을 다시 여세요.",
  ],
  missingToken: [
    "Reopen the original private startup link. For a manual link, restart Bridge with --no-browser; do not share it.",
    "请以 --no-browser 重启获取私密链接，勿分享。",
    "--no-browser で再起動して非公開リンクを取得し、共有しないでください。",
    "--no-browser로 다시 시작하고 비공개 링크를 공유하지 마세요。",
  ],
};
Object.assign(COPY, {
  versionCheck: [
    "Checking latest official Android version",
    "正在检查官方最新安卓版本",
    "最新の公式Androidバージョンを確認中",
    "최신 공식 Android 버전 확인 중",
  ],
  apkHint: [
    "Choose your original Japanese Android APK or XAPK (up to 512 MiB). Its package and version are detected locally. Before each sign-in, Bridge reads the latest official Google Play version and uses it for requests; unavailable metadata or a new protocol major stops sign-in. The temporary upload is deleted after processing.",
    "选择自己的日服原版安卓 APK 或 XAPK（最大 512 MiB），本机自动识别包名和版本。每次登录前读取官方 Google Play 最新版本并用于请求；获取失败或跨协议大版本会停止登录。处理后删除临时安装包。",
    "日本版Androidの元のAPK/XAPK（最大512 MiB）を選択。パッケージ名とバージョンをローカルで検出し、ログイン前に毎回公式Google Playの最新版を取得してリクエストに使用します。取得失敗や新しいプロトコルメジャーでは認証を停止します。一時ファイルは処理後に削除します。",
    "일본판 원본 Android APK/XAPK(최대 512 MiB)를 선택하세요. 패키지와 버전을 로컬에서 감지하고 매 로그인 전에 공식 Google Play 최신 버전을 요청에 적용합니다. 조회 실패나 새 프로토콜 메이저에서는 인증을 중단합니다. 처리 후 임시 파일을 삭제합니다.",
  ],
  detectedVersion: [
    "Request version / APK",
    "请求版本 / 安装包版本",
    "リクエスト / APKバージョン",
    "요청 버전 / APK",
  ],
  versionPending: [
    "Latest version will be checked before sign-in.",
    "登录前将自动检查最新版本。",
    "ログイン前に最新版を自動確認します。",
    "로그인 전에 최신 버전을 자동 확인합니다。",
  ],
});
const $ = (s) => document.querySelector(s),
  languages = { en: 0, zh: 1, ja: 2, ko: 3 };
let lang = "en",
  state = null,
  busy = false,
  lastList = "",
  noticeKey = "";
const token = location.hash.slice(1);
if (token) history.replaceState(null, "", location.pathname + location.search);
const t = (key) => (COPY[key] || COPY.requestFailed)[languages[lang]];
function notice(text, error = false) {
  $("#notice").textContent = text;
  $("#notice").classList.toggle("error", error);
}
async function api(path, body, raw = false) {
  const response = await fetch(path, {
    method: body === undefined ? "GET" : "POST",
    headers: {
      "X-Bridge-Token": token,
      ...(raw ? {} : { "Content-Type": "application/json" }),
    },
    body: body === undefined ? undefined : raw ? body : JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) {
    const e = Error(data.error?.message || t("requestFailed"));
    e.code = data.error?.code;
    throw e;
  }
  return data;
}
function apply() {
  document.documentElement.lang = lang === "zh" ? "zh-CN" : lang;
  for (const e of document.querySelectorAll("[data-i]"))
    e.textContent = t(e.dataset.i);
  render();
  if (noticeKey) notice(t(noticeKey));
}
function render() {
  if (!state) return;
  const job = state.job;
  $("#version").textContent = "v" + state.version + " · " + state.compatibility;
  $("#output").textContent = state.outputDirectory;
  $("#profile").textContent = t(
    busy ? "uploading" : state.profileReady ? "ready" : "notReady",
  );
  $("#collect").disabled =
    busy || job.status === "running" || !state.profileReady;
  $("#apk").disabled = busy || job.status === "running";
  $("#cancel").hidden = job.status !== "running";
  $("#stage").textContent =
    t(
      job.stage === "account"
        ? "readAccount"
        : job.stage === "version"
          ? "versionCheck"
          : job.stage,
    ) +
    " · " +
    job.percent +
    "%";
  $("#progress").value = job.percent;
  $("#game-version").textContent = job.versionInfo
    ? t("detectedVersion") +
      ": " +
      job.versionInfo.appVersion +
      " / " +
      job.versionInfo.apkVersion
    : t("versionPending");
  if (job.error) notice(job.error.code + " · " + job.error.message, true);
  else if (job.status === "complete") {
    noticeKey = "completeNote";
    notice(t(noticeKey));
  }
  const signature = JSON.stringify(state.backups) + lang;
  if (lastList === signature) return;
  lastList = signature;
  const area = $("#backups");
  area.replaceChildren();
  if (!state.backups.length) {
    const p = document.createElement("p");
    p.textContent = t("none");
    area.append(p);
  }
  for (const file of state.backups) {
    const row = document.createElement("div");
    row.className = "backup";
    const label = document.createElement("div");
    label.textContent =
      file.filename + " · " + (file.bytes / 1024 / 1024).toFixed(2) + " MiB";
    const button = document.createElement("button");
    button.textContent = t("download");
    button.addEventListener("click", async () => {
      try {
        button.disabled = true;
        const response = await fetch(
          "/api/export/" + encodeURIComponent(file.filename),
          { headers: { "X-Bridge-Token": token } },
        );
        if (!response.ok) throw Error(t("requestFailed"));
        const blob = await response.blob(),
          url = URL.createObjectURL(blob),
          a = document.createElement("a");
        a.href = url;
        a.download = file.filename;
        a.click();
        setTimeout(() => URL.revokeObjectURL(url), 5000);
      } catch (e) {
        notice(e.message, true);
      } finally {
        button.disabled = false;
      }
    });
    row.append(label, button);
    area.append(row);
  }
}
$("#language").addEventListener("change", () => {
  lang = $("#language").value;
  apply();
});
$("#apk").addEventListener("change", async () => {
  const file = $("#apk").files[0];
  if (!file) return;
  busy = true;
  noticeKey = "";
  notice("");
  render();
  try {
    await api("/api/profile", file, true);
    state = await api("/api/state");
  } catch (e) {
    notice(e.message, true);
  } finally {
    busy = false;
    $("#apk").value = "";
    render();
  }
});
$("#form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const values = {
    transferId: $("#uid").value.trim(),
    password: $("#password").value,
    proxy: $("#proxy").value.trim(),
    confirm: $("#confirm").checked,
    includeImageLinks: $("#image-links").checked,
  };
  $("#password").value = "";
  noticeKey = "";
  notice("");
  busy = true;
  render();
  try {
    await api("/api/collect", values);
    state = await api("/api/state");
  } catch (error) {
    notice((error.code ? error.code + " · " : "") + error.message, true);
  } finally {
    values.password = "";
    busy = false;
    render();
  }
});
$("#cancel").addEventListener("click", async () => {
  try {
    await api("/api/cancel");
  } catch (e) {
    notice(e.message, true);
  }
});
async function poll() {
  try {
    state = await api("/api/state");
    render();
  } catch (e) {
    notice(e.message, true);
  } finally {
    setTimeout(poll, 1200);
  }
}
apply();
if (token) poll();
else notice(t("missingToken"), true);
