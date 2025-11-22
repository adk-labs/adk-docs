# Tavily

[Tavily MCP Server](https://github.com/tavily-ai/tavily-mcp)は、
ADKエージェントをTavilyのAIに特化した検索、抽出、およびクローリングプラットフォームに接続します。
このツールにより、エージェントはリアルタイムのWeb検索を実行し、Webページから
特定のデータをインテリジェントに抽出し、Webサイトをクロールまたは
構造化マップを作成する能力を得ることができます。

## ユースケース (Use cases)

- **リアルタイムWeb検索 (Real-Time Web Search)**: 最適化されたリアルタイムWeb検索を実行し、
  エージェントのタスクに必要な最新情報を取得します。

- **インテリジェントなデータ抽出 (Intelligent Data Extraction)**: HTML全体を解析することなく、
  あらゆるWebページから特定かつクリーンなデータとコンテンツを抽出します。

- **Webサイトの探索 (Website Exploration)**: Webサイトを自動的にクロールしてコンテンツを探索したり、
  サイトのレイアウトやページの構造化マップを作成したりします。

## 前提条件 (Prerequisites)

- [Tavilyアカウント](https://app.tavily.com/)に登録してAPIキーを取得してください。
  詳細については[ドキュメント](https://docs.tavily.com/documentation/quickstart)を参照してください。

## エージェントでの使用 (Use with agent)

=== "ローカルMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="tavily_agent",
        instruction="Help users get information from Tavily",
        tools=[
           McpToolset(
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
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

    TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="tavily_agent",
        instruction="""Help users get information from Tavily""",
        tools=[
           McpToolset(
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

## 使用例 (Example usage)

エージェントの設定と実行が完了したら、コマンドラインインターフェース（CLI）または
Webインターフェースを通じて対話できます。以下は簡単な例です：

**エージェントプロンプトの例:**

> tavily.com上のすべてのドキュメントページを見つけ、Tavilyの始め方に関する手順を提供してください

エージェントは複数のTavilyツールを自動的に呼び出して包括的な回答を提供するため、
手動でナビゲートすることなく、Webサイトの探索や情報収集を簡単に行うことができます：

<img src="../../../assets/tools-tavily-screenshot.png">

## 利用可能なツール (Available tools)

接続されると、エージェントはTavilyのWebインテリジェンスツールにアクセスできるようになります：

ツール <img width="100px"/> | 説明
---- | -----------
`tavily-search` | Web全体から関連情報を検索するための検索クエリを実行します。
`tavily-extract` | あらゆるWebページから構造化データを抽出します。単一ページからテキスト、リンク、画像を抽出したり、複数のURLを効率的にバッチ処理したりします。
`tavily-map` | Webサイトをグラフのように走査（トラバース）し、インテリジェントな発見機能により数百のパスを並行して探索して、包括的なサイトマップを生成します。
`tavily-crawl` | 組み込みの抽出およびインテリジェントな発見機能を備え、数百のパスを並行して探索できる走査（トラバーサル）ツールです。

## 追加リソース (Additional resources)

- [Tavily MCPサーバー ドキュメント](https://docs.tavily.com/documentation/mcp)
- [Tavily MCPサーバー リポジトリ](https://github.com/tavily-ai/tavily-mcp)