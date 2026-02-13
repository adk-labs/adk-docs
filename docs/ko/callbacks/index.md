# 콜백: 에이전트 행동 관찰, 사용자 정의 및 제어

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

콜백(Callbacks)은 ADK의 핵심 기능으로, 에이전트의 실행 프로세스에 연결하여 개입할 수 있는 강력한 메커니즘을 제공합니다. 콜백을 사용하면 핵심 ADK 프레임워크 코드를 수정하지 않고도 미리 정의된 특정 지점에서 에이전트의 행동을 관찰하고, 사용자 정의하며, 심지어 제어할 수 있습니다.

**콜백이란 무엇인가요?** 본질적으로 콜백은 여러분이 정의하는 표준 함수입니다. 그리고 에이전트를 생성할 때 이 함수들을 에이전트와 연결합니다. ADK 프레임워크는 주요 단계에서 여러분의 함수를 자동으로 호출하여 관찰하거나 개입할 수 있도록 합니다. 에이전트 프로세스 중의 체크포인트처럼 생각할 수 있습니다.

*   **에이전트가 요청에 대한 주요 작업을 시작하기 전과 완료한 후:** 에이전트에게 어떤 작업(예: 질문에 답변하기)을 요청하면, 에이전트는 응답을 파악하기 위해 내부 로직을 실행합니다.
    *   `Before Agent` 콜백은 특정 요청에 대한 이 주요 작업이 시작되기 *직전에* 실행됩니다.
    *   `After Agent` 콜백은 에이전트가 해당 요청에 대한 모든 단계를 마치고 최종 결과를 준비한 *직후*, 하지만 결과가 반환되기 바로 전에 실행됩니다.
    *   이 "주요 작업"은 단일 요청을 처리하기 위한 에이전트의 *전체* 프로세스를 포함합니다. 이는 LLM 호출 결정, 실제 LLM 호출, 도구 사용 결정, 도구 사용, 결과 처리, 그리고 최종적으로 답변을 종합하는 과정을 포함할 수 있습니다. 이 콜백들은 본질적으로 입력을 받아 해당 상호작용에 대한 최종 출력을 생성하기까지의 전체 시퀀스를 감싸는 역할을 합니다.
*   **거대 언어 모델(LLM)에 요청을 보내기 전 또는 응답을 받은 후:** `Before Model`, `After Model` 콜백은 LLM으로 가고 오는 데이터를 구체적으로 검사하거나 수정할 수 있게 해줍니다.
*   **도구(Python 함수나 다른 에이전트 등)를 실행하기 전 또는 완료한 후:** 마찬가지로, `Before Tool`, `After Tool` 콜백은 에이전트가 호출한 도구의 실행을 중심으로 제어 지점을 제공합니다.

![intro_components.png](../assets/callback_flow.png)

**왜 사용해야 하나요?** 콜백은 상당한 유연성을 제공하며 고급 에이전트 기능을 가능하게 합니다.

*   **관찰 및 디버깅:** 모니터링 및 문제 해결을 위해 중요한 단계에서 상세 정보를 기록합니다.
*   **사용자 정의 및 제어:** 에이전트를 통과하는 데이터(LLM 요청이나 도구 결과 등)를 수정하거나, 자체 로직에 따라 특정 단계를 완전히 건너뛸 수 있습니다.
*   **가드레일 구현:** 안전 규칙을 강제하고, 입/출력을 검증하거나, 허용되지 않는 작업을 방지합니다.
*   **상태 관리:** 실행 중에 에이전트의 세션 상태를 읽거나 동적으로 업데이트합니다.
*   **통합 및 향상:** 외부 작업(API 호출, 알림)을 트리거하거나 캐싱과 같은 기능을 추가합니다.

