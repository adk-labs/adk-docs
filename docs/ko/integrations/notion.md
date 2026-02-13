---
catalog_title: Notion
catalog_description: 워크스페이스를 검색하고 페이지를 생성하며 작업과 데이터베이스를 관리합니다
catalog_icon: /adk-docs/integrations/assets/notion.png
catalog_tags: ["mcp"]
---
# Notion

[Notion MCP 서버](https://github.com/makenotion/notion-mcp-server)는 ADK 에이전트를 Notion에 연결하여 작업 공간 내에서 페이지, 데이터베이스 등을 검색, 생성 및 관리할 수 있도록 합니다. 이를 통해 에이전트는 자연어를 사용하여 Notion 작업 공간의 콘텐츠를 쿼리, 생성 및 구성할 수 있습니다.

## 사용 사례

- **작업 공간 검색**: 콘텐츠를 기반으로 프로젝트 페이지, 회의록 또는 문서를 찾습니다.

- **새 콘텐츠 만들기**: 회의록, 프로젝트 계획 또는 작업에 대한 새 페이지를 생성합니다.

- **작업 및 데이터베이스 관리**: 작업 상태를 업데이트하거나, 데이터베이스에 항목을 추가하거나, 속성을 변경합니다.

- **작업 공간 구성**: 페이지를 이동하거나, 템플릿을 복제하거나, 문서에 댓글을 추가합니다.

## 전제 조건

- 프로필의 [Notion 통합](https://www.notion.so/profile/integrations)으로 이동하여 Notion 통합 토큰을 얻습니다. 자세한 내용은 [인증 설명서](https://developers.notion.com/docs/authorization)를 참조하세요.
- 관련 페이지 및 데이터베이스에 통합이 액세스할 수 있는지 확인합니다. [Notion 통합](https://www.notion.so/profile/integrations) 설정의 액세스 탭을 방문한 다음 사용하려는 페이지를 선택하여 액세스 권한을 부여합니다.

## 에이전트와 함께 사용

=== "로컬 MCP 서버"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool import McpToolset
    from mcp import StdioServerParameters

    NOTION_TOKEN = "YOUR_NOTION_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="notion_agent",
        instruction="사용자가 Notion에서 정보를 얻도록 돕습니다.",
        tools=[
            McpToolset(
                connection_params=StdioConnectionParams(
                    server_params = StdioServerParameters(
                        command="npx",
                        args=[
                            "-y",
                            "@notionhq/notion-mcp-server",
                        ],
                        env={
                            "NOTION_TOKEN": NOTION_TOKEN,
                        }
                    ),
                    timeout=30,
                ),
            )
        ],
    )
    ```

## 사용 가능한 도구

도구 <img width="200px"/> | 설명
---- | -----------
`notion-search` | Notion 작업 공간 및 Slack, Google Drive, Jira와 같은 연결된 도구에서 검색합니다. AI 기능을 사용할 수 없는 경우 기본 작업 공간 검색으로 대체됩니다.
`notion-fetch` | URL로 Notion 페이지 또는 데이터베이스에서 콘텐츠를 검색합니다.
`notion-create-pages` | 지정된 속성 및 콘텐츠로 하나 이상의 Notion 페이지를 만듭니다.
`notion-update-page` | Notion 페이지의 속성 또는 콘텐츠를 업데이트합니다.
`notion-move-pages` | 하나 이상의 Notion 페이지 또는 데이터베이스를 새 상위 항목으로 이동합니다.
`notion-duplicate-page` | 작업 공간 내에서 Notion 페이지를 복제합니다. 이 작업은 비동기적으로 완료됩니다.
`notion-create-database` | 지정된 속성으로 새 Notion 데이터베이스, 초기 데이터 원본 및 초기 보기를 만듭니다.
`notion-update-database` | Notion 데이터 원본의 속성, 이름, 설명 또는 기타 특성을 업데이트합니다.
`notion-create-comment` | 페이지에 댓글 추가
`notion-get-comments` | 스레드 토론을 포함하여 특정 페이지의 모든 댓글을 나열합니다.
`notion-get-teams` | 현재 작업 공간의 팀(팀스페이스) 목록을 검색합니다.
`notion-get-users` | 작업 공간의 모든 사용자를 세부 정보와 함께 나열합니다.
`notion-get-user` | ID로 사용자 정보 검색
`notion-get-self` | 자신의 봇 사용자와 연결된 Notion 작업 공간에 대한 정보를 검색합니다.

## 추가 리소스

- [Notion MCP 서버 설명서](https://developers.notion.com/docs/mcp)
- [Notion MCP 서버 리포지토리](https://github.com/makenotion/notion-mcp-server)
