# 멀티툴 에이전트 만들기

이 빠른 시작 가이드는 Agent Development Kit (ADK)를 설치하고, 여러 툴을 갖춘 기본 에이전트를 설정한 후, 터미널 또는 브라우저 기반의 대화형 개발 UI에서 로컬로 실행하는 방법을 안내합니다.

<!-- <img src="../../assets/quickstart.png" alt="Quickstart setup"> -->

이 빠른 시작 가이드는 Python 3.9 이상 또는 Java 17 이상이 설치된 로컬 IDE(VS Code, PyCharm, IntelliJ IDEA 등)와 터미널 사용이 가능하다고 가정합니다. 이 방법은 애플리케이션을 전적으로 사용자 기기에서 실행하며, 내부 개발용으로 권장됩니다.

## 1. 환경 설정 및 ADK 설치 { #set-up-environment-install-adk }

=== "Python"

    가상 환경 생성 및 활성화 (권장):

    ```bash
    # 생성
    python -m venv .venv
    # 활성화 (새 터미널마다 실행)
    # macOS/Linux: source .venv/bin/activate
    # Windows CMD: .venv\Scripts\activate.bat
    # Windows PowerShell: .venv\Scripts\Activate.ps1
    ```

    ADK 설치:

    ```bash
    pip install google-adk
    ```

=== "Java"

    ADK를 설치하고 환경을 설정하려면 다음 단계를 진행하세요.

## 2. 에이전트 프로젝트 생성 { #create-agent-project }

### 프로젝트 구조

