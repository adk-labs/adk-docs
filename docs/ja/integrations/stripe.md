---
catalog_title: Stripe
catalog_description: 決済、顧客、サブスクリプション、請求書を管理します
catalog_icon: /adk-docs/integrations/assets/stripe.png
catalog_tags: ["mcp"]
---

# ADK 向け Stripe MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Stripe MCP Server](https://docs.stripe.com/mcp) は ADK エージェントを
[Stripe](https://stripe.com/) エコシステムへ接続します。
この連携により、エージェントは自然言語で決済、顧客、サブスクリプション、請求書を管理し、
自動化されたコマースワークフローと財務運用を実現できます。

## ユースケース

- **決済運用の自動化**: 会話コマンドで支払いリンク作成、
  返金処理、PaymentIntent 一覧取得を行います。

- **請求処理の効率化**: 開発環境を離れずに
  請求書作成/確定、明細追加、未払い追跡を実行できます。

- **ビジネスインサイトへのアクセス**: アカウント残高照会、商品/価格一覧、
  Stripe リソース横断検索でデータ駆動の意思決定を行います。

## 前提条件

- [Stripe アカウント](https://dashboard.stripe.com/register) の作成
- Stripe Dashboard で [Restricted API key](https://dashboard.stripe.com/apikeys) を生成

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="stripe_agent",
            instruction="Help users manage their Stripe account",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@stripe/mcp",
                                "--tools=all",
                                # (Optional) Specify which tools to enable
                                # "--tools=customers.read,invoices.read,products.read",
                            ],
                            env={
                                "STRIPE_SECRET_KEY": STRIPE_SECRET_KEY,
                            }
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="stripe_agent",
            instruction="Help users manage their Stripe account",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url="https://mcp.stripe.com",
                        headers={
                            "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "stripe_agent",
            instruction: "Help users manage their Stripe account",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "@stripe/mcp",
                            "--tools=all",
                            // (Optional) Specify which tools to enable
                            // "--tools=customers.read,invoices.read,products.read",
                        ],
                        env: {
                            STRIPE_SECRET_KEY: STRIPE_SECRET_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const STRIPE_SECRET_KEY = "YOUR_STRIPE_SECRET_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "stripe_agent",
            instruction: "Help users manage their Stripe account",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.stripe.com",
                    header: {
                        Authorization: `Bearer ${STRIPE_SECRET_KEY}`,
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! tip "ベストプラクティス"

    ツール操作に人間確認を挟む設定を有効化し、
    プロンプトインジェクションリスク軽減のため、Stripe MCP サーバーを他 MCP サーバーと併用する際は
    とくに注意してください。

## 利用可能なツール

Resource | Tool | API
-------- | ---- | ----
Account | `get_stripe_account_info` | Retrieve account
Balance | `retrieve_balance` | Retrieve balance
Coupon | `create_coupon` | Create coupon
Coupon | `list_coupons` | List coupons
Customer | `create_customer` | Create customer
Customer | `list_customers` | List customers
Dispute | `list_disputes` | List disputes
Dispute | `update_dispute` | Update dispute
Invoice | `create_invoice` | Create invoice
Invoice | `create_invoice_item` | Create invoice item
Invoice | `finalize_invoice` | Finalize invoice
Invoice | `list_invoices` | List invoices
Payment Link | `create_payment_link` | Create payment link
PaymentIntent | `list_payment_intents` | List PaymentIntents
Price | `create_price` | Create price
Price | `list_prices` | List prices
Product | `create_product` | Create product
Product | `list_products` | List products
Refund | `create_refund` | Create refund
Subscription | `cancel_subscription` | Cancel subscription
Subscription | `list_subscriptions` | List subscriptions
Subscription | `update_subscription` | Update subscription
Others | `search_stripe_resources` | Search Stripe resources
Others | `fetch_stripe_resources` | Fetch Stripe object
Others | `search_stripe_documentation` | Search Stripe knowledge

## 追加リソース

- [Stripe MCP Server Documentation](https://docs.stripe.com/mcp)
- [Stripe MCP Server on GitHub](https://github.com/stripe/ai/tree/main/tools/modelcontextprotocol)
- [Build on Stripe with LLMs](https://docs.stripe.com/building-with-llms)
- [Add Stripe to your agentic workflows](https://docs.stripe.com/agents)
