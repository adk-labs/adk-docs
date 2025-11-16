---
hide:
  - toc
---
# 브라우저베이스

[브라우저베이스 MCP 서버](https://github.com/browserbase/mcp-server-browserbase)는 [브라우저베이스](https://www.browserbase.com/) 및 [스테이지핸드](https://github.com/browserbase/stagehand)를 사용하여 클라우드 브라우저 자동화 기능에 연결합니다. ADK 에이전트가 웹 페이지와 상호 작용하고, 스크린샷을 찍고, 정보를 추출하고, 자동화된 작업을 수행할 수 있도록 합니다.

## 사용 사례

- **자동화된 웹 워크플로**: 에이전트가 웹사이트에 로그인하고, 양식을 작성하고, 데이터를 제출하고, 복잡한 사용자 흐름을 탐색하는 등 다단계 작업을 수행할 수 있도록 지원합니다.

- **지능형 데이터 추출**: 특정 페이지로 자동으로 이동하여 구조화된 데이터, 텍스트 콘텐츠 또는 기타 정보를 에이전트 작업에 사용하기 위해 추출합니다.

- **시각적 모니터링 및 상호 작용**: 전체 페이지 또는 요소별 스크린샷을 캡처하여 웹사이트를 시각적으로 모니터링하고, UI 요소를 테스트하거나, 시각적 컨텍스트를 비전 지원 모델에 다시 제공합니다.

## 전제 조건

- API 키와 프로젝트 ID를 얻으려면 [브라우저베이스 계정](https://www.browserbase.com/sign-up)에 가입하세요. 자세한 내용은 [설명서](https://docs.browserbase.com/introduction/getting-started)를 참조하세요.

## 에이전트와 함께 사용

=== "로컬 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from mcp import StdioServerParameters

    BROWSERBASE_API_KEY = "YOUR_BROWSERBASE_API_KEY"
    BROWSERBASE_PROJECT_ID = "YOUR_BROWSERBASE_PROJECT_ID"
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="browserbase_agent",
        instruction="사용자가 브라우저베이스에서 정보를 얻도록 돕습니다.",
        tools=[
            MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "@browserbasehq/mcp-server-browserbase",
                        ],
                        env={
                            "BROWSERBASE_API_KEY": BROWSERBASE_API_KEY,
                            "BROWSERBASE_PROJECT_ID": BROWSERBASE_PROJECT_ID,
                            "GEMINI_API_KEY": GEMINI_API_KEY,
                        }
                    ),
                    timeout=300,
                ),
            )
        ],
    )
    ```

## 사용 가능한 도구

도구 <img width="200px"/> | 설명
---- | -----------
`browserbase_stagehand_navigate` | 브라우저에서 모든 URL로 이동
`browserbase_stagehand_act` | 자연어를 사용하여 웹 페이지에서 작업 수행
`browserbase_stagehand_extract` | 현재 페이지에서 모든 텍스트 콘텐츠 추출(CSS 및 JavaScript 필터링)
`browserbase_stagehand_observe` | 웹 페이지에서 실행 가능한 요소 관찰 및 찾기
`browserbase_screenshot` | 현재 페이지의 PNG 스크린샷 캡처
`browserbase_stagehand_get_url` | 브라우저 페이지의 현재 URL 가져오기
`browserbase_session_create` | 완전히 초기화된 스테이지핸드로 브라우저베이스를 사용하여 클라우드 브라우저 세션 생성 또는 재사용
`browserbase_session_close` | 현재 브라우저베이스 세션을 닫고 브라우저 연결을 끊고 스테이지핸드 인스턴스 정리

## 구성

브라우저베이스 MCP 서버는 다음 명령줄 플래그를 허용합니다.

플래그 | 설명
---- | -----------
`--proxies` | 세션에 브라우저베이스 프록시 활성화
`--advancedStealth` | 브라우저베이스 고급 스텔스 활성화(스케일 플랜 사용자만 해당)
`--keepAlive` | 브라우저베이스 세션 유지 활성화
`--contextId <contextId>` | 사용할 브라우저베이스 컨텍스트 ID 지정
`--persist` | 브라우저베이스 컨텍스트 유지 여부(기본값: true)
`--port <port>` | HTTP/SHTTP 전송을 수신할 포트
`--host <host>` | 서버를 바인딩할 호스트(기본값: localhost, 모든 인터페이스에 0.0.0.0 사용)
`--cookies [json]` | 브라우저에 주입할 쿠키의 JSON 배열
`--browserWidth <width>` | 브라우저 뷰포트 너비(기본값: 1024)
`--browserHeight <height>` | 브라우저 뷰포트 높이(기본값: 768)
`--modelName <model>` | 스테이지핸드에 사용할 모델(기본값: gemini-2.0-flash)
`--modelApiKey <key>` | 사용자 지정 모델 공급자의 API 키(사용자 지정 모델 사용 시 필요)
`--experimental` | 실험적 기능 활성화(기본값: false)

## 추가 리소스

- [브라우저베이스 MCP 서버 설명서](https://docs.browserbase.com/integrations/mcp/introduction)
- [브라우저베이스 MCP 서버 구성](https://docs.browserbase.com/integrations/mcp/configuration)
- [브라우저베이스 MCP 서버 리포지토리](https://github.com/browserbase/mcp-server-browserbase)
