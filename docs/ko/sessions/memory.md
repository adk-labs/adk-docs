# 메모리: `MemoryService`를 사용한 장기 지식

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

`Session`이 단일 대화의 기록(`events`) 및 임시 데이터(`state`)를 추적하는 반면, 에이전트는 과거 상호작용의 정보를 회상해야 할 수도 있습니다. 이것이 바로 **장기 지식(Long-Term Knowledge)**과 **`MemoryService`**의 개념이 필요한 부분입니다. 다음과 같이 생각할 수 있습니다:

- **`Session` / `State`:** 특정 채팅 중의 단기 기억입니다.
- **장기 지식(`MemoryService`)**: 에이전트가 참조할 수 있는 검색 가능한 아카이브 또는 지식 라이브러리로, 여러 과거 채팅이나 기타 소스의 정보를 포함할 수 있습니다.

## `MemoryService` 역할

`BaseMemoryService`(Go에서는 `Service`)는 이 검색 가능한 장기 지식 저장소를 관리하기 위한 인터페이스를 정의합니다. 다음 작업을 지원합니다:

- **정보 수집(Ingesting Information):**
    - **`add_session_to_memory`**: 완료된 `Session`을 가져와 관련 정보를 장기 지식 저장소에 추가합니다. 이 방식은 대화의 핵심을 자동으로 캡처하는 데 이상적입니다.
    - **`add_events_to_memory`**: 전체 세션을 다시 수집하지 않고 이벤트 델타(예: 최신 턴)를 추가합니다. 장기 실행 세션 도중 메모리에 쓰고 싶을 때 유용합니다.
    - **`add_memory`**: 명시적인 `MemoryEntry` 객체를 메모리에 직접 추가합니다. 이 메서드는 세밀한 제어를 제공하며 다른 소스의 특정 팩트를 주입할 때 유용합니다.
- **정보 검색(`search_memory`):** 에이전트(일반적으로 `Tool`을 통해)가 지식 저장소를 쿼리하고 검색 쿼리를 기반으로 관련 스니펫이나 컨텍스트를 가져올 수 있도록 합니다.

`add_events_to_memory`와 `add_memory`는 선택 사항이며 모든 서비스에서 구현되는 것은 아니므로, 사용하기 전에 선택한 서비스가 이를 지원하는지 확인하세요.

## 올바른 메모리 서비스 선택

Python ADK는 세 가지 `MemoryService` 구현을 제공합니다. 아래 표를 사용하여 에이전트에 가장 적합한 것을 결정하세요.

| **기능** | **InMemoryMemoryService** | **VertexAiMemoryBankService** | **VertexAiRagMemoryService** |
| :--- | :--- | :--- | :--- |
| **지속성** | 없음(다시 시작하면 데이터가 손실됨) | 예(Agent Platform에서 관리) | 예(Knowledge Engine에 저장) |
| **주요 사용 사례** | 프로토타이핑, 로컬 개발 및 간단한 테스트. | 사용자 대화에서 의미 있고 진화하는 메모리를 구축합니다. | 전체 대화 코퍼스 또는 다른 RAG 색인 콘텐츠와 함께 벡터 검색을 수행합니다. |
| **메모리 추출** | 전체 대화 저장 | LLM을 기반으로 대화에서 [의미 있는 정보](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/generate-memories)를 추출하고 기존 메모리와 통합합니다. | [Knowledge Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)으로 색인된 전체 대화를 저장합니다. |
| **검색 기능** | 기본 키워드 일치. | 고급 시맨틱 검색. | Knowledge Engine 기반 벡터 유사도 검색. |
| **설정 복잡성** | 없음. 기본값입니다. | 낮음. Agent Platform의 [Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview) 인스턴스가 필요합니다. | 중간. [Knowledge Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/manage-your-rag-corpus)이 필요합니다. |
| **종속성** | 없음. | Google Cloud 프로젝트, Agent Platform API | Google Cloud 프로젝트, Knowledge Engine, Agent Platform SDK(선택 설치). |
| **사용 시기** | 프로토타이핑을 위해 여러 세션의 채팅 기록을 검색하려는 경우. | 에이전트가 과거 상호작용을 기억하고 학습하기를 원하는 경우. | 이미 RAG 인프라가 있거나 원시 대화 기록을 검색하려는 경우. |

