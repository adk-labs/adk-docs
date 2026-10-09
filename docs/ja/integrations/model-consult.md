---
catalog_title: Model Consult
catalog_description: 高速な実行モデルでの困難な推論を、より強力なアドバイザーモデルにエスカレーションします
catalog_tags: ["resilience", "observability"]
---

# ADK 用 Model Consult ツール

<div class="language-support-tag">
  <span class="lst-supported">ADK でのサポート</span><span class="lst-python">Python v2.11.0</span>
</div>

単一のモデルを使用するエージェントはトレードオフに直面します。高速で低コストなモデルは日常的なステップを素早く少ないリソースで処理できますが、複雑なタスクにおける綿密な分析や意思決定にはあまり向いていない場合があります。対照的に、より強力なモデルは複雑な意思決定をうまく処理できますが、エージェントの各ステップにおける応答時間とリソースコストが増加します。

Model Consult を使用すると、エージェントは両方の長所を活用できます。エージェントは高速な実行（executor）モデルで動作し、自信を持って解決できない判断に直面したときに Model Consult ツールを呼び出して、より強力なアドバイザー（advisor）モデルからガイダンスを受け取ります。その後、エージェントは自身のツールを使用してタスクを続行します。エージェントは必要なステップでのみ強力なモデルを使用し、相談（consultation）が失敗した場合や相談の予算（上限回数）を使い果たした場合でも、すでに持っている情報を使って作業を続けます。

## ユースケース

- **コストの最適化**: エージェントの日常的なオーケストレーションやツールループは低コストのモデルで実行し、必要なステップでのみより強力なモデルに相談させます。
- **ポリシーの調整**: 複数条項にわたる複雑なポリシー判断をフロンティアモデルにエスカレーションさせ、そのガイダンスに基づいて自身のツールでアクションを実行させます。
- **ループからの救出（Loop rescue）**: エージェントが同じツール呼び出しを繰り返し出力した際により強力なモデルに相談させることで、反復ループから抜け出せるように支援します。

## 前提条件

- ADK Python v2.11.0 以降。
- 2 つのモデルへのアクセス: 低コストの実行モデルと、より強力なアドバイザーモデル（Google Cloud でホストされている Gemini Flash と Gemini Pro など）。
- ADK 用に構成されたモデルの認証情報: Vertex AI API が有効になっている Google Cloud プロジェクト、または Gemini API キーのいずれか。

## インストール

Model Consult は ADK Python パッケージに直接含まれているネイティブツールです。

```bash
pip install "google-adk>=2.11.0"
```

## エージェントでの使用

以下の `lookup_order` 関数の例のように、ドメインツールと並べて `ModelConsultTool` を `Agent` にアタッチします。このツールは `model_consult` 関数宣言を登録し、実行モデルのシステムインストラクションにデフォルトのエスカレーションポリシーを追加することで、いつどのようにアドバイザーに相談すべきかについての明確なルールをエージェントに与えます。

```python
from google.adk.agents import Agent
from google.adk.tools import ModelConsultTool

def lookup_order(order_id: str) -> dict[str, str]:
    """Looks up order status by identifier."""
    return {"order_id": order_id, "status": "held_for_fraud_review"}

root_agent = Agent(
    model="gemini-flash-latest",
    name="support_executor",
    instruction=(
        "You are an order support assistant. Resolve customer issues using"
        " your tools."
    ),
    tools=[
        lookup_order,
        ModelConsultTool(
            model="gemini-pro-latest",  # Advisor model
            max_uses=2,
            session_max_uses=5,
            thinking_level="high",
        ),
    ],
)
```

この例では次のように動作します。

* `support_executor` エージェントは高速なモデル（`gemini-flash-latest`）で実行され、`lookup_order` ツールを使用してユーザーの問題を解決しようとします。
* 実行モデルがいつ `model_consult` を呼び出すかを判断します。デフォルトの設定では、決定を下す前、行き詰まったとき、およびタスク完了を宣言する前に `model_consult` を呼び出すよう実行モデルに指示されます。
* `ModelConsultTool` は呼び出しをインターセプトし、`max_uses` の予算を確認して、現在のセッションイベントと `lookup_order` ツールの説明を 1 つのアドバイザー相談リクエストにパッケージ化します。
* アドバイザーモデルはコンテキストを評価して構造化されたテキストガイダンスを返し、`support_executor` が制御を再開して推奨されたツールを実行し、ターンを完了できるようにします。


