# エージェントアクティビティトレース

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.17.0</span><span class="lst-go">Go v1.0.0</span>
</div>

Agent Development Kit (ADK) は、リクエストがエージェントのアーキテクチャを通過する際のエンドツーエンドのプロセスを視覚化するのに役立つ分散トレース機能を提供します。メトリクスはプロセスにかかった「時間」を示し、ログは「何が起こった」かを示しますが、トレースはこれらのイベントを結び付けて、時間が費やされた正確な「場所」と、LLM 推論、ツール呼び出し、外部 API の間の階層関係を示します。

## トレース哲学

ADK のトレースへのアプローチは、既存の可観測性スタックとのシームレスな統合を保証するために、標準プロトコルに基づいて構築されています。

* **OpenTelemetry セマンティック規則:** ADK は OpenTelemetry (OTel) [Semantic Conventions for GenAI](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md) を実装します。これにより、トレース スパンと属性が標準の予測可能な名前で記録されるようになります。
* **OTLP ワイヤ形式:** ADK は標準の OTLP 形式を使用してデータを送信し、トレースが OTel 互換のバックエンド (例: Google Cloud Trace、Jaeger、Grafana Tempo、Datadog) にシームレスに統合されるようにします。
* **階層的な視覚化:** トレースは「スパン」に編成されます。エージェントの実行はルート スパンであり、これには LLM 操作の子スパンが含まれ、さらにツール実行の子スパンが含まれる場合もあります。これにより、エージェントの推論ループの明確な「ウォーターフォール」ビューが作成されます。
* **コンテキストの伝播:** ADK は、プロセス境界を越えてトレース コンテキストを自動的に渡し、エージェントがツール経由で外部マイクロサービスを呼び出す場合、そのサービスのスパンがエージェントのルート トレースにリンクされるようにします。

---

## トレーススキーマ

トレースが有効な場合、ADK はエージェントの OpenTelemetry GenAI セマンティック規則に従ってキー操作を自動的に計測します。典型的なトレース ウォーターフォールには次のスパンが含まれます。

|スパン名 |タイプ |説明 |主要な属性 |
| :--- | :--- | :--- | :--- |
| **[`invoke_agent`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-agent-client-span)** |クライアント/内部スパン |リモート サービスまたはローカルでの GenAI エージェントの呼び出しについて説明します。エージェント対話のライフサイクルを表します。| `gen_ai.agent.name`、`gen_ai.system` |
| **[`invoke_workflow`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-workflow-span)** |子スパン |複数ステップのエージェントワークフローの呼び出しについて説明します。 | `gen_ai.workflow.name`、`gen_ai.system`|
| **[`execute_tool`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#execute-tool-span)** |子スパン | GenAI システムによって要求された特定のツールまたは関数呼び出しの実行を表します。 `gen_ai.tool.name`、`gen_ai.system`|
| **[`generate_content {model.name}`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md)** |内部スパン |コンテンツを生成するための、(GenAI SDK を介した) 基礎となる言語モデルの呼び出しを表します。リクエストパラメータ、レスポンスの詳細、使用状況メトリクスを追跡します。 | `gen_ai.operation.name`、`gen_ai.system`、`gen_ai.request.model`、`gen_ai.agent.name`、`gen_ai.conversation.id`、`user.id`、`gen_ai.request.top_p`、`gen_ai.request.max_tokens`、`gen_ai.response.finish_reasons`、 `gen_ai.usage.input_tokens`、`gen_ai.usage.output_tokens` |

---

## トレースのエクスポート設定

### ADK Web でのトレースのエクスポート

`adk web` または `adk api_server` CLI コマンドを使用してエージェントを実行している場合は、トレース エクスポートを構成できます。

#### OTLP エクスポート

トレースを OTLP 互換バックエンドにエクスポートするには、標準の OTel 環境変数を設定します。

```bash
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="http://your-collector:4318/v1/traces"
adk web path/to/your/agents_dir
```

> **注:** トレースに加えてメトリクスとログを同じエンドポイントに送信したい場合は、一般的な `OTEL_EXPORTER_OTLP_ENDPOINT` 環境変数を設定することもできます。


#### GCP エクスポート

Google Cloud Trace へのトレースのエクスポートを有効にするには、`--otel_to_cloud` フラグを使用します。

```bash
adk web --otel_to_cloud path/to/your/agents_dir
```

### プログラムによるトレースのエクスポート

アプリケーション コードでプログラム的にトレース エクスポートを構成することもできます。

#### OTLP エクスポートのセットアップ

トレースを有効にし、プログラムでスパンを OpenTelemetry Collector にエクスポートするには、次の手順を実行します。

```python
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = "http://your-collector:4318/v1/traces"
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers()
```

#### GCP エクスポートの設定

トレースをプログラムで Google Cloud Trace にエクスポートするには、OpenTelemetry Google Cloud エクスポータを使用します。 Python での例を次に示します。

```python
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

gcp_exporters = get_gcp_exporters(
  enable_cloud_tracing = True,
)
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers([gcp_exporters])
```
