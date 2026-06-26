---
catalog_title: Google Cloud Storage
catalog_description: Google Cloud Storage バケットおよびオブジェクトにアクセスして操作を実行します
catalog_icon: /integrations/assets/gcs.png
catalog_tags: ["data", "google"]
---

# Google Cloud Storage (GCS)

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.3.0</span>
</div>

`GCSToolset` および `GCSAdminToolset` を使用すると、ADK 에이전트가 [Google Cloud Storage (GCS)](https://cloud.google.com/storage) と相互作用してバケットを管理し、オブジェクトを読み書きできるようになります。

## 主なユースケース

- **オブジェクト管理 (Object Management)**: GCS オブジェクトの読み取り, ダウンロード, 作成, アップロード, 一覧表示, メタデータ確認, および削除を行います。
- **バケット管理 (Bucket Management)**: クラウドストレージバケットの一覧表示, 新規バケットの作成, バージョン管理や一様なバケットレベルのアクセスなどの構成の変更, およびバケットの削除を行います。
- **데이터 통합 (Data Integration)**: ファイルの処理や取り込み(ingestion)など, エージェントのワークフローの一部としてクラウドストレージオブジェクトを動的に사용します。

## 前提条件

- 対象の Google Cloud プロジェクトで **Google Cloud Storage API を有効化**します。
- **IAM 権限**: 認証されたプリンシパル（アプリケーションのデフォルト認証情報, サービスアカウント, またはユーザー）は, GCS バケットおよびオブジェクトの操作を実行するために, `roles/storage.objectAdmin` および `roles/storage.admin` を含む正しい権限を持っている必要があります。
- Google Cloud プロジェクト ID が構成されている必要があります。

## 認証

`GCSToolset` と `GCSAdminToolset` は, `GCSCredentialsConfig` を通じて複数の認証メカニズムをサポートしています:

### アプリケーションのデフォルト認証情報 (Application Default Credentials)

ローカル開発および Agent Runtime, Cloud Run, GKE を含む Google Cloud へのデプロイに推奨されます。

```python
import google.auth
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# アプリケーションのデフォルト認証情報をロード
credentials, _ = google.auth.default()

# ツールセットを構成
credentials_config = GCSCredentialsConfig(credentials=credentials)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

### サービスアカウント (Service Account)

サービスアカウントファイルから資格情報を提供できます。

```python
import google.auth
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# サービスアカウントの資格情報をロード
credentials, _ = google.auth.load_credentials_from_file('path/to/key.json')

# ツールセットを構成
credentials_config = GCSCredentialsConfig(credentials=credentials)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

### 外部アクセストークン (External Access Token)

OAuth2 フローや外部 ID プロバイダなどを通じて, エンドユーザーの代わりに行動する場合に使用します。

```python
from google.oauth2.credentials import Credentials
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# 外部 OAuth フローを介して 'user_token' を取得したと仮定
credentials = Credentials(token=user_token)

# ツールセットを構成
credentials_config = GCSCredentialsConfig(credentials=credentials)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

### 外部認証プロバイダ (External Auth Providers)

Gemini Enterprise のように, トークンが環境やプラットフォームによって外部で管理されるプラットフォーム向けです。

```python
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# セッション状態のアクセストークンを参照するために使用されるキー
credentials_config = GCSCredentialsConfig(
    external_access_token_key="YOUR_AUTH_ID"
)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

### 対話型認証 (ADK Web)

`adk web` インターフェースを使用した対話型セッションで, OAuth 2.0 ログインフローをトリガーする場合に使用します。

```python
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# OAuth 2.0 クライアント ID とクライアントシークレットを提供
credentials_config = GCSCredentialsConfig(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

## エージェントでの使用

次の例は, 資格情報を構成し, 書き込みアクセスが有効なストレージツールセットのインスタンスを作成する方法を示しています。

```python
import google.auth
from google.adk.agents.llm_agent import LlmAgent
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.settings import GCSToolSettings, Capabilities
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# 1. アプリケーションのデフォルト認証情報（ADC）をロード
application_default_credentials, _ = google.auth.default()

# 2. 資格情報の構成
credentials_config = GCSCredentialsConfig(
    credentials=application_default_credentials
)

# 3. 設定の構成 (読み書きの許可)
tool_settings = GCSToolSettings(capabilities=[Capabilities.READ_WRITE])

# 4. GCS ツールセットのインスタンスを作成
gcs_toolset = GCSToolset(
    credentials_config=credentials_config,
    gcs_tool_settings=tool_settings
)

# 5. ツールセットを使用して LLM エージェントを定義
agent = LlmAgent(
    model="gemini-2.5-flash",
    name="gcs_agent",
    description="Agent for interacting with GCS buckets and objects.",
    instruction="""
        You are a storage assistant agent. Use the GCS tools to answer questions,
        list objects, upload files, or perform admin tasks as requested.
    """,
    tools=[gcs_toolset]
)
```

## 利用可能なツール

GCS 連携は, 機能を大きく2つのツールセットに分けます:

### GCS ストレージツール (`GCSToolset`)

ツール | 説明
---- | -----------
`gcs_get_bucket` | GCS バケットに関するメタデータ情報を取得します。
`gcs_list_objects` | GCS バケット内のオブジェクト名を一覧表示します。オプションで接頭辞フィルタリングとページネーションをサポートします。
`gcs_get_object_metadata` | 特定의 GCS オブジェクト(blob)のメタデータプロパティを取得します。
`gcs_create_object` | メモリ内の文字列データまたはローカルファイルのアップロードから, バケット内に新しいオブジェクト(blob)を作成します。
`gcs_get_object_data` | GCS オブジェクトのコンテンツを文字列として取得するか, ローカルファイルに直接ダウンロードします。
`gcs_delete_objects` | バケットから複数の GCS オブジェクト(blob)を削除します.

### GCS 管理ツール (`GCSAdminToolset`)

ツール | 説明
---- | -----------
`gcs_list_buckets` | Google Cloud プロジェクト内の GCS バケット名を一覧表示します。
`gcs_create_bucket` | 特定のロケーションに新しい GCS バケットを作成します。
`gcs_update_bucket` | GCS バケットのプロパティ（バージョン管理や一様なバケットレベルのアクセスなど）を更新します。
`gcs_delete_bucket` | GCS バケットを削除します（バケットは事前に空である必要があります）。

## サンプルエージェント

詳細な認証構成を含む, GCS を利用したエージェントの実行可能な完全な例については, 以下を参照してください。

- [GCS ストレージサンプルエージェント](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/gcs)
- [GCS 管理サンプルエージェント](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/gcs_admin)

## リソース

- [Google Cloud Storage 公式ドキュメント](https://cloud.google.com/storage/docs)
- [GitHub リポジトリ](https://github.com/google/adk-python)
