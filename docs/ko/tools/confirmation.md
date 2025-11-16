---
hide:
  - toc
---
# ADK 도구에 대한 작업 확인 받기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.14.0</span><span class="lst-preview">실험적</span>
</div>

일부 에이전트 워크플로는 의사 결정, 확인, 보안 또는 일반적인 감독을 위해 확인이 필요합니다. 이러한 경우 워크플로를 진행하기 전에 사람이나 감독 시스템으로부터 응답을 받아야 합니다. 에이전트 개발 키트(ADK)의 *도구 확인* 기능을 사용하면 ADK 도구가 실행을 일시 중지하고 사용자 또는 다른 시스템과 상호 작용하여 확인하거나 구조화된 데이터를 수집한 후 진행할 수 있습니다. 다음과 같은 방법으로 ADK 도구와 함께 도구 확인을 사용할 수 있습니다.

-   **[부울 확인](#boolean-confirmation):** `require_confirmation` 매개변수를 사용하여 FunctionTool을 구성할 수 있습니다. 이 옵션은 예 또는 아니요 확인 응답을 위해 도구를 일시 중지합니다.
-   **[고급 확인](#advanced-confirmation):** 구조화된 데이터 응답이 필요한 시나리오의 경우 확인을 설명하는 텍스트 프롬프트와 예상 응답으로 `FunctionTool`을 구성할 수 있습니다.

!!! example "실험적"
    도구 확인 기능은 실험적이며 몇 가지 [알려진 제한 사항](#known-limitations)이 있습니다.
    [피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=tool%20confirmation)을 환영합니다!

요청이 사용자에게 전달되는 방식을 구성할 수 있으며 시스템은 ADK 서버의 REST API를 통해 전송된 [원격 응답](#remote-response)을 사용할 수도 있습니다. ADK 웹 사용자 인터페이스와 함께 확인 기능을 사용하는 경우 에이전트 워크플로는 그림 1과 같이 사용자에게 대화 상자를 표시하여 입력을 요청합니다.

![도구 확인을 위한 기본 사용자 인터페이스 스크린샷](/adk-docs/assets/confirmation-ui.png)

**그림 1.** 고급 도구 응답 구현을 사용하는 예제 확인 응답 요청 대화 상자.

다음 섹션에서는 확인 시나리오에 이 기능을 사용하는 방법을 설명합니다. 전체 코드 샘플은 [human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py) 예제를 참조하세요. 에이전트 워크플로에 사람의 입력을 통합하는 추가 방법이 있습니다. 자세한 내용은 [Human-in-the-loop](/adk-docs/agents/multi-agents/#human-in-the-loop-pattern) 에이전트 패턴을 참조하세요.

## 부울 확인 {#boolean-confirmation}

도구에서 사용자로부터 간단한 '예' 또는 '아니요'만 필요한 경우 `FunctionTool` 클래스를 래퍼로 사용하여 확인 단계를 추가할 수 있습니다. 예를 들어 `reimburse`라는 도구가 있는 경우 다음 예와 같이 `FunctionTool` 클래스로 래핑하고 `require_confirmation` 매개변수를 `True`로 설정하여 확인 단계를 활성화할 수 있습니다.

```python
# agent.py에서
root_agent = Agent(
   ...
   tools=[
        # 도구 호출에 대한 사용자 확인을 요구하려면 require_confirmation을 True로 설정합니다.
        FunctionTool(reimburse, require_confirmation=True),
    ],
...
```

이 구현 방법은 최소한의 코드가 필요하지만 사용자 또는 확인 시스템의 간단한 승인으로 제한됩니다. 이 접근 방식의 전체 예는 [human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py) 코드 샘플을 참조하세요.

### 확인 함수 요구

`require_confirmation` 응답의 동작을 부울 응답을 반환하는 함수로 입력 값을 대체하여 수정할 수 있습니다. 다음 예는 확인이 필요한지 여부를 결정하는 함수를 보여줍니다.

```python
async def confirmation_threshold(
    amount: int, tool_context: ToolContext
) -> bool:
  """금액이 1000보다 크면 true를 반환합니다."""
  return amount > 1000
```

이 함수는 `require_confirmation` 매개변수의 매개변수 값으로 설정할 수 있습니다.

```python
root_agent = Agent(
   ...
   tools=[
        # 사용자 확인을 요구하려면 require_confirmation을 True로 설정합니다.
        FunctionTool(reimburse, require_confirmation=confirmation_threshold),
    ],
...
```

이 구현의 전체 예는 [human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py) 코드 샘플을 참조하세요.

## 고급 확인 {#advanced-confirmation}

도구 확인에 사용자에 대한 자세한 내용이나 더 복잡한 응답이 필요한 경우 tool_confirmation 구현을 사용합니다. 이 접근 방식은 `ToolContext` 개체를 확장하여 사용자에 대한 요청에 대한 텍스트 설명을 추가하고 더 복잡한 응답 데이터를 허용합니다. 이 방법으로 도구 확인을 구현할 때 도구 실행을 일시 중지하고 특정 정보를 요청한 다음 제공된 데이터로 도구를 다시 시작할 수 있습니다.

이 확인 흐름에는 시스템이 사람의 응답에 대한 입력 요청을 조합하여 보내는 요청 단계와 시스템이 반환된 데이터를 수신하고 처리하는 응답 단계가 있습니다.

### 확인 정의

고급 확인 기능이 있는 도구를 만들 때 ToolContext 개체를 포함하는 함수를 만듭니다. 그런 다음 tool_confirmation 개체, `hint` 및 `payload` 매개변수가 있는 `tool_context.request_confirmation()` 메서드를 사용하여 확인을 정의합니다. 이러한 속성은 다음과 같이 사용됩니다.

-   `hint`: 사용자에게 필요한 것을 설명하는 설명 메시지입니다.
-   `payload`: 반환할 것으로 예상되는 데이터의 구조입니다. 이 데이터 유형은 Any이며 사전 또는 pydantic 모델과 같이 JSON 형식 문자열로 직렬화할 수 있어야 합니다.

다음 코드는 직원의 휴가 요청을 처리하는 도구에 대한 예제 구현을 보여줍니다.

```python
def request_time_off(days: int, tool_context: ToolContext):
  """직원의 휴가를 요청합니다."""
  ...
  tool_confirmation = tool_context.tool_confirmation
  if not tool_confirmation:
    tool_context.request_confirmation(
        hint=(
            '예상되는 ToolConfirmation 페이로드가 있는 FunctionResponse로 응답하여'
            ' tool call request_time_off()를 승인하거나 거부하십시오.'
        ),
        payload={
            'approved_days': 0,
        },
    )
    # 도구가 확인 응답을 기다리고 있음을 나타내는 중간 상태를 반환합니다.
    return {'status': '관리자 승인이 필요합니다.'}

  approved_days = tool_confirmation.payload['approved_days']
  approved_days = min(approved_days, days)
  if approved_days == 0:
    return {'status': '휴가 요청이 거부되었습니다.', 'approved_days': 0}
  return {
      'status': 'ok',
      'approved_days': approved_days,
  }
```

이 접근 방식의 전체 예는 [human_tool_confirmation](https://github.com/google/adk-python/blob/fc90ce968f114f84b14829f8117797a4c256d710/contributing/samples/human_tool_confirmation/agent.py) 코드 샘플을 참조하세요. 에이전트 워크플로 도구 실행은 확인을 받는 동안 일시 중지된다는 점을 명심하세요. 확인을 받은 후 `tool_confirmation.payload` 개체에서 확인 응답에 액세스한 다음 워크플로 실행을 계속할 수 있습니다.

## REST API를 사용한 원격 확인 {#remote-response}

에이전트 워크플로에 대한 사람의 확인을 위한 활성 사용자 인터페이스가 없는 경우 명령줄 인터페이스를 통해 확인을 처리하거나 이메일 또는 채팅 애플리케이션과 같은 다른 채널을 통해 라우팅할 수 있습니다. 도구 호출을 확인하려면 사용자 또는 호출 애플리케이션이 도구 확인 데이터와 함께 `FunctionResponse` 이벤트를 보내야 합니다.

요청을 ADK API 서버의 `/run` 또는 `/run_sse` 엔드포인트로 보내거나 ADK 실행기로 직접 보낼 수 있습니다. 다음 예에서는 `curl` 명령을 사용하여 확인을 `/run_sse` 엔드포인트로 보냅니다.

```bash
 curl -X POST http://localhost:8000/run_sse \
 -H "Content-Type: application/json" \
 -d '{
    "app_name": "human_tool_confirmation",
    "user_id": "user",
    "session_id": "7828f575-2402-489f-8079-74ea95b6a300",
    "new_message": {
        "parts": [
            {
                "function_response": {
                    "id": "adk-13b84a8c-c95c-4d66-b006-d72b30447e35",
                    "name": "adk_request_confirmation",
                    "response": {
                        "confirmed": true
                    }
                }
            }
        ],
        "role": "user"
    }
}'
```

확인에 대한 REST 기반 응답은 다음 요구 사항을 충족해야 합니다.

-   `function_response`의 `id`는 `RequestConfirmation` `FunctionCall` 이벤트의 `function_call_id`와 일치해야 합니다.
-   `name`은 `adk_request_confirmation`이어야 합니다.
-   `response` 개체에는 확인 상태와 도구에 필요한 추가 페이로드 데이터가 포함됩니다.

!!! note "참고: 재개 기능으로 확인"

    ADK 에이전트 워크플로가 [재개](/adk-docs/runtime/resume/) 기능으로 구성된 경우 확인 응답과 함께 호출 ID(`invocation_id`) 매개변수도 포함해야 합니다. 제공하는 호출 ID는 확인 요청을 생성한 것과 동일한 호출이어야 합니다. 그렇지 않으면 시스템이 확인 응답으로 새 호출을 시작합니다. 에이전트가 재개 기능을 사용하는 경우 응답에 포함될 수 있도록 확인 요청과 함께 호출 ID를 매개변수로 포함하는 것을 고려하세요. 재개 기능 사용에 대한 자세한 내용은 [중지된 에이전트 재개](/adk-docs/runtime/resume/)를 참조하세요.

## 알려진 제한 사항 {#known-limitations}

도구 확인 기능에는 다음과 같은 제한 사항이 있습니다.

-   [DatabaseSessionService](/adk-docs/api-reference/python/google-adk.html#google.adk.sessions.DatabaseSessionService)는 이 기능에서 지원되지 않습니다.
-   [VertexAiSessionService](/adk-docs/api-reference/python/google-adk.html#google.adk.sessions.VertexAiSessionService)는 이 기능에서 지원되지 않습니다.

## 다음 단계

에이전트 워크플로용 ADK 도구 빌드에 대한 자세한 내용은 [함수 도구](/adk-docs/tools/function-tools/)를 참조하세요.
