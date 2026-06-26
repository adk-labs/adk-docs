---
catalog_title: Google Cloud Storage
catalog_description: Google Cloud Storage 버킷 및 객체에 접근하고 작업을 수행합니다
catalog_icon: /integrations/assets/gcs.png
catalog_tags: ["data", "google"]
---

# Google Cloud Storage (GCS)

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v2.3.0</span>
</div>

`GCSToolset` 및 `GCSAdminToolset`을 사용하면 ADK 에이전트가 [Google Cloud Storage (GCS)](https://cloud.google.com/storage)와 상호작용하여 버킷을 관리하고 객체를 읽고 쓸 수 있습니다.

## 주요 사용 사례

- **객체 관리 (Object Management)**: GCS 객체의 읽기, 다운로드, 생성, 업로드, 목록 조회, 메타데이터 확인 및 삭제 작업을 수행합니다.
- **버킷 관리 (Bucket Management)**: 클라우드 스토리지 버킷의 목록을 조회하고, 신규 버킷을 생성하며, 버전 관리(versioning) 또는 균일한 버킷 수준 액세스(uniform bucket-level access) 활성화와 같은 구성을 변경하고, 버킷을 삭제합니다.
- **데이터 통합 (Data Integration)**: 에이전트 워크플로의 일부로 클라우드 스토리지 객체를 동적으로 사용하여 파일 처리 및 수집(ingestion)을 수행합니다.

## 사전 요구사항

- 대상 Google Cloud 프로젝트에서 **Google Cloud Storage API를 활성화**해야 합니다.
- **IAM 권한**: 인증된 주체(애플리케이션 기본 자격 증명, 서비스 계정 또는 사용자)는 GCS 버킷 및 객체 작업을 수행하는 데 필요한 `roles/storage.objectAdmin` 및 `roles/storage.admin`을 포함한 올바른 권한을 가지고 있어야 합니다.
- Google Cloud 프로젝트 ID가 구성되어 있어야 합니다.

## 인증

`GCSToolset` 및 `GCSAdminToolset`은 `GCSCredentialsConfig`를 통해 여러 인증 방식을 지원합니다:

### 애플리케이션 기본 자격 증명 (Application Default Credentials)

로컬 개발 및 Agent Runtime, Cloud Run, GKE를 포함한 Google Cloud로의 배포 시 권장되는 방식입니다.

```python
import google.auth
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# 애플리케이션 기본 자격 증명 로드
credentials, _ = google.auth.default()

# 툴셋 구성
credentials_config = GCSCredentialsConfig(credentials=credentials)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

### 서비스 계정 (Service Account)

서비스 계정 키 파일에서 자격 증명을 제공할 수 있도록 지원합니다.

```python
import google.auth
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# 서비스 계정 자격 증명 로드
credentials, _ = google.auth.load_credentials_from_file('path/to/key.json')

# 툴셋 구성
credentials_config = GCSCredentialsConfig(credentials=credentials)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

### 외부 액세스 토큰 (External Access Token)

OAuth2 흐름 또는 외부 ID 제공업체를 통해 최종 사용자를 대리하여 작업을 수행할 때 사용합니다.

```python
from google.oauth2.credentials import Credentials
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# 외부 OAuth 흐름을 통해 'user_token'을 획득했다고 가정
credentials = Credentials(token=user_token)

# 툴셋 구성
credentials_config = GCSCredentialsConfig(credentials=credentials)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

### 외부 인증 제공업체 (External Auth Providers)

Gemini Enterprise와 같이 토큰이 환경이나 플랫폼에 의해 외부에서 관리되는 플랫폼용입니다.

```python
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# 세션 상태에서 액세스 토큰을 조회하는 데 사용되는 키
credentials_config = GCSCredentialsConfig(
    external_access_token_key="YOUR_AUTH_ID"
)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

### 대화형 인증 (ADK Web)

`adk web` 인터페이스를 사용한 대화형 세션에서 OAuth 2.0 로그인 흐름을 실행할 때 사용합니다.

```python
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# OAuth 2.0 클라이언트 ID 및 보안 비밀번호(Secret) 제공
credentials_config = GCSCredentialsConfig(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
gcs_toolset = GCSToolset(credentials_config=credentials_config)
```

## 에이전트와 함께 사용하기

다음 예시는 자격 증명을 구성하고 쓰기 액세스 권한이 활성화된 스토리지 툴셋의 인스턴스를 생성하는 방법을 보여줍니다.

```python
import google.auth
from google.adk.agents.llm_agent import LlmAgent
from google.adk.integrations.gcs import GCSToolset
from google.adk.integrations.gcs.settings import GCSToolSettings, Capabilities
from google.adk.integrations.gcs.gcs_credentials import GCSCredentialsConfig

# 1. 애플리케이션 기본 자격 증명(ADC) 로드
application_default_credentials, _ = google.auth.default()

# 2. 자격 증명 구성
credentials_config = GCSCredentialsConfig(
    credentials=application_default_credentials
)

# 3. 설정 구성 (읽기 및 쓰기 작업 허용)
tool_settings = GCSToolSettings(capabilities=[Capabilities.READ_WRITE])

# 4. GCS 툴셋 인스턴스 생성
gcs_toolset = GCSToolset(
    credentials_config=credentials_config,
    gcs_tool_settings=tool_settings
)

# 5. 툴셋을 사용하여 LLM 에이전트 정의
agent = LlmAgent(
    model="gemini-2.5-flash",
    name="gcs_agent",
    description="Agent for interacting with GCS buckets and objects.",
    instruction="""
        You are a storage assistant agent. Use the GCS tools to answer questions,
        list objects, upload files, or perform admin tasks as requested.
    """,
    tools=[gcs_toolset]
)
```

## 사용 가능한 도구

GCS 연동은 크게 두 가지 툴셋으로 기능을 나눕니다:

### GCS 스토리지 도구 (`GCSToolset`)

도구 | 설명
---- | -----------
`gcs_get_bucket` | GCS 버킷에 대한 메타데이터 정보를 가져옵니다.
`gcs_list_objects` | GCS 버킷의 객체 이름을 조회합니다. 선택적으로 접두사 필터링 및 페이지네이션을 지원합니다.
`gcs_get_object_metadata` | 특정 GCS 객체(blob)의 메타데이터 속성을 가져옵니다.
`gcs_create_object` | 메모리 내의 문자열 데이터 또는 로컬 파일 업로드를 통해 버킷에 새로운 객체(blob)를 생성합니다.
`gcs_get_object_data` | GCS 객체의 콘텐츠를 문자열로 가져오거나 로컬 파일로 직접 다운로드합니다.
`gcs_delete_objects` | 버킷에서 여러 GCS 객체(blob)를 삭제합니다.

### GCS 관리 도구 (`GCSAdminToolset`)

도구 | 설명
---- | -----------
`gcs_list_buckets` | Google Cloud 프로젝트의 GCS 버킷 이름을 조회합니다.
`gcs_create_bucket` | 특정 위치에 새로운 GCS 버킷을 생성합니다.
`gcs_update_bucket` | GCS 버킷의 속성(예: 버전 관리 또는 균일한 버킷 수준 액세스)을 업데이트합니다.
`gcs_delete_bucket` | GCS 버킷을 삭제합니다 (버킷이 먼저 비어 있어야 합니다).

## 샘플 에이전트

상세한 인증 구성이 포함된 GCS 기반 에이전트의 즉시 실행 가능한 전체 예시는 다음을 참조하세요:

- [GCS 스토리지 샘플 에이전트](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/gcs)
- [GCS 관리 샘플 에이전트](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/gcs_admin)

## 리소스

- [Google Cloud Storage 공식 문서](https://cloud.google.com/storage/docs)
- [GitHub 저장소](https://github.com/google/adk-python)
