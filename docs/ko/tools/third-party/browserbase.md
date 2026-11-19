---
hide:
  - toc
---
# Browserbase

[Browserbase MCP 서버](https://github.com/browserbase/mcp-server-browserbase)는 [Browserbase](https://www.browserbase.com/) 및 [Stagehand](https://github.com/browserbase/stagehand)를 사용하여 클라우드 브라우저 자동화 기능을 연결합니다. 이를 통해 ADK 에이전트가 웹 페이지와 상호작용하고, 스크린샷을 캡처하고, 정보를 추출하며, 자동화된 작업을 수행할 수 있습니다.

## 사용 사례

- **자동화된 웹 워크플로**: 에이전트가 웹사이트에 로그인하고, 양식을 작성하고, 데이터를 제출하고, 복잡한 사용자 흐름을 탐색하는 등 다단계 작업을 수행할 수 있도록 지원합니다.

- **지능형 데이터 추출**: 특정 페이지로 자동 이동하여 구조화된 데이터, 텍스트 콘텐츠 등 에이전트 작업에 활용할 정보를 추출합니다.

- **시각적 모니터링 및 상호작용**: 전체 페이지 또는 요소별 스크린샷을 캡처하여 웹사이트를 시각적으로 모니터링하고, UI 요소를 테스트하거나, 비전 지원 모델에 시각적 컨텍스트를 다시 전달합니다.

## 전제 조건

- API 키와 프로젝트 ID를 발급받으려면 [Browserbase 계정](https://www.browserbase.com/sign-up)에 가입하세요. 자세한 내용은 [설명서](https://docs.browserbase.com/introduction/getting-started)를 참고하세요.

## 에이전트와 함께 사용

=== "로컬 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool import McpToolset
    from mcp import StdioServerParameters

    BROWSERBASE_API_KEY = "YOUR_BROWSERBASE_API_KEY"
    BROWSERBASE_PROJECT_ID = "YOUR_BROWSERBASE_PROJECT_ID"
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="browserbase_agent",
        instruction="사용자가 브라우저베이스에서 정보를 얻도록 돕습니다.",
        tools=[
            McpToolset(
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
`browserbase_stagehand_navigate` | 브라우저에서 지정한 URL로 이동
`browserbase_stagehand_act` | 자연어를 사용하여 웹 페이지에서 작업 수행
`browserbase_stagehand_extract` | 현재 페이지에서 모든 텍스트 콘텐츠 추출(CSS 및 JavaScript 제외)
`browserbase_stagehand_observe` | 웹 페이지에서 조작 가능한 요소 관찰 및 탐색
`browserbase_screenshot` | 현재 페이지의 PNG 스크린샷 캡처
`browserbase_stagehand_get_url` | 브라우저 페이지의 현재 URL 조회
`browserbase_session_create` | 초기화된 Stagehand와 함께 Browserbase 클라우드 브라우저 세션 생성 또는 재사용
`browserbase_session_close` | 현재 Browserbase 세션을 종료하고 브라우저 연결 해제 및 Stagehand 인스턴스 정리

## 구성

Browserbase MCP 서버는 다음 명령줄 플래그를 지원합니다.

플래그 | 설명
---- | -----------
`--proxies` | 세션에 Browserbase 프록시 활성화
`--advancedStealth` | Browserbase 고급 스텔스 모드 활성화(Scale 플랜 사용자 전용)
`--keepAlive` | Browserbase 세션 유지(Keep-Alive) 활성화
`--contextId <contextId>` | 사용할 Browserbase 컨텍스트 ID 지정
`--persist` | Browserbase 컨텍스트 영구 저장 여부(기본값: true)
`--port <port>` | HTTP/SHTTP 전송을 수신 대기할 포트
`--host <host>` | 서버를 바인딩할 호스트(기본값: localhost, 모든 인터페이스에 바인딩하려면 0.0.0.0 사용)
`--cookies [json]` | 브라우저에 주입할 쿠키의 JSON 배열
`--browserWidth <width>` | 브라우저 뷰포트 너비(기본값: 1024)
`--browserHeight <height>` | 브라우저 뷰포트 높이(기본값: 768)
`--modelName <model>` | Stagehand에 사용할 모델(기본값: gemini-2.0-flash)
`--modelApiKey <key>` | 커스텀 모델 제공자의 API 키(커스텀 모델 사용 시 필요)
`--experimental` | 실험적 기능 활성화(기본값: false)

## 추가 리소스

- [Browserbase MCP 서버 설명서](https://docs.browserbase.com/integrations/mcp/introduction)
- [Browserbase MCP 서버 구성](https://docs.browserbase.com/integrations/mcp/configuration)
- [Browserbase MCP 서버 리포지토리](https://github.com/browserbase/mcp-server-browserbase)
