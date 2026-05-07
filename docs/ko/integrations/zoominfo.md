---
catalog_title: ZoomInfo
catalog_description: 회사를 찾고, 연락처를 보강하며, go-to-market 인텔리전스를 표시합니다
catalog_icon: /integrations/assets/zoominfo.png
catalog_tags: ["mcp", "connectors"]
---

# ADK용 ZoomInfo MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[ZoomInfo MCP Server](https://docs.zoominfo.com/docs/zi-api-mcp-overview)는
ADK 에이전트를 [ZoomInfo](https://www.zoominfo.com/) B2B 인텔리전스
플랫폼에 연결하여 1억 개 이상의 회사 프로필, 3억 개 이상의 전문 연락처,
go-to-market 신호에 접근할 수 있게 합니다. 이 통합은 에이전트가 자연어로
잠재 고객을 찾고, 레코드를 보강하고, 의도 신호를 표시하고, 계정을 조사하는
능력을 제공합니다.

## 사용 사례

- **잠재 고객 탐색:** 업종, 위치, 회사 규모, 직무, 직급, 기술 스택 같은
  필터를 사용해 ICP에 맞는 회사와 연락처를 찾습니다.

- **계정 및 연락처 보강:** 에이전트 워크플로 안에서 기존 레코드에 매출,
  직원 수, 이메일, 직통 번호, 투자 유치 정보 같은 검증된 기업 및 인구통계
  데이터를 추가합니다.

- **Go-to-Market 신호 감지:** 의도 신호, 리더십 변경, 전략적 scoop을
  표시하여 적절한 시점에 구매자에게 접근할 수 있게 합니다.

## 전제 조건

- [ZoomInfo 계정](https://www.zoominfo.com/free-trial-contact-sales)에 가입
- ZoomInfo SalesOS 또는 Copilot 구독

## 에이전트와 함께 사용

=== "Python"

    === "로컬 MCP 서버"

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

    === "로컬 MCP 서버"

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

    이 에이전트를 처음 실행하면 OAuth로 접근 권한을 요청하기 위해 브라우저
    창이 자동으로 열립니다. 또는 콘솔에 출력되는 승인 URL을 사용할 수도
    있습니다. 에이전트가 ZoomInfo 데이터에 접근할 수 있도록 이 요청을
    승인해야 합니다.

## 사용 가능한 도구

Tool | Description
---- | -----------
`search_companies` | 이름, 업종, 위치, 직원 수, 매출, 기술 스택, 성장 지표, 투자 정보를 기준으로 ZoomInfo 회사 데이터베이스를 검색합니다
`search_contacts` | 이름, 직무, 관리 레벨, 부서, 회사, 위치, 정확도 점수를 기준으로 ZoomInfo 연락처 데이터베이스를 검색합니다
`enrich_companies` | 호출당 최대 10개 회사에 대해 매출, 직원 수, 투자, 기술 스택, 기업 구조 등 전체 회사 프로필을 가져옵니다
`enrich_contacts` | 호출당 최대 10개 연락처에 대해 이메일, 전화번호, 직무, 경력, 정확도 점수 같은 검증된 비즈니스 연락처 세부 정보를 가져옵니다
`find_similar_companies` | ML 기반 기업 특성 매칭으로 기준 회사와 유사한 회사를 찾으며, lookalike prospecting 및 영역 확장에 유용합니다
`find_similar_contacts` | 기준 인물과 유사한 연락처를 찾고, 선택적으로 대상 회사로 제한할 수 있으며, ML 기반 페르소나 매칭을 사용합니다
`get_recommended_contacts` | PROSPECTING, DEAL_ACCELERATION, RENEWAL_AND_GROWTH 같은 영업 모션을 기준으로 대상 회사의 AI 순위 연락처 추천을 가져옵니다
`search_intent` | 신호 점수와 대상 고객 강도 필터를 사용해 ZoomInfo 데이터베이스 전반에서 특정 주제를 적극적으로 조사 중인 회사를 검색합니다
`enrich_intent` | 특정 회사의 구매자 의도 신호, 즉 조사한 주제, 신호 점수, 대상 고객 강도, 기간을 가져옵니다
`search_scoops` | 리더십 변경, 투자 이벤트, 제품 출시, 파트너십 등 실시간 비즈니스 인텔리전스 신호를 모든 회사에서 검색합니다
`enrich_scoops` | 특정 회사의 최신 scoop을 가져와 단순 헤드라인이 아닌 신호의 전체 맥락을 제공합니다
`enrich_news` | 특정 회사의 최근 뉴스 보도를 가져오며 투자, M&A, 임원 이동, 제품 출시 같은 카테고리로 필터링할 수 있습니다
`account_research` | 회사 개요, 재무, 경쟁사, 구매 위원회, 딜 상태, 참여 활동 같은 AI 생성 전략 인텔리전스를 가져옵니다
`contact_research` | 특정 인물의 경력 이력, 전문성, CRM 레코드, 아웃리치 맥락 같은 AI 생성 전문 배경 정보를 가져옵니다
`lookup` | 업종, 관리 레벨, 광역 지역, 기술 제품, 의도 주제 등 검색 필터에 사용할 표준화된 참조 데이터를 조회합니다
`submit_feedback` | 데이터 품질, 기능 요청, 접근 문제 또는 기타 주제에 대한 ZoomInfo MCP 도구 피드백을 제출합니다

## 추가 리소스

- [ZoomInfo MCP Overview](https://docs.zoominfo.com/docs/zi-api-mcp-overview)
- [ZoomInfo Developer Documentation](https://docs.zoominfo.com/)
