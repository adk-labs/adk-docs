---
catalog_title: Stripe
catalog_description: 결제, 고객, 구독, 인보이스를 관리합니다
catalog_icon: /adk-docs/integrations/assets/stripe.png
catalog_tags: ["mcp"]
---

# ADK용 Stripe MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Stripe MCP Server](https://docs.stripe.com/mcp)는 ADK 에이전트를
[Stripe](https://stripe.com/) 생태계와 연결합니다.
이 통합을 통해 에이전트는 자연어로 결제, 고객, 구독, 인보이스를 관리해
자동화된 커머스 워크플로와 재무 운영을 구현할 수 있습니다.

## 사용 사례

- **결제 운영 자동화**: 대화형 명령으로 결제 링크 생성,
  환불 처리, payment intent 목록 조회를 수행합니다.

- **인보이스 처리 간소화**: 개발 환경을 벗어나지 않고
  인보이스 생성/확정, 라인 아이템 추가, 미수금 추적을 수행합니다.

- **비즈니스 인사이트 확보**: 계정 잔액 조회, 상품/가격 목록 조회,
  Stripe 리소스 검색으로 데이터 기반 의사결정을 수행합니다.

## 사전 준비 사항

- [Stripe 계정](https://dashboard.stripe.com/register) 생성
- Stripe Dashboard에서 [Restricted API key](https://dashboard.stripe.com/apikeys) 생성

## 에이전트와 함께 사용

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

!!! tip "모범 사례"

    도구 실행에 대한 사람 승인(human confirmation)을 활성화하고,
    프롬프트 인젝션 위험을 줄이기 위해 Stripe MCP 서버를 다른 MCP 서버와 함께 사용할 때는
    특히 주의하세요.

## 사용 가능한 도구

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

## 추가 리소스

- [Stripe MCP Server Documentation](https://docs.stripe.com/mcp)
- [Stripe MCP Server on GitHub](https://github.com/stripe/ai/tree/main/tools/modelcontextprotocol)
- [Build on Stripe with LLMs](https://docs.stripe.com/building-with-llms)
- [Add Stripe to your agentic workflows](https://docs.stripe.com/agents)
