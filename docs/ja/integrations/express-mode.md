---
catalog_title: Vertex AI express mode
catalog_description: Try development with Vertex AI services at no cost
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["google"]
---
# Vertex AI Expressモード：Vertex AIセッションとメモリの使用

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

`VertexAiSessionService` または `VertexAiMemoryBankService` の利用に興味があるものの、Google Cloudプロジェクトをお持ちでない場合は、Vertex AI Expressモードに登録することで、無料でこれらのサービスにアクセスして試すことができます。対象となる***gmail***アカウントで[こちら](https://console.cloud.google.com/expressmode)から登録できます。Vertex AI Expressモードの詳細については、[概要ページ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)をご覧ください。
登録後、[APIキー](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview#api-keys)を取得すれば、ローカルのADKエージェントでVertex AIセッションおよびメモリサービスを使い始めることができます！

!!! info Vertex AI Expressモードの制限事項

    Vertex AI Expressモードは、無料利用枠にいくつかの制限があります。無料のExpressモードプロジェクトは90日間のみ有効で、限られた割り当てで一部のサービスのみが利用可能です。例えば、エージェントエンジン（Agent Engine）の数は10個に制限されており、エージェントエンジンへのデプロイは有料利用枠専用です。割り当て制限を解除し、Vertex AIのすべてのサービスを利用するには、Expressモードプロジェクトに請求先アカウントを追加してください。

## エージェントエンジンの作成

`Session` オブジェクトは `AgentEngine` の子要素です。Vertex AI Expressモードを使用する場合、すべての `Session` および `Memory` オブジェクトを管理するための親として、空の `AgentEngine` を作成できます。
まず、環境変数が正しく設定されていることを確認してください。例えば、Pythonの場合は以下のようになります。

```env title="agent/.env"
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_API_KEY=ここに実際のEXPRESSモードのAPIキーを貼り付けてください
```

次に、エージェントエンジンのインスタンスを作成します。Vertex AI SDKを使用できます。

=== "Vertex AI SDK"

    1. Vertex AI SDKをインポートします。

        ```py
        import vertexai
        from vertexai import agent_engines
        ```

    2. APIキーでVertex AIクライアントを初期化し、エージェントエンジンのインスタンスを作成します。
        
        ```py
        # Gen AI SDKでエージェントエンジンを作成
        client = vertexai.Client(
          api_key="YOUR_API_KEY",
        )

        agent_engine = client.agent_engines.create(
          config={
            "display_name": "デモ・エージェントエンジン",
            "description": "セッションとメモリ用のエージェントエンジン",
          })
        ```

    3. `YOUR_AGENT_ENGINE_DISPLAY_NAME` と `YOUR_AGENT_ENGINE_DESCRIPTION` をご自身のユースケースに合わせて置き換えてください。
    4. レスポンスからエージェントエンジンの名前とIDを取得し、メモリとセッションで使用します。

        ```py
        APP_ID = agent_engine.api_resource.name.split('/')[-1]
        ```

## `VertexAiSessionService`によるセッション管理

[`VertexAiSessionService`](session.md###sessionservice-implementations) は Vertex AI ExpressモードのAPIキーと互換性があります。プロジェクトやロケーションを指定せずにセッションオブジェクトを初期化できます。

```py
# 必要なライブラリ: pip install google-adk[vertexai]
# 加えて環境変数の設定:
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=ここに実際のEXPRESSモードのAPIキーを貼り付けてください
from google.adk.sessions import VertexAiSessionService

# このサービスで使用されるapp_nameは、Reasoning EngineのIDまたは名前である必要があります
APP_ID = "your-reasoning-engine-id"

# Vertex Expressモードで初期化する場合、プロジェクトとロケーションは不要です
session_service = VertexAiSessionService(agent_engine_id=APP_ID)
# サービスメソッドを呼び出す際はREASONING_ENGINE_APP_IDを使用します。例：
# session = await session_service.create_session(app_name=APP_ID, user_id= ...)
```

!!! info セッションサービスの割り当て

    無料のExpressモードプロジェクトの場合、`VertexAiSessionService` には以下の割り当てがあります：

    - Vertex AI エージェントエンジンセッションの作成、削除、更新：毎分10回
    - Vertex AI エージェントエンジンセッションへのイベント追加：毎分30回

## `VertexAiMemoryBankService`によるメモリ管理

[`VertexAiMemoryBankService`](memory.md###memoryservice-implementations) は Vertex AI ExpressモードのAPIキーと互換性があります。プロジェクトやロケーションを指定せずにメモリオブジェクトを初期化できます。

```py
# 必要なライブラリ: pip install google-adk[vertexai]
# 加えて環境変数の設定:
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_API_KEY=ここに実際のEXPRESSモードのAPIキーを貼り付けてください
from google.adk.memory import VertexAiMemoryBankService

# このサービスで使用されるapp_nameは、Reasoning EngineのIDまたは名前である必要があります
APP_ID = "your-reasoning-engine-id"

# Vertex Expressモードで初期化する場合、プロジェクトとロケーションは不要です
memory_service = VertexAiMemoryBankService(agent_engine_id=APP_ID)
# エージェントがユーザーに関する詳細を記憶できるよう、そのセッションからメモリを生成します
# memory = await memory_service.add_session_to_memory(session)
```

!!! info メモリサービスの割り当て

    無料のExpressモードプロジェクトの場合、`VertexAiMemoryBankService` には以下の割り当てがあります：

    - Vertex AI エージェントエンジンメモリリソースの作成、削除、更新：毎分10回
    - Vertex AI エージェントエンジンメモリバンクからの取得、一覧表示、検索：毎分10回

## コードサンプル：Vertex AI Expressモードを使用したセッションとメモリ機能を持つ天気エージェント

このサンプルでは、`VertexAiSessionService` と `VertexAiMemoryBankService` の両方を利用してコンテキスト管理を行う天気エージェントを作成します。これにより、エージェントはユーザーの好みや会話を思い出すことができます！

**[Vertex AI Expressモードを使用したセッションとメモリ機能を持つ天気エージェント](https://github.com/google/adk-docs/blob/main/examples/python/notebooks/express-mode-weather-agent.ipynb)**
