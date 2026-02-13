# コンテキスト

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Agent Development Kit (ADK) において、「コンテキスト」とは、エージェントとそのツールが特定の操作中に利用できる重要な情報の集合体を指します。現在のタスクや会話のターンを効果的に処理するために必要な背景知識やリソースだと考えてください。

エージェントがうまく機能するためには、多くの場合、最新のユーザーメッセージ以上の情報が必要です。コンテキストは以下を可能にするため、不可欠です。

1.  **状態の維持：** 会話の複数のステップにわたる詳細（例：ユーザーの好み、以前の計算結果、ショッピングカートのアイテム）を記憶します。これは主に**セッション状態（session state）**を通じて管理されます。
2.  **データの受け渡し：** あるステップ（LLMの呼び出しやツールの実行など）で発見または生成された情報を、後続のステップと共有します。ここでもセッション状態が鍵となります。
3.  **サービスへのアクセス：** 以下のようなフレームワークの機能と対話します。
    *   **アーティファクトストレージ：** セッションに関連付けられたファイルやデータのかたまり（PDF、画像、設定ファイルなど）を保存または読み込みます。
    *   **メモリ：** ユーザーに関連する過去の対話や外部の知識ソースから関連情報を検索します。
    *   **認証：** ツールが外部APIに安全にアクセスするために必要な認証情報を要求および取得します。
4.  **IDと追跡：** 現在どのエージェントが実行されているか（`agent.name`）を把握し、ロギングとデバッグのために現在のリクエスト-レスポンスサイクル（`invocation_id`）を一意に識別します。
5.  **ツール固有のアクション：** 現在の対話の詳細へのアクセスを必要とする、認証要求やメモリ検索など、ツール内での特化した操作を有効にします。

単一の完全なユーザーリクエストから最終レスポンスまでのサイクル（**呼び出し (invocation)**）に関するこれらすべての情報をまとめる中心的な要素が`InvocationContext`です。しかし、通常、このオブジェクトを直接作成したり管理したりすることはありません。ADKフレームワークは、呼び出しが開始されるとき（例：`runner.run_async`経由で）にこれを作成し、関連するコンテキスト情報をエージェントコード、コールバック、ツールに暗黙的に渡します。

=== "Python"

    ```python
    # 概念的な疑似コード：フレームワークがコンテキストを提供する方法（内部ロジック）
    
    # runner = Runner(agent=my_root_agent, session_service=..., artifact_service=...)
    # user_message = types.Content(...)
    # session = session_service.get_session(...) # または新規作成
    
    # --- runner.run_async(...) の内部 ---
    # 1. フレームワークがこの特定の実行のためのメインコンテキストを作成します
    # invocation_context = InvocationContext(
    #     invocation_id="this-run-のための一意なID",
    #     session=session,
    #     user_content=user_message,
    #     agent=my_root_agent, # 開始エージェント
    #     session_service=session_service,
    #     artifact_service=artifact_service,
    #     memory_service=memory_service,
    #     # ... その他必要なフィールド ...
    # )
    #
    # 2. フレームワークがエージェントのrunメソッドを呼び出し、コンテキストを暗黙的に渡します
    #    （エージェントのメソッドシグネチャがこれを受け取ります。例：runAsyncImpl(InvocationContext invocationContext)）
    # await my_root_agent.run_async(invocation_context)
    #   --- 内部ロジックの終わり ---
    #
    # 開発者として、あなたはメソッドの引数で提供されるコンテキストオブジェクトを扱います。
    ```

=== "Go"

    ```go
    /* 概念的な疑似コード：フレームワークがコンテキストを提供する方法（内部ロジック） */
    --8<-- "examples/go/snippets/context/main.go:conceptual_runner_example"
    ```

=== "Java"

    ```java
    /* 概念的な疑似コード：フレームワークがコンテキストを提供する方法（内部ロジック） */
    InMemoryRunner runner = new InMemoryRunner(agent);
    Session session = runner
        .sessionService()
        .createSession(runner.appName(), USER_ID, initialState, SESSION_ID )
        .blockingGet();

    try (Scanner scanner = new Scanner(System.in, StandardCharsets.UTF_8)) {
      while (true) {
        System.out.print("\nYou > ");
      }
      String userInput = scanner.nextLine();
      if ("quit".equalsIgnoreCase(userInput)) {
        break;
      }
      Content userMsg = Content.fromParts(Part.fromText(userInput));
      Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg);
      System.out.print("\nAgent > ");
      events.blockingForEach(event -> System.out.print(event.stringifyContent()));
    }
    ```

## 様々な種類のコンテキスト

`InvocationContext`が包括的な内部コンテナとして機能する一方で、ADKは特定の状況に合わせた特化したコンテキストオブジェクトを提供します。これにより、あらゆる場所で内部コンテキストの完全な複雑さを扱う必要なく、目の前のタスクに適したツールと権限を持つことができます。以下に、遭遇するであろう様々な「種類」を示します。

