# エージェントのアクティビティロギング

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

Agent Development Kit（ADK）は、エージェントの動作を監視し、問題を効果的にデバッグするための柔軟で強力なロギング機能を提供します。

## ロギングの思想

ADKのロギングに対するアプローチは、デフォルトで過度に冗長になることなく、詳細な診断情報を提供することです。アプリケーション開発者が設定できるように設計されており、開発環境であれ本番環境であれ、特定のニーズに合わせてログ出力を調整できます。

- **標準ライブラリの統合:** ADKはホスト言語の標準ロギング機能（Pythonの `logging` モジュール、Goの `log` パッケージなど）を使用します。
- **構造化されたGenAIロギング:** ADKはOpenTelemetryを使用してGenAIのリクエストとレスポンスに関する構造化イベントを記録し、クラウド環境での高度な監視とデバッグを可能にします。
- **ユーザーによる設定:** ADKはデフォルト設定やCLIツールとの統合を提供しますが、特定の環境に合わせてロギングを設定することは、最終的にはアプリケーション開発者の責任です。

## ロギングスキーマ

ADKは標準ライブラリ機能とOpenTelemetryによる構造化GenAIイベントを使用してログを出力します。

### 構造化GenAIログ

OpenTelemetryを介して出力される構造化GenAIログは、[Semantic Conventions for GenAI](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-events.md) に準拠しています。

