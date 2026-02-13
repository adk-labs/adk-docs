---
catalog_title: Spanner ツール
catalog_description: Spanner と連携してデータ取得、検索、SQL 実行を行います
catalog_icon: /adk-docs/integrations/assets/spanner.png
catalog_tags: ["data","google"]
---

# ADK 向け Google Cloud Spanner ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.11.0</span>
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
