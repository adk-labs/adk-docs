---
catalog_title: Asana
catalog_description: チームコラボレーションのためにプロジェクト、タスク、目標を管理します
catalog_icon: /integrations/assets/asana.png
catalog_tags: ["mcp"]
---

# ADK 向け Asana MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Asana MCP Server](https://developers.asana.com/docs/using-asanas-mcp-server) は
ADK エージェントを [Asana](https://asana.com/) のワークマネジメント
プラットフォームに接続します。この連携により、エージェントは
自然言語でプロジェクト、タスク、目標、チームコラボレーションを管理できます。

## ユースケース

- **プロジェクト状況の追跡**: プロジェクト進捗のリアルタイム更新を取得し、
  ステータスレポートを確認し、マイルストーンと期限情報を取得します。

- **タスク管理**: 自然言語でタスクを作成・更新・整理します。
  エージェントにタスク割り当て、ステータス変更、優先度更新を任せられます。

- **目標のモニタリング**: Asana Goals にアクセスして更新し、
  組織全体のチーム目標と主要成果を追跡します。

## 前提条件

- ワークスペースへアクセス可能な [Asana](https://asana.com/) アカウント

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="asana_agent",
            instruction="Help users manage projects, tasks, and goals in Asana",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.asana.com/sse",
                            ]
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "asana_agent",
            instruction: "Help users manage projects, tasks, and goals in Asana",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.asana.com/sse",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    このエージェントを初めて実行すると、OAuth によるアクセス許可を要求するため
    ブラウザウィンドウが自動で開きます。または、コンソールに表示される
    認可 URL を使用することもできます。エージェントが Asana データへアクセスするには、
    このリクエストを承認する必要があります。

## 利用可能なツール

Asana の MCP サーバーにはカテゴリ別に整理された 30 以上のツールが含まれます。
ツールはエージェント接続時に自動検出されます。エージェント実行後、
トレースグラフで利用可能なツールを確認するには
[ADK Web UI](/runtime/web-interface/) を使用してください。

カテゴリ | 説明
-------- | -----------
プロジェクトの追跡 | プロジェクトの進捗状況の更新やレポートを取得します
タスク管理 | タスクを作成、更新、整理します
ユーザー情報 | ユーザーの詳細情報と割り当て状況を参照します
目標（Goals） | Asana Goals を追跡・更新します
チーム編成 | チーム構成とメンバーシップを管理します
オブジェクト検索 | Asana オブジェクト全体をすばやくインクリメンタル検索（オートコンプリート）します

## 追加リソース

- [Asana MCP Server ドキュメント](https://developers.asana.com/docs/using-asanas-mcp-server)
- [Asana MCP 連携ガイド](https://developers.asana.com/docs/integrating-with-asanas-mcp-server)
