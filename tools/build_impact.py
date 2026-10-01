# coding: utf-8
from pathlib import Path
from bs4 import BeautifulSoup
import json,csv,datetime,html
R=Path(__file__).resolve().parents[1]; D=R/'ira/impact'; D.mkdir(exist_ok=True)
sources={}
def source(i,title,url,kind):
 sources[i]={'id':i,'title':title,'url':url,'type':kind,'checked':'2026-10-01'}
source('I01','재무부 · 2022.8.16 최초 시행 안내','https://home.treasury.gov/news/press-releases/jy0923','정부')
source('I02','IRS · 2022년 이전 적격 차량 및 경과 규칙','https://www.irs.gov/credits-deductions/manufacturers-and-models-for-new-qualified-clean-vehicles-purchased-in-2022-and-before','정부')
source('I03','재무부 · 2022.12.29 상업용 공제 후속 안내','https://home.treasury.gov/news/press-releases/jy1179','정부')
source('I04','IRS · 차량 소유자와 리스 공제 귀속','https://www.irs.gov/newsroom/topic-a-frequently-asked-questions-about-the-eligibility-rules-for-the-new-clean-vehicle-credit-under-ss30d-effective-jan-1-2023','정부')
source('I05','IRS · 2025.9.30 이후 취득 차량 공제 종료','https://www.irs.gov/clean-vehicle-tax-credits','정부')
source('I06','현대차 · 2022 미국 판매','https://www.hyundainews.com/releases/3732?lang=en_US','기업 판매 원자료')
source('I07','현대차 · 2024 및 2023 미국 판매 비교표','https://www.prnewswire.com/news-releases/hyundai-motor-america-reports-all-time-december-q4-and-2024-sales-records-302341746.html','기업 판매 원자료')
source('I08','현대차 · 2025 미국 판매','https://www.prnewswire.com/news-releases/hyundai-motor-america-achieves-record-december-and-fifth-consecutive-year-of-record-retail-sales-302652033.html','기업 판매 원자료')
source('I09','현대차 · 2022.6 및 2분기 판매','https://www.prnewswire.com/news-releases/hyundai-motor-america-reports-june-and-q2-2022-sales-301579536.html','기업 판매 원자료')
source('I10','현대차 · 2022.7 판매','https://www.prnewswire.com/news-releases/hyundai-motor-america-reports-july-2022-sales-301597861.html','기업 판매 원자료')
source('I11','현대차 · 2022.8 판매','https://www.prnewswire.com/news-releases/hyundai-motor-america-reports-august-2022-sales-301616198.html','기업 판매 원자료')
source('I12','현대차 · 2023.9 발표의 2022.9 비교값','https://www.prnewswire.com/news-releases/hyundai-motor-america-reports-september-and-q3-2023-sales-301945499.html','기업 판매 원자료')
source('I13','현대차 · 2022.10 판매','https://www.prnewswire.com/news-releases/hyundai-motor-america-reports-october-2022-sales-301664531.html','기업 판매 원자료')
source('I14','현대차 · 2022.11 판매','https://www.prnewswire.com/news-releases/hyundai-motor-america-reports-record-november-2022-sales-301691442.html','기업 판매 원자료')
source('I15','기아 · 2023 및 2022 미국 판매','https://www.kiamedia.com/us/es/media/pressreleases/21629/kia-america-reports-all-time-best-annual-sales','기업 판매 원자료')
source('I16','기아 · 2024 및 2023 미국 판매','https://www.kiamedia.com/us/en/media/pressreleases/22986/kia-america-posts-all-time-best-annual-sales-for-the-second-consecutive-year','기업 판매 원자료')
source('I17','기아 · 2025 미국 판매','https://www.kiamedia.com/us/es/media/pressreleases/24209/kia-america-postshighest-ever-annual-sales-in-company-history','기업 판매 원자료')
source('I18','Cox/KBB · 2024 미국 BEV 판매, 수정된 2023 비교값','https://www.coxautoinc.com/insights/q4-2024-ev-sales/','시장 집계')
source('I19','조선일보 · 2022.10.4 IRA와 판매 감소 연결 보도','https://www.chosun.com/economy/auto/2022/10/04/6TRJ3RGMNZADXDWQO2AI5HMXX4/','언론 보도')
source('I20','뉴시스 · 2023.1.26 현대차 CFO 리스 확대 설명','https://www.newsis.com/view/NISX20230126_0002170723','기업 발언 보도')
source('I21','뉴스핌 · 2023.4.25 현대차 3월 리스 비중 35% 설명','https://www.newspim.com/news/view/20230425000862','기업 발언 보도')
source('I23','현대차그룹 · 2022.5.20 미국 EV 공장 투자 발표','https://www.hyundai.com/content/hyundai/worldwide/en/newsroom/detail/hyundai-motor-group-to-establish-first-dedicated-ev-plant-and-battery-manufacturing-facility-in-the-u.s.-0000000068.html','기업 투자 발표')
source('I24','HMGMA · 2024.10 아이오닉 5 생산 개시','https://www.hmgma.com/our-facility/','기업 생산 이력')
source('I25','조지아주 · 2022.11.23 현대모비스 투자 발표','https://gov.georgia.gov/press-releases/2022-11-23/gov-kemp-second-global-automotive-supplier-hyundai-metaplant-create-1500','정부 투자 발표')
source('I26','조지아주 · 2023.2.1 서연이화 투자 발표','https://gov.georgia.gov/press-releases/2023-02-01/gov-kemp-seoyon-e-hwa-joins-growing-list-hyundai-suppliers-nearly-doubles','정부 투자 발표')
source('I27','LG · 2025.1.24 LG에너지솔루션 2024 실적','https://www.lg.co.kr/media/release/28612','기업 결산 발표')
source('I28','산업부 · 2023 자동차 수출 실적','https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/168480/view','정부 수출 통계')
source('I29','산업부 · 2024 자동차 산업 동향','https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/170049/view','정부 수출 통계')
source('I30','재무부 · 2023.3.31 배터리·광물 기준 설명','https://home.treasury.gov/news/press-releases/jy1379','정부')
source('I31','IRS · 45X 첨단제조 생산 공제','https://www.irs.gov/credits-deductions/advanced-manufacturing-production-credit','정부')
def cite(*ids):
 return ' <span class="impact-cites">'+' · '.join(f'<a href="{html.escape(sources[i]["url"])}" target="_blank" rel="noopener">{i}</a>' for i in ids)+'</span>'
