# 2026-03-21 asset reference audit

## 목적

- `docs/**` 내 로컬 이미지 및 assets 참조가 실제 파일을 가리키는지 점검
- 잘못된 상대경로를 수정해 문서 화면에서 자산 누락이 발생하지 않도록 보정

## 검사 범위

- Markdown 이미지 `![...](...)`
- HTML 이미지 `<img src="...">`
- 대상 파일: `docs/**/*.md`, `docs/**/*.html`
- 검사 대상 로컬 이미지 참조 수: `1254`

## 초기 결과

- 깨진 로컬 이미지 참조: `29`
- 주된 원인:
  - 루트 문서에서 `../assets/...` 같은 잘못된 상대경로 사용
  - locale 문서가 원문 폴더의 `assets` 하위 디렉터리를 상대경로로 그대로 참조
  - 중첩 깊이에 비해 `../../assets/...`, `../../../assets/...` 계산이 잘못된 경우

## 수정 파일

- `docs/community.md`
- `docs/get-started/quickstart.md`
- `docs/tools-custom/mcp-tools.md`
- `docs/ko/integrations/galileo.md`
- `docs/ja/integrations/galileo.md`
- `docs/ko/streaming/dev-guide/part4.md`
- `docs/ja/streaming/dev-guide/part4.md`
- `docs/ko/integrations/mcp-toolbox-for-databases.md`
- `docs/ja/integrations/mcp-toolbox-for-databases.md`
- `docs/ko/tools/third-party/tavily.md`
- `docs/ja/tools/third-party/tavily.md`

## 수정 내용 요약

- `community.md`:
  - `../assets/...` 를 `assets/...` 로 수정
- `get-started/quickstart.md`:
  - 주석 처리된 예시 이미지 경로 `../../assets/...` 를 `../assets/...` 로 수정
- `tools-custom/mcp-tools.md`:
  - `../../assets/...` 를 `../assets/...` 로 수정
- locale `galileo.md`:
  - 공유 자산을 `/adk-docs/integrations/assets/galileo-log.png` 로 지정
- locale `streaming/dev-guide/part4.md`:
  - 공유 자산을 `/adk-docs/streaming/dev-guide/assets/adk-streaming-guide-quota-console.png` 로 지정
- locale `mcp-toolbox-for-databases.md`:
  - `../../assets/...` 를 locale 자산 폴더 기준 `../assets/...` 로 수정
- locale `tools/third-party/tavily.md`:
  - `../../../assets/...` 를 locale 자산 폴더 기준 `../../assets/...` 로 수정

## 최종 검증

- `git diff --check` 통과
- 로컬 이미지 참조 재검사 결과:
  - 검사 수 `1254`
  - 깨진 참조 `0`
