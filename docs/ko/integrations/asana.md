---
catalog_title: Asana
catalog_description: 팀 협업을 위해 프로젝트, 작업, 목표를 관리합니다
catalog_icon: /adk-docs/integrations/assets/asana.png
catalog_tags: ["mcp"]
---

# ADK용 Asana MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Asana MCP Server](https://developers.asana.com/docs/using-asanas-mcp-server)는
ADK 에이전트를 [Asana](https://asana.com/) 워크 매니지먼트
플랫폼과 연결합니다. 이 통합을 통해 에이전트는 자연어로 프로젝트,
작업, 목표, 팀 협업을 관리할 수 있습니다.

## 사용 사례

- **프로젝트 상태 추적**: 프로젝트 진행 상황의 실시간 업데이트를 받고,
  상태 보고서를 확인하며, 마일스톤과 마감일 정보를 조회합니다.

- **작업 관리**: 자연어로 작업을 생성, 업데이트, 정리합니다.
  에이전트가 작업 할당, 상태 변경, 우선순위 업데이트를 처리하도록 할 수 있습니다.

- **목표 모니터링**: Asana Goals에 접근하고 업데이트해 조직 전반의
  팀 목표와 핵심 결과를 추적합니다.

## 사전 준비 사항

- 워크스페이스 접근 권한이 있는 [Asana](https://asana.com/) 계정

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
            name="asana_agent",
            instruction="Help users manage projects, tasks, and goals in Asana",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.asana.com/sse",
                            ]
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

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "asana_agent",
            instruction: "Help users manage projects, tasks, and goals in Asana",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.asana.com/sse",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    이 에이전트를 처음 실행하면 OAuth를 통한 접근 권한 요청을 위해
    브라우저 창이 자동으로 열립니다. 또는 콘솔에 출력되는
    인증 URL을 사용할 수도 있습니다. 에이전트가 Asana 데이터에 접근하려면
    이 요청을 승인해야 합니다.

## 사용 가능한 도구

Asana의 MCP 서버에는 카테고리별로 구성된 30개 이상의 도구가 포함되어 있습니다. 도구는
에이전트 연결 시 자동으로 탐지됩니다. 에이전트를 실행한 뒤
트레이스 그래프에서 사용 가능한 도구를 보려면
[ADK Web UI](/adk-docs/runtime/web-interface/)를 사용하세요.

Category | Description
-------- | -----------
Project tracking | 프로젝트 상태 업데이트 및 보고서 조회
Task management | 작업 생성, 업데이트, 정리
User information | 사용자 정보 및 할당 조회
Goals | Asana Goals 추적 및 업데이트
Team organization | 팀 구조 및 멤버십 관리
Object search | Asana 객체 전반에서 빠른 typeahead 검색

## 추가 리소스

- [Asana MCP Server Documentation](https://developers.asana.com/docs/using-asanas-mcp-server)
- [Asana MCP Integration Guide](https://developers.asana.com/docs/integrating-with-asanas-mcp-server)
