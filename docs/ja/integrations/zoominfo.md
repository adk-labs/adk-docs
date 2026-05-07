---
catalog_title: ZoomInfo
catalog_description: 企業を検索し、連絡先を補強し、go-to-market インテリジェンスを提示します
catalog_icon: /integrations/assets/zoominfo.png
catalog_tags: ["mcp", "connectors"]
---

# ADK 向け ZoomInfo MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[ZoomInfo MCP Server](https://docs.zoominfo.com/docs/zi-api-mcp-overview) は、
ADK エージェントを [ZoomInfo](https://www.zoominfo.com/) の B2B
インテリジェンスプラットフォームに接続し、1 億件以上の企業プロファイル、
3 億件以上の専門職連絡先、go-to-market シグナルへアクセスできるようにします。
この統合により、エージェントは自然言語で見込み客を探し、レコードを補強し、
インテントシグナルを提示し、アカウントを調査できます。

## ユースケース

- **見込み客の発見:** 業界、所在地、企業規模、職種、役職レベル、技術スタック
  などのフィルタを使って ICP に一致する企業と連絡先を探します。

- **アカウントと連絡先の補強:** エージェントワークフロー内の既存レコードに、
  売上、従業員数、メールアドレス、直通番号、資金調達情報などの検証済み企業
  データと人物属性データを追加します。

- **Go-to-Market シグナル検出:** インテントシグナル、リーダーシップ変更、
  戦略的 scoop を提示し、適切なタイミングで購入者にアプローチできるようにします。

## 前提条件

- [ZoomInfo アカウント](https://www.zoominfo.com/free-trial-contact-sales)に登録
- ZoomInfo SalesOS または Copilot サブスクリプション

## エージェントでの使用

=== "Python"

    === "ローカル MCP サーバー"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters


        root_agent = Agent(
            model="gemini-flash-latest",
            name="zoominfo_agent",
            instruction="Help users find companies, enrich contacts, and surface go-to-market insights using ZoomInfo",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.zoominfo.com/mcp",
                            ]
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "ローカル MCP サーバー"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "zoominfo_agent",
            instruction: "Help users find companies, enrich contacts, and surface go-to-market insights using ZoomInfo",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.zoominfo.com/mcp",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    このエージェントを初めて実行すると、OAuth でアクセスを要求するために
    ブラウザウィンドウが自動的に開きます。代わりに、コンソールに表示される
    認可 URL を使用することもできます。エージェントが ZoomInfo データに
    アクセスできるよう、この要求を承認する必要があります。

## 利用可能なツール

Tool | Description
---- | -----------
`search_companies` | 名前、業界、所在地、従業員数、売上、技術スタック、成長指標、資金調達情報で ZoomInfo の企業データベースを検索します
`search_contacts` | 名前、職種、管理レベル、部門、企業、所在地、精度スコアで ZoomInfo の連絡先データベースを検索します
`enrich_companies` | 1 回の呼び出しで最大 10 社について、売上、従業員数、資金調達、技術スタック、企業構造などの完全な企業プロファイルを取得します
`enrich_contacts` | 1 回の呼び出しで最大 10 件の連絡先について、メール、電話番号、職種、職歴、精度スコアなどの検証済みビジネス連絡先詳細を取得します
`find_similar_companies` | ML ベースの企業属性マッチングで基準企業に似た企業を探し、lookalike prospecting やテリトリー拡張に役立てます
`find_similar_contacts` | ML ベースのペルソナマッチングを使って基準人物に似た連絡先を探し、任意で対象企業に限定できます
`get_recommended_contacts` | PROSPECTING、DEAL_ACCELERATION、RENEWAL_AND_GROWTH などの営業モーションに基づき、対象企業で AI が順位付けした連絡先推薦を取得します
`search_intent` | シグナルスコアとオーディエンス強度フィルタを使い、ZoomInfo データベース全体から特定トピックを積極的に調査している企業を検索します
`enrich_intent` | 特定企業のバイヤーインテントシグナル、つまり調査トピック、シグナルスコア、オーディエンス強度、期間を取得します
`search_scoops` | リーダーシップ変更、資金調達イベント、製品ローンチ、パートナーシップなどのリアルタイムビジネスインテリジェンスシグナルを全企業から検索します
`enrich_scoops` | 特定企業の最新 scoop を取得し、見出しだけでなくシグナルの完全な文脈を提供します
`enrich_news` | 特定企業の最近のニュース報道を取得し、資金調達、M&A、役員異動、製品ローンチなどのカテゴリでフィルタできます
`account_research` | 企業概要、財務、競合、購買委員会、案件健全性、エンゲージメント活動など、AI 生成の戦略インテリジェンスを取得します
`contact_research` | 特定人物の職歴、専門性、CRM レコード、アウトリーチ文脈など、AI 生成の専門的背景情報を取得します
`lookup` | 業界、管理レベル、大都市圏、技術製品、インテントトピックなど、検索フィルタに使う標準化済み参照データを取得します
`submit_feedback` | データ品質、機能リクエスト、アクセス問題、その他のトピックに関する ZoomInfo MCP ツールのフィードバックを送信します

## 追加リソース

- [ZoomInfo MCP Overview](https://docs.zoominfo.com/docs/zi-api-mcp-overview)
- [ZoomInfo Developer Documentation](https://docs.zoominfo.com/)
