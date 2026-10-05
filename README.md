# 미국 입법사 연구 / U.S. legislative history

공개 페이지: https://woochangkang.github.io/us_legislature/ira/

## IRA 전기차 최종 조립 요건

`ira/`는 2021–2022년 입법 과정의 조문 비교와 주장–증거 자료집입니다.

- 법안 버전 9개, 근거 27개, 후속 조사 질문 6개
- 주제별 탭 탐색, 행위자·증거·질문 선택 패널, 모바일 선택 메뉴 및 직접 링크·뒤로 가기 지원
- 5단계 대화형 입법 흐름도: 조립 지역·시행 시점, 근거·PDF·조문 비교 연결
- 원문·사본 PDF 16건 (하원 9월 초안은 동일 해시의 두 미러 사본): `ira/pdfs/`
- HTML PDF 뷰어: `ira/viewer.html`
- 인용 페이지 39개의 문구 좌표: `ira/highlights.json`
- 분석 데이터와 CSV: `ira/research-data.json`, `ira/*.csv`

### 원문과 하이라이트

PDF는 확보 당시 파일을 수정하지 않고 보관합니다. SHA-256은 `research-data.json`의 각 source에서 확인할 수 있습니다. 하이라이트는 PDF 위에 HTML로 겹쳐 표시하는 연구자 주석이며 원문의 일부가 아닙니다. 뷰어는 PDF 페이지 순서를 사용합니다. 인쇄 쪽수와 PDF 쪽수가 다르면 근거 목록의 locator를 확인하세요.

인용 페이지는 정적 이미지로도 제공하여 PDF 렌더러가 불가능한 환경에서도 원문과 강조 표시를 볼 수 있습니다. 전체 PDF 페이지는 자체 호스팅한 Mozilla PDF.js로 렌더링합니다. PDF.js 6.3.289와 포함 구성요소의 라이선스는 `ira/vendor/pdfjs/`에 있습니다.

### 검증 범위

보유한 6,628쪽 전체의 정독 결과가 아닙니다. 관련 조문과 발언을 선별 검토했습니다. 2021년 위원회 속기록 111쪽의 작성자 진술은 2021년 선행 설계에 관한 증거이며, 2022년 북미 확대·시행일 변경의 개인별 작성자를 입증하지 않습니다. 속기록 부록 223–332쪽 110면의 OCR·분류를 완료했습니다. 지정 검색어에서 추가 EV 조립 근거를 찾지 못했습니다. OCR 전체 글자·숫자를 교정하지는 않았습니다. 후속 조사 결과·접근 장애·무발견 범위는 `ira/followup-report.html` 및 `ira/followup/report.md`에 기록했습니다.

### 로컬 실행 및 갱신

```sh
python3 -m http.server 8000
# http://localhost:8000/ira/
python3 -m pip install PyMuPDF Pillow beautifulsoup4
python3 tools/build_highlights.py
```

`tools/prepare_public.py`는 기존 연구 HTML에 뷰어를 통합하는 일회성 변환기입니다. 이미 통합된 HTML에 중복 실행하지 마세요. 게시 파일은 정적 HTML/JS/CSS이며 서버측 코드나 외부 API 키가 필요하지 않습니다. GitHub Pages는 main 브랜치 루트에서 제공합니다.

### 출처와 이용

각 자료의 확보 출처 URL과 파일 식별값을 보존했습니다. 하원 9월 초안은 공식 옛 경로의 접근 실패와 대체 미러를 명시했습니다. 미국 연방정부 발행 기록과 법안 원문을 연구·검증 목적으로 제공하며, 보조 웹자료는 짧은 인용·요약과 출처 링크로 제공합니다. 의회 제출 PDF에 편입된 제3자 보고서의 OCR은 원문 확인을 돕는 기계 추출물이며 권리 이전이나 자유 이용 선언이 아닙니다. 포함 문서의 별도 제3자 저작물 및 소프트웨어에는 해당 권리가 적용됩니다.

### 양원 절차와 수정안 (2026-10-01)

`ira/#proc-route`의 양원 진행 흐름과 `ira/#proc-branches`의 수정·재수정 분기, 의원별 집계, 개별 수정안, 기명표결 및 선행 위원회 자료를 탭으로 제공합니다.

