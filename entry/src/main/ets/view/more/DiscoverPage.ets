import { NaviContainer } from "../../components/NaviContainer"
import { discoverVM } from "../../viewmodel/DiscoverViewModel"
import { PixState } from "../../entryability/AppState"
import { SegmentButtonV2Items, TabSegmentButtonV2 } from "@kit.ArkUI"
import { WaterFlowView } from "../../components/WaterFlowView"
import { PixivIllust } from "../../services/PixivTypes"

@Builder
export function DiscoverPageBuilder() {
  DiscoverPage()
}

/**
 * 随便看看（发现）页：随机优质作品 + 全站最新
 * 入口在「更多 → 功能 → 随便看看」，全屏路由 discover
 */
@ComponentV2
struct DiscoverPage {

  // onReady 时才拿到真实导航栈，用 @Local 保证重新赋值能同步到子组件
  @Local pageStack: NavPathStack = new NavPathStack()
  private swiperController: SwiperController = new SwiperController()
  private filterTabItems: SegmentButtonV2Items = new SegmentButtonV2Items([
    { text: $r('app.string.discover_random') },
    { text: $r('app.string.discover_latest') },
  ]);

  aboutToAppear(): void {
    discoverVM.onReady();
  }

  aboutToDisappear(): void {
    discoverVM.onDisappear();
  }

  build() {
    NaviContainer({
      title: $r('app.string.discover'),
      content: () => { this.Content() },
      onReady: (ctx) => { this.pageStack = ctx.pathStack },
      onBackPressed: () => false
    })
  }

  @Builder Content() {
    Column({ space: 10 }) {
      // 筛选器区域：随便看看 / 全站最新
      Row() {
        TabSegmentButtonV2({
          items: this.filterTabItems,
          selectedIndex: discoverVM.filterIndex,
          enableStateAnimation: true,
          onItemClicked: (tab) => { this.onFilterClick(tab); }
        })
      }
      .padding({ left: PixState.PageMarginValue, right: PixState.PageMarginValue })
      .width('100%')

      // 左右滑动在 随便看看/全站最新 间切换（同收藏页交互）
      Swiper(this.swiperController) {
        ForEach([0, 1], (index: number) => {
          DiscoverFeedPage({ index: index, pageStack: this.pageStack })
        }, (index: number) => `${index}`)
      }
      .index(discoverVM.filterIndex)
      .loop(false)
      .indicator(false)
      .cachedCount(1)
      .duration(280)
      .nestedScroll(SwiperNestedScrollMode.SELF_FIRST)
      .onChange((index: number) => {
        discoverVM.syncFilter(index);
      })
      .layoutWeight(1)
      .width('100%')
    }
    .width('100%').height('100%')
    .justifyContent(FlexAlign.Start)
  }

  // 筛选器点击：同步 Swiper 翻页
  private onFilterClick(index: number) {
    discoverVM.syncFilter(index);
    this.swiperController.changeIndex(index);
  }

}

/**
 * 单个发现页（随便看看 / 全站最新）。
 * 独立成组件以便在挂载时触发懒加载（首次进入、预载时均生效）
 */
@ComponentV2
struct DiscoverFeedPage {

  @Param index: number = 0;
  @Param pageStack: NavPathStack = new NavPathStack()

  aboutToAppear(): void {
    discoverVM.ensurePageLoaded(this.index);
  }

  build() {
    Stack() {
      if (discoverVM.page(this.index).isLoading && !discoverVM.page(this.index).loaded) {
        LoadingProgress()
          .width(40)
          .height(40)
          .color(PixState.currentThemeColor)
      } else {
        Refresh({ refreshing: discoverVM.page(this.index).isRefreshing }) {
          WaterFlowView({
            contentEndOffset: PixState.widthBp == 2 ? 56 : 16,
            illustList: discoverVM.page(this.index).illusts,
            emptyText: $r('app.string.no_data'),
            showBookmarkBadge: true,
            onCardClick: (illust: PixivIllust) => { discoverVM.handleIllustClick(illust, this.pageStack); },
            onReachEnd: () => { discoverVM.loadMore(); }
          })
        }
        .width('100%')
        .height('100%')
        .onRefreshing(async () => { await discoverVM.refreshPage(this.index) })
      }
    }
    .width('100%')
    .height('100%')
  }

}
