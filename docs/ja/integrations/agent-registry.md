---
catalog_title: Google Cloud Agent Registry
catalog_description: AI エージェントと MCP サーバーを検出して接続する
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["google", "mcp", "connectors"]
---


# Google Cloud エージェント レジ스트リ

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.26.0</span><span class="lst-go">Go v2.1.0</span><span class="lst-preview">プレビュー</span>
</div>

Agent Development Kit (ADK) 内の Agent Registry クライアント ライブラリを使用すると、開発者は [Google Cloud Agent Registry](https://docs.cloud.google.com/agent-registry/overview) にカタログ化されている AI エージェントや MCP サーバーを検出、検索、接続できます。これにより、管理対象のコンポーネントを使用したエージェントベースのアプリケーションの動的な構成が可能になります。

## 使用例

- **開発の加速**: 既存のエージェントやツール (MCP サーバー) を再構築するのではなく、中央カタログから簡単に見つけて再利用できます。
- **動的統合**: 実行時にエージェントや MCP サーバーのエンドポイントを検出し、環境の変化に対してアプリケーションをより堅牢にします。
- **強化されたガバナンス**: ADK アプリケーション内でレジストリの管理および検証されたコンポーネントを利用します。

## 前提条件

- [Google Cloud プロジェクト](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects)。
- Google Cloud プロジェクトで有効化された [Agent Registry API](https://docs.cloud.google.com/agent-registry/setup)。
- お使いの環境に合わせて構成された認証。[Application Default Credentials](https://docs.cloud.google.com/docs/authentication/application-default-credentials) (`gcloud auth application-default login`) を使用してログインしてください。
- 環境変数 `GOOGLE_CLOUD_PROJECT` をプロジェクト ID に設定し、`GOOGLE_CLOUD_LOCATION` を適切なリージョン (例: `global`、`us-central1`) に設定します。
- [インストール](#installation) の説明に従って使用言語の ADK をインストール。

ADK エージェントから Google Cloud への接続に関する詳細については、[Google Cloud および Agent Platform への接続](/get-started/google-cloud/) を参照してください。

## インストール

[Agent Registry](https://docs.cloud.google.com/agent-registry/overview) 統合はコア ADK ライブラリの一部です。

=== "Python"

    ```bash
    pip install google-adk
    ```

    ### 必須の依存関係

    `google.adk.integrations.agent_registry` モジュールは、モジュールスコープで A2A SDK と エージェント ID (Agent Identity) 認証プロバイダーの両方をインポートするため、コア機能のみのインストールでは `AgentRegistry` インポート時に `ImportError` が発生します。`a2a` と `agent-identity` の両方の追加パッケージをインストールしてください。

    ```bash
    pip install "google-adk[a2a,agent-identity]"
    ```

=== "Go"

    ```bash
    go get google.golang.org/adk/v2
    ```

    クライアントはコアモジュールの `google.golang.org/adk/v2/agentregistry` パッケージに含まれているため、追加でインストールするものはありません。

## エージェントと一緒に使用する

ADK エージェント内で Agent Registry 統合を使用する主な方法は、Agent Registry クライアントを使用してリモートエージェントやツールセットを動的に取得することです。

=== "Python"

    ```py
    from google.adk.agents.llm_agent import LlmAgent
    from google.adk.integrations.agent_registry import AgentRegistry
    import os

    # 1. Initialization
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")

    registry = AgentRegistry(
        project_id=project_id,
        location=location,
    )

    # 2. Listing Resources
    print("Listing Agents...")
    agents_response = registry.list_agents()
    for agent in agents_response.get("agents", []):
        print(f"  - {agent.get('name')} ({agent.get('displayName')})")

    print("Listing MCP Servers...")
    mcp_servers_response = registry.list_mcp_servers()
    for server in mcp_servers_response.get("mcpServers", []):
        print(f"  - {server.get('name')} ({server.get('displayName')})")

    # 3. Using a Remote A2A Agent
    # Replace with the full resource name of your registered agent
    agent_name = f"projects/{project_id}/locations/{location}/agents/YOUR_AGENT_ID"
    my_remote_agent = registry.get_remote_a2a_agent(agent_name=agent_name)

    # 4. Using an MCP Toolset
    # Replace with the full resource name of your registered MCP server
    mcp_server_name = f"projects/{project_id}/locations/{location}/mcpServers/YOUR_MCP_SERVER_ID"
    my_mcp_toolset = registry.get_mcp_toolset(mcp_server_name=mcp_server_name)

    # 5. Example Agent Composition
    main_agent = LlmAgent(
        model="gemini-flash-latest", # Or your preferred model
        name="demo_agent",
        instruction="You can leverage registered tools and sub-agents.",
        tools=[my_mcp_toolset],
        sub_agents=[my_remote_agent],
    )
    ```

=== "Go"

    ```go
    package main

    import (
    	"cmp"
    	"context"
    	"fmt"
    	"log"
    	"os"

    	"google.golang.org/genai"

    	"google.golang.org/adk/v2/agent"
    	"google.golang.org/adk/v2/agent/llmagent"
    	"google.golang.org/adk/v2/agentregistry"
    	"google.golang.org/adk/v2/cmd/launcher"
    	"google.golang.org/adk/v2/cmd/launcher/full"
    	"google.golang.org/adk/v2/model/gemini"
    	"google.golang.org/adk/v2/tool"
    )

    func main() {
    	ctx := context.Background()

    	// 1. Initialization
    	projectID := os.Getenv("GOOGLE_CLOUD_PROJECT")
    	if projectID == "" {
    		log.Fatal("GOOGLE_CLOUD_PROJECT environment variable not set.")
    	}
    	location := cmp.Or(os.Getenv("GOOGLE_CLOUD_LOCATION"), "global")

    	registry, err := agentregistry.New(ctx, agentregistry.Config{
    		ProjectID: projectID,
    		Location:  location,
    	})
    	if err != nil {
    		log.Fatalf("Failed to create the registry client: %v", err)
    	}

    	// 2. Listing Resources. The All* iterators fetch pages on demand and
    	// report a failed page fetch as a single (nil, error).
    	fmt.Println("Listing Agents...")
    	for a, err := range registry.AllAgents(ctx) {
    		if err != nil {
    			log.Fatalf("Failed to list agents: %v", err)
    		}
    		fmt.Printf("  - %s (%s)\n", a.Name, a.DisplayName)
    	}

    	fmt.Println("Listing MCP Servers...")
    	for s, err := range registry.AllMCPServers(ctx) {
    		if err != nil {
    			log.Fatalf("Failed to list MCP servers: %v", err)
    		}
    		fmt.Printf("  - %s (%s)\n", s.Name, s.DisplayName)
    	}

    	// 3. Using a Remote A2A Agent
    	// Replace with the full resource name of your registered agent
    	agentName := fmt.Sprintf("projects/%s/locations/%s/agents/YOUR_AGENT_ID", projectID, location)
    	myRemoteAgent, err := registry.RemoteAgent(ctx, agentName)
    	if err != nil {
    		log.Fatalf("Failed to resolve the remote agent: %v", err)
    	}

    	// 4. Using an MCP Toolset
    	// Replace with the full resource name of your registered MCP server
    	mcpServerName := fmt.Sprintf("projects/%s/locations/%s/mcpServers/YOUR_MCP_SERVER_ID", projectID, location)
    	myMCPToolset, err := registry.MCPToolset(ctx, mcpServerName)
    	if err != nil {
    		log.Fatalf("Failed to connect to the MCP server: %v", err)
    	}

    	// 5. Example Agent Composition
    	model, err := gemini.NewModel(ctx, "gemini-flash-latest", &genai.ClientConfig{})
    	if err != nil {
    		log.Fatalf("Failed to create the model: %v", err)
    	}

    	rootAgent, err := llmagent.New(llmagent.Config{
    		Name:        "demo_agent",
    		Model:       model,
    		Instruction: "You can leverage registered tools and sub-agents.",
    		Toolsets:    []tool.Toolset{myMCPToolset},
    		SubAgents:   []agent.Agent{myRemoteAgent},
    	})
    	if err != nil {
    		log.Fatalf("Failed to create the agent: %v", err)
    	}

    	config := &launcher.Config{AgentLoader: agent.NewSingleLoader(rootAgent)}
    	l := full.NewLauncher()
    	if err := l.Execute(ctx, config, os.Args[1:]); err != nil {
    		log.Fatalf("Run failed: %v\n\n%s", err, l.CommandLineSyntax())
    	}
    }
    ```

## Google MCP サーバーとリモート A2A エージェントの認証

### リモート A2A エージェント

リモート A2A エージェントへの呼び出しは自動的には認証されません。Google A2A エージェントに接続する場合は、リモートエージェントの作成時に認証済みの HTTP クライアントを指定してください。

=== "Python"

    Google 認証ヘッダーが設定された `httpx.AsyncClient` を `get_remote_a2a_agent` メソッドに渡します。

    ```python
    import httpx
    import google.auth
    from google.auth.transport.requests import Request

    class GoogleAuth(httpx.Auth):
        def __init__(self):
            self.creds, _ = google.auth.default()
        def auth_flow(self, request):
            if not self.creds.valid:
                self.creds.refresh(Request())
            request.headers["Authorization"] = f"Bearer {self.creds.token}"
            yield request

    httpx_client = httpx.AsyncClient(auth=GoogleAuth(), timeout=httpx.Timeout(60.0))
    remote_agent = registry.get_remote_a2a_agent(
        f"projects/{project_id}/locations/{location}/agents/YOUR_AGENT_ID",
        httpx_client=httpx_client,
    )
    ```

=== "Go"

    認証済みの `*http.Client` を `WithA2AHTTPClient` で渡すか、静的ヘッダーを `WithA2AHeaders` で渡します。

    ```go
    import (
    	"golang.org/x/oauth2/google"

    	"google.golang.org/adk/v2/agentregistry"
    )

    httpClient, err := google.DefaultClient(ctx, "https://www.googleapis.com/auth/cloud-platform")
    if err != nil {
    	log.Fatalf("Failed to load Application Default Credentials: %v", err)
    }

    remoteAgent, err := registry.RemoteAgent(ctx, agentName,
    	agentregistry.WithA2AHTTPClient(httpClient),
    )
    ```

    タイムアウトは、リクエスト全体に適用されストリーミングレスポンスを途切れさせる可能性のある `http.Client.Timeout` ではなく、クライアントの `Transport` に設定してください。

### Google MCP サーバー

Google MCP サーバーの場合、認証ヘッダーは自動的に渡されます。

=== "Python"

    自動認証が期待どおりに機能しない場合は、`AgentRegistry` コンストラクターの `header_provider` 引数を使用して手動でヘッダーを指定できます。

    ```python
    import google.auth
    from google.auth.transport.requests import Request
    from google.adk.integrations.agent_registry import AgentRegistry

    def google_auth_header_provider(context):
        creds, _ = google.auth.default()
        if not creds.valid:
            creds.refresh(Request())
        return {"Authorization": f"Bearer {creds.token}"}

    registry = AgentRegistry(
        project_id=project_id,
        location=location,
        header_provider=google_auth_header_provider
    )
    ```

=== "Go"

    `*.googleapis.com` エンドポイントへのリクエストは、レジストリクライアント自体の認証情報を再利用します。その他のエンドポイントの場合、またはそのデフォルトをオーバーライドするには、`WithMCPHTTPClient` と `WithMCPHeaders` を渡します。

    ```go
    toolset, err := registry.MCPToolset(ctx, mcpServerName,
    	agentregistry.WithMCPHTTPClient(httpClient),
    	agentregistry.WithMCPHeaders(map[string]string{"X-Tenant-Id": "acme"}),
    )
    ```

    この方法で設定されたヘッダーは、ツールセットが MCP サーバーに送信するすべてのリクエストに適用されます。Agent Registry API 自体への呼び出しには影響しません。

## API リファレンス

=== "Python"

    `AgentRegistry` クラスは次のコアメソッドを提供します。

    - `list_mcp_servers(self, filter_str, page_size, page_token)`: 登録された MCP サーバーのリストを取得します。
    - `get_mcp_server(self, name)`: 特定の MCP サーバーの詳細なメタデータを取得します。
    - `get_mcp_toolset(self, mcp_server_name)`: 登録された MCP サーバーから ADK `McpToolset` インスタンスを構築します。
    - `list_agents(self, filter_str, page_size, page_token)`: 登録された A2A エージェントのリストを取得します。
    - `get_agent_info(self, name)`: 特定の A2A エージェントの詳細なメタデータを取得します。
    - `get_remote_a2a_agent(self, agent_name)`: 登録された A2A エージェントから ADK `RemoteA2aAgent` インスタンスを作成します。

=== "Go"

    `agentregistry.Client` 型は、リソース種別ごとに 3 つの検出メソッドを提供します。`List*` は単一ページを返し、`Get*` は完全なリソース名で 1 つのリソースを返し、`All*` はオンデマンドでページを取得する `iter.Seq2` を返します。

    - `ListAgents(ctx, opts ...ListOption)`, `GetAgent(ctx, name)`, `AllAgents(ctx, opts ...ListOption)`: 登録された A2A エージェント
    - `ListMCPServers(ctx, opts ...ListOption)`, `GetMCPServer(ctx, name)`, `AllMCPServers(ctx, opts ...ListOption)`: 登録された MCP サーバー
    - `ListEndpoints(ctx, opts ...ListOption)`, `GetEndpoint(ctx, name)`, `AllEndpoints(ctx, opts ...ListOption)`: 登録されたモデルエンドポイント
    - `RemoteAgent(ctx, name, opts ...RemoteAgentOption)`: 登録された A2A エージェントをサブエージェントとして使用可能な `agent.Agent` に解決します。
    - `MCPToolset(ctx, name, opts ...MCPToolsetOption)`: 登録された MCP サーバーを `tool.Toolset` に解決します。

    リストオプションには `WithFilter`、`WithPageSize`、`WithPageToken` があります。`All*` イテレーターはページトークンを自身で管理します。Agent Registry API からの 2xx 以外のレスポンスは、`StatusCode` とレスポンス `Body` を含む `*agentregistry.APIError` として返されます。

## 構成オプション

=== "Python"

    `AgentRegistry` コンストラクターは次の引数を受け入れます。

    - `project_id` (文字列、必須): Google Cloud プロジェクト ID。
    - `location` (文字列、必須): `global`、`us-central1` などの Google Cloud の場所/リージョン。
    - `header_provider` (呼び出し可能、オプション): `ReadonlyContext` を受け取り、`get_mcp_toolset` が返す [McpToolset](/tools-custom/mcp-tools/#mcptoolset-class) によるターゲット MCP サーバーへのリクエストに含まれるカスタムヘッダーの辞書を返す呼び出し可能オブジェクト。これらのヘッダーは、Agent Registry API 自体への呼び出しや [RemoteA2aAgent](/a2a/quickstart-consuming/#quickstart-consuming-a-remote-agent-via-a2a) によるリクエストには影響しません。それらのリクエストの場合は、[リモート A2A エージェント](#remote-a2a-agents) のセクションに示すように、認証済みの `httpx.AsyncClient` を `get_remote_a2a_agent` に渡してください。

=== "Go"

    `agentregistry.New` コンストラクターは `Config` 構造体を受け取ります。

    - `ProjectID` (文字列、必須): Google Cloud プロジェクト ID。
    - `Location` (文字列、必須): `global`、`us-central1` などの Google Cloud の場所/リージョン。
    - `HTTPClient` (`*http.Client`、オプション): Agent Registry API 呼び出しに使用されるクライアント。`nil` の場合、ADK は Application Default Credentials からクライアントを構築し、`GOOGLE_API_USE_MTLS_ENDPOINT` および `GOOGLE_API_USE_CLIENT_CERTIFICATE` から mTLS を含むエンドポイントを解決します。このクライアントは、`*.googleapis.com` エンドポイントへの [McpToolset](/tools-custom/mcp-tools/) トラフィックにも再利用されますが、[A2A](/a2a/quickstart-consuming-go/) トラフィックには使用されません。

    解決されたエンドポイントへの送信 (Egress) トラフィックは、代わりに呼び出しごとに構成されます。`RemoteAgent` では `WithA2AHTTPClient` と `WithA2AHeaders`、`MCPToolset` では `WithMCPHTTPClient` と `WithMCPHeaders` を指定します。

## 追加のリソース
- [サンプル エージェント コード (Python)](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/agent_registry_agent)
- [サンプル エージェント コード (Go)](https://github.com/google/adk-go/tree/main/examples/agentregistry)
- [Agent Registry クライアント (Python)](https://github.com/google/adk-python/blob/main/src/google/adk/integrations/agent_registry/agent_registry.py)
- [Agent Registry クライアント (Go)](https://pkg.go.dev/google.golang.org/adk/v2/agentregistry)
- [Google Auth ライブラリ](https://google-auth.readthedocs.io/en/latest/)
