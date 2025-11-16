# 상태(State): 세션의 스크래치패드

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

각 `Session`(대화 스레드) 내에서 **`state`** 속성은 해당 특정 상호작용을 위한 에이전트의 전용 스크래치패드(임시 작업 공간)처럼 작동합니다. `session.events`가 전체 기록을 담고 있는 반면, `session.state`는 에이전트가 대화 *중에* 필요한 동적 세부 정보를 저장하고 업데이트하는 곳입니다.

## `session.state`란 무엇인가?

개념적으로, `session.state`는 키-값 쌍을 담고 있는 컬렉션(딕셔너리 또는 Map)입니다. 에이전트가 현재 대화를 효과적으로 만들기 위해 기억하거나 추적해야 하는 정보를 위해 설계되었습니다:

* **상호작용 개인화:** 이전에 언급된 사용자 선호도 기억 (예: `'user_preference_theme': 'dark'`).
* **작업 진행 상황 추적:** 여러 턴에 걸친 프로세스의 단계를 추적 (예: `'booking_step': 'confirm_payment'`).
* **정보 축적:** 목록이나 요약 생성 (예: `'shopping_cart_items': ['book', 'pen']`).
* **정보에 기반한 결정:** 다음 응답에 영향을 미치는 플래그나 값 저장 (예: `'user_is_authenticated': True`).

### `State`의 주요 특징

1. **구조: 직렬화 가능한 키-값 쌍**

    * 데이터는 `key: value`로 저장됩니다.
    * **키(Keys):** 항상 문자열(`str`)입니다. 명확한 이름을 사용하세요 (예: `'departure_city'`, `'user:language_preference'`).
    * **값(Values):** **직렬화 가능**해야 합니다. 이는 `SessionService`에 의해 쉽게 저장되고 로드될 수 있음을 의미합니다. 문자열, 숫자, 불리언, 그리고 *오직* 이러한 기본 타입만 포함하는 단순한 리스트나 딕셔너리와 같은 특정 언어(Python/Go/Java)의 기본 타입을 사용하세요. (정확한 세부 정보는 API 문서를 참조하세요).
    * **⚠️ 복잡한 객체 사용 피하기:** **직렬화 불가능한 객체**(사용자 정의 클래스 인스턴스, 함수, 연결 등)를 상태에 직접 저장하지 마세요. 필요한 경우 단순 식별자를 저장하고, 복잡한 객체는 다른 곳에서 검색하세요.

2. **가변성: 변경 가능함**

    * `state`의 내용은 대화가 진행됨에 따라 변경될 것으로 예상됩니다.

3. **영속성: `SessionService`에 따라 다름**

    * 상태가 애플리케이션 재시작 후에도 유지되는지 여부는 선택한 서비스에 따라 다릅니다:

      * `InMemorySessionService`: **영속성 없음.** 재시작 시 상태가 손실됩니다.
      * `DatabaseSessionService` / `VertexAiSessionService`: **영속성 있음.** 상태가 안정적으로 저장됩니다.

!!! 참고
    기본 요소에 대한 특정 매개변수나 메서드 이름은 SDK 언어에 따라 약간 다를 수 있습니다(예: Python의 `session.state['current_intent'] = 'book_flight'`, Go의 `context.State().Set("current_intent", "book_flight")`, Java의 `session.state().put("current_intent", "book_flight)`). 자세한 내용은 언어별 API 문서를 참조하세요.

### 접두사를 사용한 상태 구성: 범위의 중요성

상태 키의 접두사는 특히 영속성 있는 서비스와 함께 사용할 때, 범위와 영속성 동작을 정의합니다:

* **접두사 없음 (세션 상태):**

    * **범위:** *현재* 세션(`id`)에 한정됩니다.
    * **영속성:** `SessionService`가 영속적(`Database`, `VertexAI`)인 경우에만 유지됩니다.
    * **사용 사례:** 현재 작업 내 진행 상황 추적(예: `'current_booking_step'`), 이번 상호작용을 위한 임시 플래그(예: `'needs_clarification'`).
    * **예시:** `session.state['current_intent'] = 'book_flight'`

