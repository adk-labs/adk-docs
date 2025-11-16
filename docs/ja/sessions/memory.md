# メモリ：`MemoryService`による長期的な知識

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`Session`が*単一の進行中の会話*の履歴（`events`）と一時データ（`state`）を追跡する方法を見てきました。しかし、エージェントが*過去*の会話から情報を思い出す必要がある場合はどうでしょうか？ここで、**長期的な知識**と**`MemoryService`**の概念が登場します。

次のように考えてみてください。

* **`Session` / `State`:** 特定のチャット中の短期記憶のようなものです。
* **長期的な知識（`MemoryService`）**: エージェントが参照できる検索可能なアーカイブまたは知識ライブラリのようなもので、多くの過去のチャットや他のソースからの情報が含まれている可能性があります。

## `MemoryService`の役割

`BaseMemoryService`は、この検索可能な長期的な知識ストアを管理するためのインターフェイスを定義します。その主な責任は次のとおりです。

1. **情報の取り込み（`add_session_to_memory`）：** （通常は完了した）`Session`のコンテンツを取得し、関連情報を長期的な知識ストアに追加します。
2. **情報の検索（`search_memory`）：** エージェント（通常は`Tool`を介して）が知識ストアをクエリし、検索クエリに基づいて関連するスニペットまたはコンテキストを取得できるようにします。

## 適切なメモリサービスの選択

ADKは、それぞれ異なるユースケースに合わせて調整された2つの異なる`MemoryService`実装を提供します。以下の表を使用して、エージェントに最適なものを決定してください。

| **機能** | **InMemoryMemoryService** | **VertexAiMemoryBankService** |
| :--- | :--- | :--- |
| **永続性** | なし（再起動時にデータは失われます） | はい（Vertex AIによって管理されます） |
| **主なユースケース** | プロトタイピング、ローカル開発、および簡単なテスト。 | ユーザーの会話から意味のある、進化する記憶を構築します。 |
| **メモリ抽出** | 完全な会話を保存します | 会話から[意味のある情報](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/generate-memories)を抽出し、既存の記憶と統合します（LLMを利用） |
| **検索機能** | 基本的なキーワードマッチング。 | 高度なセマンティック検索。 |
| **セットアップの複雑さ** | なし。デフォルトです。 | 低。Vertex AIに[エージェントエンジン](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)インスタンスが必要です。 |
| **依存関係** | なし。 | Google Cloudプロジェクト、Vertex AI API |
| **使用するタイミング** | プロトタイピングのために複数のセッションのチャット履歴を検索する場合。 | エージェントに過去のやり取りから記憶させ、学習させたい場合。 |

## インメモリメモリ

`InMemoryMemoryService`は、アプリケーションのメモリにセッション情報を保存し、検索のために基本的なキーワードマッチングを実行します。セットアップは不要で、永続性が必要ないプロトタイピングや簡単なテストシナリオに最適です。

=== "Python"

    ```py
    from google.adk.memory import InMemoryMemoryService
    memory_service = InMemoryMemoryService()
    ```

=== "Go"
    ```go
    import (
      "google.golang.org/adk/memory"
      "google.golang.org/adk/session"
    )

    // 状態とメモリを共有するには、ランナー間でサービスを共有する必要があります。
    sessionService := session.InMemoryService()
    memoryService := memory.InMemoryService()
    ```


**例：メモリの追加と検索**

この例では、簡単にするために`InMemoryMemoryService`を使用した基本的なフローを示します。

