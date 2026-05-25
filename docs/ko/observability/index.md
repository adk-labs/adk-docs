# 에이전트를 위한 관측 가능성(Observability)

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

에이전트를 위한 관측 가능성은 시스템의 외부 텔레메트리와 구조화된 로그를
분석하여, 추론 트레이스, 도구 호출, 잠재 모델 출력(latent model outputs)을 포함한
시스템 내부 상태를 측정할 수 있게 합니다. 에이전트를 구축할 때,
실행 중 동작(in-process behavior)을 디버깅하고 진단하기 위해 이러한
기능이 필요할 수 있습니다. 일정 수준 이상의 복잡도를 가진 에이전트에서는
기본적인 입력/출력 모니터링만으로는 보통 충분하지 않습니다.

Agent Development Kit(ADK)는 에이전트 모니터링 및 디버깅을 위한
[로깅](/ko/observability/logging/), [메트릭](/ko/observability/metrics/),
[트레이스](/ko/observability/traces/) 기능을 기본 제공합니다. 다만 모니터링 및
분석을 위해서는 더 고급의 [observability ADK 통합](/ko/integrations/?topic=observability)
기능도 고려해야 할 수 있습니다.

## 빠른 시작: Kotlin에서 관측성 활성화

Kotlin에서는 트레이스를 위한 OpenTelemetry를 구성하고 자세한 콘솔 출력을 위한 `LoggingPlugin`을 사용하여 포괄적인 관측성을 활성화할 수 있습니다.

```kotlin
--8<-- "examples/kotlin/snippets/observability/SetupExample.kt:full_example"
```

!!! tip "관측 가능성을 위한 ADK 통합"
    ADK용 사전 구축된 관측 가능성 라이브러리 목록은
    [도구 및 통합](/ko/integrations/?topic=observability)을 참조하세요.