## 利用可能なツール

ツール | 説明
---- | -----------
`model_consult` | セッション履歴と特定の質問をより強力なアドバイザーモデルにエスカレーションし、構造化されたガイダンスを取得します。

## 仕組み

実行モデルが `model_consult` を呼び出すと、`ModelConsultTool` は次の 4 つのステップを実行し、構造化された辞書を実行モデルに返します。

1. **予算の確認** — `ModelConsultTool` はターンごとのカウンターを `max_uses` と照合し、セッション全体のカウンターを `session_max_uses` と照合します。いずれかの上限に達している場合、ツールはアドバイザーモデルを呼び出さずに即座に `"status": "limit_reached"` を返し、すでに収集した情報で続行するよう実行モデルに指示します。
2. **コンテキストの引き継ぎ（Context handover）** — `ModelConsultTool` は相談内容を単一の `role='user'` の `types.Content` メッセージにパッケージ化します。`include_agent_instruction` と `include_tool_inventory` が `True` の場合、メッセージは解決された実行モデルのインストラクションと併用ツールのインベントリから始まります。次に、`ModelConsultTool` は `ModelConsultContextConfig` に従って `Session.events` 内の非部分的（non-partial）かつ巻き戻されていない（non-rewound）イベントを変換し、テキストパートを発話者ごとにラベル付けし、進行中の `model_consult` 呼び出しを除外しながら過去のツール呼び出しとツールレスポンスを読みやすいテキスト要約にフラット化します。最後に、`ModelConsultTool` はアクティブなエージェント名、実行モデルの質問、および実行モデルから渡された追加の `context` 文字列を含むハンドオフパートを追加します。
3. **ツールなしのアドバイザー呼び出し** — `ModelConsultTool` はツール呼び出しを無効にし、デフォルトのアドバイザーシステムインストラクション（または指定されている場合はカスタムの `advisor_instruction`）を使用して、構成されたアドバイザー `BaseLlm` を呼び出します。アドバイザーへのリクエストからはツール宣言が除外されるため、アドバイザー自身がツールを実行したり副作用を生じさせたりすることはできず、実行モデルが次にどのツールをどの引数で呼び出すべきかを示すテキストガイダンスのみを返すことができます。
4. **構造化されたツールレスポンス** — `ModelConsultTool` がエージェントループに例外を送出することはありません。代わりに、[レスポンスのステータス値](#response-status-values)で説明されているように、`status` 値を含む辞書を返します。

### レスポンスのステータス値 {#response-status-values}

`model_consult` が返す辞書の `status` フィールドには、次のいずれかの値が入ります。

| ステータス | 返される条件 | フィールド | 相談予算 |
| --- | --- | --- | --- |
| `ok` | アドバイザーがガイダンスを返した場合。 | `guidance`, `advisor_model`, `thinking_level`, `consults`, `usage`, `latency_ms` | ターンごとおよびセッションのカウンターをインクリメントします。 |
| `limit_reached` | `max_uses` または `session_max_uses` がすでに上限に達している場合。アドバイザーモデルは呼び出されません。 | `message`, `consults` | 消費されません。 |
| `error` | アドバイザー呼び出しがタイムアウトした、失敗した、または表示可能なテキストを生成しなかった場合。 | `error`, `message`, `advisor_model`, `consults` | 消費されません。 |
| `invalid_request` | `question` が空または空白文字のみの場合。 | `message` | 消費されません。 |

相談が成功すると、次のような辞書構造が返されます。示されているトークン数とレイテンシは例示であり、代表的な測定値ではありません。

```json
{
    "status": "ok",
    "guidance": "1. Call lookup_order with order_id='ORD-42'.",
    "advisor_model": "gemini-3.1-pro-preview",
    "thinking_level": "high",
    "consults": {
        "used_this_turn": 1,
        "max_uses": 2,
        "used_this_session": 1,
        "session_max_uses": 5,
        "remaining": 1
    },
    "usage": {
        "prompt_tokens": 612,
        "output_tokens": 184,
        "thoughts_tokens": 320,
        "total_tokens": 1116
    },
    "latency_ms": 842.5
}
```

## ベストプラクティス

Model Consult は追加の設定なしで動作します。結果を向上させるには、次のプラクティスを活用してください。

* 実行モデルで思考（thinking）機能を有効にする。
* デフォルトのエスカレーションポリシーを維持するか、ユースケースに合わせて実行モデルのプロンプトでエスカレーションポリシーを調整する。

### 実行モデルで思考機能を有効にする

実行モデルはいつ `model_consult` を呼び出すかを判断するため、推論できる状態にあるほどより良い判断を下せます。実行モデルで思考機能を有効にしてください。たとえば、動的思考（dynamic thinking）を備えた軽量モデルを使用します。

### 実行モデルがアドバイザーに相談するタイミングをカスタマイズする

`ModelConsultTool` オブジェクトは、実行モデルのシステムインストラクションにエスカレーションポリシーを追加します。デフォルトでは、このポリシーは決定を下す前、行き詰まったとき、およびタスク完了を宣言する前に `model_consult` を呼び出すよう実行モデルに指示します。これらは次の表の計画（Plan）、診断（Diagnose）、レビュー（Review）のトリガーをカバーしています。

デフォルトのポリシーを置き換えるには、`executor_instruction` に独自のテキストを渡します。ポリシーを削除するには、空の文字列（`""`）を渡します。

```python
ModelConsultTool(
    executor_instruction=(
        "Call model_consult before your first response, and whenever a"
        " tool call fails for a reason you cannot explain."
    ),
)
```

### 一般的な相談トリガー

次の表に、アドバイザーに相談する一般的な理由と、`executor_instruction` に追加できるトリガーを示します。

| 理由 | 役立つ理由 | トリガーの例 |
| --- | --- | --- |
| 計画（Plan） | タスク初期における誤った解釈やアプローチは、その後のすべてのステップに影響し、時間とトークンを浪費します。 | * 最初の応答の前。<br>* 実行モデルが事実を収集した後、本作業を開始する前。<br>* リクエストで解決策が提案されており、その検証方法を尋ねる場合。<br>* 複数のアプローチや解釈が可能で、特定のものを支持する証拠がない場合。<br>* 難しいとわかっているリクエストタイプの場合。 |
| 診断（Diagnose） | 失敗や矛盾は、実行モデルの前提のいずれかが誤っていることを意味します。 | * ツール呼び出しが失敗したか予期しない結果を返し、実行モデルがその理由を説明できない場合。<br>* 新しい情報がないまま、実行モデルが同じツール呼び出しや似たバリエーションを繰り返す場合。<br>* 実行モデルが自身の作業をやり直す場合。<br>* 2 つのソースまたはツールの結果が食い違う場合。<br>* 実行モデルがリクエスト自体が誤っていると結論付けた場合。 |
| レビュー（Review） | 要件に照らして結果を確認することで、ユーザーが気付く前にエラーや抜け漏れを発見できます。 | * 最終回答の前。<br>* 実行モデルが複雑なタスクの大部分を完了した後。 |

## 設定オプション

`ModelConsultTool` オブジェクトはアドバイザーモデルの選択、相談予算、プロンプトのオーバーライドを構成し、`ModelConsultContextConfig` は引き継ぎ前にセッションイベントをフォーマットおよび制限する方法を制御します。

### ModelConsultTool のオプション

`ModelConsultTool` クラスは次のコンストラクタ引数を受け取ります。

| オプション | 型 | デフォルト | 説明 |
| --- | --- | --- | --- |
| `model` | `str` \| `BaseLlm` | `'gemini-3.1-pro-preview'` | ADK のモデルレジストリを通じて解決されるアドバイザーモデル名、または事前構成された `BaseLlm` インスタンス。デフォルトはプレビューモデルであり、変更される可能性があります。 |
| `max_uses` | `int` | `None` | ユーザーターンごとの成功した相談の最大回数。`None` はターンごとの上限なしを意味します。 |
| `session_max_uses` | `int` | `None` | セッション全体での成功した相談の最大回数。`None` はセッション全体の上限なしを意味します。 |
| `thinking_level` | `str` \| `types.ThinkingLevel` | `'high'` | アドバイザーモデルの推論の深さ（effort）: `'minimal'`、`'low'`、`'medium'`、`'high'`、`types.ThinkingLevel` 列挙値、または思考を未設定のままにする場合は `'off'`、`'none'`、`None`。 |
| `max_output_tokens` | `int` | `None` | 推論モデルにおける表示可能な出力と思考トークンの両方を含む、アドバイザーの出力トークン数のオプション上限。 |
| `timeout_seconds` | `float` | `None` | 呼び出しごとの実時間（wall-clock）タイムアウト（秒）。`None` はツールレベルのタイムアウトなしを意味します。 |
| `context_config` | `ModelConsultContextConfig` | `None` | アドバイザー向けにセッション履歴をパッケージ化および制限する方法を制御します。 |
| `executor_instruction` | `str` | `None` | 実行モデルの `system_instruction` に自動的に追加されるデフォルトのエスカレーションポリシーをオーバーライドします。自動注入を無効にするには `""` を渡します。 |
| `advisor_instruction` | `str` | `None` | アドバイザーモデルに送信されるデフォルトのシステムインストラクションをオーバーライドします。 |
| `description` | `str` | `None` | 実行モデルに表示されるデフォルトのツール説明をオーバーライドします。 |
| `include_agent_instruction` | `bool` | `True` | ガイダンスが実行モデルの制約を尊重するよう、実行エージェント自身のインストラクションをアドバイザーに転送します。 |
| `include_tool_inventory` | `bool` | `True` | アドバイザー相談プロンプトに、実行モデルが持つ他のツールの名前と説明を含めます。 |
| `generate_content_config` | `types.GenerateContentConfig` | `None` | `temperature` や `safety_settings` など、アドバイザー呼び出しごとに複製されるベース生成設定。 |
| `name` | `str` | `'model_consult'` | 実行モデルに公開されるツール名。 |

### ModelConsultContextConfig のオプション

`ModelConsultContextConfig` は、`Session.events` をアドバイザーの入力コンテンツに変換する方法を制御します。

| オプション | 型 | デフォルト | 説明 |
| --- | --- | --- | --- |
| `include_session` | `bool` | `True` | `True` の場合は変換された `Session.events` 履歴を送信し、`False` の場合は過去のセッションイベントを省略します。 |
| `max_events` | `int` | `None` | 文字数予算を適用する前に、最新の非部分的（non-partial）なセッションイベントを最大でこの数まで保持します。`None` はすべてのイベントを保持します。 |
| `max_chars` | `int` | `200000` | 引き継がれるすべてのセッションターンにわたる文字数予算。`None` は文字数予算を無効にします。 |
| `max_part_chars` | `int` | `4000` | レンダリングされたツール呼び出し、ツール結果、およびコードブロックに対するパートごとの文字数上限（プレーンテキストパートはこの上限の 8 倍まで許可されます）。 |
| `include_media` | `bool` | `True` | `True` の場合はインラインメディアとファイル参照をアドバイザーモデルに転送し、`False` の場合はテキストプレースホルダーに置き換えます。セッションメディアをアドバイザーモデルに送信すべきでない場合は `False` に設定してください。 |
| `include_thoughts` | `bool` | `False` | `True` の場合、アドバイザーへの引き継ぎ内容に実行モデルの内部思考（thought）パートを含めます。 |

## 追加リソース

* [Model Consult Unit Guide](https://github.com/google/adk-python/blob/main/docs/guides/tools/model_consult/model_consult_tool/index.md)
