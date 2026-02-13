# WandBのWeaveによるエージェントの可観測性

[Weights & Biases (WandB) の Weave](https://weave-docs.wandb.ai/) は、モデル呼び出しのロギングと可視化のための強力なプラットフォームを提供します。Google ADKをWeaveと統合することで、OpenTelemetry（OTEL）トレースを使用して、エージェントのパフォーマンスと振る舞いを追跡・分析できます。

## 事前準備

1. [WandB](https://wandb.ai) でアカウントにサインアップしてください。

2. [WandB Authorize](https://wandb.ai/authorize) からAPIキーを取得してください。

3. 必要なAPIキーで環境を設定してください。

   ```bash
   export WANDB_API_KEY=<あなたのWandB-APIキー>
   export GOOGLE_API_KEY=<あなたのGoogle-APIキー>
   ```

## 依存関係のインストール

必要なパッケージがインストールされていることを確認してください。

```bash
pip install google-adk opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

## Weaveへのトレース送信

この例では、Google ADKのトレースをWeaveに送信するようにOpenTelemetryを設定する方法を示します。

```python
# math_agent/agent.py

import base64
import os
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from dotenv import load_dotenv

load_dotenv()

# Weaveのエンドポイントと認証を設定
WANDB_BASE_URL = "https://trace.wandb.ai"
PROJECT_ID = "your-entity/your-project"  # 例: "teamid/projectid"
OTEL_EXPORTER_OTLP_ENDPOINT = f"{WANDB_BASE_URL}/otel/v1/traces"

# 認証をセットアップ
WANDB_API_KEY = os.getenv("WANDB_API_KEY")
AUTH = base64.b64encode(f"api:{WANDB_API_KEY}".encode()).decode()

OTEL_EXPORTER_OTLP_HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "project_id": PROJECT_ID,
}

# エンドポイントとヘッダーを持つOTLPスパンエクスポーターを作成
exporter = OTLPSpanExporter(
    endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
    headers=OTEL_EXPORTER_OTLP_HEADERS,
)

# トレーサープロバイダーを作成し、エクスポーターを追加
tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))

# ADKをインポートまたは使用する前に、グローバルなトレーサープロバイダーを設定
trace.set_tracer_provider(tracer_provider)

# デモンストレーション用の簡単なツールを定義
def calculator(a: float, b: float) -> str:
    """二つの数値を足し算し、結果を返します。

    Args:
        a: 一つ目の数値
        b: 二つ目の数値

    Returns:
        aとbの合計
    """
    return str(a + b)

calculator_tool = FunctionTool(func=calculator)

# LLMエージェントを作成
root_agent = LlmAgent(
    name="MathAgent",
    model="gemini-2.0-flash-exp",
    instruction=(
        "あなたは数学ができる、役に立つアシスタントです。"
        "数学の問題が出されたら、電卓ツールを使って解いてください。"
    ),
    tools=[calculator_tool],
)
```

## Weaveダッシュボードでのトレース表示

エージェントが実行されると、そのすべてのトレースは[Weaveダッシュボード](https://wandb.ai/home)の対応するプロジェクトに記録されます。

![Weaveでのトレース](https://wandb.github.io/weave-public-assets/google-adk/traces-overview.png)

実行中にADKエージェントが行った呼び出しのタイムラインを表示できます。

![タイムラインビュー](https://wandb.github.io/weave-public-assets/google-adk/adk-weave-timeline.gif)


## 注記

- **環境変数**: WandBとGoogleの両方のAPIキーの環境変数が正しく設定されていることを確認してください。
- **プロジェクト設定**: `<your-entity>/<your-project>`を実際のWandBエンティティとプロジェクト名に置き換えてください。
- **エンティティ名**: [WandBダッシュボード](https://wandb.ai/home)にアクセスし、左側のサイドバーにある**Teams**フィールドを確認することで、エンティティ名を見つけることができます。
- **トレーサープロバイダー**: 適切なトレースを確保するため、ADKコンポーネントを使用する前にグローバルなトレーサープロバイダーを設定することが非常に重要です。

これらの手順に従うことで、Google ADKをWeaveと効果的に統合し、AIエージェントのモデル呼び出し、ツール呼び出し、推論プロセスを包括的にロギングおよび可視化できます。

## リソース

- **[OpenTelemetryのトレースをWeaveに送信](https://weave-docs.wandb.ai/guides/tracking/otel)** - 認証や高度な設定オプションを含む、WeaveでOTELを設定するための包括的なガイドです。

- **[トレースビューのナビゲート](https://weave-docs.wandb.ai/guides/tracking/trace-tree)** - トレース階層やスパンの詳細の理解を含む、Weave UIでトレースを効果的に分析・デバッグする方法を学びます。

- **[Weaveインテグレーション](https://weave-docs.wandb.ai/guides/integrations/)** - 他のフレームワークとのインテグレーションを探索し、WeaveがAIスタック全体でどのように機能するかを確認します。