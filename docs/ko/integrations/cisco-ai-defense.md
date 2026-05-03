---
catalog_title: Cisco AI Defense
catalog_description: 에이전트 프롬프트 및 도구 호출을 모니터링하거나 차단하는 보안 가드레일
catalog_icon: /integrations/assets/cisco-ai-defense.png
---


# ADK용 Cisco AI Defense 플러그인

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Cisco AI
Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html)
런타임 가드레일을 제공하는 엔터프라이즈 AI 보안 플랫폼입니다.
신속한 주입, 데이터 유출, 유해한 위협 등으로부터 보호
내용. [ADK
plugin](https://github.com/cisco-ai-defense/ai-defense-google-adk)는 통합
이러한 가드레일은 ADK Runner 라이프사이클에 직접적으로 포함됩니다. 프롬프트를 검사하고,
모델 응답 및 도구 호출을 수행한 다음 구성 가능한 항목에 따라 이를 허용하거나 차단합니다.
보안 정책.

## 사용 사례

- **모델 호출을 위한 런타임 보호**: 모델 이전에 사용자 프롬프트를 검사합니다.
  생성 후 호출 및 모델 출력을 수행한 다음 정책에 따라 허용하거나 차단합니다.
  (`monitor` 또는 `enforce`).
- **도구 및 MCP 호출 검사**: 실행 전 도구 호출 요청을 검사합니다.
  실행 후 도구 응답을 확인하고 안전하지 않은 도구 동작을 차단합니다.
  명확한 메타데이터가 포함된 `enforce` 모드.
- **감사 가능한 결정 추적 및 경고**: 결정 컨텍스트 캡처(작업,
  심각도, 분류, request_id/event_id)를 선택하고 선택적으로
  모니터링 및 사고 대응을 위한 `on_violation` 콜백.

## 전제조건

- [Cisco AI Defense](https://www.cisco.com/site/us/en/products/security/ai-defense/index.html) 계정 및 API 키
- 파이썬 >= 3.10
- [ADK](https://adk.dev) >= 1.0.0

## 설치

```bash
pip install cisco-aidefense-google-adk
```

`AI_DEFENSE_API_KEY` 환경 변수(및 `AI_DEFENSE_MCP_API_KEY`)를 설정합니다.
도구 검사용).

## 에이전트와 함께 사용

### 빠른 시작

한 줄로 Cisco AI Defense를 ADK 에이전트에 추가합니다.

```python
from aidefense_google_adk import defend

agent = defend(agent, mode="enforce")
```

또는 전체 앱용 플러그인을 다운로드하세요.

```python
from aidefense_google_adk import defend

plugin = defend(mode="enforce")
app = App(name="my_app", root_agent=agent, plugins=[plugin])
```

### 글로벌 플러그인

`CiscoAIDefensePlugin`를 사용하여 모든 에이전트에 전역적으로 검사를 적용합니다.
주자:

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

플러그인은 세 가지 작동 모드를 지원합니다.

모드 | 행동
---- | --------
`monitor` | 모든 트래픽 검사, 위반 기록, 차단 안 함(기본값)
`enforce` | 모든 트래픽을 검사하고, 정책을 위반하는 요청/응답을 차단합니다.
`off` | 검사를 완전히 건너뛰세요

모드는 전역적으로 또는 채널별로 설정할 수 있습니다.

```python
CiscoAIDefensePlugin(
    mode="monitor",      # default for both
    llm_mode="enforce",  # override for LLM only
    mcp_mode="off",      # override for tools only
)
```

## 위반 콜백

`on_violation` 콜백을 사용하여 모든 위반에 대한 알림을 받습니다.
`monitor` 및 `enforce` 모드 모두:

```python
def handle_violation(result):
    print(f"Violation: {result.action} / {result.severity}")

CiscoAIDefensePlugin(
    mode="monitor",
    on_violation=handle_violation,
)
```

## 재시도 및 페일오픈 지원

지수 백오프를 사용한 자동 재시도의 경우 페일오픈/페일클로즈 의미론,
구조화된 `Decision` 객체의 경우 `AgentsecPlugin` 변형을 사용합니다.

```python
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
