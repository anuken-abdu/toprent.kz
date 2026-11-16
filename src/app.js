(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var CFG = window.__C || {};
  var fmt = function (n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, " "); };

  /* ---------- конверсии: одна функция Google (gtag_report_conversion) ----------
     Ссылки tel: и wa.me получают onclick при сборке; здесь — только форма и ссылки, созданные скриптом (чат). */
  function conv() { if (typeof window.gtag_report_conversion === "function") window.gtag_report_conversion(); }

  /* ---------- мобильное меню ---------- */
  var drawer = $("#drawer"), burger = $(".burger");
  if (drawer && burger) {
    var close = function () { drawer.classList.remove("on"); burger.setAttribute("aria-expanded", "false"); document.body.style.overflow = ""; burger.focus(); };
    burger.addEventListener("click", function () { drawer.classList.add("on"); burger.setAttribute("aria-expanded", "true"); document.body.style.overflow = "hidden"; var b = $("button", drawer); if (b) b.focus(); });
    $("[data-close]", drawer).addEventListener("click", close);
    $$("a", drawer).forEach(function (a) { a.addEventListener("click", function () { drawer.classList.remove("on"); burger.setAttribute("aria-expanded", "false"); document.body.style.overflow = ""; }); });
    drawer.addEventListener("click", function (e) { if (e.target === drawer) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && drawer.classList.contains("on")) close(); });
  }

  /* ---------- фильтр и сортировка автопарка ---------- */
  var grid = $("[data-grid]");
  if (grid) {
    var cards = $$(".card", grid), cur = "all";
    var apply = function () { cards.forEach(function (c) { c.hidden = !(cur === "all" || (" " + c.dataset.cls + " ").indexOf(" " + cur + " ") > -1); }); };
    $$("[data-f]").forEach(function (b) {
      b.addEventListener("click", function () {
        cur = b.dataset.f;
        $$("[data-f]").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        apply();
      });
    });
    var srt = $("[data-sort]"), asc = true;
    if (srt) srt.addEventListener("click", function () {
      cards.sort(function (a, b) { return asc ? b.dataset.p - a.dataset.p : a.dataset.p - b.dataset.p; });
      asc = !asc;
      cards.forEach(function (c) { grid.appendChild(c); });
      srt.textContent = asc ? "Цена ↑" : "Цена ↓";
    });
  }

  /* ---------- галерея ---------- */
  var gm = $(".gal-m img");
  $$(".gal-t button[data-src]").forEach(function (b) {
    b.addEventListener("click", function () {
      var base = b.dataset.src.replace(/-1200\.webp$/, "");
      gm.srcset = base + "-480.webp 480w, " + base + "-800.webp 800w, " + base + "-1200.webp 1200w"; gm.src = base + "-800.webp";
      $$(".gal-t button").forEach(function (x) { x.setAttribute("aria-current", x === b ? "true" : "false"); });
    });
  });

  /* ---------- бронь: расчёт и отправка в WhatsApp ---------- */
  var form = $("#book");
  if (form) {
    var el = form.elements, out = $("[data-calc]", form);
    var today = new Date(); today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
    var iso = today.toISOString().slice(0, 10);
    el.d1.min = iso; el.d2.min = iso;
    var days = function () {
      if (!el.d1.value || !el.d2.value) return 0;
      var n = Math.round((new Date(el.d2.value) - new Date(el.d1.value)) / 864e5);
      return n > 0 ? n : 0;
    };
    var calc = function () {
      var o = el.car.options[el.car.selectedIndex], p = +(o && o.dataset.p || 0), n = days();
      if (el.d1.value) el.d2.min = el.d1.value;
      if (!p) { out.innerHTML = "<span>Выберите машину</span><span>Депозит: <b>" + fmt(CFG.dep) + " ₸</b></span>"; return; }
      out.innerHTML = n
        ? "<span>" + n + " сут. × " + fmt(p) + " ₸ = <b>" + fmt(n * p) + " ₸</b></span><span>+ депозит <b>" + fmt(CFG.dep) + " ₸</b> (вернём)</span>"
        : "<span>" + fmt(p) + " ₸ / сутки</span><span>+ депозит <b>" + fmt(CFG.dep) + " ₸</b> (вернём)</span>";
    };
    ["change", "input"].forEach(function (ev) { form.addEventListener(ev, calc); });
    calc();
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ph = el.phone.value.replace(/\D/g, "");
      if (ph.length < 10) { el.phone.setCustomValidity("Укажите номер телефона"); el.phone.reportValidity(); return; }
      el.phone.setCustomValidity("");
      var o = el.car.options[el.car.selectedIndex], n = days(), g = el.get ? el.get.value : "";
      var d = function (v) { return v ? v.split("-").reverse().join(".") : "—"; };
      var t = "Здравствуйте! Хочу арендовать авто.\nМашина: " + (o && o.value ? o.dataset.n : "подберите") +
        "\nДаты: " + d(el.d1.value) + " — " + d(el.d2.value) + (n ? " (" + n + " сут.)" : "") + (g ? "\nПолучение: " + g : "") +
        "\nИмя: " + (el.name.value || "—") + "\nТелефон: " + el.phone.value;
      conv();
      window.open("https://wa.me/" + CFG.wa + "?text=" + encodeURIComponent(t), "_blank", "noopener");
    });
    el.phone.addEventListener("input", function () { el.phone.setCustomValidity(""); });
  }

  /* ---------- плавающие кнопки: назад, наверх, связь ---------- */
  var top = $("[data-top]"), back = $("[data-back]");
  var onScroll = function () { if (top) top.hidden = window.scrollY < 600; };
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  if (top) top.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
  if (back) {
    var same = document.referrer && document.referrer.indexOf(location.origin) === 0;
    back.hidden = location.pathname === "/" && !same;
    back.addEventListener("click", function (e) { if (same && history.length > 1) { e.preventDefault(); history.back(); } });
  }
  var fm = $(".flo-m"), fp = $(".flo-p");
  var floClose = function () { if (fp) { fp.hidden = true; fm.setAttribute("aria-expanded", "false"); } };
  if (fm) {
    fm.addEventListener("click", function (e) { e.stopPropagation(); var o = fp.hidden; fp.hidden = !o; fm.setAttribute("aria-expanded", o ? "true" : "false"); });
    document.addEventListener("click", function (e) { if (fp && !fp.hidden && !fp.contains(e.target)) floClose(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") floClose(); });
  }

  /* ---------- анимация на кнопке связи: грузим после загрузки страницы, чтобы не тормозить первый экран ---------- */
  var fi = fm && $("img[data-anim]", fm);
  if (fi && !(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches)) {
    var anim = function () { setTimeout(function () { fi.src = fi.dataset.anim; }, 1200); };
    if (document.readyState === "complete") anim(); else window.addEventListener("load", anim);
  }

  /* ---------- ИИ-чат: окно строится при первом открытии; /api/chat, без ключа — встроенный автоответчик.
     Машины (фото, цена) — /assets/cars.json, грузится при открытии чата. ИИ помечает машины кодами [[slug]] ---------- */
  var chat, list, flo = $(".flo"), hist = [], CARS = [];
  var WA_BASE = "https://wa.me/" + CFG.wa + "?text=";
  var CLS = { ekonom: "Эконом", biznes: "Бизнес", vnedorozhniki: "Внедорожники и кроссоверы", premium: "Премиум" };
  var FB = [
    [/депоз|залог/i, "Депозит — " + fmt(CFG.dep) + " ₸. Возвращаем сразу после того, как вы вернёте машину."],
    [/возраст|лет|стаж/i, "Арендовать можно с 20 лет при водительском стаже от 2 лет."],
    [/документ|паспорт|удостовер|прав/i, "Нужны удостоверение личности и водительские права."],
    [/такси|яндекс|доставк.*(еды|заказ)|курьер/i, "Под режим такси и другую работу машины не выдаём."],
    [/привез|доставк|адрес.*машин|район/i, "Доставка по Астане — за доплату, сумма зависит от адреса. Забрать машину в офисе (" + CFG.addr + ") — без доплаты."],
    [/город|трасс|выезд|поездк|межгород/i, "Машины выдаём для поездок по Астане. Выезд за город — по согласованию и с доплатой, сумма зависит от направления."],
    [/график|время|работаете|час/i, "Работаем ежедневно с 10:00 до 23:00."],
    [/цен|стоим|сколько|прайс|тенге|₸/i, "От 15 000 ₸ в сутки (Hyundai Accent) до 100 000 ₸ (Lexus LX570 2019, Mercedes W222). Выберите класс кнопкой ниже — покажу машины с фото и ценой."],
    [/адрес|где|наход/i, "Мы в Астане: " + CFG.addr + ". Перед приездом позвоните: " + CFG.phone + "."]
  ];
  var CLS_RE = [[/эконом|дешев|бюджет|недорог/i, "ekonom"], [/бизнес/i, "biznes"], [/внедорож|джип|кроссовер|suv/i, "vnedorozhniki"], [/премиум|люкс|vip|вип|свадьб|статус/i, "premium"]];
  var bySlug = function (s) { for (var i = 0; i < CARS.length; i++) if (CARS[i].s === s) return CARS[i]; return null; };
  var loadCars = function () {
    if (CARS.length) return Promise.resolve(CARS);
    return fetch("/assets/cars.json").then(function (r) { return r.json(); }).then(function (d) { CARS = d || []; return CARS; }).catch(function () { return CARS; });
  };
  var scroll = function () { list.scrollTop = list.scrollHeight; };
  var add = function (t, who) { var d = document.createElement("div"); d.className = "msg " + (who || ""); d.textContent = t; list.appendChild(d); scroll(); return d; };
  var lastQ = function () { for (var i = hist.length - 1; i >= 0; i--) if (hist[i].role === "user") return hist[i].content; return ""; };
  var actions = function () {
    var q = lastQ(), box = document.createElement("div"); box.className = "msg-a";
    var tel = document.createElement("a"); tel.href = "tel:" + CFG.tel; tel.textContent = "Позвонить";
    var w = document.createElement("a"); w.href = WA_BASE + encodeURIComponent("Здравствуйте! Хочу арендовать авто." + (q ? "\nВопрос из чата: " + q : "")); w.target = "_blank"; w.rel = "noopener"; w.textContent = "В WhatsApp";
    [tel, w].forEach(function (a) { a.addEventListener("click", function () { conv(); }); box.appendChild(a); });
    list.appendChild(box); scroll();
  };
  /* карточки машин: фото, цена за сутки, бронь в WhatsApp, страница машины */
  var cards = function (cars) {
    var box = document.createElement("div"); box.className = "msg-c" + (cars.length > 1 ? " many" : "");
    cars.forEach(function (c) {
      var el = document.createElement("div"); el.className = "cc";
      var pic = document.createElement("a"); pic.className = "cc-i"; pic.href = c.u; pic.setAttribute("aria-label", c.n + " — подробнее");
      if (c.i) { var im = document.createElement("img"); im.src = c.i + "-480.webp"; im.width = 480; im.height = 320; im.alt = c.n; im.decoding = "async"; im.addEventListener("load", scroll); pic.appendChild(im); }
      else { var ph = document.createElement("span"); ph.textContent = c.n.split(" ")[0]; pic.appendChild(ph); }
      var b = document.createElement("div"); b.className = "cc-b";
      var nm = document.createElement("b"); nm.textContent = c.n;
      var pr = document.createElement("span"); pr.textContent = fmt(c.p) + " ₸ / сутки";
      var ac = document.createElement("div"); ac.className = "cc-a";
      var w = document.createElement("a"); w.href = WA_BASE + encodeURIComponent("Здравствуйте! Хочу арендовать " + c.n + " (" + fmt(c.p) + " ₸ в сутки). Подскажите, свободна ли машина на мои даты?");
      w.target = "_blank"; w.rel = "noopener"; w.textContent = "Забронировать"; w.addEventListener("click", function () { conv(); });
      var more = document.createElement("a"); more.href = c.u; more.textContent = "Подробнее";
      ac.appendChild(w); ac.appendChild(more); b.appendChild(nm); b.appendChild(pr); b.appendChild(ac);
      el.appendChild(pic); el.appendChild(b); box.appendChild(el);
    });
    list.appendChild(box); scroll();
  };
  /* какие машины упомянуты: сначала коды [[slug]] от ИИ, иначе полные названия в тексте */
  var pick = function (t) {
    var out = [], m, re = /\[\[([a-z0-9-]+)\]\]/g;
    while ((m = re.exec(t))) { var c = bySlug(m[1]); if (c && out.indexOf(c) < 0) out.push(c); }
    if (!out.length) CARS.forEach(function (c) { if (t.indexOf(c.n) > -1) out.push(c); });
    return out.slice(0, 4);
  };
  var strip = function (t) { return t.replace(/\s*\[\[[a-z0-9-]*\]\]/g, "").replace(/[ \t]+$/gm, "").trim(); };
  /* автоответчик: сначала машина по названию (камри, крузак, гелик…), потом класс, потом частые вопросы */
  var findCars = function (q) {
    var low = q.toLowerCase(), hit = CARS.filter(function (c) { return new RegExp(c.k, "i").test(low); });
    var yr = low.match(/20\d\d/);
    if (yr && hit.some(function (c) { return String(c.y) === yr[0]; })) hit = hit.filter(function (c) { return String(c.y) === yr[0]; });
    return hit;
  };
  var ofClass = function (k) { return CARS.filter(function (c) { return c.c.indexOf(k) > -1; }); };
  var local = function (q) {
    var hit = findCars(q);
    if (hit.length) return { t: hit.length === 1
      ? hit[0].n + " — " + fmt(hit[0].p) + " ₸ в сутки, плюс депозит " + fmt(CFG.dep) + " ₸ (вернём). Нажмите «Забронировать» — менеджер проверит, свободна ли машина на ваши даты."
      : "Вот что есть — цена за сутки на карточках. Плюс депозит " + fmt(CFG.dep) + " ₸ (вернём). Нажмите «Забронировать» у нужной машины.", c: hit.slice(0, 4) };
    for (var i = 0; i < CLS_RE.length; i++) if (CLS_RE[i][0].test(q)) return classAns(CLS_RE[i][1]);
    for (var j = 0; j < FB.length; j++) if (FB[j][0].test(q)) return { t: FB[j][1], c: [] };
    return { t: "Подскажу по машинам, ценам и условиям. Выберите класс кнопкой ниже или напишите модель — покажу фото и цену. Забронировать: WhatsApp или " + CFG.phone + ".", c: [] };
  };
  var classAns = function (k) {
    var cs = ofClass(k);
    return { t: CLS[k] + ": " + cs.length + " " + (cs.length === 1 ? "машина" : cs.length < 5 ? "машины" : "машин") + ", от " + fmt(cs[0] ? cs[0].p : 0) + " ₸ в сутки. Листайте карточки и нажмите «Забронировать» у нужной.", c: cs };
  };
  var reply = function (t, cs) {
    add(t); hist.push({ role: "assistant", content: t });
    if (cs && cs.length) cards(cs); else actions();
  };
  var ask = function (q) {
    q = (q || "").trim(); if (!q) return;
    add(q, "u"); hist.push({ role: "user", content: q });
    var w = add("печатает…", "t");
    var ctrl = window.AbortController ? new AbortController() : null;
    var to = setTimeout(function () { if (ctrl) ctrl.abort(); }, 15000);
    var fallback = function () { clearTimeout(to); loadCars().then(function () { w.remove(); var a = local(q); reply(a.t, a.c); }); };
    Promise.all([loadCars(), fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ messages: hist.slice(-12), page: location.pathname }), signal: ctrl ? ctrl.signal : undefined })
      .then(function (r) { if (!r.ok) throw 0; return r.json(); })])
      .then(function (res) {
        var d = res[1]; if (!d || !d.text) throw 0;
        clearTimeout(to); w.remove();
        var cs = pick(d.text), t = strip(d.text);
        if (!cs.length) cs = findCars(q).slice(0, 4);
        reply(t || "Вот подходящая машина.", cs);
      })
      .catch(fallback);
  };
  var askClass = function (b) {
    var k = b.dataset.cls; add(b.textContent, "u"); hist.push({ role: "user", content: "Покажи машины класса " + b.textContent });
    loadCars().then(function () { var a = classAns(k); reply(a.t, a.c); });
  };
  var closeChat = function () { chat.hidden = true; if (flo) flo.hidden = false; };
  var buildChat = function () {
    var t = $("#chat-t"); if (!t) return false;
    document.body.appendChild(t.content.cloneNode(true));
    chat = $("#chat"); list = $(".chat-l", chat);
    $("[data-chat-x]", chat).addEventListener("click", closeChat);
    $(".chat-f", chat).addEventListener("submit", function (e) { e.preventDefault(); var i = this.elements.q; ask(i.value); i.value = ""; });
    $$(".chat-q button", chat).forEach(function (b) { b.addEventListener("click", function () { if (b.dataset.cls) askClass(b); else ask(b.textContent); }); });
    $(".chat-w", chat).addEventListener("click", function () { conv(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !chat.hidden) closeChat(); });
    add("Здравствуйте! Я ИИ-консультант " + CFG.brand + ". Выберите класс или напишите, какая машина нужна, — покажу фото и цену за сутки.");
    loadCars();
    return true;
  };
  var openChat = function () {
    floClose();
    if (!chat && !buildChat()) return;
    chat.hidden = false; if (flo) flo.hidden = true;
    setTimeout(function () { var i = $("input", chat); if (i && window.innerWidth > 767) i.focus(); }, 50);
  };
  $$("[data-chat]").forEach(function (b) { b.addEventListener("click", openChat); });
})();
