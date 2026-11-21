# -*- coding: utf-8 -*-
"""PixHarbor 换牌：把选定的叠影 P 图标写成 HarmonyOS 资源。

决策（用户 2026-11-21 确认）：
  - 桌面主图标固定 8 号 Pixiv 蓝（AppScope 分层 + entry 分层 base，不做 dark 覆盖）
  - 应用内明暗自动切换：浅色=9 融合增强（白底饱和 P），深色=8
    载体：entry base/dark 的 app_icon.png / app_icon_round.png / startIcon.png
    （splash startWindowAppIcon、Index/Login logo 用 app_icon_round；About logo 用 app_icon）
  - assets/app_icon.png(8) / assets/app_icon_light.png(9) 供 README 引用（入库）

仿 tunbox apply_icon.py：background 全幅渐变（系统裁圆角）、foreground 透明安全区、
合成圆角回退图、.orig 备份（已加入 .gitignore）。
"""
import os
import shutil
from PIL import Image, ImageDraw
from gen_icons import N, OUT, gradient, white_layer, soft_shadow, round_mask, LANCZOS
from gen_icons_p import draw_p

ROOT = r"D:\WorkSpace\HarmonyApp\Prixiv_View"
APP_MEDIA = os.path.join(ROOT, "AppScope", "resources", "base", "media")
ENTRY_BASE = os.path.join(ROOT, "entry", "src", "main", "resources", "base", "media")
ENTRY_DARK = os.path.join(ROOT, "entry", "src", "main", "resources", "dark", "media")
ASSETS = os.path.join(ROOT, "assets")

# 8 号：Pixiv 蓝 + 原版半透明青/粉叠影
BG8 = dict(top='#00A5F0', bottom='#0057B8', glow='#7FD4FF', glow_alpha=0.5)
P8 = ((34, 211, 238, 215), (244, 114, 182, 215), 60)
# 9 号：浅色白底 + 饱和青/玫红叠影
BG9 = dict(top='#F8FAFC', bottom='#D8E2F0', glow='#FFFFFF', glow_alpha=0.6)
P9 = ((8, 145, 178, 230), (219, 39, 119, 230), 30)


def build(bgcfg, pcfg):
    bg = gradient(N, bgcfg['top'], bgcfg['bottom'], glow=bgcfg['glow'],
                  glow_pos=(0.5, 0.25), glow_alpha=bgcfg['glow_alpha'])
    cyan, pink, shadow = pcfg
    l1, l2 = white_layer(), white_layer()
    draw_p(ImageDraw.Draw(l1), cyan, dx=-0.028, dy=-0.022)
    draw_p(ImageDraw.Draw(l2), pink, dx=0.028, dy=0.022)
    return bg, l1, l2, shadow


def foreground(bg, l1, l2, shadow):
    fg = soft_shadow(Image.new('RGBA', (N, N), (0, 0, 0, 0)), l1, opacity=shadow)
    fg.alpha_composite(l2)
    return fg


def composite(size, bg, l1, l2, shadow):
    big = size * 2
    out = Image.new('RGBA', (big, big), (0, 0, 0, 0))
    out.alpha_composite(bg.resize((big, big), LANCZOS))
    out.alpha_composite(foreground(bg, l1, l2, shadow).resize((big, big), LANCZOS))
    out = out.resize((size, size), LANCZOS)
    res = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    res.paste(out, (0, 0), round_mask(size, int(size * 0.225)))
    return res


def backup(p):
    if os.path.exists(p) and not os.path.exists(p + '.orig'):
        shutil.copy2(p, p + '.orig')
        print('backup ->', p + '.orig')


def put(p, im):
    backup(p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    im.save(p)
    print('wrote', p, im.size)


def existing_size(p, default):
    if os.path.exists(p):
        with Image.open(p) as im:
            return im.size[0]
    return default


def main():
    bg8, l18, l28, sh8 = build(BG8, P8)
    bg9, l19, l29, sh9 = build(BG9, P9)
    fg8 = foreground(bg8, l18, l28, sh8).resize((1024, 1024), LANCZOS)
    fg9 = foreground(bg9, l19, l29, sh9).resize((1024, 1024), LANCZOS)
    bg8s = bg8.resize((1024, 1024), LANCZOS)
    bg9s = bg9.resize((1024, 1024), LANCZOS)

    # 桌面分层图标：固定 8（AppScope 与 entry base 一致；entry 不做 dark 分层覆盖）
    for d in (APP_MEDIA, ENTRY_BASE):
        put(os.path.join(d, 'background.png'), bg8s)
        put(os.path.join(d, 'foreground.png'), fg8)
    for name in ('app_icon.png', 'app_icon_round.png'):
        p = os.path.join(APP_MEDIA, name)
        put(p, composite(existing_size(p, 512), bg8, l18, l28, sh8))

    # 应用内：base=9（浅色），dark=8（深色）
    for name, default in (('app_icon.png', 512), ('app_icon_round.png', 512), ('startIcon.png', 256)):
        pb = os.path.join(ENTRY_BASE, name)
        pd = os.path.join(ENTRY_DARK, name)
        size = existing_size(pb, default)
        put(pb, composite(size, bg9, l19, l29, sh9))
        put(pd, composite(existing_size(pd, size), bg8, l18, l28, sh8))

    # README 用图（入库）
    put(os.path.join(ASSETS, 'app_icon.png'), composite(1024, bg8, l18, l28, sh8))
    put(os.path.join(ASSETS, 'app_icon_light.png'), composite(1024, bg9, l19, l29, sh9))

    # 预览：桌面 / 应用内浅色 / 应用内深色
    cell, pad = 360, 30
    sheet = Image.new('RGB', (3 * cell + 4 * pad, cell + 2 * pad), (243, 246, 251))
    dark = Image.new('RGB', (cell + 2 * pad, cell + 2 * pad), (18, 22, 30))
    icons = [composite(cell, bg8, l18, l28, sh8),
             composite(cell, bg9, l19, l29, sh9),
             composite(cell, bg8, l18, l28, sh8)]
    sheet.paste(icons[0], (pad, pad), icons[0])
    sheet.paste(icons[1], (2 * pad + cell, pad), icons[1])
    dark.paste(icons[2], (pad, pad), icons[2])
    sheet.paste(dark, (2 * cell + 3 * pad, 0))
    sheet.save(os.path.join(OUT, 'applied_preview.png'))
    print('saved applied_preview.png')


if __name__ == '__main__':
    main()
