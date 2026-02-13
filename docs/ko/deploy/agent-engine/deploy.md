# Vertex AI Agent Engine에 배포

<div class="language-support-tag" title="Vertex AI Agent Engine은 현재 Python만 지원합니다.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

이 가이드는 Google Cloud
[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)에
ADK 에이전트 코드를 표준 방식으로 배포하는 절차를 설명합니다.
기존 Google Cloud 프로젝트가 있으며 ADK 에이전트를 Agent Engine 런타임에
신중하게 배포하려는 경우 이 경로를 선택합니다. 이 가이드는 Cloud Console,
gcloud, ADK CLI를 사용합니다. 이미 Google Cloud 프로젝트 구성에 익숙で、운영 배포를 준비 중인 사용자에게 권장됩니다.

이 가이드에서는 다음 단계로 구성된 배포 과정을 설명합니다.

*   [Google Cloud 프로젝트 설정](#setup-cloud-project)
*   [에이전트 프로젝트 폴더 준비](#define-your-agent)
*   [에이전트 배포](#deploy-agent)

## Google Cloud 프로젝트 설정 {#setup-cloud-project}

에이전트를 Agent Engine에 배포하려면 Google Cloud 프로젝트가 필요합니다.

1. **Google Cloud 로그인**:
    * 기존 Google Cloud 사용자:
        * [https://console.cloud.google.com](https://console.cloud.google.com)에서 로그인
        * 만료된 무료 체험 기간이 있는 경우 [유료 결제 계정](https://docs.cloud.google.com/free/docs/free-cloud-features#how-to-upgrade)으로 전환해야 할 수 있습니다.
    * Google Cloud 신규 사용자:
        * [무료 체험 프로그램](https://docs.cloud.google.com/free/docs/free-cloud-features)에 가입할 수 있습니다.
          무료 체험에서는 91일 동안 $300 크레딧을 [Google Cloud 제품](https://docs.cloud.google.com/free/docs/free-cloud-features#during-free-trial)에서 사용할 수 있습니다.
          또한 사용량이 무료 한도 내인 일부 제품에 대해 [Google Cloud Free Tier](https://docs.cloud.google.com/free/docs/free-cloud-features#free-tier) 접근 권한도 제공합니다.

2. **Google Cloud 프로젝트 생성**
    * 기존 프로젝트가 있으면 사용할 수 있지만, 이 과정에서 새 서비스가 추가될 수 있습니다.
    * 새 프로젝트가 필요하면 [프로젝트 생성](https://console.cloud.google.com/projectcreate) 페이지에서 생성할 수 있습니다.

3. **Google Cloud 프로젝트 ID 확인**
    * GCP 홈페이지에서 프로젝트 ID(영문/숫자 및 하이픈)를 확인합니다. 프로젝트 번호가 아니라 프로젝트 ID를 기록해야 합니다.

    <img src="/adk-docs/assets/project-id.png" alt="Google Cloud Project ID">

4. **프로젝트에서 Vertex AI 사용 설정**
    * Agent Engine 사용을 위해 [Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)를 활성화하세요.
      버튼을 클릭해 "Enable" 후 상태가 "API Enabled"인지 확인합니다.

5. **프로젝트에서 Cloud Resource Manager API 사용 설정**
    * [Cloud Resource Manager API](https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview)를 활성화하세요.
      버튼 클릭 후 "API Enabled"를 확인합니다.

## 코딩 환경 설정 {#prerequisites-coding-env}

Google Cloud 프로젝트 준비가 끝나면 코딩 환경으로 돌아옵니다. 아래 단계에서는 터미널에서 명령어를 실행해야 합니다.

### 코딩 환경에서 Google Cloud 인증

*   Google Cloud와 상호 작용하려면 인증이 필요합니다. gcloud CLI가 필요합니다.
    아직 사용한 적이 없다면, 먼저 [설치](https://docs.cloud.google.com/sdk/docs/install-sdk)하세요.

*   사용자 계정으로 Google Cloud에 접근하려면 터미널에서 아래 명령을 실행합니다.

    ```shell
    gcloud auth login
    ```

    인증 후 `You are now authenticated with the gcloud CLI!` 메시지를 확인할 수 있습니다.

*   코드가 Google Cloud와 동작하도록 인증합니다.

    ```shell
    gcloud auth application-default login
    ```

    인증 후 동일한 메시지가 표시됩니다.

*   (선택) 기본 프로젝트를 변경해야 하면:

    ```shell
    gcloud config set project MY-PROJECT-ID
    ```

### 에이전트 정의 {#define-your-agent}

Google Cloud 및 코딩 환경이 준비되면 배포할 수 있습니다. 다음과 같은 에이전트 프로젝트 폴더가 있다고 가정합니다.

```shell
multi_tool_agent/
├── .env
├── __init__.py
└── agent.py
```

프로젝트 파일 및 형식에 대한 자세한 내용은
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
샘플 코드를 참고하세요.

## 에이전트 배포 {#deploy-agent}

터미널에서 `adk deploy` CLI를 사용해 배포할 수 있습니다. 이 과정에서 코드를 패키징하고 컨테이너로 빌드한 다음
관리형 Agent Engine 서비스에 배포합니다. 이 단계에는 몇 분이 소요될 수 있습니다.

아래 예시는 `multi_tool_agent` 샘플 코드를 배포할 때의 명령어입니다.

```shell
PROJECT_ID=my-project-id
LOCATION_ID=us-central1

adk deploy agent_engine \
        --project=$PROJECT_ID \
        --region=$LOCATION_ID \
        --display_name="My First Agent" \
        multi_tool_agent
```

`region` 값은 [Vertex AI Agent Builder locations](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine)에서
지원되는 리전 목록을 확인하세요.
`adk deploy agent_engine`의 CLI 옵션은 [ADK CLI Reference](https://google.github.io/adk-docs/api-reference/cli/cli.html#adk-deploy-agent-engine)를 참고하세요.

### 배포 명령 출력

성공 시 다음과 같은 출력이 나타납니다.

```shell
Creating AgentEngine
Create AgentEngine backing LRO: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944/operations/2356952072064073728
View progress and logs at https://console.cloud.google.com/logs/query?project=hopeful-sunset-478017-q0
AgentEngine created. Resource name: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944
To use this AgentEngine in another session:
agent_engine = vertexai.agent_engines.get('projects/123456789/locations/us-central1/reasoningEngines/751619551677906944')
Cleaning up the temp folder: /var/folders/k5/pv70z5m92s30k0n7hfkxszfr00mz24/T/agent_engine_deploy_src/20251219_134245
```

출력에 `RESOURCE_ID`가 포함됩니다. 예에서는 `751619551677906944` 입니다.
이 값은 다른 값과 함께 Agent Engine에서 에이전트를 사용하기 위해 필요합니다.

## Agent Engine에서 에이전트 사용

ADK 프로젝트 배포가 완료되면 Vertex AI SDK, Python requests 라이브러리 또는 REST API 클라이언트를 사용해 쿼리할 수 있습니다.
이 섹션에서는 에이전트와 상호작용하는 데 필요한 값과 REST API URL 구성 방법을 설명합니다.

Agent Engine에서 에이전트와 상호작용하려면 다음 값이 필요합니다:

*   **PROJECT_ID** (예: "my-project-id") → [프로젝트 세부 정보 페이지](https://console.cloud.google.com/iam-admin/settings)에서 확인
*   **LOCATION_ID** (예: "us-central1") → 배포 시 사용한 값
*   **RESOURCE_ID** (예: "751619551677906944") → [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)에서 확인

쿼리 URL 구조:

```shell
https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query
```

이 URL 형식으로 요청을 보내면 됩니다. 자세한 내용은 Agent Engine 문서의
[Use an Agent Development Kit agent](https://docs.cloud.google.com/agent-builder/agent-engine/use/adk#rest-api)와
[배포된 에이전트 관리](https://docs.cloud.google.com/agent-builder/agent-engine/manage/overview)에서 확인하세요.
배포된 에이전트 테스트 및 상호작용 방법은 [Agent Engine에서 배포된 에이전트 테스트](/adk-docs/deploy/agent-engine/test/)를 참고하세요.

### 모니터링 및 검증

*   Google Cloud Console의 [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)에서 배포 상태를 확인할 수 있습니다.
*   상세 내용은 Agent Engine 문서의
    [에이전트 배포](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy)
    및
    [배포된 에이전트 관리](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)를 참조하세요.

## 배포된 에이전트 테스트

ADK 에이전트 배포 완료 후에는 새 호스팅 환경에서 워크플로를 테스트해야 합니다.
자세한 내용은 [Agent Engine에서 배포된 에이전트 테스트](/adk-docs/deploy/agent-engine/test/)를 참고하세요.