`google.adk.memory`에서 `VertexAiRagMemoryService`를 항상 가져올 수 있지만, `pip install google-adk[gcp]`를 통해 Agent Platform SDK가 설치되어 있지 않으면 생성 시 `ImportError`가 발생합니다. Memory Bank와 RAG 기반 메모리는 아래의 [Memory Bank](#memory-bank) 및 [RAG 메모리](#rag-memory)에 설명되어 있습니다.


## `InMemoryMemoryService`

`InMemoryMemoryService`는 애플리케이션의 메모리에 세션 정보를 저장하고 검색을 위해 기본 키워드 일치를 수행합니다. 설정이 필요 없으며 지속성이 필요하지 않은 프로토타이핑 및 간단한 테스트 시나리오에 가장 적합합니다.

=== "Python"

    ```py
    from google.adk.memory import InMemoryMemoryService
    memory_service = InMemoryMemoryService()
    ```

=== "TypeScript"

    ```typescript
    import { InMemoryMemoryService } from '@google/adk';
    const memoryService = new InMemoryMemoryService();
    ```

=== "Go"

    ```go
    import (
      "google.golang.org/adk/v2/memory"
      "google.golang.org/adk/v2/session"
    )

    // Services must be shared across runners to share state and memory.
    sessionService := session.InMemoryService()
    memoryService := memory.InMemoryService()
    ```

=== "Java"

    ```java
    import com.google.adk.memory.InMemoryMemoryService;

    InMemoryMemoryService memoryService = new InMemoryMemoryService();
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:instantiate_service"
    ```

**예: 메모리 추가 및 검색**

이 예는 단순성을 위해 `InMemoryMemoryService`를 사용하는 기본 흐름을 보여줍니다.

=== "Python"

    ```py
    import asyncio
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.memory import InMemoryMemoryService # Import MemoryService
    from google.adk.runners import Runner
    from google.adk.tools import load_memory # Tool to query memory
    from google.genai.types import Content, Part

    # --- Constants ---
    APP_NAME = "memory_example_app"
    USER_ID = "mem_user"
    MODEL = "gemini-flash-latest" # Use a valid model

    # --- Agent Definitions ---
    # Agent 1: Simple agent to capture information
    info_capture_agent = LlmAgent(
        model=MODEL,
        name="InfoCaptureAgent",
        instruction="Acknowledge the user's statement.",
    )

    # Agent 2: Agent that can use memory
    memory_recall_agent = LlmAgent(
        model=MODEL,
        name="MemoryRecallAgent",
        instruction="Answer the user's question. Use the 'load_memory' tool "
                    "if the answer might be in past conversations.",
        tools=[load_memory] # Give the agent the tool
    )

    # --- Services ---
    # Services must be shared across runners to share state and memory
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService() # Use in-memory for demo

    async def run_scenario():
        # --- Scenario ---

        # Turn 1: Capture some information in a session
        print("--- Turn 1: Capturing Information ---")
        runner1 = Runner(
            # Start with the info capture agent
            agent=info_capture_agent,
            app_name=APP_NAME,
            session_service=session_service,
            memory_service=memory_service # Provide the memory service to the Runner
        )
        session1_id = "session_info"
        await runner1.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
        user_input1 = Content(parts=[Part(text="My favorite project is Project Alpha.")], role="user")

        # Run the agent
        final_response_text = "(No final response)"
        async for event in runner1.run_async(user_id=USER_ID, session_id=session1_id, new_message=user_input1):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
        print(f"Agent 1 Response: {final_response_text}")

        # Get the completed session
        completed_session1 = await runner1.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)

        # Add this session's content to the Memory Service
        print("\n--- Adding Session 1 to Memory ---")
        await memory_service.add_session_to_memory(completed_session1)
        print("Session added to memory.")

        # Turn 2: Recall the information in a new session
        print("\n--- Turn 2: Recalling Information ---")
        runner2 = Runner(
            # Use the second agent, which has the memory tool
            agent=memory_recall_agent,
            app_name=APP_NAME,
            session_service=session_service, # Reuse the same service
            memory_service=memory_service   # Reuse the same service
        )
        session2_id = "session_recall"
        await runner2.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session2_id)
        user_input2 = Content(parts=[Part(text="What is my favorite project?")], role="user")

        # Run the second agent
        final_response_text_2 = "(No final response)"
        async for event in runner2.run_async(user_id=USER_ID, session_id=session2_id, new_message=user_input2):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text_2 = event.content.parts[0].text
        print(f"Agent 2 Response: {final_response_text_2}")

    # To run this example, you can use the following snippet:
    # asyncio.run(run_scenario())

    # await run_scenario()
    ```

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/sessions/memory_example.ts:full_example"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/memory_example/memory_example.go:full_example"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/sessions/MemoryExample.java:full_example"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:full_example"
    ```

### 도구 내에서 메모리 검색

도구 컨텍스트를 사용하여 커스텀 도구 내에서 메모리를 검색할 수도 있습니다.

=== "Python"

    ```python
    from google.adk.tools import ToolContext

    async def search_past_conversations(
        query: str, tool_context: ToolContext
    ) -> dict:
        response = await tool_context.search_memory(query)
        return {
            "results": [
                part.text
                for entry in response.memories
                for part in (entry.content.parts or [])
                if part.text
            ]
        }
    ```

=== "TypeScript"

    ```typescript
    // Within a tool implementation
    async runAsync({ args, toolContext }: RunAsyncToolRequest) {
      const query = args['query'] as string;
      const response = await toolContext.searchMemory(query);
      // process response
      return {
        memories: response.memories.map(m => m.content.parts?.map(p => p.text).join(' ')).join('\n')
      };
    }
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/memory_example/memory_example.go:tool_search"
    ```

=== "Java"

    ```java
    // Within a tool implementation
    public Single<ToolOutput> execute(ToolContext context) {
      String query = ...; // get query from arguments
      return context.searchMemory(query)
          .map(response -> {
              // process response
              return new ToolOutput(response.memories().toString());
          });
    }
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:search_within_tool"
    ```

## Memory Bank {#memory-bank}

`VertexAiMemoryBankService`는 에이전트를 대화형 에이전트를 위한 정교하고 지속적인 메모리 기능을 제공하는 완전 관리형 Google Cloud 서비스인 [Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)에 연결합니다.

### 작동 방식

이 서비스는 두 가지 주요 작업을 처리합니다:

- **메모리 생성:** 대화가 끝나면 세션의 이벤트를 Memory Bank로 보낼 수 있으며, Memory Bank는 정보를 지능적으로 처리하여 "메모리"로 저장합니다.
- **메모리 검색:** 에이전트 코드는 Memory Bank에 대해 검색 쿼리를 실행하여 과거 대화에서 관련 메모리를 검색할 수 있습니다.

### `add_memory`를 사용한 직접 메모리 수집

세션 기록에서 메모리를 생성하는 것 외에도 `VertexAiMemoryBankService`는 `add_memory` 메서드를 통한 직접 메모리 수집을 지원합니다. 이 메서드를 사용하면 Memory Bank에 저장되는 팩트를 정밀하게 제어할 수 있습니다.

작동 방식은 `enable_consolidation` 옵션에 따라 달라집니다:

- **직접 생성(기본값):** 기본적으로 `add_memory`는 기본 `memories.create` API를 호출합니다. 제공하는 각 `MemoryEntry`는 별개의 독립된 메모리 항목으로 추가됩니다.

    ```python
    from google.adk.memory import VertexAiMemoryBankService
    from google.adk.memory.memory_entry import MemoryEntry
    from google.genai.types import Content, Part

    memory_service = VertexAiMemoryBankService(...)

    await memory_service.add_memory(
        app_name="my-app",
        user_id="user-123",
        memories=[
            MemoryEntry(content=Content(parts=[Part(text="The user's favorite color is blue.")]))
        ]
    )
    ```

- **통합을 통한 생성(Creation with Consolidation):** `custom_metadata`에서 `enable_consolidation`을 `True`로 설정하면 서비스는 `memories.generate` API를 사용합니다. 이 설정을 통해 Memory Bank는 새로운 메모리 항목을 기존 관련 메모리와 지능적으로 통합하여 중복을 방지하고 보다 일관된 지식 기반을 구축할 수 있습니다.

    ```python
    await memory_service.add_memory(
        app_name="my-app",
        user_id="user-123",
        memories=[
            MemoryEntry(content=Content(parts=[Part(text="The user's favorite color is light blue.")]))
        ],
        custom_metadata={"enable_consolidation": True}
    )
    ```

### 전제 조건

이 기능을 사용하려면 다음이 있어야 합니다:

1. **Google Cloud 프로젝트:** Agent Platform API가 활성화되어 있어야 합니다.
2. **Agent Runtime:** Agent Platform에서 Agent Runtime을 생성해야 합니다. Memory Bank를 사용하기 위해 에이전트를 Agent Runtime에 배포할 필요는 없습니다. 이 설정을 통해 구성에 필요한 **Agent Runtime ID**를 얻을 수 있습니다.
3. **인증:** 로컬 환경이 Google Cloud 서비스에 액세스하도록 인증되었는지 확인합니다. 가장 간단한 방법은 다음을 실행하는 것입니다:

    ```bash
    gcloud auth application-default login
    ```

4. **환경 변수:** 이 서비스에는 Google Cloud 프로젝트 ID와 위치가 필요합니다. 이를 환경 변수로 설정하세요:

    ```bash
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    export GOOGLE_CLOUD_LOCATION="your-gcp-location"
    ```

ADK 에이전트에서 Google Cloud에 연결하는 방법에 대한 자세한 내용은 [Google Cloud 및 Agent Platform에 연결](/get-started/google-cloud/)을 참조하세요.

### 구성

에이전트를 Memory Bank에 연결하려면 ADK 서버(`adk web` 또는 `adk api_server`)를 시작할 때 `--memory_service_uri` 플래그를 사용합니다. URI는 `agentengine://<agent_engine_id>` 형식이어야 합니다.

```bash title="bash"
adk web path/to/your/agents_dir --memory_service_uri="agentengine://1234567890"
```

또는 `VertexAiMemoryBankService`를 수동으로 인스턴스화하고 `Runner`에 전달하여 Memory Bank를 사용하도록 에이전트를 구성할 수 있습니다.

=== "Python"

    ```py
    from google import adk
    from google.adk.memory import VertexAiMemoryBankService

    memory_service = VertexAiMemoryBankService(
        project="PROJECT_ID",
        location="LOCATION",
        agent_engine_id="AGENT_ENGINE_ID"
    )

    runner = adk.Runner(
        ...
        memory_service=memory_service
    )
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:memory_bank"
    ```

## RAG 메모리 {#rag-memory}

`VertexAiRagMemoryService`는 대화를 [Knowledge Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)에 저장하고 벡터 유사도를 통해 검색합니다. 이미 RAG 인프라가 있거나 Memory Bank에서 생성된 LLM 추출 메모리 대신 원시 대화 기록 검색을 원할 때 사용하세요. Agent Platform SDK가 필요합니다.

=== "Python"

    ```py
    from google.adk.memory import VertexAiRagMemoryService

    memory_service = VertexAiRagMemoryService(
        rag_corpus="projects/PROJECT_ID/locations/LOCATION/ragCorpora/CORPUS_ID",
        similarity_top_k=5,
        vector_distance_threshold=0.6,
    )
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:rag_memory"
    ```

## 에이전트에서 메모리 사용

메모리 서비스가 구성되면 에이전트는 도구 또는 콜백을 사용하여 메모리를 검색할 수 있습니다. ADK에는 메모리 검색을 위한 두 가지 기본 제공 도구가 포함되어 있습니다:

- **메모리 미리 로드(Preload memory)**: 콜백과 유사하게 각 턴이 시작될 때 메모리를 자동으로 검색합니다.
- **메모리 로드(Load memory)**: 에이전트가 도움이 될 것이라고 판단할 때 메모리를 검색합니다.

**예:**

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools import preload_memory

    agent = Agent(
        model=MODEL_ID,
        name='weather_sentiment_agent',
        instruction="...",
        tools=[preload_memory]
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, PRELOAD_MEMORY } from '@google/adk';

    const agent = new LlmAgent({
        model: MODEL_ID,
        name: 'weather_sentiment_agent',
        instruction: "...",
        tools: [PRELOAD_MEMORY]
    });
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/v2/agent/llmagent"
        "google.golang.org/adk/v2/tool"
        "google.golang.org/adk/v2/tool/preloadmemorytool"
    )

    agent, _ := llmagent.New(llmagent.Config{
        Model:       model,
        Name:        "weather_sentiment_agent",
        Instruction: "...",
        Tools:       []tool.Tool{preloadmemorytool.New()},
    })
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.LoadMemoryTool;

    LlmAgent agent = new LlmAgent.Builder()
        .model(MODEL_ID)
        .name("weather_sentiment_agent")
        .instruction("...")
        .tools(new LoadMemoryTool())
        .build();
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:preload_memory_agent"
    ```

세션에서 메모리를 추출하려면 `add_session_to_memory`를 호출해야 합니다. 예를 들어 콜백을 사용하여 이 단계를 자동화할 수 있습니다:

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools import preload_memory

    async def auto_save_session_to_memory_callback(callback_context):
        await callback_context.add_session_to_memory()

    agent = Agent(
        model=MODEL,
        name="Generic_QA_Agent",
        instruction="Answer the user's questions",
        tools=[preload_memory],
        after_agent_callback=auto_save_session_to_memory_callback,
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, PRELOAD_MEMORY, SingleAgentCallback } from '@google/adk';

    const autoSaveSessionToMemoryCallback: SingleAgentCallback = async (callbackContext) => {
        if (callbackContext.invocationContext.memoryService) {
            await callbackContext.invocationContext.memoryService.addSessionToMemory(
                callbackContext.invocationContext.session
            );
        }
    };

    const agent = new LlmAgent({
        model: MODEL,
        name: "Generic_QA_Agent",
        instruction: "Answer the user's questions",
        tools: [PRELOAD_MEMORY],
        afterAgentCallback: autoSaveSessionToMemoryCallback,
    });
    ```

