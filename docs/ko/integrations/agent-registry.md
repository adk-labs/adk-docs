---
catalog_title: Google Cloud Agent Registry
catalog_description: AI 에이전트 및 MCP 서버 검색 및 연결
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["google", "mcp", "connectors"]
---


# Google Cloud 에이전트 레지스트리

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.26.0</span><span class="lst-go">Go v2.1.0</span><span class="lst-preview">미리보기</span>
</div>

ADK(에이전트 개발 키트) 내의 에이전트 레지스트리 클라이언트 라이브러리를 통해 개발자는 [Google Cloud Agent Registry](https://docs.cloud.google.com/agent-registry/overview)에 카탈로그로 등록된 AI 에이전트 및 MCP 서버를 검색, 조회 및 연결할 수 있습니다. 이를 통해 관리형 구성 요소를 사용하는 에이전트 기반 애플리케이션의 동적 구성이 가능해집니다.

## 사용 사례

- **가속화된 개발**: 기존 에이전트 및 도구(MCP 서버)를 재구축하는 대신 중앙 카탈로그에서 쉽게 찾고 재사용할 수 있습니다.
- **동적 통합**: 런타임에 에이전트 및 MCP 서버 엔드포인트를 검색하여 환경 변화에 애플리케이션을 더 탄력적으로 유연하게 연동합니다.
- **향상된 거버넌스**: ADK 애플리케이션 내에서 레지스트리의 검증된 관리형 구성 요소를 활용합니다.

## 전제조건

- [Google Cloud 프로젝트](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects).
- Google Cloud 프로젝트에서 사용 설정된 [Agent Registry API](https://docs.cloud.google.com/agent-registry/setup).
- 환경에 맞게 구체화된 인증 설정. [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/application-default-credentials)(`gcloud auth application-default login`)를 사용해 로그인해야 합니다.
- 환경 변수 `GOOGLE_CLOUD_PROJECT`를 프로젝트 ID로 설정하고 `GOOGLE_CLOUD_LOCATION`을 적절한 지역(예: `global`, `us-central1`)으로 설정합니다.
- [설치](#installation) 단원의 설명에 따라 사용 언어에 맞는 ADK 설치.

ADK 에이전트에서 Google Cloud 연결과 관련된 자세한 내용은 [Google Cloud 및 Agent Platform 연결](/get-started/google-cloud/) 가이드를 참고하세요.

## 설치

[Agent Registry](https://docs.cloud.google.com/agent-registry/overview) 통합은 핵심 ADK 라이브러리의 일부로 제공됩니다.

=== "Python"

    ```bash
    pip install google-adk
    ```

    ### 필수 종속성

    `google.adk.integrations.agent_registry` 모듈은 모듈 스코프에서 A2A SDK와 에이전트 식별자(Agent Identity) 인증 제공업체를 모두 가져오므로 핵심 기능만 설치하면 `AgentRegistry` 임포트 시 `ImportError`가 발생합니다. `a2a`와 `agent-identity` 부가 패키지를 함께 설치하세요.

    ```bash
    pip install "google-adk[a2a,agent-identity]"
    ```

=== "Go"

    ```bash
    go get google.golang.org/adk/v2
    ```

    클라이언트는 핵심 모듈의 `google.golang.org/adk/v2/agentregistry` 패키지에 포함되어 있으므로 별도의 부가 패키지 설치가 필요하지 않습니다.

## 에이전트와 함께 사용

ADK 에이전트 내에서 Agent Registry 통합을 사용하는 주요 방법은 Agent Registry 클라이언트를 통해 원격 에이전트나 도구 세트를 동적으로 가져오는 것입니다.

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

## Google MCP 서버 및 원격 A2A 에이전트 인증

### 원격 A2A 에이전트

원격 A2A 에이전트 호출은 자동으로 인증되지 않습니다. Google A2A 에이전트에 연결하는 경우 원격 에이전트를 생성할 때 인증된 HTTP 클라이언트를 직접 제공해야 합니다.

=== "Python"

    `get_remote_a2a_agent` 메서드에 Google 인증 헤더로 구성된 `httpx.AsyncClient`를 전달합니다.

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

    `WithA2AHTTPClient`로 인증된 `*http.Client`를 전달하거나 `WithA2AHeaders`로 고정 헤더를 전달합니다.

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

    타임아웃은 전체 요청에 적용되어 스트리밍 응답을 중단시킬 수 있는 `http.Client.Timeout` 대신 클라이언트의 `Transport`에 설정하세요.

### Google MCP 서버

Google MCP 서버의 경우 인증 헤더가 자동으로 전달됩니다.

=== "Python"

    자동 인증이 정상 작동하지 않는 경우 `AgentRegistry` 생성자의 `header_provider` 인수를 통해 직접 헤더를 제공할 수 있습니다.

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

    `*.googleapis.com` 엔드포인트에 대한 요청은 레지스트리 클라이언트 자체의 자격 증명을 재사용합니다. 다른 엔드포인트의 경우 또는 해당 기본값을 변경하려면 `WithMCPHTTPClient`와 `WithMCPHeaders`를 전달하세요.

    ```go
    toolset, err := registry.MCPToolset(ctx, mcpServerName,
    	agentregistry.WithMCPHTTPClient(httpClient),
    	agentregistry.WithMCPHeaders(map[string]string{"X-Tenant-Id": "acme"}),
    )
    ```

    이 방식으로 설정된 헤더는 도구 세트가 MCP 서버로 보내는 모든 요청에 적용됩니다. Agent Registry API 자체 호출에는 영향을 주지 않습니다.

## API 참조

=== "Python"

    `AgentRegistry` 클래스는 다음 핵심 메서드를 제공합니다.

    - `list_mcp_servers(self, filter_str, page_size, page_token)`: 등록된 MCP 서버 목록을 가져옵니다.
    - `get_mcp_server(self, name)`: 특정 MCP 서버의 상세 메타데이터를 가져옵니다.
    - `get_mcp_toolset(self, mcp_server_name)`: 등록된 MCP 서버로부터 ADK `McpToolset` 인스턴스를 생성합니다.
    - `list_agents(self, filter_str, page_size, page_token)`: 등록된 A2A 에이전트 목록을 가져옵니다.
    - `get_agent_info(self, name)`: 특정 A2A 에이전트의 상세 메타데이터를 가져옵니다.
    - `get_remote_a2a_agent(self, agent_name)`: 등록된 A2A 에이전트로부터 ADK `RemoteA2aAgent` 인스턴스를 생성합니다.

=== "Go"

    `agentregistry.Client` 유형은 리소스 종류별로 3가지 검색 메서드를 노출합니다. `List*`는 단일 페이지를 반환하고, `Get*`은 전체 리소스 이름으로 개별 리소스를 반환하며, `All*`은 요청 시 페이지를 가져오는 `iter.Seq2`를 반환합니다.

    - `ListAgents(ctx, opts ...ListOption)`, `GetAgent(ctx, name)`, `AllAgents(ctx, opts ...ListOption)`: 등록된 A2A 에이전트
    - `ListMCPServers(ctx, opts ...ListOption)`, `GetMCPServer(ctx, name)`, `AllMCPServers(ctx, opts ...ListOption)`: 등록된 MCP 서버
    - `ListEndpoints(ctx, opts ...ListOption)`, `GetEndpoint(ctx, name)`, `AllEndpoints(ctx, opts ...ListOption)`: 등록된 모델 엔드포인트
    - `RemoteAgent(ctx, name, opts ...RemoteAgentOption)`: 등록된 A2A 에이전트를 서브 에이전트로 사용할 수 있는 `agent.Agent`로 해석합니다.
    - `MCPToolset(ctx, name, opts ...MCPToolsetOption)`: 등록된 MCP 서버를 `tool.Toolset`으로 해석합니다.

    목록 옵션으로는 `WithFilter`, `WithPageSize`, `WithPageToken`이 있습니다. `All*` 이터레이터는 페이지 토큰을 직접 관리합니다. Agent Registry API의 2xx 이외 응답은 `StatusCode`와 응답 `Body`를 포함하는 `*agentregistry.APIError` 형태로 반환됩니다.

## 구성 옵션

=== "Python"

    `AgentRegistry` 생성자는 다음 인수를 받습니다.

    - `project_id` (str, 필수): Google Cloud 프로젝트 ID.
    - `location` (str, 필수): `global`, `us-central1`과 같은 Google Cloud 위치/지역.
    - `header_provider` (Callable, 선택): `ReadonlyContext`를 받아 대상 MCP 서버로 `get_mcp_toolset`이 반환하는 [McpToolset](/tools-custom/mcp-tools/#mcptoolset-class) 요청에 포함할 사용자 지정 헤더 딕셔너리를 반환하는 콜러블입니다. 이 헤더는 Agent Registry API 자체 호출이나 [RemoteA2aAgent](/a2a/quickstart-consuming/#quickstart-consuming-a-remote-agent-via-a2a)의 요청에는 영향을 주지 않습니다. 해당 요청의 경우 [원격 A2A 에이전트](#remote-a2a-agents) 섹션처럼 인증된 `httpx.AsyncClient`를 `get_remote_a2a_agent`에 전달하세요.

=== "Go"

    `agentregistry.New` 생성자는 `Config` 구조체를 받습니다.

    - `ProjectID` (string, 필수): Google Cloud 프로젝트 ID.
    - `Location` (string, 필수): `global`, `us-central1`과 같은 Google Cloud 위치/지역.
    - `HTTPClient` (`*http.Client`, 선택): Agent Registry API 호출에 사용되는 클라이언트입니다. `nil`인 경우 ADK는 Application Default Credentials로부터 클라이언트를 생성하고 `GOOGLE_API_USE_MTLS_ENDPOINT` 및 `GOOGLE_API_USE_CLIENT_CERTIFICATE` 환경 변수를 바탕으로 mTLS를 포함한 엔드포인트를 결정합니다. 이 클라이언트는 `*.googleapis.com` 엔드포인트로 전송되는 [McpToolset](/tools-custom/mcp-tools/) 트래픽에도 재사용되지만, [A2A](/a2a/quickstart-consuming-go/) 트래픽에는 사용되지 않습니다.

    해결된 엔드포인트로의 아웃바운드(Egress) 트래픽은 대신 호출별로 설정됩니다. `RemoteAgent`에서는 `WithA2AHTTPClient` 및 `WithA2AHeaders`, `MCPToolset`에서는 `WithMCPHTTPClient` 및 `WithMCPHeaders`를 사용합니다.

## 추가 리소스
- [샘플 에이전트 코드 (Python)](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/agent_registry_agent)
- [샘플 에이전트 코드 (Go)](https://github.com/google/adk-go/tree/main/examples/agentregistry)
- [Agent Registry 클라이언트 (Python)](https://github.com/google/adk-python/blob/main/src/google/adk/integrations/agent_registry/agent_registry.py)
- [Agent Registry 클라이언트 (Go)](https://pkg.go.dev/google.golang.org/adk/v2/agentregistry)
- [Google Auth 라이브러리](https://google-auth.readthedocs.io/en/latest/)
