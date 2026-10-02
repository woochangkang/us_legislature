// Hash-routed tabs, evidence deep links, evidence filter, theme toggle.
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
    if (target && target.classList.contains("evidence")) {
      show("archive");
      target.open = true;
      target.classList.remove("flash");
      void target.offsetWidth;
      target.classList.add("flash");
      target.scrollIntoView({ block: "start" });
      return;
    }
    // any other element inside a panel (e.g. H/L source rows): open its tab and enclosing <details>
    var panel = target && !target.classList.contains("panel") && target.closest(".panel");
    if (panel) {
      show(panel.id);
      for (var d = target.closest("details"); d; d = d.parentElement && d.parentElement.closest("details")) d.open = true;
      target.scrollIntoView({ block: "center" });
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
  route();

  // evidence filter
  var q = document.getElementById("ev-q");
  var theme = document.getElementById("ev-theme");
  var level = document.getElementById("ev-level");
  var count = document.getElementById("ev-n");
  var items = Array.prototype.slice.call(document.querySelectorAll("#ev-list .evidence"));
  function filter() {
    var text = (q.value || "").trim().toLowerCase();
    var n = 0;
    items.forEach(function (it) {
      var ok = (!theme.value || it.dataset.theme === theme.value) &&
        (!level.value || it.dataset.level === level.value) &&
        (!text || it.textContent.toLowerCase().indexOf(text) >= 0);
      it.hidden = !ok;
      if (ok) n++;
    });
    count.textContent = n + " / " + items.length + "건";
  }
  if (q) {
    [q, theme, level].forEach(function (el) { el.addEventListener("input", filter); });
    filter();
  }

  // theme toggle (per-viewer preference only)
  var btn = document.createElement("button");
  btn.className = "theme-toggle";
  btn.type = "button";
  var root = document.documentElement;
  function stored() { try { return localStorage.getItem("aukus-theme"); } catch (e) { return null; } }
  function apply(v) {
    if (v) root.dataset.theme = v; else delete root.dataset.theme;
    var dark = v ? v === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    btn.textContent = dark ? "밝게" : "어둡게";
    btn.setAttribute("aria-label", dark ? "밝은 화면으로" : "어두운 화면으로");
  }
  btn.addEventListener("click", function () {
    var dark = root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    var v = dark ? "light" : "dark";
    try { localStorage.setItem("aukus-theme", v); } catch (e) {}
    apply(v);
  });
  apply(stored());
  document.querySelector(".mast").appendChild(btn);

  // print: open all evidence
  window.addEventListener("beforeprint", function () {
    document.querySelectorAll(".evidence").forEach(function (d) { d.open = true; });
  });
})();
