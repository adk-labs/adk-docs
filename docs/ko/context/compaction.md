# 성능을 위한 에이전트 컨텍스트 압축

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.16.0</span>
</div>

ADK 에이전트가 실행되면 사용자 지침, 검색된 데이터, 도구 응답 및 생성된 콘텐츠를 포함한 *컨텍스트* 정보를 수집합니다. 이 컨텍스트 데이터의 크기가 커짐에 따라 에이전트 처리 시간도 일반적으로 증가합니다. 에이전트가 사용하는 생성 AI 모델로 점점 더 많은 데이터가 전송되어 처리 시간이 늘어나고 응답이 느려집니다. ADK 컨텍스트 압축 기능은 에이전트 워크플로 이벤트 기록의 이전 부분을 요약하여 에이전트가 실행될 때 컨텍스트 크기를 줄이도록 설계되었습니다.

컨텍스트 압축 기능은 [세션](/adk-docs/sessions/session/) 내에서 에이전트 워크플로 이벤트 데이터를 수집하고 요약하기 위해 *슬라이딩 윈도우* 접근 방식을 사용합니다. 에이전트에서 이 기능을 구성하면 현재 세션에서 특정 수의 워크플로 이벤트 또는 호출 임계값에 도달하면 이전 이벤트의 데이터를 요약합니다.

## 컨텍스트 압축 구성

워크플로의 앱 객체에 이벤트 압축 구성 설정을 추가하여 에이전트 워크플로에 컨텍스트 압축을 추가합니다. 구성의 일부로 다음 샘플 코드와 같이 압축 간격과 겹침 크기를 지정해야 합니다.

```python
from google.adk.apps.app import App
from google.adk.apps.app import EventsCompactionConfig

app = App(
    name='my-agent',
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,  # 3개의 새 호출마다 압축 트리거
        overlap_size=1          # 이전 창의 마지막 호출 포함
    ),
)
```

구성되면 ADK `Runner`는 세션이 간격에 도달할 때마다 백그라운드에서 압축 프로세스를 처리합니다.

## 컨텍스트 압축 예

`compaction_interval`을 3으로 설정하고 `overlap_size`를 1로 설정하면 이벤트 3, 6, 9 등이 완료될 때 이벤트 데이터가 압축됩니다. 겹침 설정은 그림 1과 같이 두 번째 요약 압축 및 이후 각 요약의 크기를 늘립니다.

![컨텍스트 압축 예시 그림](/adk-docs/assets/context-compaction.svg)
**그림 1.** 간격이 3이고 겹침이 1인 이벤트 압축 구성 그림.

이 예제 구성을 사용하면 컨텍스트 압축 작업이 다음과 같이 발생합니다.

1.  **이벤트 3 완료**: 3개의 이벤트가 모두 요약으로 압축됩니다.
2.  **이벤트 6 완료**: 이전 이벤트 1개의 겹침을 포함하여 이벤트 3~6이 압축됩니다.
3.  **이벤트 9 완료**: 이전 이벤트 1개의 겹침을 포함하여 이벤트 6~9가 압축됩니다.

## 구성 설정

이 기능의 구성 설정은 이벤트 데이터가 압축되는 빈도와 에이전트 워크플로가 실행될 때 유지되는 데이터 양을 제어합니다. 선택적으로 압축기 객체를 구성할 수 있습니다.

*   **`compaction_interval`**: 이전 이벤트 데이터의 압축을 트리거하는 완료된 이벤트 수를 설정합니다.
*   **`overlap_size`**: 이전에 압축된 이벤트 중 새로 압축된 컨텍스트 세트에 포함될 이벤트 수를 설정합니다.
*   **`compactor`**: (선택 사항) 요약에 사용할 특정 AI 모델을 포함한 압축기 객체를 정의합니다. 자세한 내용은 [압축기 정의](#define-compactor)를 참조하십시오.

### 압축기 정의 {#define-compactor}

`SlidingWindowCompactor` 클래스를 사용하여 압축기 객체를 정의하여 컨텍스트 압축 작업을 사용자 지정할 수 있습니다. 다음 코드 예제는 압축기를 정의하는 방법을 보여줍니다.

```python
from google.adk.apps.app import App
from google.adk.apps.app import EventsCompactionConfig
from google.adk.models import Gemini
from google.adk.apps.sliding_window_compactor import SlidingWindowCompactor

# 특정 AI 모델을 사용하여 압축기 정의:
summarization_llm = Gemini(model="gemini-2.5-flash")
my_compactor = SlidingWindowCompactor(llm=summarization_llm)

app = App(
    name='my-agent',
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compactor=my_compactor,
        compaction_interval=3, overlap_size=1
    ),
)    
```

해당 클래스의 `prompt_template` 설정을 변경하는 것을 포함하여 요약기 클래스 `LlmEventSummarizer`를 수정하여 `SlidingWindowCompactor`의 작동을 추가로 구체화할 수 있습니다. 자세한 내용은 [`LlmEventSummarizer` 코드](https://github.com/google/adk-python/blob/main/src/google/adk/apps/llm_event_summarizer.py#L60)를 참조하십시오.
