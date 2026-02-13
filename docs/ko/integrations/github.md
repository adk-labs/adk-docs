---
hide:
  - toc
---
# GitHub

[GitHub MCP 서버](https://github.com/github/github-mcp-server)는 AI 도구를 GitHub 플랫폼에 직접 연결합니다. 이를 통해 ADK 에이전트는 리포지토리 및 코드 파일을 읽고, 문제 및 PR을 관리하고, 코드를 분석하고, 자연어를 사용하여 워크플로를 자동화할 수 있습니다.

## 사용 사례

- **리포지토리 관리**: 액세스 권한이 있는 모든 리포지토리에서 코드를 탐색 및 쿼리하고, 파일을 검색하고, 커밋을 분석하고, 프로젝트 구조를 이해합니다.
- **문제 및 PR 자동화**: 문제 및 끌어오기 요청을 생성, 업데이트 및 관리합니다. AI가 버그를 분류하고, 코드 변경 사항을 검토하고, 프로젝트 보드를 유지 관리하도록 돕습니다.
- **코드 분석**: 보안 결과를 검사하고, Dependabot 경고를 검토하고, 코드 패턴을 이해하고, 코드베이스에 대한 포괄적인 통찰력을 얻습니다.

## 전제 조건

- GitHub에서 [개인용 액세스 토큰](https://github.com/settings/personal-access-tokens/new)을 만듭니다. 자세한 내용은 [설명서](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)를 참조하세요.

## 에이전트와 함께 사용

=== "원격 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
    from google.adk.tools.mcp_tool import McpToolset

    GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="github_agent",
        instruction="사용자가 GitHub에서 정보를 얻도록 돕습니다.",
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

## 사용 가능한 도구

도구 | 설명
---- | -----------
`context` | 현재 사용자와 작업 중인 GitHub 컨텍스트에 대한 컨텍스트를 제공하는 도구
`copilot` | Copilot 관련 도구(예: Copilot 코딩 에이전트)
`copilot_spaces` | Copilot Spaces 관련 도구
`actions` | GitHub Actions 워크플로 및 CI/CD 작업
`code_security` | GitHub 코드 스캐닝과 같은 코드 보안 관련 도구
`dependabot` | Dependabot 도구
`discussions` | GitHub 토론 관련 도구
`experiments` | 아직 안정적인 것으로 간주되지 않는 실험적 기능
`gists` | GitHub Gist 관련 도구
`github_support_docs_search` | GitHub 제품 및 지원 질문에 답변하기 위해 문서 검색
`issues` | GitHub 문제 관련 도구
`labels` | GitHub 레이블 관련 도구
`notifications` | GitHub 알림 관련 도구
`orgs` | GitHub 조직 관련 도구
`projects` | GitHub 프로젝트 관련 도구
`pull_requests` | GitHub 끌어오기 요청 관련 도구
`repos` | GitHub 리포지토리 관련 도구
`secret_protection` | GitHub 비밀 스캐닝과 같은 비밀 보호 관련 도구
`security_advisories` | 보안 권고 관련 도구
`stargazers` | GitHub 스타게이저 관련 도구
`users` | GitHub 사용자 관련 도구

## 구성

원격 GitHub MCP 서버에는 사용 가능한 도구 세트 및 읽기 전용 모드를 구성하는 데 사용할 수 있는 선택적 헤더가 있습니다.

- `X-MCP-Toolsets`: 활성화할 도구 세트의 쉼표로 구분된 목록입니다. (예: "repos,issues")
    - 목록이 비어 있으면 기본 도구 세트가 사용됩니다. 잘못된 도구 세트가 제공되면 서버가 시작되지 않고 400 잘못된 요청 상태를 내보냅니다. 공백은 무시됩니다.

- `X-MCP-Readonly`: "읽기" 도구만 활성화합니다.
    - 이 헤더가 비어 있거나 "false", "f", "no", "n", "0" 또는 "off"(공백 및 대소문자 무시)이면 false로 해석됩니다. 다른 모든 값은 true로 해석됩니다.


## 추가 리소스

- [GitHub MCP 서버 리포지토리](https://github.com/github/github-mcp-server)
- [원격 GitHub MCP 서버 설명서](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)
- [GitHub MCP 서버에 대한 정책 및 거버넌스](https://github.com/github/github-mcp-server/blob/main/docs/policies-and-governance.md)
