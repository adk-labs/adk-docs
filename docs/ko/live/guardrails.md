# 라이브 에이전트를 위한 가드레일

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.8.0</span>
</div>

가드레일은 프로덕션 환경에서 실시간 음성 에이전트가 어떻게 동작할지를 통제하여 대화가 주제에서 벗어나지 않고(on-topic), 정책을 준수하며(on-policy), 안전(safe)하게 유지되도록 합니다. 실시간 연결에서는 오디오가 지속적으로 스트리밍되고 모델이 실시간으로 발화를 시작합니다. ADK는 대화 지연 시간(latency)에 미치는 영향을 최소화하면서 대화를 안전하게 보호하기 위해 함께 작동하는 다중 계층 보호 기능을 제공합니다.

일반적인 콜백 메커니즘 및 플러그인 등록 방법은 [콜백 유형](../callbacks/types-of-callbacks.md) 및 [플러그인](../plugins/index.md)을 참조하세요.

## 가드레일 계층

| 계층 | 역할 | 보호 초점 | 지연 시간 영향 |
| :--- | :--- | :--- | :--- |
| 시스템 지침 (System instructions) | 톤, 대화 규칙 및 경계를 형성 | 행동 가이드 | 애플리케이션 추가 지연 시간 없음 |
| 안전 설정 (Safety settings) | 콘텐츠 안전에 대한 플랫폼 임계값을 적용 | 플랫폼 안전 필터 | 애플리케이션 추가 지연 시간 없음 |
| 입력 유효성 검사 (Input validation) | 프롬프트 인젝션 및 금지된 주제 감지 | 사용자 입력 검증 | 최소화 (턴당 실행) |
| 응답 유효성 검사 (Response validation) | 비즈니스 정책에 따라 에이전트 응답을 선별 | 에이전트 응답 검증 | 검사 방식에 따라 다름 |
| 도구 가드레일 (Tool guardrails) | 도구 실행을 가로채고 매개변수를 검증 | 도구 실행 안전성 | 최소화 (도구 호출당 실행) |

이러한 계층들은 함께 연계되어 심층 방어(defense in depth)를 제공합니다. 시스템 지침은 자연스러운 대화 흐름을 형성하고, 플랫폼 안전 필터는 기본적인 유해성 경계를 적용하며, 애플리케이션 검증기는 입력, 응답 및 도구 호출을 독립적으로 검증합니다. 명확한 지침과 독립적인 유효성 검사를 결합하면 한 계층을 우회하는 예외적인 케이스(edge case)가 발생하더라도 다른 계층에서 이를 차단할 수 있습니다.

## 지침 및 안전 설정

지침과 안전 설정은 세션 전체의 기준 동작을 설정합니다. 두 설정 모두 세션을 생성할 때 에이전트에 구성합니다.

```python
from google.adk.agents import Agent
from google.genai import types

root_agent = Agent(
    model='gemini-live-2.5-flash-native-audio',
    name='support_agent',
    instruction=(
        'You help customers with billing questions. '
        'Never quote a price; offer to transfer to sales instead. '
        'Never discuss a competitor.'
    ),
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
        ]
    ),
)
```

모델은 대화 컨텍스트가 누적됨에 따라 모든 턴에 걸쳐 시스템 지침을 평가합니다. 실시간 에이전트를 위한 지침을 설계할 때는 페르소나, 대화 규칙, 대화 가드레일을 순서대로 정의하세요. 엄격한 제약 조건의 경우 대안을 제시하거나 발신자를 상담원에게 호전환(transfer)하는 등 경계 조건에 부딪혔을 때 수행해야 할 명시적인 처리 규칙을 제공하세요.

안전 설정은 실시간 세션에 [안전 및 콘텐츠 필터](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/configure-safety-filters)를 적용합니다. 모델이 구성된 임계값을 초과하는 콘텐츠를 생성하면 플랫폼에서 생성을 중단합니다.

실시간 연결은 시작 시점에 이러한 설정을 설정하므로 세션 지속 시간 동안 고정된 상태로 유지됩니다. 세션 상태를 보간(interpolate)하는 지침 문자열은 세션이 시작될 때 한 번 렌더링되며, 재개된 연결은 해당 렌더링된 지침을 재사용합니다.

## 대화 유효성 검사

대화 유효성 검사는 사용자의 발화와 에이전트의 응답을 독립적으로 평가합니다. 관리형 엔터프라이즈 정책의 경우, [Model Armor 플러그인](../integrations/model-armor.md)이 Google Cloud 템플릿을 기반으로 프롬프트 인젝션, 민감한 데이터 및 정책 위반 사항을 선별합니다. ADK 모델 콜백을 사용하여 커스텀 유효성 검사를 구현할 수도 있습니다.

### 사용자 입력 유효성 검사

