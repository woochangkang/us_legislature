#!/usr/bin/env python3
"""Moolenaar LD203 lookup across all registrants that disclosed Coupang as client.
All years; not an attribution of firms' donations to a specific client.
"""
import json,time,urllib.parse
from pathlib import Path
from collect_coupang_lda import API,fetch,dump,PAUSE,csvout
out=Path('lda_letter_actors');out.mkdir(exist_ok=True);log=[]
def pages(ep,params,label):
 url=API+ep+'/?'+urllib.parse.urlencode(dict(params,page_size=25));rows=[];i=0
 while url:
  i+=1;b,_=fetch(url,True);d=json.loads(b);dump(out/'raw'/f'{label}_{i}.json',d)
  log.append({'url':url,'count':d['count'],'rows':len(d['results'])});rows+=d['results'];url=d['next'];time.sleep(PAUSE)
 print(label,len(rows),flush=True);return rows
filings=pages('filings',{'client_name':'Coupang'},'coupang')
regs={f['registrant']['id']:f['registrant']['name'] for f in filings}
roster={}
for f in filings:
 for a in f.get('lobbying_activities') or []:
  for l in a.get('lobbyists') or []:
   p=l['lobbyist'];roster.setdefault(p['id'],[]).append({'year':f['filing_year'],'period':f['filing_period'],'posted':f['dt_posted'],'source':f['filing_document_url']})
reports={}
for target in ['Jordan','Rubio','Hegseth','Lutnick','Greer','Thornberry']:
 for rid,name in regs.items():
  for field in ['contribution_honoree','contribution_payee']:
   for r in pages('contributions',{'registrant_id':rid,field:target},str(rid)+'_'+target+'_'+field):
    assert r['registrant']['id']==rid
    reports[r['filing_uuid']]=r
# Fetch every report of matched filers to resolve amendments even if a match was removed.
for rid,lid in sorted({(r['registrant']['id'],(r.get('lobbyist') or {}).get('id')) for r in reports.values()},key=str):
 if lid in roster:
  for r in pages('contributions',{'registrant_id':rid,'lobbyist_id':lid},str(rid)+'_filer_'+str(lid)):
   reports[r['filing_uuid']]=r
best={}
for r in reports.values():
 k=(r['registrant']['id'],(r.get('lobbyist') or {}).get('id'),r['filing_year'],r['filing_period'])
 if k not in best or str(r['dt_posted'])>str(best[k]['dt_posted']):best[k]=r
selected={r['filing_uuid'] for r in best.values()};rows=[]
for uid,r in reports.items():
 for it in r.get('contribution_items') or []:
  if not any(n in json.dumps(it).lower() for n in ['jordan','rubio','hegseth','lutnick','greer','thornberry']):continue
  lb=r.get('lobbyist') or {};name=' '.join(str(lb.get(k) or '') for k in ['first_name','middle_name','last_name']).strip()
  rows.append(dict(target_match=';'.join(n for n in ['Jordan','Rubio','Hegseth','Lutnick','Greer','Thornberry'] if n.lower() in json.dumps(it).lower()),filing_uuid=uid,registrant=r['registrant']['name'],filer=name,lobbyist_id=lb.get('id'),coupang_named_lobbyist=lb.get('id') in roster,year=r['filing_year'],period=r['filing_period'],posted=r['dt_posted'],selected_latest=uid in selected,contributor=it.get('contributor_name'),payee=it.get('payee_name'),honoree=it.get('honoree_name'),amount=it.get('amount'),date=it.get('date'),source=r['filing_document_url']))
 if uid in selected and any(x['filing_uuid']==uid and x['coupang_named_lobbyist'] for x in rows):
  b,_=fetch(r['filing_document_url']);(out/'raw'/f'{uid}.html').write_bytes(b)
dump(out/'reports.json',list(reports.values()));dump(out/'roster.json',roster);dump(out/'query_log.json',log)
csvout(out/'matches.csv',rows,list(rows[0]) if rows else ['filing_uuid'])
print('Match rows',len(rows),'Latest named lobbyist rows',sum(x['selected_latest'] and x['coupang_named_lobbyist'] for x in rows))
