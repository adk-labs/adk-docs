---
catalog_title: Dapr
catalog_description: 人間の承認と安全なバージョニングを備えた durable、long-running、self-recovering エージェント
catalog_icon: /integrations/assets/dapr.png
catalog_tags: ["resilience"]
---

# ADK 向け Dapr プラグイン

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Dapr](https://dapr.io) は、ADK エージェントを障害に強くする分散 workflow
orchestration engine です。LLM 呼び出しとツール実行は、自動リトライと復旧を
備えた Dapr
[Workflow](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-overview/)
activity として実行されます。何かが失敗すると、エージェントは中断したまさにその
場所から自動的に再開します。

## ユースケース

Dapr プラグインはエージェントに次の機能を提供します。

- **Durable execution:** 進行状況を失いません。エージェントが crash または stall
  した場合、Dapr は最後に成功した activity から自動復旧し、[手動再開](/ja/runtime/resume/)
  は不要です。
- **組み込みリトライと backoff:** LLM provider や tool API の一時的な障害を処理する
  ため、exponential backoff 付きの構成可能な [retry
  policy](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#retry-policies)
  を提供します。
- **Long-running と ambient agent:** Dapr の persistent state store を基盤に、数時間、
  数日、または無期限に実行されるエージェントとツールをサポートします。
- **ポータブルなインフラ:** エージェントコードを変更せずに、Redis、GCP Firestore、
  PostgreSQL、DynamoDB、Cosmos DB など 15 以上のデータベースと [さらに多くの state
  store](https://docs.dapr.io/reference/components-reference/supported-state-stores/)を
  差し替えられます。Dapr の pluggable component model により、ローカル開発から
  任意のクラウドへ移行できます。
- **可観測性とデバッグ:** Dapr workflow API でエージェント実行の各ステップを調査し、
  Dapr の組み込み [OpenTelemetry
  integration](https://docs.dapr.io/operations/observability/tracing/tracing-overview/)
  を通じて trace と metric を出力します。

## 前提条件

- Python 3.11+
- [Gemini API キー](https://aistudio.google.com/app/api-keys)、または任意の
  [サポート対象モデル](/ja/agents/models/)
- Dapr CLI と runtime のインストール（[インストール
  ガイド](https://docs.dapr.io/getting-started/install-dapr-cli/)）
- workflow persistence 用に構成された Dapr [state store
  component](https://docs.dapr.io/reference/components-reference/supported-state-stores/)

## インストール

Dapr 用の [Diagrid Agent package](https://pypi.org/project/diagrid/) をインストールします。
このパッケージには ADK extension が含まれています。

```bash
pip install diagrid
```

Dapr を初期化します。

```bash
dapr init
```

## エージェントでの使用

### 基本設定

この統合は、各 LLM 呼び出しと各ツール実行が durable Dapr Workflow activity として
実行されるように ADK エージェントをラップします。runner は workflow 登録を処理し、
Dapr workflow runtime を起動し、エージェントを呼び出すための async interface を
公開します。

**エージェントと runner を定義**

通常どおり ADK エージェントを作成し、`DaprWorkflowAgentRunner` に渡します。

```python
import asyncio
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from diagrid.agent.adk import DaprWorkflowAgentRunner


def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The name of the city to get weather for.

    Returns:
        A string describing the weather.
    """
    # Your weather API call here
    return f"72°F and sunny in {city}"


# Define the ADK agent
agent = LlmAgent(
    name="weather_agent",
    model="gemini-flash-latest",
    instruction="You are a helpful assistant that can check the weather.",
    tools=[FunctionTool(get_weather)],
)


async def main():
    # Wrap the agent so each tool call runs as a durable Dapr activity
    runner = DaprWorkflowAgentRunner(
        agent=agent,
        name="weather-agent",
        max_iterations=10,
    )

    # Start the Dapr Workflow runtime
    runner.start()

    try:
        async for event in runner.run_async(
            user_message="What's the weather in San Francisco?",
            session_id="session-001",
        ):
            if event["type"] == "workflow_completed":
                print(event["final_response"])
    finally:
        runner.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
```

**Dapr でエージェントを実行**

Dapr Workflow は lightweight sidecar と構成済み state store を使用します。次の
コマンドで Dapr をローカル実行し、エージェントを一緒に起動します。

```bash
dapr run --app-id weather-agent -- python3 agent.py
```

!!! note

    デフォルトでは、Dapr は Dapr とともにインストールされた Redis component を
    使用します。場所は `~/.dapr/components/statestore.yaml` です。使用する state
    store を変更するには [supported state
    stores](https://docs.dapr.io/reference/components-reference/supported-state-stores/)
    を参照してください。

### Crash recovery

エージェントをホストするプロセスが実行途中で crash した場合、アプリが再起動すると
Dapr は最後に成功した activity から workflow を自動再開します。カスタム replay
ロジックは不要です。

```python
# First run: process crashes after tool 1 completes.
# Second run: Dapr automatically resumes and executes tools 2 and 3.
runner = DaprWorkflowAgentRunner(agent=agent, name="sequential-agent")
runner.start()

async for event in runner.run_async(
    user_message="Run the three-step pipeline.",
    session_id="pipeline-001",
):
    if event["type"] == "workflow_completed":
        print(event["final_response"])
```

`session_id` と workflow instance ID が安定しているため、同じアプリを Dapr とともに
再起動すると、sidecar が進行中の workflow を引き継いで完了まで進めます。手動再開は
不要です。

## 仕組み

プラグインは ADK エージェントループを Dapr Workflow に変換し、各ステップを
checkpoint、retry、自動 replay 可能にします。

- **LLM 呼び出し**は Dapr Workflow
  [activity](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#workflow-activities)
  として実行されます。呼び出しが失敗したり worker が crash したりすると、Dapr は
  構成済み retry policy に従ってリトライするか、最後に成功した activity から
  workflow を replay し、resilience を高め token spend を削減します。
- **ツール実行**は、ツール呼び出しごとに 1 つの独立した activity として実行されます。
  workflow は Dapr の `when_all` primitive を使って並列ツール呼び出しを fan out し、
  完了を待ってから LLM を再呼び出しします。
- **Workflow state**（message、tool call、tool result）は各 activity の後に
  serialize され、構成済み Dapr state store に保存されます。そのため、state store
  にアクセスできる任意の replica が実行を引き継げます。
- **Deterministic orchestration:** `agent_workflow` 関数には deterministic control
  flow のみが含まれます。すべての side effect（LLM 呼び出し、ツール呼び出し）は
  activity 内で発生し、これは replay safety のために Dapr Workflow が要求する
  モデルです。

## 機能

| Capability | Description |
| --- | --- |
| Durable tool execution | 各 ADK ツールが Dapr Workflow activity として実行され、失敗時には自動 retry、backoff、replay が適用されます |
| Parallel tool calls | 単一 LLM 応答の複数ツール呼び出しが activity として同時に dispatch され、次の LLM ステップの前に join されます |
| Portable state stores | コード変更なしで Dapr component により Redis、GCP Firestore、PostgreSQL、Cosmos DB など複数の state store を切り替えます |
| Long-running agents | workflow は数時間、数日、または無期限に実行でき、state は完了まで Dapr state store に保持されます |
| Observability | すべての LLM 呼び出しとツール実行は workflow activity であり、Dapr の OpenTelemetry integration で trace し、workflow API で調査できます |
| Kubernetes-native | Dapr sidecar injection を使用して、同じエージェントをコード変更なしで Kubernetes にデプロイします |

## 追加リソース

- [Dapr Workflow documentation](https://docs.dapr.io/developing-applications/building-blocks/workflow/) - Dapr workflow building block の完全な reference
- [Diagrid Agent SDK on GitHub](https://github.com/diagridio/python-ai) - Dapr ADK 統合のソースコード
- [Dapr Community Discord](https://bit.ly/dapr-discord) - 質問、バグ報告、コミュニティでの議論
- [Supported state stores](https://docs.dapr.io/reference/components-reference/supported-state-stores/) - Dapr Workflow と互換性のある state store component 一覧
