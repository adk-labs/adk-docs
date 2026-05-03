---
catalog_title: Knowledge Engine
catalog_description: 지식 엔진을 사용하여 개인 데이터 검색 수행
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["data","google"]
---


# ADK용 지식 엔진 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`vertex_ai_rag_retrieval` 도구를 사용하면 에이전트가 개인 데이터를 수행할 수 있습니다.
지식 엔진을 사용하여 검색합니다.

Knowledge Engine으로 Grounding을 사용할 경우 RAG Corpus를 준비해야 합니다.
미리. [RAG ADK agent
sample](https://github.com/google/adk-samples/blob/main/python/agents/RAG/rag/shared_libraries/prepare_corpus_and_data.py)를 참조하십시오
또는 [Knowledge Engine
page](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-quickstart)
설정을 위해.

!!! warning "경고: 에이전트당 단일 도구 제한"

    이 도구는 에이전트 인스턴스 내에서 ***자체적으로***만 사용할 수 있습니다.
    이 제한 사항 및 해결 방법에 대한 자세한 내용은 다음을 참조하세요.
    [Limitations for ADK tools](/tools/limitations/).

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/rag_engine.py"
    ```
