# 에이전트 활동 로깅

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

에이전트 개발 키트(ADK)는 에이전트의 동작을 모니터링하고 문제를 효과적으로 디버깅할 수 있도록 유연하고 강력한 로깅 기능을 제공합니다.

## 로깅 철학

ADK의 로깅 접근 방식은 기본적으로 지나치게 장황하지 않으면서도 상세한 진단 정보를 제공하는 것입니다. 애플리케이션 개발자가 직접 구성할 수 있도록 설계되어, 개발 환경이든 프로덕션 환경이든 특정 요구 사항에 맞게 로그 출력을 맞춤 설정할 수 있습니다.

- **표준 라이브러리 통합:** ADK는 호스트 언어의 표준 로깅 기능(예: Python의 `logging` 모듈, Go의 `log` 패키지)을 사용합니다.
- **구조화된 GenAI 로깅:** ADK는 OpenTelemetry를 사용하여 GenAI 요청 및 응답에 대한 구조화된 이벤트를 기록하므로, 클라우드 환경에서 고급 모니터링 및 디버깅이 가능합니다.
- **사용자 구성:** ADK는 기본값 및 CLI 도구와의 통합을 제공하지만, 특정 환경에 맞게 로깅을 구성하는 것은 궁극적으로 애플리케이션 개발자의 책임입니다.

## 로깅 스키마

ADK는 표준 라이브러리 기능과 OpenTelemetry를 통한 구조화된 GenAI 이벤트를 사용하여 로그를 출력합니다.

### 구조화된 GenAI 로그

OpenTelemetry를 통해 출력되는 구조화된 GenAI 로그는 [GenAI를 위한 시맨틱 규칙(Semantic Conventions for GenAI)](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/gen-ai/gen-ai-events.md)을 따릅니다.

