# Agents CLI를 사용하여 Agent Runtime에 배포하기

<div class="language-support-tag" title="Agent Runtime은 현재 Python과 Go를 지원합니다.">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-go">Go v1.2.0</span>
</div>

이 문서에서는 [Agent Platform의 Agents CLI](https://google.github.io/agents-cli/)와 ADK를 사용하여 배포를 수행하는 절차를 설명합니다. Agents CLI를 통해 Agent Runtime에 배포하면 프로덕션 준비 환경을 빠르게 구축할 수 있습니다. Agents CLI는 전체 개발 라이프사이클을 지원하도록 Google Cloud 리소스, CI/CD 파이프라인, 코드형 인프라(Terraform)를 자동으로 구성합니다. 모범 사례로서, 프로덕션에 배포하기 전에는 생성된 구성이 조직의 보안 및 규정 준수 표준에 부합하는지 항상 검토하세요.

이 배포 가이드에서는 Agents CLI를 사용하여 기존 프로젝트에 프로젝트 템플릿을 적용하고, 배포 아티팩트를 추가하며, 에이전트 프로젝트를 배포 가능한 상태로 준비합니다. 다음 단계에 따라 Agents CLI로 ADK 프로젝트 배포에 필요한 Google Cloud 프로젝트 서비스를 프로비저닝할 수 있습니다.

- [사전 요구사항](#prerequisites-ad): Google Cloud 프로젝트 및 IAM 권한을 설정하고 필수 소프트웨어를 설치합니다.
- [ADK 프로젝트 준비](#prepare-ad): 기존 ADK 프로젝트 파일을 배포에 맞게 수정합니다.
- [Google Cloud 프로젝트에 연결](#connect-ad): 개발 환경을 Google Cloud 및 대상 프로젝트에 연결합니다.
- [ADK 프로젝트 배포](#deploy-ad): Google Cloud 프로젝트에 필요한 서비스를 프로비저닝하고 ADK 프로젝트 코드를 업로드합니다.

배포된 에이전트 테스트 방법은 [배포된 에이전트 테스트](test.md)를 참고하세요. Agents CLI와 명령줄 도구 사용에 대한 자세한 내용은 [CLI 레퍼런스](https://google.github.io/agents-cli/cli/) 및 [가이드](https://google.github.io/agents-cli/)를 참고하세요.

### 사전 요구사항 {#prerequisites-ad}

이 배포 경로를 사용하려면 다음 리소스가 구성되어 있어야 합니다.

- **Google Cloud 프로젝트 및 권한**: [결제가 활성화된](https://cloud.google.com/billing/docs/how-to/modify-project) Google Cloud 프로젝트가 필요합니다. 기존 프로젝트를 사용하거나 새 프로젝트를 만들 수 있으며, 해당 프로젝트 내에 다음 IAM 역할 중 하나가 할당되어 있어야 합니다.
    - **Agent Platform 사용자 역할(Agent Platform User)** — Agent Runtime에 에이전트를 배포하는 데 충분합니다.
    - **소유자 역할(Owner)** — 전체 프로덕션 설정(Terraform 인프라 프로비저닝, CI/CD 파이프라인, IAM 구성)에 필요합니다.

!!! tip "참고"
    기존 리소스와의 충돌을 피하려면 비어 있는 프로젝트를 사용하는 것이 좋습니다. 새 프로젝트 생성에 관한 자세한 내용은 [프로젝트 생성 및 관리](https://cloud.google.com/resource-manager/docs/creating-managing-projects)를 참고하세요.

- **Python 환경**: [Agents CLI](https://google.github.io/agents-cli/guide/getting-started/)에서 지원하는 Python 버전.
- **uv 도구:** Python 개발 환경 관리 및 `agents-cli` 도구 실행에 사용합니다. 설치 방법은 [uv 설치](https://docs.astral.sh/uv/getting-started/installation/)를 참고하세요.
- **Google Cloud CLI 도구**: `gcloud` 명령줄 인터페이스입니다. 설치 방법은 [Google Cloud 명령줄 인터페이스](https://cloud.google.com/sdk/docs/install)를 참고하세요.
- **Make 도구**: 빌드 자동화 도구입니다. 대부분의 Unix 기반 시스템에 기본 포함되어 있으며, 설치 방법은 [Make 도구](https://www.gnu.org/software/make/) 문서를 참고하세요.

### ADK 프로젝트 준비 {#prepare-ad}

ADK 프로젝트를 Agent Runtime에 배포하려면 배포 작업을 지원하는 추가 파일이 필요합니다. 아래 Agents CLI 명령어는 기존 프로젝트를 백업한 후 배포에 필요한 파일들을 프로젝트에 추가합니다.

이 지침은 배포를 위해 수정할 기존 ADK 프로젝트가 있다고 가정합니다. ADK 프로젝트가 없거나 테스트용 프로젝트를 사용하려는 경우, [시작하기](/get-started/) 가이드 중 하나를 완료하여 에이전트 프로젝트를 생성하세요. 아래 안내에서는 `my_agent` 프로젝트를 예시로 사용합니다.

Agent Runtime 배포를 위해 ADK 프로젝트를 준비하려면 다음 단계를 따르세요.

1. 개발 환경의 터미널 창에서 에이전트 폴더가 포함된 **상위 디렉터리**로 이동합니다. 예를 들어 프로젝트 구조가 다음과 같다면:

    ```
    your-project-directory/
    ├── my_agent/
    │   ├── __init__.py
    │   ├── agent.py
    │   └── .env
    ```

    `your-project-directory/`로 이동합니다.

1. Agents CLI의 `scaffold enhance` 명령어를 실행하여 배포에 필요한 파일을 프로젝트에 추가합니다.

    ```shell
    agents-cli scaffold enhance --deployment-target agent_runtime
    ```

1. Agents CLI 도구의 안내에 따릅니다. 일반적으로 모든 질문에 기본값을 선택해도 되지만, **GCP 리전(GCP region)** 옵션에서는 반드시 Agent Runtime의 [지원 리전](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine) 중 하나를 선택하세요.

이 과정을 성공적으로 완료하면 도구에 다음 메시지가 표시됩니다.

```
> Success! Your agent project is ready.
```

!!! tip "참고"
    실행 중에 Agents CLI 도구가 Google Cloud 연결을 안내하는 알림을 표시할 수 있지만, 이 단계에서는 연결이 *필수*가 아닙니다.

Agents CLI가 ADK 프로젝트에 적용하는 변경 사항에 대한 자세한 내용은 [ADK 프로젝트 변경 사항](#adk-agents-cli-changes)을 참고하세요.

### Google Cloud 프로젝트에 연결 {#connect-ad}

ADK 프로젝트를 배포하기 전에 Google Cloud 및 대상 프로젝트에 연결해야 합니다. Google Cloud 계정에 로그인한 후, 배포 대상 프로젝트가 계정에서 조회되고 현재 프로젝트로 설정되어 있는지 확인하세요.

Google Cloud에 연결하고 프로젝트를 설정하려면 다음 단계를 따르세요.

1. 개발 환경의 터미널 창에서 Google Cloud 계정에 로그인합니다.

    ```shell
    gcloud auth application-default login
    ```

1. Google Cloud 프로젝트 ID를 사용하여 대상 프로젝트를 설정합니다.

    ```shell
    gcloud config set project your-project-id-xxxxx
    ```

1. Google Cloud 대상 프로젝트가 올바르게 설정되었는지 확인합니다.

    ```shell
    gcloud config get-value project
    ```

Google Cloud에 연결하고 Cloud 프로젝트 ID 설정을 마쳤다면 ADK 프로젝트 파일을 Agent Runtime에 배포할 준비가 완료된 것입니다.

### ADK 프로젝트 배포 {#deploy-ad}

Agents CLI를 사용할 때는 `agents-cli deploy` 명령어로 배포합니다. 이 명령어는 에이전트 코드로 컨테이너를 빌드하고 레지스트리에 푸시한 뒤, 호스팅 환경의 Agent Runtime에 배포합니다.

!!! warning "중요"
    *이 단계를 수행하기 전에 Google Cloud 배포 대상 프로젝트가 **현재 프로젝트**로 설정되어 있는지 반드시 확인하세요.* `agents-cli deploy` 명령어는 배포 시 현재 설정된 Google Cloud 프로젝트를 사용합니다. 현재 프로젝트 설정 및 확인 방법은 [Google Cloud 프로젝트에 연결](#connect-ad)을 참고하세요.

Google Cloud 프로젝트의 Agent Runtime에 ADK 프로젝트를 배포하려면 다음 단계를 따르세요.

1. 터미널 창에서 에이전트 프로젝트 디렉터리(예: `your-project-directory/`)로 이동합니다.

2. Google Cloud 개발 환경에 에이전트 코드를 배포합니다.

    ```shell
    agents-cli deploy
    ```

    이 명령어는 `pyproject.toml`에서 `deployment_target`을 읽어 설정된 대상(Agent Runtime, Cloud Run 또는 GKE)에 배포합니다.

3. (선택 사항) 프롬프트-응답 로깅 및 콘텐츠 로그 같은 관측 가능성(observability) 기능을 활성화하려면 텔레메트리 인프라를 프로비저닝합니다.

    ```shell
    agents-cli infra single-project
    ```

    자세한 내용은 [관측 가능성 가이드](https://google.github.io/agents-cli/guide/observability/)를 참고하세요.

이 과정이 성공적으로 완료되면 Google Cloud Agent Runtime에서 실행 중인 에이전트와 상호작용할 수 있습니다. 배포된 에이전트 테스트에 대한 자세한 내용은 [배포된 에이전트 테스트](/deploy/agent-runtime/test/)를 참고하세요.

### ADK 프로젝트 변경 사항 {#adk-agents-cli-changes}

Agents CLI 도구는 배포를 위해 프로젝트에 여러 파일을 추가하며, 기존 프로젝트 파일을 수정하기 전에 먼저 백업합니다. 이 가이드에서는 [multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent) 프로젝트를 참조 예시로 사용합니다. 원본 프로젝트의 초기 파일 구조는 다음과 같습니다.

```
my_agent/
├─ __init__.py
├─ agent.py
└─ .env
```

Agent Runtime 배포 구성을 추가하기 위해 Agents CLI `scaffold enhance` 명령어를 실행한 후의 새로운 구조는 다음과 같습니다.

```
my-agent/
├─ app/                 # Core application code
│   ├─ agent.py         # Main agent logic
│   ├─ agent_engine_app.py # Agent Runtime application logic
│   └─ utils/           # Utility functions and helpers
├─ .cloudbuild/         # CI/CD pipeline configurations for Google Cloud Build
├─ deployment/          # Infrastructure and deployment scripts
├─ notebooks/           # Jupyter notebooks for prototyping and evaluation
├─ tests/               # Unit, integration, and load tests
├─ Makefile             # Makefile for common commands
├─ GEMINI.md            # AI-assisted development guide
└─ pyproject.toml       # Project dependencies and configuration
```

자세한 내용은 업데이트된 ADK 프로젝트 폴더의 *README.md* 파일을 참고하세요. Agents CLI 사용에 대한 자세한 내용은 [Agents CLI 문서](https://google.github.io/agents-cli/)를 참고하세요.

## 배포된 에이전트 테스트

ADK 에이전트 배포를 완료한 후에는 새로운 호스팅 환경에서 워크플로를 테스트해야 합니다. Agent Runtime에 배포된 ADK 에이전트 테스트 방법은 [Agent Runtime에 배포된 에이전트 테스트](/deploy/agent-runtime/test/)를 참고하세요.
