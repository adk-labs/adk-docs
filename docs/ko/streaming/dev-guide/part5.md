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

ADK Gemini Live API Toolkit에서 이미지와 비디오는 모두 JPEG 프레임으로 처리됩니다.
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

Live API는 사용자 입력과 모델 출력 오디오를 자동으로 텍스트 전사할 수 있습니다.
별도 STT 서비스를 붙이지 않아도 실시간 자막, 대화 로그, 접근성 기능을 구현할 수 있습니다.

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

전사는 `Event.input_transcription`, `Event.output_transcription` 필드로 전달됩니다.
각 `Transcription` 객체는 `.text`와 `.finished` 속성을 가집니다.

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

### 전사 전달 방식

전사는 `content.parts`가 아니라 별도 필드로 들어옵니다. 텍스트/오디오 이벤트와 분리해서 처리해야 합니다.

### 멀티 에이전트 전사 요구사항

`sub_agents`가 있는 멀티 에이전트 시나리오에서는
에이전트 전환 컨텍스트 유지를 위해 전사가 자동 활성화됩니다.
`RunConfig`에서 `None`으로 꺼도 내부적으로 활성화됩니다.

### 클라이언트 측 오디오 전사 처리

웹 애플리케이션에서는 서버가 전사 이벤트를 브라우저로 전달하고, UI가 이를 자막이나 말풍선으로 렌더링하는 패턴이 일반적입니다.

1. 서버는 ADK 이벤트를 그대로 WebSocket으로 전달
2. 브라우저는 `inputTranscription` / `outputTranscription` 이벤트를 구분해 처리
3. `finished: true`일 때 말풍선을 최종 확정

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

에이전트 레벨 설정은 멀티 에이전트 워크플로에서 특히 유용합니다. 서로 다른 페르소나나 역할에 다른 목소리를 부여할 수 있습니다.

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

세션 수준 `speech_config`는 단일 에이전트 앱이나 모든 에이전트가 동일한 음성을 사용해야 하는 경우에 적합합니다.

### 우선순위

1. Gemini 인스턴스 `speech_config`
2. RunConfig `speech_config`
3. Live API 기본 음성

멀티 에이전트에서는 에이전트별 다른 음성을 부여할 수 있습니다.

### 구성 파라미터

- `voice_config`: 사용할 프리빌트 음성을 지정합니다.
- `language_code`: 음성 합성 언어 코드를 지정합니다.

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

### 플랫폼 가용성

- Gemini Live API: 문서화된 음성을 그대로 사용할 수 있습니다.
- Vertex AI Live API: 지원 음성이 다를 수 있으므로 공식 문서를 확인해야 합니다.

### 중요 사항

- 음성 설정은 오디오 출력이 가능한 Live API 모델에서만 사용할 수 있습니다.
- `speech_config`는 에이전트 레벨과 세션 레벨 둘 다 설정할 수 있으며, 에이전트 레벨이 우선합니다.
- Native audio 모델은 문맥에서 언어를 자동 판별하는 경우가 많습니다.

!!! note "더 알아보기"

    완전한 RunConfig 참고는 [Part 4: RunConfig 이해하기](part4.md)를 참고하세요.

## Voice Activity Detection (VAD)

VAD는 사용자의 발화 시작/종료를 자동 감지해 자연스러운 턴테이킹을 제공합니다.
기본값은 **활성화**입니다.

### VAD 동작 방식

VAD가 켜져 있으면 Live API는 사용자의 발화 시작, 발화 종료, 턴 전환, 중단을 자동으로 감지합니다.

### VAD 비활성화가 필요한 경우

- push-to-talk
- 클라이언트 측 VAD 사용
- 수동 턴 제어 UX 요구

VAD를 끄면 수동 활동 신호(`ActivityStart`/`ActivityEnd`)를 사용해 턴을 제어해야 합니다.

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

### 서버 측 구성 예시

클라이언트가 활동 신호를 직접 보내는 구조에서는 서버가 자동 VAD를 끄고, `LiveRequestQueue`에 들어오는 신호를 그대로 모델에 전달합니다.

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.genai import types

run_config = RunConfig(
    streaming_mode=StreamingMode.BIDI,
    response_modalities=["AUDIO"],
    realtime_input_config=types.RealtimeInputConfig(
        automatic_activity_detection=types.AutomaticActivityDetection(
            disabled=True
        )
    )
)
```

### 클라이언트 측 VAD 구현 예시

브라우저의 AudioWorklet에서 RMS를 계산해 음성 여부를 판단하고, 음성이 감지된 구간에만 오디오를 전송합니다.

```javascript
class VADProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.threshold = 0.05;
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        if (input && input.length > 0) {
            const channelData = input[0];
            let sum = 0;
            for (let i = 0; i < channelData.length; i++) {
                sum += channelData[i] ** 2;
            }
            const rms = Math.sqrt(sum / channelData.length);
            this.port.postMessage({
                voice: rms > this.threshold,
                rms: rms
            });
        }
        return true;
    }
}
registerProcessor("vad-processor", VADProcessor);
```

### 클라이언트 측 VAD 조정 예시

```javascript
let isSilence = true;
let lastVoiceTime = 0;
const SILENCE_TIMEOUT = 2000;

