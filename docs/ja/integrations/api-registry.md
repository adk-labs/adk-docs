---
catalog_title: API Registry
catalog_description: Google Cloud サービスを MCP ツールとして動的に接続します
catalog_icon: /adk-docs/integrations/assets/developer-tools-color.svg
catalog_tags: ["google", "mcp", "connectors"]
---

# ADK 向け Google Cloud API Registry ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.20.0</span><span class="lst-preview">Preview</span>
</div>

Agent Development Kit (ADK) 向け Google Cloud API Registry コネクターツールを使うと、
[Google Cloud API Registry](https://docs.cloud.google.com/api-registry/docs/overview)
を通じて、エージェントから幅広い Google Cloud サービスへ
Model Context Protocol (MCP) サーバーとしてアクセスできます。
このツールを設定することで、エージェントを Google Cloud プロジェクトへ接続し、
そのプロジェクトで有効化されている Cloud サービスへ動的にアクセスできます。

!!! example "Preview リリース"
    Google Cloud API Registry 機能は Preview リリースです。
    詳細は
    [launch stage descriptions](https://cloud.google.com/products#product-launch-stages)
    を参照してください。

## 前提条件

エージェントで API Registry を利用する前に、次を確認してください:

-   **Google Cloud プロジェクト:**
    既存の Google Cloud プロジェクトを使って、エージェントが AI モデルへアクセスできるよう設定します。

-   **API Registry へのアクセス:**
    エージェント実行環境には、利用可能 MCP サーバー一覧取得のために
    `apiregistry.viewer` ロールを持つ Google Cloud
    [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc)
    が必要です。

-   **Cloud API:**
    Google Cloud プロジェクトで
    *cloudapiregistry.googleapis.com* と *apihub.googleapis.com* API を有効化します。

-   **MCP サーバーとツールアクセス:**
    エージェントで利用したい Cloud プロジェクト内 Google Cloud サービスの MCP サーバーを
    API Registry で有効化してください。
    Cloud Console から有効化するか、次の gcloud コマンドを使えます:
    `gcloud beta api-registry mcp enable bigquery.googleapis.com --project={PROJECT_ID}`。
    エージェントで使う資格情報には、MCP サーバー本体およびツールが利用する基盤サービスへの権限が必要です。
    たとえば BigQuery ツールを使うには、サービスアカウントに
    `bigquery.dataViewer` や `bigquery.jobUser` などの BigQuery IAM ロールが必要です。
    必要権限の詳細は [Authentication and access](#auth) を参照してください。

次の gcloud コマンドで、API Registry で有効化された MCP サーバーを確認できます:

```console
gcloud beta api-registry mcp servers list --project={PROJECT_ID}.
```

## エージェントで使う

API Registry コネクターツールをエージェントで構成する際は、まず
***ApiRegistry*** クラスを初期化して Cloud サービスとの接続を確立し、
その後 `get_toolset()` 関数で API Registry に登録された特定 MCP サーバーの
ツールセットを取得します。次のコード例は、API Registry に登録された MCP サーバーの
ツールを使うエージェント作成方法を示します。
このエージェントは BigQuery との対話を想定しています:

```python
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.api_registry import ApiRegistry

# Configure with your Google Cloud Project ID and registered MCP server name
PROJECT_ID = "your-google-cloud-project-id"
MCP_SERVER_NAME = "projects/your-google-cloud-project-id/locations/global/mcpServers/your-mcp-server-name"

# Example header provider for BigQuery, a project header is required.
def header_provider(context):
    return {"x-goog-user-project": PROJECT_ID}

# Initialize ApiRegistry
api_registry = ApiRegistry(
    api_registry_project_id=PROJECT_ID,
    header_provider=header_provider
)

# Get the toolset for the specific MCP server
registry_tools = api_registry.get_toolset(
    mcp_server_name=MCP_SERVER_NAME,
    # Optionally filter tools:
    #tool_filter=["list_datasets", "run_query"]
)

# Create an agent with the tools
root_agent = LlmAgent(
    model="gemini-1.5-flash", # Or your preferred model
    name="bigquery_assistant",
    instruction="""
Help user access their BigQuery data using the available tools.
    """,
    tools=[registry_tools],
)
```

この例の完全コードは
[api_registry_agent](https://github.com/google/adk-python/tree/main/contributing/samples/api_registry_agent/)
サンプルを参照してください。設定オプションは
[Configuration](#configuration)、
認証については
[Authentication and access](#auth) を参照してください。

## 認証とアクセス {#auth}

エージェントで API Registry を使うには、アクセス対象サービスへの認証が必要です。
このツールはデフォルトで Google Cloud
[Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc)
を認証に使います。次の権限とアクセスを確保してください:

-   **API Registry アクセス:**
    `ApiRegistry` クラスは Application Default Credentials (`google.auth.default()`) を使って
    Google Cloud API Registry へのリクエストを認証し、利用可能 MCP サーバーを列挙します。
    エージェント実行環境の資格情報には、`apiregistry.viewer` のような
    API Registry リソース閲覧権限が必要です。

-   **MCP サーバーとツールアクセス:**
    `get_toolset` が返す `McpToolset` もデフォルトで
    Google Cloud Application Default Credentials を使って
    実際の MCP サーバーエンドポイント呼び出しを認証します。
    使用する資格情報には次の両方が必要です:
    1.  MCP サーバー自体へのアクセス権。
    1.  ツールが利用する基盤サービス/リソースの利用権。

-   **MCP ツール利用者ロール:**
    API registry 経由で MCP ツールを呼び出せるよう、エージェントで使うアカウントに
    MCP tool user ロールを付与します:
    `gcloud projects add-iam-policy-binding {PROJECT_ID} --member={member}
    --role="roles/mcp.toolUser"`

たとえば BigQuery と連携する MCP サーバーツールを使う場合、
サービスアカウントなど資格情報に紐づくアカウントには
データセットアクセスやクエリ実行のため
`bigquery.dataViewer` や `bigquery.jobUser` など適切な BigQuery IAM ロールが必要です。
bigquery MCP サーバーでは、ツール利用に
`"x-goog-user-project": PROJECT_ID` ヘッダーが必要です。
認証やプロジェクト文脈の追加ヘッダーは `ApiRegistry` コンストラクタの
`header_provider` 引数で注入できます。

## 設定 {#configuration}

***APIRegistry*** オブジェクトの設定オプション:

-   **`api_registry_project_id`** (str):
    API Registry が配置されている Google Cloud プロジェクト ID。

-   **`location`** (str, optional):
    API Registry リソースのロケーション。
    デフォルトは `"global"`。

-   **`header_provider`** (Callable, optional):
    呼び出しコンテキストを受け取り、MCP サーバーへのリクエストに付与する
    追加 HTTP ヘッダー辞書を返す関数。
    動的認証やプロジェクト固有ヘッダーによく使います。

`get_toolset()` 関数の設定オプション:

-   **`mcp_server_name`** (str):
    ツールを読み込む登録済み MCP サーバーの完全名。
    例: `projects/my-project/locations/global/mcpServers/my-server`。

-   **`tool_filter`** (Union[ToolPredicate, List[str]], optional):
    ツールセットに含めるツールを指定。
    -   文字列リストの場合、リスト内名前のツールのみ含める。
    -   `ToolPredicate` 関数の場合、各ツールに対して関数を呼び、
        `True` を返したツールのみ含める。
    -   `None` の場合、MCP サーバーの全ツールを含める。

-   **`tool_name_prefix`** (str, optional):
    生成ツールセットの各ツール名に付与する接頭辞。

## 追加リソース

-   [api_registry_agent](https://github.com/google/adk-python/tree/main/contributing/samples/api_registry_agent/)
    ADK コードサンプル
-   [Google Cloud API Registry](https://docs.cloud.google.com/api-registry/docs/overview)
    ドキュメント
