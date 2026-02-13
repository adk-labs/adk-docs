---
catalog_title: Data Agents
catalog_description: AI 搭載エージェントでデータを分析します
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["data", "google"]
---

# ADK 向け Google Cloud Data Agents ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.23.0</span>
</div>

これは [Conversational Analytics API](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/overview) を利用した Data Agents 連携のためのツールセットです。

Data Agents は自然言語でデータ分析を支援する AI エージェントです。Data Agent の設定時に、**BigQuery**、**Looker**、**Looker Studio** などの対応データソースを選択できます。

**前提条件**

これらのツールを使う前に、Google Cloud 上で Data Agents を構築・設定する必要があります:

* [HTTP と Python で data agent を構築する](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-http)
* [Python SDK で data agent を構築する](https://docs.cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-sdk)
* [BigQuery Studio で data agent を作成する](https://docs.cloud.google.com/bigquery/docs/create-data-agents#create_a_data_agent)

`DataAgentToolset` には次のツールが含まれます:

* **`list_accessible_data_agents`**: 設定済み GCP プロジェクト内でアクセス権のある Data Agents を一覧表示します。
* **`get_data_agent_info`**: 完全修飾リソース名を指定して特定 Data Agent の詳細を取得します。
* **`ask_data_agent`**: 自然言語で特定 Data Agent と対話します。

これらは `DataAgentToolset` ツールセットとして提供されています。

```py
--8<-- "examples/python/snippets/tools/built-in-tools/data_agent.py"
```
