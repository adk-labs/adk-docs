---
catalog_title: BigQuery Agent Analytics Plugin
catalog_description: 動作分析とロギングのための詳細なエージェント分析
catalog_icon: /integrations/assets/bigquery.png
catalog_tags: ["observability", "google"]
---

# ADK 向け BigQuery Agent Analytics プラグイン

<div class="language-support-tag">
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v1.21.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v1.5.0</span><span class="lst-kotlin">Kotlin v0.8.0</span>
</div>

BigQuery Agent Analytics プラグインは、エージェントの動作を詳細に分析するための堅牢なソリューションを提供することにより、Agent Development Kit（ADK）を大幅に強化します。ADK プラグインアーキテクチャと **BigQuery Storage Write API** を使用して、重要な運用イベントを Google BigQuery テーブルに直接キャプチャしてログに記録し、デバッグ、リアルタイム監視、および包括的なオフラインパフォーマンス評価のための高度な機能を提供します。

また、本プラグインは **自動スキーマアップグレード（Auto Schema Upgrade）**（既存テーブルへの新しい列の安全な追加）、**ツールの出所追跡（Tool Provenance）**（`LOCAL`、`MCP`、`SUB_AGENT`、`A2A`、`TRANSFER_AGENT`、`TRANSFER_A2A`、`TOOLBOX`、`SKILL`）、ヒューマンインザループ（HITL）インタラクション向けの **HITL イベントトレース**、および **自動ビュー作成（Automatic View Creation）**（クエリしやすいフラットなイベントビューの生成）を提供します。

