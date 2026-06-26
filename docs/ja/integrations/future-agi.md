---
catalog_title: Future AGI
catalog_description: traceAI OpenTelemetry 統合で ADK エージェントを追跡、評価、改善
catalog_icon: /integrations/assets/futureagi.png
catalog_tags: ["observability", "evaluation"]
---

# ADK 向け Future AGI オブザーバビリティ

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[Future AGI](https://futureagi.com) は、AI エージェント向けの
オブザーバビリティと評価プラットフォームです。
[`traceai-google-adk`](https://pypi.org/project/traceai-google-adk/)
パッケージは ADK エージェントを自動計測し、すべてのエージェント実行、
モデル呼び出し、ツール実行、イベントループサイクルを OpenTelemetry
span として Future AGI にエクスポートします。ダッシュボードでは実行
ツリーを調査し、動作を評価し、実験を実行できます。

![Future AGI ADK traces](../../integrations/assets/future_agi_traces.png)

## 概要

`traceai-google-adk` パッケージは ADK に OpenTelemetry 計測を追加し、
次のことを可能にします。

- **エージェント実行の追跡:** すべてのエージェント呼び出し、ツール
  呼び出し、モデルリクエストとレスポンスを、プロンプト、補完結果、
  パラメータ、トークン使用量とともにキャプチャします。
- **動作の評価:** キャプチャした trace に対して、事前構築済みまたは
  カスタム evaluator を実行します。
- **エージェントのデバッグ:** 階層的な実行ツリーを掘り下げ、失敗した
  ツール呼び出し、レイテンシのボトルネック、予期しない分岐を見つけます。

## 前提条件

1. [app.futureagi.com](https://app.futureagi.com) にサインアップします。
2. ダッシュボードから `FI_API_KEY` と `FI_SECRET_KEY` をコピーします。
3. 環境変数を設定します。

   ```bash
   export FI_API_KEY=<your-fi-api-key>
   export FI_SECRET_KEY=<your-fi-secret-key>
   export GOOGLE_API_KEY=<your-google-api-key>
   ```

## インストール

```bash
pip install traceai-google-adk
```

`traceai-google-adk` パッケージは `google-adk` と `google-genai` を
ランタイム依存関係として宣言しているため、これらも推移的に
インストールされます。

## Future AGI に trace を送信する

起動時に Future AGI tracer を一度登録し、エージェントを実行する
**前に** `GoogleADKInstrumentor` を接続します。以降の ADK エージェント
呼び出しは自動的にキャプチャされます。

```python
import asyncio

from fi_instrumentation import register
from fi_instrumentation.fi_types import ProjectType
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from traceai_google_adk import GoogleADKInstrumentor

tracer_provider = register(
    project_type=ProjectType.OBSERVE,
    project_name="adk-weather-agent",
)
GoogleADKInstrumentor().instrument(tracer_provider=tracer_provider)


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city."""
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": "The weather in New York is sunny with a temperature of 25°C.",
        }
    return {
        "status": "error",
        "error_message": f"Weather information for '{city}' is not available.",
    }


agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    description="Agent to answer weather questions.",
    instruction="You must use the available tools to find an answer.",
    tools=[get_weather],
)


async def main():
    runner = InMemoryRunner(agent=agent, app_name="weather_app")
    await runner.session_service.create_session(
        app_name="weather_app", user_id="user", session_id="session"
    )
    async for event in runner.run_async(
        user_id="user",
        session_id="session",
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="What is the weather in New York?")],
        ),
    ):
        if event.is_final_response():
            print(event.content.parts[0].text.strip())


if __name__ == "__main__":
    asyncio.run(main())
```

## ダッシュボードで trace を表示する

エージェントを実行したら、[Future AGI ダッシュボード](https://app.futureagi.com)
でプロジェクトを開きます。各 ADK エージェント実行は、プロンプト、
補完結果、モデルパラメータ、トークン使用量、ツール入力と出力、
イベントループサイクルを調査できる階層的な trace を生成します。

## リソース

- [PyPI の `traceai-google-adk`](https://pypi.org/project/traceai-google-adk/)
- [GitHub の `traceAI`](https://github.com/future-agi/traceAI/tree/main/python/frameworks/google-adk)
- [Future AGI ドキュメント](https://docs.futureagi.com)
