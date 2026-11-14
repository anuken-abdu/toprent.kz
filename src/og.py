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
@font-face{{font-family:F;src:url({font('onest-cyrillic-wght-normal.woff2')});font-weight:200 800}}@font-face{{font-family:F;src:url({font('onest-latin-wght-normal.woff2')});font-weight:200 800;unicode-range:U+0000-00FF}}@font-face{{font-family:F;src:url({font('onest-tenge-wght.woff2')});font-weight:200 800;unicode-range:U+20B8}}
@font-face{{font-family:S;src:url({font('cormorant-garamond-cyrillic-500-italic.woff2')});font-style:italic}}
body{{margin:0;width:1200px;height:630px;background:radial-gradient(60% 70% at 50% 0,#14262a 0,#0a0b0c 70%);color:#f2f0eb;font-family:F;position:relative;overflow:hidden}}
.l{{position:absolute;left:80px;top:72px;font-size:26px;font-weight:300;letter-spacing:9px}}.l b{{font-weight:700}}.l i{{display:inline-block;width:8px;height:8px;border-radius:50%;background:#00e5ff;margin-left:2px;vertical-align:middle}}
h1{{position:absolute;left:76px;top:170px;margin:0;font-size:104px;font-weight:300;line-height:1.02;letter-spacing:-4px}}
h1 em{{font-family:S;font-weight:500;font-size:1.1em;letter-spacing:-1px}}
.f{{position:absolute;left:80px;right:80px;bottom:70px;display:flex;border-top:1px solid rgba(255,255,255,.14);font-size:30px;font-weight:300;letter-spacing:-.5px}}
.f div{{flex:1;padding:26px 0 0}}.f div+div{{border-left:1px solid rgba(255,255,255,.14);padding-left:30px}}
</style></head><body><div class="l"><b>TOP</b>RENT<i></i></div>
<h1>Аренда авто <em>без<br>водителя</em> в Астане</h1>
<div class="f"><div>от {nb(MIN_PRICE)} ₸ / сутки</div><div>депозит {nb(DEPOSIT)} ₸</div><div>{PHONE_DISPLAY}</div></div></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    import tempfile, os
    fd, tmp = tempfile.mkstemp(suffix=".html"); os.write(fd, OG.encode()); os.close(fd)
    pg.goto(Path(tmp).as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
    pg.screenshot(path=str(A / "og.png")); os.unlink(tmp)
    svg = (A / "favicon.svg").read_text()
    for n, s in [("icon-512.png", 512), ("icon-192.png", 192), ("apple-touch-icon.png", 180), ("_48.png", 48), ("_32.png", 32), ("_16.png", 16)]:
        pg.set_viewport_size({"width": s, "height": s})
        pg.set_content(f'<html><body style="margin:0">{svg.replace("<svg ", f"<svg width={s} height={s} ")}</body></html>')
        pg.screenshot(path=str(A / n), omit_background=False)
    b.close()
# favicon.ico из png 16, 32 и 48
imgs = [(A / f"_{n}.png").read_bytes() for n in (16, 32, 48)]
hdr = struct.pack("<HHH", 0, 1, len(imgs)); off = 6 + 16 * len(imgs); ent = b""
for d, s in zip(imgs, (16, 32, 48)):
    ent += struct.pack("<BBBBHHII", s, s, 0, 0, 1, 32, len(d), off); off += len(d)
(A / "favicon.ico").write_bytes(hdr + ent + b"".join(imgs))
[(A / f"_{n}.png").unlink() for n in (16, 32, 48)]
print("og.png и иконки готовы")
