# Gemini를 사용한 컨텍스트 캐싱

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.15.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.7.0</span>
</div>

에이전트로 작업을 수행할 때 생성형 AI 모델에 보내는 여러 에이전트 요청에서 긴 지침(instruction)이나 대규모 데이터셋을 반복해서 재사용해야 하는 경우가 있습니다. 요청할 때마다 동일한 데이터를 다시 전송하면 처리 속도가 느려지고 비효율적이며 비용도 많이 발생할 수 있습니다. 생성형 AI 모델의 컨텍스트 캐싱 기능을 사용하면 응답 속도를 크게 높이고 매 요청마다 모델로 전송되는 토큰 수를 줄일 수 있습니다.

ADK 컨텍스트 캐싱 기능을 사용하면 Gemini 2.0 이상 모델을 비롯하여 이를 지원하는 생성형 AI 모델에 요청 데이터를 캐싱할 수 있습니다. 이 문서에서는 컨텍스트 캐싱을 구성하고 사용하는 방법을 설명합니다.

!!! example "실험적 기능 (Experimental)"
    `ContextCacheConfig` 클래스는 실험적 기능이므로 향후 릴리스에서 API나 동작이 변경될 수 있습니다. Python에서는 인스턴스 생성 시 경고가 출력되며, Kotlin에서는 `@OptIn(ExperimentalContextCachingFeature::class)` 어노테이션이 필요합니다.

## 컨텍스트 캐싱 구성

컨텍스트 캐싱 기능은 에이전트를 감싸는 ADK `App` 객체 수준에서 구성합니다. 다음 코드 샘플과 같이 `ContextCacheConfig` 클래스를 사용하여 관련 설정을 지정하세요.

=== "Python"

    ```python
    from google.adk import Agent
    from google.adk.apps.app import App
    from google.adk.agents.context_cache_config import ContextCacheConfig

    root_agent = Agent(
      name='my_caching_agent',
      # Gemini 2.0 이상을 사용하는 에이전트 구성
    )

    # 컨텍스트 캐싱 구성으로 앱 만들기
    app = App(
        name='my-caching-agent-app',
        root_agent=root_agent,
        context_cache_config=ContextCacheConfig(
            min_tokens=2048,    # 캐싱을 트리거하는 최소 토큰
            ttl_seconds=600,    # 최대 10분 동안 저장
            cache_intervals=5,  # 5회 사용 후 새로 고침
        ),
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.ContextCacheConfig;
    import com.google.adk.apps.App;
    import java.time.Duration;

    // 컨텍스트 캐싱 구성으로 App 생성
    App app = App.builder()
                 .name("my-caching-agent-app")
                 .rootAgent(rootAgent)
                 .contextCacheConfig(
                     new ContextCacheConfig(
                         5, /* cache_intervals (최대 호출 횟수) */
                         Duration.ofMinutes(10), /* ttl */
                         2048 /* min_tokens */))
                 .build();
    ```

=== "Kotlin"

    ```kotlin
    @file:OptIn(ExperimentalContextCachingFeature::class)

    import com.google.adk.kt.agents.ContextCacheConfig
    import com.google.adk.kt.agents.LlmAgent
    import com.google.adk.kt.annotations.ExperimentalContextCachingFeature
    import com.google.adk.kt.apps.App
    import com.google.adk.kt.models.Gemini
    import kotlin.time.Duration.Companion.minutes

    val rootAgent =
        LlmAgent(
            name = "my_caching_agent",
            // configure an agent using Gemini 2.0 or higher
            model = Gemini(name = "gemini-flash-latest"),
        )

    // Create the app with context caching configuration
    @OptIn(ExperimentalContextCachingFeature::class)
    val app =
        App(
            appName = "my-caching-agent-app",
            rootAgent = rootAgent,
            contextCacheConfig =
                ContextCacheConfig(
                    // Gemini는 모델에 따라 고유한 최소 캐시 가능 크기를 적용합니다.
                    minTokens = 8192,
                    ttl = 10.minutes, // 최대 10분 동안 저장
                    cacheIntervals = 5, // 5회 사용 후 새로고침
                    // 타임아웃 시 생성이 실패하고 요청은 캐시되지 않은 상태로 진행됩니다.
                    createHttpOptions = HttpOptions(timeout = 10.seconds),
                ),
        )
    ```

