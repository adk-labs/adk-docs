---
catalog_title: Phoenix
catalog_description: LLM アプリケーション向けのオープンソース・セルフホスト可観測性、トレース、評価を提供します
catalog_icon: /adk-docs/integrations/assets/phoenix.png
catalog_tags: ["observability"]
---
# Phoenixによるエージェントのオブザーバビリティ

[Phoenix](https://arize.com/docs/phoenix)は、LLMアプリケーションとAIエージェントを大規模に監視、デバッグ、改善するためのオープンソース、セルフホスト型のオブザーバビリティプラットフォームです。Google ADKアプリケーションに包括的なトレーシングと評価機能を提供します。始めるには、[無料アカウント](https://phoenix.arize.com/)にサインアップしてください。

## 概要

Phoenixは、[OpenInferenceインストルメンテーション](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)を使用してGoogle ADKからトレースを自動的に収集できます。これにより、以下のことが可能になります。

-   **エージェントの対話をトレース** - エージェントの実行、ツールの呼び出し、モデルのリクエスト、およびレスポンスを、完全なコンテキストとメタデータと共に自動的にキャプチャします。
-   **パフォーマンスを評価** - カスタムまたは事前構築済みのエバリュエータを使用してエージェントの動作を評価し、エージェントの構成をテストするための実験を実行します。
-   **問題をデバッグ** - 詳細なトレースを分析して、ボトルネック、失敗したツールの呼び出し、予期しないエージェントの動作を迅速に特定します。
-   **セルフホストによる管理** - データを独自のインフラストラクチャ上に保持します。

## インストール

### 1. 必要なパッケージをインストールする

```bash
pip install openinference-instrumentation-google-adk google-adk arize-phoenix-otel
```

## セットアップ

### 1. Phoenixを起動する

この手順ではPhoenix Cloudの使用方法を説明します。ノートブック、ターミナル、またはコンテナを使用したセルフホストで[Phoenixを起動する](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing)こともできます。

まず、[無料のPhoenixアカウント](https://phoenix.arize.com/)にサインアップします。

**PhoenixのエンドポイントとAPIキーを設定します:**

```python
import os

# トレーシング用にPhoenix APIキーを追加
PHOENIX_API_KEY = "YOUR_API_KEY_HERE"
os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={PHOENIX_API_KEY}"
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "https://app.phoenix.arize.com"
```

**Phoenix APIキー**は、ダッシュボードのKeysセクションで確認できます。

### 2. アプリケーションをPhoenixに接続する

```python
from phoenix.otel import register

# Phoenixトレーサーを設定
tracer_provider = register(
    project_name="my-llm-app",  # デフォルトは'default'
    auto_instrument=True        # インストール済みのOI依存関係に基づいてアプリを自動で計装
)
```

## 監視

トレーシングの設定が完了したので、すべてのGoogle ADK SDKリクエストはオブザーバビリティと評価のためにPhoenixにストリーミングされます。

```python
import nest_asyncio
nest_asyncio.apply()

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# ツール関数を定義
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
                "ニューヨークの天気は晴れで、気温は摂氏25度（華氏77度）です。"
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"'{city}'の天気情報はありません。",
        }

# ツールを持つエージェントを作成
agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash-exp",
    description="天気ツールを使用して質問に答えるエージェント。",
    instruction="答えを見つけるには、利用可能なツールを使用する必要があります。",
    tools=[get_weather]
)

app_name = "weather_app"
user_id = "test_user"
session_id = "test_session"
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id
)

# エージェントを実行（すべての対話がトレースされます）
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(role="user", parts=[
        types.Part(text="ニューヨークの天気は？")]
    )
):
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## サポートとリソース
-   [Phoenixドキュメント](https://arize.com/docs/phoenix/integrations/llm-providers/google-gen-ai/google-adk-tracing)
-   [コミュニティSlack](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
-   [OpenInferenceパッケージ](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
