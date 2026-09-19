---
catalog_title: BigQuery Agent Analytics Plugin
catalog_description: 動作分析とロギングのための詳細なエージェント分析
catalog_icon: /integrations/assets/bigquery.png
catalog_tags: ["observability", "google"]
---

# ADK 向け BigQuery Agent Analytics プラグイン

<div class="language-support-tag">
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v1.21.0</span><span class="lst-java">Java v1.5.0</span><span class="lst-kotlin">Kotlin v0.8.0</span>
</div>

BigQuery Agent Analytics プラグインは、エージェントの動作を詳細に分析するための堅牢なソリューションを提供することにより、Agent Development Kit（ADK）を大幅に強化します。ADK プラグインアーキテクチャと **BigQuery Storage Write API** を使用して、重要な運用イベントを Google BigQuery テーブルに直接キャプチャしてログに記録し、デバッグ、リアルタイム監視、および包括的なオフラインパフォーマンス評価のための高度な機能を提供します。

また、本プラグインは **自動スキーマアップグレード（Auto Schema Upgrade）**（既存テーブルへの新しい列の安全な追加）、**ツールの出所追跡（Tool Provenance）**（LOCAL、MCP、SUB_AGENT、A2A、TRANSFER_AGENT、TRANSFER_A2A）、ヒューマンインザループ（HITL）インタラクション向けの **HITL イベントトレース**、および **自動ビュー作成（Automatic View Creation）**（クエリしやすいフラットなイベントビューの生成）を提供します。

