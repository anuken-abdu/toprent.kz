# -*- coding: utf-8 -*-
"""Фото машин: orig/<slug>-1.jpg … -4.jpg → assets/img/cars/<slug>-N-{480,800,1200}.webp.
EXIF и GPS удаляются (сохраняем только пиксели). Запуск локально: python3 src/images.py
Vercel ничего не пересжимает — берёт готовые файлы из assets/."""
import sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "orig"
OUT = ROOT / "assets" / "img" / "cars"
SIZES = (480, 800, 1200)
EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".heic"}

def main():
    sys.path.insert(0, str(ROOT / "src"))
    from data import CARS
    slugs = {c["slug"] for c in CARS}
    OUT.mkdir(parents=True, exist_ok=True)
    done, skipped = 0, []
    for f in sorted(SRC.glob("*")) if SRC.exists() else []:
        if f.suffix.lower() not in EXT: continue
        stem = f.stem.lower()
        slug, _, n = stem.rpartition("-")
        if slug not in slugs or n not in ("1", "2", "3", "4"):
            skipped.append(f.name); continue
        with Image.open(f) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")          # поворот по EXIF, затем EXIF выбрасываем
            w, h = im.size
            tw = 1536; th = 1024                                       # кадр 3:2
            if w / h > 1.5: nw = int(h * 1.5); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
            elif w / h < 1.5: nh = int(w / 1.5); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
            clean = Image.new("RGB", im.size); clean.paste(im)       # новый объект без метаданных
            for s in SIZES:
                clean.resize((s, round(s / 1.5)), Image.LANCZOS).save(OUT / f"{slug}-{n}-{s}.webp", "WEBP", quality=80, method=6)
        done += 1
    print(f"фото обработано: {done}" + (f"; пропущены (имя не по коду машины): {', '.join(skipped)}" if skipped else ""))

if __name__ == "__main__":
    main()
