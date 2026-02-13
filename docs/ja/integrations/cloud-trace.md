# Cloud Traceによるエージェントの可観測性

ADKを使用すると、[こちら](https://google.github.io/adk-docs/evaluate/#debugging-with-the-trace-view)で説明されている強力なWeb開発UIを利用して、エージェントのインタラクションをローカルで検査および監視できます。ただし、クラウドへのデプロイを目指す場合は、実際のトラフィックを監視するための一元化されたダッシュボードが必要になります。

Cloud TraceはGoogle Cloud Observabilityのコンポーネントです。これは、特にトレース機能に重点を置くことで、アプリケーションのパフォーマンスを監視、デバッグ、改善するための強力なツールです。Agent Development Kit（ADK）アプリケーションの場合、Cloud Traceは包括的なトレースを可能にし、リクエストがエージェントのインタラクションをどのように通過するかを理解し、AIエージェント内のパフォーマンスのボトルネックやエラーを特定するのに役立ちます。

## 概要

Cloud Traceは、トレースデータを生成するための多くの言語と取り込み方法をサポートするオープンソース標準である[OpenTelemetry](https://opentelemetry.io/)上に構築されています。これは、OpenTelemetry互換の計装も活用するADKアプリケーションの可観測性の実践と一致しており、次のことが可能になります。

- エージェントのインタラクションのトレース：Cloud Traceはプロジェクトからトレースデータを継続的に収集および分析し、ADKアプリケーション内のレイテンシの問題やエラーを迅速に診断できるようにします。この自動データ収集により、複雑なエージェントワークフローでの問題の特定プロセスが簡素化されます。
- 問題のデバッグ：詳細なトレースを分析することで、レイテンシの問題やエラーを迅速に診断します。異なるサービス間での通信レイテンシの増加として現れる問題や、ツール呼び出しなどの特定のエージェントアクション中に現れる問題を理解するために重要です。
- 詳細な分析と視覚化：Trace Explorerはトレースを分析するための主要なツールであり、スパン期間のヒートマップやリクエスト/エラー率の折れ線グラフなどの視覚的な補助機能を提供します。また、サービスや操作ごとにグループ化できるスパンテーブルも提供し、代表的なトレースへのワンクリックアクセスと、エージェントの実行パス内のボトルネックやエラーの原因を簡単に特定できるウォーターフォールビューを提供します。

次の例では、次のエージェントディレクトリ構造を想定しています。

```
working_dir/
├── weather_agent/
│   ├── agent.py
│   └── __init__.py
└── deploy_agent_engine.py
└── deploy_fast_api_app.py
└── agent_runner.py
```

```python
# weather_agent/agent.py

import os
from google.adk.agents import Agent

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "{your-project-id}")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


# ツール関数を定義する
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
            "error_message": f"'{city}'の天気情報は利用できません。",
        }


# ツールを持つエージェントを作成する
root_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    description="天気ツールを使用して質問に答えるエージェント。",
    instruction="答えを見つけるには、利用可能なツールを使用する必要があります。",
    tools=[get_weather],
)
```

## Cloud Traceのセットアップ

### Agent Engineデプロイのセットアップ

#### Agent Engineデプロイ - ADK CLIから

`adk deploy agent_engine`コマンドを使用してエージェントをデプロイするときに`--trace_to_cloud`フラグを追加することで、クラウドトレースを有効にできます。

```bash
adk deploy agent_engine \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --staging_bucket=$STAGING_BUCKET \
    --trace_to_cloud \
    $AGENT_PATH
```

#### Agent Engineデプロイ - Python SDKから

Python SDKを使用する場合は、`AdkApp`オブジェクトを初期化するときに`enable_tracing=True`を追加することで、クラウドトレースを有効にできます。

```python
# deploy_agent_engine.py

from vertexai.preview import reasoning_engines
from vertexai import agent_engines
from weather_agent.agent import root_agent

import vertexai

PROJECT_ID = "{your-project-id}"
LOCATION = "{your-preferred-location}"
STAGING_BUCKET = "{your-staging-bucket}"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

adk_app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)


remote_app = agent_engines.create(
    agent_engine=adk_app,
    extra_packages=[
        "./weather_agent",
    ],
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ],
)
```

### Cloud Runデプロイのセットアップ

#### Cloud Runデプロイ - ADK CLIから

`adk deploy cloud_run`コマンドを使用してエージェントをデプロイするときに`--trace_to_cloud`フラグを追加することで、クラウドトレースを有効にできます。

```bash
adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --trace_to_cloud \
    $AGENT_PATH
```

クラウドトレースを有効にし、Cloud Runでカスタマイズされたエージェントサービスデプロイを使用する場合は、以下の[カスタマイズされたデプロイのセットアップ](#setup-for-customized-deployment)セクションを参照してください。

### カスタマイズされたデプロイのセットアップ

#### 組み込みの`get_fast_api_app`モジュールから

独自のエージェントサービスをカスタマイズする場合は、組み込みの`get_fast_api_app`モジュールを使用してFastAPIアプリを初期化し、`trace_to_cloud=True`を設定することで、クラウドトレースを有効にできます。

```python
# deploy_fast_api_app.py

import os
from google.adk.cli.fast_api import get_fast_api_app
from fastapi import FastAPI

# クラウドトレースのためにGOOGLE_CLOUD_PROJECT環境変数を設定する
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "alvin-exploratory-2")

# 現在の作業ディレクトリで`weather_agent`ディレクトリを検出する
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# クラウドトレースを有効にしてFastAPIアプリを作成する
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    trace_to_cloud=True,
)

app.title = "weather-agent"
app.description = "エージェントweather-agentと対話するためのAPI"


# メインの実行
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
```


#### カスタマイズされたエージェントランナーから

ADKエージェントランタイムを完全にカスタマイズする場合は、Opentelemetryの`CloudTraceSpanExporter`モジュールを使用してクラウドトレースを有効にできます。

```python
# agent_runner.py

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from weather_agent.agent import root_agent as weather_agent
from google.genai.types import Content, Part
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import export
from opentelemetry.sdk.trace import TracerProvider

APP_NAME = "weather_agent"
USER_ID = "u_123"
SESSION_ID = "s_123"

provider = TracerProvider()
processor = export.BatchSpanProcessor(
    CloudTraceSpanExporter(project_id="{your-project-id}")
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

session_service = InMemorySessionService()
runner = Runner(agent=weather_agent, app_name=APP_NAME, session_service=session_service)


async def main():
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    if session is None:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )

    user_content = Content(
        role="user", parts=[Part(text="パリの天気はどうですか？")]
    )

    final_response_content = "応答なし"
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_content = event.content.parts[0].text

    print(final_response_content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```

## Cloud Traceの検査

セットアップが完了すると、エージェントと対話するたびにトレースデータが自動的にCloud Traceに送信されます。[console.cloud.google.com](https://console.cloud.google.com)にアクセスし、構成済みのGoogle CloudプロジェクトでTrace Explorerにアクセスしてトレースを検査できます。

![cloud-trace](../assets/cloud-trace1.png)

すると、`invocation`、`agent_run`、`call_llm`、`execute_tool`などのいくつかのスパン名で構成されたADKエージェントによって生成されたすべての利用可能なトレースが表示されます。

![cloud-trace](../assets/cloud-trace2.png)

トレースの1つをクリックすると、`adk web`コマンドを使用してWeb開発UIで表示されるものと同様の詳細なプロセスのウォーターフォールビューが表示されます。

![cloud-trace](../assets/cloud-trace3.png)

## リソース

- [Google Cloud Traceドキュメント](https://cloud.google.com/trace)
