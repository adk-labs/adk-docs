# 앰비언트 에이전트로 작업 트리거하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.29.0</span><span class="lst-go">Go v1.1.0</span>
</div>

에이전트 워크플로를 실행할 때, 사람이 입력하기를 기다리는 대신 이벤트가 발생하거나
새 데이터가 제공되는 시점에 워크플로를 활성화하고 싶을 수 있습니다. ADK 에이전트는
트리거를 구성해 이벤트에 응답하고 작업을 수행할 수 있으며, 이를 *앰비언트 에이전트*라고
합니다. 이러한 에이전트는 백그라운드 프로세스로 실행되어 데이터를 처리하고, 이벤트를
모니터링하며, 사람의 개입 없이 비동기적으로 응답할 수 있습니다. 앰비언트 에이전트는
다음 작업에 사용할 수 있습니다.

- **클라우드 이벤트에 반응합니다.** 파일이 업로드되면 처리합니다.
  [Cloud Storage](https://cloud.google.com/storage), 데이터베이스에 응답
  감사 로그 항목을 변경하거나 처리합니다.
- **큐의 메시지를 처리합니다.** 들어오는 지원 티켓을 분석하고,
  콘텐츠를 검토하고, 문서를 분류하고, 항목이 도착하면 QA를 실행하세요.
- **일정에 따라 실행됩니다.** 일일 보고서 생성, 주기적인 모니터링 실행
  정기적으로 일괄 작업을 확인하거나 처리합니다.
- **인프라를 모니터링합니다.** 전체에서 지속적인 이벤트 스트림에 반응합니다.
  인프라를 구축하고 변경 사항에 자율적으로 조치를 취하세요.

## 주변 에이전트로부터 결과 얻기

주변 에이전트는 사람의 상호 작용 없이 실행되므로 라우팅해야 합니다.
알림 채널로 출력됩니다. 일반적인 패턴은 다음과 같습니다.

- **[Structured logging](../observability/logging.md).** JSON 로그를 작성하고
  [Cloud Monitoring](https://cloud.google.com/monitoring/support/notification-options) 구성
  이메일, Slack 또는 PagerDuty를 통해 알리는 경고입니다.
- **[Pub/Sub](https://cloud.google.com/pubsub).** 주제에 결과 게시
  다운스트림 서비스가 소비되도록 합니다.
- **[Application Integration](https://cloud.google.com/application-integration/docs/listen-pub-sub-topic-send-email).**
  에이전트 출력을 이메일, Jira 또는 기타 시스템으로 라우팅합니다.

## 주변 에이전트를 구축하는 방법

ADK는 두 가지 접근 방식을 제공합니다.

| | [`/run`](api-server.md) | 트리거 엔드포인트 |
| :--- | :--- | :--- |
| **이벤트 소스** | 모두(Pub/Sub, 웹훅, 크론, 커스텀 서비스) | [Cloud Pub/Sub](https://cloud.google.com/pubsub), [Eventarc](https://cloud.google.com/eventarc)([Standard](https://cloud.google.com/eventarc/standard/docs/overview) 및 [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview)) |
| **페이로드 구문 분석** | 당신이 처리 | 자동(Base64 디코딩, CloudEvent 구문 분석) |
| **세션 생성** | `--auto_create_session` 활성화 | 자동(이벤트당 하나) |
| **세션 저장** | 구성된 [`SessionService`](../sessions/session/index.md) | 구성된 [`SessionService`](../sessions/session/index.md) |
| **동시성 제어** | 당신이 처리 | 제한을 구성할 수 있는 내장형 세마포어 |
| **재시도 로직** | 당신이 처리 | 일시적인 오류에 대한 지터가 있는 지수 백오프 |
| **최고의 대상** | 맞춤 통합, GCP가 아닌 소스 | GCP 기반 이벤트 기반 워크로드 |

## `/run` 사용하기

완전한 제어가 필요할 때 [`/run`](api-server.md) 엔드포인트를 사용하세요.
통합을 진행 중이거나 GCP가 아닌 이벤트 소스로 작업 중입니다. 활성화
`--auto_create_session`를 사용하여 세션이 자동으로 생성되도록 한 다음
이벤트가 도착하면 HTTP 클라이언트를 연결하여 `/run`를 호출합니다.

```bash
adk api_server --auto_create_session path/to/your/agent
```

이 패턴은 HTTP 요청을 할 수 있는 모든 이벤트 소스에서 작동합니다.

??? "예: 들어오는 웹훅 처리"

    다음 [Cloud Run function](https://cloud.google.com/functions/docs/writing/write-event-driven-functions)
    외부 서비스(예: GitHub)로부터 웹훅을 수신하고
    이를 에이전트에 전달합니다.

    ```python
    import json
    import uuid

    import functions_framework
    import requests

    AGENT_URL = "https://my-agent-service-xxxxx.run.app"

    @functions_framework.http
    def handle_webhook(request):
        """Cloud Run function that receives webhooks and forwards to the agent."""
        payload = request.get_json(silent=True) or {}

        requests.post(
            f"{AGENT_URL}/apps/my_agent/run",
            json={
                "app_name": "my_agent",
                "user_id": payload.get("account", "webhook-caller"),
                "session_id": str(uuid.uuid4()),
                "new_message": {
                    "role": "user",
                    "parts": [{"text": json.dumps(payload)}],
                },
            },
        )

        return ("ok", 200)
    ```

??? "예: 컬을 사용하여 이벤트 보내기"

    ```bash
    curl -X POST http://localhost:8000/apps/my_agent/run \
      -H "Content-Type: application/json" \
      -d '{
        "app_name": "my_agent",
        "user_id": "webhook-caller",
        "session_id": "session-123",
        "new_message": {
          "role": "user",
          "parts": [{"text": "{\"order_id\": \"1234\", \"status\": \"new\"}"}]
        }
      }'
    ```

## 트리거 엔드포인트 사용

이벤트 소스가 Pub/Sub 또는 Eventarc이고
ADK가 페이로드 구문 분석, 세션 생성, 동시성 및 재시도를 처리하기를 원합니다.

### 이벤트 처리 방법

Pub/Sub 및 Eventarc는 이벤트를 HTTP POST 요청으로 에이전트에 전달합니다.
트리거 엔드포인트가 이벤트를 수신하면 다음을 수행합니다.

1. 소스 형식(Pub/Sub 푸시 메시지)에 따라 **요청을 구문 분석**합니다.
   또는 CloudEvent).
2. **페이로드를 디코딩합니다.** Base64로 인코딩된 메시지 데이터가 디코딩되고,
   가능하며 JSON으로 구문 분석됩니다.
3. 생성된 UUID를 사용하여 자동으로 **세션을 생성**합니다. `/run`와 달리
   엔드포인트에서는 `--auto_create_session`를 활성화할 필요가 없습니다 — 트리거
   엔드포인트는 항상 이벤트마다 새 세션을 생성합니다.
4. 디코딩된 이벤트를 사용자 메시지로 사용하여 **에이전트를 실행**합니다.
5. **상태 코드를 반환합니다.** `200` 응답은 Pub/Sub 또는 Eventarc에 다음을 알려줍니다.
   이벤트가 성공적으로 처리되었습니다. `500` 응답은 실패를 나타냅니다.
   이벤트 소스는 재시도 정책에 따라 전달을 재시도합니다.

### 지원되는 소스

| 소스 | 엔드포인트 | 설명 |
| :----- | :------- | :---------- |
| **게시/구독** | `/apps/{app_name}/trigger/pubsub` | [Pub/Sub push subscription](https://cloud.google.com/pubsub/docs/push)로부터 메시지를 받습니다. |
| **이벤트 아크** | `/apps/{app_name}/trigger/eventarc` | [Eventarc](https://cloud.google.com/eventarc)([Standard](https://cloud.google.com/eventarc/standard/docs/overview) 또는 [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview))에서 전달한 [CloudEvents](https://cloudevents.io/)를 수신하며 구조화된 콘텐츠 모드와 바이너리 콘텐츠 모드를 모두 지원합니다. |

### 예시 에이전트

=== "Python"
    다음 에이전트는 트리거 엔드포인트의 이벤트를 처리합니다. 그것은
    이벤트 데이터와 속성을 추출한 후 분석하는 `parse_event` 도구
    내용.

    ???+ "에이전트 코드(`event_processing_agent/agent.py`)"

        ```python
        --8<-- "examples/python/snippets/runtime/triggers/event_processing_agent/agent.py:event_processor"
        ```

=== "Go"
    다음 에이전트는 트리거 엔드포인트의 이벤트를 처리합니다. 이벤트 데이터와 속성을 추출한 후 내용을 분석합니다.

    ???+ "에이전트 코드(`event_processing_agent.go`)"

        ```go
        --8<-- "examples/go/snippets/runtime/triggers/event_processing_agent.go:event_processor"
        ```

### 트리거 활성화

=== "Python"

    트리거 끝점은 기본적으로 비활성화되어 있습니다. 다음을 사용하여 활성화하세요.
    `--trigger_sources` 플래그:

    ```shell
    adk api_server --trigger_sources "pubsub,eventarc" path/to/your/agent
    ```

    프로덕션 배포의 경우 프로그래밍 방식으로 트리거를 활성화할 수 있습니다.
    사용자 정의 FastAPI 진입점:

    ???+ "배포 진입점(`main.py`)"

        === "Python"
            ```python
            --8<-- "examples/python/snippets/runtime/triggers/main.py:triggers"
            ```

=== "Go"

    트리거 끝점은 기본적으로 비활성화되어 있습니다. 다음을 사용하여 활성화하세요.
    해당 트리거 플래그:

    ```shell
    go run agent.go web api pubsub eventarc
    ```

### 로컬에서 사용해 보세요

**1. 트리거를 활성화하여 서버를 시작합니다.**

=== "Python"

    ```bash
    adk api_server --trigger_sources "pubsub" event_processing_agent
    ```

=== "Go"

    ```bash
    go run event_processing_agent.go web api pubsub
    ```

**2. 테스트 이벤트 보내기:**

```bash
curl -X POST http://localhost:8000/apps/event_processing_agent/trigger/pubsub \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "data": "eyJvcmRlcl9pZCI6ICIxMjM0IiwgInN0YXR1cyI6ICJuZXcifQ==",
      "attributes": {"source": "orders-service"}
    },
    "subscription": "projects/my-project/subscriptions/orders-sub"
  }'
```

Base64 값은 `{"order_id": "1234", "status": "new"}`로 디코딩됩니다.

성공적인 응답:

```json
{"status": "success"}
```

## 트리거 소스

### 매개변수 매핑

`/run` 엔드포인트를 사용하려면 `app_name`, `user_id` 및
`session_id`. 트리거 엔드포인트는 다음을 자동으로 파생합니다.

| 매개변수 | 소스 |
| :-------- | :----- |
| `app_name` | URL 경로(`/apps/{app_name}/trigger/...`)에서 추출됨 |
| `session_id` | 이벤트당 자동 생성된 UUID |
| `user_id` | 게시/구독: `subscription` 필드. Eventarc: `source` 또는 `ce-source` 헤더. |

### 메시지 형식

모든 트리거 엔드포인트는 수신 이벤트를 일관된 JSON으로 정규화합니다.
에이전트에 사용자 메시지로 전달하기 전에 다음 구조를 따르세요.

```json
{
  "data": "<decoded event payload>",
  "attributes": {"key": "value"}
}
```

- **`data`**: 디코딩된 이벤트 페이로드입니다. 원본 데이터가 JSON인 경우
  구조화된 객체로 파싱됩니다. 그렇지 않으면 일반 문자열로 전달됩니다.
- **`attributes`**: 이벤트 소스의 키-값 메타데이터(예: Pub/Sub)
  메시지 속성 또는 CloudEvents 헤더(예: `ce-type`, `ce-source`).

에이전트는 이 JSON 문자열을 입력 메시지로 수신하고 이를 구문 분석할 수 있습니다.
데이터와 속성을 추출합니다.

### 게시/구독

Pub/Sub 트리거 엔드포인트는 다음의 메시지를 처리합니다.
[Pub/Sub push subscription](https://cloud.google.com/pubsub/docs/push). 그것을 사용
애플리케이션이나 서비스가 주제에 메시지를 게시할 때, 예를 들면 다음과 같습니다.

- 지원 포털은 분류 및 라우팅을 위해 들어오는 티켓을 게시합니다.
- 콘텐츠 파이프라인은 분류 또는 조정을 위해 문서를 보냅니다.
- 모니터링 서비스는 자동화된 분석을 위한 경고를 게시합니다.

#### 요청 형식

Pub/Sub 푸시 구독은 다음 형식으로 요청을 보냅니다.

```json
{
  "message": {
    "data": "eyJvcmRlcl9pZCI6ICIxMjM0IiwgInN0YXR1cyI6ICJuZXcifQ==",
    "attributes": {"source": "orders-service"},
    "messageId": "123456789",
    "publishTime": "2026-04-08T12:00:00Z"
  },
  "subscription": "projects/my-project/subscriptions/my-sub"
}
```

`data` 필드는 Base64로 인코딩됩니다. 트리거 엔드포인트가 이를 디코딩합니다.
자동으로.

#### 응답

| HTTP 상태 | 의미 |
| :---------- | :------ |
| **200** | 이벤트가 성공적으로 처리되었습니다. Pub/Sub가 메시지를 확인합니다. |
| **400** | 잘못된 요청입니다(잘못된 Base64 인코딩). 메시지가 재시도되지 않습니다. |
| **500** | 처리에 실패했습니다(일시적 또는 비일시적 에이전트 오류). Pub/Sub는 [retry policy](https://cloud.google.com/pubsub/docs/handling-failures)를 기반으로 전송을 재시도합니다. 반복적으로 실패하는 메시지를 포착하도록 [dead-letter queue](https://cloud.google.com/pubsub/docs/dead-letter-topics)를 구성하십시오. |

### 이벤트아크

Eventarc 트리거 엔드포인트 프로세스
[CloudEvents](https://cloud.google.com/eventarc/docs/cloudevents) 제공자
[Eventarc](https://cloud.google.com/eventarc), 둘 다
[Standard](https://cloud.google.com/eventarc/standard/docs/overview) 및
[Advanced](https://cloud.google.com/eventarc/advanced/docs/overview) 에디션.
이를 사용하여 Google Cloud 전반의 이벤트에 대응합니다. 예를 들면 다음과 같습니다.

- 파일이 [Cloud Storage](https://cloud.google.com/storage)에 업로드됩니다(문서의 데이터 분류, 요약 또는 추출).
- [BigQuery](https://cloud.google.com/bigquery)에 기록이 기록됩니다(이상 탐지 실행 또는 경고 생성).
- [Audit Log](https://cloud.google.com/logging/docs/audit) 항목이 생성됩니다(플래그 정책 위반 또는 의심스러운 활동).

두 가지 콘텐츠 모드가 모두 지원됩니다.

- **바이너리 콘텐츠 모드**(Eventarc 기본값): CloudEvents 속성이 전송됩니다.
  `ce-*` HTTP 헤더로 구성되며 본문에는 이벤트 데이터(일반적으로
  Pub/Sub 메시지 래퍼).
- **구조화된 콘텐츠 모드**: 모든 CloudEvents 속성과 데이터는
  JSON 본문.

??? "curl로 테스트(구조화된 모드)"

    ```bash
    curl -X POST http://localhost:8000/apps/my_agent/trigger/eventarc \
      -H "Content-Type: application/json" \
      -d '{
        "specversion": "1.0",
        "type": "google.cloud.storage.object.v1.finalized",
        "source": "//storage.googleapis.com/projects/my-project",
        "id": "event-123",
        "data": {
          "bucket": "my-bucket",
          "name": "uploads/document.pdf"
        }
      }'
    ```

??? "curl로 테스트(바이너리 모드)"

    ```bash
    curl -X POST http://localhost:8000/apps/my_agent/trigger/eventarc \
      -H "Content-Type: application/json" \
      -H "ce-type: google.cloud.storage.object.v1.finalized" \
      -H "ce-source: //storage.googleapis.com/projects/my-project" \
      -H "ce-id: event-456" \
      -H "ce-specversion: 1.0" \
      -d '{
        "message": {
          "data": "eyJidWNrZXQiOiAibXktYnVja2V0IiwgIm5hbWUiOiAiZG9jLnBkZiJ9",
          "attributes": {"eventType": "OBJECT_FINALIZE"}
        },
        "subscription": "projects/my-project/subscriptions/eventarc-sub"
      }'
    ```

#### 응답

| HTTP 상태 | 의미 |
| :---------- | :------ |
| **200** | 이벤트가 성공적으로 처리되었습니다. Eventarc에서 배송을 확인합니다. |
| **500** | 처리에 실패했습니다. Eventarc는 재시도 정책에 따라 전송을 재시도합니다. |

## 구성

### 동시성 제어

트리거 엔드포인트는 세마포어를 사용하여 동시 에이전트 수를 제한합니다.
호출. 이렇게 하면 에이전트가 LLM 모델 할당량을 초과하는 것을 방지할 수 있습니다.
폭발적인 이벤트 중에.

=== "Python"

    | 설정 | 기본값 | 환경 변수 |
    | :------ | :------ | :------------------- |
    | 최대 동시 호출 | 10 | `ADK_TRIGGER_MAX_CONCURRENT` |

=== "Go"

    | 설정 | 기본값 | 플래그 |
    | :------ | :------ | :------------------- |
    | 최대 동시 호출 | 10 | `--trigger_max_concurrent_runs` |

동시성 제한에 도달하면 들어오는 요청이 대기열에 추가되어 처리됩니다.
슬롯을 사용할 수 있게 되면 동시성 제어는 프로세스별로 이루어집니다. 배포하는 경우
여러 Cloud Run 인스턴스, 각 인스턴스는 자체적으로 독립적인 상태를 유지합니다.
세마포어.

=== "Python"

    ```bash
    # Allow up to 5 concurrent agent invocations
    export ADK_TRIGGER_MAX_CONCURRENT=5
    ```

=== "Go"

    ```bash
    go run event_processing_agent.go web api pubsub --trigger_max_concurrent_runs=5
    ```

### 백오프를 사용한 자동 재시도

트리거 끝점에는 다음과 같은 일시적인 오류에 대한 기본 재시도 논리가 포함되어 있습니다.
`429 RESOURCE_EXHAUSTED` 응답. 일시적인 오류가 감지되면
지수 백오프 및 지터를 사용하여 요청을 재시도합니다.

=== "Python"

    | 설정 | 기본값 | 환경 변수 |
    | :------ | :------ | :------------------- |
    | 최대 재시도 횟수 | 3 | `ADK_TRIGGER_MAX_RETRIES` |
    | 기본 백오프 지연 | 1.0초 | `ADK_TRIGGER_RETRY_BASE_DELAY` |
    | 최대 백오프 지연 | 30.0초 | `ADK_TRIGGER_RETRY_MAX_DELAY` |

=== "Go"

    | 설정 | 기본값 | 플래그 |
    | :------ | :------ | :------------------- |
    | 최대 재시도 횟수 | 3 | `--trigger_max_retries` |
    | 기본 백오프 지연 | 1.0초 | `--trigger_base_delay` |
    | 최대 백오프 지연 | 30.0초 | `--trigger_max_delay` |

모든 재시도가 소진되면 엔드포인트는 HTTP 500을 반환하고 신호를 보냅니다.
Pub/Sub 또는 Eventarc를 사용하여 더 높은 수준에서 전송을 재시도합니다.
일시적이지 않은 오류는 재시도 없이 즉시 실패합니다.

### 오류 처리 및 재해 복구

트리거 기반 워크로드의 재해 복구는 트리거링을 통해 처리됩니다.
ADK가 아닌 서비스:

- 에이전트가 충돌하거나 오류를 반환하는 경우 Pub/Sub 또는 Eventarc는
  승인을 받고 자동으로 메시지를 재전송합니다.
- 최대 재시도 횟수가 소진된 후 처리되지 않은 메시지는
  [dead-letter queue (DLQ)](https://cloud.google.com/pubsub/docs/dead-letter-topics)
  구성된 경우.
- 각각의 재전송은 새로운 세션을 생성합니다. 트리거 워크로드는 상태 비저장입니다.
  디자인 상.

### 시간 초과 고려사항

모든 트리거 엔드포인트는 동기식으로 처리되며 에이전트가
응답을 반환하기 전에 완료하세요. 이는 의도적으로 설계된 것입니다. HTTP를 유지하는 것입니다.
요청 활성은 호스팅 인프라가 종료되지 않도록 보장합니다.
에이전트가 작동하는 동안 처리하세요. 동기 응답 코드
(200 또는 500)은 Pub/Sub 및 Eventarc가 올바르게 인식할 수 있게 해줍니다.
성공하거나 재시도를 트리거합니다.

최대 처리 시간은 업스트림 서비스에 따라 결정됩니다.

| 서비스 | 최대 시간 초과 |
| :------ | :---------- |
| 게시/구독 푸시 | 10분(승인 기한) |
| 이벤트타르크 | 10분([Standard](https://cloud.google.com/eventarc/standard/docs/overview)는 Pub/Sub를 전송으로 사용하고 [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview)는 파이프라인을 통해 제공) |

트리거 엔드포인트는 10분 이내에 완료되는 에이전트를 위해 설계되었습니다.
이는 개별 이벤트 처리, 유효성 검사 실행,
문서를 분류하고 결과를 다운스트림 서비스에 기록합니다.

!!! warning "장기 실행 에이전트"
    트리거 엔드포인트는 10개 이상을 사용하는 에이전트에는 적합하지 않습니다.
    완료하는 데 몇 분 걸립니다. 장기 실행 워크로드의 경우 다음을 사용하세요.
    [Pub/Sub pull subscriptions](https://cloud.google.com/pubsub/docs/pull),
    [Cloud Run Jobs](https://cloud.google.com/run/docs/create-jobs) 또는
    대신 작업자 풀 아키텍처.

### 세션 수명주기

세션은 다른 모든 ADK 진입점과 동일한 패턴을 따릅니다. 그들은
구성된 것을 통해 생성됨
[`SessionService`](../sessions/session/index.md). 기본적으로 ADK는 다음을 사용합니다.
트리거 세션을 임시로 만드는 `InMemorySessionService`:
이벤트 처리 후 폐기됩니다.

영구 `SessionService`(예: `DatabaseSessionService`)를 구성하는 경우
트리거 세션은 자동으로 저장됩니다. 이는 감사에 유용할 수 있습니다.
이벤트 중심 워크로드의 디버깅 및 사후 분석.

## 배포

아래 예에서는 [Cloud Run](https://cloud.google.com/run)를
배포 대상. Cloud Run은 현재 권장되는 플랫폼입니다.
트리거 엔드포인트를 사용하여 주변 에이전트를 배포합니다.

!!! note "인증 및 보안"
    트리거 엔드포인트는 ADK 웹 서버 내의 표준 HTTP 경로입니다.
    인증 및 보안은 배포 수준에서 시행됩니다.
    다른 ADK 엔드포인트와 동일합니다. 인증이 활성화된 상태로 배포된 경우
    (권장) 모든 엔드포인트에는 유효한 자격 증명이 필요합니다. GCP 서비스
    [service account](https://cloud.google.com/iam/docs/service-accounts)를 사용하여 인증
    정체성. 자세한 내용은 각 서비스의 설명서를 참조하세요.

=== "Python"

    다음을 사용하여 트리거를 활성화하여 Cloud Run에 에이전트를 배포합니다.
    `--trigger_sources` 플래그:

    ```bash
    adk deploy cloud_run \
      --project=$GOOGLE_CLOUD_PROJECT \
      --region=$GOOGLE_CLOUD_LOCATION \
      --trigger_sources="pubsub,eventarc" \
      path/to/your/agent
    ```

=== "Go"

    해당 트리거 플래그를 사용하여 트리거가 활성화된 Cloud Run에 에이전트를 배포합니다(모든 설정에는 트리거 유형이 앞에 붙습니다).

    ```bash
    adk deploy cloud_run \
      --project=$GOOGLE_CLOUD_PROJECT \
      --region=$GOOGLE_CLOUD_LOCATION \
      --pubsub \
      --pubsub_max_concurrent_runs=5 \
      --eventarc \
      --eventarc_max_concurrent_runs=5
    ```

배포 후 적절한 GCP 인프라를 에이전트의 인프라에 연결하세요.
트리거 끝점:

- **Pub/Sub**: [push subscription](https://cloud.google.com/pubsub/docs/push) 생성
  `/apps/{app_name}/trigger/pubsub`를 가리키고 있습니다.
- **Eventarc**: [Eventarc Standard trigger](https://docs.cloud.google.com/eventarc/standard/docs/event-providers-targets) 생성
  또는 [Eventarc Advanced pipeline](https://cloud.google.com/eventarc/advanced/docs/overview)
  `/apps/{app_name}/trigger/eventarc`로 라우팅됩니다.
- **클라우드 스케줄러**: [scheduler job](https://cloud.google.com/scheduler/docs/creating) 생성
  크론 일정에 따라 Pub/Sub 주제에 게시됩니다.

전체 배포는 [Deploy to Cloud Run](../deploy/cloud-run.md)를 참조하세요.
지침.

## 다음은 무엇입니까?

- [deploy your agent to Cloud Run](../deploy/cloud-run.md) 방법 알아보기
- 대화형 에이전트 호출을 위해 [API server endpoints](api-server.md) 살펴보기
- [Pub/Sub toolset](../integrations/pubsub.md)를 사용하여 에이전트에 메시지 게시 및 가져오기 기능 제공
