# -*- coding: utf-8 -*-
"""OG-картинка 1200×630 через Playwright (иконки и логотип — src/brand.py). Запуск: python3 src/og.py"""
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
body{{margin:0;width:1200px;height:630px;background:linear-gradient(160deg,#1c2026 0%,#0e1013 60%);color:#eceef1;font-family:F;position:relative;overflow:hidden}}
.l{{position:absolute;left:80px;top:64px;height:64px}}
h1{{position:absolute;left:76px;top:170px;margin:0;font-size:100px;font-weight:500;line-height:1.04;letter-spacing:-4px}}
h1 em{{font-style:normal;background:linear-gradient(180deg,#f3f4f6 0%,#cfd3d9 48%,#a9aeb6 100%);-webkit-background-clip:text;background-clip:text;color:transparent}}
.f{{position:absolute;left:80px;right:80px;bottom:70px;display:flex;border-top:1px solid rgba(255,255,255,.14);font-size:30px;font-weight:400;letter-spacing:-.5px;color:#c9ced5}}
.f div{{flex:1;padding:26px 0 0}}.f div+div{{border-left:1px solid rgba(255,255,255,.14);padding-left:30px}}
</style></head><body><img class="l" src="{(A / "logo-light-full.png").as_uri()}" alt="">
<h1>Аренда авто <em>без<br>водителя</em> в Астане</h1>
<div class="f"><div>от {nb(MIN_PRICE)} ₸ / сутки</div><div>депозит {nb(DEPOSIT)} ₸</div><div>{PHONE_DISPLAY}</div></div></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    import tempfile, os
    fd, tmp = tempfile.mkstemp(suffix=".html"); os.write(fd, OG.encode()); os.close(fd)
    pg.goto(Path(tmp).as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
    pg.screenshot(path=str(A / "og.png")); os.unlink(tmp)
    b.close()
print("og.png готова")
