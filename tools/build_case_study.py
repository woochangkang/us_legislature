# coding: utf-8
"""Arrange the existing evidence atlas as a seven-chapter case study. Idempotent."""
from pathlib import Path
from bs4 import BeautifulSoup
import json,html
R=Path(__file__).resolve().parents[1];P=R/'ira';f=P/'index.html';s=BeautifulSoup(f.read_text(),'html.parser');main=s.find('main',id='main')
def parse(text):return BeautifulSoup(text,'html.parser')
def node(id):
 x=s.find(id=id)
 if x:x.extract()
 return x
def section(id,title,kicker,body=''):
 x=s.new_tag('section',id=id);x.append(parse(f'<div class="section-title"><div><p class="kicker">{kicker}</p><h2>{title}</h2></div></div>'+body));return x
def workspace(parent,id,items):
 w=s.new_tag('div',id=id)
 for panel,label in items:
  panel['data-case-label']=label;w.append(panel)
 parent.append(w)
# Preserve existing content and deep links before replacing chapter wrappers.
ids=['research-update','legislative-flow','procedure','comparison','finding','actors','evidence','questions','sources','industry-impact','impact-warning']
# Extract warning before its parent to keep one canonical copy.
warning=node('impact-warning')
parts={id:node(id) for id in ids if id!='impact-warning'}
for id in ['case-start','korean-stakes','early-warning','research-library']:
 old=s.find(id=id)
 if old:old.decompose()
for old in main.select('.chapter-next'):old.decompose()
for x in parts.values():
 if x:
  for old in x.select('.chapter-next'):old.decompose()