1.  **`InvocationContext`**
    *   **使用場所：** エージェントのコア実装メソッド（`_run_async_impl`、`_run_live_impl`）内で`ctx`引数として直接受け取ります。
    *   **目的：** 現在の呼び出しの*全体*の状態へのアクセスを提供します。これは最も包括的なコンテキストオブジェクトです。
    *   **主な内容：** `session`（`state`と`events`を含む）、現在の`agent`インスタンス、`invocation_id`、初期の`user_content`、設定されたサービス（`artifact_service`、`memory_service`、`session_service`）への参照、およびライブ/ストリーミングモードに関連するフィールドへの直接アクセス。
    *   **ユースケース：** 主にエージェントのコアロジックがセッション全体やサービスに直接アクセスする必要がある場合に使用されますが、状態やアーティファクトの操作は、独自のコンテキストを使用するコールバック/ツールに委譲されることが多いです。また、呼び出し自体を制御するためにも使用されます（例：`ctx.end_invocation = True`の設定）。

    === "Python"
    
        ```python
        # 疑似コード：InvocationContextを受け取るエージェントの実装
        from google.adk.agents import BaseAgent
        from google.adk.agents.invocation_context import InvocationContext
        from google.adk.events import Event
        from typing import AsyncGenerator
    
        class MyAgent(BaseAgent):
            async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
                # 直接アクセスの例
                agent_name = ctx.agent.name
                session_id = ctx.session.id
                print(f"エージェント {agent_name} がセッション {session_id} で呼び出し {ctx.invocation_id} のために実行中")
                # ... ctxを使用するエージェントのロジック ...
                yield # ... イベント ...
        ```
    
    === "Go"

        ```go
        import (
        	"google.golang.org/adk/agent"
        	"google.golang.org/adk/session"
        )
        
        --8<-- "examples/go/snippets/context/main.go:invocation_context_agent"
        ```

    === "Java"
    
        ```java
        // 疑似コード：InvocationContextを受け取るエージェントの実装
        import com.google.adk.agents.BaseAgent;
        import com.google.adk.agents.InvocationContext;
        
            LlmAgent root_agent =
                LlmAgent.builder()
                    .model("gemini-***")
                    .name("sample_agent")
                    .description("ユーザーの質問に答えます。")
                    .instruction(
                        """
                        ここにエージェントへの指示を入力してください。
                        """
                    )
                    .tools(sampleTool)
                    .outputKey("YOUR_KEY")
                    .build();
    
            ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>();
            initialState.put("YOUR_KEY", "");
          
            InMemoryRunner runner = new InMemoryRunner(agent);
            Session session =
                  runner
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
                  Flowable<Event> events = 
                          runner.runAsync(session.userId(), session.id(), userMsg);
        
                  System.out.print("\nAgent > ");
                  events.blockingForEach(event -> 
                          System.out.print(event.stringifyContent()));
              }
        
            protected Flowable<Event> runAsyncImpl(InvocationContext invocationContext) {
                // 直接アクセスの例
                String agentName = invocationContext.agent.name
                String sessionId = invocationContext.session.id
                String invocationId = invocationContext.invocationId
                System.out.println("エージェント " + agent_name + " がセッション " + session_id + " で呼び出し " + invocationId + " のために実行中")
                // ... ctxを使用するエージェントのロジック ...
            }
        ```

2.  **`ReadonlyContext`**
    *   **使用場所：** 基本情報への読み取りアクセスのみが必要で、変更が許可されていないシナリオ（例：`InstructionProvider`関数）で提供されます。他のコンテキストのベースクラスでもあります。
    *   **目的：** 基本的なコンテキスト詳細の安全な読み取り専用ビューを提供します。
    *   **主な内容：** `invocation_id`、`agent_name`、および現在の`state`の読み取り専用*ビュー*。

    === "Python"
    
        ```python
        # 疑似コード：ReadonlyContextを受け取るInstruction provider
        from google.adk.agents.readonly_context import ReadonlyContext
    
        def my_instruction_provider(context: ReadonlyContext) -> str:
            # 読み取り専用アクセスの例
            user_tier = context.state().get("user_tier", "standard") # 状態の読み取りが可能
            # context.state['new_key'] = 'value' # これは通常エラーを引き起こすか、効果がない
            return f"{user_tier} ユーザーのリクエストを処理してください。"
        ```

    === "Go"

        ```go
        import "google.golang.org/adk/agent"
        
        --8<-- "examples/go/snippets/context/main.go:readonly_context_instruction"
        ```

    === "Java"
    
        ```java
        // 疑似コード：ReadonlyContextを受け取るInstruction provider
        import com.google.adk.agents.ReadonlyContext;
    
        public String myInstructionProvider(ReadonlyContext context){
            // 読み取り専用アクセスの例
            String userTier = context.state().get("user_tier", "standard");
            context.state().put('new_key', 'value'); //これは通常エラーを引き起こします
            return userTier + " ユーザーのリクエストを処理してください。";
        }
        ```
    
