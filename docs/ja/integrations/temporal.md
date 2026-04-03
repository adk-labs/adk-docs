---
catalog_title: Temporal
catalog_description: 耐障害性と拡張性を備えたエージェント、長時間実行のエージェントとツール、人間の承認、安全なバージョニング
catalog_icon: /integrations/assets/temporal.png
catalog_tags: ["resilience"]
---

# ADK 向け Temporal プラグイン

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Temporal](https://temporal.io) は、ADK エージェントを耐障害性が高く、拡張可能で、本番運用に適したものにする汎用の永続実行プラットフォームです。
LLM 呼び出しとツール実行は、自動再試行と復旧を備えた Temporal [Activity](https://docs.temporal.io/activities) として実行されます。
何かが失敗しても、エージェントはちょうど中断したところから再開し、手動のセッション管理や外部データベースは不要です。

## ユースケース

Temporal プラグインは、エージェントに次の機能を提供します。

- **永続実行**: 進行状況を失いません。エージェントがクラッシュしたり停止したりしても、Temporal は最後に成功したステップから自動的に復旧します。手動の [セッション再開](/runtime/resume/#resume-a-stopped-workflow) は不要です。
- **組み込みの再試行とレート制限**: バックオフ付きの [再試行ポリシー](https://docs.temporal.io/encyclopedia/retry-policies) を構成でき、LLM プロバイダーからのバックプレッシャー処理機構も備えています。
- **長時間実行・常駐エージェント**: ブロッキング await を使って、数時間、数日、あるいは無期限に動作するエージェントやツールをサポートします。
- **Human-in-the-loop**: 人間が承認するまで実行を一時停止し、その後中断した場所から再開します。Temporal の [task routing](https://docs.temporal.io/task-routing) は、ユーザーのチャットや承認のような受信シグナルを、適切なワークフローへスケーラブルに振り分けます。
- **可観測性とデバッグ**: エージェント実行のすべてのステップを確認し、ワークフローを決定論的に再生し、[Temporal UI](https://docs.temporal.io/web-ui) を使って失敗箇所を特定できます。

## 前提条件

- Python 3.10+
- [Gemini API キー](https://aistudio.google.com/app/api-keys)(または任意の [対応モデル](/agents/models/))
- 実行中の Temporal サーバー([ローカル開発サーバー](https://docs.temporal.io/cli#start-dev-server)、[セルフホスト](https://docs.temporal.io/self-hosted-guide)、または [Temporal Cloud](https://temporal.io/cloud))
- Temporal Python SDK [1.24.0](https://github.com/temporalio/sdk-python/releases/tag/1.24.0)

Temporal Python 1.24.0 時点では、この統合は実験的であり、今後互換性を壊す変更が入る可能性があります。


## インストール

google-adk の extra とあわせて Temporal Python SDK をインストールします:

```bash
pip install "temporalio[google-adk]"
```

## エージェントで使う

### 基本設定

この統合には、**ワークフロー側**(エージェントが実行される場所)と
**ワーカー側**(実行環境をホストする場所)の 2 つの側面があります。

**1. エージェントとワークフローを定義する**

ADK エージェントを作成し、Temporal Workflow で包みます。`TemporalModel` を使って LLM 呼び出しを Temporal Activity 経由でルーティングします。

```python
from contextlib import aclosing
from datetime import timedelta
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from temporalio import activity, workflow
from temporalio.common import RetryPolicy
from temporalio.contrib.google_adk_agents import TemporalModel
from temporalio.contrib.google_adk_agents.workflow import activity_tool
from temporalio.workflow import ActivityConfig

# Temporal Activity を定義します

@activity.defn
async def get_weather(city: str) -> str:
    """都市の現在の天気を取得します。"""
    # ここに天気 API 呼び出しを追加します
    return f"72°F and sunny in {city}"

# Activity を ADK ツールとしてラップします。このツールには memoize、retry、timeout が適用されます。
weather_tool = activity_tool(
    get_weather,
    start_to_close_timeout=timedelta(seconds=30),
    retry_policy=RetryPolicy(maximum_attempts=3),
)

# エージェントを使用します
agent = Agent(
    name="weather_agent",
    model=TemporalModel(
      "gemini-2.5-pro",
      activity_config=ActivityConfig(summary="Weather Agent")),
    tools=[weather_tool],
)

# エージェントを Workflow に入れて、永続実行を与えます。

@workflow.defn
class WeatherAgentWorkflow:
    @workflow.run
    async def run(self, user_message: str) -> str:
        # テスト用です。本番では Runner() を使います
        runner = InMemoryRunner(agent=agent, app_name="weather_app")
        session = await runner.session_service.create_session(
            user_id="user", app_name="weather_app"
        )
        result = ""
        async with aclosing(runner.run_async(
            user_id="user",
            session_id=session.id,
            new_message=types.Content(
                role="user", parts=[types.Part.from_text(text=user_message)]
            ),
        )) as events:
            async for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            result = part.text
        return result
```

**2. ワーカーを構成して起動する**

`GoogleAdkPlugin` を使ってワーカーを構成すると、分散システム上の Workflow で ADK を実行できるようになります:

```python
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.contrib.google_adk_agents import GoogleAdkPlugin

async def main():
    client = await Client.connect(
        "localhost:7233",
        plugins=[GoogleAdkPlugin()]
    )

    worker = Worker(
        client,
        task_queue="my-agent-task-queue",
        workflows=[WeatherAgentWorkflow],
        activities=[get_weather],
    )
    await worker.run()

asyncio.run(main())
```

**3. Workflow 実行を開始する**

```python
import asyncio
from temporalio.client import Client
from temporalio.contrib.google_adk_agents import GoogleAdkPlugin

async def start():
    client = await Client.connect(
        "localhost:7233",
        plugins=[GoogleAdkPlugin()]
    )
    result = await client.execute_workflow(
        WeatherAgentWorkflow.run,
        "What's the weather in San Francisco?",
        id="weather-agent-1",
        task_queue="my-agent-task-queue",
    )
    print(result)

asyncio.run(start())
```


### MCP ツールを使う

[MCP](/mcp/) ツールを Temporal Activity として実行します:

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from temporalio.client import Client
from temporalio.contrib.google_adk_agents import (
    GoogleAdkPlugin,
    TemporalModel,
    TemporalMcpToolSet,
    TemporalMcpToolSetProvider,
)

# 必要に応じて Temporal が MCPToolset をインスタンス化できるよう、ファクトリを定義します。
toolset_provider = TemporalMcpToolSetProvider(
    "my-tools",
    lambda _: McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
            ),
        ),
    ),
)

# ツールセットプロバイダーを使ってクライアントを構成します。
client = await Client.connect(
    "localhost:7233",
    plugins=[GoogleAdkPlugin(toolset_providers=[toolset_provider])]
)

# Agent を宣言するとき( @workflow.run の内側)に、名前でツールセットを参照します。
agent = Agent(
    name="tool_agent",
    model=TemporalModel("gemini-2.5-pro"),
    tools=[TemporalMcpToolSet("my-tools")],
)
```

## 動作の仕組み

このプラグインは、ADK エージェントが Temporal Workflow コード内で決定論的に実行されることを保証し、
堅牢な復旧のために入力と出力をシリアライズして記録します。たとえば:

- **LLM 呼び出し**は `TemporalModel` を通じて Temporal Activity として実行されます。呼び出しが失敗したりワーカーがクラッシュしたりしても、Temporal は最後に成功したステップから再試行または再生し、耐障害性を高めてトークン消費を抑えます。
- **非決定的な操作**(`time.time()`、`uuid.uuid4()` など)は、Workflow コードで実行されると Temporal の決定論的な代替(`workflow.now()`、`workflow.uuid4()`)に自動的に置き換えられます(Activity コードでは対象外です)。
- **ADK および Gemini モジュール**は、自動 passthrough 付きの Temporal [sandbox](https://docs.temporal.io/develop/python/sandbox-environment) 環境向けに構成されます。
- **Pydantic シリアライゼーション**は ADK のデータ型に対して自動的に構成されます。

## 追加機能

| 機能 | 説明 |
| --- | --- |
| 耐久性のあるツール実行 | `activity_tool` はツール関数を Activity としてラップし、長時間実行ツール、自動再試行、ハートビートをサポートします |
| MCP ツールサポート | `TemporalMcpToolSet` は、完全なイベント伝播を維持しながら MCP ツールを Activity として実行します |
| Human-in-the-loop | Agent Workflow は [Signals](https://docs.temporal.io/signals) と [Updates](https://docs.temporal.io/messages#updates) を待機して人間の入力を受け付けられ、クライアントはそれを送って Agent を再開できます |
| 決定論的ランタイム | `GoogleAdkPlugin` は非決定的な呼び出しを Temporal-safe な代替に置き換えます |
| デバッグしやすさ | すべての LLM 呼び出しとツール実行が Temporal UI で Activity として見えるため、障害のデバッグが容易です |
| 可観測性 | OpenTelemetry を使ってお好みの可観測性ソリューションと連携でき、プロセス間 span はクラッシュに対して耐性があります |
| 安全なバージョニング | [Temporal Worker Versioning](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning) を使って、進行中の実行を妨げずに新しいエージェントバージョンをデプロイできます |
| マルチエージェントオーケストレーション | Workflow 内で複数のエージェントを構成したり、[Child Workflows](https://docs.temporal.io/child-workflows) や [Nexus](https://docs.temporal.io/nexus) を使ってより複雑なユースケースに拡張できます |


## 追加資料

- [Temporal Python SDK ドキュメント](https://docs.temporal.io/develop/python) - Temporal Python SDK の完全リファレンス
- [PyPI の Temporal Python SDK](https://pypi.org/project/temporalio/) - Python パッケージ
- [Temporal Cloud](https://temporal.io/cloud) - マネージド Temporal サービス
- [Temporal で ambient agent をオーケストレーションする](https://temporal.io/blog/orchestrating-ambient-agents-with-temporal) - 長時間実行エージェントパターンに関するブログ記事
