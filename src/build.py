# -*- coding: utf-8 -*-
"""Генератор сайта аренды авто без водителя: src/ → dist/. Запуск: python3 src/build.py
Фото машин: images/cars/<slug>-1.webp, -2, -3 (свои). Если своих нет — при сборке на Vercel
скачиваются текущие фото с topautorent.kz (по одной-две на машину)."""
import json, os, re, shutil, sys, html, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from data import *

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
VER = "1311261"
E = html.escape
CLS = {c["slug"]: c for c in CLASSES}
nb = lambda n: f"{n:,}".replace(",", " ")
rub = lambda n: f"{nb(n)} ₸"
WA = f"https://wa.me/{WA_NUMBER}"
def wa(text): return WA + "?text=" + urllib.request.quote(text)

# ---------------------------------------------------------------- иконки (линейные, 24×24)
_P = {
 "age": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>',
 "exp": '<path d="M3 12h4l3-8 4 16 3-8h4"/>',
 "doc": '<rect x="3" y="5" width="18" height="14"/><circle cx="9" cy="11" r="2"/><path d="M6 16c.6-1.5 1.7-2 3-2s2.4.5 3 2M14 10h4M14 13h4"/>',
 "dep": '<rect x="3" y="6" width="18" height="13"/><path d="M3 10h18M16 15h2"/>',
 "city": '<path d="M4 21V9l5-3v15M9 21V4l6 3v14M15 21v-9l5 2v7M2 21h20"/>',
 "taxi": '<path d="M5 16V11l2-5h10l2 5v5M3 16h18v3H3zM7 19v2M17 19v2"/><path d="M3 3l18 18"/>',
 "time": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>',
 "car": '<path d="M5 15l1.5-6h11L19 15M3 15h18v4H3zM6 19v2M18 19v2"/><circle cx="7" cy="17" r=".6"/><circle cx="17" cy="17" r=".6"/>',
 "chat": '<path d="M4 4h16v12H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
 "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3M15 8l2 2"/>',
 "phone": '<path d="M5 3h4l2 5-3 2a11 11 0 0 0 6 6l2-3 5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z"/>',
 "up": '<path d="M12 20V5M5 12l7-7 7 7"/>',
 "back": '<path d="M20 12H5M12 5l-7 7 7 7"/>',
 "x": '<path d="M5 5l14 14M19 5L5 19"/>',
 "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
 "bot": '<rect x="4" y="7" width="16" height="12"/><path d="M12 3v4M9 12v2M15 12v2M2 12v4M22 12v4"/>',
 "send": '<path d="M3 11l18-8-8 18-2-8z"/>',
 "pin": '<path d="M12 22s7-7 7-12a7 7 0 0 0-14 0c0 5 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
 "check": '<path d="M4 12l5 5L20 6"/>',
 "fit": '<path d="M5 12l5 5L20 7"/>',
}
def ic(n): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square" aria-hidden="true">{_P[n]}</svg>'
WA_IC = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.2-.2.3-.8 1-.9 1.1-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5.3-.5c.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.1-.3-.2-.6-.3zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4A9.8 9.8 0 1 1 12 21.8zm8.4-18.2A11.8 11.8 0 0 0 1.7 17.8L0 24l6.4-1.7A11.8 11.8 0 0 0 24 12a11.7 11.7 0 0 0-3.6-8.4z"/></svg>'

# ---------------------------------------------------------------- фото
IMG_EXT = (".webp", ".jpg", ".jpeg", ".png", ".avif")
def fetch(url, dst):
    if os.environ.get("NO_FETCH"): return False
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "Referer": "https://topautorent.kz/"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = r.read()
            if r.status != 200 or len(data) < 3000 or not r.headers.get("Content-Type", "").startswith("image/"): return False
        dst.write_bytes(data); return True
    except Exception as e:
        print("  фото не скачано:", url, type(e).__name__); return False

def photos(c):
    out_dir = DIST / "img" / "cars"; out_dir.mkdir(parents=True, exist_ok=True)
    res = []
    for i in (1, 2, 3):
        for ext in IMG_EXT:
            f = ROOT / "images" / "cars" / f"{c['slug']}-{i}{ext}"
            if f.exists():
                shutil.copyfile(f, out_dir / f.name); res.append(f"/img/cars/{f.name}"); break
    if not res:
        for i, url in enumerate(c["img"], 1):
            ext = os.path.splitext(url)[1].lower() or ".jpg"
            name = f"{c['slug']}-{i}{ext}"
            if fetch(url, out_dir / name): res.append(f"/img/cars/{name}")
    return res

