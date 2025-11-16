# 콜백의 종류

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

프레임워크는 에이전트 실행의 다양한 단계에서 트리거되는 여러 종류의 콜백을 제공합니다. 각 콜백이 언제 실행되고 어떤 컨텍스트를 받는지 이해하는 것이 효과적인 사용의 핵심입니다.

## 에이전트 생명주기 콜백

이 콜백들은 `BaseAgent`를 상속하는 *모든* 에이전트(`LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent` 등 포함)에서 사용할 수 있습니다.

!!! Note
    특정 메서드 이름이나 반환 타입은 SDK 언어에 따라 약간 다를 수 있습니다(예: Python에서는 `None`, Java에서는 `Optional.empty()` 또는 `Maybe.empty()` 반환). 자세한 내용은 각 언어별 API 문서를 참조하세요.

### Before Agent 콜백

**시점:** 에이전트의 `_run_async_impl`(또는 `_run_live_impl`) 메서드가 실행되기 *직전에* 호출됩니다. 에이전트의 `InvocationContext`가 생성된 후, 하지만 핵심 로직이 시작되기 *전에* 실행됩니다.

**목적:** 이 특정 에이전트 실행에만 필요한 리소스나 상태를 설정하거나, 실행이 시작되기 전에 세션 상태(`callback_context.state`)에 대한 유효성 검사를 수행하거나, 에이전트 활동의 진입점을 로깅하거나, 핵심 로직이 사용하기 전에 호출 컨텍스트를 수정하는 데 이상적입니다.

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_agent_callback.py"
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

**`before_agent_callback` 예제에 대한 참고:**

*   **보여주는 내용:** 이 예제는 `before_agent_callback`을 보여줍니다. 이 콜백은 주어진 요청에 대해 에이전트의 주 처리 로직이 시작되기 *직전에* 실행됩니다.
*   **동작 방식:** 콜백 함수(`check_if_agent_should_run`)는 세션 상태의 `skip_llm_agent` 플래그를 확인합니다.
    *   플래그가 `True`이면 콜백은 `types.Content` 객체를 반환합니다. 이는 ADK 프레임워크에게 에이전트의 주 실행을 **완전히 건너뛰고** 콜백이 반환한 콘텐츠를 최종 응답으로 사용하라고 지시합니다.
    *   플래그가 `False`(또는 설정되지 않음)이면 콜백은 `None` 또는 빈 객체를 반환합니다. 이는 ADK 프레임워크에게 에이전트의 정상적인 실행(이 경우 LLM 호출)을 **계속 진행하라고** 지시합니다.
*   **예상 결과:** 두 가지 시나리오를 볼 수 있습니다:
    1. `skip_llm_agent: True` 상태가 있는 세션에서는 에이전트의 LLM 호출이 건너뛰어지고, 출력이 콜백에서 직접 나옵니다("Agent... skipped...").
    2. 해당 상태 플래그가 없는 세션에서는 콜백이 에이전트 실행을 허용하고, LLM의 실제 응답(예: "Hello!")을 보게 됩니다.
*   **콜백의 이해:** 이는 `before_` 콜백이 어떻게 주요 단계 *전에* 실행을 가로채서 상태, 입력 유효성 검사, 권한 등의 확인에 따라 실행을 막을 수 있게 해주는 **문지기(gatekeeper)** 역할을 하는지 보여줍니다.

### After Agent 콜백

**시점:** 에이전트의 `_run_async_impl`(또는 `_run_live_impl`) 메서드가 성공적으로 완료된 *직후에* 호출됩니다. `before_agent_callback`이 콘텐츠를 반환하여 에이전트가 건너뛰어졌거나, 에이전트 실행 중에 `end_invocation`이 설정된 경우에는 실행되지 *않습니다*.

**목적:** 정리 작업, 실행 후 검증, 에이전트 활동 완료 로깅, 최종 상태 수정, 또는 에이전트의 최종 출력 보강/대체에 유용합니다.

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_agent_callback.py"
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

**`after_agent_callback` 예제에 대한 참고:**

*   **보여주는 내용:** 이 예제는 `after_agent_callback`을 보여줍니다. 이 콜백은 에이전트의 주 처리 로직이 완료되어 결과를 생성한 *직후*, 하지만 그 결과가 확정되어 반환되기 *전에* 실행됩니다.
*   **동작 방식:** 콜백 함수(`modify_output_after_agent`)는 세션 상태의 `add_concluding_note` 플래그를 확인합니다.
    *   플래그가 `True`이면 콜백은 *새로운* `types.Content` 객체를 반환합니다. 이는 ADK 프레임워크에게 에이전트의 원본 출력을 콜백이 반환한 콘텐츠로 **대체하도록** 지시합니다.
    *   플래그가 `False`(또는 설정되지 않음)이면 콜백은 `None` 또는 빈 객체를 반환합니다. 이는 ADK 프레임워크에게 에이전트가 생성한 원본 출력을 **사용하도록** 지시합니다.
