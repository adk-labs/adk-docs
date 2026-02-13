# Part 5: Audio, Image, Video 사용 방법

이 섹션에서는 ADK Live API 통합에서 오디오, 이미지, 비디오 기능을 다룹니다.
지원 모델, 오디오 모델 아키텍처, 포맷/스펙, 음성/비디오 기능 구현 모범 사례를 포함합니다.

## 오디오 사용 방법

Live API 오디오 기능은 양방향 오디오 스트리밍으로
서브초 단위 지연의 자연스러운 음성 대화를 지원합니다.

### 오디오 입력 전송

**오디오 포맷 요구사항:**

`send_realtime()` 호출 전에 오디오가 다음 형식이어야 합니다.

- **Format**: 16-bit PCM (signed integer)
- **Sample Rate**: 16,000 Hz (16kHz)
- **Channels**: Mono

ADK는 오디오 포맷 변환을 수행하지 않습니다.
잘못된 포맷은 품질 저하 또는 오류를 유발합니다.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L181-L184" target="_blank">main.py:181-184</a>'
audio_blob = types.Blob(
    mime_type="audio/pcm;rate=16000",
    data=audio_data
)
live_request_queue.send_realtime(audio_blob)
```

#### 오디오 입력 전송 모범 사례

1. **청크 스트리밍**: 지연 요구에 맞춰 작은 청크로 전송
   - 초저지연: 10~20ms
   - 균형(권장): 50~100ms
   - 오버헤드 절감: 100~200ms

2. **즉시 전달**: `LiveRequestQueue`는 청크를 배치/병합 없이 즉시 전달

3. **연속 처리**: 기본 자동 VAD 환경에서는 연속 전송하고 API가 경계를 감지하게 함

4. **Activity 신호**: VAD를 명시적으로 끈 경우에만 수동 턴 제어로 사용

#### 클라이언트에서 오디오 입력 처리

브라우저에서는 Web Audio API + AudioWorklet로 마이크를 캡처하고,
16kHz PCM16으로 변환해 WebSocket으로 전송합니다.

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/audio-recorder.js#L7-L58" target="_blank">audio-recorder.js:7-58</a>'
// Start audio recorder worklet
export async function startAudioRecorderWorklet(audioRecorderHandler) {
    const audioRecorderContext = new AudioContext({ sampleRate: 16000 });
    const workletURL = new URL("./pcm-recorder-processor.js", import.meta.url);
    await audioRecorderContext.audioWorklet.addModule(workletURL);

    micStream = await navigator.mediaDevices.getUserMedia({
        audio: { channelCount: 1 }
    });
    const source = audioRecorderContext.createMediaStreamSource(micStream);

    const audioRecorderNode = new AudioWorkletNode(
        audioRecorderContext,
        "pcm-recorder-processor"
    );

    source.connect(audioRecorderNode);
    audioRecorderNode.port.onmessage = (event) => {
        const pcmData = convertFloat32ToPCM(event.data);
        audioRecorderHandler(pcmData);
    };
    return [audioRecorderNode, audioRecorderContext, micStream];
}

function convertFloat32ToPCM(inputData) {
    const pcm16 = new Int16Array(inputData.length);
    for (let i = 0; i < inputData.length; i++) {
        pcm16[i] = inputData[i] * 0x7fff;
    }
    return pcm16.buffer;
}
```

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/static/js/pcm-recorder-processor.js#L1-L18" target="_blank">pcm-recorder-processor.js:1-18</a>'
class PCMProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
    }

    process(inputs, outputs, parameters) {
        if (inputs.length > 0 && inputs[0].length > 0) {
            const inputChannel = inputs[0][0];
            const inputCopy = new Float32Array(inputChannel);
            this.port.postMessage(inputCopy);
        }
        return true;
    }
}

