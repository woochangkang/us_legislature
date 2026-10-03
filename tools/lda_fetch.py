#!/usr/bin/env python3
"""Fetch Senate LDA lobbying filings related to South Korea (run from a U.S. network, e.g. GitHub Actions).

lda.gov's Akamai edge refuses requests from some networks (observed from Korea: HTTP 403 `$(SERVE_403)`),
so this runs in .github/workflows/lda-fetch.yml. Standard library only.

Usage: python3 tools/lda_fetch.py --years 2025 2026 --out lda_out
Env:   LDA_API_KEY (optional; anonymous = 15 req/min, key = 120 req/min)
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

BASE = "https://lda.gov/api/v1/filings/"
KEY = os.environ.get("LDA_API_KEY", "").strip()
PAUSE = 0.6 if KEY else 4.2  # stay under 120/min or 15/min

# (label, query params) — results are unioned by filing_uuid
QUERIES = [
    ("foreign_entity_KR", {"foreign_entity_country": "KR"}),
    ("client_KR", {"client_country": "KR"}),
    ("text_Korea", {"filing_specific_lobbying_issues": "Korea"}),
    ("text_Hanwha", {"filing_specific_lobbying_issues": "Hanwha"}),
    ("text_Hyundai", {"filing_specific_lobbying_issues": "Hyundai"}),
    ("text_Samsung", {"filing_specific_lobbying_issues": "Samsung"}),
    ("client_Hanwha", {"client_name": "Hanwha"}),
    ("client_Hyundai", {"client_name": "Hyundai"}),
    ("client_Samsung", {"client_name": "Samsung"}),
]
FLAGS = {
    "korea": r"\bKorea|\bROK\b|Republic of Korea",
    "ndaa": r"National Defense Authorization|\bNDAA\b",
    "hr8800": r"H\.?\s?R\.?\s?8800\b",
    "s4784": r"\bS\.?\s?4784\b",
    "shipbuilding": r"shipbuild|shipyard|naval vessel|ship repair|\bMRO\b|maintenance, repair|SHIPS for America|MASGA",
    "usfk": r"USFK|Forces Korea|troop|force posture",
}


def get(url, tries=6):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "us-legislature-research/1.0"})
    if KEY:
        req.add_header("Authorization", f"Token {KEY}")
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as err:
            if err.code == 429:
                wait = int(err.headers.get("Retry-After", "60"))
                print(f"  429 throttled, waiting {wait}s", flush=True)
                time.sleep(wait + 1)
                continue
            if err.code >= 500 and i < tries - 1:
                time.sleep(10 * (i + 1))
                continue
            raise
    raise RuntimeError(f"gave up: {url}")


def fetch(params, year):
    q = dict(params, filing_year=year, ordering="-dt_posted")
    url = BASE + "?" + urllib.parse.urlencode(q)
    out = []
    while url:
        data = get(url)
        out.extend(data.get("results", []))
        print(f"  {len(out)}/{data.get('count')} {q}", flush=True)
        url = data.get("next")
        time.sleep(PAUSE)
    return out


def flatten(f, labels):
    acts = f.get("lobbying_activities") or []
    text = " ".join((a.get("description") or "") for a in acts)
    lobbyists = []
    for a in acts:
        for lb in a.get("lobbyists") or []:
            p = lb.get("lobbyist") or {}
            name = " ".join(x for x in (p.get("first_name"), p.get("last_name")) if x)
            cp = (lb.get("covered_position") or "").strip()
            entry = name + (f" [{cp}]" if cp else "")
            if entry and entry not in lobbyists:
                lobbyists.append(entry)
    ents = sorted({g.get("name", "") for a in acts for g in (a.get("government_entities") or [])})
    reg, cl = f.get("registrant") or {}, f.get("client") or {}
    fe = "; ".join(f'{x.get("name")} ({x.get("country")})' for x in (f.get("foreign_entities") or []))
    row = {
        "filing_uuid": f.get("filing_uuid"), "filing_year": f.get("filing_year"), "filing_period": f.get("filing_period"),
        "filing_type": f.get("filing_type_display") or f.get("filing_type"), "dt_posted": (f.get("dt_posted") or "")[:10],
        "registrant": reg.get("name"), "client": cl.get("name"), "client_country": cl.get("country"),
        "foreign_entities": fe, "income": f.get("income"), "expenses": f.get("expenses"),
        "issue_codes": "; ".join(sorted({a.get("general_issue_code") or "" for a in acts})),
        "government_entities": "; ".join(ents), "lobbyists": "; ".join(lobbyists),
        "specific_issues": re.sub(r"\s+", " ", text).strip(), "matched_queries": "; ".join(sorted(labels)),
        "url": f.get("filing_document_url"),
    }
    for k, pat in FLAGS.items():
        row["flag_" + k] = "Y" if re.search(pat, text, re.I) else ""
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", nargs="+", type=int, default=[2025, 2026])
    ap.add_argument("--out", default="lda_out")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    print(f"auth: {'API key' if KEY else 'anonymous'}", flush=True)
    filings, labels = {}, {}
    for label, params in QUERIES:
        for y in a.years:
            print(f"[{label} {y}]", flush=True)
            for f in fetch(params, y):
                u = f["filing_uuid"]
                filings[u] = f
                labels.setdefault(u, set()).add(label)
    with open(os.path.join(a.out, "filings_raw.json"), "w", encoding="utf-8") as fh:
        json.dump(list(filings.values()), fh, ensure_ascii=False)
    rows = [flatten(f, labels[u]) for u, f in filings.items()]
    rows.sort(key=lambda r: (r["dt_posted"] or ""), reverse=True)
    with open(os.path.join(a.out, "filings.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["filing_uuid"])
        w.writeheader()
        w.writerows(rows)
    summary = {"fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "auth": "key" if KEY else "anonymous",
               "years": a.years, "queries": [q[0] for q in QUERIES], "filings": len(rows),
               "flag_counts": {k: sum(1 for r in rows if r["flag_" + k]) for k in FLAGS}}
    with open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    sys.exit(main())
