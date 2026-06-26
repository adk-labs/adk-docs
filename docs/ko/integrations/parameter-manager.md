---
catalog_title: Google Cloud Parameter Manager
catalog_description: ADK 에이전트를 위해 런타임 구성 매개변수 및 보안 비밀번호(secret)를 안전하게 관리하고 가져옵니다.
catalog_icon: /integrations/assets/parameter_manager.png
catalog_tags: ["google"]
---

# ADK를 위한 Parameter Manager 연동

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v1.30.0</span>
</div>

[Google Cloud Parameter Manager](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/overview) 연동은 Agent Development Kit (ADK) 에이전트가 Google Cloud Parameter Manager 서비스에 연결하여 런타임에 렌더링된 매개변수 값을 가져올 수 있는 표준 인터페이스를 제공합니다. 이 모듈을 사용하면 Google Cloud Parameter Manager 서비스를 에이전트 지시사항(instruction) 및 도구 구성의 단일 소스(single source of truth)로 사용할 수 있습니다.

## 주요 사용 사례

Parameter Manager 연동은 다음과 같은 작업을 지원합니다:

*   **동적 지시사항 업데이트 (Dynamic instruction updates)**: 코드를 다시 배포하지 않고도 프롬프트 주입 공격을 차단하고, 필수 면책 조항(disclaimer) 리소스를 업데이트하거나, 에이전트의 톤을 즉시 조정할 수 있도록 매개변수를 실시간으로 발행할 수 있습니다.
*   **기능 플래그 및 매개변수 관리 (Feature flag and parameter management)**: 구성을 JSON 페이로드로 저장하고 도구 컨텍스트를 통해 가져와 쿼리 속도를 낮추거나, 테스트용 API 엔드포인트와 프로덕션용 API 엔드포인트 간의 전환을 수행할 수 있습니다.
*   **입출력 쌍을 통한 정확도 향상 (Accuracy improvement with input and output pairs)**: 퓨샷(few-shot) 예시를 YAML 파일로 저장하고 이를 세션 상태에 로드하여 에이전트의 성능을 점진적으로 향상시킬 수 있습니다.
*   **도구 실시간 권한 부여 (Just-in-time tool authorization)**: 초기화 코드에 안전하지 않은 정적 API 키를 사용하는 대신, 필요에 따라 보안 비밀번호(secret)를 메모리에 실시간으로 로드할 수 있습니다.
*   **보안 다중 테넌트 워크플로 (Secure multi-tenant workflows)**: 사용자에 매핑되는 Parameter Manager ID를 저장하고 콜백을 사용하여 확인된 OAuth 토큰으로 세션 상태를 복원할 수 있습니다.
*   **암호화된 시스템 작업 (Encrypted system tasks)**: 백그라운드 폴링 작업 중에 메인 데이터베이스 비밀번호가 LLM 대화 기록에 노출되는 것을 방지합니다.
*   **다중 지역 배포 (Multi-region deployments)**: 전역 배포 시 공유 로직을 유지하면서, 지역별 Parameter Manager 재정의(override)를 사용하여 현지 통화 및 연락처 정보를 적용할 수 있습니다.

## 사전 요구사항

연동을 구성하기 전에 다음 요구사항을 충족해야 합니다:

