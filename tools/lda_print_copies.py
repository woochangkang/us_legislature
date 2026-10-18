#!/usr/bin/env python3
"""Fetch LDA print pages (and API JSON) for given filing IDs from a U.S. runner.
lda.gov's Akamai edge blocks some non-U.S. networks, so readers there cannot open the originals.
Usage: lda_print_copies.py --ids "filing:<uuid> contribution:<uuid> ..." --out DIR"""
import argparse, hashlib, json, os, time, urllib.request, urllib.error, datetime
p = argparse.ArgumentParser(); p.add_argument('--ids', required=True); p.add_argument('--out', required=True); a = p.parse_args()
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36', 'Accept': 'text/html,application/json'}
API = {'filing': 'filings', 'contribution': 'contributions'}
def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r: return r.status, r.read()
        except urllib.error.HTTPError as e:
            print('  ', e.code, url, flush=True)
            if e.code in (429, 500, 502, 503, 504): time.sleep(15 * (i + 1)); continue
            return e.code, e.read()
        except Exception as e:
            print('  ', type(e).__name__, e, url, flush=True); time.sleep(5 * (i + 1))
    return 0, b''
man = []
for tok in a.ids.split():
    kind, uid = tok.split(':', 1); d = os.path.join(a.out, kind); os.makedirs(d, exist_ok=True)
    url = f'https://lda.gov/filings/public/{kind}/{uid}/print/'
    s1, html = get(url); time.sleep(0.5)
    s2, js = get(f'https://lda.gov/api/v1/{API[kind]}/{uid}/'); time.sleep(4.2)   # anonymous API: 15 requests/min
    ok = s1 == 200 and b'Access Denied' not in html and (b'LD-203' in html or b'LD-2' in html or b'LD-1' in html)
    if s1 == 200: open(os.path.join(d, uid + '.html'), 'wb').write(html)
    if s2 == 200: open(os.path.join(d, uid + '.json'), 'wb').write(js)
    man.append(dict(kind=kind, uuid=uid, url=url, print_status=s1, api_status=s2, valid=ok, bytes=len(html),
                    sha256=hashlib.sha256(html).hexdigest() if s1 == 200 else '', fetched_utc=datetime.datetime.utcnow().isoformat() + 'Z'))
    print(kind, uid, s1, s2, 'ok' if ok else 'CHECK', flush=True)
json.dump(man, open(os.path.join(a.out, 'manifest.json'), 'w'), indent=1)
print('valid', sum(m['valid'] for m in man), 'of', len(man))
