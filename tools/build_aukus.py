#!/usr/bin/env python3
"""Build aukus/index.html from aukus/data/*.csv and narrative.json.

Usage: python3 tools/build_aukus.py
"""
import csv
import json
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
    tab_pos = f"""<section class="panel" id="positions" aria-labelledby="t-positions">
<p class="kicker">06 · THREE CAMPS</p><h2 id="t-positions">입장 차이: 행정부·상원·하원은 무엇을 원했고 어떻게 바뀌었나</h2>
<p class="section-intro">{nar['positions_intro']}</p>
<div class="table-scroll"><table class="positions"><thead><tr><th>시기</th><th>행정부 (국방부·해군)</th><th>상원</th><th>하원</th></tr></thead><tbody>{prow}</tbody></table></div>
<h3>정리</h3>
{nar['positions_summary']}
</section>"""

    # 6. actors
    acards = "".join(
        f'<article class="actor"><h3>{e(a["name"])}</h3><p class="small">{e(a.get("role_at_time"))} · {e(a.get("party_state"))}</p>'
        f'<p>{e(a.get("what_they_did"))}</p><p class="small">자료 {e(a.get("source_ids"))}</p></article>'
        for a in actors
    )
    tab6 = f"""<section class="panel" id="actors" aria-labelledby="t-actors">
<p class="kicker">07 · ACTORS</p><h2 id="t-actors">행위자</h2>
<p class="section-intro">{nar['actors_intro']}</p>
<div class="finding-grid">{acards}</div>
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
