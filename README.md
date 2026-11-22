<div align="center">

# PixHarbor

> 为 HarmonyOS 打造的原生轻量级 Pixiv 第三方客户端 · 把灵感停泊在掌心

![HarmonyOS](https://img.shields.io/badge/HarmonyOS-ArkTS-green)
![API](https://img.shields.io/badge/API-24%2B-blue)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

<img src="assets/app_icon.png" alt="PixHarbor Icon" width="120">

</div>

## ✨ 项目简介

PixHarbor 基于上游开源项目 [SYTKILLER/PixLume](https://github.com/SYTKILLER/PixLume) v1.2.0（GPL-3.0）二次开发：
全新品牌与自制图标，并在此基础上持续演进性能与功能（实施计划见 [docs/](docs/)）。
它基于 ArkTS / TypeScript 开发，深度整合 HarmonyOS 系统能力，提供账号登录、推荐浏览、搜索发现与用户互动等完整功能。

## 🚀 核心功能

- **🔐 登录**：账号密码 / Refresh Token / Web OAuth 三种方式，Token 自动刷新长期在线
- **🎨 探索**：推荐流、日/周/月/小说排行榜与历史排行按日期回看、关键词搜索与智能补全、「猜你喜欢」
- **🖼 浏览**：插画/漫画/小说三形态，沉浸式阅读与暗色模式；小说阅读进度记忆、自动翻页与进度条；动图原生播放、下载自动转 GIF 存相册
- **⚡ 直连模式**：启动自动探测（auto/off/on 三档），普通网络不可用时自动切换直连链路，接口/图片/下载全覆盖；可与 VPN 共存兜底
- **❤️ 互动**：公开/私密收藏与自定义标签、关注画师
- **🗂 本地**：下载管理、小说 TXT 导出、历史记录、关键词译文/收藏/屏蔽、数据备份与导入导出
- **📱 体验**：桌面卡片「灵感图卡」、智感握姿悬浮按钮换边、底部悬浮页签

## 🎨 图标

自制「叠影 P」设计（生成脚本见 [tools/icon-gen/](tools/icon-gen/)）：

- **桌面主图标**：固定浅色版（白底饱和 P）
- **应用内**：随明暗模式自动切换 —— 浅色 = 白底饱和版，深色 = Pixiv 蓝版

<div align="center">
  <img src="assets/app_icon.png" alt="桌面/浅色版" width="96">
  <img src="assets/app_icon_dark.png" alt="应用内深色版" width="96">
</div>

## 🛠 技术栈

- **开发语言**：ArkTS / TypeScript（@ComponentV2 状态管理）
- **运行环境**：HarmonyOS 6.1.1（API 24）及以上
- **网络**：@ohos/axios / RCP，直连模式静态 DNS + DoH
- **图片**：@ohos/imageknifepro（降采样 + 二级缓存）
- **存储**：Preferences / KV Store（自研 ORM + DAO）
- **开发工具**：DevEco Studio 6.1+

## 🧑‍💻 本地构建

1. 克隆本仓库：`git clone https://github.com/hero708/PixHarbor.git`
2. DevEco Studio 打开项目，等待依赖同步（或 `ohpm install`）
3. 签名：`File > Project Structure > Signing Configs` 勾选自动生成调试签名
   （**换牌后 bundleName 已变更，需重新生成签名证书**）
4. 连接设备 Run，或命令行：

   ```bash
   hvigorw assembleHap --mode module -p product=default -p buildMode=release --no-daemon
   ```

## 🌐 网络说明

国内网络下 Pixiv 域名存在 DNS 污染：直连模式以候选 IP + 静态 DNS 尽力而为（节点表见
`entry/src/main/ets/common/utils/HostMap.ts`，失效时自动回退普通模式）；开启 VPN 时自动走普通模式，两者可共存。
详见实施文档 §5.4。

## 🗺 演进计划

- **P2 性能（已完成）**：主瀑布流 ForEach → LazyForEach 懒加载 + 触底预加载；翻页增量追加不回跳、卡片按真实宽高比预留高度零重排（详情页 Swiper 缓存 / 冷启动 / 图片管线经实测上游已优化）
- **P3 功能（持续迭代）**：已落地历史排行（按日期回看）、小说排行榜、小说阅读体验（进度记忆 / 自动翻页 / 进度条）；待补以图搜图（SauceNAO 自研）、随便看看 / 发现页、珍藏册等差距项
- 详见 [docs/方案1-基于PixLume二次开发实施方案.md](docs/方案1-基于PixLume二次开发实施方案.md)

## 🙏 致谢

- **[SYTKILLER/PixLume](https://github.com/SYTKILLER/PixLume)**（上游基线，作者 [March](https://github.com/SYTKILLER)）
- **[XHXYT/Pixark](https://github.com/XHXYT/Pixark)**、**[Pixiv-Shaft](https://github.com/CeuiLiSA/Pixiv-Shaft)**、**[Pixez](https://github.com/Notsfsssf/pixez-flutter)**、**[PixivPy](https://github.com/upbit/pixivpy)**（上游致谢链）
- **[pixiv-viewer-app](https://github.com/asadahimeka/pixiv-viewer-app)**（仅功能思路参考，AGPL-3.0，未复制代码）

完整第三方声明见 [NOTICE.md](NOTICE.md)。

## ⚠️ 免责声明

- **PixHarbor** 是非官方第三方客户端，与 Pixiv Inc. 没有任何从属关系。
- 本项目仅供学习交流使用，请勿用于商业用途；使用风险与责任由使用者自行承担。
- 请遵守 Pixiv 官方服务条款及相关法律法规。

## 📄 开源协议

本项目基于 [GNU General Public License v3.0](LICENSE) 开源（上游 PixLume 同为 GPL-3.0）。
你可以自由使用、修改和分发本软件，但所有衍生作品必须以相同协议开源。