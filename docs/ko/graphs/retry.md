# 재시도 및 타임아웃으로 노드 실패 처리하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원됨</span><span class="lst-python">Python v2.0.0</span><span class="lst-typescript">TypeScript v2.0.0</span><span class="lst-go">Go v2.0.0</span><span class="lst-java">Java v1.14.0</span><span class="lst-kotlin">Kotlin v1.2.0</span>
</div>

그래프 기반 워크플로우의 노드는 모델 API, 원격 도구, 데이터베이스와 같이 간헐적으로 실패하거나 응답이 느린 서비스를 호출하는 경우가 많습니다. Agent Development Kit(ADK)를 사용하면 각 노드에 재시도 정책(retry policy)과 타임아웃(timeout)을 연결할 수 있으므로, 노드가 전체 워크플로우를 실패시키지 않고도 일시적인 오류에서 복구할 수 있으며, 지연된 노드가 워크플로우를 차단하는 대신 설정된 시간 후에 실패하도록 할 수 있습니다. 재시도 및 타임아웃 기능을 사용하여 다음을 수행하세요.

-   연결 오류로 실패한 도구 호출을 재시도하되, 원격 서비스가 복구할 시간을 가질 수 있도록 각 시도 사이의 대기 시간을 점점 늘립니다.
-   30초 이내에 응답하지 않은 모델 호출을 중지하고 다시 시도합니다.
-   두 번째 시도에서 성공할 가능성이 있는 오류만 재시도하고 다른 모든 오류에서는 즉시 실패하도록 처리합니다.

재시도 정책이 있는 노드는 실패할 경우 시도가 성공하거나 최대 시도 횟수에 도달할 때까지 다시 실행됩니다. 최대 시도 횟수에 도달한 후에야 실패가 나머지 워크플로우로 전달됩니다. 재시도 정책이 없는 노드는 재시도되지 않습니다.

!!! example "TypeScript, Java 및 Kotlin에서 실험적 기능"
    ADK TypeScript, ADK Java 및 ADK Kotlin에서 노드 재시도 및 타임아웃이 의존하는 워크플로우 API는 실험적 릴리스입니다. 이러한 API에는 제한 사항이 있을 수 있으며 해당 언어에서는 프로덕션 환경에서 사용하는 것을 권장하지 않습니다.

## 시작하기 {#get-started}

다음 예시는 두 개의 노드로 구성된 워크플로우를 빌드합니다. 첫 번째 노드는 불안정한 일기예보 서비스를 호출하며, 총 3번의 시도를 허용하고 첫 번째 재시도 전에 1초를 기다리며 서비스 오류와 타임아웃만 재시도하고 각 시도를 10초로 제한하도록 설정되어 있습니다. 두 번째 노드는 결과를 보고합니다.

=== "Python"

    ```python
    import random

    from google.adk import Context
    from google.adk import Event
    from google.adk import Workflow
    from google.adk.workflow import NodeTimeoutError
    from google.adk.workflow import RetryConfig
    from google.adk.workflow import node


    class ServiceUnavailableError(Exception):
      """Stands in for a transient failure from a remote service."""


    @node(
        retry_config=RetryConfig(
            max_attempts=3,  # 1 original attempt + 2 retries
            initial_delay=1.0,  # seconds before the first retry
            exceptions=[ServiceUnavailableError, NodeTimeoutError],
        ),
        timeout=10.0,  # seconds allowed for each attempt
    )
    async def fetch_forecast(ctx: Context):
      """Simulates an unreliable call to a forecast service."""
      yield Event(message=f"Fetching forecast, attempt {ctx.attempt_count}")
      if random.random() < 0.5:
        raise ServiceUnavailableError("Forecast service unavailable")
      yield "sunny"


    def report_forecast(node_input: str):
      return Event(message=f"The forecast is {node_input}.")


    root_agent = Workflow(
        name="forecast_workflow",
        edges=[("START", fetch_forecast, report_forecast)],
    )
    ```

=== "TypeScript"

    `node()`에 옵션으로 `retryConfig`와 `timeout`을 전달합니다. 지연 시간과 타임아웃 단위는 초(seconds)입니다.

    ```typescript
    --8<-- "examples/typescript/snippets/graphs/retry/get_started.ts:get-started"
    ```

=== "Go"

    노드 생성자에 전달하는 `workflow.NodeConfig`에서 `RetryConfig`와 `Timeout`을 설정합니다. `workflow.DefaultRetryConfig()`에서 시작하여 필요한 필드만 변경하세요.

    ```go
    --8<-- "examples/go/snippets/graphs/retry/main.go:get-started"
    ```

