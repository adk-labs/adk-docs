---
hide:
  - toc
---
# Firecrawl

[Firecrawl MCP Server](https://github.com/firecrawl/firecrawl-mcp-server)は、ADKエージェントを[Firecrawl](https://www.firecrawl.dev/) APIに接続します。このサービスは、あらゆるWebサイトをクロールし、そのコンテンツをクリーンで構造化されたマークダウンに変換できます。これにより、エージェントは、すべてのサブページを含むあらゆるURLからWebデータを取り込み、検索し、推論できます。

## 特徴

- **エージェントベースのWebリサーチ**: トピックを取り上げ、検索ツールを使用して関連するURLを見つけ、スクレイピングツールを使用して各ページの完全なコンテンツを分析または要約できるエージェントを展開します。

- **構造化データ抽出**: 抽出ツールを使用して、LLM抽出を利用して、製品名、価格、連絡先情報などの特定の構造化情報をURLのリストから取得します。

- **大規模なコンテンツの取り込み**: バッチスクレイピングおよびクロールツールを使用して、Webサイト全体またはURLの大きなバッチのスクレイピングを自動化します。これは、RAG（検索拡張生成）パイプラインのベクトルデータベースを作成するのに最適です。

## 前提条件

- [Firecrawlにサインアップ](https://www.firecrawl.dev/signin)して[APIキーを取得](https://firecrawl.dev/app/api-keys)

## ADKでの使用

=== "ローカルMCPサーバー"

    ```python
    from google.adk.agents.llm_agent import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool import McpToolset
    from mcp import StdioServerParameters

    FIRECRAWL_API_KEY = "YOUR_FIRECRAWL_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="firecrawl_agent",
        description="FirecrawlでWebサイトをスクレイピングするのに役立つアシスタント",
        instruction="ユーザーがWebサイトのコンテンツを検索するのを支援します",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "firecrawl-mcp",
                        ],
                        env={
                            "FIRECRAWL_API_KEY": FIRECRAWL_API_KEY,
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
    from google.adk.agents.llm_agent import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
    from google.adk.tools.mcp_tool import McpToolset

    FIRECRAWL_API_KEY = "YOUR_FIRECRAWL_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="firecrawl_agent",
        description="FirecrawlでWebサイトをスクレイピングするのに役立つアシスタント",
        instruction="ユーザーがWebサイトのコンテンツを検索するのを支援します",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(
                    url=f"https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/mcp",
                ),
            )
        ],
    )
    ```

## 利用可能なツール

このツールセットは、Webクロール、スクレイピング、検索のための包括的な機能スイートを提供します。

ツール | 名前 | 説明
---- | ---- | -----------
スクレイピングツール | `firecrawl_scrape` | 高度なオプションを使用して単一のURLからコンテンツをスクレイピングします
バッチスクレイピングツール | `firecrawl_batch_scrape` | 組み込みのレート制限と並列処理を使用して複数のURLを効率的にスクレイピングします
バッチステータスの確認 | `firecrawl_check_batch_status` | バッチ操作のステータスを確認します
マップツール | `firecrawl_map` | Webサイトをマッピングして、サイト上のすべてのインデックス付きURLを検出します
検索ツール | `firecrawl_search` | Webを検索し、オプションで検索結果からコンテンツを抽出します
クロールツール | `firecrawl_crawl` | 高度なオプションを使用して非同期クロールを開始します
クロールステータスの確認 | `firecrawl_check_crawl_status` | クロールジョブのステータスを確認します
抽出ツール | `firecrawl_extract` | LLM機能を使用してWebページから構造化情報を抽出します。クラウドAIとセルフホストLLM抽出の両方をサポートします

## 構成

Firecrawl MCPサーバーは、環境変数を使用して構成できます。

**必須**:

- `FIRECRAWL_API_KEY`: Firecrawl APIキー
    - クラウドAPIを使用する場合に必須（デフォルト）
    - `FIRECRAWL_API_URL`を使用してセルフホストインスタンスを使用する場合はオプション

**Firecrawl API URL（オプション）**:

- `FIRECRAWL_API_URL`（オプション）: セルフホストインスタンス用のカスタムAPIエンドポイント
    - 例: `https://firecrawl.your-domain.com`
    - 指定しない場合、クラウドAPIが使用されます（APIキーが必要です）

**再試行構成（オプション）**:

- `FIRECRAWL_RETRY_MAX_ATTEMPTS`: 最大再試行回数（デフォルト: 3）
- `FIRECRAWL_RETRY_INITIAL_DELAY`: 最初の再試行前の初期遅延（ミリ秒）（デフォルト: 1000）
- `FIRECRAWL_RETRY_MAX_DELAY`: 再試行間の最大遅延（ミリ秒）（デフォルト: 10000）
- `FIRECRAWL_RETRY_BACKOFF_FACTOR`: 指数バックオフ乗数（デフォルト: 2）

**クレジット使用量監視（オプション）**:

- `FIRECRAWL_CREDIT_WARNING_THRESHOLD`: クレジット使用量警告しきい値（デフォルト: 1000）
- `FIRECRAWL_CREDIT_CRITICAL_THRESHOLD`: クレジット使用量クリティカルしきい値（デフォルト: 100）

## 追加リソース

- [Firecrawl MCPサーバードキュメント](https://docs.firecrawl.dev/mcp-server)
- [Firecrawl MCPサーバーリポジトリ](https://github.com/firecrawl/firecrawl-mcp-server)
- [Firecrawlユースケース](https://docs.firecrawl.dev/use-cases/overview)
- [Firecrawl高度なスクレイピングガイド](https://docs.firecrawl.dev/advanced-scraping-guide)
