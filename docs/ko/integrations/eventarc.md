---
catalog_title: Google Cloud Eventarc 도구
catalog_description: 스키마 검증과 함께 구조화된 CloudEvent를 메시지 버스로 게시
catalog_icon: /integrations/assets/eventarc.png
catalog_tags: ["google"]
---

# ADK용 Google Cloud Eventarc 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.6.0</span><span class="lst-preview">실험적 기능 (Experimental)</span>
</div>

`EventarcToolset`을 사용하면 에이전트가 [Google Cloud Eventarc](https://cloud.google.com/eventarc)와 상호작용하여 비동기식으로 구조화된 [CloudEvents](https://cloudevents.io)를 Eventarc 메시지 버스(Message Bus)로 게시할 수 있습니다. 이 도구 세트는 호출 간 연결 풀링 및 캐싱 기능을 기본 제공하며, 일반적인 목적의 이벤트 게시 및 도메인 특화된 스키마 강제 이벤트 도구를 모두 지원합니다.

!!! example "실험적 기능 (Experimental)"
    이 기능은 실험적이며 향후 릴리스에서 업데이트될 수 있습니다.

## 사전 요구 사항 (Prerequisites)

`EventarcToolset`을 사용하기 전에 다음 설정 단계를 완료해야 합니다.

1.  **Eventarc API 활성화**: Google Cloud 프로젝트에서 Eventarc 및 Eventarc Publishing API를 활성화합니다.

    ```bash
    gcloud services enable eventarc.googleapis.com eventarcpublishing.googleapis.com
    ```

2.  **인증 및 권한 부여**: 에이전트를 실행하는 주체(Principal)에게 Eventarc 메시지 버스에 메시지를 게시할 수 있는 필요한 IAM 권한(예: `roles/eventarc.publisher` 역할)이 있는지 확인합니다. Eventarc IAM 역할에 대한 자세한 내용은 [Eventarc 액세스 제어 문서](https://cloud.google.com/eventarc/docs/access-control)를 참조하세요. 로컬 개발 자격 증명을 설정하려면 [애플리케이션 기본 자격 증명(ADC) 제공](https://cloud.google.com/docs/authentication/provide-credentials-adc)을 참조하세요.
3.  **메시지 버스 생성**: 게시된 이벤트를 수신할 대상 Eventarc Advanced 메시지 버스를 Google Cloud 프로젝트에 생성합니다.

    ```bash
    gcloud eventarc message-buses create my-bus \
        --location=us-central1 \
        --logging-config=DEBUG
    ```

4.  **필수 종속성 설치**: Google Cloud Eventarc 클라이언트 라이브러리가 포함되도록 `gcp` 추가 패키지를 설치합니다.

    ```bash
    pip install "google-adk[gcp]"
    ```

## 에이전트와 함께 사용

다음 예제는 CloudEvent를 게시하기 위해 `EventarcToolset`을 구성하고 에이전트에 장착하는 방법을 보여줍니다.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/eventarc.py"
```

## 도구 목록

`EventarcToolset`에는 기본적으로 다음과 같은 일반 게시 도구가 포함되어 있습니다.

### `publish_message`

Google Cloud Eventarc Advanced 메시지 버스에 구조화된 CloudEvent를 게시합니다.

| 매개변수 | 타입 | 설명 |
| --- | --- | --- |
| `bus` | `str` | Eventarc 메시지 버스의 전체 리소스 이름 (예: `projects/my-project/locations/us-central1/messageBuses/my-bus`). |
| `type` | `str` | 발생한 사건을 나타내는 CloudEvents 타입 식별자 (예: `com.example.user.signup`). |
| `source` | `str` | 이벤트가 발생한 컨텍스트를 식별하는 CloudEvents 소스 URI (예: `//my-service/auth`). |
| `data` | `dict \| str \| Any` | (선택 사항) CloudEvent에 포함할 이벤트 페이로드 데이터. |
| `datacontenttype` | `str` | (선택 사항) `data`의 미디어 타입 (예: `application/json`). 딕셔너리나 JSON 데이터가 제공되면 기본값은 `application/json`입니다. |
| `subject` | `str` | (선택 사항) 이벤트 생산자 컨텍스트에서의 이벤트 주제. |
| `id` | `str` | (선택 사항) 이벤트의 고유 식별자. 제공되지 않으면 UUID가 자동으로 생성됩니다. |
| `time` | `str` | (선택 사항) RFC 3339 형식의 이벤트 발생 타임스탬프. 제공되지 않으면 현재 UTC 타임스탬프가 사용됩니다. |
| `specversion` | `str` | (선택 사항) CloudEvents 사양 버전. 기본값은 `1.0`입니다. |
| `is_base64_encoded` | `bool` | (선택 사항) `data`가 Base64로 인코딩된 바이너리 데이터인지 여부. 기본값은 `False`입니다. |
| `include_tracing_extension` | `bool` | (선택 사항) 분산 추적 컨텍스트를 자동으로 추출하여 CloudEvent의 확장 속성에 주입할지 여부. 기본값은 `False`입니다. |
| `custom_attributes` | `dict[str, str]` | (선택 사항) 이벤트에 첨부할 추가 커스텀 CloudEvent 확장 속성. |

## 도메인 특화 게시 도구 (Domain-specific publish tools)

프로덕션 멀티 에이전트 아키텍처에서는 LLM이 라우팅 매개변수(`bus`, `type`, `source`)를 자유롭게 채우도록 허용하면 환각(hallucination)으로 인한 잘못된 목적지 설정이나 유형이 맞지 않는 이벤트 스키마가 발생할 수 있습니다. `EventarcToolset.create_publish_tool` 팩토리 메서드를 사용하면 엄격한 스키마를 갖춘 도메인 특화 게시 도구를 생성할 수 있습니다.

도메인 특화 도구를 생성하면 `CloudEventAttributesBinding`을 사용하여 라우팅 속성을 바인딩하는 동시에 이벤트 페이로드(`payload_schema`)에 대해 엄격한 Pydantic 모델을 강제할 수 있습니다. 이를 통해 생성된 이벤트가 비즈니스 도메인과 일치하고 승인된 메시지 버스로만 라우팅되도록 보장합니다.

### 에이전트와 함께 사용

```py
--8<-- "examples/python/snippets/tools/built-in-tools/eventarc_domain_specific.py"
```

### `create_publish_tool` 매개변수

`create_publish_tool` 메서드는 다음 키워드 전용 인수를 수용합니다.

| 매개변수 | 타입 | 설명 |
| --- | --- | --- |
| `name` | `str` | LLM에 노출되는 함수 도구 이름 (예: `complete_outreach_static`). |
| `description` | `str` | LLM이 이 도구를 언제 호출해야 하고 어떤 작업을 수행하는지 지시하는 자연어 설명. |
| `bus` | `str \| Callable[[Any], str] \| AgentProvided` | 대상 Eventarc 메시지 버스. 고정 URI 문자열, 도구 컨텍스트에 따라 평가되는 런타임 콜러블(Callable), 또는 LLM이 공급하도록 요청하는 `AgentProvided` 인스턴스일 수 있습니다. |
| `ce_attributes_binding` | `CloudEventAttributesBinding` | CloudEvent 속성(`type`, `source`, `subject`, `datacontenttype`, `time`, `id`, `specversion`, `custom_attributes`)에 대한 바인딩 규칙. |
| `payload_schema` | `type[pydantic.BaseModel] \| None` | (선택 사항) 구조화된 이벤트 페이로드를 정의하는 Pydantic 스키마 클래스. 지정된 경우 도구 시그니처에는 이 모델을 준수하는 `event_data` 매개변수가 필요합니다. 제공되지 않거나 `None`인 경우 도구 시그니처에 `event_data` 매개변수가 추가되지 않으며, 도구는 데이터 페이로드 본문 없이 알림 전용 CloudEvent를 게시합니다. |

### CloudEvent 속성 바인딩 및 센티널 (Attribute bindings and sentinels)

`CloudEventAttributesBinding` 데이터 클래스는 개별 CloudEvent 필드가 채워지는 방식을 구성합니다. 각 속성(`type`, `source`, `datacontenttype`, `subject`, `time`, `id`, `specversion`, `custom_attributes`)에는 다음 바인딩 메커니즘 중 하나를 할당할 수 있습니다.

| 바인딩 타입 | 예시 | LLM에 노출 여부 | 설명 |
| --- | --- | --- | --- |
| **Static String** | `type="vendor_outreach.completed"` | 아니오 | 고정된 리터럴 문자열을 강제합니다. 이 속성은 LLM 시그니처에서 숨겨지며 모든 호출에 자동으로 적용됩니다. |
| **Runtime Lambda** | `source=lambda ctx: f"//agent/{ctx.id}"` | 아니오 | 도구 런타임 컨텍스트를 사용하여 실행 시점에 동적으로 평가되는 콜러블(`Callable[[Any], str]`)입니다. LLM 시그니처에서 숨겨집니다. |
| **`AgentProvided`** | `subject=AgentProvided("Customer ID")` | 예 | ADK가 속성을 함수 시그니처의 명시적 매개변수로 노출하여 LLM이 이를 제공할 수 있도록 지시합니다. `description` 문자열을 허용합니다. |
| **`MISSING`** | `time=MISSING` | 아니오 | 선택적 속성의 기본 센티널입니다. 기본 동작이 적용됨을 나타냅니다 (예: `time`의 경우 현재 UTC 타임스탬프 자동 생성, `id`의 경우 UUID 자동 생성). |
| **`OMIT`** | `time=OMIT` | 아니오 | 생성된 CloudEvent에서 선택적 속성을 명시적으로 제외합니다. 필수 속성(`type`, `source`, `bus`)은 `OMIT`으로 설정할 수 없습니다. |

#### 예시: `MISSING`과 `OMIT` 차이점 이해하기

`MISSING`과 `OMIT`의 차이를 이해하기 위해 `time`과 같은 선택적 CloudEvent 속성에 어떤 영향을 미치는지 살펴보겠습니다.

-   **`time=MISSING` (기본 동작)**: `time=MISSING`으로 설정하거나 `time`을 지정하지 않은 채로 두면 도구 세트가 내장된 기본 동작을 적용합니다. `time`의 경우 RFC 3339 형식으로 현재 UTC 타임스탬프를 자동으로 생성하여 포함합니다 (예: `"time": "2026-07-31T20:20:00Z"`).
-   **`time=OMIT`**: `time=OMIT`으로 명시적으로 설정하면 게시된 CloudEvent 페이로드에서 `time` 필드가 완전히 제외됩니다. 다운스트림 이벤트 소비자가 선택적 속성을 필요로 하지 않거나 예상하지 않는 경우 `OMIT`을 사용하세요.

```py
from google.adk.integrations.eventarc import (
    CloudEventAttributesBinding,
    MISSING,
    OMIT,
)

# 1. MISSING 사용 (기본값): CloudEvent에 현재 UTC 타임스탬프가 자동으로 포함됨
binding_with_timestamp = CloudEventAttributesBinding(
    type="vendor_outreach.completed",
    source="//my-agent/outreach",
    time=MISSING,  # 결과: "time": "2026-07-31T20:20:00Z"
)

# 2. OMIT 사용: CloudEvent에 'time' 속성이 포함되지 않음
binding_without_timestamp = CloudEventAttributesBinding(
    type="vendor_outreach.completed",
    source="//my-agent/outreach",
    time=OMIT,  # 게시된 이벤트에서 'time' 필드가 제외됨
)
```

## 추가 리소스

- [Google Cloud Eventarc 문서](https://cloud.google.com/eventarc/docs)
- [ADK Python GitHub 리포지토리](https://github.com/google/adk-python)
