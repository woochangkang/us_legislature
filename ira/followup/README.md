# 1차 후속 조사 자료

report.md는 결과·범위·한계, results.json은 질문별 상태, source-manifest.json은 신규 PDF 출처·해시다. *-pages.json은 PDF의 페이지별 기계 추출 텍스트이며 독립적인 검증 결과가 아니다.

appendix-ocr.json은 T의 PDF 223–332쪽을 144 dpi로 렌더링해 Apple Vision accurate en-US로 처리한 결과다. wrapper_page는 PDF 연속 번호이며 보고서 자체 쪽수와 다를 수 있다. box는 Apple Vision 좌표(좌하단 원점)다. PDF 뷰어의 네이티브 텍스트 하이라이트 좌표와 혼용하지 않는다.

재현: macOS에서 tools/ocr_appendix.swift를 swiftc로 컴파일하고 144 dpi PNG 경로들을 인자로 전달한다. 각 이미지 옆 JSON이 생성된다. 원본 PDF를 수정하지 않는다. 이번 OCR의 분류·검색 범위는 report.md에 기록했다.
