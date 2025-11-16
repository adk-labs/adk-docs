# Vertex AI Agent Engine에 배포하기

<div class="language-support-tag" title="Vertex AI Agent Engine은 현재 Python만 지원합니다.">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span>
</div>

[Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)은 개발자가 프로덕션 환경에서 AI 에이전트를 배포, 관리, 확장할 수 있게 해주는 완전 관리형 Google Cloud 서비스입니다. Agent Engine은 프로덕션 환경에서 에이전트를 확장하기 위한 인프라를 처리하므로, 여러분은 지능적이고 영향력 있는 애플리케이션을 만드는 데 집중할 수 있습니다. 이 가이드는 ADK 프로젝트를 신속하게 배포하고자 할 때를 위한 빠른 배포 절차와, 에이전트를 Agent Engine에 신중하게 배포하고자 할 때를 위한 표준 단계별 절차를 제공합니다.

!!! example "미리보기: Vertex AI Express 모드"
    Google Cloud 프로젝트가 없더라도 [Vertex AI Express 모드](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)를 사용하여 Agent Engine을 무료로 사용해 볼 수 있습니다. 이 기능 사용에 대한 자세한 내용은 [표준 배포](#standard-deployment) 섹션을 참조하세요.

## 신속 배포

이 섹션에서는 [Agent Starter Pack](https://github.com/GoogleCloudPlatform/agent-starter-pack) (ASP)과 ADK 명령줄 인터페이스(CLI) 도구를 사용한 배포 방법을 설명합니다. 이 접근 방식은 ASP 도구를 사용하여 기존 프로젝트에 프로젝트 템플릿을 적용하고, 배포 아티팩트를 추가하며, 에이전트 프로젝트를 배포 준비 상태로 만듭니다. 다음 지침은 ASP를 사용하여 ADK 프로젝트 배포에 필요한 서비스들을 Google Cloud 프로젝트에 프로비저닝하는 방법을 보여줍니다.

-   [사전 요구사항](#prerequisites-ad): Google Cloud 계정, 프로젝트 설정 및 필수 소프트웨어 설치.
-   [ADK 프로젝트 준비](#prepare-ad): 배포 준비를 위해 기존 ADK 프로젝트 파일 수정.
-   [Google Cloud 프로젝트에 연결](#connect-ad): 개발 환경을 Google Cloud 및 Google Cloud 프로젝트에 연결.
-   [ADK 프로젝트 배포](#deploy-ad): Google Cloud 프로젝트에 필요한 서비스를 프로비저닝하고 ADK 프로젝트 코드 업로드.

배포된 에이전트 테스트에 대한 정보는 [배포된 에이전트 테스트](#test-deployment)를 참조하세요. Agent Starter Pack과 그 명령줄 도구 사용에 대한 자세한 정보는 [CLI 참조](https://googlecloudplatform.github.io/agent-starter-pack/cli/enhance.html)와 [개발 가이드](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html)를 참조하세요.

### 사전 요구사항 {#prerequisites-ad}

이 배포 경로를 사용하려면 다음 리소스가 구성되어 있어야 합니다.

-   **Google Cloud 계정**: 다음 리소스에 대한 관리자 접근 권한 필요.
-   **Google Cloud 프로젝트**: [결제가 활성화된](https://cloud.google.com/billing/docs/how-to/modify-project) 비어 있는 Google Cloud 프로젝트. 프로젝트 생성 정보는 [프로젝트 생성 및 관리](https://cloud.google.com/resource-manager/docs/creating-managing-projects)를 참조하세요.
-   **Python 환경**: 3.9에서 3.13 사이의 Python 버전.
-   **UV 도구**: Python 개발 환경 관리 및 ASP 도구 실행. 설치 정보는 [UV 설치](https://docs.astral.sh/uv/getting-started/installation/)를 참조하세요.
-   **Google Cloud CLI 도구**: gcloud 명령줄 인터페이스. 설치 정보는 [Google Cloud 명령줄 인터페이스](https://cloud.google.com/sdk/docs/install)를 참조하세요.
-   **Make 도구**: 빌드 자동화 도구. 대부분의 Unix 기반 시스템에 포함되어 있으며, 설치 정보는 [Make 도구](https://www.gnu.org/software/make/) 문서를 참조하세요.

### ADK 프로젝트 준비 {#prepare-ad}

ADK 프로젝트를 Agent Engine에 배포할 때는 배포 작업을 지원하기 위한 추가 파일이 필요합니다. 다음 ASP 명령어는 프로젝트를 백업한 후 배포 목적의 파일들을 프로젝트에 추가합니다.

이 지침은 배포를 위해 수정할 기존 ADK 프로젝트가 있다고 가정합니다. ADK 프로젝트가 없거나 테스트 프로젝트를 사용하려면, Python [빠른 시작](/adk-docs/get-started/quickstart/) 가이드를 완료하여 [multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent) 프로젝트를 생성하세요. 다음 지침에서는 `multi_tool_agent` 프로젝트를 예시로 사용합니다.

ADK 프로젝트를 Agent Engine에 배포하기 위해 준비하려면:

1.  개발 환경의 터미널 창에서 에이전트 폴더를 포함하는 **상위 디렉토리**로 이동합니다. 예를 들어, 프로젝트 구조가 다음과 같다면:

    ```
    your-project-directory/
    ├── multi_tool_agent/
    │   ├── __init__.py
    │   ├── agent.py
    │   └── .env
    ```

    `your-project-directory/`로 이동합니다.

1.  ASP `enhance` 명령어를 실행하여 배포에 필요한 파일들을 프로젝트에 추가합니다.

    ```shell
    uvx agent-starter-pack enhance --adk -d agent_engine
    ```

1.  ASP 도구의 지시를 따릅니다. 일반적으로 모든 질문에 기본 답변을 선택할 수 있습니다. 단, **GCP 리전** 옵션에서는 [Agent Engine이 지원하는 리전](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#supported-regions) 중 하나를 선택해야 합니다.

이 과정을 성공적으로 완료하면 도구는 다음 메시지를 표시합니다.

```
> Success! Your agent project is ready.
```

!!! tip "참고"
    실행 중에 ASP 도구가 Google Cloud 연결을 상기시키는 메시지를 표시할 수 있지만, 이 단계에서는 연결이 *필수*가 아닙니다.

ASP가 ADK 프로젝트에 적용하는 변경 사항에 대한 자세한 내용은 [ADK 프로젝트 변경 사항](#adk-asp-changes)을 참조하세요.

### Google Cloud 프로젝트에 연결 {#connect-ad}

ADK 프로젝트를 배포하기 전에 Google Cloud 및 프로젝트에 연결해야 합니다. Google Cloud 계정에 로그인한 후, 배포 대상 프로젝트가 계정에서 보이고 현재 프로젝트로 구성되어 있는지 확인해야 합니다.

Google Cloud에 연결하고 프로젝트를 나열하려면:

1.  개발 환경의 터미널 창에서 Google Cloud 계정에 로그인합니다.

    ```shell
    gcloud auth application-default login
    ```

2.  Google Cloud 프로젝트 ID를 사용하여 대상 프로젝트를 설정합니다.

    ```shell
    gcloud config set project your-project-id-xxxxx
    ```

3.  Google Cloud 대상 프로젝트가 설정되었는지 확인합니다.

    ```shell
    gcloud config get-value project
    ```

Google Cloud에 성공적으로 연결하고 Cloud 프로젝트 ID를 설정했다면, ADK 프로젝트 파일을 Agent Engine에 배포할 준비가 된 것입니다.

### ADK 프로젝트 배포 {#deploy-ad}

ASP 도구를 사용할 때, 배포는 단계적으로 이루어집니다. 첫 번째 단계에서는 `make` 명령어를 실행하여 Agent Engine에서 ADK 워크플로를 실행하는 데 필요한 서비스를 프로비저닝합니다. 두 번째 단계에서는 프로젝트 코드가 Agent Engine 서비스에 업로드되고 에이전트 프로젝트가 실행됩니다.

!!! warning "중요"
    *이 단계를 수행하기 전에 Google Cloud 배포 대상 프로젝트가 ***현재 프로젝트***로 설정되어 있는지 확인하세요.* `make backend` 명령어는 배포를 수행할 때 현재 설정된 Google Cloud 프로젝트를 사용합니다. 현재 프로젝트 설정 및 확인에 대한 정보는 [Google Cloud 프로젝트에 연결](#connect-ad)을 참조하세요.

Google Cloud 프로젝트의 Agent Engine에 ADK 프로젝트를 배포하려면:

1.  터미널 창에서 에이전트 폴더를 포함하는 상위 디렉토리(예: `your-project-directory/`)에 있는지 확인합니다.

1.  다음 ASP make 명령어를 실행하여 업데이트된 로컬 프로젝트의 코드를 Google Cloud 개발 환경에 배포합니다.

    ```shell
    make backend
    ```

이 과정이 성공적으로 완료되면, Google Cloud Agent Engine에서 실행 중인 에이전트와 상호 작용할 수 있습니다. 배포된 에이전트 테스트에 대한 자세한 내용은 다음 섹션을 참조하세요.

이 과정이 성공적으로 완료되면, Google Cloud Agent Engine에서 실행 중인 에이전트와 상호 작용할 수 있습니다. 배포된 에이전트 테스트에 대한 자세한 내용은 [배포된 에이전트 테스트](#test-deployment)를 참조하세요.

### ADK 프로젝트 변경 사항 {#adk-asp-changes}

ASP 도구는 배포를 위해 프로젝트에 더 많은 파일을 추가합니다. 아래 절차는 기존 프로젝트 파일을 수정하기 전에 백업합니다. 이 가이드는 [multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent) 프로젝트를 참조 예시로 사용합니다. 원래 프로젝트의 파일 구조는 다음과 같습니다.

```
multi_tool_agent/
├─ __init__.py
├─ agent.py
└─ .env
```

Agent Engine 배포 정보를 추가하기 위해 ASP enhance 명령어를 실행한 후의 새로운 구조는 다음과 같습니다.

```
multi-tool-agent/
├─ app/                 # 핵심 애플리케이션 코드
│   ├─ agent.py         # 주 에이전트 로직
│   ├─ agent_engine_app.py # Agent Engine 애플리케이션 로직
│   └─ utils/           # 유틸리티 함수 및 헬퍼
├─ .cloudbuild/         # Google Cloud Build를 위한 CI/CD 파이프라인 구성
├─ deployment/          # 인프라 및 배포 스크립트
├─ notebooks/           # 프로토타이핑 및 평가를 위한 Jupyter 노트북
├─ tests/               # 단위, 통합 및 부하 테스트
├─ Makefile             # 공통 명령어를 위한 Makefile
├─ GEMINI.md            # AI 지원 개발 가이드
└─ pyproject.toml       # 프로젝트 의존성 및 구성
```

자세한 내용은 업데이트된 ADK 프로젝트 폴더의 README.md 파일을 참조하세요. Agent Starter Pack 사용에 대한 자세한 정보는 [개발 가이드](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide.html)를 참조하세요.

## 표준 배포

이 섹션에서는 Agent Engine에 단계별로 배포하는 방법을 설명합니다. 이 지침은 배포 설정을 신중하게 관리하거나 Agent Engine으로 기존 배포를 수정하려는 경우에 더 적합합니다.

### 사전 요구사항

이 지침은 이미 ADK 프로젝트와 GCP 프로젝트가 정의되어 있다고 가정합니다. ADK 프로젝트가 없다면, [에이전트 정의](#define-your-agent)에서 테스트 프로젝트 생성 지침을 참조하세요.

!!! example "미리보기: Vertex AI Express 모드"
    기존 GCP 프로젝트가 없는 경우, [Vertex AI Express 모드](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)를 사용하여 Agent Engine을 무료로 체험할 수 있습니다.

=== "Google Cloud 프로젝트"

    배포 절차를 시작하기 전에 다음 사항을 확인하세요.

    1.  **Google Cloud 프로젝트**: [Vertex AI API가 활성화된](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com) Google Cloud 프로젝트.

    2.  **인증된 gcloud CLI**: Google Cloud에 인증되어 있어야 합니다. 터미널에서 다음 명령어를 실행하세요.
        ```shell
        gcloud auth application-default login
        ```

    3.  **Google Cloud Storage (GCS) 버킷**: Agent Engine은 배포를 위해 에이전트의 코드와 의존성을 스테이징할 GCS 버킷이 필요합니다. 버킷이 없다면 [여기](https://cloud.google.com/storage/docs/creating-buckets)의 지침에 따라 생성하세요.

    4.  **Python 환경**: 3.9에서 3.13 사이의 Python 버전.

    5.  **Vertex AI SDK 설치**

        Agent Engine은 Python용 Vertex AI SDK의 일부입니다. 자세한 정보는 [Agent Engine 빠른 시작 문서](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/quickstart)를 참조할 수 있습니다.

        ```shell
        pip install google-cloud-aiplatform[adk,agent_engines]>=1.111
        ```

=== "Vertex AI Express 모드"

    배포 절차를 시작하기 전에 다음 사항을 확인하세요.

    1.  **Express 모드 프로젝트의 API 키**: [Express 모드 가입](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview#eligibility)에 따라 gmail 계정으로 Express 모드 프로젝트에 가입하세요. Agent Engine에서 사용할 API 키를 해당 프로젝트에서 받으세요!

    2.  **Python 환경**: 3.9에서 3.13 사이의 Python 버전.

    3.  **Vertex AI SDK 설치**

        Agent Engine은 Python용 Vertex AI SDK의 일부입니다. 자세한 정보는 [Agent Engine 빠른 시작 문서](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/quickstart)를 참조할 수 있습니다.

        ```shell
        pip install google-cloud-aiplatform[adk,agent_engines]>=1.111
        ```

### 에이전트 정의 {#define-your-agent}

이 지침은 배포를 위해 수정할 기존 ADK 프로젝트가 있다고 가정합니다. ADK 프로젝트가 없거나 테스트 프로젝트를 사용하려면, Python [빠른 시작](/adk-docs/get-started/quickstart/) 가이드를 완료하여 [multi_tool_agent](https://github.com/google/adk-docs/tree/main/examples/python/snippets/get-started/multi_tool_agent) 프로젝트를 생성하세요. 다음 지침에서는 `multi_tool_agent` 프로젝트를 예시로 사용합니다.

### Vertex AI 초기화

다음으로, Vertex AI SDK를 초기화합니다. 이는 SDK에 사용할 Google Cloud 프로젝트와 리전, 그리고 배포 파일을 스테이징할 위치를 알려줍니다.

!!! tip "IDE 사용자를 위한 팁"
    이 초기화 코드를 다음 3~6단계의 배포 로직과 함께 별도의 `deploy.py` 스크립트에 배치할 수 있습니다.

=== "Google Cloud 프로젝트"

    ```python title="deploy.py"
    import vertexai
    from agent import root_agent # agent.py에 에이전트가 없는 경우 수정하세요

    # TODO: 프로젝트에 맞게 이 값들을 채워 넣으세요
    PROJECT_ID = "your-gcp-project-id"
    LOCATION = "us-central1"  # 다른 옵션은 https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#supported-regions 참조
    STAGING_BUCKET = "gs://your-gcs-bucket-name"

    # Vertex AI SDK 초기화
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )
    ```

=== "Vertex AI Express 모드"

    ```python title="deploy.py"
    import vertexai
    from agent import root_agent # agent.py에 에이전트가 없는 경우 수정하세요

    # TODO: API 키에 맞게 이 값을 채워 넣으세요
    API_KEY = "your-express-mode-api-key"

    # Vertex AI SDK 초기화
    vertexai.init(
        api_key=API_KEY,
    )
    ```

### 배포를 위한 에이전트 준비

에이전트를 Agent Engine과 호환되게 하려면 `AdkApp` 객체로 감싸야 합니다.

```python title="deploy.py"
from vertexai import agent_engines

# 에이전트를 AdkApp 객체로 감싸기
app = agent_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)
```

!!!info
    AdkApp이 Agent Engine에 배포되면, 영구적인 관리형 세션 상태를 위해 자동으로 `VertexAiSessionService`를 사용합니다. 이를 통해 추가 구성 없이 다중 턴 대화 메모리를 제공합니다. 로컬 테스트의 경우, 애플리케이션은 기본적으로 임시 인메모리 세션 서비스를 사용합니다.

### 로컬에서 에이전트 테스트 (선택 사항)

배포하기 전에 로컬에서 에이전트의 동작을 테스트할 수 있습니다.

`async_stream_query` 메서드는 에이전트의 실행 추적을 나타내는 이벤트 스트림을 반환합니다.

```python title="deploy.py"
# 대화 기록을 유지하기 위한 로컬 세션 생성
session = await app.async_create_session(user_id="u_123")
print(session)
```

`create_session`의 예상 출력 (로컬):

```console
Session(id='c6a33dae-26ef-410c-9135-b434a528291f', app_name='default-app-name', user_id='u_123', state={}, events=[], last_update_time=1743440392.8689594)
```

에이전트에 쿼리를 보냅니다. 다음 코드를 "deploy.py" 파이썬 스크립트나 노트북에 복사-붙여넣기 하세요.

```py title="deploy.py"
events = []
async for event in app.async_stream_query(
    user_id="u_123",
    session_id=session.id,
    message="whats the weather in new york",
):
    events.append(event)

# 전체 이벤트 스트림은 에이전트의 사고 과정을 보여줍니다
print("--- Full Event Stream ---")
for event in events:
    print(event)

# 빠른 테스트를 위해 최종 텍스트 응답만 추출할 수 있습니다
final_text_responses = [
    e for e in events
    if e.get("content", {}).get("parts", [{}])[0].get("text")
    and not e.get("content", {}).get("parts", [{}])[0].get("function_call")
]
if final_text_responses:
    print("\n--- Final Response ---")
    print(final_text_responses[0]["content"]["parts"][0]["text"])
```

#### 출력 이해하기

위 코드를 실행하면 몇 가지 유형의 이벤트를 볼 수 있습니다.

*   **도구 호출 이벤트**: 모델이 도구(예: `get_weather`)를 호출하도록 요청합니다.
*   **도구 응답 이벤트**: 시스템이 도구 호출 결과를 모델에 다시 제공합니다.
*   **모델 응답 이벤트**: 에이전트가 도구 결과를 처리한 후의 최종 텍스트 응답입니다.

`async_stream_query`의 예상 출력 (로컬):

```console
{'parts': [{'function_call': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-a33fedb0-29e6-4d0c-9eb3-00c402969395', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

### Agent Engine에 배포하기

에이전트의 로컬 동작에 만족했다면 배포할 수 있습니다. Python SDK나 `adk` 명령줄 도구를 사용하여 이 작업을 수행할 수 있습니다.

이 과정은 코드를 패키징하고, 컨테이너로 빌드한 후, 관리형 Agent Engine 서비스에 배포합니다. 이 과정은 몇 분 정도 걸릴 수 있습니다.

=== "ADK CLI"

    터미널에서 `adk deploy` 명령줄 도구를 사용하여 배포할 수 있습니다. 다음 예제 배포 명령어는 `multi_tool_agent` 샘플 코드를 배포할 프로젝트로 사용합니다.

    ```shell
    adk deploy agent_engine \
        --project=my-cloud-project-xxxxx \
        --region=us-central1 \
        --staging_bucket=gs://my-cloud-project-staging-bucket-name \
        --display_name="My Agent Name" \
        /multi_tool_agent
    ```

    사용 가능한 스토리지 버킷의 이름은 Google Cloud 콘솔의 배포 프로젝트 내 [Cloud Storage 버킷](https://pantheon.corp.google.com/storage/browser) 섹션에서 찾을 수 있습니다. `adk deploy` 명령어 사용에 대한 자세한 내용은 [ADK CLI 참조](/adk-docs/api-reference/cli/cli.html#adk-deploy)를 참조하세요.

    !!! tip
        ADK 프로젝트를 배포할 때 주 ADK 에이전트 정의(`root_agent`)를 찾을 수 있도록 하세요.

=== "Python"

    이 코드 블록은 Python 스크립트나 노트북에서 배포를 시작합니다.

    ```python title="deploy.py"
    from vertexai import agent_engines

    remote_app = agent_engines.create(
        agent_engine=app,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]"   
        ]
    )

    print(f"Deployment finished!")
    print(f"Resource Name: {remote_app.resource_name}")
    # Resource Name: "projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"
    #       참고: PROJECT_NUMBER는 PROJECT_ID와 다릅니다.
    ```

=== "Vertex AI Express 모드"

    Vertex AI Express 모드는 ADK CLI 배포와 Python 배포를 모두 지원합니다.

    다음 예제 배포 명령어는 `multi_tool_agent` 샘플 코드를 Express 모드로 배포할 프로젝트로 사용합니다.

    ```shell
    adk deploy agent_engine \
        --display_name="My Agent Name" \
        --api_key=your-api-key-here
        /multi_tool_agent
    ```

    !!! tip
        ADK 프로젝트를 배포할 때 주 ADK 에이전트 정의(`root_agent`)를 찾을 수 있도록 하세요.

    이 코드 블록은 Python 스크립트나 노트북에서 배포를 시작합니다.

    ```python title="deploy.py"
    from vertexai import agent_engines

    remote_app = agent_engines.create(
        agent_engine=app,
        requirements=[
            "google-cloud-aiplatform[adk,agent_engines]"   
        ]
    )

    print(f"Deployment finished!")
    print(f"Resource Name: {remote_app.resource_name}")
    # Resource Name: "projects/{PROJECT_NUMBER}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"
    #       참고: PROJECT_NUMBER는 PROJECT_ID와 다릅니다.
    ```

#### 모니터링 및 확인

*   Google Cloud 콘솔의 [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)에서 배포 상태를 모니터링할 수 있습니다.
*   `remote_app.resource_name`은 배포된 에이전트의 고유 식별자입니다. 에이전트와 상호 작용하려면 이 정보가 필요합니다. ADK CLI 명령어가 반환하는 응답에서도 이 정보를 얻을 수 있습니다.
*   추가적인 세부 정보는 Agent Engine 문서의 [에이전트 배포](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/deploy) 및 [배포된 에이전트 관리](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)를 참조할 수 있습니다.

## 배포된 에이전트 테스트 {#test-deployment}

에이전트를 Agent Engine에 배포 완료한 후, Google Cloud 콘솔을 통해 배포된 에이전트를 보고, REST 호출이나 Python용 Vertex AI SDK를 사용하여 에이전트와 상호 작용할 수 있습니다.

Cloud 콘솔에서 배포된 에이전트를 보려면:

-   Google Cloud 콘솔의 Agent Engine 페이지로 이동합니다:
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

이 페이지에는 현재 선택된 Google Cloud 프로젝트에 배포된 모든 에이전트가 나열됩니다. 에이전트가 보이지 않는 경우, Google Cloud 콘솔에서 대상 프로젝트를 선택했는지 확인하세요. 기존 Google Cloud 프로젝트 선택에 대한 자세한 내용은 [프로젝트 생성 및 관리](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects)를 참조하세요.

### Google Cloud 프로젝트 정보 찾기

배포를 테스트하려면 프로젝트의 주소와 리소스 식별 정보(`PROJECT_ID`, `LOCATION`, `RESOURCE_ID`)가 필요합니다. Cloud 콘솔이나 `gcloud` 명령줄 도구를 사용하여 이 정보를 찾을 수 있습니다.

!!! note "Vertex AI Express 모드 API 키"
    Vertex AI Express 모드를 사용하는 경우, 이 단계를 건너뛰고 API 키를 사용할 수 있습니다.

Google Cloud 콘솔에서 프로젝트 정보를 찾으려면:

1.  Google Cloud 콘솔에서 Agent Engine 페이지로 이동합니다:
    [https://console.cloud.google.com/vertex-ai/agents/agent-engines](https://console.cloud.google.com/vertex-ai/agents/agent-engines)

2.  페이지 상단에서 **API URL**을 선택한 다음, 배포된 에이전트의 **쿼리 URL** 문자열을 복사합니다. 형식은 다음과 같습니다:

        https://$(LOCATION_ID)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION_ID)/reasoningEngines/$(RESOURCE_ID):query

`gcloud`로 프로젝트 정보를 찾으려면:

1.  개발 환경에서 Google Cloud에 인증되었는지 확인하고 다음 명령어를 실행하여 프로젝트를 나열합니다:

    ```shell
    gcloud projects list
    ```

2.  배포에 사용된 프로젝트 ID를 가져와 다음 명령어를 실행하여 추가 세부 정보를 얻습니다:

    ```shell
    gcloud asset search-all-resources \
        --scope=projects/$(PROJECT_ID) \
        --asset-types='aiplatform.googleapis.com/ReasoningEngine' \
        --format="table(name,assetType,location,reasoning_engine_id)"
    ```

### REST 호출을 사용한 테스트

배포된 에이전트와 Agent Engine에서 상호 작용하는 간단한 방법은 `curl` 도구를 사용한 REST 호출입니다. 이 섹션에서는 에이전트 연결 확인 방법과 배포된 에이전트의 요청 처리 테스트 방법을 설명합니다.

#### 에이전트 연결 확인

Cloud 콘솔의 Agent Engine 섹션에서 사용할 수 있는 **쿼리 URL**을 사용하여 실행 중인 에이전트와의 연결을 확인할 수 있습니다. 이 확인은 배포된 에이전트를 실행하지는 않지만 에이전트에 대한 정보를 반환합니다.

배포된 에이전트로부터 응답을 받기 위해 REST 호출을 보내려면:

-   개발 환경의 터미널 창에서 요청을 빌드하고 실행합니다:

    === "Google Cloud 프로젝트"

        ```shell
        curl -X GET \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            "https://$(LOCATION)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION)/reasoningEngines"
        ```

    === "Vertex AI Express 모드"
    
        ```shell
        curl -X GET \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            "https://aiplatform.googleapis.com/v1/reasoningEngines"
        ```

배포가 성공적이었다면, 이 요청은 유효한 요청 목록과 예상 데이터 형식으로 응답합니다.

!!! tip "에이전트 연결 접근 권한"
    이 연결 테스트는 호출하는 사용자가 배포된 에이전트에 대한 유효한 액세스 토큰을 가지고 있어야 합니다. 다른 환경에서 테스트할 때, 호출하는 사용자가 Google Cloud 프로젝트의 에이전트에 연결할 접근 권한이 있는지 확인하세요.

#### 에이전트 요청 보내기

에이전트 프로젝트로부터 응답을 받으려면 먼저 세션을 생성하고 세션 ID를 받은 다음, 해당 세션 ID를 사용하여 요청을 보내야 합니다. 이 과정은 다음 지침에 설명되어 있습니다.

REST를 통해 배포된 에이전트와의 상호 작용을 테스트하려면:

1.  개발 환경의 터미널 창에서 다음 템플릿을 사용하여 요청을 빌드하여 세션을 생성합니다:

    === "Google Cloud 프로젝트"

        ```shell
        curl \
            -H "Authorization: Bearer $(gcloud auth print-access-token)" \
            -H "Content-Type: application/json" \
            https://$(LOCATION)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION)/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

    === "Vertex AI Express 모드"
    
        ```shell
        curl \
            -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
            -H "Content-Type: application/json" \
            https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):query \
            -d '{"class_method": "async_create_session", "input": {"user_id": "u_123"},}'
        ```

2.  이전 명령어의 응답에서 **id** 필드로부터 생성된 **세션 ID**를 추출합니다:

    ```json
    {
        "output": {
            "userId": "u_123",
            "lastUpdateTime": 1757690426.337745,
            "state": {},
            "id": "4857885913439920384", # 세션 ID
            "appName": "9888888855577777776",
            "events": []
        }
    }
    ```

3.  개발 환경의 터미널 창에서 다음 템플릿과 이전 단계에서 생성된 세션 ID를 사용하여 요청을 빌드하여 에이전트에 메시지를 보냅니다:

    === "Google Cloud 프로젝트"

        ```shell
        curl \
        -H "Authorization: Bearer $(gcloud auth print-access-token)" \
        -H "Content-Type: application/json" \
        https://$(LOCATION)-aiplatform.googleapis.com/v1/projects/$(PROJECT_ID)/locations/$(LOCATION)/reasoningEngines/$(RESOURCE_ID):streamQuery?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "Hey whats the weather in new york today?",
        }
        }'
        ```

    === "Vertex AI Express 모드"

        ```shell
        curl \
        -H "x-goog-api-key:YOUR-EXPRESS-MODE-API-KEY" \
        -H "Content-Type: application/json" \
        https://aiplatform.googleapis.com/v1/reasoningEngines/$(RESOURCE_ID):streamQuery?alt=sse -d '{
        "class_method": "async_stream_query",
        "input": {
            "user_id": "u_123",
            "session_id": "4857885913439920384",
            "message": "Hey whats the weather in new york today?",
        }
        }'
        ```

이 요청은 배포된 에이전트 코드로부터 JSON 형식의 응답을 생성해야 합니다. REST 호출을 사용하여 Agent Engine에 배포된 ADK 에이전트와 상호 작용하는 방법에 대한 자세한 내용은 Agent Engine 문서의 [배포된 에이전트 관리](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview#console)와 [Agent Development Kit 에이전트 사용](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)을 참조하세요.

### Python을 사용한 테스트

Agent Engine에 배포된 에이전트를 더 정교하고 반복적으로 테스트하기 위해 Python 코드를 사용할 수 있습니다. 이 지침은 배포된 에이전트와 세션을 생성한 다음, 처리를 위해 에이전트에 요청을 보내는 방법을 설명합니다.

#### 원격 세션 생성

`remote_app` 객체를 사용하여 배포된 원격 에이전트에 연결을 생성합니다.

```py
# 새 스크립트에 있거나 ADK CLI를 사용하여 배포한 경우 다음과 같이 연결할 수 있습니다:
# remote_app = agent_engines.get("your-agent-resource-name")
remote_session = await remote_app.async_create_session(user_id="u_456")
print(remote_session)
```

`create_session`의 예상 출력 (원격):

```console
{'events': [],
'user_id': 'u_456',
'state': {},
'id': '7543472750996750336',
'app_name': '7917477678498709504',
'last_update_time': 1743683353.030133}
```

`id` 값은 세션 ID이며, `app_name`은 Agent Engine에 배포된 에이전트의 리소스 ID입니다.

#### 원격 에이전트에 쿼리 보내기

```py
async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message="whats the weather in new york",
):
    print(event)
```

`async_stream_query`의 예상 출력 (원격):

```console
{'parts': [{'function_call': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'args': {'city': 'new york'}, 'name': 'get_weather'}}], 'role': 'model'}
{'parts': [{'function_response': {'id': 'af-f1906423-a531-4ecf-a1ef-723b05e85321', 'name': 'get_weather', 'response': {'status': 'success', 'report': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}}}], 'role': 'user'}
{'parts': [{'text': 'The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).'}], 'role': 'model'}
```

Agent Engine에 배포된 ADK 에이전트와의 상호 작용에 대한 자세한 내용은 Agent Engine 문서의 [배포된 에이전트 관리](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/manage/overview)와 [Agent Development Kit 에이전트 사용](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk)을 참조하세요.

#### 멀티모달 쿼리 보내기

에이전트에 멀티모달 쿼리(예: 이미지 포함)를 보내려면, `async_stream_query`의 `message` 매개변수를 `types.Part` 객체 목록으로 구성할 수 있습니다. 각 파트는 텍스트 또는 이미지일 수 있습니다.

이미지를 포함하려면, 이미지의 Google Cloud Storage (GCS) URI를 제공하여 `types.Part.from_uri`를 사용할 수 있습니다.

```python
from google.genai import types

image_part = types.Part.from_uri(
    file_uri="gs://cloud-samples-data/generative-ai/image/scones.jpg",
    mime_type="image/jpeg",
)
text_part = types.Part.from_text(
    text="What is in this image?",
)

async for event in remote_app.async_stream_query(
    user_id="u_456",
    session_id=remote_session["id"],
    message=[text_part, image_part],
):
    print(event)
```

!!!note 
    모델과의 기본 통신에는 이미지에 대한 Base64 인코딩이 포함될 수 있지만, Agent Engine에 배포된 에이전트에 이미지 데이터를 보내는 권장 및 지원되는 방법은 GCS URI를 제공하는 것입니다.

## 배포 페이로드 {#payload}

ADK 에이전트 프로젝트를 Agent Engine에 배포하면 다음 콘텐츠가 서비스에 업로드됩니다.

- ADK 에이전트 코드
- ADK 에이전트 코드에 선언된 모든 의존성

배포에는 ADK API 서버나 ADK 웹 사용자 인터페이스 라이브러리가 포함되지 *않습니다*. Agent Engine 서비스가 ADK API 서버 기능을 위한 라이브러리를 제공합니다.

## 배포 정리

테스트 목적으로 배포를 수행한 경우, 작업이 끝난 후 클라우드 리소스를 정리하는 것이 좋습니다. Google Cloud 계정에 예기치 않은 요금이 부과되는 것을 방지하기 위해 배포된 Agent Engine 인스턴스를 삭제할 수 있습니다.

```python
remote_app.delete(force=True)
```

`force=True` 매개변수는 세션과 같이 배포된 에이전트에서 생성된 모든 하위 리소스도 삭제합니다. Google Cloud의 [Agent Engine UI](https://console.cloud.google.com/vertex-ai/agents/agent-engines)를 통해 배포된 에이전트를 삭제할 수도 있습니다.