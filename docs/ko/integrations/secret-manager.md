---
catalog_title: Google Cloud Secret Manager
catalog_description: LLM에 노출하지 않고 런타임에 보안 비밀번호(secret)를 안전하게 가져옵니다
catalog_icon: /integrations/assets/secret_manager.png
catalog_tags: ["google"]
---

# ADK용 Secret Manager 연동

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v1.29.0</span>
</div>

[Secret Manager](https://docs.cloud.google.com/secret-manager/docs/overview) 연동은 ADK 에이전트가 런타임에 민감한 자격 증명(예: API 키, 데이터베이스 패스워드, 개인 키)을 안전하게 가져올 수 있는 표준 인터페이스를 제공합니다. 이 방식을 사용하면 소스 코드에 민감한 정보를 하드코딩하지 않고, LLM의 컨텍스트 윈도우, 대화 기록 또는 관측성(observability) 로그에 유출되지 않도록 안전하게 보호할 수 있습니다.

## 주요 사용 사례

- **적시(Just-in-time) 도구 권한 부여**: 에이전트 초기화 코드에 정적 API 키를 저장하는 방식은 보안상 취약합니다. 이 연동을 사용하면 ADK 에이전트가 런타임에 Secret Manager에서 자격 증명을 동적으로 가져와 필요할 때 온디맨드로 키를 메모리에 로드할 수 있습니다.
- **안전한 멀티 테넌트 워크플로**: 프론트엔드에서 원시(raw) 사용자 토큰을 직접 전달하지 않도록 에이전트가 사용자 ID를 특정 Secret Manager 리소스에 매핑할 수 있습니다. `before_agent_callback` 훅이 사용자의 보안 비밀번호를 동적으로 가져와 `session.state`의 OAuth 토큰을 안전하게 복원합니다.
- **암호화된 시스템 작업**: 데이터베이스 폴링과 같은 백그라운드 시스템 작업은 도구 로직 내부에서 Secret Manager로부터 직접 자격 증명을 가져옵니다. 이를 통해 패스워드가 LLM의 대화 기록에 유입되는 것을 방지하고 모델에는 실행 요약만 전달합니다.

## 사전 요구사항

- **필수 소프트웨어 버전**: ADK Python 버전 v1.29.0 이상
- **필수 계정 / API**: [**Secret Manager API**](https://docs.cloud.google.com/secret-manager/docs/configuring-secret-manager) 및 **Agent Development Kit API**가 활성화된 [Google Cloud 프로젝트](https://docs.cloud.google.com/resource-manager/docs/creating-managing-projects).

다음 설정 단계를 완료하세요:

1.  [ADK로 에이전트를 설정합니다](/get-started/).
2.  Secret Manager에서 [보안 비밀번호(secret)를 생성](https://docs.cloud.google.com/secret-manager/docs/creating-and-accessing-secrets)(예: API 키)합니다.
3.  에이전트 ID에 [`Secret Manager Secret Accessor`](https://docs.cloud.google.com/iam/docs/roles-permissions/secretmanager#secretmanager.secretAccessor) IAM 역할을 부여합니다.

## 설치

```bash
pip install "google-adk[extensions]"
```

## 에이전트와 함께 사용하기

```python
import os

from google.adk import Agent
from google.adk.integrations.secret_manager.secret_client import SecretManagerClient

# 글로벌 Secret Manager에서 보안 비밀번호 가져오기
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
secret_id = os.environ.get("ADK_TEST_SECRET_ID")
secret_version = os.environ.get("ADK_TEST_SECRET_VERSION", "latest")

if not project_id or not secret_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT and ADK_TEST_SECRET_ID environment variables must be set.")

resource_name = f"projects/{project_id}/secrets/{secret_id}/versions/{secret_version}"

print("Fetching secret from global Secret Manager...")
# Secret Manager 클라이언트 초기화 (글로벌)
client = SecretManagerClient()

# 보안 비밀번호 가져오기
try:
    secret_payload = client.get_secret(resource_name)
    print("Successfully fetched secret.")
    # 이제 필요에 따라 에이전트나 그 도구에서 secret_payload를 사용할 수 있습니다.
except Exception as e:
    print(f"Error fetching secret: {e}")
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
- [Secret Manager 공식 문서](https://docs.cloud.google.com/secret-manager/docs/overview).
- [ADK GitHub 저장소](https://github.com/google/adk-python).