=== "Python"

    ```py
    import asyncio
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService, Session
    from google.adk.memory import InMemoryMemoryService # MemoryServiceをインポート
    from google.adk.runners import Runner
    from google.adk.tools import load_memory # メモリをクエリするツール
    from google.genai.types import Content, Part

    # --- 定数 ---
    APP_NAME = "memory_example_app"
    USER_ID = "mem_user"
    MODEL = "gemini-1.5-flash" # 有効なモデルを使用

    # --- エージェントの定義 ---
    # エージェント1：情報をキャプチャするためのシンプルなエージェント
    info_capture_agent = LlmAgent(
        model=MODEL,
        name="InfoCaptureAgent",
        instruction="ユーザーの発言を承認します。",
    )

    # エージェント2：メモリを使用できるエージェント
    memory_recall_agent = LlmAgent(
        model=MODEL,
        name="MemoryRecallAgent",
        instruction="ユーザーの質問に答えます。答えが過去の会話にある可能性がある場合は、「load_memory」ツールを使用してください。",
        tools=[load_memory] # エージェントにツールを提供
    )

    # --- サービス ---
    # 状態とメモリを共有するには、ランナー間でサービスを共有する必要があります
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService() # デモ用にインメモリを使用

    async def run_scenario():
        # --- シナリオ ---

        # ターン1：セッションでいくつかの情報をキャプチャする
        print("--- ターン1：情報のキャプチャ ---")
        runner1 = Runner(
            # 情報キャプチャエージェントから開始
            agent=info_capture_agent,
            app_name=APP_NAME,
            session_service=session_service,
            memory_service=memory_service # ランナーにメモリサービスを提供
        )
        session1_id = "session_info"
        await runner1.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)
        user_input1 = Content(parts=[Part(text="私のお気に入りのプロジェクトはプロジェクトアルファです。")])

        # エージェントを実行
        final_response_text = "（最終応答なし）"
        async for event in runner1.run_async(user_id=USER_ID, session_id=session1_id, new_message=user_input1):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
        print(f"エージェント1の応答：{final_response_text}")

        # 完了したセッションを取得
        completed_session1 = await runner1.session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session1_id)

        # このセッションのコンテンツをメモリサービスに追加
        print("\n--- セッション1をメモリに追加 ---")
        await memory_service.add_session_to_memory(completed_session1)
        print("セッションがメモリに追加されました。")

        # ターン2：新しいセッションで情報を思い出す
        print("\n--- ターン2：情報の想起 ---")
        runner2 = Runner(
            # メモリツールを持つ2番目のエージェントを使用
            agent=memory_recall_agent,
            app_name=APP_NAME,
            session_service=session_service, # 同じサービスを再利用
            memory_service=memory_service   # 同じサービスを再利用
        )
        session2_id = "session_recall"
        await runner2.session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session2_id)
        user_input2 = Content(parts=[Part(text="私のお気に入りのプロジェクトは何ですか？")])

        # 2番目のエージェントを実行
        final_response_text_2 = "（最終応答なし）"
        async for event in runner2.run_async(user_id=USER_ID, session_id=session2_id, new_message=user_input2):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text_2 = event.content.parts[0].text
        print(f"エージェント2の応答：{final_response_text_2}")

    # この例を実行するには、次のスニペットを使用できます。
    # asyncio.run(run_scenario())

    # await run_scenario()
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/memory_example/memory_example.go:full_example"
    ```


### ツール内でのメモリ検索

`tool.Context`を使用して、カスタムツール内からメモリを検索することもできます。

=== "Go"

    ```go
    --8<-- "examples/go/snippets/sessions/memory_example/memory_example.go:tool_search"
    ```

## Vertex AIメモリバンク

`VertexAiMemoryBankService`は、エージェントを[Vertex AIメモリバンク](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/memory-bank/overview)に接続します。これは、会話型エージェントに高度で永続的なメモリ機能を提供する、完全に管理されたGoogle Cloudサービスです。

### 仕組み

このサービスは、2つの主要な操作を処理します。

*   **メモリの生成：** 会話の最後に、セッションのイベントをメモリバンクに送信できます。メモリバンクは、情報をインテリジェントに処理して「メモリ」として保存します。
*   **メモリの取得：** エージェントコードは、メモリバンクに対して検索クエリを発行して、過去の会話から関連するメモリを取得できます。

### 前提条件

この機能を使用する前に、次のものが必要です。

1.  **Google Cloudプロジェクト：** Vertex AI APIが有効になっていること。
2.  **エージェントエンジン：** Vertex AIでエージェントエンジンを作成する必要があります。メモリバンクを使用するためにエージェントをエージェントエンジンランタイムにデプロイする必要はありません。これにより、構成に必要な**エージェントエンジンID**が提供されます。
3.  **認証：** ローカル環境がGoogle Cloudサービスにアクセスできるように認証されていることを確認します。最も簡単な方法は、次を実行することです。
    ```bash
    gcloud auth application-default login
    ```
4.  **環境変数：** このサービスには、Google CloudプロジェクトIDとロケーションが必要です。それらを環境変数として設定します。
    ```bash
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    export GOOGLE_CLOUD_LOCATION="your-gcp-location"
    ```

### 構成

エージェントをメモリバンクに接続するには、ADKサーバー（`adk web`または`adk api_server`）を起動するときに`--memory_service_uri`フラグを使用します。URIは`agentengine://<agent_engine_id>`の形式である必要があります。

```bash title="bash"
adk web path/to/your/agents_dir --memory_service_uri="agentengine://1234567890"
```

または、`VertexAiMemoryBankService`を手動でインスタンス化し、それを`Runner`に渡すことで、メモリバンクを使用するようにエージェントを構成できます。

=== "Python"
  ```py
  from google.adk.memory import VertexAiMemoryBankService

  agent_engine_id = agent_engine.api_resource.name.split("/")[-1]

  memory_service = VertexAiMemoryBankService(
      project="PROJECT_ID",
      location="LOCATION",
      agent_engine_id=agent_engine_id
  )

  runner = adk.Runner(
      ...
      memory_service=memory_service
  )
  ```

## エージェントでのメモリの使用

メモリサービスが構成されている場合、エージェントはツールまたはコールバックを使用してメモリを取得できます。ADKには、メモリを取得するための2つの組み込みツールが含まれています。

* `PreloadMemory`: 各ターンの開始時に常にメモリを取得します（コールバックに似ています）。
* `LoadMemory`: エージェントが役立つと判断したときにメモリを取得します。

**例：**

