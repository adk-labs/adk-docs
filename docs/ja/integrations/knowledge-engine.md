---
catalog_title: Knowledge Engine
catalog_description: ナレッジ エンジンを使用してプライベート データの取得を実行する
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["data","google"]
---


# ADK 用のナレッジ エンジン ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`vertex_ai_rag_retrieval` ツールを使用すると、エージェントはプライベート データを実行できます。
ナレッジエンジンを使用した検索。

Knowledge Engine でグラウンディングを使用する場合は、事前に RAG コーパスを準備する必要があります。設定方法については [Knowledge Engine ページ](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-quickstart) を参照してください。

!!! warning "警告: エージェントごとに 1 つのツールの制限"

    このツールは、エージェント インスタンス内で***単独で***のみ使用できます。
    この制限と回避策の詳細については、次を参照してください。
    [Limitations for ADK tools](/tools/limitations/)。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/rag_engine.py"
    ```
