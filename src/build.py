# -*- coding: utf-8 -*-
"""Генератор сайта аренды авто без водителя: src/ → dist/. Запуск: python3 src/build.py
Языки: русский (основной, все страницы), английский /en/, казахский /kz/, китайский /zh/ — переводы в src/i18n.py.
Фото машин: orig/<slug>-1.jpg … -4.jpg → python3 src/images.py → assets/img/cars/.
Видео на главной: assets/video/hero-pc.mp4 и hero-mob.mp4 (+ hero-pc.jpg / hero-mob.jpg — первый кадр) — подхватываются автоматически."""
import json, os, re, shutil, sys, html, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from data import *
from i18n import TR, CHAT_T

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
VER = "1711262"
E = html.escape
CLS = {c["slug"]: c for c in CLASSES}
nb = lambda n: f"{n:,}".replace(",", " ")
rub = lambda n: f"{nb(n)} ₸"
WA = f"https://wa.me/{WA_NUMBER}"
def wa(text): return WA + "?text=" + urllib.request.quote(text)

# ---------------------------------------------------------------- языки
LANGS = {  # код: (префикс URL, название в меню, короткое, og:locale, html lang, hreflang)
    "ru": ("", "Русский", "RU", "ru_KZ", "ru", "ru"),
    "en": ("/en", "English", "EN", "en_US", "en", "en"),
    "kk": ("/kz", "Қазақша", "KZ", "kk_KZ", "kk", "kk"),
    "zh": ("/zh", "中文", "中文", "zh_CN", "zh-Hans", "zh-Hans"),
}
L = "ru"
MISSING = {k: [] for k in LANGS}
def T(s):
    """Перевод строки сайта на текущий язык (ключ — русский текст)."""
    if L == "ru": return s
    t = TR[L].get(s)
    if t is None:
        if s not in MISSING[L]: MISSING[L].append(s)
        return s
    return t
ML = ("/avto/", "/klass/", "/ceny/", "/usloviya/", "/kontakty/", "/politika/")
def ml(p): return p == "/" or p.startswith(ML)          # страница есть на всех языках
def U(p): return (LANGS[L][0] + p) if ml(p) else p        # ссылка на текущем языке
def cars_n(n):
    if L == "en": return f"{n} cars"
    if L == "kk": return f"{n} көлік"
    if L == "zh": return f"{n}辆车"
    m = abs(n) % 100; k = m % 10
    return f"{n} " + ("машин" if 10 < m < 20 else "машина" if k == 1 else "машины" if 2 <= k <= 4 else "машин")

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
 "menu": '<path d="M4 7h16M4 12h16M4 17h10"/>',
 "send": '<path d="M3 11l18-8-8 18-2-8z"/>',
 "check": '<path d="M4 12l5 5L20 6"/>',
 "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.5 3.8 5.5 3.8 9s-1.3 6.5-3.8 9c-2.5-2.5-3.8-5.5-3.8-9S9.5 5.5 12 3z"/>',
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 "moon": '<path d="M20 14.5A8 8 0 1 1 9.5 4 6.5 6.5 0 0 0 20 14.5z"/>',
 "arr": '<path d="M5 12h14M13 6l6 6-6 6"/>',
}
ROBOT = ('<svg viewBox="0 0 64 64" aria-hidden="true"><path fill="currentColor" fill-rule="evenodd" d="M26 12h12a14 14 0 0 1 14 14v10a14 14 0 0 1-14 14H25l-12.5 8.5L15 47A14 14 0 0 1 12 36V26a14 14 0 0 1 14-14zm-1.5 9.5A6.5 6.5 0 0 0 18 28v5.5a6.5 6.5 0 0 0 6.5 6.5h15a6.5 6.5 0 0 0 6.5-6.5V28a6.5 6.5 0 0 0-6.5-6.5z"/>'
         '<rect x="4.5" y="23" width="5" height="15" rx="2.5" fill="currentColor"/><rect x="54.5" y="23" width="5" height="15" rx="2.5" fill="currentColor"/>'
         '<path d="M7 23v-7M57 23v-7" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>'
         '<path d="M23 31.5q3.2-3.8 6.4 0M34.6 31.5q3.2-3.8 6.4 0M29 35.6q3 2.6 6 0" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>')
def ic(n): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square" aria-hidden="true">{_P[n]}</svg>'
WA_IC = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.2-.2.3-.8 1-.9 1.1-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5.3-.5c.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.1-.3-.2-.6-.3zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4A9.8 9.8 0 1 1 12 21.8zm8.4-18.2A11.8 11.8 0 0 0 1.7 17.8L0 24l6.4-1.7A11.8 11.8 0 0 0 24 12a11.7 11.7 0 0 0-3.6-8.4z"/></svg>'.replace("1.7.6", "1.7.6")

# ---------------------------------------------------------------- фото и видео
def photos(c):
    d = ROOT / "assets" / "img" / "cars"
    return [f"/assets/img/cars/{c['slug']}-{i}" for i in (1, 2, 3, 4) if (d / f"{c['slug']}-{i}-800.webp").exists()]
def srcset(p): return ", ".join(f"{p}-{s}.webp {s}w" for s in (480, 800, 1200))
def img(p, alt, sizes, eager=False, w=1200, h=800):
    pr = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="{p}-800.webp" srcset="{srcset(p)}" sizes="{sizes}" alt="{E(alt)}" width="{w}" height="{h}" {pr} decoding="async">'
VID = ROOT / "assets" / "video"
HERO_CAR = "mercedes-s-class-w222"    # запасной фон главной, пока нет видео (не Lexus)

# ---------------------------------------------------------------- общие блоки
def minify_css(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s*\n\s*", "", s)
    return re.sub(r"\s*([{};,>])\s*", r"\1", s).replace(";}", "}")
CSS = minify_css((ROOT / "src" / "styles.css").read_text(encoding="utf-8"))
THEME_JS = ("<script>(function(){var d=document.documentElement,t;try{t=localStorage.getItem('theme')}catch(e){}"
            "if(t!=='light'&&t!=='dark')t='light';d.dataset.theme=t})()</script>")

def conv_js():
    """Код события конверсии по инструкции Google + защита от блокировщиков (done + 800 мс)."""
    if not (GADS_ID and GADS_LABEL): return ""
    return ("<script>\n  function gtag_report_conversion(url) {\n    var done = false;\n    var callback = function () { if (done) return; done = true; if (typeof(url) != 'undefined') { window.location = url; } };\n"
            f"    if (typeof gtag === 'function') {{ gtag('event', 'conversion', {{ 'send_to': '{GADS_ID}/{GADS_LABEL}', 'value': 1.0, 'currency': 'KZT', 'event_callback': callback }}); }}\n"
            "    setTimeout(callback, 800);\n    return false;\n  }\n</script>\n")

def gtag():
    if not TAG_ID: return ""
    src = "gtm.js" if TAG_ID.startswith("GTM-") else "gtag/js"
    return (f'<script async src="https://www.googletagmanager.com/{src}?id={TAG_ID}"></script>\n'
            "<script>\n  window.dataLayer = window.dataLayer || [];\n  function gtag(){dataLayer.push(arguments);}\n  gtag('js', new Date());\n"
            + ("" if TAG_ID.startswith("GTM-") else f"  gtag('config', '{TAG_ID}');\n") + "</script>\n")

def org():
    return {"@type": "AutoRental", "@id": SITE_URL + "/#org", "name": BRAND, "url": SITE_URL + "/", "telephone": PHONE_TEL,
            "image": SITE_URL + "/assets/og.png", "logo": SITE_URL + "/assets/icon-512.png",
            "address": {"@type": "PostalAddress", "streetAddress": T(STREET), "addressLocality": T(CITY), "addressCountry": "KZ"},
            "areaServed": {"@type": "City", "name": T(CITY)},
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": OPENS, "closes": CLOSES}],
            "priceRange": f"{nb(MIN_PRICE)}–{nb(max(c['price'] for c in CARS))} KZT", "currenciesAccepted": "KZT", "sameAs": [WA]}

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + u} for i, (n, u) in enumerate(items)]}
def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}