# ---------------------------------------------------------------- общие блоки
def minify_css(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s*\n\s*", "", s)
    return re.sub(r"\s*([{};,>])\s*", r"\1", s).replace(";}", "}")
CSS = minify_css((ROOT / "src" / "styles.css").read_text(encoding="utf-8"))

def gtag():
    if not TAG_ID: return ""
    src = "gtm.js" if TAG_ID.startswith("GTM-") else "gtag/js"
    return (f'<script async src="https://www.googletagmanager.com/{src}?id={TAG_ID}"></script>\n'
            "<script>\n  window.dataLayer = window.dataLayer || [];\n  function gtag(){dataLayer.push(arguments);}\n  gtag('js', new Date());\n"
            + ("" if TAG_ID.startswith("GTM-") else f"  gtag('config', '{TAG_ID}');\n") + "</script>\n")

ORG = {"@type": "AutoRental", "@id": SITE_URL + "/#org", "name": BRAND, "url": SITE_URL + "/", "telephone": PHONE_TEL,
       "image": SITE_URL + "/assets/og.png", "logo": SITE_URL + "/assets/icon-512.png",
       "address": {"@type": "PostalAddress", "streetAddress": STREET, "addressLocality": CITY, "addressCountry": "KZ"},
       "areaServed": {"@type": "City", "name": CITY},
       "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": OPENS, "closes": CLOSES}],
       "priceRange": f"{nb(MIN_PRICE)}–{nb(max(c['price'] for c in CARS))} KZT", "currenciesAccepted": "KZT",
       "sameAs": [WA]}

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + u} for i, (n, u) in enumerate(items)]}
def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

NAV = [("Автопарк", "/avto/"), ("Цены", "/ceny/"), ("Условия", "/usloviya/"), ("Контакты", "/kontakty/")]
LOGO = f'<b>T</b><span>Top Autorent<small>аренда авто · {CITY}</small></span>'

def header(cur):
    nav = "".join(f'<a href="{u}"{" aria-current=page" if cur == u else ""}>{n}</a>' for n, u in NAV)
    dnav = "".join(f'<a href="{u}">{n}</a>' for n, u in [("Главная", "/")] + NAV + [(c["name"], f'/klass/{c["slug"]}/') for c in CLASSES])
    return f'''<a class="skip" href="#main">К содержимому</a>
<header class="hd"><div class="w">
<a class="logo" href="/">{LOGO}</a>
<nav class="nav" aria-label="Главное меню">{nav}</nav>
<a class="hd-tel" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
<button class="burger" type="button" aria-label="Открыть меню" aria-expanded="false" aria-controls="drawer">{ic("menu")}</button>
</div></header>
<div class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="Меню">
<div class="x"><b>{BRAND}</b><button type="button" data-close aria-label="Закрыть меню">{ic("x")}</button></div>
<nav aria-label="Меню">{dnav}</nav>
<a class="dt" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><p class="dh">Ежедневно {HOURS}</p>
</div>'''

def footer():
    cls = "".join(f'<a href="/klass/{c["slug"]}/">{c["name"]}</a>' for c in CLASSES)
    nav = "".join(f'<a href="{u}">{n}</a>' for n, u in NAV)
    return f'''<footer class="ft"><div class="w">
<div><a class="logo" href="/">{LOGO}</a><p class="fp">Аренда авто без водителя в Астане: эконом, бизнес, внедорожники и премиум. Ежедневно {HOURS}.</p></div>
<div><h3>Классы</h3>{cls}</div>
<div><h3>Разделы</h3>{nav}<a href="/privacy-policy/">Политика конфиденциальности</a></div>
<div><h3>Контакты</h3><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><a href="{WA}" target="_blank" rel="noopener">WhatsApp</a><p>{ADDRESS}</p><p>Ежедневно {HOURS}</p></div>
<div class="bt"><span>© {BRAND}, {CITY}</span><span>Разработка и продвижение — <a href="{DEV[1]}" target="_blank" rel="noopener">{DEV[0]}</a></span></div>
</div></footer>'''

def fab():
    q = "".join(f"<button type=button>{x}</button>" for x in ["Какие нужны документы?", "Какой депозит?", "Можно за город?", "Цены"])
    return f'''<div class="fab">
<a class="sm" href="/" data-back aria-label="Назад" title="Назад">{ic("back")}</a>
<button class="sm" type="button" data-top hidden aria-label="Наверх" title="Наверх">{ic("up")}</button>
<div class="fab-p" id="fabp" hidden>
<a href="{wa("Здравствуйте! Хочу арендовать авто.")}" target="_blank" rel="noopener">{WA_IC}<span>WhatsApp<small>ответим в чате</small></span></a>
<a href="tel:{PHONE_TEL}">{ic("phone")}<span>Позвонить<small>{PHONE_DISPLAY}</small></span></a>
<button type="button" data-chat>{ic("bot")}<span>ИИ-консультант<small>ответит сразу</small></span></button>
</div>
<button class="fab-m" type="button" aria-label="Связаться: WhatsApp, звонок, ИИ-чат" aria-expanded="false" aria-controls="fabp">{ic("chat")}</button>
</div>
<section class="chat" id="chat" hidden aria-label="ИИ-консультант">
<div class="chat-h"><span><b>ИИ-консультант</b><small>машины, цены, условия</small></span><button type="button" data-chat-x aria-label="Закрыть чат">{ic("x")}</button></div>
<div class="chat-l" aria-live="polite"></div>
<div class="chat-q">{q}</div>
<form class="chat-f"><label class="sr" for="cq">Ваш вопрос</label><input id="cq" name="q" autocomplete="off" placeholder="Ваш вопрос" maxlength="500"><button type="submit" aria-label="Отправить">{ic("send")}</button></form>
<a class="chat-w" href="{wa("Здравствуйте! Хочу арендовать авто.")}" target="_blank" rel="noopener">{WA_IC}Написать менеджеру в WhatsApp</a>
</section>'''

