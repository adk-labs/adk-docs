---
catalog_title: Atlassian
catalog_description: 課題を管理し、ページを検索し、チームコンテンツを更新します
catalog_icon: /adk-docs/integrations/assets/atlassian.png
catalog_tags: ["mcp"]
---

# ADK 向け Atlassian MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Atlassian MCP Server](https://github.com/atlassian/atlassian-mcp-server) は
ADK エージェントを [Atlassian](https://www.atlassian.com/) エコシステムへ接続し、
Jira のプロジェクト追跡と Confluence のナレッジ管理の橋渡しを行います。
この連携により、エージェントは自然言語で課題管理、ドキュメントページの検索/更新、
コラボレーションワークフローの効率化を実行できます。

## ユースケース

- **統合ナレッジ検索**: Jira 課題と Confluence ページを同時に検索し、
  仕様、意思決定、過去のコンテキストを見つけます。

- **課題管理の自動化**: Jira 課題を作成・編集・遷移したり、
  既存チケットへコメントを追加します。

- **ドキュメントアシスタント**: エージェントから直接 Confluence ドキュメントの
  ページ内容取得、ドラフト生成、インラインコメント追加を行います。

## 前提条件

- [Atlassian アカウント](https://id.atlassian.com/signup) の作成
- Jira および/または Confluence を含む Atlassian Cloud サイト

## エージェントで使う

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

    このエージェントを初めて実行すると、OAuth によるアクセス許可を要求するため
    ブラウザウィンドウが自動で開きます。あるいはコンソールに表示される
    認可 URL を使用することもできます。エージェントが Atlassian データへアクセスするには
    この要求を承認する必要があります。

## 利用可能なツール

Tool | Description
---- | -----------
`atlassianUserInfo` | ユーザー情報を取得
`getAccessibleAtlassianResources` | アクセス可能な Atlassian リソース情報を取得
`getJiraIssue` | Jira 課題情報を取得
`editJiraIssue` | Jira 課題を編集
`createJiraIssue` | 新しい Jira 課題を作成
`getTransitionsForJiraIssue` | Jira 課題の遷移情報を取得
`transitionJiraIssue` | Jira 課題を遷移
`lookupJiraAccountId` | Jira アカウント ID を検索
`searchJiraIssuesUsingJql` | JQL で Jira 課題を検索
`addCommentToJiraIssue` | Jira 課題にコメントを追加
`getJiraIssueRemoteIssueLinks` | Jira 課題のリモート課題リンクを取得
`getVisibleJiraProjects` | 表示可能な Jira プロジェクトを取得
`getJiraProjectIssueTypesMetadata` | Jira プロジェクトの課題タイプメタデータを取得
`getJiraIssueTypeMetaWithFields` | Jira 課題のフィールド付き課題タイプメタデータを取得
`getConfluenceSpaces` | Confluence スペース情報を取得
`getConfluencePage` | Confluence ページ情報を取得
`getPagesInConfluenceSpace` | Confluence スペース内ページ情報を取得
`getConfluencePageFooterComments` | Confluence ページのフッターコメント情報を取得
`getConfluencePageInlineComments` | Confluence ページのインラインコメント情報を取得
`getConfluencePageDescendants` | Confluence ページの子孫ページ情報を取得
`createConfluencePage` | 新しい Confluence ページを作成
`updateConfluencePage` | 既存 Confluence ページを更新
`createConfluenceFooterComment` | Confluence ページにフッターコメントを作成
`createConfluenceInlineComment` | Confluence ページにインラインコメントを作成
`searchConfluenceUsingCql` | CQL を使って Confluence を検索
`search` | 情報を検索
`fetch` | 情報を取得

## 追加リソース

- [Atlassian MCP Server Repository](https://github.com/atlassian/atlassian-mcp-server)
- [Atlassian MCP Server Documentation](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)