!!! tip
    보안 가드레일과 정책을 구현할 때는 콜백보다 모듈성과 유연성이 더 좋은
    ADK 플러그인을 사용하세요. 자세한 내용은
    [보안 가드레일을 위한 콜백 및 플러그인](/adk-docs/ko/safety/#callbacks-and-plugins-for-security-guardrails)을 참조하세요.

**어떻게 추가하나요:**

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/callback_basic.py:callback_basic"
        ```

    === "Go"

        ```go
        --8<-- "examples/go/snippets/callbacks/main.go:imports"


        --8<-- "examples/go/snippets/callbacks/main.go:callback_basic"
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/AgentWithBeforeModelCallback.java:init"
        ```

## 콜백 메커니즘: 가로채기와 제어

ADK 프레임워크가 콜백이 실행될 수 있는 지점(예: LLM을 호출하기 직전)에 도달하면, 해당 에이전트에 대해 상응하는 콜백 함수를 제공했는지 확인합니다. 만약 제공했다면 프레임워크는 여러분의 함수를 실행합니다.

**컨텍스트가 중요합니다:** 콜백 함수는 독립적으로 호출되지 않습니다. 프레임워크는 특별한 **컨텍스트 객체**(`CallbackContext` 또는 `ToolContext`)를 인수로 제공합니다. 이 객체들은 호출 세부 정보, 세션 상태, 그리고 아티팩트나 메모리와 같은 서비스에 대한 참조를 포함하여 에이전트 실행의 현재 상태에 대한 중요한 정보를 담고 있습니다. 여러분은 이 컨텍스트 객체를 사용하여 상황을 이해하고 프레임워크와 상호작용합니다. (자세한 내용은 "컨텍스트 객체" 전용 섹션을 참조하세요).

**흐름 제어 (핵심 메커니즘):** 콜백의 가장 강력한 측면은 **반환 값**이 에이전트의 후속 작업에 어떻게 영향을 미치는지에 있습니다. 이를 통해 실행 흐름을 가로채고 제어할 수 있습니다.

1.  **`return None` (기본 동작 허용):**

    *   특정 반환 타입은 언어에 따라 다를 수 있습니다. Java에서는 `Optional.empty()`가 이에 해당합니다. 언어별 지침은 API 문서를 참조하세요.
    *   이는 콜백이 자신의 작업(예: 로깅, 검사, `llm_request`와 같은 *변경 가능한* 입력 인수의 약간의 수정)을 마쳤으며 ADK 에이전트가 **정상적인 작업을 계속 진행해야 함**을 알리는 표준 방식입니다.
    *   `before_*` 콜백(`before_agent`, `before_model`, `before_tool`)의 경우 `None`을 반환하면 다음 단계(에이전트 로직 실행, LLM 호출, 도구 실행)가 발생합니다.
    *   `after_*` 콜백(`after_agent`, `after_model`, `after_tool`)의 경우 `None`을 반환하면 바로 이전 단계에서 생성된 결과(에이전트의 출력, LLM의 응답, 도구의 결과)가 그대로 사용됩니다.

2.  **`return <특정 객체>` (기본 동작 재정의):**

    *   `None` 대신 *특정 타입의 객체*를 반환하는 것은 ADK 에이전트의 기본 동작을 **재정의(override)**하는 방법입니다. 프레임워크는 여러분이 반환한 객체를 사용하고, 정상적으로 뒤따랐을 단계를 *건너뛰거나* 방금 생성된 결과를 *대체*합니다.
    *   **`before_agent_callback` → `types.Content`**: 에이전트의 주 실행 로직(`_run_async_impl` / `_run_live_impl`)을 건너뜁니다. 반환된 `Content` 객체는 즉시 해당 턴에 대한 에이전트의 최종 출력으로 처리됩니다. 간단한 요청을 직접 처리하거나 접근 제어를 강제하는 데 유용합니다.
    *   **`before_model_callback` → `LlmResponse`**: 외부 거대 언어 모델 호출을 건너뜁니다. 반환된 `LlmResponse` 객체는 마치 LLM의 실제 응답인 것처럼 처리됩니다. 입력 가드레일 구현, 프롬프트 검증, 또는 캐시된 응답을 제공하는 데 이상적입니다.
    *   **`before_tool_callback` → `dict` 또는 `Map`**: 실제 도구 함수(또는 하위 에이전트)의 실행을 건너뜁니다. 반환된 `dict`는 도구 호출의 결과로 사용되며, 이는 일반적으로 LLM에 다시 전달됩니다. 도구 인자 검증, 정책 제한 적용, 또는 모의/캐시된 도구 결과를 반환하는 데 완벽합니다.
    *   **`after_agent_callback` → `types.Content`**: 에이전트의 실행 로직이 방금 생성한 `Content`를 *대체*합니다.
    *   **`after_model_callback` → `LlmResponse`**: LLM으로부터 받은 `LlmResponse`를 *대체*합니다. 출력 내용을 정제하거나, 표준 면책 조항을 추가하거나, LLM의 응답 구조를 수정하는 데 유용합니다.
    *   **`after_tool_callback` → `dict` 또는 `Map`**: 도구가 반환한 `dict` 결과를 *대체*합니다. 도구 출력을 LLM에 다시 보내기 전에 후처리하거나 표준화할 수 있습니다.

**개념적 코드 예제 (가드레일):**

이 예제는 `before_model_callback`을 사용한 가드레일의 일반적인 패턴을 보여줍니다.

??? "Code"
    === "Python"

        ```python
        --8<-- "examples/python/snippets/callbacks/before_model_callback.py"
        ```

    === "Go"
        ```go
        --8<-- "examples/go/snippets/callbacks/main.go:imports"


        --8<-- "examples/go/snippets/callbacks/main.go:guardrail_init"
        ```

    === "Java"
        ```java
        --8<-- "examples/java/snippets/src/main/java/callbacks/BeforeModelGuardrailExample.java:init"
        ```

`None`을 반환하는 것과 특정 객체를 반환하는 것의 차이를 이해함으로써 에이전트의 실행 경로를 정밀하게 제어할 수 있으며, 이는 ADK로 정교하고 신뢰할 수 있는 에이전트를 구축하는 데 있어 콜백을 필수적인 도구로 만들어 줍니다.