#!/usr/bin/env python3
"""Follow-up to lda_census.py: for the registrants and lobbyists that appear on
AUKUS-related LDA filings (lda_census/aukus_relevant.csv), download

  1. LD-203 contribution reports for 2023 and 2024 filed under each registrant
     (registrant-level and each lobbyist's own report) — names payees/honorees
     such as members' campaign committees and events honoring members;
  2. each lobbyist's disclosed covered (former government) positions, from any
     filing that lists one.

lda.gov blocks this Mac's network, so run from a US network:

    /usr/bin/python3 lda_ld203.py

Reads the API key from ../../.env.md and never prints it. Writes raw JSON into
lda_ld203/; matching against members is done afterwards.
"""
import csv
import glob
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CENSUS = HERE / "lda_census"
OUT = HERE / "lda_ld203"
ENV = HERE.parent.parent / ".env.md"
API = "https://lda.gov/api/v1/"
YEARS = [2023, 2024]


def api_key():
    m = re.search(r"REST API Key:\s*([0-9a-f]+)", ENV.read_text(encoding="utf-8"))
    if not m:
        sys.exit(f"API key not found in {ENV}")
    return m.group(1)


def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": f"Token {key}", "Accept": "application/json"})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", 30)))
                continue
            if e.code == 403:
                sys.exit("HTTP 403 from lda.gov — this network is blocked. Use a US network and rerun.")
            if e.code >= 500:
                time.sleep(10 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as e:
            # dropped connection / reset by peer / timeout: back off and retry
            print(f"  network error ({e.__class__.__name__}), retry {attempt + 1}/8")
            time.sleep(10 * (attempt + 1))
    sys.exit("gave up after repeated errors — rerun later; finished files are kept and skipped")


def all_pages(endpoint, params, key, max_pages=None):
    url = API + endpoint + "?" + urllib.parse.urlencode({**params, "page_size": 25})
    pages = []
    while url and (max_pages is None or len(pages) < max_pages):
        pages.append(get(url, key))
        url = pages[-1].get("next")
        time.sleep(0.6)
    return pages


def targets():
    """Registrant ids and lobbyist ids on the AUKUS-relevant activities."""
    rel = {r["filing_uuid"] for r in csv.DictReader(open(CENSUS / "aukus_relevant.csv", encoding="utf-8"))}
    raw = {}
    for f in glob.glob(str(CENSUS / "raw_*.json")):
        for page in json.load(open(f)):
            for r in page.get("results", []):
                raw[r["filing_uuid"]] = r
    regs, lobs = {}, {}
    for u in rel:
        f = raw[u]
        regs[f["registrant"]["id"]] = f["registrant"]["name"]
        for a in f["lobbying_activities"]:
            d = a.get("description") or ""
            if not (re.search("AUKUS", d) or re.search(r"S\.?\s?1471|TORPEDO\)? Act", d)
                    or (re.search("Virginia", d) and "Australia" in d)):
                continue
            for l in a.get("lobbyists") or []:
                lb = l["lobbyist"]
                lobs[lb["id"]] = {"name": " ".join(filter(None, [lb.get("first_name"), lb.get("last_name")])),
                                  "registrant": f["registrant"]["name"]}
    return regs, lobs


def main():
    key = api_key()
    OUT.mkdir(exist_ok=True)
    regs, lobs = targets()
    (OUT / "targets.json").write_text(json.dumps({"registrants": regs, "lobbyists": lobs}, indent=1), encoding="utf-8")
    print(f"{len(regs)} registrants, {len(lobs)} lobbyists")

    for rid, name in regs.items():
        for year in YEARS:
            path = OUT / f"contrib_{rid}_{year}.json"
            if path.exists():  # resume: already downloaded in an earlier run
                continue
            pages = all_pages("contributions/", {"registrant_id": rid, "filing_year": year}, key)
            path.write_text(json.dumps(pages, indent=1), encoding="utf-8")
            n = sum(len(p.get("results", [])) for p in pages)
            print(f"LD-203 {name[:40]} {year}: {n} reports")

    for lid, info in lobs.items():
        path = OUT / f"lobbyist_{lid}.json"
        if path.exists():
            continue
        pages = all_pages("filings/", {"lobbyist_id": lid, "lobbyist_covered_position_indicator": "true"}, key, max_pages=2)
        path.write_text(json.dumps(pages, indent=1), encoding="utf-8")
        positions = set()
        for p in pages:
            for f in p.get("results", []):
                for a in f.get("lobbying_activities") or []:
                    for l in a.get("lobbyists") or []:
                        if l["lobbyist"]["id"] == lid and (l.get("covered_position") or "").strip():
                            positions.add(l["covered_position"].strip())
        print(f"lobbyist {info['name']}: {len(positions)} covered-position text(s)")
    print(f"done -> {OUT}")


if __name__ == "__main__":
    main()
