# coding: utf-8
from pathlib import Path
import xml.etree.ElementTree as E,json,re,collections,hashlib,csv,fitz
root=Path('ira');out=root/'procedure';b=E.parse(out/'BILLSTATUS-117hr5376.xml').getroot().find('bill')
def j(name,obj): (out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def txt(e,p,default=''):return e.findtext(p,default) or default
record=fitz.open(root/'pdfs/2022-08-06_Congressional_Record_Senate.pdf');record_pages=[p.get_text() for p in record];full='';pagecuts=[]
for i,t in enumerate(record_pages):pagecuts.append((len(full),i+1));full+=t+'\n'
starts=list(re.finditer(r'\bSA (\d{4})\.\s',full));texts={}
for i,m in enumerate(starts):
 num=m.group(1);end=starts[i+1].start() if i+1<len(starts) else len(full)
 page=max(n for pos,n in pagecuts if pos<=m.start());last=max(n for pos,n in pagecuts if pos<end)
 texts[num]=dict(text=full[m.start():end].strip(),page=page,end_page=last)
amend=[];votes={}
def actions(e,path):
 rows=[]
 for a in e.findall(path):
  vs=[]
  for v in a.findall('recordedVotes/recordedVote'):
   key=(txt(v,'chamber'),txt(v,'sessionNumber'),txt(v,'rollNumber'));u=txt(v,'url');t=txt(a,'text');match=re.search(r'(\d+)\s*-\s*(\d+)',t)
   if key not in votes:votes[key]=dict(chamber=key[0],session=key[1],number=key[2],date=txt(a,'actionDate'),url=u,yes=int(match[1]) if match else None,no=int(match[2]) if match else None,description=t,related_amendments=[])
   vs.append('|'.join(key))
  rows.append(dict(date=txt(a,'actionDate'),text=txt(a,'text'),code=txt(a,'actionCode'),votes=vs))
 return rows
billactions=actions(b,'actions/item')
ko={5488:'SALT 공제 한도 연장을 취소하고 비법인 초과사업손실 제한을 연장',5487:'석유·가스 임대 및 에너지 관련 조항 대체',5480:'Title 42에 따른 입국 제한 종료 절차 신설',5472:'법인 최저한세의 소득 합산 기준 변경과 SALT 공제 한도 1년 연장',5469:'슈퍼펀드 세금 부활 삭제',5435:'국토안보부 예산을 남서부 국경 장벽 건설로 전환',5421:'자본이득·이자·물가연동 세제 수정',5418:'석탄 임대 승인 관련 변경',5409:'추가 육상 석유·가스 임대 의무',5404:'소득 40만 달러 미만 납세자에 대한 IRS 추가 예산 사용 제한',5389:'의약품 접근 관련 변경',5387:'외대륙붕 석유·가스 임대 의무',5385:'저·중소득층 인슐린 할인',5384:'Title 42 집행 추가 예산',5383:'에너지·인프라 인허가 절차 변경',5382:'대기청정법 관련 활동 예산 삭제',5316:'주택 에너지 환급 예산을 지방정부 보상금으로 이전',5301:'에너지 관련 증세 조항 삭제 제안',5281:'§§13104–50265 에너지·기후 조항 대체',5265:'전략비축유의 중국 수출 제한 조건',5263:'IRS 추가 예산 약 800억 달러 삭제',5262:'메디케이드 미확대 주 저소득 성인 보장',5211:'메디케어 치과·청력·시력 보장 확대',5210:'메디케어 B·D 처방약 비용 상한',5209:'민간 기후봉사단 신설',5208:'2021년 아동세액공제 특별규칙 연장 및 법인세율 인상',5194:'하원 BBB 본문을 IRA 대체안으로 교체'}
for a in b.find('amendments'):
 n=txt(a,'number');sen=txt(a,'type')=='SAMDT';id=('SA' if sen else 'HA')+n;acts=actions(a,'actions/actions/item');last=txt(a,'latestAction/text');prop=bool(txt(a,'proposedDate')) or not sen
 if 'not agreed to' in last:status='rejected'
 elif 'agreed to' in last.lower():status='agreed'
 elif 'ruled out of order' in last:status='out_of_order'
 else:status='not_proposed' if not prop else 'other'
 sponsor=txt(a,'sponsors/item/fullName',txt(a,'sponsors/item/name'));body=texts.get(n,{}) if sen else {}
 if id=='SA5194':body={'page':20,'text':''}
 if n=='5488':body['text']=body.get('text','').split('PRIVILEGES OF THE FLOOR')[0].rstrip()
 effect={'rejected':'해당 수정안은 부결되어 이 처리 경로로 반영되지 않았다.','out_of_order':'예산규율 면제 동의가 필요한 표를 얻지 못해 의사진행상 배제됐다.','not_proposed':'제출됐으나 본회의 제안·채택 이력이 없다. 이를 부결로 세지 않는다. 비공식 흡수 여부는 이 이력만으로 판단할 수 없다.','agreed':'수정안 채택. 이후 수정·삭제 여부는 별도로 확인해야 한다.'}.get(status,'별도 확인 필요')
 if id=='SA5472':effect='최저한세 소득 합산 기준 변경은 유지됐다. SALT 한도 연장 부분은 뒤이어 채택된 SA5488이 되돌렸다. 따라서 전부 원형대로 반영된 것은 아니다.'
 if id=='SA5488':effect='SA5472의 SALT 한도 연장을 취소하고 비법인 초과사업손실 제한을 2029년 전까지 연장하는 조문을 대체안에 반영했다.'
 if id=='SA5194':effect='추가 수정안과 예산규율에 따른 문구 삭제를 거친 대체안이 구두표결로 채택됐다. 그 후 법안 전체가 51–50으로 통과했다. 초안 전체의 원형 보존을 뜻하지 않는다.'
 if id.startswith('HA'):effect='2021년 하원 BBB에 규칙에 따라 채택된 수정안이다. 2022년 상원 IRA 대체안으로 본문이 교체됐으므로 2021년 채택을 IRA 최종 반영과 동일시하지 않는다.'
 row=dict(id=id,number=int(n),chamber='Senate' if sen else 'House',sponsor=sponsor,party=txt(a,'sponsors/item/party'),state=txt(a,'sponsors/item/state'),submitted=txt(a,'submittedDate')[:10],proposed=txt(a,'proposedDate')[:10],floor_proposed=prop,status=status,purpose=txt(a,'purpose',txt(a,'description')),summary_ko=ko.get(int(n),'규칙위원회 일괄 수정' if not sen else '미상정 제출안 · 원문 확인'),latest_action=last,actions=acts,parent='SA'+txt(a,'amendedAmendment/number') if txt(a,'amendedAmendment/number') else 'HR5376',url=f'https://www.congress.gov/amendment/117th-congress/{"senate" if sen else "house"}-amendment/{n}',effect=effect,record_page=body.get('page'),record_text=body.get('text',''),ev_keyword_hit=bool(re.search(r'electric\s+vehicle|clean\s+vehicle|section\s+30D|section\s+13401',body.get('text',''),re.I)))
 for act in acts:
  for key in act['votes']:
   v=votes[tuple(key.split('|'))]
   if id not in v['related_amendments']:v['related_amendments'].append(id)
 amend.append(row)
# Derive vote categories from the question voted on, never treat waiver votes as adoption.
for v in votes.values():
 t=v['description'].lower()
 v['kind']='예산규율 면제 동의' if 'waive' in t else '위원회 회부 동의' if 'commit' in t else '법안 통과' if 'passed senate' in t or 'on passage' in t else '상원 수정안 동의' if 'house agree' in t else '심의 개시 동의' if 'proceed' in t else '재고 동의 보류' if 'table' in t else '수정안 표결'
 v['result']='부결' if any(w in t for w in ['rejected','not agreed','failed']) else '가결'
 if v['chamber']=='Senate':
  n=int(v['number']);hits=[i+1 for i,t in enumerate(record_pages) if re.search(r'Rollcall Vote No\.\s*'+str(n)+r'\b',t)];v['record_pages']=hits
stats=collections.Counter(x['status'] for x in amend if x['chamber']=='Senate');people=[]
for name in sorted(set(x['sponsor'] for x in amend)):
 rows=[x for x in amend if x['sponsor']==name];c=collections.Counter(x['status'] for x in rows);people.append(dict(sponsor=name,submitted=len(rows),floor_proposed=sum(x['floor_proposed'] for x in rows),agreed=c['agreed'],rejected=c['rejected'],out_of_order=c['out_of_order'],not_proposed=c['not_proposed'],ids=[x['id'] for x in rows]))
assert len(amend)==295;assert sum(x['floor_proposed'] for x in amend if x['chamber']=='Senate')==27;assert stats==dict(agreed=3,rejected=18,out_of_order=6,not_proposed=266);assert len(votes)==43
j('amendments.json',amend);j('sponsors.json',people);j('votes.json',sorted(votes.values(),key=lambda v:(v['date'],v['chamber'],int(v['number']))));j('bill-actions.json',billactions)
for name,rows,keys in [('amendments.csv',amend,['id','sponsor','submitted','proposed','status','purpose','summary_ko','effect','parent','url','record_page']),('sponsors.csv',people,['sponsor','submitted','floor_proposed','agreed','rejected','out_of_order','not_proposed']),('votes.csv',list(votes.values()),['chamber','session','number','date','kind','yes','no','result','description','url'])]:
 with (out/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows)
print('stats',stats,'sponsors',len(people),'record coverage',sum(bool(x['record_page']) for x in amend),'EV keywords',[(x['id'],x['record_page']) for x in amend if x['ev_keyword_hit']]);print('top',sorted(people,key=lambda x:-x['submitted'])[:6]);print('votes',[(v['number'],v['yes'],v['no'],v['kind']) for v in votes.values() if v['yes'] is None]);