registerProcessor("pcm-recorder-processor", PCMProcessor);
```

```javascript title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/2f7b82f182659e0990bfb86f6ef400dd82633c07/python/agents/bidi-demo/app/static/js/app.js#L979-L988" target="_blank">app.js:977-986</a>'
function audioRecorderHandler(pcmData) {
    if (websocket && websocket.readyState === WebSocket.OPEN && is_audio) {
        websocket.send(pcmData);
        console.log("[CLIENT TO AGENT] Sent audio chunk: %s bytes", pcmData.byteLength);
    }
}
```

**핵심 구현 포인트:**

- 입력은 16kHz mono PCM16
- AudioWorklet은 메인 스레드와 분리되어 저지연 처리
- Float32(-1.0~1.0) → PCM16 변환 필요
- JSON base64보다 바이너리 WebSocket 프레임 전송이 효율적

### 오디오 출력 수신

`response_modalities=["AUDIO"]`에서 모델 출력 오디오는 `inline_data`로 옵니다.

**출력 포맷:**

- 16-bit PCM
- 24,000 Hz (native audio 모델)
- mono
- MIME: `audio/pcm;rate=24000`

```python
from google.adk.agents.run_config import RunConfig, StreamingMode

run_config = RunConfig(
    response_modalities=["AUDIO"],
    streaming_mode=StreamingMode.BIDI
)

async for event in runner.run_live(
    user_id="user_123",
    session_id="session_456",
    live_request_queue=live_request_queue,
    run_config=run_config
):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                audio_bytes = part.inline_data.data
                await stream_audio_to_client(audio_bytes)
```

!!! note "자동 Base64 디코딩"

    Live API wire 프로토콜은 base64 문자열을 쓰지만,
    google.genai types(Pydantic)가 역직렬화 시 bytes로 자동 디코딩합니다.

#### 클라이언트에서 오디오 이벤트 처리

bidi-demo는 서버에서 오디오를 직접 재생하지 않고,
이벤트를 그대로 클라이언트로 전달해 브라우저에서 재생합니다.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L225-L233" target="_blank">main.py:225-233</a>'
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=live_request_queue,
    run_config=run_config
):
    event_json = event.model_dump_json(exclude_none=True, by_alias=True)
    await websocket.send_text(event_json)
```

오디오 플레이어는 AudioWorklet ring buffer로 지터를 흡수해 재생합니다.
(자세한 구현은 `app.js`, `audio-player.js`, `pcm-player-processor.js` 참고)

## 이미지/비디오 사용 방법

ADK Bidi-streaming에서 이미지와 비디오는 모두 JPEG 프레임으로 처리됩니다.
HLS/mp4/H.264 연속 비디오 스트리밍이 아니라,
정적 이미지/비디오 프레임을 JPEG 단위로 보내는 방식입니다.

**이미지/비디오 스펙:**

- Format: JPEG (`image/jpeg`)
- Frame rate: 최대 권장 1 FPS
- Resolution: 권장 768x768

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L202-L217" target="_blank">main.py:202-217</a>'
image_data = base64.b64decode(json_message["data"])
mime_type = json_message.get("mimeType", "image/jpeg")