=== "Go"

    ADK Go에서 에이전트 콜백은 메모리 서비스에 액세스할 수 없습니다. 대신 플러그인의 `AfterRunCallback`에서 세션을 저장하고, 메모리 서비스와 함께 러너에 플러그인을 등록하세요:

    ```go
    import (
        "log"

        "google.golang.org/adk/v2/agent"
        "google.golang.org/adk/v2/agent/llmagent"
        "google.golang.org/adk/v2/plugin"
        "google.golang.org/adk/v2/runner"
        "google.golang.org/adk/v2/tool"
        "google.golang.org/adk/v2/tool/loadmemorytool"
    )

    autoSavePlugin, _ := plugin.New(plugin.Config{
        Name: "auto_save_session_to_memory",
        AfterRunCallback: func(ctx agent.InvocationContext) {
            if m := ctx.Memory(); m != nil {
                if err := m.AddSessionToMemory(ctx, ctx.Session()); err != nil {
                    log.Printf("failed to save session to memory: %v", err)
                }
            }
        },
    })

    rootAgent, _ := llmagent.New(llmagent.Config{
        Model:       model,
        Name:        "Generic_QA_Agent",
        Instruction: "Answer the user's questions",
        Tools:       []tool.Tool{loadmemorytool.New()},
    })

    r, _ := runner.New(runner.Config{
        AppName:        "my_app",
        Agent:          rootAgent,
        SessionService: sessionService,
        MemoryService:  memoryService,
        PluginConfig: runner.PluginConfig{
            Plugins: []*plugin.Plugin{autoSavePlugin},
        },
    })
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:auto_save_callback"
    ```

