---
catalog_title: MLflow Scorers
catalog_description: 에이전트 평가를 위해 ADK 평가기(evaluator)를 MLflow 스코어러(scorer)로 사용하세요
catalog_icon: /integrations/assets/mlflow.png
catalog_tags: ["evaluation"]
---

# ADK 에이전트를 위한 MLflow 스코어러 (MLflow scorers)

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python</span>
</div>

[MLflow](https://mlflow.org/docs/latest/genai/eval-monitor/)는 5개의 ADK 평가기(evaluator)를 타사 스코어러(third-party scorer)로 래핑하여, 모든 `mlflow.genai.evaluate()` 실행 내에서 ADK의 궤적 일치(trajectory matching), ROUGE 응답 유사도 및 LLM 판단(LLM-judge) 메트릭을 사용할 수 있도록 지원합니다. 이 연동은 ADK의 `TrajectoryEvaluator`, `RougeEvaluator`, `FinalResponseMatchV2Evaluator`, `SafetyEvaluatorV1`, `HallucinationsV1Evaluator`를 포함합니다.

ADK 에이전트를 트레이싱하고 있다면, 한 줄의 코드로 OTel 자동 트레이싱을 설정하는 [MLflow Tracing 연동](/integrations/mlflow-tracing/)을 참조하세요. 아래의 결정론적 스코어러는 이러한 트레이스로부터 직접 도구 호출 기록을 읽어옵니다.

## 주요 사용 사례

- **도구 궤적 평가 (Tool trajectory evaluation)**: 에이전트가 올바른 도구를 올바른 순서로 호출했는지 `EXACT`, `IN_ORDER`, 또는 `ANY_ORDER` 일치 방식으로 검증합니다.
- **응답 유사도 (Response similarity)**: ROUGE-1 F-measure를 사용하여 기준 답변에 대해 에이전트의 최종 응답 점수를 매깁니다.
- **LLM 판단 응답 품질 (LLM-judged response quality)**: 다수결 투표 방식을 통해 Gemini가 에이전트의 응답과 예상 응답이 의미론적으로 일치하는지 평가하도록 합니다.
- **환각 감지 (Hallucination detection)**: Gemini를 사용하여 에이전트의 응답에 왜곡되거나 조작된 사실이 포함되어 있는지 평가합니다.
- **안전성 검사 (Safety checks)**: 별도의 판단 모델을 관리하지 않고 Vertex AI의 사전 구축된 SAFETY 메트릭을 사용하여 안전하지 않은 출력을 플래깅합니다.
- **평가 방식 혼합 (Mix-and-match scoring)**: 단일 `mlflow.genai.evaluate()` 호출에서 결정론적 스코어러와 LLM 판단을 함께 실행하여, 비용이 많이 드는 판단 모델 호출 하위에 저렴한 구조적 검사들을 배치합니다.

## 사전 요구사항

- 전체 스코어러 세트를 사용하려면 MLflow 3.13 이상이 필요합니다. MLflow 3.11은 2개의 결정론적 스코어러를 제공하며, 3개의 LLM 판단 스코어러는 3.13에서 제공됩니다.
- 환경에 ADK가 설치되어 있어야 합니다.
- LLM 판단 스코어러의 경우: `GEMINI_API_KEY`(Gemini Developer API) 또는 Google Cloud 프로젝트 자격 증명(Vertex AI). `Safety`는 관리형 메트릭에 위임되므로 항상 Vertex AI 환경이 필요합니다.

## 종속성 설치

```bash
pip install "mlflow>=3.13" google-adk
```

## 사용 가능한 스코어러

평가 방식에 따라 그룹화된 5개의 MLflow 스코어러:

| 스코어러 | 평가 항목 | 래핑 대상 |
| --- | --- | --- |
| `ToolTrajectory` | 에이전트가 올바른 도구를 올바른 순서로 호출했는지 여부 | `TrajectoryEvaluator` |
| `ResponseMatch` | 실제 응답과 예상 응답 간의 어휘적 유사성 (ROUGE-1 F-measure) | `RougeEvaluator` |
| `ResponseEvaluation` | 최종 응답이 예상 응답과 의미론적으로 일치하는지 여부 (LLM judge) | `FinalResponseMatchV2Evaluator` |
| `Safety` | 응답에 안전하지 않은 콘텐츠가 포함되어 있는지 여부 | `SafetyEvaluatorV1` (Vertex AI 관리형) |
| `Hallucination` | 응답에 환각(왜곡된) 콘텐츠가 포함되어 있는지 여부 (LLM judge) | `HallucinationsV1Evaluator` |

`ToolTrajectory`와 `ResponseMatch`는 마이크로초 단위로 실행되며 API 비용이 발생하지 않습니다. `ResponseEvaluation`과 `Hallucination`은 5회 샘플 다수결 투표 방식을 통해 기본 Gemini Flash 판단 모델을 호출하며, 모델과 샘플 횟수 모두 구성 가능합니다. 단, `Safety`는 예외적으로 자체 모델 선택을 관리하는 Vertex AI의 사전 구축된 SAFETY 메트릭을 통해 작동하므로, `model`이나 `num_samples`를 전달하면 `TypeError`가 발생합니다.

## 빠른 시작

스코어러 직접 호출:

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

print(feedback.value)            # "yes" 또는 "no"
print(feedback.metadata["score"]) # 완전 일치 시 1.0
```

또는 단일 평가 내에서 여러 스코어러를 혼합하여 구성:

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

## 도구 호출 확인(resolve) 방식

`ToolTrajectory`는 예상되는 도구 호출(`expectations["expected_tool_calls"]`)과 에이전트가 실제로 실행한 도구 호출이 모두 필요합니다. 실제 호출은 다음 순서로 확인(resolve)됩니다:

1. `expectations["actual_tool_calls"]`가 존재할 때. 도구 호출 기록을 데이터로 캡처한 오프라인 평가에 유용합니다.
2. MLflow 트레이스의 `TOOL` 스팬. 명시적인 재정의(override)가 없을 때, 스코어러는 트레이스를 따라가며 `TOOL`로 태그된 스팬에서 도구 호출을 읽어옵니다. 트레이스를 직접 전달하거나 `mlflow.genai.evaluate(predict_fn=...)`을 사용하는 온라인 평가에 해당합니다.
3. 빈 목록. 둘 다 사용할 수 없는 경우, 스코어러는 예상 목록을 빈 실제 목록과 비교하며, 이는 비어 있지 않은 예상 사항에 대해 0.0의 점수를 반환합니다.

이를 [MLflow Tracing 연동](/integrations/mlflow-tracing/)과 연결하면 완전히 온라인화된 구성을 구축할 수 있습니다: ADK는 에이전트 실행 중에 OTel 스팬을 내보내고, MLflow는 이를 수집하며, 스코어러는 명시적인 데이터 전송 없이 트레이스에서 도구 호출 기록을 읽어옵니다.

## LLM 판단(LLM-judge) 구성

`ResponseEvaluation`과 `Hallucination`은 Gemini 모델 ID, 합격/불합격 임계값, 다수결 투표를 위한 샘플 수를 취합니다:

```python
from mlflow.genai.scorers.google_adk import Hallucination, ResponseEvaluation

response_eval = ResponseEvaluation(
    model="gemini-flash-latest",
    threshold=0.5,
    num_samples=5,
)

hallucination = Hallucination(model="gemini-flash-latest", threshold=0.5)
```

모델 이름은 `gemini-flash-latest`나 `gemini-pro-latest`처럼 ADK의 `LlmRegistry`가 해석할 수 있는 이름이어야 합니다. ADK의 평가기들이 Google의 모델 레지스트리에 직접 연결되므로, `databricks`나 `openai:/gpt-4o`와 같은 MLflow 모델 URI는 여기서 지원되지 않습니다.

`Safety`는 Vertex AI의 관리형 SAFETY 메트릭을 통해 실행됩니다. 이를 위해서는 `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` 및 `gcloud auth application-default login`(또는 서비스 계정)이 필요합니다:

```python
from mlflow.genai.scorers.google_adk import Safety

safety = Safety(threshold=0.5)
```

인증 정보가 누락된 경우, LLM 판단 스코어러는 예외를 발생시키는 대신 `error` 필드가 포함된 `Feedback`을 반환합니다. 평가 실행은 계속 진행되며 샘플별로 잘못된 구성이 표시됩니다.

## 리소스

- [MLflow ADK 스코어러 문서](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/third-party/google-adk/)
- [ADK를 위한 MLflow Tracing 연동](/integrations/mlflow-tracing/)
- [ADK를 위한 MLflow AI Gateway 연동](/integrations/mlflow-gateway/)
- [ADK 평가 가이드](/evaluate/)
- [GitHub의 MLflow 저장소](https://github.com/mlflow/mlflow)