*   **예상 결과:** 두 가지 시나리오를 볼 수 있습니다:
    1. `add_concluding_note: True` 상태가 없는 세션에서는 콜백이 에이전트의 원본 출력("Processing complete!")을 사용하도록 허용합니다.
    2. 해당 상태 플래그가 있는 세션에서는 콜백이 에이전트의 원본 출력을 가로채서 자신의 메시지("Concluding note added...")로 대체합니다.
*   **콜백의 이해:** 이는 `after_` 콜백이 어떻게 **후처리** 또는 **수정**을 가능하게 하는지 보여줍니다. 특정 단계(에이전트 실행)의 결과를 검사하고, 자체 로직에 따라 그대로 통과시킬지, 변경할지, 또는 완전히 대체할지 결정할 수 있습니다.

## LLM 상호작용 콜백

이 콜백들은 `LlmAgent`에 특화되어 있으며 거대 언어 모델과의 상호작용 지점에 연결됩니다.

### Before Model 콜백

**시점:** `LlmAgent`의 흐름 내에서 `generate_content_async`(또는 동등한) 요청이 LLM에 전송되기 직전에 호출됩니다.

**목적:** LLM으로 가는 요청을 검사하고 수정할 수 있습니다. 사용 사례로는 동적 지침 추가, 상태에 기반한 퓨샷(few-shot) 예제 주입, 모델 설정 수정, 가드레일(비속어 필터 등) 구현, 또는 요청 수준 캐싱 구현 등이 있습니다.

**반환 값 효과:**  
콜백이 `None`(Java의 경우 `Maybe.empty()` 객체)을 반환하면 LLM은 정상적인 워크플로우를 계속합니다. 콜백이 `LlmResponse` 객체를 반환하면 LLM 호출은 **건너뛰어집니다**. 반환된 `LlmResponse`는 마치 모델에서 직접 온 것처럼 사용됩니다. 이는 가드레일이나 캐싱을 구현할 때 매우 강력합니다.

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_model_callback.py"
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

**시점:** LLM으로부터 응답(`LlmResponse`)을 받은 직후, 호출한 에이전트가 이를 추가로 처리하기 전에 호출됩니다.

**목적:** 원본 LLM 응답을 검사하거나 수정할 수 있습니다. 사용 사례는 다음과 같습니다:

*   모델 출력 로깅,
*   응답 형식 재지정,
*   모델이 생성한 민감 정보 검열,
*   LLM 응답에서 구조화된 데이터를 파싱하여 `callback_context.state`에 저장하기,
*   또는 특정 에러 코드 처리.

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_model_callback.py"
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

이 콜백들 역시 `LlmAgent`에 특화되어 있으며, LLM이 요청할 수 있는 도구(`FunctionTool`, `AgentTool` 등 포함)의 실행 전후에 트리거됩니다.

### Before Tool 콜백

**시점:** LLM이 특정 도구에 대한 함수 호출을 생성한 후, 해당 도구의 `run_async` 메서드가 호출되기 직전에 호출됩니다.

**목적:** 도구 인자를 검사하고 수정하거나, 실행 전 권한 확인을 수행하거나, 도구 사용 시도를 로깅하거나, 도구 수준의 캐싱을 구현할 수 있습니다.

**반환 값 효과:**

1.  콜백이 `None`(Java의 경우 `Maybe.empty()` 객체)을 반환하면, 도구의 `run_async` 메서드가 (수정되었을 수 있는) `args`와 함께 실행됩니다.
2.  딕셔너리(Java의 경우 `Map`)가 반환되면, 도구의 `run_async` 메서드는 **건너뛰어집니다**. 반환된 딕셔너리가 도구 호출의 결과로 직접 사용됩니다. 이는 캐싱이나 도구 동작을 재정의하는 데 유용합니다.

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/before_tool_callback.py"
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

1.  콜백이 `None`(Java의 경우 `Maybe.empty()` 객체)을 반환하면, 원래의 `tool_response`가 사용됩니다.
2.  새로운 딕셔너리가 반환되면, 이는 원래의 `tool_response`를 **대체합니다**. 이를 통해 LLM이 보게 될 결과를 수정하거나 필터링할 수 있습니다.

??? "Code"
    === "Python"
    
        ```python
        --8<-- "examples/python/snippets/callbacks/after_tool_callback.py"
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
