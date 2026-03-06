# ユーザーシミュレーション

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.18.0</span>
</div>

会話型エージェントを評価する際、会話は予期しない方向に進むことがあるため、
固定のユーザープロンプト集合を使うのが常に実用的とは限りません。
たとえば、エージェントがタスクを実行するためにユーザーから2つの値を受け取る必要がある場合、
それらを1つずつ尋ねることもあれば、まとめて尋ねることもあります。
この問題を解決するために、ADK は生成 AI モデルを使って
ユーザープロンプトを動的に生成できます。

この機能を使用するには、エージェントとの会話におけるユーザーの目標を定義する
[`ConversationScenario`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/conversation_scenarios.py)
を指定する必要があります。さらに、ユーザーが従うことを期待する
ユーザーペルソナを指定することもできます。

`ConversationScenario` は次の構成要素から成ります。

*   `starting_prompt`: ユーザーがエージェントとの会話を始めるときに使う固定の初期プロンプト
*   `conversation_plan`: ユーザーが達成すべき目標に関する高レベルのガイドライン
*   `user_persona`: 技術的な熟練度や言語スタイルなど、ユーザー特性の定義

[`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world)
エージェントの会話シナリオ例を以下に示します。

```json
{
  "starting_prompt": "何ができますか？",
  "conversation_plan": "エージェントに20面ダイスを振るよう依頼します。結果を受け取ったら、その数が素数かどうかを確認するよう依頼します。"
}
```

LLM は `conversation_plan` と会話履歴を組み合わせて、
ユーザープロンプトを動的に生成します。

次のように、あらかじめ用意された `user_persona` を指定することもできます。

```json
{
  "starting_prompt": "何ができますか？",
  "conversation_plan": "エージェントに20面ダイスを振るよう依頼します。結果を受け取ったら、その数が素数かどうかを確認するよう依頼します。",
  "user_persona": "NOVICE"
}
```

会話プランが何を達成すべきかを定めるのに対し、ペルソナはモデルがどのように質問を表現し、エージェントの応答にどう反応するかを定めます。

!!! tip "Colabで試す"

    [ADK エージェントを動的に評価するためのユーザー会話シミュレーション](https://github.com/google/adk-samples/blob/main/python/notebooks/evaluation/user_simulation_in_adk_evals.ipynb)
    のインタラクティブノートブックで、このワークフロー全体を自分で試せます。
    会話シナリオを定義し、対話を確認するための「ドライラン」を実行したあと、
    完全な評価を行ってエージェントの応答を採点します。

## ユーザーペルソナ

User Persona は、シミュレートされたユーザーが会話中に採用する役割です。
これは、コミュニケーションのスタイル、情報の提供方法、
エラーへの反応の仕方など、ユーザーがエージェントとどう相互作用するかを定める
**behaviors** の集合として定義されます。

`UserPersona` は次のフィールドで構成されます。

*   `id`: ペルソナの一意な識別子
*   `description`: そのユーザーがどのような人物で、エージェントとどう相互作用するかの高レベル説明
*   `behaviors`: 具体的な特性を定義する `UserBehavior` オブジェクトのリスト

各 `UserBehavior` には次が含まれます。

*   `name`: 行動の名前
*   `description`: 期待される行動の要約
*   `behavior_instructions`: シミュレートされたユーザー（LLM）に対して、どう振る舞うべきかを示す具体的な指示
*   `violation_rubrics`: 評価器が、この行動にユーザーが従っているかを判断するために使う基準です。これらの rubric の **いずれか** が満たされた場合、評価器はその行動が **守られていない** と判断すべきです。

## 組み込みペルソナ

ADK には、一般的な行動を組み合わせた事前定義ペルソナのセットが用意されています。
以下の表は各ペルソナの行動を要約したものです。

| 行動 | **EXPERT** ペルソナ | **NOVICE** ペルソナ | **EVALUATOR** ペルソナ |
| :--- | :--- | :--- | :--- |
| **Advance** | 詳細志向（積極的に詳細を提供する） | 目標志向（詳細は尋ねられるまで待つ） | 詳細志向 |
| **Answer** | 関連する質問にのみ答える | すべての質問に答える | 関連する質問にのみ答える |
| **Correct Agent Inaccuracies** | はい | いいえ | いいえ |
| **Troubleshoot Agent Errors** | 1回は試す | 決して試さない | 決して試さない |
| **Tone** | プロフェッショナル | 会話調 | 会話調 |

## 例: 会話シナリオを用いて [`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) エージェントを評価する

会話シナリオを含む評価ケースを新規または既存の
[`EvalSet`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py)
に追加するには、まずエージェントをテストする会話シナリオのリストを作成する必要があります。

以下を `contributing/samples/hello_world/conversation_scenarios.json` に保存してみてください。

