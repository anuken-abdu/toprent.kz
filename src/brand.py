# -*- coding: utf-8 -*-
"""Логотип и иконки: orig/brand/night.png (белый на чёрном), day.png (чёрный на белом), fav.png (круглая иконка 512, прозрачный фон).
→ assets/logo-light.webp (белый, прозрачный фон; в дневной теме CSS делает его чёрным), иконки вкладки 16/32/48 (favicon.ico), 180, 192, 512.
Запуск: python3 src/brand.py"""
import struct, io
from pathlib import Path
from PIL import Image, ImageOps
ROOT = Path(__file__).resolve().parent.parent; O = ROOT / "orig" / "brand"; A = ROOT / "assets"

def logo():
    src = O / "night.png" if (O / "night.png").exists() else None
    if src:
        g = ImageOps.grayscale(Image.open(src).convert("RGB"))                    # белый знак на чёрном → яркость = прозрачность
    else:
        g = ImageOps.invert(ImageOps.grayscale(Image.open(O / "day.png").convert("RGB")))
    g = g.point(lambda v: 0 if v < 12 else min(255, int((v - 12) * 255 / 228)))   # чистый фон без серой дымки
    box = g.getbbox(); g = g.crop((max(0, box[0] - 2), max(0, box[1] - 2), min(g.width, box[2] + 2), min(g.height, box[3] + 2)))
    im = Image.new("RGBA", g.size, (255, 255, 255, 0)); im.putalpha(g)
    white = Image.new("RGBA", g.size, (255, 255, 255, 255)); white.putalpha(g)
    h = 80; w = round(g.width * h / g.height)                                      # 2,5× для высоты 32 px
    white.resize((w, h), Image.LANCZOS).save(A / "logo-light.webp", "WEBP", quality=90, method=6)
    white.save(A / "logo-light-full.png")                                           # для картинки соцсетей
    return w, h

def icons():
    im = Image.open(O / "fav.png").convert("RGBA")
    data = []
    for s in (16, 32, 48):
        b = io.BytesIO(); im.resize((s, s), Image.LANCZOS).save(b, "PNG"); data.append((s, b.getvalue()))
    hdr = struct.pack("<HHH", 0, 1, len(data)); off = 6 + 16 * len(data); ent = b""
    for s, d in data: ent += struct.pack("<BBBBHHII", s, s, 0, 0, 1, 32, len(d), off); off += len(d)
    (A / "favicon.ico").write_bytes(hdr + ent + b"".join(d for _, d in data))
    im.resize((32, 32), Image.LANCZOS).save(A / "favicon-32.png")
    for n, s in (("icon-192.png", 192), ("icon-512.png", 512)): im.resize((s, s), Image.LANCZOS).save(A / n, optimize=True)
    bg = Image.new("RGBA", (180, 180), (0, 0, 0, 255)); bg.alpha_composite(im.resize((164, 164), Image.LANCZOS), (8, 8))   # iPhone не любит прозрачность
    bg.convert("RGB").save(A / "apple-touch-icon.png", optimize=True)

if __name__ == "__main__":
    print("логотип", logo()); icons(); print("иконки готовы")