3.  **`CallbackContext`**
    *   **使用場所：** エージェントのライフサイクルコールバック（`before_agent_callback`、`after_agent_callback`）およびモデルインタラクションコールバック（`before_model_callback`、`after_model_callback`）に`callback_context`として渡されます。
    *   **目的：** *特にコールバック内で*、状態の検査と変更、アーティファクトとの対話、および呼び出し詳細へのアクセスを容易にします。
    *   **主な機能（`ReadonlyContext`に追加）：**
        *   **変更可能な`state`プロパティ：** セッション状態の読み取り*と書き込み*を許可します。ここで行われた変更（`callback_context.state['key'] = value`）は追跡され、コールバック後にフレームワークによって生成されるイベントに関連付けられます。
        *   **アーティファクトメソッド：** 設定された`artifact_service`と対話するための`load_artifact(filename)`および`save_artifact(filename, part)`メソッド。
        *   直接の`user_content`アクセス。

    === "Python"
    
        ```python
        # 疑似コード：CallbackContextを受け取るコールバック
        from google.adk.agents.callback_context import CallbackContext
        from google.adk.models import LlmRequest
        from google.genai import types
        from typing import Optional
    
        def my_before_model_cb(callback_context: CallbackContext, request: LlmRequest) -> Optional[types.Content]:
            # 状態の読み書きの例
            call_count = callback_context.state.get("model_calls", 0)
            callback_context.state["model_calls"] = call_count + 1 # 状態を変更
    
            # オプションでアーティファクトをロード
            # config_part = callback_context.load_artifact("model_config.json")
            print(f"呼び出し {callback_context.invocation_id} のためのモデルコール #{call_count + 1} を準備中")
            return None # モデルコールの続行を許可
        ```
    
    === "Go"

        ```go
        import (
        	"google.golang.org/adk/agent"
        	"google.golang.org/adk/model"
        )
        
        --8<-- "examples/go/snippets/context/main.go:callback_context_callback"
        ```

    === "Java"
    
        ```java
        // 疑似コード：CallbackContextを受け取るコールバック
        import com.google.adk.agents.CallbackContext;
        import com.google.adk.models.LlmRequest;
        import com.google.genai.types.Content;
        import java.util.Optional;
    
        public Maybe<LlmResponse> myBeforeModelCb(CallbackContext callbackContext, LlmRequest request){
            // 状態の読み書きの例
            callCount = callbackContext.state().get("model_calls", 0)
            callbackContext.state().put("model_calls") = callCount + 1 # 状態を変更
    
            // オプションでアーティファクトをロード
            // Maybe<Part> configPart = callbackContext.loadArtifact("model_config.json");
            System.out.println("モデルコール " + callCount + 1 + " を準備中");
            return Maybe.empty(); // モデルコールの続行を許可
        }
        ```

4.  **`ToolContext`**
    *   **使用場所：** `FunctionTool`を支える関数や、ツールの実行コールバック（`before_tool_callback`、`after_tool_callback`）に`tool_context`として渡されます。
    *   **目的：** `CallbackContext`が提供するすべてに加えて、認証の処理、メモリの検索、アーティファクトの一覧表示など、ツールの実行に不可欠な特化したメソッドを提供します。
    *   **主な機能（`CallbackContext`に追加）：**
        *   **認証メソッド：** 認証フローをトリガーする`request_credential(auth_config)`と、ユーザー/システムによって提供された認証情報を取得する`get_auth_response(auth_config)`。
        *   **アーティファクトの一覧表示：** セッションで利用可能なアーティファクトを発見する`list_artifacts()`。
        *   **メモリ検索：** 設定された`memory_service`にクエリを実行する`search_memory(query)`。
        *   **`function_call_id`プロパティ：** このツールの実行をトリガーしたLLMからの特定の関数呼び出しを識別し、認証要求や応答を正しくリンクするために重要です。
        *   **`actions`プロパティ：** このステップの`EventActions`オブジェクトに直接アクセスし、ツールが状態の変更、認証要求などを通知できるようにします。

    === "Python"
    
        ```python
        # 疑似コード：ToolContextを受け取るツール関数
        from google.adk.tools import ToolContext
        from typing import Dict, Any
    
        # この関数がFunctionToolによってラップされていると仮定
        def search_external_api(query: str, tool_context: ToolContext) -> Dict[str, Any]:
            api_key = tool_context.state.get("api_key")
            if not api_key:
                # 必要な認証設定を定義
                # auth_config = AuthConfig(...)
                # tool_context.request_credential(auth_config) # 認証情報を要求
                # 'actions'プロパティを使用して認証要求が行われたことを通知
                # tool_context.actions.requested_auth_configs[tool_context.function_call_id] = auth_config
                return {"status": "認証が必要です"}
    
            # APIキーを使用...
            print(f"APIキーを使用してクエリ '{query}' のためのツールを実行中。呼び出し: {tool_context.invocation_id}")
    
            # オプションでメモリを検索したり、アーティファクトを一覧表示したりする
            # relevant_docs = tool_context.search_memory(f"{query}に関する情報")
            # available_files = tool_context.list_artifacts()
    
            return {"result": f"{query}のデータを取得しました。"}
        ```
    
    === "Go"

        ```go
        import "google.golang.org/adk/tool"
        
        --8<-- "examples/go/snippets/context/main.go:tool_context_tool"
        ```

    === "Java"
    
        ```java
        // 疑似コード：ToolContextを受け取るツール関数
        import com.google.adk.tools.ToolContext;
        import java.util.HashMap;
        import java.util.Map;
    
        // この関数がFunctionToolによってラップされていると仮定
        public Map<String, Object> searchExternalApi(String query, ToolContext toolContext){
            String apiKey = toolContext.state.get("api_key");
            if(apiKey.isEmpty()){
                // 必要な認証設定を定義
                // authConfig = AuthConfig(...);
                // toolContext.requestCredential(authConfig); # 認証情報を要求
                // 'actions'プロパティを使用して認証要求が行われたことを通知
                ...
                return Map.of("status", "認証が必要です");
    
            // APIキーを使用...
            System.out.println("APIキーを使用してクエリ " + query + " のためのツールを実行中。");
    
            // オプションでアーティファクトを一覧表示
            // Single<List<String>> availableFiles = toolContext.listArtifacts();
    
            return Map.of("result", query + " のデータを取得しました");
        }
        ```