```json
{
  "scenarios": [
    {
      "starting_prompt": "何ができますか？",
      "conversation_plan": "エージェントに20面ダイスを振るよう依頼します。結果を受け取ったら、その数が素数かどうかを確認するよう依頼します。",
      "user_persona": "NOVICE"
    },
    {
      "starting_prompt": "こんにちは、素数が悪い数字として扱われるテーブルトークRPGを遊んでいます！",
      "conversation_plan": "値自体は気にしておらず、その出目が良いか悪いかだけ教えてほしいと伝えます。エージェントが同意したら、6面ダイスを振るよう依頼します。最後に、20面ダイス2個でも同じことをするよう依頼します。",
      "user_persona": "EXPERT"
    }
  ]
}
```

評価時に使用する情報を含むセッション入力ファイルも必要です。
以下を `contributing/samples/hello_world/session_input.json` に保存してみてください。

```json
{
  "app_name": "hello_world",
  "user_id": "user"
}
```

その後、会話シナリオを `EvalSet` に追加できます。

```bash
# （任意）新しい EvalSet を作成
adk eval_set create \
  contributing/samples/hello_world \
  eval_set_with_scenarios

# 会話シナリオを新しい評価ケースとして EvalSet に追加
adk eval_set add_eval_case \
  contributing/samples/hello_world \
  eval_set_with_scenarios \
  --scenarios_file contributing/samples/hello_world/conversation_scenarios.json \
  --session_input_file contributing/samples/hello_world/session_input.json
```

ADK はデフォルトで、エージェントの期待応答を指定する必要があるメトリクスで評価を実行します。
しかし動的な会話シナリオでは、そのような期待応答を事前に定義できないため、
代わりにいくつかの代替サポートメトリクスを含む
[`EvalConfig`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py)
を使用します。

以下を `contributing/samples/hello_world/eval_config.json` に保存してみてください。

```json
{
  "criteria": {
    "hallucinations_v1": {
      "threshold": 0.5,
      "evaluate_intermediate_nl_responses": true
    },
    "safety_v1": {
      "threshold": 0.8
    }
  }
}
```

最後に、`adk eval` コマンドを使って評価を実行できます。

```bash
adk eval \
    contributing/samples/hello_world \
    --config_file_path contributing/samples/hello_world/eval_config.json \
    eval_set_with_scenarios \
    --print_detailed_results
```

## ユーザーシミュレーターの構成

デフォルトのユーザーシミュレーター構成を上書きして、
モデル、内部モデルの振る舞い、最大のユーザー-エージェント対話回数を変更できます。
以下の `EvalConfig` は、デフォルトのユーザーシミュレーター構成を示します。

```json
{
  "criteria": {
    # 以前と同じ
  },
  "user_simulator_config": {
    "model": "gemini-2.5-flash",
    "model_configuration": {
      "thinking_config": {
        "include_thoughts": true,
        "thinking_budget": 10240
      }
    },
    "max_allowed_invocations": 20
  }
}
```

*   `model`: ユーザーシミュレーターを支えるモデル
*   `model_configuration`: モデルの振る舞いを制御する
    [`GenerateContentConfig`](https://github.com/googleapis/python-genai/blob/6196b1b4251007e33661bb5d7dc27bafee3feefe/google/genai/types.py#L4295)
*   `max_allowed_invocations`: 会話が強制終了されるまでに許可される最大ユーザー-エージェント対話回数です。これは `EvalSet` 内で最も長い妥当なユーザー-エージェント対話より大きく設定する必要があります。
*   `custom_instructions`: 任意。ユーザーシミュレーターのデフォルト指示を上書きします。指示文字列には
    [Jinja](https://jinja.palletsprojects.com/en/stable/templates/#) 構文を使って次のプレースホルダーを含める必要があります
    （*値は事前に置換しないでください*）。
    *   `{{ stop_signal }}`: ユーザーシミュレーターが会話終了と判断した際に生成するテキスト
    *   `{{ conversation_plan }}`: ユーザーシミュレーターが従うべき会話全体の計画
    *   `{{ conversation_history }}`: これまでのユーザーとエージェントの会話履歴
    *   `{{ persona }}`: `UserPersona` オブジェクトにもアクセスできるプレースホルダー

## カスタムペルソナ

`ConversationScenario` に `UserPersona` オブジェクトを与えることで、
独自のカスタムペルソナを定義できます。

カスタムペルソナ定義の例:

```json
{
  "starting_prompt": "アカウントについて助けてほしいです。",
  "conversation_plan": "エージェントにパスワードのリセットを依頼します。",
  "user_persona": {
    "id": "IMPATIENT_USER",
    "description": "急いでいて、すぐに苛立つユーザーです。",
    "behaviors": [
      {
        "name": "短い応答",
        "description": "ユーザーは非常に短く、時には不完全な応答を返すべきです。",
        "behavior_instructions": [
            "応答は10語以内に保ってください。",
            "丁寧な表現は省いてください。"
        ],
        "violation_rubrics": [
            "ユーザーの応答が10語を超えている。",
            "ユーザーの応答が過度に丁寧である。"
        ]
      }
    ]
  }
}
```
