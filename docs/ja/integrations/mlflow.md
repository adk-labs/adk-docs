---
catalog_title: MLflow
catalog_description: エージェント実行、ツール呼び出し、モデル要求の OpenTelemetry トレースを収集します
catalog_icon: /adk-docs/integrations/assets/mlflow.png
catalog_tags: ["observability"]
---

# ADK 向け MLflow observability

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[MLflow Tracing](https://mlflow.org/docs/latest/genai/tracing/) は
OpenTelemetry (OTel) トレースの取り込みを第一級でサポートします。Google ADK は
エージェント実行、ツール呼び出し、モデル要求の OTel span を出力でき、
それらを MLflow Tracking Server に直接送って分析・デバッグできます。

## 前提条件

- MLflow 3.6.0 以上。OpenTelemetry 取り込みは
  MLflow 3.6.0+ のみ対応です。
- SQL ベースのバックエンドストア (例: SQLite、PostgreSQL、MySQL)。
  ファイルベースストアは OTLP 取り込みをサポートしません。
- 環境に Google ADK がインストール済みであること。

## 依存関係のインストール

```bash
pip install "mlflow>=3.6.0" google-adk opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

## MLflow Tracking Server を起動

SQL バックエンドとポート (この例では 5000) で MLflow を起動します:

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000
```

`--backend-store-uri` は他の SQL バックエンド (PostgreSQL、MySQL、MSSQL) も指定可能です。
OTLP 取り込みはファイルベースバックエンドではサポートされません。

## OpenTelemetry の設定 (必須)

ADK コンポーネントを使う前に、OTLP exporter を設定し、
グローバルトレーサープロバイダーを設定する必要があります。これにより span が MLflow へ送信されます。

ADK エージェント/ツールを import・構築する前に、OTLP exporter と
グローバルトレーサープロバイダーをコードで初期化してください:

```python
# my_agent/agent.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

exporter = OTLPSpanExporter(
    endpoint="http://localhost:5000/v1/traces",
    headers={"x-mlflow-experiment-id": "123"}  # replace with your experiment id
)

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(exporter))
trace.set_tracer_provider(provider)  # set BEFORE importing/using ADK
```

この設定で OpenTelemetry パイプラインが構成され、実行ごとに ADK span が MLflow サーバーへ送信されます。

## 例: ADK エージェントをトレースする

次に、OTLP exporter と tracer provider の設定コードの後に、
シンプルな算数エージェントのコードを追加できます:

```python
# my_agent/agent.py
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool


def calculator(a: float, b: float) -> str:
    """Add two numbers and return the result."""
    return str(a + b)


calculator_tool = FunctionTool(func=calculator)

root_agent = LlmAgent(
    name="MathAgent",
    model="gemini-2.0-flash-exp",
    instruction=(
        "You are a helpful assistant that can do math. "
        "When asked a math problem, use the calculator tool to solve it."
    ),
    tools=[calculator_tool],
)
```

次のコマンドでエージェントを実行します:

```bash
adk run my_agent
```

算数問題を質問します:

```console
What is 12 + 34?
```

次のような出力が表示されます:

```console
[MathAgent]: The answer is 46.
```

## MLflow でトレースを確認

`http://localhost:5000` で MLflow UI を開き、実験を選択して、
ADK エージェントが生成したトレースツリーと span を確認してください。

![MLflow Traces](https://mlflow.org/docs/latest/images/llms/tracing/google-adk-tracing.png)

## ヒント

- ADK オブジェクトを import/初期化する前に tracer provider を設定し、
  すべての span を確実に収集してください。
- プロキシ配下やリモートホストでは `localhost:5000` を
  サーバーアドレスに置き換えてください。

## リソース

- [MLflow Tracing Documentation](https://mlflow.org/docs/latest/genai/tracing/):
  他ライブラリ連携や評価、監視、検索など、トレースの下流利用まで扱う公式ドキュメント。
- [OpenTelemetry in MLflow](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/):
  MLflow で OpenTelemetry を使う詳細ガイド。
- [MLflow for Agents](https://mlflow.org/docs/latest/genai/):
  本番向けエージェント構築のための MLflow 総合ガイド。