これらの異なるコンテキストオブジェクトと、それらをいつ使用するかを理解することは、ADKアプリケーションの状態を効果的に管理し、サービスにアクセスし、フローを制御するための鍵となります。次のセクションでは、これらのコンテキストを使用して実行できる一般的なタスクについて詳しく説明します。

## コンテキストを使用した一般的なタスク

様々なコンテキストオブジェクトについて理解したところで、エージェントやツールを構築する際に、それらを使って一般的なタスクを実行する方法に焦点を当てましょう。

### 情報へのアクセス

コンテキスト内に保存された情報を読み取る必要が頻繁にあります。

*   **セッション状態の読み取り：** 以前のステップで保存されたデータや、ユーザー/アプリレベルの設定にアクセスします。`state`プロパティに対して辞書のようにアクセスします。

    === "Python"
    
        ```python
        # 疑似コード：ツール関数内
        from google.adk.tools import ToolContext
    
        def my_tool(tool_context: ToolContext, **kwargs):
            user_pref = tool_context.state.get("user_display_preference", "default_mode")
            api_endpoint = tool_context.state.get("app:api_endpoint") # アプリレベルの状態を読み取り
    
            if user_pref == "dark_mode":
                # ... ダークモードのロジックを適用 ...
                pass
            print(f"使用中のAPIエンドポイント: {api_endpoint}")
            # ... 残りのツールのロジック ...
    
        # 疑似コード：コールバック関数内
        from google.adk.agents.callback_context import CallbackContext
    
        def my_callback(callback_context: CallbackContext, **kwargs):
            last_tool_result = callback_context.state.get("temp:last_api_result") # 一時的な状態を読み取り
            if last_tool_result:
                print(f"最後のツールからの一時的な結果が見つかりました: {last_tool_result}")
            # ... コールバックのロジック ...
        ```
    
    === "Go"

        ```go
        import (
        	"google.golang.org/adk/agent"
        	"google.golang.org/adk/session"
            "google.golang.org/adk/tool"
        	"google.golang.org/genai"
        )
        
        --8<-- "examples/go/snippets/context/main.go:accessing_state_tool"

        --8<-- "examples/go/snippets/context/main.go:accessing_state_callback"
        ```

    === "Java"
    
        ```java
        // 疑似コード：ツール関数内
        import com.google.adk.tools.ToolContext;
    
        public void myTool(ToolContext toolContext){
           String userPref = toolContext.state().get("user_display_preference");
           String apiEndpoint = toolContext.state().get("app:api_endpoint"); // アプリレベルの状態を読み取り
           if(userPref.equals("dark_mode")){
                // ... ダークモードのロジックを適用 ...
                pass
            }
           System.out.println("使用中のAPIエンドポイント: " + api_endpoint);
           // ... 残りのツールのロジック ...
        }
    
    
        // 疑似コード：コールバック関数内
        import com.google.adk.agents.CallbackContext;
    
            public void myCallback(CallbackContext callbackContext){
                String lastToolResult = (String) callbackContext.state().get("temp:last_api_result"); // 一時的な状態を読み取り
            }
            if(!(lastToolResult.isEmpty())){
                System.out.println("最後のツールからの一時的な結果が見つかりました: " + lastToolResult);
            }
            // ... コールバックのロジック ...
        ```

*   **現在の識別子の取得：** ロギングや、現在の操作に基づいたカスタムロジックに便利です。

    === "Python"
    
        ```python
        # 疑似コード：任意のコンテキスト内（ToolContextの例）
        from google.adk.tools import ToolContext
    
        def log_tool_usage(tool_context: ToolContext, **kwargs):
            agent_name = tool_context.agent_name
            inv_id = tool_context.invocation_id
            func_call_id = getattr(tool_context, 'function_call_id', 'N/A') # ToolContextに固有
    
            print(f"ログ: 呼び出し={inv_id}, エージェント={agent_name}, 関数呼び出しID={func_call_id} - ツールが実行されました。")
        ```
    
    === "Go"

        ```go
        import "google.golang.org/adk/tool"
        
        --8<-- "examples/go/snippets/context/main.go:accessing_ids"
        ```

    === "Java"
    
        ```java
        // 疑似コード：任意のコンテキスト内（ToolContextの例）
         import com.google.adk.tools.ToolContext;
    
         public void logToolUsage(ToolContext toolContext){
                    String agentName = toolContext.agentName;
                    String invId = toolContext.invocationId;
                    String functionCallId = toolContext.functionCallId().get(); // ToolContextに固有
                    System.out.println("ログ: 呼び出し= " + invId + " エージェント= " + agentName);
                }
        ```

