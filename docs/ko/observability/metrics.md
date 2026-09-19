# 에이전트 활동 메트릭

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.32.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

Agent Development Kit(ADK)는 에이전트의 성능, 비용, 사용 패턴을 이해하는 데 도움이
되는 내장형 벤더 중립 메트릭 수집 기능을 제공합니다. 로그가 *무엇이* 일어났는지에
대한 자세한 서사를 제공한다면, 메트릭은 일이 *얼마나 자주*, *얼마나 빠르게* 일어나는지
답할 수 있는 집계된 정량 데이터를 제공합니다.

## 메트릭 철학

ADK의 메트릭 접근 방식은 가볍고 표준화되어 있으며, 선택한 모니터링 백엔드와 완전히
독립적으로 동작하도록 설계되었습니다.

*   **OpenTelemetry 시맨틱 규칙:** ADK는 OpenTelemetry(OTel)
    [GenAI 시맨틱 규칙](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-metrics.md)을
    구현합니다. 이를 통해 메트릭이 표준화되고 예측 가능한 속성 및 메트릭 이름으로 기록됩니다.
*   **OTLP 전송 형식:** ADK는 표준 OTLP 형식으로 데이터를 내보내므로, 모든
    OTel 호환 백엔드(예: Prometheus, Datadog, SigNoz, Google Cloud Monitoring)와
    자연스럽게 통합됩니다.
*   **비용 및 성능 중심:** 대규모 데이터 범위에 대한 분석에서는 메트릭이 로그나
    트레이스보다 훨씬 저렴하고 성능 효율적입니다. ADK는 LLM 애플리케이션의 핵심
    신호인 토큰 사용량, 요청 지연 시간, 도구 실행 신뢰성을 추적합니다.
*   **벤더 중립 내보내기:** ADK는 특정 메트릭 파이프라인에 종속되지 않습니다.
    표준 OTel meter provider를 인스턴스화하고 인프라 요구 사항에 맞는 위치로
    데이터를 내보낼 수 있습니다.

---

## 메트릭 스키마

메트릭을 활성화하면 ADK는 OpenTelemetry GenAI 시맨틱 규칙을 기반으로 에이전트
수명주기, 워크플로 단계, 도구 실행을 자동으로 계측합니다. 다음 핵심 메트릭이
방출됩니다.

| 메트릭 이름 | 유형 | 설명 | 주요 속성(차원) |
| :--- | :--- | :--- | :--- |
| **`gen_ai.invoke_agent.duration`** | Histogram (seconds) | 에이전트가 프롬프트를 처리하고 응답을 반환하는 데 걸린 총 시간입니다. | `gen_ai.agent.name`, `error.type` |
| **`gen_ai.invoke_workflow.duration`** | Histogram (seconds) | 워크플로를 실행하는 데 걸린 시간입니다. | `gen_ai.operation.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (중첩 워크플로만 해당), `error.type` |
| **`gen_ai.execute_tool.duration`** | Histogram (seconds) | 에이전트가 호출한 개별 도구의 실행 지연 시간입니다. 느린 외부 API를 파악하는 데 유용합니다. | `gen_ai.agent.name`, `gen_ai.tool.name`, `gen_ai.tool.type`, `error.type` |
| **`gen_ai.invoke_agent.inference_calls`** | Histogram (count) | 단일 에이전트 호출 동안 수행된 추론(모델) 호출 횟수입니다. | `gen_ai.agent.name` |
| **`gen_ai.invoke_agent.tool_calls`** | Histogram (count) | 단일 에이전트 호출 동안 수행된 도구 호출 횟수입니다. | `gen_ai.agent.name` |
| **`gen_ai.client.operation.duration`** | Histogram (seconds) | 단일 모델 `generate_content` 호출의 지연 시간입니다. | `gen_ai.agent.name`, `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `error.type` |
| **`gen_ai.client.token.usage`** | Histogram (tokens) | 모델 호출당 토큰 소비량으로, `gen_ai.token.type`에 의해 입력과 출력으로 나뉩니다. | `gen_ai.agent.name`, `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.token.type` |

### 실험적 메트릭

ADK는 `adk.experimental.*` 네임스페이스 아래에서 추가 텔레메트리를 방출하며, 이는 아래 메트릭뿐만 아니라 스팬 속성(span attributes)도 포함합니다. 이 항목들은 아직 OpenTelemetry 시맨틱 규칙의 일부가 아니므로 릴리스 간에 이름, 속성, 의미가 변경될 수 있습니다. 자유롭게 탐색해 보되, 이름이 확정되기 전까지 이를 기반으로 구축된 장기 실행 구성은 재검토가 필요할 수 있음을 염두에 두세요.