### 콜백에서 특정 이벤트 또는 팩트 쓰기

<div class="language-support-tag">
   <span class="lst-supported">ADK에서 지원</span><span class="lst-kotlin">Kotlin v0.7.0</span>
</div>

`CallbackContext.addSessionToMemory` 메서드는 메모리의 기본 동작이며 에이전트의 전체 세션을 저장합니다. 더 세밀한 제어가 필요한 경우 `CallbackContext`는 선택한 이벤트의 하위 집합을 위한 `addEventsToMemory`와 직접 구성한 팩트를 위한 `addMemory`의 두 가지 메서드를 추가로 제공합니다. 둘 다 선택적 `customMetadata`를 허용하며, 현재 호출에서 앱, 사용자 및 세션을 자동으로 채웁니다.

```kotlin
--8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:callback_memory_writes"
```

세 가지 메서드 모두 러너에 메모리 서비스가 구성되어 있지 않은 경우 `IllegalStateException`을 발생시키므로 컴파일 시점이 아닌 런타임에 실패합니다.

## 메모리 기능 확장

`BaseMemoryService`를 확장한 메모리 서비스는 커스텀 메타데이터를 포함하여 에이전트 메모리에 세션 및 이벤트를 추가하는 기능을 지원합니다. 다음 코드 예시와 같이 `InMemoryMemoryService`와 같은 메모리 서비스의 `add_session_to_memory` 및 `add_events_to_memory` 메서드를 사용하여 메모리 데이터를 수정할 수 있습니다.

