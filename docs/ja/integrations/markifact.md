---
catalog_title: Markifact
catalog_description: Google Ads、Meta、GA4、TikTok、その他 15 以上のプラットフォームにまたがるマーケティング業務を管理
catalog_icon: /integrations/assets/markifact.png
catalog_tags: ["mcp", "connectors"]
---

# ADK 向け Markifact MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Markifact MCP Server](https://github.com/markifact/markifact-mcp) は、ADK エージェントを
[Markifact](https://www.markifact.com) に接続します。Markifact は Google Ads、
Meta Ads、GA4、TikTok Ads、Shopify など 20 以上のプラットフォームにまたがる
300 以上の操作を備えた AI マーケティング自動化プラットフォームです。この統合により、
エージェントは自然言語でキャンペーンを管理し、パフォーマンスを分析し、マーケティング
ワークフローを自動化できます。すべての書き込み操作には承認プロンプトが適用されます。

## ユースケース

- **支出の健全性管理**: Google Ads、Meta、TikTok、LinkedIn 全体で無駄な予算を
  特定し、具体的な一時停止や再配分の推奨を提示します。
- **統合レポート**: 1 つのプロンプトで、接続されたすべてのチャネルと GA4 全体の
  ブレンド支出、ROAS、CAC、コンバージョン変化を生成します。
- **ブリーフからライブキャンペーンへ**: 1 行のブリーフから、人間の承認を待つ
  Search、Performance Max、Meta Advantage+、TikTok、LinkedIn キャンペーンの
  下書きまで作成します。
- **リードの引き継ぎ**: Meta と LinkedIn のリードフォームを収集し、HubSpot または
  Klaviyo でエンリッチして、WhatsApp または Slack のフォローアップをトリガーします。

## 前提条件

- [Markifact](https://www.markifact.com) アカウント（無料枠あり）
- Markifact ダッシュボードで 1 つ以上のプラットフォームが接続されていること
  （Google Ads、Meta、GA4、Shopify など）
- 接続設定については [Markifact ドキュメント](https://docs.markifact.com) を参照してください。

## エージェントで使用する

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        root_agent = Agent(
            model="gemini-flash-latest",
            name="marketing_agent",
            instruction=(
                "You are a performance marketing agent that helps users manage "
                "ad campaigns, run analytics, sync e-commerce data, and "
                "execute marketing workflows across Google Ads, Meta Ads, GA4, "
                "TikTok Ads, LinkedIn Ads, Shopify, HubSpot, and more. "
                "Always confirm with the user before any write operation."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://api.markifact.com/mcp",
                            ],
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

        !!! note

            このエージェントを初めて実行すると、OAuth によるアクセス要求のために
            ブラウザウィンドウが自動的に開きます。ブラウザで要求を承認すると、
            エージェントが接続済みアカウントへアクセスできるようになります。

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        MARKIFACT_ACCESS_TOKEN = "YOUR_MARKIFACT_ACCESS_TOKEN"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="marketing_agent",
            instruction=(
                "You are a performance marketing agent that helps users manage "
                "ad campaigns, run analytics, sync e-commerce data, and "
                "execute marketing workflows across Google Ads, Meta Ads, GA4, "
                "TikTok Ads, LinkedIn Ads, Shopify, HubSpot, and more. "
                "Always confirm with the user before any write operation."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.markifact.com/mcp",
                        headers={
                            "Authorization": f"Bearer {MARKIFACT_ACCESS_TOKEN}",
                        },
                    ),
                )
            ],
        )
        ```

        !!! note

            すでに Markifact アクセストークンを持っている場合は、OAuth のブラウザフローを
            使わずに Streamable HTTP で直接接続できます。

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "marketing_agent",
            instruction:
                "You are a performance marketing agent that helps users manage " +
                "ad campaigns, run analytics, sync e-commerce data, and " +
                "execute marketing workflows across Google Ads, Meta Ads, GA4, " +
                "TikTok Ads, LinkedIn Ads, Shopify, HubSpot, and more. " +
                "Always confirm with the user before any write operation.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://api.markifact.com/mcp",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            このエージェントを初めて実行すると、OAuth によるアクセス要求のために
            ブラウザウィンドウが自動的に開きます。ブラウザで要求を承認すると、
            エージェントが接続済みアカウントへアクセスできるようになります。

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const MARKIFACT_ACCESS_TOKEN = "YOUR_MARKIFACT_ACCESS_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "marketing_agent",
            instruction:
                "You are a performance marketing agent that helps users manage " +
                "ad campaigns, run analytics, sync e-commerce data, and " +
                "execute marketing workflows across Google Ads, Meta Ads, GA4, " +
                "TikTok Ads, LinkedIn Ads, Shopify, HubSpot, and more. " +
                "Always confirm with the user before any write operation.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://api.markifact.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${MARKIFACT_ACCESS_TOKEN}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            すでに Markifact アクセストークンを持っている場合は、OAuth のブラウザフローを
            使わずに Streamable HTTP で直接接続できます。

## 利用可能なツール

ツール | 説明
---- | -----------
`find_operations` | プラットフォームと意図のスコープ内で操作レジストリを意味検索します。
`get_operation_inputs` | 特定操作の入力に対する JSON Schema を返します。
`run_operation` | 読み取り操作を実行します。
`run_write_operation` | 承認プロトコル付きで書き込み操作を実行します。
`list_connections` | ワークスペース内の OAuth 接続を一覧表示します。
`get_file_url` | レポートやエクスポートの URL を取得します。
`read_file` | ファイル内容を読み取ります。
`upload_media` | メディアアセットをアップロードします。

## 機能

機能 | 説明
---------- | -----------
Discovery | 読み取り/書き込み分類を含む 300 以上の操作を意味検索します。
承認付き書き込み | 支出や破壊的変更を伴うすべての `run_write_operation` に 4 ステップのプロトコルを適用します。
キャンペーン管理 | すべての有料チャネルでキャンペーン、広告セット、広告を作成、編集、一時停止、再開します。
レポートとアトリビューション | クロスプラットフォームの支出、ROAS、コンバージョンのブレンド指標に加え、GA4 の経路とチャネル分析を提供します。
オーディエンス | プラットフォームごとのカスタムオーディエンス、類似オーディエンス、除外、行動ターゲティングを管理します。
クリエイティブ | アセットアップロード、バリアントローテーション、疲労検出、承認付き公開をサポートします。
コマースと CRM | Shopify、HubSpot、Klaviyo を有料メディアと同期し、クローズドループレポートを提供します。
メッセージング | 承認、アラート、リード引き継ぎのための WhatsApp と Slack 通知を提供します。
ファイル I/O | `get_file_url`、`read_file`、`upload_media` によるレポート、エクスポート、アップロードをサポートします。

## 対応プラットフォーム

カテゴリ | プラットフォーム
-------- | ---------
有料メディア | Google Ads, Meta Ads, TikTok Ads, LinkedIn Ads, Microsoft Ads, Reddit Ads, Pinterest Ads, Snapchat Ads, Amazon Ads, DV360
分析 | GA4, BigQuery, Google Search Console, Google Merchant Center
E コマース、CRM、メッセージング | Shopify, HubSpot, Klaviyo, WhatsApp, Slack
オーガニックとソーシャル | Facebook, Instagram, LinkedIn, Google Business Profile

## 追加リソース

- [Markifact ウェブサイト](https://www.markifact.com)
- [GitHub の Markifact MCP Server](https://github.com/markifact/markifact-mcp)
- [skills.sh の Skills](https://skills.sh/markifact/markifact-mcp)
