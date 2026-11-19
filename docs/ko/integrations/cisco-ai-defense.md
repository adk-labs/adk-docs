---
catalog_title: Cisco AI Defense
catalog_description: 에이전트 프롬프트 및 도구 호출을 모니터링하거나 차단하는 보안 가드레일
catalog_icon: /integrations/assets/cisco-ai-defense.png
---


# ADK용 Cisco AI Defense 플러그인

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[Cisco AI
Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html)는
프롬프트 인젝션(prompt injection), 데이터 유출, 유해 콘텐츠 등의 위협으로부터 보호하기 위해 런타임 가드레일을 제공하는 엔터프라이즈 AI 보안 플랫폼입니다. [ADK
플러그인](https://github.com/cisco-ai-defense/ai-defense-google-adk)은 이러한 가드레일을 ADK `Runner` 라이프사이클에 직접 통합합니다. 프롬프트, 모델 응답, 도구 호출을 검사한 뒤 설정 가능한 보안 정책에 따라 허용하거나 차단합니다.

## 사용 사례

- **모델 호출을 위한 런타임 보호**: 모델 호출 전 사용자 프롬프트와 생성 후 모델 출력을 검사한 뒤 정책(`monitor` 또는 `enforce`)에 따라 허용하거나 차단합니다.
- **도구 및 MCP 호출 검사**: 실행 전 도구 호출 요청과 실행 후 도구 응답을 검사하고, `enforce` 모드에서는 명확한 메타데이터와 함께 안전하지 않은 도구 동작을 차단합니다.
- **감사 가능한 결정 추적 및 알림**: 결정 컨텍스트(조치, 심각도, 분류, `request_id`/`event_id`)를 기록하고, 선택적으로 모니터링 및 인시던트 대응을 위한 `on_violation` 콜백을 트리거합니다.

## 사전 요구사항

- [Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html) 계정 및 API 키
- Python >= 3.10
- [ADK](https://adk.dev) >= 1.0.0

## 설치

```bash
pip install cisco-aidefense-google-adk
```

`AI_DEFENSE_API_KEY` 환경 변수(및 도구 검사용 `AI_DEFENSE_MCP_API_KEY`)를 설정합니다.

## 에이전트와 함께 사용

### 빠른 시작

단 한 줄의 코드로 ADK 에이전트에 Cisco AI Defense를 추가할 수 있습니다:

```python
from google.adk.apps import App

from aidefense_google_adk import defend

agent = defend(agent, mode="enforce")
```

또는 전체 앱용 플러그인을 생성할 수도 있습니다:

```python
from google.adk.apps import App

from aidefense_google_adk import defend

plugin = defend(mode="enforce")
app = App(name="my_app", root_agent=agent, plugins=[plugin])
```

### 전역 플러그인

`CiscoAIDefensePlugin`을 사용하여 `Runner` 내의 모든 에이전트에 전역으로 검사를 적용합니다:

```python
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from aidefense_google_adk import CiscoAIDefensePlugin

agent = LlmAgent(
    model="gemini-flash-latest",
    name="assistant",
    instruction="You are a helpful assistant.",
)

app = App(
    name="my_app",
    root_agent=agent,
    plugins=[
        CiscoAIDefensePlugin(mode="enforce"),
    ],
)
runner = Runner(app=app, session_service=InMemorySessionService())
```

### 에이전트별 콜백

`make_aidefense_callbacks`를 사용하여 특정 에이전트에 검사를 연결합니다.

```python
from google.adk.agents import LlmAgent
from aidefense_google_adk import make_aidefense_callbacks

cbs = make_aidefense_callbacks(mode="enforce")

agent = LlmAgent(
    model="gemini-flash-latest",
    name="assistant",
    instruction="You are a helpful assistant.",
)
cbs.apply_to(agent)  # wires all 4 callbacks
```

## 모드

플러그인은 세 가지 작동 모드를 지원합니다:

모드 | 동작
---- | --------
`monitor` | 모든 트래픽을 검사하고 위반 사항을 로깅하며 차단하지 않음 (기본값)
`enforce` | 모든 트래픽을 검사하고 정책을 위반하는 요청/응답을 차단함
`off` | 검사를 완전히 건너뜀

모드는 전역으로 설정하거나 채널별로 설정할 수 있습니다:

```python
CiscoAIDefensePlugin(
    mode="monitor",      # default for both
    llm_mode="enforce",  # override for LLM only
    mcp_mode="off",      # override for tools only
)
```

## 위반 콜백

`on_violation` 콜백을 사용하면 `monitor` 및 `enforce` 모드 모두에서 모든 정책 위반에 대한 알림을 받을 수 있습니다:

```python
def handle_violation(result):
    print(f"Violation: {result.action} / {result.severity}")

CiscoAIDefensePlugin(
    mode="monitor",
    on_violation=handle_violation,
)
```

## 재시도 및 페일오픈 지원

지수 백오프를 사용한 자동 재시도, 페일오픈(fail-open)/페일클로즈(fail-closed) 동작 방식, 구조화된 `Decision` 객체가 필요한 경우 `AgentsecPlugin` 변형을 사용하세요:

```python
from google.adk.apps import App

from aidefense_google_adk import AgentsecPlugin

app = App(
    name="my_app",
    root_agent=agent,
    plugins=[
        AgentsecPlugin(
            mode="enforce",
            fail_open=True,
            retry_total=3,
            retry_backoff=0.5,
        ),
    ],
)
```

또는 에이전트별 수준에서:

```python
from aidefense_google_adk import make_agentsec_callbacks

cbs = make_agentsec_callbacks(mode="enforce", fail_open=True)
cbs.apply_to(agent)
```

## 추가 리소스

- [GitHub Repository](https://github.com/cisco-ai-defense/ai-defense-google-adk)
- [PyPI Package](https://pypi.org/project/cisco-aidefense-google-adk/)
- [Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html)
- [cisco-aidefense-sdk on PyPI](https://pypi.org/project/cisco-aidefense-sdk/)
