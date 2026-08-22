# ADK용 Agents CLI 빠른 시작

이 가이드는 Agents CLI를 사용하여 Agent Development Kit (ADK)를 빠르게 시작하고 실행하는 방법을 보여줍니다. Antigravity, Claude Code, Codex와 같은 코딩 에이전트와 함께 Agents CLI 도구 세트를 사용하여 ADK 에이전트를 빌드, 평가 및 배포할 수 있습니다. 자세한 내용은 [Agents CLI](https://google.github.io/agents-cli/) 문서를 참조하세요.
시작하기 전에 다음이 설치되어 있는지 확인하세요.

*   Python 3.11 이상: Agents CLI는 Python 기반 ADK 에이전트를 지원합니다.
*   환경 및 종속 항목을 관리하기 위한 [`uv`](https://docs.astral.sh/uv/getting-started/installation/) 도구
*   스킬을 설치하기 위한 [Node.js](https://nodejs.org/en/download)
*   [Antigravity](https://antigravity.google/), [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Codex](https://github.com/openai/codex)와 같은 코딩 에이전트

Google Cloud와 같은 서비스에 ADK 에이전트를 배포하려는 경우 다음 도구도 설치되어 있는지 확인하세요.

*   [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
*   [Terraform](https://developer.hashicorp.com/terraform/downloads)

## 설치

다음 명령어를 실행하여 Agents CLI를 설치합니다. 이 단계는 `agents-cli` 명령, ADK Python 패키지 및 컴퓨터에 이미 설치된 모든 코딩 에이전트에 ADK 스킬을 설치합니다.

```shell
uvx google-agents-cli setup
```

??? tip "대체 설치 방법"

    **pipx:**

    ```shell
    pipx install google-agents-cli && agents-cli setup
    ```

    **pip:**

    ```shell
    pip install google-agents-cli && agents-cli setup
    ```

    **스킬 전용:**

    ```shell
    npx skills add google/agents-cli
    ```

직접 실행해야 하는 명령어는 설치 명령어뿐입니다. 설치가 완료되면 코딩 에이전트를 사용하여 ADK 에이전트를 빌드하고 실행할 수 있습니다.

## 인증

Agents CLI에서 에이전트를 실행하려면 제너레이티브 AI API용 사용자 인증 정보가 필요합니다. 가장 간단한 옵션은 Google AI Studio의 Gemini API 키입니다. [API 키](https://aistudio.google.com/app/apikey) 페이지에서 키를 생성한 다음, 다음 단계에서 프로젝트를 스캐폴딩한 후 해당 `.env` 파일을 열고 다음과 같이 설정합니다.

```env title="업데이트: .env"
GEMINI_API_KEY=YOUR_API_KEY
```

동일한 파일의 세 가지 `GOOGLE_CLOUD_*` 줄을 주석 처리하여 SDK가 Vertex AI 대신 해당 키를 사용하도록 합니다.

??? note "대신 Google Cloud Agent Platform 사용하기"

    이미 Google Cloud 프로젝트가 있는 경우 Agents CLI는 애플리케이션 기본 사용자 인증 정보(ADC)를 가져옵니다.

    ```shell
    gcloud auth application-default login
    ```

    생성된 `.env` 파일의 `GOOGLE_CLOUD_*` 줄 주석 처리를 해제하고 프로젝트 식별자로 설정했는지 확인하세요. ADK로 Google Cloud 서비스 및 프로젝트에 연결하는 방법에 대한 자세한 내용은 ADK의 [Google Cloud 설정 가이드](/ko/get-started/google-cloud/)를 참조하세요.

## 에이전트 빌드

코딩 에이전트를 열고 스킬을 인식할 수 있는지 확인합니다.

=== "Antigravity"

    ```shell
    antigravity            # IDE 또는 터미널에서 실행
    # 환경에 Agents CLI 스킬이 나열되어 있는지 확인
    ```

=== "Claude Code"

    ```shell
    claude
    /skills                # 목록에 google-agents-cli-* 항목이 표시되는지 확인
    ```

=== "Codex"

    ```shell
    codex
    /skills                # 목록에 google-agents-cli-* 항목이 표시되는지 확인
    ```

??? note "기타 코딩 에이전트 사용"

    Agents CLI는 [스킬](https://agentskills.io/what-are-skills)을 지원하는 모든 코딩 에이전트와 작동합니다. 대부분의 에이전트는 `/skills` 명령이나 설정 패널을 통해 스킬을 나열합니다.

그런 다음 코딩 에이전트에게 빌드하려는 내용을 알립니다.

```shell title="코딩 에이전트 프롬프트"
Use agents-cli to build an agent that turns long text into short
bullet-point summaries
```

코딩 에이전트는 `google-agents-cli-workflow` 및 `google-agents-cli-scaffold` 스킬을 활성화하고 에이전트가 호출할 도구, 예상되는 입력 및 출력, 평가 기준에 대한 구체적인 질문을 한 후 프로젝트를 스캐폴딩합니다.

다음으로 코딩 에이전트는 `google-agents-cli-adk-code` 스킬을 사용하여 에이전트 코드를 `app/agent.py`에 작성합니다. 최종적으로 에이전트 코드, 테스트 및 평가 데이터 세트가 포함된 작동하는 프로젝트가 다음 파일 구조로 생성됩니다.

```none
my-agent/
    app/
        agent.py                # 메인 에이전트 코드
        fast_api_app.py         # 서버, 원격 분석 및 라우트
        app_utils/              # 세션 및 아티팩트 서비스
    tests/
        eval/                   # 평가 데이터 세트 및 메트릭
        integration/            # 엔드투엔드 에이전트 테스트
        unit/
    pyproject.toml              # 프로젝트 구성 및 종속 항목
    agents-cli-manifest.yaml    # Agents CLI 구성
    Dockerfile                  # 배포용 컨테이너 이미지
    GEMINI.md                   # 코딩 에이전트용 프로젝트 지침
    .env                        # API 키 또는 프로젝트 ID
```

에이전트를 테스트, 평가 및 배포하려는 경우 이 프로젝트 구조를 사용하세요. ADK 학습을 위한 단일 파일 에이전트를 생성하려면 대신 `adk create` 명령을 사용하세요.

## 에이전트 실행

코딩 에이전트에게 로컬 플레이그라운드를 시작하도록 요청하거나 직접 실행합니다.

```console
agents-cli playground
```

이 명령어는 핫 리로드를 통해 ADK 웹 인터페이스를 시작하므로 편집 시 변경 사항이 프로젝트에 바로 반영됩니다. 플레이그라운드는 [http://localhost:8080](http://localhost:8080)에서 액세스할 수 있습니다. 왼쪽 상단에서 에이전트를 선택하고 몇 개의 텍스트 문단을 붙여넣습니다. 에이전트가 짧은 글머리 기호 요약으로 응답합니다.

## 다음 단계: 에이전트 평가 및 배포

이제 Agents CLI를 설치하고 첫 번째 에이전트를 실행했으므로 다음과 같은 지침을 사용하여 코딩 에이전트로 평가 및 배포할 수 있습니다.

*   ***"이 에이전트에 대한 평가를 작성하고 실행해줘"***: 범위를 지정할 때 설정한 성공 기준에 따라 [에이전트를 평가](https://google.github.io/agents-cli/guide/evaluation/)합니다. 코딩 에이전트가 결과를 채점하고 원인별로 실패를 그룹화하며 통과할 때까지 에이전트 지침을 조정합니다.
*   ***"이 에이전트를 Cloud Run에 배포해줘"***: Agent Runtime, Cloud Run 또는 GKE로 [에이전트를 배포](/ko/deploy/agent-runtime/agents-cli/)합니다.
*   ***"내 에이전트를 위한 관찰 가능성 인프라를 설정해줘"***: 프롬프트-응답 로깅 및 콘텐츠 로그를 추가합니다.

평가, 배포 및 관찰 가능성을 포함한 전체 연습 과정은 Agents CLI [튜토리얼: 첫 번째 에이전트 빌드](https://google.github.io/agents-cli/guide/quickstart-tutorial/)를 참조하세요.
