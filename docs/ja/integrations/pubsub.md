---
catalog_title: Pub/Sub ツール
catalog_description: Google Cloud Pub/Sub でメッセージの publish、pull、acknowledge を行います
catalog_icon: /adk-docs/integrations/assets/pubsub.png
catalog_tags: ["google"]
---

# ADK 向け Google Cloud Pub/Sub ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.22.0</span>
</div>

`PubSubToolset` を使うと、エージェントは
[Google Cloud Pub/Sub](https://cloud.google.com/pubsub)
サービスと連携して、メッセージの publish、pull、acknowledge を行えます。

## 前提条件

`PubSubToolset` を使用する前に、次を満たしてください:

1.  Google Cloud プロジェクトで **Pub/Sub API を有効化**する。
2.  **認証と認可**: エージェントを実行するプリンシパル (例: ユーザー、サービスアカウント) が Pub/Sub 操作に必要な IAM 権限を持っていること。Pub/Sub ロールの詳細は [Pub/Sub アクセス制御ドキュメント](https://cloud.google.com/pubsub/docs/access-control) を参照してください。
3.  **トピックまたはサブスクリプションを作成**する: メッセージ publish 用に [トピックを作成](https://cloud.google.com/pubsub/docs/create-topic) し、受信用に [サブスクリプションを作成](https://cloud.google.com/pubsub/docs/create-subscription) します。


## 使用方法

```py
--8<-- "examples/python/snippets/tools/built-in-tools/pubsub.py"
```
## ツール

`PubSubToolset` には次のツールが含まれます:

### `publish_message`

Pub/Sub トピックにメッセージを publish します。

| Parameter      | Type                | Description                                                                                             |
| -------------- | ------------------- | ------------------------------------------------------------------------------------------------------- |
| `topic_name`   | `str`               | Pub/Sub トピック名 (例: `projects/my-project/topics/my-topic`)。                            |
| `message`      | `str`               | publish するメッセージ本文。                                                                         |
| `attributes`   | `dict[str, str]`    | (任意) メッセージに付与する属性。                                                         |
| `ordering_key` | `str`               | (任意) メッセージの ordering key。これを設定するとメッセージは順序どおりに publish されます。 |

### `pull_messages`

Pub/Sub サブスクリプションからメッセージを pull します。

| Parameter           | Type    | Description                                                                                                 |
| ------------------- | ------- | ----------------------------------------------------------------------------------------------------------- |
| `subscription_name` | `str`   | Pub/Sub サブスクリプション名 (例: `projects/my-project/subscriptions/my-sub`)。                      |
| `max_messages`      | `int`   | (任意) pull するメッセージの最大件数。デフォルトは `1`。                                         |
| `auto_ack`          | `bool`  | (任意) メッセージを自動で acknowledge するか。デフォルトは `False`。                            |

### `acknowledge_messages`

Pub/Sub サブスクリプション上の 1 件以上のメッセージを acknowledge します。

| Parameter           | Type          | Description                                                                                       |
| ------------------- | ------------- | ------------------------------------------------------------------------------------------------- |
| `subscription_name` | `str`         | Pub/Sub サブスクリプション名 (例: `projects/my-project/subscriptions/my-sub`)。            |
| `ack_ids`           | `list[str]`   | acknowledge する acknowledgment ID の一覧。                                                      |
