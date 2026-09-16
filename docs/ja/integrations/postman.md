---
catalog_title: Postman
catalog_description: API コレクション、ワークスペース管理、クライアントコード生成を行います
catalog_icon: /integrations/assets/postman.png
catalog_tags: ["mcp"]
---

# ADK 向け Postman MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span>
</div>

[Postman MCP Server](https://github.com/postmanlabs/postman-mcp-server) は
ADK エージェントを [Postman](https://www.postman.com/) エコシステムへ接続します。
この連携により、エージェントは自然言語操作でワークスペースアクセス、
コレクション/環境管理、API 評価、ワークフロー自動化を実行できます。

## ユースケース

- **API テスト**: Postman コレクションを使って API を継続的にテストします。

- **コレクション管理**: エディタを離れずにコレクション作成/タグ付け、
  ドキュメント更新、コメント追加、複数コレクション操作を実行できます。

- **ワークスペース/環境管理**: ワークスペースと環境を作成し、
  環境変数を管理します。

- **クライアントコード生成**: ベストプラクティスとプロジェクト規約に沿った
  本番利用可能な API クライアントコードを生成します。

## 前提条件

- [Postman アカウント](https://identity.getpostman.com/signup) 作成
- [Postman API キー](https://postman.postman.co/settings/me/api-keys) 生成

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="postman_agent",
            instruction="Help users manage their Postman workspaces and collections",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@postman/postman-mcp-server",
                                # "--full",  # Use all 100+ tools
                                # "--code",  # Use code generation tools
                                # "--region", "eu",  # Use EU region
                            ],
                            env={
                                "POSTMAN_API_KEY": POSTMAN_API_KEY,
                            },
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

        POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="postman_agent",
            instruction="Help users manage their Postman workspaces and collections",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPServerParams(
                        url="https://mcp.postman.com/mcp",
                        # (Optional) Use "/minimal" for essential tools only
                        # (Optional) Use "/code" for code generation tools
                        # (Optional) Use "https://mcp.eu.postman.com" for EU region
                        headers={
                            "Authorization": f"Bearer {POSTMAN_API_KEY}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "postman_agent",
            instruction: "Help users manage their Postman workspaces and collections",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "@postman/postman-mcp-server",
                            // "--full",  // Use all 100+ tools
                            // "--code",  // Use code generation tools
                            // "--region", "eu",  // Use EU region
                        ],
                        env: {
                            POSTMAN_API_KEY: POSTMAN_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const POSTMAN_API_KEY = "YOUR_POSTMAN_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "postman_agent",
            instruction: "Help users manage their Postman workspaces and collections",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.postman.com/mcp",
                    // (Optional) Use "/minimal" for essential tools only
                    // (Optional) Use "/code" for code generation tools
                    // (Optional) Use "https://mcp.eu.postman.com" for EU region
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${POSTMAN_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

=== "Go"

    === "Local MCP Server"

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

        const postmanAPIKey = "YOUR_POSTMAN_API_KEY"

        func main() {
        	ctx := context.Background()

        	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{
        		APIKey: os.Getenv("GOOGLE_API_KEY"),
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the model: %v", err)
        	}

        	args := []string{"-y", "@postman/postman-mcp-server"}
        	// args = append(args, "--full")          // Use all 100+ tools
        	// args = append(args, "--code")          // Use code generation tools
        	// args = append(args, "--region", "eu")  // Use EU region

        	server := exec.CommandContext(ctx, "npx", args...)
        	// Forward only what npx needs, plus the Postman key. The parent environment
        	// may hold unrelated secrets, such as the GOOGLE_API_KEY read above.
        	server.Env = []string{"POSTMAN_API_KEY=" + postmanAPIKey}
        	for _, k := range []string{
        		"PATH", "HOME", // POSIX
        		"APPDATA", "LOCALAPPDATA", "TEMP", "USERPROFILE", // Windows
        	} {
        		if v, ok := os.LookupEnv(k); ok {
        			server.Env = append(server.Env, k+"="+v)
        		}
        	}

        	postman, err := mcptoolset.New(mcptoolset.Config{
        		Transport: &mcp.CommandTransport{Command: server},
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the Postman tool set: %v", err)
        	}

        	rootAgent, err := llmagent.New(llmagent.Config{
        		Model:       model,
        		Name:        "postman_agent",
        		Instruction: "Help users manage their Postman workspaces and collections",
        		Toolsets:    []tool.Toolset{postman},
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

    === "Remote MCP Server"

        ```go
        package main

        import (
        	"context"
        	"log"
        	"os"

        	"google.golang.org/genai"

        	"google.golang.org/adk/v2/agent"
        	"google.golang.org/adk/v2/agent/llmagent"
        	"google.golang.org/adk/v2/auth"
        	"google.golang.org/adk/v2/cmd/launcher"
        	"google.golang.org/adk/v2/cmd/launcher/full"
        	"google.golang.org/adk/v2/model/gemini"
        	"google.golang.org/adk/v2/tool"
        	"google.golang.org/adk/v2/tool/mcptoolset"
        )

        const postmanAPIKey = "YOUR_POSTMAN_API_KEY"

        func main() {
        	ctx := context.Background()

        	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{
        		APIKey: os.Getenv("GOOGLE_API_KEY"),
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the model: %v", err)
        	}

        	postman, err := mcptoolset.New(mcptoolset.Config{
        		// (Optional) Use "/minimal" for essential tools only
        		// (Optional) Use "/code" for code generation tools
        		// (Optional) Use "https://mcp.eu.postman.com/mcp" for EU region
        		Endpoint: "https://mcp.postman.com/mcp",
        		// Auth sets "Authorization: Bearer <key>" on every request.
        		Auth: auth.StaticToken(postmanAPIKey),
        	})
        	if err != nil {
        		log.Fatalf("Failed to create the Postman tool set: %v", err)
        	}

        	rootAgent, err := llmagent.New(llmagent.Config{
        		Model:       model,
        		Name:        "postman_agent",
        		Instruction: "Help users manage their Postman workspaces and collections",
        		Toolsets:    []tool.Toolset{postman},
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

## 設定

Postman は 3 種類のツール構成を提供します:

- **Minimal** (デフォルト): 基本的な Postman 操作用の最小セット。
  コレクション/ワークスペース/環境の簡易変更向け。
- **Full**: 利用可能な Postman API ツール全体 (100+ ツール)。
  高度な協業やエンタープライズ機能向け。
- **Code**: API 定義検索とクライアントコード生成向け。
  API 利用コードが必要な開発者向け。

構成選択方法:

- **ローカルサーバー**: `args` に `--full` または `--code` を追加。
- **リモートサーバー**: URL パスを `/minimal`、`/mcp` (full)、`/code` に変更。

EU リージョンでは `--region eu` (ローカル) または `https://mcp.eu.postman.com` (リモート) を使用します。

## 追加リソース

- [Postman MCP Server on GitHub](https://github.com/postmanlabs/postman-mcp-server)
- [Postman API key settings](https://postman.postman.co/settings/me/api-keys)
- [Postman Learning Center](https://learning.postman.com/)
