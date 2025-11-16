# 런타임 구성(Runtime Configuration)

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

`RunConfig`는 ADK의 에이전트에 대한 런타임 동작과 옵션을 정의합니다. 이는 음성 및 스트리밍 설정, 함수 호출, 아티팩트(artifact) 저장, LLM 호출 제한 등을 제어합니다.

에이전트 실행을 구성할 때 `RunConfig`를 전달하여 에이전트가 모델과 상호 작용하고, 오디오를 처리하며, 응답을 스트리ミング하는 방식을 사용자 정의할 수 있습니다. 기본적으로 스트리밍은 활성화되어 있지 않으며 입력은 아티팩트로 보존되지 않습니다. `RunConfig`를 사용하여 이러한 기본값을 재정의하세요.

## 클래스 정의

`RunConfig` 클래스는 에이전트의 런타임 동작에 대한 구성 매개변수를 가집니다.

-   Python ADK는 이 유효성 검사를 위해 Pydantic을 사용합니다.
-   Go ADK는 기본적으로 가변 구조체(mutable struct)입니다.
-   Java ADK는 일반적으로 불변 데이터 클래스(immutable data class)를 사용합니다.


=== "Python"

    ```python
    class RunConfig(BaseModel):
        """Configs for runtime behavior of agents."""

        model_config = ConfigDict(
            extra='forbid',
        )

        speech_config: Optional[types.SpeechConfig] = None
        response_modalities: Optional[list[str]] = None
        save_input_blobs_as_artifacts: bool = False
        support_cfc: bool = False
        streaming_mode: StreamingMode = StreamingMode.NONE
        output_audio_transcription: Optional[types.AudioTranscriptionConfig] = None
        max_llm_calls: int = 500
    ```

=== "Go"

    ```go
    type StreamingMode string

    const (
    	StreamingModeNone StreamingMode = "none"
    	StreamingModeSSE  StreamingMode = "sse"
    )

    // RunConfig controls runtime behavior.
    type RunConfig struct {
    	// Streaming mode, None or StreamingMode.SSE.
    	StreamingMode StreamingMode
    	// Whether or not to save the input blobs as artifacts
    	SaveInputBlobsAsArtifacts bool
    }
    ```

=== "Java"

    ```java
    public abstract class RunConfig {

      public enum StreamingMode {
        NONE,
        SSE,
        BIDI
      }

      public abstract @Nullable SpeechConfig speechConfig();

      public abstract ImmutableList<Modality> responseModalities();

      public abstract boolean saveInputBlobsAsArtifacts();

      public abstract @Nullable AudioTranscriptionConfig outputAudioTranscription();

      public abstract int maxLlmCalls();

      // ...
    }
    ```

## 런타임 매개변수

| 매개변수                        | Python 타입                                  | Go 타입         | Java 타입                                             | 기본값 (Py / Go / Java )               | 설명                                                                                                                              |
| :------------------------------ | :------------------------------------------- |:----------------|:------------------------------------------------------|:----------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------|
| `speech_config`                 | `Optional[types.SpeechConfig]`               | N/A             | `SpeechConfig` (`@Nullable`을 통해 nullable)           | `None` / N/A / `null`                   | `SpeechConfig` 타입을 사용하여 음성 합성(음성, 언어)을 구성합니다.                                                               |
| `response_modalities`           | `Optional[list[str]]`                        | N/A             | `ImmutableList<Modality>`                             | `None` / N/A / 빈 `ImmutableList`       | 원하는 출력 모달리티 목록입니다 (예: Python: `["TEXT", "AUDIO"]`; Java: 구조화된 `Modality` 객체 사용).                            |
| `save_input_blobs_as_artifacts` | `bool`                                       | `bool`          | `boolean`                                             | `False` / `false` / `false`             | `true`인 경우, 디버깅/감사를 위해 입력 blob(예: 업로드된 파일)을 실행 아티팩트로 저장합니다.                                     |
| `streaming_mode`                | `StreamingMode`                              | `StreamingMode` | `StreamingMode`                                       | `StreamingMode.NONE` / `agent.StreamingModeNone` / `StreamingMode.NONE` | 스트리밍 동작을 설정합니다: `NONE`(기본값), `SSE`(서버-전송 이벤트), 또는 `BIDI`(양방향) (**Python/Java**).                            |
| `output_audio_transcription`    | `Optional[types.AudioTranscriptionConfig]`   | N/A             | `AudioTranscriptionConfig` (`@Nullable`을 통해 nullable) | `None` / N/A / `null`                   | `AudioTranscriptionConfig` 타입을 사용하여 생성된 오디오 출력의 텍스트 변환을 구성합니다.                                        |
| `max_llm_calls`                 | `int`                                        | N/A             | `int`                                                 | `500` / N/A / `500`                     | 실행당 총 LLM 호출을 제한합니다. `0` 또는 음수 값은 무제한(경고 표시)을 의미하며, `sys.maxsize`는 `ValueError`를 발생시킵니다.       |
| `support_cfc`                   | `bool`                                       | N/A             | `bool`                                                | `False` / N/A / `false`                 | **Python:** 구성적 함수 호출(Compositional Function Calling)을 활성화합니다. `streaming_mode=SSE`가 필요하며 LIVE API를 사용합니다. **실험적 기능.** |

