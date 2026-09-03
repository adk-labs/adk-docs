# ライブエージェントの評価

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.6.0</span>
</div>

ライブエージェントは、実際に使用されるのと同じ方法で評価できます。シミュレートされたユーザーが音声で発話し、エージェントは実際の双方向セッションを通じて応答し、その応答内容を評価スコアリングします。評価セット、評価基準、および `adk eval` ループは、[エージェントの評価](../evaluate/index.md) で解説されているテキストエージェント向けのものと同じです。

## 音声によるエージェントの駆動

`llm_audio` ユーザーシミュレーターは、Text-to-Speech（TTS）モデルを使用してシミュレートされたユーザーの各ターンを合成し、エージェントに音声としてストリーミングします。これにより、ユーザーが通るパス（音声入力、音声活動検出（VAD）、ターン交代、音声出力、文字起こし）がエンドツーエンドで実行されます。音声エージェントにテキストを入力すると、これらすべてがスキップされてしまいます。

```json
{
  "user_simulator_config": {
    "type": "llm_audio",
    "model": "gemini-3.7-flash",
    "max_allowed_invocations": 10,
    "audio_model": "gemini-3.1-flash-tts-preview",
    "audio_model_configuration": {
      "response_modalities": ["AUDIO"],
      "speech_config": {
        "voice_config": {
          "prebuilt_voice_config": { "voice_name": "Kore" }
        },
        "language_code": "en-US"
      }
    }
  }
}
```

ここでは 2 つのモデルが異なる役割を果たします。`model` はシミュレートされたユーザーが次に言うべき内容を決定し、`audio_model` はそれを音声に変換します。`voice_name` と `language_code` を変更することで、さまざまな声やアクセントに対してエージェントをテストできます。これは、テキスト評価では検出できない回帰（リグレッション）を捉えるのに有効です。

既存の評価ケースはそのまま維持されます。同じ会話シナリオや固定された会話を使用してテキスト実行と音声実行の両方を駆動できるため、既存のスイートを再利用できます。完全なスキーマ、ペルソナ、およびシナリオの作成方法については、[オーディオユーザーシミュレーション](../evaluate/user-sim.md#audio-user-simulation-live-agents) を参照してください。

## ルーブリックによるスコアリング

発話による返答は何通りもの異なる言い回しで正解となり得るため、参照文字列と単純比較する基準では正しい回答でも不合格となってしまいます。ルーブリックに基づく審査（Judge）を使用すると、自然言語で意図を一度記述するだけで、スイート内のすべての会話に適用できます。

| 評価基準 | 評価対象 |
|---|---|
| [`rubric_based_final_response_quality_v1`](../evaluate/criteria.md#rubric_based_final_response_quality_v1) | 単一ターンの返答 |
| [`rubric_based_tool_use_quality_v1`](../evaluate/criteria.md#rubric_based_tool_use_quality_v1) | ツールが正しく呼び出されたかどうか |
| [`rubric_based_multi_turn_trajectory_quality_v1`](../evaluate/criteria.md#rubric_based_multi_turn_trajectory_quality_v1) | 会話全体のエンドツーエンドの軌跡 |

```json
{
  "criteria": {
    "rubric_based_multi_turn_trajectory_quality_v1": {
      "threshold": 0.7,
      "judge_model_options": { "judge_model": "gemini-3.7-flash" },
      "rubrics": [
        {
          "rubric_id": "verifies_identity_first",
          "rubric_content": {
            "text_property": "通話全体を通じて、エージェントは予約の詳細を開示する前に、発信者の名前を確認し生年月日を検証している。"
          }
        }
      ]
    }
  }
}
```

単一ターンの発言内容よりも、エージェントが順序どおりに実行されクリーンに引き継がれたかどうかが重要な [ワークフロー](workflows.md) では、軌跡（trajectory）基準を活用してください。回答が明確に決まっている場合は、[`tool_trajectory_avg_score`](../evaluate/criteria.md#tool_trajectory_avg_score) を使用して、言い回しを完全に無視してツール呼び出しの正確な順序のみをチェックできます。

## 評価を実行する

`test_config.json` に `live_model_config` ブロックを追加します。これにより評価がライブモードになり、テキスト評価で使用される単項の `generateContent` エンドポイントでは提供されない [ライブモデル](models.md#live-models) で必須となります。

```json
{
  "live_model_config": {
    "timeout_seconds": 300
  }
}
```

`timeout_seconds`（デフォルト 300）は、ターンが終了するまでの ADK の最大待機時間を制限します。エージェントが長いツール呼び出しについて説明する場合は増やし、スタックしたセッションを迅速に失敗させるには減らします。

```shell
adk eval path/to/your_agent \
  path/to/your_agent/live.evalset.json \
  --config_file_path path/to/your_agent/test_config.json
```

これには eval エクストラ（`pip install "google-adk[eval]"`）と、Live API および TTS モデルの認証情報が必要です。`AgentEvaluator` を通じても同じ実行が可能であり、これにより CI に音声評価を組み込むことができます。

`adk web` では、評価ダイアログに **Standard | Live** の切り替えトグルがあり、入力モダリティやシミュレートされたユーザーの音声と言語を設定できます。実行が完了すると、ADK は各ターンに再生可能なクリップが付いた文字起こしに音声を再構成するため、エージェントの発言内容を読むだけでなく、どのように聞こえたかを実際に確認できます。

## サンプル

[`live_workflow` サンプル](https://github.com/google/adk-python/tree/main/contributing/samples/live/live_workflow) は、実際に実行できる完全な音声評価のサンプルです。グラフワークフロー内の 3 つのライブエージェント、途中のツール呼び出し、そして 3 つのルーブリック基準すべてが設定された評価セットと `test_config.json` が含まれています。