* **`user:` 접두사 (사용자 상태):**

    * **범위:** `user_id`에 연결되며, 해당 사용자의 (동일한 `app_name` 내의) *모든* 세션에서 공유됩니다.
    * **영속성:** `Database` 또는 `VertexAI`에서 영속적입니다. (`InMemory`에 의해 저장되지만 재시작 시 손실됩니다).
    * **사용 사례:** 사용자 선호도(예: `'user:theme'`), 프로필 세부 정보(예: `'user:name'`).
    * **예시:** `session.state['user:preferred_language'] = 'fr'`

* **`app:` 접두사 (앱 상태):**

    * **범위:** `app_name`에 연결되며, 해당 애플리케이션의 *모든* 사용자와 세션에서 공유됩니다.
    * **영속성:** `Database` 또는 `VertexAI`에서 영속적입니다. (`InMemory`에 의해 저장되지만 재시작 시 손실됩니다).
    * **사용 사례:** 전역 설정(예: `'app:api_endpoint'`), 공유 템플릿.
    * **예시:** `session.state['app:global_discount_code'] = 'SAVE10'`

* **`temp:` 접두사 (임시 호출 상태):**

    * **범위:** 현재 **호출(invocation)**에 한정됩니다 (에이전트가 사용자 입력을 받아 해당 입력에 대한 최종 출력을 생성하기까지의 전체 프로세스).
    * **영속성:** **영속성 없음.** 호출이 완료된 후 폐기되며 다음 호출로 이어지지 않습니다.
    * **사용 사례:** 단일 호출 내에서 도구 호출 간에 전달되는 중간 계산, 플래그 또는 데이터 저장.
    * **사용하지 말아야 할 경우:** 사용자 선호도, 대화 기록 요약, 누적 데이터와 같이 여러 호출에 걸쳐 유지되어야 하는 정보.
    * **예시:** `session.state['temp:raw_api_response'] = {...}`

!!! 참고 "하위 에이전트와 호출 컨텍스트"
    부모 에이전트가 하위 에이전트를 호출할 때(예: `SequentialAgent` 또는 `ParallelAgent` 사용), `InvocationContext`를 하위 에이전트에 전달합니다. 이는 전체 에이전트 호출 체인이 동일한 호출 ID를 공유하고, 따라서 동일한 `temp:` 상태를 공유함을 의미합니다.

**에이전트가 보는 방식:** 에이전트 코드는 단일 `session.state` 컬렉션(dict/Map)을 통해 *결합된* 상태와 상호작용합니다. `SessionService`는 접두사를 기반으로 올바른 기본 스토리지에서 상태를 가져오고 병합하는 것을 처리합니다.

### 에이전트 지침에서 세션 상태 접근하기

`LlmAgent` 인스턴스로 작업할 때, 간단한 템플릿 구문을 사용하여 세션 상태 값을 에이전트의 지침 문자열에 직접 주입할 수 있습니다. 이를 통해 자연어 지시에만 의존하지 않고 동적이고 컨텍스트를 인식하는 지침을 만들 수 있습니다.

#### `{key}` 템플릿 사용하기

세션 상태에서 값을 주입하려면, 원하는 상태 변수의 키를 중괄호로 묶습니다: `{key}`. 프레임워크는 이 플레이스홀더를 지침을 LLM에 전달하기 전에 `session.state`의 해당 값으로 자동 교체합니다.

**예시:**

=== "Python"

    ```python
    from google.adk.agents import LlmAgent

    story_generator = LlmAgent(
        name="StoryGenerator",
        model="gemini-2.0-flash",
        instruction="""고양이에 대한 짧은 이야기를 작성하되, 주제는 {topic}에 초점을 맞추세요."""
    )

    # session.state['topic']이 "friendship"으로 설정되었다고 가정하면, LLM은
    # 다음 지침을 받게 됩니다:
    # "고양이에 대한 짧은 이야기를 작성하되, 주제는 friendship에 초점을 맞추세요."
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/instruction_template/instruction_template_example.go:key_template"
    ```

