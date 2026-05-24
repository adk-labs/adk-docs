---
catalog_title: e2a
catalog_description: AI 에이전트를 위한 인증된 이메일 게이트웨이와 human-in-the-loop 승인
catalog_icon: /integrations/assets/e2a.png
catalog_tags: ["mcp"]
---

# ADK용 e2a MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[e2a MCP Server](https://github.com/Mnexa-AI/e2a/tree/main/mcp)는 ADK
에이전트를 AI 에이전트용으로 구축된 인증 이메일 게이트웨이인
[e2a](https://e2a.dev)에 연결합니다. 이 통합을 사용하면 에이전트가
자체 이메일 받은편지함을 갖고 자연어로 메시지를 보내고, 받고, 답장할 수
있습니다. 또한 SPF/DKIM으로 검증된 수신 메일과 발신 메시지에 대한 선택적
human-in-the-loop 승인을 제공합니다.

## 사용 사례

- **에이전트에 전용 받은편지함 제공**: `support-bot@your-domain.com` 같은
  전용 이메일 주소를 프로비저닝하고, 팀원처럼 메일을 주고받게 합니다.
- **인증된 수신 메일**: 모든 수신 메시지는 SPF 및 DKIM 검증 결과와 함께
  도착하므로, 에이전트가 보낸 사람이 실제 주장하는 사람인지 판단할 수
  있습니다.
- **Human-in-the-loop 승인**: 에이전트에 HITL을 구성하면 발신 메시지가
  검토자가 승인할 때까지 대기 큐에 보관됩니다. 승인 전에 제목, 본문,
  수신자를 선택적으로 수정할 수도 있습니다.
- **스레드 대화 자동화**: 수신 이메일에 답장할 때 In-Reply-To 및
  References 헤더를 보존하므로 여러 턴에 걸쳐 스레드가 유지됩니다.

## 기본 요건

- 무료 [e2a 계정](https://e2a.dev) 및 대시보드의 API 키
- Node.js 18 이상(로컬 MCP 서버를 사용할 때만 필요)

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        E2A_API_KEY = "YOUR_E2A_API_KEY"
        E2A_AGENT_EMAIL = "your-bot@your-domain.com"  # optional default inbox

        root_agent = Agent(
            model="gemini-flash-latest",
            name="e2a_agent",
            instruction=(
                "You manage email through the e2a tools. Call whoami once "
                "to find your inbox address. Use list_messages and "
                "get_message to read; use reply_to_message (not "
                "send_email) when replying to an existing thread so "
                "threading headers are preserved."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=["-y", "@e2a/mcp-server"],
                            env={
                                "E2A_API_KEY": E2A_API_KEY,
                                "E2A_AGENT_EMAIL": E2A_AGENT_EMAIL,
                            },
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
        from google.adk.tools.mcp_tool.mcp_session_manager import (
            StreamableHTTPConnectionParams,
        )

        E2A_API_KEY = "YOUR_E2A_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="e2a_agent",
            instruction=(
                "You manage email through the e2a tools. Call whoami once "
                "to find your inbox address. Use list_messages and "
                "get_message to read; use reply_to_message (not "
                "send_email) when replying to an existing thread so "
                "threading headers are preserved."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.e2a.dev/mcp",
                        headers={"Authorization": f"Bearer {E2A_API_KEY}"},
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

        const E2A_API_KEY = "YOUR_E2A_API_KEY";
        const E2A_AGENT_EMAIL = "your-bot@your-domain.com"; // optional default inbox

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "e2a_agent",
            instruction:
                "You manage email through the e2a tools. Call whoami once " +
                "to find your inbox address. Use list_messages and " +
                "get_message to read; use reply_to_message (not " +
                "send_email) when replying to an existing thread so " +
                "threading headers are preserved.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@e2a/mcp-server"],
                        env: {
                            E2A_API_KEY: E2A_API_KEY,
                            E2A_AGENT_EMAIL: E2A_AGENT_EMAIL,
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

        const E2A_API_KEY = "YOUR_E2A_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "e2a_agent",
            instruction:
                "You manage email through the e2a tools. Call whoami once " +
                "to find your inbox address. Use list_messages and " +
                "get_message to read; use reply_to_message (not " +
                "send_email) when replying to an existing thread so " +
                "threading headers are preserved.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.e2a.dev/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${E2A_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

### ID

도구 | 설명
---- | -----------
`whoami` | 기본 에이전트의 전체 레코드를 반환합니다. 계정에 에이전트가 둘 이상이면 `E2A_AGENT_EMAIL`이 필요합니다.
`list_agents` | 인증된 사용자가 소유한 모든 에이전트 받은편지함을 나열합니다.
`create_agent` | 공유 도메인의 slug를 사용해 새 받은편지함을 등록합니다. 기본값은 `local` 모드이므로 에이전트가 폴링으로 메일을 수신하고 webhook은 필요하지 않습니다.
`update_agent` | 기존 에이전트의 webhook URL, 모드 또는 HITL 설정을 업데이트합니다.
`delete_agent` | 에이전트를 영구 삭제하고 해당 주소의 메일 수신을 중단합니다. `confirm: true`가 필요합니다.

!!! warning "Cloud 모드 에이전트는 webhook 서명을 검증해야 합니다"

    `agent_mode: "cloud"`로 생성된 에이전트는 폴링 대신 webhook으로 메일을
    받습니다. webhook 핸들러는 모든 전달에 대해 HMAC 서명을 검증해야
    합니다. 서명 검증을 포함한 전체 설정은
    [cloud-mode webhook 예제](https://github.com/Mnexa-AI/e2a/tree/main/examples/adk-cloud-webhook)를
    참고하세요.

### 메시지

도구 | 설명
---- | -----------
`send_email` | 새 이메일을 보냅니다. HITL이 활성화되어 있으면 `sent` 대신 `status: pending_approval`을 반환합니다.
`reply_to_message` | 수신 메시지에 답장하고 In-Reply-To 및 References 헤더를 보존합니다.
`list_messages` | `status` 필터(unread / read / all)와 페이지네이션으로 수신 메일을 나열합니다.
`get_message` | 한 메시지의 전체 본문, 헤더, 첨부파일 메타데이터를 가져옵니다.
`get_attachment_data` | 메시지 ID와 0부터 시작하는 첨부파일 인덱스로 첨부파일 바이트를 다운로드합니다(base64로 반환).

### Human-in-the-loop 승인

도구 | 설명
---- | -----------
`list_pending_messages` | human 승인 대기 중인 발신 메일을 만료가 빠른 순서로 나열합니다.
`get_pending_message` | 대기 중인 메시지의 전체 초안(제목, 수신자, 본문)을 가져옵니다.
`approve_pending_message` | 검토자가 선택적으로 수정한 제목, 본문, 수신자로 보류 메시지를 보냅니다.
`reject_pending_message` | 보류 메시지를 폐기합니다. 선택적 `reason`은 감사용으로 저장됩니다.

### 도메인

도구 | 설명
---- | -----------
`list_domains` | 인증된 사용자에게 등록된 모든 커스텀 도메인과 검증 상태를 나열합니다.
`register_domain` | 커스텀 도메인을 추가하고 소유권 증명에 필요한 DNS 레코드를 반환합니다.
`verify_domain` | DNS 레코드를 설정한 뒤 등록된 도메인의 DNS 검증을 다시 실행합니다.
`delete_domain` | 커스텀 도메인을 제거합니다. `confirm: true`가 필요하며 공유 도메인의 에이전트에는 영향이 없습니다.

## 구성

변수 | 필수 | 기본값 | 설명
---- | ---- | ------ | -----------
`E2A_API_KEY` | 예 | — | e2a API 키입니다.
`E2A_AGENT_EMAIL` | 아니요 | — | 기본 에이전트 받은편지함입니다. 도구 범위를 제한하므로 LLM이 매번 지정할 필요가 없습니다.
`E2A_BASE_URL` | 아니요 | `https://e2a.dev` | 자체 호스팅 배포 URL입니다(로컬 MCP 서버만 해당).

## 추가 리소스

- [e2a MCP Server 소스](https://github.com/Mnexa-AI/e2a/tree/main/mcp)
- [실행 가능한 ADK 예제](https://github.com/Mnexa-AI/e2a/tree/main/mcp/examples/adk)
- [Cloud-mode webhook 예제](https://github.com/Mnexa-AI/e2a/tree/main/examples/adk-cloud-webhook)
- [e2a 문서](https://e2a.dev)
- [npm 패키지](https://www.npmjs.com/package/@e2a/mcp-server)
