---
catalog_title: Apigee API Hub
catalog_description: Apigee API hub の文書化された API をツールとして変換
catalog_icon: /adk-docs/integrations/assets/apigee.png
catalog_tags: ["connectors", "google"]
---

# ADK 用 Apigee API Hub ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

**ApiHubToolset** を使うと、Apigee API Hub の文書化された API を
数行のコードでツール化できます。このセクションでは、API への安全な接続のための認証設定を含め、
ステップごとの手順を示します。

**前提条件**

1. [ADK をインストール](/adk-docs/get-started/installation/)
2. [Google Cloud CLI](https://cloud.google.com/sdk/docs/install?db=bigtable-docs#installation_instructions) のインストール
3. 文書化済み（OpenAPI 仕様）API を持つ [Apigee API Hub](https://cloud.google.com/apigee/docs/apihub/what-is-api-hub) インスタンス
4. プロジェクト構成を設定し、必要なファイルを作成

```console
project_root_folder
 |
 `-- my_agent
     |-- .env
     |-- __init__.py
     |-- agent.py
     `__ tool.py
```

## API Hub Toolset を作成

注意: このチュートリアルにはエージェント作成が含まれます。既にエージェントがある場合は、いくつかの手順のみ実施してください。

1. APIHubToolset が API Hub API から仕様を取得できるよう、アクセストークンを取得します。
   ターミナルで次のコマンドを実行してください。

    ```shell
    gcloud auth print-access-token
    # 'ya29....' のようなアクセストークンが表示されます
    ```

2. 使用するアカウントに必要な権限があるか確認します。事前定義の
   `roles/apihub.viewer` を使うか、以下の権限を付与します。

    1. **apihub.specs.get（必須）**
    2. apihub.apis.get（任意）
    3. apihub.apis.list（任意）
    4. apihub.versions.get（任意）
    5. apihub.versions.list（任意）
    6. apihub.specs.list（任意）

3. `tools.py` に `APIHubToolset` でツールを作成します。

   API が認証を必要とする場合は、ツールへ認証を設定する必要があります。以下のコードは
   API キーの設定例です。ADK はトークンベース認証（API Key、Bearer token）、サービスアカウント、
   OpenID Connect をサポートします。将来的に各種 OAuth2 フローのサポートを追加予定です。

    ```py
    from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
    from google.adk.tools.apihub_tool.apihub_toolset import APIHubToolset

    # API に必要な認証を提供します。API が認証不要の場合は不要です。
    auth_scheme, auth_credential = token_to_scheme_credential(
        "apikey", "query", "apikey", apikey_credential_str
    )

    sample_toolset = APIHubToolset(
        name="apihub-sample-tool",
        description="Sample Tool",
        access_token="...",  # 手順1で生成されたアクセストークンを貼り付けます
        apihub_resource_name="...", # API Hub リソース名
        auth_scheme=auth_scheme,
        auth_credential=auth_credential,
    )
    ```

   本番環境でのデプロイでは、アクセストークンよりもサービスアカウントの使用を推奨します。
   上記スニペットでは `service_account_json=service_account_cred_json_str` を使用し、
   トークンの代わりにサービスアカウントの認証情報を渡します。

   `apihub_resource_name` は、API で使用している OpenAPI Spec の ID が分かる場合、
   `` `projects/my-project-id/locations/us-west1/apis/my-api-id/versions/version-id/specs/spec-id` `` を使用します。
   ツールセットに API から最初に利用可能な spec を自動で取得させる場合は
   `` `projects/my-project-id/locations/us-west1/apis/my-api-id` `` を使用します。

4. `agent.py` を作成し、作成したツールをエージェント定義に追加します。

    ```py
    from google.adk.agents.llm_agent import LlmAgent
    from .tools import sample_toolset

    root_agent = LlmAgent(
        model='gemini-2.0-flash',
        name='enterprise_assistant',
        instruction='Help user, leverage the tools you have access to',
        tools=sample_toolset.get_tools(),
    )
    ```

5. `__init__.py` を設定してエージェントを公開します。

    ```py
    from . import agent
    ```

6. Google ADK Web UI を起動してエージェントを試してください。

    ```shell
    # `project_root_folder` から `adk web` を実行してください
    adk web
    ```

   次に [http://localhost:8000](http://localhost:8000) にアクセスし、Web UI からエージェントを試験運用します。