아래 메트릭은 단일 모델 호출을 측정하는 `gen_ai.client.*`보다 한 단계 높은 수준인 에이전트 호출 전체 또는 워크플로 전체에 걸쳐 토큰 소비량과 호출 횟수를 집계하므로, 모델 호출을 직접 합산하지 않고도 단일 턴의 비용을 파악할 수 있습니다.

이 메트릭들은 기본적으로 비활성화되어 있습니다. 활성화하려면 환경 변수를 설정하세요:

```bash
export ADK_EXPERIMENTAL_TELEMETRY=true
```

환경 변수보다 우선 적용되는 요청별 옵트인도 가능합니다:

```python
from google.adk.agents.run_config import RunConfig
from google.adk.telemetry import TelemetryConfig

run_config = RunConfig(
    telemetry=TelemetryConfig(adk_experimental_telemetry_opt_in=True)
)
```

둘 다 설정되지 않은 경우 아래 메트릭은 기록되지 않습니다.

8개의 `invoke_workflow` 행은 한 가지 추가 사항이 필요합니다: Vertex AI Agent Engine에서는 기본값이고 그 외 환경에서는 꺼져 있는 텔레메트리 스키마 v2입니다. 다른 환경에서는 `ADK_TELEMETRY_SCHEMA_VERSION_OPT_IN=2`를 설정해야 하며, 그렇지 않으면 해당 행은 비어 있게 됩니다. `invoke_agent` 행은 영향을 받지 않으며, `Workflow` 엔진으로 구축된 앱은 두 버전 모두에서 노드별 데이터 포인트를 기록합니다.

| 메트릭 이름 | 유형 | 설명 | 주요 속성(차원) |
| :--- | :--- | :--- | :--- |
| **`adk.experimental.invoke_agent.input_tokens`** | Histogram (tokens) | 서버 측 도구 결과 및 캐시된 프롬프트 토큰을 포함하여, 단일 에이전트 호출에 걸쳐 합산된 입력(프롬프트) 토큰입니다. | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.output_tokens`** | Histogram (tokens) | 추론 토큰 및 도구 호출 생성에 사용된 토큰을 포함하여, 단일 에이전트 호출에 걸쳐 합산된 출력(완성) 토큰입니다. | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.total_tokens`** | Histogram (tokens) | 단일 에이전트 호출에 대한 입력 및 출력 토큰의 합계입니다. | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.cache_read.input_tokens`** | Histogram (tokens) | 제공업체 관리 캐시에서 제공된 입력 토큰으로, 단일 에이전트 호출에 걸쳐 합산됩니다. | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.reasoning.output_tokens`** | Histogram (tokens) | 추론(생각의 사슬 / 확장된 생각)에 사용된 출력 토큰으로, 단일 에이전트 호출에 걸쳐 합산됩니다. | `gen_ai.agent.name` |
| **`adk.experimental.invoke_agent.tool.input_tokens`** | Histogram (tokens) | 코드 실행이나 검색 접지(grounding)와 같이 단일 요청 내에서 모델이 다시 입력으로 피드백한 서버 측 도구 결과의 입력 토큰입니다. 클라이언트 측 함수 도구의 경우 0입니다. | `gen_ai.agent.name` |
| **`adk.experimental.invoke_workflow.input_tokens`** | Histogram (tokens) | 단일 워크플로 호출에서 실행된 모든 에이전트에 걸쳐 합산된 위의 `input_tokens`입니다. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (중첩 워크플로만 해당) |
| **`adk.experimental.invoke_workflow.output_tokens`** | Histogram (tokens) | 단일 워크플로 호출에서 실행된 모든 에이전트에 걸쳐 합산된 위의 `output_tokens`입니다. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (중첩 워크플로만 해당) |
| **`adk.experimental.invoke_workflow.total_tokens`** | Histogram (tokens) | 단일 워크플로 호출에서 실행된 모든 에이전트에 걸쳐 합산된 위의 `total_tokens`입니다. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (중첩 워크플로만 해당) |
| **`adk.experimental.invoke_workflow.cache_read.input_tokens`** | Histogram (tokens) | 단일 워크플로 호출에서 실행된 모든 에이전트에 걸쳐 합산된 위의 `cache_read.input_tokens`입니다. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (중첩 워크플로만 해당) |
| **`adk.experimental.invoke_workflow.reasoning.output_tokens`** | Histogram (tokens) | 단일 워크플로 호출에서 실행된 모든 에이전트에 걸쳐 합산된 위의 `reasoning.output_tokens`입니다. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (중첩 워크플로만 해당) |
| **`adk.experimental.invoke_workflow.tool.input_tokens`** | Histogram (tokens) | 단일 워크플로 호출에서 실행된 모든 에이전트에 걸쳐 합산된 위의 `tool.input_tokens`입니다. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (중첩 워크플로만 해당) |
| **`adk.experimental.invoke_workflow.inference_calls`** | Histogram (count) | 단일 워크플로 호출 전반에서 수행된 추론(모델) 호출 횟수입니다. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (중첩 워크플로만 해당) |
| **`adk.experimental.invoke_workflow.tool_calls`** | Histogram (count) | 단일 워크플로 호출 전반에서 수행된 도구 호출 횟수입니다. | `adk.experimental.root_agent.name`, `gen_ai.workflow.name`, `gen_ai.workflow.nested` (중첩 워크플로만 해당) |

