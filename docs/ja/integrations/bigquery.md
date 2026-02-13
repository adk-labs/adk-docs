---
catalog_title: BigQuery ツール
catalog_description: BigQuery に接続してデータ取得と分析を行います
catalog_icon: /adk-docs/integrations/assets/bigquery.png
catalog_tags: ["data", "google"]
---

# ADK 向け BigQuery ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.1.0</span>
</div>

BigQuery 連携を提供するツールセットは次のとおりです:

* **`list_dataset_ids`**: GCP プロジェクト内に存在する BigQuery データセット ID を取得します。
* **`get_dataset_info`**: BigQuery データセットのメタデータを取得します。
* **`list_table_ids`**: BigQuery データセット内に存在するテーブル ID を取得します。
* **`get_table_info`**: BigQuery テーブルのメタデータを取得します。
* **`execute_sql`**: BigQuery で SQL クエリを実行し、結果を取得します。
* **`forecast`**: `AI.FORECAST` 関数を使用して BigQuery AI 時系列予測を実行します。
* **`ask_data_insights`**: 自然言語で BigQuery テーブルのデータに関する質問に回答します。

これらは `BigQueryToolset` ツールセットとして提供されています。

```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigquery.py"
```

注: BigQuery データエージェントをツールとして利用したい場合は、[ADK 向け Data Agents ツール](data-agent.md)を参照してください。
