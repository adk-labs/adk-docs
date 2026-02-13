# Runtime Event Loop

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">Typescript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK Runtime은 사용자 상호작용 중 에이전트 애플리케이션을 구동하는 기반 엔진입니다.
정의한 에이전트/도구/콜백을 오케스트레이션하고,
입력에 따라 정보 흐름, 상태 변경, LLM/스토리지 같은 외부 서비스 연동을 관리합니다.

Runtime을 에이전트 애플리케이션의 **엔진**으로 생각하면 됩니다.
개발자는 부품(에이전트/도구)을 정의하고,
Runtime이 이들을 연결해 사용자 요청을 처리합니다.

## 핵심 개념: Event Loop

ADK Runtime의 중심에는 **Event Loop**가 있습니다.
이 루프는 `Runner`와 실행 로직(Agent, LLM 호출, Callback, Tool) 간의
왕복 협력을 담당합니다.

![intro_components.png](../assets/event-loop.png)

간단히 보면:

1. `Runner`가 사용자 질의를 받고 메인 `Agent` 실행을 시작
2. `Agent`가 응답/도구 요청/상태 변경 등 보고할 내용이 생기면 `Event`를 `yield`(emit)
3. `Runner`가 이벤트를 받아 처리(예: Services를 통한 상태 저장) 후 상위로 전달
4. `Agent`는 `Runner`가 처리한 뒤에만 중단 지점에서 재개
5. 현재 질의에 대해 더 이상 이벤트가 없을 때까지 반복

이 이벤트 기반 루프가 ADK 실행 모델의 핵심 패턴입니다.

## Event Loop 내부 동작

!!! Note
    메서드명/파라미터명은 SDK 언어별로 다를 수 있습니다.
    (예: Python `agent.run_async(...)`, Go `agent.Run(...)`, Java/TS `agent.runAsync(...)`)

### Runner의 역할(오케스트레이터)

`Runner`는 단일 사용자 invocation의 중앙 조정자입니다.

1. **시작**: 사용자 질의(`new_message`)를 수신해 SessionService에 기록
2. **Kick-off**: 메인 에이전트 실행(`agent_to_run.run_async(...)`) 시작
3. **수신/처리**: 에이전트가 `yield`한 `Event`를 즉시 처리
   - `event.actions`의 `state_delta`, `artifact_delta` 등을 Services로 커밋
4. **상위 전달**: 처리된 이벤트를 UI/호출자에게 전달
5. **반복**: 에이전트가 다음 이벤트를 생성하도록 재개 신호 제공

### 실행 로직의 역할(Agent/Tool/Callback)

실제 의사결정/연산은 에이전트·도구·콜백 코드가 수행합니다.

1. 현재 `InvocationContext` 기반 실행
2. 결과/요청을 `Event`로 만들어 `yield`
3. `yield` 직후 실행 일시중지
4. `Runner` 처리 완료 후 재개
5. 재개 시 이전 이벤트의 커밋된 상태를 신뢰 가능

이 협력적 `yield/pause/resume` 사이클이 Runtime의 기본 동작입니다.

## Runtime 주요 구성 요소

1. ### `Runner`

      * **역할:** 단일 사용자 질의 실행의 진입점/오케스트레이터 (`run_async`)
      * **기능:** Event Loop 관리, 이벤트 처리/커밋, 상위 전달

2. ### 실행 로직 구성요소

      * `Agent` (`BaseAgent`, `LlmAgent` 등)
      * `Tools` (`BaseTool`, `FunctionTool`, `AgentTool` 등)
      * `Callbacks` (사용자 정의 훅 함수)
      * **기능:** 실제 판단/연산/외부 호출 수행 후 `Event`를 `yield`

3. ### `Event`

      * **역할:** Runner와 실행 로직 사이 메시지
      * **기능:** 내용 + 부작용 의도(`actions`, 예: `state_delta`)를 캡슐화

