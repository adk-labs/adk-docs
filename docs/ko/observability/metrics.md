# 에이전트 활동 메트릭

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.32.0</span>
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
| **`gen_ai.agent.invocation.duration`** | Histogram | 에이전트가 프롬프트를 처리하고 응답을 반환하는 데 걸린 총 시간입니다. | `gen_ai.agent.name`, `error.type` |
| **`gen_ai.tool.execution.duration`** | Histogram | 에이전트가 호출한 개별 도구의 실행 지연 시간입니다. 느린 외부 API를 찾는 데 유용합니다. | `gen_ai.tool.name`, `error.type` |
| **`gen_ai.agent.request.size`** | Histogram | 에이전트로 전송된 입력 요청의 크기 또는 복잡도입니다. | `gen_ai.agent.name` |
| **`gen_ai.agent.response.size`** | Histogram | 에이전트가 생성한 최종 응답의 크기 또는 복잡도입니다. | `gen_ai.agent.name` |
| **`gen_ai.agent.workflow.steps`** | Histogram | 에이전트가 워크플로를 완료하는 데 사용한 반복 단계 또는 추론 루프 수를 추적합니다. | `gen_ai.agent.name` |

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

Google Cloud Monitoring으로 메트릭 내보내기를 활성화하려면 `-otel_to_cloud`
플래그를 사용하세요.

```bash
adk web -otel_to_cloud path/to/your/agents_dir
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
