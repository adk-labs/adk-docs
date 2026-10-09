---
catalog_title: Model Consult
catalog_description: 빠른 실행 모델의 어려운 추론을 더 강력한 어드바이저 모델로 에스컬레이션합니다
catalog_tags: ["resilience", "observability"]
---

# ADK용 Model Consult 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원됨</span><span class="lst-python">Python v2.11.0</span>
</div>

단일 모델을 사용하는 에이전트는 트레이드오프에 직면합니다. 빠르고 저렴한 모델은 일상적인 단계를 신속하고 적은 리소스로 처리하지만, 복잡한 작업에 대한 심층적인 분석과 의사결정에는 덜 적합할 수 있습니다. 반대로 더 강력한 모델은 복잡한 결정을 잘 처리하지만 각 에이전트 단계마다 응답 시간과 리소스 비용이 증가합니다.

Model Consult를 사용하면 에이전트가 두 모델의 장점을 모두 활용할 수 있습니다. 에이전트는 빠른 실행(executor) 모델에서 실행되다가, 확신을 가지고 해결할 수 없는 결정에 도달하면 Model Consult 도구를 호출하여 더 강력한 어드바이저(advisor) 모델로부터 가이드를 받습니다. 그런 다음 에이전트는 자체 도구를 사용하여 작업을 계속 진행합니다. 에이전트는 필요한 단계에서만 더 강력한 모델을 사용하며, 자문(consultation)이 실패하거나 자문 예산이 소진되더라도 이미 보유한 정보를 바탕으로 작업을 계속 수행합니다.

## 사용 사례

- **비용 최적화**: 에이전트의 일상적인 오케스트레이션과 도구 루프는 저비용 모델에서 실행하고, 필요한 단계에서만 더 강력한 모델에 자문을 구하도록 합니다.
- **정책 조율**: 에이전트가 복잡하고 여러 조항이 얽힌 정책 결정을 프론티어 모델로 에스컬레이션한 후, 그 가이드에 따라 자체 도구로 작업을 수행하도록 합니다.
- **루프 탈출(Loop rescue)**: 에이전트가 동일한 도구 호출을 반복해서 생성할 때 더 강력한 모델에 자문을 구하여 반복 루프에서 벗어나도록 돕습니다.

## 사전 요구사항

- ADK Python v2.11.0 이상.
- 두 개의 모델에 대한 액세스 권한: 저비용 실행 모델과 더 강력한 어드바이저 모델(예: Google Cloud에서 호스팅되는 Gemini Flash 및 Gemini Pro).
- ADK용으로 구성된 모델 자격 증명: Vertex AI API가 활성화된 Google Cloud 프로젝트 또는 Gemini API 키.

## 설치

Model Consult는 ADK Python 패키지에 직접 포함된 기본(native) 도구입니다.

```bash
pip install "google-adk>=2.11.0"
```

## 에이전트와 함께 사용하기

아래 예시의 `lookup_order` 함수와 같은 도메인 도구와 함께 `ModelConsultTool`을 `Agent`에 연결합니다. 이 도구는 `model_consult` 함수 선언을 등록하고 실행 모델의 시스템 인스트럭션에 기본 에스컬레이션 정책을 추가하여, 에이전트가 언제 어떻게 어드바이저에게 자문을 구해야 하는지에 대한 명확한 규칙을 제공합니다.

```python
from google.adk.agents import Agent
from google.adk.tools import ModelConsultTool

def lookup_order(order_id: str) -> dict[str, str]:
    """Looks up order status by identifier."""
    return {"order_id": order_id, "status": "held_for_fraud_review"}

root_agent = Agent(
    model="gemini-flash-latest",
    name="support_executor",
    instruction=(
        "You are an order support assistant. Resolve customer issues using"
        " your tools."
    ),
    tools=[
        lookup_order,
        ModelConsultTool(
            model="gemini-pro-latest",  # Advisor model
            max_uses=2,
            session_max_uses=5,
            thinking_level="high",
        ),
    ],
)
```

이 예시에서는 다음과 같이 작동합니다.

