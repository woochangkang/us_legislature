#!/usr/bin/env python3
"""Build ndaa_korea/index.html from ndaa_korea/data/*.csv and narrative.json.

Usage: python3 tools/build_ndaa_korea.py   (standard library only; do not edit index.html by hand)
"""
import csv
import json
import re
from collections import Counter, OrderedDict, defaultdict
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
    b = (b or "").strip()
    if not b:
        return ""
    cls = {"사실": "b-fact", "정황": "b-circ", "추정": "b-inf"}.get(b, "b-mix" if "사실" in b else "b-inf")
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
LOBBYIST_RE = re.compile(r"\s*([^;\[\]]+?)\s*(?:\[([^\]]*)\])?\s*(?:;|$)")  # "NAME [covered; position]; NAME2"


def smart_title(name):
    """Title-case an all-caps company name but keep short tokens (USA, HD, LIG, LLC) upper-case."""
    return " ".join(w if len(w.strip(".,()")) <= 3 else w.title() for w in (name or "").split())


def url_links(raw):
    """URLs in a ';'-separated field -> short domain links; local paths are dropped."""
    out = []
    for tok in re.split(r"\s*;\s*", raw or ""):
        tok = tok.strip().split(" ")[0]
        if tok.startswith("http"):
            dom = re.sub(r"^www\.", "", tok.split("/")[2])
            out.append(f'<a href="{e(tok)}" rel="noopener">{e(dom)}</a>')
    return " ".join(out)


