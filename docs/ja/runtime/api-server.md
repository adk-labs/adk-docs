# APIサーバーの使用

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

エージェントをデプロイする前に、意図したとおりに動作するかどうかをテストする必要があります。開発環境でエージェントをテストする最も簡単な方法は、ADK APIサーバーを使用することです。

=== "Python"

    ```py
    adk api_server
    ```

=== "Go"

    ```go
    go run agent.go web api
    ```

=== "Java"

    ポート番号を更新してください。
    === "Maven"
        MavenでADK Webサーバーをコンパイルして実行します。
        ```console
        mvn compile exec:java \
         -Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"
        ```
    === "Gradle"
        Gradleの場合、`build.gradle` または `build.gradle.kts` ビルドファイルのプラグインセクションに、次のJavaプラグインが必要です。

        ```groovy
        plugins {
            id('java')
            // 他のプラグイン
        }
        ```
        次に、ビルドファイルの別の場所、トップレベルに新しいタスクを作成します。

        ```groovy
        tasks.register('runADKWebServer', JavaExec) {
            dependsOn classes
            classpath = sourceSets.main.runtimeClasspath
            mainClass = 'com.google.adk.web.AdkWebServer'
            args '--adk.agents.source-dir=src/main/java/agents', '--server.port=8080'
        }
        ```

        最後に、コマンドラインで次のコマンドを実行します。
        ```console
        gradle runADKWebServer
        ```


    Javaでは、Dev UIとAPIサーバーは一緒にバンドルされています。

このコマンドはローカルWebサーバーを起動し、cURLコマンドを実行したりAPIリクエストを送信したりしてエージェントをテストできます。

!!! tip "高度な使用法とデバッグ"

    利用可能なすべてのエンドポイント、リクエスト/レスポンス形式、およびデバッグのヒント（インタラクティブAPIドキュメントの使用方法を含む）に関する完全なリファレンスについては、以下の **ADK APIサーバーガイド** を参照してください。

## ローカルテスト

ローカルテストでは、ローカルWebサーバーを起動し、セッションを作成し、エージェントにクエリを送信します。まず、正しい作業ディレクトリにいることを確認してください。

```console
parent_folder/
└── my_sample_agent/
    └── agent.py (または Agent.java)
```

**ローカルサーバーの起動**

次に、上記のコマンドを使用してローカルサーバーを起動します。

出力は次のようになります。

=== "Python"

    ```shell
    INFO:     Started server process [12345]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
    ```

=== "Java"

    ```shell
    2025-05-13T23:32:08.972-06:00  INFO 37864 --- [ebServer.main()] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http) with context path '/'
    2025-05-13T23:32:08.980-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : Started AdkWebServer in 1.15 seconds (process running for 2.877)
    2025-05-13T23:32:08.981-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : AdkWebServer application started successfully.
    ```

これでサーバーがローカルで実行されています。後続のすべてのコマンドで正しい **_ポート番号_** を使用するようにしてください。

**新しいセッションの作成**

APIサーバーを実行したまま、新しいターミナルウィンドウまたはタブを開き、以下を使用してエージェントとの新しいセッションを作成します。

```shell
curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"key1": "value1", "key2": 42}'
```

何が起こっているかを分解してみましょう。

* `http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123`: これは、エージェントフォルダの名前であるエージェント `my_sample_agent` に対して、ユーザーID (`u_123`) とセッションID (`s_123`) を持つ新しいセッションを作成します。`my_sample_agent` は自分のエージェントフォルダの名前に置き換えることができます。`u_123` は特定のユーザーIDに、`s_123` は特定のセッションIDに置き換えることができます。
* `{"key1": "value1", "key2": 42}`: これはオプションです。セッション作成時にエージェントの既存の状態 (dict) をカスタマイズするために使用できます。

セッションが正常に作成された場合、セッション情報が返されるはずです。出力は次のようになります。

```json
{"id":"s_123","appName":"my_sample_agent","userId":"u_123","state":{"key1":"value1","key2":42},"events":[],"lastUpdateTime":1743711430.022186}
```

!!! info

    まったく同じユーザーIDとセッションIDで複数のセッションを作成することはできません。試行した場合、`{"detail":"Session already exists: s_123"}` のようなレスポンスが表示されることがあります。これを修正するには、そのセッション (例: `s_123`) を削除するか、別のセッションIDを選択します。

**クエリの送信**

POST経由でエージェントにクエリを送信するには、`/run` または `/run_sse` の2つのルートがあります。

* `POST http://localhost:8000/run`: すべてのイベントをリストとして収集し、一度にすべて返します。ほとんどのユーザーに適しています（どちらを使うべきかわからない場合は、こちらを使用することをお勧めします）。
* `POST http://localhost:8000/run_sse`: サーバーセントイベント（Server-Sent-Events）として返します。これはイベントオブジェクトのストリームです。イベントが利用可能になったらすぐに通知を受けたいユーザーに適しています。`/run_sse`では、`streaming` を `true` に設定してトークンレベルのストリーミングを有効にすることもできます。