### `speech_config`

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

!!! Note
    `SpeechConfig`의 인터페이스나 정의는 언어에 관계없이 동일합니다.

오디오 기능이 있는 라이브 에이전트를 위한 음성 구성 설정입니다.
`SpeechConfig` 클래스는 다음 구조를 가집니다:

```python
class SpeechConfig(_common.BaseModel):
    """The speech generation configuration."""

    voice_config: Optional[VoiceConfig] = Field(
        default=None,
        description="""The configuration for the speaker to use.""",
    )
    language_code: Optional[str] = Field(
        default=None,
        description="""Language code (ISO 639. e.g. en-US) for the speech synthesization.
        Only available for Live API.""",
    )
```

`voice_config` 매개변수는 `VoiceConfig` 클래스를 사용합니다:

```python
class VoiceConfig(_common.BaseModel):
    """The configuration for the voice to use."""

    prebuilt_voice_config: Optional[PrebuiltVoiceConfig] = Field(
        default=None,
        description="""The configuration for the speaker to use.""",
    )
```

그리고 `PrebuiltVoiceConfig`는 다음 구조를 가집니다:

```python
class PrebuiltVoiceConfig(_common.BaseModel):
    """The configuration for the prebuilt speaker to use."""

    voice_name: Optional[str] = Field(
        default=None,
        description="""The name of the prebuilt voice to use.""",
    )
```

이러한 중첩된 구성 클래스를 통해 다음을 지정할 수 있습니다:

* `voice_config`: 사용할 사전 빌드된 음성의 이름 (`PrebuiltVoiceConfig` 내)
* `language_code`: 음성 합성을 위한 ISO 639 언어 코드 (예: "en-US")

음성 지원 에이전트를 구현할 때, 에이전트가 말하는 소리를 제어하기 위해 이 매개변수들을 구성하세요.

### `response_modalities`

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

에이전트의 출력 모달리티를 정의합니다. 설정되지 않은 경우 기본값은 AUDIO입니다.
응답 모달리티는 에이전트가 다양한 채널(예: 텍스트, 오디오)을 통해 사용자와 소통하는 방식을 결정합니다.

### `save_input_blobs_as_artifacts`

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

활성화되면, 입력 blob이 에이전트 실행 중에 아티팩트로 저장됩니다.
이는 개발자가 에이전트가 수신한 정확한 데이터를 검토할 수 있게 하여 디버깅 및 감사 목적에 유용합니다.

### `support_cfc`

<div class="language-support-tag" title="이 기능은 실험적인 미리보기 릴리스입니다.">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-preview">실험적 기능</span>
</div>

구성적 함수 호출(Compositional Function Calling, CFC) 지원을 활성화합니다. StreamingMode.SSE를 사용할 때만 적용 가능합니다. 활성화되면, CFC 기능은 LIVE API에서만 지원되므로 해당 API가 호출됩니다.

!!! example "실험적 릴리스"

    `support_cfc` 기능은 실험적이며 향후 릴리스에서 API나 동작이 변경될 수 있습니다.

### `streaming_mode`

<div class="language-support-tag" title="이 기능은 실험적인 미리보기 릴리스입니다.">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span>
</div>

에이전트의 스트리밍 동작을 구성합니다. 가능한 값:

* `StreamingMode.NONE`: 스트리밍 없음; 응답이 완전한 단위로 전달됨
* `StreamingMode.SSE`: 서버-전송 이벤트(Server-Sent Events) 스트리밍; 서버에서 클라이언트로의 단방향 스트리밍
* `StreamingMode.BIDI`: 양방향(Bidirectional) 스트리밍; 양방향으로 동시 통신

스트리밍 모드는 성능과 사용자 경험 모두에 영향을 미칩니다. SSE 스트리밍은 사용자가 부분적인 응답이 생성되는 것을 볼 수 있게 해주며, BIDI 스트리밍은 실시간 상호작용 경험을 가능하게 합니다.