image_blob = types.Blob(
    mime_type=mime_type,
    data=image_data
)
live_request_queue.send_realtime(image_blob)
```

**적합하지 않은 경우:**

- 실시간 동작 인식(1 FPS 한계)
- 스포츠 분석/모션 트래킹

### 클라이언트 이미지 입력 처리

브라우저에서 카메라 입력을 받아 캔버스에 프레임을 그리고,
JPEG(base64)로 WebSocket 전송합니다.

(구현 예시는 `app.js`의 `openCameraPreview`, `captureImageFromPreview`, `sendImage` 참고)

### 커스텀 비디오 스트리밍 툴 지원

ADK는 스트리밍 세션 중 비디오 프레임을 처리하는 특수 툴 패턴을 지원합니다.
비동기 제너레이터 기반 툴이 지속적으로 결과를 yield할 수 있습니다.

**라이프사이클:**

1. 시작: 모델이 툴 호출 시 async generator 시작
2. 스트림: `AsyncGenerator`로 연속 결과 반환
3. 중지: `stop_streaming(function_name: str)` 호출/세션 종료/오류 시 취소

자세한 내용: [Streaming Tools documentation](https://google.github.io/adk-docs/streaming/streaming-tools/)

## 오디오 모델 아키텍처 이해

Live API 오디오 모델은 크게 2가지입니다.

- **Native Audio**: 입력/출력을 모두 end-to-end 오디오로 처리
- **Half-Cascade**: 입력은 오디오, 출력은 텍스트 생성 후 TTS 변환

### Native Audio Models

| Audio Model Architecture | Platform | Model | Notes |
|-------------------|----------|-------|-------|
| Native Audio | Gemini Live API | [gemini-2.5-flash-native-audio-preview-12-2025](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash-live) |Publicly available|
| Native Audio | Vertex AI Live API | [gemini-live-2.5-flash-native-audio](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash-live-api) | Public preview |

**특징:**

- 중간 텍스트 변환 없이 오디오 end-to-end
- 자연스러운 prosody
- 확장 음성 라이브러리
- 자동 언어 감지
- affective dialog / proactive audio 같은 고급 기능
- `RunConfig`에서 AUDIO-only

### Half-Cascade Models

| Audio Model Architecture | Platform | Model | Notes |
|-------------------|----------|-------|-------|
| Half-Cascade | Gemini Live API | [gemini-2.0-flash-live-001](https://ai.google.dev/gemini-api/docs/models#gemini-2.0-flash-live) | Deprecated on December 09, 2025 |
| Half-Cascade | Vertex AI Live API | [gemini-live-2.5-flash](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash#2.5-flash) | Private GA, not publicly available |

**특징:**

- 입력 오디오는 네이티브, 출력은 TTS 기반
- `RunConfig`에서 TEXT 모달리티 지원
- `speech_config.language_code`로 명시 언어 제어 가능
- 안정적인 툴 실행/운영 신뢰성
- 8개 prebuilt voice 지원

### 모델명 처리 방법

환경 변수로 모델명을 관리하는 방식이 권장됩니다.

```python
import os
from google.adk.agents import Agent

agent = Agent(
    name="my_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
    tools=[...],
    instruction="..."
)
```

**이유:**

- 모델 릴리스/deprecated가 자주 발생
- Gemini/Vertex 간 모델명 규칙 차이
- 코드 수정 없이 환경별 전환 가능

```bash
DEMO_AGENT_MODEL=gemini-2.5-flash-native-audio-preview-12-2025
# DEMO_AGENT_MODEL=gemini-live-2.5-flash-native-audio
```

!!! note "`.env` 로딩 순서"

    `.env`는 환경변수를 읽는 모듈 import 전에 로드해야 합니다.

## Audio Transcription

Live API는 사용자 입력/모델 출력 오디오를 자동 텍스트 전사할 수 있습니다.
별도 STT 서비스 없이 실시간 자막/로그/접근성 기능 구현이 가능합니다.

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

# 기본적으로 전사는 활성화됨
run_config = RunConfig(
    response_modalities=["AUDIO"]
)

# 전사를 명시적으로 끄는 경우
run_config = RunConfig(
    response_modalities=["AUDIO"],
    input_audio_transcription=None,
    output_audio_transcription=None
)
```

전사는 `Event.input_transcription`, `Event.output_transcription`으로 전달됩니다.
`Transcription` 객체는 `.text`, `.finished`를 가집니다.

```python
async for event in runner.run_live(...):
    if event.input_transcription:
        user_text = event.input_transcription.text
        is_finished = event.input_transcription.finished
        if user_text and user_text.strip():
            update_caption(user_text, is_user=True, is_final=is_finished)

    if event.output_transcription:
        model_text = event.output_transcription.text
        is_finished = event.output_transcription.finished
        if model_text and model_text.strip():
            update_caption(model_text, is_user=False, is_final=is_finished)
```

