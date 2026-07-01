#!/usr/bin/env python3
"""
utils/create_placeholders.py
Run once to generate placeholder images so the app doesn't break
before any real images are uploaded.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')
os.makedirs(BASE, exist_ok=True)


def _make(filename, text, size=(200, 200), bg=(79, 70, 229), fg=(255, 255, 255)):
    img  = Image.new('RGB', size, color=bg)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
    except Exception:
        font = ImageFont.load_default()
    w, h = draw.textbbox((0, 0), text, font=font)[2:]
    draw.text(((size[0]-w)//2, (size[1]-h)//2), text, font=font, fill=fg)
    img.save(os.path.join(BASE, filename))
    print(f'Created {filename}')


if __name__ == '__main__':
    _make('default-avatar.png', 'No Photo',  (200, 200), (100, 116, 139))
    _make('no-image.png',       'No Image',  (400, 300), (148, 163, 184))
    print('Done.')
