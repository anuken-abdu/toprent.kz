TOPRENT — сайт аренды авто без водителя (www.toprent.kz)
=========================================================

Как устроено
- Все данные (телефон, адрес, машины, цены, районы, статьи, теги Google) — в src/data.py.
- Сайт собирается командой: python3 src/build.py  ->  папка dist/
- Vercel собирает сам (buildCommand в vercel.json), руками dist/ заливать не нужно.

Запуск на Vercel
1. Залить проект в GitHub и импортировать в Vercel (Framework: Other).
2. Settings -> Domains: добавить www.toprent.kz (основной) и toprent.kz с редиректом на www.
3. У регистратора домена: A-запись @ -> 76.76.21.21, CNAME www -> cname.vercel-dns.com.
   Старые A/AAAA для @ и www удалить. MX и TXT (почта) не трогать.
4. Settings -> Environment Variables: ANTHROPIC_API_KEY = ключ (для ИИ-чата). Без ключа чат
   работает встроенным автоответчиком.

Фото машин
1. Положить фото в папку orig/ с именами по коду машины: toyota-camry-70-2020-1.jpg … -4.jpg
   (коды — поле slug в src/data.py).
2. Выполнить: python3 src/images.py  (нужен Pillow) — получатся WebP 480/800/1200 без EXIF и GPS
   в assets/img/cars/.
3. python3 src/build.py — фото появятся в карточках, на страницах машин и в превью.

Теги Google и конверсии
- В src/data.py: TAG_ID = "GTM-…", GADS_ID = "AW-…", GADS_LABEL = "метка" (копировать текстом).
- После сборки тег стоит в <head> каждой страницы, на всех ссылках tel: и WhatsApp — onclick
  с gtag_report_conversion. Проверка: Ctrl+U, Google Tag Assistant.

После запуска
- Search Console: добавить ресурс, отправить https://www.toprent.kz/sitemap.xml,
  запросить индексирование главной и ключевых страниц.
- Google Business Profile, 2ГИС, Instagram, WhatsApp Business — ссылка на www.toprent.kz.
- Проверить скорость живого сайта: https://www.anuken.kz/skorost.html

Разработка и продвижение: Anuken.kz — https://www.anuken.kz
