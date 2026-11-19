---
catalog_title: Knowledge Engine
catalog_description: Knowledge Engine을 사용하여 비공개 데이터 검색 수행
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["data","google"]
---


# ADK용 Knowledge Engine 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span><span class="lst-kotlin">Kotlin v0.7.0</span>
</div>

`vertex_ai_rag_retrieval` 도구를 사용하면 에이전트가 Knowledge Engine을 통해 비공개 데이터를 검색할 수 있습니다.

Knowledge Engine으로 그라운딩(Grounding)을 사용할 때는 사전에 RAG 코퍼스(corpus)를 준비해야 합니다. 설정 방법은 [Knowledge Engine 페이지](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-quickstart)를 참고하세요.

!!! warning "경고: 에이전트당 단일 도구 제한"

    이 도구는 에이전트 인스턴스 내에서 **단독으로만**(다른 도구와 함께 사용 불가) 사용할 수 있습니다.
    이 제한 사항 및 우회 방법에 대한 자세한 내용은
    [ADK 도구 제한 사항](/tools/limitations/)을 참고하세요.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/rag_engine.py"
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/integrations/RagEngine.kt:full_code"
    ```
