# 2026-03-06 integrations translation sync

## 작업 범위

- 수정 반영
  - `docs/integrations/code-exec-agent-engine.md`
  - `docs/integrations/github.md`
  - `docs/integrations/gke-code-executor.md`
  - `docs/integrations/hugging-face.md`
  - `docs/integrations/linear.md`
  - `docs/integrations/n8n.md`
  - `docs/integrations/postman.md`
  - `docs/integrations/stripe.md`
- 신규 번역 생성
  - `docs/integrations/stackone.md`
  - `docs/integrations/supermetrics.md`
  - `docs/integrations/windsor-ai.md`

위 영문 문서를 `docs/ko` 및 `docs/ja`에 반영.

## 수행 내용

- `code-exec-agent-engine`의 설정/설명 변경을 ko/ja에 반영
- `github`, `gke-code-executor`, `hugging-face`의 upstream 대규모 본문 변경을 ko/ja에 동기화
- `linear`, `n8n`, `postman`, `stripe`의 소규모 기능/문구 변경 반영
- 신규 문서 `stackone`, `supermetrics`, `windsor-ai`의 ko/ja 전문 번역 생성

## 검증

- `git diff --check` 통과
- 신규 문서 6개 생성 확인
- 구조 비교 결과
  - `stackone`, `supermetrics`, `windsor-ai`는 헤더/탭/목록 구조가 영문과 대응
  - 수정 문서들도 헤더/탭/목록 수가 영문과 맞거나 변경 범위 내에서 합리적으로 유지됨

## 메모

- `bigquery-agent-analytics`는 기존 번역본과 최신 영문 간 구조 차이가 커서 별도 전체 동기화 배치로 분리한다.