**ADK 2.0** マルチエージェントワークフローのサポートにより、エージェントのハンドオフ、状態チェックポイント、イベント圧縮（compaction）、および長時間実行ツールのトレースまで拡張されます。4 つの新しいイベントタイプ（`AGENT_TRANSFER`、`AGENT_STATE_CHECKPOINT`、`EVENT_COMPACTION`、`TOOL_PAUSED`）が追加されました。また、すべての行に `attributes.adk` エンベロープをスタンプするため、エージェントの実行グラフを再構築し、一時停止されたツールをそれを再開する行と結合できます。**Java** では、現在このサポートは `TOOL_PAUSED` イベントおよびその一時停止/再開ペアリングキーのみを対象としており（`attributes.adk` エンベロープは含みません）、詳細については [エージェントワークフローと一時停止/再開イベント（ADK 2.0）](#adk-2-events) を参照してください。

プラグインには 3 つの信頼性と可観測性の修正が含まれています（Java: v1.7.0 以降）:

- **クロスリージョン Storage Write API ルーティング:** `US` マルチリージョン以外（例: `EU` や `northamerica-northeast1`）の BigQuery データセットへの書き込みが、書き込みストリームを所有するリージョンにルーティングされるようになりました。以前は「session not found」/ stream-not-found エラーで失敗し、すべての行が暗黙的にドロップされる可能性がありました。
- **配信およびコンテンツインシデントの可観測性:** 配信損失が原因別に追跡されます。また、Python ではセンチネル行が書き込まれるフォーマッタおよびパーサーのエラーもカウントされます。これらのカウンタは `BigQueryAgentAnalyticsPlugin.get_drop_stats()`（Python）または `getDropStats()`（Java）を介して公開されるため、ホストがポーリングして独自のモニタリングにエクスポートできます。原因キーとセマンティクスは言語によって異なります。[ドロップされたイベントの可観測性](#dropped-event-observability) を参照してください。
- **Cloud Trace における重複スパンの防止:** Agent Engine テレメトリ（`GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true`）またはその他の Cloud Trace エクスポーターがグローバルトレーサープロバイダーに接続されている場合、プラグインは各フレームワークスパンの横に重複したスパンを生成しなくなりました。プラグインは依然として周囲の OTel スパンから `trace_id` を継承するため、BigQuery の行は Cloud Trace トレースとスムーズに結合されます。

Python v2.7.0 以降では、すべての行が書き込みキューに入る前に安定した `event_id` を受け取ります。この ID は Storage Write API の再試行全体で保持されるため、コンシューマは再試行による重複を識別できます。オプトインの `exactly_once_delivery` モードは、コミット済みストリームと明示的なオフセットを使用して、ライブプロセッサ内での曖昧な再試行による重複を防ぎます。このモードはロスレス配信を保証するものではありません。[配信と重複排除](#delivery-and-deduplication) を参照してください。

同じ Python リリースで、モデルとワークフローの終了詳細が追加されました。最終的な `LLM_RESPONSE` 行には `finish_reason` が含まれ、モデルから提供された場合はサニタイズされた `error_message` が含まれます。ワークフローノードは `NODE_OUTPUT` と `NODE_ERROR` を出力でき、未処理のエージェントまたは実行例外は `AGENT_ERROR` と `INVOCATION_ERROR` を出力します。

!!! warning "BigQuery Storage Write API"

    この機能は有料サービスである **BigQuery Storage Write API** を使用します。料金の詳細については、[BigQuery ドキュメント](https://cloud.google.com/bigquery/pricing?e=48754805&hl=ja#data-ingestion-pricing) を参照してください。

??? note "Kotlin のサポート"

    **Kotlin** プラグインは呼び出しライフサイクルイベントをログに記録します。呼び出しが開始されたときに `INVOCATION_STARTING` 行を書き込み、終了したときに `INVOCATION_COMPLETED` 行を書き込み、まだ存在しない場合は初回使用時にパーティション分割およびクラスタ化されたイベントテーブルを作成します。

    行は、Python や Java で使用される Storage Write API ではなく、呼び出しパス上で同期的に `tabledata.insertAll` を介して 1 行ずつ挿入されます。

    Kotlin では、LLM、ツール、エージェント、状態、HITL、A2A イベント、ADK 2.0 ワークフローイベント、自動ビュー作成、自動スキーマアップグレード、ツールの出所追跡、GCS オフロード、ドロップ統計は実装されていません。

## ユースケース

- **エージェントワークフローのデバッグと分析:** 広範な *プラグインライフサイクルイベント*（LLM 呼び出し、ツール使用状況）および *エージェント生成イベント*（ユーザー入力、モデル応答）を適切に定義されたスキーマにキャプチャします。
- **大量の分析とデバッグ:** 高スループットと低レイテンシを実現するために、Storage Write API を使用して非同期でロギング操作を実行します。
- **マルチモーダル分析:** テキスト、画像、その他のモダリティをログに記録して分析します。大きなファイルは GCS にオフロードされ、Object Tables 経由で BigQuery ML からアクセス可能になります。
- **分散トレース:** エージェントの実行フローを視覚化するために、OpenTelemetry スタイルのトレース（`trace_id`、`span_id`）をネイティブにサポートします。
- **ツールの出所追跡:** 各ツール呼び出しの出所（ローカル関数、MCP サーバー、サブエージェント、A2A リモートエージェント、または転送エージェント）を追跡します。
- **Human-in-the-Loop（HITL）トレース:** 認証情報リクエスト、確認プロンプト、およびユーザー入力リクエスト専用のイベントタイプを提供します。
- **エージェントワークフローのトレース（ADK 2.0）:** 実行グラフを再構築するための `attributes.adk` エンベロープとともに、エージェント転送、状態チェックポイント、イベント圧縮、および長時間実行ツールの一時停止/再開をキャプチャします。
- **クエリ可能なイベントビュー:** JSON ペイロードデータを unnest してダウンストリーム分析を簡素化する、イベントタイプごとのフラットな BigQuery ビュー（例: `v_llm_request`、`v_tool_completed`）を自動的に作成します。

### キャプチャされたイベントの概要

次の表は、プラグインが記録するすべてのイベントタイプの一覧です。詳細なペイロードの例については、[イベントタイプとペイロード](#event-types) を参照してください。**ビュー** 列はオプションの BigQuery ビューを示します。Python はデフォルトでビューを作成します。Java は `createViews(true)` が構成されている場合にのみビューを作成します。

**Kotlin** では、プラグインは `INVOCATION_STARTING` と `INVOCATION_COMPLETED` のみを記録し、ビューを作成しないため、他の行および **ビュー** 列全体は Python および Java に適用されます。

この表は、Python と Java のイベントセットの和集合です。`INVOCATION_ERROR`、`AGENT_ERROR`、`AGENT_TRANSFER`、`AGENT_STATE_CHECKPOINT`、`EVENT_COMPACTION`、`NODE_OUTPUT`、`NODE_ERROR` は Python 専用です。Java は `TOOL_PAUSED` を出力しますが、他のワークフロー固有のイベントは出力しません。残りの行は両方の言語に適用されます。

| イベントタイプ | キャプチャのタイミング | 主要なペイロードフィールド | ビュー |
| --- | --- | --- | --- |
| `USER_MESSAGE_RECEIVED` | ユーザーメッセージが呼び出しに入ったとき | テキスト要約 / コンテンツパーツ | `v_user_message_received` |
| `INVOCATION_STARTING` | 呼び出しが開始されたとき | *(共通列のみ)* | `v_invocation_starting` |
| `INVOCATION_COMPLETED` | 呼び出しが終了したとき | *(共通列のみ)* | `v_invocation_completed` |
| `INVOCATION_ERROR` | 呼び出しが未処理の例外で失敗したとき | エラーメッセージ、サニタイズされたトレースバック | `v_invocation_error` |
| `AGENT_STARTING` | エージェントの実行が開始されたとき | 指示の要約 | `v_agent_starting` |
| `AGENT_COMPLETED` | エージェントの実行が終了したとき | レイテンシ | `v_agent_completed` |
| `AGENT_ERROR` | エージェントの実行が未処理の例外で失敗したとき | エラーメッセージ、サニタイズされたトレースバック、レイテンシ | `v_agent_error` |
| `LLM_REQUEST` | モデルリクエストが送信されたとき | モデル、プロンプト、設定、ツール | `v_llm_request` |
| `LLM_RESPONSE` | モデル応答を受信したとき | 応答、使用トークン、キャッシュメタデータ、終了理由、レイテンシ、TTFT | `v_llm_response` |
| `LLM_ERROR` | モデル呼び出しが失敗したとき | エラーメッセージ、レイテンシ | `v_llm_error` |
| `TOOL_STARTING` | ツールが実行を開始したとき | ツール名、引数、出所 | `v_tool_starting` |
| `TOOL_COMPLETED` | ツールが成功したとき | ツール名、結果、出所、レイテンシ | `v_tool_completed` |
| `TOOL_ERROR` | ツールが失敗したとき | ツール名、引数、出所、エラー、レイテンシ | `v_tool_error` |
| `STATE_DELTA` | セッション状態が変更されたとき | 状態デルタ | `v_state_delta` |
| `HITL_CREDENTIAL_REQUEST` | 認証情報リクエストが出力されたとき | 合成ツール名、引数 | `v_hitl_credential_request` |
| `HITL_CONFIRMATION_REQUEST` | 確認リクエストが出力されたとき | 合成ツール名、引数 | `v_hitl_confirmation_request` |
| `HITL_INPUT_REQUEST` | ユーザー入力リクエストが出力されたとき | 合成ツール名、引数 | `v_hitl_input_request` |
| `HITL_CREDENTIAL_REQUEST_COMPLETED` | ユーザーが認証情報応答を提供したとき | 合成ツール名、結果 | *(ベーステーブルのみ)* |
| `HITL_CONFIRMATION_REQUEST_COMPLETED` | ユーザーが確認応答を提供したとき | 合成ツール名、結果 | *(ベーステーブルのみ)* |
| `HITL_INPUT_REQUEST_COMPLETED` | ユーザーが入力応答を提供したとき | 合成ツール名、結果 | *(ベーステーブルのみ)* |
| `A2A_INTERACTION` | リモート A2A 呼び出しが完了したとき | 応答、タスク ID、コンテキスト ID、リクエスト/レスポンス | `v_a2a_interaction` |
| `AGENT_RESPONSE` | 最終的なエージェント応答が生成されたとき | 応答（content）、ソースイベント ID/作成者/ブランチ（attributes） | `v_agent_response` |
| `AGENT_TRANSFER` | あるエージェントが別のエージェントに制御を渡したとき | 転送元エージェント、転送先エージェント、ソースイベント ID | `v_agent_transfer` |
| `AGENT_STATE_CHECKPOINT` | エージェントが状態のスナップショットを作成したとき（または実行終了をマークしたとき） | エージェント状態、エージェント終了フラグ、ソースイベント ID | `v_agent_state_checkpoint` |
| `EVENT_COMPACTION` | 一連のイベント期間が要約に圧縮されたとき | ウィンドウの開始/終了タイムスタンプ、圧縮されたコンテンツ | `v_event_compaction` |
| `TOOL_PAUSED` | 長時間実行ツール（または HITL リクエスト）が一時停止し、再開を待機しているとき | ツール名、引数、一時停止の種類、関数呼び出し ID | `v_tool_paused` |
| `NODE_OUTPUT` | ワークフローノードが最終的な構造化出力を出力したとき | 出力、ノードパス、実行 ID、親実行 ID | `v_node_output` |
| `NODE_ERROR` | ワークフローノードが非モデルエラーで終了したとき | エラーコード、エラーメッセージ、ノードパス、実行 ID、親実行 ID | `v_node_error` |

## インストール

Python の場合、専用の BigQuery Agent Analytics エクストラ（extra）を使用して ADK をインストールします。このエクストラには、プラグインに必要な BigQuery クライアント、Cloud Storage クライアント、および `pyarrow` が含まれています。

```bash
pip install "google-adk[bigquery-analytics]>=2.7.0"
```

`pyarrow` の依存関係は、一般的な `gcp` エクストラには含まれなくなりました。`pyarrow` が不足している場合、プラグインのインポートエラーによってインストールすべき `bigquery-analytics` エクストラが示されます。

## クイックスタート

=== "Python"

    エージェントの `App` オブジェクトにプラグインを追加します。前提条件については、
    [前提条件](#prerequisites) を参照してください。

    ```python title="agent.py"
    import os
    from google.adk.agents import Agent
    from google.adk.apps import App
    from google.adk.models.google_llm import Gemini
    from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin

    os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-gcp-project-id'
    os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'
    os.environ['GOOGLE_GENAI_USE_ENTERPRISE'] = 'True'

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

=== "Java"

    ランナーのプラグインリストにプラグインを追加します。前提条件については、
    [前提条件](#prerequisites) を参照してください。

    ```java title="Agent.java"
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.agents.RunConfig;
    import com.google.adk.models.Gemini;
    import com.google.adk.plugins.Plugin;
    import com.google.adk.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin;
    import com.google.adk.plugins.agentanalytics.BigQueryLoggerConfig;
    import com.google.adk.runner.InMemoryRunner;
    import com.google.common.collect.ImmutableList;

    public final class Agent {
      public static void main(String[] args) throws Exception {
        Plugin bqLoggingPlugin = new BigQueryAgentAnalyticsPlugin(
            BigQueryLoggerConfig.builder()
                .projectId("your-gcp-project-id")
                .datasetId("your-big-query-dataset-id")
                .tableName("agent_events") // Optional; default in v1.8.0+
                .build());

        InMemoryRunner runner = new InMemoryRunner(
            LlmAgent.builder()
                .model(Gemini.builder().modelName("gemini-2.5-flash").build())
                .name("my_agent")
                .instruction("You are a helpful assistant.")
                .build(),
            "my_agent",
            ImmutableList.of(bqLoggingPlugin));

        // Use runner ...

        // Close runner to flush and close plugin
        runner.close().blockingAwait();
      }
    }
    ```

=== "Kotlin"

    エージェントの `App` オブジェクトにプラグインを追加します。前提条件については、
    [前提条件](#prerequisites) を参照してください。 The plugin is JVM-only and ships outside
    core, so add the integrations artifact:

    ```kotlin title="build.gradle.kts"
    implementation("com.google.adk:google-adk-kotlin-integrations:1.0.0")
    ```

    ```kotlin title="BigQueryAnalyticsExample.kt"
    --8<-- "examples/kotlin/snippets/integrations/BigQueryAnalyticsExample.kt:quickstart"
    ```

    The plugin creates the events table on first use, so the credentials in
    scope need permission to create a table in the dataset, not only to insert
    rows. Set `location` to your dataset's location; it defaults to `"US"`. For
    the full set of options, see [Configuration
    options](#configuration-options).

    Logging never fails the turn: if the table cannot be created or a row cannot
    be inserted, the plugin logs the error and the invocation continues. When
    rows are missing, enable logging for
    `com.google.adk.kt.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin` —
    logs are emitted under that class name, not under the plugin's ADK name
    (`bigquery_agent_analytics`).


### Run and test agent

Test the plugin by running the agent and making a few requests through the chat
interface, such as "tell me what you can do" or "List datasets in my cloud
project <your-gcp-project-id>". These actions create events which are recorded
in your Google Cloud project BigQuery instance. Once these events have been
processed, you can view the data for them in the [BigQuery
Console](https://console.cloud.google.com/bigquery), using this query:

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

??? example "Full example with GCS offloading, OpenTelemetry, and BigQuery tools"

    === "Python"

        ```python title="my_bq_agent/agent.py"
        # my_bq_agent/agent.py
        import os
        import google.auth
        from google.adk.apps import App
        from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin, BigQueryLoggerConfig
        from google.adk.agents import Agent
        from google.adk.models.google_llm import Gemini
        from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig


        # --- OpenTelemetry note (no setup required for BQAA) ---
        # The BQAA plugin does NOT export OTel spans of its own. It tracks the
        # parent-child hierarchy on an internal stack: the root invocation span
        # reuses the ambient OTel span's id (as a 16-hex string) when one is
        # active, and child BQAA spans are generated internally as 16-hex
        # strings. The plugin's `trace_id`
        # column inherits from whichever OpenTelemetry span is active in the
        # surrounding runtime when the agent runs:
        #   * Agent Engine wires its invocation span automatically, so
        #     `trace_id` in BigQuery joins to Cloud Trace out of the box.
        #   * Locally, framework-instrumented runners open an invocation span
        #     for you.
        #   * If neither is available, the plugin falls back to a per-invocation
        #     trace_id and the parent-child hierarchy is still preserved in
        #     BigQuery; no OTel setup needed.
        # Setting a bare `TracerProvider` with no ambient span will NOT cause
        # `trace_id` to be populated with a "real" OTel id; only an *active*
        # span does. See the "Tracing and observability" section for details.

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
        os.environ['GOOGLE_GENAI_USE_ENTERPRISE'] = 'True'

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

    === "Java"

        ```java
        package adk.plugins.agentanalytics.demo;

        import static java.nio.charset.StandardCharsets.UTF_8;
        import static java.util.Collections.singletonList;

        import com.google.adk.agents.LlmAgent;
        import com.google.adk.agents.RunConfig;
        import com.google.adk.events.Event;
        import com.google.adk.models.Gemini;
        import com.google.adk.plugins.Plugin;
        import com.google.adk.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin;
        import com.google.adk.plugins.agentanalytics.BigQueryLoggerConfig;
        import com.google.adk.runner.InMemoryRunner;
        import com.google.adk.sessions.Session;
        import com.google.adk.tools.FunctionTool;
        import com.google.adk.tools.ToolContext;
        import com.google.genai.types.Content;
        import com.google.genai.types.GenerateContentConfig;
        import com.google.genai.types.Part;
        import io.opentelemetry.sdk.OpenTelemetrySdk;
        import io.opentelemetry.sdk.common.CompletableResultCode;
        import io.opentelemetry.sdk.trace.SdkTracerProvider;
        import io.opentelemetry.sdk.trace.data.SpanData;
        import io.opentelemetry.sdk.trace.export.SimpleSpanProcessor;
        import io.opentelemetry.sdk.trace.export.SpanExporter;
        import io.reactivex.rxjava3.core.Flowable;
        import java.util.Collection;
        import java.util.Scanner;

        /** Demo agent showing how to use BigQueryAgentAnalyticsPlugin. */
        public final class BqDemoAgent {
          private static final String PROJECT_ID = "your-gcp-project-id";
          private static final String DATASET_ID = "your-gcp-dataset_id";
          private static final String TABLE_ID = "your-gcp-table";
          private static final String GCS_BUCKET_NAME = "your-gcs-bucket-name";
          private static final String API_KEY = "your-api_key";

          // A simple tool to demonstrate tool execution logging
          public static String reverseString(String input, ToolContext toolContext) {
            return new StringBuilder(input).reverse().toString();
          }

          public static void main(String[] args) throws Exception {
            // 0. Initialize OpenTelemetry
            initOpenTelemetry();

            // 1. Configure the BigQuery Logger
            BigQueryLoggerConfig config =
                BigQueryLoggerConfig.builder()
                    .projectId(PROJECT_ID)
                    .datasetId(DATASET_ID)
                    .tableName(TABLE_ID)
                    .gcsBucketName(GCS_BUCKET_NAME)
                    .createViews(true)
                    .build();

            // 2. Create the plugin instance
            Plugin bqLoggingPlugin = new BigQueryAgentAnalyticsPlugin(config);

            // 3. Initialize the model (Gemini)
            Gemini model =
                Gemini.builder()
                    .modelName("gemini-3-flash-preview") // Use appropriate model
                    .apiKey(API_KEY)
                    .build();

            // 4. Create the agent with the tool and plugin
            LlmAgent agent =
                LlmAgent.builder()
                    .model(model)
                    .name("bq_demo_agent")
                    .instruction(
                        "You are a helpful assistant. You have a tool 'reverseString' that you can use to"
                            + " reverse text.")
                    .tools(FunctionTool.create(BqDemoAgent.class, "reverseString"))
                    .generateContentConfig(GenerateContentConfig.builder().temperature(0.5f).build())
                    .build();

            // 5. Initialize the runner
            InMemoryRunner runner =
                new InMemoryRunner(agent, "bq_demo_agent", singletonList(bqLoggingPlugin));

            // 6. Create a session
            Session session =
                runner.sessionService().createSession(runner.appName(), "demo_user").blockingGet();

            RunConfig runConfig = RunConfig.builder().build();

            System.out.println("Agent ready. Type 'quit' to exit.");

            try (Scanner scanner = new Scanner(System.in, UTF_8)) {
              while (true) {
                System.out.print("\nUser: ");
                String userInput = scanner.nextLine();
                if (userInput.trim().equalsIgnoreCase("quit")) {
                  break;
                }

                Content userMsg = Content.fromParts(Part.fromText(userInput));

                // Run the agent and stream events
                Flowable<Event> events =
                    runner.runAsync(session.userId(), session.id(), userMsg, runConfig);

                System.out.print("Agent: ");
                events.blockingForEach(
                    event -> {
                      if (event.finalResponse()) {
                        System.out.println(event.stringifyContent());
                      }
                    });
              }
            } finally {
              System.out.println("Closing runner (flushing remaining logs)...");
              runner.close().blockingAwait();
              System.out.println("Done.");
            }
          }

          private static void initOpenTelemetry() {
            PrintingSpanExporter exporter = new PrintingSpanExporter();
            SdkTracerProvider tracerProvider =
                SdkTracerProvider.builder().addSpanProcessor(SimpleSpanProcessor.create(exporter)).build();
            OpenTelemetrySdk.builder().setTracerProvider(tracerProvider).buildAndRegisterGlobal();
          }

          private static class PrintingSpanExporter implements SpanExporter {
            @Override
            public CompletableResultCode export(Collection<SpanData> spans) {
              for (SpanData span : spans) {
                System.out.println("--- Span: " + span.getName() + " ---");
                System.out.println("  TraceId: " + span.getTraceId());
                System.out.println("  SpanId: " + span.getSpanId());
                System.out.println("  ParentSpanId: " + span.getParentSpanId());
                System.out.println("  Attributes: " + span.getAttributes());
                System.out.println("------------------------");
              }
              return CompletableResultCode.ofSuccess();
            }

            @Override
            public CompletableResultCode flush() {
              return CompletableResultCode.ofSuccess();
            }

            @Override
            public CompletableResultCode shutdown() {
              return CompletableResultCode.ofSuccess();
            }
          }

          private BqDemoAgent() {}
        }
        ```

!!! tip "Agent Runtime にデプロイしますか？"

    [Agent Runtime にデプロイ](#deploy-agent-runtime) を参照してください。

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

=== "Python"

    ### コンストラクタパラメータ

    `BigQueryAgentAnalyticsPlugin` コンストラクタは次のパラメータを受け入れます。また、`**kwargs` も受け入れ、これらは `BigQueryLoggerConfig` に直接転送されます（下記参照）。

    | パラメータ | 型 | デフォルト値 | 使用するタイミング |
    | --- | --- | --- | --- |
    | `project_id` | `str` | *(必須)* | Google Cloud プロジェクトを選択 |
    | `dataset_id` | `str` | *(必須)* | BigQuery データセットを選択 |
    | `table_id` | `Optional[str]` | `None` | カスタムテーブル名を使用（config の `table_id` をオーバーライド） |
    | `config` | `Optional[BigQueryLoggerConfig]` | `None` | 詳細なチューニングのための構成オブジェクトを渡す |
    | `location` | `str` | `"US"` | BigQuery データセットのロケーションに一致（例: `"US"`, `"EU"`, `"us-central1"`） |
    | `credentials` | `Optional[google.auth.credentials.Credentials]` | `None` | [ADC](https://cloud.google.com/docs/authentication/application-default-credentials) の代わりに明示的なサービスアカウント、偽装、またはクロスプロジェクトの認証情報を使用 |

    ```python
    plugin = BigQueryAgentAnalyticsPlugin(
        project_id="my-project",
        dataset_id="my_dataset",
        batch_size=10,           # BigQueryLoggerConfig に転送
        shutdown_timeout=5.0,    # BigQueryLoggerConfig に転送
    )
    ```

    ### BigQueryLoggerConfig オプション

    以下のオプションはすべてオプションであり、適切なデフォルト値が設定されています。これらを `BigQueryLoggerConfig` またはプラグインコンストラクタの `**kwargs` として渡します。

    | オプション | 型 | デフォルト値 | 説明 |
    | --- | --- | --- | --- |
    | `enabled` | `bool` | `True` | ロギングを一時的に無効化 |
    | `table_id` | `str` | `"agent_events"` | カスタム BigQuery テーブル名を指定 |
    | `clustering_fields` | `List[str]` | `["event_type", "agent", "user_id"]` | 作成時のテーブルクラスタ化フィールドをカスタマイズ |
    | `gcs_bucket_name` | `Optional[str]` | `None` | 大きなテキストやマルチモーダルコンテンツを GCS にオフロード |
    | `connection_id` | `Optional[str]` | `None` | GCS コンテンツをクエリするための BigQuery ObjectRef / オブジェクトテーブルを使用 |
    | `max_content_length` | `int` | `500 * 1024` | オフロード/切り詰め前のインラインペイロードサイズ（バイト）を制御 |
    | `batch_size` | `int` | `1` | 書き込みスループットとレイテンシのバランスを調整（デフォルトの 1 は低レイテンシ向け、高スループットの場合は増やす） |
    | `batch_flush_interval` | `float` | `1.0` | 部分バッチを定期的にフラッシュ（秒） |
    | `shutdown_timeout` | `float` | `10.0` | シャットダウン時に最終フラッシュを待機する時間（秒） |
    | `event_allowlist` | `Optional[List[str]]` | `None` | 選択したイベントタイプのみをログに記録 |
    | `event_denylist` | `Optional[List[str]]` | `None` | 機密性の高いイベントタイプやノイズの多いイベントタイプをスキップ |
    | `content_formatter` | `Optional[Callable]` | `None` | イベントごとにカスタムマスキング/フォーマットを適用（シークレットの墨消しなど） |
    | `log_multi_modal_content` | `bool` | `True` | GCS 参照を含む `content_parts` の詳細をキャプチャ |
    | `queue_max_size` | `int` | `10000` | メモリ内のイベントキューサイズを制限 |
    | `retry_config` | `Optional[RetryConfig]` | `None` | 再試行動作を調整 |
    | `log_session_metadata` | `bool` | `True` | `attributes` にセッション情報を追加（`session_id`, `app_name`, `user_id`, `state`）。`temp:` プレフィックスのキーは[墨消し](#built-in-redaction)されます。 |
    | `custom_tags` | `Dict[str, Any]` | `{}` | すべてのイベントの `attributes` に静的タグ（例: `{"env": "prod"}`）を追加 |
    | `auto_schema_upgrade` | `bool` | `True` | 既存のテーブルに新しい列を自動追加（追加のみ） |
    | `create_views` | `bool` | `True` | イベントタイプごとの BigQuery ビューを作成 |
    | `view_prefix` | `str` | `"v"` | 複数のプラグインがデータセットを共有する場合のビュー名衝突を防止（例: `"v_staging"`） |
    | `enable_otel_correlation` | `bool` | `False` | ベストエフォートの Cloud Trace 結合キーとして周囲の OpenTelemetry スパンコンテキストを `attributes.otel.{span_id, trace_id}` にキャプチャ |
    | `custom_metadata_allowlist` | `Optional[List[str]]` | `None` | 選択した `event.custom_metadata` キーを `attributes.custom_metadata.*` にキャプチャ: 正確なキーまたは `"prefix*"` パターン |
    | `payload_column_denylist` | `Optional[List[str]]` | `None` | 書き込み時にテーブルからペイロード列（`content`, `content_parts`, `attributes`, `latency_ms`）を除外射影 |
    | `final_response_tool_names` | `FrozenSet[str]` | `frozenset()` | 成功した選択ツールの呼び出し引数を `AGENT_RESPONSE` ペイロードとしてログ記録 |
    | `flush_on_run_end` | `bool` | `True` | 各実行の終了時にキューに入っている行の書き込み完了を待機 |
    | `exactly_once_delivery` | `bool` | `False` | コミット済みストリームと明示的なオフセットを使用して、ライブプロセッサ内での曖昧な再試行による重複を防止 |

    次のコードサンプルは、BigQuery Agent Analytics プラグインの構成を定義する方法を示しています。

    ```python
    import json
    import re
    from typing import Any

    from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryLoggerConfig

    def redact_dollar_amounts(event_content: Any, event_type: str) -> str:
        """
        ドル金額（例: $600, $12.50）を墨消しし、
        入力が辞書の場合は JSON 出力を保証するカスタムフォーマッタ。

        Args:
            event_content: イベントの未加工コンテンツ。
            event_type: イベントタイプ文字列（例: "LLM_REQUEST", "LLM_RESPONSE"）。
        """
        text_content = ""
        if isinstance(event_content, dict):
            text_content = json.dumps(event_content)
        else:
            text_content = str(event_content)

        # ドル金額の正規表現: $ の後に数字が続き、オプションでカンマや小数点が含まれる
        # 例: $600, $1,200.50, $0.99
        redacted_content = re.sub(r'\$\d+(?:,\d{3})*(?:\.\d+)?', 'xxx', text_content)

        return redacted_content

    config = BigQueryLoggerConfig(
        enabled=True,
        event_allowlist=["LLM_REQUEST", "LLM_RESPONSE"], # これらのイベントのみ記録
        # event_denylist=["TOOL_STARTING"], # これらのイベントをスキップ
        shutdown_timeout=10.0, # 終了時にログフラッシュを最大 10 秒待機
        max_content_length=500, # コンテンツを 500 文字に切り詰め
        content_formatter=redact_dollar_amounts, # ロギングコンテンツ内のドル金額を墨消し
        queue_max_size=10000, # メモリ内に保持する最大イベント数
        auto_schema_upgrade=True, # 既存テーブルに新しい列を自動追加
        create_views=True, # イベントタイプごとのビューを自動作成
        # retry_config=RetryConfig(max_retries=3), # オプション: 再試行の構成
    )

    plugin = BigQueryAgentAnalyticsPlugin(
        project_id="my-project",
        dataset_id="my_dataset",
        config=config,
    )
    ```

    ### トレース相関、メタデータキャプチャ、および列射影

    <div class="language-support-tag">
      <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v2.4.0</span>
    </div>

    3 つのオプションが、`attributes` に追加されるコンテキストと、ペイロード列をテーブルに書き込むかどうかを制御します。各オプションは上記の `BigQueryLoggerConfig` オプション表に記載されています。以下の注意点は、フラットな表では表現できないクロスオプションのルールを補足するものです。

    - **`enable_otel_correlation`**: キャプチャされたスパンコンテキストは外部キーではなくベストエフォートの Cloud Trace 相関キーです。無効（デフォルト）の場合、`attributes.otel` は書き込まれません。
    - **`custom_metadata_allowlist`**: 設定しない場合、組み込みの `a2a:*` キャプチャのみが実行される従来の動作が維持されます。キャプチャされた値は、他のすべてのログコンテンツと同じ安全性パイプライン（切り詰め、機密キーの墨消し、循環参照の処理）を通過します。
    - **`payload_column_denylist`**: `content`、`content_parts`、`attributes`、`latency_ms` のみを指定できます。識別列および相関列は保護されており、指定すると `ValueError` が発生します。射影はスキーマ優先で適用されるため、テーブルスキーマ、書き込まれた行、および自動作成されたビューの一貫性が維持されます（ビューは拒否された列に依存する派生列を削除します）。`attributes` を拒否すると `attributes.otel` および `attributes.custom_metadata` も無効になり、空でない `custom_metadata_allowlist` と組み合わせると構築時に拒否されます。

    ```python
    config = BigQueryLoggerConfig(
        enable_otel_correlation=True,                      # Cloud Trace との結合キー
        custom_metadata_allowlist=["ticket_id", "exp:*"],  # 選択した custom_metadata キーをキャプチャ
        # payload_column_denylist=["content_parts"],       # マルチモーダルペイロードを永続化しない
    )
    ```

    ### 最終回答のキャプチャと実行終了時のフラッシュ

    エージェントがプレーンテキストの最終イベントを出力するのではなく専用ツールの呼び出しによって最終回答を提供する場合、`final_response_tool_names` を使用します。一致するツール呼び出しが成功すると、プラグインはツールの呼び出し引数を `AGENT_RESPONSE` 行として書き込み、`attributes` に `source_tool` を追加します。

    `flush_on_run_end` オプションのデフォルトは `True` であり、これにより `after_run_callback` は現在のイベントループの書き込みキューを待機します。応答パスからこのフラッシュを削除するには `False` に設定します。バックグラウンドライターはキューの排出を継続するため、実行が返されてから少し後に BigQuery に行が表示される場合があります。

    ```python
    config = BigQueryLoggerConfig(
        final_response_tool_names=frozenset({"submit_final_response"}),
        flush_on_run_end=False,
    )
    ```

    ### 配信と重複排除 {#delivery-and-deduplication}

    <div class="language-support-tag">
      <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v2.7.0</span>
    </div>

    すべての行は、エンキュー前に 32 文字の 16 進数 `event_id` を受け取ります。Storage Write API がその行を再試行する際にも同じ ID が再利用されるため、デフォルトの配信モードでの重複排除キーとして機能します。

    ```sql
    SELECT *
    FROM `your-gcp-project-id.adk_agent_logs.agent_events`
    QUALIFY
      event_id IS NULL
      OR ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY timestamp) = 1;
    ```

    `event_id IS NULL` 条件は、列が導入される前に書き込まれた行を保持します。

    ループローカルなコミット済みストリームと明示的なオフセットを使用するには、`exactly_once_delivery=True` を設定します。これにより、最初の結果が曖昧だった再試行が、そのプロセッサの存続期間内に重複を作成するのを防ぎます。ストリームのローテーションが必要な場合、追加の BigQuery `CreateWriteStream` クォータを消費する可能性があります。

    ```python
    config = BigQueryLoggerConfig(exactly_once_delivery=True)
    ```

    その名前に反して、このオプションはロスレス配信を保証するものではありません。再試行の枯渇、オフセットの競合、または置換ストリームの失敗の後でも、バッチがドロップされる可能性があります。ストリームローテーションに失敗した後、30 秒のローテーションバックオフ中に到着したイベントもドロップされます。`offset_conflict` やその他の[ドロップ理由](#dropped-event-observability)を監視し、コンシューマ側の重複排除キーとして `event_id` を維持してください。

=== "Java"

    Java では、すべての構成は `BigQueryLoggerConfig` ビルダーを介して管理されます。

    #### BigQueryLoggerConfig Builder オプション

    | ビルダーメソッド | 型 | デフォルト値 | 説明 |
    | --- | --- | --- | --- |
    | `enabled(boolean)` | `boolean` | `true` | ロギングを一時的に無効化 |
    | `projectId(String)` | `String` | *(必須)* | Google Cloud プロジェクトを選択 |
    | `datasetId(String)` | `String` | *(必須)* | BigQuery データセットを選択 |
    | `tableName(String)` | `String` | `"agent_events"` | カスタムテーブル名を使用 |
    | `location(String)` | `String` | `"us"` | BigQuery データセットのロケーションに一致 |
    | `clusteringFields(List<String>)` | `List<String>` | `["event_type", "agent", "user_id"]` | 作成時のテーブルクラスタ化をカスタマイズ |
    | `gcsBucketName(String)` | `String` | `""` | 大きなテキストやマルチモーダルコンテンツを GCS にオフロード |
    | `connectionId(String)` | `String` | `null` | BigQuery ObjectRef / オブジェクトテーブルを使用 |
    | `maxContentLength(int)` | `int` | `500 * 1024` | オフロード/切り詰め前のインラインペイロードサイズを制御 |
    | `batchSize(int)` | `int` | `1` | 書き込みスループットとレイテンシのバランスを調整 |
    | `batchFlushInterval(Duration)` | `Duration` | `Duration.ofSeconds(1)` | 部分バッチを定期的にフラッシュ |
    | `shutdownTimeout(Duration)` | `Duration` | `Duration.ofSeconds(10)` | シャットダウン時に最終フラッシュを待機 |
    | `eventAllowlist(List<String>)` | `List<String>` | `[]` | 選択したイベントタイプのみを記録 |
    | `eventDenylist(List<String>)` | `List<String>` | `[]` | 機密性の高いイベントタイプやノイズの多いイベントタイプをスキップ |
    | `contentFormatter(BiFunction)` | `BiFunction<Object, String, Object>` | `null` | イベントごとにカスタムマスキング/フォーマットを適用 |
    | `logMultiModalContent(boolean)` | `boolean` | `true` | GCS 参照を含む `content_parts` の詳細をキャプチャ |
    | `queueMaxSize(int)` | `int` | `10000` | メモリ内のイベントキューサイズを制限 |
    | `retryConfig(RetryConfig)` | `RetryConfig` | `RetryConfig.builder().build()` | 再試行動作を調整 |
    | `logSessionMetadata(boolean)` | `boolean` | `true` | `attributes` にセッション情報を追加 |
    | `customTags(Map<String, Object>)` | `Map<String, Object>` | `{}` | すべてのイベントの `attributes` に静的タグを追加 |
    | `autoSchemaUpgrade(boolean)` | `boolean` | `true` | 既存テーブルに新しい列を自動追加 |
    | `createViews(boolean)` | `boolean` | `false` | イベントタイプごとの BigQuery ビューを作成（注: Python の `true` と異なり、デフォルトは `false`） |
    | `viewPrefix(String)` | `String` | `"v"` | ビュー名の衝突を防止 |
    | `credentials(Credentials)` | `Credentials` | `null` | 明示的なサービスアカウントの認証情報を使用 |

    Java v1.8.0 以降では、`datasetId` が必須であり、`tableName` のデフォルト値は `"agent_events"` です。Java v1.7.0 以前では、これらのデフォルト値はそれぞれ `"agent_analytics"` および `"events"` でした。

    次のコードサンプルは、Java で BigQuery Agent Analytics プラグインの構成を定義する方法を示しています。

    ```java
    import com.google.adk.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin;
    import com.google.adk.plugins.agentanalytics.BigQueryLoggerConfig;
    import java.time.Duration;
    import java.util.function.BiFunction;

    // ドル金額を墨消しするカスタムフォーマッタ
    BiFunction<Object, String, Object> redactDollarAmounts = (content, eventType) -> {
      String textContent = content.toString();
      return textContent.replaceAll("\$\d+(?:,\d{3})*(?:\.\d+)?", "xxx");
    };

    BigQueryLoggerConfig config = BigQueryLoggerConfig.builder()
        .enabled(true)
        .projectId("my-project")
        .datasetId("my_dataset")
        .tableName("agent_events")
        .batchSize(1)
        .batchFlushInterval(Duration.ofMillis(500))
        .contentFormatter(redactDollarAmounts)
        .autoSchemaUpgrade(true)
        .createViews(true)
        .build();

    BigQueryAgentAnalyticsPlugin plugin = new BigQueryAgentAnalyticsPlugin(config);
    ```

=== "Kotlin"

    Kotlin では、すべての構成はプラグインの唯一の必須引数として渡される `BigQueryLoggerConfig` データクラスを介して管理されます。

    #### BigQueryLoggerConfig プロパティ

    | オプション | 型 | デフォルト値 | 使用するタイミング |
    | --- | --- | --- | --- |
    | `projectId` | `String` | *(必須)* | Google Cloud プロジェクトを選択 |
    | `datasetId` | `String` | *(必須)* | BigQuery データセットを選択 |
    | `enabled` | `Boolean` | `true` | ロギングを一時的に無効化 |
    | `location` | `String` | `"US"` | BigQuery データセットのロケーションに一致（例: `"EU"` または `"us-central1"`） |
    | `tableName` | `String` | `"agent_events"` | カスタムテーブル名を使用 |
    | `credentials` | `Credentials?` | `null` | [ADC](https://cloud.google.com/docs/authentication/application-default-credentials) の代わりに明示的なサービスアカウントの認証情報を使用 |

    次のコードサンプルは、Kotlin で BigQuery Agent Analytics プラグインの構成を定義する方法を示しています。

    ```kotlin
    import com.google.adk.kt.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin
    import com.google.adk.kt.plugins.agentanalytics.BigQueryLoggerConfig

    val config =
        BigQueryLoggerConfig(
            projectId = "my-project",
            datasetId = "my_dataset",
            location = "EU",
            tableName = "agent_events",
        )

    val plugin = BigQueryAgentAnalyticsPlugin(config = config)
    ```

    バッチ処理、コンテンツフォーマット、イベント許可リスト、GCS オフロード、ビュー作成など、**Python** および **Java** タブに記載されているオプションは Kotlin には存在しません。

## スキーマと本番環境セットアップ

### スキーマリファレンス

イベントテーブル（`agent_events`）は柔軟なスキーマを使用します。次の表は、サンプル値を含む包括的なリファレンスを提供します。

| フィールド名 | 型 | モード | 説明 | サンプル値 |
| --- | --- | --- | --- | --- |
| **timestamp** | `TIMESTAMP` | `REQUIRED` | イベント作成の UTC タイムスタンプ。プライマリソートキーおよび日次パーティションキーとして機能します。精度はマイクロ秒です。 | `2026-02-03 20:52:17 UTC` |
| **event_id** | `STRING` | `NULLABLE` | エンキュー前に割り当てられた 32 文字の 16 進数 ID。コンシューマが重複行を識別できるように、Storage Write API の再試行全体で保持されます。スキーマバージョン 2 より前に書き込まれた行は `NULL` です。 | `ca5e3c9d99e24e46b614f2f44f93bf6e` |
| **event_type** | `STRING` | `NULLABLE` | 正規のイベントカテゴリ。[イベントタイプとペイロード](#event-types) で説明されている LLM、ツール、エージェント、呼び出し、状態、HITL、A2A、レスポンス、ワークフロー、ノード出力、ノードエラーイベントなどの標準値が含まれます。高レベルのフィルタリングに使用されます。 | `LLM_REQUEST` |
| **agent** | `STRING` | `NULLABLE` | このイベントを担当するエージェントの名前。エージェントの初期化中または `root_agent_name` コンテキストを介して定義されます。 | `my_bq_agent` |
| **session_id** | `STRING` | `NULLABLE` | 会話スレッド全体の永続的な識別子。複数のターンやサブエージェント呼び出しにわたって一定に保たれます。 | `04275a01-1649-4a30-b6a7-5b443c69a7bc` |
| **invocation_id** | `STRING` | `NULLABLE` | セッション内の個々のエージェント実行またはターンのユニークな識別子。 | `81014e7a-90da-4cb0-adbf-cb6d53955685` |
| **user_id** | `STRING` | `NULLABLE` | 現在のセッションに関連付けられているユーザーの識別子。ユーザーごとの分析に役立ちます。 | `user_12345` |
| **trace_id** | `STRING` | `NULLABLE` | 32 文字の 16 進数トレース ID。アクティブな場合は周囲の OpenTelemetry スパンから継承され、それ以外の場合はプラグインによって呼び出しごとに生成されます。 | `4bf92f3577b34da6a3ce929d0e0e4736` |
| **span_id** | `STRING` | `NULLABLE` | この特定の操作に対する 16 文字の 16 進数スパン ID。プラグインの内部スタックで追跡されます。ルート呼び出しスパンは周囲の OTel スパン ID を再利用でき、子 BQAA スパンは内部で生成されます。OpenTelemetry スパンは作成もエクスポートもされません。 | `00f067aa0ba902b7` |
| **parent_span_id** | `STRING` | `NULLABLE` | 直前の呼び出し元の 16 文字の 16 進数スパン ID。親子実行ツリーを再構築するために使用されます。 | `5fb397be34d23b0f` |
| **content** | `JSON` | `NULLABLE` | JSON として保存されるイベント固有のデータ（ペイロード）。構造はイベントタイプによって異なります。 | `{"model": "gemini-flash-latest", ...}` |
| **content_parts** | `ARRAY<STRUCT>` | `REPEATED` | 構造化パーツの配列。テキストチャンク、GCS に保存されているファイルへの URI/ObjectRef（ストレージオフロード用）、MIME タイプ、パーツメタデータをキャプチャします。 | `[{mime_type: "image/png", uri: "gs://..."}]` |
| **attributes** | `JSON` | `NULLABLE` | 追加メタデータ（例: `root_agent_name`、`model_version`、`usage_metadata`、`session_metadata`、`custom_tags`）のための任意のキー値ペア。 | `{"model_version": "gemini-flash-latest", ...}` |
| **latency_ms** | `JSON` | `NULLABLE` | レイテンシ測定値（例: 合計ミリ秒数である `total_ms`）。 | `{"total_ms": 1250}` |
| **status** | `STRING` | `NULLABLE` | イベントの結果。通常は 'OK' または 'ERROR' です。 | `OK` |
| **error_message** | `STRING` | `NULLABLE` | サニタイズされたエラーまたはモデル終了診断メッセージ。 | `ResourceExhausted: Quota exceeded` |
| **is_truncated** | `BOOLEAN` | `NULLABLE` | インラインコンテンツが `max_content_length` 制限を超えて切り詰められたかどうかを示すフラグ。 | `false` |

??? example "本番環境向け BigQuery DDL（手動作成用）"

    プラグインに自動的にテーブルを作成させる代わりに、本番環境の要件に合わせてカスタムパーティショニング、クラスタリング、および列レベルのセキュリティを適用してテーブルを事前プロビジョニングできます。

    ```sql
    CREATE TABLE IF NOT EXISTS `your-gcp-project-id.your-big-query-dataset-id.agent_events`
    (
      timestamp TIMESTAMP OPTIONS(description="UTC timestamp of event creation. Acts as the primary ordering key and the daily partitioning key."),
      event_id STRING OPTIONS(description="32-char hex ID assigned before enqueue; preserved across Storage Write API retries for consumer deduplication."),
      event_type STRING OPTIONS(description="The canonical category of the event."),
      agent STRING OPTIONS(description="The name of the agent responsible for this event."),
      session_id STRING OPTIONS(description="A persistent identifier for the entire conversation thread."),
      invocation_id STRING OPTIONS(description="A unique identifier for each individual agent execution or turn within a session."),
      user_id STRING OPTIONS(description="The identifier of the user associated with the current session."),
      trace_id STRING OPTIONS(description="32-char hex trace ID. Inherited from the ambient OpenTelemetry span when one is active; otherwise generated per invocation by the plugin."),
      span_id STRING OPTIONS(description="16-char hex span ID for this specific operation. Tracked on the plugin's internal stack; the root invocation span may reuse the ambient OTel span id, while child BQAA spans are generated internally. No OpenTelemetry span is created or exported."),
      parent_span_id STRING OPTIONS(description="16-char hex span ID of the immediate caller, used to reconstruct the parent-child execution tree."),
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
      error_message STRING OPTIONS(description="Sanitized error or model termination diagnostic."),
      is_truncated BOOLEAN OPTIONS(description="Flag indicates if content was truncated.")
    )
    PARTITION BY DATE(timestamp)
    CLUSTER BY event_type, agent, user_id;
    ```

### 自動作成されるビュー

<div class="language-support-tag">
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v1.27.0</span><span class="lst-java">Java v1.5.0</span>
</div>

Python では、`create_views=True`（デフォルト）により各イベントタイプのビューが自動生成されます。Java では `createViews(true)` を設定します（デフォルトは `false`）。Kotlin はビューを作成しません。ビューは一般的な JSON 構造をフラットな型付き列に unnest するため、反復的な `JSON_VALUE` および `JSON_QUERY` 式を記述する必要がなくなります。

ビュー名は `{view_prefix}_{event_type_lowercase}` の命名規則に従います（例: デフォルトプレフィックス `"v"` の場合、`LLM_REQUEST` は `v_llm_request` になります）。複数のプラグインインスタンスが同一データセット内の異なるテーブルに書き込む場合は、`BigQueryLoggerConfig` で `view_prefix` に固有の値を設定して、ビュー名の競合を防止してください。

```python
# 同一データセット内で異なるビュープレフィックスを使用する 2 つのプラグイン
plugin_prod = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID,
    table_id="agent_events_prod",
    config=BigQueryLoggerConfig(view_prefix="v_prod"),
)
# 作成されるビュー: v_prod_llm_request, v_prod_tool_completed, ...

plugin_staging = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, dataset_id=DATASET_ID,
    table_id="agent_events_staging",
    config=BigQueryLoggerConfig(view_prefix="v_staging"),
)
# 作成されるビュー: v_staging_llm_request, v_staging_tool_completed, ...
```

スキーマアップグレード後などに手動でビューを更新するには、パブリックな非同期メソッド `await plugin.create_analytics_views()` を呼び出すこともできます。

すべての Python ビューには次の **共通列** が含まれます: `timestamp`、`event_id`、`event_type`、`agent`、`session_id`、`invocation_id`、`user_id`、`trace_id`、`span_id`、`parent_span_id`、`status`、`error_message`、`is_truncated`。Java ビューには、`event_id` を除く同じ共通列が含まれます。

次の表は、Python ビューとそれぞれのイベント固有の列の一覧です。

| ビュー名 | イベント固有の列 |
| --- | --- |
| **`v_user_message_received`** | *(共通列のみ)* |
| **`v_llm_request`** | `model` (STRING), `request_content` (JSON), `llm_config` (JSON), `tools` (JSON) |
| **`v_llm_response`** | `response` (JSON), `usage_prompt_tokens` (INT64), `usage_completion_tokens` (INT64), `usage_total_tokens` (INT64), `usage_cached_tokens` (INT64), `usage_thinking_tokens` (INT64), `usage_tool_use_tokens` (INT64), `context_cache_hit_rate` (FLOAT64), `total_ms` (INT64), `ttft_ms` (INT64), `model_version` (STRING), `usage_metadata` (JSON), `cache_metadata` (JSON), `cache_type` (STRING), `finish_reason` (STRING) |
| **`v_llm_error`** | `total_ms` (INT64) |
| **`v_tool_starting`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING) |
| **`v_tool_completed`** | `tool_name` (STRING), `tool_result` (JSON), `tool_origin` (STRING), `total_ms` (INT64), `pause_kind` (STRING), `function_call_id` (STRING) |
| **`v_tool_error`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING), `total_ms` (INT64) |
| **`v_agent_starting`** | `agent_instruction` (STRING) |
| **`v_agent_completed`** | `total_ms` (INT64) |
| **`v_agent_error`** | `total_ms` (INT64), `error_traceback` (STRING) |
| **`v_invocation_starting`** | *(共通列のみ)* |
| **`v_invocation_completed`** | *(共通列のみ)* |
| **`v_invocation_error`** | `error_traceback` (STRING) |
| **`v_state_delta`** | `state_delta` (JSON) |
| **`v_hitl_credential_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_hitl_confirmation_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_hitl_input_request`** | `tool_name` (STRING), `tool_args` (JSON) |
| **`v_a2a_interaction`** | `response_content` (JSON), `a2a_task_id` (STRING), `a2a_context_id` (STRING), `a2a_request` (JSON), `a2a_response` (JSON) |
| **`v_agent_response`** | `response_text` (STRING), `source_event_id` (STRING), `source_event_author` (STRING), `source_event_branch` (STRING) |
| **`v_agent_transfer`** | `from_agent` (STRING), `to_agent` (STRING), `source_event_id` (STRING) |
| **`v_agent_state_checkpoint`** | `agent_state` (JSON), `agent_state_type` (STRING), `end_of_agent` (BOOL), `source_event_id` (STRING) |
| **`v_event_compaction`** | `start_seconds` (FLOAT64), `end_seconds` (FLOAT64), `window_start` (TIMESTAMP), `window_end` (TIMESTAMP), `compacted_content` (JSON, フォーマットされた要約文字列を保持) |
| **`v_tool_paused`** | `tool_name` (STRING), `tool_args` (JSON), `pause_kind` (STRING), `function_call_id` (STRING) |
| **`v_node_output`** | `node_path` (STRING), `node_run_id` (STRING), `node_parent_run_id` (STRING), `output` (JSON) |
| **`v_node_error`** | `node_path` (STRING), `node_run_id` (STRING), `node_parent_run_id` (STRING), `error_code` (STRING) |

4 つのワークフロービュー（`v_agent_transfer`、`v_agent_state_checkpoint`、`v_event_compaction`、`v_tool_paused`）および `v_tool_completed` の `pause_kind` / `function_call_id` 列は、[ADK 2.0 ワークフローイベントサポート](#adk-2-events) によって提供されます。**Java**（v1.7.0+）では、`v_tool_paused` と `v_tool_completed` の `pause_kind` / `function_call_id` 列のみが作成されます。`v_agent_transfer`、`v_agent_state_checkpoint`、`v_event_compaction` は Python 専用です（Java プラグインはこれらのイベントを出力しません）。`v_node_output` および `v_node_error` ビューは Python v2.7.0 以降で利用可能です。

その他の Java ビューの違いは以下の通りです。

- Java はこれらのイベントを出力しないため、`v_agent_error`、`v_invocation_error`、`v_node_output`、`v_node_error` を作成しません。
- Java の `v_llm_response` は `usage_metadata` で終了します。`usage_thinking_tokens`、`usage_tool_use_tokens`、`cache_metadata`、`cache_type`、`finish_reason` は公開されません。
- Java の `v_agent_response` は `response_text` ではなく `text_summary` を公開します。
- Java の `v_a2a_interaction` は `a2a_response` を省略します。応答は `response_content` で引き続き利用可能です。

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

**Kotlin** では、2 つの呼び出しイベントは空のオブジェクトではなく、サマリーメッセージを保持します: `{"message": "Invocation started"}` および `{"message": "Invocation completed"}`。

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

### エージェントワークフローと一時停止/再開イベント（ADK 2.0） {#adk-2-events}

<div class="language-support-tag">
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v2.3.0</span><span class="lst-java">Java v1.7.0</span>
</div>

!!! note "Java のサポート"

    **Java** プラグインはこのセクションのサブセットをサポートします。`TOOL_PAUSED` および後述の一時停止/再開ペアリングを出力しますが、`AGENT_TRANSFER`、`AGENT_STATE_CHECKPOINT`、`EVENT_COMPACTION` は出力**せず**、`attributes.adk` エンベロープも書き込みません。Java プラグインは、代わりに `pause_kind` と `function_call_id` を `attributes` の**トップレベル**に格納します（以下のクエリの注意点を参照）。

ADK 2.0 では、マルチエージェントワークフロー（制御を渡すエージェント、状態をチェックポイントするエージェント、長い履歴を圧縮するエージェント）と、ターンをまたいで一時停止および再開する長時間実行ツールが導入されました。プラグインは、4 つの新しいイベントタイプと小さなメタデータエンベロープである `attributes.adk` を介してこれらのフローを可観測にし、行をそれを生成した ADK イベントに関連付けます。

#### `attributes.adk` エンベロープ

このエンベロープは **Python** プラグインでのみ書き込まれます。現在、すべての行に `attributes.adk` オブジェクトが含まれています。`schema_version` と `app_name` は常に存在します。残りのフィールドは、ADK イベント（ライフサイクルおよびワークフローイベント）から発生した行にのみ追加されるため、コールバックのみの行には存在しません（クエリ時には SQL `NULL` に解決されます）。

| フィールド | 型 | 意味 |
| --- | --- | --- |
| `schema_version` | string | エンベロープのバージョン（現在は `"1"`）。エンベロープが進化した場合に、これに基づいてダウンストリームクエリを制御できます。 |
| `app_name` | string | 行を生成した ADK アプリ。 |
| `source_event_id` | string | 発生元の ADK `Event` の ID。単一のイベントが生成する複数の行を結合するための信頼性の高いキーです。 |
| `node` | object | ワークフローノードのアイデンティティ: `{ "path", "run_id", "parent_run_id" }`。`parent_run_id` は親ノードの実行 ID です（ルートでは `null`）。 |
| `branch` | string | ワークフローが分岐したパスを実行している場合のイベントのブランチ。 |
| `scope` | object | 分離スコープ `{ "id", "kind" }`。ここで `kind` は `node_run`（ワークフローノード実行、例: `loopA@42`）、`function_call`（モデルが生成した呼び出し ID）、または `unknown` です。 |
| `route` | string | イベントアクションによって選択されたルート（設定されている場合）。 |
| `render_ui_widgets` | array | イベントアクションによって要求されたシリアル化された UI ウィジェット（設定されている場合）。 |
| `rewind_before_invocation_id` | string | イベントアクションが巻き戻しを要求する基準となる呼び出し ID（設定されている場合）。 |
| `pause_kind` | string | `TOOL_PAUSED` の場合: 通常の長時間実行ツールの場合は `tool`、HITL リクエストの場合は `hitl_credential` / `hitl_confirmation` / `hitl_input`。再開された `TOOL_COMPLETED` 行では常に `tool`。HITL の完了は `TOOL_COMPLETED` ではなく `HITL_*_REQUEST_COMPLETED` としてログに記録されます。 |
| `function_call_id` | string | 関数呼び出し ID。両者をペアリングできるように、`TOOL_PAUSED` および対応する再開された `TOOL_COMPLETED` 行に設定されます（通常のツールのみ）。 |

!!! tip "エンベロープのクエリ"

    エンベロープフィールドは `JSON_VALUE(attributes, '$.adk.<field>')`（`node` / `scope` オブジェクトの場合は `JSON_QUERY`）で読み取ります。自動作成されたビューは、一般的に使用されるフィールド（`source_event_id`、`pause_kind`、`function_call_id`）をすでにフラットな列として公開しているため、ほとんどのクエリではビューを直接使用できます。

#### AGENT_TRANSFER

あるエージェントが別のエージェントに制御を渡したときに記録されます（例: コーディネーターが専門のサブエージェントにルーティングする場合）。

```json
{
  "event_type": "AGENT_TRANSFER",
  "content": {
    "from_agent": "coordinator",
    "to_agent": "flight_agent"
  },
  "attributes": {
    "adk": { "source_event_id": "evt-abc123" }
  }
}
```

#### AGENT_STATE_CHECKPOINT

エージェントがその状態のスナップショットを作成したときに記録されます。プラグインはまた、エージェントの実行の終了をマークするために `end_of_agent: true` を含むチェックポイントを出力します。`v_agent_state_checkpoint` ビューは `agent_state_type` を公開するため、実際状態オブジェクトと明示的な `null` チェックポイント（実行終了マーカー）および未設定の値を区別できます。

```json
{
  "event_type": "AGENT_STATE_CHECKPOINT",
  "content": {
    "agent_state": { "step": 3, "retries": 0 },
    "end_of_agent": false
  },
  "attributes": {
    "adk": { "source_event_id": "evt-def456" }
  }
}
```

#### EVENT_COMPACTION

ADK が以前のイベントウィンドウを要約に圧縮したときに記録されます（長い会話をコンテキストウィンドウ内に維持するために使用）。タイムスタンプは小数を含むエポック秒です。ビューはこれらを BigQuery `TIMESTAMP` 列（`window_start`、`window_end`）としても公開します。`compacted_content` は構造化オブジェクトではなく、プラグインによってフォーマットされた圧縮ウィンドウのテキスト（文字列）を保持します。

```json
{
  "event_type": "EVENT_COMPACTION",
  "content": {
    "start_timestamp": 1733856000.123,
    "end_timestamp": 1733856120.456,
    "compacted_content": "User booked a flight to SFO, then asked about baggage..."
  }
}
```

#### NODE_OUTPUT および NODE_ERROR

<div class="language-support-tag">
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v2.7.0</span>
</div>

ワークフローノードパスを持つ最終的な非部分イベントの場合、プラグインは該当するノード固有の終了行を出力します。

- `NODE_OUTPUT` は、`event.output` が存在し、ノードがそのメッセージを出力として使用しない場合に出力されます。イベント出力は `content` に直接格納されます。
- `NODE_ERROR` は、`event.error_code` が存在し、それがモデルの終了理由またはブロック理由でない場合に出力されます。コードは `content.error_code` に格納され、サニタイズされたメッセージは `error_message` に格納され、`status` は `ERROR` になります。

両方の自動作成ビューは、`attributes.adk.node` から `node_path`、`node_run_id`、`node_parent_run_id` を公開します。

```json
{
  "event_type": "NODE_ERROR",
  "content": { "error_code": "VALIDATION_FAILED" },
  "attributes": {
    "adk": {
      "node": {
        "path": "workflow/validate@run-7",
        "run_id": "run-7",
        "parent_run_id": null
      }
    }
  },
  "status": "ERROR",
  "error_message": "Input did not satisfy the node contract"
}
```

#### TOOL_PAUSED および一時停止/再開のペアリング

通常の長時間実行ツールは、生成（yield）時に `TOOL_PAUSED` 行を出力し、結果が届いたとき（多くの場合、後のターン）に `TOOL_COMPLETED` 行を出力します。両方の行は同じ `function_call_id` と `tool` という `pause_kind` を持つため、一時停止とその完了をペアリングしてツールが中断されていた時間を測定できます。（HITL リクエストも `TOOL_PAUSED` を出力しますが、その完了は異なって記録されます。以下の注意点を参照してください。）

```json
{
  "event_type": "TOOL_PAUSED",
  "content": {
    "tool": "request_manager_approval",
    "args": { "amount": 5000 }
  },
  "attributes": {
    "adk": { "pause_kind": "tool", "function_call_id": "call-789" }
  }
}
```

!!! note "Java の属性の場所"

    Java プラグインは、`adk` ラッパーなしで `attributes` のトップレベルにペアキーを書き込みます:
    `"attributes": {"pause_kind": "tool", "function_call_id": "call-789"}`。
    以下のベーステーブルクエリでは、`'$.adk.pause_kind'` / `'$.adk.function_call_id'` を
    `'$.pause_kind'` / `'$.function_call_id'` に置き換えてください。ビューベースのクエリは、ビューがキーをフラットな列として公開するため、両言語で変更なく動作します。

    Java はまた、同じトップレベルのペアキーを `HITL_*_REQUEST_COMPLETED` 行にもスタンプするため、ベーステーブルで HITL の `TOOL_PAUSED` 行を `function_call_id` でその完了に直接結合できます（HITL 完了専用のビューはありません）。

!!! note "HITL イベントとの関係"

    HITL リクエスト（`adk_request_confirmation` など）は、[HITL イベント](#hitl-events) で説明されているように、引き続き専用の `HITL_*_REQUEST` イベントを出力します。そのリクエストが長時間実行される場合、プラグインはさらに HITL 種別（例: `hitl_confirmation`）を識別する `pause_kind` を持つ `TOOL_PAUSED` 行を出力し、HITL の一時停止にツールの一時停止と同じ可観測性を提供します。

    **ただし、HITL の完了は `TOOL_COMPLETED` としては届きません。** ユーザーの応答は `TOOL_COMPLETED` ではなく対応する `HITL_*_REQUEST_COMPLETED` イベントとして記録されるため、`hitl_*` の一時停止は以下のツール結合ではペアリングされません。HITL の一時停止が解決されたことを確認するには、その `HITL_*_REQUEST_COMPLETED` イベントを確認してください（[HITL イベント](#hitl-events) を参照）。したがって、以下の一時停止/再開クエリは通常のツール（`pause_kind = 'tool'`）にスコープされています。

共有キーを使用して、一時停止されたツールをその完了とペアリングします。ベーステーブルの場合:

```sql
SELECT
  p.timestamp AS paused_at,
  c.timestamp AS resumed_at,
  TIMESTAMP_DIFF(c.timestamp, p.timestamp, SECOND) AS paused_seconds,
  JSON_VALUE(p.content, '$.tool') AS tool_name,
  JSON_VALUE(p.attributes, '$.adk.pause_kind') AS pause_kind
FROM `your-gcp-project-id.adk_agent_logs.agent_events` AS p
JOIN `your-gcp-project-id.adk_agent_logs.agent_events` AS c
  ON  c.event_type = 'TOOL_COMPLETED'
  AND c.session_id = p.session_id
  AND c.user_id = p.user_id
  AND JSON_VALUE(c.attributes, '$.adk.function_call_id')
      = JSON_VALUE(p.attributes, '$.adk.function_call_id')
WHERE p.event_type = 'TOOL_PAUSED'
  AND JSON_VALUE(p.attributes, '$.adk.pause_kind') = 'tool'
ORDER BY paused_at;
```

または、`pause_kind` と `function_call_id` をフラットな列として公開する自動作成されたビューに対して、よりシンプルにクエリを実行できます。

```sql
SELECT
  p.timestamp AS paused_at,
  c.timestamp AS resumed_at,
  TIMESTAMP_DIFF(c.timestamp, p.timestamp, SECOND) AS paused_seconds,
  p.tool_name,
  p.pause_kind
FROM `your-gcp-project-id.adk_agent_logs.v_tool_paused` AS p
JOIN `your-gcp-project-id.adk_agent_logs.v_tool_completed` AS c
  USING (session_id, user_id, function_call_id)
WHERE p.pause_kind = 'tool'
ORDER BY paused_at;
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

## コンテキストグラフ {#context-graph}

行レベルの `agent_events` に加えて、[BigQuery Agent Analytics SDK](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK) を使用して**コンテキストグラフ**を実体化（materialize）できます。これは、エージェントの意思決定（処理したリクエスト、検討したオプション、選択した結果）をクエリ可能な BigQuery の [プロパティグラフ](https://cloud.google.com/bigquery/docs/graph-overview) です。単にイベントがログに記録されたという事実だけでなく、Graph Query Language（GQL）を使用して意思決定が何故行われたかの *理由* を追跡できます。

![Context graph flow: an ADK agent's events flow through the BigQuery Agent Analytics plugin into the agent_events table; the SDK's bqaa context-graph command materializes a structured decision graph that auditors, operators, and executives consume through GQL in BigQuery Studio and Conversational Analytics — with no external graph database.](/integrations/assets/bigquery-agent-analytics-context-graph-flow.png)

グラフは、テーブルの DDL と `CREATE PROPERTY GRAPH` スキーマの 2 つの宣言的なアーティファクトで定義されます。SDK の `bqaa context-graph --property-graph` コマンドは、これらと実際のテーブルスキーマから抽出対象（取得するエンティティと関係性、およびその列の型）を導き出します。一般的なケースでは別個のオントロジーやバインディングファイルは不要で、AI プロンプトのガイドとして説明が必要な場合や、エンティティの継承、派生プロパティ、または列名の変更が必要な場合にのみ明示的な `ontology.yaml` / `binding.yaml` を使用します。

ローカルで 1 回実行するか、Cloud Scheduler でトリガーされる Cloud Run ジョブとしてスケジュール実行します。これには、読み取り専用イベント/書き込み可能グラフのデータセット分割、最小権限のサービスアカウント、構造化された JSON ログ、および Cloud Monitoring アラートが含まれます。運用リファレンス（前提条件、IAM マトリックス、推奨スケジュール、JSON ログの形状、監視、およびクリーンアップ）は SDK リポジトリにあります。

- [定期的実体化（Periodic materialization）コードラボ](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/blob/main/docs/codelabs/periodic_materialization.md) — 意思決定グラフをエンドツーエンドで構築してクエリします。
- [スケジュールされたデプロイのランブック](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/blob/main/docs/guides/scheduled-context-graph-deploy.md) — グラフをメンテナンス不要のスケジュールデプロイへ適用します。
- [デプロイリファレンス（Cloud Run + Cloud Scheduler）](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/blob/main/examples/context_graph/periodic_materialization/README.md) — 完全な IAM マトリックス、スケジュール、監視、および Terraform モジュールです。

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

プラグインを含む `App` オブジェクトを持つエージェントプロジェクトフォルダーを
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

os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = "True"

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

!!! warning "OAuth トークン、API キー、クライアントシークレットをログに記録しないでください"

    BigQuery Agent Analytics プラグインは、ツール引数、LLM プロンプト、認証関連イベント（HITL 認証情報リクエストなど）を含む詳細なイベントペイロードをキャプチャします。組み込みの墨消しは、小文字化とハイフン正規化の後にキー名を正確に一致させるため、`clientSecret` や `accessToken` などの camelCase バリアントは一致**しません**。ADK は `adk_request_credential` 引数を camelCase エイリアスでシリアル化するため、`AuthenticatedFunctionTool` OAuth2 フローによって `client_secret` および `access_token` の値が引き続き `content` 列に書き込まれる可能性があります（[google/adk-python#3845](https://github.com/google/adk-python/issues/3845)、未解決）。墨消しは一般的なデータ損失防止（DLP）システムではないため、アプリケーション固有のキーまたは自由形式テキストに含まれるシークレットも BigQuery に書き込まれる可能性があります。

プラグインには、一般的なシークレットを自動的に保護する **組み込みの墨消し** 機能が含まれています。さらに制御が必要な場合は、カスタム墨消しを重ねて適用できます。

### 組み込みの墨消し {#built-in-redaction}

<div class="language-support-tag">
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python</span><span class="lst-java">Java v1.7.0</span>
</div>

Python プラグインはキー名を小文字に正規化し、ハイフンをアンダースコアのように扱います。構造化された `content` または `attributes` のどこに現れても、これらのキーの値を再帰的に `[REDACTED]` に置き換えます:

`client_secret`, `access_token`, `refresh_token`, `id_token`, `api_key`,
`password`, `private_key`, `proxy_authorization`, `google_access_id`, `sig`,
`signature`, `token`, `secret`, `authorization`, `x_api_key`,
`x_amz_credential`, `x_amz_signature`, `x_goog_credential`,
`x_goog_security_token`, `x_goog_signature`

**`temp:`** プレフィックスが付いたキーも、セッション状態および `state_delta` 行を含めて `[REDACTED]` に置き換えられます。

!!! warning "訂正: セッション状態では `temp:` のみが墨消しされます"

    以前のドキュメントでは、`secret:` プレフィックスが付いたキーも墨消しされると誤って記載されていました。プラグインは `temp:` プレフィックスのみに一致します。セッション状態に `secret:`（例: `secret:token`）の下でシークレットを保存した場合、カスタム `content_formatter` でマスクされない限り平文でログに記録されます。そのガイダンスに依存していた場合は、既存の `agent_events` テーブルで `temp:` 以外のキーの下にログ記録された値を監査してください。

プラグインはまた、`error_message`、エージェントおよび実行のトレースバック、外部 URI 内の認証情報パターンをサニタイズします。これには、認証ヘッダー、bearer および basic 認証情報、署名付き URL クエリパラメータ、および上記の機密名を使用するキー/値フラグメントが含まれます。安全に書き換えることができないエンコードされた認証情報構成は、フェイルクローズ（拒否）されます。

!!! info "設定不要"

    構造化属性および状態ロギングの組み込み墨消しは常にアクティブであり、属性値内のネストされた辞書および JSON エンコードされた文字列に再帰的に適用されます。カスタム `content_formatter` は、未加工コンテンツに対して **最初** に実行されます。エラーが発生するかサポートされていない型が返された場合、Python は元のコンテンツの代わりに `[FORMATTER_FAILED]` を書き込み、`formatter_failed` インシデントカウンタをインクリメントします。

!!! note "Java における組み込みの墨消し"

    Java プラグインには、v1.7.0 以降で組み込みの墨消しが含まれています。
    セッション状態および状態デルタを含む、組み立てられた `attributes` ツリー全体で `client_secret`、`access_token`、`refresh_token`、`id_token`、`api_key`、`password`（大文字と小文字を区別しない）、および **`temp:`** プレフィックスが付いた任意のキーを再帰的に墨消しします。シークレットを他の状態スコープから排除するか、カスタム `contentFormatter` でマスクしてください。

    カスタム Java `contentFormatter` は **スレッドセーフ**（呼び出し間で同時に呼び出される）かつ **高速/非ブロッキング**（イベント処理パス上で実行される）である必要があり、受け取ったコンテンツを変更するのではなく **新しいオブジェクト** を返す必要があります。例外をスローした場合、Java プラグインは未フォーマットのペイロードをログに記録するのではなく、行のコンテンツをドロップ（フェイルクローズ）します。

### `content_formatter` を使用して追加のシークレットを墨消しする

`BigQueryLoggerConfig` にカスタム `content_formatter` 関数を提供して、機密フィールドが書き込まれる前に削除またはマスクします:

=== "Python"

    ```python
    import json
    import re
    from typing import Any

    SENSITIVE_KEYS = {"client_secret", "access_token", "refresh_token", "api_key", "secret"}

    def redact_credentials(event_content: Any, event_type: str) -> str:
        """ログ記録されたコンテンツから OAuth シークレットとトークンを墨消しします。"""
        if isinstance(event_content, dict):
            text = json.dumps(event_content)
        else:
            text = str(event_content)

        for key in SENSITIVE_KEYS:
            # JSON ライクな文字列内の値を墨消し: "client_secret": "GOCSPX-xxx"
            text = re.sub(
                rf'("{key}"\s*:\s*)"[^"]*"',
                rf'\1"[REDACTED]"',
                text,
                flags=re.IGNORECASE,
            )
        return text

    config = BigQueryLoggerConfig(
        content_formatter=redact_credentials,
        # ... その他のオプション
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Gemini;
    import com.google.adk.models.LlmRequest;
    import com.google.adk.models.LlmResponse;
    import com.google.adk.runner.Runner;
    import com.google.genai.types.Content;
    import com.google.genai.types.GenerateContentConfig;
    import com.google.genai.types.Part;
    import java.util.ArrayList;
    import java.util.List;

    public final class AgentContentFormatter {
      private static final String PROJECT_ID = "your-gcp-project-id";
      private static final String DATASET_ID = "your-gcp-dataset_id";
      private static final String TABLE_ID = "your-gcp-table";
      private static final String API_KEY = "your-api_key";
      private static final String GCS_BUCKET_NAME = "your-gcs-bucket-name";

      /** テストするフォーマッタロジックを返します。 */
      private static Object formatter(Object content, String eventType) {
        if (content instanceof LlmRequest req) {
          List<Content> maskedContents = new ArrayList<>();
          for (Content c : req.contents()) {
            maskedContents.add(maskContent(c));
          }
          return req.toBuilder().contents(maskedContents).build();
        } else if (content instanceof LlmResponse res) {
          if (res.content().isPresent()) {
            return res.toBuilder().content(maskContent(res.content().get())).build();
          }
          return res;
        } else if (content instanceof Content content2) {
          return maskContent(content2);
        } else if (content instanceof Map<?, ?> map) {
          Map<Object, Object> maskedMap = new LinkedHashMap<>();
          for (Map.Entry<?, ?> entry : map.entrySet()) {
            maskedMap.put(entry.getKey(), formatter(entry.getValue(), eventType));
          }
          return maskedMap;
        }
        return content;
      }

      private static Content maskContent(Content originalContent) {
        if (originalContent.parts().isPresent()) {
          List<Part> maskedParts = new ArrayList<>();
          for (Part part : originalContent.parts().get()) {
            if (part.text().isPresent() && part.text().get().contains("secret")) {
              String maskedText = part.text().get().replace("secret", "****");
              maskedParts.add(part.toBuilder().text(maskedText).build());
            } else {
              maskedParts.add(part);
            }
          }
          return originalContent.toBuilder().parts(maskedParts).build();
        }
        return originalContent;
      }

      public static void main(String[] args) throws Exception {
        // 1. カスタムフォーマッタで Config を設定
        BigQueryLoggerConfig config =
            BigQueryLoggerConfig.builder()
                .projectId(PROJECT_ID)
                .datasetId(DATASET_ID)
                .tableName(TABLE_ID)
                .gcsBucketName(GCS_BUCKET_NAME)
                .contentFormatter(AgentContentFormatter::formatter)
                .logMultiModalContent(true)
                .build();

        // 2. プラグインを設定
        BigQueryAgentAnalyticsPlugin plugin = new BigQueryAgentAnalyticsPlugin(config);

        // 3. 応答するエージェントを設定
        LlmAgent agent =
            LlmAgent.builder()
                .model(
                    Gemini.builder()
                        .modelName("gemini-3-flash-preview") // 適切なモデルを使用
                        .apiKey(API_KEY)
                        .build())
                .name("bq_demo_agent")
                .instruction("You are a helpful assistant")
                .generateContentConfig(GenerateContentConfig.builder().temperature(0.5f).build())
                .build();

        // 4. Runner を設定
        Runner runner = Runner.builder().agent(agent).appName("test_app").plugins(plugin).build();
        // 5. runner を使用してシナリオを実行
        ...
      }

      private AgentContentFormatter() {}
    }
    ```

### `event_denylist` を使用して資格情報イベントをスキップする

認証関連のイベントをログに記録する必要がない場合は、完全に除外します:

=== "Python"

    ```python
    config = BigQueryLoggerConfig(
        event_denylist=[
            "HITL_CREDENTIAL_REQUEST",
            "HITL_CREDENTIAL_REQUEST_COMPLETED",
        ],
        # ... その他のオプション
    )
    ```

=== "Java"

    ```java
    import com.google.common.collect.ImmutableList;

    BigQueryLoggerConfig config = BigQueryLoggerConfig.builder()
        .eventDenylist(ImmutableList.of(
            "HITL_CREDENTIAL_REQUEST",
            "HITL_CREDENTIAL_REQUEST_COMPLETED"
        ))
        // ... その他のオプション
        .build();
    ```

### 一般的なベストプラクティス

- エージェントのソースコードに **シークレットを決してハードコードしないでください**。OAuth クライアントシークレットや API キーには、環境変数またはシークレットマネージャー（例: Google Cloud Secret Manager）を使用してください。
- IAM を使用して **BigQuery テーブルへのアクセスを制限** し、ログに記録されたイベントデータを読み取ることができるユーザーを制限してください。
- 予期しない機密データがキャプチャされていないことを確認するために、定期的に **ログを監査** してください。

## 運用

### トレースと可観測性

プラグインは、親子実行ツリー（エージェント → LLM 呼び出し / ツール呼び出し）が BigQuery からきれいに再構築できるように、出力されるすべての行に `trace_id`、`span_id`、`parent_span_id` 列を入力します。

- **内部スパン追跡、OTel スパンエクスポートなし。** プラグインは、16 文字の 16 進数 `span_id` 値の独自の内部スタックで親子階層を追跡します。ルート呼び出しスパンは、周囲の OTel スパンがアクティブな場合にその ID を再利用します（ランナーの呼び出しスパンと一致させます）。子 BQAA スパンは内部で生成されます。設定された OpenTelemetry `TracerProvider` に対して `tracer.start_span(...)` を呼び出さ**ない**ため、そのインストルメンテーションが設定されたエクスポーターに到達することはありません。これにより、Agent Engine テレメトリが有効になっている場合（`GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true`）や、他の Cloud Trace エクスポーターをホストプロセスに接続した場合に、Cloud Trace でスパンが重複するのを防ぎます。同じ内部 ID のみのスパン追跡が、v1.7.0 以降の Java プラグインにも適用されます。以前の Java ビルドでは、フレームワークのスパンの横に重複して表示される可能性のあるプラグイン所有の OpenTelemetry スパンが作成されていました。
- **周囲の OTel スパンが存在する場合の `trace_id` 継承。** Agent Engine の呼び出しスパン、ADK `Runner` 呼び出しスパン、またはエージェントの実行前に開始した任意のスパンなど、周囲のランタイムがすでに OTel スパンを開始している場合、プラグインはその `trace_id` を読み取り、すべての BigQuery 行にスタンプします。周囲のスパンがない場合、プラグインは呼び出しごとに一意の 32 文字の 16 進数 `trace_id` を生成します。
- **明示的に保持される親子関係。** プラグインの内部スタックにより、各サブ操作（`LLM_REQUEST`、`TOOL_STARTING` など）が正しい呼び出しレベルまたはエージェントレベルの `span_id` を `parent_span_id` として参照することが保証されます。

### パブリックメソッド

=== "Python"

    `BigQueryAgentAnalyticsPlugin` は、ライフサイクルとメンテナンスの制御のために次のパブリックメソッドを公開します。

    - **`await plugin.flush()`**: バックグラウンド書き込みキューが空になるまで待機します。組み込みの `after_run_callback` は、実行ごとにこれを自動的に実行します。プロセスの終了前や、ターン間での早期永続化を保証するために明示的に呼び出すことができます。
    - **`await plugin.close()`**: プラグイン終了タイムスタンプ（`shutdown_timeout` にバインド）までキューをフラッシュし、バックグラウンドワーカーをキャンセルして、BigQuery 書き込みクライアントセッションを閉じます。`App` の終了時に呼び出す必要があります。
    - **`await plugin.create_analytics_views()`**: BigQuery 内の分析ビューセットを冪等に再作成または更新します。通常は `create_views=True` により初期化時に自動的に呼び出されますが、手動のスキーマアップグレード後に明示的に呼び出すこともできます。
    - **`plugin.get_drop_stats()`**（v2.7.0+）: プラグイン開始以降のドロップされたイベント数のスナップショットである辞書（`{reason: count}`）を返します。詳細については、[ドロップされたイベントの可観測性](#dropped-event-observability) を参照してください。

    ```python
    # 手動フラッシュとグレースフルシャットダウン
    await plugin.flush()
    await plugin.close()
    ```

=== "Java"

    Java では、プラグインのライフサイクルは `Plugin` から継承された `close()` メソッドを介して管理され、これは RxJava の `Completable` を返します。

    - **`plugin.close()`**: プラグインを正常にシャットダウンし、保留中のイベントをフラッシュしてリソース（BigQuery 書き込みクライアントとエグゼキュータを含む）を解放します。
    - **自動クローズ**: `InMemoryRunner` を使用している場合、`runner.close()` を呼び出すと、BigQuery Agent Analytics プラグインを含む登録されているすべてのプラグインが自動的にクローズされます。
    - **`plugin.getDropStats()`**（v1.7.0+）: ドロップ理由ごとのドロップイベント数の `ImmutableMap<String, Long>` を返します。[ドロップされたイベントの可観測性](#dropped-event-observability) を参照してください。
    - **JVM シャットダウンフック**（v1.7.0+）: プラグインは構築時にシャットダウンフックを登録するため、`close()` が呼び出されなかった場合でも、JVM 終了時に保留中のイベントが排出されます（`shutdownTimeout` にバインドされたベストエフォート）。明示的な `close()` を呼び出すとフックが登録解除されます。決定論的なフラッシュのためには、明示的に `close()` を呼び出すことを推奨します。

    ```java
    // 手動シャットダウン
    plugin.close().blockingAwait();
    ```

### ドロップされたイベントの可観測性 {#dropped-event-observability}

<div class="language-support-tag">
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python</span><span class="lst-java">Java v1.7.0</span>
</div>

BigQuery のログ記録はベストエフォートです。メモリ内キューのオーバーフロー、セットアップの利用不能、シャットダウンとコールバックの競合、または最終的な書き込み失敗時に、イベントがドロップされる可能性があります。プラグインはまた、コンテンツの代わりにセンチネルを伴って行が書き込まれるフォーマッタおよびパーサーのエラーもカウントします。カウンタはループのクリーンアップやシャットダウンをまたいで保持されます。

**ドロップ理由（Python）:**

| 理由 | 原因 |
|---|---|
| `queue_full` | メモリ内のバッチキューがオーバーフローしました（ホストがドレイナーが送信できる速度よりも速くイベントを生成しています）。`BigQueryLoggerConfig` の `queue_max_size` を増やすか、`batch_size` を増やして大きなチャンクでドレインするか、コンシューマ側をスケールしてください。 |
| `arrow_prep_failed` | 行を Arrow 表現に変換できませんでした（通常はスキーマ/型の不一致）。ログで問題のあるフィールドを調べてください。 |
| `retry_exhausted` | 再試行予算が使い果たされるまで、Storage Write API 呼び出しが再試行可能なエラー（例: 一時的な gRPC 障害）を返し続けました。 |
| `non_retryable` | Storage Write API が再試行不可能なエラー（権限、クォータ、スキーマの拒否）を返しました。通常、オペレーターの介入が必要です。 |
| `unexpected_error` | バッチの準備または書き込み中に捕捉されたその他の例外。 |
| `shutdown_timeout` | 制限されたシャットダウンまたはクローズがタイムアウトしたときに、行がキューに残っていました。 |
| `shutdown_cancelled` | 外部のクローズタイムアウトなど、ホストによってシャットダウンがキャンセルされたときに、行がキューに残っていました。 |
| `offset_conflict` | `exactly_once_delivery` モードで、コミット済みストリームがオフセットを拒否したか、置換ストリームが利用できませんでした。 |
| `setup_unavailable` | プラグインのセットアップが失敗したか再試行バックオフ状態だったため、行を受け入れられませんでした。 |
| `shutdown_race` | シャットダウンの開始中または進行中に、コールバックが行を受け入れようとしました。 |
| `stale_loop` | キューに入れられた行が、すでにクローズされており排出できないイベントループに属していました。 |
| `formatter_failed` | カスタムフォーマッタが失敗したか、サポートされていない型を返しました。行は `[FORMATTER_FAILED]` で書き込まれます。これはドロップされた行数ではなく、インシデントカウントです。 |
| `content_parse_failed` | コンテンツの解析に失敗しました。行は `[CONTENT_PARSE_FAILED]` で書き込まれます。これはドロップされた行数ではなく、インシデントカウントです。 |

**ドロップ理由（Java、v1.7.0+）:**

| 理由 | 原因 |
|---|---|
| `queue_full` | メモリ内のバッチキューがオーバーフローしました。`BigQueryLoggerConfig` の `queueMaxSize` を増やすか、`batchSize` を増やすか、コンシューマ側をスケールしてください。 |
| `append_error` | タイムアウト、再試行の枯渇または再試行不可能な書き込み、予期しない変換障害など、`AppendSerializationError` 以外の原因でバッチの準備または追加が失敗しました。 |
| `serialization_error` | 書き込みストリーム用に行をシリアル化できませんでした（通常はスキーマ/型の不一致）。ログで問題のあるフィールドを調べてください。 |
| `after_close` | 行がすでに閉じられている呼び出しごとのプロセッサに到達しました。 |
| `shutdown_timeout` | 制限された最終ドレインが期限切れになったときに、キューに行が残っていました。 |
| `writer_permit_exhausted` | 通常、Storage Write の停止または遅延したクリーンアップ中に、ライブライターのセーフティ上限が枯渇しました。 |
| `writer_create_error` | `StreamWriter` の構築またはプロセッサの起動に失敗しました。 |
| `late_after_finalize` | 呼び出しが確定した後、またはプラグインのクローズ中に非同期処理が完了しました。 |

**カウントの読み取り:**

=== "Python"

    ```python
    # プラグイン開始以降の {reason: count} のスナップショット。
    stats = plugin.get_drop_stats()
    # 例: {"queue_full": 12, "retry_exhausted": 0,
    #      "formatter_failed": 1, ...}

    loss_reasons = {
        "queue_full", "arrow_prep_failed", "retry_exhausted",
        "non_retryable", "unexpected_error", "shutdown_timeout",
        "shutdown_cancelled", "offset_conflict", "setup_unavailable",
        "shutdown_race", "stale_loop",
    }
    total_rows_lost = sum(stats.get(reason, 0) for reason in loss_reasons)
    ```

=== "Java"

    ```java
    // プラグイン開始以降の {drop_reason: count} のスナップショット。
    ImmutableMap<String, Long> stats = plugin.getDropStats();
    // 例: {queue_full=12, append_error=0, serialization_error=0,
    //      after_close=0, shutdown_timeout=0, writer_permit_exhausted=0,
    //      writer_create_error=0, late_after_finalize=0}

    long totalDropped = stats.values().stream().mapToLong(Long::longValue).sum();
    ```

**モニタリングシステムへのエクスポート**: 定期的にポーリングして差分（delta）を送信します:

```python
import asyncio

async def export_loop(plugin):
    last = {}
    while True:
        current = plugin.get_drop_stats()
        for reason, count in current.items():
            delta = count - last.get(reason, 0)
            if delta:
                # 例: metric_client.write_point(
                #         metric="bqaa_dropped_events",
                #         labels={"reason": reason}, value=delta)
                ...
        last = current
        await asyncio.sleep(60)
```

ゼロ以外のすべての理由に対してアラートを設定してください。ほとんどの理由は、BigQuery に到達する前に行が失われたことを意味します。一方、`formatter_failed` および `content_parse_failed` の理由は、センチネルコンテンツで行が書き込まれたことを意味するため、プライバシーまたはデータ品質のインシデントとしてアラートを設定してください。`queue_full`、`retry_exhausted`、`non_retryable`、または `offset_conflict` のカウントが持続する場合は、一般にスループット、配信、または Storage Write の健全性の問題を示します。Java における同等の書き込みエラーバケットは `append_error` です。

### マルチプロセッシングと fork セーフティ

Python プラグインは fork を認識します。gRPC C-core ライブラリを読み込む前に `GRPC_ENABLE_FORK_SUPPORT=1` を設定し、子プロセスで継承されたランタイム状態（gRPC チャネル、書き込みストリーム、イベントループ）をリセットする `os.register_at_fork` ハンドラを登録します。これにより、プラグインはファイル記述子をリークしたり、親プロセスの接続でデータを送信したりすることなく、`os.fork()` 後も存続できます。

ただし、本番環境へのデプロイには **`spawn` が推奨されるマルチプロセッシング開始方法** です。`fork` は処理中の gRPC 状態を含む親のアドレス空間をコピーし、fork 後のリセットによって各子プロセスの最初の書き込みにレイテンシが追加されます。`spawn` を使用すると、各ワーカーがプラグインをクリーンに初期化します。

特に Gunicorn デプロイの場合:

- 遅延プラグイン初期化（プラグインは最初のイベントが記録されるまでセットアップを延期します）と組み合わせた `--preload` を優先するか、
- 各ワーカーが独自のクライアントを取得できるように、`post_fork` フック内でプラグインを初期化してください。

!!! note

    fork セーフティメカニズムはランタイム状態のみをリセットします。fork の時点で親プロセスでキューに入っていたがまだフラッシュされていなかったイベントは、**再再生されません**。配信を保証する必要がある場合は、fork 前に `await plugin.flush()` を呼び出してください。

## 記録データを利用する追加方法

### BigQuery Agent Analytics SDK

[BigQuery Agent Analytics SDK](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/tree/main) は、プラグインによってログに記録されたデータをプログラムで利用および分析する方法を提供します。SDK は以下の目的で使用します:

- **エージェント評価**: エージェントの実行を期待される結果と比較
- **ゴールデン軌道（Golden trajectory）マッチング**: エージェントの実行パスが承認されたシーケンスと一致することを検証
- **トレースの可視化**: ログに記録されたスパンからエージェントの実行フローを再構築して視覚化

### ダッシュボードの構築

ホストされた Looker Studio テンプレート、既製の Looker Block、またはサンプルノートブックから構築された独自のダッシュボードを使用して、エージェントのパフォーマンスデータを視覚化できます。

#### Looker Studio テンプレート

[BigQuery Agent Analytics ダッシュボード設定ページ](https://googlecloudplatform.github.io/BigQuery-Agent-Analytics-SDK/) は、すぐに使い始めるための簡単な方法です。イベントテーブルの完全修飾 ID（`project.dataset.table`）を入力すると、事前構築されたレポートページを備えた公開テンプレートのプライベートコピーを作成する Looker Studio リンクが生成されます。生成されたビューやデータパイプラインを使用せず、ベーステーブルを直接クエリします。設定ページにはバックエンドがなく、クライアント側でリンクを構築すると記載されています。テーブル ID を入力する前にソースを確認してください。

コピーは **所有者の認証情報（Owner's credentials）** で作成されます。各閲覧者が独自のアクセス権で BigQuery をクエリできるように、データソースを **閲覧者の認証情報（Viewer's credentials）** に切り替えるまでレポートを非公開にしておき、共有する前に閲覧専用アカウントで切り替えを確認してください。

#### Looker Block

[BigQuery Agent Analytics Looker Block](https://marketplace.looker.com/marketplace/detail/agent_analytics) は、エージェントの監視、デバッグ、および最適化のためのすぐに使用できるダッシュボードを提供し、インタラクション、ツールの使用状況、LLM のパフォーマンス、およびコストフットプリントに関するインサイトを提供します。以下が可視化されます:

- **集計メトリクス**: トークン消費量、ユーザーエンゲージメント、ツールの実行量。
- **システムヘルス**: ボトルネックを特定するのに役立つ P50〜P99 のレイテンシ分布とツールの障害追跡。
- **インタラクティブなドリルダウン**: メトリクスをクリックして、根本原因分析のためのコンテキストに応じた可視化を開きます。

このブロックは、ログに記録された JSON ペイロードを直接解析するネイティブ派生テーブル（Native Derived Table）アーキテクチャを使用するため、追加のデータパイプラインは必要ありません。使用を開始するには、Looker Marketplace から無料でインストールし、BigQuery プロジェクト ID、データセット名、およびベーステーブル名を指定してください。

#### ノートブックからのカスタムダッシュボード

BigQuery Agent Analytics SDK には、エージェントのパフォーマンスデータをクエリして視覚化する方法を示す [サンプルの Jupyter ノートブック](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/blob/main/examples/dashboard_v2.ipynb) が含まれています。これを起点として、BigQuery Agent Analytics データセットに合わせて調整された独自のカスタムダッシュボードを構築してください。[Colab Data Apps](https://docs.cloud.google.com/bigquery/docs/colab-data-apps) を使用して、ノートブックをインタラクティブなダッシュボードとして公開することもできます。

## フィードバック

BigQuery Agent Analytics に関するフィードバックを歓迎します。質問、提案、問題が
ある場合は [bqaa-feedback@google.com](mailto:bqaa-feedback@google.com) までご連絡ください。

## 追加リソース

- [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [Introduction to Object Tables](https://docs.cloud.google.com/bigquery/docs/object-table-introduction)
- [Interactive Demo Notebook](https://github.com/haiyuan-eng-google/demo_BQ_agent_analytics_plugin_notebook)
