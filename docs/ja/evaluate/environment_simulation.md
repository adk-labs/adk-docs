# 評価のための環境シミュレーション

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.24.0</span>
</div>

API、データベース、サードパーティサービスなどの外部依存に頼るエージェントを評価する場合、テスト中にそれらのツールを実行すると遅く、高コストで、不安定になりがちです。**環境シミュレーター**を使うと、エージェント自体を変更せずに、実行中のツール呼び出しを安全に横取りし、制御された決定的な応答に置き換えられます。これにより、エージェントのロジックだけを分離した hermetic なオフラインテストを作成し、安定した採点を行えます。

この機能でできること:

*   API エラーやエッジケースの応答をどう扱うかをテストする
*   ライブバックエンドにアクセスせずにオフラインで評価を実行する
*   LLM を使って現実的なモック応答を自動生成する
*   確率的な注入結果をシードで固定して再現可能なテストを作る

環境シミュレーションは [`before_tool_callback`](/ja/callbacks/types-of-callbacks/#tool-execution-callbacks) フックまたは [プラグインシステム](/ja/plugins/) を通じて ADK のツール実行パイプラインに統合されます。そのため、エージェントコードを変更する必要はありません。

```
環境シミュレーションは実験的機能です。API は今後のリリースで変更される可能性があります。
```

## 動作の仕組み

[User Simulation](/ja/evaluate/user-sim/) が会話を前へ進めるのに対し、環境シミュレーションは安定したバックエンドを提供します。高レベルでは、環境シミュレーターはエージェントとツールの間に挟まります。エージェントがツールを呼ぶと、シミュレーターはその呼び出しを横取りし、事前定義された注入応答や LLM 生成のモック応答を返すか、実ツールを実行させるかを判断します。

各ツールについての判断順序は次のとおりです。

1.  **Injection config** を順番に確認します。引数の一致と確率条件を満たすものがあれば、そのエラーまたは応答を即座に返します。
2.  一致する注入がなければ、**mock strategy** をフォールバックとして使います。ツールのスキーマと状態コンテキストに基づいて、LLM が現実的な応答を生成します。
3.  シミュレーター設定に存在しないツールなら `None` を返し、実ツールを通常実行させます。

## 統合

`EnvironmentSimulationFactory` は 2 つの統合ポイントを提供します。

*   `create_callback()` - 任意の `LlmAgent` の `before_tool_callback` に使える非同期コールバックを返します。
*   `create_plugin()` - ADK のプラグインシステムと統合する `EnvironmentSimulationPlugin` インスタンスを返します。

### コールバックとして使う

次の例は、環境シミュレーションを ADK エージェントのコールバックとして使う方法です。

```python
from google.adk.agents import LlmAgent
from google.adk.tools.environment_simulation import EnvironmentSimulationFactory
from google.adk.tools.environment_simulation.environment_simulation_config import (
    EnvironmentSimulationConfig,
    InjectedError,
    InjectionConfig,
    ToolSimulationConfig,
)

config = EnvironmentSimulationConfig(
    tool_simulation_configs=[
        ToolSimulationConfig(
            tool_name="get_user_profile",
            injection_configs=[
                InjectionConfig(
                    injected_error=InjectedError(
                        injected_http_error_code=503,
                        error_message="Service temporarily unavailable.",
                    )
                )
            ],
        )
    ]
)

agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    tools=[get_user_profile],
    before_tool_callback=EnvironmentSimulationFactory.create_callback(config),
)
```

### プラグインとして使う

次の例は、環境シミュレーションを ADK エージェントプラグインとして使う方法です。

```python
from google.adk.apps import App
from google.adk.tools.environment_simulation import EnvironmentSimulationFactory
from google.adk.tools.environment_simulation.environment_simulation_config import (
    EnvironmentSimulationConfig,
    MockStrategy,
    ToolSimulationConfig,
)

config = EnvironmentSimulationConfig(
    tool_simulation_configs=[
        ToolSimulationConfig(
            tool_name="search_products",
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
        )
    ]
)

app = App(
    agent=my_agent,
    plugins=[EnvironmentSimulationFactory.create_plugin(config)],
)
```

## 設定リファレンス

環境シミュレーターは複数の dataclass で設定できます。以下では各設定オブジェクトを詳しく説明します。

### `EnvironmentSimulationConfig`

最上位の設定オブジェクトです。

Field | Type | Default | Description
:--- | :--- | :--- | :---
`tool_simulation_configs` | `List[ToolSimulationConfig]` | required | シミュレーションするツールごとの設定です。空にはできず、ツール名は重複不可です。
`simulation_model` | `str` | `"gemini-2.5-flash"` | ツール接続の分析とモック応答生成に使う LLM です。
`simulation_model_configuration` | `GenerateContentConfig` | thinking enabled | 内部シミュレーター呼び出し用の LLM 生成設定です。
`environment_data` | `str \| None` | `None` | より現実的な応答を生成するためにモック戦略へ渡す任意の環境コンテキストです。例: JSON のデータベーススナップショット。
`tracing` | `str \| None` | `None` | 過去の文脈を与えるための trace データです。例: 以前のエージェント実行 trace の JSON 文字列。

### `ToolSimulationConfig`

単一のツールをどうシミュレートするかを定義します。

Field | Type | Default | Description
:--- | :--- | :--- | :---
`tool_name` | `str` | required | 登録済みのツール名と完全一致している必要があります。
`injection_configs` | `List[InjectionConfig]` | `[]` | モック戦略より前に順番に確認される注入設定です。
`mock_strategy_type` | `MockStrategy` | `MOCK_STRATEGY_UNSPECIFIED` | 注入がない場合のフォールバック戦略です。

### `InjectionConfig`

ツール呼び出しへ挿入する単一の synthetic 応答を制御します。
`injected_error` または `injected_response` のどちらか一方だけを設定してください。

Field | Type | Default | Description
:--- | :--- | :--- | :---
`injected_error` | `InjectedError \| None` | `None` | 返すエラーです。`injected_response` とは排他的です。
`injected_response` | `Dict[str, Any] \| None` | `None` | 返す固定レスポンス dict です。`injected_error` とは排他的です。
`injection_probability` | `float` | `1.0` | この注入が発火する確率です。範囲は `[0.0, 1.0]` です。
`match_args` | `Dict[str, Any] \| None` | `None` | 設定すると、ツール引数が `match_args` のキーと値をすべて含む場合にだけ発火します。
`injected_latency_seconds` | `float` | `0.0` | 注入結果を返す前に加える人工遅延です。最大 120 秒です。
`random_seed` | `int \| None` | `None` | 確率判定用のシードです。再現可能な注入動作に役立ちます。

### `InjectedError`

HTTP スタイルのエラー応答を定義します。

| Field | Type | Description |
| :--- | :--- | :--- |
| `injected_http_error_code` | `int` | ツール応答の `error_code` として返す HTTP ステータスコードです。 |
| `error_message` | `str` | ツール応答の `error_message` として返す、人が読めるメッセージです。 |

### `MockStrategy`

注入がないときにシミュレーターが応答をどう生成するかを制御する enum です。

| Value | Description |
| :--- | :--- |
| `MOCK_STRATEGY_TOOL_SPEC` | ツールのスキーマと状態コンテキストを使って、LLM に現実的な応答を生成させます。 |
| `MOCK_STRATEGY_TRACING` | *(Deprecated)* 代わりに tracing 入力付きの `MOCK_STRATEGY_TOOL_SPEC` を使ってください。 |

## 注入モード

注入設定は、特定の失敗やエッジケースをテストするために使います。
注入はリスト順に評価され、`match_args` 条件を満たし、確率チェックを通過した最初のものが適用されます。

### エラーの注入

次の例は、特定のエラーコードとエラーメッセージをエージェントに注入する方法です。

```python
from google.adk.tools.environment_simulation.environment_simulation_config import (
    InjectedError,
    InjectionConfig,
    ToolSimulationConfig,
)

ToolSimulationConfig(
    tool_name="charge_payment",
    injection_configs=[
        InjectionConfig(
            injected_error=InjectedError(
                injected_http_error_code=402,
                error_message="Payment declined.",
            )
        )
    ],
)
```

エージェントは実際のツール結果の代わりに `{"error_code": 402, "error_message": "Payment declined."}` を受け取り、支払い失敗時の振る舞いを評価できます。

### 固定応答の注入

固定の成功レスポンスを返すには、次のように `InjectionConfig` を使います。

```python
InjectionConfig(
    injected_response={"status": "ok", "order_id": "ORD-9999"}
)
```

### 引数マッチによる条件付き注入

特定の引数が渡されたときだけ注入するには `match_args` を使います。

```python
InjectionConfig(
    match_args={"item_id": "ITEM-404"},
    injected_error=InjectedError(
        injected_http_error_code=404,
        error_message="Item not found.",
    ),
)
```

この場合、`item_id="ITEM-404"` で呼ばれたときだけエラーが注入されます。それ以外の呼び出しは次の注入設定かモック戦略に進みます。

### 確率的注入

`injection_probability` を `0.0` から `1.0` の値に設定すると、flaky な動作をシミュレートできます。再現可能なテストのために `random_seed` も固定してください。

```python
InjectionConfig(
    injection_probability=0.3,
    random_seed=42,
    injected_error=InjectedError(
        injected_http_error_code=500,
        error_message="Internal server error.",
    ),
)
```

### 遅延の注入

`injected_latency_seconds` を使うと、遅いバックエンド応答を再現できます。timeout 対応や、劣化時の UX テストに便利です。

```python
InjectionConfig(
    injected_latency_seconds=5.0,
    injected_response={"result": "slow but successful"},
)
```

### 複数の注入設定を組み合わせる

1つのツールに複数の注入設定を置くと、順番に確認されます。次のように複数のシナリオを組み合わせられます。

```python
ToolSimulationConfig(
    tool_name="get_inventory",
    injection_configs=[
        # 品切れ SKU は常に失敗
        InjectionConfig(
            match_args={"sku": "OOS-001"},
            injected_response={"quantity": 0, "available": False},
        ),
        # それ以外は 20% の確率で失敗
        InjectionConfig(
            injection_probability=0.2,
            random_seed=7,
            injected_error=InjectedError(
                injected_http_error_code=503,
                error_message="Inventory service unavailable.",
            ),
        ),
    ],
)
```

## モック戦略モード

手作業の値ではなく、シミュレーターにそれらしい応答を自動生成させたいときは `MOCK_STRATEGY_TOOL_SPEC` を使います。

シミュレーターは LLM を使って次を行います。

1.  エージェントが使える全ツールのスキーマを分析し、ツール間の **stateful dependencies** を見つけます。
2.  セッション中に生成された ID やリソースを追跡する **state store** を維持します。
3.  現在の状態とツールスキーマに整合した応答を生成し、まだ作られていないリソースを要求された場合は 404 風のエラーを返します。

```python
from google.adk.tools.environment_simulation.environment_simulation_config import (
    EnvironmentSimulationConfig,
    MockStrategy,
    ToolSimulationConfig,
)

config = EnvironmentSimulationConfig(
    tool_simulation_configs=[
        ToolSimulationConfig(
            tool_name="create_order",
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
        ),
        ToolSimulationConfig(
            tool_name="get_order",
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
        ),
        ToolSimulationConfig(
            tool_name="cancel_order",
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
        ),
    ]
)
```

この設定では、`create_order` がモックされると `order_id` が自動生成され、その後 `get_order` や `cancel_order` が呼ばれたときに、一貫した結果または not-found エラーを返します。

### 環境データを渡す

ドメイン固有の文脈を `environment_data` に渡すと、モック応答をより現実的にできます。たとえば、データベースのスナップショットや、LLM に参照させたい構造化コンテキストを JSON 文字列で渡せます。

```python
import json

db_snapshot = {
    "products": [
        {"id": "P-001", "name": "Wireless Headphones", "price": 79.99, "stock": 12},
        {"id": "P-002", "name": "USB-C Hub", "price": 34.99, "stock": 0},
    ],
    "warehouse_location": "US-WEST-2",
}

config = EnvironmentSimulationConfig(
    tool_simulation_configs=[
        ToolSimulationConfig(
            tool_name="search_products",
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
        ),
    ],
    environment_data=json.dumps(db_snapshot),
)
```

LLM はこのデータを使って、任意のプレースホルダー値ではなく、ドメインに合った商品名・価格・在庫数を返します。

### tracing データを渡す

エージェントで生成した trace を `tracing` として渡すと、より現実的なモック応答にできます。

```python
import json

agent_traces = [
    {
        "invocation_id": "inv-001",
        "user_content": {"role": "user", "parts": [{"text": "Search for high-end headphones"}]},
        "intermediate_data": {
            "tool_uses": [
                {
                    "name": "search_products",
                    "args": {"query": "high-end headphones"},
                    "response": {"products": [{"id": "P-123", "name": "Premium Wireless ANC Headphones"}]}
                }
            ]
        }
    }
]

config = EnvironmentSimulationConfig(
    tool_simulation_configs=[
        ToolSimulationConfig(
            tool_name="search_products",
            mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
        ),
    ],
    tracing=json.dumps(agent_traces),
)
```

LLM はこのデータを使って、ドメインに合った商品名・価格・在庫数を返します。

## 注入とモック戦略を組み合わせる

同じツールに注入設定とモック戦略を共存させられます。注入が常に先に確認され、適用されない場合のみモック戦略が動きます。

```python
ToolSimulationConfig(
    tool_name="send_notification",
    injection_configs=[
        # 既知の不正な受信者は常に失敗
        InjectionConfig(
            match_args={"recipient_id": "INVALID"},
            injected_error=InjectedError(
                injected_http_error_code=400,
                error_message="Invalid recipient.",
            ),
        ),
    ],
    # それ以外の受信者には、それらしい成功応答を生成する
    mock_strategy_type=MockStrategy.MOCK_STRATEGY_TOOL_SPEC,
)
```