POLICY = "/politika/"
LOGO = '<b>TOP</b>RENT'
def nav_items():
    n = [(T("Автопарк"), "/avto/"), (T("Цены"), "/ceny/"), (T("Условия"), "/usloviya/")]
    if L == "ru": n.append(("Статьи", "/stati/"))
    return n + [(T("Контакты"), "/kontakty/")]
def hello(): return T("Здравствуйте! Хочу арендовать авто.")

def lang_menu(path, cls=""):
    cur = LANGS[L]
    items = "".join(f'<a href="{(v[0] + path) if ml(path) else (path if k == "ru" else v[0] + "/")}" hreflang="{v[5]}" lang="{v[4]}"{" aria-current=true" if k == L else ""}>{v[1]}</a>' for k, v in LANGS.items())
    return f'<details class="lang {cls}"><summary aria-label="{cur[2]} — {E(T("Язык"))}: {cur[1]}">{ic("globe")}<span>{cur[2]}</span></summary><div class="lang-m">{items}</div></details>'

def theme_btn(cls=""):
    return f'<button class="thm {cls}" type="button" data-theme-t aria-label="{E(T("Дневной или ночной режим"))}" title="{E(T("Дневной или ночной режим"))}">{ic("moon")}{ic("sun")}</button>'

def header(cur, path):
    sub = "".join(f'<a href="{U("/klass/" + c["slug"] + "/")}">{T(c["name"])}<span>{T("от")} {rub(min(x["price"] for x in CARS if c["slug"] in x["cls"]))}</span></a>' for c in CLASSES)
    nav = ""
    for n, u in nav_items():
        a = f'<a href="{U(u)}"{" aria-current=page" if cur == u else ""}>{n}</a>'
        nav += f'<div class="dd">{a}<div class="dd-m">{sub}<a href="{U("/avto/")}" class="all">{T("Весь автопарк")}</a></div></div>' if u == "/avto/" else a
    chips = "".join(f'<a href="{U("/klass/" + c["slug"] + "/")}"><b>{T(c["name"])}</b><span>{T("от")} {rub(min(x["price"] for x in CARS if c["slug"] in x["cls"]))}</span></a>' for c in CLASSES)
    dn = [(T("Главная"), "/")] + nav_items()
    if L == "ru": dn.insert(-1, ("Районы Астаны", "/rayony/"))
    dnav = "".join(f'<a href="{U(u)}"{" aria-current=page" if cur == u else ""}>{n}{ic("arr")}</a>' + (f'<div class="d-cls">{chips}</div>' if u == "/avto/" else "") for n, u in dn)
    return f'''<a class="skip" href="#main">{T("К содержимому")}</a>
<header class="hd"><div class="w">
<a class="logo" href="{U("/")}" aria-label="TOPRENT — {E(T("на главную"))}">{LOGO}</a>
<nav class="nav" aria-label="{E(T("Главное меню"))}">{nav}</nav>
<div class="hd-r">{lang_menu(path)}{theme_btn()}
<a class="hd-tel" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
<a class="hd-ic" href="tel:{PHONE_TEL}" aria-label="{E(T("Позвонить"))} {PHONE_DISPLAY}">{ic("phone")}</a>
<button class="burger" type="button" aria-label="{E(T("Открыть меню"))}" aria-expanded="false" aria-controls="drawer">{ic("menu")}<span>{T("Меню")}</span></button></div>
</div></header>
<div class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="{E(T("Меню"))}"><div class="d-p">
<div class="x"><a class="logo" href="{U("/")}">{LOGO}</a><button type="button" data-close aria-label="{E(T("Закрыть меню"))}">{ic("x")}</button></div>
<nav aria-label="{E(T("Меню"))}">{dnav}</nav>
<div class="d-bt"><div class="d-ct"><a class="btn c" href="tel:{PHONE_TEL}">{ic("phone")}{T("Позвонить")}</a><a class="btn" href="{wa(hello())}" target="_blank" rel="noopener">{WA_IC}WhatsApp</a></div>
<p class="dh">{PHONE_DISPLAY} · {T("ежедневно")} {HOURS}</p></div>
</div></div>'''

def footer():
    cls = "".join(f'<a href="{U("/klass/" + c["slug"] + "/")}">{T(c["name"])}</a>' for c in CLASSES)
    nav = "".join(f'<a href="{U(u)}">{n}</a>' for n, u in nav_items())
    extra = '<a href="/rayony/">Районы Астаны</a>' if L == "ru" else ""
    return f'''<footer class="ft"><div class="w">
<div><a class="logo" href="{U("/")}" aria-label="TOPRENT — {E(T("на главную"))}">{LOGO}</a><p class="fp">{T("Аренда авто без водителя в Астане: эконом, бизнес, внедорожники и премиум. Только для личных поездок.")}</p></div>
<div><h3>{T("Классы")}</h3>{cls}</div>
<div><h3>{T("Разделы")}</h3>{nav}{extra}<a href="{U(POLICY)}">{T("Политика конфиденциальности")}</a></div>
<div><h3>{T("Контакты")}</h3><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><a href="{WA}" target="_blank" rel="noopener">WhatsApp</a><p>{T(ADDRESS)}</p><p>{T("Ежедневно")} {HOURS}</p></div>
<div class="bt"><span>© {BRAND}, {T(CITY)}</span></div>
</div></footer>'''

def flo():
    q = "".join(f'<button type=button data-cls="{c["slug"]}">{T(c["name"])}</button>' for c in CLASSES) + "".join(f"<button type=button>{T(x)}</button>" for x in ["Какие нужны документы?", "Какой депозит?"])
    return f'''<div class="flo">
<a class="sm" href="{U("/")}" data-back aria-label="{E(T("Назад"))}" title="{E(T("Назад"))}">{ic("back")}</a>
<button class="sm" type="button" data-top hidden aria-label="{E(T("Наверх"))}" title="{E(T("Наверх"))}">{ic("up")}</button>
<div class="flo-p" id="flop" hidden>
<button type="button" data-chat>{ROBOT}<span>{T("ИИ-консультант")}<small>{T("фото и цены машин")}</small></span></button>
<a href="{wa(hello())}" target="_blank" rel="noopener">{WA_IC}<span>WhatsApp<small>{T("ответим в чате")}</small></span></a>
<a href="tel:{PHONE_TEL}">{ic("phone")}<span>{T("Позвонить")}<small>{PHONE_DISPLAY}</small></span></a>
</div>
<button class="flo-m" type="button" aria-label="{E(T("Связаться: ИИ-консультант, WhatsApp, звонок"))}" aria-expanded="false" aria-controls="flop"><img src="/assets/img/sale-0.webp" data-anim="/assets/img/sale.webp" width="60" height="60" alt="" decoding="async"></button>
</div>
<template id="chat-t"><section class="chat" id="chat" aria-label="{E(T("ИИ-консультант"))}">
<div class="chat-h"><span class="av">{ROBOT}</span><span><b>{T("ИИ-консультант")}</b><small>{T("машины, цены, условия")}</small></span><button type="button" data-chat-x aria-label="{E(T("Закрыть чат"))}">{ic("x")}</button></div>
<div class="chat-l" aria-live="polite"></div>
<div class="chat-q">{q}</div>
<form class="chat-f"><label class="sr" for="cq">{T("Ваш вопрос")}</label><input id="cq" name="q" autocomplete="off" placeholder="{E(T("Ваш вопрос"))}" maxlength="500"><button type="submit" aria-label="{E(T("Отправить"))}">{ic("send")}</button></form>
<a class="chat-w" href="{wa(hello())}" target="_blank" rel="noopener">{WA_IC}{T("Написать менеджеру в WhatsApp")}</a>
</section></template>'''

