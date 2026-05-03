---
catalog_title: Agent Search
catalog_description: Agent Search で設定済みのプライベート データ ストア全体を検索する
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["search","google"]
---


# ADK 用エージェント検索ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

`vertex_ai_search_tool` は Google Cloud Agent Search を使用し、
エージェントは、プライベートな設定済みデータ ストア (内部データ ストアなど) 全体を検索します。
文書、会社ポリシー、ナレッジベース)。この組み込みツールを使用するには、
構成時に特定のデータ ストア ID を指定します。さらに詳しく
ツールについては、を参照してください。
[Understanding Grounding with Search](/grounding/grounding_with_search/)。

!!! warning "警告: エージェントごとに 1 つのツールの制限"

    このツールは、エージェント インスタンス内で***単独で***のみ使用できます。
    この制限と回避策の詳細については、次を参照してください。
    [Limitations for ADK tools](/tools/limitations/#one-tool-one-agent)。

```py
--8<-- "examples/python/snippets/tools/built-in-tools/agent_search.py"
```