4. ### `Services`

      * `SessionService`: Session 저장/로드, state 적용, event history 관리
      * `ArtifactService`: 바이너리 아티팩트 저장/조회
      * `MemoryService`: (선택) 사용자 장기 의미 메모리
      * **기능:** Runner가 이벤트 액션을 영속화하는 백엔드 계층

5. ### `Session`

      * **역할:** 한 대화의 상태/이력 컨테이너
      * **기능:** `state`, `events`, 아티팩트 참조 보관

6. ### `Invocation`

      * **역할:** 단일 사용자 질의에 대한 전체 처리 단위
      * **기능:** 여러 agent run/LLM call/tool 실행/callback을 하나의 `invocation_id`로 묶음

## 단순 invocation 흐름

![intro_components.png](../assets/invocation-flow.png)

예시(도구 호출이 있는 질의):

1. 사용자 입력 수신
2. Runner가 Session 로드/사용자 이벤트 기록
3. Runner가 root agent 실행
4. LLM이 도구 호출 필요 판단
5. Agent가 FunctionCall 이벤트 `yield`
6. Agent 일시중지
7. Runner가 이벤트 기록/전달
8. Agent 재개
9. Agent가 도구 실행
10. 도구 결과 반환
11. Agent가 FunctionResponse 이벤트 `yield`
12. Agent 일시중지
13. Runner가 상태/아티팩트 델타 커밋 및 전달
14. Agent 재개
15. LLM 최종 응답 생성
16. Agent가 최종 텍스트 이벤트 `yield`
17. Agent 일시중지
18. Runner가 기록/전달
19. Agent 종료
20. Runner 루프 종료

## 중요한 Runtime 동작

### 상태 업데이트 커밋 타이밍

코드에서 상태를 바꿔도,
해당 `state_delta`를 담은 이벤트가 `yield`되고 Runner가 처리한 뒤에야
영속 커밋이 보장됩니다.

즉, `yield` 이후 재개된 코드에서는 이전 이벤트의 상태 커밋을 신뢰할 수 있습니다.

### Session State의 "Dirty Read"

같은 invocation 내부에서,
커밋 전 로컬 변경 상태가 읽히는 경우가 있습니다(Dirty Read).

- 장점: 같은 invocation 단계 내 구성요소 간 빠른 협업
- 주의: 커밋 전 실패 시 변경 유실 가능

중요 상태 전환은 반드시 Runner가 처리할 이벤트로 커밋되도록 설계하세요.

### 스트리밍 vs 비스트리밍 (`partial=True`)

- 스트리밍: 부분 이벤트(`partial=True`)를 즉시 전달
  - 일반적으로 Runner는 부분 이벤트의 `actions`는 커밋하지 않음
- 최종 이벤트(`partial=False` 또는 `turn_complete=True`)에서
  상태/아티팩트 델타를 원자적으로 커밋
- 비스트리밍: 단일 non-partial 이벤트를 처리

이 방식은 UI의 점진 출력과 상태 일관성을 동시에 달성합니다.

## Async 중심 설계 (`run_async`)

ADK Runtime은 비동기 실행을 기본으로 설계되어,
LLM 응답 대기/도구 실행 같은 동시 작업을 효율적으로 처리합니다.

- 주요 진입점: `Runner.run_async`
- 동기 `run`은 편의 래퍼로, 내부적으로 `run_async`를 호출하는 경우가 많음

### 동기 콜백/툴 사용 시 주의

- 블로킹 I/O는 이벤트 루프 지연 유발 가능
  - Python: `asyncio.to_thread` 등으로 완화 가능
  - TypeScript: Promise 기반 비동기 I/O 권장
- CPU-bound 동기 작업은 실행 스레드를 점유

이 동작들을 이해하면 상태 일관성, 스트리밍 업데이트, 비동기 실행 관련 문제를
더 예측 가능하게 설계/디버깅할 수 있습니다.
