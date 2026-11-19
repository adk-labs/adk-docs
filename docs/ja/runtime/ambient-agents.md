# アンビエントエージェントでアクションをトリガーする

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.29.0</span><span class="lst-go">Go v1.1.0</span>
</div>

エージェントワークフローを実行するとき、人間の入力を待つのではなく、イベントや新しいデータの到着に応じてワークフローを起動したい場合があります。ADK エージェントには、イベントに応答して処理を実行するトリガーを構成できます。これを *アンビエントエージェント* と呼びます。これらのエージェントはバックグラウンドプロセスとして実行され、人間の介入なしにデータの処理、イベントの監視、非同期での応答を行えます。アンビエントエージェントは次の用途に活用できます。

- **クラウドイベントへの反応:** [Cloud Storage](https://cloud.google.com/storage) にファイルがアップロードされたときの処理、データベースの変更への応答、監査ログエントリの処理などを行います。
- **キューからのメッセージ処理:** 受信したサポートチケットの分析、コンテンツのモデレーション、ドキュメントの分類、アイテム到着時の QA の実行などを行います。
- **スケジュール実行:** 日次レポートの生成、定期的な監視チェックの実行、一定間隔でのバッチジョブ処理などを行います。
- **インフラストラクチャの監視:** インフラストラクチャ全体の継続的なイベントストリームに反応し、変更に対して自律的に対処します。

## アンビエントエージェントから結果を取得する

アンビエントエージェントは人間の介入なしで実行されるため、その出力を通知チャネルにルーティングする必要があります。一般的なパターンは次のとおりです。

- **[構造化ロギング（Structured logging）](../observability/logging.md):** JSON ログを出力し、メール、Slack、PagerDuty 経由で通知する [Cloud Monitoring](https://cloud.google.com/monitoring/support/notification-options) アラートを構成します。
- **[Pub/Sub](https://cloud.google.com/pubsub):** ダウンストリームのサービスが利用できるように、結果をトピックにパブリッシュ（発行）します。
- **[Application Integration](https://cloud.google.com/application-integration/docs/listen-pub-sub-topic-send-email):** エージェントの出力をメール、Jira、その他のシステムにルーティングします。

## アンビエントエージェントを構築する方法

ADK は 2 つのアプローチを提供します。

| | [`/run`](api-server.md) | トリガーエンドポイント |
| :--- | :--- | :--- |
| **イベントソース** | 任意（Pub/Sub、Webhook、cron、カスタムサービス） | [Cloud Pub/Sub](https://cloud.google.com/pubsub)、[Eventarc](https://cloud.google.com/eventarc)（[Standard](https://cloud.google.com/eventarc/standard/docs/overview) および [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview)） |
| **ペイロード解析** | 開発者側で実装 | 自動（Base64 デコード、CloudEvent 解析） |
| **セッションの作成** | `--auto_create_session` を有効化 | 自動（イベントごとに 1 つ） |
| **セッションストレージ** | 構成済みの [`SessionService`](../sessions/session/index.md) | 構成済みの [`SessionService`](../sessions/session/index.md) |
| **同時実行制御** | 開発者側で実装 | 上限を設定可能な組み込みセマフォ |
| **再試行ロジック** | 開発者側で実装 | 一時的なエラーに対するジッター付き指数バックオフ |
| **適した用途** | カスタム統合、Google Cloud 以外のソース | Google Cloud ネイティブのイベント駆動型ワークロード |

## `/run` を使用する

統合処理を完全に制御したい場合や、Google Cloud 以外のイベントソースを扱う場合は、[`/run`](api-server.md) エンドポイントを使用します。セッションが自動的に作成されるように `--auto_create_session` を有効にし、イベント到着時に任意の HTTP クライアントから `/run` を呼び出します。

```bash
adk api_server --auto_create_session path/to/your/agent
```

このパターンは、HTTP リクエストを送信できるあらゆるイベントソースで利用できます。

??? "例: 受信 Webhook の処理"

    次の [Cloud Run function](https://cloud.google.com/functions/docs/writing/write-event-driven-functions) は、外部サービス（GitHub など）から Webhook を受信し、エージェントに転送します。

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

イベントソースが Pub/Sub または Eventarc であり、ペイロードの解析、セッションの作成、同時実行制御、再試行を ADK に任せたい場合は、トリガーエンドポイントを使用します。

### イベントの処理方法

Pub/Sub と Eventarc は、イベントを HTTP POST リクエストとしてエージェントに配信します。トリガーエンドポイントがイベントを受信すると、次の処理が行われます。

1. **リクエストの解析:** ソース形式（Pub/Sub push メッセージまたは CloudEvent）に従ってリクエストを解析します。
2. **ペイロードのデコード:** Base64 エンコードされたメッセージデータをデコードし、可能な場合は JSON として解析します。
3. **セッションの自動作成:** 生成された UUID を使用してセッションを自動作成します。`/run` エンドポイントとは異なり、`--auto_create_session` を有効にする必要はありません。トリガーエンドポイントは常にイベントごとに新しいセッションを作成します。
4. **エージェントの実行:** デコードされたイベントをユーザーメッセージとしてエージェントを実行します。
5. **ステータスコードの返却:** `200` レスポンスは、イベントが正常に処理されたことを Pub/Sub または Eventarc に伝えます。`500` レスポンスは処理失敗を示し、イベントソースは再試行ポリシーに基づいて配信を再試行します。

### サポートされているソース

| ソース | エンドポイント | 説明 |
| :----- | :------- | :---------- |
| **Pub/Sub** | `/apps/{app_name}/trigger/pubsub` | [Pub/Sub push サブスクリプション](https://cloud.google.com/pubsub/docs/push)からメッセージを受信します。 |
| **Eventarc** | `/apps/{app_name}/trigger/eventarc` | [Eventarc](https://cloud.google.com/eventarc)（[Standard](https://cloud.google.com/eventarc/standard/docs/overview) または [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview)）によって配信された [CloudEvents](https://cloudevents.io/) を受信し、構造化コンテンツモードとバイナリコンテンツモードの両方をサポートします。 |

### エージェントの例

=== "Python"
    次のエージェントは、トリガーエンドポイントからのイベントを処理します。`parse_event` ツールを使用してイベントデータと属性を抽出し、その内容を分析します。

    ???+ "エージェントコード(`event_processing_agent/agent.py`)"

        ```python
        --8<-- "examples/python/snippets/runtime/triggers/event_processing_agent/agent.py:event_processor"
        ```

=== "Go"
    次のエージェントは、トリガーエンドポイントからのイベントを処理します。イベントデータと属性を抽出し、内容を分析します。

    ???+ "エージェントコード(`event_processing_agent.go`)"

        ```go
        --8<-- "examples/go/snippets/runtime/triggers/event_processing_agent.go:event_processor"
        ```

### トリガーを有効にする

=== "Python"

    トリガーエンドポイントはデフォルトでは無効になっています。有効にするには `--trigger_sources` フラグを使用します:

    ```shell
    adk api_server --trigger_sources "pubsub,eventarc" path/to/your/agent
    ```

    本番環境へのデプロイでは、カスタム FastAPI エントリポイントでプログラムからトリガーを有効にできます:

    ???+ "デプロイ用エントリポイント (`main.py`)"

        === "Python"
            ```python
            --8<-- "examples/python/snippets/runtime/triggers/main.py:triggers"
            ```

=== "Go"

    トリガーエンドポイントはデフォルトでは無効になっています。有効にするには対応するトリガーフラグを指定します:

    ```shell
    go run agent.go web api pubsub eventarc
    ```

### ローカルで試してみる

**1. トリガーを有効にしてサーバーを起動します:**

=== "Python"

    ```bash
    adk api_server --trigger_sources "pubsub" event_processing_agent
    ```

=== "Go"

    ```bash
    go run event_processing_agent.go web api pubsub
    ```

    Go サーバーの場合は、次のリクエストの URL として `http://localhost:8080/api/apps/event_processor/trigger/pubsub` を使用してください。

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

`/run` エンドポイントでは `app_name`、`user_id`、および `session_id` を指定する必要がありますが、トリガーエンドポイントはこれらを自動的に導出します。

| パラメータ | 取得元 |
| :-------- | :----- |
| `app_name` | URL パス（`/apps/{app_name}/trigger/...`）から抽出 |
| `session_id` | イベントごとに自動生成される UUID |
| `user_id` | Pub/Sub: `subscription` フィールド。Eventarc: `source` または `ce-source` ヘッダー。 |

### メッセージ形式

すべてのトリガーエンドポイントは、受信イベントを一貫した JSON 構造に正規化してから、ユーザーメッセージとしてエージェントに渡します。

```json
{
  "data": "<decoded event payload>",
  "attributes": {"key": "value"}
}
```

- **`data`**: デコードされたイベントペイロード。元データが JSON の場合は構造化オブジェクトに解析され、それ以外の場合はプレーン文字列として渡されます。
- **`attributes`**: イベントソースからのキー・バリュー形式のメタデータ（Pub/Sub メッセージ属性や、`ce-type`、`ce-source` などの CloudEvents ヘッダーなど）。

エージェントはこの JSON 文字列を入力メッセージとして受け取り、解析してデータと属性を抽出できます。

### Pub/Sub

Pub/Sub トリガーエンドポイントは、[Pub/Sub push サブスクリプション](https://cloud.google.com/pubsub/docs/push)からのメッセージを処理します。アプリケーションやサービスがトピックにメッセージをパブリッシュ（発行）する場合に使用します。例:

- サポートポータルが、トリアージとルーティングのために受信チケットをパブリッシュする。
- コンテンツパイプラインが、分類やモデレーションのためにドキュメントを送信する。
- 監視サービスが、自動分析のためにアラートをパブリッシュする。

#### リクエスト形式

Pub/Sub push サブスクリプションは次の形式でリクエストを送信します。

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

`data` フィールドは Base64 エンコードされています。トリガーエンドポイントはこれを自動的にデコードします。

#### レスポンス

| HTTP ステータス | 意味 |
| :---------- | :------ |
| **200** | イベントが正常に処理されました。Pub/Sub はメッセージを確認応答（ack）します。 |
| **400** | 無効なリクエスト（不正な Base64 エンコーディング）。メッセージは再試行されません。 |
| **500** | 処理に失敗しました（一時的または永続的なエージェントエラー）。Pub/Sub は[再試行ポリシー](https://cloud.google.com/pubsub/docs/handling-failures)に基づいて配信を再試行します。繰り返し失敗するメッセージを捕捉するために[デッドレターキュー](https://cloud.google.com/pubsub/docs/dead-letter-topics)を構成してください。 |

### Eventarc

Eventarc トリガーエンドポイントは、[Eventarc](https://cloud.google.com/eventarc)（[Standard](https://cloud.google.com/eventarc/standard/docs/overview) と [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview) の両エディション）によって配信される [CloudEvents](https://cloud.google.com/eventarc/docs/cloudevents) を処理します。Google Cloud 全体のイベントに応答するために使用します。例:

- [Cloud Storage](https://cloud.google.com/storage) にファイルがアップロードされたとき（ドキュメントの分類、要約、データ抽出）。
- [BigQuery](https://cloud.google.com/bigquery) にレコードが書き込まれたとき（異常検知の実行やアラート生成）。
- [監査ログ（Audit Log）](https://cloud.google.com/logging/docs/audit)のエントリが作成されたとき（ポリシー違反や不審なアクティビティの検出）。

両方のコンテンツモードがサポートされています。

- **バイナリコンテンツモード**（Eventarc のデフォルト）: CloudEvents 属性は `ce-*` HTTP ヘッダーとして送信され、ボディにはイベントデータ（通常は Pub/Sub メッセージラッパー）が含まれます。
- **構造化コンテンツモード**: すべての CloudEvents 属性とデータが JSON ボディに含まれます。

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

#### レスポンス

| HTTP ステータス | 意味 |
| :---------- | :------ |
| **200** | イベントが正常に処理されました。Eventarc は配信を確認応答（ack）します。 |
| **500** | 処理に失敗しました。Eventarc は再試行ポリシーに基づいて配信を再試行します。 |

## 構成

### 同時実行制御

トリガーエンドポイントはセマフォを使用して、同時に実行されるエージェント呼び出しの数を制限します。これにより、イベントのバースト発生時にエージェントが LLM モデルのクォータ（割り当て上限）を超過するのを防ぎます。

=== "Python"

    | 設定 | デフォルト | 環境変数 |
    | :------ | :------ | :------------------- |
    | 最大同時呼び出し数 | 10 | `ADK_TRIGGER_MAX_CONCURRENT` |

=== "Go"

    | 設定 | デフォルト | フラグ |
    | :------ | :------ | :------------------- |
    | 最大同時呼び出し数 | 100 | `--trigger_max_concurrent_runs` |

    デフォルトでは、ADK Go は最大 100 件の同時呼び出しを許可し、ADK Python は 10 件を許可します。

    !!! note "ADK Go における Pub/Sub トリガーの同時実行性"

        ADK Go v2.3.0 から v2.5.0 では、Pub/Sub トリガーに `--trigger_max_concurrent_runs` が適用されないため、Pub/Sub イベントは同時実行制限なしで実行されます。Pub/Sub の同時実行数を制限するには、ADK Go v2.6.0 以降を使用してください。

同時実行数の上限に達すると、受信リクエストはキューに入れられ、スロットが空き次第順次処理されます。同時実行制御はプロセス単位で行われます。複数の Cloud Run インスタンスをデプロイした場合、各インスタンスがそれぞれ独立したセマフォを保持します。

=== "Python"

    ```bash
    # Allow up to 5 concurrent agent invocations
    export ADK_TRIGGER_MAX_CONCURRENT=5
    ```

=== "Go"

    ```bash
    go run event_processing_agent.go web api eventarc --trigger_max_concurrent_runs=5
    ```

### バックオフによる自動再試行

トリガーエンドポイントには、`429 RESOURCE_EXHAUSTED` レスポンスなどの一時的なエラーに対する再試行ロジックが組み込まれています。一時的なエラーが検出されると、ジッター付きの指数バックオフでリクエストが再試行されます。

=== "Python"

    | 設定 | デフォルト | 環境変数 |
    | :------ | :------ | :------------------- |
    | 最大再試行回数 | 3 | `ADK_TRIGGER_MAX_RETRIES` |
    | ベースバックオフ遅延 | 1.0s | `ADK_TRIGGER_RETRY_BASE_DELAY` |
    | 最大バックオフ遅延 | 30.0s | `ADK_TRIGGER_RETRY_MAX_DELAY` |

=== "Go"

    | 設定 | デフォルト | フラグ |
    | :------ | :------ | :------------------- |
    | 最大再試行回数 | 3 | `--trigger_max_retries` |
    | ベースバックオフ遅延 | 1.0s | `--trigger_base_delay` |
    | 最大バックオフ遅延 | 10.0s | `--trigger_max_delay` |

    デフォルトでは、ADK Go はバックオフ遅延の上限を 10 秒とし、ADK Python は 30 秒とします。

すべての再試行を使い果たすと、エンドポイントは HTTP 500 を返し、上位レベルで配信を再試行するよう Pub/Sub または Eventarc に通知します。一時的でないエラーは再試行されず、即座に失敗します。

### エラー処理と障害復旧

トリガーベースのワークロードにおける障害復旧は、ADK ではなくトリガー元のサービスによって処理されます。

- エージェントがクラッシュするかエラーを返した場合、Pub/Sub または Eventarc は確認応答（ack）を受信しないため、メッセージを自動的に再配信します。
- 最大再試行回数に達すると、未処理のメッセージは（構成されている場合）[デッドレターキュー（DLQ）](https://cloud.google.com/pubsub/docs/dead-letter-topics)に移動します。
- 再配信のたびに新しいセッションが作成されます。トリガーワークロードは設計上ステートレスです。

### タイムアウトに関する考慮事項

すべてのトリガーエンドポイントは同期的に処理を行い、エージェントの実行が完了してからレスポンスを返します。これは意図的な設計です。HTTP リクエストを接続状態に保つことで、エージェントの実行中にホスティングインフラストラクチャがプロセスを終了してしまうのを防ぎます。また、同期的なレスポンスコード（200 または 500）によって、Pub/Sub や Eventarc が処理成功を正しく認識したり再試行をトリガーしたりできるようになります。

最大処理時間はアップストリームのサービスによって決まります。

| サービス | 最大タイムアウト |
| :------ | :---------- |
| Pub/Sub push | 10 分（確認応答期限） |
| Eventarc | 10 分（[Standard](https://cloud.google.com/eventarc/standard/docs/overview) はトランスポートとして Pub/Sub を使用、[Advanced](https://cloud.google.com/eventarc/advanced/docs/overview) はパイプライン経由で配信） |

トリガーエンドポイントは、10 分以内に完了するエージェント向けに設計されています。個々のイベントの処理、検証の実行、ドキュメントの分類、ダウンストリームサービスへの結果の書き込みなどに適しています。

!!! warning "長時間実行されるエージェント"
    トリガーエンドポイントは、完了までに 10 分以上かかるエージェントには適していません。長時間実行されるワークロードには、代わりに [Pub/Sub pull サブスクリプション](https://cloud.google.com/pubsub/docs/pull)、[Cloud Run ジョブ](https://cloud.google.com/run/docs/create-jobs)、またはワーカープールアーキテクチャを使用してください。

### セッションのライフサイクル

セッションは、他のすべての ADK エントリポイントと同じパターンに従い、構成された [`SessionService`](../sessions/session/index.md) を通じて作成されます。デフォルトでは ADK は `InMemorySessionService` を使用するため、トリガーセッションはエフェメラル（一時的）となり、イベントごとに作成されて処理完了後に破棄されます。

永続的な `SessionService`（`DatabaseSessionService` など）を構成すると、トリガーセッションは自動的に永続化されます。これはイベント駆動型ワークロードの監査、デバッグ、および事後分析に役立ちます。

## デプロイ

以下の例では、デプロイ先として [Cloud Run](https://cloud.google.com/run) を使用します。現在、トリガーエンドポイントを備えたアンビエントエージェントのデプロイには Cloud Run が推奨プラットフォームです。

!!! note "認証とセキュリティ"
    トリガーエンドポイントは ADK Web サーバー内の標準的な HTTP ルートです。認証とセキュリティは、他の ADK エンドポイントと同様にデプロイレベルで適用されます。認証を有効にしてデプロイした場合（推奨）、すべてのエンドポイントで有効な認証情報が必要です。Google Cloud サービスは[サービスアカウント](https://cloud.google.com/iam/docs/service-accounts) ID を使用して認証します。詳細については、各サービスのドキュメントを参照してください。

=== "Python"

    `--trigger_sources` フラグを使用してトリガーを有効にし、エージェントを Cloud Run にデプロイします:

    ```bash
    adk deploy cloud_run \
      --project=$GOOGLE_CLOUD_PROJECT \
      --region=$GOOGLE_CLOUD_LOCATION \
      --trigger_sources="pubsub,eventarc" \
      path/to/your/agent
    ```

=== "Go"

    `adkgo` CLI と各トリガーのフラグを使用して、エージェントを Cloud Run にデプロイします:

    ```bash
    ./adkgo deploy cloudrun \
      -p $GOOGLE_CLOUD_PROJECT \
      -r $GOOGLE_CLOUD_LOCATION \
      -s $SERVICE_NAME \
      -e ./main.go \
      --pubsub \
      --eventarc \
      --eventarc_max_concurrent_runs=5
    ```

    ADK Go は `/api` パスプレフィックス配下でトリガーエンドポイントを提供するため、push サブスクリプションと Eventarc トリガーは `/api/apps/{app_name}/trigger/pubsub` および `/api/apps/{app_name}/trigger/eventarc` を指すように設定してください。

デプロイ後、適切な Google Cloud インフラストラクチャをエージェントのトリガーエンドポイントに接続します:

- **Pub/Sub**: `/apps/{app_name}/trigger/pubsub` を指す [push サブスクリプション](https://cloud.google.com/pubsub/docs/push)を作成します。
- **Eventarc**: `/apps/{app_name}/trigger/eventarc` にルーティングする [Eventarc Standard トリガー](https://docs.cloud.google.com/eventarc/standard/docs/event-providers-targets)または [Eventarc Advanced パイプライン](https://cloud.google.com/eventarc/advanced/docs/overview)を作成します。
- **Cloud Scheduler**: cron スケジュールに従って Pub/Sub トピックにパブリッシュ（発行）する[スケジューラジョブ](https://cloud.google.com/scheduler/docs/creating)を作成します。

完全なデプロイ手順については、[Cloud Run へのデプロイ](../deploy/cloud-run.md)を参照してください。

## 次のステップ

- [エージェントを Cloud Run にデプロイする](../deploy/cloud-run.md)方法を学ぶ
- インタラクティブなエージェント呼び出しについては、[API サーバーエンドポイント](api-server.md)を参照する
- [Pub/Sub ツールセット](../integrations/pubsub.md)を使用して、エージェントにメッセージのパブリッシュおよび pull 機能を付与する
