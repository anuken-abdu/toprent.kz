# -*- coding: utf-8 -*-
"""Google Ads для веб-интерфейса: Инструменты → Массовые действия → Загрузки (xlsx), файлы 0 → 5.
13 самых рентабельных ключей, фразовое соответствие с городом. Первые 3 заголовка закреплены на позиции 1.
Запуск: python3 src/ads.py → google-ads/"""
import sys, collections
from pathlib import Path
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font
sys.path.insert(0, str(Path(__file__).parent))
from data import SITE_URL, PHONE_DISPLAY, CARS, MIN_PRICE

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "google-ads"
CAMP = "TopAutorent Поиск"
NEG_LIST = "TopAutorent минус-слова"
GEO = "Astana, Kazakhstan"
BUDGET = 5
ERR = []

COMMON_H = ["Депозит 20 000 ₸, вернём сразу", "Аренда с 20 лет, стаж 2 года", "Только удостоверение и права",
            "Ежедневно с 10:00 до 23:00", "Бронь в WhatsApp", "Эконом, бизнес и премиум", "Цены на сайте — без звонка",
            "Цена и условия каждой машины", "Без водителя — за рулём вы", "Toyota, Hyundai, Lexus, Kia"]
COMMON_D = ["С 20 лет и стажем от 2 лет. Нужны только удостоверение личности и водительские права.",
            "Депозит 20 000 ₸ возвращаем сразу после возврата авто. Ежедневно с 10:00 до 23:00."]

# (группа, URL, ключи, 3 закреплённых, свои заголовки, 2 описания, Path 1)
G = [
    ("Аренда авто", "/", ["аренда авто астана", "аренда машины астана", "прокат авто астана", "аренда авто без водителя астана", "аренда авто посуточно астана"],
     ["{KeyWord:Аренда авто в Астане}", "Аренда авто без водителя", "Прокат авто в Астане"],
     ["От 15 000 ₸ в сутки", "Hyundai Accent — Mercedes G63", "Посуточная аренда авто"],
     ["Аренда авто без водителя в Астане от 15 000 ₸ в сутки. Эконом, бизнес и премиум.",
      "Выберите машину на сайте — у каждой своя страница с фото, ценой и условиями."], "аренда-авто"),
    ("Toyota Camry", "/klass/biznes/", ["аренда камри астана", "прокат камри астана"],
     ["{KeyWord:Аренда Camry Астана}", "Аренда Toyota Camry 70", "Camry 70 — 30 000 ₸/сутки"],
     ["Бизнес-класс без водителя", "Sonata, K5, Lexus ES", "Для встреч и праздников"],
     ["Toyota Camry 70 без водителя в Астане — 30 000 ₸ в сутки. Есть Sonata, Kia K5, Lexus ES.",
      "Просторный седан бизнес-класса для деловых встреч, праздников и командировок."], "camry"),
    ("Внедорожники", "/klass/vnedorozhniki/", ["аренда внедорожника астана", "аренда кроссовера астана"],
     ["{KeyWord:Аренда внедорожника}", "Внедорожники в аренду", "Tucson, LC200, LX570, G63"],
     ["Кроссоверы от 20 000 ₸/сутки", "Для семьи и зимних дорог", "Land Cruiser 200 в аренду"],
     ["Hyundai Creta и Tucson, Toyota Land Cruiser 200, Lexus LX570, Mercedes G63 без водителя.",
      "Высокая посадка и вместительный багажник — для семьи, багажа и зимы в Астане."], "внедорожники"),
    ("Премиум", "/klass/premium/", ["аренда гелендвагена астана", "аренда мерседес астана", "аренда лексус астана"],
     ["{KeyWord:Аренда премиум-авто}", "Mercedes G63 и W222", "Lexus LX570 в аренду"],
     ["Премиум без водителя", "Для свадеб и VIP-встреч", "Гелендваген в аренду"],
     ["Mercedes G63, Mercedes S-Class W222, Lexus LX570 и Land Cruiser 200 без водителя.",
      "Для свадеб, статусных встреч и особых событий. Цены и фото каждой машины на сайте."], "премиум"),
    ("Эконом", "/klass/ekonom/", ["аренда авто недорого астана"],
     ["{KeyWord:Недорогая аренда авто}", "Аренда авто от 15 000 ₸", "Эконом-авто без водителя"],
     ["Accent, Elantra, Corolla", "Hyundai Creta — 20 000 ₸", "Недорого на каждый день"],
     ["Hyundai Accent, Elantra, Creta и Toyota Corolla без водителя — от 15 000 ₸ в сутки.",
      "Экономичные машины для поездок по городу, работы и встреч гостей."], "эконом"),
]

