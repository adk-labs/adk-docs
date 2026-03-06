# 2026-03-06 Translation coverage audit

## 목적

- 영어 원문 기준으로 `docs/ko`, `docs/ja`에 번역 누락이 없는지 전수 조사했다.
- 단순 파일 존재 여부뿐 아니라 구조적 축약 여부를 함께 점검했다.

## 감사 범위

- 영어 원문 감사 대상: **155개 문서**
- 제외:
  - `docs/api-reference/java/legal/dejavufonts.md`
  - `docs/api-reference/java/legal/jquery.md`
  - `docs/api-reference/java/legal/jqueryUI.md`
  - 제외 사유: `mkdocs.yml`의 `exclude_docs` 대상
  - `docs/translation-upstream-sync-spec.md`
  - 제외 사유: 영문 원문이 아니라 내부 한글 운영 문서

## 검수 방법

1. 영어 원문 경로와 `docs/ko/<path>`, `docs/ja/<path>`의 대응 파일 존재 여부 비교
2. 대응 파일이 있는 경우 다음 구조 지표 비교
   - heading 수
   - code fence 수
   - admonition 수
   - tab block 수
   - 링크 수
   - 전체 line ratio
3. 구조 차이가 큰 문서는 실제 본문/헤더를 직접 대조하여 누락 여부 확인

## 전수 조사 결과

- 감사 대상 영어 문서: **155개**
- ko 대응 파일 존재: **154개**
- ja 대응 파일 존재: **154개**
- ko/ja 공통 실제 미번역 문서: **1개**
  - `docs/integrations/goodmem.md`
- 자동 구조 비교 기준 고위험 문서 수:
  - ko: **37개**
  - ja: **37개**
- 이 중 직접 대조로 “실제 누락/축약”으로 확인한 고신뢰 이슈:
  - 공통 누락 파일 1건
  - 공통 대폭 축약/미동기화 문서 7건
  - ja 추가 대폭 축약 문서 1건

## 고신뢰 누락/미동기화 목록

### 1. 번역 파일 자체가 없는 문서

- `docs/integrations/goodmem.md`
  - 누락 경로:
    - `docs/ko/integrations/goodmem.md`
    - `docs/ja/integrations/goodmem.md`

### 2. 영어 원문 대비 본문이 대폭 축약된 문서 (ko/ja 공통)

- `docs/streaming/dev-guide/part1.md`
  - 영어 원문은 `1.2 Gemini Live API and Vertex AI Live API`부터 `1.6 What We Will Learn`까지 포함
  - ko/ja는 초반부 이후 다른 구조의 문서로 이어져 동일 내용 전문을 유지하지 못함
- `docs/streaming/dev-guide/part3.md`
  - 영어: heading `80`, code fence `82`, admonition `31`
  - ko: heading `32`, code fence `28`, admonition `2`
  - ja: heading `26`, code fence `24`, admonition `1`
- `docs/streaming/dev-guide/part5.md`
  - 영어: heading `80`, code fence `60`, admonition `11`
  - ko: heading `30`, code fence `30`, admonition `4`
  - ja: heading `18`, code fence `20`, admonition `1`
- `docs/runtime/event-loop.md`
  - 영어는 Python/TypeScript/Go/Java 탭 예제를 포함
  - ko/ja는 탭 구조가 사라지고 요약형 설명 위주로 재작성됨
- `docs/sessions/session/index.md`
  - 영어의 `InMemorySessionService`, `VertexAiSessionService`, `DatabaseSessionService` 세부 설명과 다수 언어 탭이 ko/ja에서 축약됨
- `docs/agents/llm-agents.md`
  - 영어의 TypeScript 탭과 일부 planner/code execution 예제가 ko/ja에서 누락됨
- `docs/sessions/state.md`
  - 영어의 일부 TypeScript/Java 탭 구성이 ko/ja에서 빠져 있어 원문 전문 동기화 상태가 아님

### 3. 영어 원문 대비 본문이 대폭 축약된 문서 (ja 추가)

- `docs/streaming/dev-guide/part4.md`
  - 영어: heading `50`, code fence `40`, admonition `9`
  - ja: heading `35`, code fence `24`, admonition `3`
  - ko는 구조상 대부분 유지되지만 ja는 추가 축약이 큼

## 별도 관찰 사항

- 아래 문서들은 “영문 내용 누락”이라기보다 locale 문서가 영어 원문과 다른 세대/구조를 가진 상태로 보인다.
  - `docs/runtime/index.md`
  - `docs/plugins/index.md`
  - `docs/mcp/index.md`
  - `docs/context/index.md`
- 즉, 단순 번역 누락보다는 경로 동일 문서의 내용 드리프트 가능성이 있다.
- 후속 작업에서는 누락 보정과 별도로 “영문 최신 구조에 맞춘 재동기화”가 필요하다.

## 우선순위 제안

1. `integrations/goodmem.md` ko/ja 신규 번역 생성
2. `streaming/dev-guide/part1`, `part3`, `part5` ko/ja 전문 재동기화
3. `streaming/dev-guide/part4` ja 재동기화
4. `runtime/event-loop`, `sessions/session/index`, `agents/llm-agents`, `sessions/state` ko/ja 구조 복원
5. `runtime/index`, `plugins/index`, `mcp/index`, `context/index`의 경로-내용 드리프트 점검
