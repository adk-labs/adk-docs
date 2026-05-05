# 모델 간 라우팅

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-typescript">TypeScript v1.0.0</span><span class="lst-preview">실험적</span>
</div>

!!! example "실험적"

    모델 라우팅은 실험적 기능이며 향후 릴리스에서 변경될 수 있습니다.
    [의견](https://github.com/google/adk-js/issues/new?template=feature_request.md)을
    환영합니다.

`LlmAgent`는 기본적으로 하나의 모델을 사용합니다. 요청마다 서로 다른 모델 중
하나를 동적으로 선택해야 한다면, 사용할 모델을 고르는 라우팅 함수를 정의할 수
있습니다. `RoutedLlm`은 이 기능을 제공하며, 오류 발생 시 모델 폴백, 모델 간
A/B 테스트, 입력 복잡도에 따른 자동 라우팅을 가능하게 합니다. 선택된 모델이
출력을 생성하기 전에 실패하면, 오류 컨텍스트와 함께 라우팅 함수가 다시 호출되어
다른 모델을 선택할 수 있습니다.

`RoutedLlm`을 `LlmAgent`의 `model` 매개변수로 전달합니다. 라우트마다 모델만
달라지는 경우 `RoutedLlm`을 사용하세요. 지침, 도구 또는 하위 에이전트도 함께
전환해야 한다면 대신 [`RoutedAgent`](../routing.md)를 사용하세요.

## 라우팅 작동 방식

`LlmRouter` 함수는 사용 가능한 모델 맵과 현재 `LlmRequest`를 받고, 사용할 모델의
키를 반환합니다.

=== "TypeScript"

    ```typescript
    type LlmRouter = (
      models: Readonly<Record<string, BaseLlm>>,
      request: LlmRequest,
      errorContext?: { failedKeys: ReadonlySet<string>; lastError: unknown },
    ) => Promise<string | undefined> | string | undefined;
    ```

`models` 매개변수는 명시적 키가 있는 `Record<string, BaseLlm>` 또는 `BaseLlm`
인스턴스 배열을 받을 수 있습니다. 배열을 제공하면 각 모델의 이름이 키로 사용됩니다.

페일오버는 [`RoutedAgent`](../routing.md#how-routing-works)와 동일한 규칙을
따릅니다. 선택된 모델이 응답을 하나도 yield하기 전에 실패한 경우에만 라우터가
`errorContext`와 함께 다시 호출됩니다. yield 이후의 오류는 재시도 없이 전파됩니다.
라우터는 재시도를 중단하고 마지막 오류를 전파하도록 `undefined`를 반환할 수 있습니다.

**실시간 연결:** `RoutedLlm.connect()`는 연결 시점에 모델을 선택합니다. 실시간
연결이 설정된 후에는 스트림 중간에 모델을 전환할 수 없습니다.

## 기본 사용법

다음 예시는 먼저 기본 모델을 시도하고 기본 모델이 실패하면 보조 모델로 폴백하는
`RoutedLlm`을 만듭니다. 라우터는 실패한 모델을 다시 선택하지 않도록
`errorContext.failedKeys`를 확인합니다.

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/agents/models/routing/basic-usage.ts:full"
    ```
