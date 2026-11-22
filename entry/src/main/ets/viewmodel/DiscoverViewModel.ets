import { DetailPageParams, IIllustSwiperProvider } from "../common/entity/DetailEntity";
import { PixivIllust } from "../services/PixivTypes";
import { createLogger } from "../common/utils/Logger";
import { pixiv } from "../services/PixivService";

const logger = createLogger('DiscoverViewModel');

/** 单个发现页（0 随便看看 / 1 全站最新）的插画数据，每个 Swiper 页独立持有 */
@ObservedV2
export class DiscoverPageData {
  @Trace illusts: PixivIllust[] = [];
  @Trace isLoading: boolean = false;
  // 仅供 Refresh 组件绑定：加载更多也会置 isLoading，若 Refresh 绑定 isLoading，
  // 触底加载会被误判为下拉刷新并触发 onRefreshing 重载第一页
  @Trace isRefreshing: boolean = false;
  loaded: boolean = false;
  nextUrl: string = '';
  // 该页进行中的加载任务：强制刷新前需等待其收尾，避免刷新被防抖吞掉或新旧数据错拼
  inflight?: Promise<void>;
}

/**
 * 随便看看（发现）页 ViewModel
 * 两个数据页：0 随便看看（官方随机优质发现流 /v1/walkthrough/illusts）
 *           1 全站最新（大家的新作 /v1/illust/new）
 * 支持 Swiper 滑动切换、下拉刷新（换一批）、触底加载更多、详情页滑动联动
 */
@ObservedV2
class DiscoverViewModel implements IIllustSwiperProvider {

  // --- 筛选器状态（与 Swiper 页联动）：0 随便看看, 1 全站最新 ---
  @Trace filterIndex: number = 0;

  // --- 数据状态 ---
  @Trace isInitialLoading: boolean = true;
  @Trace isLoadingMore: boolean = false;

  // 页面是否处于前台（账号切换时仅前台页面立即重载）
  isActive: boolean = false;

  private pages: DiscoverPageData[] = [new DiscoverPageData(), new DiscoverPageData()];

  // --- 生命周期 ---
  async onReady() {
    this.isActive = true;
    logger.debug('[onReady] Discover page ready.');
    // 先加载当前页，随后后台预载另一页，保证滑动切换即有内容
    await this.loadPage(this.filterIndex);
    this.isInitialLoading = false;
    this.preloadOtherPages();
  }

  onDisappear() {
    this.isActive = false;
  }

  // --- UI 数据访问 ---
  page(index: number): DiscoverPageData {
    return this.pages[index];
  }

  // --- 页切换 ---
  syncFilter(index: number) {
    if (index < 0 || index > 1) return;
    this.filterIndex = index;
    this.ensurePageLoaded(index);
  }

  ensurePageLoaded(index: number) {
    const page = this.pages[index];
    if (page.loaded || page.isLoading) return;
    this.loadPage(index);
  }

  private preloadOtherPages() {
    for (let i = 0; i < 2; i++) {
      if (i !== this.filterIndex) {
        this.ensurePageLoaded(i);
      }
    }
  }

  // 强制重置并重新加载（用于切换账号）
  public resetAndLoad() {
    // 原地重置（页面 UI 持有各页实例的引用，不能整体替换数组）
    for (const page of this.pages) {
      page.illusts = [];
      page.isLoading = false;
      page.isRefreshing = false;
      page.loaded = false;
      page.nextUrl = '';
    }
    this.isInitialLoading = true;
    if (this.isActive) {
      this.onReady();
    }
  }

  // --- 详情页滑动联动 (IIllustSwiperProvider) ---
  get illustIds(): number[] {
    return this.pages[this.filterIndex].illusts.map(i => i.id);
  }

  get hasMore(): boolean {
    return !!this.pages[this.filterIndex].nextUrl;
  }

  get isLoading(): boolean {
    return this.isLoadingMore;
  }

  // --- 加载逻辑 ---
  async loadPage(index: number, isLoadMore: boolean = false, force: boolean = false) {
    const page = this.pages[index];
    // 防抖：该页已有任务在跑时直接返回；强制刷新则先等旧任务收尾再执行
    if (page.inflight !== undefined) {
      if (!force) return;
      await page.inflight.catch(() => {});
      if (page.inflight !== undefined) return;
    }
    if (!isLoadMore && page.loaded && !force) return;
    if (isLoadMore && (this.isLoadingMore || !page.nextUrl)) return;
    if (isLoadMore) this.isLoadingMore = true;
    page.isLoading = true;
    const task = (async () => {
      try {
        const res = index === 0
          ? await pixiv.walkthroughIllusts(isLoadMore ? page.nextUrl : undefined)
          : await pixiv.getNewIllusts('illust', isLoadMore ? page.nextUrl : undefined);
        page.nextUrl = res.next_url || '';
        const rawData: PixivIllust[] = res.illusts || [];
        // 随便看看：官方 walkthrough 返回的是固定优质池（无 next_url），
        // 客户端打乱顺序，使每次进入 / 下拉换一批都呈现不同的随机排列；
        // 全站最新保持时间序，不打乱。
        const newData: PixivIllust[] = (index === 0 && !isLoadMore) ? this.shuffleIllusts(rawData) : rawData;
        // 加载更多为纯追加，已有项不动；刷新为整体替换
        page.illusts = isLoadMore ? [...page.illusts, ...newData] : newData;
        page.loaded = true;
        logger.debug(`[loadPage] tab=${index} loaded=${newData.length} next=${!!page.nextUrl}`);
      } catch (e) {
        logger.error(`[loadPage] tab=${index} failed: ${e.message}`);
      }
    })();
    page.inflight = task;
    try {
      await task;
    } finally {
      if (page.inflight === task) page.inflight = undefined;
      page.isLoading = false;
      if (isLoadMore) this.isLoadingMore = false;
    }
  }

  // 下拉刷新（随便看看页即"换一批"）：等待在途请求收尾后强制重载第一页
  async refreshPage(index: number) {
    const page = this.pages[index];
    if (page.isRefreshing) return;
    page.isRefreshing = true;
    try {
      await this.loadPage(index, false, true);
    } finally {
      page.isRefreshing = false;
    }
  }

  // Fisher–Yates 洗牌：返回打乱后的新数组，不改动入参
  private shuffleIllusts(arr: PixivIllust[]): PixivIllust[] {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = a[i];
      a[i] = a[j];
      a[j] = tmp;
    }
    return a;
  }

  // --- 交互逻辑 ---
  handleIllustClick(illust: PixivIllust, pageStack: NavPathStack) {
    const list = this.pages[this.filterIndex].illusts;
    const index = list.findIndex(i => i.id === illust.id);
    const params: DetailPageParams = {
      id: illust.id,
      swiperProvider: this,
      swiperIndex: index >= 0 ? index : 0,
      // 数据兜底：残缺数据（无 user）置空，让详情页自己拉
      illust: illust.user ? illust : undefined
    };
    pageStack.pushPathByName('illust_detail', params, true);
  }

  // --- 加载更多 ---
  async loadMore(): Promise<void> {
    await this.loadPage(this.filterIndex, true);
  }

}

export const discoverVM = new DiscoverViewModel();