def page(path, title, desc, body, cur="", ld=None, preload=None, og=None, noindex=False):
    url = SITE_URL + path
    cfg = json.dumps({"wa": WA_NUMBER, "dep": DEPOSIT, "phone": PHONE_DISPLAY, "addr": STREET, "brand": BRAND, "ads": GADS_ID, "label": GADS_LABEL}, ensure_ascii=False)
    graph = [ORG, {"@type": "WebSite", "@id": SITE_URL + "/#site", "url": SITE_URL + "/", "name": BRAND, "inLanguage": "ru"}] + (ld or [])
    og_img = og or SITE_URL + "/assets/og.png"
    pre = f'<link rel="preload" as="image" href="{preload}" fetchpriority="high">\n' if preload else ""
    doc = f'''<!doctype html>
<html lang="ru">
<head>
{gtag()}<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
{'<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'}
<meta name="theme-color" content="#0a0a0a">
<meta property="og:type" content="website"><meta property="og:locale" content="ru_RU"><meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="32x32"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/unbounded-cyrillic-800-normal.woff2" as="font" type="font/woff2" crossorigin>
{pre}<style>{CSS}</style>
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)}</script>
</head>
<body>
{header(cur)}
<main id="main">
{body}
</main>
{footer()}
{fab()}
<script>window.__C={cfg}</script>
<script src="/assets/app.js?v={VER}" defer></script>
</body>
</html>
'''
    out = DIST / path.strip("/") / "index.html" if path != "/404.html" else DIST / "404.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    if path != "/404.html" and not noindex: SITEMAP.append(path)

SITEMAP = []

# ---------------------------------------------------------------- блоки контента
def year(c): return f"{c['year']} г." if c["year"] else "год уточняйте"
def cls_names(c): return " · ".join(CLS[x]["name"] for x in c["cls"])

def meta_cls(c):
    k = [x for x in c["cls"] if not (x == "vnedorozhniki" and c["body"] in ("Внедорожник", "Кроссовер"))] or c["cls"]
    return CLS[k[-1]]["name"]

def card(c, eager=False):
    ph = c["ph"]
    img = (f'<img src="{ph[0]}" alt="{E(c["full"])} — аренда в Астане" width="768" height="597" loading="{"eager" if eager else "lazy"}" decoding="async">'
           if ph else f'<div class="ph-x" aria-hidden="true">{ic("car")}<span>фото скоро</span></div>')
    meta = " · ".join(x for x in [str(c["year"]) if c["year"] else "", c["body"], meta_cls(c)] if x)
    return f'''<article class="card" data-cls="{" ".join(c["cls"])}" data-p="{c["price"]}">
<div class="ph">{img}</div>
<div class="cb"><h3><a href="/avto/{c["slug"]}/">{E(c["short"])}</a></h3><p class="meta">{E(meta)}</p>
<div class="pr"><b>{rub(c["price"])}</b><span>за сутки</span></div>
<a class="go" href="{wa(f"Здравствуйте! Хочу арендовать {c['full']}.")}" target="_blank" rel="noopener">{WA_IC}Забронировать</a></div>
</article>'''

def cards(lst, eager=0): return '<div class="cards" data-grid>' + "".join(card(c, i < eager) for i, c in enumerate(lst)) + "</div>"

def filters():
    b = '<button type="button" data-f="all" aria-pressed="true">Все</button>' + "".join(f'<button type="button" data-f="{c["slug"]}" aria-pressed="false">{c["name"]}</button>' for c in CLASSES)
    return f'<div class="flt" role="group" aria-label="Фильтр по классу">{b}<button type="button" class="srt" data-sort title="Сортировка по цене">Цена ↑</button></div>'

def terms_html():
    t = "".join(f'<div class="term{" neg" if k == "taxi" else ""}"><span class="ic">{ic(k)}</span><h3>{E(h)}</h3><p>{E(p)}</p></div>' for k, h, p in TERMS)
    t += f'<a class="term cta" href="{wa("Здравствуйте! Вопрос по условиям аренды.")}" target="_blank" rel="noopener"><span class="ic">{WA_IC}</span><h3>Остались вопросы?</h3><p>Напишите в WhatsApp — ответим по условиям, датам и доставке.</p></a>'
    r = "".join(f"<li>{E(x)}</li>" for x in RULES)
    return f'<div class="terms">{t}</div><ul class="rules">{r}</ul>'