```python
import asyncio
from google.adk.memory import InMemoryMemoryService

# Assume my_memory_service is an instance of InMemoryMemoryService
# and my_latest_events is a list of new adk.Event objects from the latest turn.
my_latest_events = [...]

async def update_incremental_memory(my_memory_service, my_latest_events):
    # Example 1: Basic incremental update
    await my_memory_service.add_events_to_memory(
        app_name="my-app",
        user_id="my-user",
        events=my_latest_events,
        session_id="my-optional-session-id"
    )

    # Example 2: Incremental update with Custom Metadata
    await my_memory_service.add_events_to_memory(
        app_name="my-app",
        user_id="my-user",
        events=my_latest_events,
        session_id="my-optional-session-id",
        custom_metadata={
            "my_custom_key": "my_custom_value"
        }
    )

async def update_session_memory(my_memory_service, my_completed_session):
    # Example 3: Applying custom metadata to a full session
    await my_memory_service.add_session_to_memory(
        session=my_completed_session,
        custom_metadata={
            "category": "user_preference"
        }
    )

```

## 고급 개념

### 실제 메모리 작동 방식

메모리 워크플로에는 다음 단계가 포함됩니다:

1. **세션 상호작용:** 사용자는 `SessionService`에서 관리하는 `Session`을 통해 에이전트와 상호작용합니다. 이 상호작용 동안 이벤트가 기록되고 세션 상태가 업데이트될 수 있습니다.
2. **메모리로 수집:** 세션이 종료되거나 중요한 정보를 캡처하면 애플리케이션은 `memory_service.add_session_to_memory(session)`을 호출합니다. 이 작업은 핵심 데이터를 추출하여 Agent Runtime Memory Bank와 같은 장기 지식 저장소에 영구 저장합니다.
3. **추후 쿼리:** 다른 세션 또는 동일한 세션에서 과거 컨텍스트가 필요한 질문(예: "지난주에 프로젝트 X에 대해 무엇을 논의했나요?")을 할 수 있습니다.
4. **에이전트의 메모리 도구 사용:** 기본 제공 `load_memory` 도구와 같은 메모리 검색 도구가 장착된 에이전트는 과거 컨텍스트의 필요성을 인식합니다. 검색 쿼리(예: "discussion project X last week")를 제공하여 도구를 호출합니다.
5. **검색 실행:** 도구는 내부적으로 `memory_service.search_memory(app_name=..., user_id=..., query=...)`를 호출합니다.
6. **결과 반환:** `MemoryService`는 키워드 일치 또는 시맨틱 검색을 사용하여 저장소를 검색하고, 일치하는 스니펫을 `content`와 선택 사항인 `id`, `author`, `timestamp`, `custom_metadata`를 보유하는 `MemoryEntry` 객체 리스트가 포함된 `SearchMemoryResponse`로 반환합니다.
7. **에이전트의 결과 사용:** 도구는 일반적으로 컨텍스트 또는 함수 응답의 일부로 이 결과를 에이전트에 반환합니다. 그런 다음 에이전트는 이 검색된 정보를 사용하여 사용자에 대한 최종 답변을 작성할 수 있습니다.

