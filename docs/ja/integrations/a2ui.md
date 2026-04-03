---
catalog_title: A2UI
catalog_description: Agent-to-UI プロトコルを使って、エージェントからリッチで構造化された UI を生成します
catalog_icon: /integrations/assets/a2ui.svg
---

# ADK 向け A2UI - Agent-to-UI

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

A2UI を使うと、エージェントはテキストだけでなく、カード、フォーム、チャート、テーブルなどの **実際の UI** を生成できます。
エージェントは構造化された JSON を出力し、クライアント側のレンダラーがそれをインタラクティブなコンポーネントに変換します。

転送方式に依存しないのも特徴です。A2UI のペイロードは A2A、MCP、REST、WebSocket、その他の任意のプロトコル上で動作します。
エージェントは *何を* 表示するかを記述し、クライアントが *どのように* レンダリングするかを決定します。

!!! info "A2UI について詳しく知る"
    [a2ui.org](https://a2ui.org/) には、完全な仕様、コンポーネントギャラリー、カタログリファレンス、レンダラードキュメントがあります。

## クイックスタート

### SDK のインストール

```bash
pip install a2ui-agent-sdk
```

### 1. Schema Manager を設定する

`A2uiSchemaManager` はコンポーネントカタログを読み込み、LLM が有効な A2UI JSON を生成できるようにするシステムプロンプトを作成します。

```python
from a2ui.core.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

schema_manager = A2uiSchemaManager(
    catalogs=[
        BasicCatalog.get_config(
            examples_path="examples",
        ),
    ],
)
```

!!! note
    Schema manager は、受信したクライアントリクエストから A2UI のバージョンを自動的に検出します。
    必要であれば `version=VERSION_0_9` を渡して、バージョンを明示的に指定することもできます。

!!! tip
    `catalogs` パラメータを省略すると、Schema manager は A2UI チームが管理する
    [Basic Catalog](https://a2ui.org/latest/catalogs/) を使用します。
    このカタログには、Text、Card、Button、Image などの一般的なコンポーネントが含まれています。
    [カスタムカタログ](#custom-catalogs) を作成してドメイン固有のコンポーネントを追加したり、
    基本カタログと独自のカタログを組み合わせたりすることもできます。
    詳細は下の [高度なパターン](#advanced-patterns) を参照してください。

### 2. システムプロンプトを生成する

`generate_system_prompt` メソッドは、エージェントの役割説明と A2UI JSON スキーマ、few-shot 例を組み合わせるため、
LLM は出力形式を正確に把握できます。

```python
instruction = schema_manager.generate_system_prompt(
    role_description="You are a helpful assistant that presents information with rich UI.",
    workflow_description="Analyze the user's request and return structured UI when appropriate.",
    ui_description="Use cards for summaries, tables for comparisons, and forms for user input.",
    include_schema=True,
    include_examples=True,
    allowed_components=["Heading", "Text", "Card", "Button", "Table"],
)
```

### 3. ADK エージェントを作成する

生成した指示をエージェントの system prompt として使います:

```python
from google.adk.agents.llm_agent import LlmAgent

agent = LlmAgent(
    model="gemini-flash-latest",
    name="ui_agent",
    description="An agent that generates rich UI responses.",
    instruction=instruction,
)
```

### 4. A2UI 出力を検証してストリームする

クライアントに送信する前に、LLM の JSON 出力は必ず検証してください。
SDK には、パース、修正、検証のユーティリティがあります:

```python
from a2ui.core.parser.parser import parse_response
from a2ui.a2a import parse_response_to_parts

# 有効なカタログの validator を取得します
selected_catalog = schema_manager.get_selected_catalog()

# Option A: 手動でパース + 検証
response_parts = parse_response(llm_output_text)
for part in response_parts:
    if part.a2ui_json:
        selected_catalog.validator.validate(part.a2ui_json)

# Option B: A2A Parts を返す 1 行版
parts = parse_response_to_parts(
    llm_output_text,
    validator=selected_catalog.validator,
    fallback_text="見つかった内容はこちらです。",
)
```

A2UI のペイロードは、レンダラーが識別できるよう MIME タイプ `application/json+a2ui` の
A2A `DataPart` にラップされます:

```python
from a2ui.a2a import create_a2ui_part

part = create_a2ui_part({"type": "Card", "props": {"title": "Hello"}})
# → DataPart(data={...}, metadata={"mimeType": "application/json+a2ui"})
```

## 高度なパターン

### 動的カタログ

文脈によって異なる UI コンポーネントが必要なエージェント(たとえば、データ問い合わせ用のチャートや設定用フォーム)では、
ランタイムでカタログを解決してセッション状態に保存します:

```python
async def _prepare_session(self, context, run_request, runner):
    session = await super()._prepare_session(context, run_request, runner)

    # リクエストのメタデータからクライアント機能を判定します
    capabilities = context.message.metadata.get("a2ui_client_capabilities")

    # 適切なカタログを選択します
    a2ui_catalog = self.schema_manager.get_selected_catalog(
        client_ui_capabilities=capabilities
    )
    examples = self.schema_manager.load_examples(a2ui_catalog, validate=True)

    # ツールから参照できるようセッション状態に保存します
    await runner.session_service.append_event(
        session,
        Event(
            actions=EventActions(
                state_delta={
                    "system:a2ui_enabled": True,
                    "system:a2ui_catalog": a2ui_catalog,
                    "system:a2ui_examples": examples,
                }
            ),
        ),
    )
    return session
```

### カスタムカタログ

ドメイン固有の UI 向けに、独自のコンポーネントカタログを定義できます:

```python
from a2ui.core.schema.manager import CatalogConfig

schema_manager = A2uiSchemaManager(
    catalogs=[
        BasicCatalog.get_config(),
        CatalogConfig.from_path(
            name="my_dashboard_catalog",
            catalog_path="catalogs/dashboard.json",
            examples_path="catalogs/dashboard_examples",
        ),
    ],
)
```

### マルチエージェントオーケストレーション

オーケストレーターエージェントは、サブエージェントの A2UI 機能を集約して AgentCard に公開できます:

```python
from a2ui.a2a import get_a2ui_agent_extension

# サブエージェントからカタログ ID を収集します
supported_catalog_ids = set()
for subagent in subagents:
    for extension in subagent_card.capabilities.extensions:
        if extension.uri == "https://a2ui.org/a2a-extension/a2ui/v0.9":
            supported_catalog_ids.update(
                extension.params.get("supportedCatalogIds") or []
            )

# オーケストレーターの AgentCard に公開します
agent_card = AgentCard(
    capabilities=AgentCapabilities(
        extensions=[
            get_a2ui_agent_extension(
                supported_catalog_ids=list(supported_catalog_ids),
            )
        ]
    )
)
```

## サンプル

A2UI リポジトリには、すぐに実行できる ADK サンプルエージェントが含まれています:

| サンプル | 説明 |
|---|---|
| [contact_lookup](https://github.com/google/A2UI/tree/main/samples/agent/adk/contact_lookup) | 静的スキーマを使うシンプルなエージェントです。連絡先を検索し、結果をカードとして表示します |
| [restaurant_finder](https://github.com/google/A2UI/tree/main/samples/agent/adk/restaurant_finder) | レストラン情報を検索して表示する静的スキーマエージェントです |
| [rizzcharts](https://github.com/google/A2UI/tree/main/samples/agent/adk/rizzcharts) | 文脈に応じてチャートコンポーネントを選択する動的カタログエージェントです |
| [orchestrator](https://github.com/google/A2UI/tree/main/samples/agent/adk/orchestrator) | サブエージェントに処理を委譲し、UI 機能を集約するマルチエージェント構成です |

## リソース

- [A2UI 仕様](https://a2ui.org/)
- [A2UI GitHub リポジトリ](https://github.com/google/A2UI)
- [A2UI Python SDK (`a2ui-agent-sdk`)](https://pypi.org/project/a2ui-agent-sdk/)
- [エージェント開発ガイド](https://github.com/google/A2UI/blob/main/agent_sdks/python/agent_development.md)
- [コンポーネントギャラリー](https://a2ui.org/latest/reference/components/)
- [A2A プロトコル](https://google.github.io/A2A/)
