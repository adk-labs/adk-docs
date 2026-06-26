---
catalog_title: MLflow Scorers
catalog_description: エージェント評価のために ADK 評価器（evaluator）を MLflow スコアラー（scorer）として使用します
catalog_icon: /integrations/assets/mlflow.png
catalog_tags: ["evaluation"]
---

# ADK エージェント向けの MLflow スコアラー（MLflow scorers）

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[MLflow](https://mlflow.org/docs/latest/genai/eval-monitor/)は、5つの ADK 評価器（evaluator）をサードパーティのスコアラーとしてラップするため、任意の `mlflow.genai.evaluate()` 実行内で ADK の軌跡一致（trajectory matching）、ROUGE 応答類似度、および LLM-judge メトリクスを使用できます。この連携は、ADK の `TrajectoryEvaluator`、`RougeEvaluator`、`FinalResponseMatchV2Evaluator`、`SafetyEvaluatorV1`、および `HallucinationsV1Evaluator` を対象としています。

ADK エージェントをトレースしている場合は、1行で OTel 自動トレースを設定できる [MLflow Tracing 連携](/integrations/mlflow-tracing/) を参照してください。以下の決定論的スコアラーは、それらのトレースから直接ツール呼び出しを読み取ります。

## 主なユースケース

- **ツール軌跡評価 (Tool trajectory evaluation)**: エージェントが正しいツールを正しい順序で呼び出したかを、`EXACT`、`IN_ORDER`、または `ANY_ORDER` マッチングで検証します。
- **応答の類似性 (Response similarity)**: ROUGE-1 F-measure を使用して、参照回答に対するエージェントの最終応答のスコアを算出します。
- **LLM 判定の応答品質 (LLM-judged response quality)**: 多数決投票を用いて、エージェントの応答が想定される応答と意味的に一致するかを Gemini に評価させます。
- **ハルシネーション検出 (Hallucination detection)**: Gemini を使用して、エージェント의 応答に捏造された事実が含まれているかを評価します。
- **安全性チェック (Safety checks)**: 判定モデルを管理することなく、Vertex AI の組み込み SAFETY メトリクスを使用して危険な出力にフラグを立てます。
- **スコアリングの混在 (Mix-and-match scoring)**: 単一の `mlflow.genai.evaluate()` 呼び出しで決定論的スコアラーと LLM 判定を一緒に実行し、高コストの判定モデル呼び出しの下に安価な構造チェックを重ねます。

## 前提条件

- フルスコアラーセットには MLflow 3.13 以降が必要です。MLflow 3.11 は2つの決定論的スコアラーを提供し、3つの LLM 判定スコアラーは 3.13 で追加されました。
- 環境に ADK がインストールされている必要があります。
- LLM 判定スコアラーの場合: `GEMINI_API_KEY`（Gemini Developer API）または Google Cloud プロジェクトの資格情報（Vertex AI）。 `Safety` は管理されたメトリクスに委譲するため、常に Vertex AI 環境が必要です。

## 依存関係のインストール

```bash
pip install "mlflow>=3.13" google-adk
```

## 利用可能なスコアラー

評価対象に基づいてグループ化された 5 つの MLflow スコアラー:

| スコアラー | 評価対象 | ラップするクラス |
| --- | --- | --- |
| `ToolTrajectory` | エージェントが正しいツールを正しい順序で呼び出したか | `TrajectoryEvaluator` |
| `ResponseMatch` | 実際の応答と想定される応答の間の語彙の類似性（ROUGE-1 F-measure） | `RougeEvaluator` |
| `ResponseEvaluation` | 最終応答が想定される応答と意味的に一致するか（LLM 判定） | `FinalResponseMatchV2Evaluator` |
| `Safety` | 応答に安全でないコンテンツが含まれているか | `SafetyEvaluatorV1` (Vertex AI 管理) |
| `Hallucination` | 応答にハルシネーション（捏造）コンテンツが含まれているか（LLM 判定） | `HallucinationsV1Evaluator` |

`ToolTrajectory` と `ResponseMatch` はマイクロ秒単位で実行され、API コストは発生しません。`ResponseEvaluation` と `Hallucination` は、5サンプルの多数決投票でデフォルトの Gemini Flash 判定モデルを呼び出します。モデルとサンプル数の両方が構成可能です。`Safety` は例外です。それ自体でモデル選択を管理する Vertex AI の組み込み SAFETY メトリクスを介してルーティングされるため、スコアラーに `model` または `num_samples` を渡すと `TypeError` が発生します。

## クイックスタート

スコアラーを直接呼び出す:

```python
from mlflow.genai.scorers.google_adk import ToolTrajectory

scorer = ToolTrajectory(match_type="EXACT", threshold=0.5)
feedback = scorer(
    inputs="Book a flight to Paris",
    outputs="Booked flight AA123 to Paris",
    expectations={
        "expected_tool_calls": [
            {"name": "search_flights", "args": {"destination": "Paris"}},
            {"name": "book_flight", "args": {"flight_id": "AA123"}},
        ],
        "actual_tool_calls": [
            {"name": "search_flights", "args": {"destination": "Paris"}},
            {"name": "book_flight", "args": {"flight_id": "AA123"}},
        ],
    },
)

print(feedback.value)            # "yes" または "no"
print(feedback.metadata["score"]) # 完全一致時に 1.0
```

または、単一の評価で複数のスコアラーを構成する:

```python
import mlflow
from mlflow.genai.scorers.google_adk import (
    ToolTrajectory,
    ResponseMatch,
    ResponseEvaluation,
)

eval_data = [
    {
        "inputs": {"query": "Find me a flight to Paris next Friday."},
        "outputs": "I found 3 flights to Paris on Friday: AA101, DL202, UA303.",
        "expectations": {
            "expected_tool_calls": [
                {"name": "search_flights", "args": {"destination": "Paris"}},
            ],
            "actual_tool_calls": [
                {"name": "search_flights", "args": {"destination": "Paris"}},
            ],
            "expected_response": "Here are flights to Paris next Friday.",
        },
    },
]

results = mlflow.genai.evaluate(
    data=eval_data,
    scorers=[
        ToolTrajectory(match_type="EXACT", threshold=0.5),
        ResponseMatch(threshold=0.5),
        ResponseEvaluation(threshold=0.6),
    ],
)
```

## ツール呼び出しの解決方法

`ToolTrajectory` には、想定されるツール呼び出し（`expectations["expected_tool_calls"]`）と、エージェントが実際に実行したツール呼び出しの両方が必要です。実際の呼び出しは次の順序で解決されます。

1. `expectations["actual_tool_calls"]` が存在する場合。ツール呼び出しをデータとしてキャプチャしたオフライン評価に便利です。
2. MLflow トレース上の `TOOL` スパン。明示的なオーバーライドがない場合, スコアラーはトレースをスキャンし, `TOOL` とタグ付けされたスパンからツール呼び出しを読み取ります。トレースを直接渡すか, `mlflow.genai.evaluate(predict_fn=...)` を使用するライブ評価のパスです。
3. 空のリスト。どちらも利用できない場合, スコアラーは想定されるリストを空の実際のリストと比較し, 結果として想定が空でない場合は 0.0 のスコアになります。

これを [MLflow Tracing 連携](/integrations/mlflow-tracing/) と組み合わせると、完全にオンラインのセットアップが可能になります: エージェント実行中に ADK が OTel スパンを放出し、MLflow がそれらを取り込み、スコアラーは明示的なデータ配管なしでトレースからツール呼び出しを読み戻します。

## LLM 判定の構成

`ResponseEvaluation` と `Hallucination` は、Gemini モデル ID、合否しきい値、および多数決のためのサンプル数を受け取ります:

```python
from mlflow.genai.scorers.google_adk import Hallucination, ResponseEvaluation

response_eval = ResponseEvaluation(
    model="gemini-flash-latest",
    threshold=0.5,
    num_samples=5,
)

hallucination = Hallucination(model="gemini-flash-latest", threshold=0.5)
```

モデル名は、`gemini-flash-latest` や `gemini-pro-latest` のように ADK の `LlmRegistry` が解決できる名前である必要があります。ADK の評価器は Google のモデルレジストリに直接接続するため、`databricks` や `openai:/gpt-4o` などの MLflow モデル URI はここではサポートされません。

`Safety` は Vertex AI の管理された SAFETY メトリクスを介して実行されます。これには、`GOOGLE_CLOUD_PROJECT`、`GOOGLE_CLOUD_LOCATION`、および `gcloud auth application-default login`（またはサービスアカウント）が必要です:

```python
from mlflow.genai.scorers.google_adk import Safety

safety = Safety(threshold=0.5)
```

認証情報がない場合、LLM 判定スコアラーは例外をスローするのではなく、`error` フィールドを持つ `Feedback` を返します。評価の実行は継続され、サンプルごとに対処すべき構成エラーが表面化します。

## リソース

- [MLflow ADK スコアラードキュメント](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/third-party/google-adk/)
- [MLflow Tracing 連携](/integrations/mlflow-tracing/)
- [MLflow AI Gateway 連携](/integrations/mlflow-gateway/)
- [ADK 評価ガイド](/evaluate/)
- [GitHub の MLflow リポジトリ](https://github.com/mlflow/mlflow)
