---
catalog_title: Data Agents
catalog_description: AI を活用したエージェントでデータを分析する
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["data", "google"]
---

# ADK 用 Google Cloud Data Agents ツール

<div class="language-support-tag">
  <span class="lst-supported">ADK でのサポート</span><span class="lst-python">Python v1.23.0</span>
</div>

これらは、[Conversational Analytics API](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/overview) を活用したデータエージェントとの統合を提供することを目的としたツールセットです。
データエージェントは、自然言語を使用してデータを分析するのに役立つ AI 搭載のエージェントです。データエージェントを構成する際は、**BigQuery**、**Looker**、**Looker Studio** などのサポートされているデータソースから選択できます。
`DataAgentToolset` には、デフォルトで次の読み取り専用ツールが含まれています。

* **`list_accessible_data_agents`**: 指定された Google Cloud プロジェクト内でアクセス権限があるデータエージェントを一覧表示します。オプションの `location` オーバーライドや、自動または手動のページネーション（`page_size` と `page_token`）をサポートしています。
* **`get_data_agent_info`**: 完全なリソース名（`projects/{project}/locations/{location}/dataAgents/{agent}`）を指定して、特定のデータエージェントに関する詳細と公開済みのコンテキストを取得します。
* **`ask_data_agent`**: 特定のデータエージェントに自然言語の質問を送信し、そのレスポンスを返します。

`DataAgentToolConfig` で `enable_data_agent_modification=True` を設定すると、ツールセットには次のツールも含まれます。

