# 사용자 시뮬레이션

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.18.0</span>
</div>

대화형 에이전트를 평가할 때는 대화가 예상치 못한 방향으로 진행될 수 있기 때문에
고정된 사용자 프롬프트 집합을 사용하는 것이 항상 실용적이지는 않습니다.
예를 들어 에이전트가 작업을 수행하기 위해 사용자에게 두 개의 값을 제공받아야 한다면,
그 값을 하나씩 요청할 수도 있고 한 번에 모두 요청할 수도 있습니다.
이 문제를 해결하기 위해 ADK는 생성형 AI 모델을 사용해 사용자 프롬프트를
동적으로 생성할 수 있습니다.

이 기능을 사용하려면 에이전트와의 대화에서 사용자의 목표를 규정하는
[`ConversationScenario`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/conversation_scenarios.py)를
지정해야 합니다. 또한 사용자가 따라야 한다고 기대하는 사용자 페르소나를
지정할 수도 있습니다.

`ConversationScenario`는 다음 구성 요소로 이루어집니다.

*   `starting_prompt`: 사용자가 에이전트와 대화를 시작할 때 사용해야 하는 고정된 초기 프롬프트
*   `conversation_plan`: 사용자가 달성해야 하는 목표에 대한 상위 수준 가이드라인
*   `user_persona`: 기술 숙련도나 언어 스타일과 같은 사용자 특성의 정의