*   **最初のユーザー入力へのアクセス：** 現在の呼び出しを開始したメッセージを再参照します。

    === "Python"
    
        ```python
        # 疑似コード：コールバック内
        from google.adk.agents.callback_context import CallbackContext
    
        def check_initial_intent(callback_context: CallbackContext, **kwargs):
            initial_text = "N/A"
            if callback_context.user_content and callback_context.user_content.parts:
                initial_text = callback_context.user_content.parts[0].text or "テキスト以外の入力"
    
            print(f"この呼び出しはユーザー入力で始まりました: '{initial_text}'")
    
        # 疑似コード：エージェントの_run_async_impl内
        # async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        #     if ctx.user_content and ctx.user_content.parts:
        #         initial_text = ctx.user_content.parts[0].text
        #         print(f"最初のクエリを記憶しているエージェントのロジック: {initial_text}")
        #     ...
        ```
    
    === "Go"

        ```go
        import (
        	"google.golang.org/adk/agent"
        	"google.golang.org/genai"
        )
        
        --8<-- "examples/go/snippets/context/main.go:accessing_initial_user_input"
        ```

    === "Java"
    
        ```java
        // 疑似コード：コールバック内
        import com.google.adk.agents.CallbackContext;
    
        public void checkInitialIntent(CallbackContext callbackContext){
            String initialText = "N/A";
            if((!(callbackContext.userContent().isEmpty())) && (!(callbackContext.userContent().parts.isEmpty()))){
                initialText = cbx.userContent().get().parts().get().get(0).text().get();
                ...
                System.out.println("この呼び出しはユーザー入力で始まりました: " + initialText)
            }
        }
        ```
    
### 状態管理

状態は、メモリとデータフローにとって非常に重要です。`CallbackContext`や`ToolContext`を使って状態を変更すると、その変更はフレームワークによって自動的に追跡され、永続化されます。

*   **仕組み：** `callback_context.state['my_key'] = my_value` や `tool_context.state['my_key'] = my_value` に書き込むと、この変更が現在のステップのイベントに関連付けられた`EventActions.state_delta`に追加されます。そして、`SessionService`がイベントを永続化する際にこれらのデルタを適用します。

*  **ツール間でのデータ受け渡し**

    === "Python"

        ```python
        # 疑似コード：ツール1 - ユーザーIDを取得
        from google.adk.tools import ToolContext
        import uuid
    
        def get_user_profile(tool_context: ToolContext) -> dict:
            user_id = str(uuid.uuid4()) # ID取得をシミュレート
            # 次のツールのためにIDを状態に保存
            tool_context.state["temp:current_user_id"] = user_id
            return {"profile_status": "IDが生成されました"}
    
        # 疑似コード：ツール2 - 状態からユーザーIDを使用
        def get_user_orders(tool_context: ToolContext) -> dict:
            user_id = tool_context.state.get("temp:current_user_id")
            if not user_id:
                return {"error": "状態にユーザーIDが見つかりません"}
    
            print(f"ユーザーIDの注文を取得中: {user_id}")
            # ... user_idを使って注文を取得するロジック ...
            return {"orders": ["order123", "order456"]}
        ```

    === "Go"

        ```go
        import "google.golang.org/adk/tool"
        
        --8<-- "examples/go/snippets/context/main.go:passing_data_tool1"
        
        --8<-- "examples/go/snippets/context/main.go:passing_data_tool2"
        ```

    === "Java"

        ```java
        // 疑似コード：ツール1 - ユーザーIDを取得
        import com.google.adk.tools.ToolContext;
        import java.util.UUID;
    
        public Map<String, String> getUserProfile(ToolContext toolContext){
            String userId = UUID.randomUUID().toString();
            // 次のツールのためにIDを状態に保存
            tool_context.state().put("temp:current_user_id", user_id);
            return Map.of("profile_status", "IDが生成されました");
        }
    
        // 疑似コード：ツール2 - 状態からユーザーIDを使用
        public  Map<String, String> getUserOrders(ToolContext toolContext){
            String userId = toolContext.state().get("temp:current_user_id");
            if(userId.isEmpty()){
                return Map.of("error", "状態にユーザーIDが見つかりません");
            }
            System.out.println("ユーザーIDの注文を取得中: " + userId);
             // ... user_idを使って注文を取得するロジック ...
            return Map.of("orders", "order123");
        }
        ```

*   **ユーザー設定の更新：**

    === "Python"
    
        ```python
        # 疑似コード：ツールまたはコールバックが設定を識別
        from google.adk.tools import ToolContext # または CallbackContext
    
        def set_user_preference(tool_context: ToolContext, preference: str, value: str) -> dict:
            # 永続的なSessionServiceを使用する場合、ユーザーレベルの状態には 'user:' プレフィックスを使用
            state_key = f"user:{preference}"
            tool_context.state[state_key] = value
            print(f"ユーザー設定 '{preference}' を '{value}' に設定しました")
            return {"status": "設定が更新されました"}
        ```
    
    === "Go"

        ```go
        import "google.golang.org/adk/tool"
        
        --8<-- "examples/go/snippets/context/main.go:updating_preferences"
        ```

    === "Java"
    
        ```java
        // 疑似コード：ツールまたはコールバックが設定を識別
        import com.google.adk.tools.ToolContext; // または CallbackContext
    
        public Map<String, String> setUserPreference(ToolContext toolContext, String preference, String value){
            // 永続的なSessionServiceを使用する場合、ユーザーレベルの状態には 'user:' プレフィックスを使用
            String stateKey = "user:" + preference;
            toolContext.state().put(stateKey, value);
            System.out.println("ユーザー設定 '" + preference + "' を '" + value + "' に設定しました");
            return Map.of("status", "設定が更新されました");
        }
        ```

*   **状態のプレフィックス：** 基本的な状態はセッション固有ですが、`app:`や`user:`のようなプレフィックスは、永続的な`SessionService`実装（`DatabaseSessionService`や`VertexAiSessionService`など）と共に使用して、より広いスコープ（アプリ全体またはセッションをまたいだユーザー全体）を示すことができます。`temp:`は、現在の呼び出し内でのみ関連するデータを示すために使用できます。