def steps_html():
    return '<div class="steps">' + "".join(f'<div class="step"><span class="ic">{ic(k)}</span><h3>{E(h)}</h3><p>{E(p)}</p></div>' for k, h, p in STEPS) + "</div>"

def faq_html(faq): return '<div class="faq">' + "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq) + "</div>"

def class_tiles():
    out = ""
    for c in CLASSES:
        lst = [x for x in CARS if c["slug"] in x["cls"]]
        out += f'<a href="/klass/{c["slug"]}/"><b>{c["name"]}</b><span>{len(lst)} {plural(len(lst))}</span><i>от {rub(min(x["price"] for x in lst))}/сут →</i></a>'
    return f'<div class="cls">{out}</div>'

def plural(n):
    n = abs(n) % 100; m = n % 10
    return "машин" if 10 < n < 20 else "машина" if m == 1 else "машины" if 2 <= m <= 4 else "машин"

def book(sel=None):
    opts = '<option value="" data-p="0">Подберите мне машину</option>' + "".join(
        f'<option value="{c["slug"]}" data-p="{c["price"]}" data-n="{E(c["full"])}"{" selected" if sel and c["slug"] == sel["slug"] else ""}>{E(c["full"])} — {rub(c["price"])}</option>' for c in sorted(CARS, key=lambda x: x["price"]))
    title = f"Забронировать {E(sel['full'])}" if sel else "Забронировать машину"
    return f'''<section class="s dk" id="bron"><div class="w book">
<div class="bk-l"><span class="tag cy">Бронь</span><h2>{title}</h2><p class="lead" style="margin-top:16px">Выберите даты — посчитаем стоимость. Заявка уйдёт менеджеру в WhatsApp, он подтвердит, что машина свободна.</p>
<ul><li>{ic("check")}<span>Удостоверение личности и водительские права</span></li><li>{ic("check")}<span>Возраст от 20 лет, стаж от 2 лет</span></li><li>{ic("check")}<span>Депозит {rub(DEPOSIT)} — вернём сразу после возврата авто</span></li><li>{ic("check")}<span>Ежедневно {HOURS}</span></li></ul></div>
<form class="form" id="book" novalidate>
<label class="full">Машина<select name="car">{opts}</select></label>
<label>Дата начала<input type="date" name="d1"></label>
<label>Дата возврата<input type="date" name="d2"></label>
<div class="calc" data-calc aria-live="polite"></div>
<label>Имя<input name="name" autocomplete="given-name" placeholder="Как к вам обращаться"></label>
<label>Телефон<input name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 7__ ___ __ __" required></label>
<button class="btn c full" type="submit">{WA_IC}Отправить в WhatsApp</button>
<small>Нажимая кнопку, вы соглашаетесь с <a href="/privacy-policy/">политикой конфиденциальности</a>. Итоговую стоимость подтвердит менеджер.</small>
</form></div></section>'''

def crumbs(items):
    out = []
    for i, (n, u) in enumerate(items):
        out.append(f'<span aria-current="page">{E(n)}</span>' if i == len(items) - 1 else f'<a href="{u}">{E(n)}</a><span aria-hidden="true">/</span>')
    return f'<nav class="crumbs w" aria-label="Хлебные крошки">{"".join(out)}</nav>'

# ---------------------------------------------------------------- страницы
def build_home():
    by_price = sorted(CARS, key=lambda c: c["price"])
    rows = "".join(f'<a href="/klass/{k["slug"]}/"><b>{k["name"]}</b><span>от {rub(min(x["price"] for x in CARS if k["slug"] in x["cls"]))}</span></a>' for k in CLASSES)
    body = f'''<section class="hero dk"><div class="w hero-g">
<div><h1>Аренда авто <span class="o">без водителя</span> <span class="cy">в Астане</span></h1>
<p class="lead">{len(CARS)} {plural(len(CARS))} — от Hyundai Accent до Mercedes G63. От {rub(MIN_PRICE)} в сутки, депозит {rub(DEPOSIT)} возвращаем сразу после возврата авто.</p>
<div class="act"><a class="btn c" href="#park">{ic("car")}Выбрать машину</a><a class="btn k" href="{wa("Здравствуйте! Хочу арендовать авто.")}" target="_blank" rel="noopener">{WA_IC}Написать в WhatsApp</a></div></div>
<nav class="hcls" aria-label="Классы машин"><p class="mo">Классы · цена за сутки</p>{rows}</nav>
<div class="facts"><div><b>от 20 лет</b><span>возраст водителя</span></div><div><b>2 года</b><span>минимальный стаж</span></div><div><b>{rub(DEPOSIT)}</b><span>депозит, вернём сразу</span></div><div><b>{HOURS}</b><span>ежедневно</span></div></div>
</div></section>
'''
    body += f'''<section class="s gr" id="park"><div class="w"><div class="sh"><h2>Автопарк</h2><p>Цена за сутки. У каждой машины своя страница с фото и условиями.</p></div>{filters()}{cards(by_price, 4)}</div></section>
<section class="s" id="usloviya"><div class="w"><div class="sh"><h2>Условия аренды</h2><p>Коротко и без мелкого шрифта. Подробнее — на странице <a href="/usloviya/">«Условия»</a>.</p></div>{terms_html()}</div></section>
<section class="s dk"><div class="w"><div class="sh"><h2>Как арендовать</h2><p>Без лишних бумаг: документы, оплата, депозит — и машина ваша.</p></div>{steps_html()}</div></section>
<section class="s"><div class="w"><div class="sh"><h2>Вопросы</h2></div>{faq_html(FAQ)}</div></section>
{book()}
{contacts_block()}'''
    items = {"@type": "ItemList", "name": "Автопарк", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE_URL}/avto/{c['slug']}/", "name": c["full"]} for i, c in enumerate(by_price)]}
    page("/", f"Аренда авто без водителя в Астане — от {nb(MIN_PRICE)} ₸/сутки | {BRAND}",
         f"Аренда авто без водителя в Астане: {len(CARS)} машин от Hyundai Accent до Mercedes G63, от {nb(MIN_PRICE)} ₸ в сутки. С 20 лет, стаж 2 года, депозит 20 000 ₸. Ежедневно 10:00–23:00.",
         body, "/", [faq_ld(FAQ), items])