#### 중요 고려사항

* 키 존재 여부: 지침 문자열에서 참조하는 키가 session.state에 존재하는지 확인하세요. 키가 없으면 에이전트가 오류를 발생시킵니다. 존재할 수도 있고 아닐 수도 있는 키를 사용하려면 키 뒤에 물음표(?)를 포함할 수 있습니다 (예: {topic?}).
* 데이터 타입: 키와 연관된 값은 문자열이거나 쉽게 문자열로 변환할 수 있는 타입이어야 합니다.
* 이스케이프: 지침에 리터럴 중괄호를 사용해야 하는 경우(예: JSON 형식 지정), 이스케이프 처리해야 합니다.

#### `InstructionProvider`로 상태 주입 우회하기

경우에 따라, 상태 주입 메커니즘을 트리거하지 않고 지침에서 `{{`와 `}}`를 문자 그대로 사용하고 싶을 수 있습니다. 예를 들어, 동일한 구문을 사용하는 템플릿 언어를 지원하는 에이전트에 대한 지침을 작성하는 경우입니다.

이를 위해, `instruction` 매개변수에 문자열 대신 함수를 제공할 수 있습니다. 이 함수를 `InstructionProvider`라고 합니다. `InstructionProvider`를 사용하면 ADK는 상태를 주입하려고 시도하지 않으며, 지침 문자열은 그대로 모델에 전달됩니다.

`InstructionProvider` 함수는 `ReadonlyContext` 객체를 받으며, 이를 사용하여 지침을 동적으로 빌드해야 하는 경우 세션 상태나 다른 컨텍셔널 정보에 접근할 수 있습니다.

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.agents.readonly_context import ReadonlyContext

    # 이것은 InstructionProvider입니다
    def my_instruction_provider(context: ReadonlyContext) -> str:
        # 선택적으로 컨텍스트를 사용하여 지침을 빌드할 수 있습니다
        # 이 예제에서는 리터럴 중괄호가 있는 정적 문자열을 반환합니다.
        return "이것은 대체되지 않을 {{리터럴_중괄호}}가 있는 지침입니다."

    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="template_helper_agent",
        instruction=my_instruction_provider
    )
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/instruction_provider/instruction_provider_example.go:bypass_state_injection"
    ```

`InstructionProvider`를 사용하면서 지침에 상태를 주입하고 싶다면 `inject_session_state` 유틸리티 함수를 사용할 수 있습니다.

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.agents.readonly_context import ReadonlyContext
    from google.adk.utils import instructions_utils

    async def my_dynamic_instruction_provider(context: ReadonlyContext) -> str:
        template = "이것은 {adjective} 지침이며 {{리터럴_중괄호}}를 포함합니다."
        # 이것은 'adjective' 상태 변수를 주입하지만 리터럴 중괄호는 그대로 둡니다.
        return await instructions_utils.inject_session_state(template, context)

    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="dynamic_template_helper_agent",
        instruction=my_dynamic_instruction_provider
    )
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/instruction_provider/instruction_provider_example.go:manual_state_injection"
    ```

**직접 주입의 이점**

* 명확성: 지침의 어느 부분이 동적이며 세션 상태에 기반하는지를 명시적으로 만듭니다.
* 신뢰성: LLM이 상태에 접근하기 위해 자연어 지침을 올바르게 해석하는 데 의존하는 것을 피합니다.
* 유지보수성: 지침 문자열을 단순화하고 상태 변수 이름을 업데이트할 때의 오류 위험을 줄입니다.

**다른 상태 접근 방법과의 관계**

이 직접 주입 방법은 LlmAgent 지침에만 해당됩니다. 다른 상태 접근 방법에 대한 자세한 내용은 다음 섹션을 참조하세요.

### 상태 업데이트 방법: 권장 방법

