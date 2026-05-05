---
catalog_title: Markifact
catalog_description: Google Ads, Meta, GA4, TikTok 및 15개 이상의 플랫폼에서 마케팅 운영 관리
catalog_icon: /integrations/assets/markifact.png
catalog_tags: ["mcp", "connectors"]
---

# ADK용 Markifact MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Markifact MCP Server](https://github.com/markifact/markifact-mcp)는 ADK 에이전트를
[Markifact](https://www.markifact.com)에 연결합니다. Markifact는 Google Ads,
Meta Ads, GA4, TikTok Ads, Shopify를 포함한 20개 이상의 플랫폼에서 300개 이상의
작업을 제공하는 AI 마케팅 자동화 플랫폼입니다. 이 통합을 사용하면 에이전트가 자연어로
캠페인을 관리하고, 성과를 분석하고, 마케팅 워크플로를 자동화할 수 있으며, 모든 쓰기
작업에는 승인 프롬프트가 적용됩니다.

## 사용 사례

- **지출 위생 관리**: Google Ads, Meta, TikTok, LinkedIn 전반의 낭비 예산을 찾아
  구체적인 일시 중지 및 재배분 권장 사항을 제시합니다.
- **통합 리포팅**: 하나의 프롬프트로 연결된 모든 채널과 GA4 전반의 혼합 지출, ROAS,
  CAC, 전환 변화량을 생성합니다.
- **브리프에서 라이브 캠페인까지**: 한 줄 브리프에서 시작해 사람의 승인을 기다리는
  Search, Performance Max, Meta Advantage+, TikTok 또는 LinkedIn 캠페인 초안을 만듭니다.
- **리드 핸드오프**: Meta 및 LinkedIn 리드 양식을 수집하고 HubSpot 또는 Klaviyo에서
  보강한 뒤 WhatsApp 또는 Slack 후속 조치를 트리거합니다.

## 사전 요구 사항

- [Markifact](https://www.markifact.com) 계정(무료 티어 사용 가능)
- Markifact 대시보드에서 연결된 플랫폼이 하나 이상 있어야 함(Google Ads, Meta, GA4,
  Shopify 등)
- 연결 설정은 [Markifact 문서](https://docs.markifact.com)를 참조하세요.

## 에이전트에서 사용하기

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

            이 에이전트를 처음 실행하면 OAuth를 통해 액세스를 요청하는 브라우저 창이
            자동으로 열립니다. 브라우저에서 요청을 승인하면 에이전트가 연결된 계정에
            액세스할 수 있습니다.

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

            이미 Markifact 액세스 토큰이 있다면 OAuth 브라우저 흐름 없이 Streamable HTTP로
            직접 연결할 수 있습니다.

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

            이 에이전트를 처음 실행하면 OAuth를 통해 액세스를 요청하는 브라우저 창이
            자동으로 열립니다. 브라우저에서 요청을 승인하면 에이전트가 연결된 계정에
            액세스할 수 있습니다.

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

            이미 Markifact 액세스 토큰이 있다면 OAuth 브라우저 흐름 없이 Streamable HTTP로
            직접 연결할 수 있습니다.

## 사용 가능한 도구

도구 | 설명
---- | -----------
`find_operations` | 플랫폼과 의도 범위 안에서 작업 레지스트리를 의미 기반으로 검색합니다.
`get_operation_inputs` | 특정 작업 입력에 대한 JSON Schema를 반환합니다.
`run_operation` | 읽기 작업을 실행합니다.
`run_write_operation` | 승인 프로토콜이 적용된 쓰기 작업을 실행합니다.
`list_connections` | 워크스페이스의 OAuth 연결을 나열합니다.
`get_file_url` | 리포트 및 내보내기 파일 URL을 가져옵니다.
`read_file` | 파일 내용을 읽습니다.
`upload_media` | 미디어 에셋을 업로드합니다.

## 기능

기능 | 설명
---------- | -----------
Discovery | 읽기/쓰기 분류가 포함된 300개 이상의 작업을 의미 기반으로 검색합니다.
승인 기반 쓰기 | 지출 또는 파괴적 변경이 포함된 모든 `run_write_operation`에 4단계 프로토콜을 적용합니다.
캠페인 관리 | 모든 유료 채널에서 캠페인, 광고 세트, 광고를 만들고, 편집하고, 일시 중지하고, 재개합니다.
리포팅 및 어트리뷰션 | 크로스 플랫폼 지출, ROAS, 전환 혼합 지표와 GA4 경로 및 채널 분석을 제공합니다.
오디언스 | 플랫폼별 커스텀 오디언스, 유사 오디언스, 제외, 행동 타기팅을 관리합니다.
크리에이티브 | 에셋 업로드, 변형 로테이션, 피로도 감지, 승인 기반 게시를 지원합니다.
커머스 및 CRM | Shopify, HubSpot, Klaviyo를 유료 미디어와 동기화해 폐쇄 루프 리포팅을 제공합니다.
메시징 | 승인, 알림, 리드 핸드오프를 위한 WhatsApp 및 Slack 알림을 제공합니다.
파일 I/O | `get_file_url`, `read_file`, `upload_media`를 통한 리포트, 내보내기, 업로드를 지원합니다.

## 지원 플랫폼

카테고리 | 플랫폼
-------- | ---------
유료 미디어 | Google Ads, Meta Ads, TikTok Ads, LinkedIn Ads, Microsoft Ads, Reddit Ads, Pinterest Ads, Snapchat Ads, Amazon Ads, DV360
분석 | GA4, BigQuery, Google Search Console, Google Merchant Center
이커머스, CRM, 메시징 | Shopify, HubSpot, Klaviyo, WhatsApp, Slack
오가닉 및 소셜 | Facebook, Instagram, LinkedIn, Google Business Profile

## 추가 리소스

- [Markifact 웹사이트](https://www.markifact.com)
- [GitHub의 Markifact MCP Server](https://github.com/markifact/markifact-mcp)
- [skills.sh의 Skills](https://skills.sh/markifact/markifact-mcp)