def contacts_block():
    maps = "https://www.google.com/maps/search/?api=1&query=" + urllib.request.quote(f"{BRAND} {ADDRESS}")
    return f'''<section class="s" id="kontakty"><div class="w"><div class="sh"><h2>Контакты</h2><p>Перед приездом позвоните или напишите — подготовим машину и документы.</p></div>
<div class="ct"><div><span>Телефон</span><a class="v" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></div>
<div><span>WhatsApp</span><a class="v" href="{wa("Здравствуйте! Хочу арендовать авто.")}" target="_blank" rel="noopener">Написать</a></div>
<div><span>Адрес</span><a class="v" href="{maps}" target="_blank" rel="noopener">{E(STREET)}</a></div>
<div><span>График</span><b>Ежедневно {HOURS}</b></div></div></div></section>'''

def build_park():
    lst = sorted(CARS, key=lambda c: c["price"])
    body = f'''{crumbs([("Главная", "/"), ("Автопарк", "/avto/")])}
<section class="s gr" style="padding-top:24px"><div class="w"><div class="sh"><div><h1>Автопарк</h1><p class="lead" style="margin-top:14px">{len(CARS)} {plural(len(CARS))} без водителя в Астане — эконом, бизнес, внедорожники и премиум. Цена за сутки, депозит {rub(DEPOSIT)}.</p></div></div><h2 class="sr">Все машины</h2>{filters()}{cards(lst, 4)}</div></section>
<section class="s"><div class="w"><div class="sh"><h2>Условия аренды</h2></div>{terms_html()}</div></section>
{book()}'''
    page("/avto/", f"Автопарк — аренда авто в Астане без водителя | {BRAND}",
         f"Все машины для аренды без водителя в Астане с ценами: Hyundai, Kia, Toyota, Lexus, Mercedes. От {nb(MIN_PRICE)} ₸ в сутки, депозит 20 000 ₸.",
         body, "/avto/", [crumbs_ld([("Главная", "/"), ("Автопарк", "/avto/")])])

def car_faq(c):
    return [(f"Сколько стоит аренда {c['full']} в Астане?", f"{rub(c['price'])} в сутки. Плюс депозит {rub(DEPOSIT)}, его вернём сразу после возврата машины."),
            (f"Что нужно, чтобы взять {c['name']} без водителя?", "Удостоверение личности и водительские права. Возраст — от 20 лет, стаж — от 2 лет."),
            (f"Можно ли выехать на {c['name']} за город?", "Машина выдаётся для поездок по Астане. Выезд за город — по согласованию и с доплатой, сумма зависит от направления."),
            ("Можно ли работать на машине в такси?", "Нет, под режим такси и другую работу машины не выдаём.")]

