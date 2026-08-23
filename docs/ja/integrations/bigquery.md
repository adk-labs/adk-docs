---
catalog_title: BigQuery ツール
catalog_description: BigQuery に接続してデータを取得し、分析を実行します
catalog_icon: /integrations/assets/bigquery.png
catalog_tags: ["data", "google"]
---

# ADK用 BigQuery ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.1.0</span>
</div>

BigQuery 統合を提供するツールセットは次のとおりです。

* **`list_dataset_ids`**: GCP プロジェクトに存在する BigQuery データセット ID を取得します。
* **`get_dataset_info`**: BigQuery データセットに関するメタデータを取得します。
* **`list_table_ids`**: BigQuery データセットに存在するテーブル ID を取得します。
* **`get_table_info`**: BigQuery テーブルに関するメタデータを取得します。
* **`get_job_info`**: BigQuery ジョブに関するメタデータ情報 (スロット使用率、構成、統計、ステータスなど) を取得します。
* **`execute_sql`**: BigQuery で SQL クエリを実行し、結果を取得します。
* **`forecast`**: `AI.FORECAST` 関数を使用して BigQuery AI 時系列予測を実行します。
* **`analyze_contribution`**: メトリックの変化の要因を把握するために BigQuery ML 寄与度分析を実行します。
* **`detect_anomalies`**: ARIMA_PLUS モデルをトレーニングし、時系列データの異常を検出します。
* **`ask_data_insights`**: 自然言語を使用して BigQuery テーブル内のデータに関する質問に回答します。
* **`search_catalog`**: Dataplex を介した自然言語セマンティック検索を使用して BigQuery データセットとテーブルを検索します。

これらは `BigQueryToolset` ツールセットとしてパッケージ化されています。

## 認証

`BigQueryToolset` は `BigQueryCredentialsConfig` を介して複数の認証メカニズムをサポートしています。

### アプリケーションのデフォルト認証情報 (Application Default Credentials)

ローカル開発や、Cloud Run や GKE などの Google Cloud サービスで実行する場合は、このアプローチを使用してください。

```python
import google.auth
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# アプリケーションのデフォルト認証情報をロード
credentials, project_id = google.auth.default()

# ツールセットの構成
credentials_config = BigQueryCredentialsConfig(credentials=credentials)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

### サービス アカウント (Service Account)

サービス アカウント ファイルまたは情報を明示的に提供できます。

```python
from google.oauth2 import service_account
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# サービス アカウントの認証情報をロード
credentials = service_account.Credentials.from_service_account_file('path/to/key.json')

# ツールセットの構成
credentials_config = BigQueryCredentialsConfig(credentials=credentials)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

### 外部アクセス トークン (External Access Token)

エンドユーザーに代わって動作する必要があるアプリケーションの場合、OAuth2 フローや外部 IDP などから取得したアクセス トークンから直接インスタンス化されたユーザー認証情報を渡すことができます。

```python
from google.oauth2.credentials import Credentials
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# 外部 OAuth フローによって 'user_token' が取得されたと仮定
credentials = Credentials(token=user_token)

# ツールセットの構成
credentials_config = BigQueryCredentialsConfig(credentials=credentials)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

### 外部認証プロバイダー (External Auth Providers)

Gemini Enterprise など、トークンがプラットフォームによって管理される外部認証プロバイダーと統合する場合は、`external_access_token_key` を使用します。

```python
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# セッション状態内のアクセス トークンを検索するために使用されるキー
credentials_config = BigQueryCredentialsConfig(
    external_access_token_key="YOUR_AUTH_ID"
)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

### 対話型認証 (Interactive Auth - ADK Web)

対話型セッションに `adk web` インターフェースを使用する場合、OAuth 2.0 クライアント認証情報を提供してログイン フローをトリガーできます。このメカニズムは、ローカル開発と Cloud Run などの環境にデプロイされた ADK エージェントの両方で機能します。

```python
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# OAuth 2.0 クライアント ID とシークレットを提供
credentials_config = BigQueryCredentialsConfig(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

## サンプル コード

次のサンプル コードは、アプリケーションのデフォルト認証情報 (ADC) を使用して ADK エージェントで `BigQueryToolset` を使用する方法を示しています。

```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigquery.py"
```

## サンプル エージェント

詳細な認証例を含む BigQuery 搭載エージェントの完全な実行可能なサンプルについては、GitHub の [BigQuery Sample Agent](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/bigquery) を参照してください。

注: BigQuery データ エージェントをツールとして使用する場合は、[ADK用 Data Agents ツール](data-agent.md)を参照してください。
