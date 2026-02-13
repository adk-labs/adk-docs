---
catalog_title: GitHub
catalog_description: コードを分析し、Issue と PR を管理し、ワークフローを自動化します
catalog_icon: /adk-docs/integrations/assets/github.png
catalog_tags: ["code", "mcp"]
---
# GitHub

[GitHub MCP Server](https://github.com/github/github-mcp-server)は、AIツールをGitHubプラットフォームに直接接続します。これにより、ADKエージェントはリポジトリとコードファイルを読み取り、IssueとPRを管理し、コードを分析し、自然言語を使用してワークフローを自動化できます。

## ユースケース

- **リポジトリ管理**: アクセス権のあるリポジトリ全体でコードを参照およびクエリし、ファイルを検索し、コミットを分析し、プロジェクト構造を理解します。
- **IssueとPRの自動化**: Issueとプルリクエストを作成、更新、管理します。AIがバグのトリアージ、コード変更のレビュー、プロジェクトボードの維持を支援します。
- **コード分析**: セキュリティの検出結果を調査し、Dependabotのアラートを確認し、コードパターンを理解し、コードベースに関する包括的な洞察を得ます。

## 前提条件

- GitHubで[個人アクセストークン](https://github.com/settings/personal-access-tokens/new)を作成します。詳細については、[ドキュメント](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)を参照してください。

## エージェントでの使用

=== "リモートMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
    from google.adk.tools.mcp_tool import McpToolset

    GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="github_agent",
        instruction="ユーザーがGitHubから情報を取得するのを支援します",
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

## 利用可能なツール

ツール | 説明
---- | -----------
`context` | 現在のユーザーと操作しているGitHubコンテキストに関するコンテキストを提供するツール
`copilot` | Copilot関連ツール（例：Copilotコーディングエージェント）
`copilot_spaces` | Copilot Spaces関連ツール
`actions` | GitHub ActionsワークフローとCI/CD操作
`code_security` | GitHubコードスキャンなどのコードセキュリティ関連ツール
`dependabot` | Dependabotツール
`discussions` | GitHubディスカッション関連ツール
`experiments` | まだ安定しているとは見なされていない実験的な機能
`gists` | GitHub Gist関連ツール
`github_support_docs_search` | GitHub製品とサポートの質問に答えるためにドキュメントを検索
`issues` | GitHub Issue関連ツール
`labels` | GitHubラベル関連ツール
`notifications` | GitHub通知関連ツール
`orgs` | GitHub組織関連ツール
`projects` | GitHubプロジェクト関連ツール
`pull_requests` | GitHubプルリクエスト関連ツール
`repos` | GitHubリポジトリ関連ツール
`secret_protection` | GitHubシークレットスキャンなどのシークレット保護関連ツール
`security_advisories` | セキュリティアドバイザリ関連ツール
`stargazers` | GitHubスターゲイザー関連ツール
`users` | GitHubユーザー関連ツール

## 構成

リモートGitHub MCPサーバーには、利用可能なツールセットと読み取り専用モードを構成するために使用できるオプションのヘッダーがあります。

- `X-MCP-Toolsets`: 有効にするツールセットのカンマ区切りリスト。（例："repos,issues"）
    - リストが空の場合、デフォルトのツールセットが使用されます。不正なツールセットが指定された場合、サーバーは起動に失敗し、400 Bad Requestステータスを発行します。空白は無視されます。

- `X-MCP-Readonly`: 「読み取り」ツールのみを有効にします。
    - このヘッダーが空、"false"、"f"、"no"、"n"、"0"、または"off"（空白と大文字小文字を無視）の場合、falseとして解釈されます。他のすべての値はtrueとして解釈されます。


## 追加リソース

- [GitHub MCPサーバーリポジトリ](https://github.com/github/github-mcp-server)
- [リモートGitHub MCPサーバードキュメント](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)
- [GitHub MCPサーバーのポリシーとガバナンス](https://github.com/github/github-mcp-server/blob/main/docs/policies-and-governance.md)
