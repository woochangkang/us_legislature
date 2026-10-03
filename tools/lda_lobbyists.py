#!/usr/bin/env python3
"""Look up LDA lobbyists by id: earliest filings and every disclosed covered (former government) position.

Covered positions are usually written only on a lobbyist's first filing for a registrant ("See prior filing" later),
so this reads each lobbyist's earliest filings. Run from a U.S. network (see lda-fetch.yml). Standard library only.
Usage: python3 tools/lda_lobbyists.py --ids 48014 51704 ... --out lda_lobbyists_out
"""
import argparse
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from lda_fetch import get, API, PAUSE  # noqa: E402
import time  # noqa: E402
import urllib.parse  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="+", type=int, required=True)
    ap.add_argument("--pages", type=int, default=2, help="earliest pages (25 filings each) to scan per lobbyist")
    ap.add_argument("--out", default="lda_lobbyists_out")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for lid in a.ids:
        url = API + "filings/?" + urllib.parse.urlencode({"lobbyist_id": lid, "ordering": "dt_posted", "page_size": 25})
        name, covered, regs, clients, first, count = "", [], set(), set(), "", 0
        for _ in range(a.pages):
            if not url:
                break
            d = get(url)
            count = d.get("count") or count
            for f in d.get("results", []):
                first = first or (f.get("dt_posted") or "")[:10]
                for act in f.get("lobbying_activities") or []:
                    for lb in act.get("lobbyists") or []:
                        p = lb.get("lobbyist") or {}
                        if p.get("id") != lid:
                            continue
                        name = name or " ".join(x for x in (p.get("first_name"), p.get("last_name")) if x)
                        regs.add((f.get("registrant") or {}).get("name", ""))
                        clients.add((f.get("client") or {}).get("name", ""))
                        cp = re.sub(r"\s+", " ", lb.get("covered_position") or "").strip()
                        if cp and cp.upper() not in ("N/A", "NONE", "NA") and not re.match(r"see prior", cp, re.I) and cp not in covered:
                            covered.append(cp)
            url = d.get("next")
            time.sleep(PAUSE)
        print(f"{lid} {name}: {len(covered)} covered; {count} filings", flush=True)
        rows.append({"lobbyist_id": lid, "name": name, "total_filings": count, "first_filing_posted": first,
                     "covered_positions": " | ".join(covered), "registrants_seen": "; ".join(sorted(regs)),
                     "clients_seen_in_earliest_filings": "; ".join(sorted(clients))[:600]})
    with open(os.path.join(a.out, "lobbyists_detail.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
