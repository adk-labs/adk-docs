# エージェント活動メトリクス

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.32.0</span>
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

| メトリクス名 | 種類 | 説明 | 主な属性（ディメンション） |
| :--- | :--- | :--- | :--- |
| **`gen_ai.agent.invocation.duration`** | Histogram | エージェントがプロンプトを処理してレスポンスを返すまでにかかった合計時間です。 | `gen_ai.agent.name`, `error.type` |
| **`gen_ai.tool.execution.duration`** | Histogram | エージェントが呼び出した個別ツールの実行レイテンシです。遅い外部 API を見つけるのに役立ちます。 | `gen_ai.tool.name`, `error.type` |
| **`gen_ai.agent.request.size`** | Histogram | エージェントに送信された入力リクエストのサイズまたは複雑さです。 | `gen_ai.agent.name` |
| **`gen_ai.agent.response.size`** | Histogram | エージェントが生成した最終レスポンスのサイズまたは複雑さです。 | `gen_ai.agent.name` |
| **`gen_ai.agent.workflow.steps`** | Histogram | エージェントがワークフローを完了するまでに要した反復ステップまたは推論ループ数を追跡します。 | `gen_ai.agent.name` |

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