`before_model_callback` 훅은 사용자 입력을 가로챕니다. 이 콜백은 입력된 텍스트가 모델에 도달하기 전에 평가하므로, 차단 시 연결을 유지하면서도 메시지가 컨텍스트에 포함되지 않도록 방지합니다. 음성 오디오의 경우 콜백은 모델이 이미 오디오를 수신한 후에 전사된 발화 전체를 검사합니다. 여기서 차단이 발생하면 라이브 세션을 다시 시작하여 이미 전송 중인 응답을 삭제합니다.

검사에서 정책 위반이 확인되면 `LlmResponse`를 반환하여 사용자의 턴을 안전한 대체 응답으로 교체합니다.

```python
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types


def block_input(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
  """경쟁사를 언급하는 사용자 턴을 차단합니다."""
  text = ''.join(
      part.text or ''
      for content in llm_request.contents
      for part in content.parts or []
  )

  if 'competitor' not in text.lower():
    return None

  return LlmResponse(
      content=types.Content(
          role='model',
          parts=[types.Part(text="I can't discuss that.")],
      )
  )
```

### 에이전트 응답 유효성 검사

`after_model_callback` 훅은 모델 응답이 사용자에게 전달되기 전이나 전달되는 도중에 이를 확인합니다. 유효성 검사는 음성 턴 중에 누적되는 전사 텍스트를 검사하여 위반 사항을 조기에 포착하거나, 전체 턴의 전사 텍스트를 평가할 수 있습니다.

```python
def block_output(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
  """답변에 가격이 언급되면 응답을 대체합니다."""
  transcription = llm_response.output_transcription
  text = transcription.text if transcription else ''

  if '$' not in text:
    return None

  return LlmResponse(
      content=types.Content(
          role='model',
          parts=[types.Part(text='Let me connect you with sales.')],
      )
  )
```

출력 콜백에서 `LlmResponse`를 반환하면 모델 생성을 즉시 중단하고 대체 메시지를 사용자에게 전달합니다. 모델이 이미 입력 처리를 시작한 음성 턴의 경우, 거부된 콘텐츠가 대화 컨텍스트에 남아 있지 않도록 ADK가 현재 턴을 지웁니다.

## 도구 가드레일

도구 콜백은 외부 시스템을 보호하고 작업을 검증합니다. `before_tool_callback` 훅은 도구가 실행되기 전에 인수를 검사하여 승인되지 않은 매개변수를 거부하거나 비즈니스 로직을 적용할 수 있도록 합니다. `after_tool_callback` 훅은 결과가 모델로 반환되기 전에 민감한 결과를 삭제(redact)합니다.

```python
from typing import Any, Optional

from google.adk.tools import BaseTool
from google.adk.tools import ToolContext


def validate_refund(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
) -> Optional[dict[str, Any]]:
  """임계값을 초과하는 승인되지 않은 환불을 방지합니다."""
  if tool.name == 'issue_refund' and args.get('amount', 0) > 100:
    return {'error': 'Refund exceeds automatic approval limit.'}
  return None
```

도구 콜백에서 결과를 반환하면 도구 실행을 우회하고 반환값을 모델에 직접 제공합니다. 자세한 내용은 [도구 실행 콜백](../callbacks/types-of-callbacks.md#tool-execution-callbacks)을 참조하세요.

실시간 오디오 스트림은 인터랙티브한 사람의 확인을 기다리기 위해 일시 중지될 수 없습니다. 실시간 에이전트가 높은 권한이 필요한 도구를 사용하는 경우 콜백 내에서 인수를 자동으로 검증하거나 요청을 사람에게 인계(handoff)하도록 라우팅하세요.

## 요구사항 및 모범 사례

- **전사(Transcription) 활성 상태 유지**: 텍스트 기반 대화 유효성 검사는 음성 전사에 의존합니다. `RunConfig.input_audio_transcription`과 `RunConfig.output_audio_transcription`은 모두 기본적으로 활성화되어 있습니다. 둘 중 하나를 `None`으로 설정하면 해당 검별 계층이 비활성화됩니다.
- **검증기 경량화 유지**: 라이브 수신 루프의 콜백은 오디오 처리와 인라인으로 실행됩니다. 빠른 로컬 검사를 통해 대화의 응답성을 유지하세요. 더 무거운 검사의 경우 전체 턴 전사를 평가하거나 장시간 실행되는 분석을 비동기적으로 오프로드하세요.
- **에이전트 전반에 걸친 정책 적용**: `App`에 [Model Armor](../integrations/model-armor.md)와 같은 플러그인을 등록하면 콜백 코드를 중복하지 않고도 애플리케이션의 모든 에이전트에 일관된 보안 규칙을 적용할 수 있습니다.

## 추가 리소스

- [Model Armor 플러그인](../integrations/model-armor.md)
- [콜백 유형](../callbacks/types-of-callbacks.md)
- [플러그인](../plugins/index.md)
- [안전 필터 구성](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/configure-safety-filters)
