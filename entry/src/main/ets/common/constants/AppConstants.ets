
export class AppConstants {

  // 应用设置键名
  static readonly KEY_APP_SETTINGS: string = 'app_settings_json'
  // 界面设置键名
  static readonly KEY_UI_SETTINGS: string = 'interface_settings_json'
  // 直连模式各主机探测胜出 IP 的持久化键名
  static readonly KEY_DIRECT_WINNERS: string = 'direct_host_winners_json'
  // 注册链接
  static readonly REGISTER_URL: string = 'https://accounts.pixiv.net/signup'
  // 请求头 Referer 值
  static readonly REFERER_URL: string = 'https://www.pixiv.net/'
  // 重定向链接
  static readonly REDIRECT_URI: string = 'https://app-api.pixiv.net/web/v1/users/auth/pixiv/callback'

  // TODO: 远程仓库创建后生效；创建前检查更新会友好失败（toast 提示）
  static readonly GITHUB_OWNER_URL = 'https://github.com/lizheming'

  static readonly GITHUB_REPO_URL = 'https://github.com/lizheming/PixHarbor'

  // GitHub Releases 最新版接口（检查更新用）
  static readonly GITHUB_RELEASES_API_URL = 'https://api.github.com/repos/lizheming/PixHarbor/releases/latest'
  // GitHub Releases 页面（前往更新时兜底跳转用）
  static readonly GITHUB_RELEASES_URL = 'https://github.com/lizheming/PixHarbor/releases'

}