* `support_executor` 에이전트는 빠른 모델(`gemini-flash-latest`)에서 실행되며 `lookup_order` 도구를 사용하여 사용자의 문제를 해결하려고 시도합니다.
* 실행 모델이 `model_consult`를 호출할 시점을 결정합니다. 기본 설정에서 실행 모델은 결정을 확정하기 전, 막혔을 때, 그리고 작업 완료를 선언하기 전에 `model_consult`를 호출하도록 지시받습니다.
* `ModelConsultTool`은 호출을 가로채고 `max_uses` 예산을 확인한 다음, 현재 세션 이벤트와 `lookup_order` 도구의 설명을 단일 어드바이저 자문 요청으로 패키징합니다.
* 어드바이저 모델은 컨텍스트를 평가하고 구조화된 텍스트 가이드를 반환하여, `support_executor`가 다시 제어권을 이어받아 권장된 도구를 실행하고 턴을 완료할 수 있도록 합니다.


## 사용 가능한 도구

도구 | 설명
---- | -----------
`model_consult` | 구조화된 가이드를 얻기 위해 세션 기록과 특정 질문을 더 강력한 어드바이저 모델로 에스컬레이션합니다.

## 작동 방식

실행 모델이 `model_consult`를 호출하면 `ModelConsultTool`은 다음 4단계를 수행하고 실행 모델에 구조화된 딕셔너리를 반환합니다.