!!! 참고 "상태를 수정하는 올바른 방법"
    세션 상태를 변경해야 할 때, 올바르고 가장 안전한 방법은 함수에 제공된 **`Context`의 `state` 객체를 직접 수정**하는 것입니다 (예: `callback_context.state['my_key'] = 'new_value'`). 프레임워크가 이러한 변경 사항을 자동으로 추적하므로 이것이 올바른 방식의 "직접적인 상태 조작"으로 간주됩니다.

    이는 `SessionService`에서 검색한 `Session` 객체의 `state`를 직접 수정하는 것(예: `my_session.state['my_key'] = 'new_value'`)과는 결정적으로 다릅니다. **이 방법은 피해야 합니다**. 이는 ADK의 이벤트 추적을 우회하고 데이터 손실로 이어질 수 있기 때문입니다. 이 페이지 끝의 "경고" 섹션에서 이 중요한 차이점에 대한 자세한 내용을 다룹니다.

상태는 **항상** `session_service.append_event()`를 사용하여 세션 기록에 `Event`를 추가하는 과정의 일부로 업데이트되어야 합니다. 이는 변경 사항이 추적되고, 영속성이 올바르게 작동하며, 업데이트가 스레드로부터 안전함을 보장합니다.

**1. 쉬운 방법: `output_key` (에이전트 텍스트 응답용)**

에이전트의 최종 텍스트 응답을 상태에 직접 저장하는 가장 간단한 방법입니다. `LlmAgent`를 정의할 때 `output_key`를 지정하세요:

=== "Python"

    ```py
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.runners import Runner
    from google.genai.types import Content, Part

    # output_key로 에이전트 정의
    greeting_agent = LlmAgent(
        name="Greeter",
        model="gemini-2.0-flash", # 유효한 모델 사용
        instruction="짧고 친근한 인사말을 생성하세요.",
        output_key="last_greeting" # 응답을 state['last_greeting']에 저장
    )

    # --- Runner 및 Session 설정 ---
    app_name, user_id, session_id = "state_app", "user1", "session1"
    session_service = InMemorySessionService()
    runner = Runner(
        agent=greeting_agent,
        app_name=app_name,
        session_service=session_service
    )
    session = await session_service.create_session(app_name=app_name,
                                        user_id=user_id,
                                        session_id=session_id)
    print(f"초기 상태: {session.state}")

    # --- 에이전트 실행 ---
    # Runner가 append_event 호출을 처리하며, 이 때 output_key를 사용하여
    # state_delta를 자동으로 생성합니다.
    user_message = Content(parts=[Part(text="Hello")])
    for event in runner.run(user_id=user_id,
                            session_id=session_id,
                            new_message=user_message):
        if event.is_final_response():
          print(f"에이전트가 응답했습니다.") # 응답 텍스트는 event.content에도 있음

    # --- 업데이트된 상태 확인 ---
    updated_session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    print(f"에이전트 실행 후 상태: {updated_session.state}")
    # 예상 출력: {'last_greeting': '안녕하세요! 무엇을 도와드릴까요?'}
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/state/GreetingAgentExample.java:full_code"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/state_example/state_example.go:greeting"
    ```

내부적으로 `Runner`는 `output_key`를 사용하여 `state_delta`가 포함된 필요한 `EventActions`를 생성하고 `append_event`를 호출합니다.

**2. 표준 방법: `EventActions.state_delta` (복잡한 업데이트용)**

더 복잡한 시나리오(여러 키 업데이트, 문자열이 아닌 값, `user:` 또는 `app:`과 같은 특정 범위, 또는 에이전트의 최종 텍스트와 직접 관련 없는 업데이트)의 경우, `EventActions` 내에서 `state_delta`를 수동으로 구성합니다.

