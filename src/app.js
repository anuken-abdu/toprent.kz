(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var CFG = window.__C || {};
  var TT = CFG.t || {};
  var tt = function (k, d) { return TT[k] || d; };
  var fmt = function (n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, " "); };

  /* ---------- конверсии: одна функция Google (gtag_report_conversion) ----------
     Ссылки tel: и wa.me получают onclick при сборке; здесь — только форма и ссылки, созданные скриптом (чат). */
  function conv() { if (typeof window.gtag_report_conversion === "function") window.gtag_report_conversion(); }

  /* ---------- меню-панель ---------- */
  var drawer = $("#drawer"), burger = $(".burger");
  if (drawer && burger) {
    var shut = function (focus) { drawer.classList.remove("on"); burger.setAttribute("aria-expanded", "false"); document.body.style.overflow = ""; if (focus) burger.focus(); };
    burger.addEventListener("click", function () { drawer.classList.add("on"); burger.setAttribute("aria-expanded", "true"); document.body.style.overflow = "hidden"; var b = $("[data-close]", drawer); if (b) b.focus(); });
    $("[data-close]", drawer).addEventListener("click", function () { shut(true); });
    $$("a", drawer).forEach(function (a) { a.addEventListener("click", function () { shut(false); }); });
    drawer.addEventListener("click", function (e) { if (e.target === drawer) shut(true); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && drawer.classList.contains("on")) shut(true); });
  }

  /* ---------- дневной / ночной режим (выбор запоминается) ---------- */
  var root = document.documentElement, tcm = $('meta[name="theme-color"]');
  var paint = function () { if (tcm) tcm.content = root.dataset.theme === "dark" ? "#050506" : "#ffffff"; };
  paint();
  $$("[data-theme-t]").forEach(function (b) {
    b.addEventListener("click", function () {
      var t = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = t; paint();
      try { localStorage.setItem("theme", t); } catch (e) {}
    });
  });

  /* ---------- видео на фоне главной: только телефон, после загрузки страницы ---------- */
  var hv = $(".hero-v");
  if (hv && window.matchMedia && matchMedia("(max-width: 767px)").matches && !matchMedia("(prefers-reduced-motion: reduce)").matches &&
      !(navigator.connection && navigator.connection.saveData)) {
    var go = function () { hv.src = hv.getAttribute("data-src"); hv.muted = true; var p = hv.play(); if (p && p.catch) p.catch(function () {}); };
    if (document.readyState === "complete") go(); else window.addEventListener("load", go);
  }

  /* ---------- язык: закрыть список по клику вне и по Esc ---------- */
  var langs = $$("details.lang");
  document.addEventListener("click", function (e) { langs.forEach(function (d) { if (d.open && !d.contains(e.target)) d.open = false; }); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") langs.forEach(function (d) { d.open = false; }); });

  /* ---------- узоры секций: подгружаем, когда секция подходит к экрану ---------- */
  var pats = $$(".gr, .bk, #usloviya");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("pin"); io.unobserve(e.target); } }); }, { rootMargin: "400px 0px" });
    pats.forEach(function (x) { io.observe(x); });
  } else pats.forEach(function (x) { x.classList.add("pin"); });

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
      srt.textContent = asc ? tt("up", "Цена ↑") : tt("down", "Цена ↓");
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
      if (!p) { out.innerHTML = "<span>" + tt("pick", "Выберите машину") + "</span><span>" + tt("dep", "Депозит") + ": <b>" + fmt(CFG.dep) + " ₸</b></span>"; return; }
      out.innerHTML = n
        ? "<span>" + n + " " + tt("days", "сут.") + " × " + fmt(p) + " ₸ = <b>" + fmt(n * p) + " ₸</b></span><span>" + tt("plus", "+ депозит") + " <b>" + fmt(CFG.dep) + " ₸</b> (" + tt("back", "вернём") + ")</span>"
        : "<span>" + fmt(p) + " ₸ / " + tt("day", "сутки") + "</span><span>" + tt("plus", "+ депозит") + " <b>" + fmt(CFG.dep) + " ₸</b> (" + tt("back", "вернём") + ")</span>";
    };
    ["change", "input"].forEach(function (ev) { form.addEventListener(ev, calc); });
    calc();
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ph = el.phone.value.replace(/\D/g, "");
      if (ph.length < 10) { el.phone.setCustomValidity(tt("phone", "Укажите номер телефона")); el.phone.reportValidity(); return; }
      el.phone.setCustomValidity("");
      var o = el.car.options[el.car.selectedIndex], n = days(), g = el.get ? el.get.value : "";
      var d = function (v) { return v ? v.split("-").reverse().join(".") : "—"; };
      var t = tt("msg", "Здравствуйте! Хочу арендовать авто.") + "\n" + tt("car", "Машина") + ": " + (o && o.value ? o.dataset.n : tt("any", "подберите")) +
        "\n" + tt("dates", "Даты") + ": " + d(el.d1.value) + " — " + d(el.d2.value) + (n ? " (" + n + " " + tt("days", "сут.") + ")" : "") + (g ? "\n" + tt("get", "Получение") + ": " + g : "") +
        "\n" + tt("name", "Имя") + ": " + (el.name.value || "—") + "\n" + tt("tel", "Телефон") + ": " + el.phone.value;
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
     Машины и фразы на языке страницы — /assets/chat-<язык>.json, грузится при открытии чата. ИИ помечает машины кодами [[slug]] ---------- */
  var chat, list, flo = $(".flo"), hist = [], CARS = [], CT = {}, loaded = null;
  var WA_BASE = "https://wa.me/" + CFG.wa + "?text=";
  var fill = function (s, o) { return String(s || "").replace(/\{(\w+)\}/g, function (m, k) { return o[k] != null ? o[k] : m; }); };
  var ct = function (k, o) { return fill(CT[k] || "", o || {}); };
  var FB = [
    [/депоз|залог|deposit|押金/i, "f_dep"], [/возраст|лет|стаж|жас|өтіл|\bage\b|years|年龄|驾龄/i, "f_age"], [/документ|паспорт|удостовер|прав|құжат|куәлік|document|license|licence|passport|\bid\b|证件|驾照|护照/i, "f_doc"],
    [/такси|яндекс|курьер|taxi|uber|courier|出租|网约/i, "f_taxi"], [/привез|доставк|район|жеткіз|deliver|送车|送到/i, "f_del"],
    [/город|трасс|выезд|межгород|қала|out of town|outside|intercity|出城|外地/i, "f_city"], [/график|время|работаете|час|кесте|уақыт|hours|open|time|营业|时间/i, "f_time"],
    [/цен|стоим|сколько|прайс|тенге|₸|баға|қанша|price|cost|how much|价格|多少钱|费用/i, "f_price"], [/адрес|где|наход|мекенжай|қайда|address|where|location|地址|在哪/i, "f_addr"]
  ];
  var CLS_RE = [[/эконом|дешев|бюджет|недорог|арзан|economy|cheap|budget|经济|便宜/i, "ekonom"], [/бизнес|business|商务/i, "biznes"], [/внедорож|джип|кроссовер|suv|jeep|crossover|жол талғам|越野|SUV/i, "vnedorozhniki"], [/премиум|люкс|vip|вип|свадьб|статус|той|premium|luxury|wedding|豪华|婚礼/i, "premium"]];
  var bySlug = function (s) { for (var i = 0; i < CARS.length; i++) if (CARS[i].s === s) return CARS[i]; return null; };
  var loadCars = function () {
    if (!loaded) loaded = fetch("/assets/chat-" + (CFG.lang || "ru") + ".json").then(function (r) { return r.json(); })
      .then(function (d) { CARS = d.cars || []; CT = d.t || {}; return CARS; }).catch(function () { loaded = null; return CARS; });
    return loaded;
  };
  var plural = function (n) {
    if (CFG.lang !== "ru") return n + " " + ct("n5");
    var m = n % 100, k = n % 10;
    return n + " " + (m > 10 && m < 20 ? ct("n5") : k === 1 ? ct("n1") : k >= 2 && k <= 4 ? ct("n2") : ct("n5"));
  };
  var scroll = function () { list.scrollTop = list.scrollHeight; };
  var add = function (t, who) { var d = document.createElement("div"); d.className = "msg " + (who || ""); d.textContent = t; list.appendChild(d); scroll(); return d; };
  var lastQ = function () { for (var i = hist.length - 1; i >= 0; i--) if (hist[i].role === "user") return hist[i].content; return ""; };
  var actions = function () {
    var q = lastQ(), box = document.createElement("div"); box.className = "msg-a";
    var tel = document.createElement("a"); tel.href = "tel:" + CFG.tel; tel.textContent = ct("call");
    var w = document.createElement("a"); w.href = WA_BASE + encodeURIComponent(ct("hello") + (q ? "\n" + ct("q") + ": " + q : "")); w.target = "_blank"; w.rel = "noopener"; w.textContent = ct("wa");
    [tel, w].forEach(function (a) { a.addEventListener("click", function () { conv(); }); box.appendChild(a); });
    list.appendChild(box); scroll();
  };
  /* карточки машин: фото, цена за сутки, бронь в WhatsApp, страница машины */
  var carCards = function (cars) {
    var box = document.createElement("div"); box.className = "msg-c" + (cars.length > 1 ? " many" : "");
    cars.forEach(function (c) {
      var el = document.createElement("div"); el.className = "cc";
      var pic = document.createElement("a"); pic.className = "cc-i"; pic.href = c.u; pic.setAttribute("aria-label", c.n + " — " + ct("more"));
      if (c.i) { var im = document.createElement("img"); im.src = c.i + "-480.webp"; im.width = 480; im.height = 320; im.alt = c.n; im.decoding = "async"; im.addEventListener("load", scroll); pic.appendChild(im); }
      else { var ph = document.createElement("span"); ph.textContent = c.n.split(" ")[0]; pic.appendChild(ph); }
      var b = document.createElement("div"); b.className = "cc-b";
      var nm = document.createElement("b"); nm.textContent = c.n;
      var pr = document.createElement("span"); pr.textContent = fmt(c.p) + " " + ct("perday");
      var ac = document.createElement("div"); ac.className = "cc-a";
      var w = document.createElement("a"); w.href = WA_BASE + encodeURIComponent(ct("bookmsg", { car: c.n, p: fmt(c.p) }));
      w.target = "_blank"; w.rel = "noopener"; w.textContent = ct("book"); w.addEventListener("click", function () { conv(); });
      var more = document.createElement("a"); more.href = c.u; more.textContent = ct("more");
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
  var classAns = function (k) {
    var cs = ofClass(k);
    return { t: ct("class", { k: (CT.cls || {})[k] || k, n: plural(cs.length), p: fmt(cs[0] ? cs[0].p : 0) }), c: cs };
  };
  var local = function (q) {
    var hit = findCars(q), o = { dep: fmt(CFG.dep), addr: CFG.addr, phone: CFG.phone };
    if (hit.length) return { t: hit.length === 1 ? ct("one", { car: hit[0].n, p: fmt(hit[0].p), dep: fmt(CFG.dep) }) : ct("many", o), c: hit.slice(0, 4) };
    for (var i = 0; i < CLS_RE.length; i++) if (CLS_RE[i][0].test(q)) return classAns(CLS_RE[i][1]);
    for (var j = 0; j < FB.length; j++) if (FB[j][0].test(q)) return { t: ct(FB[j][1], o), c: [] };
    return { t: ct("def", o), c: [] };
  };
  var reply = function (t, cs) {
    add(t); hist.push({ role: "assistant", content: t });
    if (cs && cs.length) carCards(cs); else actions();
  };
  var ask = function (q) {
    q = (q || "").trim(); if (!q) return;
    add(q, "u"); hist.push({ role: "user", content: q });
    var w = add(ct("typing") || "…", "t");
    var ctrl = window.AbortController ? new AbortController() : null;
    var to = setTimeout(function () { if (ctrl) ctrl.abort(); }, 15000);
    var fallback = function () { clearTimeout(to); loadCars().then(function () { w.remove(); var a = local(q); reply(a.t, a.c); }); };
    Promise.all([loadCars(), fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ messages: hist.slice(-12), page: location.pathname, lang: CFG.lang }), signal: ctrl ? ctrl.signal : undefined })
      .then(function (r) { if (!r.ok) throw 0; return r.json(); })])
      .then(function (res) {
        var d = res[1]; if (!d || !d.text) throw 0;
        clearTimeout(to); w.remove();
        var cs = pick(d.text), t = strip(d.text);
        if (!cs.length) cs = findCars(q).slice(0, 4);
        reply(t || ct("fit"), cs);
      })
      .catch(fallback);
  };
  var askClass = function (b) {
    var k = b.dataset.cls; add(b.textContent, "u");
    loadCars().then(function () { hist.push({ role: "user", content: ct("showcls", { k: b.textContent }) }); var a = classAns(k); reply(a.t, a.c); });
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
    loadCars().then(function () { add(ct("hi")); });
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
