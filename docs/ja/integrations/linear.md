---
catalog_title: Linear
catalog_description: 課題管理、プロジェクト追跡、開発ワークフローの効率化を行います
catalog_icon: /adk-docs/integrations/assets/linear.png
catalog_tags: ["mcp"]
---

# ADK 向け Linear MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Linear MCP Server](https://linear.app/docs/mcp) は ADK エージェントを、
プロダクト計画と開発に特化した [Linear](https://linear.app/) に接続します。
この連携により、エージェントは自然言語で課題管理、
プロジェクトサイクル追跡、開発ワークフロー自動化を実行できます。

## ユースケース

- **課題管理の効率化**: 自然言語で課題を作成・更新・整理します。
  バグ記録、タスク割り当て、ステータス更新をエージェントに任せられます。

- **プロジェクトとサイクルの追跡**: チームの進捗を即座に把握できます。
  アクティブサイクルの状態確認、マイルストーン確認、期限取得が可能です。

- **コンテキスト検索と要約**: 長い議論スレッドを素早く把握したり、
  特定仕様を見つけたりできます。エージェントはドキュメント検索や
  複雑な課題の要約を行えます。

## 前提条件

- [Linear アカウント](https://linear.app/signup) の作成
- [Linear Settings > Security & access](https://linear.app/docs/security-and-access)
  で API キーを生成 (API 認証を使う場合)

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
            name="linear_agent",
            instruction="Help users manage issues, projects, and cycles in Linear",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.linear.app/mcp",
                            ]
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

        !!! note

            このエージェントを初めて実行すると、OAuth アクセス許可のために
            ブラウザウィンドウが自動で開きます。あるいはコンソールに表示される
            認可 URL を使用できます。Linear データへアクセスするには
            この要求を承認する必要があります。

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        LINEAR_API_KEY = "YOUR_LINEAR_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="linear_agent",
            instruction="Help users manage issues, projects, and cycles in Linear",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url="https://mcp.linear.app/mcp",
                        headers={
                            "Authorization": f"Bearer {LINEAR_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

        !!! note

            このコード例は API キー認証を使います。ブラウザベースの OAuth 認証フローを
            使う場合は `headers` パラメータを削除して実行してください。

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "linear_agent",
            instruction: "Help users manage issues, projects, and cycles in Linear",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "mcp-remote", "https://mcp.linear.app/mcp"],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            このエージェントを初めて実行すると、OAuth アクセス許可のために
            ブラウザウィンドウが自動で開きます。あるいはコンソールに表示される
            認可 URL を使用できます。Linear データへアクセスするには
            この要求を承認する必要があります。

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const LINEAR_API_KEY = "YOUR_LINEAR_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "linear_agent",
            instruction: "Help users manage issues, projects, and cycles in Linear",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.linear.app/mcp",
                    header: {
                        Authorization: `Bearer ${LINEAR_API_KEY}`,
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            このコード例は API キー認証を使います。ブラウザベースの OAuth 認証フローを
            使う場合は `header` プロパティを削除して実行してください。

## 利用可能なツール

Tool | Description
---- | -----------
`list_comments` | 課題コメント一覧
`create_comment` | 課題コメント作成
`list_cycles` | プロジェクトサイクル一覧
`get_document` | ドキュメント取得
`list_documents` | ドキュメント一覧
`get_issue` | 課題取得
`list_issues` | 課題一覧
`create_issue` | 課題作成
`update_issue` | 課題更新
`list_issue_statuses` | 課題ステータス一覧
`get_issue_status` | 課題ステータス取得
`list_issue_labels` | 課題ラベル一覧
`create_issue_label` | 課題ラベル作成
`list_projects` | プロジェクト一覧
`get_project` | プロジェクト取得
`create_project` | プロジェクト作成
`update_project` | プロジェクト更新
`list_project_labels` | プロジェクトラベル一覧
`list_teams` | チーム一覧
`get_team` | チーム取得
`list_users` | ユーザー一覧
`get_user` | ユーザー取得
`search_documentation` | ドキュメント検索

## 追加リソース

- [Linear MCP Server Documentation](https://linear.app/docs/mcp)
- [Linear Getting Started Guide](https://linear.app/docs/start-guide)
