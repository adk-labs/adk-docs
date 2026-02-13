---
catalog_title: Atlassian
catalog_description: 이슈를 관리하고 페이지를 검색하며 팀 콘텐츠를 업데이트합니다
catalog_icon: /adk-docs/integrations/assets/atlassian.png
catalog_tags: ["mcp"]
---

# ADK용 Atlassian MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Atlassian MCP Server](https://github.com/atlassian/atlassian-mcp-server)는
ADK 에이전트를 [Atlassian](https://www.atlassian.com/)
생태계와 연결하여 Jira의 프로젝트 추적과 Confluence의 지식 관리 간
간극을 메워줍니다. 이 통합을 통해 에이전트는 자연어로
이슈를 관리하고, 문서 페이지를 검색/수정하고,
협업 워크플로를 간소화할 수 있습니다.

## 사용 사례

- **통합 지식 검색**: Jira 이슈와 Confluence 페이지를 동시에 검색해
  프로젝트 사양, 의사결정, 과거 컨텍스트를 찾습니다.

- **이슈 관리 자동화**: Jira 이슈를 생성, 편집, 전환하거나
  기존 티켓에 코멘트를 추가합니다.

- **문서 어시스턴트**: 에이전트에서 직접 Confluence 문서의 페이지 내용을
  조회하고, 초안을 생성하거나, 인라인 코멘트를 추가합니다.

## 사전 준비 사항

- [Atlassian 계정](https://id.atlassian.com/signup) 가입
- Jira 및/또는 Confluence가 있는 Atlassian Cloud 사이트

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
            name="atlassian_agent",
            instruction="Help users work with data in Atlassian products",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.atlassian.com/v1/mcp",
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
            name: "atlassian_agent",
            instruction: "Help users work with data in Atlassian products",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.atlassian.com/v1/mcp",
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
    인증 URL을 사용할 수도 있습니다. 에이전트가 Atlassian 데이터에 접근하려면
    이 요청을 승인해야 합니다.

## 사용 가능한 도구

Tool | Description
---- | -----------
`atlassianUserInfo` | 사용자 정보 가져오기
`getAccessibleAtlassianResources` | 접근 가능한 Atlassian 리소스 정보 가져오기
`getJiraIssue` | Jira 이슈 정보 가져오기
`editJiraIssue` | Jira 이슈 수정
`createJiraIssue` | 새 Jira 이슈 생성
`getTransitionsForJiraIssue` | Jira 이슈 전환 상태 가져오기
`transitionJiraIssue` | Jira 이슈 전환
`lookupJiraAccountId` | Jira 계정 ID 조회
`searchJiraIssuesUsingJql` | JQL로 Jira 이슈 검색
`addCommentToJiraIssue` | Jira 이슈에 코멘트 추가
`getJiraIssueRemoteIssueLinks` | Jira 이슈의 원격 이슈 링크 가져오기
`getVisibleJiraProjects` | 표시 가능한 Jira 프로젝트 가져오기
`getJiraProjectIssueTypesMetadata` | Jira 프로젝트 이슈 유형 메타데이터 가져오기
`getJiraIssueTypeMetaWithFields` | Jira 이슈의 필드 포함 이슈 유형 메타데이터 가져오기
`getConfluenceSpaces` | Confluence 스페이스 정보 가져오기
`getConfluencePage` | Confluence 페이지 정보 가져오기
`getPagesInConfluenceSpace` | Confluence 스페이스의 페이지 정보 가져오기
`getConfluencePageFooterComments` | Confluence 페이지 하단 코멘트 정보 가져오기
`getConfluencePageInlineComments` | Confluence 페이지 인라인 코멘트 정보 가져오기
`getConfluencePageDescendants` | Confluence 페이지 하위 항목 정보 가져오기
`createConfluencePage` | 새 Confluence 페이지 생성
`updateConfluencePage` | 기존 Confluence 페이지 업데이트
`createConfluenceFooterComment` | Confluence 페이지에 하단 코멘트 생성
`createConfluenceInlineComment` | Confluence 페이지에 인라인 코멘트 생성
`searchConfluenceUsingCql` | CQL로 Confluence 검색
`search` | 정보 검색
`fetch` | 정보 가져오기

## 추가 리소스

- [Atlassian MCP Server Repository](https://github.com/atlassian/atlassian-mcp-server)
- [Atlassian MCP Server Documentation](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)
