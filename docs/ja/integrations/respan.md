---
catalog_title: Respan
catalog_description: Respan 観測可能性（observability）により ADK エージェントをトレース、デバッグ、モニタリングします
catalog_icon: /integrations/assets/respan.svg
catalog_tags: ["observability"]
---

# ADK向けの Respan 観測可能性（observability）連携

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[Respan](https://www.respan.ai/)は、ADK runner、agent、model、tool のスパンをキャプチャし、Respan プラットフォームで完全なエージェントワークフローを検査できるようにします。ADK 連携には、OpenInference ADK インストルメンターをラップし、トレースがエクスポートされる前に Respan 固有のスパン正規化を追加する [`respan-instrumentation-google-adk`](https://pypi.org/project/respan-instrumentation-google-adk/) が使用されます。

## 概要

ADK で Respan を使用して以下を実行できます:

- **エージェント実行のトレース (Trace agent runs)**: ランナーの呼び出し、エージェントの実行、モデルの呼び出し、およびツールの呼び出しを1つのトレース内にキャプチャします。
- **失敗のデバッグ (Debug failures)**: ネストされた ADK ワークフロー全体の、スパンの入力, 出力, タイミング, およびエラーを検査します。
- **本番メタデータの追跡 (Track production metadata)**: リクエストから生成されるすべてのスパンに、顧客、スレッド、環境、およびカスタムメタデータを関連付けます。
- **Respan ゲートウェイを介したモデルルーティング (Route models through the Respan gateway)**: モデルルーティングを一元化したい場合に、ADK の LiteLLM アダプタを Respan の OpenAI 互換ゲートウェイと組み合わせて使用します。

## 前提条件

- Python 3.11, 3.12, または 3.13。
- Respan API キー。
- ADK エージェントが Gemini を直接呼び出す場合は Google API キー。

## インストール

Respan SDK、ADK インストルメンター、および ADK をインストールします:

```bash
pip install respan-ai respan-instrumentation-google-adk "google-adk[extensions]"
```

必要な環境変数を設定します:

```bash
export RESPAN_API_KEY="YOUR_RESPAN_API_KEY"
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
```

`RESPAN_API_KEY` はトレースを Respan に送信します。 `GOOGLE_API_KEY` は直接の Gemini モデル呼び出しに使用されます。

## ADK エージェントのトレース

ADK エージェントを実行する前に Respan を初期化します。初期化後に開始されたすべての ADK 実行は自動的にトレースされます。

```python
import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from respan import Respan
from respan_instrumentation_google_adk import GoogleADKInstrumentor

respan = Respan(
    instrumentations=[GoogleADKInstrumentor()],
    environment="development",
)

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="You are a concise assistant.",
)


async def main():
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="respan-adk-demo",
        user_id="user_1",
    )
    runner = Runner(
        agent=agent,
        app_name="respan-adk-demo",
        session_service=session_service,
    )
    message = types.Content(
        role="user",
        parts=[types.Part(text="Say hello in one sentence.")],
    )

    async for event in runner.run_async(
        user_id="user_1",
        session_id=session.id,
        new_message=message,
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)

    respan.flush()
    respan.shutdown()


asyncio.run(main())
```

[Respan トレースページ](https://platform.respan.ai/platform/traces)を開いて、ランナー、エージェント、モデル、ツールスパンを含む ADK ワークフローを表示します。

## リクエストメタデータの追加

`propagate_attributes()` を使用して、コンテキスト内で生成されるすべてのスパンにリクエストごとの識別子とメタデータを追加します。

```python
from respan import Respan, propagate_attributes
from respan_instrumentation_google_adk import GoogleADKInstrumentor

respan = Respan(instrumentations=[GoogleADKInstrumentor()])


async def handle_user_request(user_id: str, message: str):
    with propagate_attributes(
        customer_identifier=user_id,
        thread_identifier="conversation_123",
        metadata={"source": "web"},
    ):
        return await run_adk_agent(message)
```

## ツール呼び出しのトレース

ADK ツールは、シリアル化された入力、出力、およびタイミングを伴う子ツールスパンとしてキャプチャされます。

```python
from google.adk.agents import Agent


def get_weather(city: str) -> str:
    """都市の決定論的な天気予報を返す。"""
    return f"{city}: sunny, 72F, light wind"


agent = Agent(
    name="weather_agent",
    model="gemini-flash-latest",
    instruction="Use the get_weather tool when weather is requested.",
    tools=[get_weather],
)
```

## Respan ゲートウェイの使用

ADK は、LiteLLM アダプタを使用して Respan ゲートウェイを介してモデル呼び出しをルーティングできます。これは、複数のモデルプロバイダに対して1つの OpenAI 互換エンドポイントが必要な場合に便利です。

```bash
export RESPAN_API_KEY="YOUR_RESPAN_API_KEY"
export RESPAN_BASE_URL="https://api.respan.ai/api"
export RESPAN_MODEL="openai/gpt-5-mini"
```

```python
import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

agent = Agent(
    name="assistant",
    model=LiteLlm(
        model=os.getenv("RESPAN_MODEL", "openai/gpt-5-mini"),
        api_key=os.environ["RESPAN_API_KEY"],
        api_base=os.getenv("RESPAN_BASE_URL", "https://api.respan.ai/api"),
    ),
    instruction="You are a concise assistant.",
)
```

## 리소스

- [Respan ADK トレースドキュメント](https://www.respan.ai/docs/integrations/google-adk)
- [Respan ADK ゲートウェイドキュメント](https://www.respan.ai/docs/integrations/gateway/google-adk)
- [Respan Python サンプル](https://github.com/respanai/respan-example-projects/tree/main/python/tracing/google-adk)
- [Respan プラットフォーム](https://platform.respan.ai/platform/traces)