=== "Java"

    `Node` 구현의 `config()` 메서드에서 `NodeConfig`를 반환합니다.

    ```java
    import com.google.adk.agents.Context;
    import com.google.adk.workflow.Edge;
    import com.google.adk.workflow.Node;
    import com.google.adk.workflow.NodeConfig;
    import com.google.adk.workflow.NodeTimeoutException;
    import com.google.adk.workflow.RetryConfig;
    import com.google.adk.workflow.Start;
    import com.google.adk.workflow.Workflow;
    import io.reactivex.rxjava3.core.Flowable;
    import java.time.Duration;
    import java.util.concurrent.ThreadLocalRandom;

    public final class ForecastWorkflow {

      /** Stands in for a transient failure from a remote service. */
      static final class ServiceUnavailableException extends RuntimeException {
        ServiceUnavailableException(String message) {
          super(message);
        }
      }

      /** Simulates an unreliable call to a forecast service. */
      static final class FetchForecastNode implements Node {
        private static final NodeConfig CONFIG =
            NodeConfig.builder()
                .retryConfig(
                    RetryConfig.builder()
                        .maxAttempts(3) // 1 original attempt + 2 retries
                        .initialDelay(Duration.ofSeconds(1))
                        .exceptionClasses(
                            ServiceUnavailableException.class, NodeTimeoutException.class)
                        .build())
                .timeout(Duration.ofSeconds(10)) // limit for each attempt
                .build();

        @Override
        public String name() {
          return "fetch_forecast";
        }

        @Override
        public NodeConfig config() {
          return CONFIG;
        }

        @Override
        public Flowable<?> runNode(Context context, Object nodeInput) {
          if (ThreadLocalRandom.current().nextDouble() < 0.5) {
            return Flowable.error(
                new ServiceUnavailableException(
                    "Forecast service unavailable, attempt " + context.attemptCount()));
          }
          return Flowable.just("sunny");
        }
      }

      public static Workflow create() {
        return Workflow.builder()
            .name("forecast_workflow")
            .edges(new Edge(Start.INSTANCE, new FetchForecastNode()))
            .build();
      }
    }
    ```

=== "Kotlin"

    `node()`에 `NodeConfig`를 전달합니다. 워크플로우 API를 사용하려면 `ExperimentalWorkflowApi`를 옵트인(opt-in)해야 합니다.

    ```kotlin
    --8<-- "examples/kotlin/snippets/graphs/RetryExample.kt:get-started"
    ```

`fetch_forecast`가 서비스 오류로 실패하거나 타임아웃을 초과하면 ADK 에이전트는 대기한 후 동일한 입력으로 노드를 다시 실행합니다. 다음 노드인 `report_forecast`는 시도가 성공한 후에만 실행됩니다. 세 번의 시도가 모두 실패하면 노드는 마지막 시도의 오류와 함께 실패하고 워크플로우도 함께 실패합니다. Go를 제외한 모든 언어에서는 노드 컨텍스트가 1부터 시작하는 시도 횟수(attempt count)를 제공하므로 코드에서 몇 번째 시도가 실행 중인지 확인할 수 있습니다.

## 재시도 구성하기

재시도 정책은 노드가 실행되는 횟수, 시도 사이에 ADK가 대기하는 시간, 재시도를 시작하는 오류의 세 가지를 제어합니다.

-   **시도 횟수(Attempts):** 최대 시도 횟수 값에는 원래 시도가 포함되므로 값을 3으로 설정하면 2번의 재시도가 허용됩니다. 값을 0이나 1로 설정하면 재시도가 비활성화됩니다.
-   **지연 시간(Delay):** 첫 번째 재시도 전의 대기 시간이 초기 지연 시간(initial delay)입니다. ADK는 이후의 각 대기 시간에 백오프 계수(backoff factor)를 곱하므로, 기본값인 1초와 2.0을 사용하면 지터(jitter) 적용 전 기본 대기 시간이 1초, 2초, 4초, 8초가 됩니다. 최대 지연 시간(maximum delay)은 각 대기 시간의 상한선을 제한합니다.
-   **지터(Jitter):** 시스템은 동시에 실패한 많은 노드가 모두 같은 순간에 재시도하지 않도록 각 대기 시간에서 최대 `지터 계수 × 지연 시간`만큼의 무작위 값을 더하거나 뺍니다. 테스트 등에서 고정된 지연 시간을 사용하려면 지터를 0으로 설정하세요.

다음 결정 사항은 워크플로우에서 재시도가 얼마나 효과적으로 작동하는지에 가장 큰 영향을 미칩니다.

