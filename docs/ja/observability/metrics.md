# エージェント活動メトリクス

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.32.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

Agent Development Kit (ADK) は、エージェントのパフォーマンス、コスト、利用パターンを
理解するための、組み込みのベンダー中立なメトリクス収集機能を提供します。ログが
*何が* 起きたかについて詳細な物語を提供するのに対し、メトリクスは物事が
*どのくらい頻繁に*、*どのくらい速く* 起きているかに答える集計済みの定量データを
提供します。

## メトリクスの考え方

ADK のメトリクスに対するアプローチは、軽量で標準化されており、選択した
監視バックエンドに完全に依存しないように設計されています。

*   **OpenTelemetry セマンティック規約:** ADK は OpenTelemetry (OTel)
    [GenAI セマンティック規約](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-metrics.md)を
    実装しています。これにより、メトリクスは標準的で予測可能な属性名とメトリクス名で
    記録されます。
*   **OTLP ワイヤ形式:** ADK は標準の OTLP 形式でデータを出力するため、任意の
    OTel 互換バックエンド（Prometheus、Datadog、SigNoz、Google Cloud Monitoring など）に
    シームレスに統合できます。
*   **コストとパフォーマンス重視:** 大量のデータを分析する場合、メトリクスはログや
    トレースよりも大幅に低コストで高性能です。ADK は LLM アプリケーションにとって
    重要なシグナルである、トークン消費量、リクエスト遅延、ツール実行の信頼性を
    追跡します。
*   **ベンダー中立なエクスポート:** ADK は特定のメトリクスパイプラインに固定されません。
    標準の OTel meter provider をインスタンス化し、インフラ要件に応じた任意の場所へ
    データをエクスポートできます。

---

## メトリクススキーマ

メトリクスを有効にすると、ADK は OpenTelemetry GenAI セマンティック規約に基づき、
エージェントのライフサイクル、ワークフローステップ、ツール実行を自動的に計測します。
次の主要なメトリクスが出力されます。

| メトリクス名 | タイプ | 説明 | 主要な属性（次元） |
| :--- | :--- | :--- | :--- |
| **`gen_ai.invoke_agent.duration`** | Histogram (seconds) | エージェントがプロンプトを処理して応答を返すまでにかかった合計時間。 | `gen_ai.agent.name`, `error.type` |
| **`gen_ai.invoke_workflow.duration`** | Histogram (seconds) | ワークフローの実行にかかった時間。 | `gen_ai.operation.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (ネストされたワークフローのみ), `error.type` |
| **`gen_ai.execute_tool.duration`** | Histogram (seconds) | エージェントによって呼び出された個別ツールの実行レイテンシ。低速な外部 API の特定に役立ちます。 | `gen_ai.agent.name`, `gen_ai.tool.name`, `gen_ai.tool.type`, `error.type` |
| **`gen_ai.invoke_agent.inference_calls`** | Histogram (count) | 1 回のエージェント呼び出し中に実行された推論（モデル）呼び出しの回数。 | `gen_ai.agent.name` |
| **`gen_ai.invoke_agent.tool_calls`** | Histogram (count) | 1 回のエージェント呼び出し中に実行されたツール呼び出しの回数。 | `gen_ai.agent.name` |
| **`gen_ai.client.operation.duration`** | Histogram (seconds) | 単一モデルの `generate_content` 呼び出しのレイテンシ。 | `gen_ai.agent.name`, `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `error.type` |
| **`gen_ai.client.token.usage`** | Histogram (tokens) | モデル呼び出しごとのトークン消費量。`gen_ai.token.type` により入力と出力に分割されます。 | `gen_ai.agent.name`, `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.token.type` |

### 実験的メトリクス