## 구성 설정

`ContextCacheConfig` 클래스는 에이전트의 캐싱 동작 방식을 제어하는 다음 설정을 제공합니다. 이 설정을 구성하면 앱 내 모든 에이전트에 적용됩니다.

-   **`min_tokens`** (int): 캐싱을 활성화하기 위한 최소 토큰 수입니다. 성능상 이점이 미미한 소규모 요청에서 불필요한 캐싱 오버헤드가 발생하는 것을 방지합니다. ADK는 이 값을 직전 요청의 프롬프트 토큰 수와 비교하므로 세션의 첫 번째 요청은 캐싱되지 않습니다. 기본값은 `0`입니다.
-   **`ttl_seconds`** (int): 캐시의 유효 시간(TTL, 초 단위)입니다. 캐시된 콘텐츠가 갱신되기 전까지 유지되는 시간을 지정합니다. `0`보다 커야 하며, 기본값은 `1800`(30분)입니다.
-   **`cache_intervals`** (int): 동일한 캐시 콘텐츠가 만료되기 전까지 재사용할 수 있는 최대 호출 횟수입니다. TTL이 남아 있더라도 캐시 갱신 주기를 제어할 때 사용합니다. `1` 이상 `100` 이하의 값이어야 하며, 기본값은 `10`입니다.
-   **`create_http_options`** (HttpOptions): 캐시 생성 API 호출에 사용할 HTTP 옵션으로, 타임아웃 등을 설정할 수 있습니다. 타임아웃이 발생하면 캐시 생성은 실패하고 해당 요청은 캐싱 없이 그대로 진행됩니다. Python 및 Kotlin에서 지원하며 기본값은 `None`(없음)입니다.

## 캐시 적용 여부 확인

<div class="language-support-tag">
   <span class="lst-supported">ADK에서 지원</span><span class="lst-kotlin">Kotlin v0.6.0</span>
</div>

캐싱이 활성화되면 LLM 응답 기반 이벤트에 해당 호출의 캐시 동작 결과를 담은 `CacheMetadata`가 포함될 수 있습니다. 캐싱이 비활성화되었거나 해당 호출에서 캐시 메타데이터가 생성되지 않은 경우 `null`이므로 조회 전에 반드시 `null` 여부를 확인하세요. 값이 존재하는 경우 두 가지 상태 중 하나를 가집니다. `cacheName`, `expireTime`, `invocationsUsed`가 모두 설정된 **활성 캐시(active cache)** 상태와, 세 필드가 모두 `null`인 **핑거프린트 전용(fingerprint-only)** 상태입니다.

```kotlin
--8<-- "examples/kotlin/snippets/context/CacheMetadataExample.kt:cache_metadata"
```

`expireSoon`은 캐시가 약 2분 이내에 만료되거나 이미 만료되었음을 의미합니다. 이는 사용자 코드에 대한 신호일 뿐 ADK가 직접 조치를 취하는 것은 아닙니다. ADK는 실제로 `expireTime`이 지나거나 `cacheIntervals`를 초과하거나 캐시된 접두사가 변경될 때까지 캐시를 계속 재사용합니다.

토큰 수는 `CacheMetadata`에 포함되지 않으므로 `LlmResponse.usageMetadata`에서 읽으세요.

## 다음 단계

컨텍스트 캐싱 기능을 사용하고 테스트하는 방법에 대한 전체 구현은 다음 샘플을 참고하세요.

-   [`cache_analysis`](https://github.com/google/adk-python/tree/main/contributing/samples/cache_analysis):
    컨텍스트 캐싱의 성능을 분석하는 방법을 보여주는 코드 샘플입니다.

세션 전반에 걸쳐 고정된 지침을 제공해야 하는 사용 사례라면 에이전트의 `static_instruction` 매개변수 사용을 고려해 보세요. 이 매개변수를 사용하면 생성형 모델의 시스템 지침을 보완할 수 있습니다. 자세한 내용은 다음 샘플 코드를 참고하세요.

-   [`static_instruction`](https://github.com/google/adk-python/tree/main/contributing/samples/context_management/static_instruction):
    정적 지침을 사용하는 디지털 펫 에이전트 구현 예시입니다.
