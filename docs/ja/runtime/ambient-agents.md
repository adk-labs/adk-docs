# 環境エージェント

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-go">Go</span>
</div>

ADK は、**アンビエント エージェント**、データを処理し、監視する自律型エージェントをサポートします。
イベントに応答し、人間の介入なしで非同期に応答します。アンビエントを使用する
エージェントの目的:

- **クラウド イベントに反応します。** ファイルがアップロードされたときにファイルを処理します。
  [Cloud Storage](https://cloud.google.com/storage)、データベースに応答します
  変更を行うか、監査ログエントリを処理します。
- **キューからのメッセージを処理します。** 受信したサポート チケットを分析します。
  コンテンツの管理、ドキュメントの分類、アイテムの到着時の QA の実行などを行います。
- **スケジュールに従って実行します。** 日次レポートを生成し、定期的に監視を実行します。
  定期的にチェックしたり、バッチ ジョブを処理したりできます。
- **インフラストラクチャを監視します。** 全体にわたる継続的なイベント ストリームに反応します。
  インフラストラクチャを構築し、変更に自律的に対応します。

## アンビエントエージェントから結果を取得する

アンビエント エージェントは人間の介入なしで実行されるため、アンビエント エージェントをルーティングする必要があります。
通知チャネルに出力します。一般的なパターンは次のとおりです。

- **[Structured logging](../observability/logging.md).** JSON ログを書き込み、
  [Cloud Monitoring](https://cloud.google.com/monitoring/support/notification-options)を構成する
  電子メール、Slack、PagerDuty 経由で通知するアラート。
- **[Pub/Sub](https://cloud.google.com/pubsub).** 結果をトピックに公開する
  ダウンストリーム サービスが利用できるようになります。
- **[Application Integration](https://cloud.google.com/application-integration/docs/listen-pub-sub-topic-send-email).**
  エージェントの出力を電子メール、Jira、またはその他のシステムにルーティングします。

## アンビエントエージェントを構築する方法

ADK は 2 つのアプローチを提供します。

| | [`/run`](api-server.md) |トリガーエンドポイント |
| :--- | :--- | :--- |
| **イベント ソース** |任意 (Pub/Sub、Webhook、cron、カスタム サービス) | [Cloud Pub/Sub](https://cloud.google.com/pubsub)、[Eventarc](https://cloud.google.com/eventarc) ([Standard](https://cloud.google.com/eventarc/standard/docs/overview) および [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview)) |
| **ペイロード解析** |あなたがそれを処理します |自動 (Base64 デコード、CloudEvent 解析) |
| **セッションの作成** | `--auto_create_session` を有効にする |自動 (イベントごとに 1 つ) |
| **セッション ストレージ** |構成済みの [`SessionService`](../sessions/session/index.md) |構成済みの [`SessionService`](../sessions/session/index.md) |
| **同時実行制御** |あなたがそれを処理します |制限を設定可能な組み込みセマフォ |
| **再試行ロジック** |あなたがそれを処理します |一時的なエラーに対するジッターを伴う指数バックオフ |
| **こんな用途に最適** |カスタム統合、GCP 以外のソース | GCP ネイティブのイベントドリブン ワークロード |

## `/run` を使用する

を完全に制御する必要がある場合は、[`/run`](api-server.md) エンドポイントを使用します。
統合を行っているか、GCP 以外のイベント ソースを使用しています。有効にする
`--auto_create_session` セッションが自動的に作成されるようにする
イベントの到着時に `/run` を呼び出すために任意の HTTP クライアントを接続します。

```bash
adk api_server --auto_create_session path/to/your/agent
```

このパターンは、HTTP リクエストを実行できるあらゆるイベント ソースで機能します。

??? "例: 受信 Webhook の処理"

    次の [Cloud Run function](https://cloud.google.com/functions/docs/writing/write-event-driven-functions)
    外部サービス (GitHub など) から Webhook を受信し、
    それをエージェントに転送します。

    ```python
    import json
    import uuid

    import functions_framework
    import requests

    AGENT_URL = "https://my-agent-service-xxxxx.run.app"

    @functions_framework.http
    def handle_webhook(request):
        """Cloud Run function that receives webhooks and forwards to the agent."""
        payload = request.get_json(silent=True) or {}

        requests.post(
            f"{AGENT_URL}/apps/my_agent/run",
            json={
                "app_name": "my_agent",
                "user_id": payload.get("account", "webhook-caller"),
                "session_id": str(uuid.uuid4()),
                "new_message": {
                    "role": "user",
                    "parts": [{"text": json.dumps(payload)}],
                },
            },
        )

        return ("ok", 200)
    ```

??? "例：curlでイベントを送信する"

    ```bash
    curl -X POST http://localhost:8000/apps/my_agent/run \
      -H "Content-Type: application/json" \
      -d '{
        "app_name": "my_agent",
        "user_id": "webhook-caller",
        "session_id": "session-123",
        "new_message": {
          "role": "user",
          "parts": [{"text": "{\"order_id\": \"1234\", \"status\": \"new\"}"}]
        }
      }'
    ```

## トリガーエンドポイントの使用

イベント ソースが Pub/Sub または Eventarc であり、
ADK にペイロードの解析、セッションの作成、同時実行性、および再試行を処理させたい。

### イベントの処理方法

Pub/Sub と Eventarc は、イベントを HTTP POST リクエストとしてエージェントに配信します。
トリガー エンドポイントがイベントを受信すると、次の処理が行われます。

1. **ソース形式 (Pub/Sub プッシュ メッセージ) に従って **リクエストを解析します**
   またはクラウドイベント)。
2. **ペイロードをデコードします。** Base64 でエンコードされたメッセージ データがデコードされ、
   可能、JSON として解析されます。
3. 生成された UUID を使用して **セッションを自動的に作成**します。 `/run`とは異なります
   エンドポイントの場合、`--auto_create_session` — トリガーを有効にする必要はありません
   エンドポイントは常にイベントごとに新しいセッションを作成します。
4. **デコードされたイベントをユーザー メッセージとして使用してエージェントを実行します**。
5. **ステータス コードを返します。** `200` 応答は、Pub/Sub または Eventarc に次のことを伝えます。
   イベントは正常に処理されました。 `500` 応答は失敗を示します。
   イベント ソースは、再試行ポリシーに基づいて配信を再試行します。

### サポートされているソース

|出典 |エンドポイント |説明 |
| :----- | :------- | :---------- |
| **パブ/サブ** | `/apps/{app_name}/trigger/pubsub` | [Pub/Sub push subscription](https://cloud.google.com/pubsub/docs/push) からメッセージを受信します。 |
| **イヴェンターク** | `/apps/{app_name}/trigger/eventarc` | [Eventarc](https://cloud.google.com/eventarc) ([Standard](https://cloud.google.com/eventarc/standard/docs/overview) または [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview)) によって配信された [CloudEvents](https://cloudevents.io/) を受信し、構造化コンテンツ モードとバイナリ コンテンツ モードの両方をサポートします。 |

### エージェントの例

=== "Python"
    次のエージェントは、トリガー エンドポイントからのイベントを処理します。それは、
    `parse_event` イベントデータと属性を抽出して分析するツール
    内容。

    ???+ "エージェントコード(`event_processing_agent/agent.py`)"

        ```python
        --8<-- "examples/python/snippets/runtime/triggers/event_processing_agent/agent.py:event_processor"
        ```

=== "Go"
    次のエージェントは、トリガー エンドポイントからのイベントを処理します。イベントデータと属性を抽出し、内容を解析します。

    ???+ "エージェントコード(`event_processing_agent.go`)"

        ```go
        --8<-- "examples/go/snippets/runtime/triggers/event_processing_agent.go:event_processor"
        ```

### トリガーを有効にする

=== "Python"

    トリガー エンドポイントはデフォルトでは無効になっています。それらを有効にするには、
    `--trigger_sources` フラグ:

    ```shell
    adk api_server --trigger_sources "pubsub,eventarc" path/to/your/agent
    ```

    運用環境の場合、トリガーをプログラムで有効にできます。
    カスタム FastAPI エントリ ポイント:

    ???+ "展開エントリ ポイント (`main.py`)"

        === "Python"
            ```python
            --8<-- "examples/python/snippets/runtime/triggers/main.py:triggers"
            ```

=== "Go"

    トリガー エンドポイントはデフォルトでは無効になっています。それらを有効にするには、
    対応するトリガーフラグ:

    ```shell
    go run agent.go web api pubsub eventarc
    ```

### ローカルで試してみる

**1.トリガーを有効にしてサーバーを起動します:**

=== "Python"

    ```bash
    adk api_server --trigger_sources "pubsub" event_processing_agent
    ```

=== "Go"

    ```bash
    go run event_processing_agent.go web api pubsub
    ```

**2.テスト イベントを送信します:**

```bash
curl -X POST http://localhost:8000/apps/event_processing_agent/trigger/pubsub \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "data": "eyJvcmRlcl9pZCI6ICIxMjM0IiwgInN0YXR1cyI6ICJuZXcifQ==",
      "attributes": {"source": "orders-service"}
    },
    "subscription": "projects/my-project/subscriptions/orders-sub"
  }'
```

Base64 値は `{"order_id": "1234", "status": "new"}` にデコードされます。

成功した応答:

```json
{"status": "success"}
```

## トリガーソース

### パラメータのマッピング

`/run` エンドポイントでは、`app_name`、`user_id`、および
`session_id`。トリガー エンドポイントはこれらを自動的に取得します。

|パラメータ |出典 |
| :-------- | :----- |
| `app_name` | URL パスから抽出 (`/apps/{app_name}/trigger/...`) |
| `session_id` |イベントごとに自動生成される UUID |
| `user_id` | Pub/Sub: `subscription` フィールド。 Eventarc: `source` または `ce-source` ヘッダー。 |

### メッセージ形式

すべてのトリガー エンドポイントは、受信イベントを一貫した JSON に正規化します。
ユーザーメッセージとしてエージェントに渡す前に構造を変更します。

```json
{
  "data": "<decoded event payload>",
  "attributes": {"key": "value"}
}
```

- **`data`**: デコードされたイベント ペイロード。元データがJSONの場合は、
  構造化オブジェクトに解析されます。それ以外の場合は、プレーン文字列として渡されます。
- **`attributes`**: イベント ソースからのキーと値のメタデータ (Pub/Sub など)
  メッセージ属性または CloudEvents ヘッダー (`ce-type`、`ce-source` など)。

エージェントはこの JSON 文字列を入力メッセージとして受け取り、それを解析して次のようにすることができます。
データと属性を抽出します。

### パブリッシュ/サブスクライブ

Pub/Sub トリガー エンドポイントは、
[Pub/Sub push subscription](https://cloud.google.com/pubsub/docs/push)。使ってください
アプリケーションまたはサービスがトピックにメッセージをパブリッシュするとき、たとえば次のようになります。

- サポート ポータルは、トリアージとルーティングのために受信したチケットを公開します。
- コンテンツ パイプラインは、分類またはモデレーションのためにドキュメントを送信します。
- 監視サービスは、自動分析のためにアラートを発行します。

#### リクエスト形式

Pub/Sub プッシュ サブスクリプションは、次の形式でリクエストを送信します。

```json
{
  "message": {
    "data": "eyJvcmRlcl9pZCI6ICIxMjM0IiwgInN0YXR1cyI6ICJuZXcifQ==",
    "attributes": {"source": "orders-service"},
    "messageId": "123456789",
    "publishTime": "2026-04-08T12:00:00Z"
  },
  "subscription": "projects/my-project/subscriptions/my-sub"
}
```

`data` フィールドは Base64 でエンコードされます。トリガーエンドポイントがそれをデコードします
自動的に。

#### 応答

| HTTP ステータス |意味 |
| :---------- | :------ |
| **200** |イベントは正常に処理されました。 Pub/Sub はメッセージを確認します。 |
| **400** |無効なリクエスト (不正な Base64 エンコーディング)。メッセージは再試行されません。 |
| **500** |処理が失敗しました (一時的または非一時的なエージェント エラー)。 Pub/Sub は、[retry policy](https://cloud.google.com/pubsub/docs/handling-failures) に基づいて配信を再試行します。繰り返し失敗するメッセージをキャッチするように [dead-letter queue](https://cloud.google.com/pubsub/docs/dead-letter-topics) を構成します。 |

### イヴェンターク

Eventarc トリガー エンドポイント プロセス
[CloudEvents](https://cloud.google.com/eventarc/docs/cloudevents) によって配信されました
[Eventarc](https://cloud.google.com/eventarc)、両方
[Standard](https://cloud.google.com/eventarc/standard/docs/overview)と
[Advanced](https://cloud.google.com/eventarc/advanced/docs/overview) エディション。
これを使用して、Google Cloud 全体のイベントに対応します。たとえば、次のようになります。

- ファイルが [Cloud Storage](https://cloud.google.com/storage) にアップロードされます (文書の分類、要約、またはデータの抽出)。
- レコードが [BigQuery](https://cloud.google.com/bigquery) に書き込まれます (異常検出の実行またはアラートの生成)。
- [Audit Log](https://cloud.google.com/logging/docs/audit) エントリが作成されます (ポリシー違反または不審なアクティビティにフラグを立てます)。

両方のコンテンツ モードがサポートされています。

- **バイナリ コンテンツ モード** (Eventarc のデフォルト): CloudEvents 属性が送信されます
  `ce-*` HTTP ヘッダーとして保存され、本文にはイベント データ (通常は
  Pub/Sub メッセージ ラッパー)。
- **構造化コンテンツ モード**: すべての CloudEvents 属性とデータは
  JSON本体。

??? "curlでテストする（構造化モード）"

    ```bash
    curl -X POST http://localhost:8000/apps/my_agent/trigger/eventarc \
      -H "Content-Type: application/json" \
      -d '{
        "specversion": "1.0",
        "type": "google.cloud.storage.object.v1.finalized",
        "source": "//storage.googleapis.com/projects/my-project",
        "id": "event-123",
        "data": {
          "bucket": "my-bucket",
          "name": "uploads/document.pdf"
        }
      }'
    ```

??? "curlでテスト（バイナリモード）"

    ```bash
    curl -X POST http://localhost:8000/apps/my_agent/trigger/eventarc \
      -H "Content-Type: application/json" \
      -H "ce-type: google.cloud.storage.object.v1.finalized" \
      -H "ce-source: //storage.googleapis.com/projects/my-project" \
      -H "ce-id: event-456" \
      -H "ce-specversion: 1.0" \
      -d '{
        "message": {
          "data": "eyJidWNrZXQiOiAibXktYnVja2V0IiwgIm5hbWUiOiAiZG9jLnBkZiJ9",
          "attributes": {"eventType": "OBJECT_FINALIZE"}
        },
        "subscription": "projects/my-project/subscriptions/eventarc-sub"
      }'
    ```

#### 応答

| HTTP ステータス |意味 |
| :---------- | :------ |
| **200** |イベントは正常に処理されました。 Eventarc は配送を確認します。 |
| **500** |処理に失敗しました。 Eventarc は、再試行ポリシーに基づいて配信を再試行します。 |

## 構成

### 同時実行制御

トリガーエンドポイントはセマフォを使用して同時エージェントの数を制限します
呼び出し。これにより、エージェントが LLM モデルの割り当てを超過するのを防ぎます。
イベントのバースト中に。

=== "Python"

    |設定 |デフォルト |環境変数 |
    | :------ | :------ | :------------------- |
    |最大同時呼び出し数 | 10 | `ADK_TRIGGER_MAX_CONCURRENT` |

=== "Go"

    |設定 |デフォルト |旗 |
    | :------ | :------ | :------------------- |
    |最大同時呼び出し数 | 10 | `--trigger_max_concurrent_runs` |

同時実行制限に達すると、受信リクエストはキューに入れられて処理されます。
スロットが利用可能になるにつれて。同時実行制御はプロセスごとに行われます。デプロイする場合
複数の Cloud Run インスタンス。各インスタンスは独自の独立したインスタンスを維持します。
セマフォ。

=== "Python"

    ```bash
    # Allow up to 5 concurrent agent invocations
    export ADK_TRIGGER_MAX_CONCURRENT=5
    ```

=== "Go"

    ```bash
    go run event_processing_agent.go web api pubsub --trigger_max_concurrent_runs=5
    ```

### バックオフによる自動再試行

トリガーエンドポイントには、次のような一時的なエラーに対する再試行ロジックが組み込まれています。
`429 RESOURCE_EXHAUSTED` の応答。一時的なエラーが検出されると、
リクエストは指数バックオフとジッターを伴って再試行されます。

=== "Python"

    |設定 |デフォルト |環境変数 |
    | :------ | :------ | :------------------- |
    |最大再試行回数 | 3 | `ADK_TRIGGER_MAX_RETRIES` |
    |ベース バックオフ遅延 | 1.0秒 | `ADK_TRIGGER_RETRY_BASE_DELAY` |
    |最大バックオフ遅延 | 30.0秒 | `ADK_TRIGGER_RETRY_MAX_DELAY` |

=== "Go"

    |設定 |デフォルト |旗 |
    | :------ | :------ | :------------------- |
    |最大再試行回数 | 3 | `--trigger_max_retries` |
    |ベース バックオフ遅延 | 1.0秒 | `--trigger_base_delay` |
    |最大バックオフ遅延 | 30.0秒 | `--trigger_max_delay` |

すべての再試行が完了すると、エンドポイントは HTTP 500 を返し、シグナルを送信します。
Pub/Sub または Eventarc を使用して、より高いレベルで配信を再試行します。
非一時的なエラーは、再試行せずにすぐに失敗します。

### エラー処理と災害復旧

トリガーベースのワークロードの災害復旧は、トリガーによって処理されます。
ADK ではなくサービス:

- エージェントがクラッシュするかエラーを返した場合、Pub/Sub または Eventarc は機能しません。
  確認応答を受信し、メッセージを自動的に再配信します。
- 最大再試行回数に達すると、未処理のメッセージは次の場所に移動します。
  [dead-letter queue (DLQ)](https://cloud.google.com/pubsub/docs/dead-letter-topics)
  構成されている場合。
- 再配信のたびに新しいセッションが作成されます。トリガーのワークロードはステートレスです
  設計上。

### タイムアウトに関する考慮事項

すべてのトリガー エンドポイントは同期的に処理し、エージェントが次の処理を行うのを待ちます。
応答を返す前に完了してください。これは設計によるもので、HTTP を維持します。
リクエストアライブにより、ホスティングインフラストラクチャが
エージェントがまだ動作している間にプロセスを実行してください。同期応答コード
(200 または 500) により、Pub/Sub と Eventarc が正しく認識できるようになります。
成功するか、再試行をトリガーします。

最大処理時間はアップストリーム サービスによって制御されます。

|サービス |最大タイムアウト |
| :------ | :---------- |
| Pub/Sub プッシュ | 10 分 (期限確認) |
|イブンターク | 10 分 ([Standard](https://cloud.google.com/eventarc/standard/docs/overview) はトランスポートとして Pub/Sub を使用します。[Advanced](https://cloud.google.com/eventarc/advanced/docs/overview) はパイプライン経由で配信します) |

トリガー エンドポイントは、10 分以内に完了するエージェント向けに設計されています。
これは、個々のイベントの処理、検証の実行、
ドキュメントを分類し、結果をダウンストリーム サービスに書き込みます。

!!! warning "長期にわたって実行されるエージェント"
    トリガー エンドポイントは、10 を超える時間がかかるエージェントには適していません。
    完了までに数分。長時間実行されるワークロードの場合は、次を使用します。
    [Pub/Sub pull subscriptions](https://cloud.google.com/pubsub/docs/pull)、
    [Cloud Run Jobs](https://cloud.google.com/run/docs/create-jobs)、または
    代わりにワーカー プール アーキテクチャを使用します。

### セッションのライフサイクル

セッションは、他のすべての ADK エントリ ポイントと同じパターンに従います。彼らは
設定されたものを通じて作成されました
[`SessionService`](../sessions/session/index.md)。デフォルトでは、ADK は
`InMemorySessionService`、トリガーセッションを一時的にします: ごとに作成されます
イベントが発生し、処理後に破棄されます。

永続的な `SessionService` (たとえば、`DatabaseSessionService`) を構成する場合、
トリガーセッションは自動的に保存されます。これは監査に役立ちます。
イベント駆動型ワークロードのデバッグと事後分析。

## デプロイ

以下の例では、[Cloud Run](https://cloud.google.com/run) を
導入対象。現在、Cloud Run が推奨プラットフォームです。
トリガーエンドポイントを備えたアンビエントエージェントを展開します。

!!! note "認証とセキュリティ"
    トリガー エンドポイントは、ADK Web サーバー内の標準 HTTP ルートです。
    認証とセキュリティは展開レベルで適用されます。
    他の ADK エンドポイントと同じです。認証を有効にして導入した場合
    (推奨)、すべてのエンドポイントに有効な認証情報が必要です。 GCP サービス
    [service account](https://cloud.google.com/iam/docs/service-accounts) を使用して認証する
    アイデンティティ。詳細については、各サービスのドキュメントを参照してください。

=== "Python"

    を使用してトリガーを有効にしてエージェントを Cloud Run にデプロイします。
    `--trigger_sources` フラグ:

    ```bash
    adk deploy cloud_run \
      --project=$GOOGLE_CLOUD_PROJECT \
      --region=$GOOGLE_CLOUD_LOCATION \
      --trigger_sources="pubsub,eventarc" \
      path/to/your/agent
    ```

=== "Go"

    対応するトリガー フラグを使用してトリガーを有効にして、エージェントを Cloud Run にデプロイします（すべての設定にはトリガー タイプの接頭辞が付いています）

    ```bash
    adk deploy cloud_run \
      --project=$GOOGLE_CLOUD_PROJECT \
      --region=$GOOGLE_CLOUD_LOCATION \
      --pubsub \
      --pubsub_max_concurrent_runs=5 \
      --eventarc \
      --eventarc_max_concurrent_runs=5
    ```

導入後、適切な GCP インフラストラクチャをエージェントのインフラストラクチャに接続します。
トリガーエンドポイント:

- **Pub/Sub**: [push subscription](https://cloud.google.com/pubsub/docs/push) を作成します
  `/apps/{app_name}/trigger/pubsub` を指します。
- **Eventarc**: [Eventarc Standard trigger](https://docs.cloud.google.com/eventarc/standard/docs/event-providers-targets) を作成します
  または [Eventarc Advanced pipeline](https://cloud.google.com/eventarc/advanced/docs/overview)
  `/apps/{app_name}/trigger/eventarc` にルーティングします。
- **クラウド スケジューラ**: [scheduler job](https://cloud.google.com/scheduler/docs/creating) を作成します
  cron スケジュールで Pub/Sub トピックに公開します。

完全な展開については、[Deploy to Cloud Run](../deploy/cloud-run.md) を参照してください。
指示。

## 次は何ですか?

- [deploy your agent to Cloud Run](../deploy/cloud-run.md) の方法を学ぶ
- インタラクティブなエージェント呼び出しについては、[API server endpoints](api-server.md) を参照してください。
- [Pub/Sub toolset](../integrations/pubsub.md) を使用して、エージェントにメッセージのパブリッシュとプルの機能を与えます
