---
catalog_title: AgentPhone
catalog_description: 전화 통화, SMS 전송, 번호 관리, AI 음성 에이전트 구축
catalog_icon: /integrations/assets/agentphone.png
catalog_tags: ["mcp"]
---

# ADK용 AgentPhone MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[AgentPhone MCP Server](https://github.com/AgentPhone-AI/agentphone-mcp)는
ADK 에이전트를 [AgentPhone](https://agentphone.to/)과 연결합니다.
AgentPhone는 AI 에이전트를 위한 통신 플랫폼으로, 전화 걸기와 받기,
SMS 송수신, 전화번호 관리, 자연어로 동작하는 자율형 AI 음성 에이전트
생성을 지원합니다.

## 사용 사례

- **자율 전화 통화**: 에이전트가 전화번호로 전화를 걸고,
  지정한 주제에 대해 AI 기반 대화를 끝까지 이어간 뒤,
  완료 시 전체 대화 기록을 반환합니다.

- **SMS 메시징**: 문자 메시지를 보내고 받으며,
  여러 전화번호에 걸친 대화 스레드를 관리하고,
  메시지 이력을 조회합니다.

- **전화번호 관리**: 특정 지역번호가 포함된 전화번호를 프로비저닝하고,
  에이전트에 할당하거나 더 이상 필요하지 않을 때 해제합니다.

- **AI 음성 에이전트**: 웹훅 없이도 인바운드 및 아웃바운드 통화를
  자율적으로 처리하는, 구성 가능한 음성과 시스템 프롬프트를 가진
  에이전트를 만듭니다.

- **웹훅 연동**: 프로젝트 단위 또는 에이전트별 웹훅을 설정해
  인바운드 메시지와 통화 이벤트에 대한 실시간 알림을 받습니다.

## 사전 준비 사항

- [AgentPhone 계정](https://agentphone.to/)을 생성합니다.
- [AgentPhone 설정](https://agentphone.to/)에서 API 키를 발급합니다.

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="agentphone_agent",
            instruction="Help users make phone calls, send SMS, and manage phone numbers",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "agentphone-mcp",
                            ],
                            env={
                                "AGENTPHONE_API_KEY": AGENTPHONE_API_KEY,
                            }
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="agentphone_agent",
            instruction="Help users make phone calls, send SMS, and manage phone numbers",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.agentphone.to/mcp",
                        headers={
                            "Authorization": f"Bearer {AGENTPHONE_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "agentphone_agent",
            instruction: "Help users make phone calls, send SMS, and manage phone numbers",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "agentphone-mcp"],
                        env: {
                            AGENTPHONE_API_KEY: AGENTPHONE_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const AGENTPHONE_API_KEY = "YOUR_AGENTPHONE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "agentphone_agent",
            instruction: "Help users make phone calls, send SMS, and manage phone numbers",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.agentphone.to/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${AGENTPHONE_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

### 계정

Tool | Description
---- | -----------
`account_overview` | 계정 전체 요약: 에이전트, 번호, 웹훅 상태, 사용량 한도
`get_usage` | 세부 사용량 통계: 요금제 한도, 번호 쿼터, 메시지/통화 사용량

### 전화번호

Tool | Description
---- | -----------
`list_numbers` | 계정의 모든 전화번호 목록 조회
`buy_number` | 국가 및 지역번호를 지정해 새 전화번호 구매

### SMS / 메시지

Tool | Description
---- | -----------
`send_message` | 에이전트의 전화번호로 SMS 또는 iMessage 전송
`get_messages` | 특정 전화번호의 SMS 메시지 조회
`list_conversations` | 에이전트 기준으로 필터링할 수 있는 SMS 대화 스레드 목록 조회
`get_conversation` | 전체 메시지 이력이 포함된 특정 대화 조회
`update_conversation` | 대화의 메타데이터 설정 또는 해제

### 음성 통화

Tool | Description
---- | -----------
`list_calls` | 에이전트, 번호, 상태, 방향 기준으로 필터링할 수 있는 최근 통화 목록 조회
`get_call` | 선택적 장기 폴링을 포함한 통화 세부 정보와 기록 조회
`make_call` | 웹훅을 사용해 대화 처리를 위한 발신 통화 시작
`make_conversation_call` | 전체 대화 기록을 반환하는 자율형 AI 통화 시작

### 에이전트

Tool | Description
---- | -----------
`list_agents` | 전화번호와 음성 설정이 포함된 모든 에이전트 목록 조회
`create_agent` | 구성 가능한 음성과 시스템 프롬프트를 가진 새 에이전트 생성
`update_agent` | 에이전트 설정 업데이트
`delete_agent` | 에이전트 삭제
`get_agent` | 번호와 음성 설정을 포함한 에이전트 세부 정보 조회
`attach_number` | 전화번호를 에이전트에 할당
`detach_number` | 전화번호를 에이전트에서 분리
`list_voices` | 사용 가능한 음성 옵션 목록 조회

### 웹훅

모든 웹훅 도구는 선택적 `agent_id` 매개변수를 지원합니다. 이를 제공하면 해당 에이전트의 웹훅을 대상으로 하고, 생략하면 프로젝트 기본 웹훅을 대상으로 합니다. 에이전트 수준 웹훅이 프로젝트 수준 웹훅보다 우선합니다.

Tool | Description
---- | -----------
`get_webhook` | 웹훅 구성 조회
`set_webhook` | 인바운드 메시지와 통화 이벤트용 웹훅 URL 설정
`delete_webhook` | 웹훅 제거
`test_webhook` | 테스트 이벤트를 전송해 웹훅 동작 확인
`list_webhook_deliveries` | 최근 웹훅 전송 이력 조회

## 구성

AgentPhone MCP 서버는 환경 변수를 사용해 구성할 수 있습니다.

Variable | Description | Default
-------- | ----------- | -------
`AGENTPHONE_API_KEY` | AgentPhone API 키 | Required (stdio mode)
`AGENTPHONE_BASE_URL` | API 기본 URL 덮어쓰기 | `https://api.agentphone.to`

원격 HTTP 모드에서는 환경 변수 대신 `Authorization: Bearer` 헤더로 API 키를 전달합니다.

## 추가 리소스

- [GitHub의 AgentPhone MCP Server](https://github.com/AgentPhone-AI/agentphone-mcp)
- [npm의 agentphone-mcp](https://www.npmjs.com/package/agentphone-mcp)
- [AgentPhone 웹사이트](https://agentphone.to/)
