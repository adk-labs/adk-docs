# Bright Data

[Bright Data MCPサーバー](https://github.com/brightdata/brightdata-mcp)は、ADKエージェントをBright DataのWebデータプラットフォームに接続します。このツールは、エージェントにリアルタイムのWeb検索、Webページのスクレイピング、構造化データの抽出、ブラウザのリモート制御、人気のあるプラットフォームからの事前構築済みデータフィードへのアクセス機能を提供します。

## ユースケース

- **リアルタイムWeb検索**: 最適化されたWeb検索を実行して、AIに適した形式（JSON/Markdown）で最新情報を取得します。

- **構造化データ抽出**: AIを活用した抽出を使用して、オプションのカスタムプロンプトを使用して、あらゆるWebページをクリーンで構造化されたJSONデータに変換します。

- **ブラウザの自動化**: 複雑なインタラクション、JavaScriptのレンダリング、動的なコンテンツ抽出のために、実際のブラウザをリモートで制御します。

- **事前構築済みデータAPI**: Amazon、LinkedIn、Instagram、TikTok、Googleマップなど、人気のあるプラットフォームから60以上の構造化データセットにアクセスします。

- **広告分析**: 業界標準の広告ブロックフィルターリストを使用して、Webページから広告を抽出して分析します。

## 前提条件

- APIトークンを取得するには、[Bright Dataアカウント](https://brightdata.com/)にサインアップしてください。
- 詳細については、[ドキュメント](https://docs.brightdata.com/mcp-server/overview)を参照してください。
- サーバーは、プロトタイピングや日常のワークフローに役立つ**月間5,000リクエストの無料利用枠**を提供しています。

## エージェントでの使用

=== "ローカルMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool import McpToolset
    from mcp import StdioServerParameters

    BRIGHTDATA_API_TOKEN = "YOUR_BRIGHTDATA_API_TOKEN"

    root_agent = Agent(
        model="gemini-1.5-pro",
        name="brightdata_agent",
        instruction="Bright Dataを使用してユーザーがWebデータにアクセスできるように支援します",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "@brightdata/mcp",
                        ],
                        env={
                            "API_TOKEN": BRIGHTDATA_API_TOKEN,
                            "PRO_MODE": "true",  # オプション: 60以上のすべてのツールを有効にする
                        }
                    ),
                    timeout=300,
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

    BRIGHTDATA_API_TOKEN = "YOUR_BRIGHTDATA_API_TOKEN"

    root_agent = Agent(
        model="gemini-1.5-pro",
        name="brightdata_agent",
        instruction="""Bright Dataを使用してユーザーがWebデータにアクセスできるように支援します""",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(
                    url=f"https://mcp.brightdata.com/mcp?token={BRIGHTDATA_API_TOKEN}",
                ),
            )
        ],
    )
    ```

## 使用例

エージェントをセットアップして実行すると、コマンドラインインターフェイスまたはWebインターフェイスを介してエージェントと対話できます。以下にいくつかの例を示します。

**サンプルエージェントプロンプト:**

> AmazonでiPhone 15 Proの現在の価格と詳細を教えてください

> Googleで「2025年の気候変動ニュース」を検索し、上位5件の結果を要約してください

> techcrunch.comのホームページをスクレイピングし、すべての記事の見出しとリンクを抽出してください

エージェントは適切なBright Dataツールを自動的に呼び出して包括的な回答を提供するため、手動でナビゲートしたり、ブロックされることを心配したりすることなく、リアルタイムのWebデータに簡単にアクセスできます。

## 利用可能なツール

Bright Data MCPサーバーは、2つのモードで動作します。

### ラピッドモード（無料利用枠 - デフォルト）

ツール <img width="100px"/> | 説明
---- | -----------
`search_engine` | Google、Bing、またはYandexのSERPをJSONまたはMarkdownとしてスクレイピングします。
`scrape_as_markdown` | 組み込みのブロック解除機能を使用して、WebページをクリーンなMarkdownに変換します。
`scrape_as_html` | ブロッカーをバイパスしながら、Webページから生のHTMLを返します。
`extract` | カスタムプロンプトを使用して、Markdown出力を構造化JSONに変換します。
`session_stats` | セッションの使用状況の統計とツール呼び出し数を表示します。

### プロモード（60以上の追加ツール）

環境変数で`PRO_MODE=true`を設定してプロモードを有効にすると、以下にアクセスできます。

**一括操作:**
- `search_engine_batch`: 最大10件の検索クエリを同時に実行します。
- `scrape_batch`: 最大10個のURLを同時にスクレイピングします。

**ブラウザの自動化:**
- `scraping_browser.*`: 複雑なインタラクションのための完全なブラウザ制御。
- ナビゲート、クリック、入力、スクロール、スクリーンショットの撮影など。

**WebデータAPI（60以上の構造化データセット）:**

- **Eコマース**: `web_data_amazon_product`, `web_data_walmart_product`, `web_data_ebay_product`, `web_data_etsy_products`, `web_data_bestbuy_products`, `web_data_zara_products`
- **ソーシャルメディア**: `web_data_linkedin_person_profile`, `web_data_instagram_profiles`, `web_data_facebook_posts`, `web_data_tiktok_profiles`, `web_data_x_posts`, `web_data_reddit_posts`
- **ビジネスインテリジェンス**: `web_data_linkedin_company_profile`, `web_data_crunchbase_company`, `web_data_zoominfo_company_profile`
- **検索とレビュー**: `web_data_amazon_product_search`, `web_data_amazon_product_reviews`, `web_data_google_maps_reviews`, `web_data_facebook_company_reviews`
- **地図とローカル**: `web_data_google_maps_reviews`, `web_data_zillow_properties_listing`, `web_data_booking_hotel_listings`
- **アプリストア**: `web_data_google_play_store`, `web_data_apple_app_store`
- **メディアとニュース**: `web_data_youtube_videos`, `web_data_youtube_comments`, `web_data_reuter_news`
- **開発者ツール**: `web_data_github_repository_file`
- **金融**: `web_data_yahoo_finance_business`

すべてのWebデータAPIツールは、キャッシュされた、または最新の構造化データをJSON形式で返し、多くの場合、リアルタイムのスクレイピングよりも信頼性が高くなります。

## 構成オプション

Bright Data MCPサーバーは、カスタマイズのためにいくつかの環境変数をサポートしています。

変数 | 説明 | デフォルト
---- | ---- | ----
`API_TOKEN` | Bright Data APIトークン（必須） | -
`PRO_MODE` | 60以上のすべての高度なツールを有効にする | `false`
`RATE_LIMIT` | カスタムレート制限（例: "100/1h"、"50/30m"） | 制限なし
`WEB_UNLOCKER_ZONE` | カスタムWeb Unlockerゾーン名 | `mcp_unlocker`
`BROWSER_ZONE` | カスタムブラウザAPIゾーン名 | `mcp_browser`

## 追加リソース

- [Bright Data MCPサーバードキュメント](https://docs.brightdata.com/mcp-server/overview)
- [Bright Data MCPサーバーリポジトリ](https://github.com/brightdata/brightdata-mcp)
- [完全なツールドキュメント](https://github.com/brightdata-com/brightdata-mcp/blob/main/assets/Tools.md)
- [使用例](https://github.com/brightdata-com/brightdata-mcp/blob/main/examples)
- [インタラクティブプレイグラウンド](https://brightdata.com/ai/playground-chat)
