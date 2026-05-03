---
catalog_title: Google Cloud Agent Registry
catalog_description: AI 에이전트 및 MCP 서버 검색 및 연결
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["google", "mcp", "connectors"]
---


# Google Cloud 에이전트 레지스트리

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.26.0</span><span class="lst-preview">Preview</span>
</div>

ADK(에이전트 개발 키트) 내의 에이전트 레지스트리 클라이언트 라이브러리는 다음을 허용합니다.
개발자는 AI 에이전트 및 MCP 서버를 검색하고 조회하고 연결할 수 있습니다.
[Google Cloud Agent
Registry](https://docs.cloud.google.com/agent-registry/overview) 내에 카탈로그화되어 있습니다. 이를 통해
관리되는 구성 요소를 사용하는 에이전트 기반 애플리케이션의 동적 구성.

## 사용 사례

- **가속화된 개발**: 기존 에이전트 및 도구를 쉽게 찾고 재사용할 수 있습니다.
  (MCP 서버)를 재구축하는 대신 중앙 카탈로그에서 가져옵니다.
- **동적 통합**: 런타임에 에이전트 및 MCP 서버 엔드포인트를 검색합니다.
  환경 변화에 애플리케이션을 더욱 강력하게 만듭니다.
- **향상된 거버넌스**:
  ADK 애플리케이션 내의 레지스트리.

## 전제조건

- [Google Cloud
  project](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects).
- [Agent Registry API](https://docs.cloud.google.com/agent-registry/setup)
  Google Cloud 프로젝트에서 사용 설정되었습니다.
- 귀하의 환경에 맞게 인증이 구성되었습니다. 다음을 사용하여 로그인해야 합니다.
  [Application Default
  Credentials](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
  (`gcloud auth application-default login`).
- 프로젝트 ID로 설정된 환경 변수 `GOOGLE_CLOUD_PROJECT` 및
  `GOOGLE_CLOUD_LOCATION`를 적절한 지역으로 설정합니다(예: `global`,
  `us-central1`).
- `google-adk` 라이브러리가 설치되었습니다.

## 설치

[Agent Registry](https://docs.cloud.google.com/agent-registry/overview)
통합은 핵심 ADK 라이브러리의 일부입니다.

```bash
pip install google-adk
```

### 선택적 종속성

AgentRegistry 통합의 전체 기능을 사용하려면 다음이 필요할 수 있습니다.
사용 사례에 따라 추가 추가 기능을 설치하십시오.

**A2A(에이전트 간) 지원의 경우:** `get_remote_a2a_agent`를 사용할 계획인 경우
또는 원격 A2A 호환 에이전트와 상호 작용하려면 `a2a` 추가를 설치하십시오.

```bash
pip install "google-adk[a2a]"
```

**에이전트 ID(GCP 인증 제공업체)의 경우:**
`GcpAuthProvider`(예: `get_mcp_toolset`가 자동으로 해결되는 경우)
등록된 MCP 서버에 대한 IAM 바인딩을 통한 인증)
`agent-identity` 추가:

```bash
pip install "google-adk[agent-identity]"
```

## 에이전트와 함께 사용

ADK 에이전트 내에서 Agent Registry 통합을 사용하는 기본 방법은 다음과 같습니다.
AgentRegistry 클라이언트를 사용하여 원격 에이전트 또는 도구 세트를 동적으로 가져옵니다.

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

## Google MCP 서버 및 원격 A2A 에이전트에 대한 인증

### 원격 A2A 에이전트

Google A2A 상담원에 연결하는 경우
Google 인증 헤더로 구성된 `httpx.AsyncClient`
`get_remote_a2a_agent` 방법.

예:
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

### Google MCP 서버

Google MCP 서버의 경우 인증 헤더가 자동으로 전달됩니다.
그러나 자동 인증이 예상대로 작동하지 않는 경우 다음을 수행할 수 있습니다.
`header_provider` 인수를 사용하여 헤더를 수동으로 제공합니다.
`AgentRegistry` 생성자.

예:
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

## API 참조

AgentRegistry 클래스는 다음과 같은 핵심 메서드를 제공합니다.

- `list_mcp_servers(self, filter_str, page_size, page_token)`: 목록을 가져옵니다.
  등록된 MCP 서버.
- `get_mcp_server(self, name)`: 특정 MCP의 자세한 메타데이터를 검색합니다.
  서버.
- `get_mcp_toolset(self, mcp_server_name)`: ADK McpToolset을 구성합니다.
  등록된 MCP 서버의 인스턴스입니다.
- `list_agents(self, filter_str, page_size, page_token)`: 목록을 가져옵니다.
  A2A 에이전트를 등록했습니다.
- `get_agent_info(self, name)`: 특정 A2A의 자세한 메타데이터를 검색합니다.
  에이전트.
- `get_remote_a2a_agent(self, agent_name)`: ADK RemoteA2aAgent를 생성합니다.
  등록된 A2A 에이전트의 인스턴스입니다.

## 구성 옵션

AgentRegistry 생성자는 다음 인수를 허용합니다.

- `project_id`(str, 필수): Google Cloud 프로젝트 ID입니다.
- `location`(str, 필수): 다음과 같은 Google Cloud 위치/지역
  "글로벌", "us-central1".
- `header_provider`(콜러블, 옵션):
  ReadonlyContext에 포함될 사용자 정의 헤더 사전을 반환합니다.
  [McpToolset](/tools-custom/mcp-tools/#mcptoolset-class)의 요청
  또는
  [RemoteA2aAgent](/a2a/quickstart-consuming-go/#quickstart-consuming-a-remote-agent-via-a2a)
  대상 서비스에. 이는 에이전트를 호출하는 데 사용되는 헤더에는 영향을 미치지 않습니다.
  레지스트리 API 자체.

## 추가 리소스
- [Sample Agent Code](https://github.com/google/adk-python/tree/main/contributing/samples/agent_registry_agent)
- [Agent Registry Client](https://github.com/google/adk-python/blob/main/src/google/adk/integrations/agent_registry/agent_registry.py)
- [Google Auth Library](https://google-auth.readthedocs.io/en/latest/)
