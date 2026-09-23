---
catalog_title: Model Armor
catalog_description: Google Cloud 보안 템플릿을 기반으로 에이전트 입력 및 출력 필터링
catalog_icon: /integrations/assets/model-armor.png
catalog_tags: ["google"]
---

# ADK용 Model Armor 플러그인

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원 버전</span><span class="lst-python">Python v2.8.0</span>
</div>

[Model Armor](https://cloud.google.com/security-command-center/docs/model-armor-overview)는 프롬프트 인젝션 및 탈옥(jailbreak) 시도, 유해 콘텐츠, 민감한 데이터를 탐지하기 위해 텍스트를 검사하는 Google Cloud 서비스입니다. 템플릿이라고 하는 서버 측 정책에서 탐지할 대상을 정의하면, 서비스는 전송된 각 텍스트 조각에 대해 판정 결과를 반환합니다. `ModelArmorPlugin` 클래스는 ADK와 함께 제공되며 모델 콜백에서 해당 서비스를 호출합니다. 모델이 확인하기 전에 사용자 입력을 검사하고 전달 전 또는 전달 중에 모델 출력을 검사하여, 일치하는 콘텐츠를 안전한 메시지로 대체합니다.

## 사용 사례

- **프롬프트 인젝션 및 탈옥 방어**: 모델이 동작하기 전에 모든 사용자 턴을 프롬프트 템플릿에 대조하여 검사하므로, 탐지된 시도에 대해 에이전트가 따르는 대신 차단합니다.
- **민감한 데이터 및 유해 콘텐츠 필터링**: 모델 출력을 응답 템플릿에 대조하여 검사함으로써, 전달 전에 데이터가 유출되거나 콘텐츠 정책을 위반하는 답변을 포착합니다.
- **에이전트 전반의 일관된 정책**: `App`에 하나의 플러그인을 등록하면 [실시간 음성 에이전트](../live/guardrails.md)를 포함하여 실행되는 모든 에이전트가 동일한 검사 정책을 상속합니다.

## 전제 조건

- Model Armor API가 활성화되어 있고 최소 하나 이상의 템플릿이 생성된 Google Cloud 프로젝트. [Model Armor 문서](https://cloud.google.com/security-command-center/docs/manage-model-armor-templates)를 참고하세요.
- `gcloud auth application-default login`으로 설정된 Model Armor 액세스 권한이 있는 애플리케이션 기본 사용자 인증 정보(ADC).
- [ADK](https://adk.dev) >= 2.8.0

## 설치

```bash
pip install 'google-adk[gcp]'
```

별도의 `model-armor` 엑스트라는 없습니다. 플러그인은 ADK와 함께 제공되며, `gcp` 엑스트라가 필요한 `google-cloud-modelarmor` 클라이언트를 제공합니다.

## 에이전트와 함께 사용

검사 대상 템플릿과 함께 `App`에 플러그인을 등록합니다:

```python
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.integrations.model_armor import ModelArmorConfig
from google.adk.integrations.model_armor import ModelArmorPlugin

agent = LlmAgent(
    model="gemini-flash-latest",
    name="screened_agent",
    instruction="You are a helpful assistant.",
)

app = App(
    name="model_armor_demo",
    root_agent=agent,
    plugins=[
        ModelArmorPlugin(
            config=ModelArmorConfig(
                prompt_template_name=(
                    "projects/my-project/locations/us-central1/templates/my-prompt-template"
                ),
                response_template_name=(
                    "projects/my-project/locations/us-central1/templates/my-response-template"
                ),
            )
        )
    ],
)
```

템플릿 이름은 `projects/{project}/locations/{location}/templates/{template}` 형식의 전체 리소스 경로여야 합니다. 플러그인은 리전 엔드포인트를 선택하기 위해 경로에서 위치를 읽으므로 두 템플릿은 동일한 리전에 있어야 합니다. 플러그인을 구성할 때 짧은 이름이거나 일치하지 않는 쌍을 전달하면 `ValueError`가 발생합니다.

각 템플릿은 선택사항이며, 하나만 설정하면 해당 방향에 대해서만 검사합니다:

```python
config = ModelArmorConfig(
    prompt_template_name=(
        "projects/my-project/locations/us-central1/templates/my-prompt-template"
    ),
)
```

검사는 가장 최근의 사용자 콘텐츠와 모델의 응답에 적용됩니다. 도구 결과는 요청에 `function_response` 파트로 도달하며, 플러그인은 이를 건너뜁니다.

## 구성

| 옵션 | 기본값 | 설명 |
| :--- | :--- | :--- |
| `prompt_template_name` | `None` | 사용자 입력을 검사하는 데 사용되는 템플릿입니다. 설정하지 않으면 입력이 검사되지 않습니다. |
| `response_template_name` | `None` | 모델 출력을 검사하는 데 사용되는 템플릿입니다. 설정하지 않으면 출력이 검사되지 않습니다. |
| `input_blocked_message` | 아래 참고 | 사용자 입력이 차단될 때 표시되는 대체 텍스트입니다. |
| `output_blocked_message` | 아래 참고 | 모델 출력이 차단될 때 표시되는 대체 텍스트입니다. |
| `block_on_screening_failure` | `True` | 검사할 수 없는 콘텐츠를 차단할지 여부입니다. |

두 메시지의 기본값은 모두 `"I'm sorry, but I can't help with that request."`이며, 하나 이상의 템플릿 이름을 설정해야 합니다. 그렇지 않으면 구성에서 유효성 검사 오류가 발생합니다.

Model Armor 호출에서 예외가 발생하거나 서비스가 `SUCCESS` 판정 이외의 값을 반환하면 검사가 실패합니다. 기본값은 검사되지 않은 콘텐츠를 차단하는 것입니다. Model Armor를 사용할 수 없는 동안에도 에이전트가 응답하도록 유지하려면 `block_on_screening_failure=False`를 설정하세요.

차단된 턴에는 `custom_metadata['model_armor_blocked']`가 포함되므로 애플리케이션에서 정책 차단과 실제 답변을 구분할 수 있습니다.

## 추가 리소스

- [Model Armor 개요](https://cloud.google.com/security-command-center/docs/model-armor-overview)
- [템플릿 생성 및 관리](https://cloud.google.com/security-command-center/docs/manage-model-armor-templates)
- [플러그인](../plugins/index.md)
- [안전 및 보안](../safety/index.md)
- [실시간 에이전트 가드레일](../live/guardrails.md)
