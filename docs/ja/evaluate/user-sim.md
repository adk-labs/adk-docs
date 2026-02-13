# ユーザーシミュレーション

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.18.0</span>
</div>

会話型エージェントを評価する場合、会話が予期しない方向に進む可能性があるため、固定されたユーザープロンプトのセットを使用することは必ずしも実用的ではありません。たとえば、エージェントがタスクを実行するためにユーザーに2つの値を指定する必要がある場合、それらの値を一度に1つずつ、または一度に両方要求する場合があります。この問題を解決するために、ADKは生成AIモデルを使用してユーザープロンプトを動的に生成できます。

この機能を使用するには、エージェントとの会話におけるユーザーの目標を指示する[`ConversationScenario`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/conversation_scenarios.py)を指定する必要があります。[`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world)エージェントのサンプル会話シナリオを以下に示します。

```json
{
  "starting_prompt": "何ができますか？",
  "conversation_plan": "エージェントに20面ダイスを振るように依頼します。結果が出たら、それが素数かどうかを確認するようにエージェントに依頼します。"
}
```

会話シナリオの`starting_prompt`は、ユーザーがエージェントとの会話を開始するために使用する必要がある固定の初期プロンプトを指定します。エージェントがさまざまな方法で応答する可能性があるため、エージェントとの後続の対話にこのような固定プロンプトを指定することは実用的ではありません。代わりに、`conversation_plan`は、エージェントとの残りの会話がどのように進むべきかについてのガイドラインを提供します。LLMは、この会話計画を会話履歴とともに使用して、会話が完了したと判断するまでユーザープロンプトを動的に生成します。

!!! tip "Colabで試す"

    [ADKエージェントを動的に評価するためのユーザー会話のシミュレーション](https://github.com/google/adk-samples/blob/main/python/notebooks/evaluation/user_simulation_in_adk_evals.ipynb)に関するインタラクティブなノートブックで、このワークフロー全体を自分でテストしてください。会話シナリオを定義し、「ドライラン」を実行してダイアログを確認し、完全な評価を実行してエージェントの応答を採点します。

## 例：会話シナリオを使用した[`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world)エージェントの評価

会話シナリオを含む評価ケースを新規または既存の[`EvalSet`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py)に追加するには、まずエージェントをテストする会話シナリオのリストを作成する必要があります。

以下を`contributing/samples/hello_world/conversation_scenarios.json`に保存してみてください。

```json
{
  "scenarios": [
    {
      "starting_prompt": "何ができますか？",
      "conversation_plan": "エージェントに20面ダイスを振るように依頼します。結果が出たら、それが素数かどうかを確認するようにエージェントに依頼します。"
    },
    {
      "starting_prompt": "こんにちは、素数が悪い卓上RPGを実行しています！",
      "conversation_plan": "値は気にしないと言い、エージェントにロールが良いか悪いかを教えてもらうように依頼します。エージェントが同意したら、6面ダイスを振るように依頼します。最後に、エージェントに2つの20面ダイスで同じことをするように依頼します。"
    }
  ]
}
```

評価中に使用される情報を含むセッション入力ファイルも必要になります。以下を`contributing/samples/hello_world/session_input.json`に保存してみてください。

```json
{
  "app_name": "hello_world",
  "user_id": "user"
}
```

次に、会話シナリオを`EvalSet`に追加できます。

```bash
# （オプション）新しいEvalSetを作成します
adk eval_set create \
  contributing/samples/hello_world \
  eval_set_with_scenarios

# 会話シナリオを新しい評価ケースとしてEvalSetに追加します
adk eval_set add_eval_case \
  contributing/samples/hello_world \
  eval_set_with_scenarios \
  --scenarios_file contributing/samples/hello_world/conversation_scenarios.json \
  --session_input_file contributing/samples/hello_world/session_input.json
```

デフォルトでは、ADKはエージェントの期待される応答を指定する必要があるメトリックで評価を実行します。動的な会話シナリオの場合はそうではないため、いくつかの代替サポートされているメトリックを持つ[`EvalConfig`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py)を使用します。

以下を`contributing/samples/hello_world/eval_config.json`に保存してみてください。

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

最後に、`adk eval`コマンドを使用して評価を実行できます。

```bash
adk eval \
    contributing/samples/hello_world \
    --config_file_path contributing/samples/hello_world/eval_config.json \
    eval_set_with_scenarios \
    --print_detailed_results
```

## ユーザーシミュレーターの構成

デフォルトのユーザーシミュレーター構成を上書きして、モデル、内部モデルの動作、および最大ユーザーエージェントインタラクション数を変更できます。以下の`EvalConfig`は、デフォルトのユーザーシミュレーター構成を示しています。

```json
{
  "criteria": {
    # 以前と同じ
  },
  "user_simulator_config": {
    "model": "gemini-1.5-flash",
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

* `model`：ユーザーシミュレーターを支えるモデル。
* `model_configuration`：モデルの動作を制御する[`GenerateContentConfig`](https://github.com/googleapis/python-genai/blob/6196b1b4251007e33661bb5d7dc27bafee3feefe/google/genai/types.py#L4295)。
* `max_allowed_invocations`：会話が強制的に終了される前に許可される最大ユーザーエージェントインタラクション数。これは、`EvalSet`で最も長い妥当なユーザーエージェントインタラクションよりも大きく設定する必要があります。
* `custom_instructions`：任意。ユーザーシミュレーターのデフォルト指示を上書きします。指示文字列には、以下のプレースホルダーを*事前に値へ置換せずにそのまま*含める必要があります。
    * `{stop_signal}`：ユーザーシミュレーターが会話終了と判断したときに生成するテキスト
    * `{conversation_plan}`：ユーザーシミュレーターが従うべき会話全体の計画
    * `{conversation_history}`：ここまでのユーザーとエージェントの会話履歴
