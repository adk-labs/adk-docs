# GitLab

[GitLab MCP Server](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/)は、
ADKエージェントを[GitLab.com](https://gitlab.com/)またはセルフマネージドGitLabインスタンスに直接接続します。
この統合により、エージェントはイシュー（Issue）やマージリクエスト（Merge Request）の管理、
CI/CDパイプラインの検査、セマンティックコード検索の実行、自然言語を使用した開発ワークフローの自動化を
行う能力を得ることができます。

## ユースケース (Use cases)

- **セマンティックコード探索 (Semantic Code Exploration)**: 自然言語を使用してコードベースをナビゲートします。
  標準的なテキスト検索とは異なり、コードのロジックや意図を問い合わせることで、
  複雑な実装を素早く理解できます。

- **マージリクエストレビューの高速化 (Accelerate Merge Request Reviews)**: コードの変更内容を即座に把握します。
  マージリクエストのコンテキスト全体を取得し、特定の差分（diff）を分析し、コミット履歴をレビューすることで、
  チームにより迅速かつ有意義なフィードバックを提供します。

- **CI/CDパイプラインのトラブルシューティング (Troubleshoot CI/CD Pipelines)**: チャット画面を離れることなくビルドの失敗を診断します。
  パイプラインのステータスを検査し、詳細なジョブログを取得して、特定のマージリクエストやコミットが
  チェックに失敗した正確な原因を特定します。

## 前提条件 (Prerequisites)

- PremiumまたはUltimateサブスクリプションを持ち、[GitLab Duo](https://docs.gitlab.com/user/gitlab_duo/)が有効になっているGitLabアカウント
- GitLab設定で[ベータおよび実験的な機能](https://docs.gitlab.com/user/gitlab_duo/turn_on_off/#turn-on-beta-and-experimental-features)が有効になっていること

## エージェントでの使用 (Use with agent)

=== "ローカルMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    # セルフホストの場合はインスタンスURLに置き換えてください (例: "gitlab.example.com")
    GITLAB_INSTANCE_URL = "gitlab.com"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="gitlab_agent",
        instruction="Help users get information from GitLab",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "mcp-remote",
                            f"https://{GITLAB_INSTANCE_URL}/api/v4/mcp",
                            "--static-oauth-client-metadata",
                            "{\"scope\": \"mcp\"}",
                        ],
                    ),
                    timeout=30,
                ),
            )
        ],
    )
    ```

!!! note

    このエージェントを初めて実行すると、ブラウザウィンドウが自動的に開き（認証URLも出力され）、
    OAuth権限が要求されます。エージェントがGitLabデータにアクセスできるようにするには、
    このリクエストを承認する必要があります。

## 利用可能なツール (Available tools)

ツール | 説明
---- | -----------
`get_mcp_server_version` | GitLab MCPサーバーの現在のバージョンを返します
`create_issue` | GitLabプロジェクトに新しいイシューを作成します
`get_issue` | 特定のGitLabイシューに関する詳細情報を取得します
`create_merge_request` | プロジェクトにマージリクエストを作成します
`get_merge_request` | 特定のGitLabマージリクエストに関する詳細情報を取得します
`get_merge_request_commits` | 特定のマージリクエスト内のコミットリストを取得します
`get_merge_request_diffs` | 特定のマージリクエストの差分（diff）を取得します
`get_merge_request_pipelines` | 特定のマージリクエストのパイプラインを取得します
`get_pipeline_jobs` | 特定のCI/CDパイプラインのジョブを取得します
`gitlab_search` | 検索APIを使用してGitLabインスタンス全体から用語を検索します
`semantic_code_search` | プロジェクト内の関連するコードスニペットを検索します

## 追加リソース (Additional resources)

- [GitLab MCPサーバー ドキュメント](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/)