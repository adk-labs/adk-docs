---
catalog_title: Latitude
catalog_description: ADK エージェント向けのオープンソース의 観測可能性（observability）と評価
catalog_icon: /integrations/assets/latitude.png
catalog_tags: ["observability", "evaluation"]
---

# ADK向けの Latitude 観測可能性（observability）連携

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[Latitude](https://latitude.so)は、LLM アプリケーション向けのオープンソースの観測可能性（observability）および評価プラットフォームです。Latitude の [`latitude-telemetry`](https://pypi.org/project/latitude-telemetry/) Python SDK は Agent Development Kit 専用의 計測（instrumentation）を提供するため、すべてのエージェント実行、モデル生成、ツール呼び出しが OpenTelemetry トレースとしてエクスポートされ、検査、検索、評価できます。

## ADKで Latitude を使用する理由

ADK には独自の OpenTelemetry ベースのトレースが含まれています。Latitude は、エージェント向けに特別に構築されたホスト型（またはセルフホスト型）プラットフォームでこれを拡張します:

- **完全なエージェントトレース (Full agent traces)**: ネストされたエージェント、生成、およびツール呼び出しの階層構造を、ADK の呼び出し方を変更することなく自動的にキャプチャします。
- **コスト、トークン、レイテンシ (Cost, tokens, and latency)**: トレースのすべてのレベルで集計されます。
- **セッション (Sessions)**: マルチターンの会話や複数ステップのエージェント実行を単一のセッションにグループ化します。
- **評価 (Evaluations)**: LLM-as-judge またはコードベースの評価器を使用して、エージェントの出力をオフラインまたは本番環境で評価します。
- **オープンソース**: 完全にセルフホスト（self-hosted）で実行するか、管理されたクラウドサービスを使用できます。

## 前提条件

- **Latitude アカウント**と **API キー** ([console.latitude.so](https://console.latitude.so/login) で登録、またはセルフホスト)。
- **Latitude プロジェクトのスラッグ (project slug)**。
- `GOOGLE_API_KEY` として設定された **Gemini API キー**。

## インストール

```bash
pip install latitude-telemetry google-adk
```

必要な環境変数を設定します:

```bash
export LATITUDE_API_KEY="your-api-key"
export LATITUDE_PROJECT="your-project-slug"
export GOOGLE_API_KEY="your-gemini-api-key"
```

`LATITUDE_API_KEY` と `LATITUDE_PROJECT` はトレースを Latitude プロジェクトに送信します。`GOOGLE_API_KEY` は ADK の Gemini 모델呼び出しに使用されます。

## エージェントでの使用

Latitude SDK の `google_adk` 計測キーの下に `google.adk` モジュールを渡します。Latitude は OpenTelemetry トレーサープロバイダを登録し、ADK を計測します。ADK の呼び出しは現在とまったく同じままで機能します.

```python
import asyncio
import os

import google.adk
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from latitude_telemetry import Latitude, capture

latitude = Latitude(
    api_key=os.environ["LATITUDE_API_KEY"],
    project=os.environ["LATITUDE_PROJECT"],
    instrumentations={"google_adk": google.adk},
)


def get_weather(city: str) -> dict:
    """Returns the current weather for a city."""
    return {"status": "success", "report": f"The weather in {city} is sunny."}


agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    description="Agent that answers weather questions using tools.",
    instruction="Answer weather questions using get_weather.",
    tools=[get_weather],
)


async def weather_agent_run():
    runner = InMemoryRunner(agent=agent, app_name="weather_app")
    await runner.session_service.create_session(
        app_name="weather_app",
        user_id="user_123",
        session_id="session_abc",
    )

    async for event in runner.run_async(
        user_id="user_123",
        session_id="session_abc",
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What's the weather in Barcelona?")],
        ),
    ):
        if event.is_final_response() and event.content and event.content.parts:
            return event.content.parts[0].text


# capture() でリクエストやジョブをラップして、その内部で生成されるすべてのスパンに user_id、session_id、タグ、またはメタデータを関連付けます。
capture("weather-agent-run", lambda: asyncio.run(weather_agent_run()))

# プロセスが終了する前に、保留中のスパンをフラッシュしてシャットダウンします。
latitude.shutdown()
```

## 得られる機能

各エージェントの実行は、Latitude でネストされたスパンを持つトレースとして表示されます:

- **エージェントスパン (Agent spans)**: エージェント名、指示（instruction）、および構成されたツール
- **生成スパン (Generation spans)**: モデル、入出力メッセージ、およびトークン使用量
- **ツールスパン (Tool spans)**: 入力引数と出力を伴うツール呼び出し

[Latitude ダッシュボード](https://console.latitude.so/login)でプロジェクトを開き、トークン使用量とレイテンシがすべてのレベルで集計された、エージェント、生成、ツールの完全な階層構造を表示します。

## リソース

- [Latitude 公式ドキュメント](https://docs.latitude.so)
- [Latitude ADK 連携ガイド](https://docs.latitude.so/telemetry/frameworks/google-adk)
- [GitHub の Latitude リポジトリ](https://github.com/latitude-dev/latitude-llm)
