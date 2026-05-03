# 에이전트 활동 추적

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.17.0</span><span class="lst-go">Go v1.0.0</span>
</div>

ADK(에이전트 개발 키트)는 에이전트 아키텍처를 통해 이동하는 요청의 엔드투엔드 여정을 시각화하는 데 도움이 되는 분산 추적 기능을 제공합니다. 측정항목은 프로세스에 걸린 *시간*을 알려주고 로그는 *무슨 일이 일어났는지* 알려주지만, 추적은 이러한 이벤트를 연결하여 시간이 소요된 정확한 *어디*와 LLM 추론, 도구 호출 및 외부 API 간의 계층적 관계를 보여줍니다.

## 철학의 흔적

추적에 대한 ADK의 접근 방식은 기존 관찰 가능성 스택과의 원활한 통합을 보장하기 위해 표준 프로토콜을 기반으로 구축되었습니다.

* **OpenTelemetry 의미 규칙:** ADK는 OpenTelemetry(OTel) [Semantic Conventions for GenAI](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md)를 구현합니다. 이렇게 하면 추적 범위와 속성이 예측 가능한 표준 이름으로 기록됩니다.
* **OTLP Wire 형식:** ADK는 표준 OTLP 형식을 사용하여 데이터를 내보내므로 추적이 모든 OTel 호환 백엔드(예: Google Cloud Trace, Jaeger, Grafana Tempo, Datadog)에 원활하게 통합됩니다.
* **계층적 시각화:** 추적은 '범위'로 구성됩니다. 에이전트 실행은 LLM 작업을 위한 하위 범위를 포함하는 루트 범위이며, 도구 실행을 위한 하위 범위를 포함할 수 있습니다. 이는 에이전트의 추론 루프에 대한 명확한 "폭포" 보기를 생성합니다.
* **컨텍스트 전파:** ADK는 프로세스 경계를 ​​넘어 추적 컨텍스트를 자동으로 전달하여 에이전트가 도구를 통해 외부 마이크로서비스를 호출하는 경우 해당 서비스의 범위가 에이전트의 루트 추적에 연결되도록 합니다.

---

## 스키마 추적

추적이 활성화되면 ADK는 에이전트에 대한 OpenTelemetry GenAI 의미 체계 규칙에 따라 주요 작업을 자동으로 계측합니다. 일반적인 추적 폭포에는 다음 범위가 포함됩니다.

| 스팬 이름 | 유형 | 설명 | 주요 속성 |
| :--- | :--- | :--- | :--- |
| **[`invoke_agent`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-agent-client-span)** | 클라이언트/내부 범위 | 원격 서비스 또는 로컬을 통한 GenAI 에이전트 호출을 설명합니다. 에이전트 상호작용의 수명주기를 나타냅니다.| `gen_ai.agent.name`, `gen_ai.system` |
| **[`invoke_workflow`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#invoke-workflow-span)** | 하위 스팬 | 다단계 에이전트 워크플로 호출에 대해 설명합니다. | `gen_ai.workflow.name`, `gen_ai.system`|
| **[`execute_tool`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-agent-spans.md#execute-tool-span)** | 하위 스팬 | GenAI 시스템에서 요청한 특정 도구 또는 기능 호출의 실행을 나타냅니다.| `gen_ai.tool.name`, `gen_ai.system`|
| **[`generate_content {model.name}`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-spans.md)** | 내부 스팬 | 콘텐츠를 생성하기 위해 GenAI SDK를 통해 기본 언어 모델을 호출하는 것을 나타냅니다. 요청 매개변수, 응답 세부정보 및 사용량 측정항목을 추적합니다. | `gen_ai.operation.name`, `gen_ai.system`, `gen_ai.request.model`, `gen_ai.agent.name`, `gen_ai.conversation.id`, `user.id`, `gen_ai.request.top_p`, `gen_ai.request.max_tokens`, `gen_ai.response.finish_reasons`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens` |

---

## 추적 내보내기 설정

### ADK 웹에서 추적 내보내기

`adk web` 또는 `adk api_server` CLI 명령을 사용하여 에이전트를 실행하는 경우 추적 내보내기를 구성할 수 있습니다.

#### OTLP 내보내기

추적을 OTLP 호환 백엔드로 내보내려면 표준 OTel 환경 변수를 설정합니다.

```bash
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="http://your-collector:4318/v1/traces"
adk web path/to/your/agents_dir
```

> **참고:** 추적 외에 측정항목과 로그를 동일한 엔드포인트로 보내려는 경우 일반 `OTEL_EXPORTER_OTLP_ENDPOINT` 환경 변수를 설정할 수도 있습니다.


#### GCP 내보내기

Google Cloud Trace로 추적 내보내기를 활성화하려면 `-otel_to_cloud` 플래그를 사용하세요.

```bash
adk web -otel_to_cloud path/to/your/agents_dir
```

### 프로그래밍 방식 추적 내보내기

애플리케이션 코드에서 프로그래밍 방식으로 추적 내보내기를 구성할 수도 있습니다.

#### OTLP 내보내기 설정

추적을 활성화하고 프로그래밍 방식으로 범위를 OpenTelemetry Collector로 내보내려면 다음 안내를 따르세요.

```python
from google.adk.telemetry.setup import maybe_set_otel_providers
import os

os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = "http://your-collector:4318/v1/traces"
os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
maybe_set_otel_providers()
```

#### GCP 내보내기 설정

프로그래밍 방식으로 추적을 Google Cloud Trace로 내보내려면 OpenTelemetry Google Cloud 내보내기 도구를 사용하세요. 다음은 Python의 예입니다.

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
