# 라이브 에이전트를 위한 이벤트

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span>
</div>

라이브 에이전트가 생성하는 모든 결과는 `Event`로 애플리케이션에 전달됩니다. 모델이 작성하는 부분 텍스트, 원시 오디오 바이트, 대화 양측의 음성 전사(transcription), 도구 호출, 토큰 수 및 오류가 여기에 포함됩니다. 단 한 번의 발화 응답도 수십 개의 이벤트로 나뉘어 도착할 수 있으며, 이를 올바르게 처리하는 것이 지연 없이 즉각적인 음성 인터페이스를 구현하는 핵심입니다.

`Event`는 [이벤트](../events/index.md)에 설명된 ADK 공통 클래스와 동일합니다. 라이브 세션에서는 요청/응답 에이전트가 사용하지 않는 필드(오디오 Blob, 전사, 인터럽트 플래그 등)를 채워 넣고 단발성이 아닌 지속적인 스트림으로 전달합니다. 이를 생성하는 루프에 대해서는 [세션](sessions.md)을 참고하세요.

## 라이브 에이전트 이벤트 데이터

[`Event`](../api-reference/python/google-adk.html#google.adk.events.Event)는 `LlmResponse`를 확장한 Pydantic 모델입니다. 라이브 세션에서는 다음 필드를 사용합니다:

| 필드 | 내용 |
|---|---|
| `content.parts[].text` | 텍스트 파트 — 라이브 세션에서는 생각 요약(thought summary) 및 기타 발화되지 않는 내용 |
| `content.parts[].inline_data` | 재생을 위한 원시 오디오 바이트 (임시 데이터) |
| `content.parts[].file_data` | 아티팩트에 저장된 오디오에 대한 참조 (`save_live_blob=True`인 경우) |
| `content.parts[].function_call` / `function_response` | 도구 호출 및 결과 (ADK가 자동으로 실행) |
| `input_transcription` / `output_transcription` | 텍스트 형태의 사용자와 모델 발화 내용 |
| `partial` | 증분 청크인 경우 `True`, 병합된 결과인 경우 `False` |
| `turn_complete` | 모델이 전체 응답 생성을 마쳤을 때 `True` |
| `interrupted` | 응답 도중 사용자가 말을 끊었을(barge-in) 때 `True` |
| `usage_metadata` | 비용 및 쿼터 추적을 위한 토큰 수 |
| `error_code` / `error_message` | 실패 진단 정보 |
| `author` | 이벤트를 생성한 주체 (아래 설명 참조) |

### 작성자(Authorship)

라이브 세션에서 `event.author`는 전사된 사용자 음성의 경우 `"user"`이고, 모델 자체의 출력에 대해서는 리터럴 `"model"`이 아니라 **에이전트 이름**이 됩니다. 응답에 `input_transcription`이 포함되어 있거나 `content.role == 'user'`인 경우 ADK는 항상 `author="user"`를 설정합니다. 사용자 전사 응답에 항상 `role == 'user'`가 포함되는 것은 아니므로, 전사 유무를 확인하는 것이 신뢰할 수 있는 출처 구분을 가능하게 합니다([`base_llm_flow.py`](https://github.com/google/adk-python/blob/main/src/google/adk/flows/llm_flows/base_llm_flow.py)).

에이전트 이름을 사용하면 멀티 에이전트 세션에서 작성자별로 이벤트를 필터링할 수 있습니다:

```python
events = [e for e in stream if e.author == "billing_agent"]
```

## 이벤트 유형

라이브 세션 동안 에이전트는 부분 텍스트, 오디오, 음성 전사, 도구 호출, 토큰 사용량 메타데이터 등 여러 고유한 이벤트 유형을 통해 지속적인 출력을 전달합니다. 다음 섹션에서는 이러한 이벤트 유형을 설명합니다.

### 텍스트

텍스트는 `event.content.parts[].text`로 도착합니다. 라이브 세션에서 이는 생각 요약 및 기타 음성으로 발화되지 않는 내용입니다. ADK가 지원하는 모든 [라이브 모델](models.md#live-models)은 오디오를 입력받아 오디오를 출력하므로, **모델의 발화 응답은 텍스트 파트가 아니라 [출력 전사(output transcription)](configuration.md#audio-transcription)로 반환됩니다**.

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.text and not event.partial:
                update_display(part.text)
```

!!! warning "`parts`를 순회하세요. 절대 `parts[0]`만 가정하지 마세요"

    단일 이벤트에 여러 파트가 포함될 수 있으며, 라이브 모델은 이를 일상적으로 수행합니다. `event.content.parts[0].text`는 나머지 파트를 조용히 누락시키고 첫 번째 파트가 텍스트가 아닌 경우(생각 요약, 함수 호출, 오디오 Blob 등) 오류를 일으킵니다. 파트 목록을 반복 순회하고 설정된 필드에 따라 분기 처리하세요.

### 오디오

`response_modalities=["AUDIO"]`(라이브 기본값)인 경우 모델은 오디오를 `inline_data`로 반환합니다:

```python
async for event in runner.run_live(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if part.inline_data:  # 원시 PCM 바이트
                await play_audio(part.inline_data.data)
```

`inline_data`는 일시적이며 영구 저장되지 않습니다. [`save_live_blob=True`](configuration.md#save_live_blob)를 설정하면 ADK가 오디오를 아티팩트 서비스의 파일로 집계하고, 나중에 오디오를 검색할 수 있도록 원시 바이트 대신 `file_data` 참조를 제공합니다. 형식과 재생 방법은 [오디오 및 비디오](audio-video.md)를 참고하세요.

### 음성 전사(Transcription)

전사가 활성화된 경우(기본적으로 켜짐), 사용자와 모델의 음성이 `event.input_transcription` 및 `event.output_transcription`으로 도착합니다. 이는 조각(fragment) 단위로 스트리밍됩니다. `.text`는 최신 조각을 담고 있고 `.finished`는 해당 턴의 마지막 조각임을 나타내며, 이는 `event.partial`과 일치합니다. 전체 전사를 구성하려면 조각들을 이어 붙이세요. 자세한 내용은 [오디오 전사](configuration.md#audio-transcription)를 참고하세요.

```python
async for event in runner.run_live(...):
    if event.input_transcription and event.input_transcription.text:
        show_caption(event.input_transcription.text, is_user=True)
    if event.output_transcription and event.output_transcription.text:
        show_caption(event.output_transcription.text, is_user=False)
```

### 도구 호출

모델은 `part.function_call`을 통해 도구를 요청합니다. ADK는 등록된 도구를 자동으로 실행하므로 개발자가 이를 직접 처리하는 경우는 드뭅니다. [자동 도구 실행](tools.md#automatic-tool-execution)을 참고하세요.

### 메타데이터

`event.usage_metadata`는 실시간 비용 및 쿼터 추적을 위한 토큰 수(`prompt_token_count`, `candidates_token_count`, `total_token_count`, `cached_content_token_count`)를 포함합니다.

## 스트리밍 플래그

라이브 UI는 `partial`, `turn_complete`, `interrupted` 세 가지 플래그를 통해 제어됩니다.
`partial` 플래그는 증분 청크와 병합된 결과를 구분합니다:

- `partial=True`: 이전 이벤트 이후의 새로운 텍스트만 포함.
- `partial=False`: 이 세그먼트의 전체 병합된 텍스트 포함.

ADK가 청크를 자동으로 누적해주므로(`StreamingResponseAggregator`), `partial=False` 이벤트는 이미 이전 `partial=True` 청크들의 합계를 담고 있습니다. 실시간 타이핑 효과가 필요하지 않다면 partial 이벤트를 무시하고 `partial=False`에서만 동작하도록 처리하세요.

```text
Event 1: partial=True,  text="Hello",       turn_complete=False
Event 2: partial=True,  text=" world",      turn_complete=False
Event 3: partial=False, text="Hello world", turn_complete=False
Event 4: partial=False, text="",            turn_complete=True
```

`partial=False` 상태는 턴당 여러 번(예: 문장마다 한 번씩) 발생할 수 있으며, `turn_complete=True`는 마지막 세그먼트 이후 자체 이벤트로 한 번만 전달됩니다.

`turn_complete`와 `interrupted`는 UI가 진입해야 하는 상태를 알려줍니다:

| turn_complete | interrupted | 애플리케이션의 동작 |
|---|---|---|
| True | False | 입력 활성화, "준비 완료" 상태 표시 |
| False | True | 오디오 재생 중지, 부분 텍스트 지우기 |
| True | True | 턴 종료. 일반 완료와 동일하게 처리 |
| False | False | 스트리밍 텍스트 계속 표시 |

```python
async for event in runner.run_live(...):
    if event.interrupted:
        stop_audio_playback()   # 사용자가 끼어듦; 큐에 쌓인 오디오 버리기
        clear_streaming_text()
    if event.turn_complete:
        enable_microphone()     # 다음 턴 준비
```

`interrupted`를 처리하지 않으면 이미 버퍼링된 오디오가 사용자의 말 위로 계속 재생됩니다.

## 오류 처리

오류는 `event.error_code`와 `event.error_message`로 전달됩니다. 결정해야 할 핵심은 모델의 응답이 계속 진행될 수 있는지 여부입니다. 모델이 중단된 경우 `break`하고, 일시적인 장애인 경우 `continue`합니다.

```python
try:
    async for event in runner.run_live(...):
        if event.error_code:
            logger.error("Model error: %s - %s", event.error_code, event.error_message)
            if event.error_code in ("SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "MAX_TOKENS"):
                break       # 모델이 종료됨. 이번 턴에 더 이상 이벤트가 없음.
            continue        # 일시적 오류; 스트림이 복구될 수 있음.
        # ... 콘텐츠 처리 ...
finally:
    live_request_queue.close()  # break하거나 완료되더라도 항상 실행됨.
```

| 오류 코드 | 카테고리 | 조치 |
|---|---|---|
| `SAFETY`, `PROHIBITED_CONTENT`, `BLOCKLIST` | 콘텐츠 정책 | `break` — 모델이 응답을 종료함 |
| `MAX_TOKENS` | 한도 도달 | `break` — 모델이 생성을 마침 |
| `UNAVAILABLE`, `DEADLINE_EXCEEDED` | 일시적 장애 | `continue` — 네트워크 또는 타임아웃, 자동 해결될 수 있음 |
| `RESOURCE_EXHAUSTED` | 속도 제한(Rate limit) | 지수 백오프와 함께 `continue` |
| `CANCELLED` | 클라이언트 취소 | `break` — 정리 작업 수행 |
| `UNKNOWN` | 시스템 오류 | 로깅 후 `continue` |

1초 미만의 일시적인 오류는 사용자에게 알리지 마세요. `RESOURCE_EXHAUSTED`의 경우 무한 루프를 방지하기 위해 재시도 횟수를 제한하고 백오프를 적용하세요. 오류 코드는 Gemini API에서 비롯됩니다. [FinishReason](https://ai.google.dev/api/python/google/ai/generativelanguage/Candidate/FinishReason) 및 [Agent Platform 레퍼런스](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/inference)를 참고하세요.

## 클라이언트로 이벤트 전송하기

브라우저나 모바일 클라이언트로 이벤트를 스트리밍하려면 직렬화하여 전송 채널을 통해 전달합니다. `Event`는 Pydantic 모델이므로 `model_dump_json()`으로 직렬화할 수 있습니다. base64 인코딩된 오디오는 JSON 크기를 약 33% 증가시키므로 오디오는 바이너리 프레임으로 전송하는 것이 효율적입니다. 직렬화 패턴과 그에 대응하는 클라이언트 측 처리는 [커스텀 서버](custom-server.md#serializing-events)에서 확인할 수 있습니다.
