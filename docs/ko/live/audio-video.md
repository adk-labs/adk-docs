# 라이브 에이전트를 위한 오디오 및 비디오

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span>
</div>

오디오와 비디오는 라이브 에이전트를 진정한 실시간 대화형으로 만들어 주는 요소이며, 정확한 포맷을 맞추는 것이 핵심입니다. Live API는 오디오에 대해 특정한 PCM 샘플 레이트를 요구하며, 이미지와 비디오 프레임은 텍스트와 다른 전송 방식을 사용합니다.

**ADK는 미디어를 대신 변환해주지 않습니다.** 샘플 레이트, 인코딩, MIME 타입을 올바르게 맞추는 것은 개발자의 책임이며, 잘못된 포맷을 전달하면 유용한 오류 메시지 대신 무음, 노이즈 또는 연결 오류가 발생합니다. 아래에 해당 규격을 설명합니다.

이러한 모달리티를 지원하는 모델은 [지원 모델](models.md)을 참고하세요. 음성, 전사 및 턴(turn) 감지는 [구성](configuration.md)을 참고하세요. 이 모든 기능을 이미 구현한 클라이언트를 체험하려면 `adk web`에서 에이전트를 실행해 보세요. 직접 작성하려면 [커스텀 서버 구축](custom-server.md#connect-a-client)을 참고하세요.

## 오디오 입력

마이크 오디오는 [`send_realtime()`](sessions.md#liverequestqueue)를 통해 원시 바이트(raw bytes)로 전송합니다. 바이트는 Live API가 요구하는 형식이어야 하며, ADK는 이를 변환 없이 그대로 전달합니다:

| 속성 | 값 |
| :--- | :--- |
| 인코딩 | 16-bit PCM, signed, little-endian |
| 샘플 레이트 | 16,000 Hz (16 kHz) |
| 채널 | 모노(Mono) |
| MIME 타입 | `audio/pcm;rate=16000` |

```python
from google.genai import types

live_request_queue.send_realtime(
    types.Blob(mime_type="audio/pcm;rate=16000", data=audio_data)
)
```

낮은 지연 시간을 위해 작은 청크(chunk) 단위로 오디오를 스트리밍하세요. `LiveRequestQueue`는 결합(coalescing) 없이 각 청크를 즉시 전달하므로, 전송하는 청크 크기가 모델이 수신하는 세분성이 됩니다:

- **초저지연** (실시간 대화): 청크당 10~20 ms.
- **균형** (권장): 청크당 50~100 ms. 16 kHz에서 100 ms는 `16000 × 0.1 × 2 = 3200` 바이트입니다.
- **낮은 오버헤드**: 청크당 100~200 ms.

세션 전체에 일관된 청크 크기를 사용하고, 다음 청크를 보내기 전에 모델 응답을 기다리지 마세요. 모델은 턴 단위가 아니라 지속적으로 오디오를 처리합니다. [음성 활동 감지(VAD)](configuration.md#voice-activity-detection-vad)가 켜져 있는 경우(기본값) 지속적으로 스트리밍하고 API가 음성을 감지하도록 두세요. [활동 신호](sessions.md#liverequestqueue)는 VAD를 비활성화한 경우에만 전송하세요.

## 오디오 출력

`response_modalities=["AUDIO"]`(라이브 기본값)를 사용하는 경우, 모델은 이벤트 스트림에서 `inline_data` 파트로 오디오를 반환합니다:

| 속성 | 값 |
| :--- | :--- |
| 인코딩 | 16-bit PCM, signed, little-endian |
| 샘플 레이트 | 24,000 Hz (24 kHz) — 입력 레이트인 16 kHz와 다름에 유의 |
| 채널 | 모노(Mono) |
| MIME 타입 | `audio/pcm;rate=24000` |

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("audio/pcm"):
                await play_audio(part.inline_data.data)  # 원시 24 kHz PCM 바이트
```

바이트는 바로 재생할 수 있는 상태로 도착하므로 클라이언트 측에서 별도의 디코딩이 필요하지 않습니다. Live API는 네트워크를 통해 base64로 오디오를 전송하지만, `google.genai`가 대신 디코딩하므로 `part.inline_data.data`는 이미 `bytes` 타입입니다. 어떤 이벤트가 오디오를 전달하고 전사(transcription)와 어떻게 인터리빙되는지는 [이벤트](events.md#audio)를 참고하세요. 아티팩트 서비스에 오디오를 저장하려면 [`save_live_blob=True`](configuration.md#save_live_blob)를 설정하세요.

## 이미지 및 비디오

이미지와 비디오는 오디오와 동일한 [`send_realtime()`](sessions.md#liverequestqueue) 메서드를 통해 개별 JPEG 프레임으로 전송됩니다. 비디오 코덱은 사용되지 않으며, 비디오 스트림은 각 프레임이 자체 Blob으로 전송되는 정지 프레임들의 시퀀스입니다.

| 속성 | 값 |
| :--- | :--- |
| 포맷 | JPEG (`image/jpeg`) |
| 프레임 레이트 | 초당 약 1프레임 (~1 FPS, 권장 최대값) |
| 해상도 | 768×768 픽셀 (권장) |

```python
from google.genai import types

live_request_queue.send_realtime(
    types.Blob(mime_type="image/jpeg", data=jpeg_bytes)
)
```

약 1 FPS에서 모델은 사용자가 카메라로 비추고 있거나 논의 중인 대상을 볼 수 있지만, 움직임에 의존하는 것은 파악할 수 없습니다. 동작 인식, 스포츠 분석 및 모션 추적에는 이 방식이 제공하지 않는 시간적 해상도가 필요합니다.

[Shopper's Concierge 데모](https://youtu.be/LwHPYyw7u6U?si=lG9gl9aSIuu-F4ME&t=40)에서 앱은 사용자가 업로드한 이미지를 `send_realtime()`으로 전송하며, 에이전트는 컨텍스트를 인식하고 전자상거래 카탈로그에서 일치하는 상품을 검색합니다.

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
<iframe width="560" height="315" src="https://www.youtube.com/embed/LwHPYyw7u6U?si=lG9gl9aSIuu-F4ME&amp;start=40" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>
</div>

프레임이 도착할 때마다 에이전트가 반응할 수 있도록 라이브 비디오 스트림을 도구에 전달하는 방법은 [스트리밍 도구](tools.md#streaming-tools)를 참고하세요.
