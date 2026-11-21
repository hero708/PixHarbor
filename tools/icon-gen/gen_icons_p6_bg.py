# -*- coding: utf-8 -*-
"""PixHarbor 图标：6 号叠影 P 图案固定，仅更换背景配色（8 种）。"""
import os
from PIL import Image, ImageDraw, ImageFont
from gen_icons import (N, SIZE, OUT, gradient, white_layer, soft_shadow, finish, LANCZOS)
from gen_icons_p import draw_p

CYAN = (34, 211, 238, 215)
PINK = (244, 114, 182, 215)


def make(c1, c2, glow, glow_alpha=0.5, shadow=60):
    base = gradient(N, c1, c2, glow=glow, glow_pos=(0.5, 0.25), glow_alpha=glow_alpha)
    l1, l2 = white_layer(), white_layer()
    draw_p(ImageDraw.Draw(l1), CYAN, dx=-0.028, dy=-0.022)
    draw_p(ImageDraw.Draw(l2), PINK, dx=0.028, dy=0.022)
    base = soft_shadow(base, l1, opacity=shadow)
    base.alpha_composite(l2)
    return base


VARIANTS = [
    ('1 原版深夜', '#101830', '#05070F', '#334170', 0.5, 60),
    ('2 暗夜紫',   '#4C1D95', '#1E1B4B', '#8B5CF6', 0.5, 60),
    ('3 深海蓝',   '#0C4A6E', '#082F49', '#0EA5E9', 0.5, 60),
    ('4 海军蓝',   '#1E3A8A', '#0B1120', '#3B82F6', 0.5, 60),
    ('5 墨绿',     '#115E59', '#042F2E', '#2DD4BF', 0.5, 60),
    ('6 琥珀棕',   '#78350F', '#451A03', '#F59E0B', 0.45, 60),
    ('7 浅色白',   '#F8FAFC', '#D8E2F0', '#FFFFFF', 0.6, 30),
    ('8 Pixiv蓝',  '#00A5F0', '#0057B8', '#7FD4FF', 0.5, 40),
]


def main():
    imgs = []
    for i, (name, c1, c2, glow, ga, sh) in enumerate(VARIANTS, 1):
        im = finish(make(c1, c2, glow, ga, sh))
        p = os.path.join(OUT, f'icon_p6_bg{i}.png')
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
        d.text((x, y + cell + 8), VARIANTS[idx][0], fill=(30, 41, 59, 255), font=font)
    sheet.convert('RGB').save(os.path.join(OUT, 'preview_p6_bg.png'))
    print('saved preview_p6_bg.png')


if __name__ == '__main__':
    main()
