# AgentQL

[AgentQL MCP 서버](https://github.com/tinyfish-io/agentql-mcp)는 ADK 에이전트를 [AgentQL](https://www.agentql.com/)에 연결합니다. AgentQL은 CSS나 XPath 선택자 대신 의미를 기반으로 웹 요소를 쿼리하는 시맨틱 추출 엔진입니다. 이를 통해 에이전트는 자연어 정의만으로 웹 페이지, PDF 및 인증된 세션에서 원하는 데이터 포인트를 추출할 수 있습니다.

## 사용 사례

- **안정적인 웹 데이터 추출**: 자연어 설명을 사용하여 동적 웹사이트에서 데이터를 추출합니다. 레이아웃이나 CSS가 자주 변경되는 사이트에서도 코드가 깨지지 않고 안정적으로 정보를 수집할 수 있습니다.

- **데이터 정규화**: 비정형 웹 페이지를 깔끔하고 예측 가능한 JSON 형식으로 변환합니다. 여러 소스(예: 다양한 채용 공고 사이트나 쇼핑몰)의 데이터를 단일 스키마로 즉시 정규화할 수 있습니다.

## 전제 조건

- AgentQL에서 [API 키](https://dev.agentql.com/sign-in)를 만듭니다. 자세한 내용은 [설명서](https://docs.agentql.com/quick-start)를 참고하세요.

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
`extract-web-data` | 추출할 실제 데이터와 필드를 설명하는 `prompt`를 사용하여 지정된 `url`에서 구조화된 데이터를 추출합니다.

## 모범 사례

정확한 데이터 추출을 위해 에이전트에 프롬프트를 작성할 때 다음 지침을 따르세요.

- **요소가 아닌 데이터를 설명하세요**: 시각적 설명(예: "파란색 버튼")은 피하고, 데이터 엔티티(예: "제출 버튼" 또는 "제품 가격")를 중심으로 설명하세요.

- **계층 구조 정의**: 목록을 추출하는 경우 항목 컬렉션을 찾도록 에이전트에 명시적으로 지시하고, 각 항목에 필요한 필드를 정의하세요.

- **시맨틱 필터링**: 프롬프트 내에서 특정 데이터 유형(예: "광고 및 내비게이션 링크 제외")을 제외하도록 도구에 직접 지시할 수 있습니다.

## 추가 리소스

- [AgentQL MCP 서버 설명서](https://docs.exa.ai/reference/exa-mcp)
- [AgentQL MCP 서버 리포지토리](https://github.com/tinyfish-io/agentql-mcp)
