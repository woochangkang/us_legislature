# coding: utf-8
from pathlib import Path
import json,fitz,re,hashlib,collections,csv
root=Path('ira');out=root/'procedure'
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
# Keep committee inventory separate from numbered floor amendments.
doc=fitz.open(root/'pdfs/2021-05-26_Finance_Master_Amendments.pdf')
known={3:('위원장 수정안에 반영','EV 공제·미국 최종 조립 요건',111),55:('채택 · 28–0','중국산 EV 영향 평가',126),129:('부결 · 14–14','',131),81:('부결 · 14–14','',137),90:('부결 · 14–14','',143),48:('부결 · 14–14','',148),64:('부결 · 14–14','',153),101:('부결 · 14–14','',159),8:('철회','',160),113:('부결 · 14–14','',166),18:('철회','원자력 발전 세액공제',174),66:('부결 · 14–14','',181),46:('채택 · 구두표결','기관 공동 규칙 제정',183),122:('부결 · 13–15','EV 충전소 부담금',189),91:('채택 · 위원장 수용','강제·아동노동 생산품 제한',191),92:('부결 · 14–14','EV 세액공제 확대 제한',197),94:('심의 생략 발언 확인','채택·부결 표결 아님',197),108:('부결 · 14–14','에너지정보청 확인 전 폐지조항 효력 유예',204),95:('제안 후 철회','벌채 전 목재의 재해손실 공제',206),130:('논의 · 표결 요청 없음','탄소포집·석유회수',206),117:('부결 · 14–14','',214)}
rows=[]
for i,p in enumerate(doc):
 text=p.get_text();clean=' '.join(text.split());m=re.search(r'([A-Za-z]+(?:\s+Masto)?)\s+(?:Amendment\s*)?(?:#|No\.?\s*)?\s*(\d+)',clean,re.I)
 # Preserve heading rather than inventing a number when typography differs.
 name=m.group(1) if m else '';num=m.group(2) if m else '';title=re.search(r'Short Title:\s*(.*?)(?:Description of Amendment:|Description:|Offset:)',clean,re.I)
 if not name:raise ValueError((i+1,clean[:180]))
 status,summary,page=known.get(i+1,('처리 미검증','',None))
 rows.append(dict(id=f'M-{i+1}',sponsor=name,number=num,page=i+1,title=title.group(1).strip() if title else clean[:200],status=status,summary=summary,transcript_page=page))
write(out/'committee.json',rows)
with (out/'committee.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
print('committee',len(rows),collections.Counter(r['sponsor'] for r in rows),len(known))
# Evidence connects floor results to enacted text, with immutable PDF highlights.
p=root/'research-data.json';data=json.loads(p.read_text());sources={s['id']:s for s in data['sources']}
def ev(n,claim,who,quote,translation,refs,assessment,limit):
 return dict(id=f'E{n}',theme='의회 절차',claim=claim,who=who,date='2022.08.07',quote=quote,translation=translation,refs=[dict(source=s,pdf_page=page,locator=loc,url=sources[s]['url']+'#page='+str(page),viewer_url=f'viewer.html?source={s}&page={page}&evidence=E{n}') for s,page,loc in refs],assessment=assessment,limit=limit,level='표결·제정법 대조')
new=[
ev(24,'튠 수정안은 채택됐지만 SALT 부분은 뒤이어 다시 바뀌었다','존 튠 / 마크 워너','The amendment (No. 5472) was agreed to.','수정안 제5472호가 채택되었다.',[('R',150,'S4200 · PDF 150쪽'),('P',199,'136 Stat. 2015 · PDF 199쪽')],'SA5472는 57–43으로 채택됐다. 최저한세의 합산 기준 변경은 제정법 §13904에 남았으나 SALT 한도 연장은 §13903이 되돌렸다.','채택이라는 절차적 결과만으로 모든 내용의 최종 존속을 판단할 수 없다.'),
ev(25,'워너 수정안은 튠의 SALT 연장을 되돌리고 손실공제 제한을 연장했다','마크 워너','My amendment would simply strike the offset in the previous amendment','내 수정안은 앞선 수정안의 재원조달 부분을 삭제하는 것이다.',[('R',150,'S4200 · PDF 150쪽'),('R',151,'S4201 · PDF 151쪽'),('P',198,'136 Stat. 2014 · PDF 198쪽')],'SA5488은 50–50에서 부통령 찬성으로 채택됐다(공식 처리 이력 51–50, roll 324). 제정법 §13903과 문구를 대조했다.','이 수정안은 세제 재원 관련 수정이며 EV 조립지역을 바꾼 별도 수정안이 아니다.'),
ev(26,'대체안 채택과 법안 최종 통과는 서로 다른 의결이다','척 슈머 / 카멀라 해리스','The amendment (No. 5194), as amended, was agreed to.','수정된 제5194호 대체안이 채택되었다.',[('R',151,'S4201 · PDF 151쪽')],'수정된 SA5194는 구두표결로 채택됐다. 이어 H.R.5376 전체를 roll 325로 의결했고 50–50에서 부통령 찬성으로 통과했다(공식 이력 51–50).','의회 기록 표제일은 8월 6일이나 이 의결의 실제 처리일은 8월 7일이다. 구두표결에는 찬반 숫자가 없다.'),
ev(27,'57표의 찬성에도 예산규율 면제는 실패하여 문구가 삭제됐다','패티 머리 / 린지 그레이엄','The point of order is sustained, and the language will be stricken from the amendment.','의사진행 이의가 인정되어 해당 문구가 수정안에서 삭제된다.',[('R',144,'S4194 · PDF 144쪽')],'민간보험 인슐린 상한 관련 문구에 대한 예산규율 면제 동의는 57–43(roll 314)이었으나 필요한 60표를 얻지 못했다. 해당 문구는 대체안에서 삭제됐다.','이는 SA5194 전체의 부결이 아니며, 별도 제출 수정안 1건으로 추가 집계하지 않는다.')]
data['evidence']=[e for e in data['evidence'] if e['id'] not in {e['id'] for e in new}]+new;write(p,data)
write(out/'manifest.json',dict(scope='117th Congress H.R.5376 numbered amendments and recorded votes; separate 2021 Finance committee inventory',retrieved='2026-10-01',sources=[dict(file=p.name,url='https://www.govinfo.gov/bulkdata/BILLSTATUS/117/'+typ+'/'+p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p,typ in [(out/'BILLSTATUS-117hr5376.xml','hr'),(out/'BILLSTATUS-117s2118.xml','s')]],counts=dict(amendments=295,senate=293,house=2,senate_floor_proposed=27,senate_agreed=3,senate_rejected=18,senate_out_of_order=6,senate_not_proposed=266,roll_calls=43,committee_inventory=135,committee_reviewed=len(known)),notes=['Sponsor counts use named primary sponsor; cosponsors and on-behalf-of floor presenters are not additional submissions.','House two Rules Committee amendments are a separate institutional entry, not two individual members.','Senate vote XML retrieval failed with HTTP 403. Vote totals are from official BILLSTATUS actions, with key roll calls checked against Congressional Record.','No separate August 7 Senate daily PDF was retrieved; August 6 issue includes August 7 actions.','Committee inventory processing review is partial; unknown is not rejected.']))
