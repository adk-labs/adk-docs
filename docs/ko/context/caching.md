# Gemini를 사용한 컨텍스트 캐싱

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.15.0</span>
</div>

에이전트를 사용하여 작업을 완료할 때 생성 AI 모델에 대한 여러 에이전트 요청에 걸쳐 확장된 지침이나 대규모 데이터 세트를 재사용하고 싶을 수 있습니다. 각 에이전트 요청에 대해 이 데이터를 다시 보내는 것은 느리고 비효율적이며 비용이 많이 들 수 있습니다. 생성 AI 모델에서 컨텍스트 캐싱 기능을 사용하면 응답 속도를 크게 높이고 각 요청에 대해 모델로 전송되는 토큰 수를 줄일 수 있습니다.

ADK 컨텍스트 캐싱 기능을 사용하면 Gemini 2.0 이상 모델을 포함하여 이를 지원하는 생성 AI 모델로 요청 데이터를 캐시할 수 있습니다. 이 문서에서는 이 기능을 구성하고 사용하는 방법을 설명합니다.

## 컨텍스트 캐싱 구성

에이전트를 래핑하는 ADK `App` 객체 수준에서 컨텍스트 캐싱 기능을 구성합니다. 다음 코드 샘플과 같이 `ContextCacheConfig` 클래스를 사용하여 이러한 설정을 구성합니다.

```python
from google.adk import Agent
from google.adk.apps.app import App
from google.adk.agents.context_cache_config import ContextCacheConfig

root_agent = Agent(
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

## 구성 설정

`ContextCacheConfig` 클래스에는 에이전트에 대한 캐싱 작동 방식을 제어하는 다음 설정이 있습니다. 이러한 설정을 구성하면 앱 내의 모든 에이전트에 적용됩니다.

-   **`min_tokens`** (int): 캐싱을 활성화하는 데 필요한 요청의 최소 토큰 수입니다. 이 설정을 사용하면 성능 이점이 미미한 매우 작은 요청에 대한 캐싱 오버헤드를 피할 수 있습니다. 기본값은 `0`입니다.
-   **`ttl_seconds`** (int): 캐시의 TTL(Time-To-Live) (초)입니다. 이 설정은 캐시된 콘텐츠가 새로 고쳐지기 전에 저장되는 기간을 결정합니다. 기본값은 `1800`(30분)입니다.
-   **`cache_intervals`** (int): 동일한 캐시된 콘텐츠가 만료되기 전에 사용할 수 있는 최대 횟수입니다. 이 설정을 사용하면 TTL이 만료되지 않았더라도 캐시가 업데이트되는 빈도를 제어할 수 있습니다. 기본값은 `10`입니다.

## 다음 단계

컨텍스트 캐싱 기능을 사용하고 테스트하는 방법에 대한 전체 구현은 다음 샘플을 참조하십시오.

-   [`cache_analysis`](https://github.com/google/adk-python/tree/main/contributing/samples/cache_analysis):
    컨텍스트 캐싱의 성능을 분석하는 방법을 보여주는 코드 샘플입니다.

사용 사례에서 세션 전체에서 사용되는 지침을 제공해야 하는 경우 에이전트에 대한 `static_instruction` 매개변수를 사용하는 것을 고려하십시오. 이 매개변수를 사용하면 생성 모델에 대한 시스템 지침을 수정할 수 있습니다. 자세한 내용은 다음 샘플 코드를 참조하십시오.

-   [`static_instruction`](https://github.com/google/adk-python/tree/main/contributing/samples/static_instruction):
    정적 지침을 사용하는 디지털 펫 에이전트의 구현입니다.