[`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world)
에이전트에 대한 대화 시나리오 예시는 다음과 같습니다.

```json
{
  "starting_prompt": "무엇을 할 수 있나요?",
  "conversation_plan": "에이전트에게 20면체 주사위를 굴리라고 요청합니다. 결과를 받은 뒤, 그 숫자가 소수인지 확인해 달라고 요청합니다."
}
```

LLM은 `conversation_plan`과 대화 기록을 함께 사용해 사용자 프롬프트를 동적으로 생성합니다.

다음과 같이 미리 정의된 `user_persona`를 지정할 수도 있습니다.

```json
{
  "starting_prompt": "무엇을 할 수 있나요?",
  "conversation_plan": "에이전트에게 20면체 주사위를 굴리라고 요청합니다. 결과를 받은 뒤, 그 숫자가 소수인지 확인해 달라고 요청합니다.",
  "user_persona": "NOVICE"
}
```

대화 계획이 무엇을 달성해야 하는지를 규정한다면, 페르소나는 모델이 질문을 어떤 방식으로 표현하고 에이전트의 응답에 어떻게 반응하는지를 규정합니다.

!!! tip "Colab에서 사용해 보기"

    [ADK 에이전트를 동적으로 평가하기 위한 사용자 대화 시뮬레이션](https://github.com/google/adk-samples/blob/main/python/notebooks/evaluation/user_simulation_in_adk_evals.ipynb)
    대화형 노트북에서 이 전체 워크플로를 직접 시험해 볼 수 있습니다.
    대화 시나리오를 정의하고, 대화를 점검하기 위한 "드라이 런"을 실행한 뒤,
    전체 평가를 수행하여 에이전트 응답을 점수화하게 됩니다.

## 사용자 페르소나

User Persona는 시뮬레이션된 사용자가 대화 중에 취하는 역할입니다.
이는 사용자가 어떤 커뮤니케이션 스타일을 사용하는지, 정보를 어떻게 제공하는지,
오류에 어떻게 반응하는지 등을 규정하는 **행동(behaviors)** 집합으로 정의됩니다.

`UserPersona`는 다음 필드로 구성됩니다.

*   `id`: 페르소나의 고유 식별자
*   `description`: 사용자가 누구이며 에이전트와 어떻게 상호작용하는지에 대한 상위 수준 설명
*   `behaviors`: 구체적인 특성을 정의하는 `UserBehavior` 객체 목록

각 `UserBehavior`에는 다음이 포함됩니다.

*   `name`: 행동의 이름
*   `description`: 기대되는 행동에 대한 요약
*   `behavior_instructions`: 시뮬레이션된 사용자(LLM)가 어떻게 행동해야 하는지에 대해 주어지는 구체적인 지침
*   `violation_rubrics`: 평가기가 사용자가 이 행동을 따르고 있는지 판단할 때 사용하는 기준입니다. 이 rubric 중 **하나라도** 충족되면, 평가기는 해당 행동이 **지켜지지 않았다**고 판단해야 합니다.

## 사전 정의된 페르소나

ADK는 공통적인 행동으로 구성된 사전 정의 페르소나 세트를 제공합니다.
아래 표는 각 페르소나의 행동을 요약한 것입니다.

| 행동 | **EXPERT** 페르소나 | **NOVICE** 페르소나 | **EVALUATOR** 페르소나 |
| :--- | :--- | :--- | :--- |
| **Advance** | 세부 사항을 중시함(능동적으로 세부 정보를 제공) | 목표 지향적(세부 정보는 요청받을 때까지 기다림) | 세부 사항을 중시함 |
| **Answer** | 관련된 질문에만 답변 | 모든 질문에 답변 | 관련된 질문에만 답변 |
| **Correct Agent Inaccuracies** | 예 | 아니요 | 아니요 |
| **Troubleshoot Agent Errors** | 한 번은 시도함 | 절대 시도하지 않음 | 절대 시도하지 않음 |
| **Tone** | 전문적 | 대화체 | 대화체 |

## 예: 대화 시나리오로 [`hello_world`](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world) 에이전트 평가하기

대화 시나리오가 포함된 평가 케이스를 새 또는 기존
[`EvalSet`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py)에
추가하려면, 먼저 에이전트를 시험할 대화 시나리오 목록을 만들어야 합니다.

다음을 `contributing/samples/hello_world/conversation_scenarios.json`에 저장해 보세요.

```json
{
  "scenarios": [
    {
      "starting_prompt": "무엇을 할 수 있나요?",
      "conversation_plan": "에이전트에게 20면체 주사위를 굴리라고 요청합니다. 결과를 받은 뒤, 그 숫자가 소수인지 확인해 달라고 요청합니다.",
      "user_persona": "NOVICE"
    },
    {
      "starting_prompt": "안녕하세요, 소수가 나쁜 숫자로 취급되는 테이블탑 RPG를 진행 중입니다!",
      "conversation_plan": "숫자 값 자체는 중요하지 않고, 굴린 결과가 좋은지 나쁜지만 알려 달라고 말합니다. 에이전트가 동의하면 6면체 주사위를 굴리라고 요청합니다. 마지막으로 20면체 주사위 2개에 대해서도 같은 작업을 해 달라고 요청합니다.",
      "user_persona": "EXPERT"
    }
  ]
}
```

평가 중에 사용되는 정보가 들어 있는 세션 입력 파일도 필요합니다.
다음을 `contributing/samples/hello_world/session_input.json`에 저장해 보세요.

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

# 대화 시나리오를 새 평가 케이스로 EvalSet에 추가
adk eval_set add_eval_case \
  contributing/samples/hello_world \
  eval_set_with_scenarios \
  --scenarios_file contributing/samples/hello_world/conversation_scenarios.json \
  --session_input_file contributing/samples/hello_world/session_input.json
```

기본적으로 ADK는 에이전트의 기대 응답을 지정해야 하는 메트릭으로 평가를 실행합니다.
하지만 동적 대화 시나리오에서는 그러한 기대 응답을 미리 지정하지 않으므로,
대신 일부 대체 지원 메트릭이 포함된
[`EvalConfig`](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_config.py)를 사용합니다.

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

마지막으로 `adk eval` 명령으로 평가를 실행할 수 있습니다.

```bash
adk eval \
    contributing/samples/hello_world \
    --config_file_path contributing/samples/hello_world/eval_config.json \
    eval_set_with_scenarios \
    --print_detailed_results
```

## 사용자 시뮬레이터 구성

기본 사용자 시뮬레이터 구성을 재정의하여 모델, 내부 모델 동작,
최대 사용자-에이전트 상호작용 횟수를 변경할 수 있습니다.
아래 `EvalConfig`는 기본 사용자 시뮬레이터 구성을 보여 줍니다.

```json
{
  "criteria": {
    # 이전과 동일
  },
  "user_simulator_config": {
    "model": "gemini-flash-latest",
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

*   `model`: 사용자 시뮬레이터를 구동하는 모델
*   `model_configuration`: 모델 동작을 제어하는
    [`GenerateContentConfig`](https://github.com/googleapis/python-genai/blob/6196b1b4251007e33661bb5d7dc27bafee3feefe/google/genai/types.py#L4295)
*   `max_allowed_invocations`: 대화가 강제로 종료되기 전까지 허용되는 최대 사용자-에이전트 상호작용 횟수입니다. 이는 `EvalSet`에 있는 가장 긴 합리적인 사용자-에이전트 상호작용보다 크게 설정해야 합니다.
*   `custom_instructions`: 선택 사항. 사용자 시뮬레이터의 기본 지침을 재정의합니다. 지침 문자열에는
    [Jinja](https://jinja.palletsprojects.com/en/stable/templates/#) 구문을 사용하여 다음 형식의 플레이스홀더를 포함해야 합니다
    (*값을 미리 치환하지 마세요!*).
    *   `{{ stop_signal }}`: 사용자 시뮬레이터가 대화가 끝났다고 판단했을 때 생성할 텍스트
    *   `{{ conversation_plan }}`: 사용자 시뮬레이터가 따라야 하는 전체 대화 계획
    *   `{{ conversation_history }}`: 지금까지 사용자와 에이전트 간에 오간 대화
    *   `{{ persona }}`: `UserPersona` 객체에도 접근할 수 있는 플레이스홀더

## 커스텀 페르소나

`ConversationScenario`에 `UserPersona` 객체를 제공하여
자체 커스텀 페르소나를 정의할 수 있습니다.

커스텀 페르소나 정의 예시는 다음과 같습니다.

```json
{
  "starting_prompt": "계정 관련 도움을 받고 싶습니다.",
  "conversation_plan": "에이전트에게 비밀번호 재설정을 요청합니다.",
  "user_persona": {
    "id": "IMPATIENT_USER",
    "description": "바쁘고 쉽게 짜증을 내는 사용자입니다.",
    "behaviors": [
      {
        "name": "짧은 응답",
        "description": "사용자는 매우 짧고 때로는 불완전한 응답을 제공해야 합니다.",
        "behavior_instructions": [
            "응답을 10단어 이하로 유지합니다.",
            "정중한 표현은 생략합니다."
        ],
        "violation_rubrics": [
            "사용자 응답이 10단어를 초과합니다.",
            "사용자 응답이 지나치게 정중합니다."
        ]
      }
    ]
  }
}
```

## 사용자 시뮬레이션으로 평가 사례 생성하기

평가 사례를 수동으로 작성하면 시간이 많이 들고, 가능한 모든 실패 모드를 포괄하지 못할 수 있습니다. ADK는 Vertex AI Eval SDK를 사용해 에이전트 정의를 기반으로 다양한 현실적인 대화 시나리오를 자동 생성하는 명령을 제공합니다.

!!! warning "사전 요구 사항: Vertex AI 자격 증명"
    평가 사례 생성은 [Vertex Gen AI Evaluation Service API](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview)를 사용합니다. Vertex AI API가 활성화된 Google Cloud 프로젝트와, 환경에 구성된 유효한 애플리케이션 기본 자격 증명(ADC)이 필요합니다.

### 명령 구문

```bash
adk eval_set generate_eval_cases \
    <AGENT_MODULE_FILE_PATH> \
    <EVAL_SET_ID> \
    --user_simulation_config_file=<PATH_TO_CONFIG_FILE>
```

### 구성 파일 형식

`--user_simulation_config_file`은 `ConversationGenerationConfig` 스키마를 따르는 JSON 파일을 기대합니다.

```json
{
  "count": 5,
  "generation_instruction": "사용자가 다양한 조건에서 홈 디바이스를 제어해 달라고 요청하는 시나리오를 생성합니다.",
  "environment_context": "사용 가능한 디바이스: device_1(조명), device_2(온도조절기).",
  "model_name": "gemini-flash-latest"
}
```

### 구성 필드

*   **`count`** (필수): 생성할 대화 시나리오 수입니다.
*   **`generation_instruction`** (선택 사항): 테스트하고 싶은 시나리오 유형이나 목표를 안내하는 자연어 프롬프트입니다.
*   **`environment_context`** (선택 사항): 에이전트 도구가 접근할 수 있는 백엔드 데이터나 상태를 설명하는 컨텍스트입니다. 이를 통해 생성기는 현실적인 데이터(예: 유효한 디바이스 ID)에 근거한 쿼리를 만들 수 있습니다.
*   **`model_name`** (필수): 생성에 사용할 Gemini 모델입니다(예: `gemini-flash-latest`).
