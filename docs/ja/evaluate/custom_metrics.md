## エージェント評価のためのカスタムメトリクス

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.18.0</span>
</div>

組み込みのオプションではカバーされない、特定のユースケースやドメインに合わせた専用メトリクスが必要な場合は、独自のカスタムメトリクスを定義できます。

## カスタムメトリクスを定義する

カスタムメトリクスは、指定された評価ケースでエージェントのパフォーマンスを評価し、
[`EvaluationResult`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/evaluator.py) を返す Python 関数です。この関数は [`EvalMetric`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py)、
評価実行中にエージェントが生成した [`Invocation`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py) オブジェクトのリスト、そして必要に応じて期待される invocation のリスト、または評価ケースで定義された
[`ConversationScenario`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py) を受け取ります。

各 `Invocation` オブジェクトは、ユーザーとエージェントの 1 回のやり取りを表し、そのターンのツール軌跡、中間応答、最終応答などの情報を含みます。

カスタムメトリクス関数は次のシグネチャを持つ必要があります。

```python
from typing import Optional
from google.adk.evaluation.eval_case import Invocation
from google.adk.evaluation.eval_metrics import EvalMetric
from google.adk.evaluation.conversation_scenarios import ConversationScenario
from google.adk.evaluation.evaluator import EvaluationResult

def my_custom_metric_function(
    eval_metric: EvalMetric,
    actual_invocations: list[Invocation],
    expected_invocations: Optional[list[Invocation]],
    conversation_scenario: Optional[ConversationScenario],
) -> EvaluationResult:
  ...
```

この関数は、`overall_score`、`overall_eval_status`、`per_invocation_results` フィールドが埋まった `EvaluationResult` オブジェクトを返す必要があります。

### 例

以下は、各ターンでエージェントの最終応答が期待される最終応答と完全一致するかを確認する簡単なカスタムメトリクスの例です。

```python
import statistics
from typing import Optional

from google.adk.evaluation.conversation_scenarios import ConversationScenario
from google.adk.evaluation.eval_case import Invocation
from google.adk.evaluation.eval_metrics import EvalMetric
from google.adk.evaluation.eval_metrics import EvalStatus
from google.adk.evaluation.evaluator import EvaluationResult, PerInvocationResult

def check_final_response_exact_match(
    eval_metric: EvalMetric,
    actual_invocations: list[Invocation],
    expected_invocations: Optional[list[Invocation]],
    conversation_scenario: Optional[ConversationScenario],
) -> EvaluationResult:
  """Checks if the final response of the first turn matches the expected
  response."""
  if not expected_invocations:
    return EvaluationResult(overall_score=0.0, overall_eval_status=EvalStatus.NOT_EVALUATED)

  per_invocation_results = []

  for actual, expected in zip(actual_invocations, expected_invocations):
    actual_final_response = "".join([part.text for part in actual.final_response.parts])
    expected_final_response = "".join([part.text for part in expected.final_response.parts])
    score = 1.0 if actual_final_response == expected_final_response else 0.0
    eval_status = EvalStatus.PASSED if score else EvalStatus.FAILED
    invocation_result = PerInvocationResult(
        actual_invocation=actual,
        expected_invocation=expected,
        score=score,
        eval_status=eval_status
    )
    per_invocation_results.append(invocation_result)

  average_score = statistics.mean(result.score for result in per_invocation_results)

  threshold = eval_metric.criterion.threshold
  overall_eval_status = (
      EvalStatus.PASSED if average_score >= threshold else EvalStatus.FAILED
  )
  return EvaluationResult(
      overall_score=average_score,
      overall_eval_status=overall_eval_status,
      per_invocation_results=per_invocation_results,
  )
```

#### 非同期メトリクス

カスタムメトリクスが API 呼び出しなどの非同期処理を必要とする場合は、`async` 関数として定義できます。

次は、フェイクの非同期 profanity checker API を使って、エージェント応答に卑語が含まれているかを確認するカスタムメトリクス関数の例です。

