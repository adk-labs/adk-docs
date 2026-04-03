---
catalog_title: Supermetrics
catalog_description: リアルタイムのマーケティング、広告、CRM データを取得して分析します
catalog_icon: /integrations/assets/supermetrics.png
catalog_tags: ["mcp", "data"]
---

# ADK 向け Supermetrics MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Supermetrics MCP Server](https://mcp.supermetrics.com) は ADK エージェントを
[Supermetrics](https://supermetrics.com/) プラットフォームに接続し、
Google Ads、Meta Ads、LinkedIn Ads、Google Analytics 4 を含む
100 以上のソースにまたがるマーケティングデータへアクセスできるようにします。
エージェントはデータソースを発見し、利用可能な指標を確認し、接続済みアカウントに
対するクエリを自然言語で実行できます。

## ユースケース

- **マーケティングパフォーマンスレポート:** キャンペーンや期間をまたいで
  インプレッション、クリック、支出、コンバージョンを照会できます。
  複数プラットフォームのデータを 1 つの応答に集約する自動レポートを構築できます。

- **クロスプラットフォーム分析:** Google Ads、Meta Ads、LinkedIn Ads など
  複数チャネルのパフォーマンスを横並びで比較できます。基盤プラットフォームに
  依存しない一貫したクエリインターフェースを使えます。

- **キャンペーン監視:** 稼働中キャンペーンや広告アカウントの最新指標を取得し、
  エージェントに異常検知、配信ペースの追跡、日次パフォーマンスの要約をさせられます。

- **データ探索:** クエリを組み立てる前に、どのデータソース・アカウント・フィールドが
  そのユーザーに利用可能かを確認できます。これによりユーザーごとの接続状態に
  応じてエージェントを動的に適応させられます。

## 前提条件

- [Supermetrics アカウント](https://supermetrics.com/) を作成
  （初回ログイン時に 14 日間の無料トライアルが自動作成されます）
- [Supermetrics Hub](https://hub.supermetrics.com/) で API キーを生成

## エージェントでの使用

=== "Python"

    === "リモート MCP サーバー"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        SUPERMETRICS_API_KEY = "YOUR_SUPERMETRICS_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="supermetrics_agent",
            instruction="Help users query and analyze their marketing data from Supermetrics",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.supermetrics.com/mcp",
                        headers={
                            "Authorization": f"Bearer {SUPERMETRICS_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "リモート MCP サーバー"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const SUPERMETRICS_API_KEY = "YOUR_SUPERMETRICS_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "supermetrics_agent",
            instruction: "Help users query and analyze their marketing data from Supermetrics",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.supermetrics.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${SUPERMETRICS_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note "クエリワークフロー"

    データ取得は複数段階のワークフローに従います。ユーザーリクエストが来たら、
    まず `get_today` で現在日付を取得します。次に `data_source_discovery` で
    データソースを見つけ、`accounts_discovery` で接続済みアカウントを探し、
    `field_discovery` で利用可能なフィールドを確認します。その後 `data_query`
    でクエリを送信し、返された `schedule_id` を使って `get_async_query_results` を
    ポーリングし、結果が準備できるまで待ちます。

## 利用可能なツール

Tool | Description
---- | -----------
`data_source_discovery` | 利用可能なマーケティングデータソース（Google Ads、Meta Ads など）とその ID を一覧表示
`accounts_discovery` | 特定データソースに接続されたアカウントを探索
`field_discovery` | データソースで利用可能な指標とディメンションを探索
`data_query` | データクエリを送信し、非同期結果取得用の `schedule_id` を返す
`get_async_query_results` | `schedule_id` で送信済みクエリの結果をポーリングして取得
`user_info` | 認証済みユーザーのプロフィール、チーム情報、ライセンス状態を取得
`get_today` | クエリの日付範囲パラメータに適した形式で現在日付を取得

## 追加リソース

- [Supermetrics Hub](https://hub.supermetrics.com/)
- [Supermetrics Knowledge Base](https://docs.supermetrics.com/)
- [Data Source Documentation](https://docs.supermetrics.com/docs/connect)
- [OpenAPI Specification](https://mcp.supermetrics.com/openapi.json)
