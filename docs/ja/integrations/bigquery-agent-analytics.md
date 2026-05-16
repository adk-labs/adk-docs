---
catalog_title: BigQuery Agent Analytics Plugin
catalog_description: エージェントの動作分析とロギングのための詳細な分析機能を提供します
catalog_icon: /integrations/assets/bigquery.png
catalog_tags: ["observability", "google"]
---

# ADK 向け BigQuery Agent Analytics プラグイン

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.21.0</span>
</div>

!!! important "バージョン要件"

    auto-schema-upgrade、tool provenance 追跡、HITL イベントトレーシングを含む
    このドキュメントの機能を完全に利用するには、ADK Python バージョン
    1.26.0 以上を使用してください。

BigQuery Agent Analytics Plugin は、詳細なエージェント動作分析のための堅牢な
ソリューションを提供し、Agent Development Kit (ADK) を大きく拡張します。ADK
Plugin アーキテクチャと **BigQuery Storage Write API** を使って重要な運用
イベントを Google BigQuery テーブルへ直接キャプチャして記録し、デバッグ、
リアルタイム監視、包括的なオフライン性能評価のための高度な機能を提供します。

バージョン 1.26.0 では、**Auto Schema Upgrade**（既存テーブルへ新しい列を
安全に追加）、**Tool Provenance** 追跡（LOCAL、MCP、SUB_AGENT、A2A、
TRANSFER_AGENT、TRANSFER_A2A）、Human-in-the-Loop 連携のための **HITL Event
Tracing** が追加されました。バージョン 1.27.0 では、**Automatic View
Creation**（フラットでクエリしやすいイベントビューの生成）が追加されました。

