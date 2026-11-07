# 에이전트 컨텍스트

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

ADK(Agent Development Kit)에서 *컨텍스트(context)*는 에이전트와 그 도구들이 특정 작업을 수행하는 동안 사용할 수 있는 중요한 정보의 묶음을 의미합니다. 현재 작업이나 대화 차례를 효과적으로 처리하는 데 필요한 배경지식 및 리소스라고 생각할 수 있습니다.

에이전트는 종종 최신 사용자 메시지 이상의 정보가 있어야 제대로 작동합니다. 컨텍스트는 다음을 가능하게 하므로 필수적입니다.

1.  **상태 유지:** 대화의 여러 단계에 걸쳐 세부 정보를 기억합니다(예: 사용자 선호도, 이전 계산 결과, 장바구니 항목). 이는 주로 **세션 상태(session state)**를 통해 관리됩니다.
2.  **데이터 전달:** 한 단계(LLM 호출이나 도구 실행 등)에서 발견되거나 생성된 정보를 후속 단계와 공유합니다. 여기서도 세션 상태가 핵심적인 역할을 합니다.
3.  **서비스 접근:** 다음과 같은 프레임워크 기능과 상호작용합니다.
    *   **아티팩트 저장소:** 세션과 관련된 파일이나 데이터 덩어리(PDF, 이미지, 설정 파일 등)를 저장하거나 불러옵니다.
    *   **메모리:** 사용자와 연결된 과거 상호작용이나 외부 지식 소스에서 관련 정보를 검색합니다.
    *   **인증:** 도구가 외부 API에 안전하게 접근하는 데 필요한 자격 증명을 요청하고 검색합니다.
4.  **ID 및 추적:** 현재 어떤 에이전트가 실행 중인지(`agent.name`) 알고, 로깅 및 디버깅을 위해 현재 요청-응답 주기(`invocation_id`)를 고유하게 식별합니다.
5.  **도구별 작업:** 현재 상호작용의 세부 정보에 접근해야 하는 인증 요청이나 메모리 검색과 같은 도구 내 특수 작업을 활성화합니다.


단일하고 완전한 사용자 요청-최종 응답 주기(**호출(invocation)**)에 대한 이 모든 정보를 하나로 묶는 중심적인 요소는 `InvocationContext`입니다. 하지만 일반적으로 이 객체를 직접 생성하거나 관리하지는 않습니다. ADK 프레임워크는 호출이 시작될 때(예: `runner.run_async`를 통해) 이를 생성하고, 관련 컨텍스트 정보를 에이전트 코드, 콜백, 도구에 암묵적으로 전달합니다.

=== "Python"

    ```python
    # How the framework provides context
    from google.adk import Runner

    # 1. You initialize a Runner with your agent and services
    runner = Runner(
        app_name="my_app",
        agent=my_root_agent,
        session_service=my_session_service,
        artifact_service=my_artifact_service,
    )

    # 2. You call run_async with the user input
    # Note: run_async is an asynchronous generator yielding Events.
    # The framework internally creates an InvocationContext and passes it
    # implicitly to your agent code, callbacks, and tools.
    async for event in runner.run_async(
        user_id="user123",
        session_id="session456",
        new_message=user_message
    ):
        print(event.stringify_content())

    # As a developer, you work with the context objects provided in method arguments.
    ```

=== "TypeScript"

    ```typescript
    /* Conceptual Pseudocode: How the framework provides context (Internal Logic) */

    const runner = new InMemoryRunner({ agent: myRootAgent });
    const session = await runner.sessionService.createSession({ ... });
    const userMessage = createUserContent(...);

    // --- Inside runner.runAsync(...) ---
    // 1. Framework creates the main context for this specific run
    const invocationContext = new InvocationContext({
      invocationId: "unique-id-for-this-run",
      session: session,
      userContent: userMessage,
      agent: myRootAgent, // The starting agent
      sessionService: runner.sessionService,
      pluginManager: runner.pluginManager,
      // ... other necessary fields ...
    });
    //
    // 2. Framework calls the agent's run method, passing the context implicitly
    await myRootAgent.runAsync(invocationContext);
    //   --- End Internal Logic ---

    // As a developer, you work with the context objects provided in method arguments.
    ```

=== "Go"

    ```go
    /* Conceptual Pseudocode: How the framework provides context (Internal Logic) */
    --8<-- "examples/go/snippets/context/main.go:conceptual_runner_example"
    ```

=== "Java"

    ```java
    /* How the framework provides context */
    InMemoryRunner runner = new InMemoryRunner(agent);
    Session session = runner
        .sessionService()
        .createSession(runner.appName(), USER_ID, initialState, SESSION_ID )
        .blockingGet();

    try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
      while (true) {
        System.out.print("\nYou > ");
        String userInput = scanner.nextLine();
        if ("quit".equalsIgnoreCase(userInput)) {
          break;
        }
        Content userMsg = Content.fromParts(Part.fromText(userInput));
        Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg);
        System.out.print("\nAgent > ");
        events.blockingForEach(event -> System.out.print(event.stringifyContent()));
      }
    }
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.runners.InMemoryRunner

    --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:conceptual_runner_example"
    ```

## 컨텍스트 유형

ADK는 에이전트의 환경, 상태 및 리소스를 관리하는 중앙 메커니즘으로 `Context` 클래스를 사용합니다. `Context`가 모든 에이전트 상호 작용의 기본 역할을 하지만, 에이전트의 실행 흐름에서 사용되는 위치에 따라 기능과 권한의 최적의 균형을 제공하도록 설계된 특화된 "버전"으로 나타납니다.
이러한 특정 컨텍스트 유형을 사용하면 ADK는 세션 상태, 메모리 또는 자격 증명과 같은 필요한 정보에 필요한 시간과 장소에 에이전트가 정확히 액세스할 수 있도록 보장합니다.
마주하게 될 주요 컨텍스트 유형은 다음과 같습니다.

- **`InvocationContext`**: 서비스 참조 및 수명 주기 관리를 포함하여 전체 호출에 대한 포괄적인 뷰를 제공하기 위해 핵심 에이전트 실행(`_run_async_impl`, `_run_live_impl`) 중에 사용됩니다.

- **`ReadonlyContext`**: 명령 공급자(instruction provider) 내와 같이 변경이 불가능한 시나리오에서 사용되는 기본적인 컨텍스트 정보의 가볍고 제한적인 뷰입니다.

- **`Context`**: 에이전트 수명 주기 및 모델 콜백에서 사용됩니다. 세션 상태 읽기/쓰기, 아티팩트 관리 및 메모리 서비스에 데이터 주입을 위한 견고한 기능 세트를 제공합니다.

- **`ToolContext`**: 도구 실행 및 도구 관련 콜백에 맞게 조정되었습니다. Context의 기능 외에도 인증 흐름, 메모리 검색 및 아티팩트 검색을 위한 특화된 메서드가 포함되어 있습니다.

!!! note
    **호환성 정보**: Python 및 TypeScript에서 `CallbackContext`와 `ToolContext`는 `Context` 유형으로 대체되었습니다. `CallbackContext` 클래스는 하위 호환성을 보장하기 위해 `Context`에 대한 별칭(alias)으로 유지됩니다. 기존 코드베이스에서 `CallbackContext`를 만날 수 있지만, 통합된 모든 기능 세트를 활용하려면 모든 신규 개발에 **`Context` 클래스를 사용해야 합니다**.

