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
