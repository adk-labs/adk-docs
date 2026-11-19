---
catalog_title: Dapr
catalog_description: 人間の承認と安全なバージョニングを備えた、永続的かつ長時間実行可能な自己復旧型エージェント
catalog_icon: /integrations/assets/dapr.png
catalog_tags: ["resilience"]
---

# ADK 向け Dapr プラグイン

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[Dapr](https://dapr.io) は、ADK エージェントを障害に強くする分散ワークフローオーケストレーションエンジンです。LLM 呼び出しとツール実行は、自動リトライと復旧を備えた Dapr
[Workflow](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-overview/)
アクティビティとして実行されます。障害が発生しても、エージェントは中断した箇所から自動的に処理を再開します。

## ユースケース

Dapr プラグインはエージェントに次の機能を提供します。

- **永続的実行（Durable execution）:** 進行状況を失いません。エージェントがクラッシュまたは停止（ストール）した場合でも、Dapr は最後に成功したアクティビティから自動的に復旧するため、[手動再開](/ja/runtime/resume/)は不要です。
- **組み込みリトライとバックオフ:** LLM プロバイダーやツール API の一時的な障害に対処するため、指数バックオフ付きの構成可能な[リトライポリシー](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#retry-policies)を提供します。
- **長時間実行エージェントとアンビエントエージェント:** Dapr の永続ステートストアを基盤に、数時間、数日、または無期限に実行されるエージェントとツールをサポートします。
- **ポータブルなインフラ:** エージェントコードを変更せずに、Redis、GCP Firestore、PostgreSQL、DynamoDB、Cosmos DB など 15 以上のデータベースと[さらに多くのステートストア](https://docs.dapr.io/reference/components-reference/supported-state-stores/)を差し替えられます。Dapr のプラガブルなコンポーネントモデルにより、ローカル開発から任意のクラウドへそのまま移行できます。
- **可観測性とデバッグ:** Dapr ワークフロー API でエージェント実行の各ステップを検査し、Dapr 組み込みの [OpenTelemetry 統合](https://docs.dapr.io/operations/observability/tracing/tracing-overview/)を通じてトレースとメトリクスを出力します。

## 前提条件

- Python 3.11+
- [Gemini API キー](https://aistudio.google.com/app/api-keys)、または任意の
  [サポート対象モデル](/ja/agents/models/)
- Dapr CLI とランタイムのインストール（[インストールガイド](https://docs.dapr.io/getting-started/install-dapr-cli/)）
- ワークフローの永続化用に構成された Dapr [ステートストアコンポーネント](https://docs.dapr.io/reference/components-reference/supported-state-stores/)

## インストール

ADK 拡張機能が含まれている Dapr 用の [Diagrid Agent パッケージ](https://pypi.org/project/diagrid/)をインストールします。

```bash
pip install diagrid
```

Dapr を初期化します。

```bash
dapr init
```

## エージェントでの使用

### 基本設定

この統合は、各 LLM 呼び出しと各ツール実行が永続的な Dapr Workflow アクティビティとして実行されるように ADK エージェントをラップします。ランナーはワークフローの登録を処理し、Dapr ワークフローランタイムを起動して、エージェントを呼び出すための非同期インターフェースを提供します。

**エージェントとランナーを定義**

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

Dapr Workflow は軽量なサイドカーと構成済みのステートストアを使用します。次のコマンドで Dapr をローカル実行し、エージェントを一緒に起動します。

```bash
dapr run --app-id weather-agent -- python3 agent.py
```

!!! note

    デフォルトでは、Dapr とともにインストールされた Redis コンポーネント（`~/.dapr/components/statestore.yaml`）が使用されます。使用するステートストアを変更するには、[サポートされているステートストア](https://docs.dapr.io/reference/components-reference/supported-state-stores/)を参照してください。

### クラッシュリカバリ

エージェントをホストするプロセスが実行途中でクラッシュした場合でも、アプリが再起動すると Dapr は最後に成功したアクティビティからワークフローを自動再開します。カスタムのリプレイロジックは不要です。

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

`session_id` とワークフローインスタンス ID が安定しているため、同じアプリを Dapr とともに再起動すると、サイドカーが実行中のワークフローを引き継いで完了まで進めます。手動再開は不要です。

## 仕組み

このプラグインは ADK エージェントループを Dapr Workflow に変換し、各ステップでチェックポイント保存、リトライ、自動リプレイを可能にします。

- **LLM 呼び出し**は Dapr Workflow [アクティビティ](https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/#workflow-activities)として実行されます。呼び出しが失敗したりワーカーがクラッシュしたりすると、Dapr は構成済みのリトライポリシーに従ってリトライするか、最後に成功したアクティビティからワークフローをリプレイすることで、レジリエンスを高めつつトークン消費を削減します。
- **ツール実行**は、ツール呼び出しごとに 1 つの独立したアクティビティとして実行されます。ワークフローは Dapr の `when_all` プリミティブを使って並列ツール呼び出しをファンアウトし、完了を待ってから LLM を再呼び出しします。
- **ワークフロー状態**（メッセージ、ツール呼び出し、ツール結果）は各アクティビティの後にシリアライズされ、構成済みの Dapr ステートストアに保存されます。そのため、ステートストアにアクセスできる任意のレプリカが実行を引き継げます。
- **決定論的オーケストレーション:** `agent_workflow` 関数には決定論的な制御フローのみが含まれます。すべての副作用（LLM 呼び出し、ツール呼び出し）はアクティビティ内で発生します。これはリプレイの安全性を確保するために Dapr Workflow が要求するモデルです。

## 機能

| 機能 | 説明 |
| --- | --- |
| 永続的なツール実行 | 各 ADK ツールが Dapr Workflow アクティビティとして実行され、失敗時には自動リトライ、バックオフ、リプレイが適用されます |
| 並列ツール呼び出し | 単一の LLM レスポンスからの複数のツール呼び出しがアクティビティとして並行ディスパッチされ、次の LLM ステップの前に結合されます |
| ポータブルなステートストア | コードを変更せずに、Dapr コンポーネントを通じて Redis、GCP Firestore、PostgreSQL、Cosmos DB など複数のステートストアを切り替えられます |
| 長時間実行エージェント | ワークフローは数時間、数日、または無期限に実行でき、状態は完了まで Dapr ステートストアに保持されます |
| 可観測性 | すべての LLM 呼び出しとツール実行はワークフローアクティビティとして実行され、Dapr の OpenTelemetry 統合によるトレースやワークフロー API による検査が可能です |
| Kubernetes ネイティブ | Dapr のサイドカーインジェクションを使用して、同じエージェントをコード変更なしで Kubernetes にデプロイできます |

## 追加リソース

- [Dapr Workflow ドキュメント](https://docs.dapr.io/developing-applications/building-blocks/workflow/) - Dapr ワークフロービルディングブロックの完全なリファレンス
- [GitHub の Diagrid Agent SDK](https://github.com/diagridio/python-ai) - Dapr ADK 統合のソースコード
- [Dapr Community Discord](https://bit.ly/dapr-discord) - 質問、バグ報告、コミュニティでの議論
- [サポートされているステートストア](https://docs.dapr.io/reference/components-reference/supported-state-stores/) - Dapr Workflow と互換性のあるステートストアコンポーネント一覧