def page(path, title, desc, body, cur="", ld=None, preload=None, og=None, noindex=False, og_type="website", head_extra=""):
    """path — русский путь страницы; на других языках добавляется префикс."""
    pfx, _, _, loc, hl, _ = LANGS[L]
    full = (pfx + path) if path != "/404.html" else path
    if len(title) > 60 or len(desc) > 160: LONG.append((full, len(title), len(desc)))
    url = SITE_URL + full
    cfg = json.dumps({"wa": WA_NUMBER, "dep": DEPOSIT, "phone": PHONE_DISPLAY, "addr": T(STREET), "brand": BRAND, "tel": PHONE_TEL, "lang": L, "pfx": pfx,
                      "t": {k: T(v) for k, v in FORM_T.items()}}, ensure_ascii=False)
    graph = [org(), {"@type": "WebSite", "@id": SITE_URL + "/#site", "url": SITE_URL + "/", "name": BRAND, "inLanguage": hl}] + (ld or [])
    og_img = (SITE_URL + og + "-1200.webp") if og else SITE_URL + "/assets/og.png"
    pre = f'<link rel="preload" as="image" href="{preload}-800.webp" imagesrcset="{srcset(preload)}" imagesizes="(max-width: 899px) 100vw, 58vw" fetchpriority="high">\n' if preload else ""
    alts = ""
    if ml(path) and path != "/404.html":
        alts = "".join(f'<link rel="alternate" hreflang="{v[5]}" href="{SITE_URL}{v[0]}{path}">' for v in LANGS.values()) + f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}{path}">\n'
    doc = f'''<!doctype html>
<html lang="{hl}">
<head>
<meta charset="utf-8">
{gtag()}{conv_js()}{THEME_JS}
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
{alts}{'<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'}
<meta name="theme-color" content="#ffffff">
<meta name="color-scheme" content="light dark">
<meta property="og:type" content="{og_type}"><meta property="og:locale" content="{loc}"><meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og_img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{og_img}">
<meta name="geo.region" content="KZ-AST"><meta name="geo.placename" content="{CITY_EN if L != "ru" else CITY}">
<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/onest-{"latin" if L in ("en", "zh") else "cyrillic"}-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
{pre}{head_extra}<style>{CSS}</style>
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)}</script>
</head>
<body>
{header(cur, path)}
<main id="main">
{body}
</main>
{footer()}
{flo()}
<script>window.__C={cfg}</script>
<script src="/assets/app.js?v={VER}" defer></script>
</body>
</html>
'''
    head, sep, rest = doc.partition("<body>")
    doc = head + sep + typo(rest)
    if GADS_ID and GADS_LABEL:
        doc = re.sub(r'<a ([^>]*?)href="tel:([^"]+)"', lambda m: f'<a {m.group(1)}href="tel:{m.group(2)}" onclick="return gtag_report_conversion(&#39;tel:{m.group(2)}&#39;)"', doc)
        doc = re.sub(r'<a ([^>]*?)href="(https://wa\.me/[^"]+)"', lambda m: f'<a {m.group(1)}href="{m.group(2)}" onclick="gtag_report_conversion()"', doc)
    out = DIST / full.strip("/") / "index.html" if path != "/404.html" else DIST / "404.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    if path != "/404.html" and not noindex: SITEMAP.append(full)

FORM_T = {"pick": "Выберите машину", "dep": "Депозит", "back": "вернём", "day": "сутки", "days": "сут.", "plus": "+ депозит", "phone": "Укажите номер телефона",
          "msg": "Здравствуйте! Хочу арендовать авто.", "car": "Машина", "dates": "Даты", "get": "Получение", "name": "Имя", "tel": "Телефон", "any": "подберите",
          "up": "Цена ↑", "down": "Цена ↓", "light": "Дневной", "dark": "Ночной"}

SITEMAP = []; LONG = []
_SHORT = r"(?<![\w ])(в|во|и|с|со|к|ко|о|об|у|а|на|по|за|от|до|из|не|без|для|при|под|над|или|но|что|как|это)\s(?=\S)"
def _t(m):
    t = m.group(0)
    t = re.sub(r"(?<=\d) (?=\d{3}\b)", " ", t).replace(" ₸", " ₸")
    if L == "ru": t = re.sub(_SHORT, lambda x: x.group(1) + " ", t, flags=re.I)
    return t.replace(" —", " —")
def typo(html_):
    parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>|<template\b|</template>)", html_, flags=re.S)
    out = []
    for p in parts:
        if p.startswith("<script") or p.startswith("<style"): out.append(p); continue
        out.append(re.sub(r"(?<=>)[^<]+", _t, p))
    return "".join(out)

# ---------------------------------------------------------------- блоки контента
def cname(k): return T(CLS[k]["name"])
def cls_names(c): return " · ".join(cname(x) for x in c["cls"])
def meta_cls(c):
    k = [x for x in c["cls"] if not (x == "vnedorozhniki" and c["body"] in ("Внедорожник", "Кроссовер"))]
    return cname(k[-1]) if k else ""
def rent_msg(c): return T("Здравствуйте! Хочу арендовать {car}.").format(car=c["full"])

def card(c, eager=False):
    ph = c["ph"]
    pic = (img(ph[0], T("{car} — аренда в Астане").format(car=c["full"]), "(max-width: 373px) 100vw, (max-width: 599px) 50vw, (max-width: 1279px) 33vw, 300px", eager)
           if ph else f'<div class="ph-x" aria-hidden="true"><span>{E(c["brand"].split("-")[0])}</span></div>')
    parts = [(str(c["year"]) if c["year"] else "", ""), (meta_cls(c), ""), (T(c["body"]), "mb")]
    meta = "".join(f'<span{f" class={k}" if k else ""}>{E(x)}</span>' for x, k in parts if x)
    return f"""<article class="card" data-cls="{" ".join(c["cls"])}" data-p="{c["price"]}">
<div class="ph">{pic}</div>
<div class="cb"><h3><a href="{U("/avto/" + c["slug"] + "/")}">{E(c["short"])}</a></h3><p class="meta">{meta}</p>
<div class="pr"><b>{rub(c["price"])}</b><span>{T("за сутки")}</span></div>
<a class="go" href="{wa(rent_msg(c))}" target="_blank" rel="noopener">{WA_IC}{T("Забронировать")}<span class="xs"> {T("в WhatsApp")}</span></a></div>
</article>"""

def cards(lst, eager=0, grid=True): return f'<div class="cards"{" data-grid" if grid else ""}>' + "".join(card(c, i < eager) for i, c in enumerate(lst)) + "</div>"

def filters():
    b = f'<button type="button" data-f="all" aria-pressed="true">{T("Все")}</button>' + "".join(f'<button type="button" data-f="{c["slug"]}" aria-pressed="false">{T(c["name"])}</button>' for c in CLASSES)
    return f'<div class="flt" role="group" aria-label="{E(T("Фильтр по классу"))}">{b}<button type="button" class="srt" data-sort title="{E(T("Сортировка по цене"))}">{T("Цена ↑")}</button></div>'

def terms_html():
    t = "".join(f'<div class="term{" neg" if k == "taxi" else ""}"><h3>{E(T(h))}</h3><p>{E(T(p))}</p></div>' for k, h, p in TERMS)
    t += f'<a class="term cta" href="{wa(T("Здравствуйте! Вопрос по условиям аренды."))}" target="_blank" rel="noopener"><h3>{T("Остались вопросы?")}</h3><p>{T("Напишите в WhatsApp — ответим по условиям, датам и доставке.")}</p><span class="more">{T("Написать в WhatsApp")} →</span></a>'
    r = "".join(f"<li>{E(T(x))}</li>" for x in RULES)
    return f'<div class="terms">{t}</div><ul class="rules">{r}</ul>'

