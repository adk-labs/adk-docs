# Google Cloud 및 Agent Platform 연결

이 가이드는 ADK 에이전트를 Google Cloud Platform(GCP) 서비스, Google Cloud Agent Platform에서 실행되는 모델, 그리고 Agent Platform 서비스와 연결하고 인증하는 방법을 설명합니다.

## Google Cloud Agent Platform 설정

Google Cloud 또는 Agent Platform 서비스에 에이전트를 연결하기 전에 다음 사전 준비 사항을 완료해야 합니다.

*  **Agent Platform API** (`aiplatform.googleapis.com`)가 활성화된 Google Cloud 프로젝트.
*  [gcloud CLI](https://cloud.google.com/sdk/docs/install) 도구 설치.

## Google Cloud 인증 옵션

ADK 에이전트를 Google Cloud에 연결할 때 몇 가지 인증 옵션이 있으며, 아래 표에 요약되어 있습니다.

| 방법 | 주요 용도 | 인증 메커니즘 | 환경 |
| :--- | :--- | :--- | :--- |
| [**User Credentials (사용자 자격 증명)**](#user-credentials) | 로컬 개발 및 테스트 | `gcloud`를 통한 Application Default Credentials | 로컬 워크스테이션 |
| [**Service Account (서비스 계정)**](#service-account) | 프로덕션 배포 및 CI/CD | Google IAM 서비스 계정 키 / Workload Identity | Google Cloud (Agent Runtime, Cloud Run, GKE) 또는 외부 서버 |
| [**Express Mode (익스프레스 모드)**](#express-mode) | 빠른 프로토타이핑 및 테스트 | API 키 | 로컬 또는 클라우드 환경 |
| [**Agent Identity (에이전트 ID)**](/ko/integrations/agent-identity) | 프로덕션 배포 및 CI/CD | Google IAM 서비스 계정 키 / Workload Identity | Google Cloud (Agent Runtime, Cloud Run, GKE) |

!!! warning "경고: 자격 증명 보호"

    사용자 자격 증명, 서비스 계정 자격 증명 및 API 키는 매우 민감한 정보입니다. 자격 증명 파일이나 키를 코드베이스에 직접 커밋하지 마세요. 가능한 경우 [Google Cloud Agent Identity](/ko/integrations/agent-identity/), [Google Cloud Secret Manager](https://cloud.google.com/security/products/secret-manager) 또는 기타 유사한 보안 비밀 관리 도구를 사용하세요.

### 로컬 개발용 사용자 자격 증명 {#user-credentials}

로컬 개발 환경에서 작동하는 사용자 자격 증명 인증 방식으로 Google Cloud에 연결합니다.

1. ADK 에이전트 애플리케이션을 실행하기 *전에* Application Default Credentials(ADC)를 사용하여 로컬 워크스테이션을 인증합니다.
    ```bash
    gcloud auth application-default login
    ```
2. Agent Platform을 활성화하고 프로젝트 상세 정보를 지정하기 위해 환경 변수를 설정합니다.

    === ".env 파일"

        ```console
        # ADK 코드 프로젝트에 추가하되 소스 제어에는 포함하지 마세요.
        GOOGLE_GENAI_USE_ENTERPRISE=TRUE
        GOOGLE_CLOUD_PROJECT=your-project-id
        GOOGLE_CLOUD_LOCATION=cloud-location   # 예: us-central1
        ```

    === "터미널"

        ```bash
        export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
        export GOOGLE_CLOUD_PROJECT="your-project-id"
        export GOOGLE_CLOUD_LOCATION="cloud-location"   # 예: us-central1
        ```

!!! note "`GOOGLE_GENAI_USE_ENTERPRISE`는 이전에 `GOOGLE_GENAI_USE_VERTEXAI`였습니다"

    이 두 변수 이름은 동일한 기능을 수행합니다. 만약 `GOOGLE_GENAI_USE_ENTERPRISE`를 설정했으나 에이전트가 Agent Platform에 연결되지 않는다면 이전 버전의 ADK를 사용 중인 것입니다. 대신 `GOOGLE_GENAI_USE_VERTEXAI`를 사용하거나 더 최신 버전의 ADK로 업데이트하세요.

### 프로덕션용 서비스 계정 {#service-account}

보안이 설정된 호스팅 환경에 배포할 때는 연결 인증을 위해 서비스 계정을 사용하세요.

1. [서비스 계정(Service Account)](https://docs.cloud.google.com/iam/docs/service-account-overview)을 생성하고 `Agent Platform User` 역할을 부여합니다.
2. 배포 전략에 따라 에이전트 애플리케이션에 자격 증명을 제공합니다.
    * **Google Cloud 배포 (Agent Runtime, Cloud Run, GKE):**
        환경에서 자격 증명을 자동으로 제공합니다. 별도의 키 파일 구성이 필요하지 않습니다.
    * **외부 실행:**
        [서비스 계정 키 파일](https://cloud.google.com/iam/docs/keys-create-delete#console) (`.json`)을 생성하고 `GOOGLE_APPLICATION_CREDENTIALS` 환경 변수를 구성합니다.
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
        ```

!!! tip "Workload Identity 옵션"

    키 파일 대신 [Workload Identity](https://docs.cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)를 사용하여 서비스 계정을 인증할 수도 있습니다.

### 테스트용 Agent Platform 익스프레스 모드 {#express-mode}

Express Mode는 복잡한 gcloud 인증 없이 프로토타이핑을 위해 API 키 기반의 단순화된 설정을 제공합니다.

1. API 키를 얻기 위해 [Express Mode](https://console.cloud.google.com/expressmode)에 가입합니다.
2. 다음 환경 변수를 설정합니다.

    === ".env 파일"

        ```console
        # ADK 코드 프로젝트에 추가하되 소스 제어에는 포함하지 마세요.
        GOOGLE_GENAI_USE_ENTERPRISE=TRUE
        GOOGLE_GENAI_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
        ```

    === "터미널"

        ```bash
        export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
        export GOOGLE_GENAI_API_KEY="PASTE_YOUR_EXPRESS_MODE_API_KEY_HERE"
        ```

## Google Cloud 호스팅 모델

Google Cloud Agent Platform은 Gemini 모델, 서드파티 AI 모델, 오픈 가중치 모델 및 조직에 맞게 커스텀 튜닝된 모델을 포함하여 ADK 에이전트에 연결할 수 있는 광범위한 AI 모델을 호스팅합니다. ADK 에이전트를 Google Cloud 및 Agent Platform에 연결하면 애플리케이션 요구 사항에 맞는 AI 모델을 사용할 수 있습니다. 다음 리소스를 참고하여 프로젝트에 적합한 모델을 찾아보세요.

*   ADK 에이전트에서 [Gemini 모델](/ko/agents/models/google-gemini/)을 사용하는 방법에 대해 자세히 알아보세요.
*   ADK 에이전트와 함께 사용하기 위해 [Agent Platform 호스팅 모델](/ko/agents/models/agent-platform/)에서 서드파티 및 커스텀 모델 옵션을 확인해 보세요.
*   Google Cloud에서 사용 가능한 모델 및 모델 ID는 [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models) 설명서에서 찾을 수 있습니다.

## 추가 Google Cloud 서비스 연결

많은 Google Cloud 서비스가 ADK 에이전트로 GCP API 또는 리소스에 액세스하기 위한 인증 헬퍼와 함께 ADK 통합을 제공합니다. 자세한 내용은 다음 페이지를 참조하세요.

* [Google Cloud Application Integration](/ko/integrations/application-integration/)
* [BigQuery Toolset](/ko/integrations/bigquery/)
* [BigQuery Agent Analytics](/ko/integrations/bigquery-agent-analytics/)
* [Data Agent](/ko/integrations/data-agent/)
