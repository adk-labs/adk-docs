# 에이전트 간 라우팅

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-typescript">TypeScript v1.0.0</span><span class="lst-preview">실험적</span>
</div>

!!! example "실험적"

    에이전트 라우팅은 실험적 기능이며 향후 릴리스에서 변경될 수 있습니다.
    [의견](https://github.com/google/adk-js/issues/new?template=feature_request.md)을
    환영합니다.

서로 다른 작업을 위한 에이전트를 만들 때, 각 호출을 처리할 에이전트를 런타임에
선택하는 라우팅 함수를 정의할 수 있습니다. `RoutedAgent`는 이 기능을 제공하며,
오류 발생 시 에이전트 폴백, A/B 테스트, 계획 모드, 입력 복잡도 기반 자동 라우팅을
가능하게 합니다. 선택된 에이전트가 출력을 생성하기 전에 실패하면, 라우팅 함수가 오류
컨텍스트와 함께 다시 호출되어 폴백을 선택할 수 있습니다.

`RoutedAgent`는 `SequentialAgent` 또는 `ParallelAgent` 같은
[워크플로 에이전트](workflow-agents/index.md)와 다릅니다. 워크플로 에이전트는
여러 에이전트를 고정된 패턴으로 오케스트레이션합니다. 또한 LLM이 전달할 에이전트를
결정하는 [LLM 기반 위임](multi-agents.md#b-llm-driven-delegation-agent-transfer)과도
다릅니다. `RoutedAgent`에서는 개발자가 명시적인 라우팅 함수를 작성해 호출마다
**하나의** 에이전트를 선택합니다. 모델 수준 라우팅은
[모델 라우팅](models/routing.md)을 참조하세요.

## 라우팅 작동 방식 {#how-routing-works}

`RoutedAgent`와 [`RoutedLlm`](models/routing.md)은 모두 선택과 페일오버를 처리하는
공유 라우팅 유틸리티를 기반으로 합니다.

라우터 함수는 사용 가능한 에이전트 맵과 현재 컨텍스트를 받고, 실행할 에이전트의 키를
반환합니다. 동기 또는 비동기 함수일 수 있습니다.

=== "TypeScript"

    ```typescript
    type AgentRouter = (
      agents: Readonly<Record<string, BaseAgent>>,
      context: InvocationContext,
      errorContext?: { failedKeys: ReadonlySet<string>; lastError: unknown },
    ) => Promise<string | undefined> | string | undefined;
    ```

**`agents` 매개변수**는 명시적 키가 있는 `Record<string, BaseAgent>` 또는 에이전트
배열을 받을 수 있습니다. 배열을 제공하면 각 에이전트의 `name` 속성이 키로 사용됩니다.

**페일오버 동작:**

- 라우터는 초기 선택을 위해 먼저 `errorContext` 없이 호출됩니다.
- 선택된 에이전트가 **이벤트를 하나도 yield하기 전에** 오류를 던지면, 라우터가
  `failedKeys`와 `lastError`를 포함한 `errorContext`와 함께 다시 호출됩니다.
- 선택된 에이전트가 **이벤트를 yield한 후** 오류를 던지면, 부분 결과가 이미
  방출되었기 때문에 오류가 재시도 없이 직접 전파됩니다.
- 이미 시도한 키는 다시 선택할 수 없습니다. 라우터가 이전에 실패한 키를 반환하면
  오류가 전파됩니다.
- 라우터가 `undefined`를 반환하면 라우팅이 중단되고 마지막 오류가 던져집니다.

## 기본 사용법 {#basic-usage}

여러 에이전트를 만들고, 키를 반환하는 라우터 함수를 정의한 다음, 이를
`RoutedAgent`로 감쌉니다. 다음 예시는 호출 사이에 변경될 수 있는 외부 설정값에 따라
두 에이전트 사이를 라우팅합니다.

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/routing/basic-usage.ts:full"
    ```

다음 호출 전에 `config.selectedAgent`를 `'agent_b'`로 변경하면 다른 에이전트로
라우팅됩니다.

## 오류 시 폴백

에이전트가 실패하면 라우터가 `errorContext`와 함께 다시 호출되어 폴백을 선택할 수
있습니다. 페일오버는 에이전트가 이벤트를 yield하기 전에 실패한 경우에만 적용됩니다
([라우팅 작동 방식](#how-routing-works) 참조). 다음 예시는 실패한 에이전트를 다시
선택하지 않도록 `errorContext.failedKeys`를 확인합니다.

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/routing/fallback.ts:config"
    ```

## 계획 모드

라우터는 외부 상태를 읽어 서로 다른 지침, 모델, 도구를 가진 에이전트 중 하나를
선택할 수 있습니다. 이를 통해 에이전트가 동적으로 동작을 전환하는 계획 모드를 구현할
수 있습니다. 예를 들어 기본 에이전트는 읽기/쓰기 도구를 가질 수 있고, 계획 에이전트는
읽기 전용 접근으로 제한되며 분석을 위해 더 강력한 모델을 사용할 수 있습니다.

다음 예시는 다른 `RoutedAgent` 구성을 보여줍니다. 전체 runner 설정은
[기본 사용법](#basic-usage)을 참조하세요.

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/routing/planning-mode.ts:config"
    ```

호출 전에 `planningMode = true`로 설정하면 제한된 도구 세트와 다른 지침을 가진 계획
에이전트로 라우팅됩니다.

## 복잡도 기반 자동 라우팅

라우터 함수는 경량 분류 모델을 호출해 입력을 분류하고 그 결과에 따라 다른 에이전트로
라우팅할 수 있습니다. 라우터는 비동기일 수 있으므로, 에이전트를 선택하기 전에 내부에서
LLM 호출을 수행할 수 있습니다.

다음 예시는 다른 `RoutedAgent` 구성을 보여줍니다. 전체 runner 설정은
[기본 사용법](#basic-usage)을 참조하세요.

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/routing/auto-routing.ts:config"
    ```
