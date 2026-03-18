# 2026-03-18 upstream main sync

## 작업 목적

- fork 저장소의 `main`에 `upstream/main` 최신 변경을 반영한다.
- 기준 기간은 **2026-03-17 ~ 2026-03-18** upstream 변경이다.
- 병합 후 영문 원문 변경을 기준으로 ko/ja 번역 반영 작업을 진행한다.

## 병합 결과

- 병합 기준 공통 조상: `441fe9a943f3f9af2e0c4d562d5fe0f3e5bde490`
- 병합 커밋: `85d4d27867d809499bf7e2d77a27fdbec7ce581e`
- 병합 메시지: `Merge remote-tracking branch 'upstream/main'`
- 확인한 변경 로그:
  - `upstream-doc-change-log/2026-03-17.md`
  - `upstream-doc-change-log/2026-03-18.md`

## 기간 내 upstream 관련 커밋

- `8d8a78b2` `Revise title and description for root cause analysis (#1408)`
- `8a5a2ad6` `Update llm-agents.md (#1414)`
- `ee1555e6` `The app name youtube-shorts-assistant contains hyphens, which aren't valid Python identifiers. (#1436)`
- `b976dc02` `docs: Add Technical Overview page link to GetStarted page. (#1433)`
- `a0dbcca2` `feat: add A2A guardrails and correct import reference to coding skills (#1452)`
- `88b09c0b` `Update documentation of new A2A-ADK integration (#1405)`
- `94f933b7` `feat: add GKE parity across scaffold, deploy, and observability skills (#1449)`

## 번역 대상 영문 문서

- `docs/agents/llm-agents.md`
- `docs/get-started/index.md`
- `docs/integrations/bigquery-agent-analytics.md`
- `docs/a2a/index.md`
- `docs/a2a/quickstart-consuming.md`
- `docs/a2a/quickstart-exposing.md`
- `docs/a2a/a2a-extension.md`

## 비번역 범위

- `skills/adk-cheatsheet/references/python.md`
- `skills/adk-deploy-guide/SKILL.md`
- `skills/adk-deploy-guide/references/gke.md`
- `skills/adk-observability-guide/SKILL.md`
- `skills/adk-scaffold/SKILL.md`
- 예제 디렉터리 리네임 및 `.env` 삭제

## 다음 단계

1. 소규모 기존 문서부터 ko/ja 번역 동기화
2. A2A 문서 신규 추가 및 확장 섹션을 별도 배치로 정리
3. 배치별 `knowledge` 기록, 검증, subagent 리뷰, 커밋, 푸시 수행