=== "Python"

    ```py
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.events import Event, EventActions
    from google.genai.types import Part, Content
    import time

    # --- 설정 ---
    session_service = InMemorySessionService()
    app_name, user_id, session_id = "state_app_manual", "user2", "session2"
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state={"user:login_count": 0, "task_status": "idle"}
    )
    print(f"초기 상태: {session.state}")

    # --- 상태 변경 정의 ---
    current_time = time.time()
    state_changes = {
        "task_status": "active",              # 세션 상태 업데이트
        "user:login_count": session.state.get("user:login_count", 0) + 1, # 사용자 상태 업데이트
        "user:last_login_ts": current_time,   # 사용자 상태 추가
        "temp:validation_needed": True        # 임시 상태 추가 (폐기될 예정)
    }

    # --- Actions를 포함한 이벤트 생성 ---
    actions_with_update = EventActions(state_delta=state_changes)
    # 이 이벤트는 에이전트 응답뿐만 아니라 내부 시스템 작업을 나타낼 수 있습니다
    system_event = Event(
        invocation_id="inv_login_update",
        author="system", # 또는 'agent', 'tool' 등
        actions=actions_with_update,
        timestamp=current_time
        # content는 None이거나 수행된 작업을 나타낼 수 있음
    )

    # --- 이벤트 추가 (이것이 상태를 업데이트함) ---
    await session_service.append_event(session, system_event)
    print("명시적인 state delta와 함께 `append_event`가 호출되었습니다.")

    # --- 업데이트된 상태 확인 ---
    updated_session = await session_service.get_session(app_name=app_name,
                                                user_id=user_id,
                                                session_id=session_id)
    print(f"이벤트 후 상태: {updated_session.state}")
    # 예상: {'user:login_count': 1, 'task_status': 'active', 'user:last_login_ts': <timestamp>}
    # 참고: 'temp:validation_needed'는 존재하지 않음.
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/state_example/state_example.go:manual"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/state/ManualStateUpdateExample.java:full_code"
    ```

**3. `CallbackContext` 또는 `ToolContext`를 통해 (콜백 및 도구에 권장)**

에이전트 콜백(예: `on_before_agent_call`, `on_after_agent_call`)이나 도구 함수 내에서 상태를 수정하는 것은 함수에 제공된 `CallbackContext` 또는 `ToolContext`의 `state` 속성을 사용하는 것이 가장 좋습니다.

*   `callback_context.state['my_key'] = my_value`
*   `tool_context.state['my_key'] = my_value`

이러한 컨텍스트 객체는 각 실행 범위 내에서 상태 변경을 관리하도록 특별히 설계되었습니다. `context.state`를 수정하면 ADK 프레임워크는 이러한 변경 사항이 자동으로 캡처되어 콜백이나 도구에 의해 생성되는 이벤트의 `EventActions.state_delta`로 올바르게 라우팅되도록 보장합니다. 이 델타는 이벤트가 추가될 때 `SessionService`에 의해 처리되어 적절한 영속성과 추적을 보장합니다.

이 방법은 콜백 및 도구 내에서 가장 일반적인 상태 업데이트 시나리오에 대해 `EventActions`와 `state_delta`의 수동 생성을 추상화하여 코드를 더 깨끗하고 오류 발생 가능성을 줄여줍니다.

컨텍스트 객체에 대한 더 포괄적인 세부 정보는 [컨텍스트 문서](../context/index.md)를 참조하세요.

=== "Python"

    ```python
    # 에이전트 콜백 또는 도구 함수 내에서
    from google.adk.agents import CallbackContext # 또는 ToolContext

    def my_callback_or_tool_function(context: CallbackContext, # 또는 ToolContext
                                     # ... 다른 매개변수들 ...
                                    ):
        # 기존 상태 업데이트
        count = context.state.get("user_action_count", 0)
        context.state["user_action_count"] = count + 1

        # 새 상태 추가
        context.state["temp:last_operation_status"] = "success"

        # 상태 변경은 이벤트의 state_delta에 자동으로 포함됩니다
        # ... 나머지 콜백/도구 로직 ...
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/state_example/state_example.go:context"
    ```

