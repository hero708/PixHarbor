import { preferenceUtil } from './persistence/PreferenceUtil';
import { createLogger } from './Logger';

const logger = createLogger('ReadingProgress');

// 与 AppConstants.KEY_NOVEL_READ_PROGRESS 保持一致（.ts 不允许 import .ets，故此处本地定义）
const KEY_NOVEL_READ_PROGRESS: string = 'novel_read_progress_json';

/** 单本小说的阅读进度（滚动比例 + 更新时间） */
interface ProgressEntry {
  ratio: number;
  ts: number;
}

/**
 * 小说阅读进度记忆（P3-1）：
 * 以 novelId 为键存储滚动比例，偏好文件单键 JSON _map_ 持久化；
 * 写入防抖合并，条目上限 300 按最旧淘汰；接近开头/结尾不记录（避免无意义的"继续阅读"）。
 */
class ReadingProgressUtil {
  private map: Record<string, ProgressEntry> = {};
  private loaded: boolean = false;
  private writeTimer: number = -1;

  private async ensureLoaded(): Promise<void> {
    if (this.loaded) {
      return;
    }
    try {
      const jsonStr: string = await preferenceUtil.get<string>(KEY_NOVEL_READ_PROGRESS, '');
      if (jsonStr) {
        this.map = JSON.parse(jsonStr) as Record<string, ProgressEntry>;
      }
    } catch (e) {
      logger.warn('load reading progress failed:', e);
    }
    this.loaded = true;
  }

  /** 读取进度比例（0-1），无记录返回 0 */
  async getRatio(id: number): Promise<number> {
    await this.ensureLoaded();
    const entry: ProgressEntry | undefined = this.map[`${id}`];
    return entry ? entry.ratio : 0;
  }

  /** 保存进度比例；越界裁剪，过近首尾视为未读/已读完而清除 */
  async saveRatio(id: number, ratio: number): Promise<void> {
    await this.ensureLoaded();
    const clamped: number = Math.min(1, Math.max(0, ratio));
    const key: string = `${id}`;
    if (clamped < 0.01 || clamped > 0.99) {
      delete this.map[key];
    } else {
      this.map[key] = { ratio: clamped, ts: Date.now() };
    }
    this.prune();
    this.scheduleWrite();
  }

  /** 清除进度（"从头阅读"） */
  async clearRatio(id: number): Promise<void> {
    await this.ensureLoaded();
    delete this.map[`${id}`];
    this.scheduleWrite();
  }

  private prune(): void {
    const keys: string[] = Object.keys(this.map);
    if (keys.length <= 300) {
      return;
    }
    keys.sort((a: string, b: string) => this.map[a].ts - this.map[b].ts);
    const removeCount: number = keys.length - 300;
    for (let i = 0; i < removeCount; i++) {
      delete this.map[keys[i]];
    }
  }

  private scheduleWrite(): void {
    if (this.writeTimer !== -1) {
      clearTimeout(this.writeTimer);
    }
    this.writeTimer = setTimeout(() => {
      this.writeTimer = -1;
      this.flush();
    }, 400);
  }

  private async flush(): Promise<void> {
    try {
      await preferenceUtil.put(KEY_NOVEL_READ_PROGRESS, JSON.stringify(this.map));
    } catch (e) {
      logger.warn('save reading progress failed:', e);
    }
  }
}

export const readingProgress: ReadingProgressUtil = new ReadingProgressUtil();
