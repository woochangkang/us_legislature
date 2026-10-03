#!/usr/bin/env python3
"""Build ndaa_korea/index.html from ndaa_korea/data/*.csv and narrative.json.

Usage: python3 tools/build_ndaa_korea.py   (standard library only; do not edit index.html by hand)
"""
import csv
import json
import re
from collections import Counter, OrderedDict
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "ndaa_korea"
DATA = ROOT / "data"

CATS = OrderedDict([
    ("K1", "주한미군 병력·태세·전작권"), ("K2", "확장억제·핵"), ("K3", "방위비분담·기지·건설"),
    ("K4", "조선·MRO·방산협력"), ("K5", "북한"), ("K6", "한미일·인태 협력"),
    ("K7", "대중국 경쟁 속 한국"), ("K8", "기타"),
])
FYS = [str(y) for y in range(2017, 2028)]


def rows(name):
    path = DATA / name
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def e(text):
    return escape(text or "")


def cats(raw):
    return [c.strip() for c in re.split(r"[;,/ ]+", raw or "") if c.strip() in CATS]


def cat_chips(raw):
    return "".join(f'<span class="chip c-{c}" title="{e(CATS[c])}">{e(CATS[c])}</span>' for c in cats(raw))


def rel_badge(rel):
    cls = {"직접": "r-direct", "직접(북한)": "r-dprk", "간접": "r-indirect"}.get(rel, "r-indirect")
    return f'<span class="rel {cls}">{e(rel)}</span>'


def basis_badge(b):
    cls = {"사실": "b-fact", "정황": "b-circ", "추정": "b-inf"}.get((b or "").strip(), "b-inf")
    return f'<span class="basis {cls}">{e(b)}</span>'


def short_loc(loc):
    """Hide local repository paths; keep the human locator."""
    loc = loc or ""
    if "::" in loc:
        loc = loc.split("::", 1)[1]
    return re.sub(r"\(?\+?data/raw/\S+\)?", "", loc).strip(" ;·")


def src_link(url, label="원문"):
    url = (url or "").split(" ")[0]
    if not url.startswith("http"):
        return ""
    return f'<a href="{e(url)}" rel="noopener">{e(label)}</a>'


ID_RE = re.compile(r"\b([PMHSAL]\d{2,3})\b")


def link_ids(text):
    return ID_RE.sub(r'<a href="#\1">\1</a>', text)


def ids_links(raw):
    return " ".join(link_ids(e(i.strip())) for i in re.split(r"[;,]", raw or "") if i.strip())


