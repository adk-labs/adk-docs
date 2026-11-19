---
catalog_title: MLflow Tracing
catalog_description: 에이전트 실행, 도구 호출 및 모델 요청에 대한 OpenTelemetry 추적을 수집합니다.
catalog_icon: /integrations/assets/mlflow.png
catalog_tags: ["observability"]
---


# ADK용 MLflow 관측 가능성

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[MLflow Tracing](https://mlflow.org/docs/latest/genai/tracing/)은 OpenTelemetry(OTel) 트레이스 수집을 기본 수준으로 지원합니다. Google ADK는 에이전트 실행, 도구 호출, 모델 요청에 대한 OTel 스팬(span)을 생성하며, 이를 MLflow 추적 서버(Tracking Server)로 직접 전송하여 분석하고 디버깅할 수 있습니다.

## 사전 요구사항

- MLflow 버전 3.6.0 이상 (OpenTelemetry 수집은 MLflow 3.6.0 이상에서만 지원됨)
- SQL 기반 백엔드 저장소(예: SQLite, PostgreSQL, MySQL). 파일 기반 저장소는 OTLP 수집을 지원하지 않습니다.
- 실행 환경에 설치된 Google ADK

## 종속성 설치

```bash
pip install "mlflow>=3.6.0" google-adk opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
```

## MLflow 추적 서버 시작

SQL 백엔드와 포트(이 예시에서는 5000)를 지정하여 MLflow 서버를 시작합니다:

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000
```

`--backend-store-uri`에 다른 SQL 백엔드(PostgreSQL, MySQL, MSSQL)를 지정할 수도 있습니다. 파일 기반 백엔드에서는 OTLP 수집이 지원되지 않습니다.

## OpenTelemetry 구성(필수)

스팬이 MLflow로 전송되도록 하려면 ADK 구성 요소를 사용하기 전에 반드시 OTLP 익스포터(exporter)를 구성하고 전역 트레이서 프로바이더(TracerProvider)를 설정해야 합니다.

ADK 에이전트나 도구를 임포트하거나 생성하기 전에 코드에서 OTLP 익스포터와 전역 트레이서 프로바이더를 초기화하세요:

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

이렇게 하면 OpenTelemetry 파이프라인이 구성되어 실행될 때마다 ADK 스팬이 MLflow 서버로 전송됩니다.

## 예시: ADK 에이전트 트레이싱

OTLP 익스포터와 트레이서 프로바이더를 설정하는 코드 뒤에 간단한 수학 에이전트 코드를 추가할 수 있습니다:

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

## MLflow에서 트레이스 보기

`http://localhost:5000`에서 MLflow UI를 열고 실험을 선택한 다음, ADK 에이전트에서 생성된 트레이스 트리와 스팬을 검사합니다.

![MLflow Traces](https://mlflow.org/docs/latest/images/llms/tracing/google-adk-tracing.png)

## 팁

- 모든 스팬이 캡처되도록 ADK 객체를 임포트하거나 초기화하기 전에 트레이서 프로바이더를 먼저 설정하세요.
- 프록시 환경이나 원격 호스트에서는 `localhost:5000`을 실제 서버 주소로 변경하세요.

## 리소스

- [MLflow Tracing Documentation](https://mlflow.org/docs/latest/genai/tracing/): 다른 라이브러리 연동과 평가, 모니터링, 검색 등 트레이스의 다운스트림 활용법을 다루는 MLflow Tracing 공식 문서입니다.
- [OpenTelemetry in MLflow](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/): MLflow에서 OpenTelemetry를 사용하는 방법에 대한 상세 가이드입니다.
- [MLflow for Agents](https://mlflow.org/docs/latest/genai/): 프로덕션용 에이전트를 구축하기 위해 MLflow를 활용하는 방법에 대한 종합 가이드입니다.