セキュリティ上の理由から、デフォルトではログ内のプロンプト内容は省略（elide）されます。環境変数またはプログラムによる設定を使用して、プロンプトのロギングを有効にできます。`adk web` については [ADK Webでのプロンプト内容のキャプチャ](#adk-webでのプロンプト内容のキャプチャ) を、コードでの設定については [プログラムによるプロンプト内容のキャプチャ](#プロンプト内容のキャプチャ) をご覧ください。

### ログレベル（Python）

次の表は、標準ロガーを使用した場合にPythonの各レベルで記録される内容を示しています。

| レベル | 説明 | 記録される情報の種類 |
| :--- | :--- | :--- |
| **`DEBUG`** | **デバッグに不可欠。** きめ細かい診断情報を提供する最も詳細なレベル。 | <ul><li>**完全なLLMプロンプト:** システム指示、履歴、ツールを含む、言語モデルに送信された完全なリクエスト。</li><li>サービスからの詳細なAPIレスポンス。</li><li>内部状態遷移と変数の値。</li></ul> |
| **`INFO`** | エージェントのライフサイクルに関する一般情報。 | <ul><li>エージェントの初期化と起動。</li><li>セッションの作成および削除イベント。</li><li>名前と引数を含むツールの実行。</li></ul> |
| **`WARNING`** | 潜在的な問題や非推奨機能の使用を示します。エージェントは機能し続けますが、注意が必要な場合があります。 | <ul><li>非推奨のメソッドまたはパラメータの使用。</li><li>システムが回復した非クリティカルなエラー。</li></ul> |
| **`ERROR`** | 操作の完了を妨げた重大なエラー。 | <ul><li>外部サービス（LLM、セッションサービスなど）へのAPI呼び出しの失敗。</li><li>エージェント実行中の未処理の例外。</li><li>設定エラー。</li></ul> |

!!! note
    本番環境では `INFO` または `WARNING` の使用をお勧めします。`DEBUG` ログは非常に冗長であり、機密情報が含まれる可能性があるため、問題を能動的にトラブルシューティングする場合にのみ有効にしてください。

## ADK Webでのロギング

ADKの `adk web`、`adk api_server`、`adk deploy cloud_run`、`adk deploy gke` コマンドを使用してエージェントを実行する場合、ログの詳細度や出力先を制御できます。

### ADK Webでのロギングレベル

`DEBUG` レベルのロギングでWebサーバーを起動するには、次を実行します。

```bash
adk web --log_level DEBUG path/to/your/agents_dir
```

`--log_level` オプションで使用可能なログレベルは、`DEBUG`、`INFO`（デフォルト）、`WARNING`、`ERROR`、`CRITICAL` です。

### ADK Webでのプロンプト内容のキャプチャ

セキュリティ上の理由から、デフォルトではログ内のプロンプト内容は省略されます。環境変数を使用してプロンプトのロギングを有効にできます。

```bash
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

この変数で使用可能な値は、`NO_CONTENT`、`EVENT_ONLY`、`SPAN_ONLY`、`SPAN_AND_EVENT` です。ブール値の `true` または `1` は、出力されるログイベントにコンテンツを記録する `EVENT_ONLY` を意味します。これら4つ以外の値は `NO_CONTENT` にフォールバックします。推論スパン（inference span）にコンテンツを記録するには、`SPAN_ONLY` および `SPAN_AND_EVENT` で `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental` も必要です。

!!! warning
    `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` 設定は、ユーザープロンプトとエージェントレスポンスの全内容をログに記録します。これはデバッグに役立ちますが、機密データや個人情報（PII）が取得される可能性があります。本番環境では、これを false に設定するか、適切なデータ処理ポリシーが整備されていることを確認してください。

### ADK WebでのOTLPエクスポート

OTLP互換のバックエンドにログをエクスポートするには、標準のOTel環境変数を設定します。

```bash
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="http://your-collector:4318/v1/logs"
adk web path/to/your/agents_dir
```

!!! note
    ログに加えてメトリクスやトレースも同じエンドポイントに送信したい場合は、一般的な `OTEL_EXPORTER_OTLP_ENDPOINT` 環境変数を設定することもできます。

### ADK WebでのGCPエクスポート設定

`--otel_to_cloud` フラグを使用してGCPエクスポートを有効にできます。

```bash
adk web --otel_to_cloud path/to/your/agents_dir
```

## プログラムによる設定

プログラムによる設定では、システムレベルの診断や本番環境でのオブザーバビリティのために、独自のコードから基盤となるロギングフレームワークとOpenTelemetryエクスポーターを設定します。ADKは次のロギング機能を使用します。

- **Python:** ADKは標準の `logging` モジュールと、構造化GenAIログ用のOpenTelemetryを使用します。
- **Go:** ADKはOpenTelemetryの設定に `google.golang.org/adk/v2/telemetry` パッケージを使用し、一般的なイベントには標準の `log` パッケージを使用してデフォルトで `stderr` に出力します。
- **Kotlin:** ADKは標準のJVMロギング機能（デフォルトはFlogger）を使用し、構造化GenAIログにOpenTelemetryを使用します。

### ロギングレベル

次のように、標準のロギングコントロールを使用してADKエージェントのロギングレベルを設定できます。

=== "Python"

    `DEBUG` レベルのメッセージを含む詳細なロギングを有効にするには、スクリプトの先頭に以下を追加します。

    ```python
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    ```

=== "Go"

    一般的なイベント（サーバーの起動やHTTPリクエストなど）は、標準のGo `log` パッケージを使用してログに記録され、デフォルトで `stderr` に書き込まれます。

=== "Kotlin"

    ADKは標準のJVMロギング機能（デフォルトはFlogger）を使用します。ログの詳細度を調整するには、`java.util.logging` や SLF4J などのJVMロガーバックエンドを設定します。

### プロンプト内容のキャプチャ

=== "Python"

    環境変数を設定することで、プログラムから完全なプロンプトロギングを有効にできます。

    ```python
    import os

    os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "true"
    ```

    プロセス全体ではなく単一の実行（run）にコンテンツキャプチャのスコープを限定するには、環境変数ではなく `RunConfig.telemetry` を設定します。

    ```python
    from google.adk.agents.run_config import RunConfig
    from google.adk.telemetry import ContentCapturingMode, TelemetryConfig

    run_config = RunConfig(
        telemetry=TelemetryConfig(
            capture_message_content=ContentCapturingMode.SPAN_AND_EVENT,
        ),
    )
    ```

=== "Go"

    テレメトリを初期化する際に `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true` をエクスポートすることで、完全なプロンプトロギングを有効にできます。

    ```go
    package main

    import (
    	"context"
    	"os"

    	"google.golang.org/adk/v2/telemetry"
    )

    func main() {
    	ctx := context.Background()

    	// OpenTelemetry環境変数を介してGenAIメッセージコンテンツのキャプチャを有効化
    	os.Setenv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true")

    	tp, err := telemetry.New(ctx)
    	if err != nil {
    		// エラー処理
    	}
    	defer tp.Shutdown(ctx)
    	tp.SetGlobalOtelProviders()
    }
    ```

=== "Kotlin"

    グローバルの `TelemetryConfig` を設定することで、完全なプロンプトロギングを有効にできます。

    ```kotlin
    --8<-- "examples/kotlin/snippets/observability/LoggingExamples.kt:capture_content"
    ```

### OTLPエクスポート

=== "Python"

    OpenTelemetry Collector（またはOTLP互換バックエンド）にプログラムからログをエクスポートするには:

    ```python
    from google.adk.telemetry.setup import maybe_set_otel_providers
    import os

    os.environ["OTEL_EXPORTER_OTLP_LOGS_ENDPOINT"] = "http://your-collector:4318/v1/logs"
    os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
    maybe_set_otel_providers()
    ```

=== "Go"

    OTLP互換バックエンドにログをエクスポートするには、`OTEL_EXPORTER_OTLP_ENDPOINT` や `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT` などの標準OpenTelemetry環境変数を設定します。ADKテレメトリパッケージは初期化時にこれらの設定を自動的に使用します。

=== "Kotlin"

    ADK KotlinのOpenTelemetry統合は**トレースのみ**を出力します。`LoggerProvider` を登録しないため、OTLPログのエクスポートはありません。アプリケーションログはJVMロギングバックエンドに出力されます。トレースエクスポートの設定については、[トレース](traces.md) のドキュメントをご覧ください。

### GCPエクスポート設定

=== "Python"

    Google Cloud Loggingにプログラムからログをエクスポートするには、OpenTelemetry Google Cloudエクスポーターを使用します。以下はPythonの例です。

    ```python
    from google.adk.telemetry.google_cloud import get_gcp_exporters
    from google.adk.telemetry.setup import maybe_set_otel_providers
    import os

    gcp_exporters = get_gcp_exporters(
      enable_cloud_logging = True,
    )
    os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
    maybe_set_otel_providers([gcp_exporters])
    ```

=== "Go"

    Google Cloud Loggingにログをエクスポートするには、`WithOtelToCloud` オプションを使用します。

    ```go
    package main

    import (
    	"context"
    	"google.golang.org/adk/v2/telemetry"
    )

    func main() {
    	ctx := context.Background()
    	tp, err := telemetry.New(ctx,
    		telemetry.WithOtelToCloud(true),
    	)
    	if err != nil {
    		// エラー処理
    	}
    	defer tp.Shutdown(ctx)
    	tp.SetGlobalOtelProviders()
    }
    ```

    Goランチャーを使用している場合は、CLIフラグを介してGCPエクスポートを有効にすることもできます。

    ```bash
    go run main.go web -otel_to_cloud
    ```

=== "Kotlin"

    ADK KotlinはOpenTelemetryログレコードを出力しないため、Cloud Loggingが受信するものはありません。アプリケーションログはJVMロギングバックエンドに送られます。ADK Kotlinの**トレース**は、標準のOTLPエクスポーターが `telemetry.googleapis.com` を指すように設定することでGoogle Cloudに送信できます。必要な認証情報、割り当てプロジェクト、`roles/telemetry.writer` 付与については、[Google CloudでのOTLP](https://cloud.google.com/stackdriver/docs/otlp/overview) をご覧ください。

## プラグインによるアクティビティロギング

ADKは、ユーザーメッセージ、モデルのリクエストとレスポンス、ツール呼び出し、および（`DebugLoggingPlugin` を使用した場合の）セッション状態を含むエージェントのアクティビティをキャプチャする組み込みプラグインを提供します。これらのプラグインを使用する際に、エージェントのロジックを変更する必要はありません。

### `LoggingPlugin` によるコンソールロギング

実行中に構造化されたアクティビティログをコンソールに出力するには、`App` に `LoggingPlugin` をアタッチします。

=== "Python"

    ```python
    from google.adk.apps import App
    from google.adk.plugins import LoggingPlugin

    app = App(
        name="my_app",
        root_agent=root_agent,
        plugins=[LoggingPlugin()],
    )
    ```

=== "Go"

    ```go
    package main

    import (
    	"context"
    	"log"
    	"os"

    	"google.golang.org/adk/v2/agent"
    	"google.golang.org/adk/v2/cmd/launcher"
    	"google.golang.org/adk/v2/cmd/launcher/full"
    	"google.golang.org/adk/v2/plugin"
    	"google.golang.org/adk/v2/plugin/loggingplugin"
    	"google.golang.org/adk/v2/runner"
    )

    func main() {
    	ctx := context.Background()
    	logPlugin := loggingplugin.MustNew("logging_plugin")

    	config := &launcher.Config{
    		AgentLoader: agent.NewSingleLoader(rootAgent),
    		PluginConfig: runner.PluginConfig{
    			Plugins: []*plugin.Plugin{logPlugin},
    		},
    	}

    	l := full.NewLauncher()
    	if err := l.Execute(ctx, config, os.Args[1:]); err != nil {
    		log.Fatalf("run failed: %v", err)
    	}
    }
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/observability/LoggingExamples.kt:logging_plugin"
    ```

### `DebugLoggingPlugin` によるファイルへの完全なデバッグキャプチャ

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.23.0</span><span class="lst-kotlin">Kotlin v0.6.0</span>
</div>

切り捨てられたコンソール出力ではなく、人間が読める形式のYAMLとして完全なインタラクションデータを `adk_debug.yaml` に追加記録するには、`DebugLoggingPlugin` を使用します。

=== "Python"

    ```python
    from google.adk.apps import App
    from google.adk.plugins import DebugLoggingPlugin

    app = App(
        name="my_app",
        root_agent=root_agent,
        plugins=[
            DebugLoggingPlugin(
                output_path="adk_debug.yaml",
                include_session_state=True,
                include_system_instruction=True,
            ),
        ],
    )
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/observability/LoggingExamples.kt:debug_logging_plugin"
    ```

!!! warning
    出力ファイルには、未加工のプロンプト、ツールの引数、セッション状態が保持されます。ADKはPythonにおいて認証情報や `temp:` スコープの状態キーを自動的にマスキング（redact）しますが、出力ファイルは機密情報として扱ってください。

## ログ出力の理解

### Pythonログエントリのサンプル

```text
2025-07-08 11:22:33,456 - DEBUG - google_adk.google.adk.models.google_llm - LLM Request: contents { ... }
```

| ログセグメント | フォーマット指定子 | 意味 |
| ------------------------------- | ---------------- | ---------------------------------------------- |
| `2025-07-08 11:22:33,456`       | `%(asctime)s`    | タイムスタンプ |
| `DEBUG`                         | `%(levelname)s`  | 重大度レベル |
| `google_adk.google.adk.models.google_llm`  | `%(name)s`       | ロガー名（ログを生成したモジュール） |
| `LLM Request: contents { ... }` | `%(message)s`    | 実際のログメッセージ |

ロガー名を確認することで、ログの発生元を即座に特定し、エージェントのアーキテクチャ内でのコンテキストを把握できます。ADKのロガー名は `google_adk.` の後にモジュールの完全修飾名が続くため、すべてのADKロガーは `google_adk` ロガーの子になります。これらは `logging.getLogger("google_adk")` を使用してグループとして設定できます。

### デバッグの例

`DEBUG` ロギングを有効にした後（上記の [ロギングレベル](#ロギングレベル) を参照）、エージェントを実行して `google_adk.google.adk.models.google_llm` ロガーからのメッセージを探します。出力には完全なLLMリクエストとレスポンスが表示されます。

```text
2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm -
LLM Request:
-----------------------------------------------------------
System Instruction:
      You roll dice and answer questions about the outcome of the dice rolls.
      ...
-----------------------------------------------------------
Contents:
{"parts":[{"text":"Roll a 6 sided dice"}],"role":"user"}
{"parts":[{"function_call":{"args":{"sides":6},"name":"roll_die"}}],"role":"model"}
{"parts":[{"function_response":{"name":"roll_die","response":{"result":2}}}],"role":"user"}
-----------------------------------------------------------
Functions:
roll_die: {'sides': {'type': <Type.INTEGER: 'INTEGER'>}}
check_prime: {'nums': {'items': {'type': <Type.INTEGER: 'INTEGER'>}, 'type': <Type.ARRAY: 'ARRAY'>}}
-----------------------------------------------------------
2025-07-10 15:26:14,309 - INFO - google_adk.google.adk.models.google_llm -
LLM Response:
-----------------------------------------------------------
Text:
I have rolled a 6 sided die, and the result is 2.
...
```

この出力から以下を確認できます:

- システム指示は正しいか？
- 会話履歴（`user` および `model` ターン）は正確か？
- 正しいツールがモデルに提供されているか？
- ツールがモデルによって正しく呼び出されているか？
- モデルが応答するのにどれくらいの時間がかかっているか？
