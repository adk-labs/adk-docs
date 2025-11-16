# 콜백을 위한 디자인 패턴 및 모범 사례

콜백은 에이전트 라이프사이클에 개입할 수 있는 강력한 훅(hook)을 제공합니다. 다음은 ADK에서 콜백을 효과적으로 활용하는 방법을 보여주는 일반적인 디자인 패턴과 구현을 위한 모범 사례입니다.

## 디자인 패턴

이 패턴들은 콜백을 사용하여 에이전트의 동작을 향상시키거나 제어하는 대표적인 방법들을 보여줍니다.

### 1. 가드레일 및 정책 강제 { #guardrails-policy-enforcement }

**패턴 개요:**
요청이 LLM이나 도구에 도달하기 전에 가로채서 규칙을 강제합니다.

**구현:**
- `before_model_callback`을 사용하여 `LlmRequest` 프롬프트를 검사합니다.
- `before_tool_callback`을 사용하여 도구의 인자(argument)를 검사합니다.
- 정책 위반(예: 금지된 주제, 비속어)이 감지되면:
  - 미리 정의된 응답(`LlmResponse` 또는 `dict`/`Map`)을 반환하여 작업을 차단합니다.
  - 선택적으로 `context.state`를 업데이트하여 위반 사항을 기록합니다.

**사용 사례 예시:**
`before_model_callback`이 `llm_request.contents`에 민감한 키워드가 있는지 확인하고, 발견되면 "이 요청을 처리할 수 없습니다"라는 표준 `LlmResponse`를 반환하여 LLM 호출을 막습니다.

### 2. 동적 상태 관리 { #dynamic-state-management }

**패턴 개요:**
콜백 내에서 세션 상태를 읽고 써서 에이전트의 행동을 컨텍스트에 맞게 조정하고 단계 간에 데이터를 전달합니다.

**구현:**
- `callback_context.state` 또는 `tool_context.state`에 접근합니다.
- 변경 사항(`state['key'] = value`)은 후속 `Event.actions.state_delta`에서 자동으로 추적됩니다.
- 변경 내용은 `SessionService`에 의해 영구 저장됩니다.

**사용 사례 예시:**
`after_tool_callback`이 도구 결과에서 얻은 `transaction_id`를 `tool_context.state['last_transaction_id']`에 저장합니다. 이후 `before_agent_callback`은 `state['user_tier']`를 읽어 에이전트의 인사말을 맞춤 설정할 수 있습니다.

### 3. 로깅 및 모니터링 { #logging-and-monitoring }

**패턴 개요:**
관찰 가능성(observability) 및 디버깅을 위해 특정 라이프사이클 지점에 상세한 로깅을 추가합니다.

**구현:**
- 콜백(예: `before_agent_callback`, `after_tool_callback`, `after_model_callback`)을 구현합니다.
- 다음을 포함하는 구조화된 로그를 출력하거나 전송합니다:
  - 에이전트 이름
  - 도구 이름
  - 호출 ID (Invocation ID)
  - 컨텍스트나 인자에서 가져온 관련 데이터

**사용 사례 예시:**
`INFO: [Invocation: e-123] Before Tool: search_api - Args: {'query': 'ADK'}`와 같은 로그 메시지를 기록합니다.

### 4. 캐싱 { #caching }

**패턴 개요:**
결과를 캐싱하여 중복되는 LLM 호출이나 도구 실행을 방지합니다.

**구현 단계:**
1.  **작업 이전:** `before_model_callback` 또는 `before_tool_callback`에서:
    - 요청/인자를 기반으로 캐시 키를 생성합니다.
    - `context.state`(또는 외부 캐시)에서 이 키를 확인합니다.
    - 키를 찾으면 캐시된 `LlmResponse`나 결과를 직접 반환합니다.

2.  **작업 이후:** 캐시 미스(cache miss)가 발생한 경우:
    - 해당하는 `after_` 콜백을 사용하여 새로운 결과를 캐시에 해당 키로 저장합니다.

**사용 사례 예시:**
`get_stock_price(symbol)`에 대한 `before_tool_callback`이 `state[f"cache:stock:{symbol}"]`을 확인합니다. 값이 있으면 캐시된 가격을 반환하고, 없으면 API 호출을 허용한 뒤 `after_tool_callback`이 결과를 상태 키에 저장합니다.

### 5. 요청/응답 수정 { #request-response-modification }

**패턴 개요:**
데이터가 LLM/도구로 전송되기 직전이나 수신된 직후에 데이터를 변경합니다.

**구현 옵션:**
- **`before_model_callback`:** `llm_request`를 수정합니다(예: `state`를 기반으로 시스템 지침 추가).
- **`after_model_callback`:** 반환된 `LlmResponse`를 수정합니다(예: 텍스트 서식 지정, 콘텐츠 필터링).
- **`before_tool_callback`:** 도구의 `args` 딕셔너리(Java에서는 Map)를 수정합니다.
- **`after_tool_callback`:** `tool_response` 딕셔너리(Java에서는 Map)를 수정합니다.

**사용 사례 예시:**
`context.state['lang'] == 'es'`인 경우, `before_model_callback`이 `llm_request.config.system_instruction`에 "사용자 언어 설정: 스페인어"를 추가합니다.

### 6. 조건부 단계 건너뛰기 { #conditional-skipping-of-steps }

**패턴 개요:**
특정 조건에 따라 표준 작업(에이전트 실행, LLM 호출, 도구 실행)을 방지합니다.

**구현:**
- `before_` 콜백에서 값을 반환하여 정상적인 실행을 건너뜁니다:
  - `before_agent_callback`에서 `Content` 반환
  - `before_model_callback`에서 `LlmResponse` 반환
  - `before_tool_callback`에서 `dict` 반환
