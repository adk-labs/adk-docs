# 2026-03-21 translation gap audit and remediation

## 목적

- 영어 원문 `docs/**` 전체를 기준으로 `docs/ko/**`, `docs/ja/**` 전수 조사
- 구조 누락 및 번역 드리프트가 큰 문서를 우선 보정
- 배치 단위 커밋과 푸시 기록 정리

## 조사 기준

- 원문 범위: `docs/**`
- 제외:
  - `docs/ko/**`
  - `docs/ja/**`
  - `docs/api-reference/java/legal/**`
  - `docs/translation-upstream-sync-spec.md`
- 조사 대상 영문 원문 수: `165`

## 자동 점검 기준

- locale 문서 존재 여부
- heading 수
- fenced code block 수
- admonition 수
- tab 수
- bullet / table / image 수 편차

## 초기 감사 결과

- ko missing: `1` (`integrations/goodmem.md`)
- ja missing: `1` (`integrations/goodmem.md`)
- ko 구조 위험 문서: `35`
- ja 구조 위험 문서: `35`

## 처리 배치

### upstream 이후 초기 보정

- `622220a0` `docs: sync Korean docs gaps`
  - `docs/ko/integrations/goodmem.md`
  - `docs/ko/runtime/index.md`
  - `docs/ko/mcp/index.md`
  - `docs/ko/agents/index.md`
  - `docs/ko/get-started/typescript.md`

- `f4e4a3dc` `docs: sync Japanese landing pages`
  - `docs/ja/integrations/goodmem.md`
  - `docs/ja/runtime/index.md`
  - `docs/ja/mcp/index.md`
  - `docs/ja/agents/index.md`
  - `docs/ja/get-started/typescript.md`

### 고위험 비스트리밍 보정

- `775dab51` `docs: improve Japanese high-drift docs`
  - `docs/ja/plugins/index.md`
  - `docs/ja/runtime/event-loop.md`
  - `docs/ja/sessions/session/index.md`
  - `docs/ja/tools-custom/mcp-tools.md`

- `0ca9c0b0` `docs: continue korean batch 2 sync`
  - `docs/ko/agents/llm-agents.md`
  - `docs/ko/agents/multi-agents.md`
  - `docs/ko/plugins/index.md`
  - `docs/ko/sessions/session/index.md`
  - `docs/ko/tools-custom/index.md`

- `5f2768ed` `docs: continue korean batch 3 sync`
  - `docs/ko/runtime/event-loop.md`
  - `docs/ko/plugins/index.md`
  - `docs/ko/agents/multi-agents.md`

- `dda09504` `docs: add Japanese TypeScript tool tabs`
  - `docs/ja/agents/llm-agents.md`
  - `docs/ja/agents/multi-agents.md`
  - `docs/ja/tools-custom/index.md`

### 스트리밍 개발 가이드 보정

- `775aee8d` `docs: continue korean streaming sync batch 4`
  - `docs/ko/streaming/dev-guide/part1.md`
  - `docs/ko/streaming/dev-guide/part3.md`
  - `docs/ko/streaming/dev-guide/part5.md`

- `516ee793` `docs: expand Japanese streaming guide structure`
  - `docs/ja/streaming/dev-guide/part1.md`
  - `docs/ja/streaming/dev-guide/part3.md`
  - `docs/ja/streaming/dev-guide/part4.md`
  - `docs/ja/streaming/dev-guide/part5.md`

- `4a4ec03a` `docs: continue korean streaming sync batch 5`
  - `docs/ko/streaming/dev-guide/part1.md`
  - `docs/ko/streaming/dev-guide/part3.md`
  - `docs/ko/streaming/dev-guide/part5.md`
  - `docs/ko/plugins/index.md`
  - `docs/ko/runtime/event-loop.md`

- `3691ad68` `docs: expand Japanese streaming and runtime parity`
  - `docs/ja/streaming/dev-guide/part1.md`
  - `docs/ja/streaming/dev-guide/part3.md`
  - `docs/ja/streaming/dev-guide/part4.md`
  - `docs/ja/streaming/dev-guide/part5.md`
  - `docs/ja/plugins/index.md`
  - `docs/ja/runtime/event-loop.md`

## 현재 상태

- ko missing: `0`
- ja missing: `0`
- 워크트리: clean
- `main` = `origin/main`

## 현재 기준 잔여 고위험 문서

### ko

- `docs/ko/streaming/dev-guide/part3.md`
- `docs/ko/streaming/dev-guide/part1.md`
- `docs/ko/streaming/dev-guide/part5.md`
- `docs/ko/plugins/index.md`
- `docs/ko/runtime/event-loop.md`
- `docs/ko/tools-custom/mcp-tools.md`
- `docs/ko/agents/custom-agents.md`
- `docs/ko/artifacts/index.md`

### ja

- `docs/ja/streaming/dev-guide/part3.md`
- `docs/ja/streaming/dev-guide/part4.md`
- `docs/ja/streaming/dev-guide/part5.md`
- `docs/ja/streaming/dev-guide/part1.md`
- `docs/ja/plugins/index.md`
- `docs/ja/tools-custom/mcp-tools.md`
- `docs/ja/agents/llm-agents.md`
- `docs/ja/agents/multi-agents.md`

## 비고

- 자동 구조 비교 수치는 완전한 의미 동등성을 보장하지 않으며, 일부 문서는 표기 방식 차이도 포함
- 다만 상기 잔여 문서는 heading, code block, tab, admonition 편차가 아직 커서 후속 보정 우선순위가 높음
