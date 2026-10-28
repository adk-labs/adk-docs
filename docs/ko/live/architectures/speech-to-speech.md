# 음성 대 음성(Speech-to-speech) 아키텍처

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

음성 대 음성(speech-to-speech) 아키텍처에서는 단일 멀티모달 모델이 입력과 출력 사이에서 음성을 텍스트로 변환하지 않고, 지속적인 [Gemini Live API](https://ai.google.dev/gemini-api/docs/live-api) 연결을 통해 들어오는 오디오를 처리하고 추론 및 도구 호출을 실행하며 음성 오디오를 직접 생성합니다.

연결형 STT-LLM-TTS 파이프라인과의 비교는 [음성 아키텍처 선택](index.md)을 참조하세요.

## 음성 대 음성 에이전트 구성

지원되는 [네이티브 오디오 Live 모델](../models.md#live-models)을 에이전트에 전달합니다:

=== "Python"

    ```python
    import os
    from google.adk.agents import Agent

    root_agent = Agent(
        name="voice_assistant",
        model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
        instruction="You are a helpful voice assistant.",
        tools=[...],
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;

    LlmAgent rootAgent =
        LlmAgent.builder()
            .name("voice_assistant")
            .model("gemini-live-2.5-flash-native-audio")
            .instruction("You are a helpful voice assistant.")
            .build();
    ```

`adk web`으로 에이전트를 실행하거나 [`Runner.run_live()`](../sessions.md#the-run_live-loop)에 전달합니다.

## 음성 대 음성 전용 기능

다음 기능은 네이티브 오디오 모델에만 적용됩니다:

- **실시간 비디오 및 이미지 입력**: 오디오와 함께 실시간 카메라 또는 화면 프레임을 스트리밍하여 사용자가 보여주는 화면을 에이전트가 볼 수 있게 합니다. [오디오 및 비디오](../audio-video.md#images-and-video)를 참조하세요.
- **공감형 대화(Affective dialog) 및 능동형 오디오(Proactive audio)**: 지원되는 네이티브 오디오 모델은 사용자의 감정 표현에 맞춰 말하는 어조를 조절하고, 언제 말하거나 침묵할지 결정할 수 있습니다. [능동성 및 공감형 대화](../configuration.md#proactivity-and-affective-dialog)를 참조하세요.
- **상태 저장 세션 재개 및 컨텍스트 압축**: Live API는 상태 저장 WebSocket 세션에 대화 상태를 유지하므로, ADK는 연결 시간 초과 시의 자동 [세션 재개](../sessions.md#session-resumption)와 장기 실행 세션을 위한 [컨텍스트 윈도우 압축](../sessions.md#context-window-compression)을 지원합니다.
- **세션 수준 음성 및 VAD 제어**: [`RunConfig`](../configuration.md) 또는 모델 인스턴스를 통해 세션 수준에서 음성 선택 및 자동 음성 활동 감지(VAD)를 구성할 수 있습니다.

## 고려 사항 및 제한 사항

- **고정된 모델 선택**: 음성 대 음성 아키텍처는 Gemini Live API를 지원하는 모델([지원되는 모델](../models.md#live-models))이 필요합니다. 라이브 음성 세션에서 표준 Gemini 텍스트 모델이나 서드파티 LLM을 사용하려면 [캐스케이드 아키텍처](cascade.md)를 사용하세요.
- **오디오 전용 출력**: 네이티브 오디오 모델은 오디오만 출력하며 `Runner.run_async()`에서는 실행되지 않습니다. 대화 텍스트가 필요한 경우 [오디오 트랜스크립션](../configuration.md#audio-transcription)을 읽으세요.
- **가드레일이 오디오와 함께 트랜스크립션을 평가함**: 모델이 중간 텍스트 단계 없이 직접 오디오를 생성하므로, [대화 검증 콜백](../guardrails.md#conversation-validation)은 합성 전에 텍스트를 가로채는 대신 입력 및 출력 트랜스크립션을 검사합니다. 오디오가 생성되기 전에 반드시 텍스트를 필터링하거나 마스킹(redact)해야 하는 경우에는 [캐스케이드](cascade.md#custom-speech-transforms)를 사용하세요.
