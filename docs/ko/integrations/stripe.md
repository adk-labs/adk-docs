---
catalog_title: Stripe
catalog_description: 결제, 고객, 구독, 인보이스를 관리합니다
catalog_icon: /integrations/assets/stripe.png
catalog_tags: ["mcp"]
---

# ADK용 Stripe MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Stripe MCP Server](https://docs.stripe.com/mcp)는 ADK 에이전트를
[Stripe](https://stripe.com/) 생태계와 연결합니다.
이 통합을 통해 에이전트는 자연어로 결제, 고객, 구독, 인보이스를 관리해
자동화된 커머스 워크플로와 재무 운영을 구현할 수 있습니다.

## 사용 사례

- **결제 운영 자동화**: 대화형 명령으로 결제 링크 생성,
  환불 처리, 결제 인텐트(PaymentIntent) 목록 조회를 수행합니다.

- **인보이스 처리 간소화**: 개발 환경을 벗어나지 않고
  인보이스 생성/확정, 라인 아이템 추가, 미수금 추적을 수행합니다.

- **비즈니스 인사이트 확보**: 계정 잔액 조회, 상품/가격 목록 조회,
  Stripe 리소스 검색으로 데이터 기반 의사결정을 수행합니다.

## 사전 요구사항

- [Stripe 계정](https://dashboard.stripe.com/register) 생성
- Stripe 대시보드에서 [제한된 API 키(Restricted API key)](https://dashboard.stripe.com/apikeys) 생성

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
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${STRIPE_SECRET_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! tip "모범 사례"

    도구 실행 승인(Tool Confirmation)을 활성화하고,
    프롬프트 인젝션 위험을 줄이기 위해 Stripe MCP 서버를 다른 MCP 서버와 함께 사용할 때는
    특히 주의하세요.

## 사용 가능한 도구

리소스 | 도구 | API 작업
-------- | ---- | ----
계정(Account) | `get_stripe_account_info` | 계정 정보 조회
잔액(Balance) | `retrieve_balance` | 잔액 조회
쿠폰(Coupon) | `create_coupon` | 쿠폰 생성
쿠폰(Coupon) | `list_coupons` | 쿠폰 목록 조회
고객(Customer) | `create_customer` | 고객 생성
고객(Customer) | `list_customers` | 고객 목록 조회
분쟁(Dispute) | `list_disputes` | 분쟁 목록 조회
분쟁(Dispute) | `update_dispute` | 분쟁 업데이트
인보이스(Invoice) | `create_invoice` | 인보이스 생성
인보이스(Invoice) | `create_invoice_item` | 인보이스 항목 생성
인보이스(Invoice) | `finalize_invoice` | 인보이스 확정
인보이스(Invoice) | `list_invoices` | 인보이스 목록 조회
결제 링크(Payment Link) | `create_payment_link` | 결제 링크 생성
PaymentIntent | `list_payment_intents` | PaymentIntent 목록 조회
가격(Price) | `create_price` | 가격 생성
가격(Price) | `list_prices` | 가격 목록 조회
상품(Product) | `create_product` | 상품 생성
상품(Product) | `list_products` | 상품 목록 조회
환불(Refund) | `create_refund` | 환불 생성
구독(Subscription) | `cancel_subscription` | 구독 취소
구독(Subscription) | `list_subscriptions` | 구독 목록 조회
구독(Subscription) | `update_subscription` | 구독 업데이트
기타 | `search_stripe_resources` | Stripe 리소스 검색
기타 | `fetch_stripe_resources` | Stripe 객체 조회
기타 | `search_stripe_documentation` | Stripe 문서 검색

## 추가 리소스

- [Stripe MCP 서버 문서](https://docs.stripe.com/mcp)
- [GitHub의 Stripe MCP 서버](https://github.com/stripe/ai/tree/main/tools/modelcontextprotocol)
- [LLM으로 Stripe 기반 서비스 구축하기](https://docs.stripe.com/building-with-llms)
- [에이전트 워크플로에 Stripe 추가하기](https://docs.stripe.com/agents)
