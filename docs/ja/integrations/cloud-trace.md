---
catalog_title: Google Cloud Trace
catalog_description: ADK エージェントの相互作用をモニター、デバッグ、追跡します
catalog_icon: /integrations/assets/cloud-trace.svg
catalog_tags: ["observability", "google"]
---

# ADK 用 Google Cloud Trace によるオブザーバビリティ

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span>
</div>

ローカル開発中は、[ADK Web UI のトレースビュー](/evaluate/#debugging-with-the-trace-view)を使用してエージェントの動作を検査できます。エージェントをデプロイした後は、実際のトラフィックから発生するトレースデータを一元的に監視する方法が必要になります。

[Cloud Trace](https://cloud.google.com/trace) は、Google Cloud Observability の分散トレースコンポーネントです。遅延を監視し、エラーをデバッグし、アプリケーション全体のパフォーマンスを向上させることができるように、トレースデータを収集して可視化します。ADK エージェントの場合、Cloud Trace は各リクエストがモデル呼び出し、ツール実行、エージェントステップを経て流れる過程を捕捉し、本番環境のボトルネックやエラーを特定できるようにします。

## 概要

Cloud Trace は、トレースデータを生成するために複数の言語と収集方法をサポートするオープンソース標準である [OpenTelemetry](https://opentelemetry.io/) に基づいて構築されています。これは、OpenTelemetry 互換のインスツルメンテーションを利用する ADK アプリケーションのオブザーバビリティ手法と一致しており、以下を可能にします。

- **エージェント相互作用の追跡**: Cloud Trace はプロジェクトからトレースデータを継続的に収集して分析し、ADK アプリケーション内の遅延の問題やエラーを迅速に診断できるようにします。この自動データ収集は、複雑なエージェントワークフローで問題を特定するプロセスを簡素化します。
- **問題のデバッグ**: 詳細なトレースを分析して、遅延の問題やエラーを迅速に診断します。これらのトレースは、複数のサービス間にわたる通信遅延の増加や、ツール呼び出しなどの特定のエージェントアクション中に発生する問題を理解するのに重要です。
- **深い分析と視覚化**: Trace Explorer はトレースを分析するための主要なツールであり、スパン期間のヒートマップやスパンレートの折れ線グラフなどの視覚的な補助を提供します。また、サービスや操作ごとにグループ化できるスパンテーブルを提供し、代表的なトレースへのワンクリックアクセスと、エージェント実行パス内のボトルネックやエラーの原因を簡単に特定できるウォーターフォールビューを提供します。

以下の例では、次のエージェントディレクトリ構造を想定しています。

```
working_dir/
├── weather_agent/
│   ├── agent.py
│   └── __init__.py
└── deploy_agent_engine.py
└── deploy_fast_api_app.py
└── agent_runner.py
```

=== "Python"
    ```python
    # weather_agent/agent.py

    import os
    from google.adk.agents import Agent

    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "{your-project-id}")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
    os.environ.setdefault("GOOGLE_GENAI_USE_ENTERPRISE", "True")


    # ツール関数の定義
    def get_weather(city: str) -> dict:
        """指定された都市の現在の天気予報を取得します。

        Args:
            city (str): 天気予報を取得する都市の名前。

        Returns:
            dict: ステータスと結果、またはエラーメッセージ。
        """
        if city.lower() == "new york":
            return {
                "status": "success",
                "report": (
                    "ニューヨークの天気は晴れで、気温は摂氏 25 度（華氏 77 度）です。"
                ),
            }
        else:
            return {
                "status": "error",
                "error_message": f"'{city}'の天気情報は利用できません。",
            }


    # ツールの入ったエージェントを作成
    root_agent = Agent(
        name="weather_agent",
        model="gemini-flash-latest",
        description="天気ツールを使用して質問に答えるエージェント。",
        instruction="回答を見つけるには、利用可能なツールを使用する必要があります。",
        tools=[get_weather],
    )
    ```

## Cloud Trace 設定

### ADK CLI の使用

ADK CLI を使用してエージェントをデプロイまたは実行するときに、フラグを追加してクラウドトレースを有効にできます。

=== "Python"

    `adk deploy` コマンドを使用してエージェントをデプロイするとき：

    ```bash
    adk deploy agent_engine \
        --project=$GOOGLE_CLOUD_PROJECT \
        --region=$GOOGLE_CLOUD_LOCATION \
        --trace_to_cloud \
        $AGENT_PATH
    ```

=== "Go"

    ADK Go ランチャーでビルドされたエージェントを実行するとき：

    ```bash
    adkgo web -otel_to_cloud
    ```

### プログラミングによる設定

#### ADK アプリの抽象化を使用する

=== "Python"

    `AdkApp` 抽象化を使用している場合は、`enable_tracing=True` を追加することでクラウドトレースを有効にできます。

    ```python
    from google.adk.apps import AdkApp

    adk_app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )
    ```

#### テレメトリ（telemetry）モジュールを使用する

完全にカスタマイズされたエージェントランタイムの場合は、内蔵のテレメトリモジュールを使用してクラウドトレースを有効にできます。

=== "Python"

    ```python
    from google.adk import telemetry
    from google.adk.telemetry import google_cloud

    # GCP エクスポーターの設定を取得
    hooks = google_cloud.get_gcp_exporters(enable_cloud_tracing=True)

    # グローバル OTel プロバイダーの初期化と設定
    telemetry.maybe_set_otel_providers(otel_hooks_to_setup=[hooks])
    ```

=== "TypeScript"

    ```typescript
    import { getGcpExporters, maybeSetOtelProviders } from '@google/adk';

    // GCP エクスポーターの設定を取得
    const gcpExporters = await getGcpExporters({
      enableTracing: true,
    });

    // グローバル OTel プロバイダーの初期化と設定
    maybeSetOtelProviders([gcpExporters]);

    // ... エージェントコード ...
    ```

=== "Go"

    ```go
    import (
    	"context"
    	"log"
    	"time"

    	"google.golang.org/adk/v2/telemetry"
    )

    func main() {
    	ctx := context.Background()

    	// クラウドエクスポートが有効化されたテレメトリを初期化。
    	// デフォルトでは、GCP プロジェクト ID は GOOGLE_CLOUD_PROJECT 環境変数から読み取られます。
    	// telemetry.WithGcpResourceProject("my-project") を使用して明示的に指定することもできます。
    	telemetryProviders, err := telemetry.New(ctx,
    		telemetry.WithOtelToCloud(true),
    		// telemetry.WithGcpResourceProject("your-project-id"),
    	)
    	if err != nil {
    		log.Fatalf("テレメトリの初期化に失敗しました: %v", err)
    	}
    	defer func() {
    		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    		defer cancel()
    		if err := telemetryProviders.Shutdown(shutdownCtx); err != nil {
    			log.Printf("テレメトリのシャットダウンに失敗しました: %v", err)
    		}
    	}()

    	// グローバル OTel プロバイダーとして登録
    	telemetryProviders.SetGlobalOtelProviders()

    	// ... エージェントコード ...
    }
    ```

## Cloud Trace データの検査

設定が完了すると、エージェントとやり取りするたびに、トレースデータが自動的に Cloud Trace に送信されます。[Google Cloud コンソール](https://console.cloud.google.com/traces/explorer)の **Trace Explorer** にアクセスして、トレースを検査できます。

![cloud-trace](../assets/cloud-trace1.png)

ADK エージェントによって生成されたすべての利用可能なトレースが表示され、`invoke_agent`、`generate_content`、`call_llm`、`execute_tool` といったスパン名を確認できます。

![cloud-trace](../assets/cloud-trace2.png)

トレースの 1 つをクリックすると、ローカル ADK Web UI のトレースビューと同様に、詳細なプロセスのウォーターフォールビューが表示されます。

![cloud-trace](../assets/cloud-trace3.png)

### キャプチャされた属性（Attributes）

ADK は、エージェントの動作のフィルタリングや分析に役立つよう、トレースに次の属性を自動的に追加します。

- `gen_ai.agent.name`: 実行されているエージェントの名前。
- `gcp.vertex.agent.invocation_id`: 呼び出しの一意の ID。
- `gcp.vertex.agent.event_id`: 特定のイベントの ID。
- `gen_ai.conversation.id`: セッション ID。

## リソース

トレース、OpenTelemetry、Google Cloud 統合の詳細については、次のドキュメントを参照してください。

- [Google Cloud Trace ドキュメント](https://cloud.google.com/trace)
- [OpenTelemetry ドキュメント](https://opentelemetry.io/docs/)
- [Google Cloud とエージェントプラットフォームへの接続](/ja/get-started/google-cloud/)
