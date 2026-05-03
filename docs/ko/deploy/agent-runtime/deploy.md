# 에이전트 런타임에 배포

<div class="language-support-tag" title="Agent Runtime currently supports only Python.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

이 배포 절차에서는 표준 배포를 수행하는 방법을 설명합니다.
Google Cloud에 대한 ADK 에이전트 코드
[Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview).
기존 Google Cloud가 있는 경우 이 배포 경로를 따라야 합니다.
프로젝트 및 에이전트에 ADK 에이전트 배포를 신중하게 관리하려는 경우
런타임 환경. 이 안내에서는 gcloud인 Cloud Console을 사용합니다.
명령줄 인터페이스 및 ADK 명령줄 인터페이스(ADK CLI). 이 경로
Google Cloud 구성에 이미 익숙한 사용자에게 권장됩니다.
프로젝트 및 프로덕션 배포를 준비하는 사용자.

이 안내에서는 ADK 프로젝트를 Google Cloud Agent에 배포하는 방법을 설명합니다.
다음 단계를 포함하는 런타임 환경:

* [Setup Google Cloud project](#setup-cloud-project)
* [Prepare agent project folder](#define-your-agent)
* [Deploy the agent](#deploy-agent)

## Google Cloud 프로젝트 설정 {#setup-cloud-project}

에이전트 런타임에 에이전트를 배포하려면 Google Cloud 프로젝트가 필요합니다.

1. **Google Cloud에 로그인**:
    * Google Cloud의 **기존 사용자**인 경우:
        * 로그인 방법
          [https://console.cloud.google.com](https://console.cloud.google.com)
        * 이전에 만료된 무료 평가판을 사용한 경우 다음을 수행해야 할 수 있습니다.
          로 업그레이드
          [Paid billing account](https://docs.cloud.google.com/free/docs/free-cloud-features#how-to-upgrade).
    * Google Cloud의 **신규 사용자**인 경우:
        * 회원가입을 하시면 됩니다
          [Free Trial program](https://docs.cloud.google.com/free/docs/free-cloud-features).
          무료 평가판을 사용하면 91일 이상 다양한 서비스에 사용할 수 있는 $300의 환영 크레딧을 받을 수 있습니다.
          [Google Cloud products](https://docs.cloud.google.com/free/docs/free-cloud-features#during-free-trial)
          비용이 청구되지 않습니다. 무료 평가판 기간 동안 다음 서비스에도 액세스할 수 있습니다.
          [Google Cloud Free Tier](https://docs.cloud.google.com/free/docs/free-cloud-features#free-tier),
          매월 지정된 기간까지 일부 제품을 무료로 사용할 수 있습니다.
          한도 및 제품별 무료 평가판을 제공합니다.

2. **Google Cloud 프로젝트 만들기**
    * 이미 기존 구글 클라우드 프로젝트가 있다면 사용 가능하지만,
      이 프로세스로 인해 프로젝트에 새로운 서비스가 추가될 가능성이 높습니다.
    * 새로운 Google Cloud 프로젝트를 만들고 싶다면 새로 생성하면 됩니다.
      [Create Project](https://console.cloud.google.com/projectcreate)에서
      페이지.

3. **Google Cloud 프로젝트 ID 받기**
    * GCP에서 찾을 수 있는 Google Cloud 프로젝트 ID가 필요합니다.
      홈페이지. 프로젝트 ID(하이픈이 포함된 영숫자)를 기록해 두세요.
      _아님_ 프로젝트 번호(숫자)입니다.

    <img src="/assets/project-id.png" alt="Google 클라우드 프로젝트 ID">

4. **프로젝트에서 에이전트 플랫폼 활성화**
    * Agent Runtime을 사용하기 위해서는 [enable the Agent Platform API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)가 필요합니다. API를 활성화하려면 "활성화" 버튼을 클릭하세요. 일단 활성화되면,
    "API 활성화됨"이라고 표시되어야 합니다.

5. **프로젝트에서 Cloud Resource Manager API를 활성화합니다**
    * Agent Runtime을 사용하기 위해서는 [enable the Cloud Resource Manager API](https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview)가 필요합니다. API를 활성화하려면 "활성화" 버튼을 클릭하세요. 활성화되면 "API 활성화됨"이라고 표시되어야 합니다.

## 코딩 환경 설정 {#prerequisites-coding-env}

이제 Google Cloud 프로젝트를 준비했으므로 코딩으로 돌아갈 수 있습니다.
환경. 이 단계를 수행하려면 코딩 내의 터미널에 액세스해야 합니다.
명령줄 지침을 실행하는 환경입니다.

### Google Cloud로 코딩 환경 인증

* 귀하와 귀하의 코딩 환경을 인증해야 합니다.
    코드는 Google Cloud와 상호작용할 수 있습니다. 이렇게 하려면 gcloud CLI가 필요합니다.
    gcloud CLI를 사용해 본 적이 없다면 먼저 다음을 수행해야 합니다.
    [download and install it](https://docs.cloud.google.com/sdk/docs/install-sdk)
    아래 단계를 계속하기 전에:

* Google Cloud에 액세스하려면 터미널에서 다음 명령어를 실행하세요.
    사용자로 프로젝트:

    ```shell
    gcloud auth login
    ```

    인증 후 메시지가 표시됩니다.
    `You are now authenticated with the gcloud CLI!`.

* 다음 명령을 실행하여 코드가 작동할 수 있도록 인증하세요.
    구글 클라우드:

    ```shell
    gcloud auth application-default login
    ```

    인증 후 메시지가 표시됩니다.
    `You are now authenticated with the gcloud CLI!`.

* (선택사항) gcloud에서 기본 프로젝트를 설정하거나 변경해야 하는 경우
    다음을 사용할 수 있습니다:

    ```shell
    gcloud config set project MY-PROJECT-ID
    ```

### 에이전트 정의 {#define-your-agent}

Google Cloud와 코딩 환경이 준비되면 배포 준비가 완료됩니다.
당신의 대리인. 지침에서는 에이전트 프로젝트 폴더가 있다고 가정합니다.
예를 들면:

```shell
multi_tool_agent/
├── .env
├── __init__.py
└── agent.py
```

프로젝트 파일 및 형식에 대한 자세한 내용은 다음을 참조하세요.
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
코드 샘플.

## 에이전트 배포 {#deploy-agent}

`adk deploy` 명령줄 도구를 사용하여 터미널에서 배포할 수 있습니다. 이
프로세스는 코드를 패키징하고 컨테이너에 빌드한 다음
관리형 에이전트 런타임 서비스. 이 프로세스는 몇 분 정도 걸릴 수 있습니다.

다음 예제 배포 명령은 `multi_tool_agent` 샘플 코드를 다음과 같이 사용합니다.
배포할 프로젝트:

```shell
PROJECT_ID=my-project-id
LOCATION_ID=us-central1

adk deploy agent_engine \
        --project=$PROJECT_ID \
        --region=$LOCATION_ID \
        --display_name="My First Agent" \
        multi_tool_agent
```

`region`의 경우 지원되는 지역 목록은 다음에서 확인할 수 있습니다.
[Agent Builder locations page](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine).
`adk deploy agent_engine` 명령의 CLI 옵션에 대해 알아보려면 다음을 참조하세요.
[ADK CLI Reference](/api-reference/cli/#adk-deploy-agent-engine).

### 배포 명령 출력

성공적으로 배포되면 다음 출력이 표시됩니다.

```shell
Creating AgentEngine
Create AgentEngine backing LRO: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944/operations/2356952072064073728
View progress and logs at https://console.cloud.google.com/logs/query?project=hopeful-sunset-478017-q0
AgentEngine created. Resource name: projects/123456789/locations/us-central1/reasoningEngines/751619551677906944
To use this AgentEngine in another session:
agent_engine = vertexai.agent_engines.get('projects/123456789/locations/us-central1/reasoningEngines/751619551677906944')
Cleaning up the temp folder: /var/folders/k5/pv70z5m92s30k0n7hfkxszfr00mz24/T/agent_engine_deploy_src/20251219_134245
```

이제 에이전트가 배포된 `RESOURCE_ID`가 있습니다.
위 예에서는 `751619551677906944`입니다. 이 ID 번호가 필요합니다.
에이전트 런타임에서 에이전트를 사용하려면 다른 값과 함께 사용하세요.

## 에이전트 런타임에서 에이전트 사용

ADK 프로젝트 배포가 완료되면 에이전트에 쿼리할 수 있습니다.
Agent Platform SDK, Python 요청 라이브러리 또는 REST API 클라이언트를 사용합니다. 이
섹션에서는 에이전트와 상호작용하는 데 필요한 정보를 제공합니다.
에이전트의 REST API와 상호작용하기 위해 URL을 구성하는 방법을 알아보세요.

에이전트 런타임에서 에이전트와 상호작용하려면 다음이 필요합니다.

* **PROJECT_ID**(예: "my-project-id")는 다음에서 찾을 수 있습니다.
    [project details page](https://console.cloud.google.com/iam-admin/settings)
* **LOCATION_ID**(예: "us-central1"), 에이전트를 배포하는 데 사용한 것입니다.
* **RESOURCE_ID**(예: "751619551677906944"), 다음에서 찾을 수 있습니다.
    [Agent Runtime UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

쿼리 URL 구조는 다음과 같습니다.

```shell
https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query
```

이 URL 구조를 사용하여 에이전트로부터 요청할 수 있습니다. 자세한 내용은
요청 방법은 에이전트 런타임 문서의 지침을 참조하세요.
[Use an Agent Development Kit agent](https://docs.cloud.google.com/agent-builder/agent-engine/use/adk#rest-api).
또한 에이전트 런타임 문서를 확인하여 관리 방법을 알아볼 수도 있습니다.
[deployed agent](https://docs.cloud.google.com/agent-builder/agent-engine/manage/overview).
배포된 에이전트 테스트 및 상호 작용에 대한 자세한 내용은 다음을 참조하세요.
[Test deployed agents in Agent Runtime](/deploy/agent-runtime/test/).

### 모니터링 및 검증

* 배포 상태를 모니터링할 수 있습니다.
    [Agent Runtime UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)
    Google Cloud Console에서.
* 자세한 내용은 에이전트 런타임 설명서를 참조하세요.
    [deploying an agent](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy)
    그리고
    [managing deployed agents](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview).

## 배포된 에이전트 테스트

ADK 에이전트 배포를 완료한 후에는 다음에서 워크플로를 테스트해야 합니다.
새로운 호스팅 환경. ADK 에이전트 테스트에 대한 자세한 내용은
에이전트 런타임에 배포됩니다. 참조
[Test deployed agents in Agent Runtime](/deploy/agent-runtime/test/).