start=section('case-start','산업의 준비 시간은 언제 사라졌나','01 · CASE QUESTION', '''
<p class="case-lead">한국 자동차산업의 이해관계가 미국의 입법 과정에서 어떻게 바뀌었는지를 통해, <b>기업과 정부가 함께 활용할 입법 조기경보가 왜 필요한지</b> 살펴봅니다.</p>
<div class="case-two"><article><span>한국의 이해 ①</span><h3>어디서 조립해야 하는가</h3><p>미국 조립에서 북미 조립으로 범위가 넓어졌지만, <b>한국에서 조립해 수출하는 차량은 북미에 포함되지 않습니다.</b> 한국 기업의 국적이 아니라 차량의 최종 조립 장소가 기준입니다.</p><a href="#stakes-intro">조립 지역의 의미 →</a></article><article><span>한국의 이해 ②</span><h3>현지 생산을 준비할 시간이 있는가</h3><p>2021년 하원안의 2027년 이후 요건이 2022년 IRA에서는 <b>제정 직후 적용</b>으로 바뀌었습니다. 공장 가동 전 수출 판매를 이어갈 준비 시간이 핵심 이해였습니다.</p><a href="#legislative-flow">유예 기간이 바뀐 경로 →</a></article></div>
<p class="case-caution">2027년 기준은 당시 미제정 법안의 설계입니다. 이미 보장된 법적 유예를 철회한 것으로 설명하지 않습니다. 기존 구매계약 등에 대한 경과 규칙과 다른 공제 요건도 별도로 존재했습니다. <a href="#E09">하원안</a> · <a href="#E18">제정법</a></p>
<h3>이 사례를 읽는 순서</h3><ol class="case-reading"><li><a href="#korean-stakes"><b>한국의 두 이해관계</b><span>지역과 시간을 따로 보고, 함께 해석합니다.</span></a></li><li><a href="#procedure"><b>IRA 전체 입법 과정</b><span>BBB부터 양원 의결·대통령 서명까지 큰 흐름을 봅니다.</span></a></li><li><a href="#actors"><b>행위자와 역할</b><span>설계자·협상자·의결자·이해당사자를 구분합니다.</span></a></li><li><a href="#industry-impact"><b>산업의 영향과 대응</b><span>보도와 판매·투자 추세를 확인합니다.</span></a></li><li><a href="#early-warning"><b>조기경보의 함의</b><span>어떤 신호를 언제 발견하고 무엇을 준비할지 묻습니다.</span></a></li></ol>
<aside class="case-takeaway"><b>사례의 핵심 질문</b><p>“최종 법안을 알았는가”보다, <b>제안 단계부터 바뀌는 조건과 시행일을 추적해 선택 가능한 대응책을 미리 준비했는가</b>가 중요합니다. 이 사례만으로 당시 한국 정부·기업의 미인지나 대응 실패를 단정하지 않습니다.</p></aside>''')
stakes=section('korean-stakes','한국에는 ‘지역’과 ‘시간’이 함께 중요했다','02 · KOREAN STAKES')
intro=section('stakes-intro','두 조건을 한국 산업의 관점에서 읽기','REGION × TIME','''
<div class="case-two"><article><h3>북미 최종 조립</h3><p><b>미국·캐나다·멕시코</b>에서의 최종 조립을 뜻합니다. 북미에 공장이 있는 한국 기업의 차량은 지역 요건을 충족할 수 있지만, 한국 조립 수출차는 충족하지 못합니다. 북미 조립만으로 배터리 등 모든 요건을 충족하는 것도 아닙니다.</p><p>캐나다에는 미국→북미 확대가 직접적인 포함의 문제였습니다. 한국에는 <b>한국산 수출의 제외와 생산 거점 전환</b>의 문제였습니다.</p><a href="#actor-canada">캐나다 요구</a> · <a href="#actor-hyundai">현대차의 이해</a></article><article><h3>요건 적용의 유예</h3><p>지역 조건을 맞추려면 공장·설비·협력사 준비가 필요합니다. 2021년 하원안은 2027년 이후 미국 조립을 필수화하는 설계였지만, 2022년 IRA는 북미 조립 요건을 제정 직후에 적용했습니다.</p><p>따라서 지역은 넓어졌어도 <b>한국산 판매를 이어가며 전환할 수 있는 시간</b>은 짧아졌습니다. 이는 배터리 기준의 단계적 강화와 별개의 시행일 문제입니다.</p><a href="#E09">2021년 하원안</a> · <a href="#E18">2022년 제정법</a></article></div>
<div class="case-table"><table><thead><tr><th>질문</th><th>2021년 하원 통과안 · 미제정</th><th>2022년 IRA · 제정</th><th>한국 산업이 확인할 신호</th></tr></thead><tbody><tr><th>어디서?</th><td>미국 최종 조립</td><td>북미 최종 조립</td><td>한국 조립 수출차 포함 여부, 현지 공장 위치</td></tr><tr><th>언제부터?</th><td>2027년 이후 사용 개시 차량</td><td>제정일 이후 판매 기준</td><td>공장 가동 시점과 요건 적용일 사이의 공백</td></tr><tr><th>어떤 상태?</th><td>하원 통과안에 담긴 미래 조건</td><td>양원 의결·서명을 거친 실제 조건</td><td>제출·합의·의결·제정을 구분한 위험 판단</td></tr></tbody></table></div><p>근거: <a href="#E09">E09</a> · <a href="#E10">E10</a> · <a href="#E13">E13</a> · <a href="#E18">E18</a>. 아래 탭에서 2021년 선행 제안부터의 전체 문구 변화와 원문을 확인할 수 있습니다.</p>''')
workspace(stakes,'stakes-workspace',[(intro,'두 이해관계'),(parts['legislative-flow'],'조건 변화 흐름'),(parts['comparison'],'조문 대조'),(parts['finding'],'확인된 사실')])
proc=parts['procedure'];proc.find('h2').string='작은 EV 조항은 큰 입법 패키지 안에서 바뀌었다'
old=proc.find(id='proc-primer')
if old:old.decompose()
primer=section('proc-primer','BBB에서 IRA까지, 먼저 큰 그림 보기','03 · LEGISLATIVE PROCESS','''
<p>IRA는 전기차 보조금만을 다루는 독립 법안이 아니었습니다. <b>에너지·기후, 의료비·건강보험, 세금·재원</b>을 함께 다루는 법률 안에 EV 조항이 들어 있습니다. 따라서 한국과 직접 관련이 없는 세제 협상도 법안의 통과 가능성과 최종 내용에 영향을 줄 수 있었습니다. <a href="viewer.html?source=P&page=1">제정법 목차 →</a></p>
<div class="case-timeline"><article><small>2021 · 선행 논의</small><b>위원회에서 정책 설계</b><p>상원 재무위의 청정에너지 세제 논의와 하원 BBB 심사. 서로 다른 법안·문서 경로입니다.</p></article><span>→</span><article><small>2021.11.19 · 하원</small><b>BBB 통과</b><p>H.R.5376 · 220–213.<br/>하원 통과만으로 법률이 되지 않습니다.</p></article><span>→</span><article><small>2022.7–8 · 상원</small><b>협상 후 IRA로 대체</b><p>슈머·맨친 합의 → SA5194 대체안 → 연속 수정안 표결 → 8.7 통과.</p></article><span>→</span><article><small>2022.8.12–16</small><b>하원 동의 → 서명</b><p>하원 220–207 동의.<br/>8.16 대통령 서명으로 제정.</p></article></div>
<p><b>같은 법안 번호, 달라진 내용.</b> H.R.5376의 하원 BBB 본문을 상원이 IRA 대체안으로 바꿨고, 하원이 그 수정에 동의했습니다. 별도 양원협의위원회가 모든 쟁점을 다시 협상한 경로는 아닙니다. <a href="https://www.congress.gov/bill/117th-congress/house-bill/5376/all-actions">공식 처리 이력</a> · <a href="#E26">핵심 표결 기록</a></p>
<div class="case-two"><article><h3>왜 상원 표결은 51–50인가</h3><p>예산조정(reconciliation)은 일반 법안과 다른 신속 절차를 사용합니다. IRA 최종 표결에서 의원 찬반은 50–50이었고, 해리스 부통령의 결정표를 더해 51–50으로 통과했습니다.</p><a href="#actor-biden-harris">의결·서명 역할</a></article><article><h3>왜 찬성이 더 많아도 배제되는가</h3><p>예산조정에서는 내용에 대한 예산규율이 적용됩니다. 이를 면제하려면 60표가 필요한 경우가 있어, 57–43 찬성도 충분하지 않을 수 있습니다. 인슐린 문구의 일부 삭제가 그런 사례입니다.</p><a href="#proc-branches">수정안 처리의 차이</a> · <a href="#E27">인슐린 문구 기록</a></article></div>
<p class="meta">절차 설명: <a href="https://www.congress.gov/crs_external_products/R/PDF/R46468/R46468.4.pdf">CRS · 예산조정 절차</a>. 당시 사건의 결과는 본 사이트의 2021–2022년 의회 기록과 대조했습니다. 연속 수정안 표결은 흔히 vote-a-rama라고 부릅니다.</p>
<p><a class="download" href="#proc-route">날짜·표결별 양원 흐름 →</a> <a class="download" href="#proc-branches">어떤 수정안이 남았나 →</a></p>''');primer['data-proc-label']='전체 과정 이해';proc.find(id='procedure-workspace').insert(0,primer)
metrics=proc.select_one('.proc-metrics')
if metrics:proc.find(id='proc-method').insert(0,metrics.extract())
# Rebuild actor cards from a single source.
actors=parts['actors'];actors.clear();actors.append(parse('<div class="section-title"><div><p class="kicker">04 · ACTORS AND ROLES</p><h2>누가 설계하고, 협상하고, 대응했나</h2></div></div><p class="section-intro">2021–2022년 당시 직책을 기준으로 한 인물·기관 18개 항목입니다. 역할 지도를 먼저 보고 관심 행위자를 선택하세요. 공식 역할과 확인된 발언을 설명하며, 특정 문구의 작성이 미확정이면 이를 표시합니다.</p>'))
a=json.loads((P/'actors.json').read_text());grid=s.new_tag('div',attrs={'class':'actor-grid'});overview=s.new_tag('article',id='actor-overview',attrs={'class':'actor-card'});overview.append(parse('<h3>역할 지도<small>처음 읽는 독자를 위한 안내</small></h3>'))
for g in ['설계·위원회','협상·의결','국외 이해·대응','시행·해석']:
 text='<div class="case-role-group"><h4>'+g+'</h4><p>'+' · '.join(f'<a href="#actor-{x["id"]}">{x["name"]}</a>' for x in a if x['group']==g)+'</p></div>';overview.append(parse(text))
