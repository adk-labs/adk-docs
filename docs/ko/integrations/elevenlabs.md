---
catalog_title: ElevenLabs
catalog_description: 음성 생성, 보이스 클론, 오디오 전사, 효과음 생성을 수행합니다
catalog_icon: /adk-docs/integrations/assets/elevenlabs.png
catalog_tags: ["mcp"]
---

# ADK용 ElevenLabs MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[ElevenLabs MCP Server](https://github.com/elevenlabs/elevenlabs-mcp)는
ADK 에이전트를 [ElevenLabs](https://elevenlabs.io/) AI 오디오 플랫폼과 연결합니다.
이 통합을 통해 에이전트는 자연어로 음성 생성,
보이스 클로닝, 오디오 전사, 효과음 생성,
대화형 AI 경험 구축을 수행할 수 있습니다.


## 사용 사례

- **텍스트 음성 변환(TTS) 생성**: 다양한 보이스를 사용해 텍스트를 자연스러운 음성으로 변환하고,
  안정성(stability), 스타일, 유사도 설정을 세밀하게 제어합니다.

- **보이스 클로닝 및 설계**: 오디오 샘플에서 보이스를 복제하거나,
  연령/성별/억양/톤 같은 원하는 특성을 텍스트로 설명해 새 보이스를 생성합니다.

- **오디오 처리**: 배경 소음에서 음성을 분리하고,
  오디오를 다른 목소리처럼 변환하거나, 화자 식별과 함께 음성을 텍스트로 전사합니다.

- **효과음 및 사운드스케이프**: 텍스트 설명으로 효과음과 배경 사운드스케이프를 생성합니다.
  예: "동물들이 날씨에 반응하는 울창한 정글의 천둥폭풍".

## 사전 준비 사항

- [ElevenLabs 계정](https://elevenlabs.io/app/sign-up) 가입
- 계정 설정에서 [API 키](https://elevenlabs.io/app/settings/api-keys) 생성

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="elevenlabs_agent",
            instruction="Help users generate speech, clone voices, and process audio",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["elevenlabs-mcp"],
                            env={
                                "ELEVENLABS_API_KEY": ELEVENLABS_API_KEY,
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

        const ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "elevenlabs_agent",
            instruction: "Help users generate speech, clone voices, and process audio",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["elevenlabs-mcp"],
                        env: {
                            ELEVENLABS_API_KEY: ELEVENLABS_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

### 텍스트 음성 및 보이스

Tool | Description
---- | -----------
`text_to_speech` | 지정한 보이스로 텍스트를 음성으로 생성
`speech_to_speech` | 오디오를 다른 보이스처럼 변환
`text_to_voice` | 텍스트 설명으로 보이스 프리뷰 생성
`create_voice_from_preview` | 생성된 보이스 프리뷰를 라이브러리에 저장
`voice_clone` | 오디오 샘플에서 보이스 복제
`get_voice` | 특정 보이스 상세 정보 조회
`search_voices` | 라이브러리 내 보이스 검색
`search_voice_library` | 공개 보이스 라이브러리 검색
`list_models` | 사용 가능한 TTS 모델 목록 조회

### 오디오 처리

Tool | Description
---- | -----------
`speech_to_text` | 화자 식별과 함께 오디오를 텍스트로 전사
`text_to_sound_effects` | 텍스트 설명으로 효과음 생성
`isolate_audio` | 배경 소음/음악에서 음성 분리
`play_audio` | 로컬에서 오디오 파일 재생
`compose_music` | 설명으로 음악 생성
`create_composition_plan` | 음악 작곡 계획 생성

### 대화형 AI

Tool | Description
---- | -----------
`create_agent` | 대화형 AI 에이전트 생성
`get_agent` | 특정 에이전트 상세 정보 조회
`list_agents` | 모든 대화형 AI 에이전트 목록 조회
`add_knowledge_base_to_agent` | 에이전트에 지식 베이스 추가
`make_outbound_call` | 에이전트를 사용해 발신 전화 시작
`list_phone_numbers` | 사용 가능한 전화번호 목록 조회
`get_conversation` | 특정 대화 상세 정보 조회
`list_conversations` | 모든 대화 목록 조회

### 계정

Tool | Description
---- | -----------
`check_subscription` | 구독 및 크레딧 사용량 확인

## 구성

ElevenLabs MCP 서버는 환경 변수로 구성할 수 있습니다:

Variable | Description | Default
-------- | ----------- | -------
`ELEVENLABS_API_KEY` | ElevenLabs API 키 | Required
`ELEVENLABS_MCP_BASE_PATH` | 파일 작업 기본 경로 | `~/Desktop`
`ELEVENLABS_MCP_OUTPUT_MODE` | 생성 파일 반환 방식 | `files`
`ELEVENLABS_API_RESIDENCY` | 데이터 상주 리전(엔터프라이즈 전용) | `us`

### 출력 모드

`ELEVENLABS_MCP_OUTPUT_MODE` 환경 변수는 세 가지 모드를 지원합니다:

- **`files`**(기본값): 파일을 디스크에 저장하고 파일 경로 반환
- **`resources`**: 파일을 MCP 리소스(base64 인코딩 바이너리)로 반환
- **`both`**: 디스크 저장 + MCP 리소스로 반환

## 추가 리소스

- [ElevenLabs MCP Server Repository](https://github.com/elevenlabs/elevenlabs-mcp)
- [Introducing ElevenLabs MCP](https://elevenlabs.io/blog/introducing-elevenlabs-mcp)
- [ElevenLabs Documentation](https://elevenlabs.io/docs)