### `InvocationContext`
- **사용 위치:** 에이전트의 핵심 구현 메서드(`_run_async_impl`, `_run_live_impl`) 내에서 `ctx` 인자로 직접 받습니다.
- **목적:** 현재 호출의 전체 상태에 대한 액세스를 제공합니다. 이는 가장 포괄적인 컨텍스트 객체입니다.
- **주요 내용:** `session`(`state`와 `events` 포함), 현재 `agent` 인스턴스, `invocation_id`, 초기 `user_content`, 설정된 서비스(`artifact_service`, `memory_service`, `session_service`)에 대한 참조, 그리고 라이브/스트리밍 모드와 관련된 필드에 직접 액세스할 수 있습니다.
- **사용 사례:** 주로 에이전트의 핵심 로직이 전체 세션이나 서비스에 직접 액세스해야 할 때 사용됩니다. 하지만 종종 상태 및 아티팩트 상호작용은 자체 컨텍스트를 사용하는 콜백/도구에 위임됩니다. 또한 호출 자체를 제어하는 데 사용됩니다(예: `ctx.end_invocation = True` 설정).

    === "Python"

        ```python
        # Agent implementation receiving InvocationContext
        from google.adk.agents import BaseAgent
        from google.adk.agents.invocation_context import InvocationContext
        from google.adk.events import Event
        from typing import AsyncGenerator

        class MyAgent(BaseAgent):
            async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
                # Direct access example
                agent_name = ctx.agent.name
                session_id = ctx.session.id
                print(f"Agent {agent_name} running in session {session_id} for invocation {ctx.invocation_id}")
                # ... agent logic using ctx ...
                yield # ... event ...
        ```

    === "TypeScript"

        ```typescript
        // Pseudocode: Agent implementation receiving InvocationContext
        import { BaseAgent, InvocationContext, Event } from '@google/adk';

        class MyAgent extends BaseAgent {
          async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event, void, undefined> {
            // Direct access example
            const agentName = ctx.agent.name;
            const sessionId = ctx.session.id;
            console.log(`Agent ${agentName} running in session ${sessionId} for invocation ${ctx.invocationId}`);
            // ... agent logic using ctx ...
            yield; // ... event ...
          }
        }
        ```

    === "Go"

        ```go
        import (
        	"fmt"

        	"google.golang.org/adk/v2/agent"
        	"google.golang.org/adk/v2/session"
        )

        --8<-- "examples/go/snippets/context/main.go:invocation_context_agent"
        ```

    === "Java"

        ```java
        // Example: Agent implementation receiving InvocationContext
        import com.google.adk.agents.BaseAgent;
        import com.google.adk.agents.InvocationContext;
        import com.google.adk.events.Event;
        import io.reactivex.rxjava3.core.Flowable;

        public class MyAgent extends BaseAgent {
            @Override
            protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
                // Direct access example
                String agentName = invocationContext.agent().name();
                String sessionId = invocationContext.session().id();
                String invocationId = invocationContext.invocationId();
                System.out.println("Agent " + agentName + " running in session " + sessionId + " for invocation " + invocationId);
                // ... agent logic using invocationContext ...
                return Flowable.empty();
            }
        }
        ```

    === "Kotlin"

        ```kotlin
        import com.google.adk.kt.agents.BaseAgent
        import com.google.adk.kt.agents.InvocationContext
        import com.google.adk.kt.events.Event
        import kotlinx.coroutines.flow.Flow
        import kotlinx.coroutines.flow.flow

        --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:invocation_context_agent"
        ```

### `ReadonlyContext`
- **사용 위치:** 기본 정보에 대한 읽기 접근만 필요하고 수정은 허용되지 않는 시나리오(예: `InstructionProvider` 함수)에서 제공됩니다. 다른 컨텍스트의 기본 클래스이기도 합니다.
- **목적:** 기본적인 컨텍스트 세부 정보에 대한 안전한 읽기 전용 뷰를 제공합니다.
- **주요 내용:** `invocation_id`, `agent_name`, 그리고 현재 `state`의 읽기 전용 *뷰*.

    === "Python"

        ```python
        # Example: Instruction provider receiving ReadonlyContext
        from google.adk.agents.readonly_context import ReadonlyContext

        def my_instruction_provider(context: ReadonlyContext) -> str:
            # Read-only access example
            # The state property provides a read-only MappingProxyType view of the state
            user_tier = context.state.get("user_tier", "standard")
            # context.state['new_key'] = 'value' # TypeError: 'mappingproxy' object does not support item assignment
            return f"Process the request for a {user_tier} user."
        ```

    === "TypeScript"

        ```typescript
        // Pseudocode: Instruction provider receiving ReadonlyContext
        import { ReadonlyContext } from '@google/adk';

        function myInstructionProvider(context: ReadonlyContext): string {
          // Read-only access example
          // The state object is read-only
          const userTier = context.state.get('user_tier') ?? 'standard';
          // context.state.set('new_key', 'value'); // This would fail or throw an error
          return `Process the request for a ${userTier} user.`;
        }
        ```

    === "Go"

        ```go
        import (
        	"fmt"

        	"google.golang.org/adk/v2/agent"
        )

        --8<-- "examples/go/snippets/context/main.go:readonly_context_instruction"
        ```

    === "Java"

        ```java
        // Example: Instruction provider receiving ReadonlyContext
        import com.google.adk.agents.ReadonlyContext;

        public String myInstructionProvider(ReadonlyContext context) {
            // Read-only access example
            // state() returns an unmodifiable view of the session state
            String userTier = (String) context.state().getOrDefault("user_tier", "standard");
            // context.state().put("new_key", "value"); // UnsupportedOperationException
            return "Process the request for a " + userTier + " user.";
        }
        ```

    === "Kotlin"

        ```kotlin
        import com.google.adk.kt.agents.ReadonlyContext
        import com.google.adk.kt.types.Content
        import com.google.adk.kt.types.Part

        --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:readonly_context_instruction"
        ```

### `CallbackContext` 및 `Context`

- **사용 위치:** 에이전트 생명주기 콜백(`before_agent_callback`, `after_agent_callback`) 및 모델 상호작용 콜백(`before_model_callback`, `after_model_callback`)에 `callback_context`로 전달됩니다.
- **목적:** *특히 콜백 내에서* 상태를 검사 및 수정하고, 아티팩트와 상호작용하며, 호출 세부 정보에 접근하는 것을 용이하게 합니다.
- **주요 기능 (`ReadonlyContext`에 추가됨):**
    - **변경 가능한 `state` 속성:** 세션 상태를 읽고 쓸 수 있습니다. 여기서 변경된 사항(`callback_context.state['key'] = value`)은 추적되며 콜백 후 프레임워크가 생성하는 이벤트와 연결됩니다.
    - **아티팩트 메서드:** 설정된 `artifact_service`와 상호작용하기 위한 `load_artifact(filename)` 및 `save_artifact(filename, part)` 메서드.
    - 직접적인 `user_content` 접근.

!!! note

    Python 및 TypeScript에서 `CallbackContext`와 `ToolContext`는 `Context` 유형으로 대체되었습니다.

=== "Python"

    ```python
    # Example: Callback receiving Context (CallbackContext is unified into Context)
    from google.adk.agents.context import Context
    from google.adk.models import LlmRequest
    from google.genai import types
    from typing import Optional

    def my_before_model_cb(context: Context, request: LlmRequest) -> Optional[types.Content]:
        # Read/Write state example
        call_count = context.state.get("model_calls", 0)
        context.state["model_calls"] = call_count + 1 # Modify state (tracks delta)

        # Optionally load an artifact
        # config_part = context.load_artifact("model_config.json")
        print(f"Preparing model call #{call_count + 1} for invocation {context.invocation_id}")
        return None # Allow model call to proceed
    ```

