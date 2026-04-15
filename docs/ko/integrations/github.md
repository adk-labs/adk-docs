---
catalog_title: GitHub
catalog_description: 코드를 분석하고 이슈와 PR을 관리하며 워크플로를 자동화합니다
catalog_icon: /integrations/assets/github.png
catalog_tags: ["code", "mcp"]
---

# ADK용 GitHub MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[GitHub MCP Server](https://github.com/github/github-mcp-server)는 AI 도구를
GitHub 플랫폼에 직접 연결합니다. 이를 통해 ADK 에이전트는 리포지토리와
코드 파일을 읽고, 이슈와 PR을 관리하고, 코드를 분석하며, 자연어로
워크플로를 자동화할 수 있습니다.

## 사용 사례

- **리포지토리 관리:** 접근 가능한 모든 리포지토리에서 코드를 탐색 및 질의하고,
  파일을 검색하며, 커밋을 분석하고, 프로젝트 구조를 파악합니다.
- **이슈 및 PR 자동화:** 이슈와 풀 리퀘스트를 생성, 업데이트, 관리합니다.
  AI가 버그 분류, 코드 변경 검토, 프로젝트 보드 유지 관리를 도울 수 있습니다.
- **코드 분석:** 보안 탐지 결과를 살펴보고, Dependabot 경고를 검토하며,
  코드 패턴을 이해하고, 코드베이스 전반에 대한 종합적인 인사이트를 얻습니다.

## 전제 조건

- GitHub에서
  [Personal Access Token](https://github.com/settings/personal-access-tokens/new)을
  생성하세요. 자세한 내용은
  [문서](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)를
  참조하세요.

## 에이전트와 함께 사용

=== "Python"

    === "원격 MCP 서버"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="github_agent",
            instruction="사용자가 GitHub에서 정보를 얻도록 돕습니다",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url="https://api.githubcopilot.com/mcp/",
                        headers={
                            "Authorization": f"Bearer {GITHUB_TOKEN}",
                            "X-MCP-Toolsets": "all",
                            "X-MCP-Readonly": "true"
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "원격 MCP 서버"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const GITHUB_TOKEN = "YOUR_GITHUB_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "github_agent",
            instruction: "Help users get information from GitHub",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://api.githubcopilot.com/mcp/",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${GITHUB_TOKEN}`,
                                "X-MCP-Toolsets": "all",
                                "X-MCP-Readonly": "true",
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
`context` | 현재 사용자와 작업 중인 GitHub 컨텍스트에 대한 맥락을 제공하는 도구
`copilot` | Copilot 관련 도구(예: Copilot Coding Agent)
`copilot_spaces` | Copilot Spaces 관련 도구
`actions` | GitHub Actions 워크플로와 CI/CD 작업
`code_security` | GitHub Code Scanning과 같은 코드 보안 관련 도구
`dependabot` | Dependabot 도구
`discussions` | GitHub Discussions 관련 도구
`experiments` | 아직 안정적인 것으로 간주되지 않는 실험적 기능
`gists` | GitHub Gist 관련 도구
`github_support_docs_search` | GitHub 제품 및 지원 질문에 답하기 위한 문서 검색
`issues` | GitHub Issues 관련 도구
`labels` | GitHub Labels 관련 도구
`notifications` | GitHub Notifications 관련 도구
`orgs` | GitHub Organization 관련 도구
`projects` | GitHub Projects 관련 도구
`pull_requests` | GitHub Pull Request 관련 도구
`repos` | GitHub Repository 관련 도구
`secret_protection` | GitHub Secret Scanning과 같은 시크릿 보호 관련 도구
`security_advisories` | 보안 권고 관련 도구
`stargazers` | GitHub Stargazers 관련 도구
`users` | GitHub User 관련 도구

## 구성

원격 GitHub MCP 서버에는 사용할 수 있는 도구 세트와 읽기 전용 모드를
구성하기 위한 선택적 헤더가 있습니다.

- `X-MCP-Toolsets`: 활성화할 도구 세트의 쉼표 구분 목록입니다.
  (예: `"repos,issues"`)
    - 목록이 비어 있으면 기본 도구 세트가 사용됩니다. 잘못된 도구 세트가
      제공되면 서버가 시작되지 않고 400 bad request 상태를 반환합니다.
      공백은 무시됩니다.

- `X-MCP-Readonly`: "읽기" 도구만 활성화합니다.
    - 이 헤더가 비어 있거나 `"false"`, `"f"`, `"no"`, `"n"`, `"0"`, `"off"`이면
      (공백과 대소문자를 무시하고) false로 해석됩니다. 그 외의 값은 모두 true로
      해석됩니다.

## 추가 리소스

- [GitHub MCP Server Repository](https://github.com/github/github-mcp-server)
- [Remote GitHub MCP Server Documentation](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)
- [Policies and Governance for the GitHub MCP Server](https://github.com/github/github-mcp-server/blob/main/docs/policies-and-governance.md)
