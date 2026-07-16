---
catalog_title: Agent Search
catalog_description: Agent Search で設定済みのプライベート データ ストア全体を検索する
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["search","google"]
---


# ADK 用エージェント検索ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
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

## 動的構成

`VertexAiSearchTool` のサブクラスを作成し、`_build_vertex_ai_search_config` メソッドをオーバーライドすることで、会話のコンテキストに基づいて検索設定を動的に構成できます。このアプローチは、ユーザーごとのデータ フィルタリングなどの機能を実装するのに便利です。

`_build_vertex_ai_search_config` メソッドは、会話の `readonly_context` を引数として受け取ります。このコンテキストを使用して状態情報にアクセスし、実行時に検索構成を調整できます。

```python
from google.genai import types
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import VertexAiSearchTool

class MyVertexAISearchTool(VertexAiSearchTool):
    def _build_vertex_ai_search_config(
        self, readonly_context: ReadonlyContext
    ) -> types.VertexAISearch:
        """ユーザー固有のフィルターを追加して VertexAISearch 構成を構築します。"""
        config = super()._build_vertex_ai_search_config(readonly_context)
        if "user_id" in readonly_context.state:
            user_id = readonly_context.state["user_id"]
            config.filter = f'user_id: ANY("{user_id}")'
        return config
```