=== "TypeScript"

    ```typescript
    // Pseudocode: Callback receiving Context
    import { Context, LlmRequest } from '@google/adk';
    import { Content } from '@google/genai';

    function myBeforeModelCb(context: Context, request: LlmRequest): Content | undefined {
      // Read/Write state example
      const callCount = (context.state.get('model_calls') as number) || 0;
      context.state.set('model_calls', callCount + 1); // Modify state

      // Optionally load an artifact
      // const configPart = await context.loadArtifact('model_config.json');
      console.log(`Preparing model call #${callCount + 1} for invocation ${context.invocationId}`);
      return undefined; // Allow model call to proceed
    }
    ```

=== "Go"

    ```go
    import (
      "fmt"

      "google.golang.org/adk/v2/agent"
      "google.golang.org/adk/v2/model"
    )

    --8<-- "examples/go/snippets/context/main.go:callback_context_callback"
    ```

=== "Java"

    ```java
    // Example: Callback receiving CallbackContext
    import com.google.adk.agents.CallbackContext;
    import com.google.adk.models.LlmRequest;
    import com.google.adk.models.LlmResponse;
    import io.reactivex.rxjava3.core.Maybe;

    public Maybe<LlmResponse> myBeforeModelCb(CallbackContext callbackContext, LlmRequest request) {
        // Read/Write state example
        int callCount = (int) callbackContext.state().getOrDefault("model_calls", 0);
        callbackContext.state().put("model_calls", callCount + 1); // Modify state (tracks delta)

        // Optionally load an artifact
        // Maybe<Part> configPart = callbackContext.loadArtifact("model_config.json");
        System.out.println("Preparing model call " + (callCount + 1) + " for invocation " + callbackContext.invocationId());
        return Maybe.empty(); // Allow model call to proceed
    }
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.agents.CallbackContext
    import com.google.adk.kt.callbacks.CallbackChoice
    import com.google.adk.kt.models.LlmRequest
    import com.google.adk.kt.models.LlmResponse

    --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:callback_context_callback"
    ```

### `ToolContext`
- **사용 위치:** `FunctionTool`을 지원하는 함수와 도구 실행 콜백(`before_tool_callback`, `after_tool_callback`)에 `tool_context`로 전달됩니다.
- **목적:** `CallbackContext`가 제공하는 모든 것과 더불어 인증 처리, 메모리 검색, 아티팩트 목록 조회와 같이 도구 실행에 필수적인 특수 메서드를 제공합니다.
- **주요 기능 (`CallbackContext`에 추가됨):**
    - **인증 메서드:** 인증 흐름을 트리거하는 `request_credential(auth_config)`와 사용자/시스템이 제공한 자격 증명을 검색하는 `get_auth_response(auth_config)`.
    - **아티팩트 목록 조회:** 세션에서 사용 가능한 아티팩트를 찾는 `list_artifacts()`.
    - **메모리 검색:** 설정된 `memory_service`에 질의하는 `search_memory(query)`.
    - **`function_call_id` 속성:** 이 도구 실행을 트리거한 LLM의 특정 함수 호출을 식별하며, 인증 요청이나 응답을 올바르게 연결하는 데 중요합니다.
    - **`actions` 속성:** 이 단계의 `EventActions` 객체에 직접 접근하여 도구가 상태 변경, 인증 요청 등을 신호할 수 있게 합니다.

    === "Python"

        ```python
        # Example: Tool function receiving ToolContext
        from google.adk.tools import ToolContext
        from typing import Dict, Any

        # Assume this function is wrapped by a FunctionTool
        def search_external_api(query: str, tool_context: ToolContext) -> Dict[str, Any]:
            api_key = tool_context.state.get("api_key")
            if not api_key:
                # Define required auth config
                # auth_config = AuthConfig(...)
                # tool_context.request_credential(auth_config) # Request credentials
                # Use the 'actions' property to signal the auth request has been made
                # tool_context.actions.requested_auth_configs[tool_context.function_call_id] = auth_config
                return {"status": "Auth Required"}

            # Use the API key...
            print(f"Tool executing for query '{query}' using API key. Invocation: {tool_context.invocation_id}")

            # Optionally search memory or list artifacts
            # relevant_docs = tool_context.search_memory(f"info related to {query}")
            # available_files = tool_context.list_artifacts()

            return {"result": f"Data for {query} fetched."}
        ```

    === "TypeScript"

        ```typescript
        // Pseudocode: Tool function receiving Context
        import { Context } from '@google/adk';

        // __Assume this function is wrapped by a FunctionTool__
        function searchExternalApi(query: string, context: Context): { [key: string]: string } {
          const apiKey = context.state.get('api_key') as string;
          if (!apiKey) {
             // Define required auth config
             // const authConfig = new AuthConfig(...);
             // context.requestCredential(authConfig); // Request credentials
             // The 'actions' property is now automatically updated by requestCredential
             return { status: 'Auth Required' };
          }

          // Use the API key...
          console.log(`Tool executing for query '${query}' using API key. Invocation: ${context.invocationId}`);

          // Optionally search memory or list artifacts
          // Note: accessing services like memory/artifacts is typically async in TS,
          // so you would need to mark this function 'async' if you reused them.
          // context.searchMemory(`info related to ${query}`).then(...)
          // context.listArtifacts().then(...)

          return { result: `Data for ${query} fetched.` };
        }
        ```

    === "Go"

        ```go
        import "google.golang.org/adk/v2/tool"

        --8<-- "examples/go/snippets/context/main.go:tool_context_tool"
        ```

    === "Java"

        ```java
        // Example: Tool function receiving ToolContext
        import com.google.adk.tools.ToolContext;
        import java.util.Map;

        // Assume this function is wrapped by a FunctionTool
        public Map<String, Object> searchExternalApi(String query, ToolContext toolContext) {
            String apiKey = (String) toolContext.state().getOrDefault("api_key", "");
            if (apiKey.isEmpty()) {
                // Define required auth config
                // authConfig = AuthConfig(...);
                // toolContext.requestCredential(authConfig); // Request credentials
                // Use the 'actions' property to signal the auth request has been made
                return Map.of("status", "Auth Required");
            }

            // Use the API key...
            System.out.println("Tool executing for query " + query + " using API key.");

            // Optionally list artifacts
            // Single<List<String>> availableFiles = toolContext.listArtifacts();

            return Map.of("result", "Data for " + query + " fetched");
        }
        ```

    === "Kotlin"

        ```kotlin
        import com.google.adk.kt.tools.ToolContext

        --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:tool_context_tool"
        ```

이러한 다양한 컨텍스트 객체와 언제 사용해야 하는지를 이해하는 것은 ADK 애플리케이션의 상태를 효과적으로 관리하고, 서비스에 접근하며, 흐름을 제어하는 데 핵심적입니다.


## 컨텍스트를 사용하는 일반적인 작업

이제 다양한 컨텍스트 객체를 이해했으니, 에이전트와 도구를 만들 때 이를 사용하여 일반적인 작업을 수행하는 방법에 초점을 맞춰 보겠습니다.

### 정보 접근

컨텍스트에 저장된 정보를 읽어야 할 경우가 자주 있습니다.

*   **세션 상태 읽기:** 이전 단계에서 저장된 데이터나 사용자/앱 수준 설정에 접근합니다. `state` 속성에 대해 딕셔너리처럼 접근합니다.

    === "Python"

        ```python
        # Example: In a Tool function
        from google.adk.tools import ToolContext

        def my_tool(tool_context: ToolContext, **kwargs):
            user_pref = tool_context.state.get("user_display_preference", "default_mode")
            api_endpoint = tool_context.state.get("app:api_endpoint") # Read app-level state

            if user_pref == "dark_mode":
                # ... apply dark mode logic ...
                pass
            print(f"Using API endpoint: {api_endpoint}")
            # ... rest of tool logic ...

        # Example: In a Callback function
        from google.adk.agents.context import Context

        def my_callback(context: Context, **kwargs):
            last_tool_result = context.state.get("temp:last_api_result") # Read temporary state
            if last_tool_result:
                print(f"Found temporary result from last tool: {last_tool_result}")
            # ... callback logic ...
        ```

    === "TypeScript"

        ```typescript
        // Pseudocode: In a Tool function
        import { Context } from '@google/adk';

        async function myTool(context: Context) {
          const userPref = context.state.get('user_display_preference', 'default_mode');
          const apiEndpoint = context.state.get('app:api_endpoint'); // Read app-level state

          if (userPref === 'dark_mode') {
            // ... apply dark mode logic ...
          }
          console.log(`Using API endpoint: ${apiEndpoint}`);
          // ... rest of tool logic ...
        }

        // Pseudocode: In a Callback function
        import { Context } from '@google/adk';

        function myCallback(context: Context) {
          const lastToolResult = context.state.get('temp:last_api_result'); // Read temporary state
          if (lastToolResult) {
            console.log(`Found temporary result from last tool: ${lastToolResult}`);
          }
          // ... callback logic ...
        }
        ```

    === "Go"

        ```go
        import (
        	"google.golang.org/adk/v2/agent"
        	"google.golang.org/adk/v2/session"
            "google.golang.org/adk/v2/tool"
        	"google.golang.org/genai"
        )

        --8<-- "examples/go/snippets/context/main.go:accessing_state_tool"

        --8<-- "examples/go/snippets/context/main.go:accessing_state_callback"
        ```

    === "Java"

        ```java
        import com.google.adk.agents.CallbackContext;
        import com.google.adk.tools.ToolContext;

        // Example: In a Tool function
        public void myTool(ToolContext toolContext) {
            String userPref = (String) toolContext.state().getOrDefault("user_display_preference", "default_mode");
            String apiEndpoint = (String) toolContext.state().get("app:api_endpoint"); // Read app-level state

            if ("dark_mode".equals(userPref)) {
                // ... apply dark mode logic ...
            }
            System.out.println("Using API endpoint: " + apiEndpoint);
            // ... rest of tool logic ...
        }

        // Example: In a Callback function
        public void myCallback(CallbackContext callbackContext) {
            String lastToolResult = (String) callbackContext.state().get("temp:last_api_result"); // Read temporary state

            if (lastToolResult != null && !lastToolResult.isEmpty()) {
                System.out.println("Found temporary result from last tool: " + lastToolResult);
            }
            // ... callback logic ...
        }
        ```

    === "Kotlin"

        ```kotlin
        import com.google.adk.kt.agents.CallbackContext
        import com.google.adk.kt.tools.ToolContext

        --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:accessing_state_tool"

        --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:accessing_state_callback"
        ```

*   **현재 식별자 가져오기:** 로깅이나 현재 작업을 기반으로 한 사용자 정의 로직에 유용합니다.

    === "Python"

        ```python
        # Example: In any context (ToolContext shown)
        from google.adk.tools import ToolContext

        def log_tool_usage(tool_context: ToolContext, **kwargs):
            agent_name = tool_context.agent_name
            inv_id = tool_context.invocation_id
            func_call_id = getattr(tool_context, 'function_call_id', 'N/A') # Specific to ToolContext

            print(f"Log: Invocation={inv_id}, Agent={agent_name}, FunctionCallID={func_call_id} - Tool Executed.")
        ```

    === "TypeScript"

        ```typescript
        // Pseudocode: In any context
        import { Context } from '@google/adk';

        function logToolUsage(context: Context) {
          const agentName = context.agentName;
          const invId = context.invocationId;
          const functionCallId = context.functionCallId ?? 'N/A'; // Available when executing a tool

          console.log(`Log: Invocation=${invId}, Agent=${agentName}, FunctionCallID=${functionCallId} - Tool Executed.`);
        }
        ```

    === "Go"

        ```go
        import "google.golang.org/adk/v2/tool"

        --8<-- "examples/go/snippets/context/main.go:accessing_ids"
        ```

    === "Java"

        ```java
        // Example: In any context (ToolContext shown)
        import com.google.adk.tools.ToolContext;

        public void logToolUsage(ToolContext toolContext) {
            String agentName = toolContext.agentName();
            String invId = toolContext.invocationId();
            String functionCallId = toolContext.functionCallId().orElse("N/A"); // Specific to ToolContext
            System.out.println("Log: Invocation= " + invId + " Agent= " + agentName + " FunctionCallID= " + functionCallId);
        }
        ```

    === "Kotlin"

        ```kotlin
        import com.google.adk.kt.tools.ToolContext

        --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:accessing_ids"
        ```

*   **초기 사용자 입력 접근:** 현재 호출을 시작한 메시지를 다시 참조합니다.

    === "Python"

        ```python
        # Example: In a Callback
        from google.adk.agents.context import Context

        def check_initial_intent(context: Context, **kwargs):
            initial_text = "N/A"
            if context.user_content and context.user_content.parts:
                initial_text = context.user_content.parts[0].text or "Non-text input"

            print(f"This invocation started with user input: '{initial_text}'")

        # Example: In an Agent's _run_async_impl
        # async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        #     if ctx.user_content and ctx.user_content.parts:
        #         initial_text = ctx.user_content.parts[0].text
        #         print(f"Agent logic remembering initial query: {initial_text}")
        #     ...
        ```

    === "TypeScript"

        ```typescript
        // Pseudocode: In a Callback
        import { Context } from '@google/adk';

        function checkInitialIntent(context: Context) {
          let initialText = 'N/A';
          const userContent = context.userContent;
          if (userContent?.parts?.length) {
            initialText = userContent.parts[0].text ?? 'Non-text input';
          }

          console.log(`This invocation started with user input: '${initialText}'`);
        }
        ```

    === "Go"

        ```go
        import (
        	"fmt"

        	"google.golang.org/adk/v2/agent"
        	"google.golang.org/genai"
        )

        --8<-- "examples/go/snippets/context/main.go:accessing_initial_user_input"
        ```

    === "Java"

        ```java
        // Example: In a Callback
        import com.google.adk.agents.CallbackContext;
        import com.google.genai.types.Content;

        public void checkInitialIntent(CallbackContext callbackContext) {
            String initialText = "N/A";
            if (callbackContext.userContent().isPresent() && callbackContext.userContent().get().parts() != null && !callbackContext.userContent().get().parts().get().isEmpty()) {
                initialText = callbackContext.userContent().get().parts().get().get(0).text().orElse("Non-text input");
                // ...
                System.out.println("This invocation started with user input: " + initialText);
            }
        }
        ```

    === "Kotlin"

        ```kotlin
        import com.google.adk.kt.agents.CallbackContext

        --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:accessing_initial_user_input"
        ```

### 상태 관리

상태는 메모리와 데이터 흐름에 매우 중요합니다. `CallbackContext` 또는 `ToolContext`를 사용하여 상태를 수정하면 변경 사항이 프레임워크에 의해 자동으로 추적되고 유지됩니다.

*   **작동 방식:** `callback_context.state['my_key'] = my_value` 또는 `tool_context.state['my_key'] = my_value`에 값을 쓰면, 이 변경 사항이 현재 단계의 이벤트와 연관된 `EventActions.state_delta`에 추가됩니다. 그런 다음 `SessionService`는 이벤트를 영구 저장할 때 이러한 델타를 적용합니다.

*  **도구 간 데이터 전달**

    === "Python"

        ```python
        # Example: Tool 1 - Fetches user ID
        from google.adk.tools import ToolContext
        import uuid

        def get_user_profile(tool_context: ToolContext) -> dict:
            user_id = str(uuid.uuid4()) # Simulate fetching ID
            # Save the ID to state for the next tool
            tool_context.state["temp:current_user_id"] = user_id
            return {"profile_status": "ID generated"}

        # Example: Tool 2 - Uses user ID from state
        def get_user_orders(tool_context: ToolContext) -> dict:
            user_id = tool_context.state.get("temp:current_user_id")
            if not user_id:
                return {"error": "User ID not found in state"}

            print(f"Fetching orders for user ID: {user_id}")
            # ... logic to fetch orders using user_id ...
            return {"orders": ["order123", "order456"]}
        ```

    === "TypeScript"

        ```typescript
        // Pseudocode: Tool 1 - Fetches user ID
        import { Context } from '@google/adk';
        import { v4 as uuidv4 } from 'uuid';

        function getUserProfile(context: Context): Record<string, string> {
          const userId = uuidv4(); // Simulate fetching ID
          // Save the ID to state for the next tool
          context.state.set('temp:current_user_id', userId);
          return { profile_status: 'ID generated' };
        }

        // Pseudocode: Tool 2 - Uses user ID from state
        function getUserOrders(context: Context): Record<string, string | string[]> {
          const userId = context.state.get('temp:current_user_id');
          if (!userId) {
            return { error: 'User ID not found in state' };
          }

          console.log(`Fetching orders for user ID: ${userId}`);
          // ... logic to fetch orders using user_id ...
          return { orders: ['order123', 'order456'] };
        }
        ```

    === "Go"

        ```go
        import "google.golang.org/adk/v2/tool"

        --8<-- "examples/go/snippets/context/main.go:passing_data_tool1"

        --8<-- "examples/go/snippets/context/main.go:passing_data_tool2"
        ```

    === "Java"

        ```java
        // Example: Tool 1 - Fetches user ID
        import com.google.adk.tools.ToolContext;
        import java.util.Map;
        import java.util.UUID;

        public Map<String, String> getUserProfile(ToolContext toolContext) {
            String userId = UUID.randomUUID().toString();
            // Save the ID to state for the next tool
            toolContext.state().put("temp:current_user_id", userId);
            return Map.of("profile_status", "ID generated");
        }

        // Example: Tool 2 - Uses user ID from state
        public Map<String, String> getUserOrders(ToolContext toolContext) {
            String userId = (String) toolContext.state().get("temp:current_user_id");
            if (userId == null || userId.isEmpty()) {
                return Map.of("error", "User ID not found in state");
            }
            System.out.println("Fetching orders for user id: " + userId);
            // ... logic to fetch orders using userId ...
            return Map.of("orders", "order123");
        }
        ```

    === "Kotlin"

        ```kotlin
        import com.google.adk.kt.tools.ToolContext
        import java.util.UUID

        --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:passing_data_tool1"

        --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:passing_data_tool2"
        ```

*   **사용자 선호도 업데이트:**

    === "Python"

        ```python
        # Example: Tool or Callback identifies a preference
        from google.adk.tools import ToolContext # Or Context

        def set_user_preference(tool_context: ToolContext, preference: str, value: str) -> dict:
            # Use 'user:' prefix for user-level state (if using a persistent SessionService)
            state_key = f"user:{preference}"
            tool_context.state[state_key] = value
            print(f"Set user preference '{preference}' to '{value}'")
            return {"status": "Preference updated"}
        ```

    === "TypeScript"

        ```typescript
        // Pseudocode: Tool or Callback identifies a preference
        import { Context } from '@google/adk';

        function setUserPreference(context: Context, preference: string, value: string): Record<string, string> {
          // Use 'user:' prefix for user-level state (if using a persistent SessionService)
          const stateKey = `user:${preference}`;
          context.state.set(stateKey, value);
          console.log(`Set user preference '${preference}' to '${value}'`);
          return { status: 'Preference updated' };
        }
        ```

    === "Go"

        ```go
        import "google.golang.org/adk/v2/tool"

        --8<-- "examples/go/snippets/context/main.go:updating_preferences"
        ```

    === "Java"

        ```java
        // Example: Tool or Callback identifies a preference
        import com.google.adk.tools.ToolContext; // Or CallbackContext

        public Map<String, String> setUserPreference(ToolContext toolContext, String preference, String value) {
            // Use 'user:' prefix for user-level state (if using a persistent SessionService)
            String stateKey = "user:" + preference;
            toolContext.state().put(stateKey, value);
            System.out.println("Set user preference '" + preference + "' to '" + value + "'");
            return Map.of("status", "Preference updated");
        }
        ```

    === "Kotlin"

        ```kotlin
        import com.google.adk.kt.tools.ToolContext

        --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:updating_preferences"
        ```

*   **상태 접두사:** 기본 상태는 세션에만 해당되지만, `app:` 및 `user:`와 같은 접두사는 영구 `SessionService` 구현(`DatabaseSessionService` 또는 `VertexAiSessionService` 등)과 함께 사용하여 더 넓은 범위(앱 전체 또는 세션 간 사용자 전체)를 나타낼 수 있습니다. `temp:`는 현재 호출 내에서만 관련된 데이터를 나타낼 수 있습니다.

### 아티팩트 작업

세션과 관련된 파일이나 큰 데이터 덩어리를 처리하려면 아티팩트를 사용하세요. 일반적인 사용 사례: 업로드된 문서 처리.

*   **문서 요약기 예제 흐름:**

    1.  **참조 수집 (예: 설정 도구나 콜백에서):** 문서의 전체 내용이 아닌 *경로나 URI*를 아티팩트로 저장합니다.

        === "Python"

               ```python
               # Example: In a callback or initial tool
               from google.adk.agents.context import Context # Or ToolContext
               from google.genai import types

               async def save_document_reference(context: Context, file_path: str) -> None:
                   # Assume file_path is something like "gs://my-bucket/docs/report.pdf" or "/local/path/to/report.pdf"
                   try:
                       # Create a Part containing the path/URI text
                       artifact_part = types.Part.from_text(text=file_path)
                       version = await context.save_artifact("document_to_summarize.txt", artifact_part)
                       print(f"Saved document reference '{file_path}' as artifact version {version}")
                       # Store the filename in state if needed by other tools
                       context.state["temp:doc_artifact_name"] = "document_to_summarize.txt"
                   except ValueError as e:
                       print(f"Error saving artifact: {e}") # E.g., Artifact service not configured
                   except Exception as e:
                       print(f"Unexpected error saving artifact reference: {e}")

               # Example usage:
               # save_document_reference(context, "gs://my-bucket/docs/report.pdf")
               ```

        === "TypeScript"

               ```typescript
               // Pseudocode: In a callback or initial tool
               import { Context } from '@google/adk';
               import type { Part } from '@google/genai';

               async function saveDocumentReference(context: Context, filePath: string) {
                 // Assume filePath is something like "gs://my-bucket/docs/report.pdf" or "/local/path/to/report.pdf"
                 try {
                   // Create a Part containing the path/URI text
                   const artifactPart: Part = { text: filePath };
                   const version = await context.saveArtifact('document_to_summarize.txt', artifactPart);
                   console.log(`Saved document reference '${filePath}' as artifact version ${version}`);
                   // Store the filename in state if needed by other tools
                   context.state.set('temp:doc_artifact_name', 'document_to_summarize.txt');
                 } catch (e) {
                   console.error(`Unexpected error saving artifact reference: ${e}`);
                 }
               }

               // Example usage:
               // saveDocumentReference(context, "gs://my-bucket/docs/report.pdf");
               ```

        === "Go"

            ```go
            import (
            	"google.golang.org/adk/v2/tool"
            	"google.golang.org/genai"
            )

            --8<-- "examples/go/snippets/context/main.go:artifacts_save_ref"
            ```

        === "Java"

               ```java
               // Example: In a callback or initial tool
               import com.google.adk.agents.CallbackContext;
               import com.google.genai.types.Content;
               import com.google.genai.types.Part;
               import java.util.Optional;

               public void saveDocumentReference(CallbackContext context, String filePath) {
                   // Assume file_path is something like "gs://my-bucket/docs/report.pdf" or "/local/path/to/report.pdf"
                   try {
                       // Create a Part containing the path/URI text
                       Part artifactPart = Part.fromText(filePath);
                       Optional<Integer> version = context.saveArtifact("document_to_summarize.txt", artifactPart);
                       System.out.println("Saved document reference" + filePath + " as artifact version " + version.orElse(-1));
                       // Store the filename in state if needed by other tools
                       context.state().put("temp:doc_artifact_name", "document_to_summarize.txt");
                   } catch (Exception e) {
                       System.out.println("Unexpected error saving artifact reference: " + e);
                   }
               }

               // Example usage:
               // saveDocumentReference(context, "gs://my-bucket/docs/report.pdf")
               ```

        === "Kotlin"

            ```kotlin
            import com.google.adk.kt.agents.CallbackContext
            import com.google.adk.kt.types.Part

            --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:artifacts_save_ref"
            ```

    2.  **요약기 도구:** 아티팩트를 로드하여 경로/URI를 얻고, 적절한 라이브러리를 사용하여 실제 문서 내용을 읽고, 요약한 후 결과를 반환합니다.

        === "Python"

            ```python
            # Example: In the Summarizer tool function
            from google.adk.tools import ToolContext
            from google.genai import types
            # Assume libraries like google.cloud.storage or built-in open are available
            # Assume a 'summarize_text' function exists
            # from my_summarizer_lib import summarize_text

            async def summarize_document_tool(tool_context: ToolContext) -> dict:
                artifact_name = tool_context.state.get("temp:doc_artifact_name")
                if not artifact_name:
                    return {"error": "Document artifact name not found in state."}

                try:
                    # 1. Load the artifact part containing the path/URI
                    artifact_part = await tool_context.load_artifact(artifact_name)
                    if not artifact_part or not artifact_part.text:
                        return {"error": f"Could not load artifact or artifact has no text path: {artifact_name}"}

                    file_path = artifact_part.text
                    print(f"Loaded document reference: {file_path}")

                    # 2. Read the actual document content (outside ADK context)
                    document_content = ""
                    if file_path.startswith("gs://"):
                        # Example: Use GCS client library to download/read
                        pass # Replace with actual GCS reading logic
                    elif file_path.startswith("/"):
                         # Example: Use local file system
                         with open(file_path, 'r', encoding='utf-8') as f:
                             document_content = f.read()
                    else:
                        return {"error": f"Unsupported file path scheme: {file_path}"}

                    # 3. Summarize the content
                    if not document_content:
                         return {"error": "Failed to read document content."}

                    # summary = summarize_text(document_content) # Call your summarization logic
                    summary = f"Summary of content from {file_path}" # Placeholder

                    return {"summary": summary}

                except ValueError as e:
                     return {"error": f"Artifact service error: {e}"}
                except FileNotFoundError:
                     return {"error": f"Local file not found: {file_path}"}
            ```

        === "TypeScript"

            ```typescript
            // Pseudocode: In the Summarizer tool function
            import { Context } from '@google/adk';

            async function summarizeDocumentTool(context: Context): Promise<Record<string, string>> {
              const artifactName = context.state.get('temp:doc_artifact_name') as string;
              if (!artifactName) {
                return { error: 'Document artifact name not found in state.' };
              }

              try {
                // 1. Load the artifact part containing the path/URI
                const artifactPart = await context.loadArtifact(artifactName);
                if (!artifactPart?.text) {
                  return { error: `Could not load artifact or artifact has no text path: ${artifactName}` };
                }

                const filePath = artifactPart.text;
                console.log(`Loaded document reference: ${filePath}`);

                // 2. Read the actual document content (outside ADK context)
                let documentContent = '';
                if (filePath.startsWith('gs://')) {
                  // Example: Use GCS client library to download/read
                  // const storage = new Storage();
                  // const bucket = storage.bucket('my-bucket');
                  // const file = bucket.file(filePath.replace('gs://my-bucket/', ''));
                  // const [contents] = await file.download();
                  // documentContent = contents.toString();
                } else if (filePath.startsWith('/')) {
                  // Example: Use local file system
                  // import { readFile } from 'fs/promises';
                  // documentContent = await readFile(filePath, 'utf8');
                } else {
                  return { error: `Unsupported file path scheme: ${filePath}` };
                }

                // 3. Summarize the content
                if (!documentContent) {
                   return { error: 'Failed to read document content.' };
                }

                // const summary = summarizeText(documentContent); // Call your summarization logic
                const summary = `Summary of content from ${filePath}`; // Placeholder

                return { summary };

              } catch (e) {
                 return { error: `Error processing artifact: ${e}` };
              }
            }
            ```

        === "Go"

            ```go
            import "google.golang.org/adk/v2/tool"

            --8<-- "examples/go/snippets/context/main.go:artifacts_summarize"
            ```

        === "Java"

            ```java
            // Example: In the Summarizer tool function
            import com.google.adk.tools.ToolContext;
            import com.google.genai.types.Content;
            import com.google.genai.types.Part;
            import java.util.Map;
            import java.util.Optional;
            import java.io.FileNotFoundException;

            public Map<String, String> summarizeDocumentTool(ToolContext toolContext) {
                String artifactName = (String) toolContext.state().get("temp:doc_artifact_name");
                if (artifactName == null || artifactName.isEmpty()) {
                    return Map.of("error", "Document artifact name not found in state.");
                }
                try {
                    // 1. Load the artifact part containing the path/URI
                    Optional<Part> artifactPart = toolContext.loadArtifact(artifactName);
                    if (!artifactPart.isPresent() || !artifactPart.get().text().isPresent() || artifactPart.get().text().get().isEmpty()) {
                        return Map.of("error", "Could not load artifact or artifact has no text path: " + artifactName);
                    }
                    String filePath = artifactPart.get().text().get();
                    System.out.println("Loaded document reference: " + filePath);

                    // 2. Read the actual document content (outside ADK context)
                    String documentContent = "";
                    if (filePath.startsWith("gs://")) {
                        // Example: Use GCS client library to download/read into documentContent
                        // Replace with actual GCS reading logic
                    } else if (filePath.startsWith("/")) {
                        // Example: Use local file system to download/read into documentContent
                    } else {
                        return Map.of("error", "Unsupported file path scheme: " + filePath);
                    }

                    // 3. Summarize the content
                    if (documentContent.isEmpty()) {
                        return Map.of("error", "Failed to read document content.");
                    }

                    // summary = summarizeText(documentContent) // Call your summarization logic
                    String summary = "Summary of content from " + filePath; // Placeholder

                    return Map.of("summary", summary);
                } catch (IllegalArgumentException e) {
                    return Map.of("error", "Artifact service error " + e);
                } catch (Exception e) {
                    return Map.of("error", "Error reading document " + e);
                }
            }
            ```

        === "Kotlin"

            ```kotlin
            import com.google.adk.kt.tools.ToolContext
            import java.io.File
            import java.io.FileNotFoundException

            --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:artifacts_summarize"
            ```

*   **아티팩트 목록 조회:** 사용 가능한 파일이 무엇인지 확인합니다.

    === "Python"

        ```python
        # Example: In a tool function
        from google.adk.tools import ToolContext

        async def check_available_docs(tool_context: ToolContext) -> dict:
            try:
                artifact_keys = await tool_context.list_artifacts()
                print(f"Available artifacts: {artifact_keys}")
                return {"available_docs": artifact_keys}
            except ValueError as e:
                return {"error": f"Artifact service error: {e}"}
        ```

    === "TypeScript"

        ```typescript
        // Pseudocode: In a tool function
        import { Context } from '@google/adk';

        async function checkAvailableDocs(context: Context): Promise<Record<string, string[] | string>> {
          try {
            const artifactKeys = await context.listArtifacts();
            console.log(`Available artifacts: ${artifactKeys}`);
            return { available_docs: artifactKeys };
          } catch (e) {
            return { error: `Artifact service error: ${e}` };
          }
        }
        ```

    === "Go"

        ```go
        import "google.golang.org/adk/v2/tool"

        --8<-- "examples/go/snippets/context/main.go:artifacts_list"
        ```

    === "Java"

        ```java
        // Example: In a tool function
        import com.google.adk.tools.ToolContext;
        import io.reactivex.rxjava3.core.Single;
        import java.util.List;
        import java.util.Map;

        public Map<String, Object> checkAvailableDocs(ToolContext toolContext) {
            try {
                Single<List<String>> artifactKeys = toolContext.listArtifacts();
                System.out.println("Available artifacts: " + artifactKeys.blockingGet().toString());
                return Map.of("availableDocs", artifactKeys.blockingGet());
            } catch (IllegalArgumentException e) {
                return Map.of("error", "Artifact service error: " + e);
            }
        }
        ```

    === "Kotlin"

        ```kotlin
        import com.google.adk.kt.tools.ToolContext

        --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:artifacts_list"
        ```

### 도구 인증 처리

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-java">Java v0.2.0</span>
</div>

도구에 필요한 API 키나 다른 자격 증명을 안전하게 관리합니다.

=== "Python"

    ```python
    # Example: Tool requiring auth
    from google.adk.tools import ToolContext
    from google.adk.auth import AuthConfig # Assume appropriate AuthConfig is defined

    # Define your required auth configuration (e.g., OAuth, API Key)
    MY_API_AUTH_CONFIG = AuthConfig(...)
    AUTH_STATE_KEY = "user:my_api_credential" # Key to store retrieved credential

    def call_secure_api(tool_context: ToolContext, request_data: str) -> dict:
        # 1. Check if credential already exists in state
        credential = tool_context.state.get(AUTH_STATE_KEY)

        if not credential:
            # 2. If not, request it
            print("Credential not found, requesting...")
            try:
                tool_context.request_credential(MY_API_AUTH_CONFIG)
                # The framework handles yielding the event. The tool execution stops here for this turn.
                return {"status": "Authentication required. Please provide credentials."}
            except ValueError as e:
                return {"error": f"Auth error: {e}"} # e.g., function_call_id missing
            except Exception as e:
                return {"error": f"Failed to request credential: {e}"}

        # 3. If credential exists (might be from a previous turn after request)
        #    or if this is a subsequent call after auth flow completed externally
        try:
            # Optionally, re-validate/retrieve if needed, or use directly
            # This might retrieve the credential if the external flow just completed
            auth_credential_obj = tool_context.get_auth_response(MY_API_AUTH_CONFIG)
            api_key = auth_credential_obj.api_key # Or access_token, etc.

            # Store it back in state for future calls within the session
            tool_context.state[AUTH_STATE_KEY] = auth_credential_obj.model_dump() # Persist retrieved credential

            print(f"Using retrieved credential to call API with data: {request_data}")
            # ... Make the actual API call using api_key ...
            api_result = f"API result for {request_data}"

            return {"result": api_result}
        except Exception as e:
            # Handle errors retrieving/using the credential
            print(f"Error using credential: {e}")
            # Maybe clear the state key if credential is invalid?
            # tool_context.state[AUTH_STATE_KEY] = None
            return {"error": "Failed to use credential"}
    ```

=== "TypeScript"

    ```typescript
    // Pseudocode: Tool requiring auth
    import { Context } from '@google/adk'; // AuthConfig from ADK or custom

    // Define a local AuthConfig interface as it's not publicly exported by ADK
    interface AuthConfig {
      credentialKey: string;
      authScheme: { type: string }; // Minimal representation for the example
      // Add other properties if they become relevant for the example
    }

    // Define your required auth configuration (e.g., OAuth, API Key)
    const MY_API_AUTH_CONFIG: AuthConfig = {
      credentialKey: 'my-api-key', // Example key
      authScheme: { type: 'api-key' }, // Example scheme type
    };
    const AUTH_STATE_KEY = 'user:my_api_credential'; // Key to store retrieved credential

    async function callSecureApi(context: Context, requestData: string): Promise<Record<string, string>> {
      // 1. Check if credential already exists in state
      const credential = context.state.get(AUTH_STATE_KEY);

      if (!credential) {
        // 2. If not, request it
        console.log('Credential not found, requesting...');
        try {
          context.requestCredential(MY_API_AUTH_CONFIG);
          // The framework handles yielding the event. The tool execution stops here for this turn.
          return { status: 'Authentication required. Please provide credentials.' };
        } catch (e) {
          return { error: `Auth or credential request error: ${e}` };
        }
      }

      // 3. If credential exists (might be from a previous turn after request)
      //    or if this is a subsequent call after auth flow completed externally
      try {
        // Optionally, re-validate/retrieve if needed, or use directly
        // This might retrieve the credential if the external flow just completed
        const authCredentialObj = context.getAuthResponse(MY_API_AUTH_CONFIG);
        const apiKey = authCredentialObj?.apiKey; // Or accessToken, etc.

        // Store it back in state for future calls within the session
        // Note: In strict TS, might need to cast or serialize authCredentialObj
        context.state.set(AUTH_STATE_KEY, JSON.stringify(authCredentialObj));

        console.log(`Using retrieved credential to call API with data: ${requestData}`);
        // ... Make the actual API call using apiKey ...
        const apiResult = `API result for ${requestData}`;

        return { result: apiResult };
      } catch (e) {
        // Handle errors retrieving/using the credential
        console.error(`Error using credential: ${e}`);
        // Maybe clear the state key if credential is invalid?
        // toolContext.state.set(AUTH_STATE_KEY, null);
        return { error: 'Failed to use credential' };
      }
    }
    ```

=== "Java"

    ```java
    // Example: Tool requiring auth
    import com.google.adk.tools.ToolContext;
    import java.util.Map;

    // Note: AuthConfig, requestCredential, and getAuthResponse are not yet
    // fully implemented in the Java ADK public API.
    // This example relies on external auth population into the session state.

    public class SecureApiTool {
      private static final String AUTH_STATE_KEY = "user:my_api_credential";

      public Map<String, String> callSecureApi(ToolContext context, String requestData) {
        // 1. Check if credential already exists in state
        Object credential = context.state().get(AUTH_STATE_KEY);

        if (credential == null) {
          // 2. If not, request it
          System.out.println("Credential not found, requesting...");
          try {
            // context.requestCredential(MY_API_AUTH_CONFIG); // Not yet implemented in Java ADK
            // The framework handles yielding the event. The tool execution stops here for this turn.
            return Map.of("status", "Authentication required. Please provide credentials.");
          } catch (Exception e) {
            return Map.of("error", "Auth or credential request error: " + e.getMessage());
          }
        }

        // 3. If credential exists (might be from a previous turn after request)
        //    or if this is a subsequent call after auth flow completed externally
        try {
          // Optionally, re-validate/retrieve if needed, or use directly
          // String apiKey = context.getAuthResponse(MY_API_AUTH_CONFIG).getApiKey();
          String apiKey = credential.toString(); // Simplified for example

          // Store it back in state for future calls within the session
          context.state().put(AUTH_STATE_KEY, apiKey);

          System.out.println("Using retrieved credential to call API with data: " + requestData);
          // ... Make the actual API call using apiKey ...
          String apiResult = "API result for " + requestData;

          return Map.of("result", apiResult);
        } catch (Exception e) {
          // Handle errors retrieving/using the credential
          System.err.println("Error using credential: " + e.getMessage());
          return Map.of("error", "Failed to use credential");
        }
      }
    }
    ```

*기억하세요: `request_credential`은 도구를 일시 중지시키고 인증 필요성을 알립니다. 사용자/시스템이 자격 증명을 제공하면, 후속 호출에서 `get_auth_response`(또는 상태를 다시 확인)를 통해 도구가 계속 진행할 수 있습니다.* `tool_context.function_call_id`는 프레임워크에 의해 요청과 응답을 연결하는 데 암묵적으로 사용됩니다.

### 메모리 활용

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

과거 또는 외부 소스에서 관련 정보에 접근합니다.

=== "Python"

    ```python
    # Example: Tool using memory search
    from google.adk.tools import ToolContext

    async def find_related_info(tool_context: ToolContext, topic: str) -> dict:
        try:
            search_results = await tool_context.search_memory(f"Information about {topic}")
            if search_results.memories:
                print(f"Found {len(search_results.memories)} memory results for '{topic}'")
                # Process search_results.memories (which are MemoryEntry objects)
                top_entry = search_results.memories[0]
                top_result_text = next(
                    (part.text for part in (top_entry.content.parts or []) if part.text),
                    "",
                )
                return {"memory_snippet": top_result_text}
            else:
                return {"message": "No relevant memories found."}
        except ValueError as e:
            return {"error": f"Memory service error: {e}"} # e.g., Service not configured
        except Exception as e:
            return {"error": f"Unexpected error searching memory: {e}"}
    ```

=== "TypeScript"

    ```typescript
    // Pseudocode: Tool using memory search
    import { Context } from '@google/adk';

    async function findRelatedInfo(context: Context, topic: string): Promise<Record<string, string>> {
      try {
        const searchResults = await context.searchMemory(`Information about ${topic}`);
        if (searchResults.memories.length) {
          console.log(`Found ${searchResults.memories.length} memory results for '${topic}'`);
          // Process searchResults.memories
          const topResultText =
              searchResults.memories[0].content.parts?.[0]?.text ?? '';
          return { memory_snippet: topResultText };
        } else {
          return { message: 'No relevant memories found.' };
        }
      } catch (e) {
         return { error: `Memory service error: ${e}` }; // e.g., Service not configured
      }
    }
    ```

=== "Java"

    ```java
    // Example: Tool using memory search
    import com.google.adk.tools.ToolContext;
    import com.google.adk.memory.SearchMemoryResponse;
    import io.reactivex.rxjava3.core.Single;
    import java.util.Map;

    public class MemorySearchTool {
      public Single<Map<String, String>> findRelatedInfo(ToolContext context, String topic) {
        return context.searchMemory("Information about " + topic)
            .map(searchResults -> {
              if (searchResults != null && !searchResults.memories().isEmpty()) {
                System.out.println("Found " + searchResults.memories().size() + " memory results for '" + topic + "'");
                // Process searchResults.memories
                String topResultText =
                    searchResults.memories().get(0).content().text();
                return Map.of("memory_snippet", topResultText);
              } else {
                return Map.of("message", "No relevant memories found.");
              }
            })
            .onErrorReturnItem(Map.of("error", "Memory service error"));
      }
    }
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.tools.ToolContext

    --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:memory_search"
    ```

### UI 위젯 렌더링 {#render-ui-widgets}

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.27.0</span>
</div>

에이전트 응답과 함께 풍부한 UI 구성요소(예: MCP 앱 iframe)를 클라이언트로 전송하려면 `context.render_ui_widget()`을 사용하세요.

=== "Python"

    ```python
    from google.adk.events.ui_widget import UiWidget
    from google.adk.tools import ToolContext

    def render_styled_widget(color: str, context: ToolContext) -> str:
        """Render a UI widget utilizing the user-specified color."""
        
        widget = UiWidget(
            id="my_status_dashboard",
            provider="mcp",
            payload={
                "resource_uri": "ui://analytics/status",
                "tool": {"name": "get_system_status"},
                "tool_args": {"theme_color": color} # Dynamically passed from user interaction
            }
        )
        
        context.render_ui_widget(widget)
        return f"Widget successfully rendered with color: {color}"
    ```

### 고급: 직접적인 `InvocationContext` 사용

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

대부분의 상호작용은 `CallbackContext` 또는 `ToolContext`를 통해 이루어지지만, 때로는 에이전트의 핵심 로직(Python의 `_run_async_impl` 또는 `_run_live_impl`, TypeScript, Java, Kotlin의 `runAsyncImpl` 등)에서 직접 액세스해야 할 때가 있습니다.

=== "Python"

    ```python
    # Example: Inside agent's _run_async_impl
    from google.adk.agents import BaseAgent
    from google.adk.agents.invocation_context import InvocationContext
    from google.adk.events import Event
    from google.genai import types
    from typing import AsyncGenerator

    class MyControllingAgent(BaseAgent):
        async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
            # Example: Check if a specific service is available
            if not ctx.memory_service:
                print("Memory service is not available for this invocation.")
                # Potentially change agent behavior

            # Example: Early termination based on some condition
            if ctx.session.state.get("critical_error_flag"):
                print("Critical error detected, ending invocation.")
                ctx.end_invocation = True # Signal framework to stop processing
                yield Event(
                author=self.name,
                invocation_id=ctx.invocation_id,
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="Stopping due to critical error.")],
                ),
            )
                return # Stop this agent's execution

            # ... Normal agent processing ...
            yield # ... event ...
    ```

=== "TypeScript"

    ```typescript
    // Pseudocode: Inside agent's runAsyncImpl
    import { BaseAgent, InvocationContext } from '@google/adk';
    import type { Event } from '@google/adk';

    class MyControllingAgent extends BaseAgent {
      async *runAsyncImpl(ctx: InvocationContext): AsyncGenerator<Event, void, undefined> {
        // Example: Check if a specific service is available
        if (!ctx.memoryService) {
          console.log('Memory service is not available for this invocation.');
          // Potentially change agent behavior
        }

        // Example: Early termination based on some condition
        // Direct access to state via ctx.session.state or through ctx.session.state property if wrapped
        if ((ctx.session.state as { 'critical_error_flag': boolean })['critical_error_flag']) {
          console.log('Critical error detected, ending invocation.');
          ctx.endInvocation = true; // Signal framework to stop processing
          yield {
            author: this.name,
            invocationId: ctx.invocationId,
            content: { parts: [{ text: 'Stopping due to critical error.' }] }
          } as Event;
          return; // Stop this agent's execution
        }

        // ... Normal agent processing ...
        yield; // ... event ...
      }
    }
    ```

=== "Java"

    ```java
    // Example: Inside agent's runAsyncImpl
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.InvocationContext;
    import com.google.adk.events.Event;
    import com.google.genai.types.Content;
    import com.google.genai.types.Part;
    import io.reactivex.rxjava3.core.Flowable;
    import java.util.List;

    public class MyControllingAgent extends BaseAgent {

      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext ctx) {
        // Example: Check if a specific service is available
        if (ctx.memoryService() == null) {
          System.out.println("Memory service is not available for this invocation.");
          // Potentially change agent behavior
        }

        // Example: Early termination based on some condition
        Boolean criticalError = (Boolean) ctx.session().state().getOrDefault("critical_error_flag", false);
        if (criticalError != null && criticalError) {
          System.out.println("Critical error detected, ending invocation.");
          ctx.setEndInvocation(true); // Signal framework to stop processing

          Event errorEvent = Event.builder()
              .author(name())
              .invocationId(ctx.invocationId())
              .content(Content.builder().parts(List.of(Part.builder().text("Stopping due to critical error.").build())).build())
              .build();

          return Flowable.just(errorEvent); // Stop this agent's execution
        }

        // ... Normal agent processing ...
        // return Flowable.just(normalEvent);
        return Flowable.empty();
      }
    }
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.agents.BaseAgent
    import com.google.adk.kt.agents.InvocationContext
    import com.google.adk.kt.events.Event
    import com.google.adk.kt.types.Content
    import com.google.adk.kt.types.Part
    import com.google.adk.kt.types.Role
    import kotlinx.coroutines.flow.Flow
    import kotlinx.coroutines.flow.flow

    --8<-- "examples/kotlin/snippets/context/ContextExamples.kt:advanced_invocation_context"
    ```

호출 종료 플래그를 **True**로 설정하는 것은 에이전트 또는 해당 콜백이나 도구 내부에서(기본 `InvocationContext`의 플래그를 수정할 수 있는 각각의 컨텍스트 객체를 통해) 전체 요청-응답 주기를 정상적으로 중단하는 방법입니다. 구체적으로 Python에서는 `ctx.end_invocation = True`, TypeScript에서는 `ctx.endInvocation = true`, Java에서는 `ctx.setEndInvocation(true)`, Kotlin에서는 `context.isEndOfInvocation = true` 또는 `context.endInvocation()`을 사용하세요.

## 핵심 요약 및 모범 사례

*   **올바른 컨텍스트 사용:** 항상 제공되는 가장 구체적인 컨텍스트 객체를 사용하세요(`ToolContext`는 도구/도구-콜백에서, `CallbackContext`는 에이전트/모델-콜백에서, `ReadonlyContext`는 해당되는 곳에서). 전체 `InvocationContext`(`ctx`)는 `_run_async_impl` / `_run_live_impl`에서 꼭 필요할 때만 직접 사용하세요.
*   **데이터 흐름을 위한 상태:** `context.state`는 호출 *내에서* 데이터를 공유하고, 선호도를 기억하며, 대화 메모리를 관리하는 주요 방법입니다. 영구 저장소를 사용할 때는 접두사(`app:`, `user:`, `temp:`)를 신중하게 사용하세요.
*   **파일을 위한 아티팩트:** 파일 참조(경로나 URI 등)나 큰 데이터 덩어리를 관리할 때는 `context.save_artifact`와 `context.load_artifact`를 사용하세요. 참조를 저장하고, 필요할 때 내용을 로드하세요.
*   **추적되는 변경 사항:** 컨텍스트 메서드를 통해 상태나 아티팩트를 수정하면 현재 단계의 `EventActions`에 자동으로 연결되고 `SessionService`에 의해 처리됩니다.
*   **UI 렌더링:** `context.render_ui_widget(widget)`을 사용하여 풍부한 UI 구성요소(예: MCP 앱 iframe)를 클라이언트로 전송하세요.
*   **단순하게 시작:** 먼저 `state`와 기본적인 아티팩트 사용에 집중하세요. 필요가 더 복잡해지면 인증, 메모리, 그리고 고급 `InvocationContext` 필드(라이브 스트리밍용 필드 등)를 탐색하세요.

이러한 컨텍스트 객체를 이해하고 효과적으로 사용함으로써 ADK로 더 정교하고, 상태를 유지하며, 유능한 에이전트를 구축할 수 있습니다.
