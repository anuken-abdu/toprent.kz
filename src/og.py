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
@font-face{{font-family:U;src:url({font('unbounded-cyrillic-800-normal.woff2')})}}@font-face{{font-family:U;src:url({font('unbounded-latin-800-normal.woff2')});unicode-range:U+0000-00FF}}
@font-face{{font-family:M;src:url({font('jetbrains-mono-cyrillic-500-normal.woff2')})}}@font-face{{font-family:M;src:url({font('jetbrains-mono-latin-500-normal.woff2')});unicode-range:U+0000-00FF}}
body{{margin:0;width:1200px;height:630px;background:#0a0a0a;color:#fff;font-family:U;position:relative;overflow:hidden}}
.b{{position:absolute;inset:28px;border:4px solid #fff}}
.t{{position:absolute;left:72px;top:70px;font-family:M;font-size:26px;color:#00e5ff}}
h1{{position:absolute;left:68px;top:120px;margin:0;font-size:92px;line-height:1.02;text-transform:uppercase;letter-spacing:-1px}}
h1 i{{font-style:normal;color:transparent;-webkit-text-stroke:3px #00e5ff}}
.f{{position:absolute;left:72px;right:72px;bottom:72px;display:flex;border:4px solid #fff;font-family:M;font-size:26px}}
.f div{{flex:1;padding:18px 22px;border-right:4px solid #fff}}.f div:last-child{{border-right:0;background:#00e5ff;color:#0a0a0a}}
</style></head><body><div class="b"></div><div class="t">{BRAND} · {CITY}</div>
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
