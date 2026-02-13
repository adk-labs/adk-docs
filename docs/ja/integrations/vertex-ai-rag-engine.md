---
catalog_title: Vertex AI RAG Engine
catalog_description: Vertex AI RAG Engine を使ってプライベートデータを検索します
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["data","google"]
---

# ADK 向け Vertex AI RAG Engine ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`vertex_ai_rag_retrieval` ツールを使うと、エージェントは Vertex
AI RAG Engine を用いてプライベートデータ検索を実行できます。

Vertex AI RAG Engine でグラウンディングを使う場合は、事前に RAG コーパスを準備する必要があります。
設定方法は [RAG ADK agent sample](https://github.com/google/adk-samples/blob/main/python/agents/RAG/rag/shared_libraries/prepare_corpus_and_data.py) または [Vertex AI RAG Engine ページ](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-quickstart) を参照してください。

!!! warning "警告: 1 エージェント 1 ツール制限"

    このツールは、1 つのエージェントインスタンス内で ***単独でのみ*** 使用できます。
    この制限と回避策の詳細は
    [ADK ツールの制限事項](/adk-docs/tools/limitations/)を参照してください。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/vertexai_rag_engine.py"
    ```
