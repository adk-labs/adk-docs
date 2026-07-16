---
catalog_title: Google Cloud Trace
catalog_description: ADK 에이전트 상호작용을 모니터링, 디버그 및 추적합니다
catalog_icon: /integrations/assets/cloud-trace.svg
catalog_tags: ["observability", "google"]
---

# ADK용 Google Cloud Trace 관찰 가능성

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span>
</div>

로컬 개발 중에는 [ADK 웹 UI의 추적 보기](/evaluate/#debugging-with-the-trace-view)를 사용하여 에이전트 동작을 검사할 수 있습니다. 에이전트가 배포된 후에는 실제 트래픽에서 발생하는 추적 데이터를 한곳에서 모니터링할 방법이 필요합니다.

[Cloud Trace](https://cloud.google.com/trace)는 Google Cloud Observability의 분산 추적 구성 요소입니다. 대기 시간을 모니터링하고 오류를 디버그하며 애플리케이션의 성능을 향상할 수 있도록 추적 데이터를 수집하고 시각화합니다. ADK 에이전트의 경우, Cloud Trace는 각 요청이 모델 호출, 도구 실행 및 에이전트 단계를 거치며 흐르는 과정을 포착하여 프로덕션 환경의 병목 현상과 오류를 정확히 짚어낼 수 있게 해줍니다.

## 개요

Cloud Trace는 추적 데이터를 생성하기 위해 여러 언어와 수집 방법을 지원하는 오픈 소스 표준인 [OpenTelemetry](https://opentelemetry.io/)를 기반으로 구축되었습니다. 이는 OpenTelemetry 호환 계측을 활용하는 ADK 애플리케이션의 관찰 가능성 관행과 일치하며 다음을 가능하게 합니다.

- **에이전트 상호작용 추적**: Cloud Trace는 프로젝트에서 추적 데이터를 지속적으로 수집하고 분석하여 ADK 애플리케이션 내의 지연 시간 문제와 오류를 신속하게 진단할 수 있도록 합니다. 이 자동 데이터 수집은 복잡한 에이전트 워크플로에서 문제를 식별하는 프로세스를 단순화합니다.
- **문제 디버깅**: 상세한 추적을 분석하여 지연 시간 문제와 오류를 신속하게 진단합니다. 이러한 추적은 여러 서비스 간의 통신 지연 시간이 증가하거나 도구 호출과 같은 특정 에이전트 작업 중에 나타나는 문제를 이해하는 데 중요합니다.
- **심층 분석 및 시각화**: Trace Explorer는 추적을 분석하기 위한 기본 도구로, 스팬 기간에 대한 히트맵 및 스팬 비율에 대한 선형 차트와 같은 시각적 보조 기능을 제공합니다. 또한 서비스 및 작업별로 그룹화할 수 있는 스팬 테이블을 제공하여 대표적인 추적에 대한 원클릭 액세스와 에이전트 실행 경로 내의 병목 현상 및 오류 원인을 쉽게 식별할 수 있는 폭포수 보기를 제공합니다.

다음 예에서는 다음과 같은 에이전트 디렉터리 구조를 가정합니다.

```
working_dir/
├── weather_agent/
│   ├── agent.py
│   └── __init__.py
└── deploy_agent_engine.py
└── deploy_fast_api_app.py
└── agent_runner.py
```

=== "Python"
    ```python
    # weather_agent/agent.py

    import os
    from google.adk.agents import Agent

    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "{your-project-id}")
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
    os.environ.setdefault("GOOGLE_GENAI_USE_ENTERPRISE", "True")


    # 도구 함수 정의
    def get_weather(city: str) -> dict:
        """지정된 도시에 대한 현재 날씨 보고서를 검색합니다.

        Args:
            city (str): 날씨 보고서를 검색할 도시의 이름.

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
        model="gemini-flash-latest",
        description="날씨 도구를 사용하여 질문에 답변하는 에이전트.",
        instruction="답을 찾으려면 사용 가능한 도구를 사용해야 합니다.",
        tools=[get_weather],
    )
    ```

## Cloud Trace 설정

### ADK CLI 사용

ADK CLI를 사용하여 에이전트를 배포하거나 실행할 때 플래그를 추가하여 클라우드 추적을 활성화할 수 있습니다.

=== "Python"

    `adk deploy` 명령을 사용하여 에이전트를 배포할 때:

    ```bash
    adk deploy agent_engine \
        --project=$GOOGLE_CLOUD_PROJECT \
        --region=$GOOGLE_CLOUD_LOCATION \
        --trace_to_cloud \
        $AGENT_PATH
    ```

=== "Go"

    ADK Go 런처로 빌드된 에이전트를 실행할 때:

    ```bash
    adkgo web -otel_to_cloud
    ```

### 프로그래밍 방식 설정

#### ADK 앱 추상화 사용

=== "Python"

    `AdkApp` 추상화를 사용하는 경우 `enable_tracing=True`를 추가하여 클라우드 추적을 활성화할 수 있습니다.

    ```python
    from google.adk.apps import AdkApp

    adk_app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )
    ```

#### 원격 측정(telemetry) 모듈 사용

완전히 사용자 정의된 에이전트 런타임의 경우 내장된 원격 측정 모듈을 사용하여 클라우드 추적을 활성화할 수 있습니다.

=== "Python"

    ```python
    from google.adk import telemetry
    from google.adk.telemetry import google_cloud

    # GCP 내보내기 구성 가져오기
    hooks = google_cloud.get_gcp_exporters(enable_cloud_tracing=True)

    # 전역 OTel 제공자 초기화 및 설정
    telemetry.maybe_set_otel_providers(otel_hooks_to_setup=[hooks])
    ```

=== "TypeScript"

    ```typescript
    import { getGcpExporters, maybeSetOtelProviders } from '@google/adk';

    // GCP 내보내기 구성 가져오기
    const gcpExporters = await getGcpExporters({
      enableTracing: true,
    });

    // 전역 OTel 제공자 초기화 및 설정
    maybeSetOtelProviders([gcpExporters]);

    // ... 에이전트 코드 ...
    ```

=== "Go"

    ```go
    import (
    	"context"
    	"log"
    	"time"

    	"google.golang.org/adk/v2/telemetry"
    )

    func main() {
    	ctx := context.Background()

    	// 클라우드 내보내기가 활성화된 원격 측정 초기화.
    	// 기본적으로 GCP 프로젝트 ID는 GOOGLE_CLOUD_PROJECT 환경 변수에서 읽어옵니다.
    	// telemetry.WithGcpResourceProject("my-project")를 사용하여 명시적으로 지정할 수도 있습니다.
    	telemetryProviders, err := telemetry.New(ctx,
    		telemetry.WithOtelToCloud(true),
    		// telemetry.WithGcpResourceProject("your-project-id"),
    	)
    	if err != nil {
    		log.Fatalf("원격 측정 초기화 실패: %v", err)
    	}
    	defer func() {
    		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    		defer cancel()
    		if err := telemetryProviders.Shutdown(shutdownCtx); err != nil {
    			log.Printf("원격 측정 종료 실패: %v", err)
    		}
    	}()

    	// 전역 OTel 제공자로 등록
    	telemetryProviders.SetGlobalOtelProviders()

    	// ... 에이전트 코드 ...
    }
    ```

## Cloud Trace 데이터 검사

설정이 완료되면 에이전트와 상호 작용할 때마다 자동으로 추적 데이터가 Cloud Trace로 전송됩니다. [Google Cloud 콘솔](https://console.cloud.google.com/traces/explorer)의 **Trace Explorer**를 방문하여 추적을 검사할 수 있습니다.

![cloud-trace](../assets/cloud-trace1.png)

ADK 에이전트에서 생성된 모든 사용 가능한 추적을 볼 수 있으며, `invoke_agent`, `generate_content`, `call_llm`, `execute_tool`과 같은 스팬 이름을 확인할 수 있습니다.

![cloud-trace](../assets/cloud-trace2.png)

추적 중 하나를 클릭하면 로컬 ADK 웹 UI의 추적 보기와 유사하게 상세 프로세스의 폭포수 보기를 볼 수 있습니다.

![cloud-trace](../assets/cloud-trace3.png)

### 캡처된 속성(Attributes)

ADK는 에이전트의 동작을 필터링하고 분석하는 데 도움이 되도록 다음 속성으로 추적을 자동 보강합니다.

- `gen_ai.agent.name`: 실행 중인 에이전트의 이름.
- `gcp.vertex.agent.invocation_id`: 호출의 고유 ID.
- `gcp.vertex.agent.event_id`: 특정 이벤트의 ID.
- `gen_ai.conversation.id`: 세션 ID.

## 리소스

추적, OpenTelemetry 및 Google Cloud 통합에 대해 자세히 알아보려면 다음 문서를 살펴보십시오.

- [Google Cloud Trace 문서](https://cloud.google.com/trace)
- [OpenTelemetry 문서](https://opentelemetry.io/docs/)
- [Google Cloud 및 에이전트 플랫폼에 연결](/get-started/google-cloud/)
