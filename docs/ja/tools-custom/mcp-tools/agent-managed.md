# サブエージェントによる MCP の管理

**直接的な MCP ツール統合**を使用してエージェントを外部リソースに接続する方法と、**エージェント公開 MCP サーバー**を介して外部クライアントにエージェントを提供する方法については既に説明しました。ただし、ADK のマルチエージェント機能が成長するにつれて、単一モデルのコンテキスト ウィンドウに過負荷をかけることなく、複雑なマルチステップの推論を分離する方法が必要になる場合があります。

## はじめに

```python
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# ステップ 1: MCP 接続を初期化する
mcp_connection = StdioConnectionParams(
    server_params=StdioServerParameters(
        command='npx',
        args=['-y', '@modelcontextprotocol/server-postgres', 'postgres://user:pass@localhost:5432/db'],
    )
)

# ステップ 2: 子サブエージェントを作成し、McpToolset をアタッチする
database_sub_agent = LlmAgent(
    name="database_sub_agent",
    model="gemini-flash-latest",
    description="Delegates tasks to a database specialist...",
    instruction="You are a SQL expert...",
    tools=[McpToolset(connection_params=mcp_connection, tool_filter=['query_db', 'list_tables'])]
)
database_tool = AgentTool(agent=database_sub_agent)


# ステップ 3: プライマリ ルート エージェントに AgentTool を提供する
root_agent = LlmAgent(
    name="primary_orchestrator",
    model="gemini-pro-latest",
    instruction="You are the main assistant. You have access to specialized agents. Delegate data retrieval tasks to your database tool.",
    tools=[database_tool]
)
```

## アーキテクチャの役割とツールの適応
ADK フレームワークでは、`AgentTool` は `LlmAgent` をラップして、親オーケストレーターにネイティブ ツールとして公開します。子エージェントは `McpToolset` 経由でツールを使用します。このツールセットは、基盤となる MCP サーバーに接続し（`list_tools` 経由）、外部 MCP ツール定義を ADK 互換の `BaseTool` インスタンスに変換し、すべての実行呼び出し（`call_tool`）を非同期にプロキシします。

## ツールのスコープ設定と認知的フィルタリング (`tool_filter`)
特化したサブエージェントに `McpToolset` を割り当てる場合、`tool_filter` パラメータを使用して、そのエージェントで使用可能にする具体的なツールを制限できます。
* **認知的集中:** 'read_file' や 'list_directory' など、サブエージェントの目的に関連する特定のアクションのみを公開します。
* **セキュリティとサンドボックス化:** MCP サーバーによって公開される危険なツールへの意図しないアクセスを防ぎ、予測できない入力から実行面を隔離します。

## 接続転送モード
サブエージェントの `McpToolset` は、デプロイ アーキテクチャに応じて、次の 2 つのプライマリ接続モードのいずれかで構成する必要があります。
* **ローカル サブプロセス (`StdioConnectionParams`):** 標準入出力を介して通信するローカル実行可能ファイルまたはプロセス（`npx` または `python` など）を生成します。自己完結型のシングルコンテナ環境に最適です。
* **リモート ネットワーク (`StreamableHTTPConnectionParams` / `SseConnectionParams`):** `X-Goog-Api-Key` や `Authorization` などのヘッダーを使用して HTTP/SSE 経由で接続します。スケーラブル、マルチテナント、または個別に管理される MCP バックエンドに最適です。

## 定義とライフサイクル ルール
* **本番環境向けの同期インスタンス化:** Cloud Run、GKE、Agent Engine などのマルチエージェント設定をデプロイする場合、サブエージェントとその `McpToolset` は両方とも、非同期ファクトリ関数の内部ではなく、`agent.py` 内で同期的にインスタンス化する必要があります。
* **セッションの永続化と復元:** `McpToolset` は `getstate` および `setstate` を介したシリアル化をサポートしています。セッション状態はライフサイクル イベント全体で保持されますが、エージェント プロセスが復元されると、MCP ソケット/stdio 接続は動的に再初期化されます。
* **クリーンアップ管理:** カスタム ランタイムで `adk web` の外部で実行する場合、`toolset.close()` または exit stack を介した明示的な終了処理により、バックグラウンド サーバーのサブプロセスとネットワーク接続が正常に終了することが保証されます。
