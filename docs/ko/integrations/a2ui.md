---
catalog_title: A2UI
catalog_description: Agent-to-UI 프로토콜을 사용해 에이전트에서 풍부하고 구조화된 UI를 생성합니다
catalog_icon: /integrations/assets/a2ui.svg
---

# ADK용 A2UI - Agent-to-UI

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

A2UI를 사용하면 에이전트가 텍스트만이 아니라 카드, 폼, 차트, 표 같은 **실제 UI**를 생성할 수 있습니다.
에이전트는 구조화된 JSON을 출력하고, 클라이언트의 렌더러가 이를 대화형 컴포넌트로 바꿉니다.

전송 방식에는 구애받지 않습니다. A2UI 페이로드는 A2A, MCP, REST, WebSocket 또는 다른 어떤 프로토콜로도 동작합니다.
에이전트는 *무엇*을 보여줄지 설명하고, 클라이언트는 *어떻게* 렌더링할지 결정합니다.

!!! info "A2UI에 대해 더 알아보기"
    [a2ui.org](https://a2ui.org/)에서 전체 사양, 컴포넌트 갤러리, 카탈로그 참조, 렌더러 문서를 확인할 수 있습니다.

## 빠른 시작

### SDK 설치

```bash
pip install a2ui-agent-sdk
```

### 1. 스키마 관리자 설정

`A2uiSchemaManager`는 컴포넌트 카탈로그를 불러오고, LLM이 유효한 A2UI JSON을 생성하도록 안내하는 시스템 프롬프트를 만듭니다.

```python
from a2ui.core.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

schema_manager = A2uiSchemaManager(
    catalogs=[
        BasicCatalog.get_config(
            examples_path="examples",
        ),
    ],
)
```

!!! note
    스키마 관리자는 들어오는 클라이언트 요청에서 A2UI 버전을 자동으로 감지합니다.
    필요하면 `version=VERSION_0_9`를 전달해 버전을 명시적으로 지정할 수도 있습니다.

!!! tip
    `catalogs` 매개변수를 생략하면 스키마 관리자는 A2UI 팀이 관리하는
    [Basic Catalog](https://a2ui.org/latest/catalogs/)를 사용합니다.
    이 카탈로그에는 Text, Card, Button, Image 같은 공통 컴포넌트가 포함되어 있습니다.
    [사용자 지정 카탈로그](#custom-catalogs)를 만들어 도메인별 컴포넌트를 추가하거나,
    기본 카탈로그와 자체 카탈로그를 함께 섞어 사용할 수도 있습니다.
    자세한 내용은 아래 [고급 패턴](#advanced-patterns)을 참조하세요.

### 2. 시스템 프롬프트 생성

`generate_system_prompt` 메서드는 에이전트의 역할 설명과 A2UI JSON 스키마, few-shot 예시를 결합하므로
LLM이 출력 형식을 정확히 알 수 있습니다.

```python
instruction = schema_manager.generate_system_prompt(
    role_description="You are a helpful assistant that presents information with rich UI.",
    workflow_description="Analyze the user's request and return structured UI when appropriate.",
    ui_description="Use cards for summaries, tables for comparisons, and forms for user input.",
    include_schema=True,
    include_examples=True,
    allowed_components=["Heading", "Text", "Card", "Button", "Table"],
)
```

### 3. ADK 에이전트 생성

생성한 지시문을 에이전트의 시스템 프롬프트로 사용합니다:

```python
from google.adk.agents.llm_agent import LlmAgent

agent = LlmAgent(
    model="gemini-flash-latest",
    name="ui_agent",
    description="An agent that generates rich UI responses.",
    instruction=instruction,
)
```

### 4. A2UI 출력 검증 및 스트리밍

클라이언트로 보내기 전에 항상 LLM의 JSON 출력을 검증하세요.
SDK는 파싱, 수정, 검증 유틸리티를 제공합니다:

```python
from a2ui.core.parser.parser import parse_response
from a2ui.a2a import parse_response_to_parts

# 활성 카탈로그의 검증기를 가져옵니다.
selected_catalog = schema_manager.get_selected_catalog()

# 옵션 A: 수동 파싱 + 검증
response_parts = parse_response(llm_output_text)
for part in response_parts:
    if part.a2ui_json:
        selected_catalog.validator.validate(part.a2ui_json)

# 옵션 B: A2A Part를 반환하는 한 줄짜리 방법
parts = parse_response_to_parts(
    llm_output_text,
    validator=selected_catalog.validator,
    fallback_text="찾은 내용을 알려드리겠습니다.",
)
```

A2UI 페이로드는 렌더러가 식별할 수 있도록 MIME 타입 `application/json+a2ui`의
A2A `DataPart`로 감싸집니다:

```python
from a2ui.a2a import create_a2ui_part

part = create_a2ui_part({"type": "Card", "props": {"title": "Hello"}})
# → DataPart(data={...}, metadata={"mimeType": "application/json+a2ui"})
```

## 고급 패턴

### 동적 카탈로그

문맥에 따라 다른 UI 컴포넌트가 필요한 에이전트(예: 데이터 조회용 차트, 구성용 폼)의 경우,
런타임에 카탈로그를 해석해 세션 상태에 저장합니다:

```python
async def _prepare_session(self, context, run_request, runner):
    session = await super()._prepare_session(context, run_request, runner)

    # 요청 메타데이터에서 클라이언트 기능을 확인합니다.
    capabilities = context.message.metadata.get("a2ui_client_capabilities")

    # 적절한 카탈로그를 선택합니다.
    a2ui_catalog = self.schema_manager.get_selected_catalog(
        client_ui_capabilities=capabilities
    )
    examples = self.schema_manager.load_examples(a2ui_catalog, validate=True)

    # 도구에서 사용할 수 있도록 세션 상태에 저장합니다.
    await runner.session_service.append_event(
        session,
        Event(
            actions=EventActions(
                state_delta={
                    "system:a2ui_enabled": True,
                    "system:a2ui_catalog": a2ui_catalog,
                    "system:a2ui_examples": examples,
                }
            ),
        ),
    )
    return session
```

### 사용자 지정 카탈로그

도메인별 UI를 위해 자신만의 컴포넌트 카탈로그를 정의할 수 있습니다:

```python
from a2ui.core.schema.manager import CatalogConfig

schema_manager = A2uiSchemaManager(
    catalogs=[
        BasicCatalog.get_config(),
        CatalogConfig.from_path(
            name="my_dashboard_catalog",
            catalog_path="catalogs/dashboard.json",
            examples_path="catalogs/dashboard_examples",
        ),
    ],
)
```

### 다중 에이전트 오케스트레이션

오케스트레이터 에이전트는 하위 에이전트의 A2UI 기능을 집계해 에이전트 카드에 노출할 수 있습니다:

```python
from a2ui.a2a import get_a2ui_agent_extension

# 하위 에이전트의 카탈로그 ID를 수집합니다.
supported_catalog_ids = set()
for subagent in subagents:
    for extension in subagent_card.capabilities.extensions:
        if extension.uri == "https://a2ui.org/a2a-extension/a2ui/v0.9":
            supported_catalog_ids.update(
                extension.params.get("supportedCatalogIds") or []
            )

# 오케스트레이터의 AgentCard에 노출합니다.
agent_card = AgentCard(
    capabilities=AgentCapabilities(
        extensions=[
            get_a2ui_agent_extension(
                supported_catalog_ids=list(supported_catalog_ids),
            )
        ]
    )
)
```

## 샘플

A2UI 저장소에는 바로 실행할 수 있는 ADK 샘플 에이전트가 포함되어 있습니다:

| 샘플 | 설명 |
|---|---|
| [contact_lookup](https://github.com/google/A2UI/tree/main/samples/agent/adk/contact_lookup) | 정적 스키마를 사용하는 간단한 에이전트로, 연락처를 조회하고 결과를 카드로 표시합니다 |
| [restaurant_finder](https://github.com/google/A2UI/tree/main/samples/agent/adk/restaurant_finder) | 레스토랑 정보를 검색하고 표시하는 정적 스키마 에이전트입니다 |
| [rizzcharts](https://github.com/google/A2UI/tree/main/samples/agent/adk/rizzcharts) | 문맥에 따라 차트 컴포넌트를 선택하는 동적 카탈로그 에이전트입니다 |
| [orchestrator](https://github.com/google/A2UI/tree/main/samples/agent/adk/orchestrator) | 하위 에이전트에 작업을 위임하고 UI 기능을 집계하는 다중 에이전트 구성입니다 |

## 리소스

- [A2UI 사양](https://a2ui.org/)
- [A2UI GitHub 저장소](https://github.com/google/A2UI)
- [A2UI Python SDK (`a2ui-agent-sdk`)](https://pypi.org/project/a2ui-agent-sdk/)
- [에이전트 개발 가이드](https://github.com/google/A2UI/blob/main/agent_sdks/python/agent_development.md)
- [컴포넌트 갤러리](https://a2ui.org/latest/reference/components/)
- [A2A 프로토콜](https://google.github.io/A2A/)
