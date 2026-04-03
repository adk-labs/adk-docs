# 에이전트 최적화

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.24.0</span>
</div>

ADK는 평가 결과를 기반으로 에이전트를 자동으로 최적화할 수 있는 확장 가능한 프레임워크를 제공합니다.
기본적으로 `adk optimize` 명령을 사용해, 기본 옵티마이저로 ADK 평가 결과를 기반으로 간단한 에이전트를 빠르게 최적화할 수 있습니다.
더 복잡한 사용 사례에서는 사용자 지정 eval 데이터를 사용하는 샘플러를 개발하거나, 새로운 최적화 전략을 직접 구현할 수 있습니다.

### 정의

* **샘플러**: 샘플러는 에이전트 옵티마이저가 후보 최적화 에이전트를 평가할 수 있게 합니다.
요청이 있을 때 샘플러는 eval 기반 에이전트 최적화에 유용한 상세 평가 결과를 옵티마이저에 제공합니다.
* **에이전트 옵티마이저**: 에이전트 옵티마이저는 샘플러의 평가 결과를 검토하고 이를 사용해 에이전트를 개선합니다.

## 예시 - `adk optimize`로 간단한 에이전트 최적화하기 {#example}

이 예시에서는 작은 eval 세트에 대한 평가 결과를 바탕으로 [`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) 샘플 에이전트의 지침을 업데이트하기 위해 `adk optimize` 명령을 사용합니다.

### 1단계: 예시 데이터셋 지정하기 {#exampledataset}

기본 `hello_world` 에이전트 지침은 숫자가 소수인지 판별하는 방법을 설명합니다.
이 예시의 eval 세트에는 에이전트에게 지시하지 않은 또 다른 측면이 추가됩니다. 숫자는 소수 여부에 따라 "good" 또는 "bad"가 될 수 있습니다.
옵티마이저는 이 새로운 규칙을 도출해 에이전트 지침에 추가해야 합니다.

[`contributing/samples/hello_world/`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world)에 `train_eval_set.evalset.json` 파일을 만들고 다음 내용을 넣습니다.

```json
{
  "eval_set_id": "train_eval_set",
  "name": "train_eval_set",
  "eval_cases": [
    {
      "eval_id": "simple",
      "conversation": [
        {
          "invocation_id": "inv1",
          "user_content": {
            "parts": [ {"text": "Is 7 prime?"} ],
            "role": "user"
          },
          "final_response": {
            "parts": [ {"text": "7 is a prime number."} ],
            "role": "model"
          }
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user"
      }
    },
    {
      "eval_id": "is_good",
      "conversation": [
        {
          "invocation_id": "inv1",
          "user_content": {
            "parts": [ {"text": "Is 4 a bad number?"} ],
            "role": "user"
          },
          "final_response": {
            "parts": [ {"text": "4 is not prime so it is a good number."} ],
            "role": "model"
          }
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user"
      }
    },
    {
      "eval_id": "is_bad",
      "conversation": [
        {
          "invocation_id": "inv1",
          "user_content": {
            "parts": [ {"text": "Is 5 a bad number?"} ],
            "role": "user"
          },
          "final_response": {
            "parts": [ {"text": "5 is prime so it is a bad number."} ],
            "role": "model"
          }
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user"
      }
    }
  ]
}
```

### 2단계: 샘플러 구성 정의하기

샘플러 구성은 후보 최적화 에이전트를 평가하는 과정을 제어합니다.
예를 들어, 에이전트 출력의 정답 기준을 지정하고, 에이전트를 최적화할 때 사용할 eval 세트도 지정합니다.

전체 구성 옵션 목록은 [아래](#localevalsampler)에서 확인할 수 있습니다. 지금은 [`contributing/samples/hello_world/`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world)에 `sampler_config.json` 파일을 다음 내용으로 만들면 됩니다.

```json
{
  "eval_config": {
    "criteria": {
      "response_match_score": 0.75
    }
  },
  "app_name": "hello_world",
  "train_eval_set": "train_eval_set"
}
```

### 3단계: 최적화 작업 실행하기

`adk optimize` 명령을 실행하면서, `hello_world` 에이전트 디렉터리를 지정하고 위에서 만든 구성 파일을 전달합니다.

```bash
adk optimize contributing/samples/hello_world \
--sampler_config_file_path contributing/samples/hello_world/sampler_config.json
```

최종 출력은 달라질 수 있지만, 다음과 비슷할 수 있습니다.

```text
<logs and intermediate output>
================================================================================
Optimized root agent instructions:
--------------------------------------------------------------------------------
<existing unmodified instructions omitted for brevity>

**Special Rules for "Good" and "Bad" Numbers:**
*   A "bad number" is defined as a prime number.
*   A "good number" is defined as a non-prime number (i.e., a composite number or 1).
*   If a user asks if a number is "good" or "bad", you must always use the `check_prime` tool to determine its primality first.
*   After determining primality with the tool, respond according to the definitions above. Questions about "good" or "bad" numbers, when referring to primality, are objective and you are fully capable of answering them. Do not state you cannot answer such questions.
================================================================================
```

## `adk optimize` 명령 사용하기

```bash
adk optimize [OPTIONS] AGENT_MODULE_FILE_PATH
```

* `AGENT_MODULE_FILE_PATH`: `agent`라는 이름의 모듈을 포함하는 `__init__.py` 파일의 경로입니다.
`agent` 모듈에는 반드시 `root_agent`가 있어야 합니다.
올바른 설정 예시는 [`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) 에이전트를 참고하세요.
* `--sampler_config_file_path PATH`: 샘플러 구성 파일 경로입니다.
샘플러 구현과 구성 형식은 [아래](#localevalsampler)에서 설명합니다.
* `--optimizer_config_file_path PATH` (선택): 에이전트 옵티마이저 구성 파일 경로입니다.
지정하지 않으면 기본 구성을 사용합니다.
옵티마이저 구현, 구성 형식, 기본 구성은 [아래](#geparootagentpromptoptimizer)에서 설명합니다.
* `--print_detailed_results` (선택): 에이전트 옵티마이저가 측정한 세부 메트릭 출력을 활성화합니다.
* `--log_level` (선택): 로깅 수준을 설정합니다.
기본값은 `INFO`입니다.
사용 가능한 옵션은 `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`입니다.

## 사용 가능한 샘플러와 에이전트 옵티마이저

ADK에는 다음 샘플러와 에이전트 옵티마이저가 제공됩니다.
`adk optimize` 명령은 아래에 설명된 `LocalEvalSampler`와 `GEPARootAgentPromptOptimizer`를 사용합니다.
이 샘플러와 에이전트 옵티마이저는 직접 작성하는 스크립트에서도 사용할 수 있습니다.

### `LocalEvalSampler` {#localevalsampler}

[`LocalEvalSampler`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/local_eval_sampler.py)는 ADK의 [`LocalEvalService`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/local_eval_service.py)를 사용해 후보 에이전트를 평가합니다.
평가 결과를 [`UnstructuredSamplingResult`](#sampler-results)로 제공합니다.
`LocalEvalSampler`는 다음 필드를 포함하는 `LocalEvalSamplerConfig`로 설정할 수 있습니다.

* `eval_config`: 평가 기준과 사용자 시뮬레이션 옵션을 제공하는 [`EvalConfig`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py)입니다.
* `app_name`: 평가에 사용할 앱 이름입니다.
* `train_eval_set`: 최적화에 사용할 eval 세트 이름입니다.
* `train_eval_case_ids` (선택): 최적화에 사용할 eval case(example) ID 목록입니다.
지정하지 않으면 `train_eval_set`의 모든 eval case를 사용합니다.
* `validation_eval_set` (선택): 최적화된 에이전트를 검증하는 데 사용할 eval 세트 이름입니다.
지정하지 않으면 `train_eval_set`을 재사용합니다.
* `validation_eval_case_ids` (선택): 최적화된 에이전트를 검증하는 데 사용할 eval case(example) ID 목록입니다.
지정하지 않으면 `validation_eval_set`의 모든 eval case를 사용합니다.
`validation_eval_set`도 지정하지 않으면 유효한 train eval case를 재사용합니다.

`LocalEvalSampler`를 초기화할 때, `LocalEvalSamplerConfig`에 지정된 train 및 validation eval 세트에 접근할 수 있는 [`EvalSetsManager`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_sets_manager.py)도 제공해야 합니다.

### `GEPARootAgentPromptOptimizer` {#geparootagentpromptoptimizer}

[`GEPARootAgentPromptOptimizer`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/gepa_root_agent_prompt_optimizer.py)는 [GEPA](https://gepa-ai.github.io/gepa/) 옵티마이저를 사용해 루트 에이전트의 지침을 개선합니다.
이 옵티마이저는 샘플러가 평가 결과를 [`UnstructuredSamplingResult`](#sampler-results)로 제공할 것으로 기대합니다.
출력은 [`OptimizerResult`](#agent-optimizer-results)의 하위 클래스이며, [점수가 포함된 최적화 에이전트 목록](#agent-optimizer-results)과 최적화 중 수집된 추가 메트릭을 지정합니다.

참고: `GEPARootAgentPromptOptimizer`는 하위 에이전트, 에이전트 도구, 스킬 또는 루트 에이전트의 다른 측면을 개선하지 않습니다.

`GEPARootAgentPromptOptimizer`는 다음 필드를 포함하는 `GEPARootAgentPromptOptimizerConfig`로 설정할 수 있습니다.

* `optimizer_model` (선택): 평가 결과를 분석하고 에이전트를 최적화하는 데 사용하는 모델입니다.
기본값은 `"gemini-2.5-flash"`입니다.
* `model_configuration` (선택): 옵티마이저 모델의 구성입니다.
기본값은 1만 토큰 think budget을 가진 구성입니다.
* `max_metric_calls` (선택): 최적화 중 실행할 평가의 최대 횟수입니다.
기본값은 100입니다.
* `reflection_minibatch_size` (선택): 한 번에 에이전트 지침을 업데이트할 때 사용할 예시 수입니다.
기본값은 3입니다.
* `run_dir` (선택): 원하면 중간 및 최종 최적화 결과를 저장할 디렉터리입니다.
웜 스타트를 지원합니다.

## 핵심 데이터 타입

ADK는 샘플러에서 옵티마이저로 평가 데이터를 전달하는 흐름과 옵티마이저 출력을 관리하기 위해
[`optimization/data_types.py`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py)에 몇 가지 기본 데이터 타입을 정의합니다.
이 데이터 타입들은 사용자 지정 eval과 최적화 전략을 수용할 수 있도록 확장 가능하게 설계되어 있습니다.

### 샘플러 결과 {#sampler-results}

* [`SamplingResult`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py):
샘플러 출력의 기본 클래스입니다.
  * example UID를 해당 예시에 대한 에이전트의 전체 점수에 매핑하는 `scores` 사전을 포함해야 합니다.
* [`UnstructuredSamplingResult`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py):
`SamplingResult`의 내장 하위 클래스로, 궤적, 중간 출력, 하위 메트릭처럼 구조화되지 않은 각 예시별 JSON 직렬화 가능한 평가 데이터를 담을 수 있는 선택적 `data` 필드를 추가합니다.

대부분의 사용 사례에서는 `UnstructuredSamplingResult`를 사용할 수 있습니다.
대신 더 구조화된 형식으로 추가 평가 데이터를 반환하도록 `SamplingResult`의 자체 하위 클래스를 만들 수도 있습니다.
다만 샘플러와 옵티마이저가 모두 해당 형식을 지원해야 합니다.

### 에이전트 옵티마이저 결과 {#agent-optimizer-results}

* [`AgentWithScores`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py):
전체 점수와 함께 단일 최적화 에이전트를 나타냅니다.
  * 업데이트된 [`Agent`](https://github.com/google/adk-python/blob/main/src/google/adk/agents/llm_agent.py) 객체인 `optimized_agent`를 포함해야 합니다.
  * 보통 validation 세트에서 계산된 에이전트의 `overall_score`를 포함할 수 있습니다.
* [`OptimizerResult`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/data_types.py):
최적화 프로세스의 최종 출력을 나타냅니다.
  * `optimized_agents` 목록을 포함해야 합니다. 이 목록의 요소는 `AgentWithScores` 또는 그 하위 클래스여야 합니다.
  여러 메트릭에 걸쳐 에이전트의 최적성을 측정하는 경우, 파레토 프런티어를 나타내기 위해 여러 항목이 필요할 수 있습니다.

후보 최적화 에이전트에 대한 세부 메트릭을 노출하기 위해 `AgentWithScores`의 자체 하위 클래스를 만들 수 있습니다.
예를 들어 정확성, 안전성, 정렬성 등을 별도로 점수화하고 싶을 수 있습니다.
마찬가지로 `OptimizerResult`의 자체 하위 클래스를 만들어, 옵티마이저의 최적화 프로세스 전반에 대한 메트릭(평가된 후보 수, 총 평가 수 등)을 노출할 수 있습니다.

## 새 샘플러와 에이전트 옵티마이저 만들기 및 사용하기

사용 사례에 복잡한 샘플링 및 평가 로직이나 사용자 지정 에이전트 최적화 전략이 필요하다면, 아래에 설명된 `Sampler`와 `AgentOptimizer` 추상 클래스를 기반으로 사용자 지정 구현을 만들 수 있습니다.
이 API를 따르면 ADK가 제공하는 샘플러와 에이전트 옵티마이저를 사용자 지정 구현과 조합해 사용할 수 있습니다.

### 새 샘플러 만들기

사용자 지정 평가용 새 샘플러를 만들려면 [`Sampler`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/sampler.py) 기본 클래스를 확장하는 클래스를 만들어야 합니다.
또한 샘플러가 평가 결과를 반환할 때 사용할 [`SamplingResult`](#sampler-results) 하위 클래스를 지정해야 합니다.
샘플러는 다음 추상 메서드를 구현해야 합니다.

* `get_train_example_ids(self)`: 최적화에 사용할 example UID 목록을 반환합니다.
* `get_validation_example_ids(self)`: 최적화된 에이전트를 검증하는 데 사용할 example UID 목록을 반환합니다.
<!-- disableFinding(LINE_OVER_80) -->
* `sample_and_score(self, candidate, example_set, batch, capture_full_eval_data)`: 지정된 `example_set`(`"train"` 또는 `"validation"`)의 `batch` 예시에서 `candidate` 에이전트를 평가합니다.
계산된 예시별 점수와, `capture_full_eval_data`가 `True`인 경우 eval 기반 에이전트 최적화에 필요한 추가 데이터를 포함하는 [`SamplingResult`](#sampler-results) 하위 클래스를 반환해야 합니다.
추가 eval 데이터의 형식은 `SamplingResult`를 하위 클래스로 만들어 필요에 맞게 정할 수 있습니다.
다만 에이전트 옵티마이저도 같은 `SamplingResult` 하위 클래스를 지원해야 합니다.
[`UnstructuredSamplingResult`](#sampler-results)는 추가 데이터를 예시별 비구조화 사전으로 저장하는 가장 단순한 사례를 구현합니다.
<!-- enableFinding(LINE_OVER_80) -->

### 새 에이전트 옵티마이저 만들기

사용자 지정 에이전트 옵티마이저를 만들려면 [`AgentOptimizer`](https://github.com/google/adk-python/blob/main/src/google/adk/optimization/agent_optimizer.py) 기본 클래스를 확장하는 클래스를 만들어야 합니다.
또한 평가 결과를 받을 [`SamplingResult`](#sampler-results) 하위 클래스와, 각 최적화된 에이전트 및 그 점수/메트릭을 표현하는 데 사용할 [`AgentWithScores`](#agent-optimizer-results) 하위 클래스도 지정해야 합니다.
옵티마이저는 다음 추상 메서드를 구현해야 합니다.

* `optimize(self, initial_agent, sampler)`: 이 메서드는 최적화 프로세스를 조율합니다.
개선할 `initial_agent`와 후보 평가에 사용할 `sampler`를 받습니다.
후보 최적화 에이전트 목록과 그 점수/메트릭, 그리고 최적화 프로세스에 대한 전체 메트릭을 포함하는 [`OptimizerResult`](#agent-optimizer-results) 하위 클래스를 반환해야 합니다.
후보별 점수/메트릭의 형식은 `AgentWithScores`를 하위 클래스로 만들어 필요에 맞게 정할 수 있습니다.
또는 각 후보 최적화 에이전트에 대해 단일 전체 점수를 지정할 수 있는 `AgentWithScores`를 그대로 사용할 수도 있습니다.

### 프로그래밍 방식으로 에이전트 최적화하기

`adk optimize` 명령은 [`LocalEvalSampler`](#localevalsampler)와 [`GEPARootAgentPromptOptimizer`](#geparootagentpromptoptimizer)를 사용합니다.
사용자 지정 샘플러와 에이전트 옵티마이저를 사용할 때는 에이전트를 프로그래밍 방식으로 최적화해야 합니다.
아래의 참조 코드는 위 [예시](#example)에 대한 `adk optimize` 명령의 동작을 재현합니다.
이를 사용하려면 예시와 같이 [데이터셋](#exampledataset)을 만들고, [같은 디렉터리](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) 안의 Python 스크립트에서 이 코드를 실행합니다.

```python
import asyncio
import logging
import os

import agent  # the hello_world agent
from google.adk.cli.utils import envs
from google.adk.cli.utils import logs
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.local_eval_sets_manager import LocalEvalSetsManager
from google.adk.optimization.gepa_root_agent_prompt_optimizer import GEPARootAgentPromptOptimizer
from google.adk.optimization.gepa_root_agent_prompt_optimizer import GEPARootAgentPromptOptimizerConfig
from google.adk.optimization.local_eval_sampler import LocalEvalSampler
from google.adk.optimization.local_eval_sampler import LocalEvalSamplerConfig

# setup environment variables (API keys, etc.) and logging
envs.load_dotenv_for_agent(".", ".")
logs.setup_adk_logger(logging.INFO)

# create the sampler
sampler_config = LocalEvalSamplerConfig(
    eval_config=EvalConfig(criteria={"response_match_score": 0.75}),
    app_name="hello_world",  # typically the name of the directory containing the agent
    train_eval_set="train_eval_set",  # from the example
)
eval_sets_manager = LocalEvalSetsManager(
    agents_dir=os.path.dirname(os.getcwd()),
)
sampler = LocalEvalSampler(sampler_config, eval_sets_manager)

# create the optimizer
opt_config = GEPARootAgentPromptOptimizerConfig()
optimizer = GEPARootAgentPromptOptimizer(config=opt_config)

# optimize the root agent
initial_agent = agent.root_agent
result = asyncio.run(
    optimizer.optimize(initial_agent, sampler)
)

# show the results
best_idx = result.gepa_result["best_idx"]
print(
    "Validation score:",
    result.optimized_agents[best_idx].overall_score,
    "Optimized prompt:",
    result.optimized_agents[best_idx].optimized_agent.instruction,
    "GEPA metrics:",
    result.gepa_result,
    sep="\n",
)
```