!!! warning
    중첩 워크플로는 자체 데이터 포인트를 기록하며, 해당 총계는 이를 감싸는 모든 상위 워크플로에도 합산되므로 모든 데이터 포인트에 걸쳐 `invoke_workflow` 메트릭을 합산하면 이중 계산이 발생합니다.

`gen_ai.workflow.nested` 속성은 중첩 워크플로에만 설정되므로, 이를 제외하면 가장 바깥쪽 워크플로만 남아 전체 턴을 포함하는 데이터 포인트를 얻을 수 있습니다. 워크플로 전체에 걸친 값은 단일 에이전트에 귀속될 수 없으므로 워크플로 메트릭에는 에이전트 차원이 없습니다. 대신 두 가지 이름을 갖습니다: `gen_ai.workflow.name`은 `gen_ai.invoke_workflow.duration`과 조인되며, `adk.experimental.root_agent.name`은 앱을 식별하므로 턴이 서브에이전트로 진입할 때 두 이름이 달라집니다.

---

## 메트릭 내보내기 설정

### ADK Web에서 메트릭 내보내기

`adk web` 또는 `adk api_server` CLI 명령으로 에이전트를 실행하는 경우, 메트릭
내보내기를 구성할 수 있습니다.

#### OTLP 내보내기

OTLP 호환 백엔드로 메트릭을 내보내려면 표준 OTel 환경 변수를 설정하세요.

```bash
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="http://your-collector:4318/v1/metrics"
adk web path/to/your/agents_dir
```

> **참고:** 메트릭 외에도 트레이스와 로그를 같은 엔드포인트로 보내고 싶다면 일반
> `OTEL_EXPORTER_OTLP_ENDPOINT` 환경 변수를 설정할 수도 있습니다.

#### GCP 내보내기

Google Cloud Monitoring으로 메트릭 내보내기를 활성화하려면 `--otel_to_cloud`
플래그를 사용하세요.

```bash
adk web --otel_to_cloud path/to/your/agents_dir
```

### 프로그래밍 방식 메트릭 내보내기

애플리케이션 코드에서 프로그래밍 방식으로 메트릭 내보내기를 구성할 수도 있습니다.

#### OTLP 내보내기 설정

메트릭을 활성화하고 OpenTelemetry Collector 또는 OTLP 호환 백엔드로 프로그래밍
방식으로 내보내려면 다음과 같이 설정합니다.

```python
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

os.environ["OTEL_EXPORTER_OTLP_METRICS_ENDPOINT"] = "http://your-collector:4318/v1/metrics"
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers()
```

#### GCP 내보내기 설정

Google Cloud Monitoring으로 메트릭을 프로그래밍 방식으로 내보내려면 OpenTelemetry
Google Cloud exporter를 사용합니다. 다음은 Python 예시입니다.

```python
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

gcp_exporters = get_gcp_exporters(
  enable_cloud_metrics = True,
)
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers([gcp_exporters])
```

### Kotlin 프로그래밍 방식 설정

Kotlin에서 ADK는 표준 `GlobalOpenTelemetry`를 사용하여 메트릭을 관리합니다. OpenTelemetry SDK에 `MeterProvider`를 구성하면 메트릭 수집을 활성화할 수 있습니다.

```kotlin
--8<-- "examples/kotlin/snippets/observability/SetupExample.kt:full_example"
```
