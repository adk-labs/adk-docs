---
catalog_title: Notion
catalog_description: ワークスペースを検索し、ページを作成し、タスクとデータベースを管理します
catalog_icon: /integrations/assets/notion.png
catalog_tags: ["mcp"]
---
# Notion

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span>
</div>

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

=== "Python"

    === "ローカル MCP サーバー"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        NOTION_TOKEN = "YOUR_NOTION_TOKEN"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="notion_agent",
            instruction="Help users get information from Notion",
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

=== "TypeScript"

    === "ローカル MCP サーバー"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const NOTION_TOKEN = "YOUR_NOTION_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "notion_agent",
            instruction: "Help users get information from Notion",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@notionhq/notion-mcp-server"],
                        env: {
                            NOTION_TOKEN: NOTION_TOKEN,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

=== "Go"

    === "ローカル MCP サーバー"

        ```go
        package main

        import (
        	"context"
        	"log"
        	"os"
        	"os/exec"

        	"github.com/modelcontextprotocol/go-sdk/mcp"
        	"google.golang.org/genai"

        	"google.golang.org/adk/v2/agent"
        	"google.golang.org/adk/v2/agent/llmagent"
        	"google.golang.org/adk/v2/cmd/launcher"
        	"google.golang.org/adk/v2/cmd/launcher/full"
        	"google.golang.org/adk/v2/model/gemini"
        	"google.golang.org/adk/v2/tool"
        	"google.golang.org/adk/v2/tool/mcptoolset"
        )

        const notionToken = "YOUR_NOTION_TOKEN"

        func main() {
        	ctx := context.Background()

        	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{
        		APIKey: os.Getenv("GOOGLE_API_KEY"),
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the model: %v", err)
        	}

        	server := exec.CommandContext(ctx, "npx", "-y", "@notionhq/notion-mcp-server")
        	// Forward only what npx needs, plus the Notion token. The parent environment
        	// may hold unrelated secrets, such as the GOOGLE_API_KEY read above.
        	server.Env = []string{"NOTION_TOKEN=" + notionToken}
        	for _, k := range []string{
        		"PATH", "HOME", // POSIX
        		"APPDATA", "LOCALAPPDATA", "TEMP", "USERPROFILE", // Windows
        	} {
        		if v, ok := os.LookupEnv(k); ok {
        			server.Env = append(server.Env, k+"="+v)
        		}
        	}

        	notion, err := mcptoolset.New(mcptoolset.Config{
        		Transport: &mcp.CommandTransport{Command: server},
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the Notion tool set: %v", err)
        	}

        	rootAgent, err := llmagent.New(llmagent.Config{
        		Model:       model,
        		Name:        "notion_agent",
        		Instruction: "Help users get information from Notion",
        		Toolsets:    []tool.Toolset{notion},
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the agent: %v", err)
        	}

        	l := full.NewLauncher()
        	cfg := &launcher.Config{AgentLoader: agent.NewSingleLoader(rootAgent)}
        	if err := l.Execute(ctx, cfg, os.Args[1:]); err != nil {
        		log.Fatalf("Run failed: %v\n\n%s", err, l.CommandLineSyntax())
        	}
        }
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
