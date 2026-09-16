---
catalog_title: Postman
catalog_description: API 컬렉션과 워크스페이스를 관리하고 클라이언트 코드를 생성합니다
catalog_icon: /integrations/assets/postman.png
catalog_tags: ["mcp"]
---

# ADK용 Postman MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span>
</div>

[Postman MCP Server](https://github.com/postmanlabs/postman-mcp-server)는
ADK 에이전트를 [Postman](https://www.postman.com/) 생태계와 연결합니다.
이 통합을 통해 에이전트는 자연어 상호작용으로 워크스페이스 접근,
컬렉션/환경 관리, API 평가, 워크플로 자동화를 수행할 수 있습니다.

## 사용 사례

- **API 테스트**: Postman 컬렉션을 사용해 API를 지속적으로 테스트합니다.

- **컬렉션 관리**: 편집기를 벗어나지 않고 컬렉션 생성/태깅,
  문서 업데이트, 코멘트 추가, 다중 컬렉션 작업을 수행합니다.

- **워크스페이스/환경 관리**: 워크스페이스와 환경을 생성하고
  환경 변수를 관리합니다.

- **클라이언트 코드 생성**: 베스트 프랙티스와 프로젝트 규약을 따르는
  프로덕션급 API 클라이언트 코드를 생성합니다.

## 사전 준비 사항

- [Postman 계정](https://identity.getpostman.com/signup) 생성
- [Postman API 키](https://postman.postman.co/settings/me/api-keys) 생성

## 에이전트와 함께 사용

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

## 구성

Postman은 세 가지 도구 구성 모드를 제공합니다:

- **Minimal**(기본값): 기본 Postman 작업용 핵심 도구.
  컬렉션/워크스페이스/환경의 단순 수정에 적합합니다.
- **Full**: 사용 가능한 모든 Postman API 도구(100개 이상).
  고급 협업 및 엔터프라이즈 기능에 적합합니다.
- **Code**: API 정의 검색 및 클라이언트 코드 생성 도구.
  API 소비 코드가 필요한 개발자에게 적합합니다.

구성 선택 방법:

- **로컬 서버**: `args` 목록에 `--full` 또는 `--code` 추가.
- **원격 서버**: URL 경로를 `/minimal`, `/mcp`(full), `/code`로 변경.

EU 리전은 `--region eu`(로컬) 또는 `https://mcp.eu.postman.com`(원격)을 사용하세요.

## 추가 리소스

- [Postman MCP Server on GitHub](https://github.com/postmanlabs/postman-mcp-server)
- [Postman API key settings](https://postman.postman.co/settings/me/api-keys)
- [Postman Learning Center](https://learning.postman.com/)