=== "Python"

    다음과 같은 프로젝트 구조를 만들어야 합니다:

    ```console
    parent_folder/
        multi_tool_agent/
            __init__.py
            agent.py
            .env
    ```

    `multi_tool_agent` 폴더를 생성합니다:

    ```bash
    mkdir multi_tool_agent/
    ```

    !!! info "Windows 사용자 참고"

        Windows에서 ADK를 사용하여 다음 몇 단계를 진행할 때, `mkdir`, `echo`와 같은 명령어는 종종 null 바이트나 잘못된 인코딩으로 파일을 생성할 수 있으므로, 파일 탐색기나 IDE를 사용하여 Python 파일을 만드는 것을 권장합니다.

    ### `__init__.py`

    이제 폴더에 `__init__.py` 파일을 생성합니다:

    ```shell
    echo "from . import agent" > multi_tool_agent/__init__.py
    ```

    이제 `__init__.py` 파일은 다음과 같아야 합니다:

    ```python title="multi_tool_agent/__init__.py"
    --8<-- "examples/python/snippets/get-started/multi_tool_agent/__init__.py"
    ```

    ### `agent.py`

    같은 폴더에 `agent.py` 파일을 생성합니다:

    === "OS X &amp; Linux"
        ```shell
        touch multi_tool_agent/agent.py
        ```

    === "Windows"
        ```shell
        type nul > multi_tool_agent/agent.py
        ```

    다음 코드를 복사하여 `agent.py`에 붙여넣으세요:

    ```python title="multi_tool_agent/agent.py"
    --8<-- "examples/python/snippets/get-started/multi_tool_agent/agent.py"
    ```

    ### `.env`

    같은 폴더에 `.env` 파일을 생성합니다:

    === "OS X &amp; Linux"
        ```shell
        touch multi_tool_agent/.env
        ```

    === "Windows"
        ```shell
        type nul > multi_tool_agent\.env
        ```

    이 파일에 대한 자세한 내용은 다음 섹션인 [모델 설정하기](#set-up-the-model)에서 설명합니다.

=== "Java"

    Java 프로젝트는 일반적으로 다음과 같은 프로젝트 구조를 가집니다:

    ```console
    project_folder/
    ├── pom.xml (or build.gradle)
    ├── src/
    ├── └── main/
    │       └── java/
    │           └── agents/
    │               └── multitool/
    └── test/
    ```

    ### `MultiToolAgent.java` 생성하기

    `src/main/java/agents/multitool/` 디렉터리 내의 `agents.multitool` 패키지에 `MultiToolAgent.java` 소스 파일을 생성합니다.

    다음 코드를 복사하여 `MultiToolAgent.java`에 붙여넣으세요:

    ```java title="agents/multitool/MultiToolAgent.java"
    --8<-- "examples/java/cloud-run/src/main/java/agents/multitool/MultiToolAgent.java:full_code"
    ```

![intro_components.png](../assets/quickstart-flow-tool.png)

## 3. 모델 설정하기 { #set-up-the-model }

에이전트가 사용자 요청을 이해하고 응답을 생성하는 능력은 거대 언어 모델(Large Language Model, LLM)에 의해 구동됩니다. 에이전트는 이 외부 LLM 서비스에 보안 호출을 해야 하며, 이를 위해 **인증 자격 증명(authentication credentials)이 필요합니다**. 유효한 인증이 없으면 LLM 서비스는 에이전트의 요청을 거부하고 에이전트는 작동할 수 없습니다.

!!!tip "모델 인증 가이드"
    다양한 모델에 대한 인증 상세 가이드는 [인증 가이드](../agents/models.md#google-ai-studio)를 참조하세요.
    이 단계는 에이전트가 LLM 서비스에 호출할 수 있도록 보장하는 매우 중요한 과정입니다.

=== "Gemini - Google AI Studio"
    1. [Google AI Studio](https://aistudio.google.com/apikey)에서 API 키를 받으세요.
    2. Python을 사용하는 경우, `multi_tool_agent/` 내에 있는 **`.env`** 파일을 열고 다음 코드를 복사하여 붙여넣으세요.

        ```env title="multi_tool_agent/.env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

        Java를 사용하는 경우, 환경 변수를 정의하세요:

        ```console title="terminal"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        export GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3. `PASTE_YOUR_ACTUAL_API_KEY_HERE` 부분을 실제 `API 키`로 교체하세요.

=== "Gemini - Google Cloud Vertex AI"
    1. [Google Cloud 프로젝트를 설정](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)하고 [Vertex AI API를 활성화](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)하세요.
    2. [gcloud CLI를 설정](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)하세요.
    3. 터미널에서 `gcloud auth application-default login`을 실행하여 Google Cloud에 인증하세요.
    4. Python을 사용하는 경우, `multi_tool_agent/` 내에 있는 **`.env`** 파일을 열고 다음 코드를 복사하여 붙여넣은 후 프로젝트 ID와 위치(location)를 업데이트하세요.

        ```env title="multi_tool_agent/.env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=LOCATION
        ```

        Java를 사용하는 경우, 환경 변수를 정의하세요:

        ```console title="terminal"
        export GOOGLE_GENAI_USE_VERTEXAI=TRUE
        export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
        export GOOGLE_CLOUD_LOCATION=LOCATION
        ```

=== "Gemini - Google Cloud Vertex AI (Express 모드)"
    1. 무료 Google Cloud 프로젝트에 가입하고 자격 요건을 갖춘 계정으로 Gemini를 무료로 사용할 수 있습니다!
        * [Vertex AI Express 모드로 Google Cloud 프로젝트 설정하기](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)
        * Express 모드 프로젝트에서 API 키를 받으세요. 이 키를 ADK와 함께 사용하면 Gemini 모델을 무료로 사용할 수 있을 뿐만 아니라 Agent Engine 서비스에도 액세스할 수 있습니다.
    2. Python을 사용하는 경우, `multi_tool_agent/` 내에 있는 **`.env`** 파일을 열고 다음 코드를 복사하여 붙여넣은 후 프로젝트 ID와 위치를 업데이트하세요.

        ```env title="multi_tool_agent/.env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
        ```

        Java를 사용하는 경우, 환경 변수를 정의하세요:

        ```console title="terminal"
        export GOOGLE_GENAI_USE_VERTEXAI=TRUE
        export GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
        ```

## 4. 에이전트 실행하기 { #run-your-agent }

=== "Python"

    터미널을 사용하여 에이전트 프로젝트의 상위 디렉터리로 이동합니다 (`cd ..` 등 사용):

    ```console
    parent_folder/      <-- 이 디렉터리로 이동
        multi_tool_agent/
            __init__.py
            agent.py
            .env
    ```

    에이전트와 상호작용하는 방법은 여러 가지가 있습니다:

    === "개발 UI (adk web)"

        !!! success "Vertex AI 사용자 인증 설정"
            이전 단계에서 **"Gemini - Google Cloud Vertex AI"**를 선택했다면, 개발 UI를 시작하기 전에 Google Cloud로 인증해야 합니다.

            다음 명령어를 실행하고 안내를 따르세요:
            ```bash
            gcloud auth application-default login
            ```

            **참고:** "Gemini - Google AI Studio"를 사용한다면 이 단계를 건너뛰세요.

        다음 명령어를 실행하여 **개발 UI**를 시작합니다.

        ```shell
        adk web
        ```

        !!!info "Windows 사용자 참고"

            `_make_subprocess_transport NotImplementedError` 오류가 발생하면, 대신 `adk web --no-reload`를 사용해 보세요.

        **1단계:** 제공된 URL(보통 `http://localhost:8000` 또는 `http://127.0.0.1:8000`)을 브라우저에서 직접 여세요.

        **2단계:** UI의 왼쪽 상단 드롭다운 메뉴에서 에이전트를 선택할 수 있습니다. "multi_tool_agent"를 선택하세요.

        !!!note "문제 해결"

            드롭다운 메뉴에 "multi_tool_agent"가 보이지 않으면, `adk web` 명령어를 에이전트 폴더의 **상위 폴더**(즉, multi_tool_agent의 상위 폴더)에서 실행했는지 확인하세요.

        **3단계:** 이제 텍스트 상자를 사용하여 에이전트와 대화할 수 있습니다:

        ![adk-web-dev-ui-chat.png](../assets/adk-web-dev-ui-chat.png)

        **4단계:** 왼쪽의 `Events` 탭을 사용하여 개별 액션을 클릭하면 각 함수 호출, 응답, 모델 응답을 검사할 수 있습니다:

        ![adk-web-dev-ui-function-call.png](../assets/adk-web-dev-ui-function-call.png)

        `Events` 탭에서 `Trace` 버튼을 클릭하면 각 이벤트의 트레이스 로그를 볼 수 있으며, 이를 통해 각 함수 호출의 지연 시간(latency)을 확인할 수 있습니다:

        ![adk-web-dev-ui-trace.png](../assets/adk-web-dev-ui-trace.png)

        **5단계:** 마이크를 활성화하여 에이전트와 대화할 수도 있습니다:

        !!!note "음성/영상 스트리밍 모델 지원"

            ADK에서 음성/영상 스트리밍을 사용하려면 Live API를 지원하는 Gemini 모델을 사용해야 합니다. Gemini Live API를 지원하는 **모델 ID**는 다음 문서에서 찾을 수 있습니다:

            - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
            - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

            그런 다음, 이전에 생성한 `agent.py` 파일의 `root_agent`에 있는 `model` 문자열을 교체할 수 있습니다 ([해당 섹션으로 이동](#agentpy)). 코드는 다음과 같아야 합니다:

            ```py
            root_agent = Agent(
                name="weather_time_agent",
                model="모델-ID로-교체하세요", # 예: gemini-2.0-flash-live-001
                ...
            ```

        ![adk-web-dev-ui-audio.png](../assets/adk-web-dev-ui-audio.png)

    === "터미널 (adk run)"

        !!! tip

            `adk run`을 사용할 때, 다음과 같이 텍스트를 파이프로 연결하여 에이전트에 시작 프롬프트를 주입할 수 있습니다:

            ```shell
            echo "Please start by listing files" | adk run file_listing_agent
            ```

        다음 명령어를 실행하여 날씨 에이전트와 대화하세요.

        ```
        adk run multi_tool_agent
        ```

        ![adk-run.png](../assets/adk-run.png)

        종료하려면 Cmd/Ctrl+C를 사용하세요.

    === "API 서버 (adk api_server)"

        `adk api_server`를 사용하면 단일 명령어로 로컬 FastAPI 서버를 생성하여 에이전트를 배포하기 전에 로컬 cURL 요청을 테스트할 수 있습니다.

        ![adk-api-server.png](../assets/adk-api-server.png)

        테스트를 위해 `adk api_server`를 사용하는 방법은 [API 서버 사용에 대한 문서](/adk-docs/runtime/api-server/)를 참조하세요.

=== "Java"

    터미널을 사용하여 에이전트 프로젝트의 상위 디렉터리로 이동합니다 (`cd ..` 등 사용):

    ```console
    project_folder/                <-- 이 디렉터리로 이동
    ├── pom.xml (or build.gradle)
    ├── src/
    ├── └── main/
    │       └── java/
    │           └── agents/
    │               └── multitool/
    │                   └── MultiToolAgent.java
    └── test/
    ```

    === "개발 UI"

        터미널에서 다음 명령어를 실행하여 개발 UI를 시작합니다.

        **개발 UI 서버의 메인 클래스 이름은 변경하지 마세요.**

        ```console title="terminal"
        mvn exec:java \
            -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
            -Dexec.args="--adk.agents.source-dir=src/main/java" \
            -Dexec.classpathScope="compile"
        ```

        **1단계:** 제공된 URL(보통 `http://localhost:8080` 또는 `http://127.0.0.1:8080`)을 브라우저에서 직접 여세요.

        **2단계:** UI의 왼쪽 상단 드롭다운 메뉴에서 에이전트를 선택할 수 있습니다. "multi_tool_agent"를 선택하세요.

        !!!note "문제 해결"

            드롭다운 메뉴에 "multi_tool_agent"가 보이지 않으면, `mvn` 명령어를 Java 소스 코드가 있는 위치(보통 `src/main/java`)에서 실행했는지 확인하세요.

        **3단계:** 이제 텍스트 상자를 사용하여 에이전트와 대화할 수 있습니다:

        ![adk-web-dev-ui-chat.png](../assets/adk-web-dev-ui-chat.png)

        **4단계:** 개별 액션을 클릭하여 각 함수 호출, 응답, 모델 응답을 검사할 수도 있습니다:

        ![adk-web-dev-ui-function-call.png](../assets/adk-web-dev-ui-function-call.png)

    === "Maven"

        Maven을 사용하여, 다음 명령어로 Java 클래스의 `main()` 메서드를 실행합니다:

        ```console title="terminal"
        mvn compile exec:java -Dexec.mainClass="agents.multitool.MultiToolAgent"
        ```

    === "Gradle"

        Gradle을 사용하는 경우, `build.gradle` 또는 `build.gradle.kts` 빌드 파일의 `plugins` 섹션에 다음 Java 플러그인이 있어야 합니다:

        ```groovy
        plugins {
            id('java')
            // other plugins
        }
        ```

        그런 다음, 빌드 파일의 다른 곳 최상위 레벨에 에이전트의 `main()` 메서드를 실행하는 새 태스크를 생성합니다:

        ```groovy
        tasks.register('runAgent', JavaExec) {
            classpath = sourceSets.main.runtimeClasspath
            mainClass = 'agents.multitool.MultiToolAgent'
        }
        ```

        마지막으로, 명령줄에서 다음 명령어를 실행합니다:

        ```console
        gradle runAgent
        ```

### 📝 시도해 볼 만한 예시 프롬프트

* 뉴욕 날씨 어때?
* 뉴욕은 지금 몇 시야?
* 파리 날씨 어때?
* 파리는 지금 몇 시야?

## 🎉 축하합니다!

ADK를 사용하여 첫 번째 에이전트를 성공적으로 만들고 상호작용했습니다!

---

## 🛣️ 다음 단계

* **튜토리얼로 이동하기**: 에이전트에 메모리, 세션, 상태를 추가하는 방법을 배우세요:
  [튜토리얼](../tutorials/index.md).
* **고급 설정 자세히 알아보기:** 프로젝트 구조, 설정 및 기타 인터페이스에 대해 더 깊이 알아보려면 [설정](installation.md) 섹션을 탐색하세요.
* **핵심 개념 이해하기:** [에이전트 개념](../agents/index.md)에 대해 알아보세요.