def steps_html():
    return '<div class="steps">' + "".join(f'<div class="step"><h3>{E(T(h))}</h3><p>{E(T(p))}</p></div>' for k, h, p in STEPS) + "</div>"
def factors_html():
    return '<dl class="fac">' + "".join(f"<div><dt>{E(T(h))}</dt><dd>{E(T(p))}</dd></div>" for h, p in PRICE_FACTORS) + "</dl>"
def faq_html(faq): return '<div class="faq">' + "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq) + "</div>"
def tfaq(faq): return [(T(q), T(a)) for q, a in faq]

def book(sel=None, area=""):
    opts = f'<option value="" data-p="0">{T("Подберите мне машину")}</option>' + "".join(
        f'<option value="{c["slug"]}" data-p="{c["price"]}" data-n="{E(c["full"])}"{" selected" if sel and c["slug"] == sel["slug"] else ""}>{E(c["full"])} — {rub(c["price"])}</option>' for c in sorted(CARS, key=lambda x: x["price"]))
    title = T("Забронировать {car}").format(car=E(sel["full"])) if sel else T("Забронировать машину")
    dl = f"Доставка по адресу — {area}" if area else T("Доставка по адресу в Астане")
    return f"""<section class="s bk" id="bron"><div class="w book">
<div class="bk-l"><h2>{title}</h2><p class="lead">{T("Выберите даты — посчитаем стоимость. Заявка уйдёт менеджеру в WhatsApp, он подтвердит, что машина свободна.")}</p>
<ul><li><span>{T("Удостоверение личности и водительские права")}</span></li><li><span>{T("Возраст от 20 лет, стаж от 2 лет")}</span></li><li><span>{T("Депозит {dep} — вернём сразу после возврата авто").format(dep=rub(DEPOSIT))}</span></li><li><span>{T("Только личные поездки — не под такси и работу")}</span></li></ul></div>
<form class="form" id="book" novalidate>
<label class="full">{T("Машина")}<select name="car">{opts}</select></label>
<label>{T("Дата начала")}<input type="date" name="d1"></label>
<label>{T("Дата возврата")}<input type="date" name="d2"></label>
<div class="calc" data-calc aria-live="polite"></div>
<label class="full">{T("Где забрать")}<select name="get"><option>{T("В офисе")}: {E(T(STREET))}</option><option>{E(dl)} ({T("за доплату")})</option></select></label>
<label>{T("Имя")}<input name="name" autocomplete="given-name" placeholder="{E(T("Как к вам обращаться"))}"></label>
<label>{T("Телефон")}<input name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 7__ ___ __ __" required></label>
<button class="btn c full" type="submit">{WA_IC}{T("Отправить в WhatsApp")}</button>
<small>{T("Нажимая кнопку, вы соглашаетесь с")} <a href="{U(POLICY)}">{T("политикой конфиденциальности")}</a>. {T("Итоговую стоимость подтвердит менеджер.")}</small>
</form></div></section>"""

def crumbs(items):
    out = []
    for i, (n, u) in enumerate(items):
        out.append(f'<span aria-current="page">{E(n)}</span>' if i == len(items) - 1 else f'<a href="{U(u)}">{E(n)}</a><span aria-hidden="true">/</span>')
    return f'<nav class="crumbs w" aria-label="{E(T("Хлебные крошки"))}">{"".join(out)}</nav>'
def lcr(items): return [(n, U(u)) for n, u in items]   # крошки для JSON-LD

def top(cr, h1, lead, extra=""):
    return f'{crumbs(cr)}\n<section class="s pt"><div class="w"><div class="sh"><div><h1>{h1}</h1><p class="lead">{lead}</p></div></div>{extra}</div></section>'

def call_act(msg):
    return f'<div class="act"><a class="btn c" href="{wa(msg)}" target="_blank" rel="noopener">{WA_IC}{T("Написать в WhatsApp")}</a><a class="btn" href="tel:{PHONE_TEL}">{ic("phone")}{T("Позвонить")}</a></div>'

# ---------------------------------------------------------------- страницы
def hero():
    pc, mob = VID / "hero-pc.mp4", VID / "hero-mob.mp4"
    has_v = pc.exists() or mob.exists()
    pp = (VID / "hero-pc.jpg").exists(); pm = (VID / "hero-mob.jpg").exists()
    if pp or pm:   # кадр из видео — фон до запуска видео
        a, b = ("/assets/video/hero-mob.jpg" if pm else "/assets/video/hero-pc.jpg"), ("/assets/video/hero-pc.jpg" if pp else "/assets/video/hero-mob.jpg")
        poster = f'<picture><source media="(min-width: 768px)" srcset="{b}"><img src="{a}" alt="" width="1080" height="1920" fetchpriority="high" decoding="async"></picture>'
        pre = f'<link rel="preload" as="image" href="{a}" media="(max-width: 767px)" fetchpriority="high"><link rel="preload" as="image" href="{b}" media="(min-width: 768px)" fetchpriority="high">\n'
    else:
        p = f"/assets/img/cars/{HERO_CAR}-1"
        poster = f'<img src="{p}-800.webp" srcset="{srcset(p)}" sizes="100vw" alt="" width="1200" height="800" fetchpriority="high" decoding="async">'
        pre = f'<link rel="preload" as="image" href="{p}-800.webp" imagesrcset="{srcset(p)}" imagesizes="100vw" fetchpriority="high">\n'
    vid = ""
    if has_v:
        vid = f'<video muted loop playsinline preload="none" aria-hidden="true" data-pc="{"/assets/video/hero-pc.mp4" if pc.exists() else ""}" data-mob="{"/assets/video/hero-mob.mp4" if mob.exists() else ""}"></video>'
    rules = [("taxi", T("Только для личных поездок"), T("Не под такси, доставку и перевозки")),
             ("age", T("С 20 лет и стажем от 2 лет"), T("Нужны удостоверение и права")),
             ("dep", T("Депозит {dep}").format(dep=rub(DEPOSIT)), T("Вернём сразу после возврата авто"))]
    lis = "".join(f"<li><b>{h}</b><span>{p}</span></li>" for k, h, p in rules)
    html_ = f"""<section class="hero"><div class="hero-bg">{poster}{vid}</div>
<div class="w hero-in"><h1>{T("Аренда авто без водителя в Астане")}</h1>
<p class="lead">{T("{n} — от Hyundai Accent до Mercedes G63, от {p} в сутки. Машины выдаём только для личных поездок.").format(n=cars_n(len(CARS)), p=rub(MIN_PRICE))}</p>
<ul class="hero-r">{lis}</ul>
{call_act(hello())}</div></section>"""
    return html_, pre

