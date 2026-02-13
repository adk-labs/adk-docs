---
hide:
  - toc
---
# 허깅 페이스

[허깅 페이스 MCP 서버](https://github.com/huggingface/hf-mcp-server)를 사용하여 ADK 에이전트를 허깅 페이스 허브 및 수천 개의 Gradio AI 애플리케이션에 연결할 수 있습니다.

## 사용 사례

- **AI/ML 자산 검색**: 작업, 라이브러리 또는 키워드를 기반으로 허브에서 모델, 데이터 세트 및 논문을 검색하고 필터링합니다.
- **다단계 워크플로 구축**: 한 도구로 오디오를 기록한 다음 다른 도구로 결과 텍스트를 요약하는 등 도구를 함께 연결합니다.
- **AI 애플리케이션 찾기**: 배경 제거 또는 텍스트 음성 변환과 같은 특정 작업을 수행할 수 있는 Gradio Spaces를 검색합니다.

## 전제 조건

- 허깅 페이스에서 [사용자 액세스 토큰](https://huggingface.co/settings/tokens)을 만듭니다. 자세한 내용은 [설명서](https://huggingface.co/docs/hub/en/security-tokens)를 참조하세요.

## 에이전트와 함께 사용

=== "로컬 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool import McpToolset
    from mcp import StdioServerParameters

    HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="hugging_face_agent",
        instruction="사용자가 허깅 페이스에서 정보를 얻도록 돕습니다.",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "@llmindset/hf-mcp-server",
                        ],
                        env={
                            "HF_TOKEN": HUGGING_FACE_TOKEN,
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

    HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="hugging_face_agent",
        instruction="""사용자가 허깅 페이스에서 정보를 얻도록 돕습니다.""",
        tools=[
            McpToolset(
                connection_params=StreamableHTTPServerParams(
                    url="https://huggingface.co/mcp",
                    headers={
                        "Authorization": f"Bearer {HUGGING_FACE_TOKEN}",
                    },
                ),
            )
        ],
    )
    ```

## 사용 가능한 도구

도구 | 설명
---- | -----------
Spaces 의미 검색 | 자연어 쿼리를 통해 최고의 AI 앱 찾기
논문 의미 검색 | 자연어 쿼리를 통해 ML 연구 논문 찾기
모델 검색 | 작업, 라이브러리 등으로 필터링하여 ML 모델 검색
데이터 세트 검색 | 작성자, 태그 등으로 필터링하여 데이터 세트 검색
설명서 의미 검색 | 허깅 페이스 설명서 라이브러리 검색
허브 리포지토리 세부 정보 | 모델, 데이터 세트 및 스페이스에 대한 자세한 정보 얻기

## 구성

허깅 페이스 허브 MCP 서버에서 사용할 수 있는 도구를 구성하려면 허깅 페이스 계정의 [MCP 설정 페이지](https://huggingface.co/settings/mcp)를 방문하세요.


로컬 MCP 서버를 구성하려면 다음 환경 변수를 사용할 수 있습니다.

- `TRANSPORT`: 사용할 전송 유형(`stdio`, `sse`, `streamableHttp` 또는 `streamableHttpJson`)
- `DEFAULT_HF_TOKEN`: ⚠️ 요청은 `Authorization: Bearer` 헤더에서 받은 `HF_TOKEN`으로 서비스됩니다. 헤더가 전송되지 않은 경우 `DEFAULT_HF_TOKEN`이 사용됩니다. 개발/테스트 환경 또는 로컬 STDIO 배포에서만 이 값을 설정하세요. ⚠️
- stdio 전송으로 실행하는 경우 `DEFAULT_HF_TOKEN`이 설정되지 않으면 `HF_TOKEN`이 사용됩니다.
- `HF_API_TIMEOUT`: 허깅 페이스 API 요청 시간 초과(밀리초)(기본값: 12500ms / 12.5초)
- `USER_CONFIG_API`: 사용자 설정에 사용할 URL(기본값은 로컬 프런트엔드)
- `MCP_STRICT_COMPLIANCE`: JSON 모드에서 GET 405 거부에 대해 True로 설정(기본값은 시작 페이지 제공)
- `AUTHENTICATE_TOOL`: 호출 시 OAuth 챌린지를 발행하는 인증 도구를 포함할지 여부
- `SEARCH_ENABLES_FETCH`: true로 설정하면 hf_doc_search가 활성화될 때마다 hf_doc_fetch 도구가 자동으로 활성화됩니다.


## 추가 리소스

- [허깅 페이스 MCP 서버 리포지토리](https://github.com/huggingface/hf-mcp-server)
- [허깅 페이스 MCP 서버 설명서](https://huggingface.co/docs/hub/en/hf-mcp-server)