* **`create_data_agent`**: [`DataAgent` リソーススキーマ](https://docs.cloud.google.com/gemini/data-agents/reference/rest/v1/projects.locations.dataAgents#DataAgent)に準拠した JSON `agent_config` から、Google Cloud プロジェクト内に指定された `data_agent_id` で新しいデータエージェントを作成します。`location` 引数はオプションです。
* **`update_data_agent`**: JSON `agent_config` と、カンマ区切りのキャメルケース（camelCase）フィールド名の `update_mask`（例: `displayName,description`）から、既存のデータエージェントを更新します。`update_mask` にリストされているすべてのフィールドは、`agent_config` にも存在している必要があります。
* **`delete_data_agent`**: 完全なリソース名を指定して、既存のデータエージェントを削除します。

これらの変更ツールは、基盤となる長時間実行オペレーションが完了するまで、最大 `data_agent_modification_timeout_seconds` 秒間待機します。

## 前提条件

これらのツールを使用する前に、Google Cloud で次の手順を完了してください。

* Google Cloud プロジェクトで Gemini Data Analytics API（`geminidataanalytics.googleapis.com`）を有効にします。
* ツールセットで使用される認証情報に、データエージェントとその基盤となるデータソースに必要な IAM 権限があることを確認します。エージェントを Google Cloud に接続する方法の詳細については、[Google Cloud と Agent Platform への接続](/get-started/google-cloud/)ガイドをご覧ください。
* `get_data_agent_info` ツールと `ask_data_agent` ツールには、既存のデータエージェントが必要です。`create_data_agent`（`enable_data_agent_modification=True` の場合）を使用するか、次のいずれかのガイドに従って作成できます。
    * [HTTP と Python を使用してデータエージェントを構築する](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-http)
    * [Python SDK を使用してデータエージェントを構築する](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-sdk)
    * [BigQuery Studio でデータエージェントを作成する](https://docs.cloud.google.com/bigquery/docs/create-data-agents#create_a_data_agent)

## 認証

`DataAgentToolset` には `DataAgentCredentialsConfig` が必要であり、複数の認証メカニズムをサポートしています。`credentials`、`external_access_token_key`、または `client_id` と `client_secret` のペアのいずれかを指定する必要があります。デフォルトでは、`DataAgentCredentialsConfig` は `https://www.googleapis.com/auth/bigquery` OAuth スコープを使用しますが、OAuth クライアント認証情報を構成する際に `scopes` を使用してオーバーライドできます。

!!! example "試験運用版（Experimental）"
    `DataAgentCredentialsConfig` クラスは `BaseGoogleCredentialsConfig` を拡張しています。これは試験運用版であり、
    本番環境プロジェクトでは使用しないでください。

### アプリケーションのデフォルト認証情報（ADC）

ローカル開発や、Cloud Run や GKE などの Google Cloud サービス上で実行する場合は、このアプローチを使用する必要があります。

```python
import google.auth
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# アプリケーションのデフォルト認証情報を読み込む
credentials, project_id = google.auth.default()

# ツールセットを構成する
credentials_config = DataAgentCredentialsConfig(credentials=credentials)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

### サービス アカウント

サービス アカウント ファイルまたは情報を明示的に指定できます。

```python
from google.oauth2 import service_account
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# サービス アカウントの認証情報を読み込む
credentials = service_account.Credentials.from_service_account_file('path/to/key.json')

# ツールセットを構成する
credentials_config = DataAgentCredentialsConfig(credentials=credentials)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

### 外部アクセス トークン

エンドユーザーに代わって処理を行う必要があるアプリケーションの場合、OAuth2 フローや外部 IDP などから取得したアクセス トークンから直接インスタンス化されたユーザー認証情報を渡すことができます。

```python
from google.oauth2.credentials import Credentials
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# 'user_token' が外部 OAuth フロー経由で取得されていると仮定
credentials = Credentials(token=user_token)

# ツールセットを構成する
credentials_config = DataAgentCredentialsConfig(credentials=credentials)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

### 外部認証プロバイダ

Gemini Enterprise など、トークンがプラットフォームによって管理される外部認証プロバイダと統合する場合は、`external_access_token_key` を使用します。

```python
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# セッション状態内でアクセス トークンを検索するために使用されるキー
credentials_config = DataAgentCredentialsConfig(
    external_access_token_key="YOUR_AUTH_ID"
)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

### インタラクティブ認証（ADK Web）

インタラクティブ セッションに `adk web` インターフェースを使用する場合、OAuth 2.0 クライアント認証情報を指定してログインフローをトリガーできます。このメカニズムは、ローカル開発と、ADK エージェントが Cloud Run などの環境にデプロイされている場合の両方で機能します。

```python
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig

# OAuth 2.0 クライアント ID とシークレットを指定
credentials_config = DataAgentCredentialsConfig(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
data_agent_toolset = DataAgentToolset(credentials_config=credentials_config)
```

## 構成

[`DataAgentToolConfig`](../api-reference/python/google-adk.html#google.adk.tools.data_agent.DataAgentToolConfig) を使用してツールの動作をカスタマイズできます。

* **`max_query_result_rows`**（`int`、デフォルト: `50`）: `ask_data_agent` が各データ結果に対して返す最大行数。
* **`location`**（`str | None`、デフォルト: `None`）: API エンドポイントの選択に使用されるデフォルトの Google Cloud ロケーション（例: `global`、`us`、`eu`）。`location` 引数を取るツールは、引数が設定されていない場合にこの値を使用し、設定されていない場合は `global` にフォールバックします。その他のツールはデータエージェントのリソース名からロケーションを使用しますが、`ask_data_agent` はこの値が設定されている場合にこの値を使用します。
* **`api_endpoint`**（`str | None`、デフォルト: `None`）: Conversational Analytics API リクエスト用のオプションのカスタム API エンドポイント。指定した場合、デフォルトまたはロケーション由来の API エンドポイントをオーバーライドします。
* **`enable_data_agent_modification`**（`bool`、デフォルト: `False`）: `True` の場合、ツールセットに `create_data_agent`、`update_data_agent`、`delete_data_agent` も含まれます。`False` の場合、ツールセットは読み取り専用になります。
* **`data_agent_modification_timeout_seconds`**（`int`、デフォルト: `60`）: 長時間実行される作成、更新、または削除オペレーションをポーリングする際の合計タイムアウト（秒）。`0` より大きい必要があります。
* **`data_agent_modification_poll_interval_seconds`**（`int`、デフォルト: `2`）: 作成、更新、または削除オペレーションが完了するのを待機する間のポーリング間隔（秒）。`0` より大きい必要があります。

!!! warning "使用上の注意"

    `enable_data_agent_modification=True` を設定すると、エージェントが Google Cloud プロジェクト内のデータエージェントを作成、更新、削除できるようになります。ツールセットで使用される認証情報が、必要最小限の IAM 権限を持つ承認済みのプロジェクトに制限されていることを確認してください。また、`DataAgentToolset` に `tool_filter` を渡して、特定のツールのみを公開することもできます（例: `delete_data_agent` を除外する）。

```python
import google.auth
from google.adk.tools.data_agent import DataAgentToolset, DataAgentCredentialsConfig
from google.adk.tools.data_agent.config import DataAgentToolConfig

credentials, _ = google.auth.default()
credentials_config = DataAgentCredentialsConfig(credentials=credentials)

tool_config = DataAgentToolConfig(
    max_query_result_rows=100,
    enable_data_agent_modification=True,
    data_agent_modification_timeout_seconds=120,
)
data_agent_toolset = DataAgentToolset(
    credentials_config=credentials_config,
    data_agent_tool_config=tool_config,
)
```

## サンプルコード

次のサンプルコードは、アプリケーションのデフォルト認証情報（ADC）を使用して ADK エージェントで `DataAgentToolset` を使用する方法を示しています。

```py
--8<-- "examples/python/snippets/tools/built-in-tools/data_agent.py:just_code"
```

注: BigQuery のテーブルやデータセットをツールとして直接クエリする場合は、[ADK 用 BigQuery ツール](bigquery.md)をご覧ください。
