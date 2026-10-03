#!/usr/bin/env python3
"""Build aukus/index.html from aukus/data/*.csv and narrative.json.

Usage: python3 tools/build_aukus.py
"""
import csv
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "aukus"
DATA = ROOT / "data"


def rows(name):
    path = DATA / name
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def local(src, page=None):
    """Repo-relative link to a stored copy, or '' if none."""
    f = (src or {}).get("file", "")
    if not f or f.endswith("/"):
        return ""
    return f + (f"#page={page}" if page and f.endswith(".pdf") else "")


def e(text):
    return escape(text or "")


def refs_html(raw, sources):
    """Render the refs JSON list as PDF/page links."""
    try:
        refs = json.loads(raw or "[]")
    except json.JSONDecodeError:
        return f"<span>{e(raw)}</span>"
    out = []
    for r in refs:
        src = sources.get(r.get("source", ""), {})
        page = r.get("pdf_page")
        label = r.get("locator") or (f"PDF {page}쪽" if page else "")
        title = src.get("title") or r.get("source", "")
        href = local(src, page) or r.get("url", "")
        link = f'<a href="{e(href)}">{e(title)} · {e(label)}</a>' if href else f"{e(title)} · {e(label)}"
        if local(src) and r.get("url"):
            link += f' <a class="orig" href="{e(r["url"])}">원 출처</a>'
        out.append(f"<span>{link}</span>")
    return "".join(out)


def level_badge(level):
    cls = "" if level == "직접 확인" else " amber"
    return f'<span class="badge{cls}">{e(level)}</span>'


def evidence_block(ev, sources, anchor=True):
    attrs = f'id="{e(ev["id"])}" ' if anchor else ""
    return f"""<details class="evidence" {attrs}data-level="{e(ev.get('level'))}" data-theme="{e(ev.get('theme'))}">
<summary><span class="eid">{e(ev['id'])}</span><span class="summary-main"><span class="small">{e(ev.get('theme'))} · {e(ev.get('who'))} · {e(ev.get('date'))}</span><strong>{e(ev['claim'])}</strong></span>{level_badge(ev.get('level', ''))}</summary>
<div class="evidence-body">
<blockquote lang="en">{e(ev.get('quote'))}</blockquote>
<p class="translation">{e(ev.get('translation'))}</p>
<div class="two"><div><h4>평가</h4><p>{e(ev.get('assessment'))}</p></div><div><h4>한계</h4><p>{e(ev.get('limit'))}</p></div></div>
<h4>원문</h4><div class="references">{refs_html(ev.get('refs'), sources)}</div>
</div></details>"""


def ev_links(ids):
    return " ".join(f'<a href="#{e(i)}" data-ev="{e(i)}">{e(i)}</a>' for i in ids if i)


