# -*- coding: utf-8 -*-
"""Prixiv View 图标候选生成器：输出 8 版 1024x1024 PNG + 一张对比图。

参考 D:\\WorkSpace\\HarmonyApp\\tunbox-icon\\gen_icons.py 的成熟管线：
4x 超采样 + 渐变底 + 辉光 + 圆角蒙版 + 软阴影 + 对比图。
全部图形为原创程序化绘制，不含任何上游 PixLume 素材。
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
S = 4
SIZE = 1024
N = SIZE * S
R = int(N * 0.225)
LANCZOS = Image.Resampling.LANCZOS


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(size, top, bottom, glow=None, glow_pos=(0.5, 0.18), glow_r=0.55, glow_alpha=0.35):
    top, bottom = hex2rgb(top), hex2rgb(bottom)
    y = np.linspace(0, 1, size)[:, None]
    img = (np.array(top, dtype=float)[None, None, :] * (1 - y[:, :, None]) +
           np.array(bottom, dtype=float)[None, None, :] * y[:, :, None])
    img = np.repeat(img, size, axis=1)
    if glow:
        yy, xx = np.mgrid[0:size, 0:size]
        cx, cy = glow_pos[0] * size, glow_pos[1] * size
        r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (glow_r * size)
        w = np.clip(1 - r, 0, 1) ** 2 * glow_alpha
        g = np.array(hex2rgb(glow), dtype=float)
        img = img * (1 - w[:, :, None]) + g[None, None, :] * w[:, :, None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')


def round_mask(size=N, radius=R):
    m = Image.new('L', (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m


def white_layer():
    return Image.new('RGBA', (N, N), (0, 0, 0, 0))


def soft_shadow(base, layer, blur=28, offset=(0, 14), opacity=85):
    a = layer.split()[3].filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * opacity / 255)))
    base.alpha_composite(sh, offset)
    base.alpha_composite(layer)
    return base


def ring_shape(d, cx, cy, r_out, r_in, color):
    d.ellipse([cx - r_out, cy - r_out, cx + r_out, cy + r_out], fill=color)
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=(0, 0, 0, 0))


def frame_glyph(d, ink, ox=0.0, oy=0.0):
    """画框 + 山景 + 太阳（通用图片浏览语义），ox/oy 为整体偏移比例"""
    x0, y0, x1, y1 = N * (0.245 + ox), N * (0.245 + oy), N * (0.755 + ox), N * (0.755 + oy)
    d.rounded_rectangle([x0, y0, x1, y1], radius=int(N * 0.055),
                        outline=ink, width=int(N * 0.034))
    sx, sy, sr = N * (0.60 + ox), N * (0.385 + oy), N * 0.047
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=ink)
    pts = [(N * (0.305 + ox), N * (0.665 + oy)), (N * (0.445 + ox), N * (0.475 + oy)),
           (N * (0.545 + ox), N * (0.60 + oy)), (N * (0.625 + ox), N * (0.515 + oy)),
           (N * (0.715 + ox), N * (0.665 + oy))]
    d.polygon(pts, fill=ink)


# ---------- 8 个设计 ----------

def icon1():
    """画框山景：Pixiv 蓝渐变（通用图片浏览语义）"""
    base = gradient(N, '#00A5F0', '#0057B8', glow='#7FD4FF', glow_pos=(0.5, 0.2))
    layer = white_layer()
    frame_glyph(ImageDraw.Draw(layer), (255, 255, 255, 250))
    return soft_shadow(base, layer)


def icon2():
    """字母 P：圆头粗体（Pixiv 首字母）"""
    base = gradient(N, '#2F7CF6', '#1B2A8A', glow='#6FB1FF', glow_pos=(0.5, 0.22))
    layer = white_layer()
    d = ImageDraw.Draw(layer)
    stem_w = N * 0.095
    d.rounded_rectangle([N * 0.365, N * 0.255, N * 0.365 + stem_w, N * 0.745],
                        radius=int(stem_w / 2), fill=(255, 255, 255, 255))
    ring_shape(d, N * 0.505, N * 0.40, N * 0.155, N * 0.075, (255, 255, 255, 255))
    return soft_shadow(base, layer)


def icon3():
    """瀑布流：三列错落圆角卡片（App 核心交互）"""
    base = gradient(N, '#5B2A86', '#1A1040', glow='#A78BFA', glow_pos=(0.5, 0.25))
    layer = white_layer()
    d = ImageDraw.Draw(layer)
    w = N * 0.155
    rad = int(N * 0.032)
    cols = [
        (0.245, [(0.26, 0.46, 235), (0.50, 0.74, 190)]),
        (0.4225, [(0.26, 0.56, 255), (0.60, 0.74, 200)]),
        (0.60, [(0.26, 0.40, 200), (0.44, 0.74, 235)]),
    ]
    for x, tiles in cols:
        for y0, y1, a in tiles:
            d.rounded_rectangle([N * x, N * y0, N * x + w, N * y1],
                                radius=rad, fill=(255, 255, 255, a))
    return soft_shadow(base, layer)


def icon4():
    """「绘」字：微软雅黑粗体（配中文名 绘览/绘匣）"""
    base = gradient(N, '#0B3B3C', '#06202A', glow='#2DD4BF', glow_pos=(0.5, 0.25))
    layer = white_layer()
    d = ImageDraw.Draw(layer)
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', int(N * 0.50))
    except Exception:
        font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', int(N * 0.50))
    ch = '绘'
    bb = d.textbbox((0, 0), ch, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text((N / 2 - tw / 2 - bb[0], N * 0.52 - th / 2 - bb[1]), ch,
           font=font, fill=(255, 255, 255, 255))
    return soft_shadow(base, layer)


def icon5():
    """三色圆：青/粉/琥珀半透明叠色（插画调色盘意象）"""
    base = gradient(N, '#101830', '#05070F', glow='#334170', glow_pos=(0.5, 0.25), glow_alpha=0.5)
    layer = white_layer()
    d = ImageDraw.Draw(layer)
    r = N * 0.145
    for (cx, cy, c) in [(0.425, 0.42, (34, 211, 238, 215)),
                        (0.575, 0.42, (244, 114, 182, 215)),
                        (0.50, 0.565, (251, 191, 36, 215))]:
        d.ellipse([N * cx - r, N * cy - r, N * cx + r, N * cy + r], fill=c)
    return soft_shadow(base, layer, opacity=60)


def icon6():
    """画廊双框：前后两个错位画框（暖色夕阳）"""
    base = gradient(N, '#7A2E0E', '#2A0F05', glow='#FF9A3D', glow_pos=(0.5, 0.22))
    layer = white_layer()
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([N * 0.225, N * 0.225, N * 0.665, N * 0.665],
                        radius=int(N * 0.05), outline=(255, 255, 255, 130), width=int(N * 0.03))
    frame_glyph(d, (255, 255, 255, 250), ox=0.09, oy=0.09)
    return soft_shadow(base, layer)


def icon7():
    """眼睛浏览：宽椭圆 + 瞳孔（"看"的语义）"""
    base = gradient(N, '#0B2A5B', '#08122B', glow='#2F7CF6', glow_pos=(0.5, 0.22))
    layer = white_layer()
    d = ImageDraw.Draw(layer)
    cx, cy = N / 2, N / 2
    w, h = N * 0.30, N * 0.175
    d.ellipse([cx - w, cy - h, cx + w, cy + h], outline=(255, 255, 255, 250), width=int(N * 0.036))
    pr = N * 0.088
    d.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=(255, 255, 255, 255))
    hr = N * 0.026
    hx, hy = cx + pr * 0.42, cy - pr * 0.42
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(0, 0, 0, 0))
    return soft_shadow(base, layer)


def icon8():
    """浅色画框：白底 + 深蓝线稿（浅色主题/桌面更醒目）"""
    base = gradient(N, '#FFFFFF', '#E8EFF8', glow='#DCE7F5', glow_pos=(0.5, 0.15), glow_alpha=0.5)
    layer = white_layer()
    frame_glyph(ImageDraw.Draw(layer), (0, 87, 184, 255))
    return soft_shadow(base, layer, opacity=40)


ICONS = [icon1, icon2, icon3, icon4, icon5, icon6, icon7, icon8]
NAMES = ['1 画框山景', '2 字母P', '3 瀑布流', '4 绘字',
         '5 三色圆', '6 画廊双框', '7 眼睛', '8 浅色画框']


def finish(img):
    out = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    out.paste(img, (0, 0), round_mask())
    return out.resize((SIZE, SIZE), LANCZOS)


def main():
    imgs = []
    for i, fn in enumerate(ICONS, 1):
        im = finish(fn())
        p = os.path.join(OUT, f'icon_{i}.png')
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
    sheet.convert('RGB').save(os.path.join(OUT, 'preview.png'))
    print('saved preview.png')


if __name__ == '__main__':
    main()
