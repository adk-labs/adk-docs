# 2026-03-06 streaming/session translation sync

## 작업 범위

- `docs/context/compaction.md`
- `docs/get-started/streaming/quickstart-streaming.md`
- `docs/sessions/memory.md`
- `docs/sessions/state.md`
- `docs/streaming/index.md`
- `docs/streaming/dev-guide/part1.md`
- `docs/streaming/dev-guide/part2.md`
- `docs/streaming/dev-guide/part3.md`
- `docs/streaming/dev-guide/part4.md`
- `docs/streaming/dev-guide/part5.md`

위 영문 변경을 `docs/ko` 및 `docs/ja` 번역본에 반영.

## 수행 내용

- `Bidi-streaming` 명칭을 upstream 기준 `Gemini Live API Toolkit` 표기로 동기화
- `quickstart-streaming`, `streaming/index`의 다음 단계 링크를 dev-guide 시리즈 기준으로 갱신
- `sessions/memory`에 누락된 `from google import adk`, `from google.adk.agents import Agent` import 반영
- `sessions/state`의 `InstructionProvider` / 중괄호 리터럴 설명 변경과 TypeScript 예시 추가 반영
- `streaming/dev-guide/part4`의 Progressive SSE 설명을 `ADK_ENABLE_PROGRESSIVE_SSE_STREAMING=1` 실험 플래그 기준으로 갱신
- dev-guide 시리즈 전반의 source reference 해시/링크 업데이트 반영

## 검증

- `git diff --check` 통과
- `sessions/state`에서 `=== "TypeScript"` 탭 존재 확인
- `sessions/memory`에서 신규 import 존재 확인
- `streaming/dev-guide/part4`에서 `ADK_ENABLE_PROGRESSIVE_SSE_STREAMING=1` 존재 확인
- `quickstart-streaming`, `streaming/index`에서 Gemini Live API Toolkit 관련 링크/명칭 갱신 확인

## 메모

- `streaming/dev-guide` 일부 문서는 기존 ko/ja 번역본이 원문 대비 축약 상태였다.
- 이번 배치에서는 upstream 변경분이 반영된 구간을 기준으로 누락 없이 동기화했고, 전체 전문 재번역 여부는 별도 후속 작업 후보로 남긴다.
