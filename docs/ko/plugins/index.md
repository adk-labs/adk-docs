# 플러그인

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.7.0</span>
</div>

에이전트 개발 키트(ADK)의 플러그인은 콜백 후크를 사용하여 에이전트 워크플로 수명 주기의 다양한 단계에서 실행할 수 있는 사용자 지정 코드 모듈입니다. 에이전트 워크플로 전반에 적용할 수 있는 기능에 플러그인을 사용합니다. 플러그인의 일반적인 응용 프로그램은 다음과 같습니다.

-   **로깅 및 추적**: 디버깅 및 성능 분석을 위해 에이전트, 도구 및 생성 AI 모델 활동의 자세한 로그를 만듭니다.
-   **정책 시행**: 사용자가 특정 도구를 사용할 권한이 있는지 확인하고 권한이 없는 경우 실행을 방지하는 함수와 같은 보안 가드레일을 구현합니다.
-   **모니터링 및 메트릭**: 토큰 사용량, 실행 시간 및 호출 횟수에 대한 메트릭을 수집하고 Prometheus 또는 [Google Cloud Observability](https://cloud.google.com/stackdriver/docs)(이전 Stackdriver)와 같은 모니터링 시스템으로 내보냅니다.
-   **응답 캐싱**: 이전에 요청이 있었는지 확인하여 비용이 많이 들거나 시간이 많이 걸리는 AI 모델 또는 도구 호출을 건너뛰고 캐시된 응답을 반환할 수 있습니다.
-   **요청 또는 응답 수정**: AI 모델 프롬프트에 정보를 동적으로 추가하거나 도구 출력 응답을 표준화합니다.

!!! tip
    보안 가드레일 및 정책을 구현할 때 콜백보다 모듈성과 유연성이 뛰어난 ADK 플러그인을 사용하십시오. 자세한 내용은 [보안 가드레일을 위한 콜백 및 플러그인](/adk-docs/safety/#callbacks-and-plugins-for-security-guardrails)을 참조하십시오.

!!! warning "주의"
    플러그인은 [ADK 웹 인터페이스](../evaluate/#1-adk-web-run-evaluations-via-the-web-ui)에서 지원되지 않습니다. ADK 워크플로에서 플러그인을 사용하는 경우 웹 인터페이스 없이 워크플로를 실행해야 합니다.

## 플러그인은 어떻게 작동합니까?

ADK 플러그인은 `BasePlugin` 클래스를 확장하고 에이전트 수명 주기에서 플러그인을 실행해야 하는 위치를 나타내는 하나 이상의 `callback` 메서드를 포함합니다. 에이전트의 `Runner` 클래스에 플러그인을 등록하여 에이전트에 플러그인을 통합합니다. 에이전트 애플리케이션에서 플러그인을 트리거할 수 있는 방법과 위치에 대한 자세한 내용은 [플러그인 콜백 후크](#plugin-callback-hooks)를 참조하십시오.

플러그인 기능은 ADK의 확장 가능한 아키텍처의 핵심 설계 요소인 [콜백](../callbacks/)을 기반으로 합니다. 일반적인 에이전트 콜백은 *특정 작업*에 대해 *단일 에이전트, 단일 도구*에 구성되지만 플러그인은 `Runner`에 *한 번* 등록되며 해당 콜백은 해당 실행기에서 관리하는 모든 에이전트, 도구 및 LLM 호출에 *전역적으로* 적용됩니다. 플러그인을 사용하면 관련 콜백 함수를 함께 패키징하여 워크플로 전체에서 사용할 수 있습니다. 따라서 플러그인은 전체 에이전트 애플리케이션에 걸쳐 있는 기능을 구현하는 데 이상적인 솔루션입니다.

## 사전 빌드된 플러그인

ADK에는 에이전트 워크플로에 즉시 추가할 수 있는 여러 플러그인이 포함되어 있습니다.

*   [**반영 및 재시도 도구**](/adk-docs/plugins/reflect-and-retry/): 도구 오류를 추적하고 도구 요청을 지능적으로 재시도합니다.
*   [**BigQuery 로깅**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/bigquery_logging_plugin.py): BigQuery를 사용하여 에이전트 로깅 및 분석을 활성화합니다.
*   [**컨텍스트 필터**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/context_filter_plugin.py): 생성 AI 컨텍스트를 필터링하여 크기를 줄입니다.
*   [**전역 지침**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/global_instruction_plugin.py): 앱 수준에서 전역 지침 기능을 제공하는 플러그인입니다.
*   [**파일을 아티팩트로 저장**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/save_files_as_artifacts_plugin.py): 사용자 메시지에 포함된 파일을 아티팩트로 저장합니다.
*   [**로깅**](https://github.com/google/adk-python/blame/main/src/google/adk/plugins/logging_plugin.py): 각 에이전트 워크플로 콜백 지점에서 중요한 정보를 기록합니다.

## 플러그인 정의 및 등록

이 섹션에서는 플러그인 클래스를 정의하고 에이전트 워크플로의 일부로 등록하는 방법을 설명합니다. 전체 코드 예제는 리포지토리의 [플러그인 기본](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_basic)을 참조하십시오.

### 플러그인 클래스 만들기

다음 코드 예제와 같이 `BasePlugin` 클래스를 확장하고 하나 이상의 `callback` 메서드를 추가하여 시작합니다.

```py title="count_plugin.py"
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin

class CountInvocationPlugin(BasePlugin):
  """에이전트 및 도구 호출을 계산하는 사용자 지정 플러그인입니다."""

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
    print(f"[플러그인] 에이전트 실행 횟수: {self.agent_count}")

  async def before_model_callback(
      self, *, callback_context: CallbackContext, llm_request: LlmRequest
  ) -> None:
    """LLM 요청 횟수를 계산합니다."""
    self.llm_request_count += 1
    print(f"[플러그인] LLM 요청 횟수: {self.llm_request_count}")
```

이 예제 코드는 에이전트 수명 주기 동안 이러한 작업의 실행을 계산하기 위해 `before_agent_callback` 및 `before_model_callback`에 대한 콜백을 구현합니다.

### 플러그인 클래스 등록

`plugins` 매개변수를 사용하여 `Runner` 클래스의 일부로 에이전트 초기화 중에 플러그인 클래스를 등록하여 통합합니다. 이 매개변수를 사용하여 여러 플러그인을 지정할 수 있습니다. 다음 코드 예제는 이전 섹션에서 정의한 `CountInvocationPlugin` 플러그인을 간단한 ADK 에이전트에 등록하는 방법을 보여줍니다.

```py
from google.adk.runners import InMemoryRunner
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import asyncio

# 플러그인을 가져옵니다.
from .count_plugin import CountInvocationPlugin

async def hello_world(tool_context: ToolContext, query: str):
  print(f'Hello world: query is [{query}]')

root_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world',
    description='사용자 쿼리와 함께 hello world를 인쇄합니다.',
    instruction="""hello_world 도구를 사용하여 hello world 및 사용자 쿼리를 인쇄합니다.
    """,
    tools=[hello_world],
)

async def main():
  """에이전트의 기본 진입점입니다."""
  prompt = 'hello world'
  runner = InMemoryRunner(
      agent=root_agent,
      app_name='test_app_with_plugin',

      # 여기에 플러그인을 추가합니다. 여러 플러그인을 추가할 수 있습니다.
      plugins=[CountInvocationPlugin()],
  )

  # 나머지는 일반 ADK 실행기를 시작하는 것과 동일합니다.
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
    print(f'** {event.author}에서 이벤트를 받았습니다.')

if __name__ == "__main__":
  asyncio.run(main())
```

### 플러그인으로 에이전트 실행

일반적으로 하듯이 플러그인을 실행합니다. 다음은 명령줄을 실행하는 방법을 보여줍니다.

```sh
python3 -m path.to.main
```

플러그인은 [ADK 웹 인터페이스](../evaluate/#1-adk-web-run-evaluations-via-the-web-ui)에서 지원되지 않습니다. ADK 워크플로에서 플러그인을 사용하는 경우 웹 인터페이스 없이 워크플로를 실행해야 합니다.

이전에 설명한 에이전트의 출력은 다음과 유사해야 합니다.

```log
[플러그인] 에이전트 실행 횟수: 1
[플러그인] LLM 요청 횟수: 1
** hello_world에서 이벤트를 받았습니다.
Hello world: query is [hello world]
** hello_world에서 이벤트를 받았습니다.
[플러그인] LLM 요청 횟수: 2
** hello_world에서 이벤트를 받았습니다.
```


ADK 에이전트 실행에 대한 자세한 내용은 [빠른 시작](/adk-docs/get-started/quickstart/#run-your-agent) 가이드를 참조하십시오.

## 플러그인으로 워크플로 빌드

플러그인 콜백 후크는 에이전트의 실행 수명 주기를 가로채고 수정하고 심지어 제어하는 논리를 구현하기 위한 메커니즘입니다. 각 후크는 플러그인 클래스의 특정 메서드로, 핵심 순간에 코드를 실행하도록 구현할 수 있습니다. 후크의 반환 값을 기반으로 두 가지 작동 모드 중에서 선택할 수 있습니다.

-   **관찰:** 반환 값이 없는(`None`) 후크를 구현합니다. 이 접근 방식은 로깅 또는 메트릭 수집과 같은 작업에 사용되며, 에이전트의 워크플로가 중단 없이 다음 단계로 진행되도록 합니다. 예를 들어 플러그인에서 `after_tool_callback`을 사용하여 디버깅을 위해 모든 도구의 결과를 기록할 수 있습니다.
-   **개입:** 후크를 구현하고 값을 반환합니다. 이 접근 방식은 워크플로를 단락시킵니다. `Runner`는 처리를 중단하고 후속 플러그인과 모델 호출과 같은 원래 의도된 작업을 건너뛰고 플러그인 콜백의 반환 값을 결과로 사용합니다. 일반적인 사용 사례는 `before_model_callback`을 구현하여 캐시된 `LlmResponse`를 반환하여 중복되고 비용이 많이 드는 API 호출을 방지하는 것입니다.
-   **수정:** 후크를 구현하고 컨텍스트 객체를 수정합니다. 이 접근 방식을 사용하면 해당 모듈의 실행을 방해하지 않고 실행할 모듈의 컨텍스트 데이터를 수정할 수 있습니다. 예를 들어 모델 객체 실행을 위해 추가적인 표준화된 프롬프트 텍스트를 추가합니다.

**주의:** 플러그인 콜백 함수는 객체 수준에서 구현된 콜백보다 우선합니다. 이 동작은 모든 플러그인 콜백 코드가 에이전트, 모델 또는 도구 객체 콜백이 실행되기 *전에* 실행됨을 의미합니다. 또한 플러그인 수준 에이전트 콜백이 빈(`None`) 응답이 아닌 값을 반환하면 에이전트, 모델 또는 도구 수준 콜백은 *실행되지 않습니다*(건너뜁니다).

플러그인 디자인은 코드 실행 계층을 설정하고 전역적인 관심사를 로컬 에이전트 논리와 분리합니다. 플러그인은 `PerformanceMonitoringPlugin`과 같이 빌드하는 상태 저장 *모듈*이며, 콜백 후크는 해당 모듈 내에서 실행되는 특정 *함수*입니다. 이 아키텍처는 다음과 같은 중요한 방식으로 표준 에이전트 콜백과 근본적으로 다릅니다.

-   **범위:** 플러그인 후크는 *전역적*입니다. `Runner`에 플러그인을 한 번 등록하면 해당 후크는 관리하는 모든 에이전트, 모델 및 도구에 보편적으로 적용됩니다. 반면 에이전트 콜백은 *로컬*이며 특정 에이전트 인스턴스에 개별적으로 구성됩니다.
-   **실행 순서:** 플러그인은 *우선 순위*를 갖습니다. 특정 이벤트에 대해 플러그인 후크는 항상 해당 에이전트 콜백보다 먼저 실행됩니다. 이 시스템 동작은 플러그인을 보안 정책, 범용 캐싱 및 전체 애플리케이션에 걸친 일관된 로깅과 같은 교차 절단 기능을 구현하기 위한 올바른 아키텍처 선택으로 만듭니다.

### 에이전트 콜백 및 플러그인

이전 섹션에서 언급했듯이 플러그인과 에이전트 콜백 사이에는 몇 가지 기능적 유사점이 있습니다. 다음 표는 플러그인과 에이전트 콜백의 차이점을 자세히 비교합니다.

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
      <td><strong>기본 사용 사례</strong></td>
      <td><strong>수평적 기능</strong>: 로깅, 정책, 모니터링, 전역 캐싱.</td>
      <td><strong>특정 에이전트 논리</strong>: 단일 에이전트의 동작 또는 상태 수정.</td>
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

플러그인 클래스에서 정의할 콜백 함수를 사용하여 플러그인이 호출되는 시기를 정의합니다. 콜백은 사용자 메시지가 수신될 때, `Runner`, `Agent`, `Model` 또는 `Tool`이 호출되기 전후, `Events`에 대해, 그리고 `Model` 또는 `Tool` 오류가 발생할 때 사용할 수 있습니다. 이러한 콜백에는 에이전트, 모델 및 도구 클래스 내에 정의된 모든 콜백이 포함되며 우선합니다.

다음 다이어그램은 에이전트 워크플로 중에 플러그인 기능을 연결하고 실행할 수 있는 콜백 지점을 보여줍니다.

![ADK 플러그인 콜백 후크](../assets/workflow-plugin-hooks.svg)
**그림 1.** 플러그인 콜백 후크 위치가 있는 ADK 에이전트 워크플로 다이어그램.

다음 섹션에서는 플러그인에 사용할 수 있는 콜백 후크에 대해 자세히 설명합니다.

-   [사용자 메시지 콜백](#user-message-callbacks)
-   [실행기 시작 콜백](#runner-start-callbacks)
-   [에이전트 실행 콜백](#agent-execution-callbacks)
-   [모델 콜백](#model-callbacks)
-   [도구 콜백](#tool-callbacks)
-   [실행기 종료 콜백](#runner-end-callbacks)

### 사용자 메시지 콜백

*사용자 메시지* 콜백(`on_user_message_callback`)은 사용자가 메시지를 보낼 때 발생합니다. `on_user_message_callback`은 가장 먼저 실행되는 후크로, 초기 입력을 검사하거나 수정할 수 있는 기회를 제공합니다.

-   **실행 시기:** 이 콜백은 다른 처리보다 먼저 `runner.run()` 직후에 발생합니다.
-   **목적:** 사용자의 원시 입력을 검사하거나 수정할 수 있는 첫 번째 기회입니다.
-   **흐름 제어:** 사용자의 원래 메시지를 **대체**하기 위해 `types.Content` 객체를 반환합니다.

다음 코드 예제는 이 콜백의 기본 구문을 보여줍니다.

```py
async def on_user_message_callback(
    self,
    *,
    invocation_context: InvocationContext,
    user_message: types.Content,
) -> Optional[types.Content]:
```

### 실행기 시작 콜백

*실행기 시작* 콜백(`before_run_callback`)은 `Runner` 객체가 잠재적으로 수정된 사용자 메시지를 가져와 실행을 준비할 때 발생합니다. `before_run_callback`은 여기서 실행되어 에이전트 논리가 시작되기 전에 전역 설정을 허용합니다.

-   **실행 시기:** 다른 처리보다 먼저 `runner.run()`이 호출된 직후에 발생합니다.
-   **목적:** 사용자의 원시 입력을 검사하거나 수정할 수 있는 첫 번째 기회입니다.
-   **흐름 제어:** 사용자의 원래 메시지를 **대체**하기 위해 `types.Content` 객체를 반환합니다.

다음 코드 예제는 이 콜백의 기본 구문을 보여줍니다.

```py
async def before_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[types.Content]:
```

### 에이전트 실행 콜백

*에이전트 실행* 콜백(`before_agent`, `after_agent`)은 `Runner` 객체가 에이전트를 호출할 때 발생합니다. `before_agent_callback`은 에이전트의 기본 작업이 시작되기 직전에 실행됩니다. 기본 작업은 모델 또는 도구 호출을 포함할 수 있는 요청을 처리하는 에이전트의 전체 프로세스를 포함합니다. 에이전트가 모든 단계를 완료하고 결과를 준비한 후 `after_agent_callback`이 실행됩니다.

**주의:** 이러한 콜백을 구현하는 플러그인은 에이전트 수준 콜백이 실행되기 *전에* 실행됩니다. 또한 플러그인 수준 에이전트 콜백이 `None` 또는 null 응답이 아닌 다른 것을 반환하면 에이전트 수준 콜백은 *실행되지 않습니다*(건너뜁니다).

에이전트 객체의 일부로 정의된 에이전트 콜백에 대한 자세한 내용은 [콜백 유형](../callbacks/types-of-callbacks/#agent-lifecycle-callbacks)을 참조하십시오.

### 모델 콜백

모델 콜백 **(`before_model`, `after_model`, `on_model_error`)**은 모델 객체가 실행되기 전후에 발생합니다. 플러그인 기능은 아래에 자세히 설명된 대로 오류 발생 시 콜백도 지원합니다.

-   에이전트가 AI 모델을 호출해야 하는 경우 `before_model_callback`이 먼저 실행됩니다.
-   모델 호출이 성공하면 `after_model_callback`이 다음에 실행됩니다.
-   모델 호출이 예외로 실패하면 대신 `on_model_error_callback`이 트리거되어 정상적인 복구를 허용합니다.

**주의:** **`before_model`** 및 `**after_model`** 콜백 메서드를 구현하는 플러그인은 모델 수준 콜백이 실행되기 *전에* 실행됩니다. 또한 플러그인 수준 모델 콜백이 `None` 또는 null 응답이 아닌 다른 것을 반환하면 모델 수준 콜백은 *실행되지 않습니다*(건너뜁니다).

#### 모델 오류 콜백 세부 정보

모델 객체에 대한 오류 콜백은 플러그인 기능에서만 지원되며 다음과 같이 작동합니다.

-   **실행 시기:** 모델 호출 중에 예외가 발생할 때.
-   **일반적인 사용 사례:** 정상적인 오류 처리, 특정 오류 로깅 또는 "AI 서비스를 현재 사용할 수 없습니다."와 같은 대체 응답 반환.
-   **흐름 제어:**
    -   **예외를 억제**하고 대체 결과를 제공하기 위해 `LlmResponse` 객체를 반환합니다.
    -   원래 예외가 발생하도록 `None`을 반환합니다.

**참고**: 모델 객체 실행이 `LlmResponse`를 반환하면 시스템은 실행 흐름을 재개하고 `after_model_callback`이 정상적으로 트리거됩니다.****

다음 코드 예제는 이 콜백의 기본 구문을 보여줍니다.

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

플러그인에 대한 도구 콜백 **(`before_tool`, `after_tool`, `on_tool_error`)**은 도구 실행 전후 또는 오류가 발생할 때 발생합니다. 플러그인 기능은 아래에 자세히 설명된 대로 오류 발생 시 콜백도 지원합니다.

-   에이전트가 도구를 실행하면 `before_tool_callback`이 먼저 실행됩니다.
-   도구가 성공적으로 실행되면 `after_tool_callback`이 다음에 실행됩니다.
-   도구에서 예외가 발생하면 대신 `on_tool_error_callback`이 트리거되어 실패를 처리할 수 있는 기회를 제공합니다. `on_tool_error_callback`이 dict를 반환하면 `after_tool_callback`이 정상적으로 트리거됩니다.

**주의:** 이러한 콜백을 구현하는 플러그인은 도구 수준 콜백이 실행되기 *전에* 실행됩니다. 또한 플러그인 수준 도구 콜백이 `None` 또는 null 응답이 아닌 다른 것을 반환하면 도구 수준 콜백은 *실행되지 않습니다*(건너뜁니다).

#### 도구 오류 콜백 세부 정보

도구 객체에 대한 오류 콜백은 플러그인 기능에서만 지원되며 다음과 같이 작동합니다.

-   **실행 시기:** 도구의 `run` 메서드 실행 중에 예외가 발생할 때.
-   **목적:** 특정 도구 예외(`APIError` 등) 포착, 실패 로깅 및 LLM에 사용자 친화적인 오류 메시지 반환.
-   **흐름 제어:** **예외를 억제**하고 대체 결과를 제공하기 위해 `dict`를 반환합니다. 원래 예외가 발생하도록 `None`을 반환합니다.

**참고**: `dict`를 반환하면 실행 흐름이 재개되고 `after_tool_callback`이 정상적으로 트리거됩니다.

다음 코드 예제는 이 콜백의 기본 구문을 보여줍니다.

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

*이벤트 콜백*(`on_event_callback`)은 에이전트가 텍스트 응답이나 도구 호출 결과와 같은 출력을 생성할 때 `Event` 객체로 생성할 때 발생합니다. `on_event_callback`은 각 이벤트에 대해 실행되어 클라이언트로 스트리밍되기 전에 수정할 수 있는 기회를 제공합니다.

-   **실행 시기:** 에이전트가 `Event`를 생성한 후 사용자에게 전송되기 전에. 에이전트 실행은 여러 이벤트를 생성할 수 있습니다.
-   **목적:** 이벤트 수정 또는 보강(예: 메타데이터 추가) 또는 특정 이벤트를 기반으로 부작용 트리거에 유용합니다.
-   **흐름 제어:** 원래 이벤트를 **대체**하기 위해 `Event` 객체를 반환합니다.

다음 코드 예제는 이 콜백의 기본 구문을 보여줍니다.

```py
async def on_event_callback(
    self, *, invocation_context: InvocationContext, event: Event
) -> Optional[Event]:
```

### 실행기 종료 콜백

*실행기 종료* 콜백 **(`after_run_callback`)**은 에이전트가 전체 프로세스를 완료하고 모든 이벤트가 처리되면 `Runner`가 실행을 완료할 때 발생합니다. `after_run_callback`은 정리 및 최종 보고에 완벽한 최종 후크입니다.

-   **실행 시기:** `Runner`가 요청 실행을 완전히 완료한 후.
-   **목적:** 연결 닫기 또는 로그 및 메트릭 데이터 마무리와 같은 전역 정리 작업에 이상적입니다.
-   **흐름 제어:** 이 콜백은 해체 전용이며 최종 결과를 변경할 수 없습니다.

다음 코드 예제는 이 콜백의 기본 구문을 보여줍니다.

```py
async def after_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[None]:
```

## 다음 단계

ADK 프로젝트에 플러그인을 개발하고 적용하기 위한 다음 리소스를 확인하십시오.

-   더 많은 ADK 플러그인 코드 예제는 [ADK Python 리포지토리](https://github.com/google/adk-python/tree/main/src/google/adk/plugins)를 참조하십시오.
-   보안 목적으로 플러그인을 적용하는 방법에 대한 자세한 내용은 [보안 가드레일을 위한 콜백 및 플러그인](/adk-docs/safety/#callbacks-and-plugins-for-security-guardrails)을 참조하십시오.
