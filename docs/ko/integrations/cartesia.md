---
catalog_title: Cartesia
catalog_description: 음성을 생성하고 보이스 현지화 및 오디오 콘텐츠 제작을 수행합니다
catalog_icon: /adk-docs/integrations/assets/cartesia.png
catalog_tags: ["mcp"]
---

# ADK용 Cartesia MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Cartesia MCP Server](https://github.com/cartesia-ai/cartesia-mcp)는
ADK 에이전트를 [Cartesia](https://cartesia.ai/) AI 오디오 플랫폼과 연결합니다.
이 통합을 통해 에이전트는 자연어로 음성을 생성하고,
언어 간 보이스 현지화를 수행하며, 오디오 콘텐츠를 만들 수 있습니다.

## 사용 사례

- **텍스트 음성 변환(TTS) 생성**: Cartesia의 다양한 음성 라이브러리를 사용해
  텍스트를 자연스러운 음성으로 변환하고, 음성 선택 및 출력 포맷을 제어합니다.

- **보이스 현지화**: 기존 보이스를 다른 언어로 변환하면서
  원 화자의 특성을 유지합니다. 다국어 콘텐츠 제작에 적합합니다.

- **오디오 인필(Audio Infill)**: 오디오 세그먼트 사이의 빈 구간을 채워
  자연스러운 전환을 만듭니다. 팟캐스트 편집이나 오디오북 제작에 유용합니다.

- **보이스 변환**: 오디오 클립을 Cartesia 라이브러리의 다른 목소리처럼
  들리도록 변환합니다.

## 사전 준비 사항

- [Cartesia 계정](https://play.cartesia.ai/sign-in) 가입
- Cartesia playground에서 [API 키](https://play.cartesia.ai/keys) 발급

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        CARTESIA_API_KEY = "YOUR_CARTESIA_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="cartesia_agent",
            instruction="Help users generate speech and work with audio content",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["cartesia-mcp"],
                            env={
                                "CARTESIA_API_KEY": CARTESIA_API_KEY,
                                # "OUTPUT_DIRECTORY": "/path/to/output",  # Optional
                            }
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const CARTESIA_API_KEY = "YOUR_CARTESIA_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "cartesia_agent",
            instruction: "Help users generate speech and work with audio content",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["cartesia-mcp"],
                        env: {
                            CARTESIA_API_KEY: CARTESIA_API_KEY,
                            // OUTPUT_DIRECTORY: "/path/to/output",  // Optional
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

Tool | Description
---- | -----------
`text_to_speech` | 지정한 보이스로 텍스트를 오디오로 변환
`list_voices` | 사용 가능한 Cartesia 보이스 목록 조회
`get_voice` | 특정 보이스 상세 정보 조회
`clone_voice` | 오디오 샘플로 보이스 복제
`update_voice` | 기존 보이스 업데이트
`delete_voice` | 라이브러리에서 보이스 삭제
`localize_voice` | 보이스를 다른 언어로 변환
`voice_change` | 오디오 파일을 다른 보이스로 변환
`infill` | 오디오 세그먼트 사이 빈 구간 채우기

## 구성

Cartesia MCP 서버는 환경 변수로 구성할 수 있습니다:

Variable | Description | Required
-------- | ----------- | --------
`CARTESIA_API_KEY` | Cartesia API 키 | Yes
`OUTPUT_DIRECTORY` | 생성된 오디오 파일 저장 디렉터리 | No

## 추가 리소스

- [Cartesia MCP Server Repository](https://github.com/cartesia-ai/cartesia-mcp)
- [Cartesia MCP Documentation](https://docs.cartesia.ai/integrations/mcp)
- [Cartesia Playground](https://play.cartesia.ai/)
