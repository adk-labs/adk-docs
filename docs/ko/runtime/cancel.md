# 에이전트 실행 취소

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-typescript">TypeScript v1.0.0</span>
</div>

에이전트 실행이 너무 오래 걸리거나, 상황이 바뀌었거나, 더 이상 필요하지 않은 경우 이미
완료된 작업을 잃지 않고 실행을 취소하고 싶을 수 있습니다. ADK의 취소는 비파괴적입니다.
세션에 이미 커밋된 이벤트는 계속 유지됩니다.

ADK는 `AbortController`와 `AbortSignal`을 사용한 정상적인 취소를 지원합니다.
`runner.runAsync()`에 `AbortSignal`을 전달하면 에이전트 실행, LLM 생성, 도구 실행,
플러그인 콜백을 포함한 실행 스택의 어느 지점에서든 전체 호출을 취소할 수 있습니다.

## 시작하기

`AbortController`를 만들고, 해당 `signal`을 `runner.runAsync()`에 전달한 다음,
실행을 취소하려는 시점에 `controller.abort()`를 호출합니다.

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/runtime/cancel/basic-usage.ts:full"
    ```

## 취소 전파 방식

signal을 abort하면 취소가 전체 실행 스택 아래로 전파됩니다. 각 구성 요소는 주요
수명주기 지점에서 `abortSignal.aborted`를 확인하고, 취소를 감지하면 조기에 종료합니다.

| 구성 요소 | abort 시 동작 |
| :--- | :--- |
| **Runner** | 세션 가져오기 전, 플러그인 콜백 후, 이벤트 스트리밍 루프 안에서 중지합니다. |
| **LlmAgent** | 실행 단계 사이, 모델 콜백 전후, 응답 스트리밍 중에 중지합니다. |
| **LoopAgent** | 루프 반복 사이와 하위 에이전트 실행 사이에서 중지합니다. |
| **ParallelAgent** | 동시 하위 에이전트 실행 결과를 병합할 때 중지합니다. |
| **Models (Gemini)** | signal이 `config.abortSignal`을 통해 기본 Google GenAI SDK로 전달되어 진행 중인 HTTP 요청을 취소합니다. |
| **AgentTool** | signal을 하위 에이전트 runner에 전달하고 세션 생성 후 abort 여부를 확인합니다. |
| **MCPTool** | signal을 MCP 클라이언트의 `callTool` 메서드로 전달합니다. |

`InvocationContext`도 signal에 listener를 등록합니다. signal이 트리거되면
`endInvocation = true`가 자동으로 설정되어 모든 구성 요소가 종료 절차에 들어가도록
알립니다.

### 취소 시 동작

`AbortSignal`이 트리거되면 다음 동작이 적용됩니다.

- **정상 종료:** `runner.runAsync()`가 반환한 async generator는 오류를 던지지 않고
  완료됩니다. 즉, 이벤트 yield를 중단합니다.
- **커밋된 이벤트 유지:** abort 전에 Runner가 이미 yield하고 처리한 이벤트는 세션
  기록에 계속 커밋되어 있습니다.
- **부분 이벤트 없음:** 진행 중이었지만 아직 yield되지 않은 이벤트는 폐기됩니다.
- **리소스 정리:** Gemini API로 보내진 진행 중인 LLM 요청은 SDK의 기본 `AbortSignal`
  지원을 통해 취소되어 네트워크 리소스를 해제합니다.

## 고급 예시

다음 예시는 기본 `AbortController` 사용법을 넘어서는 추가 취소 패턴을 보여줍니다.

### 타임아웃으로 취소

`AbortSignal.timeout()`을 사용하면 지정된 시간 후 에이전트 실행을 자동으로 취소할 수
있습니다. 에이전트 실행에 시간 제한을 강제할 때 유용합니다.

시작하기 예시와 동일한 에이전트 및 runner 설정을 사용하고, `const controller` 이후의
모든 코드를 다음으로 바꿉니다.

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/runtime/cancel/timeout.ts:run"
    ```

`AbortSignal.any()`를 사용해 타임아웃과 프로그래밍 방식 취소를 결합할 수도 있습니다.
동일한 설정에서 `const controller` 이후의 모든 코드를 다음으로 바꿉니다.

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/runtime/cancel/combined-signal.ts:run"
    ```

### 커스텀 도구의 AbortSignal

`runner.runAsync()`에 `AbortSignal`을 전달하면 커스텀 도구 내부의
`toolContext.abortSignal`에서도 사용할 수 있습니다. 다음 예시는 커스텀 도구 안에서
abort signal을 확인하는 패턴을 보여줍니다.

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/runtime/cancel/custom-tool.ts:tool"
    ```
