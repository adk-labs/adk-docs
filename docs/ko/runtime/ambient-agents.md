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

- **클라우드 이벤트에 반응합니다.** [Cloud Storage](https://cloud.google.com/storage)에 파일이 업로드될 때 처리하거나, 데이터베이스 변경에 응답하거나, 감사 로그 항목을 처리합니다.
- **큐의 메시지를 처리합니다.** 수신되는 지원 티켓을 분석하고, 콘텐츠를 검토하고, 문서를 분류하거나, 항목이 도착할 때 QA를 실행합니다.
- **일정에 따라 실행됩니다.** 일일 보고서를 생성하거나, 주기적인 모니터링 점검을 실행하거나, 정기적으로 배치 작업을 처리합니다.
- **인프라를 모니터링합니다.** 인프라 전반의 지속적인 이벤트 스트림에 반응하고 변경 사항에 자율적으로 대응합니다.

## 앰비언트 에이전트에서 결과 받기

앰비언트 에이전트는 사람과의 상호작용 없이 실행되므로 출력을 알림 채널로 라우팅해야 합니다. 일반적인 패턴은 다음과 같습니다.

- **[구조화된 로깅](../observability/logging.md).** JSON 로그를 작성하고 이메일, Slack 또는 PagerDuty로 알림을 보내도록 [Cloud Monitoring](https://cloud.google.com/monitoring/support/notification-options) 알림을 구성합니다.
- **[Pub/Sub](https://cloud.google.com/pubsub).** 다운스트림 서비스에서 소비할 수 있도록 결과를 토픽에 발행(publish)합니다.
- **[Application Integration](https://cloud.google.com/application-integration/docs/listen-pub-sub-topic-send-email).** 에이전트 출력을 이메일, Jira 또는 기타 시스템으로 라우팅합니다.

## 앰비언트 에이전트 구축 방법

ADK는 두 가지 방식을 제공합니다.

| | [`/run`](api-server.md) | 트리거 엔드포인트 |
| :--- | :--- | :--- |
| **이벤트 소스** | 모두(Pub/Sub, 웹훅, 크론, 커스텀 서비스) | [Cloud Pub/Sub](https://cloud.google.com/pubsub), [Eventarc](https://cloud.google.com/eventarc)([Standard](https://cloud.google.com/eventarc/standard/docs/overview) 및 [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview)) |
| **페이로드 파싱** | 직접 처리 | 자동(Base64 디코딩, CloudEvent 파싱) |
| **세션 생성** | `--auto_create_session` 활성화 | 자동(이벤트당 1개) |
| **세션 저장** | 구성된 [`SessionService`](../sessions/session/index.md) | 구성된 [`SessionService`](../sessions/session/index.md) |
| **동시성 제어** | 직접 처리 | 한도를 구성할 수 있는 내장 세마포어 |
| **재시도 로직** | 직접 처리 | 일시적인 오류에 대한 지터(jitter) 포함 지수 백오프 |
| **적합한 용도** | 커스텀 통합, GCP 외부 소스 | GCP 네이티브 이벤트 기반 워크로드 |

## `/run` 사용하기

통합을 완전히 직접 제어해야 하거나 GCP 외부 이벤트 소스를 사용하는 경우 [`/run`](api-server.md) 엔드포인트를 사용하세요. 세션이 자동으로 생성되도록 `--auto_create_session`을 활성화한 다음, 이벤트가 도착할 때 임의의 HTTP 클라이언트를 연결해 `/run`을 호출하면 됩니다.

```bash
adk api_server --auto_create_session path/to/your/agent
```

이 패턴은 HTTP 요청을 할 수 있는 모든 이벤트 소스에서 작동합니다.

??? "예시: 수신 웹훅 처리"

    다음 [Cloud Run 함수](https://cloud.google.com/functions/docs/writing/write-event-driven-functions)는 외부 서비스(예: GitHub)로부터 웹훅을 수신하여 에이전트로 전달합니다.

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

??? "예시: `curl`을 사용하여 이벤트 보내기"

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

## 트리거 엔드포인트 사용하기

이벤트 소스가 Pub/Sub 또는 Eventarc이고, 페이로드 파싱, 세션 생성, 동시성 제어 및 재시도를 ADK가 처리하도록 하려면 트리거 엔드포인트를 사용하세요.

### 이벤트 처리 방식

Pub/Sub와 Eventarc는 이벤트를 HTTP POST 요청으로 에이전트에 전달합니다. 트리거 엔드포인트가 이벤트를 수신하면 다음을 수행합니다.

1. 소스 형식(Pub/Sub 푸시 메시지 또는 CloudEvent)에 따라 **요청을 파싱**합니다.
2. **페이로드를 디코딩합니다.** Base64로 인코딩된 메시지 데이터를 디코딩하고, 가능한 경우 JSON으로 파싱합니다.
3. 생성된 UUID를 사용하여 자동으로 **세션을 생성**합니다. `/run` 엔드포인트와 달리 `--auto_create_session`을 활성화할 필요가 없으며, 트리거 엔드포인트는 항상 이벤트마다 새 세션을 생성합니다.
4. 디코딩된 이벤트를 사용자 메시지로 전달해 **에이전트를 실행**합니다.
5. **상태 코드를 반환합니다.** `200` 응답은 Pub/Sub 또는 Eventarc에 이벤트가 성공적으로 처리되었음을 알립니다. `500` 응답은 실패를 나타내며, 이벤트 소스는 재시도 정책에 따라 전달을 재시도합니다.

### 지원되는 소스

| 소스 | 엔드포인트 | 설명 |
| :----- | :------- | :---------- |
| **Pub/Sub** | `/apps/{app_name}/trigger/pubsub` | [Pub/Sub 푸시 구독](https://cloud.google.com/pubsub/docs/push)으로부터 메시지를 수신합니다. |
| **Eventarc** | `/apps/{app_name}/trigger/eventarc` | [Eventarc](https://cloud.google.com/eventarc)([Standard](https://cloud.google.com/eventarc/standard/docs/overview) 또는 [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview))에서 전달한 [CloudEvents](https://cloudevents.io/)를 수신하며 구조화된 콘텐츠 모드와 바이너리 콘텐츠 모드를 모두 지원합니다. |

### 예시 에이전트

=== "Python"
    다음 에이전트는 트리거 엔드포인트에서 전달된 이벤트를 처리합니다. `parse_event` 도구를 사용해 이벤트 데이터와 속성을 추출한 뒤 내용을 분석합니다.

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

    트리거 엔드포인트는 기본적으로 비활성화되어 있습니다. `--trigger_sources` 플래그를 사용하여 활성화하세요.

    ```shell
    adk api_server --trigger_sources "pubsub,eventarc" path/to/your/agent
    ```

    프로덕션 배포의 경우 사용자 지정 FastAPI 진입점에서 프로그래밍 방식으로 트리거를 활성화할 수 있습니다.

    ???+ "배포 진입점(`main.py`)"

        === "Python"
            ```python
            --8<-- "examples/python/snippets/runtime/triggers/main.py:triggers"
            ```

=== "Go"

    트리거 엔드포인트는 기본적으로 비활성화되어 있습니다. 해당 트리거 플래그를 사용하여 활성화하세요.

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

    Go 서버의 경우 다음 요청에서 URL로 `http://localhost:8080/api/apps/event_processor/trigger/pubsub`를 사용하세요.

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

`/run` 엔드포인트는 `app_name`, `user_id`, `session_id`를 직접 전달해야 합니다. 반면 트리거 엔드포인트는 이 값들을 자동으로 도출합니다.

| 매개변수 | 소스 |
| :-------- | :----- |
| `app_name` | URL 경로(`/apps/{app_name}/trigger/...`)에서 추출됨 |
| `session_id` | 이벤트당 자동 생성된 UUID |
| `user_id` | Pub/Sub: `subscription` 필드. Eventarc: `source` 또는 `ce-source` 헤더. |

### 메시지 형식

모든 트리거 엔드포인트는 수신 이벤트를 사용자 메시지로 에이전트에 전달하기 전에 다음과 같은 일관된 JSON 구조로 정규화합니다.

```json
{
  "data": "<decoded event payload>",
  "attributes": {"key": "value"}
}
```

- **`data`**: 디코딩된 이벤트 페이로드입니다. 원본 데이터가 JSON인 경우 구조화된 객체로 파싱되며, 그렇지 않으면 일반 문자열로 전달됩니다.
- **`attributes`**: 이벤트 소스의 키-값 메타데이터입니다(예: Pub/Sub 메시지 속성 또는 `ce-type`, `ce-source`와 같은 CloudEvents 헤더).

에이전트는 이 JSON 문자열을 입력 메시지로 수신하며, 이를 파싱해 데이터와 속성을 추출할 수 있습니다.

### Pub/Sub

Pub/Sub 트리거 엔드포인트는 [Pub/Sub 푸시 구독](https://cloud.google.com/pubsub/docs/push)의 메시지를 처리합니다. 애플리케이션이나 서비스가 토픽에 메시지를 발행(publish)할 때 사용하세요. 예를 들면 다음과 같습니다.

- 지원 포털에서 분류 및 라우팅을 위해 수신 티켓을 발행합니다.
- 콘텐츠 파이프라인에서 분류 또는 검토를 위해 문서를 전송합니다.
- 모니터링 서비스에서 자동 분석을 위해 알림을 발행합니다.

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

`data` 필드는 Base64로 인코딩되어 있으며, 트리거 엔드포인트가 이를 자동으로 디코딩합니다.

#### 응답

| HTTP 상태 | 의미 |
| :---------- | :------ |
| **200** | 이벤트가 성공적으로 처리되었습니다. Pub/Sub가 메시지를 확인(ack)합니다. |
| **400** | 잘못된 요청입니다(잘못된 Base64 인코딩). 메시지가 재시도되지 않습니다. |
| **500** | 처리에 실패했습니다(일시적 또는 비일시적 에이전트 오류). Pub/Sub는 [재시도 정책](https://cloud.google.com/pubsub/docs/handling-failures)에 따라 전달을 재시도합니다. 반복적으로 실패하는 메시지를 포착하도록 [데드 레터 큐(DLQ)](https://cloud.google.com/pubsub/docs/dead-letter-topics)를 구성하세요. |

### Eventarc

Eventarc 트리거 엔드포인트는 [Eventarc](https://cloud.google.com/eventarc)의 [Standard](https://cloud.google.com/eventarc/standard/docs/overview) 및 [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview) 에디션 모두에서 전달하는 [CloudEvents](https://cloud.google.com/eventarc/docs/cloudevents)를 처리합니다. 다음과 같이 Google Cloud 전반의 이벤트에 반응할 때 사용하세요.

- [Cloud Storage](https://cloud.google.com/storage)에 파일이 업로드될 때(문서 분류, 요약 또는 데이터 추출).
- [BigQuery](https://cloud.google.com/bigquery)에 레코드가 기록될 때(이상 탐지 실행 또는 알림 생성).
- [감사 로그(Audit Log)](https://cloud.google.com/logging/docs/audit) 항목이 생성될 때(정책 위반 또는 의심스러운 활동 표시).

두 가지 콘텐츠 모드를 모두 지원합니다.

- **바이너리 콘텐츠 모드**(Eventarc 기본값): CloudEvents 속성은 `ce-*` HTTP 헤더로 전송되고, 본문에는 이벤트 데이터(일반적으로 Pub/Sub 메시지 래퍼)가 포함됩니다.
- **구조화된 콘텐츠 모드**: 모든 CloudEvents 속성과 데이터가 JSON 본문에 포함됩니다.

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
| **200** | 이벤트가 성공적으로 처리되었습니다. Eventarc가 전달을 확인(ack)합니다. |
| **500** | 처리에 실패했습니다. Eventarc는 재시도 정책에 따라 전달을 재시도합니다. |

## 구성

### 동시성 제어

트리거 엔드포인트는 세마포어를 사용하여 동시 에이전트 호출 수를 제한합니다. 이를 통해 이벤트가 급증할 때 에이전트가 LLM 모델 할당량을 초과하는 것을 방지할 수 있습니다.

=== "Python"

    | 설정 | 기본값 | 환경 변수 |
    | :------ | :------ | :------------------- |
    | 최대 동시 호출 | 10 | `ADK_TRIGGER_MAX_CONCURRENT` |

=== "Go"

    | 설정 | 기본값 | 플래그 |
    | :------ | :------ | :------------------- |
    | 최대 동시 호출 | 100 | `--trigger_max_concurrent_runs` |

    기본적으로 ADK Go는 최대 100개의 동시 호출을 허용하며, ADK Python은 10개를 허용합니다.

    !!! note "ADK Go의 Pub/Sub 트리거 동시성"

        ADK Go v2.3.0부터 v2.5.0까지는 Pub/Sub 트리거에 `--trigger_max_concurrent_runs`를 적용하지 않으므로 Pub/Sub 이벤트가 동시성 제한 없이 실행됩니다. Pub/Sub 동시성을 제한하려면 ADK Go v2.6.0 이상을 사용하세요.

동시성 한도에 도달하면 수신 요청은 큐에 추가되어 슬롯이 확보되는 대로 처리됩니다. 동시성 제어는 프로세스 단위로 적용됩니다. 여러 Cloud Run 인스턴스를 배포하는 경우 각 인스턴스는 독립적인 자체 세마포어를 유지합니다.

=== "Python"

    ```bash
    # Allow up to 5 concurrent agent invocations
    export ADK_TRIGGER_MAX_CONCURRENT=5
    ```

=== "Go"

    ```bash
    go run event_processing_agent.go web api eventarc --trigger_max_concurrent_runs=5
    ```

### 백오프를 사용한 자동 재시도

트리거 엔드포인트에는 `429 RESOURCE_EXHAUSTED` 응답과 같은 일시적인 오류에 대한 내장 재시도 로직이 포함되어 있습니다. 일시적인 오류가 감지되면 지수 백오프와 지터(jitter)를 사용해 요청을 재시도합니다.

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
    | 최대 백오프 지연 | 10.0초 | `--trigger_max_delay` |

    기본적으로 ADK Go는 백오프 지연을 최대 10초로 제한하며, ADK Python은 최대 30초로 제한합니다.

모든 재시도가 소진되면 엔드포인트는 HTTP 500을 반환하여 Pub/Sub 또는 Eventarc가 상위 수준에서 전달을 재시도하도록 알립니다. 일시적이지 않은 오류는 재시도 없이 즉시 실패합니다.

### 오류 처리 및 재해 복구

트리거 기반 워크로드의 재해 복구는 ADK가 아니라 이벤트를 트리거하는 서비스에서 처리합니다.

- 에이전트가 비정상 종료되거나 오류를 반환하면 Pub/Sub 또는 Eventarc는 확인 응답(ack)을 받지 못하므로 메시지를 자동으로 재전송합니다.
- 최대 재시도 횟수가 소진된 후에도 처리되지 않은 메시지는 [데드 레터 큐(DLQ)](https://cloud.google.com/pubsub/docs/dead-letter-topics)가 구성된 경우 해당 큐로 이동합니다.
- 각 재전송은 새로운 세션을 생성합니다. 트리거 워크로드는 설계상 무상태(stateless)로 동작합니다.

### 타임아웃 고려사항

모든 트리거 엔드포인트는 동기식으로 처리되며, 응답을 반환하기 전에 에이전트 실행이 완료될 때까지 대기합니다. 이는 의도된 설계입니다. HTTP 요청을 활성 상태로 유지해야 에이전트가 작업하는 동안 호스팅 인프라가 프로세스를 종료하지 않기 때문입니다. 또한 동기식 응답 코드(200 또는 500)를 통해 Pub/Sub와 Eventarc가 처리 성공을 확인하거나 재시도를 트리거할 수 있습니다.

최대 처리 시간은 업스트림 서비스에 따라 결정됩니다.

| 서비스 | 최대 타임아웃 |
| :------ | :---------- |
| Pub/Sub 푸시 | 10분(확인 기한) |
| Eventarc | 10분([Standard](https://cloud.google.com/eventarc/standard/docs/overview)는 Pub/Sub를 전송 계층으로 사용하며, [Advanced](https://cloud.google.com/eventarc/advanced/docs/overview)는 파이프라인을 통해 전달) |

트리거 엔드포인트는 10분 이내에 완료되는 에이전트를 위해 설계되었습니다. 개별 이벤트 처리, 유효성 검사 실행, 문서 분류 및 다운스트림 서비스로의 결과 기록에 적합합니다.

!!! warning "장기 실행 에이전트"
    트리거 엔드포인트는 완료하는 데 10분 이상 걸리는 에이전트에는 적합하지 않습니다. 장기 실행 워크로드의 경우 대신 [Pub/Sub 풀 구독](https://cloud.google.com/pubsub/docs/pull), [Cloud Run Jobs](https://cloud.google.com/run/docs/create-jobs) 또는 워커 풀 아키텍처를 사용하세요.

### 세션 라이프사이클

세션은 다른 모든 ADK 진입점과 동일한 패턴을 따르며, 구성된 [`SessionService`](../sessions/session/index.md)를 통해 생성됩니다. 기본적으로 ADK는 `InMemorySessionService`를 사용하므로 트리거 세션은 이벤트마다 생성되고 처리 후 폐기되는 임시 세션으로 동작합니다.

영구 `SessionService`(예: `DatabaseSessionService`)를 구성하면 트리거 세션이 자동으로 저장됩니다. 이는 이벤트 기반 워크로드의 감사, 디버깅 및 사후 분석에 유용합니다.

## 배포

아래 예시에서는 [Cloud Run](https://cloud.google.com/run)을 배포 대상으로 사용합니다. Cloud Run은 현재 트리거 엔드포인트를 사용하는 앰비언트 에이전트를 배포할 때 권장되는 플랫폼입니다.

!!! note "인증 및 보안"
    트리거 엔드포인트는 ADK 웹 서버 내의 표준 HTTP 경로입니다. 인증 및 보안은 다른 ADK 엔드포인트와 마찬가지로 배포 수준에서 적용됩니다. 인증을 활성화하여 배포한 경우(권장) 모든 엔드포인트에는 유효한 자격 증명이 필요합니다. GCP 서비스는 [서비스 계정](https://cloud.google.com/iam/docs/service-accounts) ID를 사용하여 인증합니다. 자세한 내용은 각 서비스의 문서를 참고하세요.

=== "Python"

    `--trigger_sources` 플래그로 트리거를 활성화하여 Cloud Run에 에이전트를 배포합니다.

    ```bash
    adk deploy cloud_run \
      --project=$GOOGLE_CLOUD_PROJECT \
      --region=$GOOGLE_CLOUD_LOCATION \
      --trigger_sources="pubsub,eventarc" \
      path/to/your/agent
    ```

=== "Go"

    `adkgo` CLI와 각 트리거용 플래그를 사용하여 에이전트를 Cloud Run에 배포합니다:

    ```bash
    ./adkgo deploy cloudrun \
      -p $GOOGLE_CLOUD_PROJECT \
      -r $GOOGLE_CLOUD_LOCATION \
      -s $SERVICE_NAME \
      -e ./main.go \
      --pubsub \
      --eventarc \
      --eventarc_max_concurrent_runs=5
    ```

    ADK Go는 `/api` 경로 접두사 아래에서 트리거 엔드포인트를 제공하므로, 푸시 구독과 Eventarc 트리거가 `/api/apps/{app_name}/trigger/pubsub` 및 `/api/apps/{app_name}/trigger/eventarc`를 가리키도록 설정하세요.

배포 후 적절한 GCP 인프라를 에이전트의 트리거 엔드포인트에 연결하세요.

- **Pub/Sub**: `/apps/{app_name}/trigger/pubsub`를 가리키는 [푸시 구독](https://cloud.google.com/pubsub/docs/push)을 생성합니다.
- **Eventarc**: `/apps/{app_name}/trigger/eventarc`로 라우팅하는 [Eventarc Standard 트리거](https://docs.cloud.google.com/eventarc/standard/docs/event-providers-targets) 또는 [Eventarc Advanced 파이프라인](https://cloud.google.com/eventarc/advanced/docs/overview)을 생성합니다.
- **Cloud Scheduler**: 크론 일정에 따라 Pub/Sub 토픽에 메시지를 발행(publish)하는 [스케줄러 작업](https://cloud.google.com/scheduler/docs/creating)을 생성합니다.

전체 배포 지침은 [Cloud Run에 배포하기](../deploy/cloud-run.md)를 참고하세요.

## 다음 단계

- [Cloud Run에 에이전트를 배포하는 방법](../deploy/cloud-run.md) 알아보기
- 대화형 에이전트 호출을 위한 [API 서버 엔드포인트](api-server.md) 살펴보기
- [Pub/Sub 도구 세트](../integrations/pubsub.md)를 사용하여 에이전트에 메시지 발행(publish) 및 풀(pull) 기능 제공하기
