# 콜백 유형

<div class="language-support-tag">
   <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK는 에이전트 실행 수명 주기의 다양한 지점에서 실행되는 여러 유형의 콜백을 제공합니다.

## 에이전트 수명 주기 콜백

이러한 콜백은 `BaseAgent`를 상속하는 *모든* 에이전트(`LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent` 등)에서 사용할 수 있습니다.

??? note "Python: 콜백 파라미터 이름"

    Python에서 ADK는 콜백 함수가 받는 파라미터 이름을 검사합니다. 임의의 이름(예: `ctx`)을 사용할 수 없으며, 아래에 나열된 정확한 이름을 사용해야 합니다.

    ```python
    # 올바름
    def before_agent_callback(callback_context):
        ...

    # 잘못됨
    def before_agent_callback(ctx):
        ...
    ```

    | 콜백 | 필수 파라미터 이름 |
    |---|---|
    | `before_agent_callback` | `callback_context` |
    | `after_agent_callback` | `callback_context` |
    | `before_model_callback` | `callback_context`, `llm_request` |
    | `after_model_callback` | `callback_context`, `llm_response` |
    | `on_model_error_callback` | `callback_context`, `llm_request`, `error` |
    | `before_tool_callback` | `tool`, `args`, `tool_context` |
    | `after_tool_callback` | `tool`, `args`, `tool_context`, `tool_response` |
    | `on_tool_error_callback` | `tool`, `args`, `tool_context`, `error` |

    모든 `BaseAgent`에 존재하는 필드는 `before_agent_callback`과 `after_agent_callback`뿐입니다. 이 테이블의 6가지 모델 및 도구 콜백은 `LlmAgent`에만 존재하는 필드입니다.

??? note "Python: `async` 콜백 및 콜백 목록"

    Python에서 콜백은 일반 `def` 또는 `async def`일 수 있습니다. ADK는 어느 쪽이든 결과를 await합니다.

    모든 콜백 필드는 단일 함수 대신 함수 목록도 허용합니다. ADK는 나열된 순서대로 호출하고 결과를 반환하는 첫 번째 콜백에서 중지합니다. 해당 값이 콜백 결과가 되고 나머지 콜백은 건너뜁니다. 결과로 간주되는 항목은 제품군에 따라 다릅니다. 에이전트, 모델, 도구의 6개 `before_`/`after_` 훅은 *truthy*(참으로 평가되는) 값에서만 중지되므로 `None` 또는 빈 `dict`와 같은 기타 falsy 값을 반환하는 콜백은 다음 콜백이 실행되도록 합니다. `on_model_error_callback` 및 `on_tool_error_callback`은 `None`이 아닌 모든 값에서 중지되므로 `on_tool_error_callback`의 빈 `dict`는 체인을 종료하고 예외를 억제하며 도구 결과가 됩니다.

    에이전트의 콜백 필드에 목록을 할당합니다:

    ```python
    root_agent = LlmAgent(
        name="my_agent",
        model="gemini-flash-latest",
        before_model_callback=[check_policy, log_request],
    )
    ```

### Before Agent 콜백

**시점:** 에이전트의 `_run_async_impl`(또는 `_run_live_impl`) 메서드가 실행되기 *직전에* 호출됩니다. 에이전트의 `InvocationContext`가 생성된 후, 하지만 핵심 로직이 시작되기 *전에* 실행됩니다.

