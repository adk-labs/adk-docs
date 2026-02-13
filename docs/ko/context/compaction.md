# 성능 향상을 위한 에이전트 컨텍스트 압축

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v1.16.0</span>
</div>

ADK 에이전트는 실행되면서 사용자 지침, 검색된 데이터, 도구 응답 및 생성된 콘텐츠를 포함한 *컨텍스트* 정보를 수집합니다. 이 컨텍스트 데이터의 크기가 커질수록 에이전트 처리 시간도 일반적으로 증가합니다. 점점 더 많은 데이터가 에이전트가 사용하는 생성형 AI 모델로 전송되어 처리 시간이 길어지고 응답이 느려집니다. ADK 컨텍스트 압축 기능은 에이전트 워크플로 이벤트 기록의 이전 부분을 요약하여 에이전트가 실행되는 동안 컨텍스트 크기를 줄이도록 설계되었습니다.

컨텍스트 압축 기능은 [세션](/adk-docs/ko/sessions/session/) 내에서 에이전트 워크플로 이벤트 데이터를 수집하고 요약하기 위해 *슬라이딩 윈도우* 접근 방식을 사용합니다. 이 기능을 에이전트에 구성하면 현재 세션에서 특정 수의 워크플로 이벤트(또는 호출) 임계값에 도달하면 이전 이벤트의 데이터를 요약합니다.

## 컨텍스트 압축 구성

워크플로의 App 객체에 이벤트 압축 구성 설정을 추가하여 에이전트 워크플로에 컨텍스트 압축을 추가합니다. 구성의 일부로 다음 샘플 코드에 표시된 대로 압축 간격과 오버랩 크기를 지정해야 합니다.

```python
from google.adk.apps.app import App
from google.adk.apps.app import EventsCompactionConfig

app = App(
    name='my-agent',
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,  # 3개의 새 호출마다 압축을 트리거합니다.
        overlap_size=1          # 이전 창의 마지막 호출을 포함합니다.
    ),
)
```

일단 구성되면 ADK `Runner`는 세션이 간격에 도달할 때마다 백그라운드에서 압축 프로세스를 처리합니다.

## 컨텍스트 압축 예시

`compaction_interval`을 3으로, `overlap_size`를 1로 설정하면 이벤트 3, 6, 9 등이 완료될 때 이벤트 데이터가 압축됩니다. 오버랩 설정은 그림 1에 표시된 대로 두 번째 요약 압축 및 이후 각 요약의 크기를 증가시킵니다.

![컨텍스트 압축 예시 그림](/adk-docs/ko/assets/context-compaction.svg)
**그림 1.** 간격 3, 오버랩 1인 이벤트 압축 구성 그림.

이 예시 구성에서 컨텍스트 압축 작업은 다음과 같이 진행됩니다.

1.  **이벤트 3 완료**: 3개 이벤트 모두 요약으로 압축됩니다.
1.  **이벤트 6 완료**: 이전 이벤트 1개의 오버랩을 포함하여 이벤트 3에서 6까지 압축됩니다.
1.  **이벤트 9 완료**: 이전 이벤트 1개의 오버랩을 포함하여 이벤트 6에서 9까지 압축됩니다.

## 구성 설정

이 기능의 구성 설정은 이벤트 데이터가 압축되는 빈도와 에이전트 워크플로가 실행되는 동안 유지되는 데이터의 양을 제어합니다. 선택적으로 압축기 객체를 구성할 수 있습니다.

*   **`compaction_interval`**: 이전 이벤트 데이터의 압축을 트리거하는 완료된 이벤트 수를 설정합니다.
*   **`overlap_size`**: 새로 압축된 컨텍스트 세트에 포함되는 이전에 압축된 이벤트 수를 설정합니다.
*   **`summarizer`**: (선택 사항) 요약에 사용할 특정 AI 모델을 포함하는 요약기 객체를 정의합니다. 자세한 내용은 [요약기 정의](#define-summarizer)를 참조하세요.

### 요약기 정의 {#define-summarizer}
요약기를 정의하여 컨텍스트 압축 프로세스를 사용자 지정할 수 있습니다. LlmEventSummarizer 클래스를 사용하면 요약에 특정 모델을 지정할 수 있습니다. 다음 코드 예시는 사용자 지정 요약기를 정의하고 구성하는 방법을 보여줍니다.

```python
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini

# 요약에 사용할 AI 모델 정의:
summarization_llm = Gemini(model="gemini-2.5-flash")

# 사용자 지정 모델로 요약기 생성:
my_summarizer = LlmEventSummarizer(llm=summarization_llm)

# 사용자 지정 요약기 및 압축 설정으로 App 구성:
app = App(
    name='my-agent',
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,
        overlap_size=1,
        summarizer=my_summarizer,
    ),
)
```

`SlidingWindowCompactor`의 `LlmEventSummarizer` 클래스의 `prompt_template` 설정을 변경하는 것을 포함하여 요약기 클래스를 수정하여 `SlidingWindowCompactor`의 작동을 더욱 세분화할 수 있습니다. 자세한 내용은 [`LlmEventSummarizer` 코드](https://github.com/google/adk-python/blob/main/src/google/adk/apps/llm_event_summarizer.py#L60)를 참조하세요.