**ADK 2.0** マルチエージェントワークフローのサポートにより、**Python** および **Go** においてエージェントのハンドオフ、状態チェックポイント、イベント圧縮（compaction）、および長時間実行ツールのトレースまで拡張されます。4 つのワークフローイベントタイプ（`AGENT_TRANSFER`、`AGENT_STATE_CHECKPOINT`（Go では `CustomMetadataAllowlist` でチェックポイントキーが有効になっている場合に出力）、`EVENT_COMPACTION`、`TOOL_PAUSED`）が追加されました。また、すべての行に `attributes.adk` エンベロープをスタンプするため、エージェントの実行グラフを再構築し、一時停止されたツールをそれを再開する行と結合できます。**Java** では、現在このサポートは `TOOL_PAUSED` イベントおよびその一時停止/再開ペアリングキーのみを対象としており（`attributes.adk` エンベロープは含みません）、詳細については [エージェントワークフローと一時停止/再開イベント（ADK 2.0）](#adk-2-events) を参照してください。

プラグインには 3 つの信頼性と可観測性の機能が含まれています（Java: v1.7.0 以降、Go）:

- **クロスリージョン Storage Write API ルーティング:** `US` マルチリージョン以外（例: `EU` や `northamerica-northeast1`）の BigQuery データセットへの書き込みが、書き込みストリームを所有するリージョンにルーティングされるようになりました。以前は「session not found」/ stream-not-found エラーで失敗し、すべての行が暗黙的にドロップされる可能性がありました。
- **配信およびコンテンツインシデントの可観測性:** 配信損失が原因別に追跡されます。また、Python と Go ではセンチネル行が書き込まれるフォーマッタのエラー（Python ではさらにパーサーのエラー）もカウントされます。これらのカウンタは `BigQueryAgentAnalyticsPlugin.get_drop_stats()`（Python）、`DropStats()`（Go、`agentanalytics.AsBigQueryAgentAnalyticsPlugin` 経由）、または `getDropStats()`（Java）を介して公開されるため、ホストがポーリングして独自のモニタリングにエクスポートできます。原因キーとセマンティクスは言語によって異なります。[ドロップされたイベントの可観測性](#dropped-event-observability) を参照してください。
- **Cloud Trace における重複スパンの防止:** Agent Engine テレメトリ（`GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true`）またはその他の Cloud Trace エクスポーターがグローバルトレーサープロバイダーに接続されている場合、プラグインは各フレームワークスパンの横に重複したスパンを生成しなくなりました。プラグインは依然として周囲の OTel スパンから `trace_id` を継承するため、BigQuery の行は Cloud Trace トレースとスムーズに結合されます。

Python（v2.7.0 以降）および Go では、すべての行が書き込みキューに入る前に安定した 32 文字の 16 進数 `event_id` を受け取ります。この ID は Storage Write API の再試行全体で保持されるため、コンシューマは再試行による重複を識別できます。オプトインの `exactly_once_delivery`（Go では `ExactlyOnceDelivery`）モードは、コミット済みストリームと明示的なオフセットを使用して、ライブプロセッサ内での曖昧な再試行による重複を防ぎます。このモードはロスレス配信を保証するものではなく、ストリームローテーションや `ResourceExhausted` の再試行処理は Python と Go で異なります。[配信と重複排除](#delivery-and-deduplication) を参照してください。

Python（v2.7.0 以降）および Go では、モデルとワークフローの終了詳細もキャプチャされます。最終的な `LLM_RESPONSE` 行には `finish_reason` が含まれ、モデルから提供された場合はサニタイズされた `error_message` が含まれます。ワークフローノードは `NODE_OUTPUT` と `NODE_ERROR` を出力でき、エージェントまたは実行の失敗は `AGENT_ERROR` と `INVOCATION_ERROR` を出力します（Go では、`AGENT_ERROR` は ADK が `AfterAgent` コールバックなしで処理する失敗したアクティベーションも対象とします）。

ADK Python v2.13.0 以降では、プラグインに次の機能が追加されています:

- **ツール結果のエラー分類**（`tool_result_classifier` および `ToolResultClassification`）: `isError=True` / `is_error=True` を持つ MCP ツール結果および `ReflectAndRetryToolPlugin` のエラー応答の組み込み検出と並行して動作し、例外を発生させる代わりに戻り値で失敗を報告するツールが `TOOL_ERROR` 行として記録されます。
- **エージェント評価ビュー**（`create_eval_views=True`、またはオンデマンドの `await plugin.create_eval_views()`）: BigQuery 内で直接 `AgentData` 評価トレースを再構築する `v_eval_session` および `v_eval_turn` ビューを作成します。

!!! warning "BigQuery Storage Write API"

    この機能は有料サービスである **BigQuery Storage Write API** を使用します。料金の詳細については、[BigQuery ドキュメント](https://cloud.google.com/bigquery/pricing?e=48754805&hl=ja#data-ingestion-pricing) を参照してください。

??? note "Kotlin のサポート"

    **Kotlin** プラグインは呼び出しライフサイクルイベントをログに記録します。呼び出しが開始されたときに `INVOCATION_STARTING` 行を書き込み、終了したときに `INVOCATION_COMPLETED` 行を書き込み、まだ存在しない場合は初回使用時にパーティション分割およびクラスタ化されたイベントテーブルを作成します。

    行は、Python、Go、および Java で使用される Storage Write API ではなく、呼び出しパス上で同期的に `tabledata.insertAll` を介して 1 行ずつ挿入されます。

    Kotlin では、LLM、ツール、エージェント、状態、HITL、A2A イベント、ADK 2.0 ワークフローイベント、自動ビュー作成、自動スキーマアップグレード、ツールの出所追跡、GCS オフロード、ドロップ統計は実装されていません。

## ユースケース

- **エージェントワークフローのデバッグと分析:** 広範な *プラグインライフサイクルイベント*（LLM 呼び出し、ツール使用状況）および *エージェント生成イベント*（ユーザー入力、モデル応答）を適切に定義されたスキーマにキャプチャします。
- **大量の分析とデバッグ:** 高スループットと低レイテンシを実現するために、Storage Write API を使用して非同期でロギング操作を実行します。
- **マルチモーダル分析:** テキスト、画像、その他のモダリティをログに記録して分析します。大きなファイルは GCS にオフロードされ、Object Tables 経由で BigQuery ML からアクセス可能になります。
- **分散トレース:** エージェントの実行フローを視覚化するために、OpenTelemetry スタイルのトレース（`trace_id`、`span_id`）をネイティブにサポートします。
- **ツールの出所追跡:** 各ツール呼び出しの出所（ローカル関数、MCP サーバー、サブエージェント、A2A リモートエージェント、転送エージェント、Toolbox ツール、または Skill ツールセット）を追跡します。
- **Human-in-the-Loop（HITL）トレース:** 認証情報リクエスト、確認プロンプト、およびユーザー入力リクエスト専用のイベントタイプを提供します。
- **エージェントワークフローのトレース（ADK 2.0）:** 実行グラフを再構築するための `attributes.adk` エンベロープとともに、エージェント転送、状態チェックポイント、イベント圧縮、および長時間実行ツールの一時停止/再開をキャプチャします。
- **クエリ可能なイベントビュー:** JSON ペイロードデータを unnest してダウンストリーム分析を簡素化する、イベントタイプごとのフラットな BigQuery ビュー（例: `v_llm_request`、`v_tool_completed`）を自動的に作成します。

### キャプチャされたイベントの概要

次の表は、プラグインが記録するすべてのイベントタイプの一覧です。詳細なペイロードの例については、[イベントタイプとペイロード](#event-types) を参照してください。**ビュー** 列はオプションの BigQuery ビューを示します。Python と Go はデフォルトでビューを作成します。Java は `createViews(true)` が構成されている場合にのみビューを作成します。

**Kotlin** では、プラグインは `INVOCATION_STARTING` と `INVOCATION_COMPLETED` のみを記録し、ビューを作成しないため、他の行および **ビュー** 列全体は Python、Go、および Java に適用されます。

ADK Python v2.13.0 と Go は以下の 28 個のイベントタイプをサポートし、イベントタイプごとの 25 個のビューを提供します。3 つの HITL 完了イベントには専用のビューがありません。

- **Python** と **Go** は表内の全 28 個のイベントタイプを出力します。
- **Java** は表内の 28 個のイベントタイプのうち 21 個を出力します（`INVOCATION_ERROR`、`AGENT_ERROR`、`AGENT_TRANSFER`、`AGENT_STATE_CHECKPOINT`、`EVENT_COMPACTION`、`NODE_OUTPUT`、`NODE_ERROR` を除くすべての行。ワークフローイベントのうち、Java は `TOOL_PAUSED` を出力します）。

| イベントタイプ | キャプチャのタイミング | 主要なペイロードフィールド | ビュー |
| --- | --- | --- | --- |
| `USER_MESSAGE_RECEIVED` | ユーザーメッセージが呼び出しに入ったとき | テキスト要約 / コンテンツパーツ | `v_user_message_received` |
| `INVOCATION_STARTING` | 呼び出しが開始されたとき | *(共通列のみ)* | `v_invocation_starting` |
| `INVOCATION_COMPLETED` | 呼び出しが終了したとき | *(共通列のみ)* | `v_invocation_completed` |
| `INVOCATION_ERROR` | 呼び出しが未処理の例外で失敗したとき | エラーメッセージ、サニタイズされたトレースバック | `v_invocation_error` |
| `AGENT_STARTING` | エージェントの実行が開始されたとき | 指示テキスト。ADK Python v2.12.0+ では、指示ソース、静的指示、説明、モデル、サブエージェント名も含む（Go はエージェント自体に設定されている場合に `instruction_source`、`agent_description`、`sub_agents`、`model` を記録し、`static_instruction` は設定しません） | `v_agent_starting` |
| `AGENT_COMPLETED` | エージェントの実行が終了したとき | レイテンシ | `v_agent_completed` |
| `AGENT_ERROR` | エージェントの実行が失敗したとき（Go では、ADK が `AfterAgent` コールバックなしで処理する失敗したアクティベーションも含む） | エラーメッセージ、サニタイズされたトレースバック、レイテンシ | `v_agent_error` |
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
| `AGENT_STATE_CHECKPOINT` | エージェントが状態のスナップショットを作成したとき（または実行終了をマークしたとき）。Go では `CustomMetadataAllowlist` でチェックポイントキーが有効になっている場合に出力 | エージェント状態、エージェント終了フラグ、ソースイベント ID | `v_agent_state_checkpoint` |
| `EVENT_COMPACTION` | 一連のイベント期間が要約に圧縮されたとき | ウィンドウの開始/終了タイムスタンプ、圧縮されたコンテンツ | `v_event_compaction` |
| `TOOL_PAUSED` | 長時間実行ツール（または HITL リクエスト）が一時停止し、再開を待機しているとき | ツール名、引数、一時停止の種類、関数呼び出し ID | `v_tool_paused` |
| `NODE_OUTPUT` | ワークフローノードが最終的な構造化出力を出力したとき | 出力、ノードパス、実行 ID、親実行 ID | `v_node_output` |
| `NODE_ERROR` | ワークフローノードが非モデルエラーで終了したとき | エラーコード、エラーメッセージ、ノードパス、実行 ID、親実行 ID | `v_node_error` |

## インストール

=== "Python"

    専用の BigQuery Agent Analytics エクストラ（extra）を使用して ADK をインストールします。このエクストラには、プラグインに必要な BigQuery クライアント、Cloud Storage クライアント、および `pyarrow` が含まれています。

    ```bash
    pip install "google-adk[bigquery-analytics]>=2.7.0"
    ```

    `pyarrow` の依存関係は、一般的な `gcp` エクストラには含まれなくなりました。`pyarrow` が不足している場合、プラグインのインポートエラーによってインストールすべき `bigquery-analytics` エクストラが示されます。

=== "Go"

    Go プラグインは、コア ADK アプリケーションが必要でない限り BigQuery および Cloud Storage クライアントの依存関係を取り込まないように、`adk-go` リポジトリ内の独立した Go サブモジュール（`plugin/agentanalytics/go.mod`）として公開されています。Go プラグインはコア `google.golang.org/adk/v2` とは別にバージョン管理されています（`module google.golang.org/adk/plugin/agentanalytics`、`/v2` メジャーバージョンサフィックスなし。プラグインリリース `v0.1.0` から `plugin/agentanalytics/v0.1.0` としてタグ付けされており、サポートバッジの `Go v0.1.0` はこれを示します）。`go get` を使用してコア ADK Go（`v2.0.0+`）とプラグインモジュールをインストールします（`@latest` は最新のタグ付きリリースに解決されます。または `google.golang.org/adk/plugin/agentanalytics@v0.1.0` のように明示的なプラグインリリースを固定することもできます）:

    ```bash
    go get google.golang.org/adk/v2@latest
    go get google.golang.org/adk/plugin/agentanalytics@latest
    ```

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

=== "Go"

    `agentanalytics.NewBigQueryAgentAnalyticsPlugin` でプラグインを作成し、`PluginConfig` を介して `runner.New` に渡します。ADK Go のランナーはプラグインを自動的にクローズしないため、終了前にバッファリングされたイベントをフラッシュして BigQuery クライアントを解放するために、実行関数内で `defer bqPlugin.Close()` を呼び出してください。前提条件については、[前提条件](#prerequisites) を参照してください。

    ```go title="main.go"
    package main

    import (
    	"context"
    	"fmt"
    	"log"

    	"google.golang.org/adk/plugin/agentanalytics"
    	"google.golang.org/adk/v2/agent"
    	"google.golang.org/adk/v2/agent/llmagent"
    	"google.golang.org/adk/v2/model/gemini"
    	"google.golang.org/adk/v2/plugin"
    	"google.golang.org/adk/v2/runner"
    	"google.golang.org/adk/v2/session"
    	"google.golang.org/genai"
    )

    func run(ctx context.Context) error {
    	bqPlugin, err := agentanalytics.NewBigQueryAgentAnalyticsPlugin(
    		ctx,
    		"your-gcp-project-id",
    		"your-big-query-dataset-id",
    		"agent_events",
    	)
    	if err != nil {
    		return fmt.Errorf("create BigQuery plugin: %w", err)
    	}
    	defer bqPlugin.Close()

    	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{
    		Project:  "your-gcp-project-id",
    		Location: "us-central1",
    		Backend:  genai.BackendVertexAI,
    	})
    	if err != nil {
    		return fmt.Errorf("create model: %w", err)
    	}

    	myAgent, err := llmagent.New(llmagent.Config{
    		Name:        "my_agent",
    		Model:       model,
    		Instruction: "You are a helpful assistant.",
    	})
    	if err != nil {
    		return fmt.Errorf("create agent: %w", err)
    	}

    	sessionService := session.InMemoryService()
    	r, err := runner.New(runner.Config{
    		AppName:        "my_agent",
    		Agent:          myAgent,
    		SessionService: sessionService,
    		PluginConfig: runner.PluginConfig{
    			Plugins: []*plugin.Plugin{bqPlugin},
    		},
    	})
    	if err != nil {
    		return fmt.Errorf("create runner: %w", err)
    	}

    	sessResp, err := sessionService.Create(ctx, &session.CreateRequest{
    		AppName: "my_agent",
    		UserID:  "demo_user",
    	})
    	if err != nil {
    		return fmt.Errorf("create session: %w", err)
    	}

    	userMsg := genai.NewContentFromText("Hello!", genai.RoleUser)
    	for _, err := range r.Run(ctx, "demo_user", sessResp.Session.ID(), userMsg, agent.RunConfig{}) {
    		if err != nil {
    			return fmt.Errorf("run error: %w", err)
    		}
    	}
    	return nil
    }

    func main() {
    	if err := run(context.Background()); err != nil {
    		log.Fatal(err)
    	}
    }
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
    [前提条件](#prerequisites) を参照してください。このプラグインは JVM 専用であり、コアの外部で
    提供されているため、統合（integrations）アーティファクトを追加します。

    ```kotlin title="build.gradle.kts"
    implementation("com.google.adk:google-adk-kotlin-integrations:1.5.0")
    ```

    ```kotlin title="BigQueryAnalyticsExample.kt"
    --8<-- "examples/kotlin/snippets/integrations/BigQueryAnalyticsExample.kt:quickstart"
    ```

    プラグインは初回使用時にイベントテーブルを作成するため、スコープ内の認証情報には、行を挿入する権限だけでなく、データセット内にテーブルを作成する権限も必要です。
    `location` にはデータセットのロケーションを設定してください（デフォルトは `"US"`）。オプションの完全なセットについては、[構成オプション](#configuration-options) を参照してください。

    ロギングの失敗によってターンが失敗することはありません。テーブルを作成できない場合や行を挿入できない場合、プラグインはエラーをログに記録し、呼び出しは続行されます。行が欠落している場合は、`com.google.adk.kt.plugins.agentanalytics.BigQueryAgentAnalyticsPlugin` のロギングを有効にしてください。ログはプラグインの ADK 名（`bigquery_agent_analytics`）ではなく、そのクラス名の下で出力されます。


### エージェントの実行とテスト

エージェントを実行し、チャットインターフェースを介して「何ができるか教えて」や「クラウドプロジェクト `<your-gcp-project-id>` のデータセットを一覧表示して」などのリクエストをいくつか送信して、プラグインをテストします。これらの操作によってイベントが生成され、Google Cloud プロジェクトの BigQuery インスタンスに記録されます。イベントが処理されたら、[BigQuery コンソール](https://console.cloud.google.com/bigquery) で次のクエリを使用してデータを確認できます。

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

??? example "Full example with GCS offloading, OpenTelemetry, and tools"

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

    === "Go"

        以下の Go の例では、カスタム `functiontool`（`reverse_string`）を登録しています。ADK Go ランナー自体は OpenTelemetry スパンを開始しないため、`cfg.EnableOTelCorrelation = true` は、`r.Run` を呼び出す前にホストアプリケーションが `ctx` 内でアクティブな OpenTelemetry スパンを開始した場合にのみ `attributes.otel` を記録することに注意してください。

        ```go title="main.go"
        package main

        import (
        	"context"
        	"fmt"
        	"log"
        	"os"
        	"time"

        	"google.golang.org/adk/plugin/agentanalytics"
        	"google.golang.org/adk/v2/agent"
        	"google.golang.org/adk/v2/agent/llmagent"
        	"google.golang.org/adk/v2/model/gemini"
        	"google.golang.org/adk/v2/plugin"
        	"google.golang.org/adk/v2/runner"
        	"google.golang.org/adk/v2/session"
        	"google.golang.org/adk/v2/tool"
        	"google.golang.org/adk/v2/tool/functiontool"
        	"google.golang.org/genai"
        )

        type ReverseArgs struct {
        	Input string `json:"input" jsonschema:"Text to reverse."`
        }

        func reverseString(_ agent.Context, args ReverseArgs) (map[string]any, error) {
        	runes := []rune(args.Input)
        	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
        		runes[i], runes[j] = runes[j], runes[i]
        	}
        	return map[string]any{"reversed": string(runes)}, nil
        }

        func run(ctx context.Context) error {
        	projectID := os.Getenv("GOOGLE_CLOUD_PROJECT")
        	datasetID := os.Getenv("BIG_QUERY_DATASET_ID")
        	gcsBucket := os.Getenv("GCS_BUCKET_NAME")

        	cfg := agentanalytics.DefaultConfig()
        	cfg.ProjectID = projectID
        	cfg.DatasetID = datasetID
        	cfg.TableName = "agent_events"
        	cfg.GCSBucketName = gcsBucket
        	cfg.LogMultiModalContent = true
        	cfg.MaxContentLen = 500 * 1024
        	cfg.EnableOTelCorrelation = true
        	cfg.ShutdownTimeout = 10 * time.Second

        	bqPlugin, err := agentanalytics.NewBigQueryAgentAnalyticsPluginWithConfig(ctx, cfg)
        	if err != nil {
        		return fmt.Errorf("failed to create BigQuery plugin: %w", err)
        	}
        	defer bqPlugin.Close()

        	reverseTool, err := functiontool.New(functiontool.Config{
        		Name:        "reverse_string",
        		Description: "Reverses the provided input string.",
        	}, reverseString)
        	if err != nil {
        		return fmt.Errorf("failed to create tool: %w", err)
        	}

        	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{
        		Project:  projectID,
        		Location: "us-central1",
        		Backend:  genai.BackendVertexAI,
        	})
        	if err != nil {
        		return fmt.Errorf("failed to create model: %w", err)
        	}

        	demoAgent, err := llmagent.New(llmagent.Config{
        		Name:        "bq_demo_agent",
        		Model:       model,
        		Instruction: "You are a helpful assistant. Use reverse_string when asked to reverse text.",
        		Tools:       []tool.Tool{reverseTool},
        	})
        	if err != nil {
        		return fmt.Errorf("failed to create agent: %w", err)
        	}

        	sessionService := session.InMemoryService()
        	r, err := runner.New(runner.Config{
        		AppName:        "bq_demo_agent",
        		Agent:          demoAgent,
        		SessionService: sessionService,
        		PluginConfig: runner.PluginConfig{
        			Plugins: []*plugin.Plugin{bqPlugin},
        		},
        	})
        	if err != nil {
        		return fmt.Errorf("failed to create runner: %w", err)
        	}

        	sessResp, err := sessionService.Create(ctx, &session.CreateRequest{
        		AppName: "bq_demo_agent",
        		UserID:  "demo_user",
        	})
        	if err != nil {
        		return fmt.Errorf("failed to create session: %w", err)
        	}

        	userMsg := genai.NewContentFromText("Please reverse the word 'analytics'.", genai.RoleUser)
        	for event, err := range r.Run(ctx, "demo_user", sessResp.Session.ID(), userMsg, agent.RunConfig{}) {
        		if err != nil {
        			return fmt.Errorf("run error: %w", err)
        		}
        		if event.IsFinalResponse() && event.Content != nil {
        			for _, part := range event.Content.Parts {
        				if part.Text != "" {
        					fmt.Printf("Agent: %s\n", part.Text)
        				}
        			}
        		}
        	}
        	return nil
        }

        func main() {
        	if err := run(context.Background()); err != nil {
        		log.Fatal(err)
        	}
        }
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
- `roles/bigquery.dataEditor`: イベントテーブルの作成またはアップグレード、イベントタイプごとのビューの作成（Python と Go はデフォルトでビューを作成）、およびログ/イベントデータの書き込みを行うためのデータセットレベル（イベントテーブルがすでに存在し、自動ビュー作成が無効になっている場合はテーブルレベル）の権限
- **GCS オフロードを使う場合:** 対象バケットの `roles/storage.objectCreator` と
  `roles/storage.objectViewer`

プリンシパルに対象テーブルのみの `roles/bigquery.dataEditor` がある場合、テーブル作成および自動ビュー作成（Python の `create_views=True`、Go の `DisableCreateViews: false`）は失敗します。データセットに対して `roles/bigquery.dataEditor` を付与するか、デプロイステップでテーブルとビューを事前作成してください（Python では `create_views=False`、Go では `DisableCreateViews: true` に加えて `bqPlugin.SyncViews(ctx)` または `cfg.ViewDefinitions()` を使用）。Go では、バックグラウンドのビュー作成の失敗は `agentanalytics.Config` に非デフォルトの `Logger` が構成されている場合にのみログ記録されるため、`Logger` を設定することを推奨します。

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
    | `credentials_identifier` | `Optional[str]` | `None` | どのプラグインインスタンスが[共有バックグラウンドライター](#shared-background-writer)を共有するかを明示的に選択。同等の認証情報とライター設定を持つインスタンスに対してのみ同じ識別子を使用してください。`config` を変更することなく `config.credentials_identifier` より優先されます |

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
    | `max_content_length` | `int` | `500 * 1024` | オフロード/切り詰め前のインラインペイロードサイズを制御。無制限にするには `-1` を使用します。それ以外の値は少なくとも `1` 以上にする必要があります |
    | `batch_size` | `int` | `1` | 書き込みスループットとレイテンシのバランスを調整（デフォルトの 1 は低レイテンシ向け、高スループットの場合は増やす） |
    | `batch_flush_interval` | `float` | `1.0` | 部分バッチを定期的にフラッシュ（秒） |
    | `shutdown_timeout` | `float` | `10.0` | シャットダウン時に最終フラッシュを待機する時間（秒） |
    | `event_allowlist` | `Optional[List[str]]` | `None` | 選択したイベントタイプのみをログに記録 |
    | `event_denylist` | `Optional[List[str]]` | `None` | 機密性の高いイベントタイプやノイズの多いイベントタイプをスキップ |
    | `content_formatter` | `Optional[Callable]` | `None` | イベントごとにカスタムマスキング/フォーマットを適用（`(content, event_type)` を受け取る） |
    | `log_multi_modal_content` | `bool` | `True` | GCS 参照を含む `content_parts` の詳細をキャプチャ |
    | `queue_max_size` | `int` | `10000` | メモリ内のイベントキューサイズを制限します。ADK Python v2.13.0 では、すべてのイベントタイプがこの容量を共有します。満杯のときは終了イベントである `INVOCATION_COMPLETED` および `INVOCATION_ERROR` 行もドロップされる可能性があり、`queue_full` としてカウントされます |
    | `retry_config` | `RetryConfig` | `RetryConfig()` | 再試行動作を調整（`max_retries=3`, `initial_delay=1.0`, `multiplier=2.0`, `max_delay=10.0`） |
    | `log_session_metadata` | `bool` | `True` | `attributes` にセッション情報を追加（`session_id`, `app_name`, `user_id`, `state`）。`temp:` プレフィックスのキーは[墨消し](#built-in-redaction)されます。 |
    | `custom_tags` | `Dict[str, Any]` | `{}` | すべてのイベントの `attributes` に静的タグ（例: `{"env": "prod"}`）を追加 |
    | `auto_schema_upgrade` | `bool` | `True` | 既存のテーブルに新しい列を自動追加（追加のみ） |
    | `create_views` | `bool` | `True` | イベントタイプごとの BigQuery ビューを作成 |
    | `create_eval_views` | `bool` | `False` | ADK Python v2.13.0 以降で、セットアップ中に[エージェント評価ビュー](#agent-evaluation-views)（`{view_prefix}_eval_session` および `{view_prefix}_eval_turn`）も作成 |
    | `view_prefix` | `str` | `"v"` | 複数のプラグインがデータセットを共有する場合のビュー名衝突を防止（例: `"v_staging"`） |
    | `enable_otel_correlation` | `bool` | `False` | ベストエフォートの Cloud Trace 結合キーとして周囲の OpenTelemetry スパンコンテキストを `attributes.otel.{span_id, trace_id}` にキャプチャ |
    | `custom_metadata_allowlist` | `Optional[List[str]]` | `None` | 選択した `event.custom_metadata` キーを `attributes.custom_metadata.*` にキャプチャ: 正確なキーまたは `"prefix*"` パターン。ADK Python v2.12.0 以降では、最終的な `LLM_RESPONSE` 行が `llm_response.custom_metadata` からキーをキャプチャします |
    | `payload_column_denylist` | `Optional[List[str]]` | `None` | 書き込み時にテーブルからペイロード列（`content`, `content_parts`, `attributes`, `latency_ms`）を除外射影 |
    | `final_response_tool_names` | `FrozenSet[str]` | `frozenset()` | 成功した選択ツールの呼び出し引数を `AGENT_RESPONSE` ペイロードとしてログ記録 |
    | `flush_on_run_end` | `bool` | `True` | 各実行の終了時にキューに入っている行の書き込み完了を待機 |
    | `exactly_once_delivery` | `bool` | `False` | コミット済みストリームと明示的なオフセットを使用して、ライブプロセッサ内での曖昧な再試行による重複を防止 |
    | `use_dedicated_background_loop` | `Optional[bool]` | `None` | バッチライターの実行場所を選択: `None` は `flush_on_run_end=False` のときに[共有バックグラウンドライター](#shared-background-writer)スレッドを使用し、`True` は常にこれを使用し、`False` はライターを呼び出し元のイベントループに維持します |
    | `credentials_identifier` | `Optional[str]` | `None` | バックグラウンドライターを共有するプラグインインスタンスを明示的に選択。コンストラクタ引数が優先されます。同等の認証情報とライター設定を持つインスタンスに対してのみ同じ識別子を使用してください |
    | `debug_content_formatter_errors` | `bool` | `False` | `content_formatter` によって発生した例外の制限付きトレースバックをプラグインのローカル Python ログ警告に追加。トレースバックには未フォーマットのコンテンツが含まれる可能性があり、BigQuery には書き込まれません |
    | `on_schema_error` | `Optional[Callable[[Exception], None]]` | `None` | ADK Python v2.12.0 以降で、[テーブル準備完了チェック](#table-readiness-callbacks)がテーブルの読み取り、作成、またはアップグレードに失敗するたびに、例外を引数として同期コールバックを実行。同期呼び出し可能オブジェクトでない値を渡すと、プラグイン構築時に `ValueError` が発生します |
    | `on_schema_ready` | `Optional[Callable[[], None]]` | `None` | ADK Python v2.12.0 以降で、要求されたすべてのビューを含め、[テーブル準備完了チェック](#table-readiness-callbacks)が成功するたびに引数なしの同期コールバックを実行。同期呼び出し可能オブジェクトでない値を渡すと、プラグイン構築時に `ValueError` が発生します |
    | `tool_result_classifier` | `Optional[ToolResultClassifier]` | `None` | ADK Python v2.13.0 以降で、`ToolResultClassification`（または組み込みの MCP `isError` / `is_error` ルールにフォールバックする場合は `None`）を返す同期コールバックを介して、返されたツール結果を `"ERROR"` または `"OK"` として分類。[ツール結果のエラー分類](#tool-result-error-classification)を参照してください |

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
    - **`custom_metadata_allowlist`**: 設定しない場合、組み込みの `a2a:*` キャプチャのみが実行される従来の動作が維持されます。キーは `event.custom_metadata` から読み取られます。ADK Python v2.12.0 以降では、最終的な（部分レスポンスではない）`LLM_RESPONSE` 行が `llm_response.custom_metadata` からキーを読み取ります。キャプチャされた値は、他のすべてのログコンテンツと同じ安全性パイプライン（切り詰め、機密キーの墨消し、循環参照の処理）を通過します。
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

    `flush_on_run_end` オプションのデフォルトは `True` であり、これにより `after_run_callback` は現在のイベントループの書き込みキューを待機します。応答パスからこのフラッシュを削除するには `False` に設定します。バックグラウンドライターはキューの排出を継続するため、実行が返されてから少し後に BigQuery に行が表示される場合があります。Python v2.10.0 以降では、この設定によりライターが[共有バックグラウンドライター](#shared-background-writer)にも移動します。

    ```python
    config = BigQueryLoggerConfig(
        final_response_tool_names=frozenset({"submit_final_response"}),
        flush_on_run_end=False,
    )
    ```

    ### 共有バックグラウンドライター {#shared-background-writer}

    <div class="language-support-tag">
      <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v2.10.0</span>
    </div>

    `flush_on_run_end=False` の場合、プラグインは呼び出し元のイベントループではなく、プロセス有効期間を持つ専用のバックグラウンドイベントループスレッドでバッチライターを実行します。`flush_on_run_end=True` の場合でもそのスレッドを使用するには `use_dedicated_background_loop=True` に設定し、ライターを呼び出し元のイベントループに維持するには `False` に設定します。

    同じプロセス内で同等の認証情報を使用して同じテーブルをターゲットとするプラグインインスタンスは、1 つのバックグラウンドライターと BigQuery 書き込みクライアントを共有するため、リクエストごとに 1 つなどの短期間のプラグインインスタンスが個別に新しいライターを開くことはありません。同等性は認証情報のアイデンティティ（サービスアカウントのメールアドレス、スコープ、プロジェクトなど）から導出されます。どのプラグインインスタンスがライターを共有するかを明示的に選択するには `credentials_identifier` を設定します。同等の認証情報とライター設定を持つインスタンスに対してのみ同じ識別子を使用してください。共有ライターは、それを作成したインスタンスの認証情報とライター設定（`batch_size` や `retry_config` など）を使用します。

    デフォルト引数で `shutdown()` または `close()` を呼び出すと、プラグインインスタンスが共有ライターから切り離されますが、ライターは実行されたままになるため、キューに入っている行は引き続き書き込まれます。インタプリタの終了時、プラグインはアクティブなライターの排出をベストエフォートで試みます。スタンドアロンスクリプトやテストの終了時などに共有ライターを明示的に排出して停止するには、`close_background_transport=True` を渡すか、`close_shared_background_transports()` を呼び出します。

    ```python
    # このプラグインのテーブルと認証情報の共有ライターを排出して停止します。
    await plugin.close(close_background_transport=True)

    # または、プロセス内のすべての共有バックグラウンドライターを排出して停止します。
    await BigQueryAgentAnalyticsPlugin.close_shared_background_transports(timeout=10.0)
    ```

    ### 配信と重複排除 {#delivery-and-deduplication}

    <div class="language-support-tag">
      <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v2.7.0</span><span class="lst-go">Go v0.1.0</span>
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

    コミット済みストリームと明示的なオフセットを使用するには、`exactly_once_delivery=True`（Go では `ExactlyOnceDelivery: true`）を設定します。これにより、最初の結果が曖昧だった再試行が、そのプロセッサの存続期間内に重複を作成するのを防ぎます。ストリームのローテーションが必要な場合、追加の BigQuery `CreateWriteStream` クォータを消費する可能性があります。

    ```python
    config = BigQueryLoggerConfig(exactly_once_delivery=True)
    ```

    その名前に反して、このオプションはロスレス配信を保証するものではありません。再試行の枯渇、オフセットの競合、または置換ストリームの失敗の後でも、バッチがドロップされる可能性があります。ストリームローテーションに失敗した後、30 秒のローテーションバックオフ中に到着したイベントもドロップされます。`offset_conflict`（Go では `AppendFailureDrops`）やその他の[ドロップ理由](#dropped-event-observability)を監視し、コンシューマ側の重複排除キーとして `event_id` を維持してください。

    **Go**（`cfg.ExactlyOnceDelivery = true`）では、ストリームローテーションと再試行の分類が Python とわずかに異なります:

    - `OutOfRange`、`NotFound`、または予期しない `AlreadyExists` の後、Go はコミット済みストリームを（バッチごとに最大 1 回）置き換え、同じ追加処理内でバッチを再送信します。ただし、以前のバッチによってストリームがローテーションされ、まだコミットされていない場合（この場合はバッチをドロップしてローテーションを一時停止します）、またはそのバッチの以前の試行の結果が不明だった場合（この場合は重複を防ぐために `OutOfRange` または `NotFound` でバッチをドロップし、次のバッチの前にストリームを置き換えます）を除きます。Python はこれら 3 つのいずれかの後にバッチをドロップし、次のバッチの前にストリームを置き換えます。
    - `Send` 成功後の RPC レベルの受信エラーにおいて、Go は `Unavailable`、`DeadlineExceeded`、`Canceled`、`Aborted`、`Internal`、および `Unknown` を結果不明として扱いますが、Python はこれらに加えて `ResourceExhausted`（`TooManyRequests`）も結果不明として扱います。

    ### テーブル準備完了コールバック {#table-readiness-callbacks}

    <div class="language-support-tag">
      <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v2.12.0</span>
    </div>

    セットアップ中にプラグインが実行するテーブル準備完了チェックを監視するには、`on_schema_error` および `on_schema_ready` を使用します。このチェックは BigQuery テーブルの読み取り、作成、またはアップグレードを行い、要求されたすべてのビューを作成します。

    - `on_schema_error`: チェックがテーブルの読み取り、作成、またはアップグレードに失敗するたびに、例外を引数として呼び出されます。チェックごとに最大 1 回トリガーされるため、セットアップの再試行中に繰り返し呼び出される可能性があります。ビューを作成できない場合やラベルのみのテーブル更新が失敗した場合は呼び出されません。プラグインはこれらの失敗をログに記録して続行します。
    - `on_schema_ready`: チェックが成功するたびに引数なしで呼び出されます。これは、テーブルが存在するか作成・アップグレードされ、要求されたすべてのビューが作成されたことを意味します。

    どちらのコールバックもイベントループではなくワーカースレッドで実行されるため、高速かつ非ブロッキングにしておく必要があります。コールバックによって発生した例外はログに記録され、抑制されます。同期呼び出し可能オブジェクトではない値を指定すると、プラグイン構築時に `ValueError` が発生します。

    チェックが成功した後は、`close()` 後、フォーク後、およびその後に pickle されたコピーを含め、同じプラグインの以降のセットアップではチェックがスキップされます。どちらのコールバックも再度トリガーされることはなく、それ以降のテーブル停止は行の書き込み時に[ドロップされた行](#dropped-event-observability)としてのみ現れます。チェックを待機していたセットアップがキャンセルされた場合、または `create_analytics_views()` の呼び出しがビューの作成に失敗した場合にのみ、以降のセットアップでチェックが再実行されます。すべてのビューを作成する `create_analytics_views()` の呼び出しにより、以降のセットアップはチェックをスキップするようになり、独自のビュー作成でコールバックが呼び出されることはありません。

    標準の `pickle` モジュールでプラグインをシリアライズする場合、コールバックはモジュールレベルの関数など、pickle 可能である必要があります。ラムダやクロージャは `pickle` でシリアライズできず、バインドされたメソッドはそのインスタンスを pickle します。

    ### ツール結果のエラー分類 {#tool-result-error-classification}

    <div class="language-support-tag">
      <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v2.13.0</span>
    </div>

    多くのツールは、例外を発生させる代わりに構造化されたエラーペイロードを返します。ADK Python v2.13.0 以降では、`after_tool_callback` がすべてのツール結果を次の 3 つのステップで評価します:

    1. **`ReflectAndRetryToolPlugin` のエラー応答**（`response_type` で識別）は、`error_details` または `error_type` を使用して常に `TOOL_ERROR` として記録されます。さらに、`on_tool_error_callback` がすでに記録した例外をツールが発生させた場合、同じ失敗が 2 回ログ記録されないように、後続のプラグインのフォールバック応答は `after_tool_callback` でスキップされます。発生したすべてのエラーを直接監視できるように、`ReflectAndRetryToolPlugin` などの再試行プラグインより前に `BigQueryAgentAnalyticsPlugin` を登録してください。
    2. **カスタム `tool_result_classifier`**: `BigQueryLoggerConfig` で構成されている場合、プラグインは `tool_result_classifier(tool=..., tool_args=..., tool_context=..., result=...)` を呼び出します。分類器は同期的である必要があり、`ToolResultClassification(status="ERROR" | "OK", error_message=...)` または `None` を返す必要があります:
       - `status="ERROR"` は、`status="ERROR"` および指定された `error_message`（省略された場合は固定のデフォルトメッセージ）を使用して、呼び出しを `TOOL_ERROR` としてログに記録します。未フォーマットのエラーペイロードが `content` に書き込まれないように、ツール結果自体は `TOOL_ERROR` のコンテンツから省略されます。`content_formatter` と `payload_column_denylist` は `error_message` には適用されないため、そのテキストの保存が許容される場合にのみツール出力を `error_message` にコピーしてください。
       - `status="OK"` は、以下の組み込み MCP ルールがフラグ付けする場合であっても、呼び出しを `TOOL_COMPLETED` としてログに記録します。
       - `None` は、判定を組み込みルールに委ねます。
    3. **組み込みの MCP `isError` / `is_error` ルール**: トップレベルの `isError` または `is_error` が `True` である辞書の結果または MCP `CallToolResult` モデルは、固定メッセージ `"Tool returned an MCP result with isError=true."` とともに `TOOL_ERROR` として記録されます。

    ```python
    from google.adk.plugins.bigquery_agent_analytics_plugin import (
        BigQueryLoggerConfig,
        ToolResultClassification,
    )

    def classify_tool_result(*, tool, tool_args, tool_context, result):
        if isinstance(result, dict) and result.get("status") == "ERROR":
            return ToolResultClassification(
                status="ERROR",
                error_message=result.get("error_code", "tool returned status=ERROR"),
            )
        return None  # 組み込みの MCP isError / is_error チェックにフォールバック

    config = BigQueryLoggerConfig(
        tool_result_classifier=classify_tool_result,
    )
    ```

    ### エージェント評価ビュー {#agent-evaluation-views}

    <div class="language-support-tag">
      <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v2.13.0</span>
    </div>

    `BigQueryLoggerConfig` で `create_eval_views=True` を設定する（またはオンデマンドで `await plugin.create_eval_views()` を呼び出す）と、セッションごとおよびターンごとのロールアップメトリクスとともに、`trace`（`JSON`）列に `google.cloud.aiplatform.v1beta1.AgentData` 評価トレースを再構築する 2 つのビューが作成されます:

    - **`{view_prefix}_eval_session`**（デフォルトは `v_eval_session`）: `session_id` ごとに 1 行で、セッションレベルのメトリクス（`turn_count`、`tool_call_count`、`tool_error_count`、`llm_error_count`、`agent_error_count`、`has_error`、`has_truncated_content`、`has_tool_loop`、`max_consecutive_identical_tool_calls`、`distinct_tools_used`、`total_prompt_tokens`、`total_completion_tokens`、`total_tokens`、`total_latency_ms`、`eval_ready`）とマルチターンの `trace` を含みます。
    - **`{view_prefix}_eval_turn`**（デフォルトは `v_eval_turn`）: `(session_id, invocation_id)` ターンごとに 1 行で、`turn_index`、ターンレベルのメトリクス（`turn_latency_ms`、トークン数とエラー数、`eval_ready`）、および内部の `turn_index` が `0` であるシングルターンの `trace` を含みます。

    ADK Python v2.13.0 では、評価ビューには `content`（`payload_column_denylist` に `"content"` を指定すると `ValueError` が発生します）と、以下にリストされている全 15 個のイベントが必要です。`event_allowlist` / `event_denylist` で必須イベントを除外することは拒否されます（このリリースには会話のみの評価モードはありません）:

    - `USER_MESSAGE_RECEIVED`、`AGENT_STARTING`、`LLM_REQUEST`、`TOOL_STARTING`、`TOOL_COMPLETED`、`TOOL_PAUSED`、`AGENT_TRANSFER`、`HITL_CREDENTIAL_REQUEST`、`HITL_CONFIRMATION_REQUEST`、`HITL_INPUT_REQUEST`、`HITL_CREDENTIAL_REQUEST_COMPLETED`、`HITL_CONFIRMATION_REQUEST_COMPLETED`、`HITL_INPUT_REQUEST_COMPLETED`、`AGENT_RESPONSE`、および `INVOCATION_COMPLETED`。

    ビューはテーブル全体を `session_id` / `invocation_id` で集計するため、`session_start_timestamp` または `turn_start_timestamp` でフィルタリングしてもベーステーブルの `timestamp` パーティションはプルーニングされません。大規模なテーブルの場合は、評価ジョブを実行する前に日付でフィルタリングしたスライスを実体化（materialize）してください。

=== "Go"

    Go（`google.golang.org/adk/plugin/agentanalytics`）では、次の 3 つのコンストラクタのいずれかを使用してプラグインを構築できます:

    - **`agentanalytics.NewBigQueryAgentAnalyticsPlugin(ctx, projectID, datasetID, tableID)`**:
      `ProjectID`、`DatasetID`、`TableName` を設定した `agentanalytics.DefaultConfig()` を使用します。
    - **`agentanalytics.NewBigQueryAgentAnalyticsPluginWithConfig(ctx, cfg)`**:
      カスタマイズされた `agentanalytics.Config` を使用します。ゼロ初期化された `agentanalytics.Config{}` は `Enabled: false` となり何もしない無効なプラグインを返すため、常に `cfg := agentanalytics.DefaultConfig()` から開始するか、明示的に `Enabled: true` を設定してください。
    - **`agentanalytics.NewBigQueryAgentAnalyticsPluginWithClients(ctx, cfg, bqClient, writeClient)`**:
      呼び出し元が提供した `*bigquery.Client` および `*bqstorage.BigQueryWriteClient` インスタンスを使用します。`bqClient` が非 nil で、`cfg.ProjectID` が空または `bigquery.DetectProjectID` の場合、プラグインは `bqClient.Project()` を使用します。事前プロビジョニングされた追加専用のデプロイ向けに、`bqClient == nil` を渡すとテーブルの検査、作成、スキーマアップグレード、および自動ビュー作成がスキップされます（そのモードでは `cfg.ProjectID` を明示的に設定する必要があり、`bqPlugin.SyncViews` を呼び出すと `agentanalytics: BigQuery client is not configured for view creation` が返されます。代わりに各ビューの `Name`、`EventType`、`Query` を取得するには `cfg.ViewDefinitions()` を使用してください）。

    #### `agentanalytics.Config` フィールド

    | フィールド | 型 | デフォルト値（`DefaultConfig()`） | 使用するタイミング |
    | --- | --- | --- | --- |
    | `Enabled` | `bool` | `true` | プラグインを有効または無効にします。`DefaultConfig()` を使用しない構造体リテラルでは、明示的に `Enabled: true` を設定してください |
    | `ProjectID` | `string` | `""`（プロジェクト ID を設定するか、プラグインがクライアントを作成する場合は `bigquery.DetectProjectID` を使用します。非 nil の `bqClient` が提供された場合、空の値は `bqClient.Project()` を使用します。`bqClient` が nil の場合は明示的なプロジェクト ID を設定してください） | Google Cloud プロジェクトを選択 |
    | `DatasetID` | `string` | `"agent_analytics"` | BigQuery データセットを選択 |
    | `TableName` | `string` | `"agent_events"` | BigQuery テーブル名を選択 |
    | `MaxContentLen` | `int` | `500 * 1024` | インラインテキスト値をこの Unicode コードポイント（rune）数で切り詰めます。`0` はデフォルト（`500 * 1024` rune）を使用し、`-1` は切り詰めを無効にします |
    | `BatchSize` | `int` | `100` | 書き込みバッチごとにデキューされる最大行数 |
    | `BatchFlushIntv` | `time.Duration` | `time.Second` | 部分バッチをフラッシュするまでの最大間隔 |
    | `QueueMaxSize` | `int` | `10000` | 新しいイベントがドロップ（`QueueFullDrops`）されるまでのメモリ内行チャネルの容量 |
    | `ClientOptions` | `[]option.ClientOption` | `nil` | BigQuery および Storage Write API クライアント用のカスタム Google Cloud クライアントオプション（認証情報、エンドポイント） |
    | `ClusteringFields` | `[]string` | `[]string{"event_type", "agent", "user_id"}` | テーブル作成時のクラスタ化フィールドをカスタマイズ（最大 4 フィールド） |
    | `CustomTags` | `map[string]any` | `map[string]any{}`（`make(map[string]any)`） | すべての行の `attributes.custom_tags` の下に静的なキー・バリュータグを追加 |
    | `LogMultiModalContent` | `bool` | `true` | ユーザーメッセージおよびモデルのリクエスト/レスポンスに対して `content_parts` を設定 |
    | `DisableMultiModalContent` | `bool` | `false` | `DefaultConfig()` から開始した場合でも `content_parts` の抽出を明示的に無効化 |
    | `ShutdownTimeout` | `time.Duration` | `10 * time.Second` | 各バックグラウンドバッチ書き込み（再試行を含む）、実行終了時のフラッシュ、および `Close()` がキューを排出する際の BigQuery 書き込みの上限時間。これは `Close()` 全体の単一の経過時間上限ではなく、GCS アップロードやビュー作成を伴う場合、`Close()` にはかなり長い時間（最大で `ShutdownTimeout` の約 2.5 倍）かかることがあります |
    | `Logger` | `agentanalytics.Logger` | `log.Default()` | 警告およびエラー診断（バックグラウンドのビュー作成失敗を含む）のために `Printf(format string, v ...any)` と `Println(v ...any)` の両方を実装するカスタムロガー |
    | `RetryConfig` | `agentanalytics.RetryConfig` | `MaxRetries: 3`, `InitialDelay: 100ms`, `MaxDelay: 10s`, `Multiplier: 2.0` | 再試行可能な Storage Write API 追加エラーに対する指数バックオフを調整 |
    | `DisableSessionMetadata` | `bool` | `false` | `attributes.session_metadata`（`session_id`, `app_name`, `user_id`, `state`）を省略 |
    | `CaptureFullMessageContent` | `bool` | `false` | テキストペイロードの長さによる切り詰めを無効化（`MaxContentLen` は無視されますが、機密キーの墨消しは引き続き実行されます） |
    | `DisableSensitiveKeyRedaction` | `bool` | `false` | 自動的な機密キー、`temp:` 値、URI、ヘッダー、および認証情報パターンの墨消しをオプトアウトします。これによって `state_delta` 内のトップレベルの小文字の `temp:` エントリが保持されるわけではなく、それらは引き続き削除され、`temp:` のみの `STATE_DELTA` 行も引き続き抑制されます |
    | `ContentFormatter` | `agentanalytics.ContentFormatter` | `nil` | シリアライズ前に適用されるカスタム `func(payload any, eventType string) (any, error)` |
    | `DebugContentFormatterErrors` | `bool` | `false` | `ContentFormatter` が失敗した際、未加工のエラーテキストをログに記録することなく、エラーの形状メタデータ（バイト長など）をローカルの警告ログに含める |
    | `EventAllowlist` | `[]string` | `nil` | リストされたイベントタイプのみをログに記録（セッションイベント行のエイリアスとして `"EVENT"` をサポート） |
    | `EventDenylist` | `[]string` | `nil` | リストされたイベントタイプをスキップ |
    | `PayloadColumnDenylist` | `[]string` | `nil` | 選択したペイロード列（`"content"`, `"content_parts"`, `"attributes"`, `"latency_ms"`）をテーブルスキーマ、書き込まれる行、およびビューから省略 |
    | `CustomMetadataAllowlist` | `[]string` | `nil` | `session.Event.CustomMetadata` および最終的な `model.LLMResponse.CustomMetadata` から一致するキー（完全一致または `"prefix*"`）を `attributes.custom_metadata` にキャプチャします。また、`AGENT_STATE_CHECKPOINT` の出力（`"adk_agent_state"` / `"agent_state"` または `"end_of_agent"` / `"adk_end_of_agent"` などのチェックポイントキーが一致する場合）および `CustomMetadata` で伝達される `"adk_compaction"` も制御します |
    | `FinalResponseToolNames` | `[]string` | `nil` | リストされたツールが完了したときに、`attributes.source_tool` を含む追加の `AGENT_RESPONSE` 行を出力 |
    | `DisableFlushOnRunEnd` | `bool` | `false` | 各 `AfterRun` コールバックの終了時にバッチキューのフラッシュを待機しない |
    | `DisableSchemaUpgrade` | `bool` | `false` | 既存テーブルに対する自動的な追加スキーマアップグレードを無効化 |
    | `EnableOTelCorrelation` | `bool` | `false` | 周囲の OpenTelemetry の `span_id` と `trace_id` を `attributes.otel` の下にキャプチャ |
    | `GCSBucketName` | `string` | `""` | `MaxInlineTextSize` より大きいインラインテキストとバイナリ blob をこの GCS バケットにオフロード |
    | `GCSClientOptions` | `[]option.ClientOption` | `nil` | デフォルトの GCS クライアント用のカスタムクライアントオプション（空の場合は `ClientOptions` にフォールバック） |
    | `GCSPathPrefix` | `string` | `""` | オフロードされた GCS パスの先頭に付加されるオプションのオブジェクト名プレフィックス |
    | `ConnectionID` | `string` | `""` | オブジェクトテーブル / 署名付き URL 向けに `object_ref.authorizer` として保存される BigQuery 接続 ID（`"location.connection_id"`） |
    | `MaxInlineTextSize` | `int` | `32 * 1024` | オフロードが構成されている場合に、これを超えるとテキストパーツが GCS にオフロードされるバイトしきい値（デフォルトは `32 KiB`） |
    | `GCSMaxConcurrentUploads` | `int` | `8` | バッチフラッシュ中の最大同時 GCS アップロード数 |
    | `GCSUploadTimeout` | `time.Duration` | `10 * time.Second` | バッチごとの同時 GCS アップロードのデッドライン。タイムアウト後、未完了のパーツはフォールバックし、同じ期間だけオフロードが一時停止します |
    | `GCSMaxPendingUploadBytes` | `int64` | `256 * 1024 * 1024` | バッファリングされた行全体で GCS アップロード用にキューに入れられた保留中のテキストおよびバイナリペイロードバイト数のメモリ上限（デフォルトは `256 MiB`） |
    | `GCSOffloader` | `agentanalytics.GCSContentOffloader` | `nil` | カスタムオフローダー実装（`GCSBucketName` から作成されるデフォルトの GCS クライアントをオーバーライド） |
    | `DisableCreateViews` | `bool` | `false` | イベントタイプごとの 25 個の BigQuery ビュー（`v_<event_type>`）のバックグラウンドでの自動作成を無効化 |
    | `ViewPrefix` | `string` | `"v"` | イベントタイプごとのビュー名のプレフィックス（`<ViewPrefix>_<event_type>`） |
    | `ExactlyOnceDelivery` | `bool` | `false` | デフォルトストリームの代わりに、明示的なバッチオフセットを持つ `COMMITTED` Storage Write ストリームを介して書き込む |

    Go では、`ContentFormatter` は未加工の型付きコンテンツペイロードを受け取ります（静的な `AGENT_STARTING` 指示の場合は文字列、`USER_MESSAGE_RECEIVED` の場合は `*genai.Content`、`LLM_REQUEST` の場合は `*model.LLMRequest`、`LLM_RESPONSE` の場合は `*model.LLMResponse`、ツールやその他のマップ形式のイベントの場合はマップ）。`NODE_OUTPUT` と `A2A_INTERACTION` は元の出力/応答値をそのまま渡し、スライスやスカラーになることもあります。属性（attributes）は変換しません。特に、`STATE_DELTA` はペイロードを `attributes.state_delta` に格納するため、`ContentFormatter` を呼び出しません。変更するポインタ、スライス、またはマップ（`*genai.Content` 内の `Part.Text`、`Part.ExecutableCode.Code`、`Part.CodeExecutionResult.Output`、`Part.FunctionCall.Args`、`Part.FunctionResponse.Response` を含む）はクローンを作成し、ライブペイロードを決して直接変更しないでください。

    以下のヘルパーは編集する値のクローンを作成し、ネストが 50 レベルに達すると停止します。過度にネストされたペイロードや循環参照を含むペイロードはエラーを返すため、プラグインはプロセスクラッシュのリスクを冒す代わりに `[FORMATTER_FAILED]` を記録します。これらのヘルパーは JSON 形式の `map[string]any` および `[]any` 値（さらに `[]string`、`map[string]string`、`[]map[string]any`）を再帰的に処理します。ツールが返すその他の具体的な型については境界のあるケースを追加するか、フォーマット前にそれらの値を正規化し、この墨消しに依存する前に実際のペイロードでテストしてください:

    ```go title="analytics.go"
    package analytics

    import (
    	"context"
    	"fmt"
    	"regexp"
    	"time"

    	"google.golang.org/adk/plugin/agentanalytics"
    	"google.golang.org/adk/v2/model"
    	"google.golang.org/genai"
    )

    var dollarPattern = regexp.MustCompile(`\$\d+(?:,\d{3})*(?:\.\d+)?`)

    func maskContent(c *genai.Content, eventType string, depth int) (*genai.Content, error) {
    	if depth >= 50 {
    		return nil, fmt.Errorf("redaction nesting limit exceeded")
    	}
    	if c == nil {
    		return nil, nil
    	}
    	cloned := *c
    	if len(c.Parts) > 0 {
    		cloned.Parts = make([]*genai.Part, len(c.Parts))
    		for i, p := range c.Parts {
    			if p == nil {
    				continue
    			}
    			partCopy := *p
    			if partCopy.Text != "" {
    				partCopy.Text = dollarPattern.ReplaceAllString(partCopy.Text, "xxx")
    			}
    			if partCopy.ExecutableCode != nil {
    				codeCopy := *partCopy.ExecutableCode
    				codeCopy.Code = dollarPattern.ReplaceAllString(codeCopy.Code, "xxx")
    				partCopy.ExecutableCode = &codeCopy
    			}
    			if partCopy.CodeExecutionResult != nil {
    				resultCopy := *partCopy.CodeExecutionResult
    				resultCopy.Output = dollarPattern.ReplaceAllString(resultCopy.Output, "xxx")
    				partCopy.CodeExecutionResult = &resultCopy
    			}
    			if partCopy.FunctionCall != nil {
    				fcCopy := *partCopy.FunctionCall
    				if fcCopy.Args != nil {
    					redactedArgs, err := redactDollarAmountsAtDepth(fcCopy.Args, eventType, depth+1)
    					if err != nil {
    						return nil, err
    					}
    					if argsMap, ok := redactedArgs.(map[string]any); ok {
    						fcCopy.Args = argsMap
    					}
    				}
    				partCopy.FunctionCall = &fcCopy
    			}
    			if partCopy.FunctionResponse != nil {
    				frCopy := *partCopy.FunctionResponse
    				if frCopy.Response != nil {
    					redactedResp, err := redactDollarAmountsAtDepth(frCopy.Response, eventType, depth+1)
    					if err != nil {
    						return nil, err
    					}
    					if respMap, ok := redactedResp.(map[string]any); ok {
    						frCopy.Response = respMap
    					}
    				}
    				partCopy.FunctionResponse = &frCopy
    			}
    			cloned.Parts[i] = &partCopy
    		}
    	}
    	return &cloned, nil
    }

    func redactDollarAmounts(payload any, eventType string) (any, error) {
    	return redactDollarAmountsAtDepth(payload, eventType, 0)
    }

    func redactDollarAmountsAtDepth(payload any, eventType string, depth int) (any, error) {
    	if depth >= 50 {
    		return nil, fmt.Errorf("redaction nesting limit exceeded")
    	}
    	switch v := payload.(type) {
    	case string:
    		return dollarPattern.ReplaceAllString(v, "xxx"), nil
    	case *genai.Content:
    		return maskContent(v, eventType, depth+1)
    	case *model.LLMRequest:
    		if v == nil {
    			return nil, nil
    		}
    		cloned := *v
    		if len(v.Contents) > 0 {
    			cloned.Contents = make([]*genai.Content, len(v.Contents))
    			for i, c := range v.Contents {
    				masked, err := maskContent(c, eventType, depth+1)
    				if err != nil {
    					return nil, err
    				}
    				cloned.Contents[i] = masked
    			}
    		}
    		if v.Config != nil && v.Config.SystemInstruction != nil {
    			maskedSys, err := maskContent(v.Config.SystemInstruction, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cfgCopy := *v.Config
    			cfgCopy.SystemInstruction = maskedSys
    			cloned.Config = &cfgCopy
    		}
    		return &cloned, nil
    	case *model.LLMResponse:
    		if v == nil {
    			return nil, nil
    		}
    		maskedContent, err := maskContent(v.Content, eventType, depth+1)
    		if err != nil {
    			return nil, err
    		}
    		cloned := *v
    		cloned.Content = maskedContent
    		return &cloned, nil
    	case map[string]any:
    		if v == nil {
    			return map[string]any(nil), nil
    		}
    		cloned := make(map[string]any, len(v))
    		for k, val := range v {
    			redacted, err := redactDollarAmountsAtDepth(val, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[k] = redacted
    		}
    		return cloned, nil
    	case map[string]string:
    		if v == nil {
    			return map[string]string(nil), nil
    		}
    		cloned := make(map[string]string, len(v))
    		for k, val := range v {
    			redacted, err := redactDollarAmountsAtDepth(val, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[k], _ = redacted.(string)
    		}
    		return cloned, nil
    	case []any:
    		if v == nil {
    			return []any(nil), nil
    		}
    		cloned := make([]any, len(v))
    		for i, item := range v {
    			redacted, err := redactDollarAmountsAtDepth(item, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[i] = redacted
    		}
    		return cloned, nil
    	case []string:
    		if v == nil {
    			return []string(nil), nil
    		}
    		cloned := make([]string, len(v))
    		for i, item := range v {
    			redacted, err := redactDollarAmountsAtDepth(item, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[i], _ = redacted.(string)
    		}
    		return cloned, nil
    	case []map[string]any:
    		if v == nil {
    			return []map[string]any(nil), nil
    		}
    		cloned := make([]map[string]any, len(v))
    		for i, item := range v {
    			redacted, err := redactDollarAmountsAtDepth(item, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[i], _ = redacted.(map[string]any)
    		}
    		return cloned, nil
    	default:
    		return payload, nil
    	}
    }

    func CreatePlugin(ctx context.Context) (*agentanalytics.BigQueryAgentAnalyticsPlugin, error) {
    	cfg := agentanalytics.DefaultConfig()
    	cfg.ProjectID = "my-project"
    	cfg.DatasetID = "my_dataset"
    	cfg.TableName = "agent_events"
    	cfg.EventAllowlist = []string{
    		agentanalytics.EventUserMessageReceived,
    		agentanalytics.EventLLMRequest,
    		agentanalytics.EventLLMResponse,
    	}
    	cfg.ShutdownTimeout = 10 * time.Second
    	cfg.MaxContentLen = 500 * 1024
    	cfg.ContentFormatter = redactDollarAmounts
    	cfg.EnableOTelCorrelation = true
    	cfg.CustomMetadataAllowlist = []string{"ticket_id", "exp:*"}
    	cfg.ExactlyOnceDelivery = true

    	adkPlugin, err := agentanalytics.NewBigQueryAgentAnalyticsPluginWithConfig(ctx, cfg)
    	if err != nil {
    		return nil, err
    	}
    	bqPlugin, ok := agentanalytics.AsBigQueryAgentAnalyticsPlugin(adkPlugin)
    	if !ok {
    		return nil, fmt.Errorf("unexpected plugin wrapper")
    	}
    	return bqPlugin, nil
    }
    ```

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

    バッチ処理、コンテンツフォーマット、イベント許可リスト、GCS オフロード、ビュー作成など、**Python**、**Go**、および **Java** タブに記載されているオプションは Kotlin には存在しません。

## スキーマと本番環境セットアップ

### スキーマリファレンス

イベントテーブル（`agent_events`）は柔軟なスキーマを使用します。次の表は、サンプル値を含む包括的なリファレンスを提供します。

| フィールド名 | 型 | モード | 説明 | サンプル値 |
| --- | --- | --- | --- | --- |
| **timestamp** | `TIMESTAMP` | `REQUIRED` | イベント作成の UTC タイムスタンプ。プライマリソートキーおよび日次パーティションキーとして機能します。精度はマイクロ秒です。 | `2026-02-03 20:52:17 UTC` |
| **event_id** | `STRING` | `NULLABLE` | エンキュー前に割り当てられた 32 文字の 16 進数 ID（Python および Go）。コンシューマが重複行を識別できるように、Storage Write API の再試行全体で保持されます。スキーマバージョン 2 より前に書き込まれた行は `NULL` です。 | `ca5e3c9d99e24e46b614f2f44f93bf6e` |
| **event_type** | `STRING` | `NULLABLE` | 正規のイベントカテゴリ。[イベントタイプとペイロード](#event-types) で説明されている LLM、ツール、エージェント、呼び出し、状態、HITL、A2A、レスポンス、ワークフロー、ノード出力、ノードエラーイベントなどの標準値が含まれます。高レベルのフィルタリングに使用されます。 | `LLM_REQUEST` |
| **agent** | `STRING` | `NULLABLE` | このイベントを担当するエージェントの名前。エージェントの初期化中または `root_agent_name` コンテキストを介して定義されます。 | `my_bq_agent` |
| **session_id** | `STRING` | `NULLABLE` | 会話スレッド全体の永続的な識別子。複数のターンやサブエージェント呼び出しにわたって一定に保たれます。 | `04275a01-1649-4a30-b6a7-5b443c69a7bc` |
| **invocation_id** | `STRING` | `NULLABLE` | 単一の実行ターンまたはリクエストサイクルのユニークな識別子。多くのコンテキストで `trace_id` に対応します。 | `e-b55b2000-68c6-4e8b-b3b3-ffb454a92e40` |
| **user_id** | `STRING` | `NULLABLE` | セッションを開始したユーザー（人間またはシステム）の識別子。`User` オブジェクトまたはメタデータから抽出されます。 | `test_user` |
| **trace_id** | `STRING` | `NULLABLE` | トレース識別子。周囲のスパン（例: Agent Engine の呼び出しスパンや ADK Runner スパン）から継承された場合は 32 文字の 16 進数 OpenTelemetry トレース ID になるため、BigQuery の行は既存の Cloud Trace トレースとスムーズに結合されます。周囲のスパンがない場合、Python はランダムな 32 文字の 16 進数フォールバックを生成します。周囲のスパンがない場合、Go は `invocation_id` が空のときにランダムな 32 文字の 16 進数 `trace_id` を生成します。それ以外の場合は、プラグインごとのランダムなシードと呼び出し ID に対して SHA-256 を使用し、そのプラグインインスタンス内で安定した 32 文字の 16 進数 ID を生成します。Java は ADK の呼び出し ID にフォールバックします。単一の分散リクエストライフサイクル内のすべての操作をリンクします。 | `a2c7f13d3a3f0bbb8793692f76a6012a` |
| **span_id** | `STRING` | `NULLABLE` | この特定の原子的操作を識別する 16 文字の 16 進数スパン ID。**プラグインの内部スタックで追跡され、OTel スパンとしてはエクスポートされません。** プラグインは設定された OpenTelemetry プロバイダーに対して `tracer.start_span` を呼び出しません。Python と Java では、ルート呼び出しスパンは周囲の OTel スパンがアクティブな場合にその ID を再利用します。Go では、プラグインは常に独自の 16 文字の 16 進数ルート `span_id` を生成し、周囲の OTel スパン ID があれば `parent_span_id` に記録します。子スパンは内部で生成されます（[トレースと可観測性](#tracing-and-observability)を参照）。 | `3916f5762bcd4d42` |
| **parent_span_id** | `STRING` | `NULLABLE` | 直前の呼び出し元のスパン ID。親子実行ツリー（DAG）を再構築するために使用されます。 | `4c4a42bfdeb84934` |
| **content** | `JSON` | `NULLABLE` | JSON として保存されるイベント固有のデータ（ペイロード）。構造はイベントタイプによって異なります。 | `{"model": "gemini-flash-latest", ...}` |
| **content_parts** | `ARRAY<STRUCT>` | `REPEATED` | 構造化パーツの配列。テキストチャンク、GCS に保存されているファイルへの URI/ObjectRef（ストレージオフロード用）、MIME タイプ、パーツメタデータをキャプチャします。 | `[{mime_type: "image/png", uri: "gs://..."}]` |
| **attributes** | `JSON` | `NULLABLE` | 追加メタデータ（例: `root_agent_name`、`model_version`、`usage_metadata`、`session_metadata`、`custom_tags`）のための任意のキー値ペア。 | `{"model_version": "gemini-flash-latest", ...}` |
| **latency_ms** | `JSON` | `NULLABLE` | レイテンシ測定値（例: 合計ミリ秒数である `total_ms`）。 | `{"total_ms": 1250}` |
| **status** | `STRING` | `NULLABLE` | イベントの結果。通常は 'OK' または 'ERROR' です。 | `OK` |
| **error_message** | `STRING` | `NULLABLE` | 例外およびモデル終了の詳細に関するサニタイズされた診断メッセージ。Python と Go では、最終的な `LLM_RESPONSE` やカスタム `content_formatter` / `ContentFormatter` が失敗した行（例: `content_formatter raised ImportError` または `content_formatter panicked`）など、`status` が `OK` のままの行にも入力される場合があります。 | `Error 404: Dataset not found` |
| **is_truncated** | `BOOLEAN` | `NULLABLE` | 設定された `max_content_length`（Go では `MaxContentLen`）、サニタイザーの深さやノードの制限、診断テキストのサニタイズなど、コンテンツまたはメタデータが安全境界によって切り詰められたか置き換えられた場合に `true`。ADK Python v2.12.0 以降では、モデルレスポンスのフォーマットされた部分での一般的な認証情報パターンの墨消しや、レスポンスまたはコンパクションコンテンツの組み込みフォーマットが失敗したときに書き込まれるプレースホルダーである `[FORMATTING FAILED]` によっても設定されます（カスタム `content_formatter` の失敗を示す `[FORMATTER_FAILED]` と混同しないでください）。通常の構造化された機密キーの墨消し自体では設定されません。 | `false` |

Python と Go では、`event_id` 列はスキーマバージョン 2 の一部です。Python の `auto_schema_upgrade=True`（または Go の `DisableSchemaUpgrade: false`、どちらもデフォルト）を使用すると、プラグインは既存のテーブルにこの列を自動的に追加します。テーブルスキーマを自分で管理する場合は、ADK Python v2.7.0+ または ADK Go を使用する前にこの列を追加してください。

Java スキーマには `event_id` は含まれません。以下の手動 DDL から作成されたテーブルは、この列が NULL 許容であるため Java との互換性が維持されます。

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
      error_message STRING OPTIONS(description="Diagnostic message for errors and model termination details; may be populated on rows whose status is 'OK', such as LLM_RESPONSE rows and rows whose content_formatter failed."),
      is_truncated BOOLEAN OPTIONS(description="Flag indicates if content was truncated.")
    )
    PARTITION BY DATE(timestamp)
    CLUSTER BY event_type, agent, user_id;
    ```

### 自動作成されるビュー

<div class="language-support-tag">
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v1.27.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v1.5.0</span>
</div>

Python（`create_views=True`）および Go（`DisableCreateViews: false`）では、プラグインはデフォルトで各イベントタイプのビューを自動生成します。Java では `createViews(true)` を設定します（デフォルトは `false`）。Kotlin はビューを作成しません。ビューは一般的な JSON 構造をフラットな型付き列に unnest するため、反復的な `JSON_VALUE` および `JSON_QUERY` 式を記述する必要がなくなります。

ビュー名は `{view_prefix}_{event_type_lowercase}` の命名規則に従います（例: デフォルトプレフィックス `"v"` の場合、`LLM_REQUEST` は `v_llm_request` になります）。複数のプラグインインスタンスが同一データセット内の異なるテーブルに書き込む場合は、`BigQueryLoggerConfig` の `view_prefix`（Go の `agentanalytics.Config` では `ViewPrefix`）に固有の値を設定して、ビュー名の競合を防止してください。

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

オンデマンドでビューを更新することもできます:

- **Python**: `await plugin.create_analytics_views()` を呼び出します（Python v2.13.0+ で[エージェント評価ビュー](#agent-evaluation-views)を作成する場合は `await plugin.create_eval_views()` も呼び出します）。
- **Go**: `bqPlugin, ok := agentanalytics.AsBigQueryAgentAnalyticsPlugin(adkPlugin)` でプラグインをアンラップし、`bqPlugin.SyncViews(ctx)` を呼び出します。`NewBigQueryAgentAnalyticsPluginWithClients(..., nil, ...)`（`bqClient == nil`）でプラグインを構築した場合、プラグインはビューを自動作成せず、`SyncViews` は `agentanalytics: BigQuery client is not configured for view creation` を返します。代わりにビュー DDL を確認または自分で実行するには、`cfg.ViewDefinitions()`（`Name`、`EventType`、`Query` を返す）を使用してください。

すべての Python および Go ビューには次の **共通列** が含まれます: `timestamp`、`event_id`、`event_type`、`agent`、`session_id`、`invocation_id`、`user_id`、`trace_id`、`span_id`、`parent_span_id`、`status`、`error_message`、`is_truncated`。Java ビューには、`event_id` を除く同じ共通列が含まれます。

次の表は、イベントタイプごとのビューとそれぞれのイベント固有の列の一覧です。

| ビュー名 | イベント固有の列 |
| --- | --- |
| **`v_user_message_received`** | *(共通列のみ)* |
| **`v_llm_request`** | `model` (STRING), `request_content` (JSON), `llm_config` (JSON), `tools` (JSON) |
| **`v_llm_response`** | `response` (JSON), `usage_prompt_tokens` (INT64), `usage_completion_tokens` (INT64), `usage_total_tokens` (INT64), `usage_cached_tokens` (INT64), `usage_thinking_tokens` (INT64), `usage_tool_use_tokens` (INT64), `context_cache_hit_rate` (FLOAT64), `total_ms` (INT64), `ttft_ms` (INT64), `model_version` (STRING), `usage_metadata` (JSON), `cache_metadata` (JSON), `cache_type` (STRING), `finish_reason` (STRING) |
| **`v_llm_error`** | `total_ms` (INT64) |
| **`v_tool_starting`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING) |
| **`v_tool_completed`** | `tool_name` (STRING), `tool_result` (JSON), `tool_origin` (STRING), `total_ms` (INT64), `pause_kind` (STRING), `function_call_id` (STRING) |
| **`v_tool_error`** | `tool_name` (STRING), `tool_args` (JSON), `tool_origin` (STRING), `total_ms` (INT64) |
| **`v_agent_starting`** | `agent_instruction` (STRING); ADK Python v2.12.0+ および Go では、`instruction_source` (STRING)、`static_instruction` (STRING; Go では常に `NULL`)、`agent_description` (STRING)、`model` (STRING)、`sub_agents` (JSON) も含む |
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

上記のイベントタイプごとのビューに加えて、ADK Python v2.13.0 以降では、`create_eval_views=True` が設定されている場合または `await plugin.create_eval_views()` が呼び出された場合に、2 つのオプションの[エージェント評価ビュー](#agent-evaluation-views)（`v_eval_session` および `v_eval_turn`）を作成できます。

Go は `v_user_message_received` から `v_node_error` までのイベントタイプごとの全 25 個のビューを作成します（同一の列名を使用し、`PayloadColumnDenylist` が設定されている場合は射影を考慮して列を削除します）。評価ビュー（`v_eval_session` および `v_eval_turn`）は Python 専用（v2.13.0+）です。

4 つのワークフロービュー（`v_agent_transfer`、`v_agent_state_checkpoint`、`v_event_compaction`、`v_tool_paused`）および `v_tool_completed` の `pause_kind` / `function_call_id` 列は、[ADK 2.0 ワークフローイベントサポート](#adk-2-events) によって提供されます。**Python** と **Go** は両方とも、これら 4 つのビューに加えて `v_node_output` および `v_node_error` を作成します。**Java**（v1.7.0+）では、`v_tool_paused` と `v_tool_completed` の `pause_kind` / `function_call_id` 列のみが作成されます。Java プラグインは `v_agent_transfer`、`v_agent_state_checkpoint`、`v_event_compaction` のイベントを出力しないため、Java ではこれらのビューは作成されません。

その他の Java ビューの違いは以下の通りです。

- Java はこれらのイベントを出力しないため、`v_agent_error`、`v_invocation_error`、`v_node_output`、`v_node_error` を作成しません。
- Java の `v_llm_response` は `usage_metadata` で終了します。`usage_thinking_tokens`、`usage_tool_use_tokens`、`cache_metadata`、`cache_type`、`finish_reason` は公開されません。
- Java の `v_agent_response` は `response_text` ではなく `text_summary` を公開します。
- Java の `v_agent_starting` は `agent_instruction` のみを公開します。
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
    "tools": [
      {
        "name": "list_dataset_ids",
        "description": "..."
      },
      {
        "name": "execute_sql",
        "description": "..."
      }
    ],
    "llm_config": {
      "temperature": 0.5,
      "top_p": 0.9
    }
  }
}
```

自動的に作成される `v_llm_request` ビューは、`tools` 属性をその `tools`（JSON）列として公開します。Python と Go では、`tools` にはツールごとに 1 つのエントリが含まれ、その `name` と、利用可能な場合は `description` および `parameters`（ツールのパラメータスキーマ）が保持されます。これらのエントリは、他の属性と同じサイズ制限および機密キーの墨消しを通過します。Java では、`["list_dataset_ids", "execute_sql"]` のようにツール名のみが記録されます。

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
    },
    "finish_reason": "STOP"
  },
  "latency_ms": {
    "time_to_first_token_ms": 2579,
    "total_ms": 2579
  }
}
```

Python および Go プラグインは、最終的な（部分レスポンスではない）レスポンスにのみ `finish_reason` を追加します。それぞれの `v_llm_response` ビューは、最終レスポンスの `cache_type` とともにこれを `STRING` として公開します。モデルが終了診断情報を提供する場合、行の `status` が `OK` のままであっても、共通の `error_message` 列にサニタイズされた値が保存されます。

Python と Go では、モデルの終了理由およびブロック理由は引き続き `LLM_RESPONSE` として分類されます。プラグインは、モデル呼び出しがエラーで失敗した場合にのみ `LLM_ERROR` を使用します。

Python と Go では、`content.response` はレスポンスパーツを `|` で区切って要約します（テキストの場合は `text: '...'`、関数呼び出しの場合は `call: <name>`、関数レスポンスの場合は `resp: <name>`、その他のパーツタイプの場合は `other` など）。`max_content_length`（Go では `MaxContentLen`）より長いテキストは切り詰められ、`is_truncated` が設定されます。ADK Python v2.12.0+ および Go では、サマリーに実行可能コードを `Executable code (<language>): <code>` として、コード実行結果を `Code execution result (<outcome>): <output>` として表示し、テキスト、コード、出力に含まれる一般的な認証情報パターンを墨消しし、切り詰められた値の末尾に `...[TRUNCATED]` を付加します。墨消しによっても `is_truncated` が設定されます。`custom_metadata_allowlist`（Go では `CustomMetadataAllowlist`）が設定されている場合、最終的な（部分レスポンスではない）`LLM_RESPONSE` 行は `llm_response.custom_metadata` から許可リストに登録されたキーを `attributes.custom_metadata` にキャプチャします。

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
| `LOCAL` | `FunctionTool` インスタンス（ローカル関数） |
| `MCP` | Model Context Protocol ツール（`McpTool` インスタンス） |
| `SUB_AGENT` | `AgentTool` インスタンス（サブエージェント） |
| `A2A` | リモート Agent2Agent インスタンス（`RemoteA2aAgent`） |
| `TRANSFER_AGENT` | `TransferToAgentTool`（`transfer_to_agent`）インスタンス（一般的なエージェント転送） |
| `TRANSFER_A2A` | Python および Go: リモート A2A エージェントに解決される `transfer_to_agent` 呼び出し（呼び出しレベルで分類） |
| `TOOLBOX` | Python（v2.13.0+）および Go: MCP Toolbox for Databases（`ToolboxTool`）ツール |
| `SKILL` | Python（v2.13.0+）: `SkillToolset` 組み込みツール（`list_skills`、`load_skill`、`load_skill_resource`、`run_skill_script`、`search_skills`、`unload_skill`）。Go: `SkillToolset` 組み込みツール（`list_skills`、`load_skill`、`load_skill_resource`） |
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

ツール実行が例外で失敗したとき、または（ADK Python v2.13.0 以降で）返されたツール結果が組み込みの MCP `isError` / `is_error` ルール、`ReflectAndRetryToolPlugin` のエラー応答、またはカスタム [`tool_result_classifier`](#tool-result-error-classification) によってエラーとして分類されたときに記録されます。ツール名、引数、ツール出自、エラーメッセージをキャプチャします。

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

!!! note "組み込みの墨消し"

    Python は `temp:` の状態値を `[REDACTED]` に置き換えます。Go はログ記録前に `state_delta` からトップレベルの小文字の `temp:` エントリを削除し、何も残らない場合は `STATE_DELTA` 行を出力しません。構造化されたコンテンツや属性内のその他の `temp:` 値は `[REDACTED]` に置き換えられます。詳しくは [組み込みの墨消し](#built-in-redaction) を参照してください。

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
| `INVOCATION_ERROR` | `{"error_traceback": "..."}` |
| `AGENT_STARTING` | `"You are a helpful agent..."`（ADK Python v2.12.0+ および Go では、指示が空または動的な指示プロバイダーである場合は `null`） |
| `AGENT_COMPLETED` | `{}` |
| `AGENT_ERROR` | `{"error_traceback": "..."}` |
| `USER_MESSAGE_RECEIVED` | `{"text_summary": "Help me book a flight."}` |
| `AGENT_RESPONSE` | `{"response": "Here are the flights..."}` |

Python と Go では、`AGENT_ERROR` および `INVOCATION_ERROR` 行は `status="ERROR"`、サニタイズされた `error_message`、およびサニタイズされた `content.error_traceback` 値（Python ではフォーマットされたトレースバック、Go ではスタックトレースなしのサニタイズされた `err.Error()` メッセージ）を持ちます。エージェントエラービューは経過した `total_ms` も公開します。Python では、両方のイベントはエージェントまたはランナーの実行からエスケープした未処理の例外を表します。Go では、再試行された失敗したノード試行や失敗したツールとしてのエージェント実行など、ADK が `AfterAgent` コールバックなしで終了し、その失敗を自体で処理したアクティベーションに対しても `AGENT_ERROR` が書き込まれます。

ADK Python v2.12.0+ および Go では、`AGENT_STARTING` 行に次の `attributes` キーを追加することもでき、`v_agent_starting` ビューはこれらを列として公開します。

- `instruction_source`: エージェントの指示が呼び出し可能な `InstructionProvider` に由来する場合は `"provider"`。
- `static_instruction`: エージェントの静的指示テキスト *（Python v2.12.0+。Go プラグインでは設定されないため、Go では `v_agent_starting.static_instruction` は `NULL` になります）*。
- `agent_description`: エージェントの説明。
- `model`: エージェントのモデル名。Python では、LLM エージェントが `model` を未設定のままにしている場合、設定されている最も近い祖先エージェントから継承されたモデルになります。Go では、エージェント自体に設定されている場合にのみ `model` が記録されます。
- `sub_agents`: エージェントのサブエージェント名。

適用されないキーや値が空のキーは省略されます。Python v2.12.0+ および Go では、行のコンテンツが指示テキストではなく `<function ...>` などの呼び出し可能オブジェクトのテキスト表現である場合、ビューの `agent_instruction` 列は `NULL` になります。

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

この例は Python および Go のペイロードを示しています。Java は表示可能なコンテンツの要約を `{"text_summary": "Here are the available flights..."}` として保存し、`v_agent_response` でそのフィールドを `text_summary` として公開します。

Python と Go では、`final_response_tool_names`（Go では `FinalResponseToolNames`）に正常に完了したツールの名前が含まれている場合、プラグインはそのツールの呼び出し引数をレスポンスペイロードとし、`attributes` に `source_tool` を含めて `AGENT_RESPONSE` も出力します。これは、表示可能なテキストイベントではなく専用のツールを介して最終回答を提供するエージェントをサポートします。

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

この例は Python および Go のペイロードを示しています。Python、Go、および Java はレスポンスを `content` に直接保存します。Python と Go は名前空間付きのレスポンスを `attributes.a2a_metadata` にも保持しますが、Java はその重複を省略します。Python と Go の `v_a2a_interaction` ビューは `response_content`、`a2a_task_id`、`a2a_context_id`、`a2a_request`、および `a2a_response` を公開します。Java は最後の列を省略します。

### エージェントワークフローと一時停止/再開イベント（ADK 2.0） {#adk-2-events}

<div class="language-support-tag">
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v2.3.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v1.7.0</span>
</div>

!!! note "Java のサポート"

    **Java** プラグインはこのセクションのサブセットをサポートします。`TOOL_PAUSED` および後述の一時停止/再開ペアリングを出力しますが、`AGENT_TRANSFER`、`AGENT_STATE_CHECKPOINT`、`EVENT_COMPACTION` は出力**せず**、`attributes.adk` エンベロープも書き込みません。Java プラグインは、代わりに `pause_kind` と `function_call_id` を `attributes` の**トップレベル**に格納します（以下のクエリの注意点を参照）。

ADK 2.0 では、マルチエージェントワークフロー（制御を渡すエージェント、状態をチェックポイントするエージェント、長い履歴を圧縮するエージェント）と、ターンをまたいで一時停止および再開する長時間実行ツールが導入されました。プラグインは、4 つの新しいイベントタイプと小さなメタデータエンベロープである `attributes.adk` を介してこれらのフローを可観測にし、行をそれを生成した ADK イベントに関連付けます。

#### `attributes.adk` エンベロープ

このエンベロープは **Python** および **Go** プラグインによって書き込まれます。すべての行に `attributes.adk` オブジェクトが含まれます。`schema_version` は常に存在します（Python では `app_name` も常に存在し、Go では `app_name` が空でない場合に存在します）。イベント由来のフィールドは ADK `Event`（ライフサイクルおよびワークフローイベント）から発生した行にのみ追加されるため、コールバックのみの行では省略され、クエリ時には SQL `NULL` に解決されます。

| フィールド | 型 | 意味 |
| --- | --- | --- |
| `schema_version` | string | エンベロープのバージョン（現在は `"1"`）。エンベロープが進化した場合に、これに基づいてダウンストリームクエリを制御できます。 |
| `app_name` | string | 行を生成した ADK アプリ（Go では空の場合に省略）。 |
| `source_event_id` | string | 発生元の ADK `Event` の ID。単一のイベントが生成する複数の行を結合するための信頼性の高いキーです。 |
| `node` | object | ワークフローノードのアイデンティティ: `{ "path", "run_id", "parent_run_id" }`。`parent_run_id` は親ノードの実行 ID です（ルートでは `null`）。Go では、`NodeInfo` に設定されている場合に `message_as_output`（bool）および `output_for`（文字列の配列）も `node` に含まれます。 |
| `branch` | string | ワークフローが分岐したパスを実行している場合のイベントのブランチ。 |
| `scope` | object | 分離スコープ `{ "id", "kind" }`。ここで `kind` は `node_run`（ワークフローノード実行、例: `loopA@42`）、`function_call`（モデルが生成した呼び出し ID）、または *（Python）* `unknown` です。 |
| `route` | string または array | イベントアクションによって選択されたルート（Python では文字列、Go では文字列の配列、設定されている場合）。 |
| `render_ui_widgets` | array | イベントアクションによって要求されたシリアル化された UI ウィジェット（設定されている場合、*Python*）。 |
| `rewind_before_invocation_id` | string | イベントアクションが巻き戻しを要求する基準となる呼び出し ID（設定されている場合、*Python*）。 |
| `pause_kind` | string | `TOOL_PAUSED` の場合: 通常の長時間実行ツールの場合は `tool`、HITL リクエストの場合は `hitl_credential` / `hitl_confirmation` / `hitl_input`。再開された `TOOL_COMPLETED` 行では常に `tool`。HITL の完了は `TOOL_COMPLETED` ではなく `HITL_*_REQUEST_COMPLETED` としてログに記録されます。 |
| `function_call_id` | string | 関数呼び出し ID。両者をペアリングできるように、`TOOL_PAUSED` および対応する再開された `TOOL_COMPLETED` 行に設定されます（通常のツールのみ）。 |

**Go** では、`attributes.adk` はすべての行に `event_id` と `author` もスタンプし、空でない場合は `adk_version` と `invocation_id` をスタンプし、`DisableSessionMetadata` が `false` で値が空でない場合は `session_id` と `user_id` をスタンプし、ADK `session.Event` から派生した行には存在する場合は `isolation_scope`、`artifact_delta`、`skip_summarization`、および `escalate` を追加します。

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

エージェントがその状態のスナップショットを作成したときに記録されます。プラグインはまた、エージェントの実行の終了をマークするために `end_of_agent: true` を含むチェックポイントを出力します。`v_agent_state_checkpoint` ビューは `agent_state_type` を公開するため、実際の状態オブジェクトと明示的な `null` チェックポイント（実行終了マーカー）および未設定の値を区別できます。Go では、チェックポイントは `CustomMetadata` キーの `adk_agent_state`/`agent_state` および `end_of_agent`/`adk_end_of_agent` から取得され、これらのキーが `CustomMetadataAllowlist` にリストされている場合にのみ出力されます。

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
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v2.7.0</span><span class="lst-go">Go v0.1.0</span>
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

`BigQueryLoggerConfig` に `gcs_bucket_name`（Go の `agentanalytics.Config` では `GCSBucketName` または `GCSOffloader`）が構成されている場合、プラグインは大きなテキストやマルチモーダルコンテンツ（画像、音声など）を Google Cloud Storage へ自動的にオフロードします。`content` 列には要約またはプレースホルダーが入り、`content_parts` には GCS URI を指す `object_ref` が保存されます。[構成オプション](#configuration-options) の `connection_id`（Go では `ConnectionID`）、`max_content_length`（Go では `MaxContentLen` および `MaxInlineTextSize`）、および Go のアップロード同時実行数/メモリ制限（`GCSMaxConcurrentUploads`、`GCSUploadTimeout`、`GCSMaxPendingUploadBytes`）も参照してください。

Go では、オフロードされたオブジェクトはそのオブジェクトパスに行のタイムスタンプの UTC 日付（`[prefix/]<YYYY-MM-DD>/<trace_id>/<span_id>_<event_id>_c<ord>_p<idx><ext>`）を使用し、`object_ref.details.gcs_metadata` に `"content_type"` とともに `"size"` を記録し（オフロードされたテキストでは `content_parts[].mime_type` を `"text/plain"` に保ちつつ GCS オブジェクトの `content_type` として `"text/plain; charset=utf-8"` を使用）、`USER_MESSAGE_RECEIVED` および `LLM_REQUEST` に加えて `LLM_RESPONSE` イベントに対しても `content_parts` を設定します。

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
        "uri": "gs://sample-bucket-name/2025-12-10/a2c7f13d3a3f0bbb8793692f76a6012a/3916f5762bcd4d42_ca5e3c9d99e24e46b614f2f44f93bf6e_c0_p1.txt",
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
        "uri": "gs://sample-bucket-name/2025-12-10/a2c7f13d3a3f0bbb8793692f76a6012a/3916f5762bcd4d42_ca5e3c9d99e24e46b614f2f44f93bf6e_c0_p2.png",
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

    BigQuery Agent Analytics プラグインは、ツール引数、LLM プロンプト、認証関連イベント（HITL 認証情報リクエストなど）を含む詳細なイベントペイロードをキャプチャします。Python では、組み込みの墨消しは小文字化とハイフン正規化の後にキー名を正確に一致させるため、`clientSecret` や `accessToken` などの camelCase バリアントは一致**しません**。Go はさらにアンダースコアとハイフンの区切り文字を無視するため、それらのバリアントに一致します。この警告の残りの部分は Python の認証情報リクエストペイロードに関するものです。ADK は `adk_request_credential` 引数を camelCase エイリアスでシリアル化するため、`AuthenticatedFunctionTool` OAuth2 フローによって `client_secret` および `access_token` の値が `content` 列に書き込まれる可能性があります（[google/adk-python#3845](https://github.com/google/adk-python/issues/3845)）。ADK Python v2.9.0 以降では、`adk_request_credential` リクエストから構成済みの OAuth2 クライアントシークレットが削除され、ADK Python v2.12.0 以降では API キー、HTTP Basic パスワード、HTTP bearer トークン、および追加の HTTP ヘッダーも削除されます。OAuth2 アクセストークンは依然として削除されません。ADK がそのリクエストから削除しないフィールドは camelCase 名を保持し、組み込みの墨消しとは一致しません。独自のツール引数に含まれる camelCase キーも同様です。墨消しは一般的なデータ損失防止（DLP）システムではないため、アプリケーション固有のキーまたは自由形式テキストに含まれるシークレットも BigQuery に書き込まれる可能性があります。

プラグインには、一般的なシークレットを自動的に保護する **組み込みの墨消し** 機能が含まれています。さらに制御が必要な場合は、カスタム墨消しを重ねて適用できます。

### 組み込みの墨消し {#built-in-redaction}

<div class="language-support-tag">
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v1.7.0</span>
</div>

Python プラグインはキー名を小文字に正規化し、ハイフンをアンダースコアのように扱います。構造化された `content` または `attributes` のどこに現れても、これらのキーの値を再帰的に `[REDACTED]` に置き換えます:

`client_secret`, `access_token`, `refresh_token`, `id_token`, `api_key`,
`password`, `private_key`, `proxy_authorization`, `google_access_id`, `sig`,
`signature`, `token`, `secret`, `authorization`, `x_api_key`,
`x_amz_credential`, `x_amz_signature`, `x_goog_credential`,
`x_goog_security_token`, `x_goog_signature`

Python は **`temp:`** の状態値を `[REDACTED]` に置き換えます。Go はログ記録前に `state_delta` からトップレベルの小文字の **`temp:`** エントリを削除し、何も残らない場合は `STATE_DELTA` 行を出力しません。構造化されたコンテンツや属性内のその他の **`temp:`** 値は `[REDACTED]` に置き換えられます。`secret:` プレフィックスには特別な意味はありません。呼び出しローカルの機密状態には `temp:` を使用するか、アプリケーション固有の状態値はロギングに到達する前にサニタイズしてください。カスタムコンテンツフォーマッタは状態属性を墨消ししません。

!!! warning "以前のガイダンスの訂正"

    以前のドキュメントでは、`secret:` プレフィックスが付いたキーも墨消しされると誤って記載されていました。プラグインは `temp:` プレフィックスのみに一致します。セッション状態に `secret:`（例: `secret:token`）の下でシークレットを保存した場合、カスタム `content_formatter` でマスクされない限り平文でログに記録されます。そのガイダンスに依存していた場合は、既存の `agent_events` テーブルで `temp:` 以外のキーの下にログ記録された値を監査してください。

プラグインはまた、`error_message`、エージェントおよび実行のトレースバック、外部 URI 内の認証情報パターンをサニタイズします。これには、認証ヘッダー、bearer および basic 認証情報、署名付き URL クエリパラメータ、および上記の機密名を使用するキー/値フラグメントが含まれます。安全に書き換えることができないエンコードされた認証情報構成は、フェイルクローズ（拒否）されます。

!!! info "設定不要"

    構造化属性および状態ロギングの組み込み墨消しは常にアクティブであり、属性値内のネストされた辞書および JSON エンコードされた文字列に再帰的に適用されます。カスタム `content_formatter` は、未加工コンテンツに対して **最初** に実行されます。エラーが発生するかサポートされていない型が返された場合、Python は元のコンテンツの代わりに `[FORMATTER_FAILED]` を書き込み、`formatter_failed` インシデントカウンタをインクリメントします。

    Python の `content_formatter` は、`None`、`str`、`dict`、または `list`（あるいはこれらのサブクラス）、または正確な `types.Content`、`types.Part`、`LlmRequest` を返すことができます。ADK Python v2.11.0 以降では、フォーマッタの失敗も行の `error_message` に記録され、例外クラスまたは戻り値クラス名のみが記載されます（例: `content_formatter raised ImportError`、`content_formatter raised <subclass of ValueError>`、または `content_formatter returned unsupported type tuple`）。イベントにすでに `TOOL_ERROR` などの `error_message` が存在する場合、そのメッセージが最初に保持され、セミコロンに続いてフォーマッタの失敗が記録されます。行の `status` は変更されないため、正常なイベントは `status` `OK` を維持しますが、null でない `error_message` をエラーとして扱うクエリでは引き続きその行がフラグ付けされます。

    例外をスローするフォーマッタをデバッグするには、`debug_content_formatter_errors=True` を設定して、プラグインのローカル Python ログ警告に制限付きトレースバックを追加します。トレースバックには未フォーマットのコンテンツが含まれる可能性があり、設定されたすべてのログハンドラーに到達するため、そのコンテンツが表示されても問題のない場所でのみ有効にしてください。BigQuery に書き込まれることはありません。

!!! note "Go における組み込みの墨消し"

    Go プラグイン（`google.golang.org/adk/plugin/agentanalytics`）は、デフォルトで組み込みの墨消しを有効にします（`DisableSensitiveKeyRedaction: false`）。キー名は小文字化され、アンダースコア（`_`）とハイフン（`-`）が削除されて正規化されるため、`snake_case`、`kebab-case`、および `camelCase` のバリアント（`api_key`、`api-key`、`apiKey`、`clientSecret`、`accessToken`、`refreshToken`、`idToken`、`privateKey`、`sessionToken`、`secretAccessKey`、`codeVerifier`、`authCode`、`passphrase` など）が一致し、構造化された `content` および `attributes` 全体で `"[REDACTED]"` に置き換えられます（`DisableSensitiveKeyRedaction: true` の場合を除く）。

    さらに、Go プラグインは次の処理を行います:

    - ログ記録前に `state_delta` からトップレベルの小文字の **`temp:`** エントリを削除し、何も残らない場合は `STATE_DELTA` 行を出力しません。構造化されたコンテンツや属性内のその他の **`temp:`** 値は `"[REDACTED]"` に置き換え、`credential` または `credentials` の下にある認証情報コンテナエンベロープ全体を墨消しします。
    - 外部 URI から認証情報ユーザー情報と機密クエリパラメータを除去し（機密クエリ値を安全に書き換えられない場合は `"[REDACTED_SENSITIVE_URI]"` にフェイルクローズします）、`error_message` と `uri` 内の `Authorization` ヘッダー、`Bearer` および `Basic` トークン、埋め込まれた JSON 認証情報フラグメントを除去します。
    - 組み込みの墨消しの前にカスタム `ContentFormatter`（`func(content any, eventType string) (any, error)`）を実行します。`ContentFormatter` が非 nil のエラーを返すか panic を起こした場合、Go プラグインは `content` に `"[FORMATTER_FAILED]"` を書き込み、`content_parts` は書き込まず、`error_message` に `content_formatter raised <error type>` または `content_formatter panicked` を追加し、`DropStats().FormatterFailureDrops` をインクリメントします。

!!! note "Java における組み込みの墨消し"

    Java プラグインには、v1.7.0 以降で組み込みの墨消しが含まれています。
    セッション状態および状態デルタを含む、組み立てられた `attributes` ツリー全体で `client_secret`、`access_token`、`refresh_token`、`id_token`、`api_key`、`password`（大文字と小文字を区別しない）、および **`temp:`** プレフィックスが付いた任意のキーを再帰的に墨消しします。シークレットを他の状態スコープから排除するか、カスタム `contentFormatter` でマスクしてください。

    カスタム Java `contentFormatter` は **スレッドセーフ**（呼び出し間で同時に呼び出される）かつ **高速/非ブロッキング**（イベント処理パス上で実行される）である必要があり、受け取ったコンテンツを変更するのではなく **新しいオブジェクト** を返す必要があります。例外をスローした場合、Java プラグインは未フォーマットのペイロードをログに記録するのではなく、行のコンテンツをドロップ（フェイルクローズ）します。

### `content_formatter` を使用して追加のシークレットを墨消しする

カスタム `content_formatter` 関数（Go では `ContentFormatter`、Java では `contentFormatter`）を提供して、機密フィールドが書き込まれる前に削除またはマスクします:

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

=== "Go"

    Go では、フォーマッタは最終的な JSON ではなく未加工の型付きコンテンツペイロード（`string`、`*genai.Content`、`*model.LLMRequest`、`*model.LLMResponse`、または `map[string]any` など）を受け取り、`attributes.state_delta` などの属性（attributes）は変換しません。変更するポインタ、スライス、またはマップ（`*genai.Content` 内の `Part.Text`、`Part.ExecutableCode.Code`、`Part.CodeExecutionResult.Output`、`Part.FunctionCall.Args`、`Part.FunctionResponse.Response` を含む）はクローンを作成し、ライブペイロードを決して直接変更しないでください。

    以下のヘルパーは編集する値のクローンを作成し、ネストが 50 レベルに達すると停止します。過度にネストされたペイロードや循環参照を含むペイロードはエラーを返すため、プラグインはプロセスクラッシュのリスクを冒す代わりに `[FORMATTER_FAILED]` を記録します。これらのヘルパーは JSON 形式の `map[string]any` および `[]any` 値（さらに `[]string`、`map[string]string`、`[]map[string]any`）を再帰的に処理します。ツールが返すその他の具体的な型については境界のあるケースを追加するか、フォーマット前にそれらの値を正規化し、この墨消しに依存する前に実際のペイロードでテストしてください:

    ```go
    package analytics

    import (
    	"fmt"
    	"regexp"
    	"strings"

    	"google.golang.org/adk/plugin/agentanalytics"
    	"google.golang.org/adk/v2/model"
    	"google.golang.org/genai"
    )

    var ssnPattern = regexp.MustCompile(`\b\d{3}-\d{2}-\d{4}\b`)

    func redactCustomSecrets(content any, eventType string) (any, error) {
    	return redactCustomSecretsAtDepth(content, eventType, 0)
    }

    func redactCustomSecretsAtDepth(content any, eventType string, depth int) (any, error) {
    	if depth >= 50 {
    		return nil, fmt.Errorf("redaction nesting limit exceeded")
    	}
    	switch v := content.(type) {
    	case string:
    		return ssnPattern.ReplaceAllString(v, "[REDACTED_SSN]"), nil
    	case *genai.Content:
    		return redactGenAIContentSecrets(v, eventType, depth+1)
    	case *model.LLMRequest:
    		if v == nil {
    			return nil, nil
    		}
    		cloned := *v
    		if len(v.Contents) > 0 {
    			cloned.Contents = make([]*genai.Content, len(v.Contents))
    			for i, c := range v.Contents {
    				redactedContent, err := redactGenAIContentSecrets(c, eventType, depth+1)
    				if err != nil {
    					return nil, err
    				}
    				cloned.Contents[i] = redactedContent
    			}
    		}
    		if v.Config != nil && v.Config.SystemInstruction != nil {
    			redactedSys, err := redactGenAIContentSecrets(v.Config.SystemInstruction, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cfgCopy := *v.Config
    			cfgCopy.SystemInstruction = redactedSys
    			cloned.Config = &cfgCopy
    		}
    		return &cloned, nil
    	case *model.LLMResponse:
    		if v == nil {
    			return nil, nil
    		}
    		redactedContent, err := redactGenAIContentSecrets(v.Content, eventType, depth+1)
    		if err != nil {
    			return nil, err
    		}
    		cloned := *v
    		cloned.Content = redactedContent
    		return &cloned, nil
    	case map[string]any:
    		if v == nil {
    			return map[string]any(nil), nil
    		}
    		cloned := make(map[string]any, len(v))
    		for k, val := range v {
    			if depth+1 >= 50 {
    				return nil, fmt.Errorf("redaction nesting limit exceeded")
    			}
    			if strings.EqualFold(k, "internal_token") {
    				cloned[k] = "[REDACTED]"
    				continue
    			}
    			redactedVal, err := redactCustomSecretsAtDepth(val, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[k] = redactedVal
    		}
    		return cloned, nil
    	case map[string]string:
    		if v == nil {
    			return map[string]string(nil), nil
    		}
    		cloned := make(map[string]string, len(v))
    		for k, val := range v {
    			if depth+1 >= 50 {
    				return nil, fmt.Errorf("redaction nesting limit exceeded")
    			}
    			if strings.EqualFold(k, "internal_token") {
    				cloned[k] = "[REDACTED]"
    				continue
    			}
    			redactedVal, err := redactCustomSecretsAtDepth(val, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[k], _ = redactedVal.(string)
    		}
    		return cloned, nil
    	case []any:
    		if v == nil {
    			return []any(nil), nil
    		}
    		cloned := make([]any, len(v))
    		for i, item := range v {
    			redactedItem, err := redactCustomSecretsAtDepth(item, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[i] = redactedItem
    		}
    		return cloned, nil
    	case []string:
    		if v == nil {
    			return []string(nil), nil
    		}
    		cloned := make([]string, len(v))
    		for i, item := range v {
    			redactedItem, err := redactCustomSecretsAtDepth(item, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[i], _ = redactedItem.(string)
    		}
    		return cloned, nil
    	case []map[string]any:
    		if v == nil {
    			return []map[string]any(nil), nil
    		}
    		cloned := make([]map[string]any, len(v))
    		for i, item := range v {
    			redactedItem, err := redactCustomSecretsAtDepth(item, eventType, depth+1)
    			if err != nil {
    				return nil, err
    			}
    			cloned[i], _ = redactedItem.(map[string]any)
    		}
    		return cloned, nil
    	default:
    		return content, nil
    	}
    }

    func redactGenAIContentSecrets(c *genai.Content, eventType string, depth int) (*genai.Content, error) {
    	if depth >= 50 {
    		return nil, fmt.Errorf("redaction nesting limit exceeded")
    	}
    	if c == nil {
    		return nil, nil
    	}
    	cloned := *c
    	if len(c.Parts) > 0 {
    		cloned.Parts = make([]*genai.Part, len(c.Parts))
    		for i, p := range c.Parts {
    			if p == nil {
    				continue
    			}
    			partCopy := *p
    			if partCopy.Text != "" {
    				partCopy.Text = ssnPattern.ReplaceAllString(partCopy.Text, "[REDACTED_SSN]")
    			}
    			if partCopy.ExecutableCode != nil {
    				codeCopy := *partCopy.ExecutableCode
    				codeCopy.Code = ssnPattern.ReplaceAllString(codeCopy.Code, "[REDACTED_SSN]")
    				partCopy.ExecutableCode = &codeCopy
    			}
    			if partCopy.CodeExecutionResult != nil {
    				resultCopy := *partCopy.CodeExecutionResult
    				resultCopy.Output = ssnPattern.ReplaceAllString(resultCopy.Output, "[REDACTED_SSN]")
    				partCopy.CodeExecutionResult = &resultCopy
    			}
    			if partCopy.FunctionCall != nil {
    				fcCopy := *partCopy.FunctionCall
    				if fcCopy.Args != nil {
    					redactedArgs, err := redactCustomSecretsAtDepth(fcCopy.Args, eventType, depth+1)
    					if err != nil {
    						return nil, err
    					}
    					if argsMap, ok := redactedArgs.(map[string]any); ok {
    						fcCopy.Args = argsMap
    					}
    				}
    				partCopy.FunctionCall = &fcCopy
    			}
    			if partCopy.FunctionResponse != nil {
    				frCopy := *partCopy.FunctionResponse
    				if frCopy.Response != nil {
    					redactedResp, err := redactCustomSecretsAtDepth(frCopy.Response, eventType, depth+1)
    					if err != nil {
    						return nil, err
    					}
    					if respMap, ok := redactedResp.(map[string]any); ok {
    						frCopy.Response = respMap
    					}
    				}
    				partCopy.FunctionResponse = &frCopy
    			}
    			cloned.Parts[i] = &partCopy
    		}
    	}
    	return &cloned, nil
    }

    func newRedactedConfig() agentanalytics.Config {
    	cfg := agentanalytics.DefaultConfig()
    	cfg.ProjectID = "your-gcp-project-id"
    	cfg.DatasetID = "agent_analytics"
    	cfg.TableName = "agent_events"
    	cfg.ContentFormatter = redactCustomSecrets
    	return cfg
    }
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

=== "Go"

    ```go
    cfg := agentanalytics.DefaultConfig()
    cfg.ProjectID = "your-gcp-project-id"
    cfg.DatasetID = "agent_analytics"
    cfg.TableName = "agent_events"
    cfg.EventDenylist = []string{
    	agentanalytics.EventHITLCredentialRequest,
    	agentanalytics.EventHITLCredentialCompleted,
    }
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

### トレースと可観測性 {#tracing-and-observability}

プラグインは、親子実行ツリー（エージェント → LLM 呼び出し / ツール呼び出し）が BigQuery からきれいに再構築できるように、出力されるすべての行に `trace_id`、`span_id`、`parent_span_id` 列を入力します。

- **内部スパン追跡、OTel スパンエクスポートなし。** プラグインは、16 文字の 16 進数 `span_id` 値の独自の内部スタックで親子階層を追跡します。Python と Java では、ルート呼び出しスパンは周囲の OTel スパンがアクティブな場合にその ID を再利用します（ランナーの呼び出しスパンと一致させます）。Go では、プラグインは常に独自の 16 文字の 16 進数ルート `span_id` を生成し、周囲の OTel スパン ID があれば `parent_span_id` に記録します。子 BQAA スパンは内部で生成されます。設定された OpenTelemetry `TracerProvider` に対して `tracer.start_span(...)` を呼び出さ**ない**ため、そのインストルメンテーションが設定されたエクスポーターに到達することはありません。これにより、Agent Engine テレメトリが有効になっている場合（`GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY=true`）や、他の Cloud Trace エクスポーターをホストプロセスに接続した場合に、Cloud Trace でスパンが重複するのを防ぎます。同じ内部 ID のみのスパン追跡が Go プラグインおよび Java プラグイン（v1.7.0+）にも適用されます。以前の Java ビルドでは、フレームワークのスパンの横に重複して表示される可能性のあるプラグイン所有の OpenTelemetry スパンが作成されていました。
- **周囲の OTel スパンが存在する場合の `trace_id` 継承。** Agent Engine の呼び出しスパン、ADK `Runner` 呼び出しスパン（Python および Java）、またはエージェントの実行前に開始した任意のスパンなど、周囲のランタイムがすでに OTel スパンを開始している場合、プラグインはその `trace_id` を読み取り、すべての BigQuery 行にスタンプします。これにより、BigQuery の行は共有された `trace_id` を介して既存の Cloud Trace トレースとスムーズに結合されます。
- **周囲のスパンが存在しない場合のフォールバック。** アクティブな周囲の OTel スパンがない場合（例: ホスト側のトレーサーが構成されていない非 Agent Engine デプロイ）、Python は呼び出しごとにランダムな 32 文字の 16 進数 `trace_id` を生成します。周囲のスパンがない場合、Go は `invocation_id` が空のときにランダムな 32 文字の 16 進数 `trace_id` を生成します。それ以外の場合は、プラグインごとのランダムなシードと呼び出し ID に対して SHA-256 を使用し、そのプラグインインスタンス内で安定した 32 文字の 16 進数 ID を生成します。Java は `trace_id` として ADK の呼び出し ID にフォールバックするため、外部トレーサーのセットアップがなくても BigQuery で親子階層が常に保持されます。
- **`TracerProvider` は不要。** アクティブなスパンなしで OpenTelemetry `TracerProvider` を構成しても効果はありません。プラグインは独自のスパンを開始しないため、すでに進行中のスパンからのみ `trace_id` を継承します。

### パブリックメソッド

=== "Python"

    プラグインは、ライフサイクル管理のためにいくつかのパブリックメソッドを公開しています:

    - **`await plugin.flush()`**: 現在のイベントループに関連付けられた保留中のイベントの書き込みが完了するまで待機します。
    - **`await plugin.shutdown(timeout=None, *, close_background_transport=False)`**: 保留中のイベントをフラッシュし、リソースを解放して、プラグインを正常にシャットダウンします。オプションの `timeout` パラメータは、構成の `shutdown_timeout` をオーバーライドします。プラグインが[共有バックグラウンドライター](#shared-background-writer)を使用している場合、シャットダウンによりプラグインはそのライターから切り離され、ライターは実行されたままになります。このプラグインのテーブルと認証情報用の共有ライターも排出して停止するには、`close_background_transport=True` を渡します。
    - **`await plugin.close(timeout=None, *, close_background_transport=False)`**: プラグインマネージャーのライフサイクルコントラクトを実行します。同じ引数で `shutdown()` に委任し、ランナーがプラグインを閉じるときに自動的に呼び出されます。
    - **`await BigQueryAgentAnalyticsPlugin.close_shared_background_transports(timeout=10.0)`**（Python v2.10.0+）: スタンドアロンスクリプト、プロセスシャットダウンハンドラー、テストクリーンアップフィクスチャなど、プロセス内のすべての共有バックグラウンドライターを排出して停止します。ライターの排出に失敗した場合、または `timeout` 内に完了しなかった場合に例外を発生させます（1 つのライターが失敗した場合はライターのエラーまたは `TimeoutError`、複数のライターが失敗した場合は `RuntimeError`）。同じ操作は、`google.adk.plugins.bigquery_agent_analytics_plugin` のモジュールレベル関数 `close_shared_background_transports(timeout=10.0)` としても利用可能です。
    - **`await plugin.create_analytics_views()`**: イベントタイプごとのすべての分析ビューを手動で（再）作成します。スキーマアップグレード後やビューを更新する必要がある場合に役立ちます。
    - **`await plugin.create_eval_views()`**（Python v2.13.0+）: `create_eval_views=False` の場合でも、エージェント評価ビュー（`{view_prefix}_eval_session` および `{view_prefix}_eval_turn`）を手動で（再）作成します。[エージェント評価ビュー](#agent-evaluation-views)を参照してください。
    - **`plugin.get_drop_stats()`**: 原因ごとの配信損失およびコンテンツサニタイズインシデント数のスナップショットを返します。[ドロップされたイベントの可観測性](#dropped-event-observability) を参照してください。

=== "Go"

    Go（`google.golang.org/adk/plugin/agentanalytics`）では、プラグインのライフサイクルおよび運用ヘルパーは ADK の `*plugin.Plugin` ハンドルとアンラップされた `*agentanalytics.BigQueryAgentAnalyticsPlugin` を介して公開されます:

    - **`adkPlugin.Close() error`**: キューに入っているイベントを排出し、バックグラウンドのバッチプロセッサを停止し（各フラッシュ/アップロードステージは `ShutdownTimeout`（デフォルト `10s`）によって制限され、合計経過時間は最大約 2.5 倍になります）、プラグイン所有の BigQuery、Storage Write、および GCS クライアントをクローズします。ADK Go のランナーはプラグインを自動的にクローズしません。構築直後に `defer bqPlugin.Close()` を記述するなどして、終了前に自分で `adkPlugin.Close()` を呼び出してください。
    - **`agentanalytics.AsBigQueryAgentAnalyticsPlugin(adkPlugin)`**: ADK の `*plugin.Plugin` ハンドルから基礎となる `*agentanalytics.BigQueryAgentAnalyticsPlugin` をアンラップします。アンラップされたハンドルは `adkPlugin.Close()` の完了後も引き続きアクセス可能です。
    - **`bqPlugin.DropStats() agentanalytics.DropStats`**: ドロップされたイベント数およびフォーマッタ失敗数のスナップショット（`QueueFullDrops`、`AppendFailureDrops`、`FormatterFailureDrops`、`ShutdownDrops`、および `TotalDrops`）を返します。[ドロップされたイベントの可観測性](#dropped-event-observability)を参照してください。
    - **`bqPlugin.SyncViews(ctx context.Context) error`**: `DisableCreateViews: true` の場合でも、イベントタイプごとの全 25 個の BigQuery 分析ビューを手動で作成または更新します（`CREATE OR REPLACE VIEW`）。プラグインが `NewBigQueryAgentAnalyticsPluginWithClients(..., nil, ...)`（`bqClient == nil`）で構築された場合、`SyncViews` は `agentanalytics: BigQuery client is not configured for view creation` を返します。
    - **`cfg.ViewDefinitions() ([]agentanalytics.ViewDefinition, error)`**: ネットワーク呼び出しを行わずに `cfg` に対する 25 個のビュー定義（`Name`、`EventType`、および `Query`）の決定論的なリストを返すため、Terraform やデプロイパイプラインを介して外部からビューをプロビジョニングできます。

    ```go
    // 具体的なプラグインをアンラップしてドロップ統計を検査するか、手動でビューを同期します:
    if bqPlugin, ok := agentanalytics.AsBigQueryAgentAnalyticsPlugin(adkPlugin); ok {
    	if err := bqPlugin.SyncViews(ctx); err != nil {
    		log.Printf("SyncViews failed: %v", err)
    	}
    }

    // シャットダウン時に保留中のイベントをフラッシュしてリソースを解放します:
    if err := adkPlugin.Close(); err != nil {
    	log.Printf("Close failed: %v", err)
    }
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
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v1.7.0</span>
</div>

BigQuery のログ記録はベストエフォートです。メモリ内キューのオーバーフロー、セットアップの利用不能、シャットダウンとコールバックの競合、または最終的な書き込み失敗時に、イベントがドロップされる可能性があります。プラグインはまた、コンテンツの代わりにセンチネルを伴って行が書き込まれるフォーマッタおよびパーサーのエラーもカウントします。カウンタはループのクリーンアップやシャットダウンをまたいで保持されます。

**ドロップ理由（Python）:**

| 理由 | 原因 |
|---|---|
| `queue_full` | メモリ内のイベントキューを制限します。ADK Python v2.13.0 では、すべてのイベントタイプがこの容量を共有します。満杯のときは終了イベントである `INVOCATION_COMPLETED` および `INVOCATION_ERROR` 行もドロップされる可能性があり、`queue_full` としてカウントされます。`BigQueryLoggerConfig` の `queue_max_size` を増やすか、`batch_size` を増やして大きなチャンクでドレインするか、コンシューマ側をスケールしてください（より多くの同時呼び出しがより速く完了するようにします）。 |
| `arrow_prep_failed` | 行を Arrow 表現に変換できませんでした（通常はスキーマ/型の不一致）。ログで問題のあるフィールドを調べてください。 |
| `retry_exhausted` | 再試行予算が使い果たされるまで、Storage Write API 呼び出しが再試行可能なエラー（例: 一時的な gRPC 障害）を返し続けました。 |
| `permission_denied` | *（Python v2.13.0+）* Storage Write API が `PERMISSION_DENIED`（`google.api_core.exceptions.PermissionDenied`）を返しました。再試行不可能です。サービスアカウントに対象テーブルの `bigquery.tables.updateData`（例: `roles/bigquery.dataEditor`）があることを確認してください。 |
| `not_found` | *（Python v2.13.0+）* 対象のデータセット、テーブル、または書き込みストリームが存在しない場合などに、Storage Write API がデフォルトストリームで `NOT_FOUND`（`google.api_core.exceptions.NotFound`）を返しました（`exactly_once_delivery` モードでの `NOT_FOUND` は `offset_conflict` としてカウントされます）。再試行不可能です。 |
| `non_retryable` | Storage Write API がその他の再試行不可能なエラー（クォータ、スキーマの拒否、無効な引数）を返しました。通常、オペレーターの介入が必要です。 |
| `unexpected_error` | バッチの準備または書き込み中に捕捉されたその他の例外。 |
| `shutdown_timeout` | 制限されたシャットダウンまたはクローズがタイムアウトしたときに、行がキューに残っていました。 |
| `shutdown_cancelled` | 外部のクローズタイムアウトなど、ホストによってシャットダウンがキャンセルされたときに、行がキューに残っていました。 |
| `offset_conflict` | `exactly_once_delivery` モードで、コミット済みストリームがオフセットを拒否したか、置換ストリームが利用できませんでした。 |
| `setup_unavailable` | プラグインのセットアップが失敗したか再試行バックオフ状態だったため、行を受け入れられませんでした。 |
| `shutdown_race` | シャットダウンの開始中または進行中に、コールバックが行を受け入れようとしました。 |
| `stale_loop` | キューに入れられた行が、すでにクローズされており排出できないイベントループに属していました。 |
| `formatter_failed` | カスタムフォーマッタが失敗したか、サポートされていない型を返しました。行は `[FORMATTER_FAILED]` で書き込まれます。これはドロップされた行数ではなく、インシデントカウントです。 |
| `content_parse_failed` | コンテンツの解析に失敗しました。行は `[CONTENT_PARSE_FAILED]` で書き込まれます。これはドロップされた行数ではなく、インシデントカウントです。 |

**ドロップカウンタ（Go）:**

`bqPlugin.DropStats()` は、次の `int64` フィールドを持つ `agentanalytics.DropStats` 構造体を返します:

| フィールド | 原因 |
|---|---|
| `QueueFullDrops` | イベントコールバックまたは `Append` が行をキューに入れようとしたときにメモリ内チャネル（`QueueMaxSize`、デフォルト `10000`）が満杯だったためにドロップされた行数。`agentanalytics.Config` の `QueueMaxSize` または `BatchSize` を増やしてください。 |
| `AppendFailureDrops` | Storage Write API 配信中に失敗として記録された行数（`MaxRetries` を使い果たしたバッチ、再試行不可能な書き込みまたはスキーマ/ディスクリプタ準備エラー、再試行が失敗する前に壊れたストリーム上で ack が失われたサーバーコミット済みの追加、回復されたコールバック panic、および `Flush` でのバッチ失敗後にスキップされた残りのバッチを含む）。 |
| `FormatterFailureDrops` | 非 nil のエラーを返したか panic を起こしたカスタム `ContentFormatter` 呼び出し。行は引き続き `"[FORMATTER_FAILED]"`、`content_parts` なし、および `error_message` に `content_formatter raised <error type>` または `content_formatter panicked` を伴って書き込まれます。これはインシデントカウントであり、`TotalDrops` には含まれません。 |
| `ShutdownDrops` | `Close()` 中に `ShutdownTimeout` が期限切れになる前に排出できなかったキュー内の残り行数と、`Close()` の開始後に `Append` に渡された行数。 |
| `TotalDrops` | ドロップとしてカウントされた行数の上限合計（`QueueFullDrops + AppendFailureDrops + ShutdownDrops`）。`AppendFailureDrops` には ack が失われたサーバーコミット済みのバッチが含まれる可能性があるため、`TotalDrops` は失われた行数の上限となります。 |

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
    #      "permission_denied": 0, "not_found": 0,
    #      "formatter_failed": 1, ...}

    loss_reasons = {
        "queue_full", "arrow_prep_failed", "retry_exhausted",
        "permission_denied", "not_found", "non_retryable",
        "unexpected_error", "shutdown_timeout", "shutdown_cancelled",
        "offset_conflict", "setup_unavailable", "shutdown_race",
        "stale_loop",
    }
    total_rows_lost = sum(stats.get(reason, 0) for reason in loss_reasons)
    ```

=== "Go"

    ```go
    if bqPlugin, ok := agentanalytics.AsBigQueryAgentAnalyticsPlugin(adkPlugin); ok {
    	stats := bqPlugin.DropStats()
    	fmt.Printf(
    		"total_drops=%d (queue_full=%d append_failure=%d shutdown=%d) formatter_failures=%d\n",
    		stats.TotalDrops,
    		stats.QueueFullDrops,
    		stats.AppendFailureDrops,
    		stats.ShutdownDrops,
    		stats.FormatterFailureDrops,
    	)
    }
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

ゼロ以外のすべての理由に対してアラートを設定してください。ほとんどの理由は、BigQuery に到達する前に行が失われたことを意味します。一方、`formatter_failed`（Go では `FormatterFailureDrops`）および `content_parse_failed` の理由は、センチネルコンテンツで行が書き込まれたことを意味するため、プライバシーまたはデータ品質のインシデントとしてアラートを設定してください。`queue_full`、`retry_exhausted`、`permission_denied`、`not_found`、`non_retryable`、または `offset_conflict` のカウントが持続する場合は、一般にスループット、IAM、配信、または Storage Write の健全性の問題を示します。Go における同等の書き込みエラーカウンタは `AppendFailureDrops` であり、Java では `append_error` です。

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

- [Python プラグインのソース](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/bigquery_agent_analytics_plugin.py)
- [Go プラグインのソース](https://github.com/google/adk-go/tree/main/plugin/agentanalytics)
- [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [Introduction to Object Tables](https://docs.cloud.google.com/bigquery/docs/object-table-introduction)
- [BigQuery Agent Analytics SDK の例](https://github.com/GoogleCloudPlatform/BigQuery-Agent-Analytics-SDK/tree/main/examples)
