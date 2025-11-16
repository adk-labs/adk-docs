---
hide:
  - toc
---
# Tavily

[Tavily MCP Server](https://github.com/tavily-ai/tavily-mcp)は、ADKエージェントをTavilyのAIに焦点を当てた検索、抽出、およびクロールプラットフォームに接続します。このツールは、エージェントにリアルタイムのWeb検索を実行し、Webページから特定のデータをインテリジェントに抽出し、Webサイトをクロールまたは構造化されたマップを作成する機能を提供します。

## ユースケース

- **リアルタイムWeb検索**: 最適化されたリアルタイムWeb検索を実行して、エージェントのタスクの最新情報を取得します。

- **インテリジェントなデータ抽出**: 完全なHTMLを解析する必要なく、任意のWebページから特定のクリーンなデータとコンテンツを抽出します。

- **Webサイトの探索**: Webサイトを自動的にクロールしてコンテンツを探索したり、サイトのレイアウトとページの構造化されたマップを作成したりします。

## 前提条件

- APIキーを取得するには、[Tavilyアカウント](https://app.tavily.com/)にサインアップしてください。詳細については、[ドキュメント](https://docs.tavily.com/documentation/quickstart)を参照してください。

## エージェントでの使用

=== "ローカルMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from mcp import StdioServerParameters

    TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="tavily_agent",
        instruction="ユーザーがTavilyから情報を取得するのを支援します",
        tools=[
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "tavily-mcp@latest",
                        ],
                        env={
                            "TAVILY_API_KEY": TAVILY_API_KEY,
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
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

    TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="tavily_agent",
        instruction="""ユーザーがTavilyから情報を取得するのを支援します""",
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPServerParams(
                    url="https://mcp.tavily.com/mcp/",
                    headers={
                        "Authorization": f"Bearer {TAVILY_API_KEY}",
                    },
                ),
            )
        ],
    )
    ```

## 使用例

エージェントがセットアップされて実行されると、コマンドラインインターフェイスまたはWebインターフェイスを介して対話できます。以下に簡単な例を示します。

**サンプルエージェントプロンプト:**

> tavily.comのすべてのドキュメントページを見つけて、Tavilyの開始方法に関する手順を提供してください

エージェントは、包括的な回答を提供するために複数のTavilyツールを自動的に呼び出し、手動ナビゲーションなしでWebサイトを簡単に探索して情報を収集できるようにします。

<img src="../../../assets/tools-tavily-screenshot.png">

## 利用可能なツール

接続すると、エージェントはTavilyのWebインテリジェンスツールにアクセスできます。

ツール <img width="100px"/> | 説明
---- | -----------
`tavily-search` | Web全体で関連情報を検索するための検索クエリを実行します。
`tavily-extract` | 任意のWebページから構造化データを抽出します。単一のページからテキスト、リンク、画像を抽出したり、複数のURLを効率的にバッチ処理したりします。
`tavily-map` | グラフのようにWebサイトをトラバースし、インテリジェントな検出で何百ものパスを並行して探索して、包括的なサイトマップを生成できます。
`tavily-crawl` | 組み込みの抽出とインテリジェントな検出により、何百ものパスを並行して探索できるトラバーサルツール。

## 追加リソース

- [Tavily MCPサーバードキュメント](https://docs.tavily.com/documentation/mcp)
- [Tavily MCPサーバーリポジトリ](https://github.com/tavily-ai/tavily-mcp)