def md(text):
    """Escape, then allow **bold** and ID links."""
    return link_ids(re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", e(text)))


def tlabel(name):
    return re.sub(r"^\d+ ", "", name or "")


def thread_cls(status):
    s = status or ""
    if s.startswith("없음"):
        return "s-none"
    if "계류" in s:
        return "s-pending"
    if "거부" in s:
        return "s-veto"
    if "부활" in s or "강화" in s or s.startswith("신설(구속") or s.startswith("신설(제재"):
        return "s-strong"
    if "약화" in s or "권고" in s or "의회 의사" in s or "언급" in s or "간접" in s or s in ("관련", "연계"):
        return "s-soft"
    if s.startswith("신설"):
        return "s-new"
    if s.startswith("변경") or "압박" in s:
        return "s-change"
    if s.startswith("유지"):
        return "s-keep"
    return "s-soft"


def build():
    nar = json.loads((DATA / "narrative.json").read_text(encoding="utf-8"))
    prov = rows("provisions.csv")
    amds = rows("amendments.csv")
    comp = rows("clause_compare.csv")
    status = rows("status_timeline.csv")
    hist = rows("history.csv")
    threads = rows("threads.csv")
    floor = rows("versions_troop_floor.csv")
    actors = rows("actors.csv")
    stances = rows("stances.csv")
    positions = rows("positions.csv")
    stmts = rows("statements.csv")
    lobby = rows("fara.csv")
    sources = rows("sources.csv")

    # ---------- 1. overview ----------
    facts = "".join(f'<div><b>{e(f["value"])}</b><span>{e(f["label"])}</span></div>' for f in nar["facts"])
    cards = "".join(
        f'<article><span class="number">{e(c["label"])}</span><h3>{e(c["title"])}</h3><p>{md(c["body"])}</p>'
        + (f'<p class="small"><a href="#{e(c["go"])}">{e(c.get("go_label", "자세히"))} →</a></p>' if c.get("go") else "")
        + "</article>"
        for c in nar["cards"]
    )
    tab_overview = f"""<section class="panel" id="overview" aria-labelledby="t-overview">
<p class="kicker">01 · OVERVIEW</p><h2 id="t-overview">{e(nar['question'])}</h2>
<p class="lede">{md(nar['lede'])}</p>
<div class="mini-path">{facts}</div>
<div class="finding-grid">{cards}</div>
<div class="note"><b>읽는 법</b><p>{md(nar['reading_note'])}</p></div>
</section>"""

    # ---------- 2. provisions (FY2027) ----------
    cat_count = Counter(c for p in prov for c in cats(p["category"]))
    rel_count = Counter(p["relation"] for p in prov)

    def prov_card(p):
        return f"""<details class="evidence prov" id="{e(p['id'])}" data-rel="{e(p['relation'])}" data-cat="{e(' '.join(cats(p['category'])))}" data-bill="{e(p['bill'])}">
<summary><span class="eid">{e(p['id'])}</span><span class="summary-main"><span class="small">{e(p['bill'])} · {e(p['version'])} · <b>{e(p['section'])}</b></span><strong>{e(p['summary_ko'])}</strong><span class="chips">{cat_chips(p['category'])}</span></span>{rel_badge(p['relation'])}</summary>
<div class="evidence-body">
<p class="small" lang="en">{e(p['heading'])}</p>
{f'<blockquote lang="en">{e(p["quote"])}</blockquote>' if p.get('quote') else ''}
<div class="two"><div><h4>한국과의 연결</h4><p>{e(p['korea_link'])}</p></div><div><h4>근거 성격</h4><p>{basis_badge(p['basis'])} 원문 대조 {e(p['quote_verified'])}</p></div></div>
<p class="references">{src_link(p['source_url'], '원문 보기')} <span class="small">{e(short_loc(p['locator']))}</span></p>
</div></details>"""

    cat_opts = "".join(f'<option value="{k}">{e(v)} ({cat_count.get(k, 0)})</option>' for k, v in CATS.items())
    bills = list(OrderedDict.fromkeys(p["bill"] for p in prov))
    bill_opts = "".join(f"<option>{e(b)}</option>" for b in bills)
    rel_opts = "".join(f'<option value="{e(r)}">{e(r)} ({n})</option>' for r, n in rel_count.items())
    prov_html = "\n".join(prov_card(p) for p in prov)

    amd_rows = "".join(
        f'<tr id="{e(a["id"])}"><th scope="row">{e(a["id"])}<small>{e(a["chamber"])}</small></th>'
        f'<td>{e(a["amendment"])}<small>{e(a["date"])}</small></td><td>{e(a["sponsor"])}<small>{e(a["party_state"])}</small></td>'
        f'<td>{e(a["purpose_ko"])}' + (f'<blockquote lang="en">{e(a["korea_text_quote"])}</blockquote>' if a.get("korea_text_quote") else "")
        + f'<span class="chips">{cat_chips(a["category"])}</span></td><td>{e(a["status"])}<small>{src_link(a["source_url"])}</small></td></tr>'
        for a in amds
    )
    tab_prov = f"""<section class="panel" id="provisions" aria-labelledby="t-provisions">
<p class="kicker">02 · FY2027 PROVISIONS</p><h2 id="t-provisions">현행 NDAA의 한국 관련 조항</h2>
<p class="section-intro">{md(nar['provisions_intro'])}</p>
<div class="cat-grid">{''.join(f'<button type="button" class="cat-btn c-{k}" data-cat="{k}"><b>{cat_count.get(k, 0)}</b><span>{e(v)}</span></button>' for k, v in CATS.items())}</div>
<div class="filters" role="search"><input type="search" id="pv-q" placeholder="조항·문구·키워드 검색" aria-label="조항 검색">
<select id="pv-rel" aria-label="관련성"><option value="">직접·간접 모두</option>{rel_opts}</select>
<select id="pv-cat" aria-label="분야"><option value="">모든 분야</option>{cat_opts}</select>
<select id="pv-bill" aria-label="법안"><option value="">하원·상원 모두</option>{bill_opts}</select>
<span id="pv-n" class="small" aria-live="polite"></span></div>
<div id="pv-list">{prov_html}</div>
<h3>한국이 언급된 수정안 <span class="count">{len(amds)}</span></h3>
<p class="section-intro">{md(nar['amendments_intro'])}</p>
<div class="table-scroll"><table class="amds"><thead><tr><th>ID</th><th>수정안</th><th>제안자</th><th>내용</th><th>처리</th></tr></thead><tbody>{amd_rows}</tbody></table></div>
</section>"""

    # ---------- 3. House vs Senate ----------
    comp_threads = list(OrderedDict.fromkeys(c["thread"] for c in comp))
    comp_html = ""
    for t in comp_threads:
        trs = "".join(
            f'<tr><th scope="row">{e(c["version"])}<small>{e(c["date"])}</small></th><td>{e(c["section"])}</td>'
            f'<td>' + (f'<blockquote lang="en">{e(c["quote"])}</blockquote>' if c.get("quote") else '<span class="small">해당 조항 없음</span>')
            + f'</td><td>{md(c["diff_ko"])}<small>{src_link(c["source_url"])} {e(short_loc(c["locator"]))}</small></td></tr>'
            for c in comp if c["thread"] == t
        )
        comp_html += f'<h3>{e(t)}</h3><div class="table-scroll"><table class="compare"><thead><tr><th>판본</th><th>조항</th><th>원문</th><th>차이</th></tr></thead><tbody>{trs}</tbody></table></div>'

    def tl(items):
        out = []
        for t in items:
            ch = (t.get("chamber") or "").replace(" ", "")
            link = src_link(t.get("source_url"), "자료")
            out.append(
                f'<li class="tl-{e(ch)}"><time>{e(t["date"])}</time><div><b>{e(t["event"])}</b>'
                f'<span class="small">{" · ".join(e(x) for x in (t.get("chamber"), t.get("actor"), t.get("vote")) if x and x != "—")}</span>'
                f'<p>{md(t.get("detail"))}</p><span class="small">{basis_badge(t.get("basis"))} {link}</span></div></li>'
            )
        return '<ol class="timeline">' + "".join(out) + "</ol>"

    tab_compare = f"""<section class="panel" id="compare" aria-labelledby="t-compare">
<p class="kicker">03 · HOUSE VS SENATE</p><h2 id="t-compare">하원안과 상원안: 무엇이 다른가, 지금 어디까지 왔나</h2>
<p class="section-intro">{md(nar['compare_intro'])}</p>
{nar['compare_matrix']}
{comp_html}
<h3 id="status">FY2027 NDAA 입법 경과</h3>
<p class="section-intro">{md(nar['status_intro'])}</p>
{tl(status)}
</section>"""

    # ---------- 4. actors ----------
    groups = list(OrderedDict.fromkeys(a["group"] for a in actors))

    def acard(a):
        return (f'<article class="actor"><h3>{e(a["name"])}</h3><p class="small">{e(a.get("role_at_time"))}'
                + (f' · {e(a["party_state"])}' if a.get("party_state") and a["party_state"] != "—" else "")
                + f'</p><p>{md(a.get("what_they_did"))}</p><p class="small">근거 {ids_links(a.get("source_ids"))}</p></article>')

    actor_html = "".join(
        f'<h3 class="actor-group">{e(g)} <span class="count">{sum(1 for a in actors if a["group"] == g)}</span></h3>'
        f'<div class="finding-grid">{"".join(acard(a) for a in actors if a["group"] == g)}</div>'
        for g in groups
    )
    lobby_html = ""
    if lobby:
        lr = "".join(
            f'<tr><th scope="row">{e(l["foreign_principal"])}</th><td>{e(l["registrant"])}<small>등록번호 {e(l["registration_number"])}</small></td>'
            f'<td>{e(l["fp_registration_date"])}</td><td>{e(l["ndaa_link"])}</td></tr>'
            for l in lobby
        )
        lobby_html = f"""<h3 id="fara">외국대리인 등록(FARA): 한국 측 의뢰인 <span class="count">{len(lobby)}</span></h3>
<p class="section-intro">{md(nar['lobbying_intro'])}</p>
<div class="table-scroll"><table class="lobby"><thead><tr><th>외국 주체</th><th>등록 대리인</th><th>등록일</th><th>NDAA 관련성</th></tr></thead><tbody>{lr}</tbody></table></div>
<p class="small">출처: {src_link("https://efile.fara.gov/bulk/zip/FARA_All_ForeignPrincipals.csv.zip", "FARA 외국주체 일괄자료")} (2026-10-03 접속)</p>"""
    tab_actors = f"""<section class="panel" id="actors" aria-labelledby="t-actors">
<p class="kicker">04 · ACTORS</p><h2 id="t-actors">주요 행위자</h2>
<p class="section-intro">{md(nar['actors_intro'])}</p>
{actor_html}
{lobby_html}
</section>"""

    # ---------- 5. positions ----------
    def stance_cls(s):
        s = s or ""
        if s.startswith("반대"):
            return "st-caution"
        if s.startswith("조건부"):
            return "st-cond"
        if s.startswith(("중립", "불명")):
            return "st-indirect"
        return "st-pro"

    issues = list(OrderedDict.fromkeys(s["issue"] for s in stances))
    st_html = ""
    for iss in issues:
        trs = "".join(
            f'<tr><th scope="row">{e(s["actor"])}<small>{e(s["group"])}</small></th><td><span class="stance {stance_cls(s["stance"])}">{e(s["stance"])}</span>'
            f'<small>{basis_badge(s["basis"])}</small></td><td>{md(s["reason"])}</td><td>{md(s["conditions_concerns"])}</td><td>{ids_links(s["evidence"])}</td></tr>'
            for s in stances if s["issue"] == iss
        )
        st_html += (f'<h3>{e(iss)}</h3><div class="table-scroll"><table class="stances"><thead><tr><th>행위자</th><th>입장</th>'
                    f'<th>이유</th><th>조건·우려</th><th>근거</th></tr></thead><tbody>{trs}</tbody></table></div>')
    prow = "".join(
        f'<tr><th scope="row">{e(p["period"])}</th><td>{e(p["actor"])}<small>{e(p["body"])}</small></td>'
        f'<td>{md(p["position"])}</td><td>{ids_links(p["evidence"])}<small>{e(p["certainty"])}</small></td></tr>'
        for p in positions
    )
    pos_html = f"""<h3>단계별 입장 이동</h3>
<div class="table-scroll"><table class="positions"><thead><tr><th>시기</th><th>행위자</th><th>입장·행동</th><th>근거</th></tr></thead><tbody>{prow}</tbody></table></div>"""
    tab_pos = f"""<section class="panel" id="positions" aria-labelledby="t-positions">
<p class="kicker">05 · POSITIONS</p><h2 id="t-positions">쟁점별 입장</h2>
<p class="section-intro">{md(nar['positions_intro'])}</p>
{nar.get('positions_summary', '')}
{pos_html}
{st_html}
</section>"""

    # ---------- 6. evolution ----------
    tnames = list(OrderedDict.fromkeys(t["thread"] for t in threads))
    cell = {}
    for t in threads:
        cell.setdefault((t["thread"], t["fy"]), []).append(t)
    head = "".join(f"<th>FY{fy[2:]}</th>" for fy in FYS)
    rank = ["s-strong", "s-veto", "s-new", "s-change", "s-keep", "s-pending", "s-soft", "s-none"]

    def mcell(tn, fy):
        ts = cell.get((tn, fy))
        if not ts:
            return '<td class="s-blank"><span class="sr">자료 없음</span></td>'
        parts = []
        for t in ts:
            first = ID_RE.search(t.get("source_ref", ""))
            inner = f'<span class="st">{e(t["status"])}</span><span class="sec">{e(t["section"]) if t["section"] not in ("—", "") else ""}</span>'
            parts.append(f'<a href="#{first.group(1)}">{inner}</a>' if first else inner)
        cls = min((thread_cls(t["status"]) for t in ts), key=rank.index)
        tip = " / ".join(f'{t["status"]} · {t["section"]} · {t["key_terms"]}' for t in ts)
        return f'<td class="{cls}" title="{e(tip)}">' + '<hr class="cell-sep">'.join(parts) + "</td>"

    matrix = "".join(f'<tr><th scope="row">{e(tlabel(tn))}</th>' + "".join(mcell(tn, fy) for fy in FYS) + "</tr>" for tn in tnames)

    thread_detail = ""
    for tn in tnames:
        lis = "".join(
            f'<li class="{thread_cls(t["status"])}"><time>FY{e(t["fy"])}</time><div><b>{e(t["section"])} · {e(t["status"])}</b>'
            f'<p>{md(t["change_ko"])}</p><span class="small">{e(t["key_terms"])} {ids_links(t["source_ref"]) if ID_RE.search(t["source_ref"] or "") else e(t["source_ref"])}</span></div></li>'
            for t in threads if t["thread"] == tn
        )
        thread_detail += f'<details class="thread"><summary>{e(tlabel(tn))}</summary><ol class="lineage">{lis}</ol></details>'

    floor_rows = "".join(
        f'<tr><th scope="row">FY{e(f["fy"])}</th><td>{e(f["chamber"])}<small>{e(f["version"])}</small></td><td>{e(f["section"])}</td>'
        f'<td>{e(f["key_terms"])}<blockquote lang="en">{e(f["quote"])}</blockquote></td><td>{src_link(f["source_url"])}</td></tr>'
        for f in floor
    )

    def hist_card(h):
        return f"""<details class="evidence hist" id="{e(h['id'])}" data-fy="{e(h['fy'])}" data-rel="{e(h['relation'])}" data-cat="{e(' '.join(cats(h['category'])))}">
<summary><span class="eid">{e(h['id'])}</span><span class="summary-main"><span class="small">FY{e(h['fy'])} · {e(h['public_law'])} · <b>{e(h['section'])}</b></span><strong>{e(h['summary_ko'])}</strong><span class="chips">{cat_chips(h['category'])}</span></span>{rel_badge(h['relation'])}</summary>
<div class="evidence-body"><p class="small" lang="en">{e(h['heading'])}</p><blockquote lang="en">{e(h['quote'])}</blockquote>
<p class="references">{src_link(h['source_url'], '공법 원문')} <span class="small">{e(h['locator'])} · 제정 {e(h['enacted_date'])} · 원문 대조 {e(h['quote_verified'])}</span></p></div></details>"""

    fy_count = Counter(h["fy"] for h in hist)
    fy_opts = "".join(f'<option value="{fy}">FY{fy} ({fy_count[fy]})</option>' for fy in sorted(fy_count))
    hist_cat_opts = "".join(f'<option value="{k}">{e(v)}</option>' for k, v in CATS.items())
    tab_evo = f"""<section class="panel" id="evolution" aria-labelledby="t-evolution">
<p class="kicker">06 · EVOLUTION FY2017–FY2027</p><h2 id="t-evolution">한국 관련 내용은 어떻게 진화했나</h2>
<p class="section-intro">{md(nar['evolution_intro'])}</p>
{nar['evolution_summary']}
<h3>쟁점 × 회계연도</h3>
<div class="legend"><span class="s-strong">구속 조항 신설·강화</span><span class="s-new">신설</span><span class="s-keep">유지</span><span class="s-change">변경</span><span class="s-soft">권고·간접·언급</span><span class="s-veto">거부권</span><span class="s-pending">계류</span><span class="s-none">없음</span></div>
<div class="table-scroll"><table class="matrix"><thead><tr><th>쟁점</th>{head}</tr></thead><tbody>{matrix}</tbody></table></div>
<p class="small">칸을 누르면 해당 조문으로 이동합니다. FY2027은 미제정이라 하원·상원안 기준입니다.</p>
<h3>쟁점별 계보</h3>
{thread_detail}
<h3>주한미군 병력 하한: 하원안·상원안·성립본</h3>
<p class="section-intro">{md(nar['floor_intro'])}</p>
<div class="table-scroll"><table class="floor"><thead><tr><th>연도</th><th>판본</th><th>조항</th><th>핵심 문언</th><th>출처</th></tr></thead><tbody>{floor_rows}</tbody></table></div>
<h3>연도별 한국 관련 조문 <span class="count">{len(hist)}</span></h3>
<div class="filters" role="search"><input type="search" id="hs-q" placeholder="조항·문구 검색" aria-label="조문 검색">
<select id="hs-fy" aria-label="회계연도"><option value="">모든 연도</option>{fy_opts}</select>
<select id="hs-cat" aria-label="분야"><option value="">모든 분야</option>{hist_cat_opts}</select>
<select id="hs-rel" aria-label="관련성"><option value="">직접·간접 모두</option><option>직접</option><option>직접(북한)</option><option>간접</option></select>
<span id="hs-n" class="small" aria-live="polite"></span></div>
<div id="hs-list">{''.join(hist_card(h) for h in hist)}</div>
</section>"""

    # ---------- 7. archive ----------
    st_rows = "".join(
        f'<tr id="{e(s["id"])}"><th scope="row">{e(s["id"])}</th><td>{e(s["actor"])}<small>{e(s.get("role_at_time"))} {e(s.get("party_state"))}</small></td>'
        f'<td>{e(s["date"])}<small>{e(s["venue"])}</small></td><td>{e(s["summary_ko"])}'
        + (f'<blockquote lang="en">{e(s["quote"])}</blockquote>' if s.get("quote") else "")
        + f'</td><td>{basis_badge(s["basis"])}<small>{src_link(s.get("source_url_or_path"))} {e(short_loc(s.get("locator")))}</small></td></tr>'
        for s in stmts
    )
    src_rows = "".join(
        f'<tr><td>{e(s["title"])}<small>{e(s["kind"])}</small></td><td>{src_link(s["url"], "원 출처")}</td><td><code>{e((s.get("sha256") or "")[:16])}</code></td><td>{e(s.get("accessed"))}</td></tr>'
        for s in sources
    )
    unresolved = "".join(f"<li>{md(u)}</li>" for u in nar["unresolved"])
    tab_arch = f"""<section class="panel" id="archive" aria-labelledby="t-archive">
<p class="kicker">ARCHIVE</p><h2 id="t-archive">근거 자료실</h2>
<h3>발언·문서 근거 <span class="count">{len(stmts)}</span></h3>
<p class="section-intro">{md(nar['statements_intro'])}</p>
<div class="table-scroll"><table class="stmts"><thead><tr><th>ID</th><th>행위자</th><th>날짜·장소</th><th>내용·인용</th><th>성격·출처</th></tr></thead><tbody>{st_rows}</tbody></table></div>
<h3>원문 자료 <span class="count">{len(sources)}</span></h3>
<div class="table-scroll"><table><thead><tr><th>자료</th><th>출처</th><th>SHA-256 앞 16자</th><th>접속</th></tr></thead><tbody>{src_rows}</tbody></table></div>
<h3>미확인·추가 확인 필요</h3><ul class="unresolved">{unresolved}</ul>
<div class="method"><div><h3>분석 방식</h3>{nar['method']}</div><div><h3>범위와 한계</h3>{nar['limits']}</div></div>
</section>"""

    tabs = [("overview", "1 개요"), ("provisions", "2 현행 조항"), ("compare", "3 하원·상원"),
            ("actors", "4 행위자"), ("positions", "5 입장"), ("evolution", "6 진화"), ("archive", "근거 자료실")]
    nav = "".join(f'<a href="#{i}" data-tab="{i}">{e(label)}</a>' for i, label in tabs)
    html = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NDAA 속의 한국</title>
<meta name="description" content="{e(nar['description'])}">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23161a2e'/%3E%3Ccircle cx='16' cy='16' r='8' fill='%23c8423b'/%3E%3Cpath d='M8 16a8 8 0 0 0 16 0a4 4 0 0 1-8 0a4 4 0 0 0-8 0z' fill='%232f5fa8'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://cdn.jsdelivr.net"><link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="ndaa_korea.css">
<link rel="canonical" href="https://woochangkang.github.io/us_legislature/ndaa_korea/">
</head><body>
<a class="skip" href="#main">본문 바로가기</a>
<header><div class="mast"><a class="brand" href="../"><span class="brand-mark" aria-hidden="true"></span>입법 증거 아틀라스</a><span class="period">{e(nar['period'])}</span></div>
<nav aria-label="사례 탭">{nav}</nav></header>
<main id="main">
<div class="title"><p class="kicker">NDAA × KOREA · FY2017–FY2027</p><h1>{e(nar['title'])}</h1><p>{e(nar['subtitle'])}</p></div>
{tab_overview}{tab_prov}{tab_compare}{tab_actors}{tab_pos}{tab_evo}{tab_arch}
</main>
<footer><b>NDAA 속의 한국</b><span>공개 원문 기반 · 사실 / 정황 / 추정 구분 · 갱신 {e(nar['updated'])}</span><a href="../aukus/">AUKUS 사례</a><a href="../ira/">IRA 사례</a></footer>
<script src="ndaa_korea.js"></script>
</body></html>
"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote {ROOT / 'index.html'}: provisions {len(prov)}, amendments {len(amds)}, compare {len(comp)}, "
          f"status {len(status)}, history {len(hist)}, threads {len(threads)}, actors {len(actors)}, "
          f"stances {len(stances)}, statements {len(stmts)}, lobbying {len(lobby)}, sources {len(sources)}")


if __name__ == "__main__":
    build()
