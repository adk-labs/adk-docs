# 2026-03-21 translation sync batch2

## 작업 범위

- upstream/main 의 ADK 2.0 워크플로 문서 신규 추가분을 기준으로 ko/ja 번역 동기화
- `mkdocs.yml` 의 ko/ja locale nav 에 ADK 2.0 워크플로 섹션 추가

## 반영 문서

- 신규 번역 문서 12건
  - `docs/ko/workflows/index.md`
  - `docs/ko/workflows/collaboration.md`
  - `docs/ko/workflows/data-handling.md`
  - `docs/ko/workflows/dynamic.md`
  - `docs/ko/workflows/graph-routes.md`
  - `docs/ko/workflows/human-input.md`
  - `docs/ja/workflows/index.md`
  - `docs/ja/workflows/collaboration.md`
  - `docs/ja/workflows/data-handling.md`
  - `docs/ja/workflows/dynamic.md`
  - `docs/ja/workflows/graph-routes.md`
  - `docs/ja/workflows/human-input.md`
- navigation 갱신 1건
  - `mkdocs.yml`

## 검증

- `git diff --check -- docs/ko/workflows docs/ja/workflows mkdocs.yml`
- 영문/ko/ja 문서별 헤더 수 일치
- 영문/ko/ja 문서별 fenced code block 수 일치
- 영문/ko/ja 문서별 admonition 수 일치

## 비고

- `docs/workflows/*` 6개 영문 원문을 기준으로 구조와 코드 블록을 유지하면서 번역
- locale nav 는 영문 `ADK 2.0` 섹션 구조를 ko/ja 에 동일하게 반영
