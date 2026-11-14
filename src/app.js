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
      gm.src = b.dataset.src;
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

  /* ---------- ИИ-чат: окно строится при первом открытии; /api/chat, без ключа — встроенный автоответчик ---------- */
  var chat, list, flo = $(".flo"), hist = [];
  var WA_BASE = "https://wa.me/" + CFG.wa + "?text=";
  var FB = [
    [/депоз|залог/i, "Депозит — " + fmt(CFG.dep) + " ₸. Возвращаем сразу после того, как вы вернёте машину."],
    [/возраст|лет|стаж/i, "Арендовать можно с 20 лет при водительском стаже от 2 лет."],
    [/документ|паспорт|удостовер|прав/i, "Нужны удостоверение личности и водительские права."],
    [/такси|яндекс|доставк.*(еды|заказ)|курьер/i, "Под режим такси и другую работу машины не выдаём."],
    [/привез|доставк|адрес.*машин|район/i, "Доставка по Астане — за доплату, сумма зависит от адреса. Забрать машину в офисе (" + CFG.addr + ") — без доплаты."],
    [/город|трасс|выезд|поездк|межгород/i, "Машины выдаём для поездок по Астане. Выезд за город — по согласованию и с доплатой, сумма зависит от направления."],
    [/график|время|работаете|час/i, "Работаем ежедневно с 10:00 до 23:00."],
    [/цен|стоим|сколько|прайс|тенге|₸/i, "От 15 000 ₸ в сутки (Hyundai Accent) до 100 000 ₸ (Lexus LX570 2019, Mercedes W222). Все цены — в разделе «Цены»: /ceny/"],
    [/адрес|где|наход/i, "Мы в Астане: " + CFG.addr + ". Перед приездом позвоните: " + CFG.phone + "."]
  ];
  var add = function (t, who) { var d = document.createElement("div"); d.className = "msg " + (who || ""); d.textContent = t; list.appendChild(d); list.scrollTop = list.scrollHeight; return d; };
  var actions = function () {
    var q = ""; for (var i = hist.length - 1; i >= 0; i--) if (hist[i].role === "user") { q = hist[i].content; break; }
    var box = document.createElement("div"); box.className = "msg-a";
    var tel = document.createElement("a"); tel.href = "tel:" + CFG.tel; tel.textContent = "Позвонить";
    var w = document.createElement("a"); w.href = WA_BASE + encodeURIComponent("Здравствуйте! Хочу арендовать авто." + (q ? "\nВопрос из чата: " + q : "")); w.target = "_blank"; w.rel = "noopener"; w.textContent = "В WhatsApp";
    [tel, w].forEach(function (a) { a.addEventListener("click", function () { conv(); }); box.appendChild(a); });
    list.appendChild(box); list.scrollTop = list.scrollHeight;
  };
  var local = function (q) { for (var i = 0; i < FB.length; i++) if (FB[i][0].test(q)) return FB[i][1]; return "Подскажу по машинам, ценам и условиям. Чтобы забронировать, напишите в WhatsApp или позвоните: " + CFG.phone + "."; };
  var ask = function (q) {
    q = (q || "").trim(); if (!q) return;
    add(q, "u"); hist.push({ role: "user", content: q });
    var w = add("печатает…", "t");
    var done = function (t) { w.remove(); add(t); hist.push({ role: "assistant", content: t }); actions(); };
    var ctrl = window.AbortController ? new AbortController() : null;
    var to = setTimeout(function () { if (ctrl) ctrl.abort(); }, 15000);
    fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ messages: hist.slice(-12), page: location.pathname }), signal: ctrl ? ctrl.signal : undefined })
      .then(function (r) { if (!r.ok) throw 0; return r.json(); })
      .then(function (d) { clearTimeout(to); done(d.text || local(q)); })
      .catch(function () { clearTimeout(to); done(local(q)); });
  };
  var closeChat = function () { chat.hidden = true; if (flo) flo.hidden = false; };
  var buildChat = function () {
    var t = $("#chat-t"); if (!t) return false;
    document.body.appendChild(t.content.cloneNode(true));
    chat = $("#chat"); list = $(".chat-l", chat);
    $("[data-chat-x]", chat).addEventListener("click", closeChat);
    $(".chat-f", chat).addEventListener("submit", function (e) { e.preventDefault(); var i = this.elements.q; ask(i.value); i.value = ""; });
    $$(".chat-q button", chat).forEach(function (b) { b.addEventListener("click", function () { ask(b.textContent); }); });
    $(".chat-w", chat).addEventListener("click", function () { conv(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !chat.hidden) closeChat(); });
    add("Здравствуйте! Я ИИ-консультант " + CFG.brand + ". Подскажу по машинам, ценам и условиям аренды.");
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