### アーティファクトの操作

セッションに関連付けられたファイルや大きなデータのかたまりを扱うには、アーティファクトを使用します。一般的なユースケース：アップロードされたドキュメントの処理。

*   **ドキュメント要約器のフロー例：**

    1.  **参照の取り込み（例：セットアップツールやコールバック内）：** ドキュメントのコンテンツ全体ではなく、*パスやURI*をアーティファクトとして保存します。

        === "Python"
    
               ```python
               # 疑似コード：コールバックまたは初期ツール内
               from google.adk.agents.callback_context import CallbackContext # または ToolContext
               from google.genai import types
                
               def save_document_reference(context: CallbackContext, file_path: str) -> None:
                   # file_pathが "gs://my-bucket/docs/report.pdf" や "/local/path/to/report.pdf" のようなものであると仮定
                   try:
                       # パス/URIテキストを含むPartを作成
                       artifact_part = types.Part(text=file_path)
                       version = context.save_artifact("document_to_summarize.txt", artifact_part)
                       print(f"ドキュメント参照 '{file_path}' をアーティファクトバージョン {version} として保存しました")
                       # 他のツールで必要な場合はファイル名を状態に保存
                       context.state["temp:doc_artifact_name"] = "document_to_summarize.txt"
                   except ValueError as e:
                       print(f"アーティファクトの保存エラー: {e}") # 例：アーティファクトサービスが設定されていない
                   except Exception as e:
                       print(f"アーティファクト参照の保存中に予期せぬエラーが発生しました: {e}")
                
               # 使用例：
               # save_document_reference(callback_context, "gs://my-bucket/docs/report.pdf")
               ```
    
        === "Go"

            ```go
            import (
            	"google.golang.org/adk/tool"
            	"google.golang.org/genai"
            )
            
            --8<-- "examples/go/snippets/context/main.go:artifacts_save_ref"
            ```

        === "Java"
    
               ```java
               // 疑似コード：コールバックまたは初期ツール内
               import com.google.adk.agents.CallbackContext;
               import com.google.genai.types.Content;
               import com.google.genai.types.Part;
                
                
               pubic void saveDocumentReference(CallbackContext context, String filePath){
                   // file_pathが "gs://my-bucket/docs/report.pdf" や "/local/path/to/report.pdf" のようなものであると仮定
                   try{
                       // パス/URIテキストを含むPartを作成
                       Part artifactPart = types.Part(filePath)
                       Optional<Integer> version = context.saveArtifact("document_to_summarize.txt", artifactPart)
                       System.out.println("ドキュメント参照 " + filePath + " をアーティファクトバージョン " + version + " として保存しました");
                       // 他のツールで必要な場合はファイル名を状態に保存
                       context.state().put("temp:doc_artifact_name", "document_to_summarize.txt");
                   } catch(Exception e){
                       System.out.println("アーティファクト参照の保存中に予期せぬエラーが発生しました: " + e);
                   }
               }
                    
               // 使用例：
               // saveDocumentReference(context, "gs://my-bucket/docs/report.pdf")
               ```

    2.  **要約ツール：** アーティファクトをロードしてパス/URIを取得し、適切なライブラリを使用して実際のドキュメントコンテンツを読み取り、要約して結果を返します。

        === "Python"

            ```python
            # 疑似コード：要約ツールの関数内
            from google.adk.tools import ToolContext
            from google.genai import types
            # google.cloud.storage や組み込みの open のようなライブラリが利用可能であると仮定
            # 'summarize_text' 関数が存在すると仮定
            # from my_summarizer_lib import summarize_text

            def summarize_document_tool(tool_context: ToolContext) -> dict:
                artifact_name = tool_context.state.get("temp:doc_artifact_name")
                if not artifact_name:
                    return {"error": "状態にドキュメントのアーティファクト名が見つかりません。"}

                try:
                    # 1. パス/URIを含むアーティファクトパートをロード
                    artifact_part = tool_context.load_artifact(artifact_name)
                    if not artifact_part or not artifact_part.text:
                        return {"error": f"アーティファクトをロードできないか、アーティファクトにテキストパスがありません: {artifact_name}"}

                    file_path = artifact_part.text
                    print(f"ロードされたドキュメント参照: {file_path}")

                    # 2. 実際のドキュメントコンテンツを読み取る（ADKコンテキスト外）
                    document_content = ""
                    if file_path.startswith("gs://"):
                        # 例：GCSクライアントライブラリを使用してダウンロード/読み取り
                        # from google.cloud import storage
                        # client = storage.Client()
                        # blob = storage.Blob.from_string(file_path, client=client)
                        # document_content = blob.download_as_text() # またはフォーマットに応じてバイト
                        pass # 実際のGCS読み取りロジックに置き換える
                    elif file_path.startswith("/"):
                         # 例：ローカルファイルシステムを使用
                         with open(file_path, 'r', encoding='utf-8') as f:
                             document_content = f.read()
                    else:
                        return {"error": f"サポートされていないファイルパススキーム: {file_path}"}

                    # 3. コンテンツを要約
                    if not document_content:
                         return {"error": "ドキュメントコンテンツの読み取りに失敗しました。"}

                    # summary = summarize_text(document_content) # 要約ロジックを呼び出す
                    summary = f"{file_path}からのコンテンツの要約" # プレースホルダー

                    return {"summary": summary}

                except ValueError as e:
                     return {"error": f"アーティファクトサービスのエラー: {e}"}
                except FileNotFoundError:
                     return {"error": f"ローカルファイルが見つかりません: {file_path}"}
                # except Exception as e: # GCSなどの特定の例外をキャッチ
                #      return {"error": f"ドキュメント {file_path} の読み取りエラー: {e}"}
            ```

        === "Go"

            ```go
            import "google.golang.org/adk/tool"
            
            --8<-- "examples/go/snippets/context/main.go:artifacts_summarize"
            ```

        === "Java"

            ```java
            // 疑似コード：要約ツールの関数内
            import com.google.adk.tools.ToolContext;
            import com.google.genai.types.Content;
            import com.google.genai.types.Part;

            public Map<String, String> summarizeDocumentTool(ToolContext toolContext){
                String artifactName = toolContext.state().get("temp:doc_artifact_name");
                if(artifactName.isEmpty()){
                    return Map.of("error", "状態にドキュメントのアーティファクト名が見つかりません。");
                }
                try{
                    // 1. パス/URIを含むアーティファクトパートをロード
                    Maybe<Part> artifactPart = toolContext.loadArtifact(artifactName);
                    if((artifactPart == null) || (artifactPart.text().isEmpty())){
                        return Map.of("error", "アーティファクトをロードできないか、アーティファクトにテキストパスがありません: " + artifactName);
                    }
                    filePath = artifactPart.text();
                    System.out.println("ロードされたドキュメント参照: " + filePath);

                    // 2. 実際のドキュメントコンテンツを読み取る（ADKコンテキスト外）
                    String documentContent = "";
                    if(filePath.startsWith("gs://")){
                        // 例：GCSクライアントライブラリを使用してdocumentContentにダウンロード/読み取り
                        pass; // 実際のGCS読み取りロジックに置き換える
                    } else if(){
                        // 例：ローカルファイルシステムを使用してdocumentContentにダウンロード/読み取り
                    } else{
                        return Map.of("error", "サポートされていないファイルパススキーム: " + filePath); 
                    }

                    // 3. コンテンツを要約
                    if(documentContent.isEmpty()){
                        return Map.of("error", "ドキュメントコンテンツの読み取りに失敗しました。"); 
                    }

                    // summary = summarizeText(documentContent) // 要約ロジックを呼び出す
                    summary = filePath + "からのコンテンツの要約"; // プレースホルダー

                    return Map.of("summary", summary);
                } catch(IllegalArgumentException e){
                    return Map.of("error", "アーティファクトサービスのエラー " + filePath + e);
                } catch(FileNotFoundException e){
                    return Map.of("error", "ローカルファイルが見つかりません " + filePath + e);
                } catch(Exception e){
                    return Map.of("error", "ドキュメント " + filePath + " の読み取りエラー: " + e);
                }
            }
            ```
        
