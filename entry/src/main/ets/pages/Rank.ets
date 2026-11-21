import { PixState, _PixState } from "../entryability/AppState"
import { animation } from "../common/utils/AnimationUtil"
import { rankVM } from "../viewmodel/RankViewModel"
import { appSettings } from "../common/entity/SettingsModel"
import { WaterFlowView } from "../components/WaterFlowView"
import { RankTab } from "../common/entity/RankModel"
import { NovelListView } from "../components/NovelListView"
import { PixivNovel } from "../services/PixivTypes"
import { EmptyStateView } from "../components/CommonWidgets"
import UIConstants from "../common/constants/UIConstants"
import { FunctionConstants } from "../common/constants/FunctionConstants"
import { SegmentButtonV2ItemOptions, SegmentButtonV2Items, TabSegmentButtonV2, LengthMetrics } from '@kit.ArkUI'


@ComponentV2
export struct Rank {
  @Local showEditPanel: boolean = false
  private swiperController: SwiperController = new SwiperController()

  // 分段按钮选项：榜单配置（勾选/排序/插画小说模式）变化时自动重建
  @Computed
  get rankTabItems(): SegmentButtonV2Items {
    return new SegmentButtonV2Items(
      rankVM.activeTabs.map((tab): SegmentButtonV2ItemOptions => ({ text: tab.label }))
    );
  }

  // 榜单分类标签表：随插画/小说全局模式切换（P3 小说排行榜）
  @Computed
  get rankModeLabels(): Record<string, string> {
    return appSettings.novel_mode ? FunctionConstants.NOVEL_RANK_MODES : FunctionConstants.ILLUST_RANK_MODES;
  }

  aboutToAppear(): void {
    // 如果已经有配置，自动加载当前分类
    if (!rankVM.isEmptyConfig) {
      rankVM.ensureFirstLoad()
    }
  }

  build() {
    Column() {
      // 顶部：分类胶囊 + 操作按钮
      this.Header()
      // 内容区域
      if (rankVM.isEmptyConfig) {
        this.EmptyState()
      } else {
        this.RankSwiper()
      }
    }
    .size({ width: '100%', height: '100%' })
    .bindSheet($$this.showEditPanel, this.EditPanelBuilder(), {
      height: '70%',
      dragBar: true,
      onWillAppear: () => rankVM.openEditMode(),
      onWillDisappear: () => {
        // 关闭时自动保存，并让 Swiper 停留在当前分类页（页签数量/顺序可能变化）
        rankVM.saveModes()
        this.swiperController.changeIndex(rankVM.currentTabIndex())
      }
    })
  }

