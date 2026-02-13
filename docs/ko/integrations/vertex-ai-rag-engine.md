---
catalog_title: Vertex AI RAG Engine
catalog_description: Vertex AI RAG Engine을 사용해 비공개 데이터를 검색합니다
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["data","google"]
---

# ADK용 Vertex AI RAG Engine 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`vertex_ai_rag_retrieval` 도구를 사용하면 에이전트가 Vertex
AI RAG Engine을 통해 비공개 데이터 검색을 수행할 수 있습니다.

Vertex AI RAG Engine으로 그라운딩을 사용하려면 먼저 RAG 코퍼스를 준비해야 합니다.
구성 방법은 [RAG ADK agent sample](https://github.com/google/adk-samples/blob/main/python/agents/RAG/rag/shared_libraries/prepare_corpus_and_data.py) 또는 [Vertex AI RAG Engine 페이지](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-quickstart)를 참조하세요.

!!! warning "경고: 에이전트당 단일 도구 제한"

    이 도구는 하나의 에이전트 인스턴스 내에서 ***단독으로만*** 사용할 수 있습니다.
    이 제한과 우회 방법에 대한 자세한 내용은
    [ADK 도구 제한 사항](/adk-docs/tools/limitations/)을 참조하세요.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/vertexai_rag_engine.py"
    ```
