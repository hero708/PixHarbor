# Prixiv_View 实施方案（方案1：基于 PixLume 二次开发）

> 文档状态：**待评审** ｜ 编写日期：2026-11-21
> 工作区：`D:\WorkSpace\HarmonyApp\Prixiv_View`
> 上游基线：[SYTKILLER/PixLume](https://github.com/SYTKILLER/PixLume) v1.2.0（versionCode 1002000），已克隆到 `reference/PixLume`（浅克隆 depth 1）

---

## 1. 方案概述

**一句话**：以 GPL-3.0 开源的鸿蒙原生 Pixiv 客户端 PixLume 为代码基线，通过"基线跑通 → 工程初始化 → 更名换牌 → 性能优化 → 定制扩展 → 构建发布"六个阶段，把它改造成你自己的原生应用 **Prixiv_View**。

| 决策项 | 结论 | 依据 |
|---|---|---|
| 技术路线 | ArkTS / ArkUI 原生（HarmonyOS NEXT） | 流畅度上限最高：无 WebView 中间层，`WaterFlow` 原生瀑布流 + ImageKnifePro 图片管线 |
| 代码基线 | PixLume v1.2.0 | 功能完整度超预期（登录/推荐/排行/搜索/收藏/关注/下载/小说/桌面卡片全都有），最难的技术点已全部趟平 |
| 许可证 | **GPL-3.0（强制）** | 复用 GPL 代码的衍生作品必须同样以 GPL-3.0 开源；个人使用/学习无负担，**不可闭源商用** |
| API 版本 | HarmonyOS 6.1.1（API 24），target = compatible = 24 | 上游 `build-profile.json5` 实测；设备系统低于 6.1.1 无法安装 |
| 开发环境 | DevEco Studio 6.1+ | ✅ 你已确认安装 |
| 首个定制版预计工作量 | 约 1 周（P0~P2 + P4 最小集） | 见第 9 节里程碑 |

**性能预期（诚实版）**：原生方案的优势在滑动跟手度、长列表内存、冷启动、系统级动画；**图片下载速度取决于网络/代理/图床镜像，与方案无关**。PixLume 已内置"直连模式"应对国内 DNS 污染，这是网络侧的关键保障。

---

## 2. 为什么选 PixLume 做基线

### 2.1 功能清单（上游 README + 源码核实）

- **登录**：账号密码、Refresh Token、Web OAuth（PKCE）三种方式，Token 自动刷新
- **浏览**：推荐流、日/周/月排行榜、搜索（关键词/标签、多图识别）、猜你喜欢、关注画师作品流
- **互动**：公开/私密收藏 + 自定义标签、信息流内收藏角标即时刷新、公开/私密关注、评论
- **沉浸式**：大图预览（手势缩放）、动图（ugoira）原生播放、暗色模式、小说阅读器 + 系列页
- **本地**：下载管理（动图自动转码 GIF 存相册）、小说导出 TXT、插画/小说历史记录、搜索历史
- **工具**：关键词自动译文、关键词收藏/屏蔽管理、分享格式自定义、桌面卡片（PixCard）、智感握姿（悬浮按钮随左右手换边）
- **网络**：直连模式启动自动探测切换，接口/图片/下载三链路全覆盖

### 2.2 性能相关的现成实现

| 机制 | 实现位置 | 说明 |
|---|---|---|
| 原生瀑布流 | `entry/src/main/ets/components/WaterFlowView.ets` | `WaterFlow` + 断点响应式列数 + `onReachEnd` 加载更多 + 弹簧边缘效果 |
| 图片缓存/降采样 | `entry/src/main/ets/components/PixivImage.ets` | `@ohos/imageknifepro` 的 `ImageKnifeComponent` + `DownSamplingStrategy`（按显示尺寸解码，省内存） |
| 画质分级 | `entry/src/main/ets/common/utils/ImageUtils.ts` | `getImageUrlByQuality()` 按设置选预览画质；图床可换 `i.pixiv.re` / `i.pixiv.cat` 镜像 |
| 请求缓存/去重 | `entry/src/main/ets/services/PixivService.ts` | 针对详情页 Swiper 重建子组件重复请求的问题已有缓存层 |
| 直连/DNS | `common/utils/HostMap.ts`、`DoHClient.ts`、`HostRefresher.ts`、`network/NetworkModeManager.ets` | 硬编码 IP 绕过 DNS 污染（节点方案源自 Pixiv-Shaft）+ 阿里 DoH + 启动探测自动切换 + IP 刷新器 |
| 防盗链 | `common/utils/BypassUrlRewriter.ts`、`network/DirectDownloader.ets` | 给 `pximg.net` 请求自动加 `Referer: https://www.pixiv.net/` |
| 动图缓存 | `common/utils/UgoiraCache.ets`、`components/UgoiraPlayer.ets` | ugoira 帧缓存与原生播放 |
| 本地数据库 | `common/utils/database/`（自研轻量 ORM + 装饰器）+ 5 个 DAO | 下载记录/插画历史/小说历史/搜索历史/标签收藏，KV Store 持久化 |

### 2.3 血缘与致谢（GPL 合规需要保留）

PixLume ← 前身 [XHXYT/Pixark](https://github.com/XHXYT/Pixark)；直连节点方案 ← [CeuiLiSA/Pixiv-Shaft](https://github.com/CeuiLiSA/Pixiv-Shaft)；架构参考 ← [Notsfsssf/pixez-flutter](https://github.com/Notsfsssf/pixez-flutter)；协议签名参考 ← [upbit/pixivpy](https://github.com/upbit/pixivpy)；应用图标设计：March（SYTKILLER）。

### 2.4 第二参考源：pixiv-viewer / pixiv-viewer-app（借功能，不借代码）

> 2026-11-21 增补：应用户要求，对 [asadahimeka/pixiv-viewer](https://github.com/asadahimeka/pixiv-viewer)（Vue 网页版，AGPL-3.0）及其客户端壳 [pixiv-viewer-app](https://github.com/asadahimeka/pixiv-viewer-app)（Capacitor/Tauri，AGPL-3.0）做了逐项功能对照（官方 Features.zh-CN.md + PixLume 源码 grep 实测）。

**许可证边界（先读）**：这两个项目均为 **AGPL-3.0**，与本项目 GPL-3.0 基线**不能直接混抄代码**——GPLv3 §13 虽允许与 AGPLv3 代码组合，但组合整体将受 AGPL 网络条款约束，许可证复杂化。因此借鉴规则是：**只借功能定义、交互设计、API 端点知识（思想与事实不受版权保护），不复制任何代码**。例如以图搜图可按 SauceNAO 公开 API 文档用 ArkTS 自行实现，保持 Prixiv_View 纯 GPL-3.0。

**实测：多数功能 PixLume 已覆盖，不必重复造轮子**——特辑推荐（`PixivData.ts:751` `/v1/spotlight/articles` + `components/BannerView.ets`）、搜索智能补全（`/v2/search/autocomplete` + `common/entity/SearchSuggestion.ts`，含作品/用户 **ID 直达**）、热门预览（`SearchViewModel.ets:212` 合并 popular-preview）、长按手势（搜索/历史/图片/详情均有 `LongPressGesture`）、导出 Token（`view/user/AccountInfo.ets:133`）、本地数据库备份/还原（`KVdbUtil.ts:595`）、图床镜像切换、AI 作品过滤（`search_ai_type`）、深色模式。

**真实差距 = 借鉴清单**（按建议优先级）：

| # | 功能 | pixiv-viewer 的实现 | PixLume 现状（实测） | 借鉴动作 |
|---|---|---|---|---|
| 1 | **以图搜图** | SauceNAO 上传图片搜相似作品 | **TODO 占位**：`pages/Search.ets:78` toast "开发中-以图搜图" | 按 SauceNAO 公开 API 用 ArkTS 自研（选图→上传→结果流），正好补上已有入口 |
| 2 | 随便看看 / 发现 | 随机优质作品 + 全站最新 | 未见 | 官方 App API 有对应端点，新增页面 |
| 3 | 历史排行 | 按日期回看排行榜 | 仅日/周/月（date 参数待核实） | rank 接口补 date 参数 + 日期选择器 |
| 4 | 珍藏册 | 官方 collections 浏览 | 未见 | 对接官方珍藏册 API |
| 5 | 动图多格式导出 | ZIP/GIF/WebM/APNG/MP4/AVIF | 仅 GIF | 借格式矩阵；鸿蒙侧用 AVCodec 原生编码，先补 WebM/ZIP |
| 6 | 小说多格式导出 | TXT/HTML/Markdown/DOC/PDF/EPUB | 仅 TXT（`DownloadsViewModel.ets:775`） | EPUB（zip+xhtml）/HTML/Markdown 纯 ArkTS 可实现 |
| 7 | 设置/历史云同步 | PBKDF2+AES 加密、冲突检测与智能合并 | 仅本地备份 | 借加密与合并**设计**；传输层用用户自有 WebDAV 或自建服务端 |
| 8 | 漫画翻译 | ONNX Runtime Web 本地 OCR+图像修复 + LLM 排版 | 无（仅关键词译文） | 远期项：鸿蒙可走 MindSpore Lite/NNRt 或 Web 组件跑 ONNX；成本高，单独立项 |
| 9 | 多语言 | 14 种语言 | 仅 base 中文一套资源 | 借资源目录结构（base/zh_CN/en_US/ja_JP），文案逐步翻译 |
| 10 | Cookie 登录 | PHPSESSID（官方亦不推荐） | 无 | 低优先级，有安全风险，不建议做 |

**明确不借鉴的部分（架构级）**：
- 其 API 层依赖 **HibiAPI / PixivNow 中转实例**（"自定义 API 实例 / AppAPI 代理模式"）——PixLume 的**直连官方 App API + 静态 IP** 架构更优（无第三方中转、隐私更好、少一个故障点），保持不变。
- Capacitor（Android/iOS）/ Tauri（桌面）打包层对鸿蒙无借鉴价值，ArkUI 原生即替代物。
- Vant UI 的移动端交互模式（下拉刷新、骨架屏、长按菜单、底部动作条）可作 **UX 参考**，用 ArkUI 原生组件实现。

---

## 3. GPL-3.0 合规要求（必读）

复用 PixLume 代码后，你的 Prixiv_View **必须**：

1. **整体以 GPL-3.0 开源**：发布 HAP 安装包时，必须同时提供完整对应源码（含构建脚本），或提供明确的源码获取渠道。
2. **保留上游 LICENSE 与版权声明**：不得删除文件头版权注释、LICENSE 文件。
3. **声明修改**：改过的文件要注明"被你修改过 + 修改日期"（git 提交历史本身即可满足大部分举证，建议在 NOTICE 中说明）。
4. **署名致谢**：保留对 PixLume / Pixark / Shaft / Pixez / PixivPy 的致谢链。
5. **图标版权单独注意**：上游图标由 March 设计，虽在 GPL 仓库内，**建议换成自制图标**避免品牌混淆（也符合商标惯例：改名换牌不要沿用原图标）。

**实操清单**（P1 阶段执行）：
- [ ] 根目录保留上游 `LICENSE`（GPL-3.0 全文）
- [ ] 新增 `NOTICE.md`：本项目基于 PixLume v1.2.0（© SYTKILLER/March，GPL-3.0）二次开发；前身 Pixark（© XHXYT）；致谢 Shaft/Pixez/PixivPy；列出主要修改
- [ ] 重写 `README.md`：项目定位、与上游的关系、构建方法、许可证声明
- [ ] 源码公开仓库（GitHub 或 Gitee）与 HAP 发布渠道绑定
- [ ] ⚠️ 若未来想**闭源商用**：GPL 代码不可用，只能走方案2（从零自研、只参考思路），届时需重写全部实现

---

## 4. 环境与前置条件

| 项 | 要求 | 状态 |
|---|---|---|
| DevEco Studio | 6.1+ | ✅ 已安装（你已确认） |
| HarmonyOS SDK | 6.1.1（API 24），DevEco 内下载 | ⬜ 首次打开工程时按 IDE 提示安装 |
| ohpm 依赖 | `@ohos/axios ^2.2.6`、`@kingtous/reqwest ^1.0.0`、`@ohos/imageknifepro ^1.0.10`、`@hmanimations/ezcustomtransition ^1.2.9`、`reflect-metadata 0.2.1` | ⬜ `ohpm install`（DevEco 打开工程会自动同步） |
| 运行设备 | HarmonyOS **6.1.1 及以上**真机（开发者模式 + USB 调试）或 API 24 模拟器 | ✅ 已实测（2026-11-21，hdc）：**HUAWEI Mate 80 Pro Max（SGT-AL10）**，HarmonyOS **7.0.0.111**，**API 26** ≥ 24，USB 调试已连接（序列号 5MT0225C11020636）；风险 R4 解除 |
| 签名 | 调试：DevEco 自动签名（需登录华为账号）；发布：AGC 申请发布证书 | ⬜ P0 阶段配置 |
| 网络 | 能访问 Pixiv（直连模式已内置，普通网络不可用时自动切换）；ohpm/GitHub 可达 | ✅ 手机已装自研 VPN **tunbox**（`com.tunbox.client`，hdc 实测）作兜底，详见 §5.4；⬜ 本机 GitHub 连接曾出现 reset，已用重试/浅克隆规避 |

---

## 5. 基线工程架构解析（实测）

### 5.1 工程配置要点

- `build-profile.json5`：单 product `default`，`targetSdkVersion = compatibleSdkVersion = "6.1.1(24)"`，`runtimeOS: HarmonyOS`，strictMode 开启 `caseSensitiveCheck` + `useNormalizedOHMUrl`；单模块 `entry`
- `AppScope/app.json5`：`bundleName: com.march.pixlume`，`vendor: march`，`versionCode: 1002000`，`versionName: 1.2.0`，图标 `$media:layered_image`（分层图标）
- `entry/src/main/module.json5`：
  - `deviceTypes`: phone / tablet / 2in1 / car / tv
  - 路由：`routerMap: $profile:route_map`（Navigation 路由表）+ `pages: $profile:main_pages`
  - 权限：`INTERNET`、`GET_NETWORK_INFO`、`DETECT_GESTURE`（智感握姿）
  - 扩展能力：`EntryBackupAbility`（备份恢复）、`PixCardFormAbility`（桌面卡片，`$profile:form_config`）
- 资源国际化：目前**只有 `base` 一套中文资源**（`entry/.../base/element/string.json` 约 1100 行），无 zh_CN/en_US 分目录

### 5.2 分层结构（MVVM）

```
pages/        页面入口（Tab 框架）：Index / Home / Rank / Trend / Search / Login / More
   │
view/         子页面与面板：IllustDetailPage / NovelDetailPage / NovelSeriesPage / CommentPanel / SearchingPage
   │            ├─ login/  WebLogin(PKCE) / TokenLogin / RegisterPage
   │            ├─ more/   UserSettings / DownloadManager / CollectionPage / FollowPage /
   │            │          PixHistory / KeywordManagerPage / AboutPage / AppData / SaveFormat / ShareFormat
   │            └─ user/   UserDetailPage / UserBookmarkPage / UserAccounts / AccountInfo
   │
viewmodel/    18 个 ViewModel（每页面一个）+ BaseDataSource（LazyForEach 的 IDataSource 实现）
   │
services/     PixivAuth.ts（OAuth/Token）/ PixivService.ts（业务聚合+缓存）/ PixivData.ts /
   │          PixivInteraction.ts（收藏/关注）/ PixivTypes.ts（类型）/ MockData.ets
   │
common/
   ├─ constants/   AppConstants（API 地址/Referer/RedirectURI）/ FunctionConstants / UIConstants
   ├─ entity/      18 个状态与模型：SettingsModel(appSettings) / BookmarkState / DownloadTask / …
   └─ utils/       30+ 工具：网络直连套件 / 图片 / DoH / MD5 / KVdb / 自研 database ORM /
                   persistence(@ObservedV2 持久化) / breakpoint(断点适配) / customtransition(转场)
components/   WaterFlowView / PixivImage / ImageViewer / UgoiraPlayer / BannerView / NaviContainer / …
entryability/ EntryAbility（入口+ImageKnife初始化）/ AppState（PixState 全局状态）
formability/  PixCardFormAbility + widget/pages/PixCard.ets（桌面卡片）
```

### 5.3 关键机制说明

1. **全局状态**：`entryability/AppState.ets` 的 `PixState`（页面边距/断点/底部安全区等）+ `common/entity/` 内 `@ObservedV2` 实体（如 `appSettings`、`bookmarkState`），配合 `Persistence.ets` 做持久化。
2. **网络三链路**：普通模式走系统网络；直连模式由 `NetworkModeManager` 启动探测（`DIRECT_PROBE_HOST = app-api.pixiv.net`），失败自动切换：API 请求用 `HostMap` 静态 IP + 适配器（`AxiosAdapter` / `ReqwestAdapter` / `RcpAxiosAdapter`），图片用 ImageKnifePro 的 `DnsOption/StaticDnsRuleItem` 静态 DNS，下载用 `DirectDownloader`（带 Referer）。
3. **登录**：`PixivAuth.ts` 直连官方 App API（`https://app-api.pixiv.net/`），OAuth 端点 `https://oauth.secure.pixiv.net/auth/token`，Web 登录 PKCE 回调 `https://app-api.pixiv.net/web/v1/users/auth/pixiv/callback`；**不依赖 HibiAPI 等第三方中转**。
4. **本地数据**：自研装饰器 ORM（`database/AutoTable.ts` + `decorator/Decorators.ts`）建表，5 个 DAO 管理下载记录/历史/标签收藏；偏好设置走 `PreferenceUtil` / KV Store。

### 5.4 网络可达性与 VPN 策略（回答"是否需要开 VPN"）

**结论：平时可以不开发 VPN；直连是尽力而为的优化，手机上的 tunbox 是可靠兜底，两者自动共存、互不冲突。**

实测设备环境（hdc，2026-11-21）：HUAWEI Mate 80 Pro Max（SGT-AL10），HarmonyOS 7.0.0.111 / API 26；已安装自研 VPN `com.tunbox.client`（tunbox）。

**三档网络策略**（`NetworkModeManager.ets`，设置项 `direct_connect_mode` = auto / off / on，默认 auto）：
1. **auto**：启动时两路并行探测（预算 ≤~2s）——普通网络（`app-api.pixiv.net` 域名解析）与直连候选 IP：
   - 普通可达 → **normal 模式**。tunbox 开启时流量走系统 VPN 隧道，此路必通 → auto 会优先用它，不启用直连 IP 规则；
   - 普通不可达（国内 DNS 污染）→ **direct 模式**：内置候选 IP（`HostMap.ts`：API/OAuth/www → 210.140.139.155~158 + Cloudflare 前置 172.64.145.x；图片 i/s.pximg.net → 210.140.139.129~133 等），API/下载走适配器，图片走 ImageKnifePro 静态 DNS；
   - 两路全失败 → 回退 normal 并 toast 提示 → **这是唯一需要开 tunbox 的场景**；开启后下次启动/重探测自动恢复。
2. **off**：强制普通模式（纯 VPN / 海外网络场景）。
3. **on**：强制直连（后台刷新候选 IP）。

**稳定性评估（分两层，如实说）**：
- **API 本身稳定**：`app-api.pixiv.net` 是 Pixiv 官方客户端在用的官方 App API，协议长期稳定（PixEz/Shaft/PixLume 生态都依赖它）。主要变量是账号风控（风险 R1），不是接口变动。
- **直连链路是"尽力而为"，不保证 100%**：候选 IP 硬编码（源自 Pixiv-Shaft），可用性随地区/运营商/时间变化；`HostMap.ts` 注释明确"IP 失效时探测会全部失败并自动回退普通模式，更新本表即可恢复直连" → **维护动作 = 跟随上游 PixLume / Pixiv-Shaft 更新 IP 表**（纳入 §8 上游同步策略）。旧"URL 换 IP + Host 头"方案因破坏 TLS/SNI 证书校验已废弃（`HostMap.ts:51`），现行方案保留域名 SNI。
- **图片链路另有备份**：i.pximg.net 被阻时可切换镜像图床 `i.pixiv.re` / `i.pixiv.cat`（`ImageUtils.ts`）。
- 有 tunbox 兜底后，整体可用性 = 直连（免 VPN、低延迟）+ VPN 兜底（可靠），体验优于"必须常开 VPN"。

---

## 6. 实施路线（P0 → P4）

### P0：基线跑通（0.5~1 天，需要你在 DevEco GUI 操作）

**目标**：未改一行代码，先确认 PixLume 在你的设备上完整可用。

1. DevEco Studio → Open → 选择 `D:\WorkSpace\HarmonyApp\Prixiv_View\reference\PixLume`
2. 等待 SDK/依赖同步（或终端 `ohpm install`）；按提示安装 API 24 SDK
3. `File → Project Structure → Signing Configs` → 勾选 **Automatically generate signature**（登录华为账号）
4. 连接真机（开发者模式+USB 调试）或启动 API 24 模拟器 → Run
5. **验收清单**：
   - [ ] 三种登录方式至少跑通一种（推荐 Web OAuth）
   - [ ] 推荐流瀑布流滑动流畅、加载更多正常
   - [ ] 插画详情大图/多图滑动、GIF 动图播放
   - [ ] 收藏/取消收藏、排行榜、搜索
   - [ ] 网络矩阵（详见 §5.4）：① tunbox 关闭 + 直连 auto → 能刷图（验证直连 IP 链路）；② tunbox 开启 + auto → 能刷图（验证 VPN 普通链路）；③ 直连 on 强制模式行为正常；④ 设置页可见当前生效模式/探测 IP
   - [ ] 下载一张图 + 一个动图（验证 GIF 转码存相册）
   - [ ] 小说阅读、桌面卡片添加
6. 记录基线体验数据（可选）：冷启动耗时、瀑布流滑动帧率（DevEco Profiler）、内存占用 —— 作为 P2 优化对照。

> 若设备系统低于 6.1.1：先解决设备/模拟器问题再往下走（风险 R4）。

### P1：工程初始化 + 更名换牌（1~2 天，可由我直接执行）

**目标**：在工作区根目录建立 Prixiv_View 自己的 git 仓库与 DevEco 工程，完成品牌替换，保留完整上游归属。

**目录布局**：
```
D:\WorkSpace\HarmonyApp\Prixiv_View\      ← git 仓库根 = DevEco 工程根
├── AppScope/  entry/  build-profile.json5  oh-package.json5  hvigorfile.ts  hvigor/
├── LICENSE（上游 GPL-3.0 原文，保留）
├── NOTICE.md（新增：归属与修改声明）
├── README.md（重写）
├── docs/（本方案等文档）
└── reference/PixLume/（上游只读快照，.gitignore 排除；DevEco 中可标记 Excluded 避免重复索引）
```

**git 初始化（推荐：保留上游历史，便于日后合并更新）**：
```powershell
# 在工作区根目录
git init
git remote add upstream https://github.com/SYTKILLER/PixLume.git
# 从本地浅克隆取基线（免网络、秒级）：
git fetch .\reference\PixLume master
git checkout -b master FETCH_HEAD
# 之后网络好时可补全历史：git fetch upstream --unshallow（可选）
```
> 备选（更简单但丢失上游历史）：直接复制 `reference/PixLume` 的工程文件到根目录（排除 `.git`），`git init` 后首个提交注明 "import PixLume v1.2.0 upstream baseline"。日后同步上游只能手工 diff。**推荐用上面的 git 方案。**

**更名换牌清单（已实测：`.ets/.ts/.json5` 代码中 0 处硬编码 "PixLume"，品牌全部集中在资源文件，改动面很小）**：

| # | 文件 | 改什么 |
|---|---|---|
| 1 | `AppScope/app.json5` | `bundleName: com.march.pixlume → com.<你的标识>.prixivview`（全网唯一，建议 `com.prixiv.view` 或带你个人域名反写）；`vendor → 你的名字`；`versionCode/versionName` 重置为 `1000000 / 0.1.0` |
| 2 | `AppScope/resources/base/element/string.json` | `app_name: "PixLume" → "Prixiv View"`（桌面图标名） |
| 3 | `entry/src/main/resources/base/element/string.json` | `EntryAbility_label: "PixLume" → "Prixiv View"`（第 13 行，任务视图名）；顺手把 `module_desc`/`EntryAbility_desc` 占位文案改成真实描述 |
| 4 | 图标资源 | `AppScope/resources/base/media/layered_image` 分层图标 + `entry/.../media/app_icon_round`（启动窗图标）→ 换成自制图标（避免沿用 March 的设计） |
| 5 | `entry/src/main/resources/base/profile/form_config.json` | 桌面卡片名称/描述里的品牌字样 |
| 6 | `entry/src/main/ets/view/more/AboutPage.ets` | 关于页：项目名走 `app_name` 资源会自动更新；检查其中硬编码的 GitHub 链接/版本号，改为 Prixiv_View 仓库；**保留上游致谢区块** |
| 7 | `README.md` | 重写：项目简介、与 PixLume 的关系、功能、构建、GPL-3.0 声明 |
| 8 | `NOTICE.md`（新增） | 第 3 节合规清单内容 |
| 9 | 全局兜底 | 大小写不敏感搜索 `pixlume`，确认除 LICENSE/NOTICE/致谢外零残留 |

**注意**：改 `bundleName` 后应用身份变化，自动签名会重新生成调试证书/Profile，需重新 Run 安装（旧 PixLume 调试包可卸载）。

**验收**：设备上安装后名称/图标为 Prixiv View，P0 全部功能回归通过；`git log` 可见上游基线 + 换牌提交。

**P1 执行记录（2026-11-21 已完成，换牌提交 a44d391）**：

- **用户决策**：bundleName `com.prixiv.view`；显示名 **PixHarbor**（候选中选定）；图标自制「叠影 P」（两轮候选 + 背景色对比后选定 6 号图案）；**桌面主图标固定 8 号 Pixiv 蓝，应用内明暗自动切换**（浅=9 号融合增强白底饱和版 / 深=8 号）；P3 首项=历史排行。
- **git 基线**：`.git` 复制法导入上游 v1.2.0（ae6d6a3），remote `upstream` 保留（本地 fetch 被沙箱 named-pipe 限制阻断，故用复制法）。
- **换牌执行**：清单 9 项全部完成，另加：存储键名 `pixlume_*`→`pixharbor_*`（EntryAbility/WidgetService）、导出文件名前缀 `PixHarbor_`（AppDataViewModel）、`AppConstants` 仓库/更新检查链接→`hero708/PixHarbor`（**远程仓库已创建**：https://github.com/hero708/PixHarbor ，公开；gh 登录账号为 hero708，故弃用最初猜测的 lizheming 命名空间）、CHANGELOG fork 头 + 0.1.0 条目、关于页新增上游 PixLume 致谢条目、vendor=prixiv、versionCode 1000000 / versionName 0.1.0。
- **图标资源落位**：AppScope 与 entry 的分层 base=8 拆分（background 全幅渐变 + foreground 透明安全区，桌面固定不随明暗变）；entry base 的 `app_icon/app_icon_round/startIcon`=9、entry **dark** 同名=8（splash `FOLLOW_SYSTEM`、Index/Login/About logo 自动明暗切换）；`assets/app_icon.png`(8)/`app_icon_light.png`(9) 供 README；原图标备份 `*.orig`（已忽略）；生成/应用脚本在 `tools/icon-gen/`。
- **.gitignore**：解除 `/docs/`、`/NOTICE.md` 忽略；新增 `/reference/`、`/tools/icon-gen/*.png`、`*.orig`、`__pycache__/`。
- **残留扫描**：功能性标识零 `pixlume` 残留；剩余命中均为上游归属（CHANGELOG 上游历史、README/NOTICE 致谢、关于页致谢条目），符合 GPL 合规要求。
- **待 P0 验收**：bundleName 已变更 → DevEco 需重新生成自动签名并 Run；设备上确认名称 PixHarbor、桌面蓝色叠影 P 图标、应用内明暗切换效果。

### P2：性能优化（2~4 天，推荐做，是你选方案3的核心收益）

| 优化项 | 现状（实测） | 改法 | 预期收益 |
|---|---|---|---|
| **瀑布流懒加载** | `WaterFlowView.ets:39` 用 `ForEach` 全量创建子组件 | 改 `LazyForEach` + 复用现成的 `viewmodel/BaseDataSource.ets`（IDataSource 已实现）；`WaterFlow.cachedCount(2~4)`；卡片组件评估 `@Reusable` 复用（注意与 `@ComponentV2` 的兼容性，API 24 上实测验证）；key 生成器从 `${id}${title}` 改为稳定 `id` | 长列表内存显著下降，快速滑动不掉帧 |
| **详情页 Swiper 缓存** | `IllustDetailPage.ets:204` `cachedCount(1,false)`；`PixivService.ts` 注释指出 cachedCount=0 时回滑会重建组件重新请求 | 验证现有请求缓存命中率；必要时提高 cachedCount 或扩展缓存层 | 回滑不重复请求、秒开 |
| **预加载下一页** | 仅 `onReachEnd` 触底加载 | 剩余条目 < N（如 8）时提前触发；配合 `PixivService` 去重 | 无限流无感加载 |
| **图片管线调优** | ImageKnifePro 已降采样；预览画质走 `appSettings.image_preview_quality` | 确认默认预览画质合理（square_medium 级）；配置磁盘缓存上限；原图仅详情页/下载时取 | 流量/内存/解码耗时下降 |
| **冷启动** | `EntryAbility` 内初始化 ImageKnife、网络探测等 | 非关键初始化延后到首帧之后；探测异步化不阻塞 UI | 冷启动提速 |

**度量方法**：DevEco Profiler（Frame / Allocation / Time）或 SmartPerf；对照 P0 记录的基线，比较：瀑布流连续滑动 30s 的平均帧率与最差帧、浏览 100 张后的内存峰值、冷启动耗时。**每项优化单独提交，可回滚。**

### P3：UI / 功能定制（持续迭代，按需排期）

先明确**上游已有**的能力（实测，详见 §2.4），避免重复造轮子：多账号（`view/user/UserAccounts.ets`）、特辑推荐、搜索补全 + ID 直达、热门预览、长按手势、导出 Token、本地备份、平板/折叠屏断点适配（`breakpoint/`）、暗色模式、下载管理、关键词屏蔽、小说系列页、桌面卡片。

**A. 借鉴 pixiv-viewer 的功能差距项**（对照表见 §2.4，只借设计不抄代码）：
1. **以图搜图（SauceNAO）**——上游已留 TODO 入口（`pages/Search.ets:78`），补全价值最高，建议 P3 首选
2. **随便看看 / 发现页**、**历史排行（按日期）**、**珍藏册**
3. **多格式导出**：小说 EPUB/HTML/Markdown；动图 WebM/ZIP（AVCodec）
4. **设置/历史云同步**（WebDAV + AES，借加密与冲突合并设计）
5. **多语言资源结构**（远期）；**漫画翻译**（远期，单独立项）

**B. 原有定制方向**：
6. **视觉个性化**：主题色/强调色（`UIConstants`、`ColorUtils`）、卡片圆角与间距、首页 Tab 结构（`pages/Index.ets`）
7. **离线收藏缓存**：收藏作品自动缓存缩略图，弱网可浏览（新增，利用 ImageKnife 缓存 + 下载记录表）
8. **下载增强**：批量下载、按画师/标签打包、Wi-Fi 自动下载关注画师新作
9. **浏览增强**：瀑布流列数手动调节、按收藏数/尺寸过滤、网格/两端对齐布局（借 viewer 多布局思路）、相似作品推荐入口
10. **小说体验**：字号/行距/背景主题、阅读进度记忆（借 viewer）、自动翻页
11. **数据管理**：历史/缓存一键清理（`view/more/AppData.ets` 已有雏形，扩展）

### P4：构建与发布（0.5~1 天）

```powershell
# 调试包（日常开发）：DevEco Run 即可
# 发布包：
hvigorw assembleHap --mode module -p product=default -p buildMode=release --no-daemon
# 产物：entry/build/default/outputs/default/entry-default-signed.hap（需配置发布签名）
```

- **自用/小范围分发**：调试签名 HAP 直接安装（自动签名已绑定你的设备）；或 GitHub/Gitee Releases 发布 HAP + 源码包
- **GPL 合规发布**：二进制与对应源码同渠道提供（仓库本身公开即满足）
- **上架 AppGallery（可选，不推荐首选）**：需 AGC 开发者认证 + 发布证书；第三方 Pixiv 客户端存在内容政策审核风险，且 GPL 开源要求与商店条款需自查；建议先走开源社区分发
- 发布前回归：P0 验收清单全量过一遍 + release 包专项（混淆/优化不破坏 reflect-metadata 装饰器 ORM，重点测历史记录/下载记录）

---

## 7. 上游同步与维护策略

- 保留 `upstream` remote（`https://github.com/SYTKILLER/PixLume.git`），每月或上游发版时：
  ```powershell
  git fetch upstream
  git merge upstream/master   # 冲突热点：更名过的资源文件、HostMap、AboutPage
  ```
- 上游值得持续吸收的更新：**HostMap 直连 IP 刷新**（IP 会失效）、Pixiv API 协议变更修复、ImageKnifePro 升级
- 你的定制尽量**集中在新文件/新目录**，对上游文件的侵入式修改最小化，降低合并冲突
- 若上游停更：fork 自维护，直连 IP 可从 Pixiv-Shaft HostManager 同步

## 8. 风险清单与缓解

| # | 风险 | 影响 | 缓解 |
|---|---|---|---|
| R1 | GPL-3.0 合规疏漏 | 法律风险 | 第 3 节清单逐项执行；发布前自查 LICENSE/NOTICE/源码可得性 |
| R2 | Pixiv 账号风控 | 第三方客户端违反 pixiv ToS，理论上有封号风险 | 建议用小号；Token 仅存本机 KV，不上传任何服务器；不做爬库/高频请求 |
| R3 | 直连 IP 失效 | 国内网络刷不出图 | auto 探测自动回退普通模式（§5.4）；**手机 tunbox 为可靠兜底**；保留图床镜像（i.pixiv.re/cat）；关注上游/Shaft 更新 `HostMap.ts` |
| R4 | 设备系统 < 6.1.1（API 24） | 无法安装 | ✅ **已解除**：实测 Mate 80 Pro Max / HarmonyOS 7.0.0.111 / API 26（§4）；其他设备先查版本，可用 API 24 模拟器替代；降 API 需大改，不建议 |
| R5 | 网络不稳（GitHub/ohpm/pixiv） | 克隆/依赖失败 | 已实测 GitHub 偶发 reset：浅克隆+重试；ohpm 失败重跑；本仓库已克隆成功不受影响 |
| R6 | release 构建优化破坏反射 ORM | 历史/下载记录失效 | P4 专项回归；必要时为 reflect-metadata 相关类配置保留规则 |
| R7 | 浅克隆历史不完整 | 无法追溯上游旧版本 | 需要时 `git fetch upstream --unshallow` |
| R8 | DETECT_GESTURE 权限（智感握姿）部分设备不支持 | 功能不可用 | 上游已有权限申请流程；验证拒绝授权时 App 正常运行（功能降级） |

## 9. 里程碑与工作量汇总

| 阶段 | 内容 | 预计 | 执行者 |
|---|---|---|---|
| P0 | 基线跑通 + 验收 + 性能基线记录 | 0.5~1 天 | 你（DevEco GUI/签名/设备），我提供排障 |
| P1 | git 初始化 + 更名换牌 + NOTICE/README | 1~2 天 | 我（代码侧全部可代做），你定 bundleName/图标 |
| P2 | 性能优化 5 项 + 度量对比 | 2~4 天 | 我改码，你跑 Profiler/真机验证 |
| P3 | 定制扩展（按挑选的方向） | 持续 | 协作 |
| P4 | release 构建 + 开源发布 | 0.5~1 天 | 协作（签名/发布账号在你侧） |

**首个可日常使用的 Prixiv_View 定制版：约 1 周。**

## 10. 批准后的下一步

你评审通过本文档后，我立即执行（无需你动手的部分）：
1. P1 全部代码侧工作：git 初始化（含上游历史）、工程文件就位、更名换牌（bundleName 用你指定的值，未指定则暂用 `com.prixiv.view`）、NOTICE.md、README.md、`.gitignore`（排除 `reference/`、构建产物）
2. 输出《P0 操作指引》：DevEco 打开工程 → SDK/依赖 → 自动签名 → 真机/模拟器 Run → 验收清单
3. P0 通过后进入 P2 性能优化（每项独立提交 + 前后对比数据）

**需要你评审时确认的 3 个问题**：
1. bundleName 用什么？（建议 `com.prixiv.view` 或 `com.<你的ID>.prixivview`）
2. 应用名显示 "Prixiv View" 还是 "Prixiv_View" 或其他？图标自制还是先用占位？
3. P3 定制方向里有没有你特别想要的功能（影响 P2 之后的排期）？

---

## 附录 A：关键文件索引（路径相对工程根）

| 路径 | 职责 |
|---|---|
| `AppScope/app.json5` | 包名/版本/应用图标与名称 |
| `build-profile.json5` | SDK 版本/产物/strictMode |
| `entry/src/main/module.json5` | 权限/设备类型/路由/卡片与备份扩展 |
| `entry/src/main/ets/entryability/EntryAbility.ets` | 入口生命周期、ImageKnife 初始化 |
| `entry/src/main/ets/entryability/AppState.ets` | PixState 全局状态 |
| `entry/src/main/ets/pages/Index.ets` | 主框架（底部 Tab） |
| `entry/src/main/ets/components/WaterFlowView.ets` | 瀑布流（P2 改造重点，现用 ForEach） |
| `entry/src/main/ets/components/PixivImage.ets` | ImageKnifePro 图片组件（降采样） |
| `entry/src/main/ets/components/ImageViewer.ets` | 大图预览 |
| `entry/src/main/ets/components/UgoiraPlayer.ets` | 动图播放 |
| `entry/src/main/ets/view/IllustDetailPage.ets` | 插画详情（Swiper cachedCount） |
| `entry/src/main/ets/view/login/WebLogin.ets` | PKCE Web 登录 |
| `entry/src/main/ets/view/login/TokenLogin.ets` | RefreshToken 登录 |
| `entry/src/main/ets/view/more/UserSettings.ets` | 设置页 |
| `entry/src/main/ets/view/more/DownloadManager.ets` | 下载管理 |
| `entry/src/main/ets/view/more/AboutPage.ets` | 关于页（换牌点） |
| `entry/src/main/ets/viewmodel/BaseDataSource.ets` | IDataSource（LazyForEach 数据源，P2 复用） |
| `entry/src/main/ets/services/PixivAuth.ts` | OAuth/Token/刷新 |
| `entry/src/main/ets/services/PixivService.ts` | 业务聚合 + 请求缓存 |
| `entry/src/main/ets/services/PixivTypes.ts` | API 类型定义 |
| `entry/src/main/ets/common/constants/AppConstants.ets` | API/Referer/RedirectURI 常量 |
| `entry/src/main/ets/common/entity/SettingsModel.ets` | appSettings（含预览画质） |
| `entry/src/main/ets/common/utils/HostMap.ts` | 直连静态 IP 表 |
| `entry/src/main/ets/common/utils/DoHClient.ts` | DNS over HTTPS |
| `entry/src/main/ets/common/utils/HostRefresher.ts` | 直连 IP 刷新 |
| `entry/src/main/ets/common/utils/BypassUrlRewriter.ts` | pximg Referer 注入 |
| `entry/src/main/ets/common/utils/ImageUtils.ts` | 画质选择/图床镜像替换 |
| `entry/src/main/ets/common/utils/network/NetworkModeManager.ets` | 直连探测与切换 |
| `entry/src/main/ets/common/utils/network/DirectDownloader.ets` | 直连下载（Referer） |
| `entry/src/main/ets/common/utils/database/` | 自研 ORM + DAO（历史/下载/标签） |
| `entry/src/main/ets/formability/PixCardFormAbility.ets` | 桌面卡片 |
| `entry/src/main/resources/base/element/string.json` | 全部 UI 文案（约 1100 行，含 EntryAbility_label） |
| `entry/src/main/resources/base/profile/form_config.json` | 卡片配置（换牌点） |

## 附录 B：常用命令

```powershell
# 依赖同步（工程根目录）
ohpm install

# 调试构建
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon

# 发布构建
hvigorw assembleHap --mode module -p product=default -p buildMode=release --no-daemon

# 上游同步
git fetch upstream
git merge upstream/master

# 品牌残留检查（应只剩 LICENSE/NOTICE/致谢中的合法引用）
git grep -i pixlume
```

## 附录 C：参考链接

- PixLume 仓库：https://github.com/SYTKILLER/PixLume ｜ Releases（HAP 下载）：https://github.com/SYTKILLER/PixLume/releases/latest
- 前身 Pixark：https://github.com/XHXYT/Pixark
- 直连节点来源 Pixiv-Shaft：https://github.com/CeuiLiSA/Pixiv-Shaft
- 架构参考 Pixez：https://github.com/Notsfsssf/pixez-flutter
- 协议参考 PixivPy：https://github.com/upbit/pixivpy
- 功能借鉴源 pixiv-viewer（AGPL-3.0，只借设计不抄代码）：https://github.com/asadahimeka/pixiv-viewer
- pixiv-viewer-app：https://github.com/asadahimeka/pixiv-viewer-app ｜ 功能清单：https://github.com/asadahimeka/pixiv-viewer-app/blob/main/docs/Features.zh-CN.md
- SauceNAO API（以图搜图自研依据）：https://saucenao.com/user.php?page=search-api
- HibiAPI（仅 API 知识参考，不引入中转依赖）：https://github.com/mixmoe/HibiAPI
- ImageKnifePro：https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Fimageknifepro
- GPL-3.0 全文：https://www.gnu.org/licenses/gpl-3.0.html
- DevEco Studio：https://developer.huawei.com/consumer/cn/deveco-studio/
