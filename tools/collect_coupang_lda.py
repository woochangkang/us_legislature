#!/usr/bin/env python3
"""Collect official Coupang LD-1/LD-2 and Coupang-registrant LD-203, preserving raw pages.
Standard library only. Adapted from NDAA tools/lda_fetch.py workflow structure.
Usage: python3 collect_coupang_lda.py --out lda_coupang
Optional LDA_API_KEY environment variable; never printed or written to files.
"""
import argparse, csv, datetime, hashlib, json, os, re, time
import urllib.request, urllib.parse, urllib.error
from pathlib import Path

API='https://lda.gov/api/v1/'
KEY=os.environ.get('LDA_API_KEY','').strip()
PAUSE=0.65 if KEY else 4.3

def dump(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

def fetch(url, api=False):
    if urllib.parse.urlparse(url).hostname not in {'lda.gov','lda.senate.gov'}:
        raise ValueError('Unexpected source host')
    headers={'User-Agent':'coupang-lda-research/1.0','Accept':'application/json' if api else '*/*'}
    if api and KEY: headers['Authorization']='Token '+KEY
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=60) as r:
                return r.read(),r.headers.get('Content-Type','')
        except urllib.error.HTTPError as e:
            if e.code==429:
                time.sleep(int(e.headers.get('Retry-After','60'))+1)
            elif e.code>=500 and attempt<4: time.sleep(5*(attempt+1))
            else: raise
        except (urllib.error.URLError,TimeoutError):
            if attempt==4: raise
            time.sleep(5*(attempt+1))
    raise RuntimeError('Repeated request failures')

