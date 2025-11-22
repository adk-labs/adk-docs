---
hide:
  - toc
---
# Exa

[Exa MCP Server](https://github.com/github/github-mcp-server)は、ADKエージェントをAI専用に構築されたプラットフォームである[Exaの検索エンジン](https://exa.ai)に接続します。これにより、エージェントは関連するWebページを検索し、リンクに基づいて類似のコンテンツを見つけ、URLからクリーンで解析されたコンテンツを取得し、質問に対する直接的な回答を取得し、自然言語を使用して詳細な調査レポートを自動化できます。

## ユースケース

- **コードと技術的な例の検索**: GitHub、ドキュメント、技術フォーラムを横断して検索し、最新のコードスニペット、APIの使用パターン、実装例を見つけます。

- **詳細な調査の実行**: 複雑なトピックに関する包括的な調査レポートを開始し、企業に関する詳細情報を収集したり、LinkedInで専門家のプロフィールを見つけたりします。

- **リアルタイムWebコンテンツへのアクセス**: 一般的なWeb検索を実行して最新情報を取得したり、特定の記事、ブログ投稿、またはWebページから完全なコンテンツを抽出したりします。

## 前提条件

- Exaで[APIキー](https://dashboard.exa.ai/api-keys)を作成します。詳細については、[ドキュメント](https://docs.exa.ai/reference/quickstart)を参照してください。

## エージェントでの使用

=== "ローカルMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool import McpToolset
    from mcp import StdioServerParameters

    EXA_API_KEY = "YOUR_EXA_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="exa_agent",
        instruction="ユーザーがExaから情報を取得するのを支援します",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "exa-mcp-server",
                            # (オプション)有効にするツールを指定します
                            # ツールを指定しない場合、デフォルトで有効になっているすべてのツールが使用されます。
                            # "--tools=get_code_context_exa,web_search_exa",
                        ],
                        env={
                            "EXA_API_KEY": EXA_API_KEY,
                        }
                    ),
                    timeout=30,
                ),
            )
        ],
    )
    ```

=== "リモートMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
    from google.adk.tools.mcp_tool import McpToolset

    EXA_API_KEY = "YOUR_EXA_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="exa_agent",
        instruction="""ユーザーがExaから情報を取得するのを支援します""",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(
                    url="https://mcp.exa.ai/mcp?exaApiKey=" + EXA_API_KEY,
                    # (オプション)有効にするツールを指定します
                    # ツールを指定しない場合、デフォルトで有効になっているすべてのツールが使用されます。
                    # url="https://mcp.exa.ai/mcp?exaApiKey=" + EXA_API_KEY + "&enabledTools=%5B%22crawling_exa%22%5D",
                ),
            )
        ],
    )
    ```

## 利用可能なツール

ツール <img width="400px"/> | 説明
---- | -----------
`get_code_context_exa` | オープンソースライブラリ、GitHubリポジトリ、プログラミングフレームワークから関連するコードスニペット、例、ドキュメントを検索して取得します。最新のコードドキュメント、実装例、APIの使用パターン、実際のコードベースからのベストプラクティスを見つけるのに最適です。
`web_search_exa` | 最適化された結果とコンテンツ抽出を使用してリアルタイムのWeb検索を実行します。
`company_research` | 企業のWebサイトをクロールして、企業に関する詳細情報を収集する包括的な企業調査ツール。
`crawling` | 特定のURLからコンテンツを抽出し、正確なURLがある場合に記事、PDF、または任意のWebページを読むのに役立ちます。
`linkedin_search` | Exa AIを使用してLinkedInで企業や人物を検索します。クエリに会社名、個人名、または特定のLinkedIn URLを含めるだけです。
`deep_researcher_start` | 複雑な質問に対してスマートなAIリサーチャーを開始します。AIはWebを検索し、多くの情報源を読み、質問について深く考えて詳細な調査レポートを作成します。
`deep_researcher_check` | 調査の準備ができているかどうかを確認し、結果を取得します。調査タスクを開始した後、これを使用して完了したかどうかを確認し、包括的なレポートを取得します。

## 構成

ローカルExa MCPサーバーで使用するツールを指定するには、`--tools`パラメーターを使用できます。

```
--tools=get_code_context_exa,web_search_exa,company_research,crawling,linkedin_search,deep_researcher_start,deep_researcher_check
```

リモートExa MCPサーバーで使用するツールを指定するには、`enabledTools` URLパラメーターを使用できます。

```
https://mcp.exa.ai/mcp?exaApiKey=YOUREXAKEY&enabledTools=%5B%22crawling_exa%22%5D
```

## 追加リソース

- [Exa MCPサーバードキュメント](https://docs.exa.ai/reference/exa-mcp)
- [Exa MCPサーバーリポジトリ](https://github.com/exa-labs/exa-mcp-server)
