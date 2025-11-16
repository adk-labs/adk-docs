# ADKにおけるマルチエージェントシステム

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

エージェント型アプリケーションが複雑になるにつれて、モノリシックな単一のエージェントとして構成することは、開発、保守、および推論が困難になる可能性があります。Agent Development Kit (ADK) は、複数の異なる`BaseAgent`インスタンスを**マルチエージェントシステム (MAS)** に組み込むことで、洗練されたアプリケーションの構築をサポートします。

ADKにおいて、マルチエージェントシステムとは、しばしば階層を形成する異なるエージェントが、より大きな目標を達成するために協力または調整するアプリケーションです。アプリケーションをこのように構成することで、モジュール性、専門性、再利用性、保守性の向上、および専用のワークフローエージェントを使用した構造化された制御フローの定義能力など、大きな利点が得られます。

`BaseAgent`から派生したさまざまなタイプのエージェントを組み合わせて、これらのシステムを構築できます。

* **LLMエージェント:** 大規模言語モデルを搭載したエージェント。（[LLMエージェント](llm-agents.md)参照）
* **ワークフローエージェント:** サブエージェントの実行フローを管理するために設計された特殊なエージェント（`SequentialAgent`、`ParallelAgent`、`LoopAgent`）。（[ワークフローエージェント](workflow-agents/index.md)参照）
* **カスタムエージェント:** `BaseAgent`を継承し、LLM以外の専門的なロジックを持つ独自のエージェント。（[カスタムエージェント](custom-agents.md)参照）

以下のセクションでは、これらのマルチエージェントシステムを効果的に構築および管理できるようにする、エージェント階層、ワークフローエージェント、インタラクションメカニズムといったADKのコアプリミティブについて詳しく説明します。

## 1. エージェント構成のためのADKプリミティブ { #adk-primitives-for-agent-composition }

ADKは、マルチエージェントシステム内のインタラクションを構造化し管理することを可能にする、コアとなる構成要素（プリミティブ）を提供します。

!!! Note
    プリミティブの特定のパラメータ名やメソッド名は、SDKの言語によって若干異なる場合があります（例：Pythonの`sub_agents`、Javaの`subAgents`）。詳細については、各言語のAPIドキュメントを参照してください。

### 1.1. エージェント階層（親エージェント、サブエージェント） { #agent-hierarchy-parent-agent-sub-agents }

マルチエージェントシステムの構成の基礎は、`BaseAgent`で定義された親子関係です。

