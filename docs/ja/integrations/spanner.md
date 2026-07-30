---
catalog_title: Spanner ツール
catalog_description: Spanner と連携してデータ取得、検索、SQL 実行を行います
catalog_icon: /integrations/assets/spanner.png
catalog_tags: ["data","google"]
---

# ADK 向け Google Cloud Spanner ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.11.0</span>
</div>

Spanner 連携を提供するツールセットは次のとおりです:

* **`list_table_names`**: GCP Spanner データベース内に存在するテーブル名を取得します。
* **`list_table_indexes`**: GCP Spanner データベース内に存在するテーブルインデックスを取得します。
* **`list_table_index_columns`**: GCP Spanner データベース内に存在するテーブルインデックス列を取得します。
* **`list_named_schemas`**: Spanner データベースの named schema を取得します。
* **`get_table_schema`**: Spanner データベースのテーブルスキーマとメタデータ情報を取得します。
* **`execute_sql`**: Spanner データベースで SQL クエリを実行し、結果を取得します。
* **`similarity_search`**: テキストクエリを使って Spanner で類似検索を実行します。

これらは `SpannerToolset` ツールセットとして提供されています。

```py
--8<-- "examples/python/snippets/tools/built-in-tools/spanner.py"
```

## Spanner Admin Toolset

`SpannerAdminToolset` は、Spanner インスタンスおよびデータベースに対する管理操作を有効にします。このツールセットを使用するには、個別のライブラリのインポートが必要です。

!!! warning "注意して使用"

    このツールセットは Spanner インスタンスおよびデータベースを作成、検査、変更できるため、アクセス権を慎重に付与してください。実行環境（Application Default Credentials やサービス アカウント キーなど）が承認されたプロジェクトにのみ制限され、`roles/spanner.admin` などの必要な最小限の IAM 権限のみを使用していることを確認してください。

### 利用可能なツール

* **`list_instances`**: プロジェクト内の Spanner インスタンスの一覧を取得します。
* **`get_instance`**: Spanner インスタンスの詳細を取得します。
* **`create_database`**: 新しい Spanner データベースを作成します。
* **`list_databases`**: インスタンス内の Spanner データベースの一覧を取得します。
* **`create_instance`**: 新しい Spanner インスタンスを作成します。
* **`list_instance_configs`**: 利用可能な Spanner インスタンス構成の一覧を取得します。
* **`get_instance_config`**: Spanner インスタンス構成の詳細を取得します。

### 構成

このツールセットを使用する前に、必要な環境変数を設定してください。

- `SPANNER_PROJECT`: 操作対象の GCP プロジェクト ID。
- `SPANNER_INSTANCE` (オプション): デフォルトの Spanner インスタンス ID。
- `SPANNER_DATABASE` (オプション): デフォルトのデータベース ID。

### エージェントでの使用

Google Cloud Spanner の管理機能にアクセスするには `SpannerAdminToolset` を初期化します。次に、`LlmAgent` の `tools` リストに渡すことで、エージェントが Spanner リソースを管理できるようにします。

```python
from google.adk.agents import LlmAgent
from google.adk.tools.spanner import SpannerAdminToolset

# Spanner 管理ツールセットを初期化
spanner_admin_tools = SpannerAdminToolset()

# エージェントにツールセットを登録
agent = LlmAgent(
    name="SpannerAdminAgent",
    model="gemini-flash-latest",
    instruction=(
        "You are a helpful database administrator. Use the SpannerAdminToolset "
        "to manage and query Spanner instances and databases in the project."
    ),
    tools=[spanner_admin_tools]
)
```
