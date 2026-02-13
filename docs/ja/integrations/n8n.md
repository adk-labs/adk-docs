---
catalog_title: n8n
catalog_description: 自動化ワークフローをトリガーし、アプリ接続とデータ処理を行います
catalog_icon: /adk-docs/integrations/assets/n8n.png
catalog_tags: ["mcp"]
---

# ADK 向け n8n MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[n8n MCP Server](https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/) は
ADK エージェントを拡張可能なワークフロー自動化ツール [n8n](https://n8n.io/) に接続します。
この連携により、エージェントは自然言語インターフェースから
n8n インスタンスへ安全に接続し、ワークフローの検索、確認、トリガーを実行できます。

!!! note "代替: ワークフローレベル MCP サーバー"

    このページの設定ガイドは **インスタンスレベル MCP アクセス**を対象とし、
    有効化されたワークフローの中央ハブへエージェントを接続します。
    代替として、
    [MCP Server Trigger node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/)
    を使って **単一ワークフロー**を独立した MCP サーバーとして動作させることもできます。
    この方法は、特定のサーバー挙動を設計したい場合や、
    1 つのワークフローに限定したツール公開をしたい場合に有効です。

## ユースケース

- **複雑なワークフロー実行**: n8n で定義された多段ビジネスプロセスを
  エージェントから直接トリガーします。
  分岐、ループ、エラーハンドリングにより一貫性を確保できます。

- **外部アプリ接続**: サービスごとにカスタムツールを書くことなく、
  n8n の事前構築済み連携を利用できます。
  API 認証、ヘッダー、ボイラープレートの管理負担を減らせます。

- **データ処理**: 複雑なデータ変換を n8n ワークフローにオフロードします。
  たとえば自然言語を API 呼び出しへ変換したり、Web ページをスクレイプして要約したり、
  必要に応じて Python/JavaScript ノードで精密に整形できます。

## 前提条件

- 稼働中の n8n インスタンス
- 設定で MCP アクセスを有効化
- 有効な MCP アクセストークン

詳細設定手順は
[n8n MCP documentation](https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/)
を参照してください。

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        N8N_INSTANCE_URL = "https://localhost:5678"
        N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="n8n_agent",
            instruction="Help users manage and execute workflows in n8n",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "supergateway",
                                "--streamableHttp",
                                f"{N8N_INSTANCE_URL}/mcp-server/http",
                                "--header",
                                f"authorization:Bearer {N8N_MCP_TOKEN}"
                            ]
                        ),
                        timeout=300,
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        N8N_INSTANCE_URL = "https://localhost:5678"
        N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="n8n_agent",
            instruction="Help users manage and execute workflows in n8n",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url=f"{N8N_INSTANCE_URL}/mcp-server/http",
                        headers={
                            "Authorization": f"Bearer {N8N_MCP_TOKEN}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const N8N_INSTANCE_URL = "https://localhost:5678";
        const N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "n8n_agent",
            instruction: "Help users manage and execute workflows in n8n",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "supergateway",
                            "--streamableHttp",
                            `${N8N_INSTANCE_URL}/mcp-server/http`,
                            "--header",
                            `authorization:Bearer ${N8N_MCP_TOKEN}`,
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const N8N_INSTANCE_URL = "https://localhost:5678";
        const N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "n8n_agent",
            instruction: "Help users manage and execute workflows in n8n",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: `${N8N_INSTANCE_URL}/mcp-server/http`,
                    header: {
                        Authorization: `Bearer ${N8N_MCP_TOKEN}`,
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

Tool | Description
---- | -----------
`search_workflows` | 利用可能ワークフローを検索
`execute_workflow` | 特定ワークフローを実行
`get_workflow_details` | ワークフローメタデータとスキーマ情報を取得

## 設定

ワークフローをエージェントから利用可能にするには、次の条件を満たす必要があります:

- **有効化されていること**: ワークフローが n8n で有効化されていること。

- **対応トリガーを含むこと**: Webhook、Schedule、Chat、Form トリガーノードを含むこと。

- **MCP 有効化**: ワークフロー設定で "Available in MCP" を有効化するか、
  ワークフローカードメニューで "Enable MCP access" を選択すること。

## 追加リソース

- [n8n MCP Server Documentation](https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/)
