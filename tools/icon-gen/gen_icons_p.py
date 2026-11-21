# -*- coding: utf-8 -*-
"""PixHarbor 图标候选第二轮：全部以字母 P 或其变形为主体。

复用 gen_icons.py 的管线（渐变/辉光/圆角/软阴影/对比图）。
P 几何修正：碗部左缘收进竖笔宽度内，消除第一轮的接缝瑕疵。
所有图形控制在分层图标前景安全区（约 0.22~0.78）内。
"""
import os
from PIL import Image, ImageDraw, ImageFont
from gen_icons import (N, SIZE, OUT, gradient, round_mask, white_layer,
                       soft_shadow, ring_shape, finish, LANCZOS)


def draw_p(d, color, scale=1.0, dx=0.0, dy=0.0):
    """标准粗体 P：竖笔 + 碗部圆环，碗左缘收进竖笔内避免接缝。"""
    def T(x, y):
        return (N * (0.535 + (x - 0.535) * scale + dx),
                N * (0.5 + (y - 0.5) * scale + dy))
    sl, sw = 0.37, 0.095
    x0, y0 = T(sl, 0.25)
    x1, y1 = T(sl + sw, 0.75)
    d.rounded_rectangle([x0, y0, x1, y1], radius=int((x1 - x0) / 2), fill=color)
    cx, cy = T(0.545, 0.405)
    ring_shape(d, cx, cy, N * 0.155 * scale, N * 0.075 * scale, color)


def waves(d, y, color, width, x0=0.28, x1=0.72, n=2, h=0.045):
    seg = (x1 - x0) / n
    for i in range(n):
        a, b = N * (x0 + i * seg), N * (x0 + (i + 1) * seg)
        d.arc([a, N * (y - h), b, N * (y + h)], 180, 360,
              fill=color, width=int(width))


WHITE = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)


def p1():
    """经典粗体 P（修正版）：Pixiv 蓝"""
    base = gradient(N, '#00A5F0', '#0057B8', glow='#7FD4FF', glow_pos=(0.5, 0.2))
    layer = white_layer()
    draw_p(ImageDraw.Draw(layer), WHITE)
    return soft_shadow(base, layer)


def p2():
    """P + 海浪：PixHarbor 港湾点题（海洋蓝）"""
    base = gradient(N, '#0EA5E9', '#0C4A6E', glow='#7DD3FC', glow_pos=(0.5, 0.2))
    layer = white_layer()
    d = ImageDraw.Draw(layer)
    draw_p(d, WHITE, scale=0.88, dy=-0.055)
    waves(d, 0.735, WHITE, N * 0.032)
    return soft_shadow(base, layer)


def p3():
    """镂空 P：白色圆底 + 透出渐变的 P（青绿）"""
    base = gradient(N, '#14B8A6', '#0F766E', glow='#5EEAD4', glow_pos=(0.5, 0.2))
    layer = white_layer()
    d = ImageDraw.Draw(layer)
    r = N * 0.30
    d.ellipse([N / 2 - r, N / 2 - r, N / 2 + r, N / 2 + r], fill=WHITE)
    draw_p(d, CLEAR, scale=0.72)
    return soft_shadow(base, layer)


def p4():
    """P 画框融合：碗部变成小画框（山景+太阳），P 的变形体"""
    base = gradient(N, '#2F7CF6', '#1E3A8A', glow='#93C5FD', glow_pos=(0.5, 0.2))
    layer = white_layer()
    d = ImageDraw.Draw(layer)
    sl, sw = 0.37, 0.095
    d.rounded_rectangle([N * sl, N * 0.25, N * (sl + sw), N * 0.75],
                        radius=int(N * sw / 2), fill=WHITE)
    d.rounded_rectangle([N * 0.44, N * 0.25, N * 0.70, N * 0.51],
                        radius=int(N * 0.07), outline=WHITE, width=int(N * 0.032))
    sx, sy, sr = N * 0.635, N * 0.315, N * 0.022
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=WHITE)
    d.polygon([(N * 0.475, N * 0.465), (N * 0.53, N * 0.39), (N * 0.575, N * 0.44),
               (N * 0.61, N * 0.40), (N * 0.665, N * 0.465)], fill=WHITE)
    return soft_shadow(base, layer)


