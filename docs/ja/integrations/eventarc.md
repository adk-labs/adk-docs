---
catalog_title: Google Cloud Eventarc ツール
catalog_description: スキーマ検証を備えた構造化 CloudEvent をメッセージバスに発行
catalog_icon: /integrations/assets/eventarc.png
catalog_tags: ["google"]
---

# ADK 用 Google Cloud Eventarc ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.6.0</span><span class="lst-preview">試験運用版 (Experimental)</span>
</div>

`EventarcToolset` を使用すると、エージェントは [Google Cloud Eventarc](https://cloud.google.com/eventarc) と相互作用し、構造化された [CloudEvents](https://cloudevents.io) を Eventarc メッセージバス (Message Bus) に非同期で発行できます。このツールセットは呼び出し間での組み込みコネクションプーリングとキャッシュを提供し、汎用的なイベント発行とドメイン固有のスキーマ適用イベントツールの両方をサポートします。

!!! example "試験運用版 (Experimental)"
    この機能は試験運用版であり、将来のリリースで更新される可能性があります。

## 前提条件 (Prerequisites)

`EventarcToolset` を使用する前に、次のセットアップ手順を完了する必要があります。

1.  **Eventarc API の有効化**: Google Cloud プロジェクトで Eventarc および Eventarc Publishing API を有効にします。

    ```bash
    gcloud services enable eventarc.googleapis.com eventarcpublishing.googleapis.com
    ```

2.  **認証と権限付与**: エージェントを実行するプリンシパルに、Eventarc メッセージバスにメッセージを発行するために必要な IAM 権限（たとえば `roles/eventarc.publisher` ロール）があることを確認します。Eventarc の IAM ロールの詳細については、[Eventarc のアクセス制御ドキュメント](https://cloud.google.com/eventarc/docs/access-control)を参照してください。ローカル開発用の認証情報を設定するには、[アプリケーションデフォルト認証情報 (ADC) の提供](https://cloud.google.com/docs/authentication/provide-credentials-adc)を参照してください。
3.  **メッセージバスの作成**: 発行されたイベントを受信するターゲット Eventarc Advanced メッセージバスを Google Cloud プロジェクトに作成します。

    ```bash
    gcloud eventarc message-buses create my-bus \
        --location=us-central1 \
        --logging-config=DEBUG
    ```

## エージェントでの使用

次の例は、CloudEvents を発行するために `EventarcToolset` を構成し、エージェントに装備する方法を示しています。

```py
--8<-- "examples/python/snippets/tools/built-in-tools/eventarc.py"
```

## ツール一覧

`EventarcToolset` には、デフォルトで次の汎用発行ツールが含まれています。

### `publish_message`

Google Cloud Eventarc Advanced メッセージバスに構造化された CloudEvent を発行します。

| パラメータ | 型 | 説明 |
| --- | --- | --- |
| `bus` | `str` | Eventarc メッセージバスの完全なリソース名（例: `projects/my-project/locations/us-central1/messageBuses/my-bus`）。 |
| `type` | `str` | 発生した事象を表す CloudEvents タイプ識別子（例: `com.example.user.signup`）。 |
| `source` | `str` | イベントが発生したコンテキストを識別する CloudEvents ソース URI（例: `//my-service/auth`）。 |
| `data` | `dict \| str \| Any` | （オプション）CloudEvent に含めるイベントペイロードデータ。 |
| `datacontenttype` | `str` | （オプション）`data` のメディアタイプ（例: `application/json`）。辞書または JSON データが提供された場合のデフォルトは `application/json` です。 |
| `subject` | `str` | （オプション）イベントプロデューサーのコンテキストにおけるイベントの件名。 |
| `id` | `str` | （オプション）イベントの一意の識別子。指定しない場合、UUID が自動生成されます。 |
| `time` | `str` | （オプション）RFC 3339 形式のイベント発生タイムスタンプ。指定しない場合、現在の UTC タイムスタンプが使用されます。 |
| `specversion` | `str` | （オプション）CloudEvents 仕様バージョン。デフォルトは `1.0` です。 |
| `is_base64_encoded` | `bool` | （オプション）`data` が Base64 エンコードされたバイナリデータかどうか。デフォルトは `False` です。 |
| `include_tracing_extension` | `bool` | （オプション）分散トレーシングコンテキストを自動的に抽出し、CloudEvent の拡張属性に注入するかどうか。デフォルトは `False` です。 |
| `custom_attributes` | `dict[str, str]` | （オプション）イベントに添付する追加のカスタム CloudEvent 拡張属性。 |

## ドメイン固有の発行ツール (Domain-specific publish tools)

本番環境のマルチエージェントアーキテクチャにおいて、LLM がルーティングパラメータ（`bus`、`type`、`source`）を自由に設定できるようにすると、ハルシネーションによる誤った送信先や不適切なイベントスキーマが発生する可能性があります。`EventarcToolset.create_publish_tool` ファクトリメソッドを使用すると、厳格なスキーマを持つドメイン固有の発行ツールを作成できます。

ドメイン固有のツールを作成することで、`CloudEventAttributesBinding` を使用してルーティング属性をバインドしながら、イベントペイロード（`payload_schema`）に対して厳格な Pydantic モデルを適用できます。これにより、生成されたイベントがビジネスドメインに一致し、承認されたメッセージバスにのみルーティングされることが保証されます。

### エージェントでの使用

```py
--8<-- "examples/python/snippets/tools/built-in-tools/eventarc_domain_specific.py"
```

### `create_publish_tool` のパラメータ

`create_publish_tool` メソッドは、以下のキーワード専用引数を受け入れます。

| パラメータ | 型 | 説明 |
| --- | --- | --- |
| `name` | `str` | LLM に公開される関数ツール名（例: `complete_outreach_static`）。 |
| `description` | `str` | LLM に対してこのツールをいつ呼び出すか、どのようなアクションを実行するかを指示する自然言語による説明。 |
| `bus` | `str \| Callable[[Any], str] \| AgentProvided` | ターゲットとなる Eventarc メッセージバス。固定の URI 文字列、ツールのコンテキストで評価されるランタイム Callable、または LLM に供給を求める `AgentProvided` インスタンスが可能です。 |
| `ce_attributes_binding` | `CloudEventAttributesBinding` | CloudEvent 属性（`type`、`source`、`subject`、`datacontenttype`、`time`、`id`、`specversion`、`custom_attributes`）のバインディングルール。 |
| `payload_schema` | `type[pydantic.BaseModel] \| None` | （オプション）構造化イベントペイロードを定義する Pydantic スキーマクラス。指定された場合、ツールシグネチャにはこのモデルに準拠する `event_data` パラメータが必要となります。指定されない場合（または `None` の場合）、ツールシグネチャに `event_data` パラメータは追加されず、ツールはデータペイロード本体のない通知専用 CloudEvent を発行します。 |

### CloudEvent 属性のバインディングとセンチネル (Attribute bindings and sentinels)

`CloudEventAttributesBinding` データクラスは、個々の CloudEvent フィールドがどのように設定されるかを構成します。各属性（`type`、`source`、`datacontenttype`、`subject`、`time`、`id`、`specversion`、`custom_attributes`）には、以下のバインディングメカニズムのいずれかを割り当てることができます。

| バインディングタイプ | 例 | LLMへの公開 | 説明 |
| --- | --- | --- | --- |
| **Static String** | `type="vendor_outreach.completed"` | いいえ | 固定のリテラル文字列を適用します。この属性は LLM シグネチャから隠され、毎回の呼び出しに自動的に適用されます。 |
| **Runtime Lambda** | `source=lambda ctx: f"//agent/{ctx.id}"` | いいえ | ツールのランタイムコンテキストを使用して実行時に動的に評価される Callable (`Callable[[Any], str]`) です。LLM シグネチャから隠されます。 |
| **`AgentProvided`** | `subject=AgentProvided("Customer ID")` | はい | ADK に対し、属性を関数シグネチャの明示的なパラメータとして公開し、LLM が提供できるように指示します。`description` 文字列を受け入れます。 |
| **`MISSING`** | `time=MISSING` | いいえ | オプション属性のデフォルトセンチネルです。デフォルトの動作が適用されることを示します（例: `time` の場合は現在の UTC タイムスタンプを自動生成、`id` の場合は UUID を自動生成）。 |
| **`OMIT`** | `time=OMIT` | いいえ | 生成された CloudEvent からオプション属性を明示的に除外します。必須属性（`type`、`source`、`bus`）を `OMIT` に設定することはできません。 |

#### 例: `MISSING` と `OMIT` の違いの理解

`MISSING` と `OMIT` の違いを理解するために、`time` などのオプションの CloudEvent 属性にどのように影響するかを見てみましょう。

-   **`time=MISSING`（デフォルトの動作）**: `time=MISSING` に設定する（または `time` を未指定のままにする）と、ツールセットはその組み込みのデフォルト動作を適用します。`time` の場合、RFC 3339 形式で現在の UTC タイムスタンプを自動的に生成して含めます（例: `"time": "2026-07-31T20:20:00Z"`）。
-   **`time=OMIT`**: 明示的に `time=OMIT` に設定すると、発行された CloudEvent ペイロードから `time` フィールドが完全に除外されます。ダウンストリームのイベントコンシューマーがオプションの属性を必要としない、または想定していない場合は `OMIT` を使用します。

```py
from google.adk.integrations.eventarc import (
    CloudEventAttributesBinding,
    MISSING,
    OMIT,
)

# 1. MISSING の使用 (デフォルト): CloudEvent に現在の UTC タイムスタンプが自動的に含まれます
binding_with_timestamp = CloudEventAttributesBinding(
    type="vendor_outreach.completed",
    source="//my-agent/outreach",
    time=MISSING,  # 結果: "time": "2026-07-31T20:20:00Z"
)

# 2. OMIT の使用: CloudEvent に 'time' 属性が含まれません
binding_without_timestamp = CloudEventAttributesBinding(
    type="vendor_outreach.completed",
    source="//my-agent/outreach",
    time=OMIT,  # 発行されたイベントから 'time' フィールドが除外されます
)
```

## 追加リソース

- [Google Cloud Eventarc ドキュメント](https://cloud.google.com/eventarc/docs)
- [ADK Python GitHub リポジトリ](https://github.com/google/adk-python)
