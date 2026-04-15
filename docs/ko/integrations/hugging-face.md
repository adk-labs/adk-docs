---
catalog_title: Hugging Face
catalog_description: 모델, 데이터셋, 연구 논문, AI 도구에 액세스합니다
catalog_icon: /integrations/assets/hugging-face.png
catalog_tags: ["mcp"]
---

# ADK용 Hugging Face MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Hugging Face MCP Server](https://github.com/huggingface/hf-mcp-server)를 사용하면
ADK 에이전트를 Hugging Face Hub와 수천 개의 Gradio AI 애플리케이션에 연결할 수 있습니다.

## 사용 사례

- **AI/ML 자산 탐색:** 작업, 라이브러리, 키워드를 기준으로 Hub에서 모델,
  데이터셋, 논문을 검색하고 필터링합니다.
- **다단계 워크플로 구축:** 한 도구로 오디오를 전사하고 다른 도구로 그 결과
  텍스트를 요약하는 식으로 도구를 연계합니다.
- **AI 애플리케이션 찾기:** 배경 제거, 텍스트 음성 변환 같은 특정 작업을 수행할 수
  있는 Gradio Spaces를 검색합니다.

## 전제 조건

- Hugging Face에서 [user access token](https://huggingface.co/settings/tokens)을
  생성하세요. 자세한 내용은
  [문서](https://huggingface.co/docs/hub/en/security-tokens)를 참조하세요.

## 에이전트와 함께 사용

=== "Python"

    === "로컬 MCP 서버"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="hugging_face_agent",
            instruction="사용자가 Hugging Face에서 정보를 얻도록 돕습니다",
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
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="hugging_face_agent",
            instruction="사용자가 Hugging Face에서 정보를 얻도록 돕습니다",
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

=== "TypeScript"

    === "로컬 MCP 서버"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "hugging_face_agent",
            instruction: "Help users get information from Hugging Face",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@llmindset/hf-mcp-server"],
                        env: {
                            HF_TOKEN: HUGGING_FACE_TOKEN,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "원격 MCP 서버"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const HUGGING_FACE_TOKEN = "YOUR_HUGGING_FACE_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "hugging_face_agent",
            instruction: "Help users get information from Hugging Face",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://huggingface.co/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${HUGGING_FACE_TOKEN}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

도구 | 설명
---- | -----------
Spaces Semantic Search | 자연어 질의로 최적의 AI 앱 찾기
Papers Semantic Search | 자연어 질의로 ML 연구 논문 찾기
Model Search | 작업, 라이브러리 등으로 필터링해 ML 모델 검색
Dataset Search | 작성자, 태그 등으로 필터링해 데이터셋 검색
Documentation Semantic Search | Hugging Face 문서 라이브러리 검색
Hub Repository Details | Models, Datasets, Spaces에 대한 상세 정보 조회

## 구성

Hugging Face Hub MCP 서버에서 어떤 도구를 사용할지 구성하려면,
Hugging Face 계정의 [MCP Settings Page](https://huggingface.co/settings/mcp)를
방문하세요.

로컬 MCP 서버를 구성하려면 다음 환경 변수를 사용할 수 있습니다.

- `TRANSPORT`: 사용할 전송 유형(`stdio`, `sse`, `streamableHttp`,
  `streamableHttpJson`)
- `DEFAULT_HF_TOKEN`: ⚠️ 요청은 `Authorization: Bearer` 헤더로 전달된 `HF_TOKEN`으로
  처리됩니다. 헤더가 전달되지 않았을 때는 `DEFAULT_HF_TOKEN`이 사용됩니다.
  이 값은 개발/테스트 환경 또는 로컬 STDIO 배포에서만 설정하세요. ⚠️
- stdio 전송으로 실행할 때 `DEFAULT_HF_TOKEN`이 설정되지 않았다면 `HF_TOKEN`이 사용됩니다.
- `HF_API_TIMEOUT`: Hugging Face API 요청 제한 시간(밀리초)
  (기본값: 12500ms / 12.5초)
- `USER_CONFIG_API`: 사용자 설정에 사용할 URL(기본값은 로컬 프런트엔드)
- `MCP_STRICT_COMPLIANCE`: JSON 모드에서 GET 405 거부를 위해 True로 설정
  (기본값은 welcome page 제공)
- `AUTHENTICATE_TOOL`: 호출 시 OAuth 챌린지를 발급하는 Authenticate 도구를
  포함할지 여부
- `SEARCH_ENABLES_FETCH`: true로 설정하면 hf_doc_search가 활성화될 때마다
  hf_doc_fetch 도구를 자동 활성화

## 추가 리소스

- [Hugging Face MCP Server Repository](https://github.com/huggingface/hf-mcp-server)
- [Hugging Face MCP Server Documentation](https://huggingface.co/docs/hub/en/hf-mcp-server)