### `output_audio_transcription`

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

오디오 응답 기능이 있는 라이브 에이전트의 오디오 출력을 텍스트로 변환하기 위한 구성입니다. 접근성, 기록 보관 및 다중 모드 애플리케이션을 위해 오디오 응답의 자동 텍스트 변환을 활성화합니다.

### `max_llm_calls`

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

주어진 에이전트 실행에 대한 총 LLM 호출 횟수에 제한을 설정합니다.

* 0보다 크고 `sys.maxsize`보다 작은 값: LLM 호출에 제한을 적용
* 0 이하의 값: 무제한 LLM 호출 허용 *(프로덕션 환경에서는 권장하지 않음)*

이 매개변수는 과도한 API 사용과 잠재적인 프로세스 폭주를 방지합니다. LLM 호출은 종종 비용을 발생시키고 리소스를 소비하므로 적절한 제한을 설정하는 것이 중요합니다.

## 유효성 검사 규칙

`RunConfig` 클래스는 적절한 에이전트 작동을 보장하기 위해 매개변수들의 유효성을 검사합니다. Python ADK는 자동 타입 검증을 위해 `Pydantic`을 사용하는 반면, Java ADK는 정적 타이핑에 의존하며 `RunConfig` 생성 시 명시적인 검사를 포함할 수 있습니다.
특히 `max_llm_calls` 매개변수의 경우:

1. 극단적으로 큰 값(Python의 `sys.maxsize`나 Java의 `Integer.MAX_VALUE` 등)은 문제를 방지하기 위해 일반적으로 허용되지 않습니다.

2. 0 이하의 값은 일반적으로 무제한 LLM 상호 작용에 대한 경고를 발생시킵니다.

## 예제

### 기본 런타임 구성

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.NONE,
        max_llm_calls=100
    )
    ```

=== "Go"

    ```go
    import "google.golang.org/adk/agent"

    config := agent.RunConfig{
        StreamingMode: agent.StreamingModeNone,
    }
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;

    RunConfig config = RunConfig.builder()
            .setStreamingMode(StreamingMode.NONE)
            .setMaxLlmCalls(100)
            .build();
    ```

이 구성은 100회의 LLM 호출 제한을 가진 비-스트리밍 에이전트를 생성하며, 완전한 응답이 선호되는 간단한 작업 지향 에이전트에 적합합니다.

### 스트리밍 활성화

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode

    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=200
    )
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
        .setStreamingMode(StreamingMode.SSE)
        .setMaxLlmCalls(200)
        .build();
    ```

SSE 스트리밍을 사용하면 사용자는 응답이 생성되는 과정을 볼 수 있어 챗봇과 어시스턴트에서 더 반응적인 느낌을 제공합니다.

### 음성 지원 활성화

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode
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
        save_input_blobs_as_artifacts=True,
        support_cfc=True,
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=1000,
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    import com.google.common.collect.ImmutableList;
    import com.google.genai.types.Content;
    import com.google.genai.types.Modality;
    import com.google.genai.types.Part;
    import com.google.genai.types.PrebuiltVoiceConfig;
    import com.google.genai.types.SpeechConfig;
    import com.google.genai.types.VoiceConfig;

    RunConfig runConfig =
        RunConfig.builder()
            .setStreamingMode(StreamingMode.SSE)
            .setMaxLlmCalls(1000)
            .setSaveInputBlobsAsArtifacts(true)
            .setResponseModalities(ImmutableList.of(new Modality("AUDIO"), new Modality("TEXT")))
            .setSpeechConfig(
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

이 종합적인 예제는 다음과 같은 기능을 가진 에이전트를 구성합니다:

* "Kore" 음성(미국 영어)을 사용한 음성 기능
* 오디오 및 텍스트 출력 모달리티 모두 지원
* 입력 blob에 대한 아티팩트 저장 (디버깅에 유용)
* 반응적인 상호 작용을 위한 SSE 스트리밍
* 1000회의 LLM 호출 제한

### 실험적인 CFC 지원 활성화

<div class="language-support-tag" title="이 기능은 실험적인 미리보기 릴리스입니다.">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-preview">실험적 기능</span>
</div>

    ```python
        from google.genai.adk import RunConfig, StreamingMode

        config = RunConfig(
            streaming_mode=StreamingMode.SSE,
            support_cfc=True,
            max_llm_calls=150
        )
    ```

구성적 함수 호출을 활성화하면 모델 출력에 따라 동적으로 함수를 실행할 수 있는 에이전트를 생성할 수 있으며, 이는 복잡한 워크플로가 필요한 애플리케이션에 강력합니다.