def build_cars():
    for c in CARS:
        p = c["ph"]; path = f"/avto/{c['slug']}/"
        if p:
            main = f'<img src="{p[0]}" alt="{E(c["full"])} — фото 1" width="768" height="597" fetchpriority="high" decoding="async">'
            th = "".join(f'<button type="button" data-src="{u}" aria-label="Фото {i + 1}" aria-current="{"true" if i == 0 else "false"}"><img src="{u}" alt="" width="256" height="199" loading="lazy" decoding="async"></button>' for i, u in enumerate(p))
            th += "".join('<button type="button" class="emp" disabled aria-hidden="true" tabindex="-1">фото скоро</button>' for _ in range(3 - len(p)))
        else:
            main = f'<div class="ph-x" aria-hidden="true">{ic("car")}<span>фото скоро</span></div>'
            th = ""
        sim = sorted([x for x in CARS if x is not c and set(x["cls"]) & set(c["cls"])], key=lambda x: abs(x["price"] - c["price"]))[:3]
        fit = "".join(f"<li>{E(x)}</li>" for x in c["fit"])
        cl = c["cls"][0]
        rows = [("Марка", c["brand"]), ("Модель", c["model"]), ("Год", str(c["year"]) if c["year"] else "уточняйте у менеджера"), ("Кузов", c["body"]),
                ("Класс", cls_names(c)), ("Цена", f"{rub(c['price'])} / сутки"), ("Депозит", f"{rub(DEPOSIT)}, возвращается сразу"), ("Эксплуатация", "по Астане; за город — с доплатой")]
        spec = "".join(f"<tr><th scope=row>{E(a)}</th><td>{E(b)}</td></tr>" for a, b in rows)
        cr = [("Главная", "/"), ("Автопарк", "/avto/"), (CLS[cl]["name"], f"/klass/{cl}/"), (c["full"], path)]
        body = f'''{crumbs(cr)}
<section class="w car-top">
<div class="gal"><div class="gal-m">{main}</div>{f'<div class="gal-t">{th}</div>' if th else ""}</div>
<div class="info"><h1>Аренда {E(c["full"])} в Астане</h1><p class="lead">{E(c["about"])}</p>
<div class="price"><div class="c1"><b>{rub(c["price"])}</b><span>в сутки</span></div><div><b>{rub(DEPOSIT)}</b><span>депозит, вернём сразу</span></div></div>
<div class="act"><a class="btn c" href="#bron">{ic("key")}Забронировать</a><a class="btn k" href="{wa(f"Здравствуйте! Хочу арендовать {c['full']}.")}" target="_blank" rel="noopener">{WA_IC}WhatsApp</a></div>
<table class="spec"><caption class="sr">Характеристики и условия</caption>{spec}</table>
<ul class="fit" aria-label="Подходит для">{fit}</ul></div>
</section>
<section class="s gr" style="border-top:var(--b)"><div class="w"><div class="sh"><h2>Условия аренды</h2></div>{terms_html()}</div></section>
{book(c)}
<section class="s"><div class="w"><div class="sh"><h2>Вопросы о {E(c["name"])}</h2></div>{faq_html(car_faq(c))}</div></section>
<section class="s gr"><div class="w"><div class="sh"><h2>Похожие машины</h2><p><a href="/klass/{cl}/">Все машины класса «{CLS[cl]["name"]}» →</a></p></div><div class="cards">{"".join(card(x) for x in sim)}</div></div></section>'''
        prod = {"@type": "Product", "name": f"Аренда {c['full']} без водителя", "brand": {"@type": "Brand", "name": c["brand"]},
                "description": c["about"], "category": "Аренда автомобилей",
                "offers": {"@type": "Offer", "price": c["price"], "priceCurrency": "KZT", "availability": "https://schema.org/InStock", "url": SITE_URL + path,
                           "seller": {"@id": SITE_URL + "/#org"},
                           "priceSpecification": {"@type": "UnitPriceSpecification", "price": c["price"], "priceCurrency": "KZT", "unitCode": "DAY", "referenceQuantity": {"@type": "QuantitativeValue", "value": 1, "unitCode": "DAY"}}}}
        if p: prod["image"] = [SITE_URL + u for u in p]
        t = f"Аренда {c['full']} в Астане — {nb(c['price'])} ₸/сутки"
        if len(t) <= 57: t += " без водителя"
        d = f"{c['full']} в аренду без водителя в Астане за {nb(c['price'])} ₸ в сутки. {c['body']}, {cls_names(c).lower()}. Депозит 20 000 ₸, с 20 лет, стаж 2 года."
        if len(d) > 160: d = f"{c['full']} без водителя в Астане за {nb(c['price'])} ₸ в сутки. Депозит 20 000 ₸, с 20 лет, стаж 2 года."
        page(path, t, d,
             body, "/avto/", [crumbs_ld(cr), prod, faq_ld(car_faq(c))], preload=p[0] if p else None, og=(SITE_URL + p[0]) if p else None)

