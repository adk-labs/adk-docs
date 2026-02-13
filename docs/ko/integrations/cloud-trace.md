---
catalog_title: Google Cloud Trace
catalog_description: ADK 에이전트 상호작용을 모니터링하고 디버그하며 추적합니다
catalog_icon: /adk-docs/integrations/assets/cloud-trace.svg
catalog_tags: ["observability", "google"]
---
# Cloud Trace를 사용한 에이전트 관찰 가능성

ADK를 사용하면 [여기](https://google.github.io/adk-docs/evaluate/#debugging-with-the-trace-view)에서 설명하는 강력한 웹 개발 UI를 활용하여 로컬에서 에이전트 상호 작용을 검사하고 관찰할 수 있습니다. 그러나 클라우드 배포를 목표로 하는 경우 실제 트래픽을 관찰하기 위한 중앙 집중식 대시보드가 필요합니다.

Cloud Trace는 Google Cloud Observability의 구성 요소입니다. 추적 기능에 특히 중점을 두어 애플리케이션의 성능을 모니터링, 디버깅 및 개선하기 위한 강력한 도구입니다. ADK(Agent Development Kit) 애플리케이션의 경우 Cloud Trace는 포괄적인 추적을 지원하여 요청이 에이전트의 상호 작용을 통해 어떻게 흐르는지 이해하고 AI 에이전트 내의 성능 병목 현상이나 오류를 식별하는 데 도움을 줍니다.

## 개요

Cloud Trace는 추적 데이터를 생성하기 위한 다양한 언어와 수집 방법을 지원하는 오픈 소스 표준인 [OpenTelemetry](https://opentelemetry.io/)를 기반으로 구축되었습니다. 이는 OpenTelemetry와 호환되는 계측을 활용하는 ADK 애플리케이션의 관찰 가능성 관행과 일치하며 다음을 수행할 수 있습니다.

- 에이전트 상호 작용 추적: Cloud Trace는 프로젝트에서 추적 데이터를 지속적으로 수집하고 분석하여 ADK 애플리케이션 내의 지연 시간 문제와 오류를 신속하게 진단할 수 있도록 합니다. 이 자동 데이터 수집은 복잡한 에이전트 워크플로에서 문제를 식별하는 프로세스를 단순화합니다.
- 문제 디버깅: 상세한 추적을 분석하여 지연 시간 문제와 오류를 신속하게 진단합니다. 여러 서비스 간의 통신 지연 시간이 증가하거나 도구 호출과 같은 특정 에이전트 작업 중에 나타나는 문제를 이해하는 데 중요합니다.
- 심층 분석 및 시각화: Trace Explorer는 추적을 분석하기 위한 기본 도구로, 스팬 기간에 대한 히트맵 및 요청/오류율에 대한 꺾은선형 차트와 같은 시각적 보조 기능을 제공합니다. 또한 서비스 및 작업별로 그룹화할 수 있는 스팬 테이블을 제공하여 대표적인 추적에 대한 원클릭 액세스와 에이전트 실행 경로 내의 병목 현상 및 오류 원인을 쉽게 식별할 수 있는 폭포수 보기를 제공합니다.

다음 예에서는 다음 에이전트 디렉터리 구조를 가정합니다.

```
working_dir/
├── weather_agent/
│   ├── agent.py
│   └── __init__.py
└── deploy_agent_engine.py
└── deploy_fast_api_app.py
└── agent_runner.py
```

```python
# weather_agent/agent.py

import os
from google.adk.agents import Agent

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "{your-project-id}")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


# 도구 함수 정의
def get_weather(city: str) -> dict:
    """지정된 도시에 대한 현재 날씨 보고서를 검색합니다.

    Args:
        city (str): 날씨 보고서를 검색할 도시의 이름입니다.

    Returns:
        dict: 상태 및 결과 또는 오류 메시지.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "뉴욕의 날씨는 맑고 기온은 섭씨 25도(화씨 77도)입니다."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"'{city}'에 대한 날씨 정보를 사용할 수 없습니다.",
        }


# 도구가 있는 에이전트 생성
root_agent = Agent(
    name="weather_agent",
    model="gemini-2.5-flash",
    description="날씨 도구를 사용하여 질문에 답변하는 에이전트.",
    instruction="답을 찾으려면 사용 가능한 도구를 사용해야 합니다.",
    tools=[get_weather],
)
```

## Cloud Trace 설정

### 에이전트 엔진 배포를 위한 설정

#### 에이전트 엔진 배포 - ADK CLI에서

`adk deploy agent_engine` 명령을 사용하여 에이전트를 배포할 때 `--trace_to_cloud` 플래그를 추가하여 클라우드 추적을 활성화할 수 있습니다.

```bash
adk deploy agent_engine \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --staging_bucket=$STAGING_BUCKET \
    --trace_to_cloud \
    $AGENT_PATH
```

#### 에이전트 엔진 배포 - Python SDK에서

Python SDK를 사용하는 것을 선호하는 경우 `AdkApp` 객체를 초기화할 때 `enable_tracing=True`를 추가하여 클라우드 추적을 활성화할 수 있습니다.

```python
# deploy_agent_engine.py

from vertexai.preview import reasoning_engines
from vertexai import agent_engines
from weather_agent.agent import root_agent

import vertexai

PROJECT_ID = "{your-project-id}"
LOCATION = "{your-preferred-location}"
STAGING_BUCKET = "{your-staging-bucket}"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

adk_app = reasoning_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)


remote_app = agent_engines.create(
    agent_engine=adk_app,
    extra_packages=[
        "./weather_agent",
    ],
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
    ],
)
```

### Cloud Run 배포를 위한 설정

#### Cloud Run 배포 - ADK CLI에서

`adk deploy cloud_run` 명령을 사용하여 에이전트를 배포할 때 `--trace_to_cloud` 플래그를 추가하여 클라우드 추적을 활성화할 수 있습니다.

```bash
adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --trace_to_cloud \
    $AGENT_PATH
```

클라우드 추적을 활성화하고 Cloud Run에서 사용자 지정 에이전트 서비스 배포를 사용하려면 아래의 [사용자 지정 배포를 위한 설정](#setup-for-customized-deployment) 섹션을 참조하세요.

### 사용자 지정 배포를 위한 설정

#### 내장 `get_fast_api_app` 모듈에서

자신만의 에이전트 서비스를 사용자 지정하려면 내장 `get_fast_api_app` 모듈을 사용하여 FastAPI 앱을 초기화하고 `trace_to_cloud=True`를 설정하여 클라우드 추적을 활성화할 수 있습니다.

```python
# deploy_fast_api_app.py

import os
from google.adk.cli.fast_api import get_fast_api_app
from fastapi import FastAPI

# 클라우드 추적을 위해 GOOGLE_CLOUD_PROJECT 환경 변수 설정
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "alvin-exploratory-2")

# 현재 작업 디렉터리에서 `weather_agent` 디렉터리 검색
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 클라우드 추적이 활성화된 FastAPI 앱 생성
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    trace_to_cloud=True,
)

app.title = "weather-agent"
app.description = "에이전트 weather-agent와 상호 작용하기 위한 API"


# 기본 실행
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
```


#### 사용자 지정 에이전트 실행기에서

ADK 에이전트 런타임을 완전히 사용자 지정하려면 Opentelemetry의 `CloudTraceSpanExporter` 모듈을 사용하여 클라우드 추적을 활성화할 수 있습니다.

```python
# agent_runner.py

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from weather_agent.agent import root_agent as weather_agent
from google.genai.types import Content, Part
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import export
from opentelemetry.sdk.trace import TracerProvider

APP_NAME = "weather_agent"
USER_ID = "u_123"
SESSION_ID = "s_123"

provider = TracerProvider()
processor = export.BatchSpanProcessor(
    CloudTraceSpanExporter(project_id="{your-project-id}")
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

session_service = InMemorySessionService()
runner = Runner(agent=weather_agent, app_name=APP_NAME, session_service=session_service)


async def main():
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    if session is None:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )

    user_content = Content(
        role="user", parts=[Part(text="파리의 날씨는 어떤가요?")]
    )

    final_response_content = "응답 없음"
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response_content = event.content.parts[0].text

    print(final_response_content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```

## Cloud Trace 검사

설정이 완료되면 에이전트와 상호 작용할 때마다 자동으로 추적 데이터가 Cloud Trace로 전송됩니다. [console.cloud.google.com](https://console.cloud.google.com)으로 이동하여 구성된 Google Cloud 프로젝트에서 Trace Explorer를 방문하여 추적을 검사할 수 있습니다.

![cloud-trace](../assets/cloud-trace1.png)

그러면 `invocation`, `agent_run`, `call_llm` 및 `execute_tool`과 같은 여러 스팬 이름으로 구성된 ADK 에이전트에서 생성된 모든 사용 가능한 추적을 볼 수 있습니다.

![cloud-trace](../assets/cloud-trace2.png)

추적 중 하나를 클릭하면 `adk web` 명령을 사용하여 웹 개발 UI에서 보는 것과 유사한 상세 프로세스의 폭포수 보기를 볼 수 있습니다.

![cloud-trace](../assets/cloud-trace3.png)

## 리소스

- [Google Cloud Trace 문서](https://cloud.google.com/trace)
