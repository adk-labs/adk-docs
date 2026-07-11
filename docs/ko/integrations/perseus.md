---
catalog_title: Perseus Context
catalog_description: ADK 에이전트를 위해 결정적이고 워크스페이스를 인식하는 컨텍스트를 컴파일합니다
catalog_icon: /integrations/assets/perseus.svg
catalog_tags: ["data", "mcp"]
---

# ADK용 Perseus Context 통합

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[`adk-perseus-context`](https://github.com/Perseus-Computing-LLC/adk-perseus-context) 통합은 결정적으로 컴파일된 컨텍스트를 ADK 에이전트의 시스템 지침(system instruction)에 주입합니다. 이 통합은 오픈 소스 컨텍스트 컴파일러인 [Perseus](https://github.com/Perseus-Computing-LLC/perseus)에 의해 구동됩니다. Perseus는 검색 인덱스, 임베딩, 추가 LLM 왕복 없이 추론 시점에 `@file`, `@search` 및 `@memory`와 같은 지시어를 바이트 안정적인 하나의 컨텍스트 문자열로 해석(resolve)합니다. 모든 프로세스는 로컬에서 실행됩니다.

Perseus는 컨텍스트 컴파일러이며 메모리나 RAG 백엔드가 아닙니다. 영구적인 세션 간 메모리를 사용하려면 자매 서비스인 [Perseus Vault](/ko/integrations/perseus-vault/)와 페어링하여 사용하세요.

## 사용 사례

- **결정적 컨텍스트 조립(Deterministic context assembly)**: 동일한 입력은 항상 동일한 컨텍스트를 컴파일하여 바이트 단위로 동일한 빌드를 보장하며 쿼리별 검색 편차가 발생하지 않습니다.

- **워크스페이스 인식 에이전트**: 에이전트가 현재 프로젝트 파일과 상태를 볼 수 있도록 `@file`, `@include`, `@search` 및 `@memory` 지시어를 해석합니다.

- **인덱스가 필요 없는 로컬 컨텍스트**: 벡터 저장소, 임베딩, 클라우드가 필요하지 않습니다. 컨텍스트는 에이전트를 실행하는 로컬 컴퓨터에서 컴파일됩니다.

- **고정된 크기로 전체 범위 지원**: top-k 슬라이스가 아닌 선언한 정확한 컨텍스트를 가져옵니다.

## 사전 준비 사항

- Python 3.10+
- `google-adk>=1.14.0`
- `perseus-ctx>=1.0.10` (`adk-perseus-context` 설치 시 자동으로 설치됨)

## 설치

```bash
pip install adk-perseus-context
```

## 에이전트와 함께 사용

컴파일된 Perseus 컨텍스트를 주입하는 방법은 두 가지가 있습니다. `Runner`의 모든 에이전트가 공유하는 컨텍스트에는 플러그인(plugin)을 사용하고, 단일 에이전트에는 콜백(callback)을 사용합니다. `source`는 `.perseus` 파일의 경로이거나 `@perseus`로 시작하는 인라인 문자열입니다.

### 러너 전체에 적용 (플러그인)

```python
from adk_perseus_context import PerseusContextPlugin
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="Help the user.",
)

app = App(
    name="perseus_app",
    root_agent=agent,
    plugins=[PerseusContextPlugin("context.perseus")],
)

runner = Runner(
    app=app,
    session_service=InMemorySessionService(),
)
```

### 단일 에이전트에 적용 (콜백)

```python
from adk_perseus_context import perseus_before_model_callback
from google.adk.agents import Agent

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="Help the user.",
    before_model_callback=perseus_before_model_callback("context.perseus"),
)
```

두 방법 모두 모델 호출 시 컴파일된 컨텍스트가 요청의 시스템 지침에 추가됩니다(ADK의 `LlmRequest.append_instructions` 사용). Perseus를 사용할 수 없거나 컴파일에 실패하면 컨텍스트 주입 없이 요청이 진행되고 경고가 기록됩니다(기본값은 `fail_open=True`).

### 세션별 컨텍스트

세션 상태를 통해 세션별로 소스를 재정의(override)할 수 있습니다. 이는 각 사용자나 작업이 서로 다른 워크스페이스 또는 지시어 세트를 타겟팅할 때 유용합니다. 비동기 함수 내부에서 세션을 생성합니다.

```python
session = await runner.session_service.create_session(
    app_name="perseus_app",
    user_id="user",
    state={
        "_perseus_source": "@perseus\n@file AGENTS.md\n@memory deployment",
        "_perseus_workspace": "/path/to/project",
    },
)
```

## MCP 서버로 사용 (선택사항)

Perseus는 지시어를 도구로 제공하는 MCP 서버도 함께 지원하므로 플러그인 대신(또는 플러그인과 함께) ADK의 `McpToolset`을 통해 사용할 수도 있습니다.

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

perseus_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="perseus",
            args=["mcp", "serve", "--workspace", "."],
        )
    )
)

agent = Agent(
    name="assistant",
    model="gemini-flash-latest",
    instruction="Use Perseus tools to read workspace context.",
    tools=[perseus_tools],
)
```

## 플러그인 참조

| 진입점 (Entry point) | 범위 | 설명 |
|---|---|---|
| `PerseusContextPlugin(source)` | 러너 전체 | 모든 에이전트의 모델 요청에 컴파일된 컨텍스트 주입 |
| `perseus_before_model_callback(source)` | 단일 에이전트 | 컴파일된 컨텍스트를 주입하는 `before_model_callback` |
| `_perseus_source` / `_perseus_workspace` | 세션 상태 | 세션별 소스 및 워크스페이스 재정의 |

## 비교

| 접근 방식 | 인덱스 / 임베딩 | 추가 모델 호출 | 출력 안정성 | 지원 범위 |
|---|---|---|---|---|
| 단순 컨텍스트 덤프 | 없음 | 없음 | 안정적 | 프롬프트의 모든 내용 |
| RAG / 벡터 검색 | 필요함 | 쿼리 임베딩 | 쿼리에 따라 다름 | 상위 k개 결과 |
| Perseus 컴파일 | 없음 | 없음 | 바이트 단위 동일 | 선언된 전체 내용 |

## 리소스

- [GitHub의 adk-perseus-context](https://github.com/Perseus-Computing-LLC/adk-perseus-context)
- [PyPI의 adk-perseus-context](https://pypi.org/project/adk-perseus-context/)
- [Perseus (컨텍스트 엔진)](https://github.com/Perseus-Computing-LLC/perseus)
- [Perseus Vault Memory 통합 가이드](/ko/integrations/perseus-vault/)
