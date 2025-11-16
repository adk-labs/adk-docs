# 에이전트를 평가하는 이유

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

기존 소프트웨어 개발에서는 단위 테스트와 통합 테스트를 통해 코드가 예상대로 작동하고 변경 사항에도 안정적으로 유지된다는 확신을 얻을 수 있습니다. 이러한 테스트는 명확한 "통과/실패" 신호를 제공하여 추가 개발을 안내합니다. 그러나 LLM 에이전트는 기존 테스트 접근 방식으로는 불충분한 수준의 가변성을 도입합니다.

모델의 확률적 특성으로 인해 결정론적 "통과/실패" 어설션은 종종 에이전트 성능 평가에 적합하지 않습니다. 대신 최종 출력과 에이전트의 궤적(솔루션에 도달하기 위해 취한 단계의 순서) 모두에 대한 정성적 평가가 필요합니다. 여기에는 에이전트의 결정 품질, 추론 프로세스 및 최종 결과 평가가 포함됩니다.

이는 설정하는 데 많은 추가 작업이 필요한 것처럼 보일 수 있지만 평가 자동화에 대한 투자는 빠르게 성과를 거두게 됩니다. 프로토타입을 넘어 진행하려는 경우 이는 적극 권장되는 모범 사례입니다.

![intro_components.png](../assets/evaluate_agent.png)

## 에이전트 평가 준비

에이전트 평가를 자동화하기 전에 명확한 목표와 성공 기준을 정의하십시오.

* **성공 정의:** 에이전트에게 성공적인 결과는 무엇입니까?
* **중요 작업 식별:** 에이전트가 수행해야 하는 필수 작업은 무엇입니까?
* **관련 메트릭 선택:** 성능을 측정하기 위해 추적할 메트릭은 무엇입니까?

이러한 고려 사항은 평가 시나리오 생성을 안내하고 실제 배포에서 에이전트 동작을 효과적으로 모니터링할 수 있도록 합니다.

## 무엇을 평가해야 합니까?

개념 증명과 프로덕션 준비 AI 에이전트 간의 격차를 해소하려면 강력하고 자동화된 평가 프레임워크가 필수적입니다. 주로 최종 출력에 초점을 맞추는 생성 모델 평가와 달리 에이전트 평가는 의사 결정 프로세스에 대한 더 깊은 이해가 필요합니다. 에이전트 평가는 두 가지 구성 요소로 나눌 수 있습니다.

1. **궤적 및 도구 사용 평가:** 도구 선택, 전략 및 접근 방식의 효율성을 포함하여 에이전트가 솔루션에 도달하기 위해 취하는 단계를 분석합니다.
2. **최종 응답 평가:** 에이전트의 최종 출력의 품질, 관련성 및 정확성을 평가합니다.

궤적은 에이전트가 사용자에게 돌아가기 전에 취한 단계의 목록일 뿐입니다. 이를 에이전트가 취했을 것으로 예상되는 단계 목록과 비교할 수 있습니다.

### 궤적 및 도구 사용 평가

사용자에게 응답하기 전에 에이전트는 일반적으로 '궤적'이라고 하는 일련의 작업을 수행합니다. 용어를 명확히 하기 위해 사용자 입력을 세션 기록과 비교하거나 정책 문서를 조회하거나 지식 기반을 검색하거나 티켓을 저장하기 위해 API를 호출할 수 있습니다. 이를 '궤적'이라고 합니다. 에이전트의 성능을 평가하려면 실제 궤적을 예상 또는 이상적인 궤적과 비교해야 합니다. 이 비교를 통해 에이전트 프로세스의 오류와 비효율성을 발견할 수 있습니다. 예상 궤적은 에이전트가 취해야 할 것으로 예상되는 단계 목록인 실측 자료를 나타냅니다.

예를 들어:

```python
# 궤적 평가는 다음을 비교합니다.
expected_steps = ["determine_intent", "use_tool", "review_results", "report_generation"]
actual_steps = ["determine_intent", "use_tool", "review_results", "report_generation"]
```