  // 头部区域：第一行分类分段按钮+操作钮；选中历史日期时日期胶囊独占第二行，避免挤压分段按钮宽度
  @Builder Header() {
    Column({ space: 4 }) {
      Row({ space: 8 }) {
        // 分类分段按钮
        Row() {
          if (rankVM.activeTabs.length > 0) {
            TabSegmentButtonV2({
              items: this.rankTabItems,
              selectedIndex: rankVM.currentTabIndex(),
              enableStateAnimation: true,
              // 等宽分栏下默认 16vp 横向内边距会把标签挤成"..."，收紧内边距与字号保证 5 页签可读
              itemFontSize: LengthMetrics.fp(13),
              itemSelectedFontSize: LengthMetrics.fp(13),
              itemPadding: {
                top: LengthMetrics.vp(6),
                bottom: LengthMetrics.vp(6),
                start: LengthMetrics.vp(8),
                end: LengthMetrics.vp(8)
              },
              onItemClicked: (index: number) => {
                this.onSegmentClick(index)
              }
            })
          }
        }
        .layoutWeight(1)

        // 未选日期：日历圆钮入口
        if (!rankVM.currentDate) {
          Button({ type: ButtonType.Circle }) {
            SymbolGlyph($r('sys.symbol.calendar'))
              .fontColor([$r('sys.color.font_primary')])
              .fontSize(22)
          }
          .width(40).height(40)
          .backgroundColor($r('sys.color.button_background_color_transparent'))
          .onClick(() => this.openDatePicker())
        }

        // 编辑/配置 Tab 按钮
        Button({ type: ButtonType.Circle }) {
          SymbolGlyph($r('sys.symbol.square_and_pencil'))
            .fontColor([$r('sys.color.font_primary')])
            .fontSize(22)
        }
        .width(40).height(40)
        .backgroundColor($r('sys.color.button_background_color_transparent'))
        .onClick(() => this.showEditPanel = true)
      }
      .width('100%')
      .height(48)
      .alignItems(VerticalAlign.Center)

      // 选中历史日期：日期胶囊 + 清除按钮（P3 历史排行 UX）
      if (rankVM.currentDate) {
        Row({ space: 8 }) {
          Button({ type: ButtonType.Capsule }) {
            Row({ space: 4 }) {
              SymbolGlyph($r('sys.symbol.calendar'))
                .fontColor([Color.White])
                .fontSize(16)
              Text(rankVM.currentDate)
                .fontSize(13)
                .fontColor(Color.White)
            }
          }
          .height(36)
          .padding({ left: 12, right: 12 })
          .backgroundColor(PixState.currentThemeColor)
          .onClick(() => this.openDatePicker())

          Button({ type: ButtonType.Circle }) {
            SymbolGlyph($r('sys.symbol.xmark'))
              .fontColor([$r('sys.color.font_primary')])
              .fontSize(18)
          }
          .width(36).height(36)
          .backgroundColor($r('sys.color.button_background_color_transparent'))
          .onClick(() => rankVM.clearDate())
        }
        .width('100%')
        .height(36)
        .alignItems(VerticalAlign.Center)
      }
    }
    .width('100%')
    .padding({ left: 8, right: 8, top: 4, bottom: 4 })
    .alignItems(HorizontalAlign.Start)
  }

  // 历史排行日期选择：取消保留当前选择（回到最新用清除按钮）
  private openDatePicker() {
    _PixState.UIContext.showDatePickerDialog({
      start: new Date(2000, 0, 1),
      // Pixiv 榜单按 JST 发布滞后一天，未发布日期选了也只会得到空列表
      end: rankVM.latestAvailableDate(),
      selected: rankVM.pickerSelectedDate(),
      showTime: false,
      onDateAccept: (value: Date) => {
        rankVM.changeDate(new Date(value))
      },
      onCancel: () => {
        // 取消不改变当前日期
      }
    })
  }

  // 分段按钮点击：切换 Swiper 页
  private onSegmentClick(index: number) {
    const tabs = rankVM.activeTabs
    if (index < 0 || index >= tabs.length) return
    if (tabs[index].key !== rankVM.currentMode) {
      rankVM.changeMode(tabs[index].key)
      this.swiperController.changeIndex(index)
    }
  }

  // Swiper 翻页结束：同步当前分类（分段按钮选中态随 currentMode 自动更新）
  private onSwiperChange(index: number) {
    rankVM.syncModeByIndex(index)
  }

  // 空状态引导
  @Builder EmptyState() {
    EmptyStateView({
      icon: $r('sys.symbol.square_and_pencil'),
      message: $r('app.string.no_custom_rank'),
      actionText: $r('app.string.click_config'),
      onAction: () => { this.showEditPanel = true }
    })
  }

  // 分类翻页容器：左右滑动在排行榜分类间切换
  @Builder RankSwiper() {
    Swiper(this.swiperController) {
      ForEach(rankVM.activeTabs, (tab: RankTab) => {
        this.RankPage(tab.key)
      }, (tab: RankTab): string => `${tab.key}_${appSettings.novel_mode ? 'n' : 'i'}`)
    }
    .index(rankVM.currentTabIndex())
    .loop(false)
    .indicator(false)
    .cachedCount(1)
    .duration(280)
    .nestedScroll(SwiperNestedScrollMode.SELF_FIRST)
    .onChange((index: number) => {
      this.onSwiperChange(index)
    })
    .width('100%')
    .layoutWeight(1)
  }

