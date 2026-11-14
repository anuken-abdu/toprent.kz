# -*- coding: utf-8 -*-
"""OG-картинка 1200×630 и иконки (png/ico) через Playwright. Запуск: python3 src/og.py"""
import sys, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from data import BRAND, CITY, MIN_PRICE, DEPOSIT, PHONE_DISPLAY
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent; A = ROOT / "assets"
nb = lambda n: f"{n:,}".replace(",", " ")
font = lambda f: (A / "fonts" / f).as_uri()
OG = f"""<html><head><style>
@font-face{{font-family:U;src:url({font('inter-tight-cyrillic-800-normal.woff2')})}}@font-face{{font-family:U;src:url({font('inter-tight-latin-800-normal.woff2')});unicode-range:U+0000-00FF}}
@font-face{{font-family:M;src:url({font('jetbrains-mono-cyrillic-500-normal.woff2')})}}@font-face{{font-family:M;src:url({font('jetbrains-mono-latin-500-normal.woff2')});unicode-range:U+0000-00FF}}
body{{margin:0;width:1200px;height:630px;background:#0d0d0d;color:#fff;font-family:U;position:relative;overflow:hidden}}
.t{{position:absolute;left:72px;top:64px;font-family:M;font-size:22px;letter-spacing:2px;text-transform:uppercase;color:#8e8e8e;display:flex;align-items:center;gap:16px}}
.t:before{{content:"";width:16px;height:16px;background:#00e5ff}}
h1{{position:absolute;left:68px;top:132px;margin:0;font-size:118px;line-height:.9;text-transform:uppercase;letter-spacing:-5px}}
h1 i{{font-style:normal;color:#6f6f6f}}
.f{{position:absolute;left:72px;right:72px;bottom:64px;display:flex;border-top:3px solid #fff;font-family:U;font-size:34px;letter-spacing:-1px}}
.f div{{flex:1;padding:22px 0 0}}.f div+div{{border-left:1px solid #2c2c2c;padding-left:28px}}
</style></head><body><div class="t">{BRAND} · {CITY}</div>
<h1>Аренда авто<br><i>без водителя</i></h1>
<div class="f"><div>от {nb(MIN_PRICE)} ₸/сутки</div><div>депозит {nb(DEPOSIT)} ₸</div><div>{PHONE_DISPLAY}</div></div></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.set_content(OG); pg.wait_for_timeout(400); pg.screenshot(path=str(A / "og.png"))
    svg = (A / "favicon.svg").read_text()
    for n, s in [("icon-512.png", 512), ("icon-192.png", 192), ("apple-touch-icon.png", 180), ("_32.png", 32), ("_16.png", 16)]:
        pg.set_viewport_size({"width": s, "height": s})
        pg.set_content(f'<html><body style="margin:0">{svg.replace("<svg ", f"<svg width={s} height={s} ")}</body></html>')
        pg.screenshot(path=str(A / n), omit_background=False)
    b.close()
# favicon.ico из png 16 и 32
imgs = [(A / "_16.png").read_bytes(), (A / "_32.png").read_bytes()]
hdr = struct.pack("<HHH", 0, 1, len(imgs)); off = 6 + 16 * len(imgs); ent = b""
for d, s in zip(imgs, (16, 32)):
    ent += struct.pack("<BBBBHHII", s, s, 0, 0, 1, 32, len(d), off); off += len(d)
(A / "favicon.ico").write_bytes(hdr + ent + b"".join(imgs))
(A / "_16.png").unlink(); (A / "_32.png").unlink()
print("og.png и иконки готовы")