overview.append(parse('<p class="actor-limit">미국 조립의 선행 설계, 북미 확대, 유예 축소는 구분해서 추적합니다. 협상 당사자·법안 제출자라는 이유만으로 세 변화의 작성자를 모두 같은 사람으로 단정할 수 없습니다.</p>'));grid.append(overview)
for x in a:
 card=s.new_tag('article',id='actor-'+x['id'],attrs={'class':'actor-card'})
 refs=' · '.join([f'<a href="#{e}">{e}</a>' for e in x['evidence']]+[f'<a href="{html.escape(u)}" target="_blank" rel="noopener">{html.escape(label)}</a>' for u,label in x['sources']])
 card.append(parse(f'<p class="kicker">{x["group"]} · {x["historical_role"]}</p><h3>{x["name"]}<small>{x["english_name"]}</small></h3><p>{x["description"]}</p><p><b>한국의 이해·입법 흐름과의 관계</b> {x["relevance"]}</p><p class="actor-limit"><b>확인 범위</b> {x["limit"]}</p><p class="e-links">{refs}</p>'));grid.append(card)
actors.append(grid)
impact=parts['industry-impact'];impact.find('h2').string='산업은 어떤 영향을 받고 어떻게 대응했나';impact.select_one('.kicker').string='05 · INDUSTRY RESPONSE'
warn=section('early-warning','조기경보는 ‘통과 소식’보다 먼저 작동해야 한다','06 · EARLY WARNING');warn.append(warning)
library=section('research-library','근거와 조사 기록','REFERENCE LIBRARY','<p>본문의 주장과 연결된 원문·PDF·수정안 자료를 확인하는 곳입니다. 조사 결과가 추가된 순서는 이 자료실에 남기고, 사례 본문의 독서 순서와 구분했습니다.</p>')
workspace(library,'library-workspace',[(parts['evidence'],'증거 원문'),(parts['sources'],'자료·방법'),(parts['questions'],'미해결 질문'),(parts['research-update'],'조사 업데이트')])
chapters=[(start,'1 사례의 질문'),(stakes,'2 한국의 이해'),(proc,'3 입법 과정'),(actors,'4 주요 행위자'),(impact,'5 산업의 대응'),(warn,'6 조기경보'),(library,'근거 자료실')]
for i,(chapter,label) in enumerate(chapters):
 links=[]
 if i:links.append(f'<a href="#{chapters[i-1][0]["id"]}">← {chapters[i-1][1]}</a>')
 if i<len(chapters)-1:links.append(f'<a href="#{chapters[i+1][0]["id"]}">{chapters[i+1][1]} →</a>')
 chapter.append(parse('<nav class="chapter-next" aria-label="사례 읽기 순서">'+''.join(links)+'</nav>'));main.append(chapter)
