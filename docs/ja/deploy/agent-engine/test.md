# Agent Engine にデプロイしたエージェントをテストする

この手順では、[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
ランタイム環境にデプロイした ADK エージェントをテストする方法を説明します。
この手順を使う前に、[利用可能な方法](/adk-docs/deploy/agent-engine/) のいずれかで
エージェントを Agent Engine ランタイムにデプロイしておく必要があります。
このガイドでは、Google Cloud Console での確認・操作方法に加え、
REST API 呼び出しまたは Vertex AI SDK for Python での操作方法を示します。

## Cloud Console でデプロイ済みエージェントを確認する

Cloud Console でデプロイ済みエージェントを確認するには:

-   Google Cloud Console の Agent Engine ページに移動します。
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

このページには、現在選択中の Google Cloud プロジェクトにデプロイされた
すべてのエージェントが表示されます。エージェントが見つからない場合は、
Cloud Console で対象プロジェクトが選択されていることを確認してください。
詳細は
[プロジェクトの作成と管理](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects)
を参照してください。

## Google Cloud プロジェクト情報を確認する

デプロイをテストするには、プロジェクトのアドレスとリソース識別子
（`PROJECT_ID`、`LOCATION_ID`、`RESOURCE_ID`）が必要です。
Cloud Console または `gcloud` コマンドラインツールで確認できます。

??? note "Vertex AI express mode API key"
    Vertex AI express mode を使用している場合、この手順はスキップして API キーを使えます。

Google Cloud Console でプロジェクト情報を確認するには:

1.  Google Cloud Console の Agent Engine ページへ移動します。
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

1.  ページ上部で **API URLs** を選択し、デプロイ済みエージェントの
    **Query URL** 文字列をコピーします。形式は次のとおりです。

        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query

`gcloud` コマンドラインツールでプロジェクト情報を確認するには:

1.  開発環境で Google Cloud への認証が済んでいることを確認し、
    次のコマンドでプロジェクト一覧を表示します。

    ```shell
    gcloud projects list
    ```

1.  デプロイに使用した Project ID を使って次のコマンドを実行し、
    追加情報を取得します。

    ```shell
    gcloud asset search-all-resources \
        --scope=projects/$(PROJECT_ID) \
        --asset-types='aiplatform.googleapis.com/ReasoningEngine' \
        --format="table(name,assetType,location,reasoning_engine_id)"
    ```

## REST 呼び出しでテストする

Agent Engine にデプロイしたエージェントとやり取りする簡単な方法は、
`curl` を使った REST 呼び出しです。このセクションでは、
エージェント接続の確認と、デプロイ済みエージェントへのリクエスト処理テストを説明します。

### エージェントへの接続を確認する

Cloud Console の Agent Engine セクションにある **Query URL** を使って、
実行中エージェントへの接続を確認できます。
この確認ではエージェントを実行せず、エージェント情報を返します。

REST 呼び出しを送って、デプロイ済みエージェントから応答を得るには:

-   開発環境のターミナルでリクエストを組み立てて実行します。

    === "Google Cloud Project"

        ```shell
        curl -X GET \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            "https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines"
        ```

    === "Vertex AI express mode"

        ```shell
        curl -X GET \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            "https://aiplatform.googleapis.com/v1/reasoningEngines"
        ```

デプロイが成功していれば、有効なリクエスト一覧と想定データ形式が返ります。

!!! tip "接続 URL の `:query` パラメータを外す"
    Agent Engine セクションの **Query URL** を使う場合、URL 末尾の `:query` パラメータを削除してください。

!!! tip "エージェント接続のアクセス権"
    この接続テストには、呼び出しユーザーがデプロイ済みエージェントへの
    有効なアクセストークンを持っている必要があります。
    別環境からテストする場合は、呼び出しユーザーに対象 Google Cloud プロジェクトで
    エージェントへ接続する権限があることを確認してください。

### エージェントへリクエストを送る

エージェントから応答を得るには、まずセッションを作成して Session ID を取得し、
その Session ID を使ってリクエストを送る必要があります。

REST でデプロイ済みエージェントとの対話をテストするには:

1.  開発環境のターミナルで、次のテンプレートを使ってセッションを作成します。

    === "Google Cloud Project"

        ```shell
        curl \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            -H "Content-Type: application/json" \
            https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

    === "Vertex AI express mode"

        ```shell
        curl \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            -H "Content-Type: application/json" \
            https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

1.  前のコマンド応答から、**id** フィールドの **Session ID** を取り出します。

    ```json
    {
        "output": {
            "userId": "u_123",
            "lastUpdateTime": 1757690426.337745,
            "state": {},
            "id": "4857885913439920384", # Session ID
            "appName": "9888888855577777776",
            "events": []
        }
    }
    ```

1.  開発環境のターミナルで、前手順で作成した Session ID を使って
    次のテンプレートでエージェントにメッセージを送ります。

    === "Google Cloud Project"

        ```shell
        curl \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "Hey whats the weather in new york today?",
        }
        }'
        ```

    === "Vertex AI express mode"

        ```shell
        curl \
        -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
        -H "Content-Type: application/json" \
        https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):query?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "Hey whats the weather in new york today?",
        }
        }'
        ```

このリクエストにより、デプロイ済みエージェントコードから JSON 形式の応答が返るはずです。
Agent Engine 上の ADK エージェントを REST で操作する詳細は、
Agent Engine ドキュメントの
[デプロイ済みエージェントの管理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview#console)
および
[Agent Development Kit エージェントを使う](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)
を参照してください。

## Python でテストする

Agent Engine にデプロイしたエージェントを、より高度かつ再現性高くテストするには
Python コードを使えます。この手順では、リモートエージェントのセッション作成と
リクエスト送信の方法を説明します。

### リモートセッションを作成する

`remote_app` オブジェクトを使って、デプロイ済みリモートエージェントへ接続します。

```py
# 新しいスクリプトで実行する場合、または ADK CLI でデプロイした場合は次のように接続できます。
# remote_app = agent_engines.get("your-agent-resource-name")
remote_session = await remote_app.async_create_session(user_id="u_456")
print(remote_session)
```

`create_session`（remote）の想定出力:

```console
{'events': [],
'user_id': 'u_456',
'state': {},
'id': '7543472750996750336',
'app_name': '7917477678498709504',
'last_update_time': 1743683353.030133}
```

`id` の値はセッション ID で、`app_name` は Agent Engine にデプロイした
エージェントのリソース ID です。

#### リモートエージェントにクエリを送る

```py
async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="whats the weather in new york",
):
    print(event)
```

`async_stream_query`（remote）の想定出力:

```console
{'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

Agent Engine 上の ADK エージェントとの連携については、
Agent Engine ドキュメントの
[デプロイ済みエージェントの管理](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)
および
[Agent Development Kit エージェントを使う](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)
を参照してください。

### マルチモーダルクエリを送信する

エージェントにマルチモーダルクエリ（例: 画像を含む）を送るには、
`async_stream_query` の `message` パラメータを `types.Part` オブジェクトの
リストで構築します。各 Part はテキストまたは画像にできます。

画像を含めるには、Google Cloud Storage（GCS）URI を指定する
`types.Part.from_uri` を使えます。

```python
from google.genai import types

image_part = types.Part.from_uri(
    file_uri="gs://cloud-samples-data/generative-ai/image/scones.jpg",
    mime_type="image/jpeg",
)
text_part = types.Part.from_text(
    text="What is in this image?",
)

async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message=[text_part, image_part],
):
    print(event)
```

!!!note
    モデルとの内部通信で画像に Base64 エンコードが使われる場合がありますが、
    Agent Engine にデプロイしたエージェントへ画像データを送る
    推奨かつサポートされる方法は GCS URI を指定することです。

## デプロイをクリーンアップする

テスト目的でデプロイした場合、完了後にクラウドリソースをクリーンアップすることを
推奨します。想定外の課金を防ぐため、デプロイ済み Agent Engine インスタンスを
削除できます。

```python
remote_app.delete(force=True)
```

`force=True` を指定すると、セッションなどデプロイ済みエージェントから生成された
子リソースも削除されます。Google Cloud の
[Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)
から削除することもできます。
