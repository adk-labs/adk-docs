---
catalog_title: Vertex AI Search
catalog_description: Vertex AI Search で設定済みのプライベートデータストア全体を検索します
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["search","google"]
---

# ADK 向け Vertex AI Search ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

`vertex_ai_search_tool` は Google Cloud Vertex AI Search を利用し、
エージェントが設定済みのプライベートデータストア (例: 社内文書、
社内ポリシー、ナレッジベース) 全体を検索できるようにします。この組み込みツールでは、
設定時に特定のデータストア ID を指定する必要があります。ツールの詳細は
[Vertex AI Search グラウンディングの理解](/adk-docs/grounding/vertex_ai_search_grounding/) を参照してください。

!!! warning "警告: 1 エージェント 1 ツール制限"

    このツールは、1 つのエージェントインスタンス内で ***単独でのみ*** 使用できます。
    この制限と回避策の詳細は
    [ADK ツールの制限事項](/adk-docs/tools/limitations/#one-tool-one-agent)を参照してください。

```py
--8<-- "examples/python/snippets/tools/built-in-tools/vertexai_search.py"
```
