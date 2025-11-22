---
hide:
  - toc
---
# Notion

[Notion MCP Server](https://github.com/makenotion/notion-mcp-server)は、ADKエージェントをNotionに接続し、ワークスペース内でページ、データベースなどを検索、作成、管理できるようにします。これにより、エージェントは自然言語を使用してNotionワークスペース内のコンテンツをクエリ、作成、整理できます。

## ユースケース

- **ワークスペースの検索**: コンテンツに基づいてプロジェクトページ、会議の議事録、またはドキュメントを検索します。

- **新しいコンテンツの作成**: 会議の議事録、プロジェクト計画、またはタスク用の新しいページを生成します。

- **タスクとデータベースの管理**: タスクのステータスを更新したり、データベースにアイテムを追加したり、プロパティを変更したりします。

- **ワークスペースの整理**: ページを移動したり、テンプレートを複製したり、ドキュメントにコメントを追加したりします。

## 前提条件

- プロフィールの[Notionインテグレーション](https://www.notion.so/profile/integrations)に移動して、Notionインテグレーショントークンを取得します。詳細については、[認証ドキュメント](https://developers.notion.com/docs/authorization)を参照してください。
- 関連するページとデータベースにインテグレーションがアクセスできることを確認します。[Notionインテグレーション](https://www.notion.so/profile/integrations)設定の[アクセス]タブにアクセスし、使用したいページを選択してアクセスを許可します。

## エージェントでの使用

=== "ローカルMCPサーバー"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from google.adk.tools.mcp_tool import McpToolset
    from mcp import StdioServerParameters

    NOTION_TOKEN = "YOUR_NOTION_TOKEN"

    root_agent = Agent(
        model="gemini-2.5-pro",
        name="notion_agent",
        instruction="ユーザーがNotionから情報を取得するのを支援します",
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

## 利用可能なツール

ツール <img width="200px"/> | 説明
---- | -----------
`notion-search` | Notionワークスペースと、Slack、Googleドライブ、Jiraなどの接続されたツールを横断して検索します。AI機能が利用できない場合は、基本的なワークスペース検索にフォールバックします。
`notion-fetch` | URLによってNotionページまたはデータベースからコンテンツを取得します。
`notion-create-pages` | 指定されたプロパティとコンテンツを持つ1つ以上のNotionページを作成します。
`notion-update-page` | Notionページのプロパティまたはコンテンツを更新します。
`notion-move-pages` | 1つ以上のNotionページまたはデータベースを新しい親に移動します。
`notion-duplicate-page` | ワークスペース内でNotionページを複製します。このアクションは非同期で完了します。
`notion-create-database` | 指定されたプロパティを持つ新しいNotionデータベース、初期データソース、および初期ビューを作成します。
`notion-update-database` | Notionデータソースのプロパティ、名前、説明、またはその他の属性を更新します。
`notion-create-comment` | ページにコメントを追加します
`notion-get-comments` | スレッド化されたディスカッションを含む、特定のページのすべてのコメントを一覧表示します。
`notion-get-teams` | 現在のワークスペースのチーム（チームスペース）のリストを取得します。
`notion-get-users` | ワークスペース内のすべてのユーザーを詳細とともに一覧表示します。
`notion-get-user` | IDでユーザー情報を取得します
`notion-get-self` | 独自のボットユーザーと接続しているNotionワークスペースに関する情報を取得します。

## 追加リソース

- [Notion MCPサーバードキュメント](https://developers.notion.com/docs/mcp)
- [Notion MCPサーバーリポジトリ](https://github.com/makenotion/notion-mcp-server)
