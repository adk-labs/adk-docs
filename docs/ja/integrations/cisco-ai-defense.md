---
catalog_title: Cisco AI Defense
catalog_description: エージェントのプロンプトとツール呼び出しを監視またはブロックするセキュリティ ガードレール
catalog_icon: /integrations/assets/cisco-ai-defense.png
---


# ADK 用 Cisco AI Defense プラグイン

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Cisco AI
Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html)
ランタイム ガードレールを提供するエンタープライズ AI セキュリティ プラットフォームです。
プロンプトインジェクション、データ漏洩、有害な脅威などの脅威から保護します。
内容。 [ADK
plugin](https://github.com/cisco-ai-defense/ai-defense-google-adk) は、
これらのガードレールは ADK Runner ライフサイクルに直接組み込まれます。プロンプトを検査し、
モデル応答とツール呼び出しを実行し、構成可能な条件に基づいてそれらを許可またはブロックします。
セキュリティポリシー。

## 使用例

- **モデル呼び出しのランタイム保護**: モデルの前にユーザー プロンプトを検査します
  生成後に呼び出しとモデル出力を実行し、ポリシーに基づいて許可またはブロックします
  (`monitor` または `enforce`)。
- **ツールおよび MCP 呼び出しの検査**: 実行前にツール呼び出しリクエストを検査します。
  および実行後のツールの応答を監視し、安全でないツールの動作をブロックします。
  明確なメタデータを備えた `enforce` モード。
- **監査可能な意思決定トレースとアラート**: 意思決定コンテキスト (アクション、
  重大度、分類、request_id/event_id)、オプションでトリガー
  モニタリングとインシデント対応のための `on_violation` コールバック。

## 前提条件

- [Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html) アカウントと API キー
- Python >= 3.10
- [ADK](https://adk.dev) >= 1.0.0

## インストール

```bash
pip install cisco-aidefense-google-adk
```

`AI_DEFENSE_API_KEY` 環境変数 (および `AI_DEFENSE_MCP_API_KEY`) を設定します。
工具検査用）。

## エージェントと一緒に使用する

### クイックスタート

次の 1 行で Cisco AI Defense を任意の ADK エージェントに追加します。

```python
from aidefense_google_adk import defend

agent = defend(agent, mode="enforce")
```

または、アプリ全体のプラグインを取得します。

```python
from aidefense_google_adk import defend

plugin = defend(mode="enforce")
app = App(name="my_app", root_agent=agent, plugins=[plugin])
```

### グローバルプラグイン

`CiscoAIDefensePlugin` を使用して、インスペクションをすべてのエージェントにグローバルに適用します。
ランナー:

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

### エージェントごとのコールバック

`make_aidefense_callbacks` を使用して、検査を特定のエージェントに接続します。

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

モード |行動
---- | --------
`monitor` |すべてのトラフィックを検査し、違反をログに記録し、ブロックしない (デフォルト)
`enforce` |すべてのトラフィックを検査し、ポリシーに違反するリクエスト/レスポンスをブロックします。
`off` |検査を完全にスキップする

モードはグローバルまたはチャネルごとに設定できます。

```python
CiscoAIDefensePlugin(
    mode="monitor",      # default for both
    llm_mode="enforce",  # override for LLM only
    mcp_mode="off",      # override for tools only
)
```

## 違反コールバック

`on_violation` コールバックを使用して、すべての違反の通知を受け取ります。
`monitor` モードと `enforce` モードの両方:

```python
def handle_violation(result):
    print(f"Violation: {result.action} / {result.severity}")

CiscoAIDefensePlugin(
    mode="monitor",
    on_violation=handle_violation,
)
```

## 再試行とフェールオープンのサポート

指数関数的バックオフ、フェールオープン/フェールクローズのセマンティクスを使用した自動再試行の場合、
および構造化された `Decision` オブジェクトの場合は、`AgentsecPlugin` バリアントを使用します。

```python
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

またはエージェントごとのレベルで:

```python
from aidefense_google_adk import make_agentsec_callbacks

cbs = make_agentsec_callbacks(mode="enforce", fail_open=True)
cbs.apply_to(agent)
```

## 追加のリソース

- [GitHub Repository](https://github.com/cisco-ai-defense/ai-defense-google-adk)
- [PyPI Package](https://pypi.org/project/cisco-aidefense-google-adk/)
- [Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html)
- [cisco-aidefense-sdk on PyPI](https://pypi.org/project/cisco-aidefense-sdk/)
