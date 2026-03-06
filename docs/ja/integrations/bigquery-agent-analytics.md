---
catalog_title: BigQuery Agent Analytics Plugin
catalog_description: エージェント挙動分析とログ収集のための詳細なエージェント分析
catalog_icon: /adk-docs/integrations/assets/bigquery.png
catalog_tags: ["observability", "google"]
---

# ADK 向け BigQuery Agent Analytics プラグイン

<div class="language-support-tag">
  <span class="lst-supported">ADK でサポート</span><span class="lst-python">Python v1.21.0</span><span class="lst-preview">プレビュー</span>
</div>

!!! important "バージョン要件"

    auto-schema-upgrade、tool provenance tracking、HITL event tracing を含むこのドキュメントの機能を十分に活用するには、ADK Python バージョン 1.26.0 以上を使用してください。

BigQuery Agent Analytics プラグインは、詳細なエージェント挙動分析のための堅牢なソリューションを提供することで、Agent Development Kit (ADK) を大きく強化します。ADK プラグインアーキテクチャと **BigQuery Storage Write API** を用いて、重要な運用イベントを Google BigQuery テーブルへ直接キャプチャして記録し、デバッグ、リアルタイム監視、包括的なオフライン性能評価のための高度な機能を提供します。

バージョン 1.26.0 では、**Auto Schema Upgrade**（既存テーブルへの新規カラム安全追加）、**Tool Provenance** 追跡（`LOCAL`, `MCP`, `SUB_AGENT`, `A2A`, `TRANSFER_AGENT`）、**HITL Event Tracing**（human-in-the-loop 相互作用追跡）が追加されました。

!!! example "プレビュー リリース"

    BigQuery Agent Analytics プラグインはプレビュー リリースです。詳細については [リリース段階の説明](https://cloud.google.com/products#product-launch-stages) を参照してください。

!!! warning "BigQuery Storage Write API"

    この機能は有料サービスである **BigQuery Storage Write API** を使用します。料金の詳細は [BigQuery ドキュメント](https://cloud.google.com/bigquery/pricing?e=48754805&hl=en#data-ingestion-pricing) を参照してください。

## ユースケース

-   **エージェントワークフローのデバッグと分析:** 明確に定義されたスキーマに、多様な *plugin lifecycle events*（LLM 呼び出し、tool usage）と *agent-yielded events*（ユーザー入力、モデル応答）を記録します。
-   **高ボリューム分析とデバッグ:** ロギング処理は高スループットと低レイテンシのために Storage Write API を使って非同期に行われます。
-   **マルチモーダル分析:** テキスト、画像、その他のモダリティを記録・分析します。大きなファイルは GCS にオフロードされ、BigQuery ML から Object Tables 経由で利用できます。
-   **分散トレーシング:** `trace_id`, `span_id` を使った OpenTelemetry スタイルの分散トレースを標準サポートし、エージェント実行フローを可視化できます。
-   **Tool Provenance:** 各 tool call の出所（ローカル関数、MCP サーバー、sub-agent、A2A remote agent、transfer agent）を追跡します。
-   **Human-in-the-Loop (HITL) Tracing:** 資格情報要求、確認プロンプト、ユーザー入力要求のための専用イベント型を提供します。

記録されるエージェントイベントデータは ADK のイベントタイプによって異なります。詳細は [イベントタイプとペイロード](#event-types) を参照してください。

## 前提条件

-   **BigQuery API** が有効な **Google Cloud プロジェクト**
-   **BigQuery データセット:** プラグインを使う前にロギングテーブル用のデータセットを作成してください。テーブルが存在しない場合、プラグインが必要なイベントテーブルをデータセット内に自動作成します。
-   **Google Cloud Storage バケット（任意）:** マルチモーダルコンテンツ（画像、音声など）をロギングする場合、大きなファイルをオフロードするために GCS バケットの作成を推奨します。
-   **認証:**
    -   **ローカル:** `gcloud auth application-default login` を実行
    -   **クラウド:** サービスアカウントに必要な権限があることを確認

### IAM 権限

エージェントが正しく動作するには、エージェントを実行する主体（例: サービスアカウント、ユーザーアカウント）に次の Google Cloud ロールが必要です。

* `roles/bigquery.jobUser` をプロジェクトレベルで付与し、BigQuery クエリを実行できるようにします。
* `roles/bigquery.dataEditor` をテーブルレベルで付与し、ログ/イベントデータを書き込めるようにします。
* **GCS オフロードを使用する場合:** 対象バケットに `roles/storage.objectCreator` と `roles/storage.objectViewer` が必要です。

## エージェントでの使用

BigQuery Agent Analytics プラグインは、ADK エージェントの App オブジェクトに構成して登録することで利用します。次の例は、GCS オフロードを含めてこのプラグインを利用するエージェント実装を示します。

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
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "US") # default location is US in the plugin
GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME", "your-gcs-bucket-name") # Optional

if PROJECT_ID == "your-gcp-project-id":
    raise ValueError("Please set GOOGLE_CLOUD_PROJECT or update the code.")

# --- CRITICAL: Set environment variables BEFORE Gemini instantiation ---
os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = LOCATION
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
    location=LOCATION
)

# --- Initialize Tools and Model ---
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials)
)

