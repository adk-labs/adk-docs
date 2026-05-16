---
catalog_title: Google Cloud Agent Identity
catalog_description: エージェントの OAuth トークンと API キーを管理します
catalog_icon: /integrations/assets/agent-identity.svg
catalog_tags: ["google"]
---

# ADK 向け Agent Identity Auth Manager

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.30.0</span><span class="lst-preview">Preview</span>
</div>

[Google Cloud Agent Identity](https://docs.cloud.google.com/iam/docs/agent-identity-overview)
サービスは、認証情報設定の保存、トークンの生成と保存、アクセス監査を含む認証情報の
ライフサイクル全体を管理する、簡素化された Google 管理のソリューションです。この
アプローチにより、安全でシンプルなエージェント開発体験が得られます。

!!! example "Preview release"

    Agent Identity Auth Manager 機能は Preview リリースです。詳細は
    [リリース段階の説明](https://cloud.google.com/products#product-launch-stages)を
    参照してください。

## ユースケース

- **簡素化された OAuth フロー**: カスタムインフラを構築せずに、認証情報の
  ライフサイクル全体を管理します。
- **トークンの安全な交換と保存**: 認証情報設定を安全に保存し、トークンを交換します。
- **監査ロギング**: 保存された認証情報へのアクセスを確認、監査します。

## 前提条件

- [Google Cloud プロジェクト](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
- プロジェクトに作成された 1 つ以上の Agent Identity
  [auth provider](https://cloud.google.com/iam/docs/manage-auth-providers)
- 呼び出し元 ID に
  [`iamconnectors.user`](https://docs.cloud.google.com/iam/docs/roles-permissions/iamconnectors#iamconnectors.user)
  ロール、または同等の権限が必要です
- [Application Default Credentials](https://docs.cloud.google.com/docs/authentication/application-default-credentials)
  (`gcloud auth application-default login`) による認証設定

## インストール

必要なクライアントライブラリを取得するには、`agent-identity` extra package group を
インストールします。

```bash
pip install "google-adk[agent-identity]"
```

## エージェントでの使用

ADK 内で Agent Identity Auth Manager を使うには、次の手順に従います。

### Auth provider の登録

ADK が特定の `CustomAuthScheme` に使用する `BaseAuthProvider` を判断できるように、
`GcpAuthProvider` インスタンスを `CredentialManager` に登録します。この処理は
エージェントコード内で一度だけ実行すれば十分です。

```python
from google.adk.auth.credential_manager import CredentialManager
from google.adk.integrations.agent_identity import GcpAuthProvider

CredentialManager.register_auth_provider(GcpAuthProvider())
```

### ツールの構成

`GcpAuthProviderScheme` オブジェクトで Agent Identity auth provider を構成し、
対応する任意の `Tool` または `Toolset` の `auth_scheme` パラメータに渡します。
次の例は `McpToolset` での使用方法を示していますが、`GcpAuthProviderScheme` は
`AuthenticatedFunctionTool` などの他のツールでも使用できます。完全な例は
[GCP Auth sample](https://github.com/google/adk-python/tree/main/contributing/samples/gcp_auth)を
参照してください。

```python
from google.adk.integrations.agent_identity import GcpAuthProviderScheme
from google.adk.tools.mcp import McpToolset

auth_scheme = GcpAuthProviderScheme(
    name="projects/PROJECT_ID/locations/LOCATION/connectors/AUTH_PROVIDER_NAME",
    # continue_uri is only needed for 3-legged OAuth flows. This URI receives
    # the redirect after user consent and must be hosted by your application.
    continue_uri=CONTINUE_URI
)

toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(url="https://YOUR_MCP_SERVER_URL"),
    auth_scheme=auth_scheme,
)
```

### OAuth 同意の処理

- **Auth Request の検出**: 既存のフローと同様に、ユーザー同意が必要になるたびに
  `adk-request-credential` という `FunctionCall` イベントが生成され、`auth_uri`
  フィールドが含まれます。ユーザーアプリは、ユーザー同意フローを続行するために
  ポップアップウィンドウで `auth_uri` を開く必要があります。
- **Continue URI Handler**:
    - ユーザーがサードパーティ provider の Web サイトで OAuth 同意フローを完了すると、
      システムは先に `GcpAuthProviderScheme` で定義した `continue_uri` callback に
      redirect します。エージェントアプリケーションサービスはこの redirect を実装する
      必要があります。発行を完了するには、handler が credentials endpoint に POST
      リクエストを送信する必要があります。
      `https://iamconnectorcredentials.googleapis.com/v1alpha/{connector_name}/credentials:finalize`.
    - 認証情報の finalization が成功したら、Web アプリケーションは FunctionResponse を
      送信してエージェントを再開する必要があります。サンプル実装は
      [sample code](https://docs.cloud.google.com/iam/docs/auth-with-3lo#resume-conversation)を
      参照してください。ネイティブなユーザー同意フローとは異なり、エージェントを再開する
      ために authorization code は不要です。
    - 詳細は
      [sample handler implementation](https://docs.cloud.google.com/iam/docs/auth-with-3lo#validation-endpoint)を
      参照してください。
- **会話の再開**: 同意フローが成功したかどうかに関係なく、エージェントアプリは
  conversation turn を完了するためにエージェントを再開する必要があります。ADK は同意が
  正常に完了したかを自動的に判断し、完了していない場合はエラーを発生させます。

## リソース

- [Google Cloud Agent Identity Overview](https://docs.cloud.google.com/iam/docs/agent-identity-overview)
- [Google Cloud Agent Identity を使用した 2-legged OAuth](https://docs.cloud.google.com/iam/docs/auth-with-2lo)
- [Google Cloud Agent Identity を使用した 3-legged OAuth](https://docs.cloud.google.com/iam/docs/auth-with-3lo)
- [Google Cloud Agent Identity を使用した API key auth](https://docs.cloud.google.com/iam/docs/auth-with-api-key)
- [Sample agent code](https://github.com/google/adk-python/tree/main/contributing/samples/gcp_auth)
