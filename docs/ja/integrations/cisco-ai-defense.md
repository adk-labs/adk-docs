---
catalog_title: Cisco AI Defense
catalog_description: エージェントのプロンプトとツール呼び出しを監視またはブロックするセキュリティガードレール
catalog_icon: /integrations/assets/cisco-ai-defense.png
---

# ADK 向け Cisco AI Defense プラグイン

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html) は、プロンプトインジェクション、データ漏洩、有害なコンテンツなどの脅威から保護するランタイムガードレールを提供するエンタープライズ AI セキュリティプラットフォームです。[ADK プラグイン](https://github.com/cisco-ai-defense/ai-defense-google-adk)は、これらのガードレールを ADK Runner のライフサイクルに直接統合します。プロンプト、モデル応答、およびツール呼び出しを検査し、構成可能なセキュリティポリシーに基づいて許可またはブロックします。

## ユースケース

- **モデル呼び出しのランタイム保護**: モデル呼び出し前のユーザープロンプトと生成後のモデル出力を検査し、ポリシー（`monitor` または `enforce`）に基づいて許可またはブロックします。
- **ツールおよび MCP 呼び出しの検査**: 実行前のツール呼び出しリクエストと実行後のツール応答を検査し、`enforce` モードでは明確なメタデータとともに安全でないツールの動作をブロックします。
- **監査可能な判定トレースとアラート**: 判定コンテキスト（アクション、重大度、分類、`request_id`/`event_id`）を記録し、任意でモニタリングやインシデント対応のための `on_violation` コールバックをトリガーします。

## 前提条件

- [Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html) アカウントと API キー
- Python >= 3.10
- [ADK](https://adk.dev) >= 1.0.0

## インストール

```bash
pip install cisco-aidefense-google-adk
```

`AI_DEFENSE_API_KEY` 環境変数（およびツール検査用の `AI_DEFENSE_MCP_API_KEY`）を設定します。

## エージェントでの使用

### クイックスタート

次の 1 行で任意の ADK エージェントに Cisco AI Defense を追加できます。

```python
from google.adk.apps import App

from aidefense_google_adk import defend

agent = defend(agent, mode="enforce")
```

または、アプリ全体向けのプラグインを取得します。

```python
from google.adk.apps import App

from aidefense_google_adk import defend

plugin = defend(mode="enforce")
app = App(name="my_app", root_agent=agent, plugins=[plugin])
```

### グローバルプラグイン

`CiscoAIDefensePlugin` を使用すると、`Runner` 内のすべてのエージェントに対して検査をグローバルに適用できます。

```python
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from aidefense_google_adk import CiscoAIDefensePlugin

agent = LlmAgent(
    model="gemini-flash-latest",
    name="assistant",
    instruction="You are a helpful assistant.",
)

app = App(
    name="my_app",
    root_agent=agent,
    plugins=[
        CiscoAIDefensePlugin(mode="enforce"),
    ],
)
runner = Runner(app=app, session_service=InMemorySessionService())
```

### エージェント単位のコールバック

`make_aidefense_callbacks` を使用して、特定のエージェントに検査を組み込みます。

```python
from google.adk.agents import LlmAgent
from aidefense_google_adk import make_aidefense_callbacks

cbs = make_aidefense_callbacks(mode="enforce")

agent = LlmAgent(
    model="gemini-flash-latest",
    name="assistant",
    instruction="You are a helpful assistant.",
)
cbs.apply_to(agent)  # wires all 4 callbacks
```

## モード

プラグインは 3 つの動作モードをサポートしています。

モード | 動作
---- | --------
`monitor` | すべてのトラフィックを検査して違反をログに記録し、ブロックは行いません（デフォルト）
`enforce` | すべてのトラフィックを検査し、ポリシーに違反するリクエスト/レスポンスをブロックします
`off` | 検査を完全にスキップします

モードはグローバルまたはチャネルごとに設定できます。

```python
CiscoAIDefensePlugin(
    mode="monitor",      # default for both
    llm_mode="enforce",  # override for LLM only
    mcp_mode="off",      # override for tools only
)
```

## 違反コールバック

`on_violation` コールバックを使用すると、`monitor` モードと `enforce` モードの両方ですべてのポリシー違反の通知を受け取れます。

```python
def handle_violation(result):
    print(f"Violation: {result.action} / {result.severity}")

CiscoAIDefensePlugin(
    mode="monitor",
    on_violation=handle_violation,
)
```

## 再試行とフェイルオープンのサポート

指数バックオフによる自動再試行、フェイルオープン/フェイルクローズのセマンティクス、および構造化された `Decision` オブジェクトが必要な場合は、`AgentsecPlugin` バリアントを使用します。

```python
from google.adk.apps import App

from aidefense_google_adk import AgentsecPlugin

app = App(
    name="my_app",
    root_agent=agent,
    plugins=[
        AgentsecPlugin(
            mode="enforce",
            fail_open=True,
            retry_total=3,
            retry_backoff=0.5,
        ),
    ],
)
```

またはエージェント単位で適用することもできます。

```python
from aidefense_google_adk import make_agentsec_callbacks

cbs = make_agentsec_callbacks(mode="enforce", fail_open=True)
cbs.apply_to(agent)
```

## 追加リソース

- [GitHub リポジトリ](https://github.com/cisco-ai-defense/ai-defense-google-adk)
- [PyPI パッケージ](https://pypi.org/project/cisco-aidefense-google-adk/)
- [Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html)
- [PyPI 上の cisco-aidefense-sdk](https://pypi.org/project/cisco-aidefense-sdk/)
