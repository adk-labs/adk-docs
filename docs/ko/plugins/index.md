# 플러그인

<div class="language-support-tag">
    <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v1.7.0</span>
</div>

ADK(Agent Development Kit)의 플러그인은 콜백 후크를 사용하여 에이전트 워크플로 수명 주기의 다양한 단계에서 실행될 수 있는 사용자 지정 코드 모듈입니다. 플러그인은 에이전트 워크플로 전반에 걸쳐 적용되는 기능에 사용합니다. 플러그인의 일반적인 애플리케이션은 다음과 같습니다.

-   **로깅 및 추적**: 디버깅 및 성능 분석을 위해 에이전트, 도구 및 생성형 AI 모델 활동에 대한 자세한 로그를 생성합니다.
-   **정책 적용**: 특정 도구를 사용할 권한이 있는지 확인하고 권한이 없는 경우 실행을 방지하는 함수와 같은 보안 보호 장치를 구현합니다.
-   **모니터링 및 측정 항목**: Prometheus 또는 [Google Cloud Observability](https://cloud.google.com/stackdriver/docs) (이전 Stackdriver)와 같은 모니터링 시스템에 토큰 사용량, 실행 시간 및 호출 횟수에 대한 측정 항목을 수집하고 내보냅니다.
-   **응답 캐싱**: 요청이 이전에 이루어졌는지 확인하여 비용이 많이 들거나 시간이 오래 걸리는 AI 모델 또는 도구 호출을 건너뛰고 캐시된 응답을 반환할 수 있습니다.
-   **요청 또는 응답 수정**: AI 모델 프롬프트에 정보를 동적으로 추가하거나 도구 출력 응답을 표준화합니다.

!!! tip "팁: 안전 기능에는 플러그인 사용"
    보안 가드레일과 정책을 구현할 때는 콜백보다 모듈성과 유연성이 높은 ADK 플러그인을 사용하는 것이 좋습니다. 자세한 내용은 [보안 가드레일을 위한 콜백 및 플러그인](/adk-docs/ko/safety/#callbacks-and-plugins-for-security-guardrails)을 참조하세요.

!!! tip "팁: ADK 통합"
    ADK용 사전 구축 플러그인 및 기타 통합 목록은 [도구 및 통합](/adk-docs/ko/integrations/)을 참조하세요.

## 플러그인은 어떻게 작동합니까?

ADK 플러그인은 `BasePlugin` 클래스를 확장하며 에이전트 수명 주기에서 플러그인이 실행되어야 하는 위치를 나타내는 하나 이상의 `callback` 메서드를 포함합니다. 에이전트의 `Runner` 클래스에 플러그인을 등록하여 에이전트에 통합합니다. 에이전트 애플리케이션에서 플러그인을 트리거할 수 있는 방법과 위치에 대한 자세한 내용은 [플러그인 콜백 후크](#plugin-callback-hooks)를 참조하십시오.

플러그인 기능은 ADK의 확장 가능한 아키텍처의 핵심 설계 요소인 [콜백](../callbacks/index.md)을 기반으로 합니다. 일반적인 에이전트 콜백은 *특정 작업*을 위해 *단일 에이전트, 단일 도구*에 구성되는 반면, 플러그인은 `Runner`에 *한 번* 등록되며 해당 콜백은 해당 러너가 관리하는 모든 에이전트, 도구 및 LLM 호출에 *전역적으로* 적용됩니다. 플러그인을 사용하면 관련 콜백 함수를 함께 묶어 워크플로 전체에서 사용할 수 있습니다. 따라서 플러그인은 전체 에이전트 애플리케이션에 걸쳐 있는 기능을 구현하는 데 이상적인 솔루션입니다.

## 사전 빌드된 플러그인

ADK에는 에이전트 워크플로에 즉시 추가할 수 있는 여러 플러그인이 포함되어 있습니다.

*   [**반영 및 재시도 도구**](/adk-docs/ko/plugins/reflect-and-retry/):
    도구 실패를 추적하고 도구 요청을 지능적으로 재시도합니다.
*   [**BigQuery 분석**](/adk-docs/ko/observability/bigquery-agent-analytics/):
    BigQuery를 사용하여 에이전트 로깅 및 분석을 활성화합니다.
*   [**컨텍스트 필터**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/context_filter_plugin.py):
    생성형 AI 컨텍스트를 필터링하여 크기를 줄입니다.
*   [**전역 지침**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/global_instruction_plugin.py):
    앱 수준에서 전역 지침 기능을 제공하는 플러그인입니다.
*   [**아티팩트로 파일 저장**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/save_files_as_artifacts_plugin.py):
    사용자 메시지에 포함된 파일을 아티팩트로 저장합니다.
*   [**로깅**](https://github.com/google/adk-python/blame/main/src/google/adk/plugins/logging_plugin.py):
    각 에이전트 워크플로 콜백 지점에서 중요한 정보를 로깅합니다.

## 플러그인 정의 및 등록

이 섹션에서는 플러그인 클래스를 정의하고 에이전트 워크플로의 일부로 등록하는 방법을 설명합니다. 완전한 코드 예시는 저장소의 [플러그인 기본](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_basic)을 참조하십시오.

### 플러그인 클래스 생성

`BasePlugin` 클래스를 확장하고 다음 코드 예시에 표시된 대로 하나 이상의 `callback` 메서드를 추가하여 시작합니다.

```py title="count_plugin.py"
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin

class CountInvocationPlugin(BasePlugin):
  """에이전트 및 도구 호출 횟수를 계산하는 사용자 지정 플러그인입니다."""

  def __init__(self) -> None:
    """카운터로 플러그인을 초기화합니다."""
    super().__init__(name="count_invocation")
    self.agent_count: int = 0
    self.tool_count: int = 0
    self.llm_request_count: int = 0

  async def before_agent_callback(
      self, *, agent: BaseAgent, callback_context: CallbackContext
  ) -> None:
    """에이전트 실행 횟수를 계산합니다."""
    self.agent_count += 1
    print(f"[Plugin] Agent run count: {self.agent_count}")

  async def before_model_callback(
      self, *, callback_context: CallbackContext, llm_request: LlmRequest
  ) -> None:
    """LLM 요청 횟수를 계산합니다."""
    self.llm_request_count += 1
    print(f"[Plugin] LLM request count: {self.llm_request_count}")
```

이 예시 코드는 에이전트 수명 주기 동안 이러한 작업의 실행 횟수를 계산하기 위해 `before_agent_callback` 및 `before_model_callback`에 대한 콜백을 구현합니다.

### 플러그인 클래스 등록

`plugins` 매개변수를 사용하여 에이전트 초기화 시 `Runner` 클래스의 일부로 플러그인 클래스를 등록하여 통합합니다. 이 매개변수로 여러 플러그인을 지정할 수 있습니다. 다음 코드 예시는 이전 섹션에서 정의된 `CountInvocationPlugin` 플러그인을 간단한 ADK 에이전트에 등록하는 방법을 보여줍니다.

```py
from google.adk.runners import InMemoryRunner
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import asyncio

# 플러그인 가져오기.
from .count_plugin import CountInvocationPlugin

async def hello_world(tool_context: ToolContext, query: str):
  print(f'Hello world: query is [{query}]')

root_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world',
    description='사용자 쿼리로 헬로월드를 출력합니다.',
    instruction="""헬로월드 도구를 사용하여 헬로월드와 사용자 쿼리를 출력하십시오.
    """,
    tools=[hello_world],
)

async def main():
  """에이전트의 메인 진입점입니다."""
  prompt = 'hello world'
  runner = InMemoryRunner(
      agent=root_agent,
      app_name='test_app_with_plugin',

      # 여기에 플러그인을 추가합니다. 여러 플러그인을 추가할 수 있습니다.
      plugins=[CountInvocationPlugin()],
  )

  # 나머지는 일반 ADK 러너를 시작하는 것과 동일합니다.
  session = await runner.session_service.create_session(
      user_id='user',
      app_name='test_app_with_plugin',
  )

  async for event in runner.run_async(
      user_id='user',
      session_id=session.id,
      new_message=types.Content(
        role='user', parts=[types.Part.from_text(text=prompt)]
      )
  ):
    print(f'** {event.author}로부터 이벤트를 받았습니다.')

if __name__ == "__main__":
  asyncio.run(main())
```

### 플러그인으로 에이전트 실행

평소처럼 플러그인을 실행합니다. 다음은 명령줄을 실행하는 방법을 보여줍니다.

```sh
python3 -m path.to.main
```

플러그인은 [ADK 웹 인터페이스](../evaluate/#1-adk-web-run-evaluations-via-the-web-ui)에서 지원되지 않습니다. ADK 워크플로에서 플러그인을 사용하는 경우 웹 인터페이스 없이 워크플로를 실행해야 합니다.

이전에 설명한 에이전트의 출력은 다음과 비슷해야 합니다.

```log
[Plugin] Agent run count: 1
[Plugin] LLM request count: 1
** Got event from hello_world
Hello world: query is [hello world]
** Got event from hello_world
[Plugin] LLM request count: 2
** Got event from hello_world
```


ADK 에이전트 실행에 대한 자세한 내용은 [빠른 시작](/adk-docs/ko/get-started/quickstart/#run-your-agent) 가이드를 참조하세요.

## 플러그인으로 워크플로 빌드

플러그인 콜백 후크는 에이전트의 실행 수명 주기를 가로채고, 수정하고, 심지어 제어하는 ​​논리를 구현하기 위한 메커니즘입니다. 각 후크는 플러그인 클래스에서 구현할 수 있는 특정 메서드로, 중요한 순간에 코드를 실행할 수 있습니다. 후크의 반환 값에 따라 두 가지 작동 모드 중에서 선택할 수 있습니다.

-   **관찰**: 반환 값이 없는 후크(`None`)를 구현합니다. 이 접근 방식은 로깅 또는 측정 항목 수집과 같은 작업에 사용되며, 에이전트 워크플로가 중단 없이 다음 단계로 진행되도록 합니다. 예를 들어, 플러그인의 `after_tool_callback`을 사용하여 디버깅을 위해 모든 도구의 결과를 로깅할 수 있습니다.
-   **개입**: 후크를 구현하고 값을 반환합니다. 이 접근 방식은 워크플로를 단락시킵니다. `Runner`는 처리를 중단하고, 후속 플러그인과 모델 호출과 같은 원래 의도된 작업을 건너뛰고, 플러그인 콜백의 반환 값을 결과로 사용합니다. 일반적인 사용 사례는 캐시된 `LlmResponse`를 반환하도록 `before_model_callback`을 구현하여 중복되고 비용이 많이 드는 API 호출을 방지하는 것입니다.
-   **수정**: 후크를 구현하고 컨텍스트 객체를 수정합니다. 이 접근 방식은 해당 모듈의 실행을 방해하지 않고 실행될 모듈의 컨텍스트 데이터를 수정할 수 있도록 합니다. 예를 들어, 모델 객체 실행을 위한 추가 표준화된 프롬프트 텍스트를 추가하는 것입니다.

**주의:** 플러그인 콜백 함수는 객체 수준에서 구현된 콜백보다 우선합니다. 이 동작은 플러그인 수준 콜백 코드가 에이전트, 모델 또는 도구 객체 콜백이 실행되기 *전에* 실행됨을 의미합니다. 또한 플러그인 수준 에이전트 콜백이 비어 있지 않은(`None`이 아닌) 응답을 반환하면 에이전트, 모델 또는 도구 수준 콜백은 *실행되지 않습니다* (건너뜀).

플러그인 설계는 코드 실행 계층 구조를 설정하고 전역 관심사를 로컬 에이전트 논리에서 분리합니다. 플러그인은 `PerformanceMonitoringPlugin`과 같이 빌드하는 상태 저장 *모듈*인 반면, 콜백 후크는 해당 모듈 내에서 실행되는 특정 *함수*입니다. 이 아키텍처는 다음과 같은 중요한 방식으로 표준 에이전트 콜백과 근본적으로 다릅니다.

-   **범위**: 플러그인 후크는 *전역적*입니다. `Runner`에 플러그인을 한 번 등록하면 해당 후크는 관리하는 모든 에이전트, 모델 및 도구에 보편적으로 적용됩니다. 대조적으로 에이전트 콜백은 *로컬*이며 특정 에이전트 인스턴스에 개별적으로 구성됩니다.
-   **실행 순서**: 플러그인이 *우선*합니다. 주어진 이벤트에 대해 플러그인 후크는 항상 해당 에이전트 콜백보다 먼저 실행됩니다. 이 시스템 동작은 플러그인을 보안 정책, 범용 캐싱 및 전체 애플리케이션에 걸친 일관된 로깅과 같은 교차 절단 기능을 구현하기 위한 올바른 아키텍처 선택으로 만듭니다.

### 에이전트 콜백 및 플러그인

이전 섹션에서 언급했듯이 플러그인과 에이전트 콜백 사이에는 기능적 유사성이 있습니다. 다음 표는 플러그인과 에이전트 콜백의 차이점을 더 자세히 비교합니다.

<table>
  <thead>
    <tr>
      <th></th>
      <th><strong>플러그인</strong></th>
      <th><strong>에이전트 콜백</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>범위</strong></td>
      <td><strong>전역</strong>: <code>Runner</code>의 모든 에이전트/도구/LLM에 적용됩니다.</td>
      <td><strong>로컬</strong>: 구성된 특정 에이전트 인스턴스에만 적용됩니다.</td>
    </tr>
    <tr>
      <td><strong>주요 사용 사례</strong></td>
      <td><strong>수평적 기능</strong>: 로깅, 정책, 모니터링, 전역 캐싱.</td>
      <td><strong>특정 에이전트 로직</strong>: 단일 에이전트의 동작 또는 상태 수정.</td>
    </tr>
    <tr>
      <td><strong>구성</strong></td>
      <td><code>Runner</code>에서 한 번 구성합니다.</td>
      <td>각 <code>BaseAgent</code> 인스턴스에서 개별적으로 구성합니다.</td>
    </tr>
    <tr>
      <td><strong>실행 순서</strong></td>
      <td>플러그인 콜백은 에이전트 콜백 <strong>전에</strong> 실행됩니다.</td>
      <td>에이전트 콜백은 플러그인 콜백 <strong>후에</strong> 실행됩니다.</td>
    </tr>
  </tbody>
</table>

## 플러그인 콜백 후크

플러그인 클래스에서 정의할 콜백 함수를 사용하여 플러그인이 호출되는 시기를 정의합니다. 콜백은 사용자 메시지가 수신될 때, `Runner`, `Agent`, `Model` 또는 `Tool`이 호출되기 전후, `이벤트`에 대해, 그리고 `Model` 또는 `Tool` 오류가 발생할 때 사용할 수 있습니다. 이러한 콜백은 에이전트, 모델 및 도구 클래스 내에 정의된 모든 콜백을 포함하며 우선합니다.

다음 다이어그램은 에이전트 워크플로 중에 플러그인 기능을 연결하고 실행할 수 있는 콜백 지점을 보여줍니다.

![ADK 플러그인 콜백 후크](../assets/workflow-plugin-hooks.svg)
**그림 1.** 플러그인 콜백 후크 위치를 포함한 ADK 에이전트 워크플로 다이어그램.

다음 섹션에서는 플러그인에 사용할 수 있는 콜백 후크에 대해 더 자세히 설명합니다.

-   [사용자 메시지 콜백](#user-message-callbacks)
-   [러너 시작 콜백](#runner-start-callbacks)
-   [에이전트 실행 콜백](#agent-execution-callbacks)
-   [모델 콜백](#model-callbacks)
-   [도구 콜백](#tool-callbacks)
-   [러너 종료 콜백](#runner-end-callbacks)

### 사용자 메시지 콜백

*사용자 메시지* 콜백(`on_user_message_callback`)은 사용자가 메시지를 보낼 때 발생합니다. `on_user_message_callback`은 실행되는 첫 번째 후크로, 초기 입력을 검사하거나 수정할 기회를 제공합니다.

-   **실행 시점:** `runner.run()` 직후, 다른 처리 이전에 발생합니다.
-   **목적:** 사용자의 원시 입력을 검사하거나 수정하는 첫 번째 기회입니다.
-   **흐름 제어:** 사용자 원본 메시지를 **대체**할 `types.Content` 객체를 반환합니다.

다음 코드 예시는 이 콜백의 기본 구문을 보여줍니다.

```py
async def on_user_message_callback(
    self,
    *,
    invocation_context: InvocationContext,
    user_message: types.Content,
) -> Optional[types.Content]:
```

### 러너 시작 콜백

*러너 시작* 콜백(`before_run_callback`)은 `Runner` 객체가 잠재적으로 수정된 사용자 메시지를 받아 실행을 준비할 때 발생합니다. `before_run_callback`은 여기서 실행되어 에이전트 로직이 시작되기 전에 전역 설정을 허용합니다.

-   **실행 시점:** `runner.run()`이 호출된 직후, 다른 처리 이전에 발생합니다.
-   **목적:** 사용자의 원시 입력을 검사하거나 수정하는 첫 번째 기회입니다.
-   **흐름 제어:** 사용자 원본 메시지를 **대체**할 `types.Content` 객체를 반환합니다.

다음 코드 예시는 이 콜백의 기본 구문을 보여줍니다.

```py
async def before_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[types.Content]:
```

### 에이전트 실행 콜백

*에이전트 실행* 콜백(`before_agent`, `after_agent`)은 `Runner` 객체가 에이전트를 호출할 때 발생합니다. `before_agent_callback`은 에이전트의 주요 작업이 시작되기 직전에 실행됩니다. 주요 작업은 모델 또는 도구 호출을 포함할 수 있는 요청 처리의 전체 에이전트 프로세스를 포괄합니다. 에이전트가 모든 단계를 완료하고 결과를 준비한 후 `after_agent_callback`이 실행됩니다.

**주의:** 이러한 콜백을 구현하는 플러그인은 에이전트 수준 콜백이 실행되기 *전에* 실행됩니다. 또한 플러그인 수준 에이전트 콜백이 `None` 또는 null 응답 이외의 다른 값을 반환하면 에이전트 수준 콜백은 *실행되지 않습니다* (건너뜀).

에이전트 객체의 일부로 정의된 에이전트 콜백에 대한 자세한 내용은 [콜백 유형](../callbacks/types-of-callbacks.md#agent-lifecycle-callbacks)을 참조하십시오.

### 모델 콜백

모델 콜백 **(`before_model`, `after_model`, `on_model_error`)**은 모델 객체가 실행되기 전후에 발생합니다. 플러그인 기능은 아래에 자세히 설명된 대로 오류 발생 시 콜백도 지원합니다.

-   에이전트가 AI 모델을 호출해야 하는 경우 `before_model_callback`이 먼저 실행됩니다.
-   모델 호출이 성공하면 `after_model_callback`이 다음으로 실행됩니다.
-   모델 호출이 예외와 함께 실패하면 `on_model_error_callback`이 대신 트리거되어 정상적인 복구를 허용합니다.

**주의:** **`before_model`** 및 **`after_model`** 콜백 메서드를 구현하는 플러그인은 모델 수준 콜백이 실행되기 *전에* 실행됩니다. 또한 플러그인 수준 모델 콜백이 `None` 또는 null 응답 이외의 다른 값을 반환하면 모델 수준 콜백은 *실행되지 않습니다* (건너뜀).

#### 모델 오류 시 콜백 세부 정보

모델 객체에 대한 오류 시 콜백은 플러그인 기능에서만 지원되며 다음과 같이 작동합니다.

-   **실행 시점:** 모델 호출 중에 예외가 발생할 때.
-   **일반적인 사용 사례:** 정상적인 오류 처리, 특정 오류 로깅 또는 "AI 서비스는 현재 사용할 수 없습니다."와 같은 대체 응답 반환.
-   **흐름 제어:**
    -   `LlmResponse` 객체를 반환하여 **예외를 억제**하고 대체 결과를 제공합니다.
    -   `None`을 반환하여 원래 예외가 발생하도록 허용합니다.

**참고**: 모델 객체의 실행이 `LlmResponse`를 반환하면 시스템은 실행 흐름을 재개하고 `after_model_callback`이 정상적으로 트리거됩니다.****

다음 코드 예시는 이 콜백의 기본 구문을 보여줍니다.

```py
async def on_model_error_callback(
    self,
    *,
    callback_context: CallbackContext,
    llm_request: LlmRequest,
    error: Exception,
) -> Optional[LlmResponse]:
```

### 도구 콜백

플러그인에 대한 도구 콜백 **(`before_tool`, `after_tool`, `on_tool_error`)**은 도구 실행 전후 또는 오류 발생 시 발생합니다. 플러그인 기능은 아래에 자세히 설명된 대로 오류 발생 시 콜백도 지원합니다.

-   에이전트가 도구를 실행하면 `before_tool_callback`이 먼저 실행됩니다.
-   도구가 성공적으로 실행되면 `after_tool_callback`이 다음으로 실행됩니다.
-   도구가 예외를 발생시키면 `on_tool_error_callback`이 대신 트리거되어 실패를 처리할 기회를 제공합니다. `on_tool_error_callback`이 dict를 반환하면 `after_tool_callback`이 정상적으로 트리거됩니다.

**주의:** 이러한 콜백을 구현하는 플러그인은 도구 수준 콜백이 실행되기 *전에* 실행됩니다. 또한 플러그인 수준 도구 콜백이 `None` 또는 null 응답 이외의 다른 값을 반환하면 도구 수준 콜백은 *실행되지 않습니다* (건너뜀).

#### 도구 오류 시 콜백 세부 정보

도구 객체에 대한 오류 시 콜백은 플러그인 기능에서만 지원되며 다음과 같이 작동합니다.

-   **실행 시점:** 도구의 `run` 메서드 실행 중에 예외가 발생할 때.
-   **목적:** 특정 도구 예외(`APIError`와 같은)를 포착하고, 실패를 로깅하고, LLM에 사용자 친화적인 오류 메시지를 다시 제공합니다.
-   **흐름 제어:** `dict`를 반환하여 **예외를 억제**하고 대체 결과를 제공합니다. `None`을 반환하여 원래 예외가 발생하도록 허용합니다.

**참고**: `dict`를 반환하면 실행 흐름이 재개되고 `after_tool_callback`이 정상적으로 트리거됩니다.

다음 코드 예시는 이 콜백의 기본 구문을 보여줍니다.

```py
async def on_tool_error_callback(
    self,
    *,
    tool: BaseTool,
    tool_args: dict[str, Any],
    tool_context: ToolContext,
    error: Exception,
) -> Optional[dict]:
```

### 이벤트 콜백

*이벤트 콜백*(`on_event_callback`)은 에이전트가 텍스트 응답 또는 도구 호출 결과와 같은 출력을 생성할 때 `Event` 객체로 출력할 때 발생합니다. `on_event_callback`은 각 이벤트에 대해 실행되어 클라이언트에 스트리밍되기 전에 이벤트를 수정할 수 있도록 합니다.

-   **실행 시점:** 에이전트가 `Event`를 생성한 후 사용자에게 보내기 전에. 에이전트 실행은 여러 이벤트를 생성할 수 있습니다.
-   **목적:** 이벤트 수정 또는 보강(예: 메타데이터 추가) 또는 특정 이벤트에 따라 부작용 트리거에 유용합니다.
-   **흐름 제어:** 원본 이벤트를 **대체**할 `Event` 객체를 반환합니다.

다음 코드 예시는 이 콜백의 기본 구문을 보여줍니다.

```py
async def on_event_callback(
    self, *, invocation_context: InvocationContext, event: Event
) -> Optional[Event]:
```

### 러너 종료 콜백

*러너 종료* 콜백 **(`after_run_callback`)**은 에이전트가 전체 프로세스를 완료하고 모든 이벤트가 처리되면 `Runner`가 실행을 완료할 때 발생합니다. `after_run_callback`은 정리 및 최종 보고에 완벽한 최종 후크입니다.

-   **실행 시점:** `Runner`가 요청 실행을 완전히 완료한 후.
-   **목적:** 연결 닫기 또는 로그 및 측정 항목 데이터 최종화와 같은 전역 정리 작업에 이상적입니다.
-   **흐름 제어:** 이 콜백은 해체 전용이며 최종 결과를 변경할 수 없습니다.

다음 코드 예시는 이 콜백의 기본 구문을 보여줍니다.

```py
async def after_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[None]:
```

## 다음 단계

ADK 프로젝트에 플러그인을 개발하고 적용하기 위한 다음 리소스를 확인하십시오.

-   더 많은 ADK 플러그인 코드 예시는 [ADK Python 저장소](https://github.com/google/adk-python/tree/main/src/google/adk/plugins)를 참조하십시오.
-   보안 목적으로 플러그인을 적용하는 방법에 대한 정보는 [보안 가드레일을 위한 콜백 및 플러그인](/adk-docs/ko/safety/#callbacks-and-plugins-for-security-guardrails)을 참조하십시오.
