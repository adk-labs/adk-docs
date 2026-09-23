---
catalog_title: Model Armor
catalog_description: Google Cloud セキュリティテンプレートに照らしてエージェントの入力と出力をスクリーニング
catalog_icon: /integrations/assets/model-armor.png
catalog_tags: ["google"]
---

# ADK 向け Model Armor プラグイン

<div class="language-support-tag">
  <span class="lst-supported">ADK サポート</span><span class="lst-python">Python v2.8.0</span>
</div>

[Model Armor](https://cloud.google.com/security-command-center/docs/model-armor-overview) は、プロンプトインジェクションやジェイルブレイクの試行、有害なコンテンツ、機密データを検出するためにテキストを検査する Google Cloud サービスです。テンプレートと呼ばれるサーバー側ポリシーで検出対象を定義すると、サービスは送信された各テキストに対して判定結果を返します。`ModelArmorPlugin` クラスは ADK に付属しており、モデルコールバックからそのサービスを呼び出します。モデルが認識する前にユーザー入力をスクリーニングし、配信前または配信中にモデル出力をスクリーニングして、一致したコンテンツを安全なメッセージに置き換えます。

## ユースケース

- **プロンプトインジェクションとジェイルブレイクの防御**: モデルが処理する前にすべてのユーザーターンをプロンプトテンプレートに照らしてスクリーニングするため、検出された試行に対してエージェントが従う代わりにブロックされます。
- **機密データと有害コンテンツのフィルタリング**: モデル出力を応答テンプレートに照らしてスクリーニングし、配信前にデータ漏洩やコンテンツポリシー違反を起こす回答を捕捉します。
- **エージェント間での統一されたポリシー**: `App` に 1 つのプラグインを登録すると、[ライブ音声エージェント](../live/guardrails.md) を含む実行対象のすべてのエージェントが同じスクリーニングを継承します。

## 前提条件

- Model Armor API が有効化され、少なくとも 1 つのテンプレートが作成された Google Cloud プロジェクト。[Model Armor のドキュメント](https://cloud.google.com/security-command-center/docs/manage-model-armor-templates) を参照してください。
- `gcloud auth application-default login` で設定された、Model Armor へのアクセス権を持つアプリケーションデフォルト認証情報（ADC）。
- [ADK](https://adk.dev) >= 2.8.0

## インストール

```bash
pip install 'google-adk[gcp]'
```

個別の `model-armor` エクストラはありません。プラグインは ADK に付属しており、`gcp` エクストラが必要な `google-cloud-modelarmor` クライアントを提供します。

## エージェントでの使用

スクリーニング対象のテンプレートを指定して、`App` にプラグインを登録します:

```python
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.integrations.model_armor import ModelArmorConfig
from google.adk.integrations.model_armor import ModelArmorPlugin

agent = LlmAgent(
    model="gemini-flash-latest",
    name="screened_agent",
    instruction="You are a helpful assistant.",
)

app = App(
    name="model_armor_demo",
    root_agent=agent,
    plugins=[
        ModelArmorPlugin(
            config=ModelArmorConfig(
                prompt_template_name=(
                    "projects/my-project/locations/us-central1/templates/my-prompt-template"
                ),
                response_template_name=(
                    "projects/my-project/locations/us-central1/templates/my-response-template"
                ),
            )
        )
    ],
)
```

テンプレート名は、`projects/{project}/locations/{location}/templates/{template}` 形式の完全なリソースパスである必要があります。プラグインはパスからロケーションを読み取ってリージョンエンドポイントを選択するため、両方のテンプレートが同じリージョンに存在する必要があります。プラグインの構築時に短い名前や一致しないペアを指定すると、`ValueError` が発生します。

各テンプレートは任意であり、一方のみを設定した場合はその方向のみがスクリーニングされます:

```python
config = ModelArmorConfig(
    prompt_template_name=(
        "projects/my-project/locations/us-central1/templates/my-prompt-template"
    ),
)
```

スクリーニングは最新のユーザーコンテンツとモデルの返答を対象とします。ツールの結果は `function_response` パーツとしてリクエストに到達しますが、プラグインはこれをスキップします。

## 構成

| オプション | デフォルト値 | 説明 |
| :--- | :--- | :--- |
| `prompt_template_name` | `None` | ユーザー入力のスクリーニングに使用されるテンプレート。未設定の場合、入力はスクリーニングされません。 |
| `response_template_name` | `None` | モデル出力のスクリーニングに使用されるテンプレート。未設定の場合、出力はスクリーニングされません。 |
| `input_blocked_message` | 下記参照 | ユーザー入力がブロックされたときに表示される代替テキスト。 |
| `output_blocked_message` | 下記参照 | モデル出力がブロックされたときに表示される代替テキスト。 |
| `block_on_screening_failure` | `True` | スクリーニングできなかったコンテンツをブロックするかどうか。 |

両方のメッセージのデフォルト値は `"I'm sorry, but I can't help with that request."` です。設定で少なくとも 1 つのテンプレート名を指定する必要があり、指定しない場合はバリデーションエラーが発生します。

Model Armor 呼び出しで例外が発生した場合、またはサービスが `SUCCESS` 以外の判定を返した場合、スクリーニングは失敗します。デフォルトでは、スクリーニングされていないコンテンツがブロックされます。Model Armor が利用できない間もエージェントの応答を維持したい場合は、`block_on_screening_failure=False` を設定してください。

ブロックされたターンには `custom_metadata['model_armor_blocked']` が設定されるため、アプリケーションはポリシーによるブロックと通常の応答を区別できます。

## 追加リソース

- [Model Armor の概要](https://cloud.google.com/security-command-center/docs/model-armor-overview)
- [テンプレートの作成と管理](https://cloud.google.com/security-command-center/docs/manage-model-armor-templates)
- [プラグイン](../plugins/index.md)
- [安全性とセキュリティ](../safety/index.md)
- [ライブエージェントのガードレール](../live/guardrails.md)
