# 2026-03-06 agents/models translation sync

## 작업 범위

- `docs/agents/llm-agents.md`
- `docs/agents/models/anthropic.md`
- `docs/agents/models/vertex.md`
- `docs/tutorials/agent-team.md`

위 영문 변경을 `docs/ko` 및 `docs/ja` 번역본에 반영.

## 수행 내용

- `llm-agents`의 `output_schema`와 `tools` 동시 사용 경고 문단을 ko/ja에 추가
- `anthropic`의 Claude 모델 식별자를 최신 표기로 동기화
- `vertex`의 Java 지원 배지, Model Garden/파인튜닝 Java 예제, Open Models 지원 표기를 ko/ja에 반영
- `agent-team`의 Claude 예제 모델 ID와 주석을 최신 값으로 갱신

## 검증

- `git diff c289ddfc^1 c289ddfc^2 -- <english-file>` 기준으로 변경 범위를 확인
- `git diff --check`로 공백/형식 오류 여부 확인
- 영문 대비 구조 검토:
  - `vertex`, `anthropic`, `agent-team`은 코드 블록/탭/헤더 구조가 유지됨
  - `llm-agents`는 이번 upstream 변경분인 경고 블록이 ko/ja 모두 반영되었는지 수동 확인

## 메모

- `llm-agents`는 기존 번역본 자체가 영문 대비 축약된 구조를 가지고 있어 전체 재번역 대상 후보로 남겨둔다. 다만 이번 작업 범위인 upstream 추가 경고 블록은 누락 없이 반영했다.
