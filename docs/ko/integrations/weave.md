---
catalog_title: W&B Weave
catalog_description: 모델 호출과 에이전트 성능을 로깅하고 시각화하며 분석합니다
catalog_icon: /adk-docs/integrations/assets/weave.png
catalog_tags: ["observability"]
---
# WandB의 Weave를 사용한 에이전트 관찰 가능성

[Weights & Biases(WandB)의 Weave](https://weave-docs.wandb.ai/)는 모델 호출을 로깅하고 시각화하기 위한 강력한 플랫폼을 제공합니다. Google ADK를 Weave와 통합하면 OpenTelemetry(OTEL) 추적을 사용하여 에이전트의 성능과 동작을 추적하고 분석할 수 있습니다.

## 사전 준비 사항

1. [WandB](https://wandb.ai)에서 계정에 가입하세요.

2. [WandB Authorize](https://wandb.ai/authorize)에서 API 키를 받으세요.

3. 필요한 API 키로 환경을 설정하세요.

   ```bash
   export WANDB_API_KEY=<여러분의-wandb-api-키>
   export GOOGLE_API_KEY=<여러분의-google-api-키>
   ```

## 의존성 설치

필요한 패키지가 설치되어 있는지 확인하세요.

```bash
pip install google-adk opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

## Weave로 추적 보내기

이 예제는 Google ADK 추적을 Weave로 보내도록 OpenTelemetry를 설정하는 방법을 보여줍니다.

```python
# math_agent/agent.py

import base64
import os
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from dotenv import load_dotenv

load_dotenv()

# Weave 엔드포인트 및 인증 설정
WANDB_BASE_URL = "https://trace.wandb.ai"
PROJECT_ID = "your-entity/your-project"  # 예: "teamid/projectid"
OTEL_EXPORTER_OTLP_ENDPOINT = f"{WANDB_BASE_URL}/otel/v1/traces"

# 인증 설정
WANDB_API_KEY = os.getenv("WANDB_API_KEY")
AUTH = base64.b64encode(f"api:{WANDB_API_KEY}".encode()).decode()

OTEL_EXPORTER_OTLP_HEADERS = {
    "Authorization": f"Basic {AUTH}",
    "project_id": PROJECT_ID,
}

# 엔드포인트와 헤더로 OTLP 스팬 내보내기 도구(exporter) 생성
exporter = OTLPSpanExporter(
    endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
    headers=OTEL_EXPORTER_OTLP_HEADERS,
)

# 트레이서 프로바이더(tracer provider)를 생성하고 내보내기 도구 추가
tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))

# ADK를 가져오거나 사용하기 전에 전역 트레이서 프로바이ダー 설정
trace.set_tracer_provider(tracer_provider)

# 시연을 위한 간단한 도구 정의
def calculator(a: float, b: float) -> str:
    """두 숫자를 더하고 결과를 반환합니다.

    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자

    Returns:
        a와 b의 합
    """
    return str(a + b)

calculator_tool = FunctionTool(func=calculator)

# LLM 에이전트 생성
root_agent = LlmAgent(
    name="MathAgent",
    model="gemini-2.0-flash-exp",
    instruction=(
        "당신은 수학을 할 수 있는 도움이 되는 어시스턴트입니다. "
        "수학 문제가 주어지면 계산기 도구를 사용하여 해결하세요."
    ),
    tools=[calculator_tool],
)
```

## Weave 대시보드에서 추적 보기

에이전트가 실행되면 모든 추적 정보가 [Weave 대시보드](https://wandb.ai/home)의 해당 프로젝트에 기록됩니다.

![Weave의 추적 정보](https://wandb.github.io/weave-public-assets/google-adk/traces-overview.png)

실행 중 ADK 에이전트가 만든 호출의 타임라인을 볼 수 있습니다.

![타임라인 뷰](https://wandb.github.io/weave-public-assets/google-adk/adk-weave-timeline.gif)


## 참고 사항

- **환경 변수**: WandB와 Google API 키 모두에 대한 환경 변수가 올바르게 설정되었는지 확인하세요.
- **프로젝트 설정**: `<your-entity>/<your-project>`를 실제 WandB 엔티티 및 프로젝트 이름으로 바꾸세요.
- **엔티티 이름**: [WandB 대시보드](https://wandb.ai/home)를 방문하여 왼쪽 사이드바의 **Teams** 필드에서 엔티티 이름을 찾을 수 있습니다.
- **트레이서 프로바이더**: 적절한 추적을 보장하려면 ADK 구성 요소를 사용하기 전에 전역 트레이서 프로바이더를 설정하는 것이 매우 중요합니다.

이 단계를 따르면 Google ADK를 Weave와 효과적으로 통합하여 AI 에이전트의 모델 호출, 도구 호출 및 추론 과정을 포괄적으로 로깅하고 시각화할 수 있습니다.

## 리소스

- **[Weave로 OpenTelemetry 추적 보내기](https://weave-docs.wandb.ai/guides/tracking/otel)** - 인증 및 고급 설정 옵션을 포함하여 Weave로 OTEL을 구성하는 방법에 대한 포괄적인 가이드입니다.

- **[추적 뷰 탐색하기](https://weave-docs.wandb.ai/guides/tracking/trace-tree)** - 추적 계층 구조 및 스팬 세부 정보 이해를 포함하여 Weave UI에서 추적 정보를 효과적으로 분석하고 디버깅하는 방법을 알아보세요.

- **[Weave 통합](https://weave-docs.wandb.ai/guides/integrations/)** - 다른 프레임워크 통합을 살펴보고 Weave가 전체 AI 스택과 어떻게 작동하는지 확인하세요.
