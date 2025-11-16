# Cloud Run에 배포하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

[Cloud Run](https://cloud.google.com/run)은 Google의 확장 가능한 인프라 위에서 코드를 직접 실행할 수 있게 해주는 완전 관리형 플랫폼입니다.

에이전트를 배포하려면 `adk deploy cloud_run` 명령어 *(Python에 권장)*를 사용하거나, Cloud Run을 통해 `gcloud run deploy` 명령어를 사용할 수 있습니다.

## 에이전트 샘플

각 명령어에 대해, [LLM 에이전트](../agents/llm-agents.md) 페이지에 정의된 `Capital Agent` 샘플을 참조할 것입니다. 이 샘플이 특정 디렉터리(예: `capital_agent`) 안에 있다고 가정합니다.

계속 진행하려면, 에이전트 코드가 다음과 같이 구성되어 있는지 확인하세요.

=== "Python"

    1. 에이전트 코드가 에이전트 디렉터리 내 `agent.py`라는 파일에 있습니다.
    2. 에이전트 변수 이름이 `root_agent`입니다.
    3. `__init__.py` 파일이 에이전트 디렉터리 내에 있으며 `from . import agent`를 포함합니다.
    4. `requirements.txt` 파일이 에이전트 디렉터리에 있습니다.

=== "Go"

    1. 애플리케이션의 진입점(main 패키지 및 main() 함수)이 단일 Go 파일에 있습니다. `main.go`를 사용하는 것이 강력한 관례입니다.
    2. 에이전트 인스턴스가 런처(launcher) 설정에 전달되며, 일반적으로 `services.NewSingleAgentLoader(agent)`를 사용합니다. `adkgo` 도구는 이 런처를 사용하여 올바른 서비스로 에이전트를 시작합니다.
    3. 의존성 관리를 위해 `go.mod`와 `go.sum` 파일이 프로젝트 디렉터리에 있습니다.

    자세한 내용은 다음 섹션을 참조하세요. Github 리포지토리에서 [샘플 앱](https://github.com/google/adk-docs/tree/main/examples/go/cloud-run)을 찾을 수도 있습니다.

=== "Java"

    1. 에이전트 코드가 에이전트 디렉터리 내 `CapitalAgent.java`라는 파일에 있습니다.
    2. 에이전트 변수는 전역 변수이며 `public static final BaseAgent ROOT_AGENT` 형식을 따릅니다.
    3. 에이전트 정의가 정적(static) 클래스 메서드에 있습니다.

    자세한 내용은 다음 섹션을 참조하세요. Github 리포지토리에서 [샘플 앱](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run)을 찾을 수도 있습니다.

## 환경 변수

[설정 및 설치](../get-started/installation.md) 가이드에 설명된 대로 환경 변수를 설정하세요.

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # 또는 선호하는 위치
export GOOGLE_GENAI_USE_VERTEXAI=True
```

*(`your-project-id`를 실제 GCP 프로젝트 ID로 바꾸세요)*

또는 AI Studio의 API 키를 사용할 수도 있습니다.

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1 # 또는 선호하는 위치
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY=your-api-key
```
*(`your-project-id`를 실제 GCP 프로젝트 ID로, `your-api-key`를 AI Studio의 실제 API 키로 바꾸세요)*

## 사전 준비 사항

1. Google Cloud 프로젝트가 있어야 합니다. 다음 정보를 알아야 합니다.
    1. 프로젝트 이름 (예: "my-project")
    2. 프로젝트 위치 (예: "us-central1")
    3. 서비스 계정 (예: "1234567890-compute@developer.gserviceaccount.com")
    4. GOOGLE_API_KEY

## 보안 비밀 (Secret)

서비스 계정이 읽을 수 있는 보안 비밀을 생성했는지 확인하세요.

### GOOGLE_API_KEY 보안 비밀 항목

보안 비밀을 수동으로 생성하거나 CLI를 사용할 수 있습니다.
```bash
echo "<<여기에 GOOGLE_API_KEY를 입력하세요>>" | gcloud secrets create GOOGLE_API_KEY --project=my-project --data-file=-
```

### 읽기 권한
서비스 계정이 이 보안 비밀을 읽을 수 있도록 적절한 권한을 부여해야 합니다.
```bash
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY --member="serviceAccount:1234567890-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor" --project=my-project
```

## 배포 페이로드 {#payload}

ADK 에이전트 워크플로우를 Google Cloud Run에 배포할 때, 다음 콘텐츠가 서비스에 업로드됩니다.

- ADK 에이전트 코드
- ADK 에이전트 코드에 선언된 모든 의존성
- 에이전트가 사용하는 ADK API 서버 코드 버전

기본 배포에는 ADK 웹 사용자 인터페이스 라이브러리가 포함되지 *않습니다*. `adk deploy cloud_run` 명령어의 `--with_ui` 옵션과 같이 배포 설정으로 지정하지 않는 한 포함되지 않습니다.

## 배포 명령어

=== "Python - adk CLI"

    ### adk CLI

    `adk deploy cloud_run` 명령어는 에이전트 코드를 Google Cloud Run에 배포합니다.

    Google Cloud에 인증했는지 확인하세요 (`gcloud auth login` 및 `gcloud config set project <your-project-id>`).

    #### 환경 변수 설정

    선택 사항이지만 권장됩니다: 환경 변수를 설정하면 배포 명령어가 더 깔끔해질 수 있습니다.

    ```bash
    # Google Cloud 프로젝트 ID 설정
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

    # 원하는 Google Cloud 위치 설정
    export GOOGLE_CLOUD_LOCATION="us-central1" # 예시 위치

    # 에이전트 코드 디렉터리 경로 설정
    export AGENT_PATH="./capital_agent" # capital_agent가 현재 디렉터리에 있다고 가정

    # Cloud Run 서비스 이름 설정 (선택 사항)
    export SERVICE_NAME="capital-agent-service"

    # 애플리케이션 이름 설정 (선택 사항)
    export APP_NAME="capital-agent-app"
    ```

    #### 명령어 사용법

    ##### 최소 명령어

    ```bash
    adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    $AGENT_PATH
    ```

    ##### 선택적 플래그를 포함한 전체 명령어

    ```bash
    adk deploy cloud_run \
    --project=$GOOGLE_CLOUD_PROJECT \
    --region=$GOOGLE_CLOUD_LOCATION \
    --service_name=$SERVICE_NAME \
    --app_name=$APP_NAME \
    --with_ui \
    $AGENT_PATH
    ```

    ##### 인수

    * `AGENT_PATH`: (필수) 에이전트 소스 코드가 포함된 디렉터리의 경로를 지정하는 위치 인수 (예: 예제의 `$AGENT_PATH` 또는 `capital_agent/`). 이 디렉터리에는 최소한 `__init__.py`와 주 에이전트 파일(예: `agent.py`)이 포함되어야 합니다.

    ##### 옵션

    * `--project TEXT`: (필수) Google Cloud 프로젝트 ID (예: `$GOOGLE_CLOUD_PROJECT`).
    * `--region TEXT`: (필수) 배포를 위한 Google Cloud 위치 (예: `$GOOGLE_CLOUD_LOCATION`, `us-central1`).
    * `--service_name TEXT`: (선택) Cloud Run 서비스의 이름 (예: `$SERVICE_NAME`). 기본값은 `adk-default-service-name`입니다.
    * `--app_name TEXT`: (선택) ADK API 서버의 애플리케이션 이름 (예: `$APP_NAME`). 기본값은 `AGENT_PATH`로 지정된 디렉터리의 이름입니다 (예: `AGENT_PATH`가 `./capital_agent`인 경우 `capital_agent`).
    * `--agent_engine_id TEXT`: (선택) Vertex AI Agent Engine을 통해 관리형 세션 서비스를 사용하는 경우, 해당 리소스 ID를 여기에 제공하세요.
    * `--port INTEGER`: (선택) 컨테이너 내에서 ADK API 서버가 수신 대기할 포트 번호입니다. 기본값은 8000입니다.
    * `--with_ui`: (선택) 이 플래그가 포함되면 에이전트 API 서버와 함께 ADK 개발 UI를 배포합니다. 기본적으로 API 서버만 배포됩니다.
    * `--temp_folder TEXT`: (선택) 배포 과정에서 생성되는 중간 파일을 저장할 디렉터리를 지정합니다. 기본값은 시스템의 임시 디렉터리에 타임스탬프가 찍힌 폴더입니다. *(참고: 이 옵션은 문제를 해결하는 경우가 아니면 일반적으로 필요하지 않습니다.)*
    * `--help`: 도움말 메시지를 표시하고 종료합니다.

    ##### 인증된 접근
    배포 과정 중에 `[your-service-name]에 대한 인증되지 않은 호출을 허용하시겠습니까? (y/N)?`라는 메시지가 나타날 수 있습니다.

    * 에이전트의 API 엔드포인트에 인증 없이 공개적으로 접근하도록 허용하려면 `y`를 입력하세요.
    * 인증이 필요하도록 하려면 `N`을 입력하거나 기본값으로 Enter 키를 누르세요 (예: "에이전트 테스트하기" 섹션에 표시된 ID 토큰 사용).

    성공적으로 실행되면, 이 명령어는 에이전트를 Cloud Run에 배포하고 배포된 서비스의 URL을 제공합니다.

=== "Python - gcloud CLI"

    ### Python용 gcloud CLI

    또는, `Dockerfile`과 함께 표준 `gcloud run deploy` 명령어를 사용하여 배포할 수도 있습니다. 이 방법은 `adk` 명령어에 비해 더 많은 수동 설정이 필요하지만, 특히 에이전트를 사용자 정의 [FastAPI](https://fastapi.tiangolo.com/) 애플리케이션에 내장하려는 경우 유연성을 제공합니다.

    Google Cloud에 인증했는지 확인하세요 (`gcloud auth login` 및 `gcloud config set project <your-project-id>`).

    #### 프로젝트 구조

    프로젝트 파일을 다음과 같이 구성하세요.

    ```txt
    your-project-directory/
    ├── capital_agent/
    │   ├── __init__.py
    │   └── agent.py       # 에이전트 코드 ("에이전트 샘플" 탭 참조)
    ├── main.py            # FastAPI 애플리케이션 진입점
    ├── requirements.txt   # Python 의존성
    └── Dockerfile         # 컨테이너 빌드 지침
    ```

    `your-project-directory/`의 루트에 다음 파일들(`main.py`, `requirements.txt`, `Dockerfile`)을 생성하세요.

    #### 코드 파일

    1. 이 파일은 ADK의 `get_fast_api_app()`을 사용하여 FastAPI 애플리케이션을 설정합니다.

        ```python title="main.py"
        import os

        import uvicorn
        from fastapi import FastAPI
        from google.adk.cli.fast_api import get_fast_api_app

        # main.py가 위치한 디렉터리 가져오기
        AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
        # 세션 서비스 URI 예시 (예: SQLite)
        SESSION_SERVICE_URI = "sqlite:///./sessions.db"
        # CORS에 허용된 출처 예시
        ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
        # 웹 인터페이스를 제공할 경우 web=True, 그렇지 않으면 False로 설정
        SERVE_WEB_INTERFACE = True

        # FastAPI 앱 인스턴스를 가져오는 함수 호출
        # 에이전트 디렉터리 이름('capital_agent')이 에이전트 폴더와 일치하는지 확인
        app: FastAPI = get_fast_api_app(
            agents_dir=AGENT_DIR,
            session_service_uri=SESSION_SERVICE_URI,
            allow_origins=ALLOWED_ORIGINS,
            web=SERVE_WEB_INTERFACE,
        )

        # 필요한 경우 아래에 더 많은 FastAPI 라우트나 설정을 추가할 수 있습니다
        # 예시:
        # @app.get("/hello")
        # async def read_root():
        #     return {"Hello": "World"}

        if __name__ == "__main__":
            # Cloud Run에서 제공하는 PORT 환경 변수를 사용, 기본값은 8080
            uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
        ```

        *참고: `agent_dir`를 `main.py`가 있는 디렉터리로 지정하고, Cloud Run 호환성을 위해 `os.environ.get("PORT", 8080)`을 사용합니다.*

    2. 필요한 Python 패키지 목록을 작성합니다.

        ```txt title="requirements.txt"
        google-adk
        # 에이전트에 필요한 다른 의존성 추가
        ```

    3. 컨테이너 이미지를 정의합니다.

        ```dockerfile title="Dockerfile"
        FROM python:3.13-slim
        WORKDIR /app

        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        RUN adduser --disabled-password --gecos "" myuser && \
            chown -R myuser:myuser /app

        COPY . .

        USER myuser

        ENV PATH="/home/myuser/.local/bin:$PATH"

        CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
        ```

    #### 여러 에이전트 정의하기

    `your-project-directory/`의 루트에 별도의 폴더를 생성하여 동일한 Cloud Run 인스턴스 내에 여러 에이전트를 정의하고 배포할 수 있습니다. 각 폴더는 하나의 에이전트를 나타내며, 설정에 `root_agent`를 정의해야 합니다.

    구조 예시:

    ```txt
    your-project-directory/
    ├── capital_agent/
    │   ├── __init__.py
    │   └── agent.py       # `root_agent` 정의 포함
    ├── population_agent/
    │   ├── __init__.py
    │   └── agent.py       # `root_agent` 정의 포함
    └── ...
    ```

    #### `gcloud`를 사용하여 배포하기

    터미널에서 `your-project-directory`로 이동하세요.

    ```bash
    gcloud run deploy capital-agent-service \
    --source . \
    --region $GOOGLE_CLOUD_LOCATION \
    --project $GOOGLE_CLOUD_PROJECT \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
    # 에이전트가 필요할 수 있는 다른 모든 환경 변수 추가
    ```

    * `capital-agent-service`: Cloud Run 서비스에 부여할 이름입니다.
    * `--source .`: gcloud에게 현재 디렉터리의 Dockerfile에서 컨테이너 이미지를 빌드하도록 지시합니다.
    * `--region`: 배포 리전을 지정합니다.
    * `--project`: GCP 프로젝트를 지정합니다.
    * `--allow-unauthenticated`: 서비스에 대한 공개 접근을 허용합니다. 비공개 서비스의 경우 이 플래그를 제거하세요.
    * `--set-env-vars`: 실행 중인 컨테이너에 필요한 환경 변수를 전달합니다. ADK와 에이전트가 요구하는 모든 변수(애플리케이션 기본 사용자 인증 정보를 사용하지 않는 경우 API 키 등)를 포함해야 합니다.

    `gcloud`는 Docker 이미지를 빌드하고 Google Artifact Registry에 푸시한 다음 Cloud Run에 배포합니다. 완료되면 배포된 서비스의 URL을 출력합니다.

    전체 배포 옵션 목록은 [`gcloud run deploy` 참조 문서](https://cloud.google.com/sdk/gcloud/reference/run/deploy)를 확인하세요.

=== "Go - adkgo CLI"

    ### adk CLI

    `adkgo` 명령어는 `google/adk-go` 리포지토리의 `cmd/adkgo` 아래에 있습니다. 사용하기 전에 `adk-go` 리포지토리의 루트에서 빌드해야 합니다.

    `go build ./cmd/adkgo`

    `adkgo deploy cloudrun` 명령어는 애플리케이션 배포를 자동화합니다. 직접 Dockerfile을 제공할 필요가 없습니다.

    #### 에이전트 코드 구조

    `adkgo` 도구를 사용할 때, `main.go` 파일은 런처 프레임워크를 사용해야 합니다. 이는 이 도구가 코드를 컴파일한 다음, 필요한 서비스를 시작하기 위해 결과 실행 파일을 특정 명령줄 인수(예: `web`, `api`, `a2a`)와 함께 실행하기 때문입니다. 런처는 이러한 인수를 올바르게 파싱하도록 설계되었습니다.

    `main.go`는 다음과 같아야 합니다.

    ```go title="main.go"
    --8<-- "examples/go/cloud-run/main.go"
    ```

    #### 작동 방식
    1. `adkgo` 도구는 `main.go`를 정적으로 연결된 Linux용 바이너리로 컴파일합니다.
    2. 이 바이너리를 최소한의 컨테이너에 복사하는 Dockerfile을 생성합니다.
    3. `gcloud`를 사용하여 이 컨테이너를 빌드하고 Cloud Run에 배포합니다.
    4. 배포 후, 새로운 서비스에 안전하게 연결하는 로컬 프록시를 시작합니다.

    Google Cloud에 인증했는지 확인하세요 (`gcloud auth login` 및 `gcloud config set project <your-project-id>`).

    #### 환경 변수 설정

    선택 사항이지만 권장됩니다: 환경 변수를 설정하면 배포 명령어가 더 깔끔해질 수 있습니다.

    ```bash
    # Google Cloud 프로젝트 ID 설정
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"

    # 원하는 Google Cloud 위치 설정
    export GOOGLE_CLOUD_LOCATION="us-central1"

    # 에이전트의 주 Go 파일 경로 설정
    export AGENT_PATH="./examples/go/cloud-run/main.go"

    # Cloud Run 서비스 이름 설정
    export SERVICE_NAME="capital-agent-service"
    ```

    #### 명령어 사용법

    ```bash
    ./adkgo deploy cloudrun \
        -p $GOOGLE_CLOUD_PROJECT \
        -r $GOOGLE_CLOUD_LOCATION \
        -s $SERVICE_NAME \
        --proxy_port=8081 \
        --server_port=8080 \
        -e $AGENT_PATH \
        --a2a --api --webui
    ```

    ##### 필수

    * `-p, --project_name`: Google Cloud 프로젝트 ID (예: `$GOOGLE_CLOUD_PROJECT`).
    * `-r, --region`: 배포를 위한 Google Cloud 위치 (예: `$GOOGLE_CLOUD_LOCATION`, `us-central1`).
    * `-s, --service_name`: Cloud Run 서비스의 이름 (예: `$SERVICE_NAME`).
    * `-e, --entry_point_path`: 에이전트 소스 코드가 포함된 주 Go 파일의 경로 (예: `$AGENT_PATH`).

    ##### 선택

    * `--proxy_port`: 인증 프록시가 수신 대기할 로컬 포트입니다. 기본값은 8081입니다.
    * `--server_port`: Cloud Run 컨테이너 내에서 서버가 수신 대기할 포트 번호입니다. 기본값은 8080입니다.
    * `--a2a`: 포함 시, Agent2Agent 통신을 활성화합니다. 기본적으로 활성화됩니다.
    * `--a2a_agent_url`: 공개 에이전트 카드에 광고될 A2A 에이전트 카드 URL입니다. 이 플래그는 `--a2a` 플래그와 함께 사용될 때만 유효합니다.
    * `--api`: 포함 시, ADK API 서버를 배포합니다. 기본적으로 활성화됩니다.
    * `--webui`: 포함 시, 에이전트 API 서버와 함께 ADK 개발 UI를 배포합니다. 기본적으로 활성화됩니다.
    * `--temp_dir`: 빌드 아티팩트를 위한 임시 디렉터리입니다. 기본값은 `os.TempDir()`입니다.
    * `--help`: 도움말 메시지를 표시하고 종료합니다.

    ##### 인증된 접근
    서비스는 기본적으로 `--no-allow-unauthenticated`로 배포됩니다.

    성공적으로 실행되면, 이 명령어는 에이전트를 Cloud Run에 배포하고 프록시를 통해 서비스에 접근할 수 있는 로컬 URL을 제공합니다.

=== "Java - gcloud CLI"

    ### Java용 gcloud CLI

    Java 에이전트는 표준 `gcloud run deploy` 명령어와 `Dockerfile`을 사용하여 배포할 수 있습니다. 이는 현재 Java 에이전트를 Google Cloud Run에 배포하는 권장 방법입니다.

    Google Cloud에 [인증](https://cloud.google.com/docs/authentication/gcloud)되었는지 확인하세요. 특히, 터미널에서 `gcloud auth login` 및 `gcloud config set project <your-project-id>` 명령어를 실행하세요.

    #### 프로젝트 구조

    프로젝트 파일을 다음과 같이 구성하세요.

    ```txt
    your-project-directory/
    ├── src/
    │   └── main/
    │       └── java/
    │             └── agents/
    │                 ├── capitalagent/
    │                     └── CapitalAgent.java    # 에이전트 코드
    ├── pom.xml                                    # Java adk 및 adk-dev 의존성
    └── Dockerfile                                 # 컨테이너 빌드 지침
    ```

    프로젝트 디렉터리의 루트에 `pom.xml`과 `Dockerfile`을 생성하세요. 에이전트 코드 파일(`CapitalAgent.java`)은 위와 같이 디렉터리 내에 위치시킵니다.

    #### 코드 파일

    1. 이것은 우리의 에이전트 정의입니다. [LLM 에이전트](../agents/llm-agents.md)에 있는 코드와 동일하지만 두 가지 주의 사항이 있습니다.

           * 에이전트는 이제 **전역 public static final 변수**로 초기화됩니다.

           * 에이전트의 정의는 정적(static) 메서드에서 노출되거나 선언 시 인라인으로 처리될 수 있습니다.

        `CapitalAgent` 예제에 대한 코드는 [examples](https://github.com/google/adk-docs/blob/main/examples/java/cloud-run/src/main/java/agents/capitalagent/CapitalAgent.java) 리포지토리에서 확인하세요.

    2. `pom.xml` 파일에 다음 의존성과 플러그인을 추가하세요.

        ```xml title="pom.xml"
        <dependencies>
          <dependency>
             <groupId>com.google.adk</groupId>
             <artifactId>google-adk</artifactId>
             <version>0.1.0</version>
          </dependency>
          <dependency>
             <groupId>com.google.adk</groupId>
             <artifactId>google-adk-dev</artifactId>
             <version>0.1.0</version>
          </dependency>
        </dependencies>

        <plugin>
          <groupId>org.codehaus.mojo</groupId>
          <artifactId>exec-maven-plugin</artifactId>
          <version>3.2.0</version>
          <configuration>
            <mainClass>com.google.adk.web.AdkWebServer</mainClass>
            <classpathScope>compile</classpathScope>
          </configuration>
        </plugin>
        ```

    3.  컨테이너 이미지를 정의합니다.

        ```dockerfile title="Dockerfile"
        --8<-- "examples/java/cloud-run/Dockerfile"
        ```

    #### `gcloud`를 사용하여 배포하기

    터미널에서 `your-project-directory`로 이동하세요.

    ```bash
    gcloud run deploy capital-agent-service \
    --source . \
    --region $GOOGLE_CLOUD_LOCATION \
    --project $GOOGLE_CLOUD_PROJECT \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
    # 에이전트가 필요할 수 있는 다른 모든 환경 변수 추가
    ```

    * `capital-agent-service`: Cloud Run 서비스에 부여할 이름입니다.
    * `--source .`: gcloud에게 현재 디렉터리의 Dockerfile에서 컨테이너 이미지를 빌드하도록 지시합니다.
    * `--region`: 배포 리전을 지정합니다.
    * `--project`: GCP 프로젝트를 지정합니다.
    * `--allow-unauthenticated`: 서비스에 대한 공개 접근을 허용합니다. 비공개 서비스의 경우 이 플래그를 제거하세요.
    * `--set-env-vars`: 실행 중인 컨테이너에 필요한 환경 변수를 전달합니다. ADK와 에이전트가 요구하는 모든 변수(애플리케이션 기본 사용자 인증 정보를 사용하지 않는 경우 API 키 등)를 포함해야 합니다.

    `gcloud`는 Docker 이미지를 빌드하고 Google Artifact Registry에 푸시한 다음 Cloud Run에 배포합니다. 완료되면 배포된 서비스의 URL을 출력합니다.

    전체 배포 옵션 목록은 [`gcloud run deploy` 참조 문서](https://cloud.google.com/sdk/gcloud/reference/run/deploy)를 확인하세요.

## 에이전트 테스트하기

에이전트가 Cloud Run에 배포되면, 배포된 UI(활성화된 경우)를 통하거나 `curl`과 같은 도구를 사용하여 API 엔드포인트와 직접 상호작용할 수 있습니다. 배포 후 제공된 서비스 URL이 필요합니다.

=== "UI 테스트"

    ### UI 테스트

    UI를 활성화하여 에이전트를 배포한 경우:

    *   **adk CLI:** 배포 중 `--webui` 플래그를 포함했습니다.
    *   **gcloud CLI:** `main.py`에서 `SERVE_WEB_INTERFACE = True`로 설정했습니다.

    웹 브라우저에서 배포 후 제공된 Cloud Run 서비스 URL로 이동하여 에이전트를 테스트할 수 있습니다.

    ```bash
    # URL 형식 예시
    # https://your-service-name-abc123xyz.a.run.app
    ```

    ADK 개발 UI를 사용하면 브라우저에서 직접 에이전트와 상호작용하고, 세션을 관리하며, 실행 세부 정보를 볼 수 있습니다.

    에이전트가 의도대로 작동하는지 확인하려면 다음을 수행할 수 있습니다.

    1. 드롭다운 메뉴에서 에이전트를 선택합니다.
    2. 메시지를 입력하고 에이전트로부터 예상된 응답을 받는지 확인합니다.

    예상치 못한 동작이 발생하면 [Cloud Run](https://console.cloud.google.com/run) 콘솔 로그를 확인하세요.

=== "API 테스트 (curl)"

    ### API 테스트 (curl)

    `curl`과 같은 도구를 사용하여 에이전트의 API 엔드포인트와 상호작용할 수 있습니다. 이는 프로그래밍 방식의 상호작용이나 UI 없이 배포한 경우에 유용합니다.

    배포 후 제공된 서비스 URL과, 서비스가 인증되지 않은 접근을 허용하도록 설정되지 않은 경우 인증을 위한 ID 토큰이 필요합니다.

    #### 애플리케이션 URL 설정

    예시 URL을 배포된 Cloud Run 서비스의 실제 URL로 바꾸세요.

    ```bash
    export APP_URL="YOUR_CLOUD_RUN_SERVICE_URL"
    # 예: export APP_URL="https://adk-default-service-name-abc123xyz.a.run.app"
    ```

    #### ID 토큰 가져오기 (필요한 경우)

    서비스에 인증이 필요한 경우(즉, `gcloud`와 함께 `--allow-unauthenticated`를 사용하지 않았거나 `adk` 프롬프트에 'N'으로 답한 경우) ID 토큰을 얻으세요.

    ```bash
    export TOKEN=$(gcloud auth print-identity-token)
    ```

    *서비스가 인증되지 않은 접근을 허용하는 경우, 아래 `curl` 명령어에서 `-H "Authorization: Bearer $TOKEN"` 헤더를 생략할 수 있습니다.*

    #### 사용 가능한 앱 목록 조회

    배포된 애플리케이션 이름을 확인합니다.

    ```bash
    curl -X GET -H "Authorization: Bearer $TOKEN" $APP_URL/list-apps
    ```

    *(이 출력에 따라 필요하다면 다음 명령어의 `app_name`을 조정하세요. 기본값은 종종 에이전트 디렉터리 이름입니다, 예: `capital_agent`)*.

    #### 세션 생성 또는 업데이트

    특정 사용자와 세션에 대한 상태를 초기화하거나 업데이트합니다. `capital_agent`를 실제 앱 이름으로 바꾸세요. `user_123`과 `session_abc` 값은 예시 식별자이므로 원하는 사용자 및 세션 ID로 바꿀 수 있습니다.

    ```bash
    curl -X POST -H "Authorization: Bearer $TOKEN" \
        $APP_URL/apps/capital_agent/users/user_123/sessions/session_abc \
        -H "Content-Type: application/json" \
        -d '{"preferred_language": "English", "visit_count": 5}'
    ```

    #### 에이전트 실행

    에이전트에 프롬프트를 보냅니다. `capital_agent`를 앱 이름으로 바꾸고, 필요에 따라 사용자/세션 ID와 프롬프트를 조정하세요.

    ```bash
    curl -X POST -H "Authorization: Bearer $TOKEN" \
        $APP_URL/run_sse \
        -H "Content-Type: application/json" \
        -d '{
        "app_name": "capital_agent",
        "user_id": "user_123",
        "session_id": "session_abc",
        "new_message": {
            "role": "user",
            "parts": [{
            "text": "캐나다의 수도는 어디인가요?"
            }]
        },
        "streaming": false
        }'
    ```

    * 서버 전송 이벤트(SSE)를 수신하려면 `"streaming": true`로 설정하세요.
    * 응답에는 최종 답변을 포함한 에이전트의 실행 이벤트가 포함됩니다.