def csvout(path,rows,fields):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='lda_coupang');ap.add_argument('--no-documents',action='store_true');a=ap.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    for d in ['raw/api','raw/documents','data']: (out/d).mkdir(parents=True,exist_ok=True)
    log=[];errors=[];filings={};labels={};contrib={}
    def pages(endpoint,params,label):
        url=API+endpoint+'/?'+urllib.parse.urlencode(dict(params,page_size=25));result=[];n=0;expected=None
        while url:
            n+=1;cache=out/'raw/api'/f'{label}_p{n:03d}.json'
            if cache.exists(): obj=json.loads(cache.read_text())
            else:
                body,_=fetch(url,True);obj=json.loads(body);dump(cache,obj);time.sleep(PAUSE)
            expected=obj.get('count') if expected is None else expected
            result.extend(obj.get('results',[]))
            log.append({'query':label,'url':url,'page':n,'count':obj.get('count'),'rows':len(obj.get('results',[])),'cache':str(cache.relative_to(out))})
            url=obj.get('next')
        if expected is not None and len(result)!=expected: errors.append({'query':label,'error':'pagination_count_mismatch','expected':expected,'actual':len(result)})
        print(label,len(result),flush=True)
        return result
    for label,params in [('client_coupang',{'client_name':'Coupang'}),('registrant_coupang',{'registrant_name':'Coupang'}),('issues_coupang',{'filing_specific_lobbying_issues':'Coupang'})]:
        for f in pages('filings',params,label):
            uid=f['filing_uuid'];filings[uid]=f;labels.setdefault(uid,set()).add(label)
    for f in pages('contributions',{'registrant_name':'Coupang'},'ld203_coupang_all_years'):
        contrib[f['filing_uuid']]=f
    dump(out/'raw/filings_raw.json',list(filings.values()));dump(out/'raw/contributions_raw.json',list(contrib.values()))
    dump(out/'query_log.json',log)
    def name(p): return ' '.join(str(p.get(k) or '').strip() for k in ['first_name','middle_name','last_name','suffix'] if p.get(k))
    frows=[];arows=[];lrows=[];grows=[]
    for uid,f in filings.items():
        reg=f.get('registrant') or {};cl=f.get('client') or {};direct='coupang' in cl.get('name','').lower()
        base={'filing_uuid':uid,'filing_year':f.get('filing_year'),'filing_period':f.get('filing_period'),'filing_type':f.get('filing_type'),'filing_type_display':f.get('filing_type_display'),'dt_posted':f.get('dt_posted'),'registrant_id':reg.get('id'),'registrant':reg.get('name'),'client_id':cl.get('id'),'client':cl.get('name'),'scope':'direct_client' if direct else 'issue_mention_or_registrant','source_url':f.get('filing_document_url')}
        descriptions=' '.join(x.get('description') or '' for x in f.get('lobbying_activities') or [])
        frows.append(dict(base,income=f.get('income'),expenses=f.get('expenses'),expenses_method=f.get('expenses_method_display') or f.get('expenses_method'),termination_date=f.get('termination_date'),matched_queries=';'.join(sorted(labels[uid])),specific_issues=descriptions,flag_ndaa=bool(re.search(r'\bNDAA\b|National Defense Authorization',descriptions,re.I))))
        for i,act in enumerate(f.get('lobbying_activities') or [],1):
            ab=dict(base,activity_no=i,issue_code=act.get('general_issue_code'),issue_code_display=act.get('general_issue_code_display'),description=act.get('description'),foreign_entity_issues=act.get('foreign_entity_issues'))
            arows.append(ab)
            for g in act.get('government_entities') or []: grows.append(dict(ab,government_entity_id=g.get('id'),government_entity=g.get('name')))
            for l in act.get('lobbyists') or []:
                p=l.get('lobbyist') or {};lrows.append(dict(ab,lobbyist_id=p.get('id'),lobbyist=name(p),covered_position=l.get('covered_position'),new=l.get('new')))
    # Registration forms never supersede quarterly reports. Preserve amendments in raw/all tables.
    best={}
    for r in frows:
        if r['filing_period'] not in {'first_quarter','second_quarter','third_quarter','fourth_quarter'}: continue
        if 'registration' in (r['filing_type_display'] or '').lower(): continue
        k=(r['registrant_id'],r['client_id'],r['filing_year'],r['filing_period'])
        if k not in best or str(r['dt_posted'])>str(best[k]['dt_posted']): best[k]=r
    selected={r['filing_uuid'] for r in best.values()}
    for r in frows:r['selected_latest_quarterly']=r['filing_uuid'] in selected
    crows=[];cr=[]
    for uid,c in contrib.items():
        lb=c.get('lobbyist') or {};reg=c.get('registrant') or {}
        base={'filing_uuid':uid,'filing_year':c.get('filing_year'),'filing_period':c.get('filing_period'),'filing_type':c.get('filing_type'),'filing_type_display':c.get('filing_type_display'),'dt_posted':c.get('dt_posted'),'registrant_id':reg.get('id'),'registrant':reg.get('name'),'lobbyist_id':lb.get('id'),'filer_lobbyist':name(lb),'source_url':c.get('filing_document_url')}
        cr.append(dict(base,filer_type=c.get('filer_type_display') or c.get('filer_type'),no_contributions=c.get('no_contributions'),pacs=json.dumps(c.get('pacs') or [],ensure_ascii=False),contribution_items=len(c.get('contribution_items') or [])))
        for i,it in enumerate(c.get('contribution_items') or [],1):
            crows.append(dict(base,item_no=i,contribution_type=it.get('contribution_type_display') or it.get('contribution_type'),contributor=it.get('contributor_name'),payee=it.get('payee_name'),honoree=it.get('honoree_name'),amount=it.get('amount'),date=it.get('date'),attribution='Registrant or individual filer disclosure; not evidence of a payment for Coupang lobbying'))
    cbest={}
    for r in cr:
        k=(r['registrant_id'],r['lobbyist_id'],r['filing_year'],r['filing_period'])
        if k not in cbest or str(r['dt_posted'])>str(cbest[k]['dt_posted']): cbest[k]=r
    cselected={r['filing_uuid'] for r in cbest.values()}
    for r in cr+crows:r['selected_latest_report']=r['filing_uuid'] in cselected
    for rs in [arows,lrows,grows]:
        for r in rs:r['selected_latest_quarterly']=r['filing_uuid'] in selected
    tables={'filings_all':frows,'filings_latest_quarterly':list(best.values()),'activities':arows,'lobbyists':lrows,'government_entities':grows,'contribution_reports':cr,'contribution_items':crows}
    for label,rs in tables.items(): csvout(out/'data'/f'{label}.csv',rs,list(rs[0]) if rs else ['filing_uuid'])
    manifest=[]
    if not a.no_documents:
        for kind,objects in [('filing',filings),('contribution',contrib)]:
            for uid,f in objects.items():
                url=f.get('filing_document_url') or f'https://lda.gov/filings/public/{kind}/{uid}/print/'
                url=url.replace('https://lda.senate.gov/','https://lda.gov/')
                try:
                    existing=list((out/'raw/documents').glob(f'{kind}_{uid}.*'))
                    if existing: path=existing[0];body=path.read_bytes();ctype='cached'
                    else:
                        body,ctype=fetch(url);ext='.pdf' if body.startswith(b'%PDF') else '.html'
                        if b'Access Denied' in body[:2000]:raise ValueError('Access denied response, not a filing')
                        if ext=='.html' and uid.encode() not in body and b'Lobbying' not in body and b'Contribution' not in body:raise ValueError('Unrecognized document body')
                        path=out/'raw/documents'/f'{kind}_{uid}{ext}';path.write_bytes(body)
                    if (len(manifest)+1)%20==0: print('Documents saved',len(manifest)+1,flush=True)
                    manifest.append({'kind':kind,'filing_uuid':uid,'url':url,'path':str(path.relative_to(out)),'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'content_type':ctype})
                except Exception as e:errors.append({'kind':kind,'filing_uuid':uid,'url':url,'error':type(e).__name__+': '+str(e)})
    csvout(out/'document_manifest.csv',manifest,['kind','filing_uuid','url','path','bytes','sha256','content_type'])
    summary={'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'years':sorted({f['filing_year'] for f in list(filings.values())+list(contrib.values())}),'year_filter':'none','api':'https://lda.gov/api/v1/','auth':'api_key' if KEY else 'anonymous','filings':len(frows),'direct_client_filings':sum(r['scope']=='direct_client' for r in frows),'latest_quarterly_filings':len(best),'activity_rows':len(arows),'lobbyist_rows':len(lrows),'government_entity_rows':len(grows),'ld203_reports':len(cr),'ld203_items':len(crows),'documents_saved':len(manifest),'errors':errors,'ld203_scope':'Reports with registrant_name=Coupang, including named individual filers. External firms and their other clients are not attributed to Coupang.','money_rule':'Do not add external firm income to Coupang in-house expenses. Do not sum repeated activity rows. Null is not zero.'}
    dump(out/'summary.json',summary);print(json.dumps(summary,ensure_ascii=False),flush=True)
    if errors:raise SystemExit(2)

if __name__=='__main__':main()