- **필수 소프트웨어 버전**: ADK Python 버전 v1.30.0 이상
- **필수 계정 / API**: [**Parameter Manager API**](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/prepare-environment#enable_api), [**Secret Manager API**](https://docs.cloud.google.com/secret-manager/docs/configuring-secret-manager), 및 **Agent Development Kit API**가 활성화된 [Google Cloud 프로젝트](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects).

다음 설정 단계를 완료하세요:

1.  [ADK로 에이전트를 설정합니다](/get-started/).
2.  [매개변수를 생성합니다](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/create-parameter).
3.  에이전트 ID에 [Parameter Manager Parameter Accessor](https://docs.cloud.google.com/iam/docs/roles-permissions/parametermanager#parametermanager.parameterAccessor) IAM 역할(`roles/parametermanager.parameterAccessor`)을 부여합니다. 이 역할은 에이전트가 런타임에 매개변수 구성을 렌더링할 수 있도록 지원합니다.
4.  매개변수에 임베디드 비밀번호가 포함된 경우, 매개변수 리소스에 [Secret Manager Secret Accessor](https://docs.cloud.google.com/iam/docs/roles-permissions/secretmanager#secretmanager.secretAccessor) 역할(`roles/secretmanager.secretAccessor`)을 부여합니다. 이 교차 서비스 권한을 통해 Parameter Manager가 에이전트를 대리하여 참조된 비밀번호를 확인(resolve)할 수 있습니다. 자세한 내용은 [매개변수에 Secret Manager Secret Accessor 역할 부여](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/reference-secrets-in-parameter#grant_the_secret_manager_secret_accessor_role_to_the_parameter)를 참조하세요.

## 설치

ADK 확장 패키지를 설치하여 Parameter Manager 연동을 활성화합니다:

```bash
pip install "google-adk[extensions]"
```

## 에이전트와 함께 사용하기

다음 예시는 글로벌 또는 리전 엔드포인트를 사용하여 ADK 에이전트 내에서 매개변수를 안전하게 가져오는 완전하고 실행 가능한 코드를 보여줍니다.

### 글로벌 매개변수

```python
import os

from google.adk import Agent
from google.adk.integrations.parameter_manager.parameter_client import ParameterManagerClient

# 글로벌 Parameter Manager에서 매개변수 가져오기
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
parameter_id = os.environ.get("ADK_TEST_PARAMETER_ID")
parameter_version = os.environ.get("ADK_TEST_PARAMETER_VERSION", "latest")

if not project_id or not parameter_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT and ADK_TEST_PARAMETER_ID environment variables must be set.")

resource_name = f"projects/{project_id}/locations/global/parameters/{parameter_id}/versions/{parameter_version}"

print("Fetching parameter from global Parameter Manager...")
# Parameter Manager 클라이언트 초기화
client = ParameterManagerClient()

# 매개변수 가져오기
try:
    parameter_payload = client.get_parameter(resource_name)
    print("Successfully fetched parameter.")
except Exception as e:
    print(f"Error fetching parameter: {e}")
    raise e

# 에이전트 초기화
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)

print("Agent initialized successfully.")
```

### 리전 매개변수

```python
import os

from google.adk import Agent
from google.adk.integrations.parameter_manager.parameter_client import ParameterManagerClient

# 리전 Parameter Manager에서 매개변수 가져오기
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
location = os.environ.get("GOOGLE_CLOUD_PROJECT_LOCATION")
parameter_id = os.environ.get("ADK_TEST_PARAMETER_ID")
parameter_version = os.environ.get("ADK_TEST_PARAMETER_VERSION", "latest")

if not project_id or not location or not parameter_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_PROJECT_LOCATION, and ADK_TEST_PARAMETER_ID environment variables must be set.")

resource_name = f"projects/{project_id}/locations/{location}/parameters/{parameter_id}/versions/{parameter_version}"

print(f"Fetching parameter from regional Parameter Manager ({location})...")
# Parameter Manager 클라이언트 초기화 (리전)
client = ParameterManagerClient(location=location)

# 매개변수 가져오기
try:
    parameter_payload = client.get_parameter(resource_name)
    print("Successfully fetched parameter.")
except Exception as e:
    print(f"Error fetching parameter: {e}")
    raise e

# 에이전트 초기화
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)

print("Agent initialized successfully.")
```

## 리소스

-   [Parameter Manager 공식 문서](https://docs.cloud.google.com/secret-manager/parameter-manager/docs/overview)
-   [ADK GitHub 저장소](https://github.com/google/adk-python)
-   [퓨샷 예시 포함하기](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/prompts/few-shot-examples)
