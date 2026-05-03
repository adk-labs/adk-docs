---
catalog_title: MLflow Tracing
catalog_description: 에이전트 실행, 도구 호출 및 모델 요청에 대한 OpenTelemetry 추적을 수집합니다.
catalog_icon: /integrations/assets/mlflow.png
catalog_tags: ["observability"]
---


# ADK에 대한 MLflow 관측 가능성

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[MLflow Tracing](https://mlflow.org/docs/latest/genai/tracing/)는 다음을 제공합니다
OpenTelemetry(OTel) 추적 수집을 위한 최고 수준의 지원입니다. Google ADK는
보낼 수 있는 에이전트 실행, 도구 호출 및 모델 요청을 위한 OTel 범위
분석 및 디버깅을 위해 MLflow 추적 서버에 직접 연결됩니다.

## 전제조건

- MLflow 버전 3.6.0 이상. OpenTelemetry 수집은 다음에서만 지원됩니다.
  MLflow 3.6.0+.
- SQL 기반 백엔드 저장소(예: SQLite, PostgreSQL, MySQL). 파일 기반 저장소
  OTLP 수집을 지원하지 않습니다.
- 귀하의 환경에 Google ADK가 설치되어 있습니다.

## 종속성 설치

```bash
pip install "mlflow>=3.6.0" google-adk opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

## MLflow 추적 서버 시작

SQL 백엔드 및 포트(이 예에서는 5000)를 사용하여 MLflow를 시작합니다.

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000
```

`--backend-store-uri`를 다른 SQL 백엔드(PostgreSQL, MySQL,
MSSQL). 파일 기반 백엔드에서는 OTLP 수집이 지원되지 않습니다.

## OpenTelemetry 구성(필수)

먼저 OTLP 내보내기를 구성하고 글로벌 추적 공급자를 설정해야 합니다.
범위가 MLflow로 내보내지도록 ADK 구성 요소를 사용합니다.

가져오기 전에 코드에서 OTLP 내보내기 및 전역 추적 프로그램 공급자를 초기화합니다.
또는 ADK 에이전트/도구 구성:

```python
# my_agent/agent.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

exporter = OTLPSpanExporter(
    endpoint="http://localhost:5000/v1/traces",
    headers={"x-mlflow-experiment-id": "123"}  # replace with your experiment id
)

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(exporter))
trace.set_tracer_provider(provider)  # set BEFORE importing/using ADK
```

이는 OpenTelemetry 파이프라인을 구성하고 ADK 범위를 MLflow로 보냅니다.
실행될 때마다 서버.

## 예: ADK 에이전트 추적

이제 간단한 수학 에이전트에 대한 에이전트 코드를 추가할 수 있습니다.
OTLP 내보내기 및 추적 프로그램 공급자를 설정합니다.

```python
# my_agent/agent.py
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool


def calculator(a: float, b: float) -> str:
    """Add two numbers and return the result."""
    return str(a + b)


calculator_tool = FunctionTool(func=calculator)

root_agent = LlmAgent(
    name="MathAgent",
    model="gemini-flash-latest",
    instruction=(
        "You are a helpful assistant that can do math. "
        "When asked a math problem, use the calculator tool to solve it."
    ),
    tools=[calculator_tool],
)
```

다음을 사용하여 에이전트를 실행합니다.

```bash
adk run my_agent
```

그리고 수학 문제를 물어보세요.

```console
What is 12 + 34?
```

그러면 다음과 유사한 출력이 표시됩니다.

```console
[MathAgent]: The answer is 46.
```

## MLflow에서 추적 보기

`http://localhost:5000`에서 MLflow UI를 열고 실험을 선택한 다음
ADK 에이전트에서 생성된 추적 트리와 범위를 검사합니다.

![MLflow Traces](https://mlflow.org/docs/latest/images/llms/tracing/google-adk-tracing.png)

## 팁

- ADK 개체를 가져오거나 초기화하기 전에 추적 공급자를 설정하여 모든
  스팬이 캡처됩니다.
- 프록시 뒤나 원격 호스트에서 `localhost:5000`를 서버로 교체하세요.
  주소.

## 리소스

- [MLflow Tracing Documentation](https://mlflow.org/docs/latest/genai/tracing/):
  다른 라이브러리를 다루는 MLflow Tracing에 대한 공식 문서
  평가, 모니터링과 같은 추적의 통합 및 다운스트림 사용
  검색 등이 있습니다.
- [OpenTelemetry in MLflow](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/):
  MLflow와 함께 OpenTelemetry를 사용하는 방법에 대한 자세한 가이드입니다.
- [MLflow for Agents](https://mlflow.org/docs/latest/genai/): 종합
  프로덕션용 에이전트를 구축하기 위해 MLflow를 사용하는 방법에 대한 가이드입니다.