```python
import asyncio
import statistics
from typing import Optional

from google.adk.evaluation.conversation_scenarios import ConversationScenario
from google.adk.evaluation.eval_case import Invocation
from google.adk.evaluation.eval_metrics import EvalMetric
from google.adk.evaluation.eval_metrics import EvalStatus
from google.adk.evaluation.evaluator import EvaluationResult, PerInvocationResult

class ProfanityChecker:
  """A fake profanity checker that mimics an async API."""

  async def check(self, text: str) -> bool:
    """Returns True if profanity is detected, False otherwise."""
    await asyncio.sleep(0.01)
    return "profanity" in text.lower()

profanity_checker = ProfanityChecker()

async def check_for_profanity(
    eval_metric: EvalMetric,
    actual_invocations: list[Invocation],
    expected_invocations: Optional[list[Invocation]],
    conversation_scenario: Optional[ConversationScenario],
) -> EvaluationResult:
  """Checks if the agent response contains profanity using a fake async API."""
  per_invocation_results = []

  for invocation in actual_invocations:
    agent_response = "".join(part.text for part in invocation.final_response.parts)
    has_profanity = await profanity_checker.check(agent_response)
    score = 0.0 if has_profanity else 1.0
    eval_status = EvalStatus.FAILED if has_profanity else EvalStatus.PASSED

    invocation_result = PerInvocationResult(
        actual_invocation=invocation,
        score=score,
        eval_status=eval_status
    )
    per_invocation_results.append(invocation_result)

  scores = [
      result.score
      for result in per_invocation_results
      if result.eval_status != EvalStatus.NOT_EVALUATED
  ]

  average_score = statistics.mean(scores)

  threshold = eval_metric.criterion.threshold
  overall_eval_status = (
      EvalStatus.PASSED if average_score >= threshold else EvalStatus.FAILED
  )
  return EvaluationResult(
      overall_score=average_score,
      overall_eval_status=overall_eval_status,
      per_invocation_results=per_invocation_results,
  )
```

## カスタムメトリクスを使う

`adk eval` による評価実行でカスタムメトリクスを使うには、`EvalConfig` JSON ファイルでそれを指定する必要があります。

1.  カスタムメトリクスを eval `criteria` の1つとして追加します。キーはメトリクス名、値は合格しきい値です。
2.  `EvalConfig` に `custom_metrics` オブジェクトを追加します。このオブジェクトの中に各カスタムメトリクスのエントリを追加し、キーはメトリクス名（`criteria` の名前と一致）、値は `code_config` を含むオブジェクトにします。
3.  `code_config` オブジェクトには、カスタムメトリクス関数への Python import path を表す文字列を持つ `name` フィールドが必要です。形式は `my.module.my_function` です。

### `EvalConfig` の例

`check_final_response_match` 関数が `my_agent.metrics.py` に定義されているとすると、`EvalConfig` は次のようになります。

```json
{
  "criteria": {
    "my_check_final_response_exact_match": {
      "threshold": 0.8
    },
    "tool_trajectory_avg_score": {
      "threshold": 1.0
    }
  },
  "custom_metrics": {
    "my_check_final_response_exact_match": {
      "code_config": {
        "name": "my_agent.metrics.check_final_response_exact_match"
      }
    }
  }
}
```

この設定で `adk eval --config_file_path=<path_to_this_config>` を実行すると、ADK は各 eval case に対して `check_final_response_exact_match` を実行し、返されたスコアが 0.8 以上かどうかを確認して `response_match` 基準を合格または不合格として扱います。

### メトリクス情報を提供する

カスタムメトリクスの説明や値の範囲などのメタデータを、`EvalConfig` 内のカスタムメトリクス定義に [`MetricInfo`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py#L369) オブジェクトを追加することで、任意で提供できます。`metric_info` が指定されていない場合、ADK はデフォルト値（`min_value`=0.0、`max_value`=1.0）を使用します。

この情報は、表示や結果集約のために ADK ツールで利用できます。

以下は、-1.0 から 1.0 の間のスコアを返すカスタムメトリクスに `metric_info` を提供する例です。

```json
{
  "criteria": {
    "my_metric": {
      "threshold": 0.5
    }
  },
  "custom_metrics": {
    "my_metric": {
      "code_config": {
        "name": "my_agent.metrics.my_metric_function"
      },
      "metric_info": {
        "metric_name": "my_metric",
        "description": "This metric evaluates XYZ and returns a score between -1.0 and 1.0.",
        "metric_value_info": {
          "interval": {
            "min_value": -1.0,
            "max_value": 1.0
          }
        }
      }
    }
  }
}
```