**`/run` の使用**

```shell
curl -X POST http://localhost:8000/run \
-H "Content-Type: application/json" \
-d '{
"app_name": "my_sample_agent",
"user_id": "u_123",
"session_id": "s_123",
"new_message": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
}
}'
```

`/run`を使用すると、イベントの完全な出力がリストとして一度に表示されます。出力は次のようになります。

```json
[{"content":{"parts":[{"functionCall":{"id":"af-e75e946d-c02a-4aad-931e-49e4ab859838","args":{"city":"new york"},"name":"get_weather"}}],"role":"model"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"longRunningToolIds":[],"id":"2Btee6zW","timestamp":1743712220.385936},{"content":{"parts":[{"functionResponse":{"id":"af-e75e946d-c02a-4aad-931e-49e4ab859838","name":"get_weather","response":{"status":"success","report":"The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}}}],"role":"user"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"PmWibL2m","timestamp":1743712221.895042},{"content":{"parts":[{"text":"OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"}],"role":"model"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"sYT42eVC","timestamp":1743712221.899018}]
```

**`/run_sse` の使用**

```shell
curl -X POST http://localhost:8000/run_sse \
-H "Content-Type: application/json" \
-d '{
"app_name": "my_sample_agent",
"user_id": "u_123",
"session_id": "s_123",
"new_message": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
},
"streaming": false
}'
```

`streaming` を `true` に設定してトークンレベルのストリーミングを有効にできます。これは、レスポンスが複数のチャンクで返されることを意味し、出力は次のようになります。

```shell
data: {"content":{"parts":[{"functionCall":{"id":"af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d","args":{"city":"new york"},"name":"get_weather"}}],"role":"model"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"longRunningToolIds":[],"id":"ptcjaZBa","timestamp":1743712255.313043}

data: {"content":{"parts":[{"functionResponse":{"id":"af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d","name":"get_weather","response":{"status":"success","report":"The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}}}],"role":"user"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"5aocxjaq","timestamp":1743712257.387306}

data: {"content":{"parts":[{"text":"OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"}],"role":"model"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"rAnWGSiV","timestamp":1743712257.391317}
```
**`/run` または `/run_sse` を使用してbase64エンコードされたファイルでクエリを送信**

```shell
curl -X POST http://localhost:8000/run \
--H 'Content-Type: application/json' \
--d '{
   "appName":"my_sample_agent",
   "userId":"u_123",
   "sessionId":"s_123",
   "newMessage":{
      "role":"user",
      "parts":[
         {
            "text":"Describe this image"
         },
         {
            "inlineData":{
               "displayName":"my_image.png",
               "data":"iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAACXBIWXMAAAsTAAALEwEAmpw...",
               "mimeType":"image/png"
            }
         }
      ]
   },
   "streaming":false
}'
```

!!! info

    `/run_sse` を使用している場合、各イベントは利用可能になり次第表示されます。

## インテグレーション

ADKは [コールバック](../callbacks/index.md) を使用して、サードパーティの可観測性ツールと統合します。これらのインテグレーションは、エージェントの呼び出しとインタラクションの詳細なトレースをキャプチャし、これは振る舞いの理解、問題のデバッグ、パフォーマンスの評価に不可欠です。

