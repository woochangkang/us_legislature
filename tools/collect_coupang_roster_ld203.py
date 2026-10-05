#!/usr/bin/env python3
"""All LD203 reports for Coupang registrants and individually disclosed lobbyists.
Client association is a roster join, never an attribution of personal donations.
"""
import json,time,urllib.parse
from pathlib import Path
from collect_coupang_lda import API,fetch,dump,PAUSE
out=Path('lda_roster');out.mkdir(exist_ok=True);log=[]
def pages(ep,params,label,validator=None):
 url=API+ep+'/?'+urllib.parse.urlencode(dict(params,page_size=25));rows=[];i=0;expected=None
 while url:
  i+=1;b,_=fetch(url,True);d=json.loads(b)
  if validator:assert all(validator(x) for x in d['results']),label+' filter mismatch'
  dump(out/'raw'/f'{label}_{i:03d}.json',d);expected=d['count'] if expected is None else expected
  log.append({'query':label,'url':url,'count':d['count'],'rows':len(d['results'])});rows+=d['results'];url=d['next'];time.sleep(PAUSE)
 assert len(rows)==expected
 print(label,len(rows),flush=True);return rows
fs=pages('filings',{'client_name':'Coupang'},'coupang');dump(out/'filings.json',fs)
regs={f['registrant']['id']:f['registrant']['name'] for f in fs};pairs=set()
for f in fs:
 for a in f.get('lobbying_activities') or []:
  for l in a.get('lobbyists') or []:pairs.add((f['registrant']['id'],l['lobbyist']['id']))
rs={}
for rid,lid in sorted(pairs):
 for r in pages('contributions',{'registrant_id':rid,'lobbyist_id':lid},f'individual_{rid}_{lid}',lambda r:r['registrant']['id']==rid and (r.get('lobbyist') or {}).get('id')==lid):rs[r['filing_uuid']]=r
 dump(out/'reports.json',list(rs.values()));dump(out/'query_log.json',log)
for rid in sorted(regs):
 for r in pages('contributions',{'registrant_id':rid,'lobbyist_exclude':'true'},f'registrant_{rid}',lambda r:r['registrant']['id']==rid and not r.get('lobbyist')):rs[r['filing_uuid']]=r
 dump(out/'reports.json',list(rs.values()));dump(out/'query_log.json',log)
dump(out/'summary.json',{'registrants':regs,'lobbyist_registrant_pairs':len(pairs),'reports':len(rs),'pages':len(log),'scope':'All years, nine Coupang registrants, named lobbyist-registrant pairs plus organization-only reports. Not every prior employer, all company employees, or every FEC filing.'})
print('Complete',len(rs),'LD203 reports',len(log),'pages',flush=True)