def evid_links(raw):
    ids = [t.strip() for t in re.split(r"\s*;\s*", raw or "") if ID_RE.fullmatch(t.strip())]
    return " ".join(f'<a href="#{i}">{i}</a>' for i in ids) + (" " + url_links(raw) if url_links(raw) else "")


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
    sources = rows("sources.csv")
    votes = rows("votes.csv")
    msum = rows("member_summary.csv")

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
<div class="site-search" role="search">
<label for="site-q"><b>사이트 전체 검색</b> <span class="small">조항·인물·쟁점·문구 — 여러 단어는 모두 포함하는 항목만</span></label>
<input type="search" id="site-q" placeholder="예: 28,500, 전작권, Golden, shipyard, Hanwha, §1235" autocomplete="off">
<p id="site-n" class="small" aria-live="polite"></p>
<ol id="site-results" class="site-results"></ol>
</div>
<div class="finding-grid">{cards}</div>
<div class="note"><b>읽는 법</b><p>{md(nar['reading_note'])}</p></div>
</section>"""

    # ---------- 2. provisions (FY2027) ----------
    cat_count = Counter(c for p in prov for c in cats(p["category"]))
    rel_count = Counter(p["relation"] for p in prov)

    def prov_card(p):
        return f"""<details class="evidence prov" id="{e(p['id'])}" data-rel="{e(p['relation'])}" data-cat="{e(' '.join(cats(p['category'])))}" data-bill="{e(p['bill'])}" data-sr="FY2027 조항" data-title="{e(p['bill'])} {e(p['section'])} — {e(p['summary_ko'])}">
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
        f'<tr id="{e(a["id"])}" data-sr="수정안" data-title="{e(a["amendment"])} · {e(a["sponsor"])}"><th scope="row">{e(a["id"])}<small>{e(a["chamber"])}</small></th>'
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
            f'<tr id="cp-{n}" data-sr="하원·상원 비교" data-title="{e(c["thread"])} · {e(c["version"])} {e(c["section"])}"><th scope="row">{e(c["version"])}<small>{e(c["date"])}</small></th><td>{e(c["section"])}</td>'
            f'<td>' + (f'<blockquote lang="en">{e(c["quote"])}</blockquote>' if c.get("quote") else '<span class="small">해당 조항 없음</span>')
            + f'</td><td>{md(c["diff_ko"])}<small>{src_link(c["source_url"])} {e(short_loc(c["locator"]))}</small></td></tr>'
            for n, c in enumerate(comp, 1) if c["thread"] == t
        )
        comp_html += f'<h3>{e(t)}</h3><div class="table-scroll"><table class="compare"><thead><tr><th>판본</th><th>조항</th><th>원문</th><th>차이</th></tr></thead><tbody>{trs}</tbody></table></div>'

    def tl(items):
        out = []
        for n, t in enumerate(items, 1):
            ch = (t.get("chamber") or "").replace(" ", "")
            link = src_link(t.get("source_url"), "자료")
            out.append(
                f'<li id="tl-{n}" data-sr="입법 경과" data-title="{e(t["date"])} {e(t["event"])}" class="tl-{e(ch)}"><time>{e(t["date"])}</time><div><b>{e(t["event"])}</b>'
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
    profiles = rows("actor_profiles.csv")
    motives = {(m["actor_name"], m["issue"]): m for m in rows("motivations.csv")}
    org_notes = {o["actor_name"]: o for o in rows("org_notes.csv")}
    msum_by_bio = {m["bioguide_id"]: m for m in msum}

    def profs_for(name):
        return [pf for pf in profiles if pf["actor_name"] == name or pf["person"] == name or pf["actor_name"].startswith(name + " (")]

    def seat(pf):
        if not pf.get("party"):
            return ""
        loc = pf["state"] + (f'-{pf["district"]}' if pf.get("district") else "")
        return f'<span class="party p-{e(pf["party"][:1])}">{e(pf["party"])}-{e(loc)}</span>'

    def prof_block(pf, full=True):
        who = f'<b>{e(pf["person"])}</b> ' if pf.get("person") else ""
        line = f'{who}{seat(pf)} {e(pf.get("terms_ko"))}'.strip()
        out = f'<div class="prof">{line}' if line else '<div class="prof">'
        out += f'<small><span class="lbl">소속</span> {e(pf.get("affiliation_ko"))}</small><small><span class="lbl">지위</span> {e(pf.get("position_ko"))}</small>'
        if full and pf.get("committees_ko"):
            out += f'<small><span class="lbl">위원회</span> {e(pf["committees_ko"])}</small>'
        if full and pf.get("caucus_ko"):
            out += f'<small><span class="lbl">코커스</span> {e(pf["caucus_ko"])}</small>'
        extra = []
        if pf.get("bioguide_id") in msum_by_bio:
            extra.append(f'<a href="#mv-{e(pf["bioguide_id"])}">표결 기록</a>')
        if full:
            extra.append(url_links(pf.get("source_urls")))
            extra.append(basis_badge(pf.get("basis", "").split("(")[0].strip()))
        out += f'<small>{" ".join(x for x in extra if x)}</small></div>'
        return out

    def acard(a):
        pfs = profs_for(a["name"])
        org = org_notes.get(a["name"])
        return (f'<article class="actor" id="ac-{actors.index(a) + 1}" data-sr="행위자 · {e(a["group"])}" data-title="{e(a["name"])}"><h3>{e(a["name"])}</h3>'
                + "".join(prof_block(pf) for pf in pfs)
                + (f'<p class="small">{e(org["org_note_ko"])}</p>' if org else "")
                + f'<p>{md(a.get("what_they_did"))}</p><p class="small">근거 {ids_links(a.get("source_ids"))}</p></article>')

    actor_html = "".join(
        f'<h3 class="actor-group">{e(g)} <span class="count">{sum(1 for a in actors if a["group"] == g)}</span></h3>'
        f'<div class="finding-grid">{"".join(acard(a) for a in actors if a["group"] == g)}</div>'
        for g in groups
    )
    tab_actors = f"""<section class="panel" id="actors" aria-labelledby="t-actors">
<p class="kicker">04 · ACTORS</p><h2 id="t-actors">주요 행위자</h2>
<p class="section-intro">{md(nar['actors_intro'])}</p>
{actor_html}
<p class="note small">한국 정부·기업의 로비 기록(LDA·FARA)은 <a href="#lobby">7 로비</a> 탭에 따로 정리했습니다.</p>
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

    sgroups = rows("stance_groups.csv")
    st_index = {(x["actor"], x["issue"]): (n, x) for n, x in enumerate(stances, 1)}
    issues = list(OrderedDict.fromkeys(g["issue"] for g in sgroups))

    def member_row(name, issue):
        n, s_ = st_index[(name, issue)]
        mv = motives.get((name, issue), {})
        pfs = profs_for(name)
        who = "".join(prof_block(pf, full=False) for pf in pfs)
        factors = "".join(f'<span class="chip">{e(f)}</span>' for f in (mv.get("factors") or "").split(";") if f)
        return (f'<tr id="st-{n}" data-sr="쟁점별 입장" data-title="{e(name)} · {e(issue)} · {e(s_["stance"])}">'
                f'<th scope="row">{e(name)}<small>{e(s_["group"])}</small>{who}</th>'
                f'<td><span class="stance {stance_cls(s_["stance"])}">{e(s_["stance"])}</span><small>판단 근거 {basis_badge(s_["basis"])}</small></td>'
                f'<td>{md(s_["reason"])}' + (f'<small>조건·우려: {md(s_["conditions_concerns"])}</small>' if s_.get("conditions_concerns") not in (None, "", "—") else "")
                + f'<small>근거 {ids_links(s_["evidence"])}</small></td>'
                f'<td>{md(mv.get("why_ko"))}<span class="chips">{factors}</span><small>이유 판단 {basis_badge(mv.get("basis"))} {evid_links(mv.get("evidence"))}</small></td></tr>')

    st_html = ""
    for iss in issues:
        gs = [g for g in sgroups if g["issue"] == iss]
        cards = ""
        for g in gs:
            names = [m for m in g["members"].split(";") if m]
            chips = "".join(f'<span class="stance {stance_cls(st_index[(m, iss)][1]["stance"])}">{e(m)}</span>' for m in names)
            trs = "".join(member_row(m, iss) for m in names)
            cards += (f'<article class="sgroup" id="sg-{e(g["group_id"])}" data-sr="입장 그룹" data-title="{e(iss)} · {e(g["label"])}">'
                      f'<header><span class="eid">{e(g["group_id"])}</span><h4>{e(g["label"])}</h4><span class="count">{len(names)}</span></header>'
                      f'<div class="sg-members">{chips}</div>'
                      f'<div class="two"><div><h5>입장</h5><p>{md(g["position_ko"])}</p></div><div><h5>왜 이런 입장인가 {basis_badge(g["basis"])}</h5><p>{md(g["why_ko"])}</p></div></div>'
                      f'<details class="sg-detail"><summary>행위자별 근거와 이유 보기</summary><div class="table-scroll"><table class="stances"><thead><tr><th>행위자</th><th>입장</th><th>입장 판단의 근거</th><th>왜 이런 입장인가</th></tr></thead><tbody>{trs}</tbody></table></div></details></article>')
        st_html += f'<h3 class="issue-head">{e(iss)} <span class="count">{len(gs)}개 그룹 · {sum(len(g["members"].split(";")) for g in gs)}행</span></h3>{cards}'
    prow = "".join(
        f'<tr id="ph-{n}" data-sr="단계별 입장" data-title="{e(p["period"])} · {e(p["actor"])}"><th scope="row">{e(p["period"])}</th><td>{e(p["actor"])}<small>{e(p["body"])}</small></td>'
        f'<td>{md(p["position"])}</td><td>{ids_links(p["evidence"])}<small>{e(p["certainty"])}</small></td></tr>'
        for n, p in enumerate(positions, 1)
    )
    pos_html = f"""<h3>단계별 입장 이동</h3>
<div class="table-scroll"><table class="positions"><thead><tr><th>시기</th><th>행위자</th><th>입장·행동</th><th>근거</th></tr></thead><tbody>{prow}</tbody></table></div>"""
    tab_pos = f"""<section class="panel" id="positions" aria-labelledby="t-positions">
<p class="kicker">05 · POSITIONS</p><h2 id="t-positions">쟁점별 입장: 비슷한 입장끼리 묶어 보기</h2>
<p class="section-intro">{md(nar['positions_intro'])}</p>
{nar.get('positions_summary', '')}
<div class="legend"><span class="basis b-fact">사실</span> 원문으로 확인 <span class="basis b-circ">정황</span> 언론·2차 자료로만 확인 <span class="basis b-mix">사실·추정 혼합</span> <span class="basis b-inf">추정</span> 연구자 추론([추정] 표시 문장)</div>
{st_html}
{pos_html}
</section>"""

    # ---------- 5b. votes ----------
    REL_ORDER = ["직접", "직접(북한)", "거부권", "포괄"]
    REL_LABEL = {"직접": "한국 직접 관련 표결", "직접(북한)": "북한 관련 표결", "거부권": "FY2021 NDAA 거부권 재의결 (거부 사유에 한국 철군 제한 명시)",
                 "포괄": "NDAA 본회의 최종 표결 (포괄 법안 — 한국 조항 입장으로 해석 불가)"}

    def vrow(v):
        nv = f' · 불참 {e(v["not_voting"])}' if v.get("not_voting") else ""
        return (f'<tr id="{e(v["vote_id"])}" data-sr="표결" data-title="{e(v["bill"])} · {e(v["description_ko"])}"><th scope="row">{e(v["vote_id"])}<small>{e(v["chamber"])} roll {e(v["rollnumber"])}<br>{e(v["date"])}</small></th>'
                f'<td><b>{e(v["bill"])}</b><small>{e(v["description_ko"])}</small></td>'
                f'<td class="tally"><b>{e(v["yea"])}–{e(v["nay"])}</b><small>{e(v["result"])}{nv}</small></td>'
                f'<td>{md(v["korea_content"])}<small>{e(v["interpretation_note"])}</small></td>'
                f'<td>{src_link(v["source_url"])}<small>{e(v["tally_verified"][:1] and "집계 대조 " + v["tally_verified"][:1])}</small></td></tr>')

    vote_tables = ""
    for rel in REL_ORDER:
        vs = [v for v in votes if v["korea_relevance"] == rel]
        if vs:
            vote_tables += (f'<h4 class="vote-group">{e(REL_LABEL[rel])} <span class="count">{len(vs)}</span></h4><div class="table-scroll"><table class="votes">'
                            f'<thead><tr><th>ID</th><th>법안·안건</th><th>결과</th><th>한국 관련 내용 · 해석 주의</th><th>출처</th></tr></thead><tbody>{"".join(vrow(v) for v in vs)}</tbody></table></div>')

    def pat_cls(pt):
        return "st-pro" if pt.startswith("찬성") or pt.startswith("전부 찬성") else ("st-caution" if "반대" in pt else "st-cond")

    person_by_bio = {pf["bioguide_id"]: pf["person"] for pf in rows("actor_profiles.csv") if pf.get("bioguide_id")}
    msum_cards = "".join(
        f'<article class="actor" id="mv-{e(m["bioguide_id"])}" data-sr="의원 표결 요약" data-title="{e(person_by_bio.get(m["bioguide_id"], m["name"]))}"><h3>{e(person_by_bio.get(m["bioguide_id"], m["name"]))}</h3>'
        + (f'<p class="small">행위자 항목: {e(m["actor_name"])}</p>' if person_by_bio.get(m["bioguide_id"]) != m["actor_name"] else "")
        + f'<p class="small">{e(m["state_district"])} · 기록 {e(m["n_votes_cast"])}건 <span class="stance {pat_cls(m["pattern"])}">{e(m["pattern"])}</span></p>'
        f'<p>{link_ids(e(m["summary_ko"]))}</p><p class="small"><button type="button" class="linkish" data-mv="{e(m["bioguide_id"])}">전체 표에서 보기</button></p></article>'
        for m in msum
    )
    vote_meta = json.dumps([{"id": v["vote_id"], "ch": v["chamber"], "rel": v["korea_relevance"], "date": v["date"], "bill": v["bill"],
                             "d": v["description_ko"], "t": f'{v["yea"]}-{v["nay"]}'} for v in votes], ensure_ascii=False)
    vote_meta_safe = vote_meta.replace("</", "<\\/")
    rel_opts = "".join(f'<option value="{e(r)}">{e(REL_LABEL[r].split(" (")[0])}</option>' for r in REL_ORDER)
    tab_votes = f"""<section class="panel" id="votes" aria-labelledby="t-votes">
<p class="kicker">06 · ROLL-CALL VOTES</p><h2 id="t-votes">표결 기록: 의원들은 한국 관련 법안에 어떻게 투표했나</h2>
<p class="section-intro">{md(nar['votes_intro'])}</p>
<div class="note"><b>먼저 읽을 점</b><p>{md(nar['votes_caution'])}</p></div>
<h3>대상 표결 <span class="count">{len(votes)}</span></h3>
{vote_tables}
<h3 id="member-votes">행위자 의원의 표결 요약 <span class="count">{len(msum)}</span></h3>
<p class="section-intro">{md(nar['member_summary_intro'])}</p>
<div class="finding-grid">{msum_cards}</div>
<h3 id="vote-matrix">전체 의원 × 표결</h3>
<p class="section-intro">{md(nar['matrix_intro'])}</p>
<div class="filters" role="search"><input type="search" id="vm-q" placeholder="의원 이름·주(예: Golden, CA)" aria-label="의원 검색">
<select id="vm-ch" aria-label="원"><option value="">양원</option><option>하원</option><option>상원</option></select>
<select id="vm-p" aria-label="정당"><option value="">모든 정당</option><option value="R">공화(R)</option><option value="D">민주(D)</option><option value="I">무소속(I)</option></select>
<select id="vm-rel" aria-label="표결 유형"><option value="">모든 표결</option>{rel_opts}</select>
<span id="vm-n" class="small" aria-live="polite"></span></div>
<div class="legend"><span class="v-Y">찬성</span><span class="v-N">반대</span><span class="v-A">불참</span><span class="v-P">출석만</span><span class="v-x">재임 아님·해당 원 아님</span></div>
<div class="table-scroll vm-wrap"><table class="vmatrix" id="vm-table"><thead></thead><tbody><tr><td class="small">표결 자료를 불러오는 중…</td></tr></tbody></table></div>
<script type="application/json" id="vote-meta">{vote_meta_safe}</script>
</section>"""

    # ---------- 5c. lobbying ----------
    PERIOD = {"first_quarter": "1분기", "second_quarter": "2분기", "third_quarter": "3분기", "fourth_quarter": "4분기",
              "mid_year": "상반기", "year_end": "하반기"}
    porder = list(PERIOD)
    lda_sum = json.loads((DATA / "lda_summary_2017_2026.json").read_text(encoding="utf-8")) if (DATA / "lda_summary_2017_2026.json").exists() else {}
    ygroups = [g for g in rows("lda_yearly_groups.csv") if not g["group"].startswith("제외")]
    yclients = [c for c in rows("lda_yearly_clients.csv") if not c["group"].startswith("제외")]
    dfy = rows("lda_defense_firms_yearly.csv")
    drep = rows("lda_defense_reports.csv")
    contrib = rows("lda_contrib_actor_members.csv")
    lobdet = {r["name"].upper(): r for r in rows("lda_lobbyists_detail.csv")}
    LYEARS = sorted({g["year"] for g in ygroups})

    def ylabel(y):
        return f"{y}<small>1–2분기</small>" if y == "2026" else y

    def musd(v):
        v = float(v or 0)
        return f"${v / 1e6:.2f}M" if v >= 1e5 else (f"${v / 1e3:.0f}K" if v else "$0")

    def heat(v, mx):
        a = min(0.85, (float(v or 0) / mx) ** 0.6 * 0.85) if mx else 0
        return f' style="background:rgba(47,95,168,{a:.2f});color:{"#fff" if a > 0.45 else "inherit"}"'

    gtot = defaultdict(float)
    for g in ygroups:
        gtot[g["group"]] += float(g["reported_amount_usd"])
    gnames = sorted(gtot, key=lambda k: -gtot[k])
    gcell = {(g["group"], g["year"]): g for g in ygroups}
    gmax = max((float(g["reported_amount_usd"]) for g in ygroups), default=1)
    g_rows = ""
    for gn in gnames:
        tds = ""
        for y in LYEARS:
            g = gcell.get((gn, y))
            tds += (f'<td class="num"{heat(g["reported_amount_usd"], gmax)} title="고객 {g["n_clients"]} · 신고자 {g["n_registrants"]} · 보고서 {g["reports"]}">{musd(g["reported_amount_usd"])}</td>'
                    if g else '<td class="num muted">—</td>')
        g_rows += f'<tr><th scope="row">{e(gn)}</th>{tds}<td class="num"><b>{musd(gtot[gn])}</b></td></tr>'
    ytot = {y: sum(float(g["reported_amount_usd"]) for g in ygroups if g["year"] == y) for y in LYEARS}
    ydef = {y: sum(float(r["reported_amount_usd"]) for r in dfy if r["year"] == y) for y in LYEARS}
    g_rows += ('<tr class="tot"><th scope="row">합계(한국 기업·기관)</th>' + "".join(f'<td class="num"><b>{musd(ytot[y])}</b></td>' for y in LYEARS)
               + f'<td class="num"><b>{musd(sum(ytot.values()))}</b></td></tr>')
    g_rows += ('<tr class="tot"><th scope="row">그중 방산·조선 기업</th>' + "".join(f'<td class="num">{musd(ydef[y]) if ydef[y] else "—"}</td>' for y in LYEARS)
               + f'<td class="num">{musd(sum(ydef.values()))}</td></tr>')
    year_head = "".join(f"<th>{ylabel(y)}</th>" for y in LYEARS)
    group_table = f'<div class="table-scroll"><table class="money"><thead><tr><th>그룹</th>{year_head}<th>합계</th></tr></thead><tbody>{g_rows}</tbody></table></div>'

    top_rows = ""
    for y in LYEARS:
        cs = sorted((c for c in yclients if c["year"] == y), key=lambda c: -float(c["reported_amount_usd"]))[:6]
        cells = "".join(f'<td>{e(smart_title(c["client"]))}<small>{e(c["group"])} · {musd(c["reported_amount_usd"])} · 신고자 {e(c["n_registrants"])}곳</small></td>' for c in cs)
        n_cl = len({c["client"] for c in yclients if c["year"] == y})
        top_rows += f'<tr><th scope="row">{ylabel(y)}<small>의뢰인 {n_cl}곳</small></th>{cells}</tr>'
    top_table = f'<div class="table-scroll"><table class="money top"><thead><tr><th>연도</th>{"".join(f"<th>{i}위</th>" for i in range(1, 7))}</tr></thead><tbody>{top_rows}</tbody></table></div>'

    # defense / shipbuilding firms
    dclients = list(OrderedDict.fromkeys(r["client"] for r in sorted(dfy, key=lambda r: r["client"])))
    dmax = max((float(r["reported_amount_usd"]) for r in dfy), default=1)
    dcell = {(r["client"], r["year"]): r for r in dfy}
    d_rows = ""
    for c in dclients:
        tds = ""
        for y in LYEARS:
            r = dcell.get((c, y))
            tds += (f'<td class="num"{heat(r["reported_amount_usd"], dmax)} title="{e(r["registrants"])}">{musd(r["reported_amount_usd"])}'
                    + ('<small>NDAA</small>' if r["ndaa_reports"] != "0" else "") + "</td>") if r else '<td class="num muted">—</td>'
        d_rows += f'<tr><th scope="row"><a href="#df-{dclients.index(c) + 1}">{e(smart_title(c))}</a></th>{tds}</tr>'
    def_table = f'<div class="table-scroll"><table class="money"><thead><tr><th>방산·조선 기업</th>{year_head}</tr></thead><tbody>{d_rows}</tbody></table></div>'

    def lobbyist_list(rs):
        seen = OrderedDict()
        for r in rs:
            for m in LOBBYIST_RE.finditer(r.get("lobbyists") or ""):
                if m.group(1).strip():
                    nm = m.group(1).strip()
                    cp = (m.group(2) or "").strip()
                    if cp.upper().startswith("SEE PRIOR") or cp.upper() in ("N/A", "NONE"):
                        cp = ""
                    seen.setdefault(nm, set())
                    if cp:
                        seen[nm].add(cp)
        out = []
        for nm, cps in seen.items():
            det = lobdet.get(nm.upper())
            if det and det.get("covered_positions"):
                cps |= set(x.strip() for x in det["covered_positions"].split(" | ") if x.strip())
            out.append((nm, sorted(cps)))
        return out

    df_cards = ""
    for i, c in enumerate(dclients, 1):
        rs = sorted([r for r in drep if r["client"] == c], key=lambda r: (r["filing_year"], porder.index(r["filing_period"]) if r["filing_period"] in porder else 9))
        years = sorted({r["filing_year"] for r in rs})
        regs = sorted({r["registrant"] for r in rs})
        ents = sorted({g for r in rs for g in (r["government_entities"] or "").split("; ") if g})
        lobs = lobbyist_list(rs)
        lob_html = "".join(f'<li><b>{e(smart_title(nm))}</b>' + (f'<small>전직: {e(" / ".join(cps))}</small>' if cps else "") + "</li>" for nm, cps in lobs)
        q_rows = "".join(
            f'<tr><th scope="row">{e(r["filing_year"])} {e(PERIOD.get(r["filing_period"], r["filing_period"]))}<small>{e(smart_title(r["registrant"]))}</small></th>'
            f'<td class="num">{musd(r["amount"]) if r["amount"] not in ("", None) else "미기재"}<small>{e(r["amount_kind"].split("(")[0])}</small></td>'
            f'<td lang="en">{e(r["specific_issues"])}' + ('<small><span class="rel r-direct">NDAA 명시</span></small>' if r["flag_ndaa"] else "") + f'</td><td>{src_link(r["url"], "신고서")}</td></tr>'
            for r in rs)
        cs = [x for x in contrib if c in x["korean_defense_clients"] and not x["member"].startswith("Mike Rogers (")]
        c_txt = ", ".join(f'{x["member"]} {musd(x["amount_usd"])}' for x in sorted(cs, key=lambda x: -float(x["amount_usd"]))[:8])
        df_cards += (f'<article class="sgroup" id="df-{i}" data-sr="로비 · 방산·조선 기업" data-title="{e(c)}">'
                     f'<header><h4>{e(smart_title(c))}</h4><span class="count">{e(years[0])}–{e(years[-1])}</span></header>'
                     f'<div class="two"><div><h5>신고 로비 회사</h5><p>{e(", ".join(smart_title(r) for r in regs))}</p><h5>접촉 기관</h5><p>{e(", ".join(ents) or "미기재")}</p></div>'
                     f'<div><h5>로비스트 {len(lobs)}명 · 신고된 전직</h5><ul class="lob-list">{lob_html}</ul></div></div>'
                     + (f'<p class="small"><b>신고 로비 회사의 정치후원금(LD-203) 중 이 사이트 행위자 수령분</b>: {e(c_txt)} — 로비 회사 전체 고객을 위한 후원이며 이 고객 몫이 아님</p>' if cs else "")
                     + f'<details class="sg-detail"><summary>분기별 신고 {len(rs)}건: 금액·목적·원문</summary><div class="table-scroll"><table class="lobby"><thead><tr><th>분기·신고자</th><th>금액</th><th>신고된 로비 목적(원문)</th><th>출처</th></tr></thead><tbody>{q_rows}</tbody></table></div></details></article>')

    ct_rows = "".join(
        f'<tr><th scope="row">{e(x["member"])}</th><td>{e(smart_title(x["registrant"]))}<small>한국 방산·조선 고객: {e(smart_title(x["korean_defense_clients"]))}</small></td>'
        f'<td class="num">{musd(x["amount_usd"])}<small>{e(x["items"])}건</small></td><td>{e(x["years"])}</td></tr>'
        for x in contrib if not x["member"].startswith("Mike Rogers (")
    )
    n_amb = sum(1 for x in contrib if x["member"].startswith("Mike Rogers ("))
    fsum = rows("fara_summary.csv")
    fact = rows("fara_activities.csv")
    fs_trs = "".join(
        f'<tr id="fara-{e(f["reg_no"])}-{n}" data-sr="로비 · FARA 등록" data-title="{e(f["registrant"])} · {e(f["foreign_principal"])}">'
        f'<th scope="row">{e(f["foreign_principal"])}<small>등록 {e(f["registration_date"])}</small></th><td>{e(f["registrant"])}<small>등록번호 {e(f["reg_no"])}</small></td>'
        f'<td>{e(f["scope_ko"])}</td><td>{e(f["ndaa_link_ko"])}<small>문서 {e(f["docs_read"])}건 열람 · 관련 활동 {e(f["activities_found"])}건 {basis_badge(f["basis"])}</small></td></tr>'
        for n, f in enumerate(fsum, 1)
    )
    REL_CLS = {"직접": "r-direct", "간접": "r-indirect", "무관": "r-dprk"}
    fa_trs = "".join(
        f'<tr id="{e(a["id"])}" data-sr="로비 · FARA 활동" data-title="{e(a["registrant"])} · {e(a["activity_ko"])}" data-rel="{e(a["ndaa_relevance"])}" data-topic="{e(a["topic"])}">'
        f'<th scope="row">{e(a["id"])}<small>{e(a["activity_date"])}</small></th><td>{e(a["registrant"])}<small>{e(a["foreign_principal"])}</small></td>'
        f'<td>{e(a["contact_person"])}</td><td>{e(a["activity_ko"])}<blockquote lang="en">{e(a["quote"])}</blockquote>'
        + (f'<small>{e(a["note"])}</small>' if a.get("note") else "")
        + f'</td><td><span class="rel {REL_CLS.get(a["ndaa_relevance"], "r-indirect")}">{e(a["ndaa_relevance"])}</span><small>{e(a["topic"])} {basis_badge(a["basis"])}</small></td>'
        f'<td>{src_link(a["doc_url"], "보고서")}<small>{e(a["page"])}</small></td></tr>'
        for a in fact
    )
    fa_rel = Counter(a["ndaa_relevance"] for a in fact)
    fa_topic = Counter(a["topic"] for a in fact)
    fara_yearly = rows("fara_yearly.csv")
    fara_agents = rows("fara_agents.csv")
    fara_html = ""
    if fara_yearly:
        fy_years = [str(y) for y in range(2017, 2027)]

        def fara_table(kind_prefix, title):
            regs = defaultdict(lambda: {"amt": defaultdict(float), "partial": defaultdict(bool), "has": defaultdict(bool), "fps": set()})
            for r in fara_yearly:
                if not r["registrant_kind"].startswith(kind_prefix) or r["year"] not in fy_years:
                    continue
                v = regs[r["registrant"]]
                v["fps"].add(r["foreign_principal"])
                if re.fullmatch(r"[0-9.]+", r["receipts_usd"] or ""):
                    v["amt"][r["year"]] += float(r["receipts_usd"]); v["has"][r["year"]] = True
                if not r["completeness"].startswith("complete"):
                    v["partial"][r["year"]] = True
            order = sorted(regs, key=lambda k: -sum(regs[k]["amt"].values()))
            mx = max((x for v in regs.values() for x in v["amt"].values()), default=1)
            trs = ""
            for rg in order:
                v = regs[rg]
                tds = "".join(
                    (f'<td class="num"{heat(v["amt"][y], mx)}>{musd(v["amt"][y])}{"*" if v["partial"][y] else ""}</td>' if v["has"][y]
                     else f'<td class="num muted">{"?" if v["partial"][y] else "—"}</td>') for y in fy_years)
                trs += f'<tr><th scope="row">{e(rg)}<small>{e("; ".join(sorted(v["fps"]))[:160])}</small></th>{tds}<td class="num"><b>{musd(sum(v["amt"].values()))}</b></td></tr>'
            tot = "".join(f'<td class="num"><b>{musd(sum(v["amt"][y] for v in regs.values()))}</b></td>' for y in fy_years)
            trs += f'<tr class="tot"><th scope="row">합계</th>{tot}<td class="num"><b>{musd(sum(x for v in regs.values() for x in v["amt"].values()))}</b></td></tr>'
            return (f'<h4 class="vote-group">{e(title)} <span class="count">{len(regs)}곳</span></h4><div class="table-scroll"><table class="money"><thead><tr><th>등록자 · 외국 주체</th>'
                    + "".join(f"<th>{y}</th>" for y in fy_years) + f'<th>합계</th></tr></thead><tbody>{trs}</tbody></table></div>')

        fara_html = (f'<h3 id="fara-money">FARA: 한국 측 외국 주체로부터의 수령액 (연도별)</h3><p class="section-intro">{md(nar.get("fara_money_intro", ""))}</p>'
                     + fara_table("대행사", "A. 로비·홍보 회사와 개인 대리인 — 용역 보수")
                     + fara_table("한국 기관", "B. 한국 기관·단체의 미국 사무소 — 본부에서 받은 운영자금(로비 보수 아님)"))
    if fara_agents:
        ag = [r for r in fara_agents if r.get("former_government_positions") and not r["former_government_positions"].startswith("미공시")]
        fa_ag = "".join(
            f'<tr><th scope="row">{e(r["person"])}<small>{e(r.get("role", ""))}</small></th><td>{e(r["registrant"])}<small>{e(r["foreign_principal"])}</small></td>'
            f'<td>{e(r["former_government_positions"])}<small>출처: {e(r.get("former_position_source", "")[:60])}</small></td><td>{e(r.get("short_form_date", ""))}<small>{src_link(r.get("source_url"), "단축신고서")}</small></td></tr>'
            for r in ag)
        fara_html += (f'<details class="house-sources"><summary>FARA 대리인 중 전직 공직 경력이 확인된 사람 <span class="count">{len(ag)}</span> / 전체 대리인 {len({r["person"] for r in fara_agents})}명</summary>'
                      f'<p class="small">FARA 단축신고서에는 전직 공직을 묻는 항목이 없습니다. LDA 신고서의 \'대상 공직(covered position)\' 기재와, 전직 연방의원 명단(Voteview)과의 이름 대조로 보완했습니다. 이름 대조로 찾은 경우는 [이름 대조·동일인 추정]으로 표시했습니다.</p>'
                      f'<div class="table-scroll"><table class="lobby"><thead><tr><th>대리인</th><th>등록자·외국 주체</th><th>전직</th><th>신고일</th></tr></thead><tbody>{fa_ag}</tbody></table></div></details>')
    tab_lobby = f"""<section class="panel" id="lobby" aria-labelledby="t-lobby">
<p class="kicker">07 · LOBBYING</p><h2 id="t-lobby">로비: 한국 정부·기업은 누구를 통해, 얼마를 들여, 무엇을 요청했나</h2>
<p class="section-intro">{md(nar['lobby_intro'])}</p>
<div class="note"><b>먼저 읽을 점</b><p>{md(nar['lobby_caution'])}</p></div>
<div class="mini-path"><div><b>{musd(sum(ytot.values()))}</b><span>한국 기업·기관 LDA 신고액 합계 (2017–2026 2분기)</span></div>
<div><b>{musd(ytot.get("2025", 0))}</b><span>2025년 (최대)</span></div>
<div><b>{musd(sum(ydef.values()))}</b><span>그중 방산·조선 기업</span></div>
<div><b>{len(fsum)}</b><span>FARA 한국 측 활성 등록</span></div></div>
<h3 id="lda-yearly">연도별 로비 금액: 한국 기업 그룹별 (LDA)</h3>
<p class="section-intro">{md(nar['lda_yearly_intro'])}</p>
{group_table}
<h3 id="lda-top">연도별 주요 로비 주체 (신고액 상위 6곳)</h3>
{top_table}
<h3 id="lda-defense">방산·조선 기업의 로비</h3>
<p class="section-intro">{md(nar['lda_defense_intro'])}</p>
{def_table}
{df_cards}
<h3 id="lda-contrib">로비 회사의 정치후원금(LD-203) 중 행위자 의원 수령분</h3>
<p class="section-intro">{md(nar['lda_contrib_intro'])}</p>
<details class="house-sources"><summary>후원 내역 <span class="count">{ct_rows.count("<tr>")}</span></summary>
<div class="table-scroll"><table class="lobby"><thead><tr><th>수령 의원</th><th>후원 신고 로비 회사</th><th>금액</th><th>연도</th></tr></thead><tbody>{ct_rows}</tbody></table></div>
<p class="small">동명이인 때문에 제외한 Mike Rogers 관련 {n_amb}행(미시간 상원 후보 Mike Rogers와 구분 불가)은 표에 넣지 않았습니다.</p></details>
{fara_html}
<h3 id="fara">FARA 외국대리인 등록: 한국 정부·기관 <span class="count">{len(fsum)}</span></h3>
<p class="section-intro">{md(nar['fara_intro'])}</p>
<div class="table-scroll"><table class="lobby"><thead><tr><th>외국 주체</th><th>등록 대리인</th><th>계약 범위</th><th>NDAA 관련성(활동보고서 확인 결과)</th></tr></thead><tbody>{fs_trs}</tbody></table></div>
<h3 id="fara-acts">FARA 활동보고서에 기록된 접촉 <span class="count">{len(fact)}</span></h3>
<p class="section-intro">{md(nar['fara_acts_intro'])}</p>
<div class="filters" role="search"><input type="search" id="fa-q" placeholder="의원실·위원회·주제 검색(예: Armed Services, Wilson, shipbuilding)" aria-label="FARA 활동 검색">
<select id="fa-rel" aria-label="NDAA 관련성"><option value="">관련성 전체</option>{''.join(f'<option value="{e(k)}">{e(k)} ({v})</option>' for k, v in fa_rel.items())}</select>
<select id="fa-topic" aria-label="주제"><option value="">주제 전체</option>{''.join(f'<option value="{e(k)}">{e(k)} ({v})</option>' for k, v in fa_topic.most_common())}</select>
<span id="fa-n" class="small" aria-live="polite"></span></div>
<div class="table-scroll"><table class="lobby" id="fa-list"><thead><tr><th>ID·날짜</th><th>등록자·외국 주체</th><th>접촉 대상</th><th>활동·원문</th><th>NDAA 관련성</th><th>출처</th></tr></thead><tbody>{fa_trs}</tbody></table></div>
<p class="small">LDA 수집: {e(lda_sum.get("fetched_at", ""))} · 질의 {len(lda_sum.get("queries", []))}종 · 2017–2026 신고서 {e(str(lda_sum.get("filings", "")))}건 중 한국 기업·기관 의뢰 {e(str(lda_sum.get("korean_actor_filings", "")))}건(수정신고 정리 전). FARA: efile.fara.gov 일괄 색인(2026-10-03)과 보고서 PDF.</p>
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
            f'<li id="th-{n}" data-sr="쟁점 계보" data-title="{e(tlabel(t["thread"]))} · FY{e(t["fy"])} {e(t["section"])}" class="{thread_cls(t["status"])}"><time>FY{e(t["fy"])}</time><div><b>{e(t["section"])} · {e(t["status"])}</b>'
            f'<p>{md(t["change_ko"])}</p><span class="small">{e(t["key_terms"])} {ids_links(t["source_ref"]) if ID_RE.search(t["source_ref"] or "") else e(t["source_ref"])}</span></div></li>'
            for n, t in enumerate(threads, 1) if t["thread"] == tn
        )
        thread_detail += f'<details class="thread"><summary>{e(tlabel(tn))}</summary><ol class="lineage">{lis}</ol></details>'

    floor_rows = "".join(
        f'<tr id="fl-{n}" data-sr="병력 하한 판본 비교" data-title="FY{e(f["fy"])} {e(f["chamber"])} {e(f["section"])}"><th scope="row">FY{e(f["fy"])}</th><td>{e(f["chamber"])}<small>{e(f["version"])}</small></td><td>{e(f["section"])}</td>'
        f'<td>{e(f["key_terms"])}<blockquote lang="en">{e(f["quote"])}</blockquote></td><td>{src_link(f["source_url"])}</td></tr>'
        for n, f in enumerate(floor, 1)
    )

    def hist_card(h):
        return f"""<details class="evidence hist" id="{e(h['id'])}" data-fy="{e(h['fy'])}" data-rel="{e(h['relation'])}" data-cat="{e(' '.join(cats(h['category'])))}" data-sr="제정법 조문" data-title="FY{e(h['fy'])} {e(h['section'])} — {e(h['summary_ko'])}">
<summary><span class="eid">{e(h['id'])}</span><span class="summary-main"><span class="small">FY{e(h['fy'])} · {e(h['public_law'])} · <b>{e(h['section'])}</b></span><strong>{e(h['summary_ko'])}</strong><span class="chips">{cat_chips(h['category'])}</span></span>{rel_badge(h['relation'])}</summary>
<div class="evidence-body"><p class="small" lang="en">{e(h['heading'])}</p><blockquote lang="en">{e(h['quote'])}</blockquote>
<p class="references">{src_link(h['source_url'], '공법 원문')} <span class="small">{e(h['locator'])} · 제정 {e(h['enacted_date'])} · 원문 대조 {e(h['quote_verified'])}</span></p></div></details>"""

    fy_count = Counter(h["fy"] for h in hist)
    fy_opts = "".join(f'<option value="{fy}">FY{fy} ({fy_count[fy]})</option>' for fy in sorted(fy_count))
    hist_cat_opts = "".join(f'<option value="{k}">{e(v)}</option>' for k, v in CATS.items())
    tab_evo = f"""<section class="panel" id="evolution" aria-labelledby="t-evolution">
<p class="kicker">08 · EVOLUTION FY2017–FY2027</p><h2 id="t-evolution">한국 관련 내용은 어떻게 진화했나</h2>
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
        f'<tr id="{e(s["id"])}" data-sr="발언·문서" data-title="{e(s["actor"])} · {e(s["date"])}"><th scope="row">{e(s["id"])}</th><td>{e(s["actor"])}<small>{e(s.get("role_at_time"))} {e(s.get("party_state"))}</small></td>'
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
            ("actors", "4 행위자"), ("positions", "5 입장"), ("votes", "6 표결"), ("lobby", "7 로비"), ("evolution", "8 진화"), ("archive", "근거 자료실")]
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
{tab_overview}{tab_prov}{tab_compare}{tab_actors}{tab_pos}{tab_votes}{tab_lobby}{tab_evo}{tab_arch}
</main>
<footer><b>NDAA 속의 한국</b><span>공개 원문 기반 · 사실 / 정황 / 추정 구분 · 갱신 {e(nar['updated'])}</span><a href="../aukus/">AUKUS 사례</a><a href="../ira/">IRA 사례</a></footer>
<script src="ndaa_korea.js"></script>
</body></html>
"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote {ROOT / 'index.html'}: provisions {len(prov)}, amendments {len(amds)}, compare {len(comp)}, "
          f"status {len(status)}, history {len(hist)}, threads {len(threads)}, actors {len(actors)}, "
          f"stances {len(stances)}, statements {len(stmts)}, lda groups {len(ygroups)}, defense reports {len(drep)}, fara {len(fact)}, sources {len(sources)}")


if __name__ == "__main__":
    build()
