# NOTICE — 第三方声明与致谢

PixHarbor（bundleName `com.prixiv.view`）是基于上游开源项目二次开发的衍生作品。
本文件依 GPL-3.0 要求保留上游版权与致谢信息。

## 上游基线（代码来源）

- **[SYTKILLER/PixLume](https://github.com/SYTKILLER/PixLume)** v1.2.0（commit `ae6d6a3`）— GPL-3.0
  本仓库全部初始代码来自该项目。依 GPL-3.0，本衍生作品整体以 GPL-3.0 开源（见 [LICENSE](LICENSE)）。
  上游作者：[March (SYTKILLER)](https://github.com/SYTKILLER)。
- 上游致谢链（一并保留）：
  - [XHXYT/Pixark](https://github.com/XHXYT/Pixark) — PixLume 的前身项目
  - [CeuiLiSA/Pixiv-Shaft](https://github.com/CeuiLiSA/Pixiv-Shaft) — 交互设计参考、直连模式候选节点方案来源
  - [Notsfsssf/pixez-flutter](https://github.com/Notsfsssf/pixez-flutter) — 架构与业务设计参考
  - [upbit/pixivpy](https://github.com/upbit/pixivpy) — Pixiv API 协议与签名逻辑参考

## 依赖库

许可证以各包自带声明为准（见 `oh-package.json5` 与关于页「三方服务」）：

- `@ohos/axios` — MIT
- `@ohos/imageknifepro` — Apache-2.0
- `reflect-metadata` — Apache-2.0
- `@kingtous/reqwest`、`@hmanimations/ezcustomtransition` — 见包内声明

## 仅借鉴思路（未复制代码）

- **[asadahimeka/pixiv-viewer](https://github.com/asadahimeka/pixiv-viewer)** /
  **[pixiv-viewer-app](https://github.com/asadahimeka/pixiv-viewer-app)** — AGPL-3.0。
  仅参考其功能定义与交互设计（如以图搜图、历史排行等差距项思路），**未复制任何代码**，
  以避免 AGPL 网络条款对本项目 GPL-3.0 许可的传染。
- **[SauceNAO](https://saucenao.com/user.php?page=search-api)** 公开 API —
  以图搜图功能将按其公开接口文档以 ArkTS 自研实现。

## 图标

应用图标为本项目**自制**（「叠影 P」设计，生成脚本见 `tools/icon-gen/`），不来自上游。
桌面主图标固定 Pixiv 蓝版；应用内资源随明暗模式自动切换（浅色=白底饱和版 / 深色=Pixiv 蓝版）。

## 免责声明

PixHarbor 是非官方第三方客户端，与 Pixiv Inc. 无任何从属关系。仅供学习交流，请遵守
Pixiv 官方服务条款及相关法律法规。