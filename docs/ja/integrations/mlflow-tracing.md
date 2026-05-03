---
catalog_title: MLflow Tracing
catalog_description: エージェントの実行、ツール呼び出し、モデルリクエストの OpenTelemetry トレースを取り込む
catalog_icon: /integrations/assets/mlflow.png
catalog_tags: ["observability"]
---


# ADK の MLflow 可観測性

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[MLflow Tracing](https://mlflow.org/docs/latest/genai/tracing/) が提供する
OpenTelemetry (OTel) トレースを取り込むためのファーストクラスのサポート。 Google ADK が発行する
OTel は、エージェントの実行、ツールの呼び出し、送信できるモデルのリクエストに対応します
分析とデバッグのために MLflow Tracking Server に直接送信します。

## 前提条件

- MLflow バージョン 3.6.0 以降。 OpenTelemetry の取り込みは以下でのみサポートされています。
  MLflow 3.6.0以降。
- SQL ベースのバックエンド ストア (SQLite、PostgreSQL、MySQL など)。ファイルベースのストア
  OTLP 取り込みはサポートされていません。
- Google ADK が環境にインストールされていること。

## 依存関係をインストールする

```bash
pip install "mlflow>=3.6.0" google-adk opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

## MLflow 追跡サーバーを開始します

SQL バックエンドとポート (この例では 5000) を使用して MLflow を開始します。

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000
```

`--backend-store-uri` を他の SQL バックエンド (PostgreSQL、MySQL、
MSSQL)。 OTLP 取り込みは、ファイルベースのバックエンドではサポートされていません。

## OpenTelemetry を構成する (必須)

前に、OTLP エクスポータを構成し、グローバル トレーサ プロバイダを設定する必要があります。
スパンが MLflow に出力されるように、ADK コンポーネントを使用します。

インポートする前に、コードで OTLP エクスポーターとグローバル トレーサー プロバイダーを初期化します。
または ADK エージェント/ツールを構築します。

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

これにより、OpenTelemetry パイプラインが構成され、ADK スパンが MLflow に送信されます。
実行ごとにサーバー。

## 例: ADK エージェントをトレースする

これで、単純な数学エージェントのエージェント コードを、
OTLP エクスポータとトレーサ プロバイダを設定します。

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
    model="gemini-flash-latest",
    instruction=(
        "You are a helpful assistant that can do math. "
        "When asked a math problem, use the calculator tool to solve it."
    ),
    tools=[calculator_tool],
)
```

次のコマンドを使用してエージェントを実行します。

```bash
adk run my_agent
```

そして、数学の問題を尋ねます。

```console
What is 12 + 34?
```

次のような出力が表示されるはずです。

```console
[MathAgent]: The answer is 46.
```

## MLflow でトレースを表示する

`http://localhost:5000` で MLflow UI を開き、実験を選択して、
ADK エージェントによって生成されたトレース ツリーとスパンを検査します。

![MLflow Traces](https://mlflow.org/docs/latest/images/llms/tracing/google-adk-tracing.png)

## ヒント

- ADK オブジェクトをインポートまたは初期化する前に、トレーサ プロバイダを設定します。
  スパンがキャプチャされます。
- プロキシの背後またはリモート ホスト上で、`localhost:5000` を実際のサーバーに置き換えます。
  住所。

## リソース

- [MLflow Tracing Documentation](https://mlflow.org/docs/latest/genai/tracing/):
  他のライブラリをカバーする MLflow Tracing の公式ドキュメント
  トレースの統合と下流での使用（評価、監視、
  検索など。
- [OpenTelemetry in MLflow](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/):
  MLflow で OpenTelemetry を使用する方法に関する詳細なガイド。
- [MLflow for Agents](https://mlflow.org/docs/latest/genai/): 包括的
  MLflow を使用して本番環境に対応したエージェントを構築する方法に関するガイド。