def build():
    nar = json.loads((DATA / "narrative.json").read_text(encoding="utf-8"))
    evidence = rows("evidence.csv")
    clauses = rows("clause-comparison.csv")
    bill_map = rows("bill-map.csv")
    positions = rows("positions.csv")
    timeline = rows("timeline.csv")
    actors = rows("actors.csv")
    manifest = rows("source_manifest.csv")
    sources = {m["id"]: m for m in manifest}
    by_theme = {}
    for ev in evidence:
        by_theme.setdefault(ev.get("theme", ""), []).append(ev)

    def evs(themes, anchor=False):
        return "\n".join(evidence_block(ev, sources, anchor) for t in themes for ev in by_theme.get(t, []))

    # 1. case question
    cards = "".join(
        f'<article><span class="number">{e(c["label"])}</span><h3>{e(c["title"])}</h3><p>{c["body"]}</p>'
        f'<p class="e-links small">근거 {ev_links(c.get("evidence", []))}</p></article>'
        for c in nar["cards"]
    )
    facts = "".join(
        f'<div><b>{e(f["value"])}</b><span>{e(f["label"])}</span></div>' for f in nar["facts"]
    )
    tab1 = f"""<section class="panel" id="question" aria-labelledby="t-question">
<p class="kicker">01 · CASE QUESTION</p><h2 id="t-question">{e(nar['question'])}</h2>
<p class="lede">{nar['lede']}</p>
<div class="mini-path">{facts}</div>
<div class="finding-grid">{cards}</div>
<div class="note"><b>읽는 법</b><p>{nar['reading_note']}</p></div>
</section>"""

    # 2. enacted provisions
    tab2 = f"""<section class="panel" id="law" aria-labelledby="t-law">
<p class="kicker">02 · ENACTED TEXT</p><h2 id="t-law">허용 조문: 제정법은 무엇을 허락했나</h2>
<p class="section-intro">{nar['law_intro']}</p>
{evs(['조문'])}
</section>"""

    # 3. origin
    def tl_rows(filter_fn):
        out = []
        for t in timeline:
            if not filter_fn(t):
                continue
            src = sources.get(t.get("source_id", ""), {})
            link = ""
            if local(src):
                link = f'<a href="{e(local(src))}">{e(t["source_id"])}</a>'
            elif src.get("url"):
                link = f'<a href="{e(src["url"])}">{e(t["source_id"])}</a>'
            else:
                link = e(t.get("source_id"))
            out.append(
                f'<li class="tl-{e(t.get("chamber", "")).replace(" ", "")}"><time>{e(t["date"])}</time>'
                f'<div><b>{e(t["event"])}</b><span class="small">{" · ".join(e(x) for x in (t.get("chamber"), t.get("actor")) if x and x != "—")}</span>'
                f'<p>{e(t.get("detail"))}</p><span class="small">자료 {link}</span></div></li>'
            )
        return "<ol class=\"timeline\">" + "".join(out) + "</ol>"

    brow = "".join(
        f'<tr><td><span class="tier tier-{e(b["tier"])}">{e(b["tier_label"])}</span></td>'
        f'<th scope="row">{e(b["bill"])}<small>{e(b["sponsor"])} · {e(b["date"])}</small></th>'
        f'<td>{e(b["role_for_sale"])}</td><td>{e(b["fate"])}</td>'
        f'<td>{ev_links([i for i in b["evidence"].split(";") if i.startswith("E")])}<small>{e(b["certainty"])}</small></td></tr>'
        for b in bill_map
    )
    tab3 = f"""<section class="panel" id="origin" aria-labelledby="t-origin">
<p class="kicker">03 · PROPOSAL</p><h2 id="t-origin">발의와 편입: 조문은 어디서 왔나</h2>
<p class="section-intro">{nar['origin_intro']}</p>
<h3>법안 지도: 각 법안은 판매 승인과 어떻게 연결되나</h3>
<p class="section-intro">{nar['billmap_intro']}</p>
<div class="table-scroll"><table class="billmap"><thead><tr><th>관계</th><th>법안·문서</th><th>판매 승인에서 한 역할</th><th>처리 결과</th><th>근거</th></tr></thead><tbody>{brow}</tbody></table></div>
<h3>발의 단계 근거</h3>
{evs(['발의', '배경'])}
</section>"""

    # 4. clause comparison
    crow = "".join(
        f'<tr><th scope="row">{e(c["date"])}<small>{e(c["version"])}</small></th><td>{e(c["section"])}</td>'
        f'<td><blockquote lang="en">{e(c["quote"])}</blockquote></td><td>{e(c["summary"])}<div class="references">{refs_html(c.get("refs"), sources)}</div></td></tr>'
        for c in clauses
    )
    tab4 = f"""<section class="panel" id="versions" aria-labelledby="t-versions">
<p class="kicker">04 · CLAUSE COMPARISON</p><h2 id="t-versions">조문 변화: 버전마다 무엇이 달랐나</h2>
<p class="section-intro">{nar['versions_intro']}</p>
{nar['versions_matrix']}
<h3>버전별 원문</h3>
<div class="table-scroll"><table><thead><tr><th>버전</th><th>조항</th><th>원문</th><th>요약·출처</th></tr></thead><tbody>{crow}</tbody></table></div>
</section>"""

    # 5. debate and passage
    tab5 = f"""<section class="panel" id="passage" aria-labelledby="t-passage">
<p class="kicker">05 · DEBATE &amp; PASSAGE</p><h2 id="t-passage">논의와 통과: 누가 무엇을 걱정했고, 어떻게 통과됐나</h2>
<p class="section-intro">{nar['passage_intro']}</p>
<h3>입법 연표</h3>
{tl_rows(lambda t: True)}
<h3>쟁점과 발언</h3>
{evs(['논의'])}
<h3>표결과 서명</h3>
{evs(['표결', '서명'])}
<h3>제정 이후</h3>
{evs(['이후'])}
</section>"""

    # 5b. positions of the three camps
    phases = []
    for p in positions:
        if p["period"] not in phases:
            phases.append(p["period"])
    camps = ["행정부", "상원", "하원"]

    def pcell(period, camp):
        items = [p for p in positions if p["period"] == period and p["actor"] == camp]
        return "".join(
            f'<div class="pos"><b>{e(p["body"])}</b><p>{e(p["position"])}</p>'
            f'<span class="small">{ev_links([i for i in p["evidence"].split(";") if i.startswith("E")])} · {e(p["certainty"])}</span></div>'
            for p in items
        ) or '<span class="small">—</span>'

    prow = "".join(
        f'<tr><th scope="row">{e(ph)}</th>' + "".join(f"<td>{pcell(ph, c)}</td>" for c in camps) + "</tr>"
        for ph in phases
    )
    # per-actor stances in six groups (links use the same E/H/L anchors as elsewhere)
    def stance_cls(s):
        if s.startswith(("신중", "회의")) or s.startswith("조건부 (") or s == "조건부(우려 제기)":
            return "st-caution"
        if s.startswith("조건부"):
            return "st-cond"
        if s.startswith(("간접", "의뢰인")):
            return "st-indirect"
        return "st-pro"

    def refs_links(ids):
        return " ".join(re.sub(r"\b([EHL]\d{2,3})\b", r'<a href="#\1">\1</a>', e(i)) for i in ids.split(";") if i)

    stances = rows("stances.csv")
    st_groups = [("행정부", "행정부"), ("상원", "상원"), ("하원", "하원"), ("호주측", "호주 측 관계자"), ("산업계", "산업계"), ("로비스트", "로비스트")]
    st_tables = ""
    for g, label in st_groups:
        trs = "".join(
            f'<tr><th scope="row">{e(s["actor"])}</th><td><span class="stance {stance_cls(s["stance"])}">{e(s["stance"])}</span>'
            f'<small>{e(s["basis"])}</small></td><td>{e(s["reason"])}</td><td>{e(s["conditions_concerns"])}</td><td>{refs_links(s["evidence"])}</td></tr>'
            for s in stances if s["group"] == g
        )
        st_tables += (f'<h4>{e(label)}</h4><div class="table-scroll"><table class="stances"><thead><tr><th>행위자</th><th>입장 · 근거 성격</th>'
                      f'<th>이유</th><th>조건 · 우려</th><th>근거</th></tr></thead><tbody>{trs}</tbody></table></div>')
    stance_html = f"""<h3 id="stances">행위자별 입장: 찬성·조건부·신중</h3>
<p class="section-intro">{nar['stances_intro']}</p>
{st_tables}"""

    tab_pos = f"""<section class="panel" id="positions" aria-labelledby="t-positions">
<p class="kicker">06 · THREE CAMPS</p><h2 id="t-positions">입장 차이: 행정부·상원·하원은 무엇을 원했고 어떻게 바뀌었나</h2>
<p class="section-intro">{nar['positions_intro']}</p>
<div class="table-scroll"><table class="positions"><thead><tr><th>시기</th><th>행정부 (국방부·해군)</th><th>상원</th><th>하원</th></tr></thead><tbody>{prow}</tbody></table></div>
<h3>정리</h3>
{nar['positions_summary']}
{stance_html}
</section>"""

    # 6. actors, grouped by camp
    def link_ids(html_text):
        """Turn [H03] / [L19] / E42 style references into in-page links."""
        html_text = re.sub(r"\b([HL]\d{2,3})\b", r'<a href="#\1">\1</a>', html_text)
        return re.sub(r"\b(E\d{2})\b", r'<a href="#\1" data-ev="\1">\1</a>', html_text)

    def md_cell(text):
        return link_ids(re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", e(text)))

    groups = ["행정부", "상원", "하원", "호주측", "산업계", "로비스트"]
    group_label = {"호주측": "호주 측 관계자"}

    def acard(a):
        src = " ".join(md_cell(s) for s in (a.get("source_ids") or "").split(";") if s)
        return (f'<article class="actor"><h3>{e(a["name"])}</h3><p class="small">{e(a.get("role_at_time"))} · {e(a.get("party_state"))}</p>'
                f'<p>{e(a.get("what_they_did"))}</p><p class="small">자료 {src}</p></article>')

    lobbyists = rows("aukus-lobbyists.csv")
    lrow = "".join(
        f'<tr><th scope="row">{e(l["lobbyist"])}</th><td>{e(l["registrant"])}</td><td>{e(l["client"])}</td>'
        f'<td>{e(l["type"])}</td><td>{e(l["quarters"])}</td><td>{md_cell(l["congress_link"])}<small>{e(l["covered_position"])}</small></td></tr>'
        for l in lobbyists
    )
    lobby_table = f"""<details class="house-sources"><summary>AUKUS 로비 공시에 이름이 오른 로비스트 <span class="count">{len(lobbyists)}</span></summary>
<p class="small">2022–2024 LDA 공시 가운데 AUKUS 관련 활동(L51)에 이름이 오른 로비스트 전원입니다. 전직은 로비스트가 신고한 '과거 공직(covered position)'이며, 의회 근무 경력이 있는 사람은 {sum(1 for l in lobbyists if l["congress_link"])}명입니다. 전직은 접근 경로의 가능성일 뿐 실제 접촉을 뜻하지 않습니다.</p>
<div class="table-scroll"><table class="lobbyists"><thead><tr><th>로비스트</th><th>소속(신고자)</th><th>의뢰인</th><th>유형</th><th>신고 분기</th><th>의회 경력 · 신고된 전직</th></tr></thead><tbody>{lrow}</tbody></table></div></details>"""
    actor_sections = ""
    for g in groups:
        cards = "".join(acard(a) for a in actors if a.get("group") == g)
        extra = lobby_table if g == "로비스트" else ""
        actor_sections += f'<h3 class="actor-group">{e(group_label.get(g, g))} <span class="count">{sum(1 for a in actors if a.get("group") == g)}</span></h3><div class="finding-grid">{cards}</div>{extra}'

    house_members = rows("house-members.csv")
    house_sources = rows("house-sources.csv")
    hm_rows = "".join(
        f'<tr><th scope="row">{e(m["member"])}</th><td>{md_cell(m["role_2023"])}</td><td>{md_cell(m["background"])}</td>'
        f'<td>{md_cell(m["district"])}</td><td>{md_cell(m["money"])}</td><td>{md_cell(m["institution"])}</td>'
        f'<td>{md_cell(m["assessment"])}</td></tr>'
        for m in house_members
    )
    hs_rows = "".join(
        f'<tr id="{e(s["id"])}"><th scope="row">{e(s["id"])}</th><td>{e(s["who"])}</td><td>{e(s["claim"])}'
        + (f'<blockquote lang="en">{e(s["quote"])}</blockquote>' if s.get("quote") else "")
        + f'</td><td><a href="{e(s["url"].split(" ")[0])}">원 출처</a><small>{e(s["source_type"])} · 접속 {e(s["accessed"])} · 원문대조 {e(s["verified"])}</small></td></tr>'
        for s in house_sources
    )
    hdir = ROOT / "house_motivation" / "sources"
    hfiles = sorted(p.name for p in hdir.iterdir() if p.is_file()) if hdir.exists() else []
    hfile_list = "".join(f'<li><a href="house_motivation/sources/{e(f)}">{e(f)}</a></li>' for f in hfiles)
    house = f"""<h3 id="house-why">하원의원은 왜 호주 잠수함 판매에 나섰나</h3>
<p class="section-intro">{link_ids(nar['house_intro'])}</p>
{nar['house_lenses']}
<h4>결론</h4>
{link_ids(nar['house_findings'])}
<h4>의원별 정리</h4>
<div class="table-scroll"><table class="house"><thead><tr><th>의원</th><th>2023년 역할</th><th>① 개인 배경</th><th>② 지역구</th><th>③ 로비·자금</th><th>④ 제도</th><th>가장 그럴듯한 설명 [추정]</th></tr></thead><tbody>{hm_rows}</tbody></table></div>
<h4>이 자료로 말할 수 없는 것</h4>
{link_ids(nar['house_cannot'])}
<h4>남은 확인 사항</h4>
{link_ids(nar['house_open'])}
<details class="house-sources"><summary>근거표 H01–L65 <span class="count">{len(house_sources)}</span></summary>
<div class="table-scroll"><table><thead><tr><th>ID</th><th>대상</th><th>내용·인용</th><th>출처</th></tr></thead><tbody>{hs_rows}</tbody></table></div>
</details>
<details class="house-sources"><summary>보관 원자료 <span class="count">{len(hfiles)}</span></summary>
<p class="small">정부·의회 문서, FEC·FARA·LDA 자료, 의원실 보도자료 사본입니다. 언론사 기사는 저작권 때문에 사본을 올리지 않고 근거표의 원 출처 링크로만 연결했습니다.</p>
<ul class="file-list">{hfile_list}</ul></details>"""

    tab6 = f"""<section class="panel" id="actors" aria-labelledby="t-actors">
<p class="kicker">07 · ACTORS</p><h2 id="t-actors">행위자</h2>
<p class="section-intro">{nar['actors_intro']}</p>
{actor_sections}
{house}
</section>"""

    # archive
    mrow = "".join(
        f'<tr><th scope="row">{e(m["id"])}</th><td>{e(m.get("date"))}</td><td>'
        + (f'<a href="{e(local(m))}">{e(m["title"])}</a>' if local(m) else e(m["title"]))
        + f'<small>{e(m.get("kind"))} · {e(m.get("pages"))}쪽</small></td>'
        f'<td><a href="{e(m.get("url"))}">원 출처</a><small>{e(m.get("access_notes"))}</small></td>'
        f'<td><code>{e((m.get("sha256") or "")[:16])}</code></td></tr>'
        for m in manifest
    )
    unresolved = "".join(f"<li>{u}</li>" for u in nar["unresolved"])
    tab7 = f"""<section class="panel" id="archive" aria-labelledby="t-archive">
<p class="kicker">ARCHIVE</p><h2 id="t-archive">근거 자료실</h2>
<h3>주장–증거 목록 <span class="count">{len(evidence)}</span></h3>
<div class="filters" role="search"><input type="search" id="ev-q" placeholder="인물·조항·문구 검색" aria-label="근거 검색">
<select id="ev-theme" aria-label="주제"><option value="">모든 주제</option>{''.join(f'<option>{e(t)}</option>' for t in by_theme)}</select>
<select id="ev-level" aria-label="증거 수준"><option value="">모든 수준</option><option>직접 확인</option><option>정황</option><option>미확인</option></select>
<span id="ev-n" class="small" aria-live="polite"></span></div>
<div id="ev-list">{evs([t for t in by_theme], anchor=True)}</div>
<h3>원문 자료 <span class="count">{len(manifest)}</span></h3>
<div class="table-scroll"><table><thead><tr><th>ID</th><th>날짜</th><th>자료</th><th>출처</th><th>SHA-256 앞 16자</th></tr></thead><tbody>{mrow}</tbody></table></div>
<h3>미확인·추가 확인 필요</h3><ul class="unresolved">{unresolved}</ul>
<div class="method"><div><h3>분석 방식</h3>{nar['method']}</div><div><h3>범위와 한계</h3>{nar['limits']}</div></div>
</section>"""

    tabs = [("question", "1 사례의 질문"), ("law", "2 허용 조문"), ("origin", "3 발의와 편입"),
            ("versions", "4 조문 변화"), ("passage", "5 논의와 통과"), ("positions", "6 입장 차이"),
            ("actors", "7 행위자"), ("archive", "근거 자료실")]
    nav = "".join(f'<a href="#{i}" data-tab="{i}">{e(label)}</a>' for i, label in tabs)

    html = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AUKUS 잠수함 이전 입법사</title>
<meta name="description" content="{e(nar['description'])}">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23112645'/%3E%3Cpath d='M5 18c0-3 4-5 11-5s11 2 11 5-4 4-11 4-11-1-11-4zm9-8h4v3h-4z' fill='%23a8d6ff'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://cdn.jsdelivr.net"><link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"><link rel="stylesheet" href="aukus.css">
<link rel="canonical" href="https://woochangkang.github.io/us_legislature/aukus/">
</head><body>
<a class="skip" href="#main">본문 바로가기</a>
<header><div class="mast"><a class="brand" href="../"><span class="brand-mark" aria-hidden="true"></span>입법 증거 아틀라스</a><span class="period">{e(nar['period'])}</span></div>
<nav aria-label="사례 탭">{nav}</nav></header>
<main id="main">
<div class="title"><p class="kicker">AUKUS CASE STUDY · FY2024 NDAA</p><h1>{e(nar['title'])}</h1><p>{e(nar['subtitle'])}</p></div>
{tab1}{tab2}{tab3}{tab4}{tab5}{tab_pos}{tab6}{tab7}
</main>
<footer><b>AUKUS 입법 증거 아틀라스</b><span>공개 원문 기반 · 직접 확인 / 정황 / 미확인 구분 · 갱신 {e(nar['updated'])}</span><a href="../ira/">IRA 사례 보기</a></footer>
<script src="aukus.js"></script>
</body></html>
"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote {ROOT / 'index.html'}: evidence {len(evidence)}, clauses {len(clauses)}, "
          f"timeline {len(timeline)}, actors {len(actors)}, sources {len(manifest)}")


if __name__ == "__main__":
    build()