!!! tip "전사 null 체크"

    1) 객체 존재 확인 → 2) 텍스트 비어있지 않은지 확인

### 멀티 에이전트 전사 요구사항

`sub_agents`가 있는 멀티 에이전트 시나리오에서는
에이전트 전환 컨텍스트 유지를 위해 전사가 자동 활성화됩니다.
`RunConfig`에서 `None`으로 꺼도 내부적으로 활성화됩니다.

## Voice Configuration (Speech Config)

Live API는 오디오 출력 음성을 커스터마이즈하는 `speech_config`를 제공합니다.
에이전트 레벨(개별 에이전트)과 RunConfig 레벨(세션 기본값) 모두 지원합니다.

### Agent-Level Configuration

```python
from google.genai import types
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search

custom_llm = Gemini(
    model="gemini-2.5-flash-native-audio-preview-12-2025",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Puck"
            )
        ),
        language_code="en-US"
    )
)

agent = Agent(
    model=custom_llm,
    tools=[google_search],
    instruction="You are a helpful assistant."
)
```

### RunConfig-Level Configuration

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                voice_name="Kore"
            )
        ),
        language_code="en-US"
    )
)
```

### 우선순위

1. Gemini 인스턴스 `speech_config`
2. RunConfig `speech_config`
3. Live API 기본 음성

멀티 에이전트에서는 에이전트별 다른 음성을 부여할 수 있습니다.

### 음성 목록

Half-cascade 지원 음성:
- Puck
- Charon
- Kore
- Fenrir
- Aoede
- Leda
- Orus
- Zephyr

Native audio는 위 + TTS 확장 목록을 지원합니다.

## Voice Activity Detection (VAD)

VAD는 사용자의 발화 시작/종료를 자동 감지해 자연스러운 턴테이킹을 제공합니다.
기본값은 **활성화**입니다.

### VAD 비활성화가 필요한 경우

- push-to-talk
- 클라이언트 측 VAD 사용
- 수동 턴 제어 UX 요구

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            disabled=True
        )
    )
)
```

### 클라이언트 측 VAD 예시

클라이언트가 RMS 기반 VAD로 `activity_start`/`activity_end`를 보내고,
발화 구간에서만 오디오를 전송하는 패턴입니다.

- CPU/네트워크 절감
- 로컬 감지로 응답성 향상
- 민감도 튜닝 가능

!!! note "Activity signal 타이밍"

    - 첫 오디오 청크 전에 `activity_start`
    - 마지막 오디오 청크 후 `activity_end`

## Proactivity and Affective Dialog

Live API의 고급 대화 기능입니다.

- **Proactive audio**: 명시적 요청 없이도 관련 응답/제안 가능
- **Affective dialog**: 음성 톤/내용의 감정 신호를 반영해 응답 스타일 조정

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig

run_config = RunConfig(
    proactivity=types.ProactivityConfig(proactive_audio=True),
    enable_affective_dialog=True
)
```

### 플랫폼 호환성

- Gemini Live API native audio 모델에서 지원
- half-cascade 모델에서는 미지원
- Vertex AI에서는 모델 가용성 차이에 따라 지원 여부가 달라질 수 있음

## 요약

이번 파트에서는 ADK Bidi-streaming의 멀티모달 기능(오디오/이미지/비디오)을
실무 구현 관점에서 다뤘습니다.
오디오 스펙, native vs half-cascade 아키텍처,
입출력 스트리밍, 전사, VAD, proactivity/affective dialog,
음성 설정 및 플랫폼 호환성까지 이해하면,
텍스트/오디오/이미지/비디오를 통합한 프로덕션급 실시간 AI 애플리케이션을 설계할 수 있습니다.

**축하합니다!**
ADK Bidi-streaming 개발 가이드를 모두 완료했습니다.

← [Previous: Part 4: Understanding RunConfig](part4.md)