=== "Python"
```python
from google.adk.agents import Agent
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

agent = Agent(
    model=MODEL_ID,
    name='weather_sentiment_agent',
    instruction="...",
    tools=[PreloadMemoryTool()]
)
```

セッションからメモリを抽出するには、`add_session_to_memory`を呼び出す必要があります。たとえば、コールバックを介してこれを自動化できます。

=== "Python"
```python
from google import adk

async def auto_save_session_to_memory_callback(callback_context):
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session)

agent = Agent(
    model=MODEL,
    name="Generic_QA_Agent",
    instruction="ユーザーの質問に答えます",
    tools=[adk.tools.preload_memory_tool.PreloadMemoryTool()],
    after_agent_callback=auto_save_session_to_memory_callback,
)
```

## 高度な概念

### メモリの実際の仕組み

メモリワークフローには、内部的に次の手順が含まれます。

1. **セッションの対話：** ユーザーは`SessionService`によって管理される`Session`を介してエージェントと対話します。イベントが追加され、状態が更新される場合があります。
2. **メモリへの取り込み：** ある時点で（多くの場合、セッションが完了したと見なされるか、重要な情報を生成した場合）、アプリケーションは`memory_service.add_session_to_memory(session)`を呼び出します。これにより、セッションのイベントから関連情報が抽出され、長期的な知識ストア（インメモリ辞書またはエージェントエンジンメモリバンク）に追加されます。
3. **後のクエリ：** *異なる*（または同じ）セッションで、ユーザーは過去のコンテキストを必要とする質問をする場合があります（例：「先週、プロジェクトXについて何を話し合いましたか？」）。
4. **エージェントがメモリツールを使用：** メモリ取得ツール（組み込みの`load_memory`ツールなど）を備えたエージェントは、過去のコンテキストの必要性を認識します。ツールを呼び出し、検索クエリ（例：「先週のプロジェクトXの議論」）を提供します。
5. **検索の実行：** ツールは内部的に`memory_service.search_memory(app_name, user_id, query)`を呼び出します。
6. **結果の返却：** `MemoryService`はストアを検索し（キーワードマッチングまたはセマンティック検索を使用）、関連するスニペットを`MemoryResult`オブジェクトのリストを含む`SearchMemoryResponse`として返します（それぞれが関連する過去のセッションのイベントを保持している可能性があります）。
7. **エージェントが結果を使用：** ツールはこれらの結果をエージェントに返し、通常はコンテキストまたは関数応答の一部として返します。その後、エージェントはこの取得した情報を使用して、ユーザーへの最終的な回答を作成できます。

### エージェントは複数のメモリサービスにアクセスできますか？

*   **標準構成を介して：いいえ。** フレームワーク（`adk web`、`adk api_server`）は、`--memory_service_uri`フラグを介して一度に1つのメモリサービスで構成するように設計されています。この単一のサービスは、エージェントに提供され、組み込みの`self.search_memory()`メソッドを介してアクセスされます。構成の観点からは、そのプロセスによって提供されるすべてのエージェントに対して1つのバックエンド（`InMemory`、`VertexAiMemoryBankService`）しか選択できません。

*   **エージェントのコード内：はい、もちろんです。** エージェントのコード内で別のメモリサービスを直接手動でインポートしてインスタンス化することを妨げるものは何もありません。これにより、単一のエージェントターン内で複数のメモリソースにアクセスできます。

たとえば、エージェントはフレームワークで構成された`InMemoryMemoryService`を使用して会話履歴を思い出し、`VertexAiMemoryBankService`を手動でインスタンス化して技術マニュアルの情報を検索できます。

#### 例：2つのメモリサービスの使用

エージェントのコードでそれを実装する方法は次のとおりです。

=== "Python"
```python
from google.adk.agents import Agent
from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService
from google.genai import types

class MultiMemoryAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.memory_service = InMemoryMemoryService()
        # ドキュメント検索用に2番目のメモリサービスを手動でインスタンス化します
        self.vertexai_memorybank_service = VertexAiMemoryBankService(
            project="PROJECT_ID",
            location="LOCATION",
            agent_engine_id="AGENT_ENGINE_ID"
        )

    async def run(self, request: types.Content, **kwargs) -> types.Content:
        user_query = request.parts[0].text

        # 1. フレームワーク提供のメモリを使用して会話履歴を検索します
        #    （構成されている場合はInMemoryMemoryServiceになります）
        conversation_context = await self.memory_service.search_memory(query=user_query)

        # 2. 手動で作成したサービスを使用してドキュメントナレッジベースを検索します
        document_context = await self.vertexai_memorybank_service.search_memory(query=user_query)

        # 両方のソースからのコンテキストを組み合わせて、より良い応答を生成します
        prompt = "過去の会話から、私は覚えています：\n"
        prompt += f"{conversation_context.memories}\n\n"
        prompt += "技術マニュアルから、私は見つけました：\n"
        prompt += f"{document_context.memories}\n\n"
        prompt += f"これらすべてに基づいて、'{user_query}'に対する私の答えは次のとおりです。"

        return await self.llm.generate_content_async(prompt)
```
