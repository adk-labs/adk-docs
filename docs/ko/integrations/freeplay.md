# Freeplay를 사용한 에이전트 관찰 가능성 및 평가

[Freeplay](https://freeplay.ai/)는 AI 에이전트를 구축하고 최적화하기 위한 엔드투엔드 워크플로우를 제공하며 ADK와 통합될 수 있습니다. Freeplay를 사용하면 전체 팀이 쉽게 협업하여 에이전트 지침(프롬프트)을 반복하고, 다양한 모델과 에이전트 변경 사항을 실험 및 비교하고, 오프라인 및 온라인에서 평가를 실행하여 품질을 측정하고, 프로덕션을 모니터링하고, 데이터를 직접 검토할 수 있습니다.

Freeplay의 주요 이점:

* **간단한 관찰 가능성** - 쉬운 사람의 검토를 위해 에이전트, LLM 호출 및 도구 호출에 중점을 둡니다.
* **온라인 평가/자동 채점기** - 프로덕션에서 오류를 감지합니다.
* **오프라인 평가 및 실험 비교** - 배포 전에 변경 사항을 테스트합니다.
* **프롬프트 관리** - Freeplay 플레이그라운드에서 코드로 직접 변경 사항을 푸시하는 것을 지원합니다.
* **사람 검토 워크플로우** - 오류 분석 및 데이터 주석에 대한 협업을 위합니다.
* **강력한 UI** - 도메인 전문가가 엔지니어와 긴밀하게 협업할 수 있도록 합니다.

Freeplay와 ADK는 서로를 보완합니다. ADK는 강력하고 표현력이 풍부한 에이전트 오케스트레이션 프레임워크를 제공하는 반면 Freeplay는 관찰 가능성, 프롬프트 관리, 평가 및 테스트를 위해 연결됩니다. Freeplay와 통합하면 Freeplay UI 또는 코드에서 프롬프트와 평가를 업데이트할 수 있으므로 팀의 모든 사람이 기여할 수 있습니다.

데모를 보려면 [여기를 클릭](https://www.loom.com/share/82f41ffde94949beb941cb191f53c3ec?sid=997aff3c-daa3-40ab-93a9-fdaf87ea2ea1)하십시오.

## 시작하기

다음은 Freeplay 및 ADK 시작 가이드입니다. 전체 샘플 ADK 에이전트 리포지토리는 [여기](https://github.com/228Labs/freeplay-google-demo)에서 찾을 수 있습니다.

### Freeplay 계정 만들기

무료 [Freeplay 계정](https://freeplay.ai/signup)에 가입하십시오.

계정을 만든 후 다음 환경 변수를 정의할 수 있습니다.

```
FREEPLAY_PROJECT_ID=
FREEPLAY_API_KEY=
FREEPLAY_API_URL=
```

### Freeplay ADK 라이브러리 사용

Freeplay ADK 라이브러리를 설치합니다.

```
pip install freeplay-python-adk
```

Freeplay는 관찰 가능성을 초기화할 때 ADK 애플리케이션에서 OTel 로그를 자동으로 캡처합니다.

```python
from freeplay_python_adk.client import FreeplayADK
FreeplayADK.initialize_observability()
```

또한 앱에 Freeplay 플러그인을 전달해야 합니다.

```python
from app.agent import root_agent
from freeplay_python_adk.freeplay_observability_plugin import FreeplayObservabilityPlugin
from google.adk.runners import App

app = App(
    name="app",
    root_agent=root_agent,
    plugins=[FreeplayObservabilityPlugin()],
)

__all__ = ["app"]
```

이제 평소와 같이 ADK를 사용할 수 있으며 관찰 가능성 섹션에서 Freeplay로 흐르는 로그를 볼 수 있습니다.

## 관찰 가능성

Freeplay의 관찰 가능성 기능은 프로덕션에서 에이전트가 어떻게 작동하는지에 대한 명확한 보기를 제공합니다. 개별 에이전트 추적을 자세히 살펴 각 단계를 이해하고 문제를 진단할 수 있습니다.

![추적 세부 정보](https://228labs.com/freeplay-google-demo/images/trace_detail.png)

Freeplay의 필터링 기능을 사용하여 관심 있는 모든 세그먼트에서 데이터를 검색하고 필터링할 수도 있습니다.

![필터](https://228labs.com/freeplay-google-demo/images/filter.png)

## 프롬프트 관리(선택 사항)

Freeplay는 다양한 프롬프트 버전을 버전 관리하고 테스트하는 프로세스를 단순화하는 [기본 프롬프트 관리](https://docs.freeplay.ai/docs/managing-prompts)를 제공합니다. Freeplay UI에서 ADK 에이전트 지침 변경 사항을 실험하고, 다양한 모델을 테스트하고, 기능 플래그와 유사하게 업데이트를 코드로 직접 푸시할 수 있습니다.

ADK와 함께 Freeplay의 프롬프트 관리 기능을 활용하려면 Freeplay ADK 에이전트 래퍼를 사용해야 합니다. `FreeplayLLMAgent`는 ADK의 기본 `LlmAgent` 클래스를 확장하므로 프롬프트를 에이전트 지침으로 하드 코딩하는 대신 Freeplay 애플리케이션에서 프롬프트를 버전 관리할 수 있습니다.

먼저 프롬프트 -> 프롬프트 템플릿 만들기로 이동하여 Freeplay에서 프롬프트를 정의합니다.

![프롬프트](https://228labs.com/freeplay-google-demo/images/prompt.png)

프롬프트 템플릿을 만들 때 다음 섹션에 설명된 대로 3가지 요소를 추가해야 합니다.

### 시스템 메시지

이것은 코드의 "지침" 섹션에 해당합니다.

### 에이전트 컨텍스트 변수

시스템 메시지 하단에 다음을 추가하면 진행 중인 에이전트 컨텍스트가 전달될 변수가 생성됩니다.

```python
{{agent_context}}
```

### 기록 블록

새 메시지를 클릭하고 역할을 '기록'으로 변경합니다. 이렇게 하면 과거 메시지가 있을 때 전달됩니다.

![프롬프트 편집기](https://228labs.com/freeplay-google-demo/images/prompt_editor.png)

이제 코드에서 ```FreeplayLLMAgent```를 사용할 수 있습니다.

```python
from freeplay_python_adk.client import FreeplayADK
from freeplay_python_adk.freeplay_llm_agent import (
    FreeplayLLMAgent,
)

FreeplayADK.initialize_observability()

root_agent = FreeplayLLMAgent(
    name="social_product_researcher",
    tools=[tavily_search],
)
```

```social_product_researcher```가 호출되면 Freeplay에서 프롬프트를 검색하고 적절한 입력 변수로 형식을 지정합니다.

## 평가

Freeplay를 사용하면 Freeplay 웹 애플리케이션에서 [평가](https://docs.freeplay.ai/docs/evaluations)를 정의, 버전 관리 및 실행할 수 있습니다. 평가 -> "새 평가"로 이동하여 프롬프트 또는 에이전트에 대한 평가를 정의할 수 있습니다.

![Freeplay에서 새 평가 만들기](https://228labs.com/freeplay-google-demo/images/eval_create.png)

이러한 평가는 온라인 모니터링 및 오프라인 평가 모두에 대해 실행되도록 구성할 수 있습니다. 오프라인 평가용 데이터 세트는 Freeplay에 업로드하거나 로그 예제에서 저장할 수 있습니다.

## 데이터 세트 관리

Freeplay로 데이터가 흐르기 시작하면 이러한 로그를 사용하여 반복적으로 테스트할 [데이터 세트](https://docs.freeplay.ai/docs/datasets)를 구축하기 시작할 수 있습니다. 프로덕션 로그를 사용하여 골든 데이터 세트 또는 변경 사항을 적용할 때 테스트하는 데 사용할 수 있는 실패 사례 모음을 만듭니다.

![테스트 케이스 저장](https://228labs.com/freeplay-google-demo/images/save_test_case.png)

## 일괄 테스트

에이전트를 반복하면서 [프롬프트](https://docs.freeplay.ai/docs/component-level-test-runs) 및 [엔드투엔드](https://docs.freeplay.ai/docs/end-to-end-test-runs) 에이전트 수준 모두에서 일괄 테스트(즉, 오프라인 실험)를 실행할 수 있습니다. 이를 통해 여러 다른 모델 또는 프롬프트 변경 사항을 비교하고 전체 에이전트 실행에서 변경 사항을 정면으로 정량화할 수 있습니다.

ADK를 사용하여 Freeplay에서 일괄 테스트를 실행하는 코드 예제는 [여기](https://github.com/228Labs/freeplay-google-demo/blob/main/examples/example_test_run.py)에 있습니다. Google ADK를 사용하여 Freeplay에서 일괄 테스트를 실행하는 코드 예제는 [여기](https://github.com/228Labs/freeplay-google-demo/blob/main/examples/example_test_run.py)에 있습니다.

## 지금 가입

[Freeplay](https://freeplay.ai/)로 이동하여 계정에 가입하고 [여기](https://github.com/228Labs/freeplay-google-demo)에서 전체 Freeplay <> ADK 통합을 확인하십시오.
