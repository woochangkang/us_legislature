// Hash-routed tabs, deep links to any row/card, list filters, theme toggle.
(function () {
  document.documentElement.classList.add("js");
  var panels = Array.prototype.slice.call(document.querySelectorAll(".panel"));
  var tabs = Array.prototype.slice.call(document.querySelectorAll("nav a[data-tab]"));
  var nav = document.querySelector("nav");
  nav.setAttribute("role", "tablist");
  tabs.forEach(function (t) {
    t.setAttribute("role", "tab");
    t.setAttribute("aria-controls", t.dataset.tab);
  });

  function show(id) {
    if (!panels.some(function (p) { return p.id === id; })) id = panels[0].id;
    panels.forEach(function (p) { p.hidden = p.id !== id; });
    tabs.forEach(function (t) {
      var on = t.dataset.tab === id;
      t.setAttribute("aria-selected", on);
      t.tabIndex = on ? 0 : -1;
      if (on) t.scrollIntoView({ block: "nearest", inline: "nearest" });
    });
  }

  function route() {
    var h = decodeURIComponent(location.hash.slice(1));
    var target = h && document.getElementById(h);
    var panel = target && !target.classList.contains("panel") && target.closest(".panel");
    if (panel) {
      show(panel.id);
      target.hidden = false;
      for (var d = target.tagName === "DETAILS" ? target : target.closest("details"); d; d = d.parentElement && d.parentElement.closest("details")) d.open = true;
      target.classList.remove("flash");
      void target.offsetWidth;
      target.classList.add("flash");
      target.scrollIntoView({ block: target.tagName === "DETAILS" ? "start" : "center" });
      return;
    }
    show(h);
    if (h) window.scrollTo(0, 0);
  }

  nav.addEventListener("keydown", function (ev) {
    var i = tabs.indexOf(document.activeElement);
    if (i < 0) return;
    var j = ev.key === "ArrowRight" ? i + 1 : ev.key === "ArrowLeft" ? i - 1 : null;
    if (j === null) return;
    ev.preventDefault();
    var next = tabs[(j + tabs.length) % tabs.length];
    next.focus();
    location.hash = next.dataset.tab;
  });
  window.addEventListener("hashchange", route);

  // generic list filter: text + data-attribute selects
  function makeFilter(prefix, listId, attrs) {
    var q = document.getElementById(prefix + "-q");
    if (!q) return null;
    var sels = attrs.map(function (a) { return [a, document.getElementById(prefix + "-" + a)]; });
    var count = document.getElementById(prefix + "-n");
    var items = Array.prototype.slice.call(document.querySelectorAll("#" + listId + " > details"));
    function run() {
      var text = (q.value || "").trim().toLowerCase();
      var n = 0;
      items.forEach(function (it) {
        var ok = sels.every(function (s) {
          var v = s[1].value;
          if (!v) return true;
          var have = (it.dataset[s[0]] || "").split(" ");
          return s[0] === "cat" ? have.indexOf(v) >= 0 : it.dataset[s[0]] === v;
        }) && (!text || it.textContent.toLowerCase().indexOf(text) >= 0);
        it.hidden = !ok;
        if (ok) n++;
      });
      count.textContent = n + " / " + items.length + "건";
    }
    [q].concat(sels.map(function (s) { return s[1]; })).forEach(function (el) { el.addEventListener("input", run); });
    run();
    return run;
  }
  var runPv = makeFilter("pv", "pv-list", ["rel", "cat", "bill"]);
  makeFilter("hs", "hs-list", ["fy", "cat", "rel"]);

  // category buttons drive the provision filter
  var catSel = document.getElementById("pv-cat");
  var catBtns = Array.prototype.slice.call(document.querySelectorAll(".cat-btn"));
  function syncBtns() {
    catBtns.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.cat === catSel.value); });
  }
  catBtns.forEach(function (b) {
    b.addEventListener("click", function () {
      catSel.value = catSel.value === b.dataset.cat ? "" : b.dataset.cat;
      if (runPv) runPv();
      syncBtns();
    });
  });
  if (catSel) { catSel.addEventListener("input", syncBtns); syncBtns(); }

  route();

  // site-wide keyword search (page 1): every element with data-sr and an id is searchable
  var sq = document.getElementById("site-q");
  if (sq) {
    var sOut = document.getElementById("site-results");
    var sN = document.getElementById("site-n");
    function spaced(node) {  // text of all descendants joined with spaces (table cells otherwise run together)
      var parts = [], w = document.createTreeWalker(node, NodeFilter.SHOW_TEXT), t;
      while ((t = w.nextNode())) if (!t.parentNode.closest(".chips")) parts.push(t.nodeValue);  // category chips are labels, not content
      return parts.join(" ").replace(/\s+/g, " ").trim();
    }
    var docs = Array.prototype.slice.call(document.querySelectorAll("[data-sr][id]")).map(function (el) {
      var text = spaced(el);
      return { id: el.id, section: el.dataset.sr, title: el.dataset.title || el.id, text: text, low: text.toLowerCase() };
    });
    function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
    function mark(s, terms) {
      var out = esc(s);
      terms.forEach(function (t) {
        out = out.replace(new RegExp("(" + esc(t).replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi"), "<mark>$1</mark>");
      });
      return out;
    }
    function search() {
      var q = sq.value.trim().toLowerCase();
      sOut.innerHTML = "";
      if (!q) { sN.textContent = ""; return; }
      var terms = q.split(/\s+/);
      var hits = docs.filter(function (d) { return terms.every(function (t) { return d.low.indexOf(t) >= 0; }); });
      sN.textContent = hits.length + "건" + (hits.length > 60 ? " (앞 60건 표시)" : "") + " / 전체 " + docs.length + "개 항목";
      hits.slice(0, 60).forEach(function (d) {
        var i = d.low.indexOf(terms[0]);
        var start = Math.max(0, i - 50);
        var snip = (start > 0 ? "…" : "") + d.text.slice(start, i + 110) + (i + 110 < d.text.length ? "…" : "");
        var li = document.createElement("li");
        li.innerHTML = '<a href="#' + d.id + '"><span class="sr-sec">' + esc(d.section) + "</span> <b>" + mark(d.title.slice(0, 100), terms) +
          '</b><span class="sr-snip">' + mark(snip, terms) + "</span></a>";
        sOut.appendChild(li);
      });
    }
    sq.addEventListener("input", search);
  }

  // theme toggle (per-viewer preference only)
  var btn = document.createElement("button");
  btn.className = "theme-toggle";
  btn.type = "button";
  var root = document.documentElement;
  function stored() { try { return localStorage.getItem("ndaa-korea-theme"); } catch (e) { return null; } }
  function apply(v) {
    if (v) root.dataset.theme = v; else delete root.dataset.theme;
    var dark = v ? v === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    btn.textContent = dark ? "밝게" : "어둡게";
    btn.setAttribute("aria-label", dark ? "밝은 화면으로" : "어두운 화면으로");
  }
  btn.addEventListener("click", function () {
    var dark = root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    var v = dark ? "light" : "dark";
    try { localStorage.setItem("ndaa-korea-theme", v); } catch (e) {}
    apply(v);
  });
  apply(stored());
  document.querySelector(".mast").appendChild(btn);

  window.addEventListener("beforeprint", function () {
    document.querySelectorAll("details").forEach(function (d) { d.open = true; });
  });
})();