def p5():
    """帆船 P：竖笔作桅杆、碗部化作帆 + 底部海浪（夜港深蓝）"""
    base = gradient(N, '#0B2A5B', '#08122B', glow='#2F7CF6', glow_pos=(0.5, 0.2))
    layer = white_layer()
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([N * 0.37, N * 0.22, N * 0.465, N * 0.70],
                        radius=int(N * 0.0475), fill=WHITE)
    d.polygon([(N * 0.47, N * 0.24), (N * 0.63, N * 0.38),
               (N * 0.71, N * 0.58), (N * 0.47, N * 0.58)], fill=WHITE)
    waves(d, 0.745, WHITE, N * 0.03)
    return soft_shadow(base, layer)


def p6():
    """叠影 P：青/粉两个错位半透明 P 叠加（深夜底，插画社区感）"""
    base = gradient(N, '#101830', '#05070F', glow='#334170', glow_pos=(0.5, 0.25), glow_alpha=0.5)
    l1, l2 = white_layer(), white_layer()
    draw_p(ImageDraw.Draw(l1), (34, 211, 238, 215), dx=-0.028, dy=-0.022)
    draw_p(ImageDraw.Draw(l2), (244, 114, 182, 215), dx=0.028, dy=0.022)
    base = soft_shadow(base, l1, opacity=60)
    base.alpha_composite(l2)
    return base


def p7():
    """救生圈 P：海用救生圈 + 中心 P（暖橙，港湾安全意象）"""
    base = gradient(N, '#F97316', '#9A3412', glow='#FDBA74', glow_pos=(0.5, 0.2))
    layer = white_layer()
    d = ImageDraw.Draw(layer)
    cx = cy = N / 2
    ro, ri = N * 0.275, N * 0.205
    ring_shape(d, cx, cy, ro, ri, WHITE)
    for a in (45, 135, 225, 315):
        d.pieslice([cx - ro, cy - ro, cx + ro, cy + ro], a - 9, a + 9, fill=CLEAR)
    draw_p(d, WHITE, scale=0.55)
    return soft_shadow(base, layer)


def p8():
    """方块 P：P 被网格切成圆角卡片（瀑布流意象，紫）"""
    base = gradient(N, '#5B2A86', '#1A1040', glow='#A78BFA', glow_pos=(0.5, 0.25))
    layer = white_layer()
    d = ImageDraw.Draw(layer)
    draw_p(d, WHITE)
    gw = N * 0.016
    x = 0.30
    while x < 0.75:
        d.rectangle([N * x, 0, N * x + gw, N], fill=CLEAR)
        x += 0.11
    y = 0.25
    while y < 0.78:
        d.rectangle([0, N * y, N, N * y + gw], fill=CLEAR)
        y += 0.11
    return soft_shadow(base, layer)


ICONS = [p1, p2, p3, p4, p5, p6, p7, p8]
NAMES = ['1 经典P', '2 P+海浪', '3 镂空P', '4 P画框',
         '5 帆船P', '6 叠影P', '7 救生圈P', '8 方块P']


def main():
    imgs = []
    for i, fn in enumerate(ICONS, 1):
        im = finish(fn())
        p = os.path.join(OUT, f'icon_p{i}.png')
        im.save(p)
        imgs.append(im)
        print('saved', p)

    cell, pad, label_h = 360, 26, 44
    cols, rows = 4, 2
    sheet = Image.new('RGBA', (cols * cell + pad * (cols + 1),
                               rows * (cell + label_h) + pad * (rows + 1)), (243, 246, 251, 255))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 24)
    except Exception:
        font = ImageFont.load_default()
    for idx, im in enumerate(imgs):
        r, c = divmod(idx, cols)
        x = pad + c * (cell + pad)
        y = pad + r * (cell + label_h + pad)
        sheet.alpha_composite(im.resize((cell, cell), LANCZOS), (x, y))
        d.text((x, y + cell + 8), NAMES[idx], fill=(30, 41, 59, 255), font=font)
    sheet.convert('RGB').save(os.path.join(OUT, 'preview_p.png'))
    print('saved preview_p.png')


if __name__ == '__main__':
    main()
