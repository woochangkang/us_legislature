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
    var items = Array.prototype.slice.call(document.querySelectorAll("#" + listId + " > details, #" + listId + " > tbody > tr"));
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
  makeFilter("fa", "fa-list", ["rel", "topic"]);

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

  // member x vote matrix (votes tab): rendered from data/member_votes.json
  var vmTable = document.getElementById("vm-table");
  if (vmTable) {
    var meta = JSON.parse(document.getElementById("vote-meta").textContent);
    var CAST = { Y: "찬성", N: "반대", A: "불참", P: "출석만", "-": "재임 아님·해당 원 아님" };
    var vq = document.getElementById("vm-q"), vch = document.getElementById("vm-ch"), vp = document.getElementById("vm-p"),
      vrel = document.getElementById("vm-rel"), vn = document.getElementById("vm-n"), members = null;
    function h(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
    function drawVotes() {
      if (!members) return;
      var cols = meta.map(function (m, i) { return i; }).filter(function (i) {
        return (!vrel.value || meta[i].rel === vrel.value) && (!vch.value || meta[i].ch === vch.value);
      });
      var q = vq.value.trim().toLowerCase();
      var head = '<tr><th>의원</th><th>정당·주</th>' + cols.map(function (i) {
        var m = meta[i];
        return '<th class="vcol" title="' + h(m.d + " · " + m.date + " · " + m.t) + '"><a href="#' + m.id + '">' + m.id + "</a><small>" + h(m.ch) + " " + m.date.slice(0, 4) + "</small></th>";
      }).join("") + "</tr>";
      var rowsHtml = [], n = 0;
      members.forEach(function (mb) {
        if (vp.value && mb.p !== vp.value) return;
        if (vch.value && mb.ch.indexOf(vch.value) < 0) return;
        if (q && (mb.n + " " + mb.s + " " + mb.b).toLowerCase().indexOf(q) < 0) return;
        if (!cols.some(function (i) { return mb.v[i] !== "-"; })) return;
        n++;
        rowsHtml.push('<tr><th scope="row">' + h(mb.n) + "</th><td>" + h(mb.p + "-" + mb.s + (mb.d && mb.d !== "0" ? "-" + mb.d : "")) + "</td>" +
          cols.map(function (i) { var c = mb.v[i]; return '<td class="v-' + (c === "-" ? "x" : c) + '" title="' + h(meta[i].id + " " + CAST[c]) + '">' + (c === "-" ? "" : CAST[c].slice(0, 1)) + "</td>"; }).join("") + "</tr>");
      });
      vmTable.tHead.innerHTML = head;
      vmTable.tBodies[0].innerHTML = rowsHtml.join("") || '<tr><td colspan="3" class="small">해당하는 의원이 없습니다.</td></tr>';
      vn.textContent = "의원 " + n + "명 · 표결 " + cols.length + "건";
    }
    [vq, vch, vp, vrel].forEach(function (el) { el.addEventListener("input", drawVotes); });
    fetch("data/member_votes.json").then(function (r) { return r.json(); }).then(function (d) {
      members = d.members;
      drawVotes();
    }).catch(function () { vmTable.tBodies[0].innerHTML = '<tr><td class="small">표결 자료를 불러오지 못했습니다. data/member_votes.json을 직접 내려받아 보세요.</td></tr>'; });
    Array.prototype.slice.call(document.querySelectorAll("button[data-mv]")).forEach(function (b) {
      b.addEventListener("click", function () {
        vq.value = b.dataset.mv; vch.value = ""; vp.value = ""; vrel.value = "";
        drawVotes();
        document.getElementById("vote-matrix").scrollIntoView({ block: "start" });
      });
    });
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
