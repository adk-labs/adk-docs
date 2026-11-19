---
hide:
  - toc
---
# Exa

[Exa MCP 서버](https://github.com/github/github-mcp-server)는 ADK 에이전트를 AI 전용으로 설계된 플랫폼인 [Exa 검색 엔진](https://exa.ai)에 연결합니다. 이를 통해 에이전트는 관련 웹페이지를 검색하고, 링크를 기반으로 유사한 콘텐츠를 찾고, URL에서 정제 및 파싱된 콘텐츠를 가져오고, 질문에 대한 직접적인 답변을 얻으며, 자연어를 사용하여 심층 리서치 보고서 작성을 자동화할 수 있습니다.

## 사용 사례

- **코드 및 기술 예제 찾기**: GitHub, 공식 문서 및 기술 포럼을 검색하여 최신 코드 스니펫, API 사용 패턴 및 구현 예제를 찾습니다.

- **심층 리서치 수행**: 복잡한 주제에 대한 포괄적인 리서치 보고서를 생성하고, 기업에 대한 상세 정보를 수집하거나, LinkedIn에서 전문가 프로필을 찾습니다.

- **실시간 웹 콘텐츠 액세스**: 일반적인 웹 검색을 수행하여 최신 정보를 얻거나 특정 기사, 블로그 게시물 또는 웹 페이지에서 전체 콘텐츠를 추출합니다.

## 전제 조건

- Exa에서 [API 키](https://dashboard.exa.ai/api-keys)를 만듭니다. 자세한 내용은 [설명서](https://docs.exa.ai/reference/quickstart)를 참고하세요.

## 에이전트와 함께 사용

=== "로컬 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool import McpToolset
    from mcp import StdioServerParameters

    EXA_API_KEY = "YOUR_EXA_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="exa_agent",
        instruction="사용자가 Exa에서 정보를 얻도록 돕습니다.",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "exa-mcp-server",
                            # (선택 사항) 활성화할 도구 지정
                            # 도구를 지정하지 않으면 기본적으로 활성화된 모든 도구가 사용됩니다.
                            # "--tools=get_code_context_exa,web_search_exa",
                        ],
                        env={
                            "EXA_API_KEY": EXA_API_KEY,
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
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
    from google.adk.tools.mcp_tool import McpToolset

    EXA_API_KEY = "YOUR_EXA_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="exa_agent",
        instruction="""사용자가 Exa에서 정보를 얻도록 돕습니다.""",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(
                    url="https://mcp.exa.ai/mcp?exaApiKey=" + EXA_API_KEY,
                    # (선택 사항) 활성화할 도구 지정
                    # 도구를 지정하지 않으면 기본적으로 활성화된 모든 도구가 사용됩니다.
                    # url="https://mcp.exa.ai/mcp?exaApiKey=" + EXA_API_KEY + "&enabledTools=%5B%22crawling_exa%22%5D",
                ),
            )
        ],
    )
    ```

## 사용 가능한 도구

도구 <img width="400px"/> | 설명
---- | -----------
`get_code_context_exa` | 오픈 소스 라이브러리, GitHub 리포지토리 및 프로그래밍 프레임워크에서 관련 코드 스니펫, 예제 및 설명서를 검색하고 가져옵니다. 최신 코드 설명서, 구현 예제, API 사용 패턴 및 실제 코드베이스의 모범 사례를 찾는 데 적합합니다.
`web_search_exa` | 최적화된 결과 및 콘텐츠 추출을 통해 실시간 웹 검색을 수행합니다.
`company_research` | 기업 웹사이트를 크롤링하여 비즈니스에 대한 상세 정보를 수집하는 포괄적인 기업 리서치 도구입니다.
`crawling` | 특정 URL에서 콘텐츠를 추출하며, 정확한 URL이 있을 때 기사, PDF 또는 모든 웹 페이지를 읽는 데 유용합니다.
`linkedin_search` | Exa AI를 사용하여 LinkedIn에서 기업 및 인물을 검색합니다. 쿼리에 회사명, 인물 이름 또는 특정 LinkedIn URL을 포함하면 됩니다.
`deep_researcher_start` | 복잡한 질문에 대해 스마트 AI 리서처 작업을 시작합니다. AI가 웹을 검색하고 다양한 출처를 분석하여 상세한 리서치 보고서를 작성합니다.
`deep_researcher_check` | 리서치 작업이 완료되었는지 확인하고 결과를 가져옵니다. 리서치 작업을 시작한 후 이 도구로 완료 여부를 확인하고 종합 보고서를 받아보세요.

## 구성

로컬 Exa MCP 서버에서 사용할 도구를 지정하려면 `--tools` 매개변수를 사용할 수 있습니다.

```
--tools=get_code_context_exa,web_search_exa,company_research,crawling,linkedin_search,deep_researcher_start,deep_researcher_check
```

원격 Exa MCP 서버에서 사용할 도구를 지정하려면 `enabledTools` URL 매개변수를 사용할 수 있습니다.

```
https://mcp.exa.ai/mcp?exaApiKey=YOUREXAKEY&enabledTools=%5B%22crawling_exa%22%5D
```

## 추가 리소스

- [Exa MCP 서버 설명서](https://docs.exa.ai/reference/exa-mcp)
- [Exa MCP 서버 리포지토리](https://github.com/exa-labs/exa-mcp-server)