def build_classes():
    for k in CLASSES:
        lst = sorted([c for c in CARS if k["slug"] in c["cls"]], key=lambda c: c["price"])
        lo, hi = min(c["price"] for c in lst), max(c["price"] for c in lst)
        faq = [(f"Сколько стоит аренда авто {k['short']} в Астане?", f"От {rub(lo)} до {rub(hi)} в сутки. Плюс депозит {rub(DEPOSIT)} — вернём сразу после возврата машины."),
               (f"Какие машины {k['short']} есть?", ", ".join(c["full"] for c in lst) + "."),
               ("Какие условия аренды?", "Возраст от 20 лет, стаж от 2 лет, удостоверение личности и права. Эксплуатация по Астане, выезд за город — по согласованию с доплатой. Под такси не выдаём.")]
        tabs = "".join(f'<a href="/klass/{c["slug"]}/"{" aria-current=page" if c is k else ""}>{c["name"]}</a>' for c in CLASSES)
        cr = [("Главная", "/"), ("Автопарк", "/avto/"), (k["name"], f"/klass/{k['slug']}/")]
        body = f'''{crumbs(cr)}
<section class="s gr" style="padding-top:24px"><div class="w"><div class="sh"><div><h1>{E(k["h1"])}</h1><p class="lead" style="margin-top:14px">{E(k["lead"])} От {rub(lo)} в сутки.</p></div></div>
<h2 class="sr">Машины класса «{k["name"]}»</h2><div class="flt" aria-label="Классы">{tabs}</div>{cards(lst, 4)}</div></section>
<section class="s"><div class="w"><div class="sh"><h2>Условия аренды</h2></div>{terms_html()}</div></section>
{book()}
<section class="s"><div class="w"><div class="sh"><h2>Вопросы</h2></div>{faq_html(faq)}</div></section>'''
        page(f"/klass/{k['slug']}/", f"{k['title']} — от {nb(lo)} ₸/сутки",
             f"{k['h1']} без водителя: {', '.join(c['short'] for c in lst[:3])}. От {nb(lo)} ₸ в сутки, депозит 20 000 ₸, с 20 лет.",
             body, "/avto/", [crumbs_ld(cr), faq_ld(faq)])

def build_prices():
    lst = sorted(CARS, key=lambda c: c["price"])
    rows = "".join(f'<tr><td><a href="/avto/{c["slug"]}/">{E(c["full"])}</a></td><td class="hm">{E(c["body"])}</td><td class="hm">{E(cls_names(c))}</td><td>{rub(c["price"])}</td></tr>' for c in lst)
    cr = [("Главная", "/"), ("Цены", "/ceny/")]
    faq = [FAQ[5], FAQ[2], ("Есть ли скидка при аренде на несколько дней?", "Условия на длительный срок уточняйте у менеджера в WhatsApp или по телефону " + PHONE_DISPLAY + ".")]
    body = f'''{crumbs(cr)}
<section class="s" style="padding-top:24px"><div class="w"><div class="sh"><div><h1>Цены на аренду авто</h1><p class="lead" style="margin-top:14px">Стоимость аренды без водителя в Астане за сутки. К аренде добавляется депозит {rub(DEPOSIT)} — возвращаем сразу после возврата машины.</p></div></div>
<table class="tbl"><thead><tr><th scope=col>Машина</th><th scope=col class="hm">Кузов</th><th scope=col class="hm">Класс</th><th scope=col>За сутки</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<section class="s gr"><div class="w"><div class="sh"><h2>Что входит и что нет</h2></div>{terms_html()}</div></section>
{book()}
<section class="s"><div class="w"><div class="sh"><h2>Вопросы о цене</h2></div>{faq_html(faq)}</div></section>'''
    page("/ceny/", f"Цены на аренду авто в Астане без водителя — от {nb(MIN_PRICE)} ₸ | {BRAND}",
         f"Прайс на аренду авто без водителя в Астане: {len(CARS)} машин от {nb(MIN_PRICE)} до {nb(lst[-1]['price'])} ₸ в сутки. Депозит 20 000 ₸, возвращается сразу.",
         body, "/ceny/", [crumbs_ld(cr), faq_ld(faq)])

def build_terms():
    cr = [("Главная", "/"), ("Условия", "/usloviya/")]
    body = f'''{crumbs(cr)}
<section class="s" style="padding-top:24px"><div class="w"><div class="sh"><div><h1>Условия аренды</h1><p class="lead" style="margin-top:14px">Кто может взять машину, какие нужны документы, сколько депозит и куда можно ездить.</p></div></div>{terms_html()}</div></section>
<section class="s dk"><div class="w"><div class="sh"><h2>Как арендовать</h2></div>{steps_html()}</div></section>
<section class="s"><div class="w"><div class="sh"><h2>Вопросы</h2></div>{faq_html(FAQ)}</div></section>
{book()}'''
    page("/usloviya/", "Условия аренды авто в Астане: с 20 лет, депозит 20 000 ₸",
         "Условия аренды авто без водителя в Астане: возраст от 20 лет, стаж от 2 лет, удостоверение и права, депозит 20 000 ₸ возвращается сразу. Не под такси.",
         body, "/usloviya/", [crumbs_ld(cr), faq_ld(FAQ)])

def build_contacts():
    cr = [("Главная", "/"), ("Контакты", "/kontakty/")]
    body = f'''{crumbs(cr)}
<section class="s" style="padding-top:24px;border-bottom:0"><div class="w"><h1>Контакты</h1><p class="lead" style="margin:14px 0 0">{BRAND} — аренда авто без водителя в Астане. Ежедневно {HOURS}.</p></div></section>
{contacts_block()}
{book()}'''
    page("/kontakty/", f"Контакты — аренда авто в Астане | {BRAND}",
         f"Аренда авто без водителя в Астане: {PHONE_DISPLAY}, WhatsApp, {STREET}. Ежедневно с 10:00 до 23:00.",
         body, "/kontakty/", [crumbs_ld(cr)])