ADK は `adk.experimental.*` ネームスペースで追加のテレメトリを出力します。これには以下のメトリクスだけでなくスパン属性も含まれます。これらはいずれも OpenTelemetry のセマンティック規約の一部ではないため、名前、属性、意味がリリース間で変更される可能性があります。自由に探索できますが、名前が確定するまではこれらに依存して構築した長期間運用する仕組みを再確認する必要が生じる可能性があることに留意してください。

以下のメトリクスは、`gen_ai.client.*` が測定する単一のモデル呼び出しよりも一段階粒度の高い、エージェント呼び出し全体またはワークフロー全体のトークン消費量と呼び出し回数を集計します。これにより、モデル呼び出しを自分で合算することなく 1 ターンのコストを把握できます。

これらはデフォルトで無効になっています。有効にするには環境変数を設定します:

```bash
export ADK_EXPERIMENTAL_TELEMETRY=true
```

リクエストごとにオプトインすることも可能で、環境変数よりも優先されます:

```python
from google.adk.agents.run_config import RunConfig
from google.adk.telemetry import TelemetryConfig

run_config = RunConfig(
    telemetry=TelemetryConfig(adk_experimental_telemetry_opt_in=True)
)
```

どちらも設定されていない場合、以下のメトリクスは記録されません。

8 つの `invoke_workflow` 行にはもう 1 つ設定が必要です: Vertex AI Agent Engine ではデフォルトで有効、それ以外の環境では無効になっているテレメトリスキーマ v2 です。他の環境では `ADK_TELEMETRY_SCHEMA_VERSION_OPT_IN=2` を設定してください。設定しない場合、それらの行は空のままになります。`invoke_agent` 行は影響を受けず、`Workflow` エンジン上に構築されたアプリはどちらのバージョンでもノードごとのデータポイントを記録します。

