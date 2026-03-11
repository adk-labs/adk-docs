# 2026-03-11 upstream main sync

## 작업 목적

- fork 저장소의 `main`에 `upstream/main` 최신 변경을 반영한다.
- 기준 기간은 **2026-03-06 ~ 2026-03-11** upstream 변경이다.
- 병합 후 영문 원문 변경을 기준으로 ko/ja 번역 반영 작업을 진행한다.

## 병합 결과

- 병합 기준 공통 조상: `2d10b0d9bf5f7d807e8e65cc2de35d496e524643`
- 병합 커밋: `d054fd262e88d02303b6b1ce05e426a58b2c85fb`
- 병합 메시지: `Merge remote-tracking branch 'upstream/main'`

## 기간 내 upstream 관련 커밋

- `201e3253` `docs: Add documentation for LiteRT-LM model hosting (#1382)`
- `20569ed5` `Update typescript context (#1393)`
- `ec9b61e5` `Implemented the missing java code snippets for plugins. (#1394)`
- `c9b0533a` `Implemented the missing java snippets in memory.md (#1395)`
- `6ae3c9d0` `docs: Add cluster-related tools to Bigtable integration docs (#1396)`
- `0e4b91a9` `Update documentation for BigQuery Agent Analytics Plugin (#1399)`
- `eed5e53f` `Add ADK Development Skills section to Coding with AI tutorial (#1402)`
- `23e09961` `docs: Add home page banner for ADK dev Skills release (#1406)`
- `1cd402e9` `fix: update remaining references to use ADK Gemini Live API Toolkit (#1381)`
- `63305dba` `Add link to ADK skills source on GitHub (#1407)`
- `90a1ba2a` `docs: remove GKE from deploy skill description (#1410)`

## 번역 대상 영문 문서

- `docs/index.md`
- `docs/agents/models/index.md`
- `docs/agents/models/litert-lm.md`
- `docs/artifacts/index.md`
- `docs/context/index.md`
- `docs/get-started/about.md`
- `docs/integrations/bigquery-agent-analytics.md`
- `docs/integrations/bigtable.md`
- `docs/integrations/galileo.md`
- `docs/plugins/index.md`
- `docs/safety/index.md`
- `docs/sessions/memory.md`
- `docs/sessions/state.md`
- `docs/streaming/dev-guide/part1.md`
- `docs/streaming/index.md`
- `docs/streaming/streaming-tools.md`
- `docs/tutorials/coding-with-ai.md`

## 초기 분류

- 신규 번역 필요 문서:
  - `docs/agents/models/litert-lm.md`
  - `docs/integrations/galileo.md`
- 기존 ko/ja 업데이트 대상 문서:
  - 나머지 15개 문서
- 설정 반영 대상:
  - `mkdocs.yml`

## 다음 단계

1. 신규 문서 2개를 ko/ja로 추가
2. 소규모 변경 문서부터 ko/ja 갱신
3. 대형 문서(`plugins`, `sessions/memory`, `tutorials/coding-with-ai`)는 별도 배치로 처리