=== "Java"

    ```java
    // 에이전트 콜백 또는 도구 메서드 내에서
    import com.google.adk.agents.CallbackContext; // 또는 ToolContext
    // ... 다른 import 문들 ...

    public class MyAgentCallbacks {
        public void onAfterAgent(CallbackContext callbackContext) {
            // 기존 상태 업데이트
            Integer count = (Integer) callbackContext.state().getOrDefault("user_action_count", 0);
            callbackContext.state().put("user_action_count", count + 1);

            // 새 상태 추가
            callbackContext.state().put("temp:last_operation_status", "success");

            // 상태 변경은 이벤트의 state_delta에 자동으로 포함됩니다
            // ... 나머지 콜백 로직 ...
        }
    }
    ```

**`append_event`가 하는 일:**

* `Event`를 `session.events`에 추가합니다.
* 이벤트의 `actions`에서 `state_delta`를 읽습니다.
* 서비스 유형에 따라 접두사와 영속성을 올바르게 처리하면서 이러한 변경 사항을 `SessionService`가 관리하는 상태에 적용합니다.
* 세션의 `last_update_time`을 업데이트합니다.
* 동시 업데이트에 대한 스레드 안전성을 보장합니다.

### ⚠️ 직접적인 상태 수정에 대한 경고

`SessionService`에서 직접 얻은 `Session` 객체(예: `session_service.get_session()` 또는 `session_service.create_session()`을 통해)의 `session.state` 컬렉션(딕셔너리/Map)을 에이전트 호출의 관리되는 라이프사이클 *외부에서*(즉, `CallbackContext`나 `ToolContext`를 통하지 않고) 직접 수정하는 것을 피하세요. 예를 들어, `retrieved_session = await session_service.get_session(...); retrieved_session.state['key'] = value`와 같은 코드는 문제가 됩니다.

`CallbackContext.state` 또는 `ToolContext.state`를 사용하는 콜백이나 도구 *내에서의* 상태 수정은 변경 사항이 추적되도록 보장하는 올바른 방법입니다. 이들 컨텍스트 객체는 이벤트 시스템과의 필요한 통합을 처리하기 때문입니다.

**직접적인 수정(컨텍스트 외부에서)이 강력히 권장되지 않는 이유:**

1. **이벤트 기록 우회:** 변경 사항이 `Event`로 기록되지 않아 감사 가능성이 손실됩니다.
2. **영속성 파괴:** 이런 식으로 변경된 내용은 `DatabaseSessionService`나 `VertexAiSessionService`에 의해 **저장되지 않을 가능성이 높습니다**. 이들은 저장을 트리거하기 위해 `append_event`에 의존합니다.
3. **스레드 안전성 없음:** 경쟁 조건과 업데이트 손실로 이어질 수 있습니다.
4. **타임스탬프/로직 무시:** `last_update_time`을 업데이트하거나 관련 이벤트 로직을 트리거하지 않습니다.

**권장 사항:** `output_key`, `EventActions.state_delta`(수동으로 이벤트를 생성할 때), 또는 각 범위 내에 있을 때 `CallbackContext`나 `ToolContext` 객체의 `state` 속성을 수정하여 상태를 업데이트하는 방법을 고수하세요. 이러한 방법은 신뢰할 수 있고, 추적 가능하며, 영속적인 상태 관리를 보장합니다. `session.state`(`SessionService`에서 검색한 세션에서)에 대한 직접 접근은 상태를 *읽기* 위해서만 사용하세요.

### 상태 설계 모범 사례 요약

* **최소주의:** 필수적이고 동적인 데이터만 저장하세요.
* **직렬화:** 기본적이고 직렬화 가능한 타입을 사용하세요.
* **설명적인 키 및 접두사:** 명확한 이름과 적절한 접두사(`user:`, `app:`, `temp:` 또는 없음)를 사용하세요.
* **얕은 구조:** 가능한 경우 깊은 중첩을 피하세요.
* **표준 업데이트 흐름:** `append_event`에 의존하세요.