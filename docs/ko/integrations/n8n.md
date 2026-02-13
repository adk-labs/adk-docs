---
catalog_title: n8n
catalog_description: 자동화 워크플로를 트리거하고 앱을 연결하며 데이터를 처리합니다
catalog_icon: /adk-docs/integrations/assets/n8n.png
catalog_tags: ["mcp"]
---

# ADK용 n8n MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[n8n MCP Server](https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/)는
ADK 에이전트를 확장 가능한 워크플로 자동화 도구 [n8n](https://n8n.io/)과 연결합니다.
이 통합을 통해 에이전트는 자연어 인터페이스에서
n8n 인스턴스에 안전하게 연결해 워크플로를 검색, 점검, 트리거할 수 있습니다.

!!! note "대안: 워크플로 단위 MCP 서버"

    이 페이지의 구성 가이드는 **인스턴스 단위 MCP 액세스**를 설명하며,
    활성화된 워크플로의 중앙 허브에 에이전트를 연결합니다.
    대안으로
    [MCP Server Trigger node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger/)
    를 사용해 **단일 워크플로**를 독립적인 MCP 서버처럼 동작시킬 수 있습니다.
    이 방법은 특정 서버 동작을 설계하거나
    한 워크플로에만 도구를 격리해 노출하고 싶을 때 유용합니다.

## 사용 사례

- **복잡한 워크플로 실행**: n8n에 정의된 다단계 비즈니스 프로세스를 에이전트에서 직접 트리거합니다.
  신뢰성 있는 분기 로직, 루프, 오류 처리를 활용해 일관성을 보장합니다.

- **외부 앱 연결**: 각 서비스별 커스텀 도구 작성 없이 n8n의 사전 구축 통합을 사용합니다.
  API 인증, 헤더, 보일러플레이트 코드 관리 부담을 줄일 수 있습니다.

- **데이터 처리**: 복잡한 데이터 변환 작업을 n8n 워크플로로 오프로드합니다.
  예를 들어 자연어를 API 호출로 변환하거나 웹페이지를 스크랩/요약하고,
  필요 시 사용자 정의 Python/JavaScript 노드로 정밀하게 가공할 수 있습니다.

## 사전 준비 사항

- 활성 n8n 인스턴스
- 설정에서 MCP 액세스 활성화
- 유효한 MCP 액세스 토큰

자세한 설정 방법은
[n8n MCP documentation](https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/)
를 참조하세요.

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        N8N_INSTANCE_URL = "https://localhost:5678"
        N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="n8n_agent",
            instruction="Help users manage and execute workflows in n8n",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "supergateway",
                                "--streamableHttp",
                                f"{N8N_INSTANCE_URL}/mcp-server/http",
                                "--header",
                                f"authorization:Bearer {N8N_MCP_TOKEN}"
                            ]
                        ),
                        timeout=300,
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        N8N_INSTANCE_URL = "https://localhost:5678"
        N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="n8n_agent",
            instruction="Help users manage and execute workflows in n8n",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url=f"{N8N_INSTANCE_URL}/mcp-server/http",
                        headers={
                            "Authorization": f"Bearer {N8N_MCP_TOKEN}",
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

        const N8N_INSTANCE_URL = "https://localhost:5678";
        const N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "n8n_agent",
            instruction: "Help users manage and execute workflows in n8n",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "supergateway",
                            "--streamableHttp",
                            `${N8N_INSTANCE_URL}/mcp-server/http`,
                            "--header",
                            `authorization:Bearer ${N8N_MCP_TOKEN}`,
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const N8N_INSTANCE_URL = "https://localhost:5678";
        const N8N_MCP_TOKEN = "YOUR_N8N_MCP_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "n8n_agent",
            instruction: "Help users manage and execute workflows in n8n",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: `${N8N_INSTANCE_URL}/mcp-server/http`,
                    header: {
                        Authorization: `Bearer ${N8N_MCP_TOKEN}`,
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

Tool | Description
---- | -----------
`search_workflows` | 사용 가능한 워크플로 검색
`execute_workflow` | 특정 워크플로 실행
`get_workflow_details` | 워크플로 메타데이터 및 스키마 정보 조회

## 구성

에이전트가 워크플로에 접근하려면, 워크플로가 다음 조건을 만족해야 합니다:

- **활성 상태**: 워크플로가 n8n에서 활성화되어 있어야 합니다.

- **지원 트리거 포함**: Webhook, Schedule, Chat, Form 트리거 노드를 포함해야 합니다.

- **MCP 활성화**: 워크플로 설정에서 "Available in MCP"를 켜거나,
  워크플로 카드 메뉴에서 "Enable MCP access"를 선택해야 합니다.

## 추가 리소스

- [n8n MCP Server Documentation](https://docs.n8n.io/advanced-ai/accessing-n8n-mcp-server/)
