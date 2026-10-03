#!/usr/bin/env python3
"""LDA census: every LD-1/LD-2 filing whose specific-issue text mentions AUKUS-related
submarine legislation, filing years 2022-2024.

lda.gov blocks this Mac's network at the edge (HTTP 403 before auth), so run it
from a US network (e.g. with a US VPN on):

    /usr/bin/python3 lda_census.py

Reads the API key from ../../.env.md ("REST API Key: ...") and never prints it.
Writes into lda_census/: raw_<term>_<year>.json (all pages) and filings.csv
(one row per filing x matching activity).
"""
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "lda_census"
ENV = HERE.parent.parent / ".env.md"
API = "https://lda.gov/api/v1/filings/"
YEARS = [2022, 2023, 2024]
# term sent to the API -> regex a matching activity description must contain.
# Per the API's "Advanced Text Searching" rules, unquoted words are OR-ed, so phrases are quoted.
TERMS = {
    "AUKUS": r"AUKUS",
    "4619": r"H\.?\s?R\.?\s?4619",
    "3939": r"H\.?\s?R\.?\s?3939",
    "TORPEDO": r"TORPEDO",
    '"Virginia Class"': r"Virginia[- ]Class.*Australia|Australia.*Virginia[- ]Class",
}


def api_key():
    m = re.search(r"REST API Key:\s*([0-9a-f]+)", ENV.read_text(encoding="utf-8"))
    if not m:
        sys.exit(f"API key not found in {ENV}")
    return m.group(1)


def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": f"Token {key}", "Accept": "application/json"})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", 30)))
                continue
            if e.code == 403:
                sys.exit("HTTP 403 from lda.gov — this network is still blocked. Turn on a US VPN and rerun.")
            raise
    sys.exit("gave up after repeated HTTP 429")


def main():
    key = api_key()
    OUT.mkdir(exist_ok=True)
    rows, counts = {}, []
    for term, pattern in TERMS.items():
        for year in YEARS:
            url = API + "?" + urllib.parse.urlencode(
                {"filing_specific_lobbying_issues": term, "filing_year": year, "page_size": 25})
            pages = []
            while url:
                page = get(url, key)
                pages.append(page)
                url = page.get("next")
                time.sleep(1)
            slug = re.sub(r"\W+", "_", term).strip("_")
            (OUT / f"raw_{slug}_{year}.json").write_text(
                json.dumps(pages, ensure_ascii=False, indent=1), encoding="utf-8")
            kept = 0
            for page in pages:
                for f in page.get("results", []):
                    for act in f.get("lobbying_activities") or []:
                        desc = act.get("description") or ""
                        if not re.search(pattern, desc, re.I | re.S):
                            continue
                        k = (f["filing_uuid"], desc)
                        row = rows.setdefault(k, {
                            "filing_uuid": f["filing_uuid"],
                            "filing_type": f.get("filing_type"),
                            "filing_year": f.get("filing_year"),
                            "filing_period": f.get("filing_period"),
                            "dt_posted": f.get("dt_posted"),
                            "registrant": (f.get("registrant") or {}).get("name"),
                            "client": (f.get("client") or {}).get("name"),
                            "income": f.get("income"),
                            "expenses": f.get("expenses"),
                            "general_issue_code": act.get("general_issue_code"),
                            "government_entities": "; ".join(g.get("name", "") for g in act.get("government_entities") or []),
                            "lobbyists": "; ".join(
                                " ".join(filter(None, [(l.get("lobbyist") or {}).get("first_name"),
                                                       (l.get("lobbyist") or {}).get("last_name")]))
                                for l in act.get("lobbyists") or []),
                            "matched_terms": set(),
                            "description": desc,
                            "filing_document_url": f.get("filing_document_url"),
                        })
                        row["matched_terms"].add(term)
                        kept += 1
            counts.append((term, year, pages[0].get("count") if pages else 0, kept))
            print(f"{term!r} {year}: API count {counts[-1][2]}, matching activities kept {kept}")
    with (OUT / "filings.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = list(next(iter(rows.values())).keys()) if rows else ["filing_uuid"]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows.values():
            w.writerow({**r, "matched_terms": ";".join(sorted(r["matched_terms"]))})
    with (OUT / "counts.csv").open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows([("term", "year", "api_count", "kept_activities"), *counts])
    print(f"done: {len({k[0] for k in rows})} distinct filings, {len(rows)} filing-activity rows -> {OUT}")


if __name__ == "__main__":
    main()
