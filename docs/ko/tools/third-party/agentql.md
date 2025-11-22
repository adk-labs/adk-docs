# AgentQL

[AgentQL MCP 서버](https://github.com/tinyfish-io/agentql-mcp)는 ADK 에이전트를 [AgentQL](https://www.agentql.com/)에 연결합니다. AgentQL은 CSS 또는 XPath 선택자 대신 의미에 따라 웹 요소를 쿼리하는 시맨틱 추출 엔진입니다. 이 기능을 통해 에이전트는 자연어 정의를 사용하여 웹 페이지, PDF 및 인증된 세션에서 특정 데이터 포인트를 검색할 수 있습니다.

## 사용 사례

- **복원력 있는 웹 추출**: 자연어 설명을 사용하여 동적 웹사이트에서 데이터를 추출합니다. 이 기능을 통해 에이전트는 레이아웃이나 CSS를 자주 업데이트하는 사이트에서 중단 없이 안정적으로 정보를 수집할 수 있습니다.

- **데이터 정규화**: 구조화되지 않은 웹 페이지를 깨끗하고 예측 가능한 JSON 형식으로 변환합니다. 이 기능을 통해 에이전트는 여러 소스(예: 여러 채용 게시판 또는 쇼핑 사이트)의 데이터를 단일 스키마로 즉시 정규화할 수 있습니다.

## 전제 조건

- AgentQL에서 [API 키](https://dev.agentql.com/sign-in)를 만듭니다. 자세한 내용은 [설명서](https://docs.agentql.com/quick-start)를 참조하세요.

## 에이전트와 함께 사용

=== "로컬 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool import McpToolset
    from mcp import StdioServerParameters

    AGENTQL_API_KEY = "YOUR_AGENTQL_API_KEY"

    root_agent = Agent(
        model="gemini-1.5-pro",
        name="agentql_agent",
        instruction="사용자가 AgentQL에서 정보를 얻도록 돕습니다.",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "agentql-mcp",
                        ],
                        env={
                            "AGENTQL_API_KEY": AGENTQL_API_KEY,
                        }
                    ),
                    timeout=300,
                ),
            )
        ],
    )
    ```

## 사용 가능한 도구

도구 <img width="100px"/> | 설명
---- | -----------
`extract-web-data` | 'prompt'를 실제 데이터 및 추출할 필드에 대한 설명으로 사용하여 주어진 'url'에서 구조화된 데이터를 추출합니다.

## 모범 사례

정확한 추출을 보장하려면 에이전트에게 프롬프트를 표시할 때 다음 지침을 따르세요.

- **요소가 아닌 데이터를 설명하세요**: 시각적 설명(예: "파란색 버튼")을 피하세요. 대신 데이터 엔터티(예: "제출 버튼" 또는 "제품 가격")를 설명하세요.

- **계층 구조 정의**: 목록을 추출하는 경우 에이전트에게 항목 모음을 찾도록 명시적으로 지시하고 각 항목에 필요한 필드를 정의하세요.

- **의미적으로 필터링**: 프롬프트 자체 내에서 특정 데이터 유형(예: "광고 및 탐색 링크 제외")을 무시하도록 도구에 지시할 수 있습니다.

## 추가 리소스

- [AgentQL MCP 서버 설명서](https://docs.exa.ai/reference/exa-mcp)
- [AgentQL MCP 서버 리포지토리](https://github.com/tinyfish-io/agentql-mcp)