* **階層の確立:** 親エージェントの初期化時に`sub_agents`引数にエージェントインスタンスのリストを渡すことで、ツリー構造を作成します。ADKは初期化中に各子エージェントに`parent_agent`属性を自動的に設定します。
* **単一の親ルール:** エージェントインスタンスは、サブエージェントとして一度しか追加できません。2番目の親を割り当てようとすると`ValueError`が発生します。
* **重要性:** この階層は[ワークフローエージェント](#12-workflow-agents-as-orchestrators)のスコープを定義し、LLM駆動の委任の潜在的なターゲットに影響を与えます。`agent.parent_agent`を使用して階層をナビゲートしたり、`agent.find_agent(name)`を使用して子孫エージェントを見つけたりすることができます。

=== "Python"

    ```python
    # 概念例：階層の定義
    from google.adk.agents import LlmAgent, BaseAgent
    
    # 個々のエージェントを定義
    greeter = LlmAgent(name="Greeter", model="gemini-2.0-flash")
    task_doer = BaseAgent(name="TaskExecutor") # カスタムの非LLMエージェント
    
    # 親エージェントを作成し、sub_agents経由で子を割り当て
    coordinator = LlmAgent(
        name="Coordinator",
        model="gemini-2.0-flash",
        description="挨拶とタスクを調整します。",
        sub_agents=[ # ここでsub_agentsを割り当て
            greeter,
            task_doer
        ]
    )
    
    # フレームワークが自動的に設定：
    # assert greeter.parent_agent == coordinator
    # assert task_doer.parent_agent == coordinator
    ```

=== "Java"

    ```java
    // 概念例：階層の定義
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.agents.LlmAgent;
    
    // 個々のエージェントを定義
    LlmAgent greeter = LlmAgent.builder().name("Greeter").model("gemini-2.0-flash").build();
    SequentialAgent taskDoer = SequentialAgent.builder().name("TaskExecutor").subAgents(...).build(); // シーケンシャルエージェント
    
    // 親エージェントを作成し、sub_agentsを割り当て
    LlmAgent coordinator = LlmAgent.builder()
        .name("Coordinator")
        .model("gemini-2.0-flash")
        .description("挨拶とタスクを調整します。")
        .subAgents(greeter, taskDoer) // ここでsub_agentsを割り当て
        .build();
    
    // フレームワークが自動的に設定：
    // assert greeter.parentAgent().equals(coordinator);
    // assert taskDoer.parentAgent().equals(coordinator);
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:hierarchy"
    ```

### 1.2. オーケストレーターとしてのワークフローエージェント { #workflow-agents-as-orchestrators }

ADKには、自身でタスクを実行するのではなく、`sub_agents`の実行フローを調整（オーケストレート）する`BaseAgent`から派生した特殊なエージェントが含まれています。

* **[`SequentialAgent`](workflow-agents/sequential-agents.md):** `sub_agents`をリストされた順に一つずつ実行します。
    * **コンテキスト:** *同じ*[`InvocationContext`](../runtime/index.md)を順次渡すことで、エージェントが共有ステートを介して結果を簡単に渡せるようにします。

=== "Python"

    ```python
    # 概念例：シーケンシャルパイプライン
    from google.adk.agents import SequentialAgent, LlmAgent

    step1 = LlmAgent(name="Step1_Fetch", output_key="data") # 出力をstate['data']に保存
    step2 = LlmAgent(name="Step2_Process", instruction="{data}からのデータを処理します。")

    pipeline = SequentialAgent(name="MyPipeline", sub_agents=[step1, step2])
    # pipelineが実行されると、Step2はStep1が設定したstate['data']にアクセスできます。
    ```

=== "Java"

    ```java
    // 概念例：シーケンシャルパイプライン
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.agents.LlmAgent;

    LlmAgent step1 = LlmAgent.builder().name("Step1_Fetch").outputKey("data").build(); // 出力をstate.get("data")に保存
    LlmAgent step2 = LlmAgent.builder().name("Step2_Process").instruction("Process data from {data}.").build();

    SequentialAgent pipeline = SequentialAgent.builder().name("MyPipeline").subAgents(step1, step2).build();
    // pipelineが実行されると、Step2はStep1が設定したstate.get("data")にアクセスできます。
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:sequential-pipeline"
    ```

* **[`ParallelAgent`](workflow-agents/parallel-agents.md):** `sub_agents`を並列で実行します。サブエージェントからのイベントはインターリーブされる可能性があります。
    * **コンテキスト:** 各子エージェントの`InvocationContext.branch`を変更し（例：`ParentBranch.ChildName`）、別個のコンテキストパスを提供します。これは一部のメモリー実装で履歴を分離するのに役立ちます。
    * **ステート:** ブランチが異なっていても、すべての並列の子は*同じ共有*`session.state`にアクセスし、初期ステートの読み取りと結果の書き込みができます（競合状態を避けるために別個のキーを使用）。

=== "Python"

    ```python
    # 概念例：並列実行
    from google.adk.agents import ParallelAgent, LlmAgent

    fetch_weather = LlmAgent(name="WeatherFetcher", output_key="weather")
    fetch_news = LlmAgent(name="NewsFetcher", output_key="news")

    gatherer = ParallelAgent(name="InfoGatherer", sub_agents=[fetch_weather, fetch_news])
    # gathererが実行されると、WeatherFetcherとNewsFetcherが同時に実行されます。
    # 後続のエージェントはstate['weather']とstate['news']を読み取ることができます。
    ```
  
=== "Java"

    ```java
    // 概念例：並列実行
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.ParallelAgent;
   
    LlmAgent fetchWeather = LlmAgent.builder()
        .name("WeatherFetcher")
        .outputKey("weather")
        .build();
    
    LlmAgent fetchNews = LlmAgent.builder()
        .name("NewsFetcher")
        .instruction("news")
        .build();
    
    ParallelAgent gatherer = ParallelAgent.builder()
        .name("InfoGatherer")
        .subAgents(fetchWeather, fetchNews)
        .build();
    
    // gathererが実行されると、WeatherFetcherとNewsFetcherが同時に実行されます。
    // 後続のエージェントはstate['weather']とstate['news']を読み取ることができます。
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/parallelagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:parallel-execution"
    ```

  * **[`LoopAgent`](workflow-agents/loop-agents.md):** `sub_agents`をループ内で順次実行します。
      * **終了:** オプションの`max_iterations`に達した場合、またはいずれかのサブエージェントが`Event Actions`に`escalate=True`を含む[`Event`](../events/index.md)を返した場合にループは停止します。
      * **コンテキストとステート:** 各イテレーションで*同じ*`InvocationContext`を渡すことで、ステートの変更（カウンター、フラグなど）がループ間で持続するようにします。

=== "Python"

      ```python
      # 概念例：条件付きループ
      from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
      from google.adk.events import Event, EventActions
      from google.adk.agents.invocation_context import InvocationContext
      from typing import AsyncGenerator

      class CheckCondition(BaseAgent): # ステートを確認するカスタムエージェント
          async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
              status = ctx.session.state.get("status", "pending")
              is_done = (status == "completed")
              yield Event(author=self.name, actions=EventActions(escalate=is_done)) # 完了したらエスカレート

      process_step = LlmAgent(name="ProcessingStep") # state['status']を更新する可能性のあるエージェント

      poller = LoopAgent(
          name="StatusPoller",
          max_iterations=10,
          sub_agents=[process_step, CheckCondition(name="Checker")]
      )
      # pollerが実行されると、Checkerがエスカレートするまで（state['status'] == 'completed'）、
      # または10回のイテレーションが経過するまで、process_stepとCheckerを繰り返し実行します。
      ```
    
=== "Java"

    ```java
    // 概念例：条件付きループ
    // ステートを確認し、エスカレートする可能性のあるカスタムエージェント
    public static class CheckConditionAgent extends BaseAgent {
      public CheckConditionAgent(String name, String description) {
        super(name, description, List.of(), null, null);
      }
  
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext ctx) {
        String status = (String) ctx.session().state().getOrDefault("status", "pending");
        boolean isDone = "completed".equalsIgnoreCase(status);

        // 条件が満たされた場合、エスカレート（ループを抜ける）を知らせるイベントを発行します。
        // 未完了の場合、escalateフラグはfalseまたは存在せず、ループは継続します。
        Event checkEvent = Event.builder()
                .author(name())
                .id(Event.generateEventId()) // イベントに一意のIDを付与することが重要
                .actions(EventActions.builder().escalate(isDone).build()) // 完了したらエスカレート
                .build();
        return Flowable.just(checkEvent);
      }
    }
  
    // state.put("status")を更新する可能性のあるエージェント
    LlmAgent processingStepAgent = LlmAgent.builder().name("ProcessingStep").build();
    // 条件をチェックするためのカスタムエージェントインスタンス
    CheckConditionAgent conditionCheckerAgent = new CheckConditionAgent(
        "ConditionChecker",
        "ステータスが'completed'かどうかをチェックします。"
    );
    LoopAgent poller = LoopAgent.builder().name("StatusPoller").maxIterations(10).subAgents(processingStepAgent, conditionCheckerAgent).build();
    // pollerが実行されると、Checkerがエスカレートするまで（state.get("status") == "completed"）、
    // または10回のイテレーションが経過するまで、processingStepAgentとconditionCheckerAgentを繰り返し実行します。
    ```

=== "Go"

    ```go
    import (
        "iter"
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/loopagent"
        "google.golang.org/adk/session"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:loop-with-condition"
    ```

### 1.3. インタラクションと通信メカニズム { #interaction-communication-mechanisms }

システム内のエージェントは、しばしば互いにデータを交換したり、アクションをトリガーしたりする必要があります。ADKはこれを以下の方法で容易にします。

#### a) 共有セッションステート（`session.state`）

同じ呼び出し内で動作し、`InvocationContext`を介して同じ[`Session`](../sessions/session.md)オブジェクトを共有するエージェントが、受動的に通信するための最も基本的な方法です。

* **メカニズム:** あるエージェント（またはそのツール/コールバック）が値を書き込み（`context.state['data_key'] = processed_data`）、後続のエージェントがそれを読み取ります（`data = context.state.get('data_key')`）。ステートの変更は[`CallbackContext`](../callbacks/index.md)を介して追跡されます。
* **利便性:** [`LlmAgent`](llm-agents.md)の`output_key`プロパティは、エージェントの最終的な応答テキスト（または構造化出力）を指定されたステートキーに自動的に保存します。
* **性質:** 非同期で受動的な通信。`SequentialAgent`によって調整されるパイプラインや、`LoopAgent`のイテレーション間でデータを渡すのに理想的です。
* **参照:** [ステート管理](../sessions/state.md)

!!! note "呼び出しコンテキストと`temp:`ステート"
    親エージェントがサブエージェントを呼び出すとき、同じ`InvocationContext`を渡します。これは、それらが同じ一時的な（`temp:`）ステートを共有することを意味し、現在のターンにのみ関連するデータを渡すのに理想的です。

=== "Python"

    ```python
    # 概念例：output_keyの使用とステートの読み取り
    from google.adk.agents import LlmAgent, SequentialAgent
    
    agent_A = LlmAgent(name="AgentA", instruction="フランスの首都を見つけてください。", output_key="capital_city")
    agent_B = LlmAgent(name="AgentB", instruction="{capital_city}に保存されている都市について教えてください。")
    
    pipeline = SequentialAgent(name="CityInfo", sub_agents=[agent_A, agent_B])
    # AgentAが実行され、「Paris」をstate['capital_city']に保存します。
    # AgentBが実行され、そのinstructionプロセッサがstate['capital_city']を読み取って「Paris」を取得します。
    ```

=== "Java"

    ```java
    // 概念例：outputKeyの使用とステートの読み取り
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    
    LlmAgent agentA = LlmAgent.builder()
        .name("AgentA")
        .instruction("Find the capital of France.")
        .outputKey("capital_city")
        .build();
    
    LlmAgent agentB = LlmAgent.builder()
        .name("AgentB")
        .instruction("Tell me about the city stored in {capital_city}.")
        .outputKey("capital_city")
        .build();
    
    SequentialAgent pipeline = SequentialAgent.builder().name("CityInfo").subAgents(agentA, agentB).build();
    // AgentAが実行され、「Paris」をstate('capital_city')に保存します。
    // AgentBが実行され、そのinstructionプロセッサがstate.get("capital_city")を読み取って「Paris」を取得します。
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:output-key-state"
    ```

#### b) LLM駆動の委任（エージェント移譲）

[`LlmAgent`](llm-agents.md)の理解力を活用して、階層内の他の適切なエージェントにタスクを動的にルーティングします。

* **メカニズム:** エージェントのLLMが特定の関数呼び出しを生成します: `transfer_to_agent(agent_name='target_agent_name')`。
* **処理:** サブエージェントが存在するか、移譲が禁止されていない場合にデフォルトで使用される`AutoFlow`がこの呼び出しを捕捉します。`root_agent.find_agent()`を使用してターゲットエージェントを特定し、`InvocationContext`を更新して実行の焦点を切り替えます。
* **要件:** 呼び出し元の`LlmAgent`には、いつ移譲するかについての明確な`instructions`が必要であり、潜在的なターゲットエージェントには、LLMが情報に基づいた決定を下せるように、明確な`description`が必要です。移譲のスコープ（親、サブエージェント、兄弟）は`LlmAgent`で設定できます。
* **性質:** LLMの解釈に基づく、動的で柔軟なルーティング。

=== "Python"

    ```python
    # 概念設定：LLM移譲
    from google.adk.agents import LlmAgent
    
    booking_agent = LlmAgent(name="Booker", description="フライトとホテルの予約を処理します。")
    info_agent = LlmAgent(name="Info", description="一般情報を提供し、質問に答えます。")
    
    coordinator = LlmAgent(
        name="Coordinator",
        model="gemini-2.0-flash",
        instruction="あなたはアシスタントです。予約タスクはBookerに、情報要求はInfoに委任してください。",
        description="メインのコーディネーター。",
        # AutoFlowは通常、ここで暗黙的に使用されます
        sub_agents=[booking_agent, info_agent]
    )
    # coordinatorが「フライトを予約して」というリクエストを受け取ると、そのLLMは次を生成するべきです：
    # FunctionCall(name='transfer_to_agent', args={'agent_name': 'Booker'})
    # その後、ADKフレームワークは実行をbooking_agentにルーティングします。
    ```

=== "Java"

    ```java
    // 概念設定：LLM移譲
    import com.google.adk.agents.LlmAgent;
    
    LlmAgent bookingAgent = LlmAgent.builder()
        .name("Booker")
        .description("フライトとホテルの予約を処理します。")
        .build();
    
    LlmAgent infoAgent = LlmAgent.builder()
        .name("Info")
        .description("一般情報を提供し、質問に答えます。")
        .build();
    
    // コーディネーターエージェントを定義
    LlmAgent coordinator = LlmAgent.builder()
        .name("Coordinator")
        .model("gemini-2.0-flash") // または希望のモデル
        .instruction("あなたはアシスタントです。予約タスクはBookerに、情報要求はInfoに委任してください。")
        .description("メインのコーディネーター。")
        // AutoFlowは、subAgentsが存在し、移譲が禁止されていないため、
        // デフォルトで（暗黙的に）使用されます。
        .subAgents(bookingAgent, infoAgent)
        .build();

    // coordinatorが「フライトを予約して」というリクエストを受け取ると、そのLLMは次を生成するべきです：
    // FunctionCall.builder.name("transferToAgent").args(ImmutableMap.of("agent_name", "Booker")).build()
    // その後、ADKフレームワークは実行をbookingAgentにルーティングします。
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent/llmagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:llm-transfer"
    ```

#### c) 明示的な呼び出し（`AgentTool`）

[`LlmAgent`](llm-agents.md)が他の`BaseAgent`インスタンスを呼び出し可能な関数や[ツール](../tools/index.md)として扱うことを可能にします。

* **メカニズム:** ターゲットエージェントインスタンスを`AgentTool`でラップし、親`LlmAgent`の`tools`リストに含めます。`AgentTool`はLLMに対応する関数宣言を生成します。
* **処理:** 親のLLMが`AgentTool`をターゲットとする関数呼び出しを生成すると、フレームワークは`AgentTool.run_async`を実行します。このメソッドはターゲットエージェントを実行し、その最終応答をキャプチャし、ステート/アーティファクトの変更を親のコンテキストに転送し、応答をツールの結果として返します。
* **性質:** 他のツールと同様に、同期的（親のフロー内）、明示的、制御された呼び出し。
* **(注：** `AgentTool`は明示的にインポートして使用する必要があります)。

=== "Python"

    ```python
    # 概念設定：ツールとしてのエージェント
    from google.adk.agents import LlmAgent, BaseAgent
    from google.adk.tools import agent_tool
    from pydantic import BaseModel
    
    # ターゲットエージェントを定義（LlmAgentまたはカスタムBaseAgent）
    class ImageGeneratorAgent(BaseAgent): # カスタムエージェントの例
        name: str = "ImageGen"
        description: str = "プロンプトに基づいて画像を生成します。"
        # ... 内部ロジック ...
        async def _run_async_impl(self, ctx): # 簡略化された実行ロジック
            prompt = ctx.session.state.get("image_prompt", "デフォルトのプロンプト")
            # ... 画像バイトを生成 ...
            image_bytes = b"..."
            yield Event(author=self.name, content=types.Content(parts=[types.Part.from_bytes(image_bytes, "image/png")]))
    
    image_agent = ImageGeneratorAgent()
    image_tool = agent_tool.AgentTool(agent=image_agent) # エージェントをラップ
    
    # 親エージェントがAgentToolを使用
    artist_agent = LlmAgent(
        name="Artist",
        model="gemini-2.0-flash",
        instruction="プロンプトを作成し、ImageGenツールを使って画像を生成してください。",
        tools=[image_tool] # AgentToolを含める
    )
    # ArtistのLLMがプロンプトを生成し、次を呼び出します：
    # FunctionCall(name='ImageGen', args={'image_prompt': '帽子をかぶった猫'})
    # フレームワークがimage_tool.run_async(...)を呼び出し、それがImageGeneratorAgentを実行します。
    # 結果の画像Partは、ツール結果としてArtistエージェントに返されます。
    ```

=== "Java"

    ```java
    // 概念設定：ツールとしてのエージェント
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;

    // カスタムエージェントの例（LlmAgentまたはカスタムBaseAgent）
    public class ImageGeneratorAgent extends BaseAgent  {
    
      public ImageGeneratorAgent(String name, String description) {
        super(name, description, List.of(), null, null);
      }
    
      // ... 内部ロジック ...
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) { // 簡略化された実行ロジック
        invocationContext.session().state().get("image_prompt");
        // 画像バイトを生成
        // ...
    
        Event responseEvent = Event.builder()
            .author(this.name())
            .content(Content.fromParts(Part.fromText("\b...")))
            .build();
    
        return Flowable.just(responseEvent);
      }
    
      @Override
      protected Flowable<Event> runLiveImpl(InvocationContext invocationContext) {
        return null;
      }
    }

    // AgentToolを使用してエージェントをラップ
    ImageGeneratorAgent imageAgent = new ImageGeneratorAgent("image_agent", "画像を生成します");
    AgentTool imageTool = AgentTool.create(imageAgent);
    
    // 親エージェントがAgentToolを使用
    LlmAgent artistAgent = LlmAgent.builder()
            .name("Artist")
            .model("gemini-2.0-flash")
            .instruction(
                    "あなたはアーティストです。画像の詳細なプロンプトを作成し、" +
                            "'ImageGen'ツールを使って画像を生成してください。" +
                            "'ImageGen'ツールは、画像プロンプトを含む'request'という名前の単一の文字列引数を期待します。" +
                            "ツールは'result'フィールドに'image_base64'、'mime_type'、'status'を含むJSON文字列を返します。"
            )
            .description("生成ツールを使用して画像を作成できるエージェントです。")
            .tools(imageTool) // AgentToolを含める
            .build();
    
    // ArtistのLLMがプロンプトを生成し、次を呼び出します：
    // FunctionCall(name='ImageGen', args={'imagePrompt': '帽子をかぶった猫'})
    // フレームワークがimageTool.runAsync(...)を呼び出し、それがImageGeneratorAgentを実行します。
    // 結果の画像Partは、ツール結果としてArtistエージェントに返されます。
    ```

=== "Go"

    ```go
    import (
        "fmt"
        "iter"
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/model"
        "google.golang.org/adk/session"
        "google.golang.org/adk/tool"
        "google.golang.org/adk/tool/agenttool"
        "google.golang.org/genai"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:agent-as-tool"
    ```

これらのプリミティブは、密結合されたシーケンシャルなワークフローから、動的なLLM駆動の委任ネットワークまで、さまざまなマルチエージェントのインタラクションを設計するための柔軟性を提供します。

## 2. ADKプリミティブを使用した一般的なマルチエージェントパターン { #common-multi-agent-patterns-using-adk-primitives }

ADKの構成プリミティブを組み合わせることで、マルチエージェント連携のための確立されたさまざまなパターンを実装できます。

### コーディネーター/ディスパッチャーパターン

* **構造:** 中央の[`LlmAgent`](llm-agents.md)（コーディネーター）が、いくつかの専門的な`sub_agents`を管理します。
* **目的:** 受信したリクエストを適切な専門エージェントにルーティングします。
* **使用されるADKプリミティブ:**
    * **階層:** コーディネーターは`sub_agents`に専門家をリストアップします。
    * **インタラクション:** 主に**LLM駆動の委任**（サブエージェントに明確な`description`とコーディネーターに適切な`instruction`が必要）または**明示的な呼び出し（`AgentTool`）**（コーディネーターが`AgentTool`でラップされた専門家を`tools`に含める）を使用します。

=== "Python"

    ```python
    # 概念コード：LLM移譲を使用するコーディネーター
    from google.adk.agents import LlmAgent
    
    billing_agent = LlmAgent(name="Billing", description="請求に関する問い合わせを処理します。")
    support_agent = LlmAgent(name="Support", description="技術サポートのリクエストを処理します。")
    
    coordinator = LlmAgent(
        name="HelpDeskCoordinator",
        model="gemini-2.0-flash",
        instruction="ユーザーのリクエストをルーティングしてください：支払い問題にはBillingエージェントを、技術的な問題にはSupportエージェントを使用してください。",
        description="メインのヘルプデスクルーター。",
        # allow_transfer=TrueはAutoFlowでsub_agentsがある場合、しばしば暗黙的に設定されます
        sub_agents=[billing_agent, support_agent]
    )
    # ユーザーの質問：「支払いが失敗しました」 -> コーディネーターのLLMは transfer_to_agent(agent_name='Billing') を呼び出すべきです。
    # ユーザーの質問：「ログインできません」 -> コーディネーターのLLMは transfer_to_agent(agent_name='Support') を呼び出すべきです。
    ```

=== "Java"

    ```java
    // 概念コード：LLM移譲を使用するコーディネーター
    import com.google.adk.agents.LlmAgent;

    LlmAgent billingAgent = LlmAgent.builder()
        .name("Billing")
        .description("請求に関する問い合わせや支払い問題を処理します。")
        .build();

    LlmAgent supportAgent = LlmAgent.builder()
        .name("Support")
        .description("技術サポートのリクエストやログイン問題を処理します。")
        .build();

    LlmAgent coordinator = LlmAgent.builder()
        .name("HelpDeskCoordinator")
        .model("gemini-2.0-flash")
        .instruction("ユーザーのリクエストをルーティングしてください：支払い問題にはBillingエージェントを、技術的な問題にはSupportエージェントを使用してください。")
        .description("メインのヘルプデスクルーター。")
        .subAgents(billingAgent, supportAgent)
        // エージェント移譲は、Autoflowでサブエージェントと共に暗黙的に行われます。
        // .disallowTransferToParentやdisallowTransferToPeersで指定されない限り。
        .build();

    // ユーザーの質問：「支払いが失敗しました」 -> コーディネーターのLLMは
    // transferToAgent(agentName='Billing') を呼び出すべきです。
    // ユーザーの質問：「ログインできません」 -> コーディネーターのLLMは
    // transferToAgent(agentName='Support') を呼び出すべきです。
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:coordinator-pattern"
    ```

### シーケンシャルパイプラインパターン

* **構造:** [`SequentialAgent`](workflow-agents/sequential-agents.md)が、固定された順序で実行される`sub_agents`を含みます。
* **目的:** あるステップの出力が次のステップの入力となる多段階プロセスを実装します。
* **使用されるADKプリミティブ:**
    * **ワークフロー:** `SequentialAgent`が順序を定義します。
    * **通信:** 主に**共有セッションステート**を使用します。前のエージェントが結果を書き込み（しばしば`output_key`経由）、後のエージェントが`context.state`からその結果を読み取ります。

=== "Python"

    ```python
    # 概念コード：シーケンシャルデータパイプライン
    from google.adk.agents import SequentialAgent, LlmAgent
    
    validator = LlmAgent(name="ValidateInput", instruction="入力を検証してください。", output_key="validation_status")
    processor = LlmAgent(name="ProcessData", instruction="{validation_status}が'valid'の場合、データを処理してください。", output_key="result")
    reporter = LlmAgent(name="ReportResult", instruction="{result}からの結果を報告してください。")
    
    data_pipeline = SequentialAgent(
        name="DataPipeline",
        sub_agents=[validator, processor, reporter]
    )
    # validator実行 -> state['validation_status']に保存
    # processor実行 -> state['validation_status']を読み取り、state['result']に保存
    # reporter実行 -> state['result']を読み取り
    ```

=== "Java"

    ```java
    // 概念コード：シーケンシャルデータパイプライン
    import com.google.adk.agents.SequentialAgent;
    
    LlmAgent validator = LlmAgent.builder()
        .name("ValidateInput")
        .instruction("入力を検証してください")
        .outputKey("validation_status") // メインのテキスト出力をsession.state["validation_status"]に保存
        .build();
    
    LlmAgent processor = LlmAgent.builder()
        .name("ProcessData")
        .instruction("{validation_status}が'valid'の場合、データを処理してください")
        .outputKey("result") // メインのテキスト出力をsession.state["result"]に保存
        .build();
    
    LlmAgent reporter = LlmAgent.builder()
        .name("ReportResult")
        .instruction("{result}からの結果を報告してください")
        .build();
    
    SequentialAgent dataPipeline = SequentialAgent.builder()
        .name("DataPipeline")
        .subAgents(validator, processor, reporter)
        .build();
    
    // validator実行 -> state['validation_status']に保存
    // processor実行 -> state['validation_status']を読み取り、state['result']に保存
    // reporter実行 -> state['result']を読み取り
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:sequential-pipeline-pattern"
    ```

### 並列ファンアウト/ギャザーパターン

* **構造:** [`ParallelAgent`](workflow-agents/parallel-agents.md)が複数の`sub_agents`を同時に実行し、しばしば後続のエージェント（`SequentialAgent`内）が結果を集約します。
* **目的:** 独立したタスクを同時に実行して遅延を減らし、その出力を結合します。
* **使用されるADKプリミティブ:**
    * **ワークフロー:** 同時実行のための`ParallelAgent`（ファンアウト）。しばしば後続の集約ステップ（ギャザー）を処理するために`SequentialAgent`内にネストされます。
    * **通信:** サブエージェントは**共有セッションステート**の別々のキーに結果を書き込みます。後続の「ギャザー」エージェントは複数のステートキーを読み取ります。

=== "Python"

    ```python
    # 概念コード：並列情報収集
    from google.adk.agents import SequentialAgent, ParallelAgent, LlmAgent
    
    fetch_api1 = LlmAgent(name="API1Fetcher", instruction="API 1からデータを取得してください。", output_key="api1_data")
    fetch_api2 = LlmAgent(name="API2Fetcher", instruction="API 2からデータを取得してください。", output_key="api2_data")
    
    gather_concurrently = ParallelAgent(
        name="ConcurrentFetch",
        sub_agents=[fetch_api1, fetch_api2]
    )
    
    synthesizer = LlmAgent(
        name="Synthesizer",
        instruction="{api1_data}と{api2_data}からの結果を結合してください。"
    )
    
    overall_workflow = SequentialAgent(
        name="FetchAndSynthesize",
        sub_agents=[gather_concurrently, synthesizer] # 並列取得後、統合
    )
    # fetch_api1とfetch_api2が同時に実行され、ステートに保存されます。
    # synthesizerがその後実行され、state['api1_data']とstate['api2_data']を読み取ります。
    ```
=== "Java"

    ```java
    // 概念コード：並列情報収集
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.ParallelAgent;
    import com.google.adk.agents.SequentialAgent;

    LlmAgent fetchApi1 = LlmAgent.builder()
        .name("API1Fetcher")
        .instruction("API 1からデータを取得してください。")
        .outputKey("api1_data")
        .build();

    LlmAgent fetchApi2 = LlmAgent.builder()
        .name("API2Fetcher")
        .instruction("API 2からデータを取得してください。")
        .outputKey("api2_data")
        .build();

    ParallelAgent gatherConcurrently = ParallelAgent.builder()
        .name("ConcurrentFetcher")
        .subAgents(fetchApi2, fetchApi1)
        .build();

    LlmAgent synthesizer = LlmAgent.builder()
        .name("Synthesizer")
        .instruction("{api1_data}と{api2_data}からの結果を結合してください。")
        .build();

    SequentialAgent overallWorfklow = SequentialAgent.builder()
        .name("FetchAndSynthesize") // 並列取得後、統合
        .subAgents(gatherConcurrently, synthesizer)
        .build();

    // fetch_api1とfetch_api2が同時に実行され、ステートに保存されます。
    // synthesizerがその後実行され、state['api1_data']とstate['api2_data']を読み取ります。
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/parallelagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:parallel-gather-pattern"
    ```

### 階層的タスク分解

* **構造:** 上位レベルのエージェントが複雑な目標を分解し、サブタスクを下位レベルのエージェントに委任する、多層のエージェントツリー。
* **目的:** 複雑な問題を再帰的により単純で実行可能なステップに分解して解決します。
* **使用されるADKプリミティブ:**
    * **階層:** 多層の`parent_agent`/`sub_agents`構造。
    * **インタラクション:** 主に親エージェントがサブエージェントにタスクを割り当てるために使用する**LLM駆動の委任**または**明示的な呼び出し（`AgentTool`）**。結果は階層を上って返されます（ツール応答またはステート経由）。

=== "Python"

    ```python
    # 概念コード：階層的リサーチタスク
    from google.adk.agents import LlmAgent
    from google.adk.tools import agent_tool
    
    # 低レベルのツールのようなエージェント
    web_searcher = LlmAgent(name="WebSearch", description="事実のためのウェブ検索を実行します。")
    summarizer = LlmAgent(name="Summarizer", description="テキストを要約します。")
    
    # ツールを組み合わせる中レベルのエージェント
    research_assistant = LlmAgent(
        name="ResearchAssistant",
        model="gemini-2.0-flash",
        description="トピックに関する情報を見つけて要約します。",
        tools=[agent_tool.AgentTool(agent=web_searcher), agent_tool.AgentTool(agent=summarizer)]
    )
    
    # リサーチを委任する高レベルのエージェント
    report_writer = LlmAgent(
        name="ReportWriter",
        model="gemini-2.0-flash",
        instruction="トピックXに関するレポートを作成してください。ResearchAssistantを使用して情報を収集してください。",
        tools=[agent_tool.AgentTool(agent=research_assistant)]
        # あるいは、research_assistantがsub_agentであればLLM移譲を使用することも可能
    )
    # ユーザーはReportWriterと対話します。
    # ReportWriterはResearchAssistantツールを呼び出します。
    # ResearchAssistantはWebSearchとSummarizerツールを呼び出します。
    # 結果は上へと流れます。
    ```

=== "Java"

    ```java
    // 概念コード：階層的リサーチタスク
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;
    
    // 低レベルのツールのようなエージェント
    LlmAgent webSearcher = LlmAgent.builder()
        .name("WebSearch")
        .description("事実のためのウェブ検索を実行します。")
        .build();
    
    LlmAgent summarizer = LlmAgent.builder()
        .name("Summarizer")
        .description("テキストを要約します。")
        .build();
    
    // ツールを組み合わせる中レベルのエージェント
    LlmAgent researchAssistant = LlmAgent.builder()
        .name("ResearchAssistant")
        .model("gemini-2.0-flash")
        .description("トピックに関する情報を見つけて要約します。")
        .tools(AgentTool.create(webSearcher), AgentTool.create(summarizer))
        .build();
    
    // リサーチを委任する高レベルのエージェント
    LlmAgent reportWriter = LlmAgent.builder()
        .name("ReportWriter")
        .model("gemini-2.0-flash")
        .instruction("トピックXに関するレポートを作成してください。ResearchAssistantを使用して情報を収集してください。")
        .tools(AgentTool.create(researchAssistant))
        // あるいは、research_assistantがsubAgentであればLLM移譲を使用することも可能
        .build();
    
    // ユーザーはReportWriterと対話します。
    // ReportWriterはResearchAssistantツールを呼び出します。
    // ResearchAssistantはWebSearchとSummarizerツールを呼び出します。
    // 結果は上へと流れます。
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/tool"
        "google.golang.org/adk/tool/agenttool"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:hierarchical-pattern"
    ```

### レビュー/批評パターン（生成者-批評家）

* **構造:** 通常、[`SequentialAgent`](workflow-agents/sequential-agents.md)内に2つのエージェント（生成者と批評家/レビューア）を含みます。
* **目的:** 生成された出力の品質や妥当性を、専門のエージェントにレビューさせることで向上させます。
* **使用されるADKプリミティブ:**
    * **ワークフロー:** `SequentialAgent`が、レビューの前に生成が行われることを保証します。
    * **通信:** **共有セッションステート**（生成者は`output_key`を使用して出力を保存し、レビューアはそのステートキーを読み取る）。レビューアは後続のステップのためにフィードバックを別のステートキーに保存する場合があります。

=== "Python"

    ```python
    # 概念コード：生成者-批評家
    from google.adk.agents import SequentialAgent, LlmAgent
    
    generator = LlmAgent(
        name="DraftWriter",
        instruction="主題Xに関する短い段落を書いてください。",
        output_key="draft_text"
    )
    
    reviewer = LlmAgent(
        name="FactChecker",
        instruction="{draft_text}のテキストを事実の正確性についてレビューしてください。'valid'または'invalid'と理由を出力してください。",
        output_key="review_status"
    )
    
    # オプション：review_statusに基づくさらなるステップ
    
    review_pipeline = SequentialAgent(
        name="WriteAndReview",
        sub_agents=[generator, reviewer]
    )
    # generator実行 -> 下書きをstate['draft_text']に保存
    # reviewer実行 -> state['draft_text']を読み取り、ステータスをstate['review_status']に保存
    ```

=== "Java"

    ```java
    // 概念コード：生成者-批評家
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    
    LlmAgent generator = LlmAgent.builder()
        .name("DraftWriter")
        .instruction("主題Xに関する短い段落を書いてください。")
        .outputKey("draft_text")
        .build();
    
    LlmAgent reviewer = LlmAgent.builder()
        .name("FactChecker")
        .instruction("{draft_text}のテキストを事実の正確性についてレビューしてください。'valid'または'invalid'と理由を出力してください。")
        .outputKey("review_status")
        .build();
    
    // オプション：review_statusに基づくさらなるステップ
    
    SequentialAgent reviewPipeline = SequentialAgent.builder()
        .name("WriteAndReview")
        .subAgents(generator, reviewer)
        .build();
    
    // generator実行 -> 下書きをstate['draft_text']に保存
    // reviewer実行 -> state['draft_text']を読み取り、ステータスをstate['review_status']に保存
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:generator-critic-pattern"
    ```

### 反復的改善パターン

* **構造:** 複数のイテレーションにわたってタスクに取り組む1つ以上のエージェントを含む[`LoopAgent`](workflow-agents/loop-agents.md)を使用します。
* **目的:** 品質基準を満たすか、最大イテレーション回数に達するまで、セッションステートに保存された結果（コード、テキスト、計画など）を段階的に改善します。
* **使用されるADKプリミティブ:**
    * **ワークフロー:** `LoopAgent`が反復を管理します。
    * **通信:** エージェントが前のイテレーションの出力を読み取り、改善版を保存するために**共有セッションステート**が不可欠です。
    * **終了:** ループは通常、`max_iterations`に基づいて、または結果が満足のいくものである場合に専用のチェックエージェントが`Event Actions`で`escalate=True`を設定することによって終了します。

=== "Python"

    ```python
    # 概念コード：反復的なコード改善
    from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
    from google.adk.events import Event, EventActions
    from google.adk.agents.invocation_context import InvocationContext
    from typing import AsyncGenerator
    
    # state['current_code']とstate['requirements']に基づいてコードを生成/改善するエージェント
    code_refiner = LlmAgent(
        name="CodeRefiner",
        instruction="state['current_code']（存在する場合）とstate['requirements']を読み取ってください。要件を満たすようにPythonコードを生成/改善してください。state['current_code']に保存してください。",
        output_key="current_code" # ステート内の前のコードを上書き
    )
    
    # コードが品質基準を満たしているかチェックするエージェント
    quality_checker = LlmAgent(
        name="QualityChecker",
        instruction="state['current_code']のコードをstate['requirements']に対して評価してください。'pass'または'fail'を出力してください。",
        output_key="quality_status"
    )
    
    # ステータスをチェックし、'pass'の場合にエスカレートするカスタムエージェント
    class CheckStatusAndEscalate(BaseAgent):
        async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
            status = ctx.session.state.get("quality_status", "fail")
            should_stop = (status == "pass")
            yield Event(author=self.name, actions=EventActions(escalate=should_stop))
    
    refinement_loop = LoopAgent(
        name="CodeRefinementLoop",
        max_iterations=5,
        sub_agents=[code_refiner, quality_checker, CheckStatusAndEscalate(name="StopChecker")]
    )
    # ループ実行：Refiner -> Checker -> StopChecker
    # State['current_code']は各イテレーションで更新されます。
    # QualityCheckerが'pass'を出力する（StopCheckerがエスカレートする）か、5回のイテレーション後にループが停止します。
    ```

=== "Java"

    ```java
    // 概念コード：反復的なコード改善
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.LoopAgent;
    import com.google.adk.events.Event;
    import com.google.adk.events.EventActions;
    import com.google.adk.agents.InvocationContext;
    import io.reactivex.rxjava3.core.Flowable;
    import java.util.List;
    
    // state['current_code']とstate['requirements']に基づいてコードを生成/改善するエージェント
    LlmAgent codeRefiner = LlmAgent.builder()
        .name("CodeRefiner")
        .instruction("state['current_code']（存在する場合）とstate['requirements']を読み取ってください。要件を満たすようにJavaコードを生成/改善してください。state['current_code']に保存してください。")
        .outputKey("current_code") // ステート内の前のコードを上書き
        .build();
    
    // コードが品質基準を満たしているかチェックするエージェント
    LlmAgent qualityChecker = LlmAgent.builder()
        .name("QualityChecker")
        .instruction("state['current_code']のコードをstate['requirements']に対して評価してください。'pass'または'fail'を出力してください。")
        .outputKey("quality_status")
        .build();
    
    BaseAgent checkStatusAndEscalate = new BaseAgent(
        "StopChecker","quality_statusをチェックし、'pass'の場合にエスカレートします。", List.of(), null, null) {
    
      @Override
      protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
        String status = (String) invocationContext.session().state().getOrDefault("quality_status", "fail");
        boolean shouldStop = "pass".equals(status);
    
        EventActions actions = EventActions.builder().escalate(shouldStop).build();
        Event event = Event.builder()
            .author(this.name())
            .actions(actions)
            .build();
        return Flowable.just(event);
      }
    };
    
    LoopAgent refinementLoop = LoopAgent.builder()
        .name("CodeRefinementLoop")
        .maxIterations(5)
        .subAgents(codeRefiner, qualityChecker, checkStatusAndEscalate)
        .build();
    
    // ループ実行：Refiner -> Checker -> StopChecker
    // State['current_code']は各イテレーションで更新されます。
    // QualityCheckerが'pass'を出力する（StopCheckerがエスカレートする）か、5回のイテレーション後にループが停止します。
    ```

=== "Go"

    ```go
    import (
        "iter"
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/loopagent"
        "google.golang.org/adk/session"
    )

    --8<-- "examples/go/snippets/agents/multi-agent/main.go:iterative-refinement-pattern"
    ```

### ヒューマン・イン・ザ・ループパターン

* **構造:** エージェントのワークフロー内に人間の介入点を統合します。
* **目的:** 人間の監督、承認、修正、またはAIが実行できないタスクを可能にします。
* **使用されるADKプリミティブ（概念的）:**
    * **インタラクション:** 実行を一時停止し、外部システム（UI、チケットシステムなど）にリクエストを送信して人間の入力を待つカスタム**ツール**を使用して実装できます。ツールはその後、人間の応答をエージェントに返します。
    * **ワークフロー:** **LLM駆動の委任**（`transfer_to_agent`）を使用して、外部ワークフローをトリガーする概念的な「ヒューマンエージェント」をターゲットにするか、`LlmAgent`内でカスタムツールを使用することができます。
    * **ステート/コールバック:** ステートは人間のためのタスク詳細を保持でき、コールバックはインタラクションフローを管理できます。
    * **注:** ADKには組み込みの「ヒューマンエージェント」タイプがないため、カスタム統合が必要です。

=== "Python"

    ```python
    # 概念コード：人間の承認にツールを使用
    from google.adk.agents import LlmAgent, SequentialAgent
    from google.adk.tools import FunctionTool
    
    # --- external_approval_toolが存在すると仮定 ---
    # このツールは以下を行います：
    # 1. 詳細（request_id、金額、理由など）を受け取ります。
    # 2. これらの詳細を人間のレビューシステムに送信します（API経由など）。
    # 3. 人間の応答（承認/拒否）をポーリングまたは待ちます。
    # 4. 人間の決定を返します。
    # async def external_approval_tool(amount: float, reason: str) -> str: ...
    approval_tool = FunctionTool(func=external_approval_tool)
    
    # リクエストを準備するエージェント
    prepare_request = LlmAgent(
        name="PrepareApproval",
        instruction="ユーザー入力に基づいて承認リクエストの詳細を準備してください。金額と理由をステートに保存してください。",
        # ... おそらくstate['approval_amount']とstate['approval_reason']を設定します ...
    )
    
    # 人間の承認ツールを呼び出すエージェント
    request_approval = LlmAgent(
        name="RequestHumanApproval",
        instruction="state['approval_amount']からの金額とstate['approval_reason']からの理由でexternal_approval_toolを使用してください。",
        tools=[approval_tool],
        output_key="human_decision"
    )
    
    # 人間の決定に基づいて処理を進めるエージェント
    process_decision = LlmAgent(
        name="ProcessDecision",
        instruction="{human_decision}を確認してください。'approved'なら続行し、'rejected'ならユーザーに通知してください。"
    )
    
    approval_workflow = SequentialAgent(
        name="HumanApprovalWorkflow",
        sub_agents=[prepare_request, request_approval, process_decision]
    )
    ```

=== "Java"

    ```java
    // 概念コード：人間の承認にツールを使用
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.SequentialAgent;
    import com.google.adk.tools.FunctionTool;
    
    // --- external_approval_toolが存在すると仮定 ---
    // このツールは以下を行います：
    // 1. 詳細（request_id、金額、理由など）を受け取ります。
    // 2. これらの詳細を人間のレビューシステムに送信します（API経由など）。
    // 3. 人間の応答（承認/拒否）をポーリングまたは待ちます。
    // 4. 人間の決定を返します。
    // public boolean externalApprovalTool(float amount, String reason) { ... }
    FunctionTool approvalTool = FunctionTool.create(externalApprovalTool);
    
    // リクエストを準備するエージェント
    LlmAgent prepareRequest = LlmAgent.builder()
        .name("PrepareApproval")
        .instruction("ユーザー入力に基づいて承認リクエストの詳細を準備してください。金額と理由をステートに保存してください。")
        // ... おそらくstate['approval_amount']とstate['approval_reason']を設定します ...
        .build();
    
    // 人間の承認ツールを呼び出すエージェント
    LlmAgent requestApproval = LlmAgent.builder()
        .name("RequestHumanApproval")
        .instruction("state['approval_amount']からの金額とstate['approval_reason']からの理由でexternal_approval_toolを使用してください。")
        .tools(approvalTool)
        .outputKey("human_decision")
        .build();
    
    // 人間の決定に基づいて処理を進めるエージェント
    LlmAgent processDecision = LlmAgent.builder()
        .name("ProcessDecision")
        .instruction("{human_decision}を確認してください。'approved'なら続行し、'rejected'ならユーザーに通知してください。")
        .build();
    
    SequentialAgent approvalWorkflow = SequentialAgent.builder()
        .name("HumanApprovalWorkflow")
        .subAgents(prepareRequest, requestApproval, processDecision)
        .build();
    ```

=== "Go"

    ```go
    import (
        "google.golang.org/adk/agent"
        "google.golang.org/adk/agent/llmagent"
        "google.golang.org/adk/agent/workflowagents/sequentialagent"
        "google.golang.org/adk/tool"
    )
    
    --8<-- "examples/go/snippets/agents/multi-agent/main.go:human-in-loop-pattern"
    ```

これらのパターンは、マルチエージェントシステムを構築するための出発点を提供します。特定のアプリケーションに最も効果的なアーキテクチャを作成するために、必要に応じてこれらを組み合わせることができます。