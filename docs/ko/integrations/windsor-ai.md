---
catalog_title: Windsor.ai
catalog_description: 325개 이상의 플랫폼에서 마케팅, 영업, 고객 데이터를 조회하고 분석합니다
catalog_icon: /integrations/assets/windsor-ai.png
catalog_tags: ["mcp", "data"]
---

# ADK용 Windsor.ai MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Windsor MCP Server](https://github.com/windsor-ai/windsor_mcp)는 ADK 에이전트를
[Windsor.ai](https://windsor.ai/)에 연결합니다. Windsor.ai는 325개 이상의 소스에서
마케팅, 영업, 고객 데이터를 통합하는 데이터 통합 플랫폼입니다. 이 통합을 통해
에이전트는 SQL이나 맞춤 스크립트를 작성하지 않고도 자연어로 채널 간 비즈니스 데이터를
질의하고 분석할 수 있습니다.

## 사용 사례

- **마케팅 성과 분석:** Facebook Ads, Google Ads, TikTok Ads 등 여러 채널의
  캠페인 성과를 분석합니다. "지난달 가장 높은 ROAS를 기록한 캠페인은 무엇인가요?"
  같은 질문을 하고 즉시 인사이트를 얻을 수 있습니다.

- **크로스 채널 리포팅:** GA4, Shopify, Salesforce, HubSpot 등 여러 플랫폼의
  데이터를 결합해 비즈니스 성과를 통합적으로 보여주는 종합 리포트를 생성합니다.

- **예산 최적화:** 성과가 낮은 캠페인을 식별하고, 예산 비효율을 감지하며,
  광고 채널 전반의 지출 배분에 대한 AI 기반 권고를 받을 수 있습니다.

## 전제 조건

- 데이터 소스가 연결된 [Windsor.ai](https://windsor.ai/) 계정
- Windsor.ai API 키
  ([onboard.windsor.ai](https://onboard.windsor.ai)에서 획득)

## 에이전트와 함께 사용

=== "Python"

    === "원격 MCP 서버"

        ```python
        import os
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        # MCP 스키마의 재귀적 $ref 지원에 필요
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

    === "원격 MCP 서버"

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

## 기능

Windsor MCP는 통합된 비즈니스 데이터에 대한 자연어 인터페이스를 제공합니다.
개별 도구를 노출하는 대신, 질문을 해석하고 연결된 데이터 소스에서 구조화된
인사이트를 반환합니다.

Capability | Description
---------- | -----------
Data querying | 325개 이상의 연결 플랫폼에서 정규화된 데이터를 질의
Performance analysis | 채널 전반의 KPI, 추세, 캠페인 지표 분석
Report generation | 마케팅 대시보드와 크로스 채널 성과 리포트 생성
Budget analysis | 지출 비효율을 식별하고 최적화 권고 제공
Anomaly detection | 성과 데이터의 이상치와 비정상 패턴 감지

## 지원되는 데이터 소스

Windsor.ai는 325개 이상의 플랫폼에 연결되며, 다음이 포함됩니다.

- **광고:** Facebook Ads, Google Ads, TikTok Ads, LinkedIn Ads, Microsoft Ads
- **분석:** Google Analytics 4, Adobe Analytics
- **CRM:** Salesforce, HubSpot
- **이커머스:** Shopify
- **기타:** [full list of connectors](https://windsor.ai/)는 Windsor.ai 웹사이트 참조

## 추가 리소스

- [Windsor MCP Server Repository](https://github.com/windsor-ai/windsor_mcp)
- [Windsor.ai Documentation](https://windsor.ai/documentation/windsor-mcp/)
- [Windsor MCP Introduction](https://windsor.ai/introducing-windsor-mcp/)
- [Windsor MCP Use Cases & Examples](https://windsor.ai/how-to-use-windsor-mcp-examples-use-cases/)
