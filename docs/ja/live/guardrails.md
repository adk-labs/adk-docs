# ライブエージェント向けガードレール

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.8.0</span>
</div>

ガードレールは、本番環境においてライブ音声エージェントがどのように動作するかを制御し、会話をトピック内（on-topic）かつポリシーに準拠（on-policy）した安全な（safe）状態に保ちます。ライブ接続では音声が継続的にストリーミングされ、モデルはリアルタイムで発話を開始します。ADKは、会話のレイテンシへの影響を最小限に抑えながら会話を保護するために連携する、多層防御の保護機能を提供します。

一般的なコールバックの仕組みとプラグインの登録方法については、[コールバックの種類](../callbacks/types-of-callbacks.md)および[プラグイン](../plugins/index.md)をご覧ください。

## ガードレールのレイヤー

| レイヤー | 役割 | 保護の焦点 | レイテンシへの影響 |
| :--- | :--- | :--- | :--- |
| システム指示（System instructions） | トーン、会話ルール、境界を形成 | 動作ガイダンス | アプリケーションの追加レイテンシなし |
| セーフティ設定（Safety settings） | コンテンツの安全性に関するプラットフォームのしきい値を適用 | プラットフォームセーフティフィルタ | アプリケーションの追加レイテンシなし |
| 入力検証（Input validation） | プロンプトインジェクションや禁止されたトピックを検出 | ユーザー入力の検証 | 最小限（ターンごとに実行） |
| レスポンス検証（Response validation） | ビジネスポリシーに基づいてエージェントのレスポンスをスクリーニング | エージェントレスポンスの検証 | チェック内容に依存 |
| ツールガードレール（Tool guardrails） | ツールの実行をインターセプトしパラメータを検証 | ツール実行の安全性 | 最小限（ツール呼び出しごとに実行） |

これらのレイヤーが連携して多層防御（defense in depth）を提供します。システム指示は自然な会話の流れを形成し、プラットフォームのセーフティフィルタは基本的な有害性の境界を適用し、アプリケーションのバリデータは入力、レスポンス、ツール呼び出しを個別に検証します。明確な指示と独立した検証を組み合わせることで、エッジケースが1つのレイヤーをすり抜けた場合でも、別のレイヤーで確実に捕捉できます。

## 指示とセーフティ設定

指示とセーフティ設定は、セッション全体のベースラインとなる動作を確立します。どちらの設定もエージェントに属し、セッション作成時に設定します。

```python
from google.adk.agents import Agent
from google.genai import types

root_agent = Agent(
    model='gemini-live-2.5-flash-native-audio',
    name='support_agent',
    instruction=(
        'You help customers with billing questions. '
        'Never quote a price; offer to transfer to sales instead. '
        'Never discuss a competitor.'
    ),
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
        ]
    ),
)
```

モデルは、会話のコンテキストが蓄積されるにつれて、ターンごとにシステム指示を評価します。ライブエージェント向けの指示を設計する際は、ペルソナ、会話ルール、会話ガードレールの順に定義してください。厳格な制約を設ける場合は、代替案の提示やオペレーターへの転送など、境界に達した際の明示的な対応ルールを指定してください。

セーフティ設定は、ライブセッションに[セーフティフィルタとコンテンツフィルタ](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/configure-safety-filters)を適用します。モデルが設定されたしきい値を超えるコンテンツを生成した場合、プラットフォームは生成を中止します。

ライブ接続は起動時にこれらの設定を確立するため、セッション期間中は固定されたままになります。セッション状態を挿入（interpolate）する指示文字列は、セッション開始時に1回レンダリングされ、再開された接続ではそのレンダリングされた指示が再利用されます。

## 会話の検証

会話の検証では、ユーザーの発言とエージェントの応答を個別に評価します。マネージドエンタープライズポリシーの場合、[Model Armor プラグイン](../integrations/model-armor.md)が Google Cloud テンプレートに基づいてプロンプトインジェクション、機密データ、ポリシー違反をスクリーニングします。ADKのモデルコールバックを使用してカスタム検証を実装することも可能です。

### ユーザー入力の検証

