# 미국 입법사 연구 / U.S. legislative history

공개 페이지: https://woochangkang.github.io/us_legislature/ira/

## IRA 전기차 최종 조립 요건

`ira/`는 2021–2022년 입법 과정의 조문 비교와 주장–증거 자료집입니다.

- 법안 버전 8개, 근거 20개, 미해결 질문 6개
- 5단계 대화형 입법 흐름도: 조립 지역·시행 시점, 근거·PDF·조문 비교 연결
- 공식 원문 PDF 11건: `ira/pdfs/`
- HTML PDF 뷰어: `ira/viewer.html`
- 인용 페이지 31개의 문구 좌표: `ira/highlights.json`
- 분석 데이터와 CSV: `ira/research-data.json`, `ira/*.csv`

### 원문과 하이라이트

PDF는 확보 당시 파일을 수정하지 않고 보관합니다. SHA-256은 `research-data.json`의 각 source에서 확인할 수 있습니다. 하이라이트는 PDF 위에 HTML로 겹쳐 표시하는 연구자 주석이며 원문의 일부가 아닙니다. 뷰어는 PDF 페이지 순서를 사용합니다. 인쇄 쪽수와 PDF 쪽수가 다르면 근거 목록의 locator를 확인하세요.

인용 페이지는 정적 이미지로도 제공하여 PDF 렌더러가 불가능한 환경에서도 원문과 강조 표시를 볼 수 있습니다. 전체 PDF 페이지는 자체 호스팅한 Mozilla PDF.js로 렌더링합니다. PDF.js 6.3.289와 포함 구성요소의 라이선스는 `ira/vendor/pdfjs/`에 있습니다.

### 검증 범위

보유한 5,676쪽 전체의 정독 결과가 아닙니다. 관련 조문과 발언을 선별 검토했습니다. 2021년 위원회 속기록 111쪽의 작성자 진술은 2021년 선행 설계에 관한 증거이며, 2022년 북미 확대·시행일 변경의 개인별 작성자를 입증하지 않습니다. 검색 텍스트가 부족한 속기록 부록 223–332쪽은 미검토 범위로 남아 있습니다.

### 로컬 실행 및 갱신

```sh
python3 -m http.server 8000
# http://localhost:8000/ira/
python3 -m pip install PyMuPDF Pillow beautifulsoup4
python3 tools/build_highlights.py
```

`tools/prepare_public.py`는 기존 연구 HTML에 뷰어를 통합하는 일회성 변환기입니다. 이미 통합된 HTML에 중복 실행하지 마세요. 게시 파일은 정적 HTML/JS/CSS이며 서버측 코드나 외부 API 키가 필요하지 않습니다. GitHub Pages는 main 브랜치 루트에서 제공합니다.

### 출처와 이용

각 자료의 공식 출처 URL과 원문 파일 식별값을 보존했습니다. 미국 연방정부 발행 기록과 법안 원문을 연구·검증 목적으로 제공하며, 제3자 웹자료는 원문 전체를 재배포하지 않고 짧은 인용·요약과 출처 링크만 제공합니다. 포함 문서의 별도 제3자 저작물 및 소프트웨어에는 해당 권리가 적용됩니다.
