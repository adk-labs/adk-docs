# メモリ：`MemoryService`による長期的な知識

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

`Session` は単一の会話の履歴（`events`）と一時データ（`state`）を追跡しますが、エージェントが過去のやり取りから情報を思い出す必要がある場合があります。ここで、**長期的な知識（Long-Term Knowledge）**と **`MemoryService`** の概念が登場します。次のように考えてみてください:

- **`Session` / `State`:** 特定の 1 つのチャット中の短期記憶です。
- **長期的な知識（`MemoryService`）**: エージェントが参照できる検索可能なアーカイブまたは知識ライブラリであり、過去の多くのチャットや他のソースからの情報が含まれている可能性があります。

## `MemoryService` の役割

`BaseMemoryService`（Go では `Service`）は、この検索可能な長期知識ストアを管理するためのインターフェースを定義します。次の操作をサポートします:

- **情報の取り込み（Ingesting Information）:**
    - **`add_session_to_memory`**: 完了した `Session` を受け取り、関連情報を長期知識ストアに追加します。このアプローチは、会話の要点を自動的にキャプチャするのに最適です。
    - **`add_events_to_memory`**: セッション全体を再取り込みすることなく、イベントの差分（たとえば最新のターン）を追加します。長時間実行されるセッションの途中でメモリに書き込みたい場合に便利です。
    - **`add_memory`**: 明示的な `MemoryEntry` オブジェクトをメモリに直接追加します。このメソッドはきめ細かな制御を提供し、他のソースから特定のファクトを注入するのに便利です。
- **情報の検索（`search_memory`）:** エージェント（通常は `Tool` を介して）が知識ストアにクエリを実行し、検索クエリに基づいて関連するスニペットやコンテキストを取得できるようにします。

`add_events_to_memory` と `add_memory` はオプションであり、すべてのサービスで実装されているわけではないため、利用する前に選択したサービスがそれらをサポートしているか確認してください。

## 適切なメモリサービスの選択

Python ADK には 3 つの `MemoryService` 実装が含まれています。以下の表を使用して、エージェントに最適なものを決定してください。

| **機能** | **InMemoryMemoryService** | **VertexAiMemoryBankService** | **VertexAiRagMemoryService** |
| :--- | :--- | :--- | :--- |
| **永続性** | なし（再起動時にデータは失われます） | あり（Agent Platform で管理） | あり（Knowledge Engine に保存） |
| **主なユースケース** | プロトタイピング、ローカル開発、および簡単なテスト。 | ユーザーの会話から意味のある、進化するメモリを構築します。 | 会話コーパス全体、または他の RAG インデックス済みコンテンツと併せたベクトル検索による取得。 |
| **メモリ抽出** | 会話全体を保存します | LLM を活用して会話から[意味のある情報](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/generate-memories)を抽出し、既存のメモリと統合します | [Knowledge Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview) でインデックス化された会話全体を保存します。 |
| **検索機能** | 基本的なキーワードマッチング。 | 高度なセマンティック検索。 | Knowledge Engine 上のベクトル類似度検索。 |
| **セットアップの複雑さ** | なし。デフォルトです。 | 低。Agent Platform 上の [Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview) インスタンスが必要です。 | 中。[Knowledge Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/manage-your-rag-corpus) が必要です。 |
| **依存関係** | なし。 | Google Cloud プロジェクト、Agent Platform API | Google Cloud プロジェクト、Knowledge Engine、Agent Platform SDK（オプションのインストール）。 |
| **使用するタイミング** | プロトタイピングのために複数のセッションのチャット履歴を横断して検索したい場合。 | エージェントに過去のやり取りを記憶させ、学習させたい場合。 | 既存の RAG インフラストラクチャがある場合、または生の会話トランスクリプトを検索したい場合。 |

