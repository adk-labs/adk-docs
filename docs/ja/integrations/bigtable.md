---
catalog_title: Bigtable ツール
catalog_description: Bigtable と連携してデータ取得と SQL 実行を行います
catalog_icon: /adk-docs/integrations/assets/bigtable.png
catalog_tags: ["data", "google"]
---

# ADK 向け Bigtable ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.12.0</span>
</div>

Bigtable 連携を提供するツールセットは次のとおりです:

* **`list_instances`**: Google Cloud プロジェクト内の Bigtable インスタンスを取得します。
* **`get_instance_info`**: Google Cloud プロジェクト内のインスタンスメタデータ情報を取得します。
* **`list_tables`**: GCP Bigtable インスタンス内のテーブルを取得します。
* **`get_table_info`**: GCP Bigtable のテーブルメタデータ情報を取得します。
* **`execute_sql`**: Bigtable テーブルで SQL クエリを実行し、結果を取得します。

これらは `BigtableToolset` ツールセットとして提供されています。

```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigtable.py"
```