| メトリクス名 | タイプ | 説明 | 主要な属性（次元） |
| :--- | :--- | :--- | :--- |
| **`adk.experimental.invoke_agent.input_tokens`** | Histogram (tokens) | サーバー側ツール結果やキャッシュされたプロンプトトークンを含め、1 回のエージェント呼び出しで合算された入力（プロンプト）トークン。 | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.output_tokens`** | Histogram (tokens) | 推論トークンおよびツール呼び出しの出力に消費されたトークンを含め、1 回のエージェント呼び出しで合算された出力（補完）トークン。 | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.total_tokens`** | Histogram (tokens) | 1 回のエージェント呼び出しの入力トークンと出力トークンの合計。 | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.cache_read.input_tokens`** | Histogram (tokens) | プロバイダー管理キャッシュから提供された入力トークン（1 回のエージェント呼び出しで合算）。 | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.reasoning.output_tokens`** | Histogram (tokens) | 推論（思考の連鎖 / 拡張思考）に消費された出力トークン（1 回のエージェント呼び出しで合算）。 | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.tool.input_tokens`** | Histogram (tokens) | コード実行や検索グラウンディングなど、単一リクエスト内でモデルが自身にフィードバックしたサーバー側ツール結果の入力トークン。クライアント側の関数ツールでは 0。 | `gen_ai.agent.name` |
| **`adk.experimental.invoke_workflow.input_tokens`** | Histogram (tokens) | 1 回のワークフロー呼び出しで実行された全エージェントにわたる上記の `input_tokens` の合算。 | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (ネストされたワークフローのみ) |
| **`adk.experimental.invoke_workflow.output_tokens`** | Histogram (tokens) | 1 回のワークフロー呼び出しで実行された全エージェントにわたる上記の `output_tokens` の合算。 | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (ネストされたワークフローのみ) |
| **`adk.experimental.invoke_workflow.total_tokens`** | Histogram (tokens) | 1 回のワークフロー呼び出しで実行された全エージェントにわたる上記の `total_tokens` の合算。 | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (ネストされたワークフローのみ) |
| **`adk.experimental.invoke_workflow.cache_read.input_tokens`** | Histogram (tokens) | 1 回のワークフロー呼び出しで実行された全エージェントにわたる上記の `cache_read.input_tokens` の合算。 | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (ネストされたワークフローのみ) |
| **`adk.experimental.invoke_workflow.reasoning.output_tokens`** | Histogram (tokens) | 1 回のワークフロー呼び出しで実行された全エージェントにわたる上記の `reasoning.output_tokens` の合算。 | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (ネストされたワークフローのみ) |
| **`adk.experimental.invoke_workflow.tool.input_tokens`** | Histogram (tokens) | 1 回のワークフロー呼び出しで実行された全エージェントにわたる上記の `tool.input_tokens` の合算。 | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (ネストされたワークフローのみ) |
| **`adk.experimental.invoke_workflow.inference_calls`** | Histogram (count) | 1 回のワークフロー呼び出し全体で行われた推論（モデル）呼び出しの回数。 | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (ネストされたワークフローのみ) |
| **`adk.experimental.invoke_workflow.tool_calls`** | Histogram (count) | 1 回のワークフロー呼び出し全体で行われたツール呼び出しの回数。 | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (ネストされたワークフローのみ) |

!!! warning
    ネストされたワークフローは独自のデータポイントを記録し、その合計はそれを囲む各親ワークフローにも組み込まれるため、すべてのデータポイントで `invoke_workflow` メトリクスを合算すると二重カウントになります。

`gen_ai.workflow.nested` 属性はネストされたワークフローにのみ設定されるため、これを除外すると最も外側のワークフローのみが残り、そのデータポイントがターン全体をカバーします。ワークフロー全体にわたる値は単一のエージェントに帰属させることができないため、ワークフローメトリクスにはエージェントの次元がありません。代わりに 2 つの名前を持ちます: `gen_ai.workflow.name` は `gen_ai.invoke_workflow.duration` と結合され、`adk.experimental.root_agent.name` はアプリを識別します（ターンがサブエージェントに入ると 2 つの名前は一致しなくなります）。

---

## メトリクスエクスポートの設定

### ADK Web でのメトリクスエクスポート

`adk web` または `adk api_server` CLI コマンドでエージェントを実行している場合、
メトリクスエクスポートを構成できます。

#### OTLP エクスポート

OTLP 互換バックエンドへメトリクスをエクスポートするには、標準の OTel 環境変数を
設定します。

```bash
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="http://your-collector:4318/v1/metrics"
adk web path/to/your/agents_dir
```

> **注:** メトリクスに加えてトレースやログも同じエンドポイントへ送信したい場合は、
> 汎用の `OTEL_EXPORTER_OTLP_ENDPOINT` 環境変数も設定できます。

#### GCP エクスポート

Google Cloud Monitoring へのメトリクスエクスポートを有効にするには、
`--otel_to_cloud` フラグを使用します。

```bash
adk web --otel_to_cloud path/to/your/agents_dir
```

### プログラムによるメトリクスエクスポート

アプリケーションコードでメトリクスエクスポートをプログラムから構成することもできます。

#### OTLP エクスポート設定

メトリクスを有効にし、OpenTelemetry Collector または OTLP 互換バックエンドへ
プログラムからエクスポートするには、次のように設定します。

```python
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

os.environ["OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"] = "http://your-collector:4318/v1/metrics"
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers()
```

#### GCP エクスポート設定

Google Cloud Monitoring へメトリクスをプログラムからエクスポートするには、
OpenTelemetry Google Cloud exporter を使用します。次は Python の例です。

```python
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

gcp_exporters = get_gcp_exporters(
  enable_cloud_metrics = True,
)
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers([gcp_exporters])
```

### Kotlinのプログラムによる設定

Kotlinでは、ADKは標準の`GlobalOpenTelemetry`を使用してメトリクスを管理します。OpenTelemetry SDKに`MeterProvider`を構成すると、メトリクス収集を有効にできます。

```kotlin
--8<-- "examples/kotlin/snippets/observability/SetupExample.kt:full_example"
```
