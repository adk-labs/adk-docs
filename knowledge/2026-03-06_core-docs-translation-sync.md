# 2026-03-06 core docs translation sync

## 작업 범위

- `docs/community.md`
- `docs/deploy/agent-engine/test.md`
- `docs/deploy/cloud-run.md`
- `docs/evaluate/criteria.md`
- `docs/evaluate/user-sim.md`
- `docs/get-started/installation.md`
- `docs/get-started/java.md`
- `docs/index.md`

위 영문 변경을 `docs/ko` 및 `docs/ja` 번역본에 반영.

## 수행 내용

- `community`의 최신 커뮤니티 콜 카드(2026-02) 반영 및 오래된 카드 제거
- `deploy/agent-engine/test`의 SSE 엔드포인트를 `:streamQuery?alt=sse`로 동기화
- `deploy/cloud-run`, `get-started/installation`, `get-started/java`, `index`의 Java 버전 표기를 `0.6.0` 기준으로 갱신
- `evaluate/criteria`에 `conversation_plan`, `persona`, `violation_rubrics` 관련 평가 설명 추가 반영
- `evaluate/user-sim`에 다음 신규 내용을 ko/ja 전체 반영
  - `ConversationScenario` 구성 요소 설명
  - `user_persona` 사용 예시
  - `User Personas`, `Pre-built Personas`, `Custom Personas` 섹션
  - Jinja placeholder 문법 (`{{ stop_signal }}`, `{{ conversation_plan }}`, `{{ conversation_history }}`, `{{ persona }}`)

## 검증

- `git diff --check` 통과
- `user-sim`에서 새 헤더/예제/토큰이 ko/ja 모두 존재하는지 확인
- `safety/index`는 upstream diff가 영문 오탈자 정리 수준이라 현 번역 의미가 유지됨을 확인하고 미수정 처리

## 메모

- `user-sim`은 upstream 추가 분량이 많아 사실상 부분 재동기화가 아니라 섹션 단위 재번역에 가깝게 반영했다.
