# REST API 레퍼런스

이 페이지는 ADK 웹 서버가 제공하는 REST API에 대한 레퍼런스를 제공합니다.
ADK REST API의 실제 사용법에 대한 자세한 내용은
[API 서버 사용하기](/adk-docs/ko/runtime/api-server/)를 참조하세요.

!!! tip
    실행 중인 ADK 웹 서버의 `/docs` 경로(예: `http://localhost:8000/docs`)로 접속하면 업데이트된 API 레퍼런스를 확인할 수 있습니다.

## 엔드포인트

### `/run`

이 엔드포인트는 에이전트 실행을 수행합니다. 실행에 대한 상세 정보가 담긴 JSON 페이로드를 입력받아, 실행 중에 생성된 이벤트 목록을 반환합니다.

**요청 본문 (Request Body)**

요청 본문은 다음 필드를 포함하는 JSON 객체여야 합니다.

- `app_name` (string, 필수): 실행할 에이전트의 이름입니다.
- `user_id` (string, 필수): 사용자의 ID입니다.
- `session_id` (string, 필수): 세션의 ID입니다.
- `new_message` (Content, 필수): 에이전트에게 보낼 새 메시지입니다. 자세한 내용은 [Content 객체](#content-object) 섹션을 참조하세요.
- `streaming` (boolean, 선택): 스트리밍 사용 여부입니다. 기본값은 `false`입니다.
- `state_delta` (object, 선택): 실행 전에 적용할 상태(state)의 변경분(delta)입니다.

**응답 본문 (Response Body)**

응답 본문은 [Event 객체](#event-object)의 JSON 배열입니다.

### `/run_sse`

이 엔드포인트는 스트리밍 응답을 위해 서버-전송 이벤트(Server-Sent Events, SSE)를 사용하여 에이전트 실행을 수행합니다. `/run` 엔드포인트와 동일한 JSON 페이로드를 입력받습니다.

**요청 본문 (Request Body)**

요청 본문은 `/run` 엔드포인트와 동일합니다.

**응답 본문 (Response Body)**

응답은 서버-전송 이벤트의 스트림입니다. 각 이벤트는 [Event 객체](#event-object)를 나타내는 JSON 객체입니다.

## 객체

### `Content` 객체

`Content` 객체는 메시지의 내용을 나타냅니다. 다음과 같은 구조를 가집니다.

```json
{
  "parts": [
    {
      "text": "..."
    }
  ],
  "role": "..."
}
```

- `parts`: 부분(part)의 목록입니다. 각 부분은 텍스트 또는 함수 호출이 될 수 있습니다.
- `role`: 메시지 작성자의 역할입니다 (예: "user", "model").

### `Event` 객체

`Event` 객체는 에이전트 실행 중에 발생한 이벤트를 나타냅니다. 다양한 선택적 필드를 가진 복잡한 구조를 가집니다. 가장 중요한 필드는 다음과 같습니다.

- `id`: 이벤트의 ID입니다.
- `timestamp`: 이벤트의 타임스탬프입니다.
- `author`: 이벤트의 작성자입니다.
- `content`: 이벤트의 내용입니다.