NEG = ["с водителем", "такси", "под такси", "яндекс", "uber", "убер", "выкуп", "с выкупом", "последующим выкупом",
       "лизинг", "кредит", "рассрочка", "купить", "продажа", "продам", "авто с пробегом", "автосалон", "тест драйв",
       "грузовик", "грузовой", "газель", "спецтехника", "автобус", "микроавтобус", "эвакуатор", "автокран", "манипулятор",
       "вакансия", "вакансии", "работа", "работу", "зарплата", "курьер", "доставка еды",
       "без залога", "без депозита", "без стажа", "без прав", "18 лет", "19 лет",
       "квартира", "квартиры", "гараж", "парковка", "автошкола", "права категории",
       "olx", "колеса", "kolesa", "крыша", "kaspi", "каспи", "2гис", "отзывы",
       "алматы", "шымкент", "караганда", "актобе", "павлодар", "кокшетау", "атырау",
       "игра", "фильм", "скачать", "фото", "картинки"]

def chk(t, n, what):
    v = t.split(":", 1)[1].rstrip("}") if t.startswith("{KeyWord:") else t
    if len(v) > n: ERR.append(f"{what} >{n}: {t} ({len(v)})")
    return t

def xlsx(path, cols, rows):
    wb = Workbook(); ws = wb.active; ws.title = "Upload"; ws.append(cols)
    for c in ws[1]: c.font = Font(bold=True)
    for r in rows: ws.append([r.get(c, "") for c in cols])
    for i, c in enumerate(cols, 1): ws.column_dimensions[ws.cell(1, i).column_letter].width = max(14, min(48, len(c) + 4))
    wb.save(path)

def campaigns_file(path, template):
    wb = openpyxl.load_workbook(template)
    for n in list(wb.sheetnames):
        if n.startswith("(Example)"): del wb[n]
    ws = wb[wb.sheetnames[0]]
    hdr = [c.value for c in ws[2]]
    if "EU political ads" not in hdr:
        ws.cell(1, len(hdr) + 1, "#Required: EU political ads"); ws.cell(2, len(hdr) + 1, "EU political ads"); hdr.append("EU political ads")
    r = {"Action": "Add", "Campaign status": "Paused", "Campaign": CAMP, "Campaign type": "Search", "Networks": "Google search",
         "Budget": BUDGET, "Budget type": "Daily", "Bid strategy type": "Maximize clicks", "Location": GEO, "EU political ads": "No"}
    ws.append([r.get(h) for h in hdr]); wb.save(path)

