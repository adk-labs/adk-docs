---
catalog_title: Supermetrics
catalog_description: 실시간 마케팅, 광고, CRM 데이터를 조회하고 분석합니다
catalog_icon: /integrations/assets/supermetrics.png
catalog_tags: ["mcp", "data"]
---

# ADK용 Supermetrics MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Supermetrics MCP Server](https://mcp.supermetrics.com)는 ADK 에이전트를
[Supermetrics](https://supermetrics.com/) 플랫폼에 연결하여 Google Ads,
Meta Ads, LinkedIn Ads, Google Analytics 4 등 100개 이상의 소스에 걸친
마케팅 데이터에 접근할 수 있게 합니다. 에이전트는 데이터 소스를 탐색하고,
사용 가능한 지표를 살펴보고, 자연어로 연결된 계정에 대해 질의를 실행할 수 있습니다.

## 사용 사례

- **마케팅 성과 보고:** 캠페인과 기간 전반에 걸쳐 노출, 클릭, 지출, 전환을 질의합니다.
  여러 플랫폼의 데이터를 하나의 응답으로 집계하는 자동화 리포트를 구축할 수 있습니다.

- **크로스 플랫폼 분석:** Google Ads, Meta Ads, LinkedIn Ads 등 여러 채널의
  성과를 나란히 비교할 수 있으며, 기반 플랫폼과 무관하게 일관된 질의 인터페이스를
  사용할 수 있습니다.

- **캠페인 모니터링:** 활성 캠페인과 광고 계정의 최신 지표를 가져와 에이전트가
  이상 징후를 감지하고, 집행 속도를 추적하거나, 일일 성과를 요약하도록 할 수 있습니다.

- **데이터 탐색:** 질의를 구성하기 전에 어떤 데이터 소스, 계정, 필드가 사용자에게
  제공되는지 확인해 각 사용자의 연결 상태에 맞춰 에이전트를 동적으로 적응시킬 수 있습니다.

## 전제 조건

- [Supermetrics 계정](https://supermetrics.com/) 생성
  (첫 로그인 시 14일 무료 체험이 자동으로 생성됨)
- [Supermetrics Hub](https://hub.supermetrics.com/)에서 API 키 생성

## 에이전트와 함께 사용

=== "Python"

    === "원격 MCP 서버"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        SUPERMETRICS_API_KEY = "YOUR_SUPERMETRICS_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="supermetrics_agent",
            instruction="Help users query and analyze their marketing data from Supermetrics",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.supermetrics.com/mcp",
                        headers={
                            "Authorization": f"Bearer {SUPERMETRICS_API_KEY}",
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

        const SUPERMETRICS_API_KEY = "YOUR_SUPERMETRICS_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "supermetrics_agent",
            instruction: "Help users query and analyze their marketing data from Supermetrics",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.supermetrics.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${SUPERMETRICS_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note "질의 워크플로"

    데이터 조회는 다단계 워크플로를 따릅니다. 사용자 요청이 들어오면 먼저
    `get_today`로 현재 날짜를 가져옵니다. 다음으로 `data_source_discovery`로
    데이터 소스를 찾고, `accounts_discovery`로 연결된 계정을 확인하며,
    `field_discovery`로 사용 가능한 필드를 조사합니다. 그 뒤 `data_query`로
    질의를 제출하고, 반환된 `schedule_id`를 사용해 `get_async_query_results`를
    반복 호출하여 결과가 준비될 때까지 폴링합니다.

## 사용 가능한 도구

Tool | Description
---- | -----------
`data_source_discovery` | 사용 가능한 마케팅 데이터 소스(Google Ads, Meta Ads 등)와 해당 ID 목록 조회
`accounts_discovery` | 특정 데이터 소스에 연결된 계정 탐색
`field_discovery` | 데이터 소스에서 사용 가능한 메트릭과 차원 탐색
`data_query` | 데이터 질의 제출. 비동기 결과 조회용 `schedule_id` 반환
`get_async_query_results` | `schedule_id`로 제출된 질의의 결과를 폴링하고 조회
`user_info` | 인증된 사용자의 프로필, 팀 정보, 라이선스 상태 조회
`get_today` | 질의 날짜 범위 파라미터에 적합한 형식으로 현재 날짜 반환

## 추가 리소스

- [Supermetrics Hub](https://hub.supermetrics.com/)
- [Supermetrics Knowledge Base](https://docs.supermetrics.com/)
- [Data Source Documentation](https://docs.supermetrics.com/docs/connect)
- [OpenAPI Specification](https://mcp.supermetrics.com/openapi.json)