* [Comet Opik](https://github.com/comet-ml/opik) は、オープンソースのLLM可観測性および評価プラットフォームであり、[ADKをネイティブにサポート](https://www.comet.com/docs/opik/tracing/integrations/adk)しています。

## エージェントのデプロイ

エージェントのローカルでの動作を確認したので、エージェントのデプロイに進む準備ができました！エージェントをデプロイする方法はいくつかあります。

* [Agent Engine](../deploy/agent-engine/index.md) にデプロイする: ADKエージェントをGoogle Cloud上のVertex AIのマネージドサービスにデプロイする最も簡単な方法です。
* [Cloud Run](../deploy/cloud-run.md) にデプロイする: Google Cloud上のサーバーレスアーキテクチャを使用して、エージェントのスケーリングと管理を完全に制御できます。


## ADK APIサーバー

ADK APIサーバーは、エージェントをRESTful APIを介して公開する、事前にパッケージ化された [FastAPI](https://fastapi.tiangolo.com/) Webサーバーです。これはローカルテストと開発のための主要なツールであり、デプロイ前にエージェントとプログラムで対話することができます。

## サーバーの実行

サーバーを起動するには、プロジェクトのルートディレクトリから次のコマンドを実行します。

```shell
adk api_server
```

デフォルトでは、サーバーは `http://localhost:8000` で実行されます。サーバーが起動したことを確認する出力が表示されます。

```shell
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

## インタラクティブAPIドキュメントによるデバッグ

APIサーバーは、Swagger UIを使用してインタラクティブなAPIドキュメントを自動的に生成します。これは、エンドポイントの探索、リクエスト形式の理解、ブラウザから直接エージェントをテストするための非常に価値のあるツールです。

インタラクティブドキュメントにアクセスするには、APIサーバーを起動し、Webブラウザで [http://localhost:8000/docs](http://localhost:8000/docs) に移動します。

利用可能なすべてのAPIエンドポイントの完全でインタラクティブなリストが表示されます。これを展開して、パラメータ、リクエストボディ、レスポンススキーマに関する詳細情報を確認できます。「Try it out」をクリックして、実行中のエージェントにライブリクエストを送信することもできます。

## APIエンドポイント

以下のセクションでは、エージェントと対話するための主要なエンドポイントについて詳しく説明します。

!!! note "JSON命名規則"
    - **リクエストボディ** はフィールド名に `snake_case` を使用する必要があります (例: `"app_name"`)。
    - **レスポンスボディ** はフィールド名に `camelCase` を使用します (例: `"appName"`)。

### ユーティリティエンドポイント

#### 利用可能なエージェントのリスト表示

サーバーによって検出されたすべてのエージェントアプリケーションのリストを返します。

*   **メソッド:** `GET`
*   **パス:** `/list-apps`

**リクエスト例**
```shell
curl -X GET http://localhost:8000/list-apps
```

**レスポンス例**
```json
["my_sample_agent", "another_agent"]
```

---

### セッション管理

セッションは、特定のユーザーとエージェントとの対話の状態とイベント履歴を保存します。

#### セッションの作成または更新

新しいセッションを作成するか、既存のセッションを更新します。指定されたIDを持つセッションがすでに存在する場合、その状態は提供された新しい状態で上書きされます。

*   **メソッド:** `POST`
*   **パス:** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**リクエストボディ**
```json
{
  "key1": "value1",
  "key2": 42
}
```

**リクエスト例**
```shell
curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc \
  -H "Content-Type: application/json" \
  -d '{"visit_count": 5}'
```

**レスポンス例**
```json
{"id":"s_abc","appName":"my_sample_agent","userId":"u_123","state":{"visit_count":5},"events":[],"lastUpdateTime":1743711430.022186}
```

#### セッションの取得

特定のセッションの詳細（現在の状態と関連するすべてのイベントを含む）を取得します。

*   **メソッド:** `GET`
*   **パス:** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**リクエスト例**
```shell
curl -X GET http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
```

**レスポンス例**
```json
{"id":"s_abc","appName":"my_sample_agent","userId":"u_123","state":{"visit_count":5},"events":[...],"lastUpdateTime":1743711430.022186}
```

#### セッションの削除

セッションとその関連データをすべて削除します。

*   **メソッド:** `DELETE`
*   **パス:** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**リクエスト例**
```shell
curl -X DELETE http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
```

**レスポンス例**
正常に削除されると、`204 No Content` ステータスコードを持つ空のレスポンスが返されます。

---

### エージェントの実行

これらのエンドポイントは、エージェントに新しいメッセージを送信し、レスポンスを取得するために使用されます。

#### エージェントの実行（単一レスポンス）

エージェントを実行し、実行が完了した後に生成されたすべてのイベントを単一のJSON配列で返します。

*   **メソッド:** `POST`
*   **パス:** `/run`

**リクエストボディ**
```json
{
  "app_name": "my_sample_agent",
  "user_id": "u_123",
  "session_id": "s_abc",
  "new_message": {
    "role": "user",
    "parts": [
      { "text": "What is the capital of France?" }
    ]
  }
}
```

**リクエスト例**
```shell
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my_sample_agent",
    "user_id": "u_123",
    "session_id": "s_abc",
    "new_message": {
      "role": "user",
      "parts": [{"text": "What is the capital of France?"}]
    }
  }'
```

#### エージェントの実行（ストリーミング）

エージェントを実行し、イベントが生成されるとすぐに [サーバーセントイベント (SSE)](https://developer.mozilla.org/ja/docs/Web/API/Server-sent_events) を使用してクライアントにストリーミングします。

*   **メソッド:** `POST`
*   **パス:** `/run_sse`

**リクエストボディ**
リクエストボディは `/run` と同じですが、オプションの `streaming` フラグが追加されています。
```json
{
  "app_name": "my_sample_agent",
  "user_id": "u_123",
  "session_id": "s_abc",
  "new_message": {
    "role": "user",
    "parts": [
      { "text": "What is the weather in New York?" }
    ]
  },
  "streaming": true
}
```
- `streaming`: (オプション) `true` に設定すると、モデルのレスポンスに対してトークンレベルのストリーミングが有効になります。デフォルトは `false` です。

**リクエスト例**
```shell
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my_sample_agent",
    "user_id": "u_123",
    "session_id": "s_abc",
    "new_message": {
      "role": "user",
      "parts": [{"text": "What is the weather in New York?"}]
    },
    "streaming": false
  }'
```