1. **예산 확인** — `ModelConsultTool`은 턴당 카운터를 `max_uses`와 비교하고 세션 전체 카운터를 `session_max_uses`와 비교합니다. 두 한도 중 하나라도 도달한 경우, 도구는 어드바이저 모델을 호출하지 않고 즉시 `"status": "limit_reached"`를 반환하며 이미 수집된 정보로 진행하도록 실행 모델에 지시합니다.
2. **컨텍스트 전달(Context handover)** — `ModelConsultTool`은 자문 내용을 단일 `role='user'` `types.Content` 메시지로 패키징합니다. `include_agent_instruction` 및 `include_tool_inventory`가 `True`인 경우, 메시지는 확인된 실행 모델 인스트럭션과 형제(sibling) 도구 목록으로 시작합니다. 다음으로, `ModelConsultTool`은 `ModelConsultContextConfig`에 따라 `Session.events`의 부분적이지 않고(non-partial) 되돌려지지 않은(non-rewound) 이벤트를 변환하여, 텍스트 파트를 화자별로 라벨링하고 이전 도구 호출과 도구 응답을 읽기 쉬운 텍스트 요약으로 평탄화하는 동시에 현재 진행 중인 `model_consult` 호출은 제외합니다. 마지막으로 `ModelConsultTool`은 활성 에이전트 이름, 실행 모델의 질문, 실행 모델이 전달한 추가 `context` 문자열을 포함하는 핸드오프 파트를 추가합니다.
3. **도구 없는 어드바이저 호출** — `ModelConsultTool`은 도구 호출이 비활성화된 상태로 기본 어드바이저 시스템 인스트럭션(또는 제공된 경우 커스텀 `advisor_instruction`)을 사용하여 구성된 어드바이저 `BaseLlm`을 호출합니다. 어드바이저 요청에서 도구 선언이 제외되므로 어드바이저는 스스로 도구를 실행하거나 부작용(side effects)을 일으킬 수 없으며, 실행 모델이 다음에 어떤 도구를 어떤 인수로 호출해야 하는지 알려주는 텍스트 가이드만 반환할 수 있습니다.
4. **구조화된 도구 응답** — `ModelConsultTool`은 에이전트 루프로 예외를 다시 발생시키지 않습니다. 대신 [응답 상태 값](#response-status-values)에 설명된 대로 `status` 값이 포함된 딕셔너리를 반환합니다.

### 응답 상태 값 {#response-status-values}

`model_consult`가 반환하는 딕셔너리의 `status` 필드는 다음 값 중 하나를 가집니다.

| 상태 | 반환 조건 | 필드 | 자문 예산 |
| --- | --- | --- | --- |
| `ok` | 어드바이저가 가이드를 반환함. | `guidance`, `advisor_model`, `thinking_level`, `consults`, `usage`, `latency_ms` | 턴당 및 세션 카운터를 증가시킴. |
| `limit_reached` | `max_uses` 또는 `session_max_uses`가 이미 소진됨. 어드바이저 모델은 호출되지 않음. | `message`, `consults` | 소모되지 않음. |
| `error` | 어드바이저 호출이 타임아웃되거나 실패하거나 표시 가능한 텍스트를 생성하지 않음. | `error`, `message`, `advisor_model`, `consults` | 소모되지 않음. |
| `invalid_request` | `question`이 비어 있거나 공백만 있음. | `message` | 소모되지 않음. |

성공적인 자문은 다음 딕셔너리 구조를 반환합니다. 표시된 토큰 수와 지연 시간은 이해를 돕기 위한 예시이며 실제 측정값이 아닙니다.

```json
{
    "status": "ok",
    "guidance": "1. Call lookup_order with order_id='ORD-42'.",
    "advisor_model": "gemini-3.1-pro-preview",
    "thinking_level": "high",
    "consults": {
        "used_this_turn": 1,
        "max_uses": 2,
        "used_this_session": 1,
        "session_max_uses": 5,
        "remaining": 1
    },
    "usage": {
        "prompt_tokens": 612,
        "output_tokens": 184,
        "thoughts_tokens": 320,
        "total_tokens": 1116
    },
    "latency_ms": 842.5
}
```

## 모범 사례

Model Consult는 추가 설정 없이도 작동합니다. 결과를 개선하려면 다음 모범 사례를 활용하세요.

* 실행 모델에서 사고(thinking) 기능을 활성화합니다.
* 기본 에스컬레이션 정책을 유지하거나, 사용 사례에 맞게 실행 모델 프롬프트에서 에스컬레이션 정책을 조정합니다.

### 실행 모델에서 사고 기능 활성화

실행 모델이 `model_consult`를 호출할 시점을 결정하므로, 추론할 수 있을 때 더 나은 결정을 내립니다. 실행 모델에서 사고 기능을 활성화하세요. 예를 들어 동적 사고(dynamic thinking)가 적용된 더 가벼운 모델을 사용할 수 있습니다.

### 실행 모델이 어드바이저에게 자문을 구하는 시점 맞춤설정

`ModelConsultTool` 객체는 실행 모델의 시스템 인스트럭션에 에스컬레이션 정책을 추가합니다. 기본적으로 이 정책은 실행 모델이 결정을 확정하기 전, 막혔을 때, 그리고 작업 완료를 선언하기 전에 `model_consult`를 호출하도록 지시합니다. 이는 다음 표의 계획(Plan), 진단(Diagnose), 검토(Review) 트리거를 포괄합니다.

기본 정책을 대체하려면 `executor_instruction`에 고유한 텍스트를 전달하세요. 정책을 제거하려면 빈 문자열(`""`)을 전달하세요.

```python
ModelConsultTool(
    executor_instruction=(
        "Call model_consult before your first response, and whenever a"
        " tool call fails for a reason you cannot explain."
    ),
)
```

### 일반적인 자문 트리거

다음 표에는 어드바이저에게 자문을 구하는 일반적인 이유와 `executor_instruction`에 추가할 수 있는 트리거가 나와 있습니다.

| 이유 | 도움이 되는 이유 | 예시 트리거 |
| --- | --- | --- |
| 계획(Plan) | 작업 초반의 잘못된 해석이나 접근 방식은 이후의 모든 단계에 영향을 미치고 시간과 토큰을 낭비하게 만듭니다. | * 첫 번째 응답 전.<br>* 실행 모델이 사실을 수집한 후 주요 작업을 시작하기 전.<br>* 요청에서 해결책을 제안할 때 이를 검증하는 방법을 묻기 위해.<br>* 여러 접근 방식이나 해석이 가능하지만 어느 한쪽을 뒷받침하는 증거가 없을 때.<br>* 어렵다고 알려진 요청 유형의 경우. |
| 진단(Diagnose) | 실패나 모순은 실행 모델의 가정 중 하나가 잘못되었음을 의미합니다. | * 도구 호출이 실패하거나 예상치 못한 결과를 반환하고 실행 모델이 그 이유를 설명할 수 없을 때.<br>* 실행 모델이 새로운 정보 없이 동일한 도구 호출이나 유사한 변형을 반복할 때.<br>* 실행 모델이 자신의 작업을 되돌릴 때.<br>* 두 소스 또는 도구 결과가 서로 일치하지 않을 때.<br>* 실행 모델이 요청 자체가 잘못되었다고 결론지을 때. |
| 검토(Review) | 요구사항에 비추어 결과를 확인하면 사용자가 발견하기 전에 오류와 누락을 찾아낼 수 있습니다. | * 최종 답변 전.<br>* 실행 모델이 복잡한 작업의 상당 부분을 완료한 후. |

## 설정 옵션

`ModelConsultTool` 객체는 어드바이저 모델 선택, 자문 예산 및 프롬프트 재정의를 구성하며, `ModelConsultContextConfig`는 전달 전에 세션 이벤트의 형식을 지정하고 범위를 제한하는 방법을 제어합니다.

### ModelConsultTool 옵션

`ModelConsultTool` 클래스는 다음 생성자 인수를 허용합니다.

| 옵션 | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `model` | `str` \| `BaseLlm` | `'gemini-3.1-pro-preview'` | ADK의 모델 레지스트리를 통해 확인되는 어드바이저 모델 이름 또는 사전 구성된 `BaseLlm` 인스턴스입니다. 기본값은 프리뷰 모델이며 변경될 수 있습니다. |
| `max_uses` | `int` | `None` | 사용자 턴당 최대 성공 자문 횟수입니다. `None`은 턴당 한도가 없음을 의미합니다. |
| `session_max_uses` | `int` | `None` | 전체 세션에 걸친 최대 성공 자문 횟수입니다. `None`은 세션 전체 한도가 없음을 의미합니다. |
| `thinking_level` | `str` \| `types.ThinkingLevel` | `'high'` | 어드바이저 모델의 추론 노력 수준입니다: `'minimal'`, `'low'`, `'medium'`, `'high'`, `types.ThinkingLevel` 열거형 값, 또는 사고 기능을 설정하지 않으려면 `'off'`, `'none'`, `None`을 지정합니다. |
| `max_output_tokens` | `int` | `None` | 추론 모델의 가시적 출력과 사고 토큰을 모두 포함하는 어드바이저 출력 토큰의 선택적 상한입니다. |
| `timeout_seconds` | `float` | `None` | 호출당 실제 경과 시간(wall-clock) 타임아웃(초)입니다. `None`은 도구 수준의 타임아웃이 없음을 의미합니다. |
| `context_config` | `ModelConsultContextConfig` | `None` | 어드바이저를 위해 세션 기록을 패키징하고 제한하는 방법을 제어합니다. |
| `executor_instruction` | `str` | `None` | 실행 모델의 `system_instruction`에 자동으로 추가되는 기본 에스컬레이션 정책을 재정의합니다. 자동 주입을 비활성화하려면 `""`를 전달하세요. |
| `advisor_instruction` | `str` | `None` | 어드바이저 모델로 전송되는 기본 시스템 인스트럭션을 재정의합니다. |
| `description` | `str` | `None` | 실행 모델에 표시되는 기본 도구 설명을 재정의합니다. |
| `include_agent_instruction` | `bool` | `True` | 가이드가 실행 모델의 제약 조건을 준수하도록 실행 에이전트 자체의 인스트럭션을 어드바이저에게 전달합니다. |
| `include_tool_inventory` | `bool` | `True` | 어드바이저 자문 프롬프트에 실행 모델의 다른 도구 이름과 설명을 포함합니다. |
| `generate_content_config` | `types.GenerateContentConfig` | `None` | `temperature` 또는 `safety_settings`와 같이 어드바이저 호출마다 복제되는 기본 생성 구성입니다. |
| `name` | `str` | `'model_consult'` | 실행 모델에 노출되는 도구 이름입니다. |

### ModelConsultContextConfig 옵션

`ModelConsultContextConfig`는 `Session.events`를 어드바이저의 입력 콘텐츠로 변환하는 방법을 제어합니다.

| 옵션 | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `include_session` | `bool` | `True` | `True`이면 변환된 `Session.events` 기록을 전송하고, `False`이면 이전 세션 이벤트를 생략합니다. |
| `max_events` | `int` | `None` | 문자 수 예산을 적용하기 전에 가장 최근의 부분적이지 않은(non-partial) 세션 이벤트를 최대 이 개수만큼 유지합니다. `None`은 모든 이벤트를 유지합니다. |
| `max_chars` | `int` | `200000` | 전달된 모든 세션 턴에 걸친 문자 수 예산입니다. `None`은 문자 수 예산을 비활성화합니다. |
| `max_part_chars` | `int` | `4000` | 렌더링된 도구 호출, 도구 결과 및 코드 블록에 대한 파트당 문자 수 상한이며, 일반 텍스트 파트는 이 상한의 8배까지 허용됩니다. |
| `include_media` | `bool` | `True` | `True`이면 인라인 미디어와 파일 참조를 어드바이저 모델에 전달하고, `False`이면 텍스트 플레이스홀더로 대체합니다. 세션 미디어를 어드바이저 모델로 보내지 않아야 하는 경우 `False`로 설정하세요. |
| `include_thoughts` | `bool` | `False` | `True`이면 어드바이저 전달 내용에 실행 모델의 내부 사고(thought) 파트를 포함합니다. |

## 추가 리소스

* [Model Consult Unit Guide](https://github.com/google/adk-python/blob/main/docs/guides/tools/model_consult/model_consult_tool/index.md)
