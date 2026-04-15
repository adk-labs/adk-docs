---
catalog_title: GitHub
catalog_description: コードを分析し、Issue と PR を管理し、ワークフローを自動化します
catalog_icon: /integrations/assets/github.png
catalog_tags: ["code", "mcp"]
---

# ADK 向け GitHub MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[GitHub MCP Server](https://github.com/github/github-mcp-server) は、AI ツールを
GitHub プラットフォームに直接接続します。これにより ADK エージェントは
リポジトリやコードファイルを読み取り、Issue と PR を管理し、コードを分析し、
自然言語でワークフローを自動化できます。

## ユースケース

- **リポジトリ管理:** アクセス可能なあらゆるリポジトリでコードを閲覧・検索し、
  ファイルを探し、コミットを分析し、プロジェクト構造を把握します。
- **Issue と PR の自動化:** Issue とプルリクエストを作成・更新・管理します。
  AI がバグのトリアージ、コード変更のレビュー、プロジェクトボードの維持を支援します。
- **コード分析:** セキュリティ検出結果を調査し、Dependabot アラートを確認し、
  コードパターンを理解し、コードベースに対する包括的な洞察を得ます。

## 前提条件

- GitHub で
  [Personal Access Token](https://github.com/settings/personal-access-tokens/new)
  を作成してください。詳細は
  [ドキュメント](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
  を参照してください。

## エージェントでの使用

=== "Python"

    === "リモート MCP サーバー"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="github_agent",
            instruction="ユーザーが GitHub から情報を取得するのを支援します",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url="https://api.githubcopilot.com/mcp/",
                        headers={
                            "Authorization": f"Bearer {GITHUB_TOKEN}",
                            "X-MCP-Toolsets": "all",
                            "X-MCP-Readonly": "true"
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "リモート MCP サーバー"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const GITHUB_TOKEN = "YOUR_GITHUB_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "github_agent",
            instruction: "Help users get information from GitHub",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://api.githubcopilot.com/mcp/",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${GITHUB_TOKEN}`,
                                "X-MCP-Toolsets": "all",
                                "X-MCP-Readonly": "true",
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

ツール | 説明
---- | -----------
`context` | 現在のユーザーと操作中の GitHub コンテキストに関する情報を提供するツール
`copilot` | Copilot 関連ツール（例: Copilot Coding Agent）
`copilot_spaces` | Copilot Spaces 関連ツール
`actions` | GitHub Actions ワークフローと CI/CD 操作
`code_security` | GitHub Code Scanning などのコードセキュリティ関連ツール
`dependabot` | Dependabot ツール
`discussions` | GitHub Discussions 関連ツール
`experiments` | まだ安定版と見なされていない実験的機能
`gists` | GitHub Gist 関連ツール
`github_support_docs_search` | GitHub 製品やサポートに関する質問に答えるためのドキュメント検索
`issues` | GitHub Issues 関連ツール
`labels` | GitHub Labels 関連ツール
`notifications` | GitHub Notifications 関連ツール
`orgs` | GitHub Organization 関連ツール
`projects` | GitHub Projects 関連ツール
`pull_requests` | GitHub Pull Request 関連ツール
`repos` | GitHub Repository 関連ツール
`secret_protection` | GitHub Secret Scanning などのシークレット保護関連ツール
`security_advisories` | セキュリティアドバイザリ関連ツール
`stargazers` | GitHub Stargazers 関連ツール
`users` | GitHub User 関連ツール

## 構成

リモート GitHub MCP サーバーには、利用可能なツールセットと読み取り専用モードを
構成するための任意ヘッダーがあります。

- `X-MCP-Toolsets`: 有効化するツールセットのカンマ区切りリストです。
  （例: `"repos,issues"`）
    - リストが空の場合はデフォルトのツールセットが使用されます。不正な
      ツールセットが指定されると、サーバーは起動に失敗し、400 bad request
      ステータスを返します。空白は無視されます。

- `X-MCP-Readonly`: 「読み取り」ツールのみを有効にします。
    - このヘッダーが空、または `"false"`、`"f"`、`"no"`、`"n"`、`"0"`、
      `"off"` の場合（空白と大文字小文字を無視）、false と解釈されます。
      それ以外の値はすべて true と解釈されます。

## 追加リソース

- [GitHub MCP Server Repository](https://github.com/github/github-mcp-server)
- [Remote GitHub MCP Server Documentation](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)
- [Policies and Governance for the GitHub MCP Server](https://github.com/github/github-mcp-server/blob/main/docs/policies-and-governance.md)
