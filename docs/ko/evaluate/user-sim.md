# 사용자 시뮬레이션

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.18.0</span>
</div>

대화형 에이전트를 평가할 때 대화가 예기치 않은 방식으로 진행될 수 있으므로 고정된 사용자 프롬프트 세트를 사용하는 것이 항상 실용적인 것은 아닙니다. 예를 들어 에이전트가 작업을 수행하기 위해 사용자가 두 개의 값을 제공해야 하는 경우 해당 값을 한 번에 하나씩 또는 한 번에 모두 요청할 수 있습니다. 이 문제를 해결하기 위해 ADK는 생성 AI 모델을 사용하여 사용자 프롬프트를 동적으로 생성할 수 있습니다.

이 기능을 사용하려면 에이전트와의 대화에서 사용자의 목표를 지시하는 [ConversationScenario](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/conversation_scenarios.py)를 지정해야 합니다. [hello_world](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) 에이전트에 대한 샘플 대화 시나리오는 다음과 같습니다.

```json
{
  "starting_prompt": "무엇을 도와드릴까요?",
  "conversation_plan": "에이전트에게 20면체 주사위를 굴리도록 요청합니다. 결과를 얻은 후 에이전트에게 소수인지 확인하도록 요청합니다."
}
```

대화 시나리오의 `starting_prompt`는 사용자가 에이전트와의 대화를 시작하는 데 사용해야 하는 고정된 초기 프롬프트를 지정합니다. 에이전트가 다른 방식으로 응답할 수 있으므로 에이전트와의 후속 상호 작용에 대해 이러한 고정 프롬프트를 지정하는 것은 실용적이지 않습니다. 대신 `conversation_plan`은 에이전트와의 나머지 대화가 진행되어야 하는 방식에 대한 지침을 제공합니다. LLM은 이 대화 계획을 대화 기록과 함께 사용하여 대화가 완료되었다고 판단할 때까지 사용자 프롬프트를 동적으로 생성합니다.

!!! tip "Colab에서 사용해 보기"

    [ADK 에이전트를 동적으로 평가하기 위한 사용자 대화 시뮬레이션](https://github.com/google/adk-samples/blob/main/python/notebooks/evaluation/user_simulation_in_adk_evals.ipynb)에 대한 대화형 노트북에서 이 전체 워크플로를 직접 테스트해 보세요. 대화 시나리오를 정의하고 "드라이 런"을 실행하여 대화를 확인한 다음 전체 평가를 수행하여 에이전트의 응답에 점수를 매깁니다.

## 예: 대화 시나리오로 [hello_world](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) 에이전트 평가

대화 시나리오가 포함된 평가 사례를 신규 또는 기존 [EvalSet](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py)에 추가하려면 먼저 에이전트를 테스트할 대화 시나리오 목록을 만들어야 합니다.

다음을 `contributing/samples/hello_world/conversation_scenarios.json`에 저장해 보세요.

```json
{
  "scenarios": [
    {
      "starting_prompt": "무엇을 도와드릴까요?",
      "conversation_plan": "에이전트에게 20면체 주사위를 굴리도록 요청합니다. 결과를 얻은 후 에이전트에게 소수인지 확인하도록 요청합니다."
    },
    {
      "starting_prompt": "안녕하세요, 소수가 나쁜 탁상용 RPG를 실행하고 있습니다!",
      "conversation_plan": "값에는 관심이 없고 에이전트가 굴림이 좋은지 나쁜지 알려주기만 하면 된다고 말합니다. 에이전트가 동의하면 6면체 주사위를 굴리도록 요청합니다. 마지막으로 에이전트에게 20면체 주사위 2개로 동일한 작업을 수행하도록 요청합니다."
    }
  ]
}
```

평가 중에 사용되는 정보가 포함된 세션 입력 파일도 필요합니다. 다음을 `contributing/samples/hello_world/session_input.json`에 저장해 보세요.

```json
{
  "app_name": "hello_world",
  "user_id": "user"
}
```

그런 다음 대화 시나리오를 `EvalSet`에 추가할 수 있습니다.

```bash
# (선택 사항) 새 EvalSet 만들기
adk eval_set create \
  contributing/samples/hello_world \
  eval_set_with_scenarios

# 대화 시나리오를 새 평가 사례로 EvalSet에 추가
adk eval_set add_eval_case \
  contributing/samples/hello_world \
  eval_set_with_scenarios \
  --scenarios_file contributing/samples/hello_world/conversation_scenarios.json \
  --session_input_file contributing/samples/hello_world/session_input.json
```

기본적으로 ADK는 에이전트의 예상 응답을 지정해야 하는 메트릭으로 평가를 실행합니다. 동적 대화 시나리오의 경우는 그렇지 않으므로 일부 대체 지원 메트릭이 포함된 [EvalConfig](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py)를 사용합니다.

다음을 `contributing/samples/hello_world/eval_config.json`에 저장해 보세요.

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

마지막으로 `adk eval` 명령을 사용하여 평가를 실행할 수 있습니다.

```bash
adk eval \
    contributing/samples/hello_world \
    --config_file_path contributing/samples/hello_world/eval_config.json \
    eval_set_with_scenarios \
    --print_detailed_results
```

## 사용자 시뮬레이터 구성

기본 사용자 시뮬레이터 구성을 재정의하여 모델, 내부 모델 동작 및 최대 사용자-에이전트 상호 작용 수를 변경할 수 있습니다. 아래 `EvalConfig`는 기본 사용자 시뮬레이터 구성을 보여줍니다.

```json
{
  "criteria": {
    # 이전과 동일
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

* `model`: 사용자 시뮬레이터를 지원하는 모델입니다.
* `model_configuration`: 모델 동작을 제어하는 [GenerateContentConfig](https://github.com/googleapis/python-genai/blob/6196b1b4251007e33661bb5d7dc27bafee3feefe/google/genai/types.py#L4295)입니다.
* `max_allowed_invocations`: 대화가 강제로 종료되기 전에 허용되는 최대 사용자-에이전트 상호 작용 수입니다. `EvalSet`에서 가장 긴 합리적인 사용자-에이전트 상호 작용보다 크게 설정해야 합니다.

```
