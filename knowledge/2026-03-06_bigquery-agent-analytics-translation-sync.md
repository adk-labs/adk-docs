# 2026-03-06 bigquery-agent-analytics translation sync

## 작업 범위

- `docs/integrations/bigquery-agent-analytics.md`

위 영문 문서를 `docs/ko/integrations/bigquery-agent-analytics.md`, `docs/ja/integrations/bigquery-agent-analytics.md`에 전문 동기화.

## 수행 내용

- 문서 서두의 버전 요구사항을 `1.26.0` 기준으로 갱신
- `Auto Schema Upgrade`, `Tool Provenance`, `HITL Event Tracing` 관련 설명 추가 반영
- OpenTelemetry 설정 예제, `table_id`, `auto_schema_upgrade`, `content_formatter` 시그니처 등 구성 예제를 최신 코드에 맞게 갱신
- `Schema Reference`, `Tracing and Observability`, `Human-in-the-Loop (HITL) Events`, `Feedback` 등 누락되어 있던 섹션을 ko/ja에 추가
- `agent_events` 기준의 SQL 예제, `tool_origin` 분석, `HITL` 분석, Looker Studio / Conversational Analytics 관련 설명을 최신 영문 구조에 맞게 재동기화

## 검증

- `git diff --check` 통과
- 영문 대비 구조 비교 결과
  - headings `35/35`
  - fenced code blocks `50/50`
  - admonitions `4/4`
  - bullets `47/47`
- 핵심 신규 토큰 존재 확인
  - `auto_schema_upgrade`
  - `tool_origin`
  - `HITL`
  - `Looker Studio Dashboard`
  - `Feedback`

## 메모

- 기존 ko/ja 번역본은 최신 영문 원문과 구조 차이가 커서 부분 패치가 아닌 사실상 전체 재동기화가 필요했다.
