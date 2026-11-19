---
catalog_title: Agent Search
catalog_description: Agent Search에 구성된 프라이빗 데이터 스토어를 검색합니다
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["search","google"]
---


# ADK용 Agent Search 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span>
</div>

`vertex_ai_search_tool`은 Google Cloud Agent Search를 사용하여 에이전트가 사전에 구성된 프라이빗 데이터 스토어(예: 사내 문서, 회사 정책, 지식 베이스)를 검색할 수 있도록 지원합니다. 이 내장 도구를 사용하려면 구성 시 특정 데이터 스토어 ID를 지정해야 합니다. 도구에 대한 자세한 내용은 [검색을 통한 그라운딩(Grounding) 이해하기](/grounding/grounding_with_search/)를 참고하세요.

!!! warning "경고: 에이전트당 단일 도구 제한"

    이 도구는 에이전트 인스턴스 내에서 **단독으로만**(다른 도구와 함께 사용 불가) 사용할 수 있습니다.
    이 제한 사항과 우회 방법에 대한 자세한 내용은
    [ADK 도구의 제한 사항](/tools/limitations/#one-tool-one-agent)을 참고하세요.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/agent_search.py"
```

## 동적 구성

`VertexAiSearchTool`의 서브클래스를 생성하고 `_build_vertex_ai_search_config` 메서드를 재정의하여 대화 컨텍스트를 기반으로 검색 설정을 동적으로 구성할 수 있습니다. 이 방식은 사용자별 데이터 필터링과 같은 기능을 구현하는 데 유용합니다.

`_build_vertex_ai_search_config` 메서드는 대화의 `readonly_context`를 인수로 받습니다. 이 컨텍스트를 사용하여 상태 정보에 접근하고 런타임에 검색 구성을 조정할 수 있습니다.

```python
from google.genai import types
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import VertexAiSearchTool

class MyVertexAISearchTool(VertexAiSearchTool):
    def _build_vertex_ai_search_config(
        self, readonly_context: ReadonlyContext
    ) -> types.VertexAISearch:
        """사용자 정의 필터를 추가하여 VertexAISearch 구성을 빌드합니다."""
        config = super()._build_vertex_ai_search_config(readonly_context)
        if "user_id" in readonly_context.state:
            user_id = readonly_context.state["user_id"]
            config.filter = f'user_id: ANY("{user_id}")'
        return config
```
