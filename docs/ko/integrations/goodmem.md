---
catalog_title: GoodMem
catalog_description: 대화 전반에 걸쳐 에이전트에 영속적인 의미 메모리를 추가합니다
catalog_icon: /integrations/assets/goodmem.svg
catalog_tags: ["data"]
---

# ADK용 GoodMem 플러그인

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[GoodMem ADK 플러그인](https://github.com/PAIR-Systems-Inc/goodmem-adk)은 ADK 에이전트를 [GoodMem](https://goodmem.ai)이라는 벡터 기반 의미 메모리 서비스에 연결합니다. 이 통합을 사용하면 에이전트가 대화 전반에 걸쳐 지속적으로 검색 가능한 메모리를 유지할 수 있어, 과거 상호작용, 사용자 선호도, 업로드된 문서를 기억할 수 있습니다.

통합 방식은 두 가지입니다.

| 방식 | 설명 |
|---|---|
| **플러그인** (`GoodmemPlugin`) | ADK 콜백을 통해 매 턴마다 암묵적이고 결정론적인 메모리를 제공합니다. 모든 대화 턴과 파일 첨부를 자동으로 저장합니다. |
| **도구** (`GoodmemSaveTool`, `GoodmemFetchTool`) | 에이전트가 메모리를 언제 저장하고 조회할지 직접 결정하는 명시적 메모리 방식입니다. |

## 사용 사례

- **에이전트를 위한 영속 메모리**: 대화 전반에 걸쳐 신뢰할 수 있는 장기 메모리를 제공합니다.
- **손이 가지 않는 멀티모달 메모리 관리**: 사용자 메시지, 에이전트 응답, 파일 첨부(PDF, DOCX 등)를 포함한 정보를 자동으로 저장하고 가져옵니다.
- **매번 처음부터 시작하지 않기**: 에이전트가 사용자, 이전 대화 내용, 이미 다뤘던 해결책을 기억하므로 토큰을 절약하고 중복 작업을 줄일 수 있습니다.

## 사전 요구 사항

- [GoodMem](https://goodmem.ai/quick-start) 인스턴스(셀프 호스팅 또는 클라우드)
- GoodMem API 키
- Gemini를 사용해 임베딩을 자동 생성하기 위한 [Gemini API 키](https://aistudio.google.com/app/api-keys)

## 설치

```bash
pip install goodmem-adk
```

## 에이전트에서 사용하기

=== "Plugin (Automatic memory)"

    ```python
    import os
    from google.adk.agents import LlmAgent
    from google.adk.apps import App
    from goodmem_adk import GoodmemPlugin

    plugin = GoodmemPlugin(
        base_url=os.getenv("GOODMEM_BASE_URL"),  # 예: "http://localhost:8080"
        api_key=os.getenv("GOODMEM_API_KEY"),
        top_k=5,  # 턴마다 가져올 메모리 개수
    )

    agent = LlmAgent(
        name="memory_agent",
        model="gemini-flash-latest",
        instruction="당신은 지속적인 메모리를 가진 유용한 어시스턴트입니다.",
    )

    app = App(name="GoodmemPluginDemo", root_agent=agent, plugins=[plugin])
    ```

=== "Tools (Agent-controlled memory)"

    ```python
    import os
    from google.adk.agents import LlmAgent
    from google.adk.apps import App
    from goodmem_adk import GoodmemSaveTool, GoodmemFetchTool

    save_tool = GoodmemSaveTool(
        base_url=os.getenv("GOODMEM_BASE_URL"),  # 예: "http://localhost:8080"
        api_key=os.getenv("GOODMEM_API_KEY"),
    )
    fetch_tool = GoodmemFetchTool(
        base_url=os.getenv("GOODMEM_BASE_URL"),
        api_key=os.getenv("GOODMEM_API_KEY"),
        top_k=5,
    )

    agent = LlmAgent(
        name="memory_agent",
        model="gemini-flash-latest",
        instruction="당신은 지속적인 메모리를 가진 유용한 어시스턴트입니다.",
        tools=[save_tool, fetch_tool],
    )

    app = App(name="GoodmemToolsDemo", root_agent=agent)
    ```

## 사용 가능한 도구

### 플러그인 콜백

`GoodmemPlugin`은 ADK 콜백을 사용해 메모리를 자동으로 관리합니다.

콜백 | 설명
---|---
`on_user_message_callback` | 사용자 메시지와 파일 첨부를 메모리에 저장합니다.
`before_model_callback` | 관련 메모리를 검색해 프롬프트에 주입합니다.
`after_model_callback` | 에이전트의 응답을 메모리에 저장합니다.

이 콜백들은 결정론적으로 동작하며 모든 에이전트 상호작용 중에 실행되어, 에이전트를 통해 전달된 모든 정보를 메모리에 저장합니다. 에이전트가 언제 저장하거나 조회할지 결정할 필요는 없습니다.

### 도구

도구 방식을 사용할 때 에이전트가 사용할 수 있는 도구는 다음과 같습니다.

도구 | 설명
---|---
`goodmem_save` | 텍스트 콘텐츠와 파일 첨부를 영속 메모리에 저장합니다.
`goodmem_fetch` | 의미적 유사도 쿼리를 사용해 메모리를 검색합니다.

이 도구들은 에이전트가 필요할 때 호출하며, 대화 컨텍스트에 따라 저장(재작성 포함) 또는 조회 시점을 에이전트가 선택할 수 있습니다.

## 설정

### 환경 변수

변수 | 필수 | 설명
---|---|---
`GOODMEM_BASE_URL` | 예 | GoodMem 서버 URL (`/v1` 접미사 제외)
`GOODMEM_API_KEY` | 예 | GoodMem API 키
`GOOGLE_API_KEY` | 예 | Gemini 임베더 자동 생성을 위한 Gemini API 키
`GOODMEM_EMBEDDER_ID` | 아니요 | 특정 임베더 고정(반드시 존재해야 함)
`GOODMEM_SPACE_ID` | 아니요 | 특정 메모리 공간 고정(반드시 존재해야 함)
`GOODMEM_SPACE_NAME` | 아니요 | 기본 공간 이름 재정의(없으면 자동 생성)

### 공간 해석

공간이 구성되지 않은 경우, 사용자별로 자동 생성됩니다.

- 플러그인: `adk_chat_{user_id}`
- 도구: `adk_tool_{user_id}`

## 추가 자료

- [GoodMem ADK on GitHub](https://github.com/PAIR-Systems-Inc/goodmem-adk)
- [GoodMem Documentation](https://goodmem.ai)
- [GoodMem ADK on PyPI](https://pypi.org/project/goodmem-adk/)
