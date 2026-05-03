---
catalog_title: Google Cloud Agent Registry
catalog_description: AI エージェントと MCP サーバーを検出して接続する
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["google", "mcp", "connectors"]
---


# Google Cloud エージェント レジストリ

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.26.0</span><span class="lst-preview">Preview</span>
</div>

Agent Development Kit (ADK) 内の Agent Registry クライアント ライブラリでは、
開発者が AI エージェントと MCP サーバーを検出、検索、接続できるようにする
[Google Cloud Agent
Registry](https://docs.cloud.google.com/agent-registry/overview) 内にカタログされています。これにより、
管理されたコンポーネントを使用したエージェントベースのアプリケーションの動的な構成。

## 使用例

- **開発の加速**: 既存のエージェントとツールを簡単に見つけて再利用します。
  (MCP サーバー) を再構築するのではなく、中央カタログから取得します。
- **動的統合**: 実行時にエージェントと MCP サーバーのエンドポイントを検出します。
  アプリケーションを環境の変化に対してより堅牢にします。
- **強化されたガバナンス**: からの管理および検証されたコンポーネントを利用します。
  ADK アプリケーション内のレジストリ。

## 前提条件

- [Google Cloud
  project](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects)。
- [Agent Registry API](https://docs.cloud.google.com/agent-registry/setup)
  Google Cloud プロジェクトで有効になっています。
- 環境に合わせて構成された認証。を使用してログインする必要があります
  [Application Default
  Credentials](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
  (`gcloud auth application-default login`)。
- 環境変数 `GOOGLE_CLOUD_PROJECT` をプロジェクト ID に設定し、
  `GOOGLE_CLOUD_LOCATION` を適切なリージョンに設定します (例: `global`、
  `us-central1`)。
- `google-adk` ライブラリがインストールされました。

## インストール

[Agent Registry](https://docs.cloud.google.com/agent-registry/overview)
統合はコア ADK ライブラリの一部です。

```bash
pip install google-adk
```

### オプションの依存関係

AgentRegistry 統合の全機能を使用するには、次のことが必要になる場合があります。
ユースケースに応じて追加のエクストラをインストールします。

**A2A (エージェント間) サポートの場合:** `get_remote_a2a_agent` を使用する予定の場合
または、リモートの A2A 準拠エージェントと対話するには、`a2a` エクストラをインストールします。

```bash
pip install "google-adk[a2a]"
```

**エージェント ID (GCP 認証プロバイダー) の場合:**
`GcpAuthProvider` (例: `get_mcp_toolset` が自動的に解決される場合)
登録された MCP サーバーの IAM バインディングによる認証)、
`agent-identity` 追加:

```bash
pip install "google-adk[agent-identity]"
```

## エージェントと一緒に使用する

ADK エージェント内でエージェント レジストリ統合を使用する主な方法は、次のとおりです。
AgentRegistry クライアントを使用して、リモート エージェントまたはツールセットを動的に取得します。

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

## Google MCP サーバーとリモート A2A エージェントの認証

### リモート A2A エージェント

Google A2A エージェントに接続している場合は、
`httpx.AsyncClient` には Google 認証ヘッダーが設定されています
`get_remote_a2a_agent` メソッド。

例：
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

### Google MCP サーバー

Google MCP サーバーの場合、認証ヘッダーが自動的に渡されます。
ただし、自動認証が期待どおりに機能しない場合は、
の `header_provider` 引数を使用してヘッダーを手動で提供します。
`AgentRegistry` コンストラクター。

例：
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

## API リファレンス

AgentRegistry クラスは、次のコア メソッドを提供します。

- `list_mcp_servers(self, filter_str, page_size, page_token)`: のリストを取得します。
  登録された MCP サーバー。
- `get_mcp_server(self, name)`: 特定の MCP の詳細なメタデータを取得します
  サーバー。
- `get_mcp_toolset(self, mcp_server_name)`: ADK McpToolset を構築します
  登録された MCP サーバーからのインスタンス。
- `list_agents(self, filter_str, page_size, page_token)`: のリストを取得します。
  登録済みの A2A エージェント。
- `get_agent_info(self, name)`: 特定の A2A の詳細なメタデータを取得します
  エージェント。
- `get_remote_a2a_agent(self, agent_name)`: ADK RemoteA2aAgent を作成します
  登録された A2A エージェントのインスタンス。

## 構成オプション

AgentRegistry コンストラクターは次の引数を受け入れます。

- `project_id` (文字列、必須): Google Cloud プロジェクト ID。
- `location` (文字列、必須): Google Cloud の場所/リージョン。
  「グローバル」、「us-central1」。
- `header_provider` (呼び出し可能、オプション): を受け取る呼び出し可能。
  ReadonlyContext に含めるカスタム ヘッダーの辞書を返します。
  [McpToolset](/tools-custom/mcp-tools/#mcptoolset-class) によって行われたリクエスト
  または
  [RemoteA2aAgent](/a2a/quickstart-consuming-go/#quickstart-consuming-a-remote-agent-via-a2a)
  対象サービスへ。これは、エージェントの呼び出しに使用されるヘッダーには影響しません。
  レジストリ API 自体。

## 追加のリソース
- [Sample Agent Code](https://github.com/google/adk-python/tree/main/contributing/samples/agent_registry_agent)
- [Agent Registry Client](https://github.com/google/adk-python/blob/main/src/google/adk/integrations/agent_registry/agent_registry.py)
- [Google Auth Library](https://google-auth.readthedocs.io/en/latest/)