llm = Gemini(model="gemini-2.5-flash")

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

### エージェントの実行とテスト

エージェントを実行し、チャットインターフェースから `"tell me what you can do"` や `"List datasets in my cloud project <your-gcp-project-id> "` のようなリクエストをいくつか送ってプラグインをテストしてください。これらの操作によって Google Cloud プロジェクトの BigQuery インスタンスにイベントが記録されます。処理後は、次のクエリを使って [BigQuery Console](https://console.cloud.google.com/bigquery) でデータを確認できます。

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

## トレーシングと可観測性

このプラグインは分散トレーシングのために **OpenTelemetry** をサポートします。OpenTelemetry は ADK のコア依存関係に含まれており、常に利用できます。

- **Automatic Span Management:** Agent 実行、LLM 呼び出し、Tool 実行の span を自動生成します。
- **OpenTelemetry Integration:** 上の例のように `TracerProvider` が構成されている場合、プラグインは有効な OTel span を使い、`trace_id`, `span_id`, `parent_span_id` に標準 OTel 識別子を記録します。これにより、エージェントログを分散システム内の他サービスと相関付けできます。
- **Fallback Mechanism:** `TracerProvider` が構成されていない場合（デフォルトの no-op provider のみが有効な場合）、プラグインは span 用に内部 UUID を生成し、`invocation_id` を trace ID として使用します。この場合でも parent-child 階層（Agent -> Span -> Tool/LLM）は常に BigQuery ログ内に保持されます。

## 構成オプション

`BigQueryLoggerConfig` を使ってプラグインをカスタマイズできます。

-   **`enabled`** (`bool`, デフォルト: `True`): エージェントデータを BigQuery テーブルへ記録しないようにするには False に設定します。
-   **`table_id`** (`str`, デフォルト: `"agent_events"`): データセット内の BigQuery テーブル ID です。`BigQueryAgentAnalyticsPlugin` コンストラクタの `table_id` パラメータでも上書きでき、そちらが優先されます。
-   **`clustering_fields`** (`List[str]`, デフォルト: `["event_type", "agent", "user_id"]`): テーブル自動作成時にクラスタリングへ使うフィールドです。
-   **`gcs_bucket_name`** (`Optional[str]`, デフォルト: `None`): 大きなコンテンツ（画像、blob、大容量テキスト）をオフロードする GCS バケット名です。指定しない場合、大きなコンテンツは切り詰められるか placeholder に置き換えられます。
-   **`connection_id`** (`Optional[str]`, デフォルト: `None`): `ObjectRef` カラムの authorizer として使う BigQuery connection ID（例: `us.my-connection`）です。BigQuery ML で `ObjectRef` を使うには必要です。
-   **`max_content_length`** (`int`, デフォルト: `500 * 1024`): GCS オフロード（構成されている場合）または切り詰め前に BigQuery に **inline** で保存するテキストコンテンツの最大長（文字数）です。デフォルトは 500 KB です。
-   **`batch_size`** (`int`, デフォルト: `1`): BigQuery に書き込む前にバッチ化するイベント数です。
-   **`batch_flush_interval`** (`float`, デフォルト: `1.0`): 部分バッチを flush する前に待つ最大時間（秒）です。
-   **`shutdown_timeout`** (`float`, デフォルト: `10.0`): 終了時にログ flush を待つ最大秒数です。
-   **`event_allowlist`** (`Optional[List[str]]`, デフォルト: `None`): ログ記録対象のイベントタイプ一覧です。`None` の場合、`event_denylist` に含まれるイベント以外をすべて記録します。対応イベントの完全一覧は [イベントタイプとペイロード](#event-types) を参照してください。
-   **`event_denylist`** (`Optional[List[str]]`, デフォルト: `None`): ログ記録をスキップするイベントタイプ一覧です。対応イベントの完全一覧は [イベントタイプとペイロード](#event-types) を参照してください。
-   **`content_formatter`** (`Optional[Callable[[Any, str], Any]]`, デフォルト: `None`): ログ記録前にイベントコンテンツを整形する任意関数です。この関数は raw content と event type 文字列（例: `"LLM_REQUEST"`）の 2 引数を受け取ります。
-   **`log_multi_modal_content`** (`bool`, デフォルト: `True`): 詳細な content parts（GCS reference を含む）を記録するかどうかです。
-   **`queue_max_size`** (`int`, デフォルト: `10000`): 新規イベントを破棄する前にメモリ内キューに保持する最大イベント数です。
-   **`retry_config`** (`RetryConfig`, デフォルト: `RetryConfig()`): 失敗した BigQuery 書き込みを再試行するための構成です（`max_retries`, `initial_delay`, `multiplier`, `max_delay`）。
-   **`log_session_metadata`** (`bool`, デフォルト: `True`): True の場合、`attributes` カラムに `session_id`, `app_name`, `user_id`, セッション `state` 辞書（gchat thread-id, customer_id などのカスタム state を含む）を記録します。
-   **`custom_tags`** (`Dict[str, Any]`, デフォルト: `{}`): 各イベントの `attributes` カラムに含める静的タグ辞書です（例: `{"env": "prod", "version": "1.0"}`）。
-   **`auto_schema_upgrade`** (`bool`, デフォルト: `True`): 有効にすると、プラグインスキーマが進化した際に既存テーブルへ新規カラムを自動追加します。追加的変更のみ行われ（カラム削除や変更はなし）、テーブル上のバージョンラベル（`adk_schema_version`）により各スキーマバージョンごとに diff は最大 1 回だけ実行されます。有効化したままで安全です。

次のコードサンプルは、BigQuery Agent Analytics プラグインの構成を定義する方法を示します。

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
    # retry_config=RetryConfig(max_retries=3), # Optional: Configure retries
)

plugin = BigQueryAgentAnalyticsPlugin(..., config=config)
```

## スキーマと本番設定

### スキーマ参照

イベントテーブル（`agent_events`）は柔軟なスキーマを使用します。以下の表は、例示値付きの包括的な参照です。

| フィールド名 | 型 | モード | 説明 | 例示値 |
|:---|:---|:---|:---|:---|
| **timestamp** | `TIMESTAMP` | `REQUIRED` | イベント作成時の UTC タイムスタンプです。主な並び順キーであり、日次パーティションキーでもあります。精度はマイクロ秒です。 | `2026-02-03 20:52:17 UTC` |
| **event_type** | `STRING` | `NULLABLE` | 正規化されたイベントカテゴリです。標準値には `LLM_REQUEST`, `LLM_RESPONSE`, `LLM_ERROR`, `TOOL_STARTING`, `TOOL_COMPLETED`, `TOOL_ERROR`, `AGENT_STARTING`, `AGENT_COMPLETED`, `STATE_DELTA`, `INVOCATION_STARTING`, `INVOCATION_COMPLETED`, `USER_MESSAGE_RECEIVED`、HITL イベント（[HITL events](#hitl-events) 参照）が含まれます。高レベルのフィルタリングに使用されます。 | `LLM_REQUEST` |
| **agent** | `STRING` | `NULLABLE` | このイベントを担当するエージェント名です。エージェント初期化時または `root_agent_name` コンテキストを介して定義されます。 | `my_bq_agent` |
| **session_id** | `STRING` | `NULLABLE` | 会話スレッド全体に対する永続的な識別子です。複数ターンや sub-agent 呼び出しをまたいでも一定です。 | `04275a01-1649-4a30-b6a7-5b443c69a7bc` |
| **invocation_id** | `STRING` | `NULLABLE` | 単一の実行ターンまたはリクエストサイクルを識別する一意の ID です。多くの文脈で `trace_id` に対応します。 | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **user_id** | `STRING` | `NULLABLE` | セッションを開始したユーザー（人間またはシステム）の識別子です。`User` オブジェクトまたはメタデータから抽出されます。 | `test_user` |
| **trace_id** | `STRING` | `NULLABLE` | **OpenTelemetry** Trace ID（32 文字 hex）です。単一の分散リクエストライフサイクル内の全操作を結び付けます。 | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **span_id** | `STRING` | `NULLABLE` | **OpenTelemetry** Span ID（16 文字 hex）です。この特定の原子的操作を一意に識別します。 | `69867a836cd94798be2759d8e0d70215` |
| **parent_span_id** | `STRING` | `NULLABLE` | 直近の呼び出し元の Span ID です。parent-child 実行ツリー（DAG）を復元するのに使います。 | `ef5843fe40764b4b8afec44e78044205` |
| **content** | `JSON` | `NULLABLE` | 主なイベント payload です。構造は `event_type` によって変わります。 | `{"system_prompt": "You are...", "prompt": [{"role": "user", "content": "hello"}], "response": "Hi", "usage": {"total": 15}}` |
| **attributes** | `JSON` | `NULLABLE` | メタデータ/拡張情報（usage stats、model info、tool provenance、custom tags）です。 | `{"model": "gemini-2.5-flash", "usage_metadata": {"total_token_count": 15}, "session_metadata": {"session_id": "...", "app_name": "...", "user_id": "...", "state": {}}, "custom_tags": {"env": "prod"}}` |
| **latency_ms** | `JSON` | `NULLABLE` | 性能指標です。標準キーは `total_ms`（総経過時間）と `time_to_first_token_ms`（ストリーミング遅延）です。 | `{"total_ms": 1250, "time_to_first_token_ms": 450}` |
| **status** | `STRING` | `NULLABLE` | 高レベルな結果です。値は `OK`（成功）または `ERROR`（失敗）です。 | `OK` |
| **error_message** | `STRING` | `NULLABLE` | 人が読める例外メッセージまたはスタックトレース断片です。`status` が `ERROR` のときのみ設定されます。 | `Error 404: Dataset not found` |
| **is_truncated** | `BOOLEAN` | `NULLABLE` | `content` または `attributes` が BigQuery セルサイズ上限（デフォルト 10MB）を超えて一部が破棄された場合に `true` です。 | `false` |
| **content_parts** | `RECORD` | `REPEATED` | マルチモーダルセグメント（Text, Image, Blob）の配列です。content を単純な JSON として直列化できない場合（例: 大きなバイナリ、GCS reference）に利用します。 | `[{"mime_type": "text/plain", "text": "hello"}]` |

プラグインはテーブルが存在しない場合、自動でテーブルを作成します。ただし本番では、柔軟性のための **JSON** 型と、マルチモーダルコンテンツのための **REPEATED RECORD** を利用する次の DDL で手動作成することを推奨します。

**推奨 DDL:**

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

### イベントタイプとペイロード {#event-types}

`content` カラムには、`event_type` ごとの **JSON** オブジェクトが格納されます。`content_parts` カラムは、特に画像やオフロードされたデータを扱うときに有用な構造化ビューを提供します。

!!! note "コンテンツの切り詰め"

    - 可変コンテンツフィールドは `max_content_length` まで切り詰められます（`BigQueryLoggerConfig` で構成、デフォルト 500KB）。
    - `gcs_bucket_name` が構成されている場合、大きなコンテンツは切り詰められず GCS にオフロードされ、`content_parts.object_ref` に参照が保存されます。

#### LLM インタラクション (plugin lifecycle)

これらのイベントは、LLM に送られた raw request と、LLM から受け取った raw response を追跡します。

**1. LLM_REQUEST**

会話履歴とシステム指示を含め、モデルに送信されたプロンプトをキャプチャします。

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
    "model": "gemini-2.5-flash",
    "tools": ["list_dataset_ids", "execute_sql"],
    "llm_config": {
      "temperature": 0.5,
      "top_p": 0.9
    }
  }
}
```

**2. LLM_RESPONSE**

モデル出力とトークン使用統計をキャプチャします。

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
    "model_version": "gemini-2.5-flash-001",
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

LLM 呼び出しが例外で失敗したときに記録されます。エラーメッセージが保存され、span が閉じられます。

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

#### Tool 使用 (plugin lifecycle)

これらのイベントはエージェントによる Tool 実行を追跡します。各 Tool イベントには、Tool の出所を分類する `tool_origin` フィールドが含まれます。

| Tool Origin | 説明 |
|:---|:---|
| `LOCAL` | `FunctionTool` インスタンス（ローカル Python 関数） |
| `MCP` | Model Context Protocol ツール（`McpTool` インスタンス） |
| `SUB_AGENT` | `AgentTool` インスタンス（sub-agent） |
| `A2A` | Remote Agent-to-Agent インスタンス（`RemoteA2aAgent`） |
| `TRANSFER_AGENT` | `TransferToAgentTool` インスタンス |
| `UNKNOWN` | 分類されていないツール |

**4. TOOL_STARTING**

エージェントが Tool 実行を開始するときに記録されます。

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

Tool 実行が完了したときに記録されます。

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

Tool 実行が例外で失敗したときに記録されます。Tool 名、引数、tool origin、エラーメッセージを保存します。

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

#### 状態管理

これらのイベントは、主に Tool によって引き起こされるエージェント状態の変化を追跡します。

**7. STATE_DELTA**

エージェント内部状態の変化（例: token cache の更新）を追跡します。

```json
{
  "event_type": "STATE_DELTA",
  "attributes": {
    "state_delta": {
      "bigquery_token_cache": "{\"token\": \"ya29...\", \"expiry\": \"...\"}"
    }
  }
}
```

#### エージェントライフサイクルと汎用イベント

<table>
  <thead>
    <tr>
      <th><strong>Event Type</strong></th>
      <th><strong>Content (JSON) Structure</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>INVOCATION_STARTING</pre></p></td>
      <td><p><pre>{}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>INVOCATION_COMPLETED</pre></p></td>
      <td><p><pre>{}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>AGENT_STARTING</pre></p></td>
      <td><p><pre>"You are a helpful agent..."</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>AGENT_COMPLETED</pre></p></td>
      <td><p><pre>{}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>USER_MESSAGE_RECEIVED</pre></p></td>
      <td><p><pre>{"text_summary": "Help me book a flight."}</pre></p></td>
    </tr>

  </tbody>
</table>

#### Human-in-the-Loop (HITL) Events {#hitl-events}

プラグインは ADK の synthetic HITL ツール呼び出しを自動検出し、その呼び出しに対応する専用イベントタイプを生成します。これらのイベントは通常の `TOOL_STARTING` / `TOOL_COMPLETED` イベントに **加えて** 記録されます。

認識される HITL ツール名は次のとおりです。

- `adk_request_credential` — ユーザー資格情報の要求（例: OAuth token）
- `adk_request_confirmation` — 処理続行前のユーザー確認要求
- `adk_request_input` — 自由形式のユーザー入力要求

<table>
  <thead>
    <tr>
      <th><strong>Event Type</strong></th>
      <th><strong>Trigger</strong></th>
      <th><strong>Content (JSON) Structure</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>HITL_CREDENTIAL_REQUEST</pre></p></td>
      <td>Agent calls <code>adk_request_credential</code></td>
      <td><p><pre>{"tool": "adk_request_credential", "args": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_CREDENTIAL_REQUEST_COMPLETED</pre></p></td>
      <td>User provides credential response</td>
      <td><p><pre>{"tool": "adk_request_credential", "result": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_CONFIRMATION_REQUEST</pre></p></td>
      <td>Agent calls <code>adk_request_confirmation</code></td>
      <td><p><pre>{"tool": "adk_request_confirmation", "args": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_CONFIRMATION_REQUEST_COMPLETED</pre></p></td>
      <td>User provides confirmation response</td>
      <td><p><pre>{"tool": "adk_request_confirmation", "result": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_INPUT_REQUEST</pre></p></td>
      <td>Agent calls <code>adk_request_input</code></td>
      <td><p><pre>{"tool": "adk_request_input", "args": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_INPUT_REQUEST_COMPLETED</pre></p></td>
      <td>User provides input response</td>
      <td><p><pre>{"tool": "adk_request_input", "result": {...}}</pre></p></td>
    </tr>
  </tbody>
</table>

HITL request イベントは `on_event_callback` の `function_call` part から検出されます。HITL completion イベントは `on_event_callback` と `on_user_message_callback` の両方にある `function_response` part から検出されます。

#### GCS オフロード例（マルチモーダル & 大容量テキスト）

`gcs_bucket_name` が構成されている場合、大容量テキストとマルチモーダルコンテンツ（画像、音声など）は自動的に GCS にオフロードされます。`content` カラムには要約または placeholder が入り、`content_parts` には GCS URI を指す `object_ref` が入ります。

**オフロードされたテキストの例**

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
        "uri": "gs://haiyuan-adk-debug-verification-1765319132/2025-12-10/e-f9545d6d/ae5235e6_p1.txt",
        "authorizer": "us.bqml_connection",
        "details": {"gcs_metadata": {"content_type": "text/plain"}}
      }
    }
  ]
}
```

**オフロードされた画像の例**

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
        "uri": "gs://haiyuan-adk-debug-verification-1765319132/2025-12-10/e-f9545d6d/ae5235e6_p2.png",
        "authorizer": "us.bqml_connection",
        "details": {"gcs_metadata": {"content_type": "image/png"}}
      }
    }
  ]
}
```

**オフロードされたコンテンツの照会（Signed URL 取得）**

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

## 高度な分析クエリ

**trace_id を使って特定の会話ターンを追跡**

```sql
SELECT timestamp, event_type, agent, JSON_VALUE(content, '$.response') as summary
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE trace_id = 'your-trace-id'
ORDER BY timestamp ASC;
```

**トークン使用量分析（JSON フィールドへのアクセス）**

```sql
SELECT
  AVG(CAST(JSON_VALUE(content, '$.usage.total') AS INT64)) as avg_tokens
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'LLM_RESPONSE';
```

**マルチモーダルコンテンツ照会（`content_parts` と `ObjectRef` を使用）**

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

**BigQuery リモートモデル（Gemini）でマルチモーダルコンテンツを分析**

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

**レイテンシ分析（LLM & Tools）**

```sql
SELECT
  event_type,
  AVG(CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64)) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
GROUP BY event_type;
```

**Span 階層と所要時間分析**

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

**エラー分析（LLM と Tool エラー）**

```sql
SELECT
  timestamp,
  event_type,
  agent,
  error_message,
  JSON_VALUE(content, '$.tool') as tool_name,
  CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64) as latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type IN ('LLM_ERROR', 'TOOL_ERROR')
ORDER BY timestamp DESC
LIMIT 20;
```

**Tool Provenance 分析**

```sql
SELECT
  JSON_VALUE(content, '$.tool_origin') as tool_origin,
  JSON_VALUE(content, '$.tool') as tool_name,
  COUNT(*) as call_count,
  AVG(CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64)) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'TOOL_COMPLETED'
GROUP BY tool_origin, tool_name
ORDER BY call_count DESC;
```

**HITL インタラクション分析**

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

### 7. AI 駆動の根本原因分析 (Agent Ops)

失敗したセッションを自動分析し、BigQuery ML と Gemini を使ってエラーの根本原因を特定します。

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
        connection_id => 'your-gcp-project-id.us.my-connection',
        endpoint => 'gemini-2.5-flash'
    ).result AS root_cause_explanation
FROM SessionContext;
```

## BigQuery における対話型分析

[BigQuery Conversational Analytics](https://cloud.google.com/bigquery/docs/conversational-analytics) を使えば、自然言語で agent log を分析することもできます。たとえば次のような問いに使えます。

*   "Show me the error rate over time"
*   "What are the most common tool calls?"
*   "Identify sessions with high token usage"

## Looker Studio ダッシュボード

事前構築済みの [Looker Studio Dashboard template](https://lookerstudio.google.com/c/reporting/f1c5b513-3095-44f8-90a2-54953d41b125/page/8YdhF) を使って、エージェント性能を可視化できます。

このダッシュボードを自分の BigQuery テーブルに接続するには、以下のリンク形式でプロジェクト、データセット、テーブル ID の placeholder を自分の値に置き換えて使用してください。

```text
https://lookerstudio.google.com/reporting/create?c.reportId=f1c5b513-3095-44f8-90a2-54953d41b125&ds.ds3.connector=bigQuery&ds.ds3.type=TABLE&ds.ds3.projectId=<your-project-id>&ds.ds3.datasetId=<your-dataset-id>&ds.ds3.tableId=<your-table-id>
```

## フィードバック

BigQuery Agent Analytics へのフィードバックを歓迎します。質問、提案、問題報告がある場合は bqaa-feedback@google.com までご連絡ください。

## 追加リソース

-   [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
-   [Introduction to Object Tables](https://docs.cloud.google.com/bigquery/docs/object-table-introduction)
-   [Interactive Demo Notebook](https://github.com/haiyuan-eng-google/demo_BQ_agent_analytics_plugin_notebook)
