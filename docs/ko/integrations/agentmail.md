---
catalog_title: AgentMail
catalog_description: AI 에이전트가 메시지를 보내고 받고 관리할 수 있는 이메일 수신함을 생성합니다
catalog_icon: /adk-docs/integrations/assets/agentmail.png
catalog_tags: ["mcp"]
---

# ADK용 AgentMail MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

The [AgentMail MCP Server](https://github.com/agentmail-to/agentmail-mcp)
는 AI 에이전트용으로 제작된 이메일 수신함 API인
[AgentMail](https://agentmail.to/)을(를) ADK 에이전트와 연결합니다.
이 통합을 통해 에이전트는 자연어로 메시지를 보내고, 받으며, 답장하고, 전달할 수 있는
고유한 이메일 수신함을 갖게 됩니다.

## 사용 사례

- **에이전트 전용 수신함 제공**: 에이전트가 인간 팀원처럼 독립적으로 이메일을 보내고 받을 수 있도록,
  전용 이메일 주소를 생성하세요.

- **이메일 워크플로우 자동화**: 초기 메시지 발송, 회신 읽기, 스레드 추적을 포함해
  이메일 대화를 처음부터 끝까지 처리하게 합니다.

- **수신함 간 대화 관리**: 스레드와 메시지를 조회·검색하고, 이메일을 전달하며, 첨부파일을 가져와
  에이전트가 항상 최신 상태를 유지하도록 관리합니다.

## 필수 조건

- [AgentMail 계정](https://agentmail.to/) 생성
- [AgentMail 대시보드](https://agentmail.to/)에서 API 키 발급

## 에이전트와 함께 사용

=== "Python"

    === "로컬 MCP 서버"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        AGENTMAIL_API_KEY = "YOUR_AGENTMAIL_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="agentmail_agent",
            instruction="Help users manage email inboxes and send messages",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "agentmail-mcp",
                            ],
                            env={
                                "AGENTMAIL_API_KEY": AGENTMAIL_API_KEY,
                            }
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "로컬 MCP 서버"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const AGENTMAIL_API_KEY = "YOUR_AGENTMAIL_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "agentmail_agent",
            instruction: "Help users manage email inboxes and send messages",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "agentmail-mcp"],
                        env: {
                            AGENTMAIL_API_KEY: AGENTMAIL_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

### 수신함 관리

도구 | 설명
---- | -----------
`list_inboxes` | 모든 수신함을 조회합니다.
`get_inbox` | 특정 수신함의 세부 정보를 가져옵니다.
`create_inbox` | 사용자명 및 도메인이 포함된 새 수신함을 생성합니다.
`delete_inbox` | 수신함을 삭제합니다.

### 스레드 관리

도구 | 설명
---- | -----------
`list_threads` | 수신함의 스레드를 조회합니다.
`get_thread` | 메시지와 함께 특정 스레드를 조회합니다.
`get_attachment` | 메시지에서 첨부파일을 다운로드합니다.

### 메시지 작업

도구 | 설명
---- | -----------
`send_message` | 수신함에서 새 이메일을 전송합니다.
`reply_to_message` | 기존 메시지에 답장합니다.
`forward_message` | 메시지를 다른 수신자에게 전달합니다.
`update_message` | 읽음 상태 등 메시지 속성을 갱신합니다.

## 추가 리소스

- [AgentMail MCP 서버 저장소](https://github.com/agentmail-to/agentmail-mcp)
- [AgentMail 문서](https://docs.agentmail.to/)
- [AgentMail 툴킷](https://github.com/agentmail-to/agentmail-toolkit)