!!! warning "BigQuery Storage Write API"

    この機能は有料サービスである **BigQuery Storage Write API** を使用します。
    コストについては [BigQuery
    ドキュメント](https://cloud.google.com/bigquery/pricing?e=48754805&hl=en#data-ingestion-pricing)
    を参照してください。

## ユースケース

- **エージェントワークフローのデバッグと分析:** 幅広い *プラグインライフサイクル
  イベント*（LLM 呼び出し、ツール使用）と *エージェントが生成したイベント*
  （ユーザー入力、モデル応答）を、明確に定義されたスキーマへキャプチャします。
- **高ボリューム分析とデバッグ:** ロギング処理は Storage Write API を使って
  非同期に実行されるため、高スループットと低レイテンシを両立できます。
- **マルチモーダル分析:** テキスト、画像、その他の modality を記録して分析します。
  大きなファイルは GCS にオフロードされ、Object Table 経由で BigQuery ML から
  利用できます。
- **分散トレーシング:** `trace_id`、`span_id` を使った OpenTelemetry スタイルの
  トレーシングを標準サポートし、エージェント実行フローを可視化できます。
- **Tool Provenance:** 各ツール呼び出しの出自（ローカル関数、MCP サーバー、
  サブエージェント、A2A リモートエージェント、transfer agent）を追跡します。
- **Human-in-the-Loop (HITL) トレーシング:** 資格情報要求、確認プロンプト、
  ユーザー入力要求のための専用イベントタイプを提供します。
- **クエリ可能なイベントビュー:** フラットなイベントタイプ別 BigQuery ビュー
  （例: `v_llm_request`, `v_tool_completed`）を自動作成し、JSON ペイロード
  データを展開して下流分析を簡素化します。

### キャプチャされるイベント概要

次の表は、プラグインが記録するすべてのイベントタイプを示します。詳しい
ペイロード例は [イベントタイプとペイロード](#event-types) を参照してください。
**View** 列は、[`create_views`](#configuration-options) が有効な場合（デフォルト）
に任意で作成される BigQuery ビューを示します。

| イベントタイプ | キャプチャされるタイミング | 主なペイロードフィールド | ビュー |
| --- | --- | --- | --- |
| `USER_MESSAGE_RECEIVED` | ユーザーメッセージが invocation に入るとき | テキスト要約 / content parts | `v_user_message_received` |
| `INVOCATION_STARTING` | invocation が開始するとき | *(共通列のみ)* | `v_invocation_starting` |
| `INVOCATION_COMPLETED` | invocation が終了するとき | *(共通列のみ)* | `v_invocation_completed` |
| `AGENT_STARTING` | エージェント実行が開始するとき | instruction 要約 | `v_agent_starting` |
| `AGENT_COMPLETED` | エージェント実行が終了するとき | レイテンシ | `v_agent_completed` |
| `LLM_REQUEST` | モデルリクエストが送信されるとき | モデル、プロンプト、設定、ツール | `v_llm_request` |
| `LLM_RESPONSE` | モデルレスポンスを受信するとき | 応答、使用トークン、キャッシュメタデータ、レイテンシ、TTFT | `v_llm_response` |
| `LLM_ERROR` | モデル呼び出しが失敗するとき | エラーメッセージ、レイテンシ | `v_llm_error` |
| `TOOL_STARTING` | ツール実行が開始するとき | ツール名、引数、出自 | `v_tool_starting` |
| `TOOL_COMPLETED` | ツールが成功するとき | ツール名、結果、出自、レイテンシ | `v_tool_completed` |
| `TOOL_ERROR` | ツールが失敗するとき | ツール名、引数、出自、エラー、レイテンシ | `v_tool_error` |
| `STATE_DELTA` | セッション状態が変化するとき | 状態 delta | `v_state_delta` |
| `HITL_CREDENTIAL_REQUEST` | 資格情報要求が発行されるとき | synthetic ツール名、引数 | `v_hitl_credential_request` |
| `HITL_CONFIRMATION_REQUEST` | 確認要求が発行されるとき | synthetic ツール名、引数 | `v_hitl_confirmation_request` |
| `HITL_INPUT_REQUEST` | ユーザー入力要求が発行されるとき | synthetic ツール名、引数 | `v_hitl_input_request` |
| `HITL_CREDENTIAL_REQUEST_COMPLETED` | ユーザーが資格情報応答を提供するとき | synthetic ツール名、結果 | *(ベーステーブルのみ)* |
| `HITL_CONFIRMATION_REQUEST_COMPLETED` | ユーザーが確認応答を提供するとき | synthetic ツール名、結果 | *(ベーステーブルのみ)* |
| `HITL_INPUT_REQUEST_COMPLETED` | ユーザーが入力応答を提供するとき | synthetic ツール名、結果 | *(ベーステーブルのみ)* |
| `A2A_INTERACTION` | リモート A2A 呼び出しが完了するとき | 応答、task ID、context ID、request/response | `v_a2a_interaction` |
| `AGENT_RESPONSE` | 最終エージェントレスポンスが yield されるとき | レスポンス(content)、source event ID/author/branch(attributes) | `v_agent_response` |

## クイックスタート

プラグインをエージェントの `App` オブジェクトに追加します。前提条件については
[前提条件](#prerequisites) を参照してください。

```python title="agent.py"
import os
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models.google_llm import Gemini
from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin

os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-gcp-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

plugin = BigQueryAgentAnalyticsPlugin(
    project_id="your-gcp-project-id",
    dataset_id="your-big-query-dataset-id",
)

root_agent = Agent(
    model=Gemini(model="gemini-flash-latest"),
    name='my_agent',
    instruction="You are a helpful assistant.",
)

app = App(
    name="my_agent",
    root_agent=root_agent,
    plugins=[plugin],
)
```

### エージェントの実行とテスト

チャットインターフェースでエージェントを実行し、`"tell me what you can do"` や
`"List datasets in my cloud project <your-gcp-project-id>"` のようなリクエストを
いくつか送ってプラグインをテストします。これらの操作により、Google Cloud
プロジェクトの BigQuery インスタンスに記録されるイベントが作成されます。
イベント処理後、[BigQuery Console](https://console.cloud.google.com/bigquery) で
次のクエリを使ってデータを確認できます。

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

??? example "GCS オフロード、OpenTelemetry、BigQuery ツールを含む完全な例"

    ```python title="my_bq_agent/agent.py"
    # my_bq_agent/agent.py
    import os
    import google.auth
    from google.adk.apps import App
    from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin, BigQueryLoggerConfig
    from google.adk.agents import Agent
    from google.adk.models.google_llm import Gemini
    from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig


    # --- OpenTelemetry TracerProvider Setup (Optional) ---
    # ADK includes OpenTelemetry as a core dependency.
    # Configuring a TracerProvider enables full distributed tracing
    # (populates trace_id, span_id with standard OTel identifiers).
    # If no TracerProvider is configured, the plugin falls back to internal
    # UUIDs for span correlation while still preserving the parent-child hierarchy.
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    trace.set_tracer_provider(TracerProvider())

    # --- Configuration ---
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
    DATASET_ID = os.environ.get("BIG_QUERY_DATASET_ID", "your-big-query-dataset-id")
    # GOOGLE_CLOUD_LOCATION must be a valid Agent Platform region (e.g., "us-central1").
    # BQ_LOCATION is the BigQuery dataset location, which can be a multi-region
    # like "US" or "EU", or a single region like "us-central1".
    VERTEX_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    BQ_LOCATION = os.environ.get("BQ_LOCATION", "US")
    GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME", "your-gcs-bucket-name") # Optional

    if PROJECT_ID == "your-gcp-project-id":
        raise ValueError("Please set GOOGLE_CLOUD_PROJECT or update the code.")

    # --- CRITICAL: Set environment variables BEFORE Gemini instantiation ---
    os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
    os.environ['GOOGLE_CLOUD_LOCATION'] = VERTEX_LOCATION
    os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True'

    # --- Initialize the Plugin with Config ---
    bq_config = BigQueryLoggerConfig(
        enabled=True,
        gcs_bucket_name=GCS_BUCKET, # Enable GCS offloading for multimodal content
        log_multi_modal_content=True,
        max_content_length=500 * 1024, # 500 KB limit for inline text
        batch_size=1, # Default is 1 for low latency, increase for high throughput
        shutdown_timeout=10.0
    )

    bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
        project_id=PROJECT_ID,
        dataset_id=DATASET_ID,
        table_id="agent_events", # default table name is agent_events
        config=bq_config,
        location=BQ_LOCATION
    )

    # --- Initialize Tools and Model ---
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    bigquery_toolset = BigQueryToolset(
        credentials_config=BigQueryCredentialsConfig(credentials=credentials)
    )

    llm = Gemini(model="gemini-flash-latest")

    root_agent = Agent(
        model=llm,
        name='my_bq_agent',
        instruction="You are a helpful assistant with access to BigQuery tools.",
        tools=[bigquery_toolset]
    )

    # --- Create the App ---
    app = App(
        name="my_bq_agent",
        root_agent=root_agent,
        plugins=[bq_logging_plugin],
    )
    ```

!!! tip "Agent Runtime にデプロイしますか？"

    [Agent Runtime へのデプロイ](#deploy-agent-runtime) を参照してください。

## 前提条件 {#prerequisites}

- **BigQuery API** が有効な **Google Cloud プロジェクト**
- **BigQuery データセット:** プラグインを使用する前に、ロギングテーブルを保存する
  データセットを作成します。テーブルが存在しない場合、プラグインは必要なイベント
  テーブルをデータセット内に自動作成します。
- **Google Cloud Storage バケット（任意）:** マルチモーダルコンテンツ（画像、
  音声など）を記録する場合は、大きなファイルをオフロードするために GCS バケットを
  作成しておくことを推奨します。
- **認証:**
    - **ローカル:** `gcloud auth application-default login` を実行します。
    - **クラウド:** サービスアカウントに必要な権限があることを確認します。

??? note "注: Gemini モデルセレクタ `gemini-flash-latest`"

    ADK ドキュメントの多くのコード例では、`gemini-flash-latest` を使って
    [利用可能な最新](https://ai.google.dev/gemini-api/docs/models#latest)の Gemini
    Flash バージョンを選択します。ただし、`us-central1` のようなリージョン
    エンドポイントから Gemini にアクセスする場合、この選択文字列が動作しない
    ことがあります。その場合は、[Gemini
    モデル](https://ai.google.dev/gemini-api/docs/models) ページまたは Google Cloud
    の [Gemini
    モデル](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models)
    一覧から具体的なモデルバージョン文字列を使用してください。

### IAM 権限 {#iam-permissions}

エージェントが正しく動作するには、エージェントを実行する principal（サービス
アカウント、ユーザーアカウントなど）に次の Google Cloud ロールが必要です。

- `roles/bigquery.jobUser`: プロジェクトレベルで BigQuery クエリを実行するため
- `roles/bigquery.dataEditor`: テーブルレベルでログ/イベントデータを書き込むため
- **GCS オフロードを使う場合:** 対象バケットの `roles/storage.objectCreator` と
  `roles/storage.objectViewer`

## 構成オプション {#configuration-options}

### コンストラクタパラメータ

`BigQueryAgentAnalyticsPlugin` コンストラクタは次のパラメータを受け取ります。
また、以下の `BigQueryLoggerConfig` に直接転送される `**kwargs` も受け取れます。

| パラメータ | 型 | デフォルト | 使用する場面 |
| --- | --- | --- | --- |
| `project_id` | `str` | *(必須)* | Google Cloud プロジェクトを選択します |
| `dataset_id` | `str` | *(必須)* | BigQuery データセットを選択します |
| `table_id` | `Optional[str]` | `None` | カスタムテーブル名を使います（config の `table_id` を上書き） |
| `config` | `Optional[BigQueryLoggerConfig]` | `None` | 詳細調整用の config オブジェクトを渡します |
| `location` | `str` | `"US"` | BigQuery データセットのロケーションに合わせます（例: `"US"`, `"EU"`, `"us-central1"`） |
| `credentials` | `Optional[google.auth.credentials.Credentials]` | `None` | [ADC](https://cloud.google.com/docs/authentication/application-default-credentials) の代わりに明示的なサービスアカウント、impersonated、cross-project 資格情報を使います |

```python
plugin = BigQueryAgentAnalyticsPlugin(
    project_id="my-project",
    dataset_id="my_dataset",
    batch_size=10,           # forwarded to BigQueryLoggerConfig
    shutdown_timeout=5.0,    # forwarded to BigQueryLoggerConfig
)
```

### BigQueryLoggerConfig オプション

以下のオプションはすべて任意で、適切なデフォルト値があります。
`BigQueryLoggerConfig` に渡すか、プラグインコンストラクタの `**kwargs` として
渡してください。

| オプション | 型 | デフォルト | 使用する場面 |
| --- | --- | --- | --- |
| `enabled` | `bool` | `True` | ロギングを一時的に無効にします |
| `table_id` | `str` | `"agent_events"` | カスタムテーブル名を使います（コンストラクタ値が優先） |
| `clustering_fields` | `List[str]` | `["event_type", "agent", "user_id"]` | テーブル作成時のクラスタリングをカスタマイズします |
| `gcs_bucket_name` | `Optional[str]` | `None` | 大きなテキストとマルチモーダルコンテンツを GCS にオフロードします |
| `connection_id` | `Optional[str]` | `None` | BigQuery ObjectRef / object table を使います（例: `us.my-connection`） |
| `max_content_length` | `int` | `500 * 1024` | オフロード/切り詰め前のインラインペイロードサイズを制御します |
| `batch_size` | `int` | `1` | 書き込みスループットとレイテンシを調整します |
| `batch_flush_interval` | `float` | `1.0` | 部分 batch を定期的に flush します（秒） |
| `shutdown_timeout` | `float` | `10.0` | 終了時の最終 flush を待ちます（秒） |
| `event_allowlist` | `Optional[List[str]]` | `None` | 選択した [イベントタイプ](#event-types) だけを記録します |
| `event_denylist` | `Optional[List[str]]` | `None` | 機密性が高い、またはノイズの多い [イベントタイプ](#event-types) をスキップします |
| `content_formatter` | `Optional[Callable]` | `None` | イベントごとのカスタムマスキング/フォーマットを適用します（`(content, event_type)` を受け取る） |
| `log_multi_modal_content` | `bool` | `True` | GCS 参照を含む `content_parts` 詳細をキャプチャします |
| `queue_max_size` | `int` | `10000` | メモリ内イベントキューの上限を設定します |
| `retry_config` | `RetryConfig` | `RetryConfig()` | リトライ動作を調整します（`max_retries=3`, `initial_delay=1.0`, `multiplier=2.0`, `max_delay=10.0`） |
| `log_session_metadata` | `bool` | `True` | `attributes` にセッション情報（`session_id`, `app_name`, `user_id`, `state`）を追加します。`temp:` または `secret:` 接頭辞のキーは [マスク](#built-in-redaction) されます。 |
| `custom_tags` | `Dict[str, Any]` | `{}` | すべてのイベントの `attributes` に静的タグ（例: `{"env": "prod"}`）を追加します |
| `auto_schema_upgrade` | `bool` | `True` | 既存テーブルへ新しい列を自動追加します（追加変更のみ） |
| `create_views` | `bool` | `True` | イベントタイプ別 BigQuery ビューを作成します（1.27.0+） |
| `view_prefix` | `str` | `"v"` | 複数のプラグインが同じデータセットを共有するとき、ビュー名の衝突を避けます（例: `"v_staging"`） |

次のコード例は、BigQuery Agent Analytics プラグインの構成を定義する方法を示します。

```python
import json
import re

from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryLoggerConfig

def redact_dollar_amounts(event_content: Any, event_type: str) -> str:
    """
    Custom formatter to redact dollar amounts (e.g., $600, $12.50)
    and ensure JSON output if the input is a dict.

    Args:
        event_content: The raw content of the event.
        event_type: The event type string (e.g., "LLM_REQUEST", "LLM_RESPONSE").
    """
    text_content = ""
    if isinstance(event_content, dict):
        text_content = json.dumps(event_content)
    else:
        text_content = str(event_content)

    # Regex to find dollar amounts: $ followed by digits, optionally with commas or decimals.
    # Examples: $600, $1,200.50, $0.99
    redacted_content = re.sub(r'\$\d+(?:,\d{3})*(?:\.\d+)?', 'xxx', text_content)

    return redacted_content

config = BigQueryLoggerConfig(
    enabled=True,
    event_allowlist=["LLM_REQUEST", "LLM_RESPONSE"], # Only log these events
    # event_denylist=["TOOL_STARTING"], # Skip these events
    shutdown_timeout=10.0, # Wait up to 10s for logs to flush on exit
    max_content_length=500, # Truncate content to 500 chars
    content_formatter=redact_dollar_amounts, # Redact the dollar amounts in the logging content
    queue_max_size=10000, # Max events to hold in memory
    auto_schema_upgrade=True, # Automatically add new columns to existing tables
    create_views=True, # Automatically create per-event-type views
    # retry_config=RetryConfig(max_retries=3), # Optional: Configure retries
)

plugin = BigQueryAgentAnalyticsPlugin(
    project_id="my-project",
    dataset_id="my_dataset",
    config=config,
)
```

## スキーマと本番環境セットアップ

### スキーマ参照

イベントテーブル（`agent_events`）は柔軟なスキーマを使用します。次の表は、例の
値を含む包括的なリファレンスです。

| フィールド名 | 型 | モード | 説明 | 例 |
| --- | --- | --- | --- | --- |
| **timestamp** | `TIMESTAMP` | `REQUIRED` | イベント作成時の UTC タイムスタンプです。主要な並び替えキーであり、日次パーティションキーです。精度はマイクロ秒です。 | `2026-02-03 20:52:17 UTC` |
| **event_type** | `STRING` | `NULLABLE` | 正規化されたイベントカテゴリです。標準値には `LLM_REQUEST`, `LLM_RESPONSE`, `LLM_ERROR`, `TOOL_STARTING`, `TOOL_COMPLETED`, `TOOL_ERROR`, `AGENT_STARTING`, `AGENT_COMPLETED`, `STATE_DELTA`, `INVOCATION_STARTING`, `INVOCATION_COMPLETED`, `USER_MESSAGE_RECEIVED`、HITL イベント（[HITL イベント](#hitl-events) 参照）が含まれます。上位レベルのフィルタリングに使います。 | `LLM_REQUEST` |
| **agent** | `STRING` | `NULLABLE` | このイベントを担当するエージェント名です。エージェント初期化時、または `root_agent_name` コンテキストで定義されます。 | `my_bq_agent` |
| **session_id** | `STRING` | `NULLABLE` | 会話スレッド全体の永続識別子です。複数ターンやサブエージェント呼び出しを通じて一定です。 | `04275a01-1649-4a30-b6a7-5b443c69a7bc` |
| **invocation_id** | `STRING` | `NULLABLE` | 単一の実行ターンまたはリクエストサイクルの一意識別子です。多くの文脈では `trace_id` に対応します。 | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **user_id** | `STRING` | `NULLABLE` | セッションを開始したユーザー（人間またはシステム）の識別子です。`User` オブジェクトまたはメタデータから抽出されます。 | `test_user` |
| **trace_id** | `STRING` | `NULLABLE` | **OpenTelemetry** Trace ID（32 文字 hex）です。単一の分散リクエストライフサイクル内のすべての操作をつなぎます。 | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **span_id** | `STRING` | `NULLABLE` | **OpenTelemetry** Span ID（16 文字 hex）です。この特定の原子的操作を一意に識別します。 | `69867a836cd94798be2759d8e0d70215` |
| **parent_span_id** | `STRING` | `NULLABLE` | 直前の呼び出し元の Span ID です。親子実行ツリー（DAG）を再構築するために使います。 | `ef5843fe40764b4b8afec44e78044205` |
| **content** | `JSON` | `NULLABLE` | 主なイベントペイロードです。構造は `event_type` によって多態的です。 | `{"system_prompt": "You are...", "prompt": [{"role": "user", "content": "hello"}], "response": "Hi", "usage": {"total": 15}}` |
| **attributes** | `JSON` | `NULLABLE` | メタデータ/エンリッチメント（使用量統計、モデル情報、ツール出自、カスタムタグ）です。 | `{"model": "gemini-flash-latest", "usage_metadata": {"total_token_count": 15}, "session_metadata": {"session_id": "...", "app_name": "...", "user_id": "...", "state": {}}, "custom_tags": {"env": "prod"}}` |
| **latency_ms** | `JSON` | `NULLABLE` | 性能指標です。標準キーは `total_ms`（wall-clock duration）と `time_to_first_token_ms`（ストリーミングレイテンシ）です。 | `{"total_ms": 1250, "time_to_first_token_ms": 450}` |
| **status** | `STRING` | `NULLABLE` | 上位レベルの結果です。値は `OK`（成功）または `ERROR`（失敗）です。 | `OK` |
| **error_message** | `STRING` | `NULLABLE` | 人間が読める例外メッセージまたはスタックトレース断片です。`status` が `ERROR` のときだけ設定されます。 | `Error 404: Dataset not found` |
| **is_truncated** | `BOOLEAN` | `NULLABLE` | `content` または `attributes` が BigQuery セルサイズ制限（デフォルト 10MB）を超えて一部削除された場合は `true` です。 | `false` |
| **content_parts** | `RECORD` | `REPEATED` | マルチモーダルセグメント（Text、Image、Blob）の配列です。大きなバイナリや GCS 参照など、content を単純な JSON としてシリアライズできない場合に使います。 | `[{"mime_type": "text/plain", "text": "hello"}]` |

テーブルが存在しない場合、プラグインが自動的に作成します。本番環境では、必要に
応じて次の DDL でテーブルを手動作成できます。

??? example "本番環境セットアップ用の手動 DDL"

    ```sql
    CREATE TABLE `your-gcp-project-id.adk_agent_logs.agent_events`
    (
      timestamp TIMESTAMP NOT NULL OPTIONS(description="The UTC time at which the event was logged."),
      event_type STRING OPTIONS(description="Indicates the type of event being logged (e.g., 'LLM_REQUEST', 'TOOL_COMPLETED')."),
      agent STRING OPTIONS(description="The name of the ADK agent or author associated with the event."),
      session_id STRING OPTIONS(description="A unique identifier to group events within a single conversation or user session."),
      invocation_id STRING OPTIONS(description="A unique identifier for each individual agent execution or turn within a session."),
      user_id STRING OPTIONS(description="The identifier of the user associated with the current session."),
      trace_id STRING OPTIONS(description="OpenTelemetry trace ID for distributed tracing."),
      span_id STRING OPTIONS(description="OpenTelemetry span ID for this specific operation."),
      parent_span_id STRING OPTIONS(description="OpenTelemetry parent span ID to reconstruct hierarchy."),
      content JSON OPTIONS(description="The event-specific data (payload) stored as JSON."),
      content_parts ARRAY<STRUCT<
        mime_type STRING,
        uri STRING,
        object_ref STRUCT<
          uri STRING,
          version STRING,
          authorizer STRING,
          details JSON
        >,
        text STRING,
        part_index INT64,
        part_attributes STRING,
        storage_mode STRING
      >> OPTIONS(description="Detailed content parts for multi-modal data."),
      attributes JSON OPTIONS(description="Arbitrary key-value pairs for additional metadata (e.g., 'root_agent_name', 'model_version', 'usage_metadata', 'session_metadata', 'custom_tags')."),
      latency_ms JSON OPTIONS(description="Latency measurements (e.g., total_ms)."),
      status STRING OPTIONS(description="The outcome of the event, typically 'OK' or 'ERROR'."),
      error_message STRING OPTIONS(description="Populated if an error occurs."),
      is_truncated BOOLEAN OPTIONS(description="Flag indicates if content was truncated.")
    )
    PARTITION BY DATE(timestamp)
    CLUSTER BY event_type, agent, user_id;
    ```

### 自動作成されるビュー（1.27.0+）

`create_views=True`（1.27.0 以降のデフォルト）にすると、プラグインは各イベント
タイプについて、共通 JSON 構造をフラットで型付きの列に展開するビューを自動作成
します。これにより SQL が大幅に簡素化され、複雑な `JSON_VALUE` や `JSON_QUERY`
関数を明示的に書く必要がなくなります。

ビュー名は `{view_prefix}_{event_type_lowercase}` の規則に従います。たとえば
デフォルト接頭辞 `"v"` では、`LLM_REQUEST` が `v_llm_request` になります。同じ
データセット内で複数のプラグインインスタンスが別テーブルへ書き込む場合は、
`BigQueryLoggerConfig` の `view_prefix` に別の値を設定してビュー名の衝突を
防いでください。

```python
# Two plugins in the same dataset with distinct view prefixes
plugin_prod = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID,
    table_id="agent_events_prod",
    config=BigQueryLoggerConfig(view_prefix="v_prod"),
)
# Creates views: v_prod_llm_request, v_prod_tool_completed, ...

plugin_staging = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID,
    table_id="agent_events_staging",
    config=BigQueryLoggerConfig(view_prefix="v_staging"),
)
# Creates views: v_staging_llm_request, v_staging_tool_completed, ...
```

スキーマアップグレード後にビューを更新する場合などは、public async メソッド
`await plugin.create_analytics_views()` を手動で呼び出すこともできます。

すべてのビューには次の **共通列** が含まれます: `timestamp`, `event_type`,
`agent`, `session_id`, `invocation_id`, `user_id`, `trace_id`, `span_id`,
`parent_span_id`, `status`, `error_message`, `is_truncated`。

次の表は、自動作成されるすべてのビューとイベント固有列を示します。

| ビュー名 | イベント固有列 |
| --- | --- |
| **`v_user_message_received`** | *(共通列のみ)* |
| **`v_llm_request`** | `model` (STRING), `request_content` (JSON), `llm_config` (JSON), `tools` (JSON) |
| **`v_llm_response`** | `response` (JSON), `usage_prompt_tokens` (INT64), `usage_completion_tokens` (INT64), `usage_total_tokens` (INT64), `usage_cached_tokens` (INT64), `total_ms` (INT64), `ttft_ms` (INT64), `model_version` (STRING), `usage_metadata` (JSON), `cache_metadata` (JSON), `context_cache_hit_rate` (FLOAT64) |
| **`v_llm_error`** | `total_ms` (INT64) |
| **`v_tool_starting`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING) |
| **`v_tool_completed`** | `tool_name` (STRING), `tool_result` (JSON), `tool_origin` (STRING), `total_ms` (INT64) |
| **`v_tool_error`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING), `total_ms` (INT64) |
| **`v_agent_starting`** | `agent_instruction` (STRING) |
| **`v_agent_completed`** | `total_ms` (INT64) |
| **`v_invocation_starting`** | *(共通列のみ)* |
| **`v_invocation_completed`** | *(共通列のみ)* |
| **`v_state_delta`** | `state_delta` (JSON) |
| **`v_hitl_credential_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_hitl_confirmation_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_hitl_input_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_a2a_interaction`** | `response_content` (JSON), `a2a_task_id` (STRING), `a2a_context_id` (STRING), `a2a_request` (JSON), `a2a_response` (JSON) |
| **`v_agent_response`** | `response_text` (STRING), `source_event_id` (STRING), `source_event_author` (STRING), `source_event_branch` (STRING) |

## イベントタイプとペイロード {#event-types}

`content` 列には、`event_type` ごとの **JSON** オブジェクトが含まれます。
`content_parts` 列はコンテンツの構造化ビューを提供し、画像やオフロードされた
データに特に便利です。

!!! note "コンテンツの切り詰め"

    - 可変コンテンツフィールドは `max_content_length`（`BigQueryLoggerConfig` で
      構成、デフォルト 500KB）で切り詰められます。
    - `gcs_bucket_name` が構成されている場合、大きなコンテンツは切り詰められず
      GCS にオフロードされ、参照が `content_parts.object_ref` に保存されます。

### LLM インタラクション（プラグインライフサイクル）

これらのイベントは、LLM に送信される生のリクエストと LLM から受け取るレスポンスを
追跡します。

**1. LLM_REQUEST**

会話履歴とシステム指示を含む、モデルへ送信されたプロンプトをキャプチャします。

```json
{
  "event_type": "LLM_REQUEST",
  "content": {
    "system_prompt": "You are a helpful assistant...",
    "prompt": [
      {
        "role": "user",
        "content": "hello how are you today"
      }
    ]
  },
  "attributes": {
    "root_agent_name": "my_bq_agent",
    "model": "gemini-flash-latest",
    "tools": ["list_dataset_ids", "execute_sql"],
    "llm_config": {
      "temperature": 0.5,
      "top_p": 0.9
    }
  }
}
```

**2. LLM_RESPONSE**

モデル出力とトークン使用量統計をキャプチャします。

```json
{
  "event_type": "LLM_RESPONSE",
  "content": {
    "response": "text: 'Hello! I'm doing well...'",
    "usage": {
      "completion": 19,
      "prompt": 10129,
      "total": 10148
    }
  },
  "attributes": {
    "root_agent_name": "my_bq_agent",
    "model_version": "gemini-flash-latest",
    "usage_metadata": {
      "prompt_token_count": 10129,
      "candidates_token_count": 19,
      "total_token_count": 10148
    }
  },
  "latency_ms": {
    "time_to_first_token_ms": 2579,
    "total_ms": 2579
  }
}
```

**3. LLM_ERROR**

LLM 呼び出しが例外で失敗したときに記録されます。エラーメッセージがキャプチャ
され、span が閉じられます。

```json
{
  "event_type": "LLM_ERROR",
  "content": null,
  "attributes": {
    "root_agent_name": "my_bq_agent"
  },
  "error_message": "Error 429: Resource exhausted",
  "latency_ms": {
    "total_ms": 350
  }
}
```

### ツール使用（プラグインライフサイクル）

これらのイベントは、エージェントによるツール実行を追跡します。各ツールイベント
には、ツールの出自を分類する `tool_origin` フィールドが含まれます。

| ツール出自 | 説明 |
| --- | --- |
| `LOCAL` | `FunctionTool` インスタンス（ローカル Python 関数） |
| `MCP` | Model Context Protocol ツール（`McpTool` インスタンス） |
| `SUB_AGENT` | `AgentTool` インスタンス（サブエージェント） |
| `A2A` | リモート Agent2Agent インスタンス（`RemoteA2aAgent`） |
| `TRANSFER_AGENT` | `TransferToAgentTool` インスタンス（一般的なエージェント transfer） |
| `TRANSFER_A2A` | `RemoteA2aAgent` へ transfer する `TransferToAgentTool` インスタンス（呼び出しレベルで分類） |
| `UNKNOWN` | 未分類のツール |

**4. TOOL_STARTING**

エージェントがツール実行を開始したときに記録されます。

```json
{
  "event_type": "TOOL_STARTING",
  "content": {
    "tool": "list_dataset_ids",
    "args": {
      "project_id": "bigquery-public-data"
    },
    "tool_origin": "LOCAL"
  }
}
```

**5. TOOL_COMPLETED**

ツール実行が完了したときに記録されます。

```json
{
  "event_type": "TOOL_COMPLETED",
  "content": {
    "tool": "list_dataset_ids",
    "result": [
      "austin_311",
      "austin_bikeshare"
    ],
    "tool_origin": "LOCAL"
  },
  "latency_ms": {
    "total_ms": 467
  }
}
```

**6. TOOL_ERROR**

ツール実行が例外で失敗したときに記録されます。ツール名、引数、ツール出自、
エラーメッセージをキャプチャします。

```json
{
  "event_type": "TOOL_ERROR",
  "content": {
    "tool": "list_dataset_ids",
    "args": {
      "project_id": "nonexistent-project"
    },
    "tool_origin": "LOCAL"
  },
  "error_message": "Error 404: Dataset not found",
  "latency_ms": {
    "total_ms": 150
  }
}
```

### 状態管理

これらのイベントは、通常はツールによってトリガーされるエージェント状態の変更を
追跡します。

**7. STATE_DELTA**

エージェントの内部状態変更（例: ツールによって更新されたカスタムアプリケーション
状態）を追跡します。

!!! note "組み込みマスキング"

    `temp:` または `secret:` 接頭辞の状態キーは、記録される `state_delta` 内で
    自動的に `[REDACTED]` にマスクされます。詳しくは [組み込み
    マスキング](#built-in-redaction) を参照してください。

```json
{
  "event_type": "STATE_DELTA",
  "attributes": {
    "state_delta": {
      "customer_tier": "enterprise",
      "last_query_dataset": "bigquery-public-data.samples"
    }
  }
}
```

### エージェントライフサイクルと汎用イベント

| イベントタイプ | コンテンツ（JSON）構造 |
| ---------- | ------------------------ |
| `INVOCATION_STARTING` | `{}` |
| `INVOCATION_COMPLETED` | `{}` |
| `AGENT_STARTING` | `"You are a helpful agent..."` |
| `AGENT_COMPLETED` | `{}` |
| `USER_MESSAGE_RECEIVED` | `{"text_summary": "Help me book a flight."}` |
| `AGENT_RESPONSE` | `{"response": "Here are the flights..."}` |

**AGENT_RESPONSE**

エージェントがユーザーへの最終レスポンスを yield したときに記録されます。レスポンス
テキストは `content` に保存され、source event metadata は `attributes` に保存されます。

```json
{
  "event_type": "AGENT_RESPONSE",
  "content": {
    "response": "Here are the available flights..."
  },
  "attributes": {
    "source_event_id": "evt-abc123",
    "source_event_author": "flight_agent",
    "source_event_branch": "main"
  }
}
```

### Human-in-the-Loop (HITL) イベント {#hitl-events}

プラグインは ADK の synthetic HITL ツール呼び出しを自動検出し、専用のイベント
タイプを出力します。これらのイベントは通常の `TOOL_STARTING` /
`TOOL_COMPLETED` イベントに **加えて** 記録されます。

認識される HITL ツール名は次のとおりです。

- `adk_request_credential`: ユーザー資格情報の要求（例: OAuth トークン）
- `adk_request_confirmation`: 続行前のユーザー確認要求
- `adk_request_input`: 自由形式のユーザー入力要求

| イベントタイプ | トリガー | コンテンツ（JSON）構造 |
| ---------- | ------- | ------------------------ |
| `HITL_CREDENTIAL_REQUEST` | エージェントが `adk_request_credential` を呼び出す | `{"tool": "adk_request_credential", "args": {...}}` |
| `HITL_CREDENTIAL_REQUEST_COMPLETED` | ユーザーが資格情報応答を提供する | `{"tool": "adk_request_credential", "result": {...}}` |
| `HITL_CONFIRMATION_REQUEST` | エージェントが `adk_request_confirmation` を呼び出す | `{"tool": "adk_request_confirmation", "args": {...}}` |
| `HITL_CONFIRMATION_REQUEST_COMPLETED` | ユーザーが確認応答を提供する | `{"tool": "adk_request_confirmation", "result": {...}}` |
| `HITL_INPUT_REQUEST` | エージェントが `adk_request_input` を呼び出す | `{"tool": "adk_request_input", "args": {...}}` |
| `HITL_INPUT_REQUEST_COMPLETED` | ユーザーが入力応答を提供する | `{"tool": "adk_request_input", "result": {...}}` |

HITL リクエストイベントは `on_event_callback` の `function_call` パートから検出
されます。HITL 完了イベントは `on_event_callback` と `on_user_message_callback`
の両方にある `function_response` パートから検出されます。

!!! note "HITL イベント用ビュー"

    自動作成ビューは、3 つの **リクエスト** イベントタイプ
    （`v_hitl_credential_request`, `v_hitl_confirmation_request`,
    `v_hitl_input_request`）に対してのみ存在します。3 つの `*_COMPLETED`
    イベントタイプはベーステーブルには記録されますが、専用ビューはありません。
    `agent_events` テーブルで `WHERE event_type LIKE 'HITL_%_COMPLETED'` を使って
    直接照会してください。

### A2A インタラクションイベント

エージェントが Agent2Agent (A2A) プロトコルでリモートエージェントと通信すると、
プラグインはリクエストとレスポンスの詳細をキャプチャする `A2A_INTERACTION`
イベントを記録します。

**A2A_INTERACTION**

A2A リモートエージェント呼び出しが完了したときに記録されます。

```json
{
  "event_type": "A2A_INTERACTION",
  "content": {
    "response_content": "The remote agent's response...",
    "a2a_task_id": "task-abc123",
    "a2a_context_id": "ctx-def456",
    "a2a_request": { ... },
    "a2a_response": { ... }
  }
}
```

## ストレージ動作: GCS オフロード

`BigQueryLoggerConfig` に `gcs_bucket_name` が構成されている場合、プラグインは
大きなテキストやマルチモーダルコンテンツ（画像、音声など）を Google Cloud
Storage へ自動的にオフロードします。`content` 列には要約または placeholder が
入り、`content_parts` には GCS URI を指す `object_ref` が保存されます。
[構成オプション](#configuration-options) の `connection_id` と
`max_content_length` も参照してください。

### オフロードされたテキスト例

```json
{
  "event_type": "LLM_REQUEST",
  "content_parts": [
    {
      "part_index": 1,
      "mime_type": "text/plain",
      "storage_mode": "GCS_REFERENCE",
      "text": "AAAA... [OFFLOADED]",
      "object_ref": {
        "uri": "gs://sample-bucket-name/2025-12-10/e-f9545d6d/ae5235e6_p1.txt",
        "authorizer": "us.bqml_connection",
        "details": {"gcs_metadata": {"content_type": "text/plain"}}
      }
    }
  ]
}
```

### オフロードされた画像例

```json
{
  "event_type": "LLM_REQUEST",
  "content_parts": [
    {
      "part_index": 2,
      "mime_type": "image/png",
      "storage_mode": "GCS_REFERENCE",
      "text": "[MEDIA OFFLOADED]",
      "object_ref": {
        "uri": "gs://sample-bucket-name/2025-12-10/e-f9545d6d/ae5235e6_p2.png",
        "authorizer": "us.bqml_connection",
        "details": {"gcs_metadata": {"content_type": "image/png"}}
      }
    }
  ]
}
```

### オフロードされたコンテンツの照会（署名付き URL の取得）

```sql
SELECT
  timestamp,
  event_type,
  part.mime_type,
  part.storage_mode,
  part.object_ref.uri AS gcs_uri,
  -- Generate a signed URL to read the content directly (requires connection_id configuration)
  STRING(OBJ.GET_ACCESS_URL(part.object_ref, 'r').access_urls.read_url) AS signed_url
FROM `your-gcp-project-id.your-dataset-id.agent_events`,
UNNEST(content_parts) AS part
WHERE part.storage_mode = 'GCS_REFERENCE'
ORDER BY timestamp DESC
LIMIT 10;
```

## クエリレシピ

### 実行をデバッグする

#### `trace_id` を使って特定の会話ターンを追跡

```sql
SELECT timestamp, event_type, agent, JSON_VALUE(content, '$.response') as summary
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE trace_id = 'your-trace-id'
ORDER BY timestamp ASC;
```

#### Span 階層と duration 分析

```sql
SELECT
  span_id,
  parent_span_id,
  event_type,
  timestamp,
  -- Extract duration from latency_ms for completed operations
  CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64) as duration_ms,
  -- Identify the specific tool or operation
  COALESCE(
    JSON_VALUE(content, '$.tool'),
    'LLM_CALL'
  ) as operation
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE trace_id = 'your-trace-id'
  AND event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
ORDER BY timestamp ASC;
```

#### エラー分析（LLM とツールエラー）

ビューを使う方法（推奨）:

```sql
-- Tool errors with provenance
SELECT timestamp, agent, tool_name, tool_origin, error_message, total_ms
FROM `your-gcp-project-id.your-dataset-id.v_tool_error`
ORDER BY timestamp DESC
LIMIT 20;

-- LLM errors
SELECT timestamp, agent, error_message, total_ms
FROM `your-gcp-project-id.your-dataset-id.v_llm_error`
ORDER BY timestamp DESC
LIMIT 20;
```

### コストと性能を監視する

#### トークン使用量分析

`v_llm_response` ビューを使う方法（推奨）:

```sql
SELECT
  AVG(usage_total_tokens) as avg_tokens,
  AVG(usage_prompt_tokens) as avg_prompt_tokens,
  AVG(usage_completion_tokens) as avg_completion_tokens
FROM `your-gcp-project-id.your-dataset-id.v_llm_response`;
```

または JSON 抽出とともにベーステーブルを使います。

```sql
SELECT
  AVG(CAST(JSON_VALUE(content, '$.usage.total') AS INT64)) as avg_tokens
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'LLM_RESPONSE';
```

#### レイテンシ分析（LLM とツール）

ビューを使う方法（推奨）:

```sql
-- LLM latency
SELECT AVG(total_ms) as avg_llm_ms, AVG(ttft_ms) as avg_ttft_ms
FROM `your-gcp-project-id.your-dataset-id.v_llm_response`;

-- Tool latency by tool name
SELECT tool_name, tool_origin, AVG(total_ms) as avg_tool_ms
FROM `your-gcp-project-id.your-dataset-id.v_tool_completed`
GROUP BY tool_name, tool_origin
ORDER BY avg_tool_ms DESC;
```

またはベーステーブルを使います。

```sql
SELECT
  event_type,
  AVG(CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64)) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
GROUP BY event_type;
```

### ツールとインタラクションを調べる

#### Tool Provenance 分析

`v_tool_completed` ビューを使う方法（推奨）:

```sql
SELECT
  tool_origin,
  tool_name,
  COUNT(*) as call_count,
  AVG(total_ms) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.v_tool_completed`
GROUP BY tool_origin, tool_name
ORDER BY call_count DESC;
```

#### HITL インタラクション分析

```sql
SELECT
  timestamp,
  event_type,
  session_id,
  JSON_VALUE(content, '$.tool') as hitl_tool,
  content
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type LIKE 'HITL_%'
ORDER BY timestamp DESC
LIMIT 20;
```

### マルチモーダルコンテンツを分析する

#### マルチモーダルコンテンツの照会（`content_parts` と ObjectRef を使用）

```sql
SELECT
  timestamp,
  part.mime_type,
  part.object_ref.uri as gcs_uri
FROM `your-gcp-project-id.your-dataset-id.agent_events`,
UNNEST(content_parts) as part
WHERE part.mime_type LIKE 'image/%'
ORDER BY timestamp DESC;
```

#### BigQuery リモートモデル（Gemini）でマルチモーダルコンテンツを分析

```sql
SELECT
  logs.session_id,
  -- Get a signed URL for the image
  STRING(OBJ.GET_ACCESS_URL(parts.object_ref, "r").access_urls.read_url) as signed_url,
  -- Analyze the image using a remote model (e.g., gemini-pro-vision)
  AI.GENERATE(
    ('Describe this image briefly. What company logo?', parts.object_ref)
  ) AS generated_result
FROM
  `your-gcp-project-id.your-dataset-id.agent_events` logs,
  UNNEST(logs.content_parts) AS parts
WHERE
  parts.mime_type LIKE 'image/%'
ORDER BY logs.timestamp DESC
LIMIT 1;
```

### AI による根本原因分析

BigQuery ML と Gemini を使い、失敗したセッションを自動分析してエラーの根本原因を
特定します。

```sql
DECLARE failed_session_id STRING;
-- Find a recent failed session
SET failed_session_id = (
    SELECT session_id
    FROM `your-gcp-project-id.your-dataset-id.agent_events`
    WHERE error_message IS NOT NULL
    ORDER BY timestamp DESC
    LIMIT 1
);

-- Reconstruct the full conversation context
WITH SessionContext AS (
    SELECT
        session_id,
        STRING_AGG(CONCAT(event_type, ': ', COALESCE(TO_JSON_STRING(content), '')), '\n' ORDER BY timestamp) as full_history
    FROM `your-gcp-project-id.your-dataset-id.agent_events`
    WHERE session_id = failed_session_id
    GROUP BY session_id
)
-- Ask Gemini to diagnose the issue
SELECT
    session_id,
    AI.GENERATE(
        ('Analyze this conversation log and explain the root cause of the failure. Log: ', full_history),
        endpoint => 'gemini-flash-latest'
    ).result AS root_cause_explanation
FROM SessionContext;
```

### 会話型分析

[BigQuery Conversational
Analytics](https://cloud.google.com/bigquery/docs/conversational-analytics) を
使って、自然言語でエージェントログを分析することもできます。`agent_events`
テーブルに接続された会話型分析エージェントを [BigQuery Agents
Hub](https://console.cloud.google.com/bigquery/agents_hub) で作成し、次のように
質問できます。

- "Show me the error rate over time"
- "What are the most common tool calls?"
- "Identify sessions with high token usage"

## プラグイン付きで Agent Runtime にデプロイ {#deploy-agent-runtime}

BigQuery Agent Analytics プラグインを含むエージェントを [Agent
Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
にデプロイできます。このセクションでは、ADK CLI を使ったデプロイ手順と、
代替として Agent Platform SDK を使うプログラム的な方法を説明します。

!!! important "バージョン要件"

    このプラグインを Agent Runtime にデプロイするには、ADK Python バージョン
    **1.24.0 以上**を使用してください。以前のバージョンでは、プラグインの
    非同期ログ writer がサーバーレスランタイムによって終了される前に、保留中の
    イベントを flush できない問題がありました。1.24.0 以降では、各 invocation
    の終了時に同期 flush を行い、すべてのイベントが書き込まれるようにします。

### 前提条件

デプロイ前に、次の項目を含む一般的な [Agent Runtime
セットアップ](/ja/deploy/agent-runtime/deploy/#setup-cloud-project) を完了して
ください。

1. **Agent Platform API** と **Cloud Resource Manager API** が有効な Google Cloud プロジェクト
2. 対象プロジェクトの **BigQuery データセット**（または適切な権限を持つ cross-project データセット）
3. デプロイアーティファクト用の **Cloud Storage staging バケット**
4. デプロイ用サービスアカウントに [IAM 権限](#iam-permissions) に記載されたロールがあること
5. コーディング環境が `gcloud auth login` と `gcloud auth application-default login` で
   [認証](/ja/deploy/agent-runtime/deploy/#prerequisites-coding-env)されていること

### ステップ 1: エージェントとプラグインを定義

プラグインを含む `App` オブジェクトを持つエージェントプロジェクトフォルダを
作成します。`App` オブジェクトは、プラグイン付き Agent Runtime デプロイに必要です。

```
my_bq_agent/
├── __init__.py
├── agent.py
└── requirements.txt
```

```python title="my_bq_agent/__init__.py"
from . import agent
```

```python title="my_bq_agent/agent.py"
import os
import google.auth
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models.google_llm import Gemini
from google.adk.plugins.bigquery_agent_analytics_plugin import (
    BigQueryAgentAnalyticsPlugin,
    BigQueryLoggerConfig,
)
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET_ID = os.environ.get("BQ_DATASET", "agent_analytics")
# BQ_LOCATION is the BigQuery dataset location (multi-region "US"/"EU" or
# a single region like "us-central1"). This is separate from the Agent Platform
# region used by GOOGLE_CLOUD_LOCATION.
BQ_LOCATION = os.environ.get("BQ_LOCATION", "US")

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# --- Plugin ---
bq_analytics_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID,
    dataset_id=DATASET_ID,
    location=BQ_LOCATION,
    config=BigQueryLoggerConfig(
        batch_size=1,
        batch_flush_interval=0.5,
        log_session_metadata=True,
    ),
)

# --- Tools ---
credentials, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials)
)

# --- Agent ---
root_agent = Agent(
    model=Gemini(model="gemini-flash-latest"),
    name="my_bq_agent",
    instruction="You are a helpful assistant with access to BigQuery tools.",
    tools=[bigquery_toolset],
)

# --- App (required for Agent Runtime with plugins) ---
app = App(
    name="my_bq_agent",
    root_agent=root_agent,
    plugins=[bq_analytics_plugin],
)
```

```text title="my_bq_agent/requirements.txt"
google-adk[bigquery]
google-cloud-bigquery-storage
pyarrow
opentelemetry-api
opentelemetry-sdk
```

### ステップ 2: ADK CLI でデプロイ

`adk deploy agent_engine` コマンドを使ってエージェントをデプロイします。
`--adk_app` フラグは、どの `App` オブジェクトを使うかを CLI に伝えます。

```shell
PROJECT_ID=your-gcp-project-id
LOCATION=us-central1

adk deploy agent_engine \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --staging_bucket=gs://your-staging-bucket \
    --display_name="My BQ Analytics Agent" \
    --adk_app=agent.app \
    my_bq_agent
```

!!! tip "`--adk_app` フラグ"

    `--adk_app` フラグは、`App` オブジェクトのモジュールパスと変数名を
    `module.variable` 形式で指定します。この例では、`agent.app` は `agent.py` の
    `app` 変数を指します。これにより、デプロイはプラグイン構成を正しく拾います。

デプロイに成功すると、次のような出力が表示されます。

```shell
AgentEngine created. Resource name: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944
```

次のステップで使う **Resource name** を控えておいてください。

### ステップ 3: デプロイしたエージェントをテスト

デプロイ後、Agent Platform SDK を使ってエージェントへクエリできます。

```python title="test_deployed_agent.py"
import uuid
import vertexai

PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
AGENT_ID = "751619551677906944"  # from deployment output

vertexai.init(project=PROJECT_ID, location=LOCATION)
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

agent = client.agent_engines.get(
    name=f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ID}"
)

user_id = f"test_user_{uuid.uuid4().hex[:8]}"
for chunk in agent.stream_query(
    message="List datasets in my project", user_id=user_id
):
    print(chunk, end="", flush=True)
```

### ステップ 4: BigQuery でイベントを確認

デプロイしたエージェントにいくつかクエリを送信した後、BigQuery テーブルを
クエリしてイベントが記録されていることを確認します。

```sql
SELECT timestamp, event_type, agent, content
FROM `your-gcp-project-id.agent_analytics.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

`INVOCATION_STARTING`, `LLM_REQUEST`, `LLM_RESPONSE`, `TOOL_STARTING`,
`TOOL_COMPLETED`, `INVOCATION_COMPLETED` などのイベントが表示されるはずです。

### 代替: Agent Platform SDK でデプロイ

Agent Platform SDK を直接使ってプログラム的にデプロイすることもできます。これは
CI/CD パイプラインやカスタムデプロイワークフローに便利です。

```python title="deploy.py"
import vertexai
from my_bq_agent.agent import app

PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://your-staging-bucket"

vertexai.init(
    project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET
)
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

remote_app = client.agent_engines.create(
    agent=app,
    config={
        "display_name": "My BQ Analytics Agent",
        "staging_bucket": STAGING_BUCKET,
        "requirements": [
            "google-adk[bigquery]",
            "google-cloud-aiplatform[agent_engines]",
            "google-cloud-bigquery-storage",
            "pyarrow",
            "opentelemetry-api",
            "opentelemetry-sdk",
        ],
    },
)
print(f"Deployed agent: {remote_app.api_resource.name}")
```

### トラブルシューティング

デプロイ後に BigQuery テーブルへイベントが表示されない場合は、次を確認します。

1. **ADK バージョンを確認:** requirements に `google-adk>=1.24.0` が含まれている
   ことを確認します。以前のバージョンは、サーバーレスランタイムがプロセスを
   停止する前に保留中イベントを flush しません。

2. **デバッグロギングを有効化:** 静かなエラーを見つけるには、`agent.py` の先頭に
   次を追加します。

    ```python
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("google_adk").setLevel(logging.DEBUG)
    ```

3. **IAM 権限を確認:** Agent Runtime サービスアカウントには、対象テーブルの
   `roles/bigquery.dataEditor` とプロジェクトの `roles/bigquery.jobUser` が必要です。
   **cross-project** ロギングでは、ソースプロジェクトで BigQuery API が有効であり、
   サービスアカウントに宛先テーブルの `bigquery.tables.updateData` があることも
   確認してください。

4. **プラグイン初期化を確認:** Cloud Logging で `resource.type="reasoning_engine"` を
   フィルタし、プラグイン起動メッセージやエラーログを探します。

5. **デバッグ用に即時 flush を使用:** バッファリング問題を切り分けるには、
   `BigQueryLoggerConfig` で `batch_size=1` と `batch_flush_interval=0.1` を設定します。

## セキュリティ: 機密資格情報のロギングを避ける {#security-credentials}

!!! warning "OAuth トークン、API キー、クライアントシークレットを記録しないでください"

    BigQuery Agent Analytics プラグインは、ツール引数、LLM プロンプト、認証関連
    イベント（HITL 資格情報要求など）を含む詳細なイベントペイロードを
    キャプチャします。エージェントが **認証済みツール**（OAuth2 を使う
    `AuthenticatedFunctionTool` など）を使用する場合、プラグインは
    `client_secret`, `access_token`, API キーなどの機密値を BigQuery テーブルの
    `content` 列に記録する可能性があります。

    これは既知の懸念
    ([google/adk-python#3845](https://github.com/google/adk-python/issues/3845)) であり、
    分析データ内で資格情報が露出する可能性があります。

プラグインには、一般的なシークレットを自動保護する **組み込みマスキング** が
含まれています。追加の制御が必要な場合は、その上にカスタムマスキングを重ねられます。

### 組み込みマスキング {#built-in-redaction}

プラグインは、`content` または `attributes` JSON のどこに現れても、次の既知の
キー名の値を自動的にマスクします（大文字小文字を区別しません）。

`client_secret`, `access_token`, `refresh_token`, `id_token`, `api_key`,
`password`

さらに、**`temp:`** または **`secret:`** 接頭辞の state key は、記録される
`state_delta` 内で自動的に `[REDACTED]` に置き換えられます。つまり、credential
service によってキャッシュされた OAuth トークンのように `secret:` scope に保存
された ADK セッション状態は、BigQuery に永続化されません。

!!! info "構成不要"

    組み込みマスキングは、構造化された attributes と state ロギングに常に有効で、
    ネストされた辞書や attribute 値内の JSON エンコード文字列にも再帰的に適用
    されます。カスタム `content_formatter` は生の content に **最初に** 実行される
    ため、自由形式ペイロードに現れる可能性のあるシークレットを追加マスクする際に
    使ってください。

### `content_formatter` で追加シークレットをマスクする

`BigQueryLoggerConfig` にカスタム `content_formatter` 関数を指定し、書き込み前に
機密フィールドを削除またはマスクできます。

```python
import json
import re
from typing import Any

SENSITIVE_KEYS = {"client_secret", "access_token", "refresh_token", "api_key", "secret"}

def redact_credentials(event_content: Any, event_type: str) -> str:
    """Redact OAuth secrets and tokens from logged content."""
    if isinstance(event_content, dict):
        text = json.dumps(event_content)
    else:
        text = str(event_content)

    for key in SENSITIVE_KEYS:
        # Redact values in JSON-like strings: "client_secret": "GOCSPX-xxx"
        text = re.sub(
            rf'("{key}"\s*:\s*)"[^"]*"',
            rf'\1"[REDACTED]"',
            text,
            flags=re.IGNORECASE,
        )
    return text

config = BigQueryLoggerConfig(
    content_formatter=redact_credentials,
    # ... other options
)
```

### `event_denylist` で資格情報イベントを除外する

認証関連イベントを記録する必要がない場合は、完全に除外します。

```python
config = BigQueryLoggerConfig(
    event_denylist=[
        "HITL_CREDENTIAL_REQUEST",
        "HITL_CREDENTIAL_REQUEST_COMPLETED",
    ],
    # ... other options
)
```

### 一般的なベストプラクティス

- エージェントソースコードにシークレットをハードコードしないでください。OAuth
  クライアントシークレットや API キーには、環境変数または Google Cloud Secret
  Manager などの secret manager を使用します。
- IAM を使って BigQuery テーブルアクセスを制限し、記録されたイベントデータを
  読める人を限定してください。
- 予期しない機密データがキャプチャされていないことを確認するため、ログを定期的に
  監査してください。

## 運用

### トレーシングと可観測性

プラグインは分散トレーシングのために **OpenTelemetry** をサポートします。
OpenTelemetry は ADK の core dependency に含まれており、常に利用可能です。

- **自動 Span 管理:** プラグインはエージェント実行、LLM 呼び出し、ツール実行に
  span を自動生成します。
- **OpenTelemetry 統合:** 上の例のように `TracerProvider` が構成されている場合、
  プラグインは有効な OTel span を使い、`trace_id`, `span_id`, `parent_span_id` を
  標準 OTel 識別子で埋めます。これにより、エージェントログを分散システム内の他の
  サービスと関連付けられます。
- **Fallback メカニズム:** `TracerProvider` が構成されていない場合（つまり、
  デフォルトの no-op provider のみが有効な場合）、プラグインは span 用の内部 UUID
  を自動生成し、`invocation_id` を trace ID として使用します。これにより、
  構成済み `TracerProvider` がなくても、親子階層（Agent -> Span -> Tool/LLM）は
  BigQuery ログ内で *常に* 保持されます。

### 公開メソッド

プラグインはライフサイクル管理のためにいくつかの public メソッドを公開しています。

- **`await plugin.flush()`**: 保留中のすべてのイベントを BigQuery に flush します。
  データ損失を避けるため、終了前に呼び出してください。
- **`await plugin.shutdown(timeout=None)`**: プラグインを正常終了し、保留中イベントを
  flush してリソースを解放します。任意の `timeout` パラメータは config の
  `shutdown_timeout` を上書きします。
- **`await plugin.create_analytics_views()`**: イベントタイプ別 analytics view を
  すべて手動で再作成します。スキーマアップグレード後やビュー更新が必要なときに
  便利です。
- **非同期 context manager:** プラグインは自動起動と終了のために `async with` を
  サポートします。

    ```python
    async with BigQueryAgentAnalyticsPlugin(
        project_id=PROJECT_ID, dataset_id=DATASET_ID
    ) as plugin:
        # plugin is initialized and ready to use
        ...
    # plugin.shutdown() is called automatically on exit
    ```

### Multiprocessing と fork 安全性

プラグインは fork-aware です。gRPC C-core ライブラリをロードする前に
`GRPC_ENABLE_FORK_SUPPORT=1` を設定し、子プロセスで継承されたランタイム状態
（gRPC channel、write stream、event loop）をリセットする
`os.register_at_fork` handler を登録します。これにより、プラグインは `os.fork()`
後も file descriptor をリークしたり、親の接続へデータを送ったりせずに動作できます。

ただし、本番デプロイでは **`spawn` multiprocessing start method** が推奨されます。
`fork` は進行中の gRPC 状態を含む親アドレス空間をコピーし、fork 後のリセットは
各子プロセスの最初の write にレイテンシを追加します。`spawn` では各 worker が
プラグインをクリーンに初期化します。

Gunicorn デプロイでは特に次を推奨します。

- lazy plugin initialization と組み合わせて `--preload` を使用します（プラグインは
  最初のイベントが記録されるまでセットアップを遅延します）。
- または `post_fork` hook 内でプラグインを初期化し、各 worker が独自の client を
  持つようにします。

!!! note

    fork-safety メカニズムはランタイム状態のみをリセットします。fork 時点で親
    プロセスの queue にあり、まだ flush されていなかったイベントを replay する
    ことはありません。配信保証が必要な場合は、fork 前に `await plugin.flush()` を
    呼び出してください。

## 記録データを利用する追加方法

### BigQuery Agent Analytics SDK

[BigQuery Agent Analytics
SDK](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/tree/main) は、
プラグインによって記録されたデータをプログラムから利用、分析する方法を提供します。
SDK は次の用途に使えます。

- **エージェント評価:** エージェント実行を期待結果と比較します。
- **Golden trajectory matching:** エージェント実行パスが承認済みシーケンスと
  一致するか検証します。
- **Trace 可視化:** 記録された span からエージェント実行フローを再構築して
  可視化します。

### ダッシュボードを構築する

BigQuery Agent Analytics SDK には、エージェント性能データをクエリして可視化する
方法を示す [Jupyter notebook
例](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/blob/main/examples/dashboard_v2.ipynb)
が含まれています。これを出発点に、BigQuery Agent Analytics データセットに合わせた
独自ダッシュボードを構築できます。[Colab Data
Apps](https://docs.cloud.google.com/bigquery/docs/colab-data-apps) を使って notebook
を interactive dashboard として公開することもできます。

## フィードバック

BigQuery Agent Analytics に関するフィードバックを歓迎します。質問、提案、問題が
ある場合は [bqaa-feedback@google.com](mailto:bqaa-feedback@google.com) までご連絡ください。

## 追加リソース

- [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [Introduction to Object Tables](https://docs.cloud.google.com/bigquery/docs/object-table-introduction)
- [Interactive Demo Notebook](https://github.com/haiyuan-eng-google/demo_BQ_agent_analytics_plugin_notebook)