**목적:** 이 특정 에이전트 실행에만 필요한 리소스나 상태를 설정하거나, 실행이 시작되기 전에 세션 상태(`callback_context.state`)에 대한 유효성 검사를 수행하거나, 에이전트 활동의 진입점을 로깅하거나, 핵심 로직이 사용하기 전에 호출 컨텍스트를 수정하는 데 이상적입니다.

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/before_agent_callback.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/callbacks/before_agent_callback.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:imports"


        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:before_agent_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeAgentCallbackExample.java:init"
        ```

**`before_agent_callback` 예제에 대한 참고사항:**

* **예제가 보여주는 것:** 이 예제는 `before_agent_callback`을 보여줍니다. 이 콜백은 주어진 요청에 대해 에이전트의 메인 처리 로직이 시작되기 *직전에* 실행됩니다.
* **작동 방식:** 콜백 함수(`check_if_agent_should_run`)는 세션 상태의 플래그(`skip_llm_agent`)를 확인합니다.
    * 플래그가 `True`이면 콜백은 `types.Content` 객체를 반환합니다. 이는 ADK 프레임워크에 에이전트의 메인 실행을 완전히 **건너뛰고** 콜백이 반환한 콘텐츠를 최종 응답으로 사용하도록 지시합니다.
    * 플래그가 `False`이거나 설정되지 않은 경우 콜백은 `None` 또는 빈 객체를 반환합니다. 이는 ADK 프레임워크에 에이전트의 일반적인 실행(이 경우 LLM 호출)을 **진행**하도록 지시합니다.
* **예상 결과:** 두 가지 시나리오가 나타납니다:
    1. `skip_llm_agent: True` 상태의 세션에서는 에이전트의 LLM 호출이 우회되고 출력이 콜백에서 직접 생성됩니다("Agent... skipped...").
    2. 해당 상태 플래그가 *없는* 세션에서는 콜백이 에이전트 실행을 허용하며 LLM의 실제 응답(예: "Hello!")을 볼 수 있습니다.
* **콜백의 이해:** 이는 `before_` 콜백이 주요 단계 *전에* 실행을 가로채고 검사(예: 상태, 입력 유효성 검사, 권한)를 기반으로 실행을 방지할 수 있는 **게이트키퍼(gatekeeper)** 역할을 수행함을 보여줍니다.

### After Agent 콜백

**시점:** 에이전트의 `_run_async_impl`(또는 `_run_live_impl`) 메서드가 성공적으로 완료된 *직후에* 호출됩니다. `before_agent_callback`이 콘텐츠를 반환하여 에이전트를 건너뛴 경우에는 실행되지 않습니다. Python에서는 에이전트 실행 중 `end_invocation`을 설정한 경우에도 건너뛰지만 이는 `run_async` 경로에만 해당됩니다. `run_live`는 `_run_live_impl`이 끝난 후 `end_invocation`을 다시 확인하지 않으므로 콜백이 계속 실행됩니다.

**목적:** 정리 작업, 실행 후 유효성 검사, 에이전트 활동 완료 로깅 또는 최종 상태 수정에 유용합니다.

!!! note "After Agent 콜백의 출력 수정 제한사항"

    `after_agent_callback`은 응답 출력을 완전히 대체할 수 없습니다. 에이전트가 AI 모델을 여러 번 호출하고 여러 이벤트를 내보냈을 수 있기 때문입니다. 따라서 출력 수정은 허용되지 않지만 추가 콘텐츠를 *추가(append)*할 수는 있습니다. AI 모델 응답을 변경하려면 `after_model_callback` 사용을 고려하세요.

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/after_agent_callback.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/callbacks/after_agent_callback.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:imports"


        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:after_agent_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterAgentCallbackExample.java:init"
        ```

**`after_agent_callback` 예제에 대한 참고사항:**

* **예제가 보여주는 것:** 이 예제는 `after_agent_callback`을 보여줍니다. 이 콜백은 에이전트의 메인 처리 로직이 완료되어 결과를 생성한 *직후*, 하지만 해당 결과가 확정되어 반환되기 *전에* 실행됩니다.
* **작동 방식:** 콜백 함수(`modify_output_after_agent`)는 세션 상태의 플래그(`add_concluding_note`)를 확인합니다.
    * 플래그가 `True`이면 콜백은 *새로운* `types.Content` 객체를 반환합니다. 이는 ADK 프레임워크에 콜백이 반환한 콘텐츠로 에이전트의 원본 출력을 **추가(append)**하도록 지시합니다.
    * 플래그가 `False`이거나 설정되지 않은 경우 콜백은 `None` 또는 빈 객체를 반환합니다. 이는 ADK 프레임워크에 에이전트가 생성한 원본 출력을 **사용**하도록 지시합니다.
* **예상 결과:** 두 가지 시나리오가 나타납니다:
    1. `add_concluding_note: True` 상태가 *없는* 세션에서는 콜백이 에이전트의 원래 출력("Processing complete!")이 사용되도록 허용합니다.
    2. 해당 상태 플래그가 *있는* 세션에서는 콜백이 에이전트의 원본 출력을 가로채 자체 메시지("Concluding note added...")를 추가합니다.
* **콜백의 이해:** 이 예제는 `after_` 콜백이 **후처리(post-processing)**를 어떻게 가능하게 하는지 보여줍니다. 단계의 결과를 검사하고 이를 그대로 통과시킬지 아니면 추가할지 결정할 수 있습니다. `after_agent_callback`은 에이전트의 출력을 대체할 수 없으며, 반환된 콘텐츠는 에이전트 자체 이벤트 뒤에 *추가 이벤트*로 방출됩니다.

## LLM 상호작용 콜백

이러한 콜백은 `LlmAgent`에 고유하며 대규모 언어 모델과의 상호작용에 대한 훅을 제공합니다. Python에서 `LlmAgent`는 모델 호출에서 예외가 발생할 때 실행되는 `on_model_error_callback`도 허용합니다. `LlmResponse`를 반환하면 예외가 억제되고 해당 응답이 대신 사용됩니다.

### Before Model 콜백

**시점:** `LlmAgent` 흐름 내에서 `generate_content_async`(또는 이에 상응하는) 요청이 LLM에 전송되기 직전에 호출됩니다.

**목적:** LLM으로 전달되는 요청을 검사하고 수정할 수 있습니다. 사용 사례에는 동적 지침 추가, 상태 기반의 퓨샷 예제 주입, 모델 구성 수정, 가드레일(예: 욕설 필터) 구현 또는 요청 수준 캐싱 구현이 포함됩니다.

