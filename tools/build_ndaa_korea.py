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
    lobby = rows("fara.csv")
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
    lobby_html = ""
    if lobby:
        lr = "".join(
            f'<tr id="fara-{n}" data-sr="FARA 등록" data-title="{e(l["foreign_principal"])} · {e(l["registrant"])}"><th scope="row">{e(l["foreign_principal"])}</th><td>{e(l["registrant"])}<small>등록번호 {e(l["registration_number"])}</small></td>'
            f'<td>{e(l["fp_registration_date"])}</td><td>{e(l["ndaa_link"])}</td></tr>'
            for n, l in enumerate(lobby, 1)
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
<p class="kicker">07 · EVOLUTION FY2017–FY2027</p><h2 id="t-evolution">한국 관련 내용은 어떻게 진화했나</h2>
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
            ("actors", "4 행위자"), ("positions", "5 입장"), ("votes", "6 표결"), ("evolution", "7 진화"), ("archive", "근거 자료실")]
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
{tab_overview}{tab_prov}{tab_compare}{tab_actors}{tab_pos}{tab_votes}{tab_evo}{tab_arch}
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
