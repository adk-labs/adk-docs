# ScrapeGraphAI

[ScrapeGraphAI MCP Server](https://github.com/ScrapeGraphAI/scrapegraph-mcp)は、
ADKエージェントを[ScrapeGraphAI](https://scrapegraphai.com/)に接続します。
この統合により、エージェントは自然言語プロンプトを使用して構造化データを抽出し、
無限スクロールのような動的コンテンツを処理し、複雑なWebページをクリーンで利用可能な
JSONまたはMarkdownに変換できるようになります。

## ユースケース (Use cases)

- **スケーラブルな抽出とクローリング (Scalable Extraction & Crawling)**: 単一ページから
  構造化データを抽出したり、Webサイト全体をクロールしたりできます。AIを活用して、
  動的コンテンツ、無限スクロール、大規模な非同期操作を処理します。

- **調査と要約 (Research and Summarization)**: AIによるWeb検索を実行してトピックを調査し、
  複数のソースからデータを集約し、結果を要約します。

- **エージェンティックワークフロー (Agentic Workflows)**: カスタマイズ可能なステップ、
  複雑なナビゲーション（認証など）、構造化された出力スキーマを備えた高度な
  エージェントスクレイピングワークフローを実行します。

## 前提条件 (Prerequisites)

- ScrapeGraphAIで[APIキー](https://dashboard.scrapegraphai.com/register/)を作成してください。
  詳細については[ドキュメント](https://docs.scrapegraphai.com/api-reference/introduction)を参照してください。
- [ScrapeGraphAI MCPサーバーパッケージ](https://pypi.org/project/scrapegraph-mcp/)をインストールしてください
  （Python 3.13以上が必要です）:

    ```console
    pip install scrapegraph-mcp
    ```

## エージェントでの使用 (Use with agent)

=== "ローカルMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    SGAI_API_KEY = "YOUR_SCRAPEGRAPHAI_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="scrapegraph_assistant_agent",
        instruction="""Help the user with web scraping and data extraction using
                      ScrapeGraph AI. You can convert webpages to markdown, extract
                      structured data using AI, perform web searches, crawl
                      multiple pages, and automate complex scraping workflows.""",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        # 以下のCLIコマンドは `pip install scrapegraph-mcp` で
                        # 利用可能です
                        command="scrapegraph-mcp",
                        env={
                            "SGAI_API_KEY": SGAI_API_KEY,
                        },
                    ),
                    timeout=300,
                ),
            # オプション: MCPサーバーから公開するツールをフィルタリング
            # tool_filter=["markdownify", "smartscraper", "searchscraper"]
            ),
        ],
    )
    ```

## 利用可能なツール (Available tools)

ツール <img width="200px"/> | 説明
---- | -----------
`markdownify` | 任意のWebページをクリーンで構造化されたMarkdown形式に変換します
`smartscraper` | AIを活用し、無限スクロールをサポートして任意のWebページから構造化データを抽出します
`searchscraper` | 構造化された実用的な結果を伴うAI駆動のWeb検索を実行します
`scrape` | ページコンテンツを取得するための基本的なスクレイピングエンドポイントです（重いJavaScriptレンダリングのオプションあり）
`sitemap` | 任意のWebサイトのサイトマップURLと構造を抽出します
`smartcrawler_initiate` | インテリジェントな複数ページWebクローリングを開始します（非同期操作）
`smartcrawler_fetch_results` | 非同期クローリング操作から結果を取得します
`agentic_scrapper` | カスタマイズ可能なステップと構造化された出力スキーマを使用して、高度なエージェントスクレイピングワークフローを実行します

## 追加リソース (Additional resources)

- [ScrapeGraphAI MCPサーバー ドキュメント](https://docs.scrapegraphai.com/services/mcp-server)
- [ScrapeGraphAI MCPサーバー リポジトリ](https://github.com/ScrapeGraphAI/scrapegraph-mcp)