`google.adk.memory` から `VertexAiRagMemoryService` を常にインポートできますが、`pip install google-adk[gcp]` で Agent Platform SDK がインストールされていない限り、構築時に `ImportError` が発生します。Memory Bank と RAG バックアップメモリについては、以下の [Memory Bank](#memory-bank) と [RAG メモリ](#rag-memory) で説明されています。


## `InMemoryMemoryService`

`InMemoryMemoryService` は、アプリケーションのメモリにセッション情報を保存し、検索のために基本的なキーワードマッチングを実行します。セットアップは不要で、永続性が必要ないプロトタイピングや簡単なテストシナリオに最適です。

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

**例：メモリの追加と検索**

この例では、簡単にするために `InMemoryMemoryService` を使用した基本的なフローを示します。

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

### ツール内でのメモリ検索

ツールコンテキストを使用して、カスタムツール内からメモリを検索することもできます。

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

`VertexAiMemoryBankService` は、会話型エージェントに高度で永続的なメモリ機能を提供するフルマネージドの Google Cloud サービスである [Memory Bank](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview) にエージェントを接続します。

### 仕組み

このサービスは、2 つの主要な操作を処理します:

- **メモリの生成:** 会話の最後に、セッションのイベントを Memory Bank に送信できます。Memory Bank は情報をインテリジェントに処理し、「メモリ」として保存します。
- **メモリの取得:** エージェントコードは、Memory Bank に対して検索クエリを発行し、過去の会話から関連するメモリを取得できます。

### `add_memory` による直接的なメモリ取り込み

セッション履歴からメモリを生成するだけでなく、`VertexAiMemoryBankService` は `add_memory` メソッドによる直接的なメモリ取り込みもサポートしています。このメソッドを使用すると、Memory Bank に保存されるファクトを正確に制御できます。

動作は `enable_consolidation` オプションによって異なります:

- **直接作成（デフォルト）:** デフォルトでは、`add_memory` は基盤となる `memories.create` API を呼び出します。指定した各 `MemoryEntry` は、個別の独立したメモリ項目として追加されます。

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

- **統合を伴う作成（Creation with Consolidation）:** `custom_metadata` で `enable_consolidation` を `True` に設定すると、サービスは `memories.generate` API を使用します。この設定により、Memory Bank は新しいメモリ項目を既存の関連メモリとインテリジェントに統合し、重複を防いでより一貫性のあるナレッジベースを構築できます。

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

### 前提条件

この機能を使用する前に、次のものが必要です:

1. **Google Cloud プロジェクト:** Agent Platform API が有効になっていること。
2. **Agent Runtime:** Agent Platform 上で Agent Runtime を作成する必要があります。Memory Bank を使用するためにエージェントを Agent Runtime にデプロイする必要はありません。このセットアップにより、構成に必要な **Agent Runtime ID** が提供されます。
3. **認証:** ローカル環境が Google Cloud サービスにアクセスできるように認証されていることを確認します。最も簡単な方法は、次を実行することです:

    ```bash
    gcloud auth application-default login
    ```

4. **環境変数:** このサービスには、Google Cloud プロジェクト ID とロケーションが必要です。それらを環境変数として設定します:

    ```bash
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    export GOOGLE_CLOUD_LOCATION="your-gcp-location"
    ```

ADK エージェントから Google Cloud に接続する方法の詳細については、[Google Cloud と Agent Platform への接続](/get-started/google-cloud/)を参照してください。

### 構成

エージェントを Memory Bank に接続するには、ADK サーバー（`adk web` または `adk api_server`）を起動するときに `--memory_service_uri` フラグを使用します。URI（Uniform Resource Identifier）は `agentengine://<agent_engine_id>` の形式である必要があります。

```bash title="bash"
adk web path/to/your/agents_dir --memory_service_uri="agentengine://1234567890"
```

または、`VertexAiMemoryBankService` を手動でインスタンス化し、それを `Runner` に渡すことで、Memory Bank を使用するようにエージェントを構成できます。

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

## RAG メモリ {#rag-memory}

`VertexAiRagMemoryService` は、会話を [Knowledge Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview) に保存し、ベクトル類似度によって取得します。既存の RAG インフラストラクチャがある場合や、Memory Bank によって生成される LLM 抽出メモリではなく生のトランスクリプト取得を行いたい場合に使用します。Agent Platform SDK が必要です。

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

## エージェントでのメモリの使用

メモリサービスが構成されている場合、エージェントはツールまたはコールバックを使用してメモリを取得できます。ADK には、メモリを取得するための 2 つの事前構築済みツールが含まれています:

- **メモリの事前ロード（Preload memory）**: コールバックと同様に、各ターンの開始時にメモリを自動的に取得します。
- **メモリのロード（Load memory）**: エージェントが役立つと判断したときにメモリを取得します。

**例:**

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

セッションからメモリを抽出するには、`add_session_to_memory` を呼び出す必要があります。たとえば、コールバックを使用してこのステップを自動化できます:

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

    ADK Go では、エージェントのコールバックからメモリサービスにアクセスできません。代わりにプラグインの `AfterRunCallback` からセッションを保存し、メモリサービスとともにそのプラグインをランナーに登録してください:

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

### コールバックから特定のイベントまたはファクトを書き込む

<div class="language-support-tag">
   <span class="lst-supported">ADKでサポート</span><span class="lst-kotlin">Kotlin v0.7.0</span>
</div>

`CallbackContext.addSessionToMemory` メソッドはメモリのデフォルトの動作であり、エージェントのセッション全体を保存します。より詳細な制御が必要な場合、`CallbackContext` は選択したイベントのサブセット用の `addEventsToMemory` と、自身で構築したファクト用の `addMemory` の 2 つの追加メソッドも提供します。どちらもオプションの `customMetadata` を受け入れ、現在の呼び出しからアプリ、ユーザー、セッションを自動的に補完します。

```kotlin
--8<-- "examples/kotlin/snippets/sessions/MemoryExample.kt:callback_memory_writes"
```

3 つのメソッドはすべて、ランナーにメモリ サービスが構成されていない場合に `IllegalStateException` をスローするため、コンパイル時ではなく実行時に失敗します。

## メモリ機能の拡張

`BaseMemoryService` を拡張したメモリ サービスは、カスタム メタデータを含め、エージェント メモリにセッションやイベントを追加することをサポートします。以下のコード例に示すように、`InMemoryMemoryService` などのメモリ サービスの `add_session_to_memory` および `add_events_to_memory` メソッドを使用してメモリ データを修正できます。

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

## 高度な概念

### 実務におけるメモリの仕組み

メモリワークフローには、次のステップが含まれます:

1. **セッションの対話:** ユーザーは `SessionService` によって管理される `Session` を介してエージェントと対話します。この対話の間、イベントが記録され、セッション状態が更新される場合があります。
2. **メモリへの取り込み:** セッションが終了するか、重要な情報が収集されると、アプリケーションは `memory_service.add_session_to_memory(session)` を呼び出します。このアクションにより、重要なデータが抽出され、Agent Runtime Memory Bank などの長期的な知識ストアに永続化されます。
3. **後のクエリ:** 異なるセッション、または同じセッションで、過去のコンテキストを必要とする質問をする場合があります（例：「先週、プロジェクト X について何を話し合いましたか？」）。
4. **エージェントがメモリツールを使用:** 組み込みの `load_memory` ツールなど、メモリ取得ツールを備えたエージェントは、過去のコンテキストの必要性を認識します。ツールを呼び出し、検索クエリ（例：「discussion project X last week」）を提供します。
5. **検索の実行:** ツールは内部的に `memory_service.search_memory(app_name=..., user_id=..., query=...)` を呼び出します。
6. **結果の返却:** `MemoryService` は、キーワードマッチングまたはセマンティック検索を使用してストアを検索し、一致するスニペットを、`content` とすべてのオプション項目（`id`、`author`、`timestamp`、`custom_metadata`）を保持する `MemoryEntry` オブジェクトのリストを含む `SearchMemoryResponse` として返します。
7. **エージェントが結果を使用:** ツールはこれらの結果をエージェントに返し、通常はコンテキストまたは関数応答の一部として返します。その後、エージェントはこの取得した情報を使用して、ユーザーへの最終的な回答を作成できます。

### エージェントは複数のメモリサービスにアクセスできますか？

- **標準構成を介して：いいえ。** フレームワーク（`adk web`、`adk api_server`）は、`--memory_service_uri` フラグを介して一度に 1 つのメモリサービスで構成するように設計されています。その単一のサービスはランナーに組み込まれ、`tool_context.search_memory()` および `callback_context.search_memory()` を介して公開されます。
- **エージェントのコード内：はい。** 2 番目の `BaseMemoryService` をインスタンス化し、フレームワークで構成されたサービス用の `ToolContext` をすでに持っているカスタムツールからそれを参照できます。

たとえば、エージェントは会話履歴用にフレームワークで構成された `InMemoryMemoryService` を使用し、別のナレッジベース用に `VertexAiMemoryBankService` や、ドキュメントコーパスに対する `VertexAiRagMemoryService`、またはその他の `BaseMemoryService` 実装などの 2 番目のサービスを手動でインスタンス化できます。

#### 例：2 つのメモリサービスの使用

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
