# Tavily

[Tavily MCP 서버](https://github.com/tavily-ai/tavily-mcp)는
ADK 에이전트를 Tavily의 AI 중심 검색, 추출 및 크롤링 플랫폼에 연결합니다.
이 도구를 사용하면 에이전트가 실시간 웹 검색을 수행하고, 웹 페이지에서
특정 데이터를 지능적으로 추출하며, 웹사이트를 크롤링하거나 구조화된 맵을
생성할 수 있습니다.

## 사용 사례 (Use cases)

- **실시간 웹 검색 (Real-Time Web Search)**: 최적화된 실시간 웹 검색을 수행하여
  에이전트의 작업에 필요한 최신 정보를 얻습니다.

- **지능형 데이터 추출 (Intelligent Data Extraction)**: 전체 HTML을 파싱할 필요 없이
  모든 웹 페이지에서 특정하고 깔끔한 데이터와 콘텐츠를 추출합니다.

- **웹사이트 탐색 (Website Exploration)**: 웹사이트를 자동으로 크롤링하여 콘텐츠를 탐색하거나
  사이트의 레이아웃 및 페이지에 대한 구조화된 맵을 생성합니다.

## 필수 조건 (Prerequisites)

- [Tavily 계정](https://app.tavily.com/)에 가입하여 API 키를 발급받으세요.
  자세한 내용은 [문서](https://docs.tavily.com/documentation/quickstart)를 참조하세요.

## 에이전트와 함께 사용하기 (Use with agent)

=== "로컬 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="tavily_agent",
        instruction="Help users get information from Tavily",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "tavily-mcp@latest",
                        ],
                        env={
                            "TAVILY_API_KEY": TAVILY_API_KEY,
                        }
                    ),
                    timeout=30,
                ),
            )
        ],
    )
    ```

=== "원격 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

    TAVILY_API_KEY = "YOUR_TAVILY_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="tavily_agent",
        instruction="""Help users get information from Tavily""",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(
                    url="https://mcp.tavily.com/mcp/",
                    headers={
                        "Authorization": f"Bearer {TAVILY_API_KEY}",
                    },
                ),
            )
        ],
    )
    ```

## 사용 예시 (Example usage)

에이전트가 설정되고 실행되면 명령줄 인터페이스(CLI) 또는 웹 인터페이스를 통해
상호 작용할 수 있습니다. 간단한 예시는 다음과 같습니다:

**에이전트 프롬프트 샘플:**

> tavily.com의 모든 문서 페이지를 찾고 Tavily 시작 방법에 대한 지침을 제공해 줘

에이전트는 자동으로 여러 Tavily 도구를 호출하여 포괄적인 답변을 제공하므로,
수동으로 탐색하지 않고도 쉽게 웹사이트를 탐색하고 정보를 수집할 수 있습니다:

<img src="../../../assets/tools-tavily-screenshot.png">

## 사용 가능한 도구 (Available tools)

연결되면 에이전트는 Tavily의 웹 인텔리전스 도구에 액세스할 수 있습니다:

도구 <img width="100px"/> | 설명
---- | -----------
`tavily-search` | 웹 전반에서 관련 정보를 찾기 위해 검색 쿼리를 실행합니다.
`tavily-extract` | 웹 페이지에서 구조화된 데이터를 추출합니다. 단일 페이지에서 텍스트, 링크, 이미지를 추출하거나 여러 URL을 효율적으로 일괄 처리합니다.
`tavily-map` | 웹사이트를 그래프처럼 순회하며, 지능형 검색(intelligent discovery)을 통해 수백 개의 경로를 병렬로 탐색하여 포괄적인 사이트 맵을 생성합니다.
`tavily-crawl` | 내장된 추출 및 지능형 검색 기능을 통해 수백 개의 경로를 병렬로 탐색할 수 있는 순회(traversal) 도구입니다.

## 추가 리소스 (Additional resources)

- [Tavily MCP 서버 문서](https://docs.tavily.com/documentation/mcp)
- [Tavily MCP 서버 리포지토리](https://github.com/tavily-ai/tavily-mcp)