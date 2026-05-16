# 런타임 구성(Runtime Configuration)

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

`RunConfig`는 streaming mode, speech setting, LLM call limit, live agent option 등
에이전트의 런타임 동작을 제어합니다. 기본 동작을 재정의하려면 `RunConfig`를
`runner.run_async()` 또는 `runner.run_live()`에 전달합니다.

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=200,
    )

    async for event in runner.run_async(
        ...,
        run_config=config,
    ):
        ...
    ```

=== "TypeScript"

    ```typescript
    import { RunConfig, StreamingMode } from '@google/adk';

    const config: RunConfig = {
      streamingMode: StreamingMode.SSE,
      maxLlmCalls: 200,
    };
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/agent"

    config := agent.RunConfig{
        StreamingMode: agent.StreamingModeSSE,
    }
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;

    RunConfig config = RunConfig.builder()
        .streamingMode(StreamingMode.SSE)
        .maxLlmCalls(200)
        .build();
    ```

## 세션 및 컨텍스트 관리

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

Long-running session에서는 얼마나 많은 history를 load할지, context window를 압축할지
제어할 수 있습니다.

- `get_session_config`: session을 load할 때 가져오는 event를 제한합니다. 매 invocation마다
  전체 event history를 load하지 않도록 `num_recent_events` 또는 `after_timestamp`를
  사용합니다.
- `context_window_compression`: LLM input에 대한 context window compression을 활성화합니다.
  session이 model context limit에 가까워질 때 유용합니다.

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig
    from google.adk.sessions.base_session_service import GetSessionConfig

    config = RunConfig(
        get_session_config=GetSessionConfig(num_recent_events=50),
    )
    ```

## 스트리밍 활성화

에이전트가 응답을 전달하는 방식을 제어하려면 `streaming_mode` 매개변수를 설정합니다.

- **`StreamingMode.NONE`**(기본값): runner가 turn마다 하나의 완성된 응답을 반환합니다.
  CLI tool, batch processing, synchronous workflow에 적합합니다.
- **`StreamingMode.SSE`**: Server-Sent Events streaming입니다. LLM이 생성하는 동안 runner가
  partial event를 yield하여 typewriter-style UI와 real-time chat display를 구현할 수 있습니다.
- **`StreamingMode.BIDI`**: bidirectional streaming용으로 예약되어 있지만 표준
  `run_async()` path에서는 **사용되지 않습니다**. Bidirectional streaming에는
  `runner.run_live()`를 사용하세요.

`StreamingMode.SSE`와 함께 `support_cfc=True`를 설정하면 Compositional Function Calling(CFC)을
활성화할 수 있습니다. CFC는 모델이 function call을 동적으로 구성하고 실행할 수 있게 하며,
내부적으로 Live API를 사용합니다.

!!! example "Experimental"
    CFC 지원은 실험적이며 향후 릴리스에서 API나 동작이 변경될 수 있습니다.

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        support_cfc=True,
        max_llm_calls=150,
    )
    ```

=== "TypeScript"

    ```typescript
    import { RunConfig, StreamingMode } from '@google/adk';

    const config: RunConfig = {
        streamingMode: StreamingMode.SSE,
        supportCfc: true,
        maxLlmCalls: 150,
    };
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/agent"

    config := agent.RunConfig{
        StreamingMode: agent.StreamingModeSSE,
    }
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;

    RunConfig config = RunConfig.builder()
        .streamingMode(StreamingMode.SSE)
        .maxLlmCalls(150)
        .build();
    ```

## 오디오 및 음성 구성

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-java">Java</span>
</div>

Voice-enabled agent에서는 speech synthesis, audio transcription, response modality를
구성합니다.

- `speech_config`: speech output의 voice와 language를 설정합니다. 예를 들어 `en-US`와
  "Kore" voice를 사용할 수 있습니다.
- `response_modalities`: output format을 제어합니다. 말하기와 text 반환을 모두 수행하는
  에이전트에는 `["AUDIO", "TEXT"]`로 설정합니다.
- `output_audio_transcription` / `input_audio_transcription`: model의 audio output과 사용자의
  audio input transcription을 활성화합니다. Python에서는 둘 다 기본값이
  `AudioTranscriptionConfig()`입니다.

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, StreamingMode
    from google.genai import types

    config = RunConfig(
        speech_config=types.SpeechConfig(
            language_code="en-US",
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"
                )
            ),
        ),
        response_modalities=["AUDIO", "TEXT"],
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=1000,
    )
    ```

=== "TypeScript"

    ```typescript
    import { RunConfig, StreamingMode } from '@google/adk';
    import { Modality } from '@google/genai';

    const config: RunConfig = {
        speechConfig: {
            languageCode: "en-US",
            voiceConfig: {
                prebuiltVoiceConfig: {
                    voiceName: "Kore"
                }
            },
        },
        responseModalities: [Modality.AUDIO, Modality.TEXT],
        streamingMode: StreamingMode.SSE,
        maxLlmCalls: 1000,
    };
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    import com.google.common.collect.ImmutableList;
    import com.google.genai.types.Modality;
    import com.google.genai.types.PrebuiltVoiceConfig;
    import com.google.genai.types.SpeechConfig;
    import com.google.genai.types.VoiceConfig;

    RunConfig runConfig =
        RunConfig.builder()
            .streamingMode(StreamingMode.SSE)
            .maxLlmCalls(1000)
            .responseModalities(ImmutableList.of(new Modality(Modality.Known.AUDIO), new Modality(Modality.Known.TEXT)))
            .speechConfig(
                SpeechConfig.builder()
                    .voiceConfig(
                        VoiceConfig.builder()
                            .prebuiltVoiceConfig(
                                PrebuiltVoiceConfig.builder().voiceName("Kore").build())
                            .build())
                    .languageCode("en-US")
                    .build())
            .build();
    ```

## Live agent 구성

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

`runner.run_live()`를 사용할 때는 다음 추가 매개변수로 real-time behavior를 구성합니다.

- `realtime_input_config`: 사용자로부터 audio input을 받는 방식을 구성합니다.
- `proactivity`: model이 proactive하게 응답하고 관련 없는 input을 무시할 수 있게 합니다.
- `enable_affective_dialog`: `True`이면 model이 사용자 감정을 감지하고 그에 맞게 tone을 조정합니다.
- `avatar_config`: live agent용 avatar를 구성합니다.
- `session_resumption`: disconnect 전반의 transparent session resumption을 활성화합니다.
- `save_live_blob`: `True`이면 live audio 및 video data를 session과 artifact service에 저장합니다.
- `tool_thread_pool_config`: event loop가 사용자 interruption에 responsive하게 유지되도록 tool
  execution을 background thread pool에서 실행합니다.

모든 매개변수가 모든 언어에서 제공되는 것은 아닙니다. 언어별 세부 정보는
[API reference](#api-reference)를 참고하세요.

=== "Python"

    ```python
    from google.adk.agents.run_config import RunConfig, ToolThreadPoolConfig

    config = RunConfig(
        save_live_blob=True,
        tool_thread_pool_config=ToolThreadPoolConfig(max_workers=8),
    )
    ```

    !!! note "Thread pool and the GIL"
        Thread pool은 blocking I/O와 GIL을 release하는 C extension(예: `time.sleep()`,
        network call, numpy)에 도움이 됩니다. 순수 Python CPU-bound code에는 도움이 되지
        않습니다. GIL이 Python bytecode의 진정한 병렬 실행을 막기 때문입니다.

=== "TypeScript"

    ```typescript
    import { RunConfig } from '@google/adk';

    const config: RunConfig = {
        enableAffectiveDialog: true,
        proactivity: {
            proactiveAudio: true,
        },
    };
    ```

## 런타임 제한 및 디버깅 구성

다음 매개변수로 runtime guardrail과 debugging을 제어합니다.

- `max_llm_calls`: run당 총 LLM call 수를 제한합니다(기본값: 500). 0 또는 음수는 무제한
  호출을 의미하지만 production에서는 권장하지 않습니다. `sys.maxsize` 이상의 값은 오류를
  발생시킵니다.
- `save_input_blobs_as_artifacts`: `True`이면 input blob(예: uploaded file)을 debugging과
  auditing용 run artifact로 저장합니다.
- `custom_metadata`: invocation에 첨부되는 임의 metadata의 `dict[str, Any]`입니다. tracing
  또는 logging에 유용합니다.

## API reference

전체 field, type, default 목록은 각 언어의 API reference를 참고하세요.

- [Python API reference](../api-reference/python/google-adk.html#google.adk.agents.RunConfig)
- [TypeScript API reference](../api-reference/typescript/interfaces/RunConfig.html)
- [Go API reference](https://pkg.go.dev/google.golang.org/adk/agent#RunConfig)
- [Java API reference](../api-reference/java/com/google/adk/agents/RunConfig.html)
