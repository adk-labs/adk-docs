# エージェント ランタイムでデプロイされたエージェントをテストする

これらの手順では、にデプロイされた ADK エージェントをテストする方法について説明します。
[Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
ランタイム環境。これらの手順を使用する前に、次の作業を完了する必要があります
エージェント ランタイム ランタイム環境へのエージェントのデプロイメント
[available methods](/deploy/agent-runtime/)の。このガイドでは、次のことを示します
Google Cloud 経由でデプロイされたエージェントを表示、操作、テストする方法
コンソール、および REST API 呼び出しまたはエージェント プラットフォーム SDK を使用してエージェントと対話する
パイソン用。

## Cloud Console でデプロイされたエージェントを表示する

Cloud Console でデプロイされたエージェントを表示するには:

- Google Cloud Console の [エージェント ランタイム] ページに移動します。
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

このページには、現在選択されている Google Cloud にデプロイされているすべてのエージェントがリストされます
プロジェクト。エージェントがリストに表示されない場合は、エージェントを持っていることを確認してください。
Google Cloud Console で選択したターゲット プロジェクト。詳細については、
既存の Google Cloud プロジェクトの選択については、を参照してください。
[Creating and managing projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects)。

## Google Cloud プロジェクト情報を見つける

プロジェクトのアドレスとリソース ID (`PROJECT_ID`、
`LOCATION_ID`、`RESOURCE_ID`) を使用して、展開をテストできるようになります。クラウドを利用できる
この情報を見つけるには、コンソールまたは `gcloud` コマンド ライン ツールを使用します。

??? note "エージェント プラットフォームのエクスプレス モード API キー"
    Agent Platform 高速モードを使用している場合は、この手順をスキップして API キーを使用できます。

Google Cloud Console でプロジェクト情報を検索するには:

1. Google Cloud Console で、[エージェント ランタイム] ページに移動します。
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

1. ページの上部で [**API URL**] を選択し、**クエリをコピーします。
    デプロイされたエージェントの URL** 文字列。次の形式である必要があります。

        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query

`gcloud` コマンド ライン ツールを使用してプロジェクト情報を検索するには:

1. 開発環境で、認証されていることを確認してください。
    Google Cloud にアクセスし、次のコマンドを実行してプロジェクトを一覧表示します。

    ```shell
    gcloud projects list
    ```

1. デプロイメントに使用したプロジェクト ID を使用して、次のコマンドを実行して取得します。
    追加の詳細:

    ```shell
    gcloud asset search-all-resources \
        --scope=projects/$(PROJECT_ID) \
        --asset-types='aiplatform.googleapis.com/ReasoningEngine' \
        --format="table(name,assetType,location,reasoning_engine_id)"
    ```

## REST 呼び出しを使用してテストする

エージェント ランタイムでデプロイされたエージェントと対話する簡単な方法は、REST を使用することです。
`curl` ツールを使用して呼び出します。このセクションでは、
エージェントへの接続と、デプロイされたエージェントによるリクエストの処理のテストにも使用できます。
エージェント。

### エージェントへの接続を確認してください

**クエリ URL** を使用して、実行中のエージェントへの接続を確認できます。
Cloud Console のエージェント ランタイム セクションで利用できます。このチェックでは、
デプロイされたエージェントを実行しますが、エージェントに関する情報を返します。

REST 呼び出しを送信し、デプロイされたエージェントから応答を取得するには:

- 開発環境のターミナル ウィンドウでリクエストを作成します。
    そしてそれを実行します:

    === "Google Cloud Project"

        ```shell
        curl -X GET \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            "https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines"
        ```

    === "Agent Platform express mode"

        ```shell
        curl -X GET \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            "https://aiplatform.googleapis.com/v1/reasoningEngines"
        ```

デプロイメントが成功した場合、このリクエストは有効なリストを返します。
リクエストと予期されるデータ形式。

!!! tip "接続 URL の `:query` パラメータを削除"
    クラウドのエージェント ランタイム セクションで利用可能な **クエリ URL** を使用する場合
    コンソールでは、アドレスの末尾から `:query` パラメータを必ず削除してください。

!!! tip "エージェント接続のためのアクセス"
    この接続テストでは、呼び出し元のユーザーがその接続に対する有効なアクセス トークンを持っている必要があります。
    配備されたエージェント。他の環境からテストする場合は、呼び出し元のユーザーが
    Google Cloud プロジェクトのエージェントに接続するためのアクセス権を持っています。

### エージェントリクエストを送信する

エージェント プロジェクトから応答を取得するときは、最初に
セッションを開始し、セッション ID を受信し、そのセッションを使用してリクエストを送信します。
ID。このプロセスについては、次の手順で説明します。

REST 経由でデプロイされたエージェントとの対話をテストするには:

1. 開発環境のターミナル ウィンドウでセッションを作成します。
    このテンプレートを使用してリクエストを作成します。

    === "Google Cloud Project"

        ```shell
        curl \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            -H "Content-Type: application/json" \
            https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

    === "Agent Platform express mode"

        ```shell
        curl \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            -H "Content-Type: application/json" \
            https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

1. 前のコマンドからの応答で、作成された **セッション ID** を抽出します。
    **id** フィールドから:

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

1. 開発環境のターミナル ウィンドウで、次の宛先にメッセージを送信します。
    このテンプレートとセッション ID を使用してリクエストを作成し、エージェントを作成します。
    前のステップで作成したもの:

    === "Google Cloud Project"

        ```shell
        curl \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):streamQuery?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "Hey whats the weather in new york today?",
        }
        }'
        ```

    === "Agent Platform express mode"

        ```shell
        curl \
        -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
        -H "Content-Type: application/json" \
        https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):streamQuery?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "Hey whats the weather in new york today?",
        }
        }'
        ```

このリクエストは、JSON でデプロイされたエージェント コードからの応答を生成する必要があります。
形式。デプロイされた ADK エージェントとの対話の詳細については、
REST 呼び出しを使用したエージェント ランタイムについては、を参照してください。
[Manage deployed agents](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview#console)
そして
[Use an Agent Development Kit agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)
エージェント ランタイムのドキュメントを参照してください。

## Python を使用してテストする

Python コードを使用すると、より洗練された反復可能なテストを行うことができます。
エージェント ランタイムにデプロイされたエージェント。これらの手順では、作成方法について説明します。
デプロイされたエージェントとのセッションを開始し、エージェントにリクエストを送信します。
処理中。

### リモートセッションを作成する

`remote_app` オブジェクトを使用して、デプロイされたリモート エージェントへの接続を作成します。

```py
# If you are in a new script or used the ADK CLI to deploy, you can connect like this:
# remote_app = agent_engines.get("your-agent-resource-name")
remote_session = await remote_app.async_create_session(user_id="u_456")
print(remote_session)
```

`create_session` (リモート) の予想される出力:

```console
{'events': [],
'user_id': 'u_456',
'state': {},
'id': '7543472750996750336',
'app_name': '7917477678498709504',
'last_update_time': 1743683353.030133}
```

`id` 値はセッション ID で、`app_name` はそのリソース ID です。
エージェント ランタイムにエージェントをデプロイします。

#### リモート エージェントにクエリを送信する

```py
async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="whats the weather in new york",
):
    print(event)
```

`async_stream_query` (リモート) の予想される出力:

```console
{'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

デプロイされた ADK エージェントとの対話の詳細については、
エージェント ランタイム、を参照してください。
[Manage deployed agents](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)
そして
[Use a Agent Development Kit agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)
エージェント ランタイムのドキュメントを参照してください。

### マルチモーダルクエリの送信

マルチモーダル クエリ (画像など) をエージェントに送信するには、`types.Part` オブジェクトのリストを使用して、`async_stream_query` の `message` パラメーターを構築できます。各パーツにはテキストまたは画像を使用できます。

画像を含めるには、`types.Part.from_uri` を使用して、画像の Google Cloud Storage (GCS) URI を指定します。

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

!!! note
    モデルとの基礎となる通信には Base64 が含まれる場合がありますが、
    画像のエンコーディング、画像を送信するために推奨およびサポートされている方法
    Agent Runtime にデプロイされたエージェントにデータを送信するには、GCS URI を提供します。

## デプロイメントをクリーンアップする

テストとして展開を実行した場合は、クリーンアップすることをお勧めします。
完了したら、クラウド リソースを削除します。デプロイされたエージェントを削除できます
ランタイム インスタンス。Google Cloud アカウントへの予期せぬ請求を回避します。

```python
remote_app.delete(force=True)
```

`force=True` パラメータは、生成されたすべての子リソースも削除します
デプロイされたエージェント (セッションなど) から。デプロイしたものを削除することもできます
エージェント経由で
[Agent Runtime UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)
Googleクラウド上で。