def build_privacy():
    body = f'''{crumbs([("Главная", "/"), ("Политика конфиденциальности", "/privacy-policy/")])}
<section class="s" style="padding-top:24px"><div class="w prose"><h1>Политика конфиденциальности</h1>
<h2>Какие данные мы получаем</h2><p>Имя, номер телефона и даты аренды, которые вы указываете в форме бронирования или пишете в WhatsApp, а также вопросы в ИИ-чате.</p>
<h2>Зачем</h2><p>Чтобы ответить на заявку, проверить, свободна ли машина, и оформить аренду. Мы не продаём и не передаём ваши данные третьим лицам, кроме случаев, предусмотренных законодательством Республики Казахстан.</p>
<h2>Как отправляются данные</h2><p>Форма бронирования не хранит данные на сайте: заявка открывается в WhatsApp, и вы сами отправляете сообщение. Вопросы в ИИ-чате обрабатываются только для ответа и не используются для рекламы.</p>
<h2>Аналитика</h2><p>Сайт может использовать Google Analytics и Google Ads, чтобы считать посещения и обращения. Эти сервисы используют файлы cookie; их можно отключить в настройках браузера.</p>
<h2>Связь</h2><p>Вопросы о данных — по телефону <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> или в WhatsApp.</p></div></section>'''
    page("/privacy-policy/", f"Политика конфиденциальности | {BRAND}", f"Как {BRAND} обрабатывает данные из формы бронирования и ИИ-чата.", body, noindex=False)

def build_404():
    body = f'''<section class="w p404"><div><h1>404</h1><p class="lead" style="margin:10px auto 26px">Такой страницы нет. Машины — в автопарке.</p><a class="btn c" href="/avto/">{ic("car")}Автопарк</a></div></section>'''
    page("/404.html", f"Страница не найдена | {BRAND}", "Страница не найдена.", body, noindex=True)

# ---------------------------------------------------------------- служебные файлы
def build_meta():
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    sm = "".join(f"<url><loc>{SITE_URL}{p}</loc><changefreq>weekly</changefreq><priority>{'1.0' if p == '/' else '0.8' if p.startswith(('/avto/', '/klass/')) else '0.6'}</priority></url>" for p in SITEMAP)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n', encoding="utf-8")
    (DIST / "site.webmanifest").write_text(json.dumps({"name": BRAND, "short_name": "TopAutorent", "start_url": "/", "display": "standalone", "background_color": "#0a0a0a", "theme_color": "#0a0a0a",
        "icons": [{"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False), encoding="utf-8")
    fleet = "\n".join(f"- {c['full']} — {nb(c['price'])} ₸/сутки; {c['body'].lower()}, {cls_names(c).lower()}: {SITE_URL}/avto/{c['slug']}/" for c in sorted(CARS, key=lambda c: c["price"]))
    terms = "\n".join(f"- {h}: {p}" for _, h, p in TERMS) + "\n" + "\n".join(f"- {x}" for x in RULES)
    faq = "\n".join(f"- {q} {a}" for q, a in FAQ)
    cls = "\n".join(f"- {c['name']}: {SITE_URL}/klass/{c['slug']}/" for c in CLASSES)
    llms = f"""# {BRAND} — аренда авто без водителя в Астане

> Прокат автомобилей без водителя в Астане (Казахстан): {len(CARS)} машин от {nb(MIN_PRICE)} ₸ в сутки — эконом, бизнес, внедорожники и премиум. Возраст от 20 лет, стаж от 2 лет, депозит {nb(DEPOSIT)} ₸ возвращается сразу после возврата авто. Ежедневно {HOURS}.

## Контакты
- Телефон и WhatsApp: {PHONE_DISPLAY}
- Адрес: {ADDRESS}
- График: ежедневно {HOURS}
- Сайт: {SITE_URL}/

## Условия аренды
{terms}

## Автопарк и цены (за сутки)
{fleet}

## Классы
{cls}

## Частые вопросы
{faq}

## Разделы
- Цены: {SITE_URL}/ceny/
- Условия: {SITE_URL}/usloviya/
- Контакты: {SITE_URL}/kontakty/
"""
    (DIST / "llms.txt").write_text(llms, encoding="utf-8")

def main():
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "assets", DIST / "assets")
    shutil.copyfile(ROOT / "src" / "app.js", DIST / "assets" / "app.js")
    if (ROOT / "assets" / "favicon.ico").exists(): shutil.copyfile(ROOT / "assets" / "favicon.ico", DIST / "favicon.ico")
    got = 0
    for c in CARS:
        c["ph"] = photos(c); got += len(c["ph"])
    build_home(); build_park(); build_cars(); build_classes(); build_prices(); build_terms(); build_contacts(); build_privacy(); build_404(); build_meta()
    print("страниц:", len(SITEMAP) + 1, "фото:", got)

if __name__ == "__main__":
    main()