*   **アーティファクトの一覧表示：** 利用可能なファイルを確認します。
    
    === "Python"
        
        ```python
        # 疑似コード：ツール関数内
        from google.adk.tools import ToolContext
        
        def check_available_docs(tool_context: ToolContext) -> dict:
            try:
                artifact_keys = tool_context.list_artifacts()
                print(f"利用可能なアーティファクト: {artifact_keys}")
                return {"available_docs": artifact_keys}
            except ValueError as e:
                return {"error": f"アーティファクトサービスのエラー: {e}"}
        ```
        
    === "Go"

        ```go
        import "google.golang.org/adk/tool"
        
        --8<-- "examples/go/snippets/context/main.go:artifacts_list"
        ```

    === "Java"
        
        ```java
        // 疑似コード：ツール関数内
        import com.google.adk.tools.ToolContext;
        
        public Map<String, String> checkAvailableDocs(ToolContext toolContext){
            try{
                Single<List<String>> artifactKeys = toolContext.listArtifacts();
                System.out.println("利用可能なアーティファクト: " + artifactKeys.tostring());
                return Map.of("availableDocs", "artifactKeys");
            } catch(IllegalArgumentException e){
                return Map.of("error", "アーティファクトサービスのエラー: " + e);
            }
        }
        ```

### ツール認証の処理 

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

ツールに必要なAPIキーやその他の認証情報を安全に管理します。