ADK는 실측 자료 기반 및 루브릭 기반 도구 사용 평가 메트릭을 모두 제공합니다. 에이전트의 특정 요구 사항 및 목표에 적합한 메트릭을 선택하려면 [기준 권장 사항](#recommendations-on-criteria)을 참조하십시오.

## ADK를 사용한 평가 작동 방식

ADK는 미리 정의된 데이터 세트 및 평가 기준에 대해 에이전트 성능을 평가하는 두 가지 방법을 제공합니다. 개념적으로 유사하지만 처리할 수 있는 데이터 양이 다르며 일반적으로 각 사용 사례에 적합한 사용 사례를 결정합니다.

### 첫 번째 접근 방식: 테스트 파일 사용

이 접근 방식은 각각 단일의 간단한 에이전트-모델 상호 작용(세션)을 나타내는 개별 테스트 파일을 만드는 것을 포함합니다. 활성 에이전트 개발 중에 가장 효과적이며 단위 테스트 형식으로 사용됩니다. 이러한 테스트는 빠른 실행을 위해 설계되었으며 간단한 세션 복잡성에 중점을 두어야 합니다. 각 테스트 파일에는 단일 세션이 포함되며 여러 턴으로 구성될 수 있습니다. 턴은 사용자와 에이전트 간의 단일 상호 작용을 나타냅니다. 각 턴에는 다음이 포함됩니다.

-   `사용자 콘텐츠`: 사용자가 발행한 쿼리입니다.
-   `예상 중간 도구 사용 궤적`: 에이전트가 사용자 쿼리에 올바르게 응답하기 위해 수행할 것으로 예상되는 도구 호출입니다.
-   `예상 중간 에이전트 응답`: 에이전트(또는 하위 에이전트)가 최종 답변을 생성하는 과정에서 생성하는 자연어 응답입니다. 이러한 자연어 응답은 일반적으로 다중 에이전트 시스템의 아티팩트이며, 여기서 루트 에이전트는 목표를 달성하기 위해 하위 에이전트에 의존합니다. 이러한 중간 응답은 최종 사용자에게는 관심이 없을 수 있지만 시스템 개발자/소유자에게는 에이전트가 최종 응답을 생성하기 위해 올바른 경로를 거쳤다는 확신을 주기 때문에 매우 중요합니다.
-   `최종 응답`: 에이전트의 예상 최종 응답입니다.

파일에 `evaluation.test.json`과 같은 이름을 지정할 수 있습니다. 프레임워크는 `.test.json` 접미사만 확인하며 파일 이름의 앞부분은 제한되지 않습니다. 테스트 파일은 공식 Pydantic 데이터 모델에 의해 지원됩니다. 두 가지 주요 스키마 파일은 [Eval Set](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 및 [Eval Case](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py)입니다. 다음은 몇 가지 예가 포함된 테스트 파일입니다.

*(참고: 주석은 설명 목적으로 포함되었으며 JSON이 유효하려면 제거해야 합니다.)*

```json
# 일부 필드는 이 문서를 읽기 쉽게 만들기 위해 제거되었습니다.
{
  "eval_set_id": "home_automation_agent_light_on_off_set",
  "name": "",
  "description": "이것은 에이전트의 `x` 동작을 단위 테스트하는 데 사용되는 평가 세트입니다.",
  "eval_cases": [
    {
      "eval_id": "eval_case_id",
      "conversation": [
        {
          "invocation_id": "b7982664-0ab6-47cc-ab13-326656afdf75", # 호출에 대한 고유 식별자입니다.
          "user_content": { # 이 호출에서 사용자가 제공한 콘텐츠입니다. 이것이 쿼리입니다.
            "parts": [
              {
                "text": "침실의 device_2를 끄십시오."
              }
            ],
            "role": "user"
          },
          "final_response": { # 벤치마크의 참조 역할을 하는 에이전트의 최종 응답입니다.
            "parts": [
              {
                "text": "device_2 상태를 꺼짐으로 설정했습니다."
              }
            ],
            "role": "model"
          },
          "intermediate_data": {
            "tool_uses": [ # 시간순으로 도구 사용 궤적입니다.
              {
                "args": {
                  "location": "Bedroom",
                  "device_id": "device_2",
                  "status": "OFF"
                },
                "name": "set_device_info"
              }
            ],
            "intermediate_responses": [] # 모든 중간 하위 에이전트 응답입니다.
          },
        }
      ],
      "session_input": { # 초기 세션 입력입니다.
        "app_name": "home_automation_agent",
        "user_id": "test_user",
        "state": {}
      },
    }
  ],
}
```

테스트 파일은 폴더로 구성할 수 있습니다. 선택적으로 폴더에는 평가 기준을 지정하는 `test_config.json` 파일도 포함될 수 있습니다.

#### Pydantic 스키마로 지원되지 않는 테스트 파일을 마이그레이션하는 방법은 무엇입니까?

참고: 테스트 파일이 [EvalSet](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 스키마 파일을 준수하지 않는 경우 이 섹션이 관련됩니다.

기존 `*.test.json` 파일을 Pydantic 지원 스키마로 마이그레이션하려면 `AgentEvaluator.migrate_eval_data_to_new_schema`를 사용하십시오.

이 유틸리티는 현재 테스트 데이터 파일과 선택적 초기 세션 파일을 가져와 새 형식으로 직렬화된 데이터가 포함된 단일 출력 json 파일을 생성합니다. 새 스키마가 더 응집력이 있다는 점을 감안할 때 이전 테스트 데이터 파일과 초기 세션 파일은 모두 무시(또는 제거)할 수 있습니다.

### 두 번째 접근 방식: Evalset 파일 사용

evalset 접근 방식은 에이전트-모델 상호 작용을 평가하기 위해 "evalset"이라는 전용 데이터 세트를 활용합니다. 테스트 파일과 유사하게 evalset에는 예제 상호 작용이 포함되어 있습니다. 그러나 evalset에는 여러 개의 잠재적으로 긴 세션이 포함될 수 있으므로 복잡한 다중 턴 대화를 시뮬레이션하는 데 이상적입니다. 복잡한 세션을 나타낼 수 있는 기능으로 인해 evalset은 통합 테스트에 적합합니다. 이러한 테스트는 더 광범위한 특성으로 인해 일반적으로 단위 테스트보다 덜 자주 실행됩니다.

evalset 파일에는 각각 고유한 세션을 나타내는 여러 "eval"이 포함되어 있습니다. 각 eval은 사용자 쿼리, 예상 도구 사용, 예상 중간 에이전트 응답 및 참조 응답을 포함하는 하나 이상의 "턴"으로 구성됩니다. 이러한 필드는 테스트 파일 접근 방식에서와 동일한 의미를 갖습니다. 또는 eval은 에이전트와의 사용자 상호 작용을 [동적으로 시뮬레이션](./user-sim.md)하는 데 사용되는 *대화 시나리오*를 정의할 수 있습니다. 각 eval은 고유한 이름으로 식별됩니다. 또한 각 eval에는 관련 초기 세션 상태가 포함됩니다.

evalset을 수동으로 만드는 것은 복잡할 수 있으므로 관련 세션을 캡처하고 evalset 내에서 eval로 쉽게 변환하는 데 도움이 되는 UI 도구가 제공됩니다. 아래에서 평가를 위해 웹 UI를 사용하는 방법에 대해 자세히 알아보십시오. 다음은 두 개의 세션이 포함된 예제 evalset입니다. eval 세트 파일은 공식 Pydantic 데이터 모델에 의해 지원됩니다. 두 가지 주요 스키마 파일은 [Eval Set](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 및 [Eval Case](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_case.py)입니다.

!!! warning
    이 evalset 평가 방법은 유료 서비스인 [Vertex Gen AI Evaluation Service API](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/evaluation)를 사용해야 합니다.

*(참고: 주석은 설명 목적으로 포함되었으며 JSON이 유효하려면 제거해야 합니다.)*

```json
# 일부 필드는 이 문서를 읽기 쉽게 만들기 위해 제거되었습니다.
{
  "eval_set_id": "eval_set_example_with_multiple_sessions",
  "name": "여러 세션이 있는 평가 세트",
  "description": "이 평가 세트는 평가 세트에 둘 이상의 세션이 있을 수 있음을 보여주는 예입니다.",
  "eval_cases": [
    {
      "eval_id": "session_01",
      "conversation": [
        {
          "invocation_id": "e-0067f6c4-ac27-4f24-81d7-3ab994c28768",
          "user_content": {
            "parts": [
              {
                "text": "무엇을 할 수 있습니까?"
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {

                "text": "다양한 크기의 주사위를 굴리고 숫자가 소수인지 확인할 수 있습니다."
              }
            ],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          },
        },
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user",
        "state": {}
      },
    },
    {
      "eval_id": "session_02",
      "conversation": [
        {
          "invocation_id": "e-92d34c6d-0a1b-452a-ba90-33af2838647a",
          "user_content": {
            "parts": [
              {
                "text": "19면체 주사위를 굴립니다."
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "17이 나왔습니다."
              }
            ],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [],
            "intermediate_responses": []
          },
        },
        {
          "invocation_id": "e-bf8549a1-2a61-4ecc-a4ee-4efbbf25a8ea",
          "user_content": {
            "parts": [
              {
                "text": "10면체 주사위를 두 번 굴린 다음 9가 소수인지 확인합니다."
              }
            ],
            "role": "user"
          },
          "final_response": {
            "parts": [
              {
                "text": "주사위 굴림에서 4와 7이 나왔고 9는 소수가 아닙니다.\n"
              }
            ],
            "role": null
          },
          "intermediate_data": {
            "tool_uses": [
              {
                "id": "adk-1a3f5a01-1782-4530-949f-07cf53fc6f05",
                "args": {
                  "sides": 10
                },
                "name": "roll_die"
              },
              {
                "id": "adk-52fc3269-caaf-41c3-833d-511e454c7058",
                "args": {
                  "sides": 10
                },
                "name": "roll_die"
              },
              {
                "id": "adk-5274768e-9ec5-4915-b6cf-f5d7f0387056",
                "args": {
                  "nums": [
                    9
                  ]
                },
                "name": "check_prime"
              }
            ],
            "intermediate_responses": [
              [
                "data_processing_agent",
                [
                  {
                    "text": "10면체 주사위를 두 번 굴렸습니다. 첫 번째 굴림은 5이고 두 번째 굴림은 3입니다.\n"
                  }
                ]
              ]
            ]
          },
        }
      ],
      "session_input": {
        "app_name": "hello_world",
        "user_id": "user",
        "state": {}
      },
    }
  ],
}
```

#### Pydantic 스키마로 지원되지 않는 평가 세트 파일을 마이그레이션하는 방법은 무엇입니까?

참고: 평가 세트 파일이 [EvalSet](https://github.com/google/adk-python/blob/main/src/google/adk/evaluation/eval_set.py) 스키마 파일을 준수하지 않는 경우 이 섹션이 관련됩니다.

평가 세트 데이터 유지 관리자에 따라 두 가지 경로가 있습니다.

1.  **ADK UI에서 유지 관리하는 평가 세트 데이터** ADK UI를 사용하여 평가 세트 데이터를 유지 관리하는 경우 *아무 조치도 필요하지 않습니다*.

2.  **수동으로 개발 및 유지 관리되고 ADK 평가 CLI에서 사용되는 평가 세트 데이터** 마이그레이션 도구가 개발 중이며, 그때까지 ADK 평가 CLI 명령은 이전 형식의 데이터를 계속 지원합니다.

### 평가 기준

ADK는 도구 궤적 일치에서 LLM 기반 응답 품질 평가에 이르기까지 에이전트 성능을 평가하기 위한 여러 기본 제공 기준을 제공합니다. 사용 가능한 기준 및 사용 시기에 대한 자세한 목록은 [평가 기준](./criteria.md)을 참조하십시오.

다음은 사용 가능한 모든 기준의 요약입니다.

*   `tool_trajectory_avg_score`: 도구 호출 궤적의 정확한 일치.
*   `response_match_score`: 참조 응답에 대한 ROUGE-1 유사성.
*   `final_response_match_v2`: 참조 응답에 대한 LLM 판단 의미론적 일치.
*   `rubric_based_final_response_quality_v1`: 사용자 지정 루브릭을 기반으로 한 LLM 판단 최종 응답 품질.
*   `rubric_based_tool_use_quality_v1`: 사용자 지정 루브릭을 기반으로 한 LLM 판단 도구 사용 품질.
*   `hallucinations_v1`: 컨텍스트에 대한 에이전트 응답의 LLM 판단 근거.
*   `safety_v1`: 에이전트 응답의 안전성/무해성.

평가 기준이 제공되지 않으면 다음 기본 구성이 사용됩니다.

* `tool_trajectory_avg_score`: 기본값은 1.0이며 도구 사용 궤적에서 100% 일치가 필요합니다.
* `response_match_score`: 기본값은 0.8이며 에이전트의 자연어 응답에서 작은 오차 범위를 허용합니다.

다음은 사용자 지정 평가 기준을 지정하는 `test_config.json` 파일의 예입니다.

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 1.0,
    "response_match_score": 0.8
  }
}
```

#### 기준 권장 사항

평가 목표에 따라 기준을 선택하십시오.

*   **CI/CD 파이프라인 또는 회귀 테스트에서 테스트 활성화:** `tool_trajectory_avg_score` 및 `response_match_score`를 사용합니다. 이러한 기준은 빠르고 예측 가능하며 빈번한 자동화된 검사에 적합합니다.
*   **신뢰할 수 있는 참조 응답 평가:** `final_response_match_v2`를 사용하여 의미론적 동등성을 평가합니다. 이 LLM 기반 검사는 정확한 일치보다 유연하며 에이전트의 응답이 참조 응답과 동일한 의미를 갖는지 여부를 더 잘 파악합니다.
*   **참조 응답 없이 응답 품질 평가:** `rubric_based_final_response_quality_v1`을 사용합니다. 신뢰할 수 있는 참조가 없지만 좋은 응답의 속성을 정의할 수 있는 경우(예: "응답이 간결합니다.", "응답이 도움이 되는 어조입니다.") 유용합니다.
*   **도구 사용의 정확성 평가:** `rubric_based_tool_use_quality_v1`을 사용합니다. 이를 통해 특정 도구가 호출되었는지 또는 도구가 올바른 순서로 호출되었는지(예: "도구 A는 도구 B보다 먼저 호출되어야 합니다.")를 확인하여 에이전트의 추론 프로세스를 검증할 수 있습니다.
*   **응답이 컨텍스트에 근거하는지 확인:** `hallucinations_v1`을 사용하여 에이전트가 사용 가능한 정보(예: 도구 출력)에 의해 지원되지 않거나 모순되는 주장을 하는지 감지합니다.
*   **유해한 콘텐츠 확인:** `safety_v1`을 사용하여 에이전트 응답이 안전하고 안전 정책을 위반하지 않는지 확인합니다.

또한 예상 에이전트 도구 사용 및/또는 응답에 대한 정보가 필요한 기준은 [사용자 시뮬레이션](./user-sim.md)과 함께 지원되지 않습니다. 현재 `hallucinations_v1` 및 `safety_v1` 기준만 이러한 평가를 지원합니다.

### 사용자 시뮬레이션

대화형 에이전트를 평가할 때 대화가 예기치 않은 방식으로 진행될 수 있으므로 고정된 사용자 프롬프트 세트를 사용하는 것이 항상 실용적인 것은 아닙니다. 예를 들어 에이전트가 작업을 수행하기 위해 사용자에게 두 개의 값을 제공해야 하는 경우 해당 값을 한 번에 하나씩 또는 한 번에 모두 요청할 수 있습니다. 이 문제를 해결하기 위해 ADK를 사용하면 AI 모델에 의해 동적으로 생성되는 사용자 프롬프트를 사용하여 특정 *대화 시나리오*에서 에이전트의 동작을 테스트할 수 있습니다. 사용자 시뮬레이션을 사용한 평가 설정에 대한 자세한 내용은 [사용자 시뮬레이션](./user-sim.md)을 참조하십시오.

## ADK로 평가를 실행하는 방법

개발자는 다음과 같은 방법으로 ADK를 사용하여 에이전트를 평가할 수 있습니다.

1. **웹 기반 UI(**`adk web`**):** 웹 기반 인터페이스를 통해 대화형으로 에이전트를 평가합니다.
2. **프로그래밍 방식(**`pytest`**):** `pytest` 및 테스트 파일을 사용하여 평가를 테스트 파이프라인에 통합합니다.
3. **명령줄 인터페이스(**`adk eval`**):** 명령줄에서 직접 기존 평가 세트 파일에 대한 평가를 실행합니다.

### 1. `adk web` - 웹 UI를 통해 평가 실행

웹 UI는 에이전트를 대화형으로 평가하고, 평가 데이터 세트를 생성하고, 에이전트 동작을 자세히 검사하는 방법을 제공합니다.

#### 1단계: 테스트 케이스 생성 및 저장

1. `adk web <path_to_your_agents_folder>`를 실행하여 웹 서버를 시작합니다.
2. 웹 인터페이스에서 에이전트를 선택하고 상호 작용하여 세션을 만듭니다.
3. 인터페이스 오른쪽의 **평가** 탭으로 이동합니다.
4. 새 평가 세트를 만들거나 기존 세트를 선택합니다.
5. **"현재 세션 추가"**를 클릭하여 대화를 새 평가 케이스로 저장합니다.

#### 2단계: 테스트 케이스 보기 및 편집

케이스가 저장되면 목록에서 해당 ID를 클릭하여 검사할 수 있습니다. 변경하려면 **현재 평가 케이스 편집** 아이콘(연필)을 클릭합니다. 이 대화형 보기를 통해 다음을 수행할 수 있습니다.

* **수정** 에이전트 텍스트 응답을 수정하여 테스트 시나리오를 구체화합니다.
* **삭제** 대화에서 개별 에이전트 메시지를 삭제합니다.
* **삭제** 더 이상 필요하지 않은 경우 전체 평가 케이스를 삭제합니다.

![adk-eval-case.gif](../assets/adk-eval-case.gif)

#### 3단계: 사용자 지정 메트릭으로 평가 실행

1. 평가 세트에서 하나 이상의 테스트 케이스를 선택합니다.
2. **평가 실행**을 클릭합니다. **평가 메트릭** 대화 상자가 나타납니다.
3. 대화 상자에서 슬라이더를 사용하여 다음의 임계값을 구성합니다.
    * **도구 궤적 평균 점수**
    * **응답 일치 점수**
4. **시작**을 클릭하여 사용자 지정 기준을 사용하여 평가를 실행합니다. 평가 기록에는 각 실행에 사용된 메트릭이 기록됩니다.

![adk-eval-config.gif](../assets/adk-eval-config.gif)

#### 4단계: 결과 분석

실행이 완료되면 결과를 분석할 수 있습니다.

* **실행 실패 분석**: **통과** 또는 **실패** 결과를 클릭합니다. 실패의 경우 `실패` 레이블 위로 마우스를 가져가면 **실제 출력과 예상 출력**의 나란히 비교와 실패를 유발한 점수를 볼 수 있습니다.

### 추적 보기로 디버깅

ADK 웹 UI에는 에이전트 동작을 디버깅하기 위한 강력한 **추적** 탭이 포함되어 있습니다. 이 기능은 평가 중뿐만 아니라 모든 에이전트 세션에서 사용할 수 있습니다.

**추적** 탭은 에이전트의 실행 흐름을 자세하고 대화형으로 검사하는 방법을 제공합니다. 추적은 사용자 메시지별로 자동으로 그룹화되어 이벤트 체인을 쉽게 따라갈 수 있습니다.

각 추적 행은 대화형입니다.

* 추적 행 위로 마우스를 가져가면 채팅 창에서 해당 메시지가 강조 표시됩니다.
* 추적 행을 클릭하면 네 개의 탭이 있는 자세한 검사 패널이 열립니다.
    * **이벤트**: 원시 이벤트 데이터입니다.
    * **요청**: 모델로 전송된 요청입니다.
    * **응답**: 모델에서 수신한 응답입니다.
    * **그래프**: 도구 호출 및 에이전트 논리 흐름의 시각적 표현입니다.

![adk-trace1.gif](../assets/adk-trace1.gif)
![adk-trace2.gif](../assets/adk-trace2.gif)

추적 보기의 파란색 행은 해당 상호 작용에서 이벤트가 생성되었음을 나타냅니다. 이러한 파란색 행을 클릭하면 하단 이벤트 세부 정보 패널이 열리고 에이전트의 실행 흐름에 대한 더 깊은 통찰력을 얻을 수 있습니다.

### 2. `pytest` - 프로그래밍 방식으로 테스트 실행

**`pytest`**를 사용하여 통합 테스트의 일부로 테스트 파일을 실행할 수도 있습니다.

#### 예제 명령

```shell
pytest tests/integration/
```

#### 예제 테스트 코드

다음은 단일 테스트 파일을 실행하는 `pytest` 테스트 케이스의 예입니다.

```py
from google.adk.evaluation.agent_evaluator import AgentEvaluator
import pytest

@pytest.mark.asyncio
async def test_with_single_test_file():
    """세션 파일을 통해 에이전트의 기본 기능을 테스트합니다."""
    await AgentEvaluator.evaluate(
        agent_module="home_automation_agent",
        eval_dataset_file_path_or_dir="tests/integration/fixture/home_automation_agent/simple_test.test.json",
    )
```

이 접근 방식을 사용하면 에이전트 평가를 CI/CD 파이프라인 또는 더 큰 테스트 스위트에 통합할 수 있습니다. 테스트에 대한 초기 세션 상태를 지정하려면 세션 세부 정보를 파일에 저장하고 `AgentEvaluator.evaluate` 메서드에 전달하면 됩니다.

### 3. `adk eval` - CLI를 통해 평가 실행

명령줄 인터페이스(CLI)를 통해 평가 세트 파일의 평가를 실행할 수도 있습니다. 이것은 UI에서 실행되는 것과 동일한 평가를 실행하지만 자동화에 도움이 됩니다. 즉, 이 명령을 일반 빌드 생성 및 확인 프로세스의 일부로 추가할 수 있습니다.

다음은 명령입니다.

```shell
adk eval \
    <AGENT_MODULE_FILE_PATH> \
    <EVAL_SET_FILE_PATH> \
    [--config_file_path=<PATH_TO_TEST_JSON_CONFIG_FILE>] \
    [--print_detailed_results]
```

예를 들어:

```shell
adk eval \
    samples_for_testing/hello_world \
    samples_for_testing/hello_world/hello_world_eval_set_001.evalset.json
```

다음은 각 명령줄 인수에 대한 세부 정보입니다.

* `AGENT_MODULE_FILE_PATH`: "agent"라는 이름의 모듈이 포함된 `__init__.py` 파일의 경로입니다. "agent" 모듈에는 `root_agent`가 포함되어 있습니다.
* `EVAL_SET_FILE_PATH`: 평가 파일 경로입니다. 하나 이상의 평가 세트 파일 경로를 지정할 수 있습니다. 각 파일에 대해 기본적으로 모든 평가가 실행됩니다. 평가 세트에서 특정 평가만 실행하려면 먼저 쉼표로 구분된 평가 이름 목록을 만든 다음 콜론 `:`으로 구분하여 평가 세트 파일 이름에 접미사로 추가합니다.
* 예: `sample_eval_set_file.json:eval_1,eval_2,eval_3`
  `이렇게 하면 sample_eval_set_file.json에서 eval_1, eval_2 및 eval_3만 실행됩니다.`
* `CONFIG_FILE_PATH`: 구성 파일 경로입니다.
* `PRINT_DETAILED_RESULTS`: 콘솔에 자세한 결과를 인쇄합니다.
