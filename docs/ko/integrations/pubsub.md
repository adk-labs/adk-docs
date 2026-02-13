---
catalog_title: Pub/Sub 도구
catalog_description: Google Cloud Pub/Sub에서 메시지를 게시, pull, acknowledge 합니다
catalog_icon: /adk-docs/integrations/assets/pubsub.png
catalog_tags: ["google"]
---

# ADK용 Google Cloud Pub/Sub 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.22.0</span>
</div>

`PubSubToolset`을 사용하면 에이전트가
[Google Cloud Pub/Sub](https://cloud.google.com/pubsub)
서비스와 상호작용하여 메시지를 게시(publish), pull, acknowledge할 수 있습니다.

## 사전 준비 사항

`PubSubToolset`을 사용하기 전에 다음이 필요합니다:

1.  Google Cloud 프로젝트에서 **Pub/Sub API를 활성화**합니다.
2.  **인증 및 권한 부여**: 에이전트를 실행하는 주체(예: 사용자, 서비스 계정)가 Pub/Sub 작업 수행에 필요한 IAM 권한을 가지고 있어야 합니다. Pub/Sub 역할에 대한 자세한 내용은 [Pub/Sub 액세스 제어 문서](https://cloud.google.com/pubsub/docs/access-control)를 참조하세요.
3.  **토픽 또는 구독 생성**: 메시지 게시를 위한 [토픽 생성](https://cloud.google.com/pubsub/docs/create-topic)과 메시지 수신을 위한 [구독 생성](https://cloud.google.com/pubsub/docs/create-subscription)이 필요합니다.


## 사용 방법

```py
--8<-- "examples/python/snippets/tools/built-in-tools/pubsub.py"
```
## 도구

`PubSubToolset`에는 다음 도구가 포함됩니다:

### `publish_message`

Pub/Sub 토픽에 메시지를 게시합니다.

| Parameter      | Type                | Description                                                                                             |
| -------------- | ------------------- | ------------------------------------------------------------------------------------------------------- |
| `topic_name`   | `str`               | Pub/Sub 토픽 이름(예: `projects/my-project/topics/my-topic`)입니다.                            |
| `message`      | `str`               | 게시할 메시지 내용입니다.                                                                         |
| `attributes`   | `dict[str, str]`    | (선택 사항) 메시지에 첨부할 속성입니다.                                                         |
| `ordering_key` | `str`               | (선택 사항) 메시지의 정렬 키입니다. 이 값을 설정하면 메시지가 순서대로 게시됩니다. |

### `pull_messages`

Pub/Sub 구독에서 메시지를 pull합니다.

| Parameter           | Type    | Description                                                                                                 |
| ------------------- | ------- | ----------------------------------------------------------------------------------------------------------- |
| `subscription_name` | `str`   | Pub/Sub 구독 이름(예: `projects/my-project/subscriptions/my-sub`)입니다.                      |
| `max_messages`      | `int`   | (선택 사항) pull할 최대 메시지 수입니다. 기본값은 `1`입니다.                                         |
| `auto_ack`          | `bool`  | (선택 사항) 메시지를 자동으로 acknowledge할지 여부입니다. 기본값은 `False`입니다.                            |

### `acknowledge_messages`

Pub/Sub 구독의 하나 이상의 메시지를 acknowledge합니다.

| Parameter           | Type          | Description                                                                                       |
| ------------------- | ------------- | ------------------------------------------------------------------------------------------------- |
| `subscription_name` | `str`         | Pub/Sub 구독 이름(예: `projects/my-project/subscriptions/my-sub`)입니다.            |
| `ack_ids`           | `list[str]`   | acknowledge할 acknowledgment ID 목록입니다.                                                      |
