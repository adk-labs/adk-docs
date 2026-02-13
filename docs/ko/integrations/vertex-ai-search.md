---
catalog_title: Vertex AI Search
catalog_description: Vertex AI Search에서 구성된 비공개 데이터 저장소 전반을 검색합니다
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["search","google"]
---

# ADK용 Vertex AI Search 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

`vertex_ai_search_tool`은 Google Cloud Vertex AI Search를 사용하여,
에이전트가 구성된 비공개 데이터 저장소(예: 내부 문서,
사내 정책, 지식 베이스) 전반을 검색할 수 있게 합니다. 이 내장 도구를 사용하려면
구성 시 특정 데이터 저장소 ID를 제공해야 합니다. 도구에 대한 자세한 내용은
[Vertex AI Search grounding 이해하기](/adk-docs/grounding/vertex_ai_search_grounding/)를 참조하세요.

!!! warning "경고: 에이전트당 단일 도구 제한"

    이 도구는 하나의 에이전트 인스턴스 내에서 ***단독으로만*** 사용할 수 있습니다.
    이 제한과 우회 방법에 대한 자세한 내용은
    [ADK 도구 제한 사항](/adk-docs/tools/limitations/#one-tool-one-agent)을 참조하세요.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/vertexai_search.py"
```
