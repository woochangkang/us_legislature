#!/usr/bin/env python3
"""Fetch Senate LDA lobbying filings related to South Korea (run from a U.S. network, e.g. GitHub Actions).

lda.gov's Akamai edge refuses requests from some networks (observed from Korea: HTTP 403 `$(SERVE_403)`),
so this runs in .github/workflows/lda-fetch.yml. Standard library only.

Usage: python3 tools/lda_fetch.py --years 2017 2018 ... 2026 --out lda_out [--contrib-years 2023 2024 2025 2026]
Env:   LDA_API_KEY (optional; anonymous = 15 req/min, key = 120 req/min)

Outputs (in --out):
  filings_raw.jsonl     every filing returned by any query (one JSON per line, deduplicated by filing_uuid)
  filings.csv           one row per filing (flattened; lobbyists with covered positions; flags)
  activities.csv        one row per lobbying activity (issue code, description, government entities, lobbyists)
  contributions_raw.jsonl / contributions.csv   LD-203 reports for registrants serving Korean defense/shipbuilding clients
  summary.json
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://lda.gov/api/v1/"
KEY = os.environ.get("LDA_API_KEY", "").strip()
PAUSE = 0.6 if KEY else 4.2  # stay under 120/min or 15/min

# (label, query params) — results are unioned by filing_uuid
QUERIES = [("client_country_KR", {"client_country": "KR"}), ("foreign_entity_KR", {"foreign_entity_country": "KR"}),
           ("text_Korea", {"filing_specific_lobbying_issues": "Korea"})]
QUERIES += [(f"client_{n.replace(' ', '_')}", {"client_name": n}) for n in (
    "Hanwha", "Hyundai", "Kia", "Samsung", "LG Electronics", "LG Energy", "LG Chem", "SK hynix", "SK Innovation", "SK Battery",
    "SK On", "SK Siltron", "SK Telecom", "Doosan", "POSCO", "Lotte", "Poongsan", "LIG", "Korea", "Korean", "Celltrion", "CJ CheilJedang")]

# Korean actor = client is Korean or Korean-owned (vs. a U.S. client whose issues merely mention Korea)
KOREAN_NAME = re.compile(r"\bHanwha|\bHyundai|\bKia\b|\bSamsung|\bLG (Electronics|Energy|Chem|Display|Innotek)|\bSK (hynix|Innovation|Battery|On|Siltron|Telecom|Inc)|"
                         r"\bDoosan|\bPOSCO|\bLotte|\bPoongsan|\bLIG Nex|\bKorea|\bKorean|\bCelltrion|\bCJ CheilJedang|\bHD Hyundai|\bKOTRA\b", re.I)
DEFENSE_TXT = re.compile(r"National Defense Authorization|\bNDAA\b|defense authorization|shipbuild|shipyard|naval|\bNavy\b|munition|ground (combat )?systems|"
                         r"Department of Defense Appropriations|defense procurement|\bMRO\b|ship repair|SHIPS for America", re.I)
FLAGS = {
    "korea": r"\bKorea|\bROK\b|Republic of Korea",
    "ndaa": r"National Defense Authorization|\bNDAA\b",
    "fy27_ndaa": r"FY ?(20)?27 (National Defense Authorization|NDAA)|H\.?\s?R\.?\s?8800\b|\bS\.?\s?4784\b",
    "shipbuilding": r"shipbuild|shipyard|naval vessel|ship repair|\bMRO\b|SHIPS for America|MASGA",
    "usfk": r"USFK|Forces Korea|troop|force posture",
    "trade_tariff": r"tariff|Section 232|KORUS|trade agreement",
    "ira_energy": r"Inflation Reduction Act|45X|30D|clean (energy|vehicle)|battery|solar",
}


def get(url, tries=8):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "us-legislature-research/1.0"})
    if KEY:
        req.add_header("Authorization", f"Token {KEY}")
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as err:
            if err.code == 429:
                wait = int(err.headers.get("Retry-After", "60"))
                print(f"  429 throttled, waiting {wait}s", flush=True)
                time.sleep(wait + 1)
                continue
            if err.code >= 500 and i < tries - 1:
                time.sleep(15 * (i + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if i < tries - 1:
                time.sleep(15 * (i + 1))
                continue
            raise
    raise RuntimeError(f"gave up: {url}")


def pages(endpoint, params):
    url = API + endpoint + "?" + urllib.parse.urlencode(dict(params, page_size=25))
    n = 0
    while url:
        data = get(url)
        for item in data.get("results", []):
            n += 1
            yield item
        print(f"  {n}/{data.get('count')} {endpoint} {params}", flush=True)
        url = data.get("next")
        time.sleep(PAUSE)


def lobbyists_of(act):
    out = []
    for lb in act.get("lobbyists") or []:
        p = lb.get("lobbyist") or {}
        name = " ".join(x for x in (p.get("first_name"), p.get("last_name")) if x)
        cp = re.sub(r"\s+", " ", (lb.get("covered_position") or "")).strip()
        out.append((name, cp, "Y" if lb.get("new") else ""))
    return out


def is_korean(f):
    cl = f.get("client") or {}
    if cl.get("country") == "KR" or any((x.get("country") == "KR") for x in f.get("foreign_entities") or []):
        return True
    return bool(KOREAN_NAME.search(cl.get("name") or ""))


def flatten(f, labels):
    acts = f.get("lobbying_activities") or []
    text = " ".join((a.get("description") or "") for a in acts)
    lob = {}
    for a in acts:
        for name, cp, new in lobbyists_of(a):
            if name and name not in lob:
                lob[name] = cp
    ents = sorted({g.get("name", "") for a in acts for g in (a.get("government_entities") or [])})
    reg, cl = f.get("registrant") or {}, f.get("client") or {}
    row = {
        "filing_uuid": f.get("filing_uuid"), "filing_year": f.get("filing_year"), "filing_period": f.get("filing_period"),
        "filing_type": f.get("filing_type"), "filing_type_display": f.get("filing_type_display"), "dt_posted": (f.get("dt_posted") or "")[:10],
        "registrant_id": reg.get("id"), "registrant": reg.get("name"), "registrant_description": reg.get("description"),
        "client_id": cl.get("id"), "client": cl.get("name"), "client_description": cl.get("general_description"),
        "client_state": cl.get("state"), "client_country": cl.get("country"),
        "client_self_select": "Y" if cl.get("client_self_select") else "",
        "foreign_entities": "; ".join(f'{x.get("name")} ({x.get("country")}; ownership {x.get("ownership_percentage")})' for x in (f.get("foreign_entities") or [])),
        "affiliated_organizations": "; ".join(f'{x.get("name")} ({x.get("country")})' for x in (f.get("affiliated_organizations") or [])),
        "income": f.get("income"), "expenses": f.get("expenses"), "expenses_method": f.get("expenses_method_display") or f.get("expenses_method"),
        "termination_date": f.get("termination_date"),
        "issue_codes": "; ".join(sorted({a.get("general_issue_code") or "" for a in acts})),
        "government_entities": "; ".join(ents),
        "lobbyists": "; ".join(n + (f" [{cp}]" if cp else "") for n, cp in lob.items()),
        "n_lobbyists": len(lob), "n_lobbyists_with_covered_position": sum(1 for cp in lob.values() if cp and cp.upper() not in ("N/A", "NONE")),
        "specific_issues": re.sub(r"\s+", " ", text).strip(), "korean_actor": "Y" if is_korean(f) else "",
        "defense_related": "Y" if DEFENSE_TXT.search(text) or any(a.get("general_issue_code") == "DEF" for a in acts) else "",
        "matched_queries": "; ".join(sorted(labels)), "url": f.get("filing_document_url"),
    }
    for k, pat in FLAGS.items():
        row["flag_" + k] = "Y" if re.search(pat, text, re.I) else ""
    return row


def activity_rows(f):
    reg, cl = f.get("registrant") or {}, f.get("client") or {}
    for i, a in enumerate(f.get("lobbying_activities") or [], 1):
        lob = lobbyists_of(a)
        yield {"filing_uuid": f.get("filing_uuid"), "filing_year": f.get("filing_year"), "filing_period": f.get("filing_period"),
               "filing_type": f.get("filing_type"), "registrant": reg.get("name"), "client": cl.get("name"),
               "korean_actor": "Y" if is_korean(f) else "", "activity_no": i, "issue_code": a.get("general_issue_code"),
               "issue_code_display": a.get("general_issue_code_display"),
               "description": re.sub(r"\s+", " ", a.get("description") or "").strip(),
               "government_entities": "; ".join(g.get("name", "") for g in (a.get("government_entities") or [])),
               "foreign_entity_issues": re.sub(r"\s+", " ", a.get("foreign_entity_issues") or "").strip(),
               "lobbyists": "; ".join(n + (f" [{cp}]" if cp else "") + (" (new)" if new else "") for n, cp, new in lob),
               "income": f.get("income"), "expenses": f.get("expenses"), "url": f.get("filing_document_url")}


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        if not rows:
            fh.write("")
            return
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", nargs="+", type=int, default=list(range(2017, 2027)))
    ap.add_argument("--contrib-years", nargs="*", type=int, default=[2023, 2024, 2025, 2026])
    ap.add_argument("--out", default="lda_out")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    print(f"auth: {'API key' if KEY else 'anonymous'}", flush=True)
    raw_path = os.path.join(a.out, "filings_raw.jsonl")
    filings, labels, counts = {}, {}, {}
    with open(raw_path, "w", encoding="utf-8") as raw:
        for label, params in QUERIES:
            for y in a.years:
                print(f"[{label} {y}]", flush=True)
                n = 0
                for f in pages("filings/", dict(params, filing_year=y, ordering="-dt_posted")):
                    n += 1
                    u = f["filing_uuid"]
                    if u not in filings:
                        raw.write(json.dumps(f, ensure_ascii=False) + "\n")
                        raw.flush()
                    filings[u] = f
                    labels.setdefault(u, set()).add(label)
                counts[f"{label} {y}"] = n
    rows = [flatten(f, labels[u]) for u, f in filings.items()]
    rows.sort(key=lambda r: (r["dt_posted"] or ""), reverse=True)
    write_csv(os.path.join(a.out, "filings.csv"), rows)
    write_csv(os.path.join(a.out, "activities.csv"), [r for f in filings.values() for r in activity_rows(f)])

    # LD-203 contributions of registrants that lobby for Korean actors on defense/shipbuilding
    regs = sorted({(r["registrant_id"], r["registrant"]) for r in rows if r["korean_actor"] and r["defense_related"] and r["registrant_id"]})
    contribs = []
    with open(os.path.join(a.out, "contributions_raw.jsonl"), "w", encoding="utf-8") as raw:
        for rid, rname in regs:
            for y in a.contrib_years:
                print(f"[contributions {rname} {y}]", flush=True)
                for c in pages("contributions/", {"registrant_id": rid, "filing_year": y}):
                    raw.write(json.dumps(c, ensure_ascii=False) + "\n")
                    lb = c.get("lobbyist") or {}
                    for it in c.get("contribution_items") or []:
                        contribs.append({
                            "filing_uuid": c.get("filing_uuid"), "filing_year": c.get("filing_year"), "filing_period": c.get("filing_period"),
                            "registrant": (c.get("registrant") or {}).get("name"),
                            "filer_lobbyist": " ".join(x for x in (lb.get("first_name"), lb.get("last_name")) if x),
                            "contribution_type": it.get("contribution_type_display") or it.get("contribution_type"),
                            "contributor": it.get("contributor_name"), "payee": it.get("payee_name"), "honoree": it.get("honoree_name"),
                            "amount": it.get("amount"), "date": it.get("date"), "url": c.get("filing_document_url")})
    write_csv(os.path.join(a.out, "contributions.csv"), contribs)

    kr = [r for r in rows if r["korean_actor"]]
    summary = {"fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "auth": "key" if KEY else "anonymous",
               "years": a.years, "contrib_years": a.contrib_years, "queries": [q[0] for q in QUERIES], "query_counts": counts,
               "filings": len(rows), "korean_actor_filings": len(kr), "korean_defense_filings": sum(1 for r in kr if r["defense_related"]),
               "contribution_registrants": [r[1] for r in regs], "contribution_items": len(contribs),
               "flag_counts": {k: sum(1 for r in rows if r["flag_" + k]) for k in FLAGS}}
    with open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k != "query_counts"}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    sys.exit(main())
