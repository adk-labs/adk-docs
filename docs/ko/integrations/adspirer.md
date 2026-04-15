---
catalog_title: Adspirer
catalog_description: Google, Meta, LinkedIn, TikTok Ads 전반의 광고 캠페인을 생성, 관리, 최적화
catalog_icon: /integrations/assets/adspirer.png
catalog_tags: ["mcp", "connectors"]
---

# ADK용 Adspirer MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Adspirer MCP Server](https://github.com/amekala/ads-mcp)는 ADK 에이전트를
[Adspirer](https://www.adspirer.com/)와 연결합니다. Adspirer는 Google Ads,
Meta Ads, LinkedIn Ads, TikTok Ads 전반에서 100개 이상의 도구를 제공하는
AI 기반 광고 플랫폼입니다. 이 통합을 사용하면 키워드 조사와 타깃 계획부터
캠페인 실행과 성과 분석까지, 자연어만으로 광고 캠페인을 생성, 관리, 최적화할 수 있습니다.

## 작동 방식

Adspirer는 ADK 에이전트와 광고 플랫폼 사이를 이어 주는 원격 MCP 서버입니다.
에이전트는 Adspirer의 MCP 엔드포인트에 연결하고, OAuth 2.1로 인증한 뒤,
광고 플랫폼 API에 직접 대응되는 100개 이상의 도구를 사용할 수 있습니다.

일반적인 흐름은 다음과 같습니다.

1. **연결**: ADK 에이전트가 `https://mcp.adspirer.com/mcp`에 연결하고 OAuth 2.1로 인증합니다. 처음 실행하면 브라우저 창이 열리며 로그인 후 광고 계정 접근을 승인해야 합니다.
2. **검색**: 에이전트가 연결된 광고 플랫폼(Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads)에 따라 사용 가능한 도구를 검색합니다.
3. **실행**: 이제 에이전트는 자연어만으로 키워드 조사, 잠재고객 계획, 캠페인 생성, 성과 분석, 예산 최적화, 광고 관리까지 전체 캠페인 수명 주기를 실행할 수 있습니다.

Adspirer는 OAuth 토큰 관리, 광고 플랫폼 API 호출, 안전 가드레일(예: 캠페인 삭제 금지, 기존 예산 수정 제한)을 처리하므로, 기본 보호 장치와 함께 에이전트가 자율적으로 동작할 수 있습니다.

## 사용 사례

- **캠페인 생성**: 자연어만으로 Google, Meta, LinkedIn, TikTok 전반에 걸친 복잡한 광고 캠페인을 실행할 수 있습니다. 대시보드에 직접 들어가지 않고도 검색, Performance Max, YouTube, Demand Gen, 이미지, 동영상, 캐러셀 캠페인을 만들 수 있습니다.
- **성과 분석**: 연결된 모든 광고 플랫폼의 캠페인 지표를 분석할 수 있습니다. "어떤 캠페인의 ROAS가 가장 좋은가요?" 또는 "어디에서 예산을 낭비하고 있나요?" 같은 질문에 최적화 권장사항과 함께 답할 수 있습니다.
- **키워드 조사 및 기획**: Google Keyword Planner의 실제 CPC, 검색량, 경쟁도 데이터를 사용해 키워드를 조사할 수 있습니다. 키워드 전략을 세우고 바로 캠페인에 추가할 수 있습니다.
- **예산 최적화**: 성과가 낮은 캠페인을 찾고, 예산 비효율을 감지하며, 채널 및 캠페인별 지출 배분에 대한 AI 기반 권장사항을 받을 수 있습니다.
- **광고 관리**: 기존 캠페인에 새 광고 그룹, 광고 세트, 광고를 추가할 수 있습니다. 크리에이티브 A/B 테스트, 광고 문구 업데이트, 키워드 관리, 캠페인 일시중지 및 재개를 모두 에이전트를 통해 수행할 수 있습니다.

## 사전 준비 사항

- [Adspirer](https://www.adspirer.com/) 계정이 필요합니다(무료 플랜 사용 가능).
- 적어도 하나의 광고 플랫폼(Google Ads, Meta Ads, LinkedIn Ads, TikTok Ads)이 연결되어 있어야 합니다. 가입 후 Adspirer 대시보드에서 연결할 수 있습니다.
- 단계별 설정 방법은 [Quickstart guide](https://www.adspirer.com/docs/quickstart)를 참고하세요.

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        에이전트를 처음 실행하면 OAuth 접근 권한을 요청하기 위해 브라우저 창이 자동으로 열립니다. 브라우저에서 요청을 승인하면 연결된 광고 계정에 에이전트가 접근할 수 있습니다.

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="advertising_agent",
            instruction=(
                "You are an advertising agent that helps users create, manage, "
                "and optimize ad campaigns across Google Ads, Meta Ads, "
                "LinkedIn Ads, and TikTok Ads."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.adspirer.com/mcp",
                            ],
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server"

        이미 Adspirer 액세스 토큰이 있다면 OAuth 브라우저 흐름 없이 Streamable HTTP로 직접 연결할 수 있습니다.

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        ADSPIRER_ACCESS_TOKEN = "YOUR_ADSPIRER_ACCESS_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="advertising_agent",
            instruction=(
                "You are an advertising agent that helps users create, manage, "
                "and optimize ad campaigns across Google Ads, Meta Ads, "
                "LinkedIn Ads, and TikTok Ads."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.adspirer.com/mcp",
                        headers={
                            "Authorization": f"Bearer {ADSPIRER_ACCESS_TOKEN}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        에이전트를 처음 실행하면 OAuth 접근 권한을 요청하기 위해 브라우저 창이 자동으로 열립니다. 브라우저에서 요청을 승인하면 연결된 광고 계정에 에이전트가 접근할 수 있습니다.

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "advertising_agent",
            instruction:
                "You are an advertising agent that helps users create, manage, " +
                "and optimize ad campaigns across Google Ads, Meta Ads, " +
                "LinkedIn Ads, and TikTok Ads.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.adspirer.com/mcp",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Remote MCP Server"

        이미 Adspirer 액세스 토큰이 있다면 OAuth 브라우저 흐름 없이 Streamable HTTP로 직접 연결할 수 있습니다.

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const ADSPIRER_ACCESS_TOKEN = "YOUR_ADSPIRER_ACCESS_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "advertising_agent",
            instruction:
                "You are an advertising agent that helps users create, manage, " +
                "and optimize ad campaigns across Google Ads, Meta Ads, " +
                "LinkedIn Ads, and TikTok Ads.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.adspirer.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${ADSPIRER_ACCESS_TOKEN}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 기능

Adspirer는 네 가지 주요 광고 플랫폼 전반에서 전체 광고 캠페인 수명 주기를 다룰 수 있도록 100개 이상의 MCP 도구를 제공합니다.

기능 | 설명
---------- | -----------
캠페인 생성 | 검색, PMax, YouTube, Demand Gen, 이미지, 동영상, 캐러셀 캠페인 실행
성과 분석 | 지표 분석, 이상 징후 탐지, 최적화 권장사항 제공
키워드 조사 | 실제 CPC, 검색량, 경쟁도 데이터를 활용한 키워드 조사
예산 최적화 | AI 기반 예산 배분 및 낭비 지출 탐지
광고 관리 | 광고, 광고 그룹, 광고 세트, 헤드라인, 설명문 생성 및 업데이트
잠재고객 타기팅 | 관심사, 행동, 직무, 맞춤 잠재고객 검색
에셋 관리 | 기존 크리에이티브 에셋 검증, 업로드, 검색
캠페인 제어 | 일시중지, 재개, 입찰, 예산, 타기팅 설정 업데이트

## 지원 플랫폼

플랫폼 | 도구 수 | 기능
-------- | ----- | ------------
Google Ads | 49 | 검색, PMax, YouTube, Demand Gen 캠페인, 키워드 조사, 광고 확장, 오디언스 시그널
Meta Ads | 30+ | 이미지, 동영상, 캐러셀, DCO 캠페인, 픽셀 추적, 리드 폼, 잠재고객 인사이트
LinkedIn Ads | 28 | 스폰서드 콘텐츠, 리드 생성, 대화형 광고, 인구통계 타기팅, 참여 분석
TikTok Ads | 4 | 캠페인 관리 및 성과 분석

## 추가 리소스

- [Adspirer Website](https://www.adspirer.com/)
- [Adspirer MCP Server on GitHub](https://github.com/amekala/ads-mcp)
- [Quickstart Guide](https://www.adspirer.com/docs/quickstart)
- [Tool Catalog](https://www.adspirer.com/docs/agent-skills/tools)
- [Core Workflows](https://www.adspirer.com/docs/agent-skills/workflows)
- [Ad Platform Guides](https://www.adspirer.com/docs)
