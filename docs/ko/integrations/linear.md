---
catalog_title: Linear
catalog_description: 이슈를 관리하고 프로젝트를 추적하며 개발 워크플로를 간소화합니다
catalog_icon: /adk-docs/integrations/assets/linear.png
catalog_tags: ["mcp"]
---

# ADK용 Linear MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Linear MCP Server](https://linear.app/docs/mcp)는 ADK 에이전트를
제품 기획/개발을 위해 설계된 도구인 [Linear](https://linear.app/)와 연결합니다.
이 통합을 통해 에이전트는 자연어로 이슈를 관리하고,
프로젝트 사이클을 추적하며, 개발 워크플로를 자동화할 수 있습니다.

## 사용 사례

- **이슈 관리 간소화**: 자연어로 이슈를 생성, 업데이트, 정리합니다.
  에이전트가 버그 기록, 작업 할당, 상태 업데이트를 처리할 수 있습니다.

- **프로젝트/사이클 추적**: 팀 진행 상황을 즉시 파악합니다.
  활성 사이클 상태를 질의하고, 프로젝트 마일스톤 및 마감일을 조회합니다.

- **컨텍스트 검색 및 요약**: 긴 토론 스레드를 빠르게 파악하거나
  특정 프로젝트 명세를 찾습니다. 에이전트가 문서를 검색하고
  복잡한 이슈를 요약할 수 있습니다.

## 사전 준비 사항

- [Linear 계정](https://linear.app/signup) 가입
- [Linear Settings > Security & access](https://linear.app/docs/security-and-access)에서
  API 키 생성(API 인증 사용 시)

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="linear_agent",
            instruction="Help users manage issues, projects, and cycles in Linear",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.linear.app/mcp",
                            ]
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

        !!! note

            이 에이전트를 처음 실행하면 OAuth 접근 요청을 위해 브라우저 창이
            자동으로 열립니다. 또는 콘솔에 출력된 인증 URL을 사용할 수 있습니다.
            에이전트가 Linear 데이터에 접근하려면 해당 요청을 승인해야 합니다.

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        LINEAR_API_KEY = "YOUR_LINEAR_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="linear_agent",
            instruction="Help users manage issues, projects, and cycles in Linear",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url="https://mcp.linear.app/mcp",
                        headers={
                            "Authorization": f"Bearer {LINEAR_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

        !!! note

            이 코드 예시는 API 키 인증을 사용합니다. 브라우저 기반 OAuth 인증 흐름을
            사용하려면 `headers` 파라미터를 제거하고 에이전트를 실행하세요.

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "linear_agent",
            instruction: "Help users manage issues, projects, and cycles in Linear",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "mcp-remote", "https://mcp.linear.app/mcp"],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            이 에이전트를 처음 실행하면 OAuth 접근 요청을 위해 브라우저 창이
            자동으로 열립니다. 또는 콘솔에 출력된 인증 URL을 사용할 수 있습니다.
            에이전트가 Linear 데이터에 접근하려면 해당 요청을 승인해야 합니다.

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const LINEAR_API_KEY = "YOUR_LINEAR_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "linear_agent",
            instruction: "Help users manage issues, projects, and cycles in Linear",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.linear.app/mcp",
                    header: {
                        Authorization: `Bearer ${LINEAR_API_KEY}`,
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

        !!! note

            이 코드 예시는 API 키 인증을 사용합니다. 브라우저 기반 OAuth 인증 흐름을
            사용하려면 `header` 속성을 제거하고 에이전트를 실행하세요.

## 사용 가능한 도구

Tool | Description
---- | -----------
`list_comments` | 이슈 코멘트 목록 조회
`create_comment` | 이슈에 코멘트 생성
`list_cycles` | 프로젝트 사이클 목록 조회
`get_document` | 문서 조회
`list_documents` | 문서 목록 조회
`get_issue` | 이슈 조회
`list_issues` | 이슈 목록 조회
`create_issue` | 이슈 생성
`update_issue` | 이슈 업데이트
`list_issue_statuses` | 이슈 상태 목록 조회
`get_issue_status` | 이슈 상태 조회
`list_issue_labels` | 이슈 라벨 목록 조회
`create_issue_label` | 이슈 라벨 생성
`list_projects` | 프로젝트 목록 조회
`get_project` | 프로젝트 조회
`create_project` | 프로젝트 생성
`update_project` | 프로젝트 업데이트
`list_project_labels` | 프로젝트 라벨 목록 조회
`list_teams` | 팀 목록 조회
`get_team` | 팀 조회
`list_users` | 사용자 목록 조회
`get_user` | 사용자 조회
`search_documentation` | 문서 검색

## 추가 리소스

- [Linear MCP Server Documentation](https://linear.app/docs/mcp)
- [Linear Getting Started Guide](https://linear.app/docs/start-guide)
