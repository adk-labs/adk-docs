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
