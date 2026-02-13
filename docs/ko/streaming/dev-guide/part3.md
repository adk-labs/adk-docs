# Part 3: run_live()로 이벤트 처리하기

`run_live()`는 ADK 스트리밍 대화의 핵심 진입점입니다.
대화가 진행되는 동안 이벤트를 실시간으로 `yield`하는 async generator를 제공합니다.
이번 파트에서는 텍스트/오디오/전사/도구 호출/에러 등 이벤트를 처리하고,
중단(interruption) 및 turn completion 신호를 이용해 대화 흐름을 제어하는 방법을 다룹니다.

!!! note "Async Context Required"

    `run_live()` 코드는 반드시 async 컨텍스트에서 실행해야 합니다.
    자세한 예시는 [Part 1: FastAPI Application Example](part1.md#fastapi-application-example)를 참고하세요.

## run_live() 동작 방식

`run_live()`는 내부 버퍼링 없이 이벤트를 즉시 전달하는 async generator입니다.
메모리 사용량은 세션 영속화 방식(in-memory/DB)에 따라 달라집니다.

### 메서드 시그니처

```python title='Source reference: <a href="https://github.com/google/adk-python/blob/29c1115959b0084ac1169748863b35323da3cf50/src/google/adk/runners.py" target="_blank">runners.py</a>'
async def run_live(
    self,
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    live_request_queue: LiveRequestQueue,
    run_config: Optional[RunConfig] = None,
    session: Optional[Session] = None,
) -> AsyncGenerator[Event, None]:
```

사용 시에는 `user_id`, `session_id`, `live_request_queue`, `run_config`를 맞춰 전달합니다.

```python title='Demo implementation: <a href="https://github.com/google/adk-samples/blob/31847c0723fbf16ddf6eed411eb070d1c76afd1a/python/agents/bidi-demo/app/main.py#L225-L233" target="_blank">main.py:225-233</a>'
async for event in runner.run_live(
    user_id=user_id,
    session_id=session_id,
    live_request_queue=live_request_queue,
    run_config=run_config
):
    event_json = event.model_dump_json(exclude_none=True, by_alias=True)
    logger.debug(f"[SERVER] Event: {event_json}")
    await websocket.send_text(event_json)
```

### run_live() 연결 라이프사이클

1. 초기화: `run_live()` 호출 시 연결 생성
2. 활성 스트리밍: 업스트림(`LiveRequestQueue`) + 다운스트림(`run_live()`) 동시 처리
3. 정상 종료: `LiveRequestQueue.close()` 호출 시 연결 종료
4. 복구: `RunConfig.session_resumption`으로 일시 장애 복구

### run_live()가 내보내는 이벤트

| Event Type | Description |
|------------|-------------|
| **Text Events** | `response_modalities=["TEXT"]`일 때 텍스트 응답 |
| **Audio Events with Inline Data** | `response_modalities=["AUDIO"]`일 때 실시간 오디오 바이트 |
| **Audio Events with File Data** | 아티팩트 파일 참조(`file_data`) 기반 오디오 |
| **Metadata Events** | 토큰 사용량/비용 추적 메타데이터 |
| **Transcription Events** | 입력/출력 오디오 전사 |
| **Tool Call Events** | 모델의 function call 요청 및 처리 |
| **Error Events** | 모델/연결 오류 정보 |

### run_live() 종료 조건

| Exit Condition | Trigger | Graceful? | Description |
|---|---|---|---|
| **Manual close** | `live_request_queue.close()` | ✅ | 사용자 명시 종료 |
| **All agents complete** | SequentialAgent 마지막 `task_completed()` | ✅ | 순차 워크플로 완료 |
| **Session timeout** | Live API 시간 제한 도달 | ⚠️ | 연결 종료 |
| **Early exit** | `end_invocation=True` | ✅ | 전처리/툴/콜백에서 조기 종료 |
| **Empty event** | 내부 종료 신호 | ✅ | 스트림 종료 |
| **Errors** | 예외/연결 오류 | ❌ | 비정상 종료 |

!!! warning "SequentialAgent Behavior"

    `SequentialAgent`에서 `task_completed()`는 앱의 `run_live()` 루프를 즉시 끝내지 않습니다.
    다음 에이전트로 전환되며, 마지막 에이전트 완료 시 루프가 종료됩니다.

### ADK Session에 저장되는 이벤트

**저장됨:**

- `save_live_blob=True`일 때 file_data 오디오 이벤트
- usage metadata 이벤트
- non-partial 전사 이벤트
- function call/response 이벤트
- 기타 control 이벤트

**저장되지 않음(실시간 전용):**

- inline_data 오디오 이벤트
- partial 전사 이벤트

## 이벤트 이해하기

### Event 클래스 핵심 필드

- `content`: 텍스트/오디오/함수 호출
- `author`: 이벤트 작성자(`user` 또는 agent 이름)
- `partial`: 부분 청크 여부
- `turn_complete`: 턴 완료 여부
- `interrupted`: 사용자 중단 여부
- `input_transcription` / `output_transcription`
- `usage_metadata`
- `error_code` / `error_message`

### event.id vs invocation_id

- `event.id`: 이벤트 고유 ID
- `event.invocation_id`: 동일 invocation 내 공통 ID

```python
async for event in runner.run_live(...):
    print(f"Event ID: {event.id}")
    print(f"Invocation ID: {event.invocation_id}")
```

### Event author 규칙

- 모델 응답은 보통 agent 이름(`"my_agent"`)을 작성자로 사용
- 사용자 오디오 전사 이벤트는 `author="user"`

## 이벤트 타입별 처리

### Text Events

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        if event.content.parts[0].text:
            text = event.content.parts[0].text
            if not event.partial:
                update_streaming_display(text)
```

**모달리티 기본값:**
`response_modalities` 미지정 시 `run_live()` 시작 시 `["AUDIO"]`가 기본입니다.
텍스트 전용 앱은 `response_modalities=["TEXT"]`를 명시하세요.

### Audio Events

```python
run_config = RunConfig(
    response_modalities=["AUDIO"],
    streaming_mode=StreamingMode.BIDI
)

async for event in runner.run_live(..., run_config=run_config):
    if event.content and event.content.parts:
        part = event.content.parts[0]
        if part.inline_data:
            audio_data = part.inline_data.data
            await play_audio(audio_data)
```

### Audio Events with File Data

오디오가 아티팩트로 저장될 때 `inline_data` 대신 `file_data` 참조를 받습니다.

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.file_data:
                file_uri = part.file_data.file_uri
                mime_type = part.file_data.mime_type
                print(f"Audio file saved: {file_uri} ({mime_type})")
```

### Metadata Events

```python
if event.usage_metadata:
    print(event.usage_metadata.prompt_token_count)
    print(event.usage_metadata.candidates_token_count)
    print(event.usage_metadata.total_token_count)
```

### Transcription Events

```python
if event.input_transcription:
    display_user_transcription(event.input_transcription)

if event.output_transcription:
    display_model_transcription(event.output_transcription)
```

### Tool Call Events

```python
if event.content and event.content.parts:
    for part in event.content.parts:
        if part.function_call:
            tool_name = part.function_call.name
            tool_args = part.function_call.args
```

### Error Events

```python
try:
    async for event in runner.run_live(...):
        if event.error_code:
            logger.error(f"Model error: {event.error_code} - {event.error_message}")
            if event.error_code in ["SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "MAX_TOKENS"]:
                break
            continue
finally:
    queue.close()
```

**`break` vs `continue` 기준:**

- `SAFETY`, `PROHIBITED_CONTENT`, `BLOCKLIST`, `MAX_TOKENS` → 보통 `break`
- `UNAVAILABLE`, `DEADLINE_EXCEEDED`, `RESOURCE_EXHAUSTED` → 재시도 가능한 경우 `continue`
- 항상 `finally`에서 `queue.close()`로 정리

## 텍스트 이벤트 플래그 처리

### `partial`

- `partial=True`: 증분 텍스트
- `partial=False`: 병합 완료 텍스트

### `interrupted`

사용자 중단 시 `interrupted=True` 이벤트가 오며,
현재 출력 렌더링/오디오 재생을 즉시 중단해야 합니다.

### `turn_complete`

모델이 턴 응답을 완료했음을 의미합니다.
입력 UI 재활성화, 타이핑 인디케이터 제거 등에 사용합니다.

## 이벤트 JSON 직렬화

`Event`는 Pydantic 모델이므로 `model_dump_json()`으로 직렬화합니다.

```python
event_json = event.model_dump_json(exclude_none=True, by_alias=True)
```

오디오 `inline_data`는 JSON에서 base64 인코딩되어 payload가 커집니다.
오디오 중심 앱은 바이너리 프레임과 메타데이터 텍스트를 분리 전송하는 패턴이 효율적입니다.

## run_live()의 자동 도구 실행

ADK는 Live API 원시 사용 시 필요한 도구 실행 오케스트레이션을 자동화합니다.

```python
import os
from google.adk.agents import Agent
from google.adk.tools import google_search

agent = Agent(
    name="google_search_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-12-2025"),
    tools=[google_search],
    instruction="You are a helpful assistant that can search the web."
)
```

`runner.run_live()` 호출 시 ADK는 함수 호출 감지, 병렬 실행, 콜백 처리,
응답 포맷팅, 모델 재전송까지 자동 처리합니다.

### 도구 이벤트 관찰

```python
async for event in runner.run_live(...):
    if event.get_function_calls():
        print(event.get_function_calls()[0].name)
    if event.get_function_responses():
        print(event.get_function_responses()[0].response)
```

### 장기 실행/스트리밍 툴

- long-running tool: `is_long_running=True`
- streaming tool: `LiveRequestQueue` 타입 `input_stream` 파라미터를 통해 실시간 업데이트 전송

## InvocationContext

`run_live()` 내부에서는 단일 invocation 동안 유지되는 `InvocationContext`가 생성됩니다.
(한 번의 `run_live()` 호출 = 하나의 InvocationContext)

### tool/callback에서 자주 쓰는 필드

- `context.invocation_id`
- `context.session.events`
- `context.session.state`
- `context.session.user_id`
- `context.run_config`
- `context.end_invocation`

```python
def my_tool(context: InvocationContext, query: str):
    user_id = context.session.user_id
    recent_events = context.session.events[-5:]
    prefs = context.session.state.get('user_preferences', {})
    # ...
```

## 멀티 에이전트 워크플로 모범 사례

ADK Bidi-streaming은 다음 패턴을 지원합니다.

- 단일 에이전트
- coordinator + sub-agent (`transfer_to_agent`)
- 순차 파이프라인(`SequentialAgent` + `task_completed`)

### SequentialAgent + BIDI

`task_completed()` 호출은 현재 에이전트 완료를 의미하며,
ADK가 다음 에이전트로 자동 전환합니다.
앱 코드는 같은 `run_live()` 루프에서 이벤트를 계속 소비하면 됩니다.

**권장 원칙:**

1. 단일 이벤트 루프 사용
2. 단일 `LiveRequestQueue` 유지
3. `event.author`로 현재 에이전트 파악
4. 에이전트 전환을 앱에서 수동 관리하지 않음

## 요약

이번 파트에서는 ADK Bidi-streaming의 이벤트 처리 전반을 학습했습니다.
텍스트/오디오/전사/도구 호출/에러 이벤트 처리,
`partial`/`interrupted`/`turn_complete` 기반 UI 상태 제어,
JSON 직렬화와 네트워크 전송,
ADK 자동 도구 실행,
InvocationContext 기반 상태 관리,
멀티 에이전트 워크플로 처리까지 다뤘습니다.

다음 파트에서는 RunConfig를 활용해 모달리티, 세션 재개, 비용 제어 등
고급 스트리밍 동작을 구성합니다.

---

← [Previous: Part 2: Sending Messages with LiveRequestQueue](part2.md) | [Next: Part 4: Understanding RunConfig](part4.md) →
