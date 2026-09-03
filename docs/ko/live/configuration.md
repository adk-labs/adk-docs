# 라이브 에이전트를 위한 구성

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`RunConfig`는 라이브 세션의 동작을 결정하는 곳입니다. 에이전트의 음성 톤, 음성 전사 방식, 턴 종료 판단 시점, 유지할 대화 히스토리의 양, 적용할 한도 등을 설정합니다. 이를 [`Runner.run_live()`](https://google.github.io/adk-docs/api-reference/python/)에 전달하면 해당 세션에만 적용됩니다. 동일한 에이전트라도 두 명의 사용자가 완전히 다른 구성으로 실행할 수 있습니다.

`RunConfig`는 라이브 전용이 아닙니다. [런타임 구성](../runtime/runconfig.md)에서는 전체 클래스와 `run_async()`에 적용되는 필드를 설명합니다. 다음은 `run_live()`에서 중요한 하위 집합과 라이브 세션에만 존재하는 음성 관련 설정입니다.

## RunConfig 매개변수 빠른 참조

다음 표는 라이브 에이전트와 가장 관련성이 높은 `RunConfig` 매개변수에 대한 빠른 참조를 제공합니다:

| 매개변수 | 타입 | 목적 | 참조 |
|---|---|---|---|
| **response_modalities** | list[str] | 출력 형식. 라이브 에이전트는 반드시 `AUDIO`를 사용해야 함 — 라이브 모델은 `TEXT`를 지원하지 않음 | [세부정보](#response-modalities) |
| **streaming_mode** | StreamingMode | `run_async()` 경로에서의 청크 또는 단일 샷 전달; `run_live()`에서는 읽히지 않음 | [세부정보](#streamingmode-bidi-or-sse) |
| **session_resumption** | SessionResumptionConfig | 자동 재연결 활성화 | [세부정보](sessions.md#session-resumption) |
| **context_window_compression** | ContextWindowCompressionConfig | 무제한 세션 지속 시간 지원 | [세부정보](sessions.md#context-window-compression) |
| **history_config** | HistoryConfig | 이전 대화 기록이 라이브 서버에 재생되는 방식 제어 | [세부정보](#history_config) |
| **max_llm_calls** | int | 세션당 총 LLM 호출 수 제한 | [세부정보](#max_llm_calls) |
| **save_live_blob** | bool | 오디오/비디오 스트림 영구 저장 | [세부정보](#save_live_blob) |
| **custom_metadata** | dict[str, Any] | 호출 이벤트에 커스텀 메타데이터 첨부 | [세부정보](#custom_metadata) |
| **speech_config** | SpeechConfig | 음성 및 언어 구성 | [음성 및 언어](#voice-and-language) |
| **input_audio_transcription** | AudioTranscriptionConfig | 사용자 음성 전사 | [오디오 전사](#audio-transcription) |
| **output_audio_transcription** | AudioTranscriptionConfig | 모델 음성 전사 | [오디오 전사](#audio-transcription) |
| **realtime_input_config** | RealtimeInputConfig | VAD 구성 | [음성 활동 감지](#voice-activity-detection-vad) |
| **explicit_vad_signal** | bool | 모델로부터 음성 활동 이벤트 방출 | [세부정보](#other-live-related-fields) |
| **proactivity** | ProactivityConfig | 능동적 오디오 활성화 (모델별 지원) | [능동적 및 감정적 대화](#proactivity-and-affective-dialog) |
| **enable_affective_dialog** | bool | 감정 적응 활성화 (모델별 지원) | [능동적 및 감정적 대화](#proactivity-and-affective-dialog) |
| **translation_config** | TranslationConfig | 실시간 음성 대 음성 번역 (번역 모델 전용) | [세부정보](#other-live-related-fields) |
| **avatar_config** | AvatarConfig | 에이전트를 애니메이션 아바타로 렌더링 | [세부정보](#other-live-related-fields) |

구성 옵션에 대한 자세한 내용은 Python API 참조의 [`RunConfig`](../api-reference/python/google-adk.html#google.adk.agents.RunConfig)를 참고하세요.

**Import 경로:**

위 표에서 참조된 모든 구성 타입 클래스는 `google.genai.types`에서 가져옵니다:

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode

# types 모듈을 통해 구성 타입에 접근합니다
run_config = RunConfig(
    session_resumption=types.SessionResumptionConfig(),
    context_window_compression=types.ContextWindowCompressionConfig(...),
    speech_config=types.SpeechConfig(...),
    # 등등
)
```

`RunConfig` 클래스 자체와 `StreamingMode` enum은 `google.adk.agents.run_config`에서 가져옵니다.

## 응답 모달리티 (Response modes)

`response_modalities` 설정은 출력 형식을 제어하며, 세션당 정확히 하나의 형식을 가집니다. **라이브 에이전트의 경우 값은 항상 `["AUDIO"]`입니다.** ADK가 지원하는 모든 [라이브 모델](models.md#live-models)은 다른 모달리티를 지원하지 않기 때문입니다. 값을 설정하지 않으면 ADK가 자동으로 채워주므로 대부분의 라이브 애플리케이션에서는 이 필드를 직접 다룰 필요가 없습니다.

!!! warning "`response_modalities=["TEXT"]` 마이그레이션 안내"

    이전 ADK 샘플과 절반 계단식(half-cascade) 모델은 텍스트 전용 라이브 세션을 허용했습니다. 하지만 이는 더 이상 작동하지 않습니다. `["TEXT"]`로 `run_live()`를 호출하면 오디오만 생성하는 최신 라이브 모델에서는 실패합니다.

    **라이브 에이전트에서 텍스트를 얻으려면 [`event.output_transcription`](#audio-transcription)을 읽으세요.** ADK에서는 전사가 기본적으로 활성화되어 있으므로 `response_modalities` 라인을 삭제하기만 해도 대부분 해결됩니다.

    표준 Gemini 모델에서 실행되는 `run_async()` 경로에서는 `["TEXT"]`가 여전히 올바른 설정입니다. [양방향 스트리밍 또는 SSE](#streamingmode-bidi-or-sse)를 참고하세요.

응답 모달리티는 모델의 출력에만 영향을 줍니다. 모델이 해당 입력 모달리티를 지원한다면 이에 관계없이 **항상 텍스트, 음성 또는 비디오 입력을 보낼 수 있습니다**.

## 양방향 스트리밍 또는 SSE { #streamingmode-bidi-or-sse }

ADK는 두 가지 서로 다른 엔드포인트를 통해 Gemini에 접근할 수 있으며, **호출하는 `Runner` 메서드에 따라 엔드포인트가 결정됩니다**:

- **`runner.run_live()`**: ADK는 **Live API**(`live.connect()`를 통한 양방향 스트리밍 엔드포인트)에 대한 WebSocket을 엽니다. 이 가이드의 나머지 부분에서 다루는 내용이며 실시간 오디오 및 비디오에 필수적입니다.
- **`runner.run_async()`**: ADK는 **표준 Gemini API**(`generate_content_async()`를 통한 단항/스트리밍 엔드포인트)에 HTTP를 사용합니다. 청크 단위로 응답을 다시 스트리밍하려면 `RunConfig.streaming_mode = StreamingMode.SSE`로 설정하세요.

두 모델 세트는 거의 겹치지 않습니다. `gemini-flash-latest`와 같은 표준 Gemini 모델은 양방향 연결을 유지하지 않으며, [지원 모델](models.md#live-models)의 모델들은 `run_live()`로 구동하도록 설계되었으므로 모델 선택은 곧 `Runner` 메서드 선택의 일부입니다.

!!! warning "Python: `StreamingMode.BIDI`는 ADK를 Live API로 전환하지 않습니다"

    **Python**에서 `RunConfig.streaming_mode`는 `run_async()` 코드 경로에서만 읽히며, 단일 완료 응답(`StreamingMode.NONE`, 기본값)과 청크 단위 전달(`StreamingMode.SSE`) 사이를 선택합니다. `run_live()` 경로는 이를 전혀 읽지 않으므로 `streaming_mode=StreamingMode.BIDI`를 설정해도 아무런 효과가 없으며 조용히 무시됩니다. **양방향 스트리밍을 사용하려면 `run_live()`를 호출해야 합니다.** ADK 자체의 Python `StreamingMode` 독스트링에서도 BIDI는 "표준 실행 경로에서 사용되지 않으며", 실제 양방향 동작은 "`streaming_mode`에 의존하지 않는 완전히 다른 코드 경로를 사용한다"고 명시하고 있습니다.

    **Java는 다릅니다.** ADK Java의 흐름은 `StreamingMode.BIDI`를 실제로 읽으며, Java 퀵스타트는 `runLive()`에 전달하는 `RunConfig`에 이를 명시적으로 설정합니다. 언어 간에 설정을 그대로 복사하지 말고 각 언어의 퀵스타트를 따르세요.

```python
# Live API: streaming_mode가 필요 없으며, run_live() 호출 자체가 이를 선택함
run_config = RunConfig(response_modalities=["AUDIO"])
async for event in runner.run_live(..., run_config=run_config):
    ...
```

이 선택은 ADK가 Gemini와 통신하는 방식에만 영향을 줍니다. 클라이언트를 향한 아키텍처는 독립적입니다. 어느 경로에서든 WebSocket 서버, REST API 또는 SSE 엔드포인트를 구축할 수 있습니다.

`run_async()` 및 SSE 경로(`streaming_mode` 값, 프로그레시브 SSE 스트리밍, 언어별 구성)에 대한 내용은 [런타임 구성](../runtime/runconfig.md#enable-streaming)을 참고하세요.

## 기타 제어 옵션

ADK는 세션 동작을 제어하고, 비용을 관리하며, 디버깅 및 컴플라이언스 목적으로 오디오 데이터를 유지하기 위한 추가 RunConfig 옵션을 제공합니다.

```python
run_config = RunConfig(
    # 호출당 총 LLM 호출 제한
    max_llm_calls=500,  # 기본값: 500 (무한 루프 방지)
                        # 0 또는 음수 = 무제한 (주의해서 사용)

    # 디버깅/컴플라이언스를 위한 오디오/비디오 아티팩트 저장
    save_live_blob=True,  # 기본값: False

    # 이벤트에 커스텀 메타데이터 첨부
    custom_metadata={"user_tier": "premium", "session_type": "support"},  # 기본값: None
)
```

### max_llm_calls

`max_llm_calls`는 호출 컨텍스트당 LLM 호출 수를 제한하며, [런타임 구성](../runtime/runconfig.md#configure-runtime-limits-and-debugging)에 전체 내용이 설명되어 있습니다.

**이 설정은 `run_live()`에는 적용되지 않습니다.** 이 매개변수는 `run_async()` 경로만 보호하므로 라이브 세션은 이를 통한 자동 비용 상한을 얻지 못합니다. 세션 지속 시간을 제한하고, 턴 수를 세며, 모델 이벤트의 `usage_metadata`([메타데이터](events.md#metadata))를 모니터링하고, 루프 앞에 서킷 브레이커를 두어 자체적으로 예산을 관리하세요.

### save_live_blob

`save_live_blob=True`는 세션의 오디오를 [세션 서비스](../sessions/index.md)에는 참조로, [아티팩트 서비스](../artifacts/index.md)에는 파일로 유지합니다. 이름과 달리 현재는 **오디오만 유지**되며 비디오는 저장되지 않습니다.

음성 동작을 디버깅하거나 규제 대상 환경의 감사 추적을 위해 활성화하세요. 그렇지 않은 경우에는 비활성화 상태로 두는 것이 좋습니다. 16 kHz PCM 입력은 두 서비스에 기록될 때 **세션당 분당 약 1.92 MB**를 차지하며, 음성 워크로드에서는 용량이 빠르게 누적됩니다. 프로덕션 환경에서 필요한 경우 모든 세션 대신 일부 세션만 샘플링하고 아티팩트 서비스에 보존 정책(retention policy)을 설정하세요. ADK는 이를 자동으로 만료시키지 않습니다.

!!! warning "`save_live_audio`는 지원 중단(deprecated)되었습니다"

    ADK는 `save_live_audio=True`를 `save_live_blob=True`로 자동 마이그레이션하고 경고를 표시하지만, 이 호환성 계층은 향후 릴리스에서 제거될 예정입니다. `save_live_blob`으로 업데이트하세요.

### history_config

이미 대화 기록이 있는 세션에 대해 ADK가 **새로운** Live API 연결을 열 때 해당 기록을 서버에 재생(replay)합니다. 해당 기록에는 모델 자체의 과거 턴이 포함되어 있으므로 서버에 다시 응답하지 않도록 알려주어야 합니다. ADK가 이를 자동으로 처리합니다. 전송할 기록이 있고 세션 재개 핸들이 활성화되지 않은 경우 연결하기 전에 `live_connect_config.history_config.initial_history_in_client_content = True`를 설정합니다.

```python
from google.genai import types

# ADK가 이를 자동으로 설정합니다. 반대 동작이 필요한 경우에만 재정의하세요.
run_config = RunConfig(
    history_config=types.HistoryConfig(
        initial_history_in_client_content=True,
    ),
)
```

**실제 의미:**

- **일반적으로 아무것도 할 필요가 없습니다.** ADK는 값을 설정하지 않았을 때만 채워 넣으므로 `RunConfig`에 명시된 `history_config`가 항상 우선 적용됩니다.
- **재연결 시에는 기록 전송을 건너뜁니다.** ADK가 세션 재개 핸들로 재연결할 때 서버는 이미 해당 세션의 상태를 유지하고 있으므로 ADK는 기록을 보내지 않으며 `history_config`를 건드리지 않습니다.
- **잘못되었을 때의 증상**: 기록을 시딩하는 동안 `initial_history_in_client_content=False`로 설정하면 모델이 *재생된* 턴에 응답하여 연결 시작 시 중복된 답변이 쏟아져 나옵니다.

### custom_metadata

`custom_metadata`는 호출 내의 모든 `Event`에 임의의 JSON 직렬화 가능한 딕셔너리를 첨부하며, [런타임 구성](../runtime/runconfig.md#configure-runtime-limits-and-debugging)에 설명된 대로 라이브 세션에서도 동일하게 작동합니다.

```python
run_config = RunConfig(
    response_modalities=["AUDIO"],
    custom_metadata={"user_tier": "premium", "session_type": "support"},
)
```

라이브 고유의 차이점은 스코프입니다. 한 번의 `run_live()` 호출이 하나의 호출(invocation)이므로, 메타데이터는 단일 턴이 아니라 전체 스트리밍 세션의 모든 이벤트에 각인됩니다. `event.custom_metadata`를 통해 이를 다시 읽을 수 있습니다.

!!! warning "`custom_metadata`에 민감한 데이터를 넣지 마세요"

    이 메타데이터를 포함하는 모든 이벤트는 세션 서비스에 저장됩니다. 개인 식별 정보(PII), 자격 증명 및 기타 민감한 정보는 제외하고 대안이 없는 경우 암호화하세요.

### 기타 라이브 관련 필드

`RunConfig`에는 `run_live()` 경로에서만 유효한 몇 가지 추가 필드가 있습니다. ADK는 이를 라이브 연결로 그대로 전달하므로 정확한 동작은 ADK가 아닌 Live API에 의해 정의됩니다:

| 필드 | 타입 | 설명 |
|---|---|---|
| `explicit_vad_signal` | `bool` | 모델이 명시적인 음성 활동 신호를 방출하도록 요청합니다. ADK는 콘텐츠로부터 턴 경계를 유추하는 대신 `event.voice_activity`로 이를 표시합니다 |
| `translation_config` | `types.TranslationConfig` | 실시간 음성 대 음성 번역을 활성화합니다. `target_language_code`(BCP-47) 및 `echo_target_language`를 받습니다. **`gemini-3.5-live-translate-preview`와 같은 번역 모델에서만 지원**되며, [지원 모델](models.md#live-models)의 일반 모델에서는 지원되지 않습니다 |
| `avatar_config` | `types.AvatarConfig` | 에이전트를 애니메이션 아바타로 렌더링합니다. `avatar_name`(빌트인 아바타) 또는 `customized_avatar`, 그리고 `audio_bitrate_bps` / `video_bitrate_bps`를 받습니다 |

```python
from google.genai import types

run_config = RunConfig(
    response_modalities=["AUDIO"],
    explicit_vad_signal=True,
)
```

라이브 전용은 아니지만 라이브 세션에서 매우 유용한 필드가 하나 더 있습니다:

- **`model_input_context`** (`list[types.Content]`): 현재 호출에 대해서만 LLM 요청에 주입되는 일시적인 컨텍스트입니다. `Runner`는 이를 세션에 저장하지 않으므로 대화 기록을 오염시키지 않고 턴별 그라운딩 정보(사용자가 방금 연 문서, 보고 있는 페이지 등)를 깔끔하게 제공할 수 있습니다.

### 합성 함수 호출 (support_cfc)

합성 함수 호출(Compositional Function Calling, CFC)은 라이브 기능이 아니라 `run_async()` / SSE 기능입니다. 현재 라이브 모델 중 CFC 요구 사항을 충족하는 모델이 없으므로 이론상으로만 적용 가능합니다. `support_cfc`는 SSE 경로에 남겨두고 라이브 세션에서는 표준 함수 호출을 사용하세요([도구](tools.md) 참고). 매개변수 자체에 대해서는 [런타임 구성](../runtime/runconfig.md)을 참고하세요.

## 오디오 전사 (Audio transcription)

Live API는 대화 양측을 모두 전사해주므로 별도의 음성 텍스트 변환(STT) 서비스 없이도 캡션을 표시하고, 대화를 기록하며, 접근성을 지원할 수 있습니다. **ADK에서는 입력(사용자 음성)과 출력(모델 음성) 모두 전사가 기본적으로 켜져 있습니다.** 특정 방향을 끄려면 해당 필드를 `None`으로 설정하세요.

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

# 기본적으로 활성화되어 있습니다. 둘 다 AudioTranscriptionConfig()로 설정하는 것과 동일합니다.
run_config = RunConfig(response_modalities=["AUDIO"])

# 사용자 입력 전사를 끄고 모델 출력 전사는 유지합니다.
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,
)
```

전사는 `event.content`와 별도로 `event.input_transcription` 및 `event.output_transcription`에 `types.Transcription` 객체로 도착합니다. 이는 조각(fragment) 단위로 스트리밍됩니다. `.text`는 최신 조각을 담고 있고 `.finished`는 해당 턴의 마지막 조각임을 표시합니다. 조각들을 이어 붙여 전체 전사를 구성할 수 있습니다.

```python
async for event in runner.run_live(...):
    if event.input_transcription and event.input_transcription.text:
        update_caption(
            event.input_transcription.text,
            is_user=True,
            is_final=event.input_transcription.finished,
        )
    if event.output_transcription and event.output_transcription.text:
        update_caption(
            event.output_transcription.text,
            is_user=False,
            is_final=event.output_transcription.finished,
        )
```

이벤트 구조에 대해서는 [전사 이벤트](events.md#transcription)를 참고하세요.

!!! note "멀티 에이전트 세션은 항상 전사를 활성화합니다"

    루트 에이전트에 `sub_agents`가 있는 경우 `run_live()`는 사용자가 `None`으로 설정하더라도 입력 및 출력 전사를 모두 활성화합니다. 에이전트 인계 시 다음 에이전트에 대화 컨텍스트를 전달하기 위해 텍스트 전사가 필요하므로 비활성화할 수 없습니다([`runners.py`](https://github.com/google/adk-python/blob/main/src/google/adk/runners.py)).

## 음성 및 언어 (Voice and language)

모델의 음성과 언어를 선택하려면 `speech_config`를 설정하세요. 두 곳에서 설정할 수 있습니다:

- **에이전트 수준**: `speech_config`가 포함된 `Gemini` 인스턴스를 전달합니다. 멀티 에이전트 워크플로에서 각 에이전트에 고유한 음성을 부여할 때 사용합니다.
- **세션 수준**: `RunConfig.speech_config`를 설정합니다. 세션 전체에 걸쳐 단일 음성을 사용할 때 사용합니다.

둘 다 설정된 경우 **에이전트 수준의 음성이 우선 적용**됩니다. 둘 다 설정되지 않은 경우 Live API가 기본 음성을 선택합니다.

```python
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.agents.run_config import RunConfig

# 에이전트 수준 음성 (RunConfig보다 우선 적용됨).
agent = Agent(
    model=Gemini(
        model="gemini-live-2.5-flash-native-audio",
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
            ),
            language_code="en-US",
        ),
    ),
    instruction="You are a helpful assistant.",
)

# 세션 수준 기본 음성 (자체 음성이 없는 에이전트가 사용).
run_config = RunConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
        ),
    ),
)
```

`voice_name`은 사전 제작된 음성을 선택합니다. [라이브 모델](models.md#live-models)은 8가지 음성(Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr)과 확장된 [Text-to-Speech 음성 목록](https://cloud.google.com/text-to-speech/docs/voices)을 지원합니다. 현재 목록과 백엔드별 가용성은 [Gemini Live API 음성 문서](https://ai.google.dev/gemini-api/docs/live-api/capabilities#change-voice-and-language)를 확인하세요. 지원되지 않는 음성은 연결 시 오류를 반환합니다.

`language_code`(예: `en-US`, `ko-KR`, `ja-JP`)는 언어와 억양을 설정합니다. 라이브 모델은 대화 내용에서 언어를 자체적으로 유추하는 경우가 많아 이 설정을 무시할 수도 있습니다.

## 음성 활동 감지 (VAD)

VAD는 사용자가 말을 시작하고 멈추는 시점을 감지하여 모델이 끼어들기 처리를 포함해 자연스럽게 턴을 주고받을 수 있도록 합니다. 모든 [라이브 모델](models.md#live-models)에서 **기본적으로 켜져 있으며**, 대부분의 애플리케이션에서는 별도 구성이 필요하지 않습니다.

Push-to-talk, 클라이언트 측 VAD 또는 사용자가 발언 완료를 직접 신호하는 UX 등 애플리케이션이 턴 경계를 자체적으로 결정하는 경우 자동 VAD를 비활성화하세요. 비활성화한 경우 [`send_activity_start()` / `send_activity_end()`](sessions.md#liverequestqueue)를 사용하여 수동으로 `ActivityStart`/`ActivityEnd` 신호를 보내야 하며, 클라이언트는 자체 턴 신호를 서버의 해당 호출로 변환해야 합니다.

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(disabled=True)
    ),
)
```

자체 VAD를 실행하는 클라이언트는 해당 신호를 서버로 보내고, 서버는 `send_activity_start()` / `send_activity_end()`로 이를 전달합니다. [클라이언트 연결](custom-server.md#connect-a-client)을 참고하세요.

## 능동적 및 감정적 대화 (Proactivity and affective dialog)

일부 라이브 모델은 기본적으로 꺼져 있는 두 가지 대화 기능을 제공합니다:

- **능동적 오디오** (`proactivity`): 모델이 응답할 시점을 스스로 결정하고, 요청하지 않아도 제안을 하거나, 관련 없는 입력을 무시할 수 있습니다.
- **감정적 대화** (`enable_affective_dialog`): 모델이 사용자의 어조에서 감정을 감지하고 그에 맞게 응답을 조정할 수 있습니다.

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    proactivity=types.ProactivityConfig(proactive_audio=True),
    enable_affective_dialog=True,
)
```

두 동작 모두 확률적이며 응답의 예측 가능성을 낮추므로 격식 있는 컨텍스트, 높은 정확도가 요구되는 환경 및 디버깅 중에는 꺼두는 것이 좋습니다.

이 설정은 `gemini-live-2.5-flash-native-audio`에 적용됩니다. 일부 라이브 모델은 이 동작이 내장되어 있어 두 설정을 모두 무시하므로 별도로 설정할 필요가 없습니다. [지원 모델](models.md#live-models)을 참고하세요.
