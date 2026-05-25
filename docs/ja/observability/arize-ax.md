# Arize AX によるエージェントの可観測性

[Arize AX](https://arize.com/docs/ax) は、大規模な LLM アプリケーションと AI エージェントを監視、デバッグ、改善するための本番運用レベルの可観測性プラットフォームです。Google ADK アプリケーション向けに包括的なトレース、評価、モニタリング機能を提供します。始めるには、[無料アカウント](https://app.arize.com/auth/join)に登録してください。

オープンソースでセルフホスト可能な代替手段については、[Phoenix](https://arize.com/docs/phoenix)を確認してください。

## 概要

Arize AX は [OpenInference インストルメンテーション](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)を使用して Google ADK からトレースを自動収集できます。これにより、次のことが可能になります。

-   **エージェントのやり取りをトレース** - すべてのエージェント実行、ツール呼び出し、モデルリクエスト、レスポンスをコンテキストとメタデータ付きで自動的にキャプチャ
-   **パフォーマンスを評価** - カスタムまたは事前構築済みの評価器を使用してエージェントの動作を評価し、エージェント構成をテストする実験を実行
-   **本番環境でモニタリング** - リアルタイム ダッシュボードとアラートを設定してパフォーマンスを追跡
-   **問題をデバッグ** - 詳細なトレースを分析して、ボトルネック、失敗したツール呼び出し、予期しないエージェント動作をすばやく特定

![エージェント トレース](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-traces.png)

## インストール

必要なパッケージをインストールします。

```bash
pip install openinference-instrumentation-google-adk google-adk arize-otel
```

## セットアップ

### 1. 環境変数を設定する

Google API キーを設定します。

```bash
export GOOGLE_API_KEY=[your_key_here]
```

### 2. アプリケーションを Arize AX に接続する

```python
from arize.otel import register

# Arize AX に登録
tracer_provider = register(
    space_id="your-space-id",      # アプリのスペース設定ページで確認できます
    api_key="your-api-key",        # アプリのスペース設定ページで確認できます
    project_name="your-project-name"  # 任意の名前を指定します
)

# OpenInference の自動インストルメンターをインポートして構成します
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

# 自動インストルメンテーションを完了
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)
```

## 観測する

トレース設定が完了すると、すべての Google ADK SDK リクエストが可観測性と評価のために Arize AX にストリーミングされます。

```python
import nest_asyncio
nest_asyncio.apply()

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

# ツール関数を定義
def get_weather(city: str) -> dict:
    """指定した都市の現在の天気レポートを取得します。

    引数:
        city (str): 天気レポートを取得する都市名。

    戻り値:
        dict: ステータスと結果、またはエラーメッセージ。
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "ニューヨークの天気は晴れで、気温は摂氏 25 度"
                "（華氏 77 度）です。"
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"'{city}' の天気情報は提供されていません。",
        }

# ツールを使ってエージェントを作成
agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash-exp",
    description="天気ツールを使用して質問に回答するエージェント。",
    instruction="回答を見つけるには、利用可能なツールを使用する必要があります。",
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

# エージェントを実行（すべてのやり取りがトレースされます）
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(role="user", parts=[
        types.Part(text="ニューヨークの天気はどうですか？")]
    )
):
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## Arize AX で結果を確認する

![Arize AX のトレース](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-dashboard.png)
![エージェントの可視化](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-agent.png)
![エージェント実験](https://storage.googleapis.com/arize-phoenix-assets/assets/images/google-adk-experiments.png)

## サポートとリソース

- [Arize AX ドキュメント](https://arize.com/docs/ax/observe/tracing-integrations-auto/google-adk)
- [Arize コミュニティ Slack](https://arize-ai.slack.com/join/shared_invite/zt-11t1vbu4x-xkBIHmOREQnYnYDH1GDfCg#/shared-invite/email)
- [OpenInference パッケージ](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)
