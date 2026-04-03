---
catalog_title: Windsor.ai
catalog_description: 325 以上のプラットフォームからマーケティング、営業、顧客データを照会・分析します
catalog_icon: /integrations/assets/windsor-ai.png
catalog_tags: ["mcp", "data"]
---

# ADK 向け Windsor.ai MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Windsor MCP Server](https://github.com/windsor-ai/windsor_mcp) は ADK エージェントを
[Windsor.ai](https://windsor.ai/) に接続します。Windsor.ai は 325 以上のソースから
マーケティング、営業、顧客データを統合するデータ統合プラットフォームです。
この統合により、エージェントは SQL やカスタムスクリプトを書かずに、自然言語で
クロスチャネルのビジネスデータを照会・分析できます。

## ユースケース

- **マーケティングパフォーマンス分析:** Facebook Ads、Google Ads、TikTok Ads
  など複数チャネルのキャンペーン成果を分析します。
  「先月もっとも高い ROAS を出したキャンペーンは？」のような質問をして、
  すぐにインサイトを得られます。

- **クロスチャネルレポート:** GA4、Shopify、Salesforce、HubSpot など複数
  プラットフォームのデータを組み合わせ、ビジネスパフォーマンスを統合的に
  可視化する包括的なレポートを生成します。

- **予算最適化:** 成果の低いキャンペーンを特定し、予算の非効率を検出し、
  広告チャネル全体での支出配分について AI 主導の提案を得られます。

## 前提条件

- データソースが接続された [Windsor.ai](https://windsor.ai/) アカウント
- Windsor.ai API キー
  （[onboard.windsor.ai](https://onboard.windsor.ai) で取得）

## エージェントでの使用

=== "Python"

    === "リモート MCP サーバー"

        ```python
        import os
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        # MCP スキーマ内の再帰的な $ref に必要
        # https://github.com/google/adk-python/issues/3870
        os.environ["ADK_ENABLE_JSON_SCHEMA_FOR_FUNC_DECL"] = "1"

        WINDSOR_API_KEY = "YOUR_WINDSOR_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="windsor_agent",
            instruction="Help users analyze their marketing and business data.",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url="https://mcp.windsor.ai",
                        headers={
                            "Authorization": f"Bearer {WINDSOR_API_KEY}",
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

        const WINDSOR_API_KEY = "YOUR_WINDSOR_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "windsor_agent",
            instruction: "Help users analyze their marketing and business data.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.windsor.ai",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${WINDSOR_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 機能

Windsor MCP は統合済みビジネスデータに対する自然言語インターフェースを提供します。
個別のツールを公開する代わりに、質問を解釈し、接続済みデータソースから
構造化されたインサイトを返します。

Capability | Description
---------- | -----------
Data querying | 325 以上の接続プラットフォームから正規化データを照会
Performance analysis | チャネル横断で KPI、トレンド、キャンペーン指標を分析
Report generation | マーケティングダッシュボードとクロスチャネル成果レポートを生成
Budget analysis | 支出の非効率を特定し、最適化提案を取得
Anomaly detection | 成果データの外れ値や異常パターンを検出

## サポートされるデータソース

Windsor.ai は 325 以上のプラットフォームに接続しており、次が含まれます。

- **広告:** Facebook Ads、Google Ads、TikTok Ads、LinkedIn Ads、Microsoft Ads
- **分析:** Google Analytics 4、Adobe Analytics
- **CRM:** Salesforce、HubSpot
- **E-commerce:** Shopify
- **その他:** [full list of connectors](https://windsor.ai/) は Windsor.ai のサイトを参照

## 追加リソース

- [Windsor MCP Server Repository](https://github.com/windsor-ai/windsor_mcp)
- [Windsor.ai Documentation](https://windsor.ai/documentation/windsor-mcp/)
- [Windsor MCP Introduction](https://windsor.ai/introducing-windsor-mcp/)
- [Windsor MCP Use Cases & Examples](https://windsor.ai/how-to-use-windsor-mcp-examples-use-cases/)