const vadNode = new AudioWorkletNode(audioContext, "vad-processor");
vadNode.port.onmessage = (event) => {
    const { voice, rms } = event.data;

    if (voice) {
        if (isSilence) {
            websocket.send(JSON.stringify({ type: "activity_start" }));
            isSilence = false;
        }
        lastVoiceTime = Date.now();
    } else {
        if (!isSilence && Date.now() - lastVoiceTime > SILENCE_TIMEOUT) {
            websocket.send(JSON.stringify({ type: "activity_end" }));
            isSilence = true;
        }
    }
};

audioRecorderNode.port.onmessage = (event) => {
    const audioData = event.data;
    if (!isSilence) {
        const pcm16 = convertFloat32ToPCM(audioData);
        const base64Audio = arrayBufferToBase64(pcm16);

        websocket.send(JSON.stringify({
            type: "audio",
            mime_type: "audio/pcm;rate=16000",
            data: base64Audio
        }));
    }
};
```

### 클라이언트 측 VAD 장점 요약

- CPU와 네트워크 사용량 감소
- 서버 왕복 없이 빠른 감지
- 환경에 맞는 감도 조정 가능

### 서버 측 구성

서버는 `RunConfig.realtime_input_config`로 자동 활동 감지를 끄고, 클라이언트가 보낸 활동 신호를 그대로 `LiveRequestQueue`에 전달합니다.

### 클라이언트 측 구현

브라우저의 AudioWorklet에서 RMS를 계산해 음성 여부를 판단하고, 음성이 감지된 구간에만 오디오를 전송합니다.

### 클라이언트 측 조정

`isSilence` 상태와 타임아웃을 함께 사용하면 자연스러운 말 끊김과 재시작을 처리할 수 있습니다.

### 클라이언트 측 VAD의 장점

- CPU와 네트워크 사용량 감소
- 서버 왕복 없이 빠른 감지
- 환경에 맞는 감도 조정 가능

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

### 실용 예시 - Customer Service Bot

```python
from google.genai import types
from google.adk.agents.run_config import RunConfig, StreamingMode

run_config = RunConfig(
    response_modalities=["AUDIO"],
    streaming_mode=StreamingMode.BIDI,
    proactivity=types.ProactivityConfig(proactive_audio=True),
    enable_affective_dialog=True
)

# 예시 상호작용:
# 고객: "주문이 3주째 안 와요..."
# 모델: "정말 죄송합니다. 주문 상태를 바로 확인해 보겠습니다."
```

### Proactivity 테스트 방법

1. 열린 문맥을 제공합니다.
   ```text
   사용자: "다음 달에 일본 여행을 계획 중이에요."
   예상: 모델이 후속 질문이나 제안을 합니다.
   ```
2. 감정 반응을 테스트합니다.
   ```text
   사용자: [짜증 난 톤] "이거 전혀 안 돼요!"
   예상: 모델이 감정을 인식하고 답변 톤을 조정합니다.
   ```
3. 예기치 않은 자발적 응답이 있는지 확인합니다.
   - 관련 정보가 가끔 자동 제안되는지 확인
   - 정말 무관한 입력은 무시하는지 확인
   - 문맥 기반 제안이 나타나는지 확인

### 언제 끄면 좋은가

- 형식적이거나 엄격한 업무 환경
- 결정론적 동작이 중요한 테스트/디버깅
- 감정 반응이 불필요한 고정형 UX

### 비활성화를 고려할 때

- 고정형 UX가 중요한 경우
- 접근성보다 일관성이 우선인 경우
- 디버깅 중 결정론적 출력을 보고 싶은 경우

## Live API 모델 호환성과 가용성

가장 최신의 모델 호환성과 가용성 정보는 항상 공식 문서를 기준으로 확인해야 합니다.

- Gemini Live API 모델: [Gemini models documentation](https://ai.google.dev/gemini-api/docs/models/gemini)
- Vertex AI Live API 모델: [Vertex AI model documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models)

프로덕션 배포 전에는 플랫폼별 지원 여부를 반드시 확인하세요.

### 추가 검증 체크리스트

- 모델명이 현재 문서와 일치하는지 확인합니다.
- 플랫폼별 지원 음성이 같은지 확인합니다.
- 전사, VAD, proactivity를 함께 사용할 때의 동작을 개발 환경에서 먼저 검증합니다.

## 요약

이번 파트에서는 ADK Gemini Live API Toolkit의 멀티모달 기능(오디오/이미지/비디오)을
실무 구현 관점에서 다뤘습니다.
오디오 스펙, native vs half-cascade 아키텍처,
입출력 스트리밍, 전사, VAD, proactivity/affective dialog,
음성 설정 및 플랫폼 호환성까지 이해하면,
텍스트/오디오/이미지/비디오를 통합한 프로덕션급 실시간 AI 애플리케이션을 설계할 수 있습니다.

**축하합니다!**
ADK Gemini Live API Toolkit 개발 가이드를 모두 완료했습니다.

← [Previous: Part 4: Understanding RunConfig](part4.md)