def build_home():
    by_price = sorted(CARS, key=lambda c: c["price"])
    h, pre = hero()
    body = f"""{h}
<section class="s gr" id="park"><div class="w"><div class="sh"><h2>{T("Автопарк")}</h2><p>{T("Цена за сутки. У каждой машины своя страница с фото и условиями.")}</p></div>{filters()}{cards(by_price)}</div></section>
<section class="s lt" id="usloviya"><div class="w"><div class="sh"><h2>{T("Условия аренды")}</h2><p>{T("Коротко и без мелкого шрифта.")} <a href="{U("/usloviya/")}">{T("Все условия")} →</a></p></div>{terms_html()}</div></section>
<section class="s"><div class="w"><div class="sh"><h2>{T("Как арендовать")}</h2><p>{T("Без лишних бумаг: документы, оплата, депозит — и машина ваша.")}</p></div>{steps_html()}</div></section>
<section class="s lt"><div class="w"><div class="sh"><h2>{T("Вопросы")}</h2></div>{faq_html(tfaq(FAQ))}</div></section>
{book()}
{contacts_block()}"""
    items = {"@type": "ItemList", "name": T("Автопарк"), "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE_URL + U(f"/avto/{c['slug']}/"), "name": c["full"]} for i, c in enumerate(by_price)]}
    page("/", T("Аренда авто без водителя в Астане от {p} ₸ | {b}").format(p=nb(MIN_PRICE), b=BRAND),
         T("Аренда авто без водителя в Астане: {n} от Hyundai Accent до Mercedes G63, от {p} ₸ в сутки. С 20 лет, депозит 20 000 ₸. Не под такси.").format(n=cars_n(len(CARS)), p=nb(MIN_PRICE)),
         body, "/", [faq_ld(tfaq(FAQ)), items], head_extra=pre)

def contacts_block():
    maps = "https://www.google.com/maps/search/?api=1&query=" + urllib.request.quote(f"{BRAND} {ADDRESS}")
    return f"""<section class="s lt" id="kontakty"><div class="w"><div class="sh"><h2>{T("Контакты")}</h2><p>{T("Перед приездом позвоните или напишите — подготовим машину и документы.")}</p></div>
<div class="ct"><div><span>{T("Телефон")}</span><a class="v" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></div>
<div><span>WhatsApp</span><a class="v" href="{wa(hello())}" target="_blank" rel="noopener">{T("Написать")}</a></div>
<div><span>{T("Адрес")}</span><a class="v" href="{maps}" target="_blank" rel="noopener">{E(T(STREET))}</a></div>
<div><span>{T("График")}</span><b>{T("Ежедневно")} {HOURS}</b></div></div></div></section>"""

def build_park():
    lst = sorted(CARS, key=lambda c: c["price"])
    cr = [(T("Главная"), "/"), (T("Автопарк"), "/avto/")]
    body = top(cr, T("Автопарк"), T("{n} без водителя в Астане — эконом, бизнес, внедорожники и премиум. Цена за сутки, депозит {dep}.").format(n=cars_n(len(CARS)), dep=rub(DEPOSIT)),
               f'<h2 class="sr">{T("Все машины")}</h2>{filters()}{cards(lst, 4)}') + f"""
<section class="s"><div class="w"><div class="sh"><h2>{T("Условия аренды")}</h2></div>{terms_html()}</div></section>
{book()}"""
    page("/avto/", T("Автопарк: аренда авто в Астане без водителя | {b}").format(b=BRAND),
         T("Все машины для аренды без водителя в Астане с ценами: Hyundai, Kia, Toyota, Lexus, Mercedes. От {p} ₸ в сутки, депозит 20 000 ₸.").format(p=nb(MIN_PRICE)),
         body, "/avto/", [crumbs_ld(lcr(cr))])

def car_faq(c):
    return [(T("Сколько стоит аренда {car} в Астане?").format(car=c["full"]), T("{p} в сутки. Плюс депозит {dep}, его вернём сразу после возврата машины.").format(p=rub(c["price"]), dep=rub(DEPOSIT))),
            (T("Что нужно, чтобы взять {car} без водителя?").format(car=c["name"]), T("Удостоверение личности и водительские права. Возраст — от 20 лет, стаж — от 2 лет.")),
            (T("Можно ли выехать на {car} за город?").format(car=c["name"]), T("Машина выдаётся для поездок по Астане. Выезд за город — по согласованию и с доплатой, сумма зависит от направления.")),
            (T("Можно ли привезти машину по адресу?"), T("Да, доставка по Астане — за доплату, сумма зависит от адреса. Забрать машину в офисе на {st} — без доплаты.").format(st=T(STREET))),
            (T("Можно ли работать на машине в такси?"), T("Нет, под режим такси и другую работу машины не выдаём."))]

def build_cars():
    for c in CARS:
        p = c["ph"]; path = f"/avto/{c['slug']}/"
        if p:
            main = img(p[0], T("{car} — фото {n}").format(car=c["full"], n=1), "(max-width: 899px) 100vw, 58vw", True)
            th = "".join(f'<button type="button" data-src="{u}-1200.webp" aria-label="{E(T("Фото"))} {i + 1}" aria-current="{"true" if i == 0 else "false"}"><img src="{u}-480.webp" alt="" width="480" height="320" loading="lazy" decoding="async"></button>' for i, u in enumerate(p))
            th = th if len(p) > 1 else ""
        else:
            main = f'<div class="ph-x" aria-hidden="true"><span>{E(c["brand"].split("-")[0])}</span><b>{E(c["model"])}</b></div>'
            th = ""
        sim = sorted([x for x in CARS if x is not c and set(x["cls"]) & set(c["cls"])], key=lambda x: abs(x["price"] - c["price"]))[:3]
        fit = "".join(f"<li>{E(T(x))}</li>" for x in c["fit"])
        cl = c["cls"][0]
        rows = [(T("Марка"), c["brand"]), (T("Модель"), c["model"]), (T("Год"), str(c["year"]) if c["year"] else T("уточняйте у менеджера")), (T("Кузов"), T(c["body"])),
                (T("Класс"), cls_names(c)), (T("Цена"), f"{rub(c['price'])} / {T('сутки')}"), (T("Депозит"), T("{dep}, возвращается сразу").format(dep=rub(DEPOSIT))),
                (T("Поездки"), T("только личные, не под такси")), (T("Эксплуатация"), T("по Астане; за город — с доплатой"))]
        spec = "".join(f"<tr><th scope=row>{E(a)}</th><td>{E(b)}</td></tr>" for a, b in rows)
        cr = [(T("Главная"), "/"), (T("Автопарк"), "/avto/"), (cname(cl), f"/klass/{cl}/"), (c["full"], path)]
        body = f"""<div class="car-wrap">{crumbs(cr)}
<section class="w car-top">
<div class="gal-c"><div class="gal"><div class="gal-m">{main}</div>{f'<div class="gal-t">{th}</div>' if th else ""}</div>
<aside class="fact"><b>{T("Интересный факт")}</b><p>{E(T(FACTS[c["slug"]]))}</p></aside></div>
<div class="info"><h1>{T("Аренда {car} в Астане").format(car=E(c["full"]))}</h1><p class="lead">{E(T(c["about"]))}</p>
<div class="price"><div class="c1"><b>{rub(c["price"])}</b><span>{T("в сутки")}</span></div><div><b>{rub(DEPOSIT)}</b><span>{T("депозит, вернём сразу")}</span></div></div>
<div class="act"><a class="btn c" href="#bron">{ic("key")}{T("Забронировать")}</a><a class="btn" href="{wa(rent_msg(c))}" target="_blank" rel="noopener">{WA_IC}WhatsApp</a></div>
<table class="spec"><caption class="sr">{T("Характеристики и условия")}</caption>{spec}</table>
<ul class="fit" aria-label="{E(T("Подходит для"))}">{fit}</ul></div>
</section></div>
<section class="s"><div class="w"><div class="sh"><h2>{T("Как арендовать {car}").format(car=E(c["short"]))}</h2><p>{T("Подготовьте удостоверение личности и водительские права — других документов не нужно.")}</p></div>{steps_html()}</div></section>
<section class="s gr"><div class="w"><div class="sh"><h2>{T("Условия аренды")}</h2></div>{terms_html()}</div></section>
{book(c)}
<section class="s lt"><div class="w"><div class="sh"><h2>{T("Вопросы о {car}").format(car=E(c["name"]))}</h2></div>{faq_html(car_faq(c))}</div></section>
<section class="s gr"><div class="w"><div class="sh"><h2>{T("Похожие машины")}</h2><p><a href="{U("/klass/" + cl + "/")}">{T("Все машины класса «{k}»").format(k=cname(cl))} →</a></p></div>{cards(sim, grid=False)}</div></section>"""
        prod = {"@type": "Product", "name": T("Аренда {car} без водителя").format(car=c["full"]), "brand": {"@type": "Brand", "name": c["brand"]},
                "description": T(c["about"]), "category": T("Аренда автомобилей"),
                "offers": {"@type": "Offer", "price": c["price"], "priceCurrency": "KZT", "availability": "https://schema.org/InStock", "url": SITE_URL + U(path),
                           "seller": {"@id": SITE_URL + "/#org"},
                           "priceSpecification": {"@type": "UnitPriceSpecification", "price": c["price"], "priceCurrency": "KZT", "unitCode": "DAY", "referenceQuantity": {"@type": "QuantitativeValue", "value": 1, "unitCode": "DAY"}}}}
        if p: prod["image"] = [SITE_URL + u + "-1200.webp" for u in p]
        t = T("Аренда {car} в Астане — {p} ₸/сутки").format(car=c["full"], p=nb(c["price"]))
        if len(t) > 60: t = T("Аренда {car} в Астане — {p} ₸/сутки").format(car=c["short"], p=nb(c["price"]))
        if len(t) > 60: t = T("{car} в аренду в Астане — {p} ₸").format(car=c["short"], p=nb(c["price"]))
        d = T("{car} в аренду без водителя в Астане за {p} ₸ в сутки. Депозит 20 000 ₸, с 20 лет, стаж 2 года. Не под такси.").format(car=c["full"], p=nb(c["price"]))
        page(path, t, d, body, "/avto/", [crumbs_ld(lcr(cr)), prod, faq_ld(car_faq(c))], preload=p[0] if p else None, og=p[0] if p else None)

def build_classes():
    for k in CLASSES:
        lst = sorted([c for c in CARS if k["slug"] in c["cls"]], key=lambda c: c["price"])
        lo, hi = min(c["price"] for c in lst), max(c["price"] for c in lst)
        faq = [(T("Сколько стоит аренда: {k}?").format(k=T(k["name"])), T("От {lo} до {hi} в сутки. Плюс депозит {dep} — вернём сразу после возврата машины.").format(lo=rub(lo), hi=rub(hi), dep=rub(DEPOSIT))),
               (T("Какие машины есть в классе «{k}»?").format(k=T(k["name"])), ", ".join(c["full"] for c in lst) + "."),
               (T("Можно ли привезти машину по адресу?"), T("Да, доставка по Астане — за доплату, сумма зависит от адреса.")),
               (T("Какие условия аренды?"), T("Возраст от 20 лет, стаж от 2 лет, удостоверение личности и права. Эксплуатация по Астане, выезд за город — по согласованию с доплатой. Под такси не выдаём."))]
        tabs = "".join(f'<a href="{U("/klass/" + c["slug"] + "/")}"{" aria-current=page" if c is k else ""}>{T(c["name"])}</a>' for c in CLASSES)
        cr = [(T("Главная"), "/"), (T("Автопарк"), "/avto/"), (T(k["name"]), f"/klass/{k['slug']}/")]
        body = top(cr, E(T(k["h1"])), f'{E(T(k["lead"]))} {T("От {p} в сутки.").format(p=rub(lo))}', f'<h2 class="sr">{T("Машины класса «{k}»").format(k=T(k["name"]))}</h2><div class="flt" aria-label="{E(T("Классы"))}">{tabs}</div>{cards(lst, 4)}') + f"""
<section class="s gr"><div class="w"><div class="sh"><h2>{T("От чего зависит цена")}</h2></div>{factors_html()}</div></section>
<section class="s"><div class="w"><div class="sh"><h2>{T("Условия аренды")}</h2></div>{terms_html()}</div></section>
{book()}
<section class="s lt"><div class="w"><div class="sh"><h2>{T("Вопросы")}</h2></div>{faq_html(faq)}</div></section>"""
        t = T("{k} — от {p} ₸/сутки").format(k=T(k["title"]), p=nb(lo))
        if len(t) > 60: t = T("{k} — от {p} ₸").format(k=T(k["h1"]), p=nb(lo))
        page(f"/klass/{k['slug']}/", t,
             T("{k} без водителя: {cars}. От {p} ₸ в сутки, депозит 20 000 ₸, с 20 лет.").format(k=T(k["h1"]), cars=", ".join(c["short"] for c in lst[:3]), p=nb(lo)),
             body, "/avto/", [crumbs_ld(lcr(cr)), faq_ld(faq)])

def build_prices():
    lst = sorted(CARS, key=lambda c: c["price"])
    rows = "".join(f'<tr><td data-l="{E(T("Машина"))}"><a href="{U("/avto/" + c["slug"] + "/")}">{E(c["full"])}</a></td><td data-l="{E(T("Кузов"))}">{E(T(c["body"]))}</td><td data-l="{E(T("Класс"))}">{E(cls_names(c))}</td><td data-l="{E(T("За сутки"))}">{rub(c["price"])}</td></tr>' for c in lst)
    cr = [(T("Главная"), "/"), (T("Цены"), "/ceny/")]
    faq = tfaq([FAQ[4], FAQ[2], FAQ[6]]) + [(T("Есть ли скидка при аренде на несколько дней?"), T("Условия на длительный срок уточняйте у менеджера в WhatsApp или по телефону {ph}.").format(ph=PHONE_DISPLAY))]
    body = top(cr, T("Цены на аренду авто"), T("Стоимость аренды без водителя в Астане за сутки. К аренде добавляется депозит {dep} — возвращаем сразу после возврата машины.").format(dep=rub(DEPOSIT)),
               f'<table class="tbl"><caption class="sr">{T("Цены за сутки")}</caption><thead><tr><th scope=col>{T("Машина")}</th><th scope=col>{T("Кузов")}</th><th scope=col>{T("Класс")}</th><th scope=col>{T("За сутки")}</th></tr></thead><tbody>{rows}</tbody></table>') + f"""
<section class="s gr"><div class="w"><div class="sh"><h2>{T("От чего зависит цена")}</h2></div>{factors_html()}</div></section>
<section class="s"><div class="w"><div class="sh"><h2>{T("Условия аренды")}</h2></div>{terms_html()}</div></section>
{book()}
<section class="s lt"><div class="w"><div class="sh"><h2>{T("Вопросы о цене")}</h2></div>{faq_html(faq)}</div></section>"""
    page("/ceny/", T("Цены на аренду авто в Астане — от {p} ₸ | {b}").format(p=nb(MIN_PRICE), b=BRAND),
         T("Прайс на аренду авто без водителя в Астане: {n} от {lo} до {hi} ₸ в сутки. Депозит 20 000 ₸, возвращается сразу.").format(n=cars_n(len(CARS)), lo=nb(MIN_PRICE), hi=nb(lst[-1]["price"])),
         body, "/ceny/", [crumbs_ld(lcr(cr)), faq_ld(faq)])

def build_terms():
    cr = [(T("Главная"), "/"), (T("Условия"), "/usloviya/")]
    body = top(cr, T("Условия аренды авто в Астане"), T("Кто может взять машину, какие нужны документы, сколько депозит и куда можно ездить."),
               f'<h2 class="sr">{T("Основные условия")}</h2>{terms_html()}') + f"""
<section class="s"><div class="w"><div class="sh"><h2>{T("Как арендовать")}</h2></div>{steps_html()}</div></section>
<section class="s gr"><div class="w"><div class="sh"><h2>{T("От чего зависит цена")}</h2></div>{factors_html()}</div></section>
<section class="s lt"><div class="w"><div class="sh"><h2>{T("Вопросы")}</h2></div>{faq_html(tfaq(FAQ))}</div></section>
{book()}"""
    page("/usloviya/", T("Условия аренды авто в Астане: с 20 лет, депозит 20 000 ₸"),
         T("Условия аренды авто без водителя в Астане: от 20 лет, стаж от 2 лет, удостоверение и права, депозит 20 000 ₸ возвращается сразу. Не под такси."),
         body, "/usloviya/", [crumbs_ld(lcr(cr)), faq_ld(tfaq(FAQ))])

def build_districts():   # только русский
    cr0 = [("Главная", "/"), ("Районы", "/rayony/")]
    tiles = "".join(f'<a href="/rayony/{d["slug"]}/"><b>{d["name"]}</b><span>офис или доставка</span></a>' for d in DISTRICTS)
    body = top(cr0, "Аренда авто по районам Астаны", f"Машину можно забрать в офисе на {E(STREET)} или заказать доставку по адресу в любом районе Астаны — за доплату, сумма зависит от адреса.",
               f'<h2 class="sr">Районы</h2><div class="dist">{tiles}</div>') + f"""
<section class="s gr"><div class="w"><div class="sh"><h2>Автопарк</h2><p><a href="/avto/">Все машины и цены →</a></p></div>{cards(sorted(CARS, key=lambda c: c["price"])[:8], grid=False)}</div></section>
{book()}"""
    page("/rayony/", f"Аренда авто по районам Астаны | {BRAND}",
         f"Аренда авто без водителя в районах Есиль, Алматы, Байконыр, Сарыарка и Нура: забрать в офисе или доставка по адресу. От {nb(MIN_PRICE)} ₸ в сутки.",
         body, "/rayony/", [crumbs_ld(cr0)])
    for d in DISTRICTS:
        path = f"/rayony/{d['slug']}/"
        cr = cr0 + [(d["name"], path)]
        area = f"район {d['name']}"
        faq = [(f"Можно ли получить машину в {d['gen']}?", f"Да. Доставка по адресу в {d['gen']} — за доплату, сумма зависит от адреса. Без доплаты машину можно забрать в офисе: {STREET}."),
               ("Сколько стоит аренда?", f"От {rub(MIN_PRICE)} до {rub(max(c['price'] for c in CARS))} в сутки — зависит от машины. Плюс депозит {rub(DEPOSIT)}, он возвращается сразу после возврата авто."),
               ("Какие нужны документы?", "Удостоверение личности и водительские права. Возраст от 20 лет, стаж от 2 лет."),
               ("Можно ли выехать за город?", "По согласованию и с доплатой, сумма зависит от направления.")]
        others = "".join(f'<a href="/rayony/{x["slug"]}/">{x["name"]}</a>' for x in DISTRICTS if x is not d)
        body = top(cr, f"Аренда авто без водителя — район {d['name']}, Астана",
                   f"Аренда авто без водителя для жителей и гостей района {d['name']}: {cars_n(len(CARS))} от {rub(MIN_PRICE)} в сутки. Заберите машину в офисе на {E(STREET)} или закажите доставку по адресу за доплату.",
                   call_act(f"Здравствуйте! Хочу арендовать авто, район {d['name']}.")) + f"""
<section class="s gr"><div class="w"><div class="sh"><h2>Машины</h2><p><a href="/avto/">Весь автопарк →</a></p></div>{filters()}{cards(sorted(CARS, key=lambda c: c["price"]), 4)}</div></section>
<section class="s"><div class="w"><div class="sh"><h2>Как получить машину</h2></div><dl class="fac"><div><dt>В офисе</dt><dd>{E(ADDRESS)}, ежедневно {HOURS}. Без доплаты.</dd></div><div><dt>Доставка в район {d["name"]}</dt><dd>По вашему адресу, за доплату — сумму назовёт менеджер.</dd></div><div><dt>Документы</dt><dd>Удостоверение личности и водительские права.</dd></div><div><dt>Депозит</dt><dd>{rub(DEPOSIT)}, возвращаем сразу после возврата машины.</dd></div></dl></div></section>
{book(area=area)}
<section class="s lt"><div class="w"><div class="sh"><h2>Вопросы</h2></div>{faq_html(faq)}<p class="oth">Другие районы: {others}</p></div></section>"""
        page(path, f"Аренда авто в районе {d['name']}, Астана | {BRAND}",
             f"Аренда авто без водителя в районе {d['name']} (Астана): от {nb(MIN_PRICE)} ₸ в сутки, забрать в офисе или доставка по адресу. С 20 лет, депозит 20 000 ₸.",
             body, "/rayony/", [crumbs_ld(cr), faq_ld(faq)])

def build_articles():   # только русский
    cr0 = [("Главная", "/"), ("Статьи", "/stati/")]
    lst = "".join(f'<a href="/stati/{a["slug"]}/"><b>{E(a["title"])}</b><span>{E(a["desc"])}</span></a>' for a in ARTICLES)
    body = top(cr0, "Статьи об аренде авто", "Коротко отвечаем на частые вопросы: документы, депозит, выезд за город и выбор машины.", f'<h2 class="sr">Все статьи</h2><div class="arts">{lst}</div>')
    page("/stati/", f"Статьи об аренде авто в Астане | {BRAND}", "Полезное об аренде авто без водителя в Астане: документы, депозит, выезд за город, выбор класса машины.", body, "/stati/", [crumbs_ld(cr0)])
    dt = ARTICLE_DATE.split("-"); human = f"{int(dt[2])} {['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'][int(dt[1]) - 1]} {dt[0]}"
    for a in ARTICLES:
        path = f"/stati/{a['slug']}/"; cr = cr0 + [(a["title"], path)]
        secs = "".join(f"<h2>{E(h)}</h2><ul>" + "".join(f"<li>{E(x)}</li>" for x in items) + "</ul>" for h, items in a["body"])
        links = " · ".join(f'<a href="{u}">{E(n)}</a>' for n, u in a["links"])
        more = "".join(f'<a href="/stati/{x["slug"]}/"><b>{E(x["title"])}</b><span>{E(x["desc"])}</span></a>' for x in ARTICLES if x is not a)
        body = f"""{crumbs(cr)}
<article class="s pt"><div class="w art"><h1>{E(a["h1"])}</h1><p class="dt"><time datetime="{ARTICLE_DATE}">{human}</time></p><p class="lead">{E(a["lead"])}</p>{secs}
<p class="rel">Смотрите также: {links}</p>{call_act(hello())}</div></article>
<section class="s gr"><div class="w"><div class="sh"><h2>Другие статьи</h2></div><div class="arts">{more}</div></div></section>"""
        art = {"@type": "Article", "headline": a["h1"], "description": a["desc"], "datePublished": ARTICLE_DATE, "dateModified": ARTICLE_DATE, "inLanguage": "ru",
               "author": {"@id": SITE_URL + "/#org"}, "publisher": {"@id": SITE_URL + "/#org"}, "mainEntityOfPage": SITE_URL + path, "image": SITE_URL + "/assets/og.png"}
        t = a["title"] if len(a["title"]) + len(BRAND) + 3 > 60 else f"{a['title']} | {BRAND}"
        page(path, t, a["desc"], body, "/stati/", [crumbs_ld(cr), art], og_type="article")

def build_contacts():
    cr = [(T("Главная"), "/"), (T("Контакты"), "/kontakty/")]
    body = f"""{crumbs(cr)}
<section class="s pt pb"><div class="w"><h1>{T("Контакты")}</h1><p class="lead">{T("{b} — аренда авто без водителя в Астане. Ежедневно {h}.").format(b=BRAND, h=HOURS)}</p></div></section>
{contacts_block()}
{book()}"""
    page("/kontakty/", T("Контакты — аренда авто в Астане | {b}").format(b=BRAND),
         T("Аренда авто без водителя в Астане: {ph}, WhatsApp, {st}. Ежедневно с 10:00 до 23:00.").format(ph=PHONE_DISPLAY, st=T(STREET)),
         body, "/kontakty/", [crumbs_ld(lcr(cr))])

def build_privacy():
    body = f"""{crumbs([(T("Главная"), "/"), (T("Политика конфиденциальности"), POLICY)])}
<section class="s lt pt"><div class="w prose"><h1>{T("Политика конфиденциальности")}</h1>
<h2>{T("Какие данные мы получаем")}</h2><p>{T("Имя, номер телефона и даты аренды, которые вы указываете в форме бронирования или пишете в WhatsApp, а также вопросы в ИИ-чате.")}</p>
<h2>{T("Зачем")}</h2><p>{T("Чтобы ответить на заявку, проверить, свободна ли машина, и оформить аренду. Мы не продаём и не передаём ваши данные третьим лицам, кроме случаев, предусмотренных законодательством Республики Казахстан.")}</p>
<h2>{T("Как отправляются данные")}</h2><p>{T("Форма бронирования не хранит данные на сайте: заявка открывается в WhatsApp, и вы сами отправляете сообщение. Вопросы в ИИ-чате обрабатываются только для ответа и не используются для рекламы.")}</p>
<h2>{T("Аналитика")}</h2><p>{T("Сайт может использовать Google Analytics и Google Ads, чтобы считать посещения и обращения. Эти сервисы используют файлы cookie; их можно отключить в настройках браузера.")}</p>
<h2>{T("Связь")}</h2><p>{T("Вопросы о данных — по телефону")} <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> {T("или в WhatsApp.")}</p></div></section>"""
    page(POLICY, T("Политика конфиденциальности | {b}").format(b=BRAND), T("Как {b} обрабатывает данные из формы бронирования и ИИ-чата.").format(b=BRAND), body)

def build_404():
    body = f"""<section class="w p404"><div><h1>404</h1><p class="lead">Такой страницы нет. Вернитесь на главную или напишите нам — подберём машину.<br><span lang="en">Page not found.</span></p>
<div class="act"><a class="btn c" href="/">На главную</a><a class="btn" href="{wa(hello())}" target="_blank" rel="noopener">{WA_IC}WhatsApp</a></div></div></section>"""
    page("/404.html", f"Страница не найдена | {BRAND}", "Страница не найдена.", body, noindex=True)

# ---------------------------------------------------------------- служебные файлы
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "anthropic-ai", "PerplexityBot", "Perplexity-User",
           "Google-Extended", "Googlebot", "Applebot", "Applebot-Extended", "Bingbot", "DuckAssistBot", "YouBot", "CCBot", "Meta-ExternalAgent", "MistralAI-User"]
