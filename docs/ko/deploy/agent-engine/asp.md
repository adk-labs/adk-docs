# Agent Starter Pack로 Agent Engine에 배포

<div class="language-support-tag" title="Vertex AI Agent Engine은 현재 Python만 지원합니다.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

이 배포 절차에서는 [Agent Starter Pack](https://github.com/GoogleCloudPlatform/agent-starter-pack)(ASP)과 ADK CLI를 사용한 배포 방법을 설명합니다.
ASP를 이용한 Agent Engine 런타임 배포는 가속 경로로, **개발 및 테스트** 용도로만 사용해야 합니다.
ASP는 ADK 에이전트 워크플로 실행에 반드시 필요한 항목이 아닌 Google Cloud 리소스를 구성할 수 있으므로,
운영 배포 전에 반드시 구성을 검토하세요.

이 가이드는 ASP 도구를 사용해 기존 프로젝트에 템플릿을 적용하고 배포 산출물을 추가해 에이전트 프로젝트를 배포 상태로 준비합니다.
다음과 같은 단계로 ADK 프로젝트를 배포에 필요한 Google Cloud 서비스로 구성합니다.

-   [사전 준비](#prerequisites-ad): Google Cloud 계정, 프로젝트 설정, 필수 소프트웨어 설치
-   [ADK 프로젝트 준비](#prepare-ad): 기존 ADK 프로젝트 파일을 배포 준비 상태로 수정
-   [Google Cloud 프로젝트 연결](#connect-ad): 개발 환경을 Google Cloud 및 프로젝트에 연결
-   [ADK 프로젝트 배포](#deploy-ad): Google Cloud 프로젝트에 필수 서비스 프로비저닝 후 코드 업로드

배포한 에이전트를 테스트하는 방법은 [배포된 에이전트 테스트](test.md)를 참고하세요.
ASP 및 CLI 도구 사용 방법은 다음을 참고하세요.
[CLI Reference](https://googlecloudplatform.github.io/agent-starter-pack/cli/enhance.html)
및
[Development guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html).

### 사전 준비 {#prerequisites-ad}

이 배포 경로를 사용하려면 다음 리소스가 준비되어 있어야 합니다.

-   **Google Cloud 계정**: 다음에 대한 관리자 권한이 필요합니다.
    -   **Google Cloud 프로젝트**: [요금 청구 사용] 설정이 완료된 빈 프로젝트
        [billing enabled](https://cloud.google.com/billing/docs/how-to/modify-project).
        프로젝트 생성 방법은 [프로젝트 만들기 및 관리](https://cloud.google.com/resource-manager/docs/creating-managing-projects)를 참조하세요.
-   **Python 환경**: [ASP 프로젝트](https://googlecloudplatform.github.io/agent-starter-pack/guide/getting-started.html)에서 지원하는 Python 버전
-   **uv 도구:** Python 개발 환경 관리 및 ASP 실행에 사용합니다.
    설치는 [uv 설치](https://docs.astral.sh/uv/getting-started/installation/)를 참고하세요.
-   **Google Cloud CLI 도구**: gcloud CLI입니다. 설치는 [Google Cloud 명령줄 인터페이스](https://cloud.google.com/sdk/docs/install)를 참고하세요.
-   **Make 도구**: 빌드 자동화 도구로, 대부분 Unix 기반 시스템에 기본 포함됩니다.
    설치는 [Make 도구](https://www.gnu.org/software/make/) 문서를 참고하세요.

### ADK 프로젝트 준비 {#prepare-ad}

Agent Engine에 ADK 프로젝트를 배포하려면 배포 작업을 지원하는 추가 파일이 필요합니다. 다음 ASP 명령은 프로젝트를 백업한 뒤 배포용 파일을 추가합니다.

이 가이드는 배포를 위해 기존 ADK 프로젝트를 수정한다고 가정합니다. ADK 프로젝트가 없는 경우 또는 테스트 프로젝트를 사용하려면
[Quickstart](/adk-docs/get-started/quickstart/) 가이드를 먼저 수행해
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
프로젝트를 생성하세요. 아래 예시는 `multi_tool_agent` 프로젝트를 사용합니다.

Agent Engine 배포를 위해 ADK 프로젝트를 준비하려면:

1.  개발 환경의 터미널에서 에이전트 폴더가 포함된 **상위 디렉터리**로 이동합니다. 예:

    ```
    your-project-directory/
    ├── multi_tool_agent/
    │   ├── __init__.py
    │   ├── agent.py
    │   └── .env
    ```

    `your-project-directory/`로 이동합니다.

1.  ASP `enhance` 명령을 실행해 배포에 필요한 파일을 프로젝트에 추가합니다.

    ```shell
    uvx agent-starter-pack enhance --adk -d agent_engine
    ```

1.  ASP 도구의 안내에 따라 진행합니다. 보통 기본값으로 진행해도 되지만,
    **GCP 리전**은 Agent Engine에서 지원되는 리전 목록([supported regions](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine))
    중 하나를 선택해야 합니다.

과정이 완료되면 다음 메시지가 표시됩니다.

```
> Success! Your agent project is ready.
```

!!! tip "참고"
    ASP 도구는 실행 중 Google Cloud 연결을 수행하라는 메시지를 표시할 수 있으나,
    이 단계에서는 해당 연결이 *필수*는 아닙니다.

ASP가 ADK 프로젝트를 변경하는 상세 내용은 [ADK 프로젝트 변경 사항](#adk-asp-changes)을 참고하세요.

### Google Cloud 프로젝트 연결 {#connect-ad}

ADK 프로젝트 배포 전 Google Cloud와 프로젝트에 연결해야 합니다. Google Cloud 계정으로 로그인한 뒤,
배포 대상 프로젝트가 계정에서 보이고 현재 프로젝트로 설정되어 있는지 확인하세요.

Google Cloud에 연결하고 프로젝트를 조회하려면:

1.  개발 환경 터미널에서 Google Cloud 계정에 로그인:

    ```shell
    gcloud auth application-default login
    ```

1.  대상 프로젝트를 설정:

    ```shell
    gcloud config set project your-project-id-xxxxx
    ```

1.  대상 프로젝트가 설정되었는지 확인:

    ```shell
    gcloud config get-value project
    ```

연결이 완료되어 Cloud Project ID가 설정되면 Agent Engine 배포 준비가 완료됩니다.

### ADK 프로젝트 배포 {#deploy-ad}

ASP를 사용할 때 배포는 단계적으로 수행됩니다. 첫 단계에서는 `make` 명령으로
ADK 워크플로 실행에 필요한 서비스를 Agent Engine에서 사용할 수 있도록 준비합니다.
둘째 단계에서는 프로젝트 코드를 Agent Engine 서비스에 업로드하고 호스팅 환경에서 실행합니다.

!!! warning "중요"
    이 단계를 수행하기 전, Google Cloud 대상 프로젝트가 현재 프로젝트로 설정되어 있는지 확인하세요.
    `make backend`는 현재 설정된 Google Cloud 프로젝트에 배포를 수행합니다.
    현재 프로젝트 설정 방법은 [Google Cloud 프로젝트 연결](#connect-ad) 섹션을 참조하세요.

ADK 프로젝트를 Google Cloud 프로젝트에 배포하려면:

1.  터미널에서 에이전트 폴더를 포함한 상위 디렉터리(예: `your-project-directory/`)에 있는지 확인합니다.

1.  다음 ASP make 명령을 실행해 업데이트된 로컬 프로젝트 코드를 Google Cloud 개발 환경에 배포합니다.

    ```shell
    make backend
    ```

성공적으로 완료되면 Google Cloud Agent Engine에서 실행 중인 에이전트와 상호 작용할 수 있습니다.
배포 에이전트 테스트 방법은 [배포된 에이전트 테스트](/adk-docs/deploy/agent-engine/test/)를 참고하세요.

### ADK 프로젝트 변경 사항 {#adk-asp-changes}

ASP 도구는 배포를 위해 프로젝트에 추가 파일을 추가합니다. 아래 절차는 기존 프로젝트를 수정하기 전에 백업합니다.
원본 예시 프로젝트는 [multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)이며,
최초 구조는 아래와 같습니다.

```
multi_tool_agent/
├─ __init__.py
├─ agent.py
└─ .env
```

ASP enhance 명령으로 Agent Engine 배포 정보를 추가한 뒤 새 구조는 다음과 같습니다.

```
multi-tool-agent/
├─ app/                 # 핵심 애플리케이션 코드
│   ├─ agent.py         # 메인 에이전트 로직
│   ├─ agent_engine_app.py # Agent Engine 애플리케이션 로직
│   └─ utils/           # 유틸리티 함수 및 헬퍼
├─ .cloudbuild/         # Google Cloud Build용 CI/CD 설정
├─ deployment/          # 인프라 및 배포 스크립트
├─ notebooks/           # 프로토타이핑/평가용 Jupyter 노트북
├─ tests/               # 단위/통합/부하 테스트
├─ Makefile             # 기본 명령용 Makefile
├─ GEMINI.md            # AI 보조 개발 가이드
└─ pyproject.toml       # 프로젝트 종속성 및 구성
```

업데이트된 ADK 프로젝트 폴더의 `README.md`에서 자세한 정보를 확인하세요.
ASP 사용 상세는 [개발 가이드](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html)를 참고하세요.

## 배포된 에이전트 테스트

ADK 에이전트 배포 후 새로운 호스팅 환경에서 워크플로를 테스트해야 합니다. Agent Engine에 배포된 ADK 에이전트 테스트 방법은
[Agent Engine에서 배포된 에이전트 테스트](/adk-docs/deploy/agent-engine/test/)를 참고하세요.
