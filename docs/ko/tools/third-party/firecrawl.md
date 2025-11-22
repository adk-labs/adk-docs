---
hide:
  - toc
---
# Firecrawl

[Firecrawl MCP 서버](https://github.com/firecrawl/firecrawl-mcp-server)는 ADK 에이전트를 [Firecrawl](https://www.firecrawl.dev/) API에 연결합니다. 이 서비스는 모든 웹사이트를 크롤링하고 해당 콘텐츠를 깨끗하고 구조화된 마크다운으로 변환할 수 있습니다. 이를 통해 에이전트는 모든 하위 페이지를 포함하여 모든 URL의 웹 데이터를 수집, 검색 및 추론할 수 있습니다.

## 기능

- **에이전트 기반 웹 리서치**: 주제를 정하고, 검색 도구를 사용하여 관련 URL을 찾은 다음, 스크랩 도구를 사용하여 분석 또는 요약을 위해 각 페이지의 전체 콘텐츠를 추출할 수 있는 에이전트를 배포합니다.

- **구조화된 데이터 추출**: 추출 도구를 사용하여 LLM 추출을 기반으로 URL 목록에서 제품 이름, 가격 또는 연락처 정보와 같은 특정 구조화된 정보를 가져옵니다.

- **대규모 콘텐츠 수집**: 일괄 스크랩 및 크롤링 도구를 사용하여 전체 웹사이트 또는 대량의 URL을 자동으로 스크랩합니다. 이는 RAG(검색 증강 생성) 파이프라인을 위한 벡터 데이터베이스를 채우는 데 이상적입니다.

## 전제 조건

- [Firecrawl에 가입](https://www.firecrawl.dev/signin)하고 [API 키 받기](https://firecrawl.dev/app/api-keys)

## ADK와 함께 사용

=== "로컬 MCP 서버"

    ```python
    from google.adk.agents.llm_agent import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool import McpToolset
    from mcp import StdioServerParameters

    FIRECRAWL_API_KEY = "YOUR_FIRECRAWL_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="firecrawl_agent",
        description="Firecrawl로 웹사이트를 스크랩하는 데 도움이 되는 도우미",
        instruction="사용자가 웹사이트 콘텐츠를 검색하도록 돕습니다.",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "firecrawl-mcp",
                        ],
                        env={
                            "FIRECRAWL_API_KEY": FIRECRAWL_API_KEY,
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
    from google.adk.agents.llm_agent import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
    from google.adk.tools.mcp_tool import McpToolset

    FIRECRAWL_API_KEY = "YOUR_FIRECRAWL_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="firecrawl_agent",
        description="Firecrawl로 웹사이트를 스크랩하는 데 도움이 되는 도우미",
        instruction="사용자가 웹사이트 콘텐츠를 검색하도록 돕습니다.",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(
                    url=f"https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/v2/mcp",
                ),
            )
        ],
    )
    ```

## 사용 가능한 도구

이 도구 세트는 웹 크롤링, 스크래핑 및 검색을 위한 포괄적인 기능 모음을 제공합니다.

도구 | 이름 | 설명
---- | ---- | -----------
스크랩 도구 | `firecrawl_scrape` | 고급 옵션으로 단일 URL에서 콘텐츠 스크랩
일괄 스크랩 도구 | `firecrawl_batch_scrape` | 내장된 속도 제한 및 병렬 처리로 여러 URL을 효율적으로 스크랩
일괄 상태 확인 | `firecrawl_check_batch_status` | 일괄 작업 상태 확인
지도 도구 | `firecrawl_map` | 웹사이트를 매핑하여 사이트의 모든 인덱싱된 URL 검색
검색 도구 | `firecrawl_search` | 웹을 검색하고 선택적으로 검색 결과에서 콘텐츠 추출
크롤링 도구 | `firecrawl_crawl` | 고급 옵션으로 비동기 크롤링 시작
크롤링 상태 확인 | `firecrawl_check_crawl_status` | 크롤링 작업 상태 확인
추출 도구 | `firecrawl_extract` | LLM 기능을 사용하여 웹 페이지에서 구조화된 정보 추출. 클라우드 AI 및 자체 호스팅 LLM 추출 모두 지원

## 구성

Firecrawl MCP 서버는 환경 변수를 사용하여 구성할 수 있습니다.

**필수**:

- `FIRECRAWL_API_KEY`: Firecrawl API 키
    - 클라우드 API 사용 시 필요(기본값)
    - `FIRECRAWL_API_URL`과 함께 자체 호스팅 인스턴스 사용 시 선택 사항

**Firecrawl API URL(선택 사항)**:

- `FIRECRAWL_API_URL`(선택 사항): 자체 호스팅 인스턴스용 사용자 지정 API 엔드포인트
    - 예: `https://firecrawl.your-domain.com`
    - 제공되지 않으면 클라우드 API가 사용됩니다(API 키 필요).

**재시도 구성(선택 사항)**:

- `FIRECRAWL_RETRY_MAX_ATTEMPTS`: 최대 재시도 횟수(기본값: 3)
- `FIRECRAWL_RETRY_INITIAL_DELAY`: 첫 번째 재시도 전 초기 지연 시간(밀리초)(기본값: 1000)
- `FIRECRAWL_RETRY_MAX_DELAY`: 재시도 간 최대 지연 시간(밀리초)(기본값: 10000)
- `FIRECRAWL_RETRY_BACKOFF_FACTOR`: 지수 백오프 승수(기본값: 2)

**크레딧 사용량 모니터링(선택 사항)**:

- `FIRECRAWL_CREDIT_WARNING_THRESHOLD`: 크레딧 사용량 경고 임계값(기본값: 1000)
- `FIRECRAWL_CREDIT_CRITICAL_THRESHOLD`: 크레딧 사용량 위험 임계값(기본값: 100)

## 추가 리소스

- [Firecrawl MCP 서버 설명서](https://docs.firecrawl.dev/mcp-server)
- [Firecrawl MCP 서버 리포지토리](https://github.com/firecrawl/firecrawl-mcp-server)
- [Firecrawl 사용 사례](https://docs.firecrawl.dev/use-cases/overview)
- [Firecrawl 고급 스크래핑 가이드](https://docs.firecrawl.dev/advanced-scraping-guide)
