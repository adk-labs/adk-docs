# ScrapeGraphAI

[ScrapeGraphAI MCP 서버](https://github.com/ScrapeGraphAI/scrapegraph-mcp)는
ADK 에이전트를 [ScrapeGraphAI](https://scrapegraphai.com/)에 연결합니다.
이 통합을 통해 에이전트는 자연어 프롬프트를 사용하여 구조화된 데이터를 추출하고,
무한 스크롤과 같은 동적 콘텐츠를 처리하며, 복잡한 웹페이지를 깔끔하고 사용 가능한
JSON 또는 Markdown으로 변환할 수 있습니다.

## 사용 사례 (Use cases)

- **확장 가능한 추출 및 크롤링 (Scalable Extraction & Crawling)**: 단일 페이지에서
  구조화된 데이터를 추출하거나 웹사이트 전체를 크롤링할 수 있으며, AI를 활용하여
  동적 콘텐츠, 무한 스크롤 및 대규모 비동기 작업을 처리합니다.

- **조사 및 요약 (Research and Summarization)**: AI 기반 웹 검색을 실행하여 주제를 조사하고,
  여러 소스의 데이터를 집계하고, 결과를 요약합니다.

- **에이전트 워크플로 (Agentic Workflows)**: 사용자 정의 가능한 단계, 복잡한 탐색(인증 등),
  구조화된 출력 스키마를 갖춘 고급 에이전트 스크래핑 워크플로를 실행합니다.

## 필수 조건 (Prerequisites)

- ScrapeGraphAI에서 [API 키](https://dashboard.scrapegraphai.com/register/)를 생성하세요.
  자세한 내용은 [문서](https://docs.scrapegraphai.com/api-reference/introduction)를 참조하세요.
- [ScrapeGraphAI MCP 서버 패키지](https://pypi.org/project/scrapegraph-mcp/)를 설치하세요
  (Python 3.13 이상 필요):

    ```console
    pip install scrapegraph-mcp
    ```

## 에이전트와 함께 사용하기 (Use with agent)

=== "로컬 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    SGAI_API_KEY = "YOUR_SCRAPEGRAPHAI_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="scrapegraph_assistant_agent",
        instruction="""Help the user with web scraping and data extraction using
                      ScrapeGraph AI. You can convert webpages to markdown, extract
                      structured data using AI, perform web searches, crawl
                      multiple pages, and automate complex scraping workflows.""",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        # 다음 CLI 명령은 `pip install scrapegraph-mcp`를 통해
                        # 사용할 수 있습니다.
                        command="scrapegraph-mcp",
                        env={
                            "SGAI_API_KEY": SGAI_API_KEY,
                        },
                    ),
                    timeout=300,
                ),
            # 선택 사항: MCP 서버에서 노출할 도구를 필터링합니다.
            # tool_filter=["markdownify", "smartscraper", "searchscraper"]
            ),
        ],
    )
    ```

## 사용 가능한 도구 (Available tools)

도구 <img width="200px"/> | 설명
---- | -----------
`markdownify` | 모든 웹페이지를 깔끔하고 구조화된 마크다운 형식으로 변환합니다.
`smartscraper` | AI를 활용하여 무한 스크롤을 지원하는 모든 웹페이지에서 구조화된 데이터를 추출합니다.
`searchscraper` | 구조화되고 실행 가능한 결과와 함께 AI 기반 웹 검색을 실행합니다.
`scrape` | 무거운 JavaScript 렌더링(선택 사항)을 포함하여 페이지 콘텐츠를 가져오는 기본 스크래핑 엔드포인트입니다.
`sitemap` | 웹사이트의 사이트맵 URL 및 구조를 추출합니다.
`smartcrawler_initiate` | 지능형 다중 페이지 웹 크롤링을 시작합니다 (비동기 작업).
`smartcrawler_fetch_results` | 비동기 크롤링 작업에서 결과를 검색합니다.
`agentic_scrapper` | 사용자 정의 가능한 단계 및 구조화된 출력 스키마로 고급 에이전트 스크래핑 워크플로를 실행합니다.

## 추가 리소스 (Additional resources)

- [ScrapeGraphAI MCP 서버 문서](https://docs.scrapegraphai.com/services/mcp-server)
- [ScrapeGraphAI MCP 서버 리포지토리](https://github.com/ScrapeGraphAI/scrapegraph-mcp)