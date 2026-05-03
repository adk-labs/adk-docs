---
catalog_title: BigQuery Agent Analytics Plugin
catalog_description: エージェント動作の分析とロギングのための詳細な分析機能を提供します
catalog_icon: /integrations/assets/bigquery.png
catalog_tags: ["observability", "google"]
---

# ADK 向け BigQuery Agent Analytics プラグイン

<div class="language-support-tag">
  <span class="lst-supported">ADK でサポート</span><span class="lst-python">Python v1.21.0</span><span class="lst-preview">プレビュー</span>
</div>

!!! important "バージョン要件"

    auto-schema-upgrade、tool provenance 追跡、HITL イベントトレーシングを含むこのドキュメントの機能を完全に利用するには、ADK Python バージョン 1.26.0 以上を使用してください。

BigQuery Agent Analytics プラグインは、Agent Development Kit (ADK) に対して詳細なエージェント動作分析のための堅牢なソリューションを提供し、ADK を大きく強化します。ADK プラグインアーキテクチャと **BigQuery Storage Write API** を使って重要な運用イベントを Google BigQuery テーブルへ直接キャプチャし記録することで、デバッグ、リアルタイム監視、包括的なオフライン性能評価のための高度な機能を提供します。

バージョン 1.26.0 では、**Auto Schema Upgrade** (既存テーブルへ新しい列を安全に追加)、**Tool Provenance** 追跡 (`LOCAL`, `MCP`, `SUB_AGENT`, `A2A`, `TRANSFER_AGENT`)、および Human-in-the-Loop 連携のための **HITL Event Tracing** が追加されました。バージョン 1.27.0 では、**Automatic View Creation**（フラットでクエリしやすいイベントビューの生成）が追加されました。

!!! example "プレビュー リリース"

    BigQuery Agent Analytics プラグインはプレビュー リリースです。詳細は [ローンチステージの説明](https://cloud.google.com/products#product-launch-stages) を参照してください。

!!! warning "BigQuery Storage Write API"

    この機能は有料サービスである **BigQuery Storage Write API** を使用します。料金については [BigQuery ドキュメント](https://cloud.google.com/bigquery/pricing?e=48754805&hl=en#data-ingestion-pricing) を参照してください。

## ユースケース

-   **エージェント ワークフローのデバッグと分析:** 幅広い *プラグイン ライフサイクル イベント* (LLM 呼び出し、ツール使用) と *エージェントが生成したイベント* (ユーザー入力、モデル応答) を、よく定義されたスキーマへ記録します。
-   **大規模分析とデバッグ:** ロギング処理は Storage Write API を使って非同期に実行されるため、高スループットと低レイテンシを両立できます。
-   **マルチモーダル分析:** テキスト、画像、その他の modality を記録・分析できます。大きなファイルは GCS へオフロードされ、Object Table 経由で BigQuery ML から利用できます。
-   **分散トレーシング:** `trace_id`, `span_id` を使う OpenTelemetry 形式のトレーシングを標準でサポートし、エージェント実行フローを可視化できます。
-   **Tool Provenance:** 各ツール呼び出しの出自 (ローカル関数、MCP サーバー、サブエージェント、A2A リモートエージェント、transfer agent) を追跡します。
-   **Human-in-the-Loop (HITL) トレーシング:** 資格情報要求、確認プロンプト、ユーザー入力要求のための専用イベントタイプを提供します。
-   **クエリ可能なイベントビュー:** フラットなイベントタイプ別 BigQuery ビュー（例: `v_llm_request`, `v_tool_completed`）を自動作成し、JSON ペイロードデータの展開を通じて下流分析を簡素化します。

記録されるエージェントイベントデータは ADK のイベントタイプによって異なります。詳細は [イベントタイプとペイロード](#event-types) を参照してください。

## 前提条件

-   **BigQuery API** が有効な **Google Cloud プロジェクト**
-   **BigQuery データセット:** プラグインを使う前にログテーブルを格納するデータセットを作成します。テーブルが存在しない場合、プラグインはそのデータセット内に必要なイベントテーブルを自動作成します。
-   **Google Cloud Storage バケット (任意):** マルチモーダルコンテンツ (画像、音声など) を記録する場合は、大きなファイルをオフロードするために GCS バケットの作成を推奨します。
-   **認証**
    -   **ローカル:** `gcloud auth application-default login` を実行
    -   **クラウド:** サービスアカウントに必要な権限があることを確認

??? note "Gemini モデルセレクタ `gemini-flash-latest`"

    ADK ドキュメントのほとんどのコード例では `gemini-flash-latest` を使って
    [最新の利用可能な](https://ai.google.dev/gemini-api/docs/models#latest)
    Gemini Flash バージョンを選択します。ただし、`us-central1` のようなリージョナル
    エンドポイントで Gemini を使う場合、この選択文字列は動作しないことがあります。
    その場合は [Gemini models](https://ai.google.dev/gemini-api/docs/models) ページや
    Google Cloud の [Gemini models](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models) 一覧から
    具体的なモデルのバージョン文字列を使ってください。

### IAM 権限

エージェントが正しく動作するには、エージェントを実行するプリンシパル (サービスアカウントやユーザーアカウントなど) に次の Google Cloud ロールが必要です。

* `roles/bigquery.jobUser`: プロジェクトレベルで BigQuery クエリを実行するための権限
* `roles/bigquery.dataEditor`: テーブルレベルでログ / イベントデータを書き込むための権限
* **GCS オフロードを使う場合:** 対象バケットに対する `roles/storage.objectCreator` と `roles/storage.objectViewer`

## エージェントで使用

BigQuery Agent Analytics プラグインは、ADK エージェントの `App` オブジェクトへ設定して登録することで利用します。次の例は、GCS オフロードを含むこのプラグイン利用エージェントの実装例です。

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
# GOOGLE_CLOUD_LOCATION は有効な Vertex AI リージョン (例: "us-central1") である必要があります。
# BQ_LOCATION は BigQuery データセットのロケーションで、"US" や "EU" のような
# マルチリージョン、または "us-central1" のような単一リージョンです。
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

### エージェントの実行とテスト

チャット インターフェース経由でエージェントを実行し、`"tell me what you can do"` や `"List datasets in my cloud project <your-gcp-project-id> "` のようなリクエストをいくつか送ってプラグインをテストします。これらの操作により、Google Cloud プロジェクトの BigQuery インスタンスにイベントが記録されます。イベントが処理された後は、[BigQuery Console](https://console.cloud.google.com/bigquery) で次のクエリを使ってデータを確認できます。

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

## プラグイン付きで Agent Engine にデプロイ {#deploy-agent-engine}

このプラグインを含むエージェントは
[Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) にデプロイできます。
このセクションでは、ADK CLI を使ったデプロイ手順と、代替として Vertex AI SDK を使う方法を説明します。

!!! important "バージョン要件"

    このプラグインを Agent Engine にデプロイするには、ADK Python バージョン **1.24.0 以上**を使用してください。
    以前のバージョンでは、プラグインの非同期ログ writer がサーバーレスランタイムにより終了される前に
    保留中のイベントを flush できない問題がありました。1.24.0 以降では、各 invocation の終了時に
    同期 flush を行い、すべてのイベントが確実に書き込まれます。

### 前提条件

デプロイ前に、一般的な [Agent Engine の設定](/ja/deploy/agent-runtime/deploy/#setup-cloud-project) を完了してください。
次を含みます。

1.  **Vertex AI API** と **Cloud Resource Manager API** が有効な Google Cloud プロジェクト
2.  対象プロジェクトの **BigQuery データセット** (または適切な権限を持つクロスプロジェクトデータセット)
3.  デプロイアーティファクト用の **Cloud Storage ステージングバケット**
4.  デプロイするサービスアカウントに [IAM 権限](#iam-権限) に記載したロールが付与されていること
5.  コーディング環境が
    [認証済み](/ja/deploy/agent-runtime/deploy/#prerequisites-coding-env)
    であり、`gcloud auth login` と `gcloud auth application-default login` を実行済みであること

### ステップ 1: エージェントとプラグインの定義

プラグインを含む `App` オブジェクトを持つエージェントプロジェクトフォルダを作成します。
`App` オブジェクトは、プラグインを使った Agent Engine デプロイに必須です。

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
# BQ_LOCATION は BigQuery データセットのロケーションです。"US"/"EU" のような
# マルチリージョン、または "us-central1" のような単一リージョンです。
# これは GOOGLE_CLOUD_LOCATION で指定する Vertex AI リージョンとは別です。
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

# --- App (required for Agent Engine with plugins) ---
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

`adk deploy agent_engine` コマンドを使ってエージェントをデプロイします。`--adk_app`
フラグは CLI にどの `App` オブジェクトを使うかを伝えます。

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

    `--adk_app` フラグは、`App` オブジェクトのモジュールパスと変数名を指定します。
    この例では `agent.app` が `agent.py` の `app` 変数を指します。
    これにより、デプロイでプラグイン設定が正しく取り込まれます。

デプロイが成功すると、次のような出力が表示されます。

```shell
AgentEngine created. Resource name: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944
```

次のステップで使う **Resource name** を控えておいてください。

### ステップ 3: デプロイしたエージェントをテスト

デプロイ後は、Vertex AI SDK を使ってエージェントを問い合わせできます。

```python title="test_deployed_agent.py"
import uuid
import vertexai

PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
AGENT_ID = "751619551677906944"  # deployment output から取得

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

デプロイしたエージェントに数回クエリを送ったあと、BigQuery テーブルを問い合わせて
イベントが記録されていることを確認します。

```sql
SELECT timestamp, event_type, agent, content
FROM `your-gcp-project-id.agent_analytics.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

`INVOCATION_STARTING`, `LLM_REQUEST`, `LLM_RESPONSE`, `TOOL_STARTING`,
`TOOL_COMPLETED`, `INVOCATION_COMPLETED` のようなイベントが表示されるはずです。

### 代替: Vertex AI SDK でデプロイ

Vertex AI SDK を直接使ってプログラムでデプロイすることもできます。CI/CD パイプラインや
カスタムデプロイワークフローに有用です。

```python title="deploy.py"
import vertexai
from vertexai import agent_engines
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

デプロイ後に BigQuery テーブルへイベントが表示されない場合は、次を確認してください。

1.  **ADK バージョンの確認**: `google-adk>=1.24.0` が requirements に含まれているか確認します。
    以前のバージョンでは、サーバーレスランタイムがプロセスを停止する前に保留中イベントを flush できません。

2.  **デバッグログを有効化**: `agent.py` の先頭に以下を追加して、静かに失敗しているエラーを可視化します。

    ```python
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("google_adk").setLevel(logging.DEBUG)
    ```

3.  **IAM 権限を確認**: Agent Engine サービスアカウントには、対象テーブルに対する `roles/bigquery.dataEditor` と
    プロジェクトに対する `roles/bigquery.jobUser` が必要です。**クロスプロジェクト** ロギングでは、
    ソースプロジェクトで BigQuery API が有効であり、かつ対象テーブルに対してサービスアカウントに
    `bigquery.tables.updateData` 権限があることも確認してください。

4.  **プラグイン初期化を確認**: Cloud Logging で `resource.type="reasoning_engine"` をフィルタし、
    プラグイン起動メッセージやエラーログを探します。

5.  **デバッグ用に即時 flush を使う**: バッファリングの問題を切り分けるため、
    `BigQueryLoggerConfig` で `batch_size=1` と `batch_flush_interval=0.1` を設定します。

## トレーシングと可観測性

このプラグインは分散トレーシングのために **OpenTelemetry** をサポートします。OpenTelemetry は ADK のコア依存関係に含まれているため、常に利用可能です。

- **自動 Span 管理:** プラグインは、エージェント実行、LLM 呼び出し、ツール実行に対する span を自動生成します。
- **OpenTelemetry 統合:** 上の例のように `TracerProvider` が設定されている場合、プラグインは有効な OTel span を使って `trace_id`, `span_id`, `parent_span_id` を標準 OTel 識別子で埋めます。これにより、分散システム内の他サービスとエージェントログを相関させられます。
- **Fallback メカニズム:** `TracerProvider` が設定されていない場合 (つまりデフォルトの no-op provider のみが有効な場合)、プラグインは内部 UUID ベースの span 生成へ自動でフォールバックし、`invocation_id` を trace ID として使います。そのため、OTel `TracerProvider` を設定していなくても、BigQuery ログ内の親子階層 (Agent -> Span -> Tool/LLM) は常に維持されます。

## 構成オプション

`BigQueryLoggerConfig` を使ってプラグインをカスタマイズできます。

-   **`enabled`** (`bool`, デフォルト: `True`): プラグインが BigQuery テーブルへエージェントデータを記録しないようにするには `False` に設定します。
-   **`table_id`** (`str`, デフォルト: `"agent_events"`): データセット内の BigQuery テーブル ID です。`BigQueryAgentAnalyticsPlugin` コンストラクタの `table_id` 引数でも上書きでき、そちらが優先されます。
-   **`clustering_fields`** (`List[str]`, デフォルト: `["event_type", "agent", "user_id"]`): テーブルを自動作成する際にクラスタリングに使用するフィールドです。
-   **`gcs_bucket_name`** (`Optional[str]`, デフォルト: `None`): 大きなコンテンツ (画像、blob、長文テキスト) をオフロードする GCS バケット名です。指定しない場合、大きなコンテンツは切り詰められるかプレースホルダーに置き換えられることがあります。
-   **`connection_id`** (`Optional[str]`, デフォルト: `None`): `ObjectRef` 列の authorizer として使う BigQuery connection ID (例: `us.my-connection`) です。BigQuery ML で `ObjectRef` を使う場合に必要です。
-   **`max_content_length`** (`int`, デフォルト: `500 * 1024`): BigQuery に **inline** で保存するテキストコンテンツの最大長 (文字数) です。これを超えると (GCS が設定されていれば) GCS へオフロードされ、そうでなければ切り詰められます。デフォルトは 500KB です。
-   **`batch_size`** (`int`, デフォルト: `1`): BigQuery に書き込む前にまとめるイベント数です。
-   **`batch_flush_interval`** (`float`, デフォルト: `1.0`): 部分バッチを flush するまで待つ最大時間 (秒) です。
-   **`shutdown_timeout`** (`float`, デフォルト: `10.0`): シャットダウン時にログの flush を待つ時間 (秒) です。
-   **`event_allowlist`** (`Optional[List[str]]`, デフォルト: `None`): 記録するイベントタイプの一覧です。`None` の場合、`event_denylist` に含まれるイベントを除くすべてのイベントを記録します。対応するイベントタイプ全体は [イベントタイプとペイロード](#event-types) を参照してください。
-   **`event_denylist`** (`Optional[List[str]]`, デフォルト: `None`): 記録対象から除外するイベントタイプの一覧です。対応するイベントタイプ全体は [イベントタイプとペイロード](#event-types) を参照してください。
-   **`content_formatter`** (`Optional[Callable[[Any, str], Any]]`, デフォルト: `None`): ログ出力前にイベントコンテンツを整形するための任意の関数です。この関数は生のコンテンツとイベントタイプ文字列 (例: `"LLM_REQUEST"`) の 2 引数を受け取ります。
-   **`log_multi_modal_content`** (`bool`, デフォルト: `True`): 詳細なコンテンツパート (`GCS_REFERENCE` を含む) を記録するかどうかです。
-   **`queue_max_size`** (`int`, デフォルト: `10000`): インメモリキューに保持するイベントの最大数です。これを超えると新しいイベントは破棄されます。
-   **`retry_config`** (`RetryConfig`, デフォルト: `RetryConfig()`): BigQuery 書き込み失敗時の再試行設定です。下位フィールドには `max_retries` (デフォルト `3`)、`initial_delay` (デフォルト `1.0` 秒)、`multiplier` (デフォルト `2.0`)、`max_delay` (デフォルト `10.0` 秒) が含まれます。
-   **`log_session_metadata`** (`bool`, デフォルト: `True`): `True` の場合、`session_id`, `app_name`, `user_id`、およびセッションの `state` 辞書 (gchat thread-id や customer_id のようなカスタム状態を含む) を `attributes` 列へ記録します。`temp:` または `secret:` プレフィックスを持つ状態キーは自動的にマスクされます。詳しくは [組み込みマスキング](#built-in-redaction) を参照してください。
-   **`custom_tags`** (`Dict[str, Any]`, デフォルト: `{}`): 全イベントの `attributes` 列へ含める静的タグの辞書です (例: `{"env": "prod", "version": "1.0"}`)。
-   **`auto_schema_upgrade`** (`bool`, デフォルト: `True`): 有効にすると、プラグインスキーマが進化した際に既存テーブルへ新しい列を自動追加します。列の削除や変更は行わず、加算的変更のみ実施します。テーブル上のバージョンラベル (`adk_schema_version`) により、スキーマバージョンごとに diff は最大 1 回だけ実行されます。デフォルトで有効にして問題ありません。
-   **`create_views`** (`bool`, デフォルト: `True`): 1.27.0 で追加されました。有効にすると、`content` や `attributes` のような構造化 JSON データをフラットで型付きの列に展開するイベントタイプ別 BigQuery ビューを自動生成し、SQL クエリを大幅に簡素化します。
-   **`view_prefix`** (`str`, デフォルト: `"v"`): 自動生成ビュー名に付く接頭辞です。デフォルトの `"v"` では `v_llm_request` のようなビューが作成されます。同じデータセット内で複数のプラグインインスタンスが別テーブルへ書き込む場合は、テーブルごとに異なる接頭辞を使ってビュー名の衝突を防いでください (例: `"v_staging"` は `v_staging_llm_request` を生成します)。空文字列は指定できません。

次のコードサンプルは BigQuery Agent Analytics プラグイン向け設定の定義例です。

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

plugin = BigQueryAgentAnalyticsPlugin(..., config=config)
```

### 公開メソッド

プラグインはライフサイクル管理のためにいくつかの公開メソッドを提供します。

-   **`await plugin.flush()`**: 保留中のすべてのイベントを BigQuery にフラッシュします。データ損失を避けるため、終了前に呼び出してください。
-   **`await plugin.shutdown(timeout=None)`**: 保留中のイベントをフラッシュし、リソースを解放しながらプラグインを正常終了します。任意の `timeout` 引数で、config の `shutdown_timeout` を上書きできます。
-   **`await plugin.create_analytics_views()`**: イベントタイプ別の分析ビューを手動で再作成します。スキーマアップグレード後や、ビューを更新したいときに便利です。
-   **非同期コンテキストマネージャー**: プラグインは自動起動と自動終了のための `async with` もサポートしています。

    ```python
    async with BigQueryAgentAnalyticsPlugin(
        project_id=PROJECT_ID, dataset_id=DATASET_ID
    ) as plugin:
        # plugin is initialized and ready to use
        ...
    # plugin.shutdown() is called automatically on exit
    ```


## スキーマと本番環境セットアップ

### スキーマ参照

イベントテーブル (`agent_events`) は柔軟なスキーマを使用します。以下の表は、例示値を含む包括的なリファレンスです。

| フィールド名 | 型 | モード | 説明 | 例 |
|:---|:---|:---|:---|:---|
| **timestamp** | `TIMESTAMP` | `REQUIRED` | イベント作成時刻の UTC タイムスタンプです。主な並び順キーであり、日次パーティションキーでもあります。精度はマイクロ秒です。 | `2026-02-03 20:52:17 UTC` |
| **event_type** | `STRING` | `NULLABLE` | 正規化されたイベントカテゴリです。標準値には `LLM_REQUEST`, `LLM_RESPONSE`, `LLM_ERROR`, `TOOL_STARTING`, `TOOL_COMPLETED`, `TOOL_ERROR`, `AGENT_STARTING`, `AGENT_COMPLETED`, `STATE_DELTA`, `INVOCATION_STARTING`, `INVOCATION_COMPLETED`, `USER_MESSAGE_RECEIVED`、および HITL イベント ([HITL events](#hitl-events) 参照) が含まれます。上位レベルのフィルタリングに使用されます。 | `LLM_REQUEST` |
| **agent** | `STRING` | `NULLABLE` | このイベントの責任を持つエージェント名です。エージェント初期化時または `root_agent_name` コンテキストを通じて定義されます。 | `my_bq_agent` |
| **session_id** | `STRING` | `NULLABLE` | 会話スレッド全体を識別する永続的な識別子です。複数の turn やサブエージェント呼び出しをまたいでも一定です。 | `04275a01-1649-4a30-b6a7-5b443c69a7bc` |
| **invocation_id** | `STRING` | `NULLABLE` | 単一の実行 turn またはリクエストサイクルの一意識別子です。多くの文脈では `trace_id` に対応します。 | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **user_id** | `STRING` | `NULLABLE` | セッションを開始したユーザー (人間またはシステム) の識別子です。`User` オブジェクトまたはメタデータから抽出されます。 | `test_user` |
| **trace_id** | `STRING` | `NULLABLE` | **OpenTelemetry** Trace ID (32 文字の 16 進数) です。単一の分散リクエストライフサイクル内のすべての操作を結び付けます。 | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **span_id** | `STRING` | `NULLABLE` | **OpenTelemetry** Span ID (16 文字の 16 進数) です。この特定の原子的操作を一意に識別します。 | `69867a836cd94798be2759d8e0d70215` |
| **parent_span_id** | `STRING` | `NULLABLE` | 直前の呼び出し元の Span ID です。親子実行ツリー (DAG) の再構築に使用します。 | `ef5843fe40764b4b8afec44e78044205` |
| **content** | `JSON` | `NULLABLE` | 主要なイベントペイロードです。構造は `event_type` に応じて変化します。 | `{"system_prompt": "You are...", "prompt": [{"role": "user", "content": "hello"}], "response": "Hi", "usage": {"total": 15}}` |
| **attributes** | `JSON` | `NULLABLE` | メタデータ / エンリッチメント情報 (使用量統計、モデル情報、tool provenance、custom tags) です。 | `{"model": "gemini-flash-latest", "usage_metadata": {"total_token_count": 15}, "session_metadata": {"session_id": "...", "app_name": "...", "user_id": "...", "state": {}}, "custom_tags": {"env": "prod"}}` |
| **latency_ms** | `JSON` | `NULLABLE` | 性能メトリクスです。標準キーは `total_ms` (総所要時間) と `time_to_first_token_ms` (ストリーミング遅延) です。 | `{"total_ms": 1250, "time_to_first_token_ms": 450}` |
| **status** | `STRING` | `NULLABLE` | 上位レベルの結果です。値は `OK` (成功) または `ERROR` (失敗) です。 | `OK` |
| **error_message** | `STRING` | `NULLABLE` | 人間が読める例外メッセージやスタックトレース断片です。`status` が `ERROR` の場合にのみ設定されます。 | `Error 404: Dataset not found` |
| **is_truncated** | `BOOLEAN` | `NULLABLE` | `content` または `attributes` が BigQuery セルサイズ上限 (デフォルト 10MB) を超え、一部が破棄された場合は `true` です。 | `false` |
| **content_parts** | `RECORD` | `REPEATED` | マルチモーダルセグメント (Text, Image, Blob) の配列です。単純な JSON としてシリアライズできないコンテンツ (大きなバイナリや GCS 参照など) に使われます。 | `[{"mime_type": "text/plain", "text": "hello"}]` |

プラグインはテーブルが存在しない場合に自動作成します。ただし本番環境では、柔軟性のための **JSON** 型とマルチモーダルコンテンツのための **REPEATED RECORD** を活用する次の DDL を使って、手動でテーブルを作成することを推奨します。

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

### 自動生成されるビュー（1.27.0+）

`create_views=True`（1.27.0 以降のデフォルト）にすると、プラグインは共通の JSON 構造をフラットで型付きの列へ展開するイベントタイプ別ビューを自動生成します。これにより SQL が大幅に簡素化され、複雑な `JSON_VALUE` や `JSON_QUERY` 関数を明示的に書く必要がなくなります。

ビュー名は `{view_prefix}_{event_type_lowercase}` の規則に従います。たとえばデフォルト接頭辞 `"v"` を使うと、`LLM_REQUEST` は `v_llm_request` になります。同じデータセット内で複数のプラグインインスタンスが別テーブルへ書き込む場合は、`BigQueryLoggerConfig` の `view_prefix` をテーブルごとに変えて、ビュー名の衝突を避けてください。

```python
# 同じデータセットで異なる接頭辞を使う 2 つのプラグイン例
plugin_prod = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID,
    table_id="agent_events_prod",
    config=BigQueryLoggerConfig(view_prefix="v_prod"),
)
# 生成されるビュー例: v_prod_llm_request, v_prod_tool_completed, ...

plugin_staging = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID,
    table_id="agent_events_staging",
    config=BigQueryLoggerConfig(view_prefix="v_staging"),
)
# 生成されるビュー例: v_staging_llm_request, v_staging_tool_completed, ...
```

スキーマアップグレード後のようにビューを再生成したい場合は、公開非同期メソッド `await plugin.create_analytics_views()` を直接呼び出すこともできます。

すべてのビューには次の **共通カラム** が含まれます。`timestamp`, `event_type`, `agent`, `session_id`, `invocation_id`, `user_id`, `trace_id`, `span_id`, `parent_span_id`, `status`, `error_message`, `is_truncated`

次の表は、自動生成される 15 個のビューとイベント固有カラムを示しています。

| ビュー名 | イベント固有カラム |
|:---|:---|
| **`v_user_message_received`** | *(共通カラムのみ)* |
| **`v_llm_request`** | `model` (STRING), `request_content` (JSON), `llm_config` (JSON), `tools` (JSON) |
| **`v_llm_response`** | `response` (JSON), `usage_prompt_tokens` (INT64), `usage_completion_tokens` (INT64), `usage_total_tokens` (INT64), `total_ms` (INT64), `ttft_ms` (INT64), `model_version` (STRING), `usage_metadata` (JSON) |
| **`v_llm_error`** | `total_ms` (INT64) |
| **`v_tool_starting`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING) |
| **`v_tool_completed`** | `tool_name` (STRING), `tool_result` (JSON), `tool_origin` (STRING), `total_ms` (INT64) |
| **`v_tool_error`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING), `total_ms` (INT64) |
| **`v_agent_starting`** | `agent_instruction` (STRING) |
| **`v_agent_completed`** | `total_ms` (INT64) |
| **`v_invocation_starting`** | *(共通カラムのみ)* |
| **`v_invocation_completed`** | *(共通カラムのみ)* |
| **`v_state_delta`** | `state_delta` (JSON) |
| **`v_hitl_credential_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_hitl_confirmation_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_hitl_input_request`** | `tool_name` (STRING), `tool_args` (JSON) |

### イベントタイプとペイロード {#event-types}

`content` 列には、`event_type` ごとの **JSON** オブジェクトが格納されます。`content_parts` 列はコンテンツの構造化ビューを提供し、特に画像やオフロードされたデータで役立ちます。

!!! note "コンテンツ切り詰め"

    - 可変長コンテンツフィールドは `max_content_length` まで切り詰められます (`BigQueryLoggerConfig` で設定、デフォルト 500KB)。
    - `gcs_bucket_name` が設定されている場合、大きなコンテンツは切り詰められる代わりに GCS へオフロードされ、その参照が `content_parts.object_ref` に保存されます。

#### LLM インタラクション (プラグイン ライフサイクル)

これらのイベントは、LLM へ送信した生のリクエストと LLM から受信した応答を追跡します。

**1. LLM_REQUEST**

会話履歴とシステム指示を含む、モデルへ送信したプロンプトを記録します。

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

モデル出力とトークン使用量統計を記録します。

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

LLM 呼び出しが例外で失敗したときに記録されます。エラーメッセージが捕捉され、span がクローズされます。

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

#### ツール使用 (プラグイン ライフサイクル)

これらのイベントはエージェントによるツール実行を追跡します。各ツールイベントには、ツールの出自を分類する `tool_origin` フィールドが含まれます。

| Tool Origin | Description |
|:---|:---|
| `LOCAL` | `FunctionTool` インスタンス (ローカル Python 関数) |
| `MCP` | Model Context Protocol ツール (`McpTool` インスタンス) |
| `SUB_AGENT` | `AgentTool` インスタンス (サブエージェント) |
| `A2A` | リモート Agent-to-Agent インスタンス (`RemoteA2aAgent`) |
| `TRANSFER_AGENT` | `TransferToAgentTool` インスタンス |
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

ツール実行が例外で失敗したときに記録されます。ツール名、引数、tool origin、エラーメッセージを記録します。

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

これらのイベントは、通常はツールによって引き起こされるエージェント状態の変化を追跡します。

**7. STATE_DELTA**

エージェント内部状態の変化 (たとえばツールが更新したカスタムアプリケーション状態) を追跡します。

!!! note "組み込みマスキング"

    `temp:` または `secret:` プレフィックスを持つ状態キーは、記録された `state_delta` 内で自動的に `[REDACTED]` へマスクされます。詳しくは [組み込みマスキング](#built-in-redaction) を参照してください。

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

#### エージェントライフサイクルと汎用イベント

<table>
  <thead>
    <tr>
      <th><strong>イベントタイプ</strong></th>
      <th><strong>コンテンツ (JSON) 構造</strong></th>
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

#### Human-in-the-Loop (HITL) イベント {#hitl-events}

このプラグインは ADK の synthetic HITL ツール呼び出しを自動検出し、専用のイベントタイプを出力します。これらのイベントは通常の `TOOL_STARTING` / `TOOL_COMPLETED` イベントに **加えて** 記録されます。

認識される HITL ツール名は次のとおりです。

- `adk_request_credential` — ユーザー資格情報の要求 (例: OAuth トークン)
- `adk_request_confirmation` — 処理を進める前のユーザー確認要求
- `adk_request_input` — 自由形式ユーザー入力の要求

<table>
  <thead>
    <tr>
      <th><strong>イベントタイプ</strong></th>
      <th><strong>トリガー</strong></th>
      <th><strong>コンテンツ (JSON) 構造</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>HITL_CREDENTIAL_REQUEST</pre></p></td>
      <td>エージェントが <code>adk_request_credential</code> を呼び出す</td>
      <td><p><pre>{"tool": "adk_request_credential", "args": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_CREDENTIAL_REQUEST_COMPLETED</pre></p></td>
      <td>ユーザーが資格情報レスポンスを提供</td>
      <td><p><pre>{"tool": "adk_request_credential", "result": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_CONFIRMATION_REQUEST</pre></p></td>
      <td>エージェントが <code>adk_request_confirmation</code> を呼び出す</td>
      <td><p><pre>{"tool": "adk_request_confirmation", "args": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_CONFIRMATION_REQUEST_COMPLETED</pre></p></td>
      <td>ユーザーが確認レスポンスを提供</td>
      <td><p><pre>{"tool": "adk_request_confirmation", "result": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_INPUT_REQUEST</pre></p></td>
      <td>エージェントが <code>adk_request_input</code> を呼び出す</td>
      <td><p><pre>{"tool": "adk_request_input", "args": {...}}</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>HITL_INPUT_REQUEST_COMPLETED</pre></p></td>
      <td>ユーザーが入力レスポンスを提供</td>
      <td><p><pre>{"tool": "adk_request_input", "result": {...}}</pre></p></td>
    </tr>
  </tbody>
</table>

HITL リクエストイベントは `on_event_callback` 内の `function_call` パートから検出されます。HITL 完了イベントは `on_event_callback` と `on_user_message_callback` の両方にある `function_response` パートから検出されます。

!!! note "HITL イベント用ビュー"

    自動生成ビューは 3 つの **リクエスト** イベントタイプ (`v_hitl_credential_request`, `v_hitl_confirmation_request`, `v_hitl_input_request`) に対してのみ提供されます。3 つの `*_COMPLETED` イベントタイプはベーステーブルには記録されますが、専用ビューは作成されません。これらは `agent_events` テーブルで `WHERE event_type LIKE 'HITL_%_COMPLETED'` として直接照会してください。

#### GCS オフロード例 (マルチモーダルと大容量テキスト)

`gcs_bucket_name` を設定すると、大きなテキストやマルチモーダルコンテンツ (画像、音声など) は自動的に GCS へオフロードされます。`content` 列には概要またはプレースホルダーが保存され、`content_parts` には GCS URI を指す `object_ref` が保存されます。

**オフロードされたテキスト例**

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

**オフロードされた画像例**

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

**オフロード済みコンテンツを問い合わせる (署名付き URL の取得)**

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

### `trace_id` を使って特定の会話ターンを追跡

```sql
SELECT timestamp, event_type, agent, JSON_VALUE(content, '$.response') as summary
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE trace_id = 'your-trace-id'
ORDER BY timestamp ASC;
```

### トークン使用量分析

`v_llm_response` ビューを使う方法を推奨します。

```sql
SELECT
  AVG(usage_total_tokens) as avg_tokens,
  AVG(usage_prompt_tokens) as avg_prompt_tokens,
  AVG(usage_completion_tokens) as avg_completion_tokens
FROM `your-gcp-project-id.your-dataset-id.v_llm_response`;
```

または、ベーステーブルから JSON を直接抽出して照会することもできます。

```sql
SELECT
  AVG(CAST(JSON_VALUE(content, '$.usage.total') AS INT64)) as avg_tokens
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'LLM_RESPONSE';
```

### マルチモーダルコンテンツの問い合わせ (`content_parts` と `ObjectRef` を使用)

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

### BigQuery リモートモデル (Gemini) でマルチモーダルコンテンツを分析

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

### レイテンシ分析 (LLM とツール)

ビューを使う方法を推奨します。

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

または、ベーステーブルを使うこともできます。

```sql
SELECT
  event_type,
  AVG(CAST(JSON_VALUE(latency_ms, '$.total_ms') AS INT64)) as avg_latency_ms
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type IN ('LLM_RESPONSE', 'TOOL_COMPLETED')
GROUP BY event_type;
```

### Span 階層と duration 分析

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

### エラー分析 (LLM とツールのエラー)

ビューを使う方法を推奨します。

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

または、ベーステーブルを使って両方をまとめて分析することもできます。

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

### Tool Provenance 分析

`v_tool_completed` ビューを使う方法を推奨します。

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

または、ベーステーブルから `content` を直接抽出することもできます。

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

### HITL インタラクション分析

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


### 7. AI による根本原因分析 (Agent Ops)

BigQuery ML と Gemini を使って失敗したセッションを自動分析し、エラーの根本原因を特定します。

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


## BigQuery の会話型分析

[BigQuery Conversational Analytics](https://cloud.google.com/bigquery/docs/conversational-analytics) を使用すると、自然言語でエージェントログを分析できます。次のような質問に答える用途で利用できます。

*   "Show me the error rate over time"
*   "What are the most common tool calls?"
*   "Identify sessions with high token usage"

## Looker Studio ダッシュボード

用意済みの [Looker Studio Dashboard template](https://lookerstudio.google.com/c/reporting/f1c5b513-3095-44f8-90a2-54953d41b125/page/8YdhF) を使ってエージェント性能を可視化できます。

このダッシュボードを自分の BigQuery テーブルへ接続するには、次のリンク形式でプロジェクト、データセット、テーブル ID のプレースホルダーを実際の値へ置き換えて使ってください。

```text
https://lookerstudio.google.com/reporting/create?c.reportId=f1c5b513-3095-44f8-90a2-54953d41b125&ds.ds3.connector=bigQuery&ds.ds3.type=TABLE&ds.ds3.projectId=<your-project-id>&ds.ds3.datasetId=<your-dataset-id>&ds.ds3.tableId=<your-table-id>
```

## 機密資格情報のロギングを避ける {#security-credentials}

!!! warning "OAuth トークン、API キー、クライアントシークレットをログに残さないでください"

    BigQuery Agent Analytics プラグインは、ツール引数、LLM プロンプト、HITL 資格情報要求などの
    認証関連イベントを含む詳細なイベントペイロードをキャプチャします。エージェントが
    **認証済みツール** (たとえば OAuth2 を使う `AuthenticatedFunctionTool`) を使用している場合、
    プラグインは `client_secret`、`access_token`、API キーなどの機密値を BigQuery テーブルの
    `content` 列に記録してしまう可能性があります。

    これは既知の問題です
    ([google/adk-python#3845](https://github.com/google/adk-python/issues/3845))
    であり、分析データにおける資格情報漏えいにつながる可能性があります。

プラグインには一般的なシークレット値を自動保護する **組み込みマスキング** が含まれています。より細かな制御が必要な場合は、その上にカスタムマスキングを追加できます。

### 組み込みマスキング {#built-in-redaction}

プラグインは `content` または `attributes` の JSON 内に現れる次の既知キー名 (大文字小文字を区別しない) の値を自動的にマスクします。

`client_secret`, `access_token`, `refresh_token`, `id_token`, `api_key`, `password`

さらに、**`temp:`** または **`secret:`** プレフィックスを持つすべての状態キーは、記録された `state_delta` で自動的に `[REDACTED]` に置き換えられます。つまり、credential service がキャッシュした OAuth トークンのように `secret:` 名前空間に保存された ADK セッション状態は、BigQuery に永続化されません。

!!! info "追加設定は不要です"

    組み込みマスキングは、構造化 attributes と状態ログに対して常に有効で、ネストした辞書や attribute 値内の JSON 文字列にも再帰的に適用されます。カスタム `content_formatter` は生コンテンツに **先に** 適用されるため、自由形式ペイロードに埋め込まれたシークレット値を追加でマスクしたいときに使ってください。

### `content_formatter` で追加のシークレット値をマスクする

`BigQueryLoggerConfig` にカスタム `content_formatter` 関数を指定し、記録前に機密フィールドを削除またはマスクします。

```python
import json
import re
from typing import Any

SENSITIVE_KEYS = {"client_secret", "access_token", "refresh_token", "api_key", "secret"}

def redact_credentials(event_content: Any, event_type: str) -> str:
    """ログされたコンテンツから OAuth の秘密値とトークンをマスクします。"""
    if isinstance(event_content, dict):
        text = json.dumps(event_content)
    else:
        text = str(event_content)

    for key in SENSITIVE_KEYS:
        # JSON 風文字列の値をマスクします: "client_secret": "GOCSPX-xxx"
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

認証関連イベントを記録する必要がない場合は、それらを完全に除外できます。

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

-   **秘密情報をコードにハードコードしないでください。** OAuth クライアントシークレットや API キーは、
    環境変数や Google Cloud Secret Manager のようなシークレットマネージャーに保存してください。
-   **BigQuery テーブルへのアクセスを制限**し、ログデータを読める人を最小限に抑えてください。
-   **ログを定期的に監査**し、予期しない機密データが収集されていないか確認してください。

## フィードバック

BigQuery Agent Analytics に関するフィードバックを歓迎します。質問、提案、問題報告があれば bqaa-feedback@google.com までご連絡ください。

## 追加リソース

-   [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
-   [Introduction to Object Tables](https://docs.cloud.google.com/bigquery/docs/object-table-introduction)
-   [Interactive Demo Notebook](https://github.com/haiyuan-eng-google/demo_BQ_agent_analytics_plugin_notebook)