def build_meta():
    bots = "".join(f"User-agent: {b}\nAllow: /\nDisallow: /api/\n\n" for b in AI_BOTS)
    (DIST / "robots.txt").write_text(f"{bots}User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    def pri(p):
        b = re.sub(r"^/(en|kz|zh)(?=/)", "", p)
        r = 1.0 if b == "/" else 0.8 if b.startswith(("/avto/", "/klass/", "/ceny/")) else 0.6
        return f"{r - (0.1 if b != p else 0):.1f}"
    sm = "".join(f"<url><loc>{SITE_URL}{p}</loc><lastmod>{ARTICLE_DATE}</lastmod><priority>{pri(p)}</priority></url>" for p in SITEMAP)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n', encoding="utf-8")
    (DIST / "site.webmanifest").write_text(json.dumps({"name": f"{BRAND} — аренда авто в Астане", "short_name": BRAND, "start_url": "/", "display": "standalone", "background_color": "#ffffff", "theme_color": "#ffffff",
        "icons": [{"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"}, {"src": "/assets/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]}, ensure_ascii=False), encoding="utf-8")
    fleet = "\n".join(f"- {c['full']} — {nb(c['price'])} ₸/сутки; {c['body'].lower()}, {cls_names(c).lower()}: {SITE_URL}/avto/{c['slug']}/" for c in sorted(CARS, key=lambda c: c["price"]))
    terms = "\n".join(f"- {h}: {p}" for _, h, p in TERMS) + "\n" + "\n".join(f"- {x}" for x in RULES)
    fac = "\n".join(f"- {h}: {p}" for h, p in PRICE_FACTORS)
    faq = "\n".join(f"- {q} {a}" for q, a in FAQ)
    cls = "\n".join(f"- {c['name']}: {SITE_URL}/klass/{c['slug']}/" for c in CLASSES)
    dist = "\n".join(f"- {d['name']}: {SITE_URL}/rayony/{d['slug']}/" for d in DISTRICTS)
    arts = "\n".join(f"- {a['title']}: {SITE_URL}/stati/{a['slug']}/" for a in ARTICLES)
    llms = f"""# {BRAND} — аренда авто без водителя в Астане

> Прокат автомобилей без водителя в Астане (Казахстан): {len(CARS)} машин от {nb(MIN_PRICE)} ₸ в сутки — эконом, бизнес, внедорожники и премиум. Только для личных поездок: не под такси, доставку и перевозки. Возраст от 20 лет, стаж от 2 лет, депозит {nb(DEPOSIT)} ₸ возвращается сразу после возврата авто. Ежедневно {HOURS}.

## Языки сайта
- Русский: {SITE_URL}/
- English: {SITE_URL}/en/
- Қазақша: {SITE_URL}/kz/
- 中文: {SITE_URL}/zh/

## Контакты
- Телефон и WhatsApp: {PHONE_DISPLAY}
- Адрес: {ADDRESS}
- График: ежедневно {HOURS}

## Условия аренды
{terms}

## От чего зависит цена
{fac}

## Автопарк и цены (за сутки)
{fleet}

## Классы
{cls}

## Районы Астаны (офис или доставка по адресу за доплату)
{dist}

## Статьи
{arts}

## Частые вопросы
{faq}

## Разделы
- Цены: {SITE_URL}/ceny/
- Условия: {SITE_URL}/usloviya/
- Контакты: {SITE_URL}/kontakty/
"""
    (DIST / "llms.txt").write_text(llms, encoding="utf-8")

def build_chat_data():
    """/assets/chat-<язык>.json — машины (фото, цена) и фразы ИИ-чата; грузится только при открытии чата."""
    cars = [{"s": c["slug"], "n": c["full"], "p": c["price"], "u": U(f"/avto/{c['slug']}/"), "i": c["ph"][0] if c["ph"] else "",
             "c": c["cls"], "y": c["year"] or 0, "k": CHAT_ALIASES.get(c["model"], c["model"].lower())} for c in sorted(CARS, key=lambda x: x["price"])]
    t = {k: T(v) for k, v in CHAT_T.items()}
    t["cls"] = {c["slug"]: T(c["name"]) for c in CLASSES}
    (DIST / "assets" / f"chat-{L}.json").write_text(json.dumps({"cars": cars, "t": t}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

def main():
    global L
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "assets", DIST / "assets")
    shutil.copyfile(ROOT / "src" / "app.js", DIST / "assets" / "app.js")
    if (ROOT / "assets" / "favicon.ico").exists(): shutil.copyfile(ROOT / "assets" / "favicon.ico", DIST / "favicon.ico")
    got = 0
    for c in CARS:
        c["ph"] = photos(c); got += len(c["ph"])
    for L in LANGS:
        build_home(); build_park(); build_cars(); build_classes(); build_prices(); build_terms(); build_contacts(); build_privacy(); build_chat_data()
        if L == "ru":
            build_districts(); build_articles(); build_404()
    L = "ru"; build_meta()
    print("страниц:", len(SITEMAP) + 1, "фото:", got)
    for p, t, d in LONG: print(f"  длинный title/description: {p} title={t} desc={d}")
    miss = {k: v for k, v in MISSING.items() if v}
    if miss:
        (ROOT / "src" / "_missing.json").write_text(json.dumps(miss, ensure_ascii=False, indent=1), encoding="utf-8")
        print("НЕТ ПЕРЕВОДА:", {k: len(v) for k, v in miss.items()})
        sys.exit(1)
    elif (ROOT / "src" / "_missing.json").exists(): (ROOT / "src" / "_missing.json").unlink()

if __name__ == "__main__":
    main()
