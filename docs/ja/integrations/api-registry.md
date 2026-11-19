---
catalog_title: API Registry
catalog_description: Google Cloud サービスを MCP ツールとして動的に接続します
catalog_icon: /integrations/assets/developer-tools-color.svg
catalog_tags: ["google", "mcp", "connectors"]
---

# ADK 向け Google Cloud API Registry ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.20.0</span><span class="lst-preview">プレビュー</span>
</div>

Agent Development Kit (ADK) 向け Google Cloud API Registry コネクターツールを使うと、
[Google Cloud API Registry](https://docs.cloud.google.com/api-registry/docs/overview)
を通じて、エージェントから幅広い Google Cloud サービスへ
Model Context Protocol (MCP) サーバーとしてアクセスできます。
このツールを設定することで、エージェントを Google Cloud プロジェクトへ接続し、
そのプロジェクトで有効化されている Cloud サービスへ動的にアクセスできます。

!!! example "プレビューリリース"
    Google Cloud API Registry 機能はプレビューリリースです。
    詳細は
    [リリースステージの説明](https://cloud.google.com/products#product-launch-stages)
    を参照してください。

## 前提条件

エージェントで API Registry を利用する前に、次を確認してください:

-   **Google Cloud プロジェクト:**
    既存の Google Cloud プロジェクトを使って、エージェントが AI モデルへアクセスできるよう設定します。

-   **API Registry へのアクセス:**
    利用可能な MCP サーバーの一覧を取得するため、エージェントの実行環境には
    `apiregistry.viewer` ロールを持つ Google Cloud
    [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc)
    が必要です。

-   **Cloud API:**
    Google Cloud プロジェクトで
    *cloudapiregistry.googleapis.com* と *apihub.googleapis.com* API を有効化します。

-   **MCP サーバーとツールアクセス:**
    エージェントから利用したい Google Cloud サービスの MCP サーバーを、対象プロジェクトの
    API Registry で有効化してください。
    Cloud コンソールから有効化するか、次の gcloud コマンドを実行します:
    `gcloud beta api-registry mcp enable bigquery.googleapis.com --project={PROJECT_ID}`。
    エージェントが使用する認証情報には、MCP サーバー自体およびツールが利用する基盤サービスへのアクセス権限が必要です。
    たとえば BigQuery ツールを使うには、サービスアカウントに
    `bigquery.dataViewer` や `bigquery.jobUser` などの BigQuery IAM ロールが必要です。
    必要な権限の詳細は [認証とアクセス](#auth) を参照してください。

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
from google.adk.integrations.api_registry import ApiRegistry

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
    model="gemini-flash-latest", # Or your preferred model
    name="bigquery_assistant",
    instruction="""
Help user access their BigQuery data using the available tools.
    """,
    tools=[registry_tools],
)
```

この例の完全なコードは
[api_registry_agent](https://github.com/google/adk-python/tree/main/contributing/samples/api_registry_agent/)
サンプルを参照してください。設定オプションについては
[設定](#configuration)、
このツールの認証については
[認証とアクセス](#auth) を参照してください。

## 認証とアクセス {#auth}

エージェントで API Registry を使うには、アクセス対象サービスへの認証が必要です。
このツールはデフォルトで Google Cloud
[Application Default Credentials](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc)
を認証に使用します。エージェントに次の権限とアクセス権があることを確認してください:

-   **API Registry アクセス:**
    `ApiRegistry` クラスは Application Default Credentials (`google.auth.default()`) を使って
    Google Cloud API Registry へのリクエストを認証し、利用可能な MCP サーバーを一覧表示します。
    エージェント実行環境の認証情報には、`apiregistry.viewer` などの
    API Registry リソース閲覧権限が必要です。

-   **MCP サーバーとツールアクセス:**
    `get_toolset` が返す `McpToolset` もデフォルトで
    Google Cloud Application Default Credentials を使って
    実際の MCP サーバーエンドポイントへの呼び出しを認証します。
    使用する認証情報には次の両方の権限が必要です:
    1.  MCP サーバー自体へのアクセス権限。
    1.  ツールが連携する基盤サービスおよびリソースの利用権限。

-   **MCP ツールユーザーロール:**
    API Registry 経由で MCP ツールを呼び出せるよう、エージェントで使用するアカウントに
    MCP ツールユーザーロール（`roles/mcp.toolUser`）を付与します:
    `gcloud projects add-iam-policy-binding {PROJECT_ID} --member={member}
    --role="roles/mcp.toolUser"`

たとえば BigQuery と連携する MCP サーバーツールを使う場合、
サービスアカウントなど認証情報に紐づくアカウントには、
データセットへのアクセスやクエリ実行のために
`bigquery.dataViewer` や `bigquery.jobUser` などの適切な BigQuery IAM ロールが必要です。
BigQuery MCP サーバーでは、ツールの利用に
`"x-goog-user-project": PROJECT_ID` ヘッダーが必要です。
認証やプロジェクトコンテキストのための追加ヘッダーは、`ApiRegistry` コンストラクタの
`header_provider` 引数から注入できます。

## 設定 {#configuration}

***APIRegistry*** オブジェクトの設定オプションは次のとおりです:

-   **`api_registry_project_id`** (`str`):
    API Registry が配置されている Google Cloud プロジェクト ID。

-   **`location`** (`str`, 任意):
    API Registry リソースのロケーション。
    デフォルトは `"global"` です。

-   **`header_provider`** (`Callable`, 任意):
    呼び出しコンテキストを受け取り、MCP サーバーへのリクエストに付与する
    追加 HTTP ヘッダーの辞書を返す関数。
    動的な認証やプロジェクト固有のヘッダー指定によく使用されます。

`get_toolset()` 関数の設定オプションは次のとおりです:

-   **`mcp_server_name`** (`str`):
    ツールを読み込む登録済み MCP サーバーの完全なリソース名。
    例: `projects/my-project/locations/global/mcpServers/my-server`。

-   **`tool_filter`** (`Union[ToolPredicate, List[str]]`, 任意):
    ツールセットに含めるツールを指定します。
    -   文字列リストの場合、リスト内の名前と一致するツールのみが含まれます。
    -   `ToolPredicate` 関数の場合、各ツールに対して関数が呼び出され、
        `True` を返したツールのみが含まれます。
    -   `None` の場合、MCP サーバーのすべてのツールが含まれます。

-   **`tool_name_prefix`** (`str`, 任意):
    生成されるツールセットの各ツール名に付与するプレフィックス。

## 追加リソース

-   [api_registry_agent](https://github.com/google/adk-python/tree/main/contributing/samples/api_registry_agent/)
    ADK コードサンプル
-   [Google Cloud API Registry](https://docs.cloud.google.com/api-registry/docs/overview)
    ドキュメント