### 에이전트가 둘 이상의 메모리 서비스에 액세스할 수 있나요?

- **표준 구성을 통해: 아니요.** 프레임워크(`adk web`, `adk api_server`)는 `--memory_service_uri` 플래그를 통해 한 번에 하나의 메모리 서비스로 구성되도록 설계되었습니다. 이 단일 서비스는 러너에 연결되며 `tool_context.search_memory()` 및 `callback_context.search_memory()`를 통해 노출됩니다.
- **에이전트 코드 내에서: 예.** 두 번째 `BaseMemoryService`를 인스턴스화하고, 프레임워크에서 구성된 서비스를 위한 `ToolContext`가 이미 있는 커스텀 도구에서 이를 참조할 수 있습니다.

예를 들어 에이전트는 대화 기록을 위해 프레임워크에서 구성된 `InMemoryMemoryService`를 사용하고, 별도의 지식 기반을 위해 `VertexAiMemoryBankService`, 문서 코퍼스 기반의 `VertexAiRagMemoryService` 또는 기타 `BaseMemoryService` 구현과 같은 두 번째 서비스를 수동으로 인스턴스화할 수 있습니다.

#### 예: 두 개의 메모리 서비스 사용

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.memory import InMemoryMemoryService
    from google.adk.tools import ToolContext

    # Second memory service for docs lookup; could be any BaseMemoryService.
    docs_memory = InMemoryMemoryService()


    async def search_all_memory(query: str, tool_context: ToolContext) -> dict:
        """Search both the conversational memory and the docs corpus."""
        conversational = await tool_context.search_memory(query)
        docs = await docs_memory.search_memory(
            app_name="docs", user_id="shared", query=query
        )
        return {
            "from_conversations": [
                part.text
                for entry in conversational.memories
                for part in (entry.content.parts or [])
                if part.text
            ],
            "from_docs": [
                part.text
                for entry in docs.memories
                for part in (entry.content.parts or [])
                if part.text
            ],
        }


    agent = Agent(
        model="gemini-flash-latest",
        name="multi_memory_agent",
        instruction=(
            "Answer questions using both your conversation history and the "
            "docs knowledge base. Use the search_all_memory tool."
        ),
        tools=[search_all_memory],
    )
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:multi_memory"
    ```
