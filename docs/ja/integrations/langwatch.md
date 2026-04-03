---
catalog_title: LangWatch
catalog_description: ADK エージェント向けの可観測性、トレース、評価、プロンプト最適化
catalog_icon: /integrations/assets/langwatch.png
catalog_tags: ["observability"]
---

# ADK 向け LangWatch 可観測性

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[LangWatch](https://langwatch.ai) は、可観測性、評価、プロンプト最適化のためのオープンソース LLMOps プラットフォームです。
[OpenInference のインスツルメンテーション](https://github.com/Arize-ai/openinference/tree/main/python/instrumentation/openinference-instrumentation-google-adk)を使って
ADK エージェントに対する包括的なトレースを提供し、開発環境と本番環境の両方でエージェントを監視、デバッグ、改善できるようにします。

## 概要

LangWatch は組み込みの OpenTelemetry サポートを使って ADK からトレースを収集し、次のような機能を提供します。

- **自動トレース** - すべてのエージェント実行、ツール呼び出し、モデルリクエストを完全なコンテキスト付きで取得します
- **オンライン評価** - 本番トラフィックの品質と安全性を継続的にスコアリングします
- **ガードレール** - 有害な応答をリアルタイムでブロックまたは修正します
- **プロンプト管理** - 組み込みの A/B テストでプロンプトをバージョン管理、テスト、最適化します
- **データセットと実験** - 実トレースから評価セットを作成し、バッチ実験を実行します

## インストール

必要なパッケージをインストールします:

```bash
pip install langwatch openinference-instrumentation-google-adk google-adk
```

## セットアップ

[langwatch.ai](https://langwatch.ai) でサインアップするか、
プラットフォームを [セルフホスト](https://langwatch.ai/docs/self-hosting/overview) してから API キーを設定します:

```bash
export LANGWATCH_API_KEY="your-langwatch-api-key"
export GOOGLE_API_KEY="your-gemini-api-key"
```

トレースを初期化します:

```python
import langwatch
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

langwatch.setup(
    instrumentors=[GoogleADKInstrumentor()]
)
```

これで完了です。すべての ADK エージェントの動作が自動的にトレースされ、LangWatch ダッシュボードに送信されます。

## 監視する

トレースを初期化したら、通常どおり ADK エージェントを実行すると、すべてのやり取りが LangWatch に表示されます:

```python
import langwatch
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

langwatch.setup(
    instrumentors=[GoogleADKInstrumentor()]
)

# ツールを定義します
def get_weather(city: str) -> dict:
    """指定した都市の現在の天気レポートを取得します。

    Args:
        city (str): 都市名です。

    Returns:
        dict: ステータスと結果、またはエラーメッセージです。
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }

# ツール付きのエージェントを作成します
agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="天気に関する質問に答えるエージェントです。",
    instruction="利用可能なツールを使って必ず答えを見つけてください。",
    tools=[get_weather],
)

app_name = "weather_app"
user_id = "test_user"
session_id = "test_session"
runner = InMemoryRunner(agent=agent, app_name=app_name)
session_service = runner.session_service

await session_service.create_session(
    app_name=app_name,
    user_id=user_id,
    session_id=session_id,
)

# エージェントを実行します - すべてのやり取りがトレースされます
async for event in runner.run_async(
    user_id=user_id,
    session_id=session_id,
    new_message=types.Content(
        role="user",
        parts=[types.Part(text="What is the weather in New York?")],
    ),
):
    if event.is_final_response():
        print(event.content.parts[0].text.strip())
```

## カスタムメタデータの追加

`@langwatch.trace()` デコレーターを使って、トレースに追加のコンテキストを付与します:

```python
@langwatch.trace(name="ADK Weather Agent")
def run_agent(user_message: str):
    current_trace = langwatch.get_current_trace()
    if current_trace:
        current_trace.update(
            metadata={
                "user_id": "user_123",
                "agent_name": "weather_agent",
                "environment": "production",
            }
        )

    user_msg = types.Content(
        role="user", parts=[types.Part(text=user_message)]
    )
    for event in runner.run(
        user_id="demo-user",
        session_id="demo-session",
        new_message=user_msg,
    ):
        if event.is_final_response():
            return event.content.parts[0].text

    return "No response generated"
```

## サポートと資料

- [LangWatch ドキュメント](https://langwatch.ai/docs)
- [ADK 統合ガイド](https://langwatch.ai/docs/integration/python/integrations/google-ai)
- [GitHub の LangWatch リポジトリ](https://github.com/langwatch/langwatch)
- [コミュニティ Discord](https://discord.gg/langwatch)
