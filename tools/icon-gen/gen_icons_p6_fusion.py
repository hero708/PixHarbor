# -*- coding: utf-8 -*-
"""叠影 P 融合增强版：7 的浅色白底 + 更饱和的青/粉 P（保留半透明叠影混色）。"""
import os
from PIL import Image, ImageDraw
from gen_icons import N, OUT, gradient, white_layer, soft_shadow, finish
from gen_icons_p import draw_p

# 比原版更深的青/粉（cyan-600 / pink-600），alpha 230：
# 白底上更清晰，同时保留两 P 交叠处的混色层次
CYAN = (8, 145, 178, 230)
PINK = (219, 39, 119, 230)


def main():
    base = gradient(N, '#F8FAFC', '#D8E2F0', glow='#FFFFFF',
                    glow_pos=(0.5, 0.25), glow_alpha=0.6)
    l1, l2 = white_layer(), white_layer()
    draw_p(ImageDraw.Draw(l1), CYAN, dx=-0.028, dy=-0.022)
    draw_p(ImageDraw.Draw(l2), PINK, dx=0.028, dy=0.022)
    base = soft_shadow(base, l1, opacity=30)
    base.alpha_composite(l2)
    im = finish(base)
    p = os.path.join(OUT, 'icon_p6_bg9.png')
    im.save(p)
    print('saved', p)


if __name__ == '__main__':
    main()