```python
# 疑似コード：認証が必要なツール
from google.adk.tools import ToolContext
from google.adk.auth import AuthConfig # 適切なAuthConfigが定義されていると仮定

# 必要な認証設定を定義（例：OAuth, APIキー）
MY_API_AUTH_CONFIG = AuthConfig(...)
AUTH_STATE_KEY = "user:my_api_credential" # 取得した認証情報を保存するキー

def call_secure_api(tool_context: ToolContext, request_data: str) -> dict:
    # 1. 認証情報が既に状態に存在するか確認
    credential = tool_context.state.get(AUTH_STATE_KEY)

    if not credential:
        # 2. 存在しない場合は要求
        print("認証情報が見つからないため、要求します...")
        try:
            tool_context.request_credential(MY_API_AUTH_CONFIG)
            # フレームワークがイベントのyieldを処理します。ツールの実行はこのターンでここで停止します。
            return {"status": "認証が必要です。認証情報を提供してください。"}
        except ValueError as e:
            return {"error": f"認証エラー: {e}"} # 例：function_call_id がない
        except Exception as e:
            return {"error": f"認証情報の要求に失敗しました: {e}"}

    # 3. 認証情報が存在する場合（要求後の前のターンからのものである可能性）
    #    または外部での認証フロー完了後の後続の呼び出しの場合
    try:
        # オプションで、必要に応じて再検証/再取得、または直接使用
        # 外部フローが完了したばかりの場合、ここで認証情報を取得できる可能性がある
        auth_credential_obj = tool_context.get_auth_response(MY_API_AUTH_CONFIG)
        api_key = auth_credential_obj.api_key # または access_token など

        # セッション内の将来の呼び出しのために状態に保存し直す
        tool_context.state[AUTH_STATE_KEY] = auth_credential_obj.model_dump() # 取得した認証情報を永続化

        print(f"取得した認証情報を使用してAPIをデータで呼び出します: {request_data}")
        # ... api_keyを使用して実際のAPI呼び出しを行う ...
        api_result = f"{request_data} の API 結果"

        return {"result": api_result}
    except Exception as e:
        # 認証情報の使用/取得エラーの処理
        print(f"認証情報の使用エラー: {e}")
        # 認証情報が無効な場合は状態キーをクリアすることも検討
        # tool_context.state[AUTH_STATE_KEY] = None
        return {"error": "認証情報の使用に失敗しました"}

```
*注意：`request_credential`はツールを一時停止し、認証の必要性を通知します。ユーザー/システムが認証情報を提供すると、後続の呼び出しで`get_auth_response`（または状態の再確認）によってツールが続行できるようになります。* `tool_context.function_call_id`は、要求と応答をリンクするためにフレームワークによって暗黙的に使用されます。

### メモリの活用 

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

過去や外部ソースから関連情報にアクセスします。

```python
# 疑似コード：メモリ検索を使用するツール
from google.adk.tools import ToolContext

def find_related_info(tool_context: ToolContext, topic: str) -> dict:
    try:
        search_results = tool_context.search_memory(f"{topic}に関する情報")
        if search_results.results:
            print(f"'{topic}' に関するメモリ検索結果が {len(search_results.results)} 件見つかりました")
            # search_results.resultsを処理（これらはSearchMemoryResponseEntry）
            top_result_text = search_results.results[0].text
            return {"memory_snippet": top_result_text}
        else:
            return {"message": "関連するメモリが見つかりませんでした。"}
    except ValueError as e:
        return {"error": f"メモリサービスのエラー: {e}"} # 例：サービスが設定されていない
    except Exception as e:
        return {"error": f"メモリ検索中に予期せぬエラーが発生しました: {e}"}
```

### 上級：直接的な `InvocationContext` の使用 

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

ほとんどのインタラクションは`CallbackContext`や`ToolContext`を介して行われますが、時にはエージェントのコアロジック（`_run_async_impl`/`_run_live_impl`）が直接アクセスする必要がある場合があります。

```python
# 疑似コード：エージェントの_run_async_impl内
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator

class MyControllingAgent(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 例：特定のサービスが利用可能か確認
        if not ctx.memory_service:
            print("この呼び出しではメモリサービスは利用できません。")
            # エージェントの振る舞いを変更する可能性

        # 例：何らかの条件に基づいて早期終了
        if ctx.session.state.get("critical_error_flag"):
            print("重大なエラーが検出されたため、呼び出しを終了します。")
            ctx.end_invocation = True # フレームワークに処理停止を通知
            yield Event(author=self.name, invocation_id=ctx.invocation_id, content="重大なエラーのため停止します。")
            return # このエージェントの実行を停止

        # ... 通常のエージェント処理 ...
        yield # ... イベント ...
```

`ctx.end_invocation = True`を設定することは、エージェントやそのコールバック/ツール内から（それぞれのコンテキストオブジェクトを介して基盤となる`InvocationContext`のフラグにアクセスし変更することで）リクエスト-レスポンスサイクル全体を正常に停止させる方法です。

## 要点とベストプラクティス

*   **適切なコンテキストを使用する：** 常に提供される最も具体的なコンテキストオブジェクトを使用してください（ツール/ツールコールバックでは`ToolContext`、エージェント/モデルコールバックでは`CallbackContext`、該当する場合は`ReadonlyContext`）。完全な`InvocationContext`（`ctx`）は、必要な場合にのみ`_run_async_impl` / `_run_live_impl`で直接使用してください。
*   **データフローのための状態：** `context.state`は、呼び出し*内*でデータを共有し、好みを記憶し、会話メモリを管理するための主要な方法です。永続ストレージを使用する場合は、プレフィックス（`app:`、`user:`、`temp:`）を慎重に使用してください。
*   **ファイルのためのアーティファクト：** ファイル参照（パスやURIなど）や大きなデータのかたまりを管理するには、`context.save_artifact`と`context.load_artifact`を使用してください。参照を保存し、必要に応じてコンテンツをロードします。
*   **追跡される変更：** コンテキストメソッドを介して状態やアーティファクトに行われた変更は、現在のステップの`EventActions`に自動的にリンクされ、`SessionService`によって処理されます。
*   **シンプルに始める：** まずは`state`と基本的なアーティファクトの使用に焦点を当ててください。ニーズがより複雑になるにつれて、認証、メモリ、および高度な`InvocationContext`のフィールド（ライブストリーミング用のものなど）を探求してください。

これらのコンテキストオブジェクトを理解し効果的に使用することで、ADKでより洗練され、ステートフルで、有能なエージェントを構築することができます。