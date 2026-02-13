---
catalog_title: Paypal
catalog_description: 결제를 관리하고 인보이스 전송 및 구독 처리를 수행합니다
catalog_icon: /adk-docs/integrations/assets/paypal.png
catalog_tags: ["mcp"]
---

# ADK용 PayPal MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[PayPal MCP Server](https://github.com/paypal/paypal-mcp-server)는
ADK 에이전트를 [PayPal](https://www.paypal.com/) 생태계와 연결합니다.
이 통합을 통해 에이전트는 자연어로 결제, 인보이스,
구독, 분쟁(dispute)을 관리할 수 있어 자동화된 커머스 워크플로와
비즈니스 인사이트를 구현할 수 있습니다.

## 사용 사례

- **재무 운영 간소화**: 컨텍스트 전환 없이 채팅에서 직접 주문 생성,
  인보이스 발송, 환불 처리를 수행할 수 있습니다.
  예: "고객 X에게 청구", "주문 Y 환불".

- **구독 및 상품 관리**: 상품 생성, 구독 플랜 설정,
  구독자 세부 관리까지 반복 과금의 전체 생명주기를 자연어로 처리합니다.

- **이슈 해결 및 성과 추적**: 분쟁 클레임 요약/수락,
  배송 상태 추적, 머천트 인사이트 조회를 통해 즉시 데이터 기반 의사결정을 수행합니다.

## 사전 준비 사항

- [PayPal Developer account](https://developer.paypal.com/) 생성
- [PayPal Developer Dashboard](https://developer.paypal.com/)에서 앱 생성 및 자격 증명 확보
- 자격 증명으로 [access token 생성](https://developer.paypal.com/reference/get-an-access-token/)

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        PAYPAL_ENVIRONMENT = "SANDBOX"  # Options: "SANDBOX" or "PRODUCTION"
        PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="paypal_agent",
            instruction="Help users manage their PayPal account",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@paypal/mcp",
                                "--tools=all",
                                # (Optional) Specify which tools to enable
                                # "--tools=subscriptionPlans.list,subscriptionPlans.show",
                            ],
                            env={
                                "PAYPAL_ACCESS_TOKEN": PAYPAL_ACCESS_TOKEN,
                                "PAYPAL_ENVIRONMENT": PAYPAL_ENVIRONMENT,
                            }
                        ),
                        timeout=300,
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

        PAYPAL_MCP_ENDPOINT = "https://mcp.sandbox.paypal.com/sse"  # Production: https://mcp.paypal.com/sse
        PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="paypal_agent",
            instruction="Help users manage their PayPal account",
            tools=[
                McpToolset(
                    connection_params=SseConnectionParams(
                        url=PAYPAL_MCP_ENDPOINT,
                        headers={
                            "Authorization": f"Bearer {PAYPAL_ACCESS_TOKEN}",
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

        const PAYPAL_ENVIRONMENT = "SANDBOX"; // Options: "SANDBOX" or "PRODUCTION"
        const PAYPAL_ACCESS_TOKEN = "YOUR_PAYPAL_ACCESS_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "paypal_agent",
            instruction: "Help users manage their PayPal account",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "@paypal/mcp",
                            "--tools=all",
                            // (Optional) Specify which tools to enable
                            // "--tools=subscriptionPlans.list,subscriptionPlans.show",
                        ],
                        env: {
                            PAYPAL_ACCESS_TOKEN: PAYPAL_ACCESS_TOKEN,
                            PAYPAL_ENVIRONMENT: PAYPAL_ENVIRONMENT,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    **토큰 만료**: PayPal Access Token의 수명은 3~8시간으로 제한됩니다.
    에이전트가 동작을 멈추면 토큰 만료 여부를 확인하고 필요 시 새 토큰을 발급하세요.
    토큰 만료를 처리하기 위한 토큰 갱신 로직을 구현하는 것이 좋습니다.

## 사용 가능한 도구

### 카탈로그 관리

Tool | Description
---- | -----------
`create_product` | PayPal 카탈로그에 새 상품 생성
`list_products` | PayPal 카탈로그 상품 목록 조회
`show_product_details` | 특정 상품 상세 정보 조회
`update_product` | 기존 상품 업데이트

### 분쟁 관리

Tool | Description
---- | -----------
`list_disputes` | 선택적 필터와 함께 모든 분쟁 요약 조회
`get_dispute` | 특정 분쟁 상세 정보 조회
`accept_dispute_claim` | 분쟁 클레임을 수락해 구매자 승으로 해결

### 인보이스

Tool | Description
---- | -----------
`create_invoice` | PayPal 시스템에 새 인보이스 생성
`list_invoices` | 인보이스 목록 조회
`get_invoice` | 특정 인보이스 상세 조회
`send_invoice` | 지정 수신자에게 기존 인보이스 발송
`send_invoice_reminder` | 기존 인보이스 리마인더 발송
`cancel_sent_invoice` | 발송된 인보이스 취소
`generate_invoice_qr_code` | 인보이스 QR 코드 생성

### 결제

Tool | Description
---- | -----------
`create_order` | 제공된 상세 정보 기반 주문 생성
`create_refund` | 캡처된 결제 건 환불 처리
`get_order` | 특정 결제 상세 조회
`get_refund` | 특정 환불 상세 조회
`pay_order` | 승인된 주문 결제 캡처

### 보고 및 인사이트

Tool | Description
---- | -----------
`get_merchant_insights` | 머천트용 BI 지표 및 분석 조회
`list_transactions` | 전체 거래 목록 조회

### 배송 추적

Tool | Description
---- | -----------
`create_shipment_tracking` | PayPal 거래의 배송 추적 정보 생성
`get_shipment_tracking` | 특정 배송의 추적 정보 조회
`update_shipment_tracking` | 특정 배송의 추적 정보 업데이트

### 구독 관리

Tool | Description
---- | -----------
`cancel_subscription` | 활성 구독 취소
`create_subscription` | 새 구독 생성
`create_subscription_plan` | 새 구독 플랜 생성
`update_subscription` | 기존 구독 업데이트
`list_subscription_plans` | 구독 플랜 목록 조회
`show_subscription_details` | 특정 구독 상세 조회
`show_subscription_plan_details` | 특정 구독 플랜 상세 조회

## 구성

`--tools` 명령줄 인수로 활성화할 도구를 제어할 수 있습니다.
이는 에이전트 권한 범위를 제한할 때 유용합니다.

`--tools=all`로 전체 도구를 활성화하거나,
특정 도구 식별자를 쉼표로 구분해 지정할 수 있습니다.

**참고**: 아래 구성 식별자는 점 표기법(예: `invoices.create`)을 사용하며,
에이전트에 노출되는 도구 이름(예: `create_invoice`)과 다릅니다.

**Products**: `products.create`, `products.list`, `products.update`,
`products.show`

**Disputes**:
`disputes.list`, `disputes.get`, `disputes.create`

**Invoices**: `invoices.create`, `invoices.list`, `invoices.get`,
`invoices.send`, `invoices.sendReminder`, `invoices.cancel`,
`invoices.generateQRC`

**Orders & Payments**: `orders.create`, `orders.get`, `orders.capture`,
`payments.createRefund`, `payments.getRefunds`

**Transactions**:
`transactions.list`

**Shipment**:
`shipment.create`, `shipment.get`

**Subscriptions**: `subscriptionPlans.create`, `subscriptionPlans.list`,
`subscriptionPlans.show`, `subscriptions.create`, `subscriptions.show`,
`subscriptions.cancel`

## 추가 리소스

- [PayPal MCP Server Documentation](https://docs.paypal.ai/developer/tools/ai/mcp-quickstart)
- [PayPal MCP Server Repository](https://github.com/paypal/paypal-mcp-server)
- [PayPal Agent Tools Reference](https://docs.paypal.ai/developer/tools/ai/agent-tools-ref)
