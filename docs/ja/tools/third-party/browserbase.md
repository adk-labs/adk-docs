---
hide:
  - toc
---
# Browserbase

[Browserbase MCP Server](https://github.com/browserbase/mcp-server-browserbase)は、[Browserbase](https://www.browserbase.com/)と[Stagehand](https://github.com/browserbase/stagehand)を使用して、クラウドブラウザの自動化機能に接続します。これにより、ADKエージェントはWebページと対話し、スクリーンショットを撮り、情報を抽出し、自動化されたアクションを実行できます。

## ユースケース

- **自動化されたWebワークフロー**: エージェントがWebサイトへのログイン、フォームへの入力、データの送信、複雑なユーザーフローのナビゲーションなどの多段階のタスクを実行できるようにします。

- **インテリジェントなデータ抽出**: 特定のページに自動的に移動し、構造化されたデータ、テキストコンテンツ、またはその他の情報をエージェントのタスクで使用するために抽出します。

- **視覚的な監視とインタラクション**: フルページまたは要素固有のスクリーンショットをキャプチャして、Webサイトを視覚的に監視し、UI要素をテストしたり、視覚的なコンテキストをビジョン対応モデルにフィードバックしたりします。

## 前提条件

- APIキーとプロジェクトIDを取得するには、[Browserbaseアカウント](https://www.browserbase.com/sign-up)にサインアップしてください。詳細については、[ドキュメント](https://docs.browserbase.com/introduction/getting-started)を参照してください。

## エージェントでの使用

=== "ローカルMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from mcp import StdioServerParameters

    BROWSERBASE_API_KEY = "YOUR_BROWSERBASE_API_KEY"
    BROWSERBASE_PROJECT_ID = "YOUR_BROWSERBASE_PROJECT_ID"
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="browserbase_agent",
        instruction="ユーザーがBrowserbaseから情報を取得するのを支援します",
        tools=[
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "@browserbasehq/mcp-server-browserbase",
                        ],
                        env={
                            "BROWSERBASE_API_KEY": BROWSERBASE_API_KEY,
                            "BROWSERBASE_PROJECT_ID": BROWSERBASE_PROJECT_ID,
                            "GEMINI_API_KEY": GEMINI_API_KEY,
                        }
                    ),
                    timeout=300,
                ),
            )
        ],
    )
    ```

## 利用可能なツール

ツール <img width="200px"/> | 説明
---- | -----------
`browserbase_stagehand_navigate` | ブラウザで任意のURLに移動します
`browserbase_stagehand_act` | 自然言語を使用してWebページでアクションを実行します
`browserbase_stagehand_extract` | 現在のページからすべてのテキストコンテンツを抽出します（CSSとJavaScriptを除外）
`browserbase_stagehand_observe` | Webページ上の実行可能な要素を監視して見つけます
`browserbase_screenshot` | 現在のページのPNGスクリーンショットをキャプチャします
`browserbase_stagehand_get_url` | ブラウザページの現在のURLを取得します
`browserbase_session_create` | 完全に初期化されたStagehandを使用してBrowserbaseでクラウドブラウザセッションを作成または再利用します
`browserbase_session_close` | 現在のBrowserbaseセッションを閉じ、ブラウザを切断し、Stagehandインスタンスをクリーンアップします

## 構成

Browserbase MCPサーバーは、次のコマンドラインフラグを受け入れます。

フラグ | 説明
---- | -----------
`--proxies` | セッションのBrowserbaseプロキシを有効にします
`--advancedStealth` | Browserbase Advanced Stealthを有効にします（スケールプランユーザーのみ）
`--keepAlive` | Browserbase Keep Aliveセッションを有効にします
`--contextId <contextId>` | 使用するBrowserbaseコンテキストIDを指定します
`--persist` | Browserbaseコンテキストを永続化するかどうか（デフォルト：true）
`--port <port>` | HTTP/SHTTPトランスポートをリッスンするポート
`--host <host>` | サーバーをバインドするホスト（デフォルト：localhost、すべてのインターフェイスに0.0.0.0を使用）
`--cookies [json]` | ブラウザに挿入するCookieのJSON配列
`--browserWidth <width>` | ブラウザのビューポート幅（デフォルト：1024）
`--browserHeight <height>` | ブラウザのビューポートの高さ（デフォルト：768）
`--modelName <model>` | Stagehandに使用するモデル（デフォルト：gemini-2.0-flash）
`--modelApiKey <key>` | カスタムモデルプロバイダーのAPIキー（カスタムモデルを使用する場合に必要）
`--experimental` | 実験的な機能を有効にします（デフォルト：false）

## 追加リソース

- [Browserbase MCPサーバーのドキュメント](https://docs.browserbase.com/integrations/mcp/introduction)
- [Browserbase MCPサーバーの構成](https://docs.browserbase.com/integrations/mcp/configuration)
- [Browserbase MCPサーバーリポジトリ](https://github.com/browserbase/mcp-server-browserbase)
