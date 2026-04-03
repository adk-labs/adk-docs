## 에이전트 평가를 위한 사용자 지정 메트릭

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.18.0</span>
</div>

기본 제공 옵션으로는 다루지 못하는 특정 사용 사례나 도메인에 맞춘 특수한 메트릭이 필요하다면, 직접 사용자 지정 메트릭을 정의할 수 있습니다.

## 사용자 지정 메트릭 정의

사용자 지정 메트릭은 주어진 평가 케이스에서 에이전트의 성능을 평가하고
[`EvaluationResult`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/evaluator.py)를 반환하는 Python 함수입니다. 이 함수는 [`EvalMetric`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py),
평가 실행 중 에이전트가 생성한 [`Invocation`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py) 객체 목록, 그리고 선택적으로 기대되는 invocation 목록 또는 평가 케이스에 정의된
[`ConversationScenario`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py)를 받습니다.

각 `Invocation` 객체는 사용자와 에이전트 사이의 한 턴 상호작용을 나타내며, 해당 턴의 도구 궤적, 중간 응답, 최종 응답 같은 정보를 포함합니다.

사용자 지정 메트릭 함수는 다음 시그니처를 가져야 합니다.

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

이 함수는 `overall_score`, `overall_eval_status`, `per_invocation_results` 필드가 채워진 `EvaluationResult` 객체를 반환해야 합니다.

### 예시

다음은 각 턴의 에이전트 최종 응답이 기대되는 최종 응답과 정확히 일치하는지 확인하는 간단한 사용자 지정 메트릭 예시입니다.

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

#### 비동기 메트릭

사용자 지정 메트릭이 API 호출 같은 비동기 호출을 수행해야 한다면 `async` 함수로 정의할 수 있습니다.

다음은 가짜 비동기 profanity checker API를 사용해 에이전트 응답에 비속어가 포함되어 있는지 확인하는 사용자 지정 메트릭 함수의 예시입니다.

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

## 사용자 지정 메트릭 사용하기

`adk eval`로 실행하는 평가에서 사용자 지정 메트릭을 사용하려면 `EvalConfig` JSON 파일에 이를 지정해야 합니다.

1.  사용자 지정 메트릭을 평가 `criteria` 중 하나로 추가합니다. 키는 메트릭 이름이고, 값은 통과 임계값입니다.
2.  `EvalConfig`에 `custom_metrics` 객체를 추가합니다. 이 객체 안에 각 사용자 지정 메트릭 항목을 넣고, 키는 메트릭 이름(`criteria`의 이름과 일치)이며 값은 `code_config`를 포함한 객체입니다.
3.  `code_config` 객체에는 문자열 형태의 `name` 필드가 있어야 하며, 이는 사용자 지정 메트릭 함수로 가는 Python import 경로를 나타냅니다. 형식은 `my.module.my_function`입니다.

### `EvalConfig` 예시

`check_final_response_match` 함수가 `my_agent.metrics.py`에 정의되어 있다고 가정하면, `EvalConfig`는 다음과 같을 수 있습니다.

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

이 구성을 사용하면 `adk eval --config_file_path=<path_to_this_config>`를 실행할 때 ADK는 각 eval case에 대해 `check_final_response_exact_match`를 실행하고, 반환된 점수가 0.8 이상인지 확인해 `response_match` 기준을 통과 또는 실패로 표시합니다.

### 메트릭 정보 제공

사용자 지정 메트릭에 대해 설명과 값 범위 같은 메타데이터를 선택적으로 제공할 수 있습니다. `EvalConfig` 안의 사용자 지정 메트릭 정의에 [`MetricInfo`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_metrics.py#L369) 객체를 추가하면 됩니다. `metric_info`가 제공되지 않으면 ADK는 기본값(`min_value`=0.0, `max_value`=1.0)을 사용합니다.

이 정보는 표시와 결과 집계를 위해 ADK 도구에서 사용할 수 있습니다.

다음은 -1.0에서 1.0 사이의 점수를 반환하는 사용자 지정 메트릭에 `metric_info`를 제공하는 예시입니다.

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