title=main.select_one(':scope > .title');title.clear();title.append(parse('<p class="kicker">IRA CASE STUDY · LEGISLATIVE EARLY WARNING</p><h1>법이 바뀌기 전에, 산업은 무엇을 알아야 했나</h1><p>IRA 전기차 조항의 북미 조립·시행 유예를 통해 읽는 입법 과정과 조기경보의 필요성</p>'))
s.title.string='IRA 사례 연구 | 한국 자동차산업과 입법 조기경보';s.find('meta',attrs={'name':'description'})['content']='한국 산업의 두 이해관계인 북미 조립과 시행 유예를 출발점으로, IRA 전체 입법 과정·행위자·산업 대응과 조기경보의 필요성을 살펴봅니다.'
s.select_one('.mast .period').string='IRA 사례 연구 · 2021–2022 / 산업 대응 후속 확인'
nav=s.select_one('header nav');viewer=nav.find('a',href=lambda h:h and h.startswith('viewer.html'));viewer.extract() if viewer else None;nav.clear()
for x,label in chapters:nav.append(parse(f'<a href="#{x["id"]}">{label}</a>'))
if viewer:nav.append(viewer)
if not s.find('link',href='case.css'):s.head.append(s.new_tag('link',rel='stylesheet',href='case.css'))
f.write_text(str(s));(P/'case-navigation.json').write_text(json.dumps([{'id':x['id'],'label':label} for x,label in chapters],ensure_ascii=False,indent=2));print('7 chapters; 18 actor entries + role map')