`before_model_callback` フックはユーザー入力をインターセプトします。このコールバックはテキスト入力がモデルに到達する前に評価するため、ブロックしても接続を維持したまま、メッセージがコンテキストに入るのを防ぎます。音声の場合、コールバックはモデルがすでに音声を受信した後にのみ、文字起こしされた発話全体を検査します。そこでブロックが発生した場合、ライブセッションを再起動して送信中の応答を破棄します。

チェックによりポリシー違反が検出された場合、`LlmResponse` を返すことでユーザーのターンを安全なフォールバックレスポンスに置き換えます。

```python
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types


def block_input(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
  """競合他社について言及するユーザーターンをブロックします。"""
  text = ''.join(
      part.text or ''
      for content in llm_request.contents
      for part in content.parts or []
  )

  if 'competitor' not in text.lower():
    return None

  return LlmResponse(
      content=types.Content(
          role='model',
          parts=[types.Part(text="I can't discuss that.")],
      )
  )
```

### エージェントレスポンスの検証

`after_model_callback` フックは、ユーザーへの配信前または配信中にモデルのレスポンスを検証します。検証では、音声ターン中に蓄積される文字起こしを検査して違反を早期に検出することも、ターン全体の文字起こしを評価することもできます。

```python
def block_output(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
  """回答で価格が提示された場合にレスポンスを置き換えます。"""
  transcription = llm_response.output_transcription
  text = transcription.text if transcription else ''

  if '$' not in text:
    return None

  return LlmResponse(
      content=types.Content(
          role='model',
          parts=[types.Part(text='Let me connect you with sales.')],
      )
  )
```

出力コールバックから `LlmResponse` を返すと、モデルの生成が直ちに停止し、代替メッセージがユーザーに配信されます。モデルが既に入力の処理を開始している音声ターンの場合、拒否されたコンテンツが会話コンテキストに残らないよう、ADKは現在のターンをクリアします。

## ツールガードレール

ツールコールバックは外部システムを保護し、アクションを検証します。`before_tool_callback` フックはツールが実行される前に引数を検査し、不正なパラメータを拒否したりビジネスロジックを適用したりできます。`after_tool_callback` フックは、結果がモデルに返される前に機密情報をマスキング（redact）します。

```python
from typing import Any, Optional

from google.adk.tools import BaseTool
from google.adk.tools import ToolContext


def validate_refund(
    tool: BaseTool,
    args: dict[str, Any],
    tool_context: ToolContext,
) -> Optional[dict[str, Any]]:
  """しきい値を超える不正な返金を防止します。"""
  if tool.name == 'issue_refund' and args.get('amount', 0) > 100:
    return {'error': 'Refund exceeds automatic approval limit.'}
  return None
```

ツールコールバックから結果を返すと、ツールの実行がバイパスされ、戻り値がモデルに直接提供されます。詳しくは[ツール実行コールバック](../callbacks/types-of-callbacks.md#tool-execution-callbacks)をご覧ください。

ライブ音声ストリームは、インタラクティブな人間による確認を待つために一時停止することはできません。ライブエージェントが高い権限を必要とするツールを使用する場合は、コールバック内で自動的に引数を検証するか、人間のオペレーターへのハンドオフにルーティングしてください。

## 要件とベストプラクティス

- **文字起こしが有効であることを確認する**: テキストベースの会話検証は音声の文字起こしに依存しています。`RunConfig.input_audio_transcription` と `RunConfig.output_audio_transcription` は両方ともデフォルトで有効になっています。いずれかを `None` に設定すると、対応するスクリーニングレイヤーが無効になります。
- **バリデータを軽量に保つ**: ライブ受信ループ内のコールバックは、音声処理とインラインで実行されます。高速なローカルチェックにより、会話の応答性を維持できます。より負荷の高いチェックを行う場合は、ターン全体の文字起こしを評価するか、時間のかかる分析を非同期でオフロードしてください。
- **エージェント全体にポリシーを適用する**: `App` に [Model Armor](../integrations/model-armor.md) などのプラグインを登録すると、コールバックコードを重複させることなく、アプリケーション内のすべてのエージェントに一貫したセキュリティルールが適用されます。

## 関連リソース

- [Model Armor プラグイン](../integrations/model-armor.md)
- [コールバックの種類](../callbacks/types-of-callbacks.md)
- [プラグイン](../plugins/index.md)
- [セーフティフィルタの構成](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/configure-safety-filters)
