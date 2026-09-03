# 라이브 에이전트를 위한 커스텀 서버

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span>
</div>

`adk web` 도구는 개발 목적으로 라이브 에이전트를 실행합니다. 마이크와 카메라를 캡처하고, 모델 오디오를 재생하며, 전사를 렌더링하는 브라우저 클라이언트를 함께 제공하므로 자체 코드 없이도 에이전트와 대화할 수 있습니다. 이를 프로덕션에 출시한다는 것은 이를 교체함을 의미합니다. 시작 시 러너와 세션 서비스를 한 번 초기화하고 연결된 사용자마다 하나의 `LiveRequestQueue`를 두어 클라이언트를 `run_live()`로 연결하는 자체 서버를 실행하는 것입니다.

다음은 해당 브릿지의 완전한 FastAPI 구현과 클라이언트가 통신하기 위해 알아야 할 사항입니다. 이 예제가 실제로 적용하는 수명 주기를 다루는 [세션](sessions.md)을 이미 읽었다고 가정합니다.

## FastAPI 애플리케이션 예제

이 FastAPI 애플리케이션은 브릿지를 구현합니다. WebSocket 메시지를 `LiveRequestQueue`로 전달하는 업스트림(upstream) 태스크와, `run_live()` 이벤트를 다시 클라이언트로 전달하는 다운스트림(downstream) 태스크라는 두 개의 동시 태스크를 실행합니다.

```python
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google_search_agent.agent import agent

# 애플리케이션 설정 (시작 시 한 번 실행)
APP_NAME = "live-agent"

app = FastAPI()

# 세션 서비스 정의
session_service = InMemorySessionService()

# 러너 정의
runner = Runner(
    app_name=APP_NAME,
    agent=agent,
    session_service=session_service
)

@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str) -> None:
    await websocket.accept()

    # 세션별 설정: RunConfig, 세션, 큐
    response_modalities = ["AUDIO"]
    run_config = RunConfig(
        response_modalities=response_modalities,
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        session_resumption=types.SessionResumptionConfig()
    )

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )
    if not session:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

    live_request_queue = LiveRequestQueue()

    async def upstream_task() -> None:
        """WebSocket에서 메시지를 수신하여 LiveRequestQueue로 전송합니다."""
        try:
            while True:
                # WebSocket에서 텍스트 메시지 수신
                data: str = await websocket.receive_text()

                # LiveRequestQueue로 전송
                content = types.Content(parts=[types.Part(text=data)])
                live_request_queue.send_content(content)
        except WebSocketDisconnect:
            # 클라이언트 연결 해제 - 큐 종료 신호 전달
            pass

    async def downstream_task() -> None:
        """run_live()에서 Event를 수신하여 WebSocket으로 전송합니다."""
        async for event in runner.run_live(
            user_id=user_id,
            session_id=session_id,
            live_request_queue=live_request_queue,
            run_config=run_config
        ):
            # 이벤트를 JSON으로 변환하여 WebSocket으로 전송
            await websocket.send_text(
                event.model_dump_json(exclude_none=True, by_alias=True)
            )

    # 두 태스크를 동시에 실행
    try:
        await asyncio.gather(
            upstream_task(),
            downstream_task(),
            return_exceptions=True
        )
    finally:
        live_request_queue.close()  # 오류 발생 시에도 항상 닫음
```

!!! note "비동기(Async) 컨텍스트 필수"

    모든 ADK 양방향 스트리밍 애플리케이션은 **비동기 컨텍스트에서 실행되어야 합니다**. 이 요구 사항은 여러 구성 요소에서 발생합니다:

    - **`run_live()`**: ADK의 스트리밍 메서드는 동기 래퍼가 없는 비동기 제너레이터입니다(`run()`과 다름).
    - **세션 작업**: `get_session()` 및 `create_session()`은 비동기 메서드입니다.
    - **WebSocket 작업**: FastAPI의 `websocket.accept()`, `receive_text()`, `send_text()`는 모두 비동기입니다.
    - **동시 태스크**: 업스트림/다운스트림 패턴은 동시 실행을 위해 `asyncio.gather()`를 필요로 합니다.

    모든 코드 예제는 비동기 컨텍스트(`async def` 내부 또는 코루틴)를 가정합니다.

## 두 개의 태스크를 사용하는 이유

브릿지는 동시에 실행되는 두 개의 루프이며, 이것이 진정한 양방향 통신을 가능하게 합니다:

- **업스트림(Upstream)**은 WebSocket에서 읽어와 `LiveRequestQueue`로 푸시하므로, 에이전트가 문장 중간에 말을 하고 있는 동안에도 사용자가 언제든지 입력을 보낼 수 있습니다.
- **다운스트림(Downstream)**은 `run_live()`에서 이벤트를 읽어 WebSocket에 기록하여 응답, 전사 및 도구 활동이 발생하는 즉시 스트리밍합니다.

순차적으로 실행하면 끼어들기(interruption) 기능을 잃게 됩니다. 사용자가 끼어들어 말하려 할 때 서버가 에이전트의 출력을 읽느라 블로킹되기 때문입니다. `asyncio.gather()`가 두 방향을 동시에 라이브 상태로 유지합니다.

`live_request_queue.close()`는 예외를 포함한 모든 종료 경로에서 실행되어야 합니다. 닫히지 않은 큐는 Live API에 종료 신호를 전달하지 못하여 세션이 타임아웃될 때까지 [동시 세션 할당량](sessions.md#concurrent-sessions)을 묶어둘 수 있으므로, 반드시 `try/finally` 블록으로 보호해야 합니다.

`gather(..., return_exceptions=True)`는 예외를 발생시키지 않고 수집하므로, 정상적인 연결 해제와 오류를 구별해야 하는 경우 반환된 값을 검사하세요.

### 프로덕션 고려사항

이 예제는 핵심 패턴을 보여줍니다. 프로덕션 애플리케이션의 경우 다음 사항을 고려하세요:

- **오류 처리 (ADK)**: ADK 스트리밍 이벤트에 대한 적절한 오류 처리를 추가합니다. 자세한 내용은 [오류 이벤트](events.md#handling-errors)를 참고하세요.
    - 종료 시 `asyncio.CancelledError`를 포착하여 태스크 취소를 정상적으로 처리합니다.
    - `return_exceptions=True`를 사용한 `asyncio.gather()`의 예외를 확인합니다(예외가 자동으로 전파되지 않음).
- **오류 처리 (Web)**: 업스트림/다운스트림 태스크에서 웹 애플리케이션 관련 오류를 처리합니다. 예를 들어 FastAPI에서는 다음이 필요합니다:
    - `WebSocketDisconnect`(클라이언트 연결 해제), `ConnectionClosedError`(연결 끊김), `RuntimeError`(닫힌 연결로 전송)를 처리합니다.
    - 전송 전에 `websocket.client_state`로 WebSocket 연결 상태를 확인하여 연결이 닫혔을 때 발생하는 오류를 방지합니다.
- **인증 및 인가**: 엔드포인트에 인증 및 권한 부여를 구현합니다.
- **속도 제한 및 할당량**: 속도 제한 및 타임아웃 제어를 추가합니다. 동시 세션 및 할당량 관리에 대한 지침은 [동시 세션](sessions.md#concurrent-sessions)을 참고하세요.
- **구조화된 로깅**: 디버깅을 위해 구조화된 로깅을 사용합니다.
- **영구 세션 서비스**: 영구 세션 서비스(`DatabaseSessionService` 또는 `VertexAiSessionService`) 사용을 고려하세요. 자세한 내용은 [ADK 세션 서비스 문서](../sessions/index.md)를 참고하세요.

## 클라이언트 연결

서버가 WebSocket을 노출하므로 클라이언트가 이에 연결해야 합니다. 개발 단계에서는 `adk web`이 이 역할을 담당합니다. 프로덕션에서는 브라우저 앱, 모바일 앱, 또는 전화/WebRTC 브릿지와 같이 개발자가 직접 작성한 클라이언트가 됩니다. 어떤 것을 구축하든 동일한 규약을 상속하므로 `adk web`이 수행하는 작업과 제한 범위를 정확히 이해하는 것이 중요합니다.

**`adk web`이 자동으로 처리하는 작업:**

| 기능 | 내장 클라이언트가 수행하는 작업 |
|---|---|
| 마이크 | 16 kHz 모노 PCM으로 캡처 및 리샘플링하여 `audio/pcm;rate=16000`으로 스트리밍 |
| 재생 | 모델 오디오를 24 kHz 모노 PCM으로 끊김 없이 재생 |
| 카메라 | 약 1 fps의 JPEG 프레임을 `image/jpeg`로 전송 |
| 전사 | 부분 조각(partial fragments)을 병합하여 사용자와 모델 전사를 모두 렌더링 |
| 끼어들기 (Barge-in) | `interrupted`가 설정된 이벤트가 도착하면 재생을 즉시 중지 |

**처리하지 않는 작업** (프로덕션 클라이언트에서 구현이 필요할 수 있음):

- 화면 공유 미지원, 활성 오디오 통화 없는 비디오 미지원.
- 모달리티 선택 불가 (응답은 항상 `AUDIO`).
- 능동적 대화, 감정적 대화, 세션 재개, `save_live_blob`, 명시적 VAD 신호를 위한 UI 미제공 (서버의 [`RunConfig`](configuration.md)를 통해 설정됨).
- 수동 [VAD](configuration.md#voice-activity-detection-vad) 미지원 (기본적으로 켜져 있는 서버 측 자동 감지에 의존).

`adk web`과 `adk api_server`는 모두 동일한 `/run_live` WebSocket을 제공합니다. `adk api_server`는 `--with_ui`를 전달하지 않는 한 브라우저 클라이언트를 제공하지 않습니다. 따라서 `adk web`을 기반으로 개발하고 커스텀 클라이언트를 둘 중 하나에 연결할 수 있습니다.

### 와이어 프로토콜 및 데이터 포맷

`/run_live` 엔드포인트는 **JSON 텍스트 프레임만** 처리합니다. 클라이언트는 직렬화된 [`LiveRequest`](sessions.md#liverequestqueue) 객체를 전송하고 직렬화된 [`Event`](events.md) 객체를 수신합니다. 바이너리 데이터(오디오 및 이미지 바이트)는 바이너리 WebSocket 프레임이 아니라 JSON *내부*에서 base64로 인코딩되어 전송됩니다.

클라이언트에서는 camelCase 필드명을 사용하여 Python과 동일한 이벤트 필드에 따라 분기 처리합니다:

```javascript
websocket.onmessage = (message) => {
    const adkEvent = JSON.parse(message.data);
    if (adkEvent.interrupted) {
        stopAudioPlayback();   // 사용자가 끼어듦; 큐에 대기 중인 오디오 버리기
        finishCurrentBubble();
        return;
    }
    if (adkEvent.turnComplete) {
        finishCurrentBubble();
        return;
    }
    for (const part of adkEvent.content?.parts ?? []) {
        if (part.text) appendText(part.text);
        if (part.inlineData) enqueueAudio(part.inlineData.data);
    }
};
```

클라이언트가 생성하고 소비해야 하는 미디어 형식(샘플 레이트, 인코딩, 청크 크기)은 [오디오 및 비디오](audio-video.md)에 설명되어 있습니다. 분기 처리에 사용되는 스트리밍 플래그(`partial`, `turnComplete`, `interrupted`)와 전사 조각 분할 방식은 [이벤트](events.md)를 참고하세요.

## 이벤트 직렬화

ADK와 Live API 사이의 `/run_live` 엔드포인트는 JSON 텍스트 전용이지만, *자체 서버*와 *자체 클라이언트* 사이의 전송 계층은 자유롭게 설계할 수 있으며 base64 오버헤드를 피하기 위해 오디오를 바이너리 프레임으로 전송할 수 있습니다.

`Event`는 Pydantic 모델이므로 `model_dump_json()`을 통해 WebSocket이나 SSE 전송을 위한 JSON 문자열로 변환할 수 있습니다. 클라이언트의 camelCase 필드명에는 `by_alias=True`를, 빈 필드를 제외하려면 `exclude_none=True`를 사용합니다:

```python
async for event in runner.run_live(...):
    await websocket.send_text(event.model_dump_json(exclude_none=True, by_alias=True))
```

`inline_data`의 바이너리 오디오는 JSON에서 base64로 인코딩되어 페이로드 크기가 약 33% 증가합니다. 오디오 트래픽이 많은 스트림의 경우 오디오를 바이너리 프레임으로 보내고 메타데이터는 JSON으로 전송하세요:

```python
async for event in runner.run_live(...):
    parts = event.content.parts if event.content else []
    audio_parts = [p for p in parts if p.inline_data]
    if audio_parts:
        for part in audio_parts:
            await websocket.send_bytes(part.inline_data.data)
        # 오디오 바이트가 없는 메타데이터
        await websocket.send_text(event.model_dump_json(
            exclude={"content": {"parts": {"__all__": {"inline_data"}}}},
            by_alias=True,
        ))
    else:
        await websocket.send_text(event.model_dump_json(exclude_none=True, by_alias=True))
```