**반환 값 효과:**
콜백이 `None`(Java의 경우 `Maybe.empty()` 객체)을 반환하면 LLM은 정상 워크플로를 계속 진행합니다. 콜백이 `LlmResponse` 객체를 반환하면 LLM 호출이 **건너뛰어집니다**. 반환된 `LlmResponse`는 마치 모델에서 직접 온 것처럼 사용됩니다. 이는 가드레일이나 캐싱을 구현하는 데 매우 강력합니다.

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/before_model_callback.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/callbacks/before_model_callback.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:imports"


        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:before_model_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeModelCallbackExample.java:init"
        ```

### After Model 콜백

**시점:** 호출한 에이전트가 추가로 처리하기 전에, LLM으로부터 응답(`LlmResponse`)을 수신한 직후에 호출됩니다.

**목적:** 원시 LLM 응답을 검사하거나 수정할 수 있습니다. 사용 사례는 다음과 같습니다:

* 모델 출력 로깅,
* 응답 재포맷팅,
* 모델이 생성한 민감한 정보 검열,
* LLM 응답에서 구조화된 데이터를 파싱하여 `callback_context.state`에 저장,
* 또는 특정 오류 코드 처리.

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/after_model_callback.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/callbacks/after_model_callback.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:imports"


        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:after_model_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterModelCallbackExample.java:init"
        ```

## 도구 실행 콜백

이러한 콜백 역시 `LlmAgent`에 고유하며 `FunctionTool` 및 `AgentTool`을 포함하여 LLM이 요청할 수 있는 도구의 실행 시점에 트리거됩니다. Python에서 `LlmAgent`는 도구에서 예외가 발생할 때 실행되는 `on_tool_error_callback`도 허용합니다. `dict`를 반환하면 예외가 억제되고 해당 `dict` 값이 도구 결과로 사용됩니다.

### Before Tool 콜백

**시점:** LLM이 함수 호출을 생성한 후 특정 도구의 `run_async` 메서드가 호출되기 직전에 호출됩니다.

**목적:** 도구 인수를 검사 및 수정하고, 실행 전에 권한 검사를 수행하고, 도구 사용 시도를 로깅하거나 도구 수준 캐싱을 구현할 수 있습니다.

**반환 값 효과:**

1. 콜백이 `None`(Java의 경우 `Maybe.empty()` 객체)을 반환하면, (잠재적으로 수정된) `args`로 도구의 `run_async` 메서드가 실행됩니다.
2. 딕셔너리(Java의 경우 `Map`)가 반환되면 도구의 `run_async` 메서드가 **건너뛰어집니다**. 반환된 딕셔너리가 도구 호출의 결과로 직접 사용됩니다. 이는 캐싱이나 도구 동작 재정의에 유용합니다.

!!! note "Python: `None`만이 도구를 실행시킵니다"

    ADK는 반환된 값을 `None`과 비교하므로 빈 `dict`도 재정의로 간주됩니다. 도구가 건너뛰어지고 `{}`가 도구 결과가 됩니다. 도구를 실행하려면 `{}`가 아닌 `None`을 반환하세요. 콜백 목록을 사용할 때 빈 `dict`는 체인을 멈추지 않고 후속 콜백이 다른 값을 반환하면 무시되므로, 이는 생성된 마지막 값에 적용됩니다.

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/before_tool_callback.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/callbacks/before_tool_callback.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:imports"
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:tool_defs"
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:before_tool_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeToolCallbackExample.java:init"
        ```

### After Tool 콜백

**시점:** 도구의 `run_async` 메서드가 성공적으로 완료된 직후에 호출됩니다.

**목적:** LLM으로 다시 전송되기 전(요약된 후일 수 있음)에 도구의 결과를 검사하고 수정할 수 있습니다. 도구 결과를 로깅하거나, 결과를 후처리 또는 포맷팅하거나, 결과의 특정 부분을 세션 상태에 저장하는 데 유용합니다.

**반환 값 효과:**

1. 콜백이 `None`(Java의 경우 `Maybe.empty()` 객체)을 반환하면, 원래의 `tool_response`가 사용됩니다.
2. 새로운 딕셔너리가 반환되면, 이는 원래의 `tool_response`를 **대체합니다**. 이를 통해 LLM이 보게 될 결과를 수정하거나 필터링할 수 있습니다.

!!! note "Python: `tool_response` 유형 및 반환 값"

    ADK는 콜백이 실행된 *후*에만 `dict`가 아닌 결과를 `{"result": <value>}`로 래핑하므로, `-> str`로 어노테이션된 도구는 `after_tool_callback`에 `dict`가 아닌 `str`을 전달합니다. 딕셔너리 메서드를 호출하기 전에 유형을 확인하세요.

    ADK는 또한 반환된 값을 `None`과 비교하므로, `{}`를 반환하면 도구 응답이 `{}`로 대체됩니다. 원본을 유지하려면 `None`을 반환하세요.

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/after_tool_callback.py"
        ```

    === "TypeScript"

        ```typescript
        --8<-- "examples/typescript/snippets/callbacks/after_tool_callback.ts"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:imports"
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:tool_defs"
        --8<-- "examples/go/snippets/callbacks/types_of_callbacks/main.go:after_tool_example"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AfterToolCallbackExample.java:init"
        ```