  // 单个分类页：懒加载数据 + 加载指示
  @Builder RankPage(mode: string) {
    Stack() {
      if (appSettings.novel_mode) {
        NovelListView({
          contentEndOffset: PixState.FloatTabBarListAvoid,
          novelList: rankVM.getPageData(mode).novels,
          onItemClick: (novel: PixivNovel) => { rankVM.handleNovelClick(novel); },
          onReachEnd: () => { rankVM.loadMore(mode); }
        }).transition(animation.modeSwitchTransition())
      } else {
        WaterFlowView({
          contentEndOffset: PixState.FloatTabBarListAvoid,
          illustList: rankVM.getPageData(mode).illusts,
          onCardClick: (illust) => { rankVM.handleIllustClick(illust); },
          onReachEnd: () => { rankVM.loadMore(mode); }
        }).transition(animation.modeSwitchTransition())
      }

      if (rankVM.getPageData(mode).isLoading && !rankVM.getPageData(mode).loaded) {
        LoadingProgress()
          .width(40)
          .height(40)
          .color(PixState.currentThemeColor)
      }
    }
    .width('100%')
    .height('100%')
  }

  // 编辑面板：勾选 + 拖拽排序
  @Builder EditPanelBuilder() {
    Column() {
      Text($r('app.string.custom_rank_items'))
        .fontSize(18)
        .fontWeight(FontWeight.Bold)
        .margin({ bottom: 8 })
      Text($r('app.string.custom_rank_items_tips'))
        .fontSize(13)
        .fontColor($r('sys.color.ohos_id_color_text_secondary'))
        .margin({ bottom: 16 })

      Grid() {
        ForEach(rankVM.editingModes, (key: string, index?: number) => {
          GridItem() {
            Text(this.rankModeLabels[key])
              .fontSize(14)
              .padding({ left: 12, right: 12, top: 8, bottom: 8 })
              .borderRadius(UIConstants.RADIUS_PILL)
              .backgroundColor(rankVM.editingSelected.has(key) ? PixState.currentThemeColor : $r('sys.color.button_background_color_transparent'))
              .fontColor(rankVM.editingSelected.has(key) ? Color.White : $r('sys.color.font_primary'))
              .border({ width: 1, color: rankVM.editingSelected.has(key) ? PixState.currentThemeColor : $r('sys.color.ohos_id_color_fourth') })
              .animation({ duration: 200, curve: Curve.Ease })
              .onClick(() => rankVM.toggleModeInEdit(key))
          }
        }, (key: string) => key)
      }
      .columnsTemplate('1fr 1fr 1fr')
      .rowsGap(10)
      .columnsGap(10)
      .width('100%')
      .editMode(true) // 开启编辑模式
      .supportAnimation(true) // 支持拖拽动画
      .onItemDragStart((event: ItemDragInfo, itemIndex: number) => { // 拖拽开始
        console.debug(`[RankUI] onItemDragStart: index=${itemIndex}`);
        return this.DragItemBuilder(rankVM.editingModes[itemIndex]); // 返回拖拽跟手样式
      })
      .onItemDrop((event: ItemDragInfo, itemIndex: number, insertIndex: number, isSuccess: boolean) => { // 拖拽释放
        console.debug(`[RankUI] onItemDrop: itemIndex=${itemIndex}, insertIndex=${insertIndex}, isSuccess=${isSuccess}`);
        if (!isSuccess || insertIndex < 0 || insertIndex >= rankVM.editingModes.length) {
          return;
        }
        rankVM.onDropTo(itemIndex, insertIndex);
      })
    }
    .padding(24)
    .width('100%')
    .height('100%')
  }

  // 拖拽时跟随手指的半透明幽灵组件
  @Builder DragItemBuilder(key: string) {
    Text(this.rankModeLabels[key])
      .fontSize(14)
      .padding({ left: 12, right: 12, top: 8, bottom: 8 })
      .borderRadius(UIConstants.RADIUS_PILL)
      .backgroundColor(PixState.currentThemeColor)
      .fontColor(Color.White)
      .opacity(0.7)
      .border({ width: 1, color: PixState.currentThemeColor })
  }

}
