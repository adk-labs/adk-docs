---
catalog_title: GitLab
catalog_description: 시맨틱 코드 검색을 수행하고 파이프라인을 점검하며 머지 리퀘스트를 관리합니다
catalog_icon: /adk-docs/integrations/assets/gitlab.png
catalog_tags: ["code", "mcp"]
---
# GitLab

[GitLab MCP 서버](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/)는
ADK 에이전트를 [GitLab.com](https://gitlab.com/) 또는 자체 관리형(Self-managed) GitLab 인스턴스에 직접 연결합니다.
이 통합을 통해 에이전트는 이슈(Issue) 및 머지 리퀘스트(Merge Request) 관리, CI/CD 파이프라인 검사,
시맨틱 코드 검색 수행, 자연어를 사용한 개발 워크플로 자동화 등의 기능을 수행할 수 있습니다.

## 사용 사례 (Use cases)

- **시맨틱 코드 탐색 (Semantic Code Exploration)**: 자연어를 사용하여 코드베이스를 탐색합니다.
  표준 텍스트 검색과 달리 코드의 로직과 의도를 질의하여 복잡한 구현을 빠르게 이해할 수 있습니다.

- **머지 리퀘스트 검토 가속화 (Accelerate Merge Request Reviews)**: 코드 변경 사항을 즉시 파악합니다.
  전체 머지 리퀘스트 컨텍스트를 검색하고, 특정 diff를 분석하고, 커밋 기록을 검토하여
  팀에 더 빠르고 의미 있는 피드백을 제공합니다.

- **CI/CD 파이프라인 문제 해결 (Troubleshoot CI/CD Pipelines)**: 채팅 화면을 벗어나지 않고 빌드 실패를 진단합니다.
  파이프라인 상태를 검사하고 상세 작업(job) 로그를 검색하여 특정 머지 리퀘스트나 커밋이
  검사에 실패한 정확한 원인을 파악합니다.

## 필수 조건 (Prerequisites)

- Premium 또는 Ultimate 구독 및 [GitLab Duo](https://docs.gitlab.com/user/gitlab_duo/)가 활성화된 GitLab 계정
- GitLab 설정에서 [베타 및 실험적 기능](https://docs.gitlab.com/user/gitlab_duo/turn_on_off/#turn-on-beta-and-experimental-features) 활성화

## 에이전트와 함께 사용하기 (Use with agent)

=== "로컬 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters

    # 자체 호스팅인 경우 인스턴스 URL로 교체하세요 (예: "gitlab.example.com")
    GITLAB_INSTANCE_URL = "gitlab.com"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="gitlab_agent",
        instruction="Help users get information from GitLab",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "mcp-remote",
                            f"https://{GITLAB_INSTANCE_URL}/api/v4/mcp",
                            "--static-oauth-client-metadata",
                            "{\"scope\": \"mcp\"}",
                        ],
                    ),
                    timeout=30,
                ),
            )
        ],
    )
    ```

!!! note

    이 에이전트를 처음 실행하면 브라우저 창이 자동으로 열리고 (인증 URL이 출력되며)
    OAuth 권한을 요청합니다. 에이전트가 GitLab 데이터에 액세스할 수 있도록
    이 요청을 승인해야 합니다.

## 사용 가능한 도구 (Available tools)

도구 | 설명
---- | -----------
`get_mcp_server_version` | GitLab MCP 서버의 현재 버전을 반환합니다.
`create_issue` | GitLab 프로젝트에 새 이슈를 생성합니다.
`get_issue` | 특정 GitLab 이슈에 대한 상세 정보를 검색합니다.
`create_merge_request` | 프로젝트에 머지 리퀘스트를 생성합니다.
`get_merge_request` | 특정 GitLab 머지 리퀘스트에 대한 상세 정보를 검색합니다.
`get_merge_request_commits` | 특정 머지 리퀘스트의 커밋 목록을 검색합니다.
`get_merge_request_diffs` | 특정 머지 리퀘스트의 diff(차이)를 검색합니다.
`get_merge_request_pipelines` | 특정 머지 리퀘스트의 파이프라인을 검색합니다.
`get_pipeline_jobs` | 특정 CI/CD 파이프라인의 작업(job)을 검색합니다.
`gitlab_search` | 검색 API를 사용하여 전체 GitLab 인스턴스에서 용어를 검색합니다.
`semantic_code_search` | 프로젝트 내에서 관련 코드 스니펫을 검색합니다.

## 추가 리소스 (Additional resources)

- [GitLab MCP 서버 문서](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/)
