# 에이전트 활동 추적

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.17.0</span><span class="lst-go">Go v1.0.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

ADK(Agent Development Kit)는 에이전트 아키텍처를 통과하는 요청의 엔드투엔드 흐름을 시각화할 수 있도록 분산 트레이싱(추적) 기능을 제공합니다. 메트릭은 작업에 걸린 *시간*을 알려주고 로그는 *무슨 일이 일어났는지* 알려준다면, 트레이스는 이러한 이벤트를 하나로 연결하여 시간이 정확히 *어디에서* 소요되었는지와 LLM 추론, 도구 호출, 외부 API 간의 계층적 관계를 보여줍니다.

## 트레이스 철학

트레이싱에 대한 ADK의 접근 방식은 기존 관측 가능성 스택과 원활하게 통합할 수 있도록 표준 프로토콜을 기반으로 설계되었습니다.

* **OpenTelemetry 시맨틱 규칙:** ADK는 OpenTelemetry(OTel) [GenAI 시맨틱 규칙(Semantic Conventions for GenAI)](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md)을 구현합니다. 이를 통해 트레이스 스팬(Span)과 속성이 예측 가능한 표준 이름으로 기록됩니다.
* **OTLP 전송 형식:** ADK는 표준 OTLP 형식을 사용하여 데이터를 내보내므로 모든 OTel 호환 백엔드(예: Google Cloud Trace, Jaeger, Grafana Tempo, Datadog)에 트레이스가 원활하게 통합됩니다.
* **계층적 시각화:** 트레이스는 여러 '스팬(Span)'으로 구성됩니다. 에이전트 실행은 루트 스팬이 되며, 그 아래에 LLM 작업을 위한 하위 스팬과 도구 실행을 위한 하위 스팬이 포함될 수 있습니다. 이를 통해 에이전트의 추론 루프를 한눈에 파악할 수 있는 워터폴(waterfall) 뷰가 생성됩니다.
* **컨텍스트 전파:** ADK는 프로세스 경계를 넘어 트레이스 컨텍스트를 자동으로 전파하므로, 에이전트가 도구를 통해 외부 마이크로서비스를 호출하면 해당 서비스의 스팬이 에이전트의 루트 트레이스에 연결됩니다.

---

## 트레이스 스키마

트레이싱이 활성화되면 ADK는 에이전트용 OpenTelemetry GenAI 시맨틱 규칙에 따라 주요 작업을 자동으로 계측합니다. 일반적인 트레이스 워터폴에는 다음과 같은 스팬이 포함됩니다.

| 스팬 이름 | 유형 | 설명 | 주요 속성 |
| :--- | :--- | :--- | :--- |
| **[`invoke_agent {agent.name}`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-agent-client-span)** | 클라이언트/내부 스팬 | 원격 서비스 또는 로컬을 통한 GenAI 에이전트 호출을 설명합니다. 에이전트 상호작용의 라이프사이클을 나타냅니다. | `gen_ai.operation.name`, `gen_ai.agent.name`, `gen_ai.agent.description`, `gen_ai.conversation.id` |
| **[`invoke_workflow {workflow.name}`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-workflow-span)** | 하위 스팬 | 다단계 에이전트 워크플로 호출에 대해 설명합니다. | `gen_ai.operation.name`, `gen_ai.workflow.name`, `gen_ai.conversation.id`, `gen_ai.workflow.nested` (중첩 워크플로만 해당) |
| **[`execute_tool {tool.name}`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#execute-tool-span)** | 하위 스팬 | GenAI 시스템에서 요청한 특정 도구 또는 함수 호출의 실행을 나타냅니다. | `gen_ai.operation.name`, `gen_ai.tool.name`, `gen_ai.tool.description`, `gen_ai.tool.type`, `gen_ai.tool.call.id`, `error.type` |
| **[`generate_content {model.name}`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md)** | 내부 스팬 | 콘텐츠를 생성하기 위해 GenAI SDK를 통해 기본 언어 모델을 호출하는 작업을 나타냅니다. 요청 매개변수, 응답 세부정보 및 사용량 메트릭을 추적합니다. | `gen_ai.operation.name`, `gen_ai.system`, `gen_ai.request.model`, `gen_ai.agent.name`, `gen_ai.conversation.id`, `gen_ai.response.finish_reasons`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` |

---

## 트레이스 내보내기 설정

### ADK Web에서 트레이스 내보내기

`adk web` 또는 `adk api_server` CLI 명령을 사용하여 에이전트를 실행하는 경우 트레이스 내보내기를 구성할 수 있습니다.

#### OTLP 내보내기

트레이스를 OTLP 호환 백엔드로 내보내려면 표준 OTel 환경 변수를 설정합니다.

```bash
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="http://your-collector:4318/v1/traces"
adk web path/to/your/agents_dir
```

> **참고:** 트레이스 외에 메트릭과 로그도 동일한 엔드포인트로 보내려는 경우 일반 `OTEL_EXPORTER_OTLP_ENDPOINT` 환경 변수를 설정할 수도 있습니다.


#### GCP 내보내기

Google Cloud Trace로 트레이스 내보내기를 활성화하려면 `--otel_to_cloud` 플래그를 사용하세요.

```bash
adk web --otel_to_cloud path/to/your/agents_dir
```

### 프로그래밍 방식 트레이스 내보내기

애플리케이션 코드에서 프로그래밍 방식으로 트레이스 내보내기를 구성할 수도 있습니다.

#### OTLP 내보내기 설정

트레이싱을 활성화하고 프로그래밍 방식으로 스팬을 OpenTelemetry Collector로 내보내려면 다음 안내를 따르세요.

```python
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = "http://your-collector:4318/v1/traces"
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers()
```

#### GCP 내보내기 설정

프로그래밍 방식으로 트레이스를 Google Cloud Trace로 내보내려면 OpenTelemetry Google Cloud 익스포터(exporter)를 사용하세요. 다음은 Python 예시입니다.

```python
from google.adk.telemetry.google_cloud import get_gcp_exporters
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

gcp_exporters = get_gcp_exporters(
  enable_cloud_tracing = True,
)
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers([gcp_exporters])
```

### Kotlin 프로그래밍 방식 설정

Kotlin에서 ADK는 전역 `GlobalOpenTelemetry` 인스턴스를 사용하여 트레이스를 내보냅니다. 에이전트를 시작하기 전에 OpenTelemetry SDK를 구성하세요.

```kotlin
--8<-- "examples/kotlin/snippets/observability/SetupExample.kt:full_example"
```