def main():
    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*"):
        if f.is_file(): f.unlink()
    H = [f"Headline {i}" for i in range(1, 16)]; D = [f"Description {i}" for i in range(1, 5)]
    grp, kws, ads, txt = [], [], [], []
    seen = collections.Counter()
    for name, path, keys, top, own, ds, p1 in G:
        if not (ROOT / "dist" / path.strip("/") / "index.html").exists(): ERR.append(f"нет страницы {path}")
        grp.append({"Action": "Add", "Campaign": CAMP, "Ad group": name, "Ad group state": "Enabled"})
        words = [f'"{k}"' for k in keys]
        for w in words:
            seen[w] += 1; plain = w.strip('"')
            kws.append({"Action": "Add", "Campaign": CAMP, "Ad group": name, "Keyword": w})
            for ng in NEG:
                if f" {ng} " in f" {plain} ": ERR.append(f"минус «{ng}» режет «{plain}»")
        heads = []
        for t in top + own + COMMON_H:
            if t.lower() not in {x.lower() for x in heads}: heads.append(t)
        heads = heads[:15]; descs = ds + COMMON_D
        url = SITE_URL + path
        r = {"Action": "Add", "Campaign": CAMP, "Ad group": name, "Ad type": "Responsive search ad", "Final URL": url, "Path 1": chk(p1, 15, "path1"), "Path 2": "астана"}
        for i, h in enumerate(heads): r[H[i]] = chk(h, 30, "headline")
        for i, d in enumerate(descs): r[D[i]] = chk(d, 90, "description")
        for i in range(3): r[H[i] + " position"] = 1
        r["Description 1 position"] = 1
        ads.append(r)
        txt += [f"Группа: {name}", f"URL: {url}", "Ключи: " + ", ".join(words), "Заголовки (первые 3 закреплены): " + " | ".join(heads), "Описания: " + " | ".join(descs), ""]
    if [k for k, v in seen.items() if v > 1]: ERR.append("дубли ключей")
    if not 10 <= len(kws) <= 15: ERR.append(f"ключей {len(kws)}")
    if ERR: print("\n".join(ERR)); raise SystemExit(1)
    campaigns_file(OUT / "0-sozdat-kampaniyu.xlsx", ROOT / "src" / "templates" / "Create_New_Campaigns.xlsx")
    xlsx(OUT / "1-gruppy.xlsx", ["Action", "Campaign", "Ad group", "Ad group state"], grp)
    xlsx(OUT / "2-klyuchevye-slova.xlsx", ["Action", "Campaign", "Ad group", "Keyword"], kws)
    cols = ["Action", "Campaign", "Ad group", "Ad type"] + [x for h in H for x in (h, h + " position")] + [x for d in D for x in (d, d + " position")] + ["Path 1", "Path 2", "Final URL"]
    xlsx(OUT / "3-obyavleniya.xlsx", cols, ads)
    xlsx(OUT / "4-minus-slova-v-spisok.xlsx", ["Action", "Negative keyword list name", "Negative keyword", "Keyword or list", "Match type"],
         [{"Action": "Add", "Negative keyword list name": NEG_LIST, "Negative keyword": x, "Keyword or list": "Keyword", "Match type": "Phrase Match"} for x in NEG])
    xlsx(OUT / "5-privyazat-spisok-k-kampanii.xlsx", ["Action", "Negative keyword", "Keyword or list", "Campaign"],
         [{"Action": "Add", "Negative keyword": NEG_LIST, "Keyword or list": "List", "Campaign": CAMP}])
    head = [f"КАМПАНИЯ: {CAMP} (создаётся файлом 0, на паузе)", f"Местоположение: {GEO}; бюджет {BUDGET} в день (в валюте аккаунта)",
            f"Групп: {len(grp)}, ключей: {len(kws)}, минус-слов: {len(NEG)} (список «{NEG_LIST}»)",
            "ПОРЯДОК: Инструменты → Массовые действия → Загрузки → файлы 0, 1, 2, 3, 4, 5 по очереди → Применить", ""]
    ext = ["РАСШИРЕНИЯ:", "  Звонок: " + PHONE_DISPLAY,
           "  Уточнения: Депозит 20 000 ₸ · С 20 лет · Стаж от 2 лет · 10:00–23:00 · Бронь в WhatsApp",
           "  Быстрые ссылки (абсолютные адреса):",
           f"    Автопарк — {SITE_URL}/avto/", f"    Цены — {SITE_URL}/ceny/", f"    Условия аренды — {SITE_URL}/usloviya/",
           f"    Премиум — {SITE_URL}/klass/premium/", f"    Внедорожники — {SITE_URL}/klass/vnedorozhniki/", f"    Контакты — {SITE_URL}/kontakty/", "",
           "НАСТРОЙКИ ПОСЛЕ ЗАГРУЗКИ:", "  • Сети: только Google Поиск (снять партнёров и КМС)", "  • AI Max и широкое соответствие — выключены",
           "  • Местоположение: «Присутствие» в Астане", "  • Язык: русский и казахский", "  • Конверсия: звонок/WhatsApp/заявка — пришлите код, вставлю на сайт",
           "  • Через 2–3 дня: Поисковые запросы → мусор в список минус-слов"]
    (OUT / "6-teksty-i-nastroyki.txt").write_text("\n".join(head + txt + ext) + "\n", encoding="utf-8")
    print("групп", len(grp), "ключей", len(kws), "минус", len(NEG))

if __name__ == "__main__":
    main()
