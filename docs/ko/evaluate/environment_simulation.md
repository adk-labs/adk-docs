# 평가를 위한 환경 시뮬레이션

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.24.0</span>
</div>

API, 데이터베이스, 서드파티 서비스 같은 외부 의존성에 기대는 에이전트를 평가할 때, 테스트 중에 실제 도구를 그대로 호출하면 느리고 비싸고 불안정할 수 있습니다. **환경 시뮬레이터**는 에이전트 자체를 수정하지 않고도, 실행 중인 도구 호출을 안전하게 가로채어 제어된 결정론적 응답으로 바꿔 줍니다. 이를 통해 에이전트 로직만 분리한 hermetic 오프라인 테스트를 만들고, 안정적인 채점을 수행할 수 있습니다.

이 기능으로 다음을 할 수 있습니다.

*   API 오류나 엣지 케이스 응답을 다루는 방식을 테스트합니다.
*   라이브 백엔드 없이 오프라인으로 평가를 실행합니다.
*   LLM을 사용해 현실적인 목(mock) 응답을 자동 생성합니다.
*   확률적 주입 결과를 시드로 고정해 재현 가능한 테스트를 만듭니다.

환경 시뮬레이션은 [`before_tool_callback`](/ko/callbacks/types-of-callbacks/#tool-execution-callbacks) 훅 또는 [플러그인 시스템](/ko/plugins/)을 통해 ADK의 도구 실행 파이프라인에 통합됩니다. 따라서 에이전트 코드를 바꿀 필요가 없습니다.

```
환경 시뮬레이션은 실험적 기능입니다. 향후 릴리스에서 API가 변경될 수 있습니다.
```

## 동작 방식

[User Simulation](/ko/evaluate/user-sim/)이 대화를 앞으로 진행시키는 역할이라면, 환경 시뮬레이션은 안정적인 백엔드 역할을 합니다. 간단히 말해, 환경 시뮬레이터는 에이전트와 도구 사이에 위치합니다. 에이전트가 도구를 호출하면, 시뮬레이터가 그 호출을 가로채어 미리 정의된 주입 응답 또는 LLM 생성 목 응답을 돌려줄지, 아니면 실제 도구를 실행할지를 결정합니다.

도구별 판단 순서는 다음과 같습니다.

1.  **주입 설정(injection config)** 을 순서대로 먼저 확인합니다. 인자 매칭과 확률 조건을 만족하는 항목이 있으면, 해당 오류나 응답을 즉시 반환합니다.
2.  일치하는 주입이 없으면 **목 전략(mock strategy)** 을 사용합니다. 이때 도구 스키마와 상태 정보를 바탕으로 LLM이 현실적인 응답을 생성합니다.
3.  시뮬레이터 설정에 없는 도구라면 `None`을 반환하여 실제 도구가 정상 실행되도록 둡니다.

## 통합

`EnvironmentSimulationFactory`는 두 가지 통합 지점을 제공합니다.

*   `create_callback()` - 모든 `LlmAgent`의 `before_tool_callback`으로 사용할 수 있는 비동기 콜백을 반환합니다.
*   `create_plugin()` - ADK 플러그인 시스템과 통합되는 `EnvironmentSimulationPlugin` 인스턴스를 반환합니다.

### 콜백으로 사용

다음 예시는 환경 시뮬레이션을 ADK 에이전트 콜백 중 하나로 만드는 방법입니다.

```python
from google.adk.agents import LlmAgent
from google.adk.tools.environment_simulation import EnvironmentSimulationFactory
from google.adk.tools.environment_simulation.environment_simulation_config import (
    EnvironmentSimulationConfig,
    InjectedError,
    InjectionConfig,
    ToolSimulationConfig,
)

config = EnvironmentSimulationConfig(
    tool_simulation_configs=[
        ToolSimulationConfig(
            tool_name="get_user_profile",
            injection_configs=[
                InjectionConfig(
                    injected_error=InjectedError(
                        injected_http_error_code=503,
                        error_message="Service temporarily unavailable.",
                    )
                )
            ],
        )
    ]
)

agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    tools=[get_user_profile],
    before_tool_callback=EnvironmentSimulationFactory.create_callback(config),
)
```

### 플러그인으로 사용

다음 예시는 환경 시뮬레이션을 ADK 에이전트 플러그인으로 만드는 방법입니다.

```python
from google.adk.apps import App
from google.adk.tools.environment_simulation import EnvironmentSimulationFactory
from google.adk.tools.environment_simulation.environment_simulation_config import (
    EnvironmentSimulationConfig,
    MockStrategy,
    ToolSimulationConfig,
)

config = EnvironmentSimulationConfig(
    tool_simulation_configs=[
        ToolSimulationConfig(
            tool_name="search_products",
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
        )
    ]
)

app = App(
    agent=my_agent,
    plugins=[EnvironmentSimulationFactory.create_plugin(config)],
)
```

## 설정 레퍼런스

환경 시뮬레이터는 여러 dataclass로 구성할 수 있습니다. 아래 섹션은 각 설정 객체를 자세히 설명합니다.

### `EnvironmentSimulationConfig`

최상위 설정 객체입니다.

Field | Type | Default | Description
:--- | :--- | :--- | :---
`tool_simulation_configs` | `List[ToolSimulationConfig]` | required | 시뮬레이션할 도구별 항목입니다. 비어 있으면 안 되며 도구 이름은 고유해야 합니다.
`simulation_model` | `str` | `"gemini-2.5-flash"` | 도구 연결 분석과 목 응답 생성을 위한 LLM입니다.
`simulation_model_configuration` | `GenerateContentConfig` | thinking enabled | 내부 시뮬레이터 호출에 대한 LLM 생성 설정입니다.
`environment_data` | `str \| None` | `None` | 더 현실적인 응답 생성을 위해 목 전략에 전달하는 선택적 환경 컨텍스트입니다. 예: JSON 데이터베이스 스냅샷.
`tracing` | `str \| None` | `None` | 과거 문맥을 제공하기 위한 추적 데이터입니다. 예: 이전 에이전트 실행 trace의 JSON 문자열.

### `ToolSimulationConfig`

단일 도구를 어떻게 시뮬레이션할지 정의합니다.

Field | Type | Default | Description
:--- | :--- | :--- | :---
`tool_name` | `str` | required | 등록된 도구 이름과 정확히 일치해야 합니다.
`injection_configs` | `List[InjectionConfig]` | `[]` | 주입 설정 목록입니다. 목 전략보다 먼저 순서대로 확인합니다.
`mock_strategy_type` | `MockStrategy` | `MOCK_STRATEGY_UNSPECIFIED` | 주입이 없을 때 사용할 기본 전략입니다.

### `InjectionConfig`

도구 호출에 삽입할 단일 synthetic 응답을 제어합니다.
`injected_error` 또는 `injected_response` 중 정확히 하나만 설정해야 합니다.

Field | Type | Default | Description
:--- | :--- | :--- | :---
`injected_error` | `InjectedError \| None` | `None` | 반환할 오류입니다. `injected_response`와는 배타적입니다.
`injected_response` | `Dict[str, Any] \| None` | `None` | 반환할 고정 응답 dict입니다. `injected_error`와는 배타적입니다.
`injection_probability` | `float` | `1.0` | 이 주입이 적용될 확률입니다. 범위는 `[0.0, 1.0]` 입니다.
`match_args` | `Dict[str, Any] \| None` | `None` | 설정되면 도구 인자가 `match_args`의 키-값 쌍을 모두 포함할 때만 적용됩니다.
`injected_latency_seconds` | `float` | `0.0` | 주입 결과를 반환하기 전의 인위적 지연 시간입니다. 최대 120초입니다.
`random_seed` | `int \| None` | `None` | 확률 판정을 위한 시드입니다. 재현 가능한 주입 동작에 유용합니다.

### `InjectedError`

HTTP 스타일 오류 응답을 정의합니다.

| Field | Type | Description |
| :--- | :--- | :--- |
| `injected_http_error_code` | `int` | 도구 응답의 `error_code` 로 노출될 HTTP 상태 코드입니다. |
| `error_message` | `str` | 도구 응답의 `error_message` 로 노출될 사람이 읽을 수 있는 메시지입니다. |

### `MockStrategy`

주입이 없을 때 시뮬레이터가 응답을 생성하는 방식을 제어하는 enum입니다.

| Value | Description |
| :--- | :--- |
| `MOCK_STRATEGY_TOOL_SPEC` | 도구 스키마와 상태 문맥을 사용해 LLM이 현실적인 응답을 생성하도록 합니다. |
| `MOCK_STRATEGY_TRACING` | *(Deprecated)* 추적 입력과 함께 `MOCK_STRATEGY_TOOL_SPEC`를 사용하세요. |

## 주입 모드

주입 설정은 특정 실패나 엣지 케이스를 테스트할 때 사용합니다.
주입은 리스트 순서대로 평가되며, `match_args` 조건을 만족하고 확률 검사를 통과한 첫 항목이 적용됩니다.

### 오류 주입

다음 예시는 특정 오류 코드와 오류 메시지를 에이전트에 주입하는 방법입니다.

```python
from google.adk.tools.environment_simulation.environment_simulation_config import (
    InjectedError,
    InjectionConfig,
    ToolSimulationConfig,
)

ToolSimulationConfig(
    tool_name="charge_payment",
    injection_configs=[
        InjectionConfig(
            injected_error=InjectedError(
                injected_http_error_code=402,
                error_message="Payment declined.",
            )
        )
    ],
)
```

에이전트는 실제 도구 결과 대신 `{"error_code": 402, "error_message": "Payment declined."}` 를 받게 되며, 이를 통해 결제 실패 처리 방식을 평가할 수 있습니다.

### 고정 응답 주입

고정된 성공 응답 페이로드를 반환하려면 아래와 같이 `InjectionConfig`를 사용합니다.

```python
InjectionConfig(
    injected_response={"status": "ok", "order_id": "ORD-9999"}
)
```

### 인자 매칭 조건부 주입

특정 인자가 들어왔을 때만 주입하려면 `match_args`를 사용합니다.

```python
InjectionConfig(
    match_args={"item_id": "ITEM-404"},
    injected_error=InjectedError(
        injected_http_error_code=404,
        error_message="Item not found.",
    ),
)
```

이 경우 `item_id="ITEM-404"` 로 호출될 때만 오류가 주입됩니다. 다른 호출은 다음 주입 설정이나 목 전략으로 넘어갑니다.

### 확률적 주입

`injection_probability`를 `0.0`에서 `1.0` 사이 값으로 설정해 flaky 한 동작을 시뮬레이션할 수 있습니다. 재현 가능한 테스트를 위해 `random_seed`를 함께 고정하세요.

```python
InjectionConfig(
    injection_probability=0.3,
    random_seed=42,
    injected_error=InjectedError(
        injected_http_error_code=500,
        error_message="Internal server error.",
    ),
)
```

### 지연 주입

`injected_latency_seconds`를 사용하면 느린 백엔드 응답을 흉내낼 수 있어, timeout 처리나 성능 저하 상황의 사용자 경험을 테스트하는 데 유용합니다.

```python
InjectionConfig(
    injected_latency_seconds=5.0,
    injected_response={"result": "slow but successful"},
)
```

### 여러 주입 설정 결합

하나의 도구에 여러 주입 설정을 두면 순서대로 확인됩니다. 아래처럼 여러 시나리오를 조합할 수 있습니다.

```python
ToolSimulationConfig(
    tool_name="get_inventory",
    injection_configs=[
        # 품절 SKU는 항상 실패
        InjectionConfig(
            match_args={"sku": "OOS-001"},
            injected_response={"quantity": 0, "available": False},
        ),
        # 나머지는 20% 확률로 실패
        InjectionConfig(
            injection_probability=0.2,
            random_seed=7,
            injected_error=InjectedError(
                injected_http_error_code=503,
                error_message="Inventory service unavailable.",
            ),
        ),
    ],
)
```

## 목 전략 모드

수작업으로 값을 넣는 대신, 시뮬레이터가 그럴듯한 응답을 자동 생성하게 하려면 `MOCK_STRATEGY_TOOL_SPEC`를 사용합니다.

시뮬레이터는 LLM을 사용해 다음을 수행합니다.

1.  에이전트가 접근할 수 있는 모든 도구의 스키마를 분석하고, 도구 간 **상태 의존성**을 찾습니다.
2.  세션 동안 생성된 ID와 리소스를 추적하는 **상태 저장소**를 유지합니다.
3.  현재 상태와 도구 스키마에 맞는 응답을 생성하고, 아직 생성되지 않은 리소스를 요청하면 404 스타일 오류를 반환합니다.

```python
from google.adk.tools.environment_simulation.environment_simulation_config import (
    EnvironmentSimulationConfig,
    MockStrategy,
    ToolSimulationConfig,
)

config = EnvironmentSimulationConfig(
    tool_simulation_configs=[
        ToolSimulationConfig(
            tool_name="create_order",
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
        ),
        ToolSimulationConfig(
            tool_name="get_order",
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
        ),
        ToolSimulationConfig(
            tool_name="cancel_order",
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
        ),
    ]
)
```

이 설정에서는 `create_order`가 목 처리될 때 `order_id`가 자동 생성되고, 이후 `get_order`나 `cancel_order`가 호출되면 그 ID를 사용해 일관된 응답 또는 not-found 오류를 돌려줍니다.

### 환경 데이터 제공

도메인별 문맥을 `environment_data`로 전달하면 목 응답이 더 현실적이 됩니다. 예를 들어 데이터베이스 스냅샷이나 LLM이 참고해야 할 구조화된 문맥을 JSON 문자열로 넘길 수 있습니다.

```python
import json

db_snapshot = {
    "products": [
        {"id": "P-001", "name": "Wireless Headphones", "price": 79.99, "stock": 12},
        {"id": "P-002", "name": "USB-C Hub", "price": 34.99, "stock": 0},
    ],
    "warehouse_location": "US-WEST-2",
}

config = EnvironmentSimulationConfig(
    tool_simulation_configs=[
        ToolSimulationConfig(
            tool_name="search_products",
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
        ),
    ],
    environment_data=json.dumps(db_snapshot),
)
```

LLM은 이 데이터를 사용해 임의의 자리표시자 값 대신, 도메인에 맞는 상품명, 가격, 재고를 반환합니다.

### 추적 데이터 제공

에이전트에서 생성한 trace를 `tracing`으로 전달하면 더 현실적인 목 응답을 만들 수 있습니다.

```python
import json

agent_traces = [
    {
        "invocation_id": "inv-001",
        "user_content": {"role": "user", "parts": [{"text": "Search for high-end headphones"}]},
        "intermediate_data": {
            "tool_uses": [
                {
                    "name": "search_products",
                    "args": {"query": "high-end headphones"},
                    "response": {"products": [{"id": "P-123", "name": "Premium Wireless ANC Headphones"}]}
                }
            ]
        }
    }
]

config = EnvironmentSimulationConfig(
    tool_simulation_configs=[
        ToolSimulationConfig(
            tool_name="search_products",
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
        ),
    ],
    tracing=json.dumps(agent_traces),
)
```

LLM은 이 데이터를 사용해 도메인에 맞는 상품명, 가격, 재고를 반환합니다.

## 주입과 목 전략 함께 쓰기

같은 도구에 주입 설정과 목 전략을 함께 둘 수 있습니다. 주입이 항상 먼저 확인되고, 적용되지 않을 때만 목 전략이 동작합니다.

```python
ToolSimulationConfig(
    tool_name="send_notification",
    injection_configs=[
        # 알려진 잘못된 수신자는 항상 실패
        InjectionConfig(
            match_args={"recipient_id": "INVALID"},
            injected_error=InjectedError(
                injected_http_error_code=400,
                error_message="Invalid recipient.",
            ),
        ),
    ],
    # 그 외 수신자는 그럴듯한 성공 응답 생성
    mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
)
```
