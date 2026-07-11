---
catalog_title: Perseus Context
catalog_description: ADK エージェント向けに、決定論的でワークスペースを認識するコンテキストをコンパイルします
catalog_icon: /integrations/assets/perseus.svg
catalog_tags: ["data", "mcp"]
---

# ADK용 Perseus Context 統合

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[`adk-perseus-context`](https://github.com/Perseus-Computing-LLC/adk-perseus-context) 統合は、決定論的にコンパイルされたコンテキストを ADK エージェントのシステム指示（system instruction）に挿入します。これはオープンソースのコンテキストコンパイラである [Perseus](https://github.com/Perseus-Computing-LLC/perseus) によって動作します。Perseus は、検索インデックスやエンベディング、余分な LLM 往復なしに、推論時に `@file`、`@search`、および `@memory` などのディレクティブを 1 つのバイトスタティックなコンテキスト文字列に解決します。すべてがローカルで動作します。

Perseus はコンテキストコンパイラであり、メモリや RAG バックエンドではありません。永続的なセッション間メモリについては、その姉妹サービスである [Perseus Vault](/ja/integrations/perseus-vault/) とペアリングして使用してください。

## ユースケース

- **決定論的なコンテキスト構築**: 同じ入力からは常に同じコンテキストがコンパイルされ、バイト単位で同一のビルドが得られ、クエリごとの取得のばらつきはありません。

- **ワークスペース認識エージェント**: `@file`、`@include`、`@search`、および `@memory` ディレクティブを解決して、エージェントが現在のプロジェクトファイルや状態を確認できるようにします。

- **インデックス不要のローカルコンテキスト**: ベクトルストア、エンベディング、クラウドは不要です。コンテキストはエージェントを実行するマシン上でコンパイルされます。

- **固定サイズでの完全なカバレッジ**: top-k スライスではなく、宣言した正確なコンテキストを取り込みます。

## 前提条件

- Python 3.10+
- `google-adk>=1.14.0`
- `perseus-ctx>=1.0.10`（`adk-perseus-context` のインストールとともに自動的にインストールされます）

## インストール

```bash
pip install adk-perseus-context
```

## エージェントとの連携

コンパイルされた Perseus コンテキストを挿入する方法は 2 つあります。`Runner` 内のすべてのエージェントで共有されるコンテキストにはプラグイン（plugin）を使用し、単一のエージェントにはコールバック（callback）を使用します。`source` は `.perseus` ファイルへのパス、または `@perseus` で始まるインライン文字列です。

### ランナー全体（プラグイン）

```python
from adk_perseus_context import PerseusContextPlugin
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="Help the user.",
)

app = App(
    name="perseus_app",
    root_agent=agent,
    plugins=[PerseusContextPlugin("context.perseus")],
)

runner = Runner(
    app=app,
    session_service=InMemorySessionService(),
)
```

### 単一エージェント（コールバック）

```python
from adk_perseus_context import perseus_before_model_callback
from google.adk.agents import Agent

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="Help the user.",
    before_model_callback=perseus_before_model_callback("context.perseus"),
)
```

どちらの方法でも、モデル呼び出しのたびにコンパイルされたコンテキストが要求のシステム指示に追加されます（ADK の `LlmRequest.append_instructions` を使用）。Perseus が利用できないかコンパイルに失敗した場合、コンテキストが挿入されずに要求が進行し、警告がログに記録されます（デフォルトは `fail_open=True`）。

### セッションごとのコンテキスト

セッション状態を介してセッションごとにソースをオーバーライドします。これは、各ユーザーまたはタスクが異なるワークスペースやディレクティブセットを対象とする場合に便利です。非同期関数内でセッションを作成します。

```python
session = await runner.session_service.create_session(
    app_name="perseus_app",
    user_id="user",
    state={
        "_perseus_source": "@perseus\n@file AGENTS.md\n@memory deployment",
        "_perseus_workspace": "/path/to/project",
    },
)
```

## MCP サーバーとしての使用（オプション）

Perseus は、そのディレクティブをツールとして公開する MCP サーバーも提供しているため、プラグインの代わりに（またはプラグインと併せて）ADK の `McpToolset` を介して利用することもできます。

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

perseus_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="perseus",
            args=["mcp", "serve", "--workspace", "."],
        )
    )
)

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="Use Perseus tools to read workspace context.",
    tools=[perseus_tools],
)
```

## プラグインリファレンス

| エントリポイント | スコープ | 説明 |
|---|---|---|
| `PerseusContextPlugin(source)` | ランナー全体 | すべてのエージェントのモデル要求にコンパイルされたコンテキストを挿入する |
| `perseus_before_model_callback(source)` | 単一エージェント | コンパイルされたコンテキストを挿入する `before_model_callback` |
| `_perseus_source` / `_perseus_workspace` | セッション状態 | セッションごとのソースとワークスペースのオーバーライド |

## 比較

| アプローチ | インデックス / 埋め込み | 追加のモデル呼び出し | 出力の安定性 | カバレッジ |
|---|---|---|---|---|
| 汎用的なコンテキストダンプ | なし | なし | 安定 | プロンプト内のすべて |
| RAG / ベクトル検索 | 必須 | クエリ埋め込み | クエリによって異なる | 上位 k 件の結果 |
| Perseus コンパイル | なし | なし | バイト単位で同一 | 宣言されたすべて |

## リソース

- [GitHub の adk-perseus-context](https://github.com/Perseus-Computing-LLC/adk-perseus-context)
- [PyPI の adk-perseus-context](https://pypi.org/project/adk-perseus-context/)
- [Perseus (コンテキストエンジン)](https://github.com/Perseus-Computing-LLC/perseus)
- [Perseus Vault Memory 統合ガイド](/ja/integrations/perseus-vault/)