- H.R.5376 등록 수정안 295건: 상원 293, 하원 2. 상원 본회의 제안 27 = 채택 3 + 부결 18 + 절차상 배제 6; 미제안 266.
- 상원의원 주 제출자 49명 + 하원 Rules Committee 기관 항목. 공동제출자는 중복 집계하지 않습니다.
- 관련 기명표결 43건: 상원 39 + 하원 4. 구두표결·이의 없는 채택은 별도 설명합니다.
- 2021년 재무위원회 Master Amendments 135항목은 별도 집계. 처리·발언 대조 21항목, 미검증 114항목입니다.
- 상원 채택 3건의 최종 반영과 인슐린 문구 삭제를 Record 및 제정법으로 대조했습니다. 미제안 266건의 비공식 흡수·모든 유사 조문까지 대조한 결과는 아닙니다.
- 자료·다운로드·접근 실패 내역: `ira/procedure/`; 방법과 보고서: `ira/procedure/report.html`.
- 재생성: 저장된 원문에 대해 `python3 tools/build_procedure.py`, `python3 tools/build_procedure_evidence.py`, `python3 tools/build_procedure_report.py`, `python3 tools/build_highlights.py`. HTML은 별도 편집합니다.


## 산업 영향 배경 · 2026-10-01

언론 보도와 판매·투자 추세를 중심으로 배경을 추가했습니다. 산업 영향 탭에는 배경, 판매 데이터, 관련 보도, 완성차·부품·배터리, 조기경보, 자료의 여섯 하위 탭이 있습니다. 엄밀한 인과 추정이나 학술연구 검토는 본문 범위에서 제외했습니다.

- `ira/impact/report.html`: 독립 보고서
- `ira/impact/observations.csv`, `sources.json`: 관측값 33행, 출처 30건
- `python3 tools/build_impact.py`: 데이터·배경·보고서 재생성 (BeautifulSoup 필요)
- `python3 tools/build_impact_charts.py`: 데이터 기반 SVG 2개 재생성 (Matplotlib 필요)
- 2022–2024년을 중심으로 설명하며, 2025년 현지 생산·차량 공제 종료는 별도 국면으로 표시했습니다.


## 사례 연구 독서 순서 · 2026-10-01

첫 화면 → 한국의 이해(조립 지역·시행 유예) → 전체 입법 과정 → 주요 행위자 → 산업의 대응 → 조기경보 → 근거 자료실로 재구성했습니다. 기존 증거·수정안·조건 변화의 hash 링크는 유지됩니다.

- `ira/actors.json`: 당시 직책과 근거를 갖춘 18개 인물·기관 항목. 역할 지도는 별도 UI입니다.
- `tools/build_case_study.py`: 기존 내용을 재배열하고 역할 카드를 생성하는 반복 실행 가능한 스크립트.
- `tools/build_impact.py` 실행 후에도 사례 구조를 자동 복원합니다.
- 근거 자료실에 조사 업데이트·미해결 질문을 모아, 자료가 추가된 순서와 사례의 읽기 순서를 구분했습니다.


## AUKUS 핵추진잠수함 호주 판매 승인 · 2026-10-01

`aukus/`는 FY2024 NDAA(H.R.2670, P.L.118-31) Title XIII Subtitle B(1321–1354조)의 입법사입니다. 핵심은 1352조의 버지니아급 판매 승인입니다.

- 근거 78개(직접 확인 74 · 정황 3 · 미확인 1), 버전 대조 11행, 연표 37건, 행위자 21명, 원문 47건(PDF 38 · 웹 4 · 표결 XML 3 등)
- 판매 승인 문구는 하원 보고안·하원 통과안·상원 원안에 없음. 협의회 보고서(H.Rept.118-301)에서 처음 NDAA에 편입됨(PDF 전문 자동 검색)
- 인용문은 해당 PDF 쪽(±1) 텍스트와 대조했고, 불일치는 0건
- 데이터: `aukus/data/*.csv`, 본문 문안 `aukus/data/narrative.json`
- 재생성: `python3 tools/build_aukus.py` (표준 라이브러리만 사용, HTML을 직접 편집하지 말 것)
- 원 조사 폴더: Dropbox `_NIS/_US_Congress/aukus/` (`research_dossier.md`, 미확인·접근 실패 목록)


## NDAA 속의 한국 (FY2017–FY2027) · 2026-10-03

`ndaa_korea/`는 미국 국방수권법(NDAA) 속 한국 관련 내용의 조항·행위자·변화를 정리한 자료입니다.