- 프레임워크는 이 반환된 값을 해당 단계의 결과로 해석합니다.

**사용 사례 예시:**
`before_tool_callback`이 `tool_context.state['api_quota_exceeded']`를 확인합니다. 만약 `True`이면 `{'error': 'API 할당량 초과'}`를 반환하여 실제 도구 함수가 실행되는 것을 막습니다.

### 7. 도구별 작업 (인증 및 요약 제어) { #tool-specific-actions-authentication-summarization-control }

**패턴 개요:**
주로 인증 및 도구 결과의 LLM 요약 제어와 같이 도구 라이프사이클에 특화된 작업을 처리합니다.

**구현:**
도구 콜백(`before_tool_callback`, `after_tool_callback`) 내에서 `ToolContext`를 사용합니다:

- **인증:** `before_tool_callback`에서 자격 증명이 필요하지만 찾을 수 없는 경우(예: `tool_context.get_auth_response` 또는 상태 확인을 통해), `tool_context.request_credential(auth_config)`를 호출합니다. 이는 인증 흐름을 시작합니다.
- **요약:** 도구의 원시 딕셔너리 출력을 LLM에 다시 전달하거나 직접 표시해야 할 경우(기본 LLM 요약 단계를 건너뛸 때), `tool_context.actions.skip_summarization = True`로 설정합니다.

**사용 사례 예시:**
보안 API를 위한 `before_tool_callback`은 상태에서 인증 토큰을 확인하고, 없으면 `request_credential`을 호출합니다. 구조화된 JSON을 반환하는 도구의 `after_tool_callback`은 `skip_summarization = True`를 설정할 수 있습니다.

### 8. 아티팩트 처리 { #artifact-handling }

**패턴 개요:**
에이전트 라이프사이클 동안 세션 관련 파일이나 대용량 데이터 블롭을 저장하거나 로드합니다.

**구현:**
- **저장:** `callback_context.save_artifact` / `await tool_context.save_artifact`를 사용하여 데이터를 저장합니다:
  - 생성된 보고서
  - 로그
  - 중간 데이터
- **로드:** `load_artifact`를 사용하여 이전에 저장된 아티팩트를 검색합니다.
- **추적:** 변경 사항은 `Event.actions.artifact_delta`를 통해 추적됩니다.

**사용 사례 예시:**
"generate_report" 도구의 `after_tool_callback`은 `await tool_context.save_artifact("report.pdf", report_part)`를 사용하여 출력 파일을 저장합니다. `before_agent_callback`은 `callback_context.load_artifact("agent_config.json")`를 사용하여 구성 아티팩트를 로드할 수 있습니다.

## 콜백 모범 사례

### 설계 원칙

**단일 책임 유지:**
각 콜백은 로깅, 유효성 검사 등 단 하나의 잘 정의된 목적을 갖도록 설계하십시오. 여러 기능을 합친 거대한 콜백은 피하십시오.

**성능 유의:**
콜백은 에이전트의 처리 루프 내에서 동기적으로 실행됩니다. 오래 실행되거나 블로킹되는 작업(네트워크 호출, 무거운 계산)을 피하십시오. 필요한 경우 오프로드하되, 이는 복잡성을 증가시킬 수 있음을 인지해야 합니다.

### 오류 처리

**오류를 우아하게 처리:**
- 콜백 함수 내에서 `try...except/catch` 블록을 사용하십시오.
- 오류를 적절히 로깅하십시오.
- 에이전트 호출을 중단할지 또는 복구를 시도할지 결정하십시오.
- 콜백 오류로 인해 전체 프로세스가 중단되지 않도록 하십시오.

### 상태 관리

**상태를 신중하게 관리:**
- `context.state`를 읽고 쓸 때 신중해야 합니다.
- 변경 사항은 _현재_ 호출 내에서 즉시 보이며, 이벤트 처리가 끝날 때 영구 저장됩니다.
- 의도하지 않은 부작용을 피하기 위해 광범위한 구조를 수정하기보다는 특정 상태 키를 사용하십시오.
- 특히 영구 `SessionService` 구현 시 명확성을 위해 상태 접두사(`State.APP_PREFIX`, `State.USER_PREFIX`, `State.TEMP_PREFIX`) 사용을 고려하십시오.

### 신뢰성

**멱등성 고려:**
콜백이 외부 부작용을 일으키는 작업(예: 외부 카운터 증가)을 수행하는 경우, 프레임워크나 애플리케이션의 잠재적인 재시도에 대비하여 가능하다면 멱등성(동일한 입력으로 여러 번 실행해도 안전함)을 갖도록 설계하십시오.

### 테스트 및 문서화

**철저한 테스트:**
- 모의(mock) 컨텍스트 객체를 사용하여 콜백 함수를 단위 테스트하십시오.
- 통합 테스트를 수행하여 콜백이 전체 에이전트 흐름 내에서 올바르게 작동하는지 확인하십시오.

**명확성 보장:**
- 콜백 함수에 서술적인 이름을 사용하십시오.
- 함수의 목적, 실행 시점, 부작용(특히 상태 수정)을 설명하는 명확한 독스트링(docstring)을 추가하십시오.

**올바른 컨텍스트 타입 사용:**
항상 제공된 특정 컨텍스트 타입(`CallbackContext`는 에이전트/모델용, `ToolContext`는 도구용)을 사용하여 적절한 메서드와 속성에 접근할 수 있도록 하십시오.

이러한 패턴과 모범 사례를 적용하면 콜백을 효과적으로 사용하여 ADK에서 더 견고하고, 관찰 가능하며, 맞춤화된 에이전트 동작을 만들 수 있습니다.
