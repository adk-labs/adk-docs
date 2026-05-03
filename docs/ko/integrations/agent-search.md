---
catalog_title: Agent Search
catalog_description: 에이전트 검색에서 비공개로 구성된 데이터 저장소를 검색하세요.
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["search","google"]
---


# ADK용 에이전트 검색 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

`vertex_ai_search_tool`는 Google Cloud Agent Search를 사용하여
구성된 개인 데이터 저장소(예: 내부
문서, 회사 정책, 지식 기반). 이 내장 도구에는 다음이 필요합니다.
구성 중에 특정 데이터 저장소 ID를 제공합니다. 자세한 내용은
도구에 대해서는 참조하세요.
[Understanding Grounding with Search](/grounding/grounding_with_search/).

!!! warning "경고: 에이전트당 단일 도구 제한"

    이 도구는 에이전트 인스턴스 내에서 ***자체적으로***만 사용할 수 있습니다.
    이 제한 사항 및 해결 방법에 대한 자세한 내용은 다음을 참조하세요.
    [Limitations for ADK tools](/tools/limitations/#one-tool-one-agent).

```py
--8<-- "examples/python/snippets/tools/built-in-tools/agent_search.py"
```