- FY2027(H.R. 8800·S. 4784, 2026-10-03 현재 미제정) 한국 관련 항목 56건(직접 31 · 직접(북한) 12 · 간접 13; 법조문 40 · 위원회 보고서 16), 한국 언급 수정안 45건, 양원 조문 비교 22행, 입법 경과 30건
- 행위자 39명, 쟁점별 입장 38행, 발언·문서 근거 70건(68건 원문 대조), FARA 한국 측 등록 24건 (LDA 로비 공시는 API 차단으로 미수집)
- FY2017–FY2026 제정법 10건의 한국 관련 조문 171행(거부권 메시지 포함), 8개 쟁점 계보 105행, 주한미군 병력 하한 하원·상원·성립본 비교 18행
- 모든 인용은 원문 XML/HTM과 공백 정규화 문자열 대조. 근거 성격은 사실 / 정황 / 추정으로 구분
- 데이터: `ndaa_korea/data/*.csv`, 본문 문안 `ndaa_korea/data/narrative.json`
- 재생성: `python3 tools/build_ndaa_korea.py` (표준 라이브러리만 사용, HTML을 직접 편집하지 말 것)
- 2026-10-04 추가: 행위자 프로필 51건(소속·지위, 의원은 정당·지역구·선수·위원회·코커스 — congress-legislators·Congress.gov 기준), 입장 이유 38건(사실/정황/추정 구분), 입장 그룹 15개(사안별로 비슷한 입장 묶음, 연구자 판단)
- 표결 탭: 한국 관련 기명표결 35건(직접 6 · 북한 8 · FY2021 거부권 재의결 2 · NDAA 포괄 표결 19; 하원은 Clerk XML, 상원은 Congress.gov·의사록과 집계 대조), 행위자 의원 31명 표결 요약, 의원 894명 × 35건 표(`ndaa_korea/data/member_votes.json`, Voteview 기반)
- 로비 탭(2026-10-04): LDA 한국 조선·방산 의뢰인 활동 29행(2025–2026, GitHub Actions `lda-fetch.yml`로 수집 — lda.gov가 한국 네트워크를 차단), FARA 한국 측 등록 24건·활동보고서 접촉 78행
- 로비 탭 확장(2026-10-04): LDA 2017–2026 한국 기업·기관 의뢰 신고 1,796건(수정신고 정리 후)의 그룹×연도 금액표·연도별 상위 주체·방산·조선 기업 6곳 상세(분기별 금액·목적 원문·로비스트 전직)·LD-203 정치후원금 중 행위자 의원 수령분; FARA 등록 55건(2017–2026) 보고서 620건의 연도별 수령액(대행사 보수 / 한국 기관 미국 사무소 운영자금 구분)과 대리인 전직. 수집: `lda-fetch.yml`, `lda-lobbyists.yml`
- 원 조사 폴더: Dropbox `_NIS/_US_Congress/ndaa_korea/` (`site_research/` 조사 산출물·notes, `site_research/prep_site_data.py`로 이 저장소에 복사). 원문 파일은 저장소에 올리지 않고 공식 URL과 SHA-256만 기록


## 비밀번호 관문 (2026-10-05)

모든 HTML 페이지(랜딩·IRA·AUKUS·NDAA 각 영역)는 StatiCrypt로 암호화되어 있고 영역마다 비밀번호가 다릅니다.

- 빌드 전 평문 복원: `python3 tools/pages_lock.py unlock` (평문 사본은 `.plain/`, gitignore)
- 빌드 후 암호화: `python3 tools/pages_lock.py lock` (비밀번호는 로컬 `.pagelock.json`, gitignore — 커밋 금지)
- `.git/hooks/pre-commit`이 평문 HTML 커밋을 막습니다(`pages_lock.py check`). 다른 기기에서는 훅을 다시 설치해야 합니다.
- 한계: StatiCrypt는 HTML만 암호화합니다. CSV·JSON·PDF 등 다른 파일과 이전 커밋의 평문 페이지는 공개 저장소에서 계속 열람 가능합니다.


## 쿠팡 로비와 미국 의회 · 2026-10-05

`coupang/`는 LD-1/2 80건·LD-203 32건을 바탕으로 로비비·로비 주체·기관·의제를 분석하고, 주요 의원 16명과 청문회·조사·법안의 관계를 대조합니다. 2026년 1월·2월·5월·9월 절차, 공식 표결 44명(찬성 15·반대 8·공란 21), RSC 서명 54명을 수록했습니다.

- `coupang/data/`: 원문 URL을 보존한 공시·의원 관계·기부·표결 CSV
- `coupang/documents/`: 공식 의회 자료 PDF 10개
- 5월 20일 상원 공식 속기록 43–44쪽에서 Hagerty–Steel 쿠팡 문답 확인
- H.R.9834 GovInfo 최신 상태: 9월 16일 위원회 보고 의결
- HTML은 Atlas 루트와 같은 비밀번호. `pages_lock.py`의 쿠팡 영역은 별도 설정이 없으면 root 비밀번호를 사용합니다. 다른 영역 설정은 유지합니다.
- 원문 기부와 의원 행동은 사실, 영향·동기에 관한 해석은 분석으로 구분합니다.