보안을 위해 기본적으로 프롬프트 내용은 로그에서 생략(elide)됩니다. 환경 변수 또는 프로그래밍 방식 구성을 사용하여 프롬프트 로깅을 활성화할 수 있습니다. `adk web`에 대해서는 [ADK Web에서 프롬프트 콘텐츠 캡처](#adk-web에서-프롬프트-콘텐츠-캡처)를 참조하고, 코드에서의 설정은 [프로그래밍 방식으로 프롬프트 콘텐츠 캡처](#프롬프트-콘텐츠-캡처)를 참조하세요.

### 로그 레벨 (Python)

다음 표는 표준 로거를 사용할 때 Python의 여러 레벨에서 기록되는 내용을 설명합니다.

| 레벨 | 설명 | 기록되는 정보 유형 |
| :--- | :--- | :--- |
| **`DEBUG`** | **디버깅에 매우 중요.** 세분화된 진단 정보를 위한 가장 상세한 레벨입니다. | <ul><li>**전체 LLM 프롬프트:** 시스템 지침, 기록 및 도구를 포함하여 언어 모델에 전송된 전체 요청.</li><li>서비스의 상세한 API 응답.</li><li>내부 상태 전이 및 변숫값.</li></ul> |
| **`INFO`** | 에이전트 수명 주기에 관한 일반 정보입니다. | <ul><li>에이전트 초기화 및 시작.</li><li>세션 생성 및 삭제 이벤트.</li><li>도구의 이름과 인수를 포함한 도구 실행.</li></ul> |
| **`WARNING`** | 잠재적인 문제 또는 지원 중단된(deprecated) 기능의 사용을 나타냅니다. 에이전트는 계속 작동하지만 주의가 필요할 수 있습니다. | <ul><li>지원 중단된 메서드 또는 매개변수 사용.</li><li>시스템이 복구한 치명적이지 않은 오류.</li></ul> |
| **`ERROR`** | 작업 완료를 방해한 심각한 오류입니다. | <ul><li>외부 서비스(예: LLM, 세션 서비스)에 대한 API 호출 실패.</li><li>에이전트 실행 중 처리되지 않은 예외.</li><li>구성 오류.</li></ul> |

!!! note
    프로덕션 환경에서는 `INFO` 또는 `WARNING`을 사용하는 것이 좋습니다. `DEBUG` 로그는 매우 장황할 수 있고 민감한 정보가 포함될 수 있으므로 문제를 적극적으로 해결할 때만 활성화하세요.

## ADK Web에서의 로깅

ADK의 `adk web`, `adk api_server`, `adk deploy cloud_run`, `adk deploy gke` 명령어를 사용하여 에이전트를 실행할 때 로그의 상세 수준이나 대상을 제어할 수 있습니다.

### ADK Web의 로깅 레벨

`DEBUG` 레벨 로깅으로 웹 서버를 시작하려면 다음을 실행하세요.

```bash
adk web --log_level DEBUG path/to/your/agents_dir
```

`--log_level` 옵션에 사용 가능한 로그 레벨은 `DEBUG`, `INFO`(기본값), `WARNING`, `ERROR`, `CRITICAL`입니다.

### ADK Web에서 프롬프트 콘텐츠 캡처

보안을 위해 기본적으로 프롬프트 내용은 로그에서 생략됩니다. 환경 변수를 사용하여 프롬프트 로깅을 활성화할 수 있습니다.

```bash
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

이 변수에 사용할 수 있는 값은 `NO_CONTENT`, `EVENT_ONLY`, `SPAN_ONLY`, `SPAN_AND_EVENT`입니다. 불리언 `true` 또는 `1`은 방출된 로그 이벤트에 콘텐츠를 기록하는 `EVENT_ONLY`를 의미하며, 이 네 가지 이외의 값은 `NO_CONTENT`로 폴백됩니다. 추론 스팬(inference span)에 콘텐츠를 기록하려면 `SPAN_ONLY` 및 `SPAN_AND_EVENT`에 `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`도 필요합니다.

!!! warning
    `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` 설정은 사용자 프롬프트 및 에이전트 응답의 전체 내용을 기록합니다. 이는 디버깅에 유용하지만 민감한 데이터나 개인 식별 정보(PII)가 캡처될 수 있습니다. 프로덕션 환경에서는 이를 false로 설정하거나 적절한 데이터 처리 정책이 마련되어 있는지 확인하세요.

### ADK Web에서 OTLP 내보내기

OTLP 호환 백엔드로 로그를 내보내려면 표준 OTel 환경 변수를 설정하세요.

```bash
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="http://your-collector:4318/v1/logs"
adk web path/to/your/agents_dir
```

!!! note
    로그 외에 메트릭과 트레이스도 동일한 엔드포인트로 전송하려면 일반 `OTEL_EXPORTER_OTLP_ENDPOINT` 환경 변수를 설정할 수도 있습니다.

### ADK Web에서 GCP 내보내기 설정

`--otel_to_cloud` 플래그를 사용하여 GCP 내보내기를 활성화할 수 있습니다.

```bash
adk web --otel_to_cloud path/to/your/agents_dir
```

## 프로그래밍 방식 설정

프로그래밍 방식 설정은 시스템 수준의 진단 및 프로덕션 관측 가능성을 위해 자체 코드에서 기본 로깅 프레임워크와 OpenTelemetry 내보내기(exporter)를 구성합니다. ADK는 다음 로깅 기능을 사용합니다.

- **Python:** ADK는 표준 `logging` 모듈과 구조화된 GenAI 로그를 위한 OpenTelemetry를 사용합니다.
- **Go:** ADK는 OpenTelemetry 구성을 위해 `google.golang.org/adk/v2/telemetry` 패키지를 사용하고, 일반 이벤트에는 표준 `log` 패키지를 사용하여 기본적으로 `stderr`에 기록합니다.
- **Kotlin:** ADK는 표준 JVM 로깅 기능(기본값은 Flogger)을 사용하고, 구조화된 GenAI 로그에는 OpenTelemetry를 사용합니다.

### 로깅 레벨

다음과 같이 표준 로깅 제어를 사용하여 ADK 에이전트의 로깅 레벨을 설정할 수 있습니다.

=== "Python"

    `DEBUG` 레벨 메시지를 포함한 상세 로깅을 활성화하려면 스크립트 상단에 다음 코드를 추가하세요.

    ```python
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    ```

=== "Go"

    일반 이벤트(서버 시작 또는 HTTP 요청 등)는 표준 Go `log` 패키지를 사용하여 기록되며 기본적으로 `stderr`에 작성됩니다.

=== "Kotlin"

    ADK는 표준 JVM 로깅 기능(기본값은 Flogger)을 사용합니다. 로그 상세도를 조정하려면 `java.util.logging` 또는 SLF4J와 같은 JVM 로거 백엔드를 구성하세요.

### 프롬프트 콘텐츠 캡처

=== "Python"

    환경 변수를 설정하여 프로그래밍 방식으로 전체 프롬프트 로깅을 활성화할 수 있습니다.

    ```python
    import os

    os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "true"
    ```

    프로세스 전체가 아닌 단일 실행(run)으로 콘텐츠 캡처 범위를 제한하려면 환경 변수 대신 `RunConfig.telemetry`를 설정하세요.

    ```python
    from google.adk.agents.run_config import RunConfig
    from google.adk.telemetry import ContentCapturingMode, TelemetryConfig

    run_config = RunConfig(
        telemetry=TelemetryConfig(
            capture_message_content=ContentCapturingMode.SPAN_AND_EVENT,
        ),
    )
    ```

=== "Go"

    `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true`를 내보내어 텔레메트리를 초기화할 때 전체 프롬프트 로깅을 활성화할 수 있습니다.

    ```go
    package main

    import (
    	"context"
    	"os"

    	"google.golang.org/adk/v2/telemetry"
    )

    func main() {
    	ctx := context.Background()

    	// OpenTelemetry 환경 변수를 통해 GenAI 메시지 콘텐츠 캡처 활성화
    	os.Setenv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true")

    	tp, err := telemetry.New(ctx)
    	if err != nil {
    		// 에러 처리
    	}
    	defer tp.Shutdown(ctx)
    	tp.SetGlobalOtelProviders()
    }
    ```

=== "Kotlin"

    전역 `TelemetryConfig`를 구성하여 전체 프롬프트 로깅을 활성화할 수 있습니다.

    ```kotlin
    --8<-- "examples/kotlin/snippets/observability/LoggingExamples.kt:capture_content"
    ```

### OTLP 내보내기

=== "Python"

    OpenTelemetry Collector(또는 OTLP 호환 백엔드)로 로그를 프로그래밍 방식으로 내보내려면 다음과 같이 작성합니다.

    ```python
    from google.adk.telemetry.setup import maybe_set_otel_providers
    import os

    os.environ["OTEL_EXPORTER_OTLP_LOGS_ENDPOINT"] = "http://your-collector:4318/v1/logs"
    os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
    maybe_set_otel_providers()
    ```

=== "Go"

    OTLP 호환 백엔드로 로그를 내보내려면 `OTEL_EXPORTER_OTLP_ENDPOINT` 또는 `OTEL_EXPORTER_OTLP_LOGS_ENDPOINT`와 같은 표준 OpenTelemetry 환경 변수를 구성하세요. ADK 텔레메트리 패키지는 초기화될 때 이러한 설정을 자동으로 사용합니다.

=== "Kotlin"

    ADK Kotlin의 OpenTelemetry 통합은 **트레이스만** 내보냅니다. `LoggerProvider`를 등록하지 않으므로 OTLP 로그 내보내기가 없습니다. 애플리케이션 로그는 JVM 로깅 백엔드로 이동합니다. 트레이스 내보내기를 구성하려면 [트레이스](traces.md) 문서를 참조하세요.

### GCP 내보내기 설정

=== "Python"

    Google Cloud Logging으로 로그를 프로그래밍 방식으로 내보내려면 OpenTelemetry Google Cloud 내보내기 도구를 사용하세요. 다음은 Python 예시입니다.

    ```python
    from google.adk.telemetry.google_cloud import get_gcp_exporters
    from google.adk.telemetry.setup import maybe_set_otel_providers
    import os

    gcp_exporters = get_gcp_exporters(
      enable_cloud_logging = True,
    )
    os.environ["OTEL_SERVICE_NAME"] = "your-adk-agent"
    os.environ["OTEL_RESOURCE_ATTRIBUTES"] = "key1=value1,key2=value2"
    maybe_set_otel_providers([gcp_exporters])
    ```

=== "Go"

    Google Cloud Logging으로 로그를 내보내려면 `WithOtelToCloud` 옵션을 사용하세요.

    ```go
    package main

    import (
    	"context"
    	"google.golang.org/adk/v2/telemetry"
    )

    func main() {
    	ctx := context.Background()
    	tp, err := telemetry.New(ctx,
    		telemetry.WithOtelToCloud(true),
    	)
    	if err != nil {
    		// 에러 처리
    	}
    	defer tp.Shutdown(ctx)
    	tp.SetGlobalOtelProviders()
    }
    ```

    Go 런처를 사용하는 경우 CLI 플래그를 통해 GCP 내보내기를 활성화할 수도 있습니다.

    ```bash
    go run main.go web -otel_to_cloud
    ```

=== "Kotlin"

    ADK Kotlin은 OpenTelemetry 로그 레코드를 방출하지 않으므로 Cloud Logging에서 수신할 것이 없습니다. 애플리케이션 로그는 JVM 로깅 백엔드로 전송됩니다. ADK Kotlin **트레이스**는 표준 OTLP 내보내기 도구가 `telemetry.googleapis.com`을 가리키도록 설정하여 Google Cloud로 보낼 수 있습니다. 필요한 자격 증명, 할당량 프로젝트 및 `roles/telemetry.writer` 권한 부여에 대한 자세한 내용은 [Google Cloud와 함께 OTLP 사용](https://cloud.google.com/stackdriver/docs/otlp/overview)을 참조하세요.

## 플러그인을 사용한 활동 로깅

ADK는 사용자 메시지, 모델 요청 및 응답, 도구 호출, 그리고(`DebugLoggingPlugin` 사용 시) 세션 상태를 포함한 에이전트 활동을 캡처하는 내장 플러그인을 제공합니다. 이러한 플러그인은 에이전트 로직을 변경할 필요가 없습니다.

### `LoggingPlugin`을 사용한 콘솔 로깅

실행 중에 콘솔에 구조화된 활동 로그를 출력하려면 `App`에 `LoggingPlugin`을 연결하세요.

=== "Python"

    ```python
    from google.adk.apps import App
    from google.adk.plugins import LoggingPlugin

    app = App(
        name="my_app",
        root_agent=root_agent,
        plugins=[LoggingPlugin()],
    )
    ```

=== "Go"

    ```go
    package main

    import (
    	"context"
    	"log"
    	"os"

    	"google.golang.org/adk/v2/agent"
    	"google.golang.org/adk/v2/cmd/launcher"
    	"google.golang.org/adk/v2/cmd/launcher/full"
    	"google.golang.org/adk/v2/plugin"
    	"google.golang.org/adk/v2/plugin/loggingplugin"
    	"google.golang.org/adk/v2/runner"
    )

    func main() {
    	ctx := context.Background()
    	logPlugin := loggingplugin.MustNew("logging_plugin")

    	config := &launcher.Config{
    		AgentLoader: agent.NewSingleLoader(rootAgent),
    		PluginConfig: runner.PluginConfig{
    			Plugins: []*plugin.Plugin{logPlugin},
    		},
    	}

    	l := full.NewLauncher()
    	if err := l.Execute(ctx, config, os.Args[1:]); err != nil {
    		log.Fatalf("run failed: %v", err)
    	}
    }
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/observability/LoggingExamples.kt:logging_plugin"
    ```

### `DebugLoggingPlugin`을 사용하여 파일로 전체 디버그 캡처

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.23.0</span><span class="lst-kotlin">Kotlin v0.6.0</span>
</div>

축약된 콘솔 출력 대신 사람이 읽을 수 있는 YAML 형식으로 전체 상호작용 데이터를 `adk_debug.yaml`에 추가하여 기록하려면 `DebugLoggingPlugin`을 사용하세요.

=== "Python"

    ```python
    from google.adk.apps import App
    from google.adk.plugins import DebugLoggingPlugin

    app = App(
        name="my_app",
        root_agent=root_agent,
        plugins=[
            DebugLoggingPlugin(
                output_path="adk_debug.yaml",
                include_session_state=True,
                include_system_instruction=True,
            ),
        ],
    )
    ```

=== "Kotlin"

    ```kotlin
    --8<-- "examples/kotlin/snippets/observability/LoggingExamples.kt:debug_logging_plugin"
    ```

!!! warning
    출력 파일에는 원시 프롬프트, 도구 인수, 세션 상태가 포함됩니다. ADK는 Python에서 자격 증명 및 `temp:` 범위의 상태 키를 자동으로 수정(redact)하지만, 출력 파일을 민감한 파일로 취급하세요.

## 로그 출력 이해

### Python 로그 항목 샘플

```text
2025-07-08 11:22:33,456 - DEBUG - google_adk.google.adk.models.google_llm - LLM Request: contents { ... }
```

| 로그 세그먼트 | 포맷 지정자 | 의미 |
| ------------------------------- | ---------------- | ---------------------------------------------- |
| `2025-07-08 11:22:33,456`       | `%(asctime)s`    | 타임스탬프 |
| `DEBUG`                         | `%(levelname)s`  | 심각도 레벨 |
| `google_adk.google.adk.models.google_llm`  | `%(name)s`       | 로거 이름 (로그를 생성한 모듈) |
| `LLM Request: contents { ... }` | `%(message)s`    | 실제 로그 메시지 |

로거 이름을 확인하여 로그의 소스를 즉시 파악하고 에이전트 아키텍처 내에서의 컨텍스트를 이해할 수 있습니다. ADK 로거의 이름은 `google_adk.` 뒤에 모듈의 정규화된 이름(fully-qualified name)이 붙으므로 모든 ADK 로거는 `google_adk` 로거의 하위 로거입니다. `logging.getLogger("google_adk")`를 사용하여 그룹으로 구성할 수 있습니다.

### 디버깅 예시

`DEBUG` 로깅을 활성화한 후(위의 [로깅 레벨](#로깅-레벨) 참조), 에이전트를 실행하고 `google_adk.google.adk.models.google_llm` 로거의 메시지를 확인하세요. 출력에는 전체 LLM 요청과 응답이 표시됩니다.

```text
2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm -
LLM Request:
-----------------------------------------------------------
System Instruction:
      You roll dice and answer questions about the outcome of the dice rolls.
      ...
-----------------------------------------------------------
Contents:
{"parts":[{"text":"Roll a 6 sided dice"}],"role":"user"}
{"parts":[{"function_call":{"args":{"sides":6},"name":"roll_die"}}],"role":"model"}
{"parts":[{"function_response":{"name":"roll_die","response":{"result":2}}}],"role":"user"}
-----------------------------------------------------------
Functions:
roll_die: {'sides': {'type': <Type.INTEGER: 'INTEGER'>}}
check_prime: {'nums': {'items': {'type': <Type.INTEGER: 'INTEGER'>}, 'type': <Type.ARRAY: 'ARRAY'>}}
-----------------------------------------------------------
2025-07-10 15:26:14,309 - INFO - google_adk.google.adk.models.google_llm -
LLM Response:
-----------------------------------------------------------
Text:
I have rolled a 6 sided die, and the result is 2.
...
```

이 출력에서 다음 사항을 확인할 수 있습니다.

- 시스템 지침이 정확한가요?
- 대화 기록(`user` 및 `model` 턴)이 정확한가요?
- 모델에 올바른 도구가 제공되고 있나요?
- 모델이 도구를 올바르게 호출하고 있나요?
- 모델이 응답하는 데 얼마나 걸리나요?
