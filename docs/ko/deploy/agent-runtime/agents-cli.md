# 에이전트 CLI를 사용하여 에이전트 런타임에 배포

<div class="language-support-tag" title="Agent Runtime currently supports only Python.">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

이 배포 절차에서는 다음을 사용하여 배포를 수행하는 방법을 설명합니다.
[Agents CLI in Agent Platform](https://google.github.io/agents-cli/)
그리고 ADK. 에이전트 CLI를 통해 에이전트 런타임에 배포하면 프로덕션 준비 환경에 대한 가속화된 경로가 제공됩니다. Agents CLI는 전체 개발 수명 주기를 지원하도록 Google Cloud 리소스, CI/CD 파이프라인, 코드형 인프라(Terraform)를 자동으로 구성합니다. 모범 사례로서 프로덕션 배포 전에 항상 생성된 구성을 검토하여 조직의 보안 및 규정 준수 표준에 부합하는지 확인하십시오.

이 배포 가이드에서는 Agents CLI를 사용하여 프로젝트 템플릿을
기존 프로젝트, 배포 아티팩트 추가 및 에이전트 프로젝트 준비
배포. 이 안내에서는 Agents CLI를 사용하여 Google을 프로비저닝하는 방법을 보여줍니다.
ADK 프로젝트를 배포하는 데 필요한 서비스가 포함된 클라우드 프로젝트는 다음과 같습니다.

- [Prerequisites](#prerequisites-ad): Google Cloud 설정
    프로젝트, IAM 권한 및 필수 소프트웨어 설치.
- [Prepare your ADK project](#prepare-ad): 수정
    기존 ADK 프로젝트 파일을 배포 준비에 사용합니다.
- [Connect to your Google Cloud project](#connect-ad):
    개발 환경을 Google Cloud 및 Google Cloud에 연결
    프로젝트.
- [Deploy your ADK project](#deploy-ad): 제공
    Google Cloud 프로젝트에 필요한 서비스를 만들고 ADK 프로젝트 코드를 업로드하세요.

배포된 에이전트 테스트에 대한 자세한 내용은 [Test deployed agent](test.md)를 참조하세요.
Agents CLI 및 해당 명령줄 도구 사용에 대한 자세한 내용은 다음을 참조하세요.
참조
[CLI reference](https://google.github.io/agents-cli/cli/)
그리고
[Guide](https://google.github.io/agents-cli/).

### 전제 조건 {#prerequisites-ad}

이 배포 경로를 사용하려면 다음 리소스를 구성해야 합니다.

- **Google Cloud 프로젝트 및 권한**: [billing enabled](https://cloud.google.com/billing/docs/how-to/modify-project)를 사용하는 Google Cloud 프로젝트입니다.
    기존 프로젝트를 사용하거나 새 프로젝트를 만들 수 있습니다. 이 프로젝트 내에는 다음 IAM 역할 중 하나가 할당되어 있어야 합니다.
    - **에이전트 플랫폼 사용자 역할** — 에이전트 런타임에 에이전트를 배포하는 데 충분합니다.
    - **소유자 역할** — 전체 프로덕션 설정(Terraform 인프라 프로비저닝, CI/CD 파이프라인, IAM 구성)에 필요합니다.

!!! tip "메모"
    기존 리소스와의 충돌을 피하기 위해 빈 프로젝트를 권장합니다.
    새로운 프로젝트에 대해서는 [Creating and managing projects](https://cloud.google.com/resource-manager/docs/creating-managing-projects)를 참조하세요.

- **Python 환경**: Python 버전이 지원됩니다.
    [Agents CLI](https://google.github.io/agents-cli/guide/getting-started/).
- **uv 도구:** Python 개발 환경 및 Agent-cli 실행 관리
    도구. 설치에 대한 자세한 내용은 다음을 참조하세요.
    [Install uv](https://docs.astral.sh/uv/getting-started/installation/).
- **Google Cloud CLI 도구**: gcloud 명령줄 인터페이스입니다. 에 대한
    설치 세부사항, 참조
    [Google Cloud Command Line Interface](https://cloud.google.com/sdk/docs/install).
- **Make tool**: 자동화 도구를 빌드합니다. 이 도구는 대부분의 일부입니다.
    Unix 기반 시스템의 설치 세부사항은 다음을 참조하십시오.
    [Make tool](https://www.gnu.org/software/make/) 문서.

### ADK 프로젝트 준비 {#prepare-ad}

ADK 프로젝트를 Agent Runtime에 배포할 때 몇 가지 추가 파일이 필요합니다.
배포 작업을 지원합니다. 다음 Agents CLI 명령은
그런 다음 배포 목적으로 프로젝트에 파일을 추가합니다.

이 지침에서는 수정 중인 기존 ADK 프로젝트가 있다고 가정합니다.
배포용. ADK 프로젝트가 없거나, 테스트를 이용하고 싶은 경우
프로젝트, [Get started](/get-started/) 가이드 중 하나를 완료하고,
에이전트 프로젝트를 생성합니다. 다음 지침에서는 `my_agent`를 사용합니다.
프로젝트를 예로 들어보겠습니다.

에이전트 런타임에 배포하기 위해 ADK 프로젝트를 준비하려면 다음 안내를 따르세요.

1. 개발 환경의 터미널 창에서
    에이전트 폴더가 포함된 **상위 디렉터리**입니다. 예를 들어, 귀하의 경우
    프로젝트 구조는 다음과 같습니다

    ```
    your-project-directory/
    ├── my_agent/
    │   ├── __init__.py
    │   ├── agent.py
    │   └── .env
    ```

    `your-project-directory/`로 이동

1. 에이전트 CLI `scaffold enhance` 명령을 실행하여 배포에 필요한 파일을 추가합니다.
    당신의 프로젝트.

    ```shell
    agents-cli scaffold enhance --deployment-target agent_engine
    ```

1. Agents CLI 도구의 지침을 따릅니다. 일반적으로 수락할 수 있습니다.
    모든 질문에 대한 기본 답변입니다. 하지만 **GCP 지역**의 경우
    옵션 중 하나를 선택했는지 확인하세요.
    [supported regions](https://docs.cloud.google.com/agent-builder/locations#supported-regions-agent-engine)
    에이전트 런타임용.

이 프로세스를 성공적으로 완료하면 도구에 다음 메시지가 표시됩니다.

```
> Success! Your agent project is ready.
```

!!! tip "메모"
    Agents CLI 도구는 동시에 Google Cloud에 연결하라는 알림을 표시할 수 있습니다.
    실행 중이지만 이 단계에서는 해당 연결이 *필요하지 않습니다*.

Agents CLI가 ADK 프로젝트에 적용한 변경 사항에 대한 자세한 내용은 다음을 참조하세요.
[Changes to your ADK project](#adk-agents-cli-changes).

### Google Cloud 프로젝트 {#connect-ad}에 연결

ADK 프로젝트를 배포하기 전에 Google Cloud와
프로젝트. Google Cloud 계정에 로그인한 후 다음 사항을 확인해야 합니다.
귀하의 배포 대상 프로젝트는 귀하의 계정에서 볼 수 있으며
현재 프로젝트로 구성됩니다.

Google Cloud에 연결하고 프로젝트를 나열하려면 다음 안내를 따르세요.

1. 개발 환경의 터미널 창에서
    Google 클라우드 계정:

    ```shell
    gcloud auth application-default login
    ```

1. Google Cloud 프로젝트 ID를 사용하여 대상 프로젝트를 설정합니다.

    ```shell
    gcloud config set project your-project-id-xxxxx
    ```

1. Google Cloud 대상 프로젝트가 설정되었는지 확인합니다.

    ```shell
    gcloud config get-value project
    ```

Google Cloud에 성공적으로 연결하고 클라우드 프로젝트를 설정한 후
ID를 사용하면 ADK 프로젝트 파일을 에이전트 런타임에 배포할 준비가 되었습니다.

### ADK 프로젝트 {#deploy-ad} 배포

Agents CLI를 사용하는 경우 `agents-cli deploy` 명령을 사용하여 배포합니다. 이
명령은 에이전트 코드에서 컨테이너를 빌드하고 이를 레지스트리에 푸시하며,
호스팅된 환경의 에이전트 런타임에 배포합니다.

!!! warning "중요한"
    *Google Cloud 대상 배포 프로젝트가 ***현재로 설정되어 있는지 확인하세요.
    프로젝트*** 이 단계를 수행하기 전에*. `agents-cli deploy` 명령은 다음을 사용합니다.
    배포를 수행할 때 현재 설정된 Google Cloud 프로젝트입니다. 에 대한
    현재 프로젝트 설정 및 확인에 대한 정보는 다음을 참조하세요.
    [Connect to your Google Cloud project](#connect-ad).

Google Cloud 프로젝트의 에이전트 런타임에 ADK 프로젝트를 배포하려면 다음 안내를 따르세요.

1. 터미널 창에서 에이전트 프로젝트 디렉터리(예:
    `your-project-directory/`).

2. Google Cloud 개발 환경에 에이전트 코드를 배포합니다.

    ```shell
    agents-cli deploy
    ```

    이 명령은 `pyproject.toml`에서 `deployment_target`를 읽고 배포합니다.
    구성된 대상(에이전트 런타임, Cloud Run, GKE)에 추가합니다.

3. (선택 사항) 프롬프트 응답 로깅 및
    콘텐츠 로그, 원격 측정 인프라 프로비저닝:

    ```shell
    agents-cli infra single-project
    ```

    자세한 내용은 다음을 참조하세요.
    [Observability Guide](https://google.github.io/agents-cli/guide/observability/).

이 프로세스가 성공적으로 완료되면 다음과 상호작용할 수 있습니다.
Google Cloud Agent Runtime에서 실행되는 에이전트. 테스트에 대한 자세한 내용은
배포된 에이전트, 참조
[Test deployed agent](/deploy/agent-runtime/test/).

### ADK 프로젝트 변경 사항 {#adk-agents-cli-changes}

Agents CLI 도구는 배포를 위해 프로젝트에 더 많은 파일을 추가합니다. 절차
아래에서는 기존 프로젝트 파일을 수정하기 전에 백업합니다. 이 가이드
을 사용합니다
[multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent)
프로젝트를 참조 사례로 사용하세요. 원본 프로젝트에는 다음 파일이 있습니다
시작하는 구조:

```
my_agent/
├─ __init__.py
├─ agent.py
└─ .env
```

에이전트 런타임 배포를 추가하기 위해 에이전트 CLI 스캐폴드 강화 명령을 실행한 후
정보에 따르면, 새로운 구조는 다음과 같습니다:

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

자세한 내용은 업데이트된 ADK 프로젝트 폴더의 *README.md* 파일을 참조하세요.
에이전트 CLI 사용에 대한 자세한 내용은 다음을 참조하세요.
[Agents CLI documentation](https://google.github.io/agents-cli/).

## 배포된 에이전트 테스트

ADK 에이전트 배포를 완료한 후에는 다음에서 워크플로를 테스트해야 합니다.
새로운 호스팅 환경. ADK 에이전트 테스트에 대한 자세한 내용은
에이전트 런타임에 배포됩니다. 참조
[Test deployed agents in Agent Runtime](/deploy/agent-runtime/test/).