rows=[]
def obs(series,period,value,unit,src,note=''):
 rows.append(dict(series=series,period=period,value=value,unit=unit,source_id=src,note=note))
for y,a,b,c,d in [(2022,22982,None,20498,None),(2023,33918,12999,18879,1118),(2024,44400,12264,21715,22017),(2025,47039,10478,12933,15051)]:
 for model,v,s in [('IONIQ 5',a,'I06' if y==2022 else 'I08' if y==2025 else 'I07'),('IONIQ 6',b,'I08' if y==2025 else 'I07'),('EV6',c,'I15' if y<2024 else 'I16' if y==2024 else 'I17'),('EV9',d,'I16' if y<2025 else 'I17')]:
  if v is not None:obs(model,str(y),v,'US sales units',s,'연간; 구매·리스 합계; EV9 2023은 출시 초기')
for m,v,s in [(6,2853,'I09'),(7,1978,'I10'),(8,1516,'I11'),(9,1306,'I12'),(10,1579,'I13'),(11,1191,'I14'),(12,1720,'I06')]:obs('IONIQ 5',f'2022-{m:02}',v,'US sales units',s,'월간; 구형 Ioniq 제외')
for y,v in [(2023,1212758),(2024,1301411)]:obs('US BEV market',str(y),v,'US sales units','I18','Cox 2025.1 발표; 2023 수정값; 일부 exotic 제외')
for y,v in [(2022,84000),(2023,144000)]:obs('Korea to US eligible-type eco vehicle exports',str(y),v,'export units','I28','BEV·PHEV·FCEV; 반올림된 수출량; 미국 소매판매와 다름')
for y,v in [(2022,54.1),(2023,70.9),(2024,70.8)]:obs('Korea worldwide automobile exports',str(y),v,'USD billion','I29' if y==2024 else 'I28','전 차종 수출 금액; 부품 제외')
for name,v in [('LGES reported operating profit',-225.5),('LGES IRA credit',377.3),('LGES operating profit excluding credit',-602.8)]:obs(name,'2024-Q4',v,'KRW billion','I27','회사 공시상 분해; 북미 조립 조항 단독 효과 아님')
for y,v in [(2024,14082),(2025,5948)]:obs('IONIQ 5',f'{y}-Q4',v,'US sales units','I08','2025는 현지 생산 및 공제 종료가 겹친 별도 국면')
with (D/'observations.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(D/'sources.json').write_text(json.dumps(list(sources.values()),ensure_ascii=False,indent=2))
(D/'observations.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
pct=lambda a,b:round((a/b-1)*100,2)
calc={'ioniq5_2023_yoy_pct':pct(33918,22982),'ioniq5_2024_yoy_pct':pct(44400,33918),'ioniq5_july_vs_june_2022_pct':pct(1978,2853),'ioniq5_september_vs_august_2022_pct':pct(1306,1516),'ioniq5_bev_share_2023_pct':round(33918/1212758*100,3),'ioniq5_bev_share_2024_pct':round(44400/1301411*100,3),'ev6_2023_yoy_pct':pct(18879,20498),'ioniq5_2025_q4_yoy_pct':pct(5948,14082),'early_signal_days':(datetime.date(2022,8,16)-datetime.date(2021,5,26)).days,'final_draft_days':(datetime.date(2022,8,16)-datetime.date(2022,7,27)).days}
(D/'calculations.json').write_text(json.dumps(calc,ensure_ascii=False,indent=2))
def table(headers, data):return '<div class="impact-table"><table><thead><tr>'+''.join('<th>'+h+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in row)+'</tr>' for row in data)+'</tbody></table></div>'
def panel(id,label,body):return f'<section id="{id}" data-impact-label="{label}">{body}</section>'
background=f'''<p class="impact-verdict">판정: <strong>구매 공제 상실과 판매 방식의 변화는 확인된다.</strong><br/>아이오닉의 판매 감소 전부를 IRA 탓으로 돌리거나, 국내 산업 전체의 순손실을 확정할 근거는 부족하다.</p>
<div class="impact-metrics"><div><b>−30.7%</b><span>아이오닉 5, 2022년 6→7월<br/>법 제정 전부터 감소</span></div><div><b>+47.6% / +30.9%</b><span>2023 / 2024 연간 판매 증가<br/>장기 판매 붕괴와는 다른 모습</span></div><div><b>447일 → 20일</b><span>선행 심사→제정 / IRA 공개안→제정<br/>긴 논의, 짧은 최종 대응 창</span></div></div>
<h3>왜 이 입법 과정을 추적하는가</h3>
<p>IRA의 전기차 세액공제는 국내 기업의 경쟁 조건이 외국 의회의 한 문구로 바뀔 수 있음을 보여준다. 한국에서 조립해 미국에 수출한 아이오닉 5와 EV6는 2022년 8월 북미 최종 조립 요건 시행으로 일반 구매자의 신규 차량 공제 경로에서 제외되었다. 기존 적격 구매자에게 최대 7,500달러였던 혜택이 사라지면서, 적격 경쟁차에 비해 불리한 조건이 생겼다. 다만 경과 규칙이 있었고, 공제액 전체가 모든 소비자의 실질 가격 상승이나 현대차의 손실로 그대로 귀속되는 것은 아니다.{cite('I01','I02')}</p>
<p>2022년 가을에는 판매 감소를 IRA와 연결하는 보도가 나왔다. 실제 아이오닉 5 판매는 8월 1,516대에서 9월 1,306대로 줄었다. 그러나 6월 2,853대에서 7월 1,978대로 이미 감소하고 있었고, 이후 연간 판매는 2022년 22,982대에서 2023년 33,918대, 2024년 44,400대로 늘었다. 이 자료는 초기 충격 가능성과 이후 회복을 함께 보여주며, 정책이 없었을 때의 판매량을 직접 알려주지는 않는다.{cite('I19','I09','I10','I11','I12','I06','I07')}</p>
<p>회복 과정에는 판매 방식의 전환이 있었다. 2023년 상업용 차량 공제(45W)는 적격 리스 사업자가 공제를 받아 고객의 리스 조건에 반영할 경로를 제공했다. 현대차 경영진도 리스 확대를 대응책으로 설명했다. 따라서 영향은 판매 대수 외에 할인·금융지원 비용, 리스의 잔존가치 위험, 생산 거점 및 공급망 전환 비용까지 보아야 한다. 리스 공제의 수급자는 원칙적으로 소유자인 리스 사업자이며, 고객에게 전액이 자동 이전되는 제도는 아니다.{cite('I03','I04','I20','I21')}</p>
<p>영향은 기업과 생산 위치에 따라 달랐다. 수입 완성차에는 불리한 자격 요건이 생겼지만, 미국 생산 설비를 가진 배터리·부품 기업에는 투자와 수주 기회 및 별도 생산 세액공제가 있었다. 해외 자회사의 이익 증가, 한국 공장의 생산·고용, 한국 수출은 서로 다른 결과다. 이 연구는 이를 구분한 뒤, 제안·수정·의결·시행의 어느 단계에서 대응 가능한 정보가 나타났는지를 묻는다.</p>
<aside class="impact-note"><b>분석 시점</b> 중심 비교는 2022–2024년이다. IRS에 따르면 30D·45W 등 차량 공제는 2025년 9월 30일 이후 취득 차량에 적용되지 않는다. 아래 리스 대응은 당시 제도에 관한 설명이며, 현재의 구매 안내가 아니다.{cite('I05')}</aside>'''
annual=[]
for name in ['IONIQ 5','IONIQ 6','EV6','EV9']:
 vals={r['period']:r for r in rows if r['series']==name and len(r['period'])==4}
 annual.append([name]+[f'{vals[str(y)]["value"]:,}'+cite(vals[str(y)]['source_id']) if str(y) in vals else '— (미출시)' for y in range(2022,2026)])
sales=f'''<h3>판매량: 단기 하락과 중기 확대를 함께 보기</h3><p>단위는 미국 판매 대수이며 구매와 리스를 합산한다. 아이오닉 5와 구형 Ioniq를 구분했다. 가격·재고·마진 자료가 없는 판매표만으로 정책의 순효과를 추정하지 않는다.</p>
<label class="impact-picker">차트 선택 <select id="impact-chart-picker"><option value="monthly">2022년 월별 아이오닉 5</option><option value="annual">2022–2025년 차종별 연간 판매</option></select></label>
<figure><img id="impact-chart" src="impact/monthly.svg" alt="2022년 6월부터 12월 아이오닉 5 판매: 2853, 1978, 1516, 1306, 1579, 1191, 1720대"/><figcaption id="impact-chart-caption">8월은 제정 전후가 섞인 달이다. 점선은 제정 시점이며 인과효과 추정선이 아니다.</figcaption></figure>
{table(['차종','2022','2023','2024','2025'],annual)}
<p>아이오닉 5는 2023년 +47.6%, 2024년 +30.9% 증가했다. EV6는 2023년 −7.9%, 2024년 +15.0%로 다른 경로를 보였다. EV9의 2023년은 출시 초기이므로 2024년 증가율을 기존 차종의 정책 회복률로 읽을 수 없다. 코나·니로의 전 동력원 합계도 BEV 판매로 합산하지 않았다.</p>
<p>Cox가 2025년 1월 발표한 동일 자료 기준으로 미국 BEV 시장은 2023년 1,212,758대(수정값), 2024년 1,301,411대였다. 이에 대한 아이오닉 5 비중은 <b>2.80% → 3.41%</b>다. 점유율 회복도 ‘IRA가 없었을 경우보다 더 팔렸다’는 인과적 결론은 아니다.{cite('I18')}</p>
<aside class="impact-note"><b>2025년은 별도 국면.</b> 아이오닉 5 연간 판매는 47,039대였지만 4분기는 5,948대로 전년 동기 14,082대보다 57.8% 감소했다. 미국 현지 생산, 9월 말 차량 공제 종료와 구매 시점 이동 등이 겹치므로, 이 감소를 2022년 북미 조립 조항 하나의 효과로 분류하지 않는다.{cite('I08','I24','I05')}</aside>
<details><summary>2022년 월별 원자료 7건</summary>{table(['월','아이오닉 5','출처'],[[r['period'],f'{r["value"]:,}',cite(r['source_id'])] for r in rows if r['series']=='IONIQ 5' and len(r['period'])==7 and '-Q' not in r['period']])}</details>'''
sector=f'''<h3>국내 산업 전체: 손해와 수혜의 경로가 다르다</h3>{table(['부문','가능한 불리한 경로','수혜·대응 경로','근거와 한계'],[
['현대차·기아의 한국산 미국 판매 BEV','구매 공제 상실, 가격 경쟁과 금융지원 부담','당시 리스 전환, 차종 구성 조정, 현지 생산','공제 배제·판매·리스 변화 확인. 모델별 순이익 손실은 미확인.'+cite('I01','I20','I21')],
['미국 현지 완성차 생산','설비 투자·가동 초기 비용, 생산 전환 시간','북미 조립 충족 및 미국 판매 기반','현대차그룹은 IRA 전인 2022.5.20 조지아 투자 발표. HMGMA 아이오닉 5 생산은 2024.10 시작. 모든 투자를 IRA 탓으로 귀속 불가.'+cite('I23','I24')],
['배터리: LG에너지솔루션·SK온·삼성SDI 등','현지 투자·원산지 대응, 낮은 가동률 위험','적격 미국 생산에는 별도 45X 생산 공제 가능','기업·설비·연도별 자격이 다름. 아래 실적 수치는 LGES만 해당.'+cite('I27','I31')],
['미국 동반 진출 부품사','고정비·인력·물류·자금 조달 부담','현지 완성차 생산에 대한 수주 기회','현대모비스·서연이화 프로젝트 확인. 투자 발표는 수익 실현이나 IRA 단독 효과가 아님.'+cite('I25','I26')],
['한국 생산 중심의 중소·하위 협력사','생산 이전 때 국내 주문 감소 위험; 해외 투자 역량 차이','미국 공장에 한국산 부품 수출·현지 협업 가능','업체별 주문·생산·고용 패널 부재. 위험 경로이며 실현된 총피해로 집계하지 않음.'],
['한국GM·르노코리아·KG모빌리티 등','미국향 적격 BEV 및 공급망 노출에 따라 직접 영향 상이','차종·수출시장·그룹 생산 배분별 대응','현대차 BEV 결과를 모든 국내 완성차 업체에 동일 적용할 근거 없음.']])}
<div class="impact-cards"><article><h4>배터리 생산 공제의 관측 사례</h4><p>LG에너지솔루션의 2024년 4분기 영업손실은 <b>2,255억원</b>. 회사가 밝힌 IRA 세액공제 <b>3,773억원</b>을 제외하면 손실은 <b>6,028억원</b>이다. 별도 생산 지원의 큰 효과를 보여주지만, 북미 완성차 조립 조항의 순효과와 같지 않다. 이는 회사가 제시한 회계적 분해이지 공제가 없었을 경우의 행동까지 반영한 인과 추정이 아니다.{cite('I27')}</p></article>
<article><h4>부품업체의 현지 투자 사례</h4><p>조지아주 발표 기준 현대모비스는 <b>9.26억달러</b>(2022.11), 서연이화는 약 <b>0.76억달러</b>(2023.2)의 투자 계획을 발표했다. 수주 기회와 자본 투입이 동시에 발생한다. 발표 금액을 실제 집행액·한국의 손실액으로 바꾸어 해석하지 않는다.{cite('I25','I26')}</p></article></div>
<p>산업부 집계에서 미국향 IRA 대상 친환경차(BEV·PHEV·FCEV) 수출은 2022년 약 8.4만대에서 2023년 약 14.4만대로 증가했다. 전 세계 자동차 수출액도 2022년 541억달러, 2023년 709억달러, 2024년 708억달러였다. 이는 ‘IRA 이후 국내 자동차 수출 전반이 붕괴했다’는 설명과 맞지 않지만, 환율·차종 구성·시장 수요를 통제한 정책 효과도 아니다. 수출은 미국 소매판매와 다른 흐름이며, 전 차종 금액을 BEV 성과로 읽지 않는다.{cite('I28','I29')}</p>
<aside class="impact-note"><b>조항을 구분해야 한다.</b> 완성차 최종 조립(30D), 핵심광물·배터리 부품 요건(30D), 상업용 차량(45W), 미국 내 적격 부품 생산(45X)은 서로 다른 경로다. 북미 완성차 조립이 모든 일반 부품의 미국산 의무를 뜻하지 않으며, 북미 조립만으로 공제의 다른 요건까지 자동 충족하지 않는다.{cite('I30','I04','I31')}</aside>'''
early=f'''<h3>함의: 입법 조기경보를 산업 의사결정에 연결하기</h3><p>입법이 오랜 기간 진행된다는 사실은 대응의 기회를 제공한다. 그러나 최종 내용이 일찍 확정된다는 뜻은 아니다. 이 사례에서 미국 조립을 우대하는 선행 심사(2021.5.26)부터 제정(2022.8.16)까지는 <b>447일</b>, 북미 조립·제정 직후 적용 문구가 나타난 2022.7.27 공개안부터 제정까지는 <b>20일</b>이다. 긴 논의 속에서도 마지막 수정은 공장 건설 기간보다 훨씬 빠르게 현실화할 수 있다. <a href="#legislative-flow">기존 조문 변화 흐름과 근거 →</a></p>
<div class="impact-flow" aria-label="정보에서 대응까지 조기경보 흐름"><article><small>01 · 탐지</small><b>제안·조문 변경</b><p>법안·위원장 대안·수정안<br/>조건과 시행일의 차이</p></article><span aria-hidden="true">→</span><article><small>02 · 연결</small><b>산업 노출 지도</b><p>차종·공장·부품사<br/>매출과 전환 소요 시간</p></article><span aria-hidden="true">→</span><article><small>03 · 판단</small><b>의결 가능성·시간</b><p>위원회·본회의·예산절차<br/>담당자 검토와 시나리오</p></article><span aria-hidden="true">→</span><article><small>04 · 실행</small><b>대안 확보·갱신</b><p>정책 의견·생산·판매 전략<br/>시행 지침까지 추적</p></article></div>
<p><b>지역 조건과 시행일을 함께 추적한다.</b> 미국→북미 확대만 보면 완화지만, 2027년 이후→제정 직후로 바뀌면 해외 생산 기업의 대응 시간은 급감한다. 제목이나 최종 통과 여부만 알리는 시스템으로는 이런 결합을 놓친다.</p>
{table(['경보 단계','탐지 조건','담당·준비할 산출물'],[
['관찰','관련 차종·부품·공장에 걸리는 제안 등장','통상·법무: 조항 ID, 원문/버전, 제안자, 제출·상정·채택 상태 구분. 모든 제출안을 동일 위험으로 취급하지 않음.'],
['주의','지역·대상·예외·시행일이 기업 노출을 변경','통상+판매+구매: 48시간 내 영향 메모를 목표로 설정. 적격 차종·관련 협력사, 전환 기간, 복수 시나리오.'],
['집중 대응','위원장 대안·표결 일정·주요 합의로 시행 가능성이 높아지거나 시간이 단축','의사결정 책임자: 24시간 내 검토를 목표로 설정. 의견 제출·단계적 시행 요청, 판매/금융 대안, 생산 배분·투자 조건부 계획.'],
['시행 추적','제정·행정지침·유권해석·후속 개정·종료','법무+사업부: 확정 요건과 실제 자격 갱신. 미채택안은 종료 이력 보존. 2025년 공제 종료 같은 후속 변화도 포함.']])}
<h4>경보 이후에 무엇을 바꿀 수 있는가</h4><p>시행 유예 의견과 산업 연합 대응, 기존 공장의 생산 전환 가능성, 차종·판매 채널 조정, 공급업체 현지 협력, 계약의 정책 변경 조건을 사전에 검토할 수 있다. 리스는 이 사건 당시의 대응 사례이며 미래의 대안은 그때의 법령에 맞춰 다시 검증해야 한다. 중소 협력사는 업종 협회·공공기관의 공동 모니터링과 노출 분석을 활용하는 설계가 현실적이다.</p>
<p>조기경보의 목적은 정책을 정확히 예언하거나 피해를 모두 없애는 것이 아니라, <b>선택 가능한 대응책과 준비 시간을 늘리는 것</b>이다. 현대차그룹은 이미 IRA 전에 미국 공장 투자를 발표했으므로 ‘사전 인지가 없어서 피해가 났다’고 단정할 수 없다. 효과는 탐지 선행 일수, 담당자 인수 시간, 중요한 제안의 누락·오경보, 대응 시점에 남아 있던 선택지로 평가한다.{cite('I23')}</p>
<aside class="impact-note"><b>준비된 설계안</b> 이 탭은 운영 요건을 제안한 것이다. 자동 수집·알림 시스템이 실제 가동 중이라는 의미는 아니다. <a href="#proc-route">상·하원 흐름</a>과 <a href="#proc-amendments">수정안 목록</a>에 산업 노출 정보를 연결하는 다음 단계로 사용할 수 있다.</aside>'''
claims = '<h3>관련 보도는 무엇을 말했나</h3>' + table(['시점·출처','보도 내용','추세와 함께 읽기'],[
['2022.10.4 조선일보'+cite('I19'),'현대차·기아 전기차의 9월 미국 판매 감소를 IRA와 연결해 보도했다.','당시의 우려와 단기 감소를 보여준다. 법 제정 전부터 판매가 줄었으므로 원인을 하나로 단정하기는 어렵다.'],
['2023.1.26 뉴시스'+cite('I20'),'현대차 CFO는 리스 비중을 5% 미만에서 30% 이상으로 확대하겠다는 대응 계획을 설명했다.','구매 세액공제에서 제외된 뒤 판매 채널을 바꾸는 움직임이 확인된다.'],
['2023.4.25 뉴스핌'+cite('I21'),'현대차 실적 설명에서 3월 리스 비중 35%와 IRA 대응 효과가 언급됐다.','리스 확대를 통해 영향을 완화했다는 기업 측 설명이다. 전체 현대차 판매 중 리스 비중이라는 뜻으로 확대하지 않는다.']]) + '<p>보도의 흐름은 <b>2022년 하반기 판매 타격 우려 → 2023년 리스 확대 대응 → 2023–2024년 판매 회복·확대</b>로 요약할 수 있다. 판매가 늘었다고 부담이 전혀 없었다는 뜻은 아니며, 공제 상실을 보완하는 할인·금융지원과 현지 생산 전환에는 비용이 따른다. 공개 자료만으로 그 비용의 총액까지 판단하지 않는다.</p>'
method=f'''<h3>자료·재계산·범위</h3><p>확인일 2026.10.01. 기업 판매 원자료, 정부 제도·수출 자료, 기업 결산, 언론 보도를 구분했다. 원자료 발표값은 회사·시장 집계의 보고치이며 별도 감사자료와 동일하지 않다.</p><p><a href="impact/observations.csv" download>판매·산업 지표 CSV ({len(rows)}행)</a> · <a href="impact/observations.json">관측값 JSON</a> · <a href="impact/calculations.json">재계산 결과</a> · <a href="impact/sources.json">출처 목록</a> · <a href="impact/report.html">배경·함의 독립 보고서</a></p><p>증감률 = (당기/전기 − 1) × 100. 점유율 = 차종 판매 / 같은 연도 미국 BEV 판매 × 100. 월별 2022년 8월은 법 제정 전후가 섞여 있다. 부품 투자액은 발표액, 수출량은 반올림치다. 원자료가 다른 리스 비중은 합치지 않았다. 차종 미출시 연도는 0이 아니라 ‘—’로 표시했다.</p>'''+table(['ID·분류','원문'],[[s['id']+' · '+s['type'],f'<a href="{html.escape(s["url"])}" target="_blank" rel="noopener">{s["title"]}</a>'] for s in sources.values()])
contents=[('impact-background','배경·판정',background),('impact-sales','판매 데이터',sales),('impact-evidence','관련 보도',claims),('impact-supplychain','완성차·부품·배터리',sector),('impact-warning','입법 조기경보',early),('impact-method','자료·다운로드',method)]
section='<section id="industry-impact"><div class="section-title"><div><p class="kicker">INDUSTRY IMPACT · EARLY WARNING</p><h2>아이오닉의 판매에서 입법 조기경보까지</h2></div><a class="download" href="impact/report.html">배경 보고서 →</a></div><div id="impact-workspace">'+''.join(panel(*x) for x in contents)+'</div></section>'
f=R/'ira/index.html';soup=BeautifulSoup(f.read_text(),'html.parser');old=soup.find(id='industry-impact')
if old:old.decompose()
old_warning=soup.find(id='impact-warning')
if old_warning:old_warning.decompose()
soup.find(id='research-update').insert_after(BeautifulSoup(section,'html.parser'))
if not soup.find('link',href='impact.css'):soup.head.append(soup.new_tag('link',rel='stylesheet',href='impact.css'))
if not soup.find('script',src='impact.js'):tag=soup.new_tag('script',src='impact.js');soup.body.append(tag)
card=BeautifulSoup('<article class="actor-card"><span class="badge">산업 영향 추가</span><h3>판매 회복과 대응 비용은 별개</h3><p>아이오닉·기아 판매, 리스 전환, 배터리 생산 공제와 부품업체 투자를 대조했습니다.</p><a href="#impact-background">배경·판정 →</a> · <a href="#impact-warning">조기경보 설계 →</a></article>','html.parser')
if not soup.select('#research-update a[href="#impact-background"]'):soup.select_one('#research-update .actor-grid').append(card)
f.write_text(str(soup))
js=R/'ira/tabs.js';t=js.read_text();t=t.replace("['research-update','legislative-flow'","['research-update','industry-impact','legislative-flow'").replace("['새 조사 결과','변화 흐름'","['새 조사 결과','산업 영향·조기경보','변화 흐름'")
needle="    const procedure=document.getElementById('procedure-workspace');"
if "const impact=" not in t:t=t.replace(needle,"    const impact=document.getElementById('impact-workspace');\n    if(impact)makeGroup(impact,Array.from(impact.querySelectorAll(':scope > section')).map(panel=>({id:panel.id,label:panel.dataset.impactLabel,panel})),'산업 영향 탐색');\n"+needle)
js.write_text(t)
report='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>IRA 산업 영향과 입법 조기경보</title><link rel="stylesheet" href="../style.css"><link rel="stylesheet" href="../tabs.css"><link rel="stylesheet" href="../impact.css"></head><body><header><div class="mast"><a href="../index.html#industry-impact">← 입법 증거 아틀라스</a><b>산업 영향 보고서 · 2026.10.01</b></div></header><main class="report"><h1>IRA 북미 조립 요건의 산업 영향과 조기경보</h1>'
for id,label,body in contents:
 b=body.replace('src="impact/','src="').replace('href="impact/','href="').replace('href="#','href="../index.html#')
 report+='<h2>'+label+'</h2>'+b
report+='</main><script src="../tabs.js"></script><script src="../impact.js"></script></body></html>'
(D/'report.html').write_text(report)
print(json.dumps(calc,indent=2));print('observations',len(rows),'sources',len(sources))

# Keep the published narrative structure when rebuilding this earlier component.
import runpy
case_builder=R/'tools/build_case_study.py'
if case_builder.exists():runpy.run_path(str(case_builder),run_name='__main__')