-   **일시적인 오류만 재시도하세요.** 기본적으로 재시도 정책은 거의 모든 오류를 재시도합니다. 잘못된 입력이나 버그로 인해 발생한 오류는 매 시도마다 똑같이 실패하므로 재시도하면 실패만 지연될 뿐입니다. 연결 오류, 속도 제한(rate limit) 오류, 타임아웃과 같이 이후 시도에서 성공할 수 있는 오류 유형만 나열하세요. 각 언어가 오류를 매칭하는 방식에 대한 자세한 내용은 [구성 옵션](#configuration-options)을 참고하세요.
-   **실패할 수 있는 노드에 정책을 설정하세요.** Python, Java 및 Kotlin에서는 중첩된 워크플로우에 재시도 정책을 연결할 수도 있으며, 이 경우 내부의 어떤 노드라도 실패하면 중첩된 워크플로우 전체가 재시도됩니다. 불안정한 서비스를 호출하는 개별 노드에 정책을 설정하면 재시도하는 작업량이 줄어들고 더 세밀하게 제어할 수 있습니다.
-   **재시도되는 작업이 반복 실행에 안전하도록(idempotent) 설계하세요.** 재시도는 노드 전체를 다시 실행합니다. 노드가 실패하기 전에 외부 시스템에 데이터를 쓰는 경우 쓰기 작업이 두 번 이상 발생할 수 있습니다. 이러한 작업은 반복 실행해도 추가적인 부작용이 없도록 설계하거나, 부작용이 있는 작업을 불안정한 호출이 성공한 후에 실행되는 별도의 노드로 분리하세요.

## 노드 타임아웃 설정하기

타임아웃은 노드의 단일 시도가 실행될 수 있는 최대 시간을 제한합니다. 이 제한은 재시도를 포함한 전체 시간이 아니라 각 시도에 개별적으로 적용되며, 시도 사이의 대기 시간은 여기에 포함되지 않습니다. 시도가 타임아웃을 초과하여 실행되면 ADK는 해당 시도를 중지하고 실패로 처리합니다.

-   Python, TypeScript, Java 및 Kotlin에서는 다음 표에 나열된 노드 타임아웃 오류와 함께 시도가 실패합니다.
-   Go에서는 노드의 컨텍스트가 마감 시간(deadline)에 도달하며 `context.DeadlineExceeded`와 함께 시도가 실패합니다.

노드에 타임아웃 오류를 포함하는 재시도 정책이 있는 경우, ADK는 타임아웃된 시도를 다른 실패와 마찬가지로 재시도합니다. 정책에 특정 오류 유형을 나열하는 경우 [시작하기](#get-started) 예시처럼 타임아웃 오류를 함께 포함하세요. 재시도 정책이 없는 타임아웃은 처음 발생하는 즉시 노드를 실패 처리합니다.

| 언어 | 타임아웃 설정 | 타임아웃 오류 | 재시도 정책에 지정할 이름 |
| :--- | :--- | :--- | :--- |
| Python | 초 단위의 `timeout` | `NodeTimeoutError` | `NodeTimeoutError` |
| TypeScript | 초 단위의 `timeout` | `NodeTimeoutError` | `NodeTimeoutError` |
| Go | `time.Duration` 타입의 `NodeConfig.Timeout` | `context.DeadlineExceeded` | `ShouldRetry`에서 `errors.Is`로 매칭 |
| Java | `Duration` 타입의 `NodeConfig.timeout` | `NodeTimeoutException` | `NodeTimeoutException` |
| Kotlin | `Duration` 타입의 `NodeConfig.timeout` | `NodeTimeoutError` | `NodeTimeoutError` |

시도를 중지하는 것은 취소(cancellation) 메커니즘에 의존하며, 취소가 코드에 전달되는 방식은 언어에 따라 다릅니다.

-   **Go:** 노드의 `agent.Context`가 마감 시간을 전달합니다. 노드가 수행하는 호출에 이 컨텍스트를 전달하거나 `ctx.Done()`을 확인하여 마감 시간이 지나면 노드가 반환되도록 하세요.
-   **TypeScript:** 타임아웃이 발생하면 ADK는 노드에서 이벤트를 읽는 것을 중단합니다. HTTP 요청과 같이 노드가 시작한 작업도 함께 취소하려면 해당 작업에 `ctx.abortSignal`을 전달하세요.
-   **Kotlin:** ADK는 코루틴(coroutine)에서 시도를 실행하며 타임아웃이 발생하면 코루틴을 취소합니다. 일시 중단 지점(suspension point)에 도달하지 않는 코드는 도달할 때까지 계속 실행됩니다.

## 구성 옵션 {#configuration-options}

재시도 정책은 모든 언어에서 동일한 옵션을 제공합니다. 시간 단위는 Python과 TypeScript에서는 초(seconds)이며, Go, Java 및 Kotlin에서는 각 언어의 고유 duration 타입을 사용합니다.

| 옵션 | 기본값 | 설명 |
| :--- | :--- | :--- |
| 최대 시도 횟수 (Maximum attempts) | `5` | 원래 시도를 포함한 총 시도 횟수입니다. 값이 0 또는 1이면 재시도를 비활성화합니다. |
| 초기 지연 시간 (Initial delay) | 1초 | 첫 번째 재시도 전 대기 시간입니다. |
| 최대 지연 시간 (Maximum delay) | 60초 | 시도 사이 대기 시간의 상한선입니다. |
| 백오프 계수 (Backoff factor) | `2.0` | 각 시도 후 대기 시간에 적용되는 배수입니다. |
| 지터 (Jitter) | `1.0` | 각 대기 시간에 적용되는 무작위 분산 비율(대기 시간의 비율)입니다. `0`으로 설정하면 고정된 대기 시간이 적용됩니다. |
| 재시도할 오류 (Errors to retry) | 모든 오류 | 재시도를 시작할 오류입니다. 다음 목록을 참고하세요. |

각 언어는 고유한 방식으로 재시도할 오류를 선택합니다.

-   **Python:** `exceptions` 설정은 예외 클래스 또는 클래스 이름을 받습니다. 나열된 클래스는 해당 서브클래스와도 매칭됩니다.
-   **TypeScript:** `exceptions` 설정은 오류 클래스 또는 클래스 이름을 받습니다. 오류의 클래스 이름이나 `name` 속성이 목록에 있으면 매칭됩니다. ADK는 클래스 계층 구조를 확인하지 않습니다.
-   **Go:** `ShouldRetry` 설정은 오류를 전달받아 재시도할 경우 `true`를 반환하는 함수입니다. 기본값은 `workflow.ErrInputValidation`을 제외한 모든 오류를 재시도합니다.
-   **Java:** `exceptions` 설정은 단순 클래스 이름(simple class name)을 받으며 정확히 일치하는 경우에만 매칭됩니다. `exceptionClasses` 설정은 클래스를 받으며 서브클래스와도 매칭됩니다. ADK는 `WorkflowConfigurationException`을 절대 재시도하지 않습니다.
-   **Kotlin:** `exceptions` 설정은 단순 클래스 이름을 받으며 정확히 일치하는 경우에만 매칭됩니다. ADK는 `WorkflowConfigurationException`을 절대 재시도하지 않습니다.

!!! warning "Go: 설정하지 않은 필드는 기본값이 아닌 제로 값(zero value)이 됩니다"
    Go에서 구조체 리터럴(struct literal)로 생성한 `RetryConfig`는 설정하지 않은 모든 필드에 기본값이 아닌 제로 값을 사용합니다. 예를 들어 `&workflow.RetryConfig{MaxAttempts: 3}`은 시도 사이에 지연 시간 없이 즉시 재시도합니다. 대신 `workflow.DefaultRetryConfig()`에서 시작하여 필요한 필드를 재정의하세요. 또한 Go는 `MaxDelay`를 적용한 후에 지터를 적용하므로 단일 대기 시간이 지터 비율만큼 `MaxDelay`보다 길어질 수 있습니다.

## 제한 사항

-   **시도 횟수는 저장되지 않습니다.** ADK는 노드의 현재 실행에 대해서만 시도 횟수를 메모리에 유지합니다. 예를 들어 [인간 입력](/ko/graphs/human-input/)을 위해 워크플로우가 일시 중지되거나 애플리케이션이 재시작되는 경우, 워크플로우가 재개된 후 다시 실행되는 노드는 모든 시도 횟수가 초기화된 상태로 1번째 시도부터 다시 시작합니다.

## 다음 단계

-   [에이전트 워크플로우를 위한 그래프 경로 빌드하기](/ko/graphs/routes/): 순차, 분기 및 병렬 경로로 노드를 연결합니다.
-   [에이전트 워크플로우를 위한 데이터 처리](/ko/graphs/data-handling/): 노드 간에 데이터를 전달합니다.
-   [에이전트 워크플로우를 위한 인간 입력](/ko/graphs/human-input/): 워크플로우를 일시 중지하여 사용자에게 입력을 요청합니다.
