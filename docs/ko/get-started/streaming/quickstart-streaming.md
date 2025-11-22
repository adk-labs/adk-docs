# Python으로 스트리밍 에이전트 구축하기

이 퀵스타트에서는 간단한 에이전트를 만들고 ADK Streaming을 활용하여 지연 시간(Latency)이 짧은 양방향 음성 및 비디오 통신을 구현하는 방법을 배웁니다. ADK를 설치하고, 기본적인 "Google 검색" 에이전트를 설정하고, `adk web` 도구로 스트리밍 에이전트를 실행해 본 다음, ADK Streaming과 [FastAPI](https://fastapi.tiangolo.com/)를 사용하여 간단한 비동기 웹 앱을 직접 구축하는 방법을 설명합니다.

**참고:** 이 가이드는 Windows, Mac, Linux 환경에서 터미널 사용 경험이 있다고 가정합니다.

## 음성/비디오 스트리밍을 위한 지원 모델 {#supported-models}

ADK에서 음성/비디오 스트리밍을 사용하려면 Live API를 지원하는 Gemini 모델을 사용해야 합니다. Gemini Live API를 지원하는 **모델 ID**는 다음 문서에서 확인할 수 있습니다.

- [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
- [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## 1. 환경 설정 및 ADK 설치 { #setup-environment-install-adk }

가상 환경 생성 및 활성화 (권장):

```bash
# 생성
python -m venv .venv
# 활성화 (새 터미널을 열 때마다 실행)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

ADK 설치:

```bash
pip install google-adk
```

## 2. 프로젝트 구조 { #project-structure }

빈 파일들로 구성된 다음 폴더 구조를 생성하세요.

```console
adk-streaming/  # 프로젝트 폴더
└── app/ # 웹 앱 폴더
    ├── .env # Gemini API 키
    └── google_search_agent/ # 에이전트 폴더
        ├── __init__.py # Python 패키지
        └── agent.py # 에이전트 정의
```

### agent.py

다음 코드 블록을 `agent.py` 파일에 복사하여 붙여넣으세요.

`model`의 경우, 앞서 [지원 모델 섹션](#supported-models)에서 설명한 대로 모델 ID를 다시 한번 확인해 주세요.

```py
from google.adk.agents import Agent
from google.adk.tools import google_search  # 도구(Tool) 임포트

root_agent = Agent(
   # 에이전트의 고유 이름입니다.
   name="basic_search_agent",
   # 에이전트가 사용할 대규모 언어 모델(LLM)입니다.
   # https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/#supported-models 에서
   # 라이브(Live)를 지원하는 최신 모델 ID를 입력해 주세요.
   model="...",  # 예: model="gemini-2.0-flash-live-001" 또는 model="gemini-2.0-flash-live-preview-04-09"
   # 에이전트의 목적에 대한 짧은 설명입니다.
   description="Agent to answer questions using Google Search.",
   # 에이전트의 행동을 설정하는 지침(Instruction)입니다.
   instruction="You are an expert researcher. You always stick to the facts.",
   # Google 검색을 통한 그라운딩(Grounding)을 수행하기 위해 google_search 도구를 추가합니다.
   tools=[google_search]
)
```

`agent.py`는 모든 에이전트의 로직이 저장되는 곳이며, 반드시 `root_agent`가 정의되어 있어야 합니다.

[Google 검색을 통한 그라운딩](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search) 기능을 얼마나 쉽게 통합했는지 확인해 보세요. `Agent` 클래스와 `google_search` 도구가 LLM과의 복잡한 상호작용 및 검색 API를 이용한 그라운딩을 처리해주므로, 여러분은 에이전트의 *목적*과 *행동*에만 집중할 수 있습니다.

![intro_components.png](../../assets/quickstart-streaming-tool.png)

다음 코드 블록을 `__init__.py` 파일에 복사하여 붙여넣으세요.

```py title="__init__.py"
from . import agent
```

## 3\. 플랫폼 설정 { #set-up-the-platform }

에이전트를 실행하려면 Google AI Studio 또는 Google Cloud Vertex AI 중 하나의 플랫폼을 선택하세요.

=== "Gemini - Google AI Studio"
    1. [Google AI Studio](https://aistudio.google.com/apikey)에서 API 키를 발급받습니다.
    2. (`app/`) 내부에 있는 **`.env`** 파일을 열고 다음 코드를 복사하여 붙여넣습니다.

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3. `PASTE_YOUR_ACTUAL_API_KEY_HERE` 부분을 실제 `API KEY`로 교체하세요.

=== "Gemini - Google Cloud Vertex AI"
    1. 기존 [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) 계정과 프로젝트가 필요합니다.
        * [Google Cloud 프로젝트](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)를 설정합니다.
        * [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)를 설정합니다.
        * 터미널에서 `gcloud auth login`을 실행하여 Google Cloud에 인증합니다.
        * [Vertex AI API를 활성화](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)합니다.
    2. (`app/`) 내부에 있는 **`.env`** 파일을 엽니다. 다음 코드를 복사하여 붙여넣고 프로젝트 ID와 위치(Region)를 업데이트하세요.

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=PASTE_YOUR_ACTUAL_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

## 4. `adk web`으로 에이전트 체험하기 { #try-the-agent-with-adk-web }

이제 에이전트를 체험할 준비가 되었습니다. 다음 명령어를 실행하여 **dev UI**를 시작합니다. 먼저 현재 디렉토리를 `app`으로 설정했는지 확인하세요.

```shell
cd app
```

또한, 다음 명령어를 사용하여 `SSL_CERT_FILE` 변수를 설정하세요. 이는 나중에 진행할 음성 및 비디오 테스트를 위해 필요합니다.

=== "OS X &amp; Linux"
    ```bash
    export SSL_CERT_FILE=$(python -m certifi)
    ```

=== "Windows"
    ```powershell
    $env:SSL_CERT_FILE = (python -m certifi)
    ```

그런 다음, dev UI를 실행합니다.

```shell
adk web
```

!!!info "Windows 사용자 주의사항"

    `_make_subprocess_transport NotImplementedError` 오류가 발생할 경우, 대신 `adk web --no-reload`를 사용해 보세요.


제공된 URL(일반적으로 `http://localhost:8000` 또는 `http://127.0.0.1:8000`)을 **브라우저에서 직접** 엽니다. 이 연결은 전적으로 로컬 컴퓨터 내에서만 유지됩니다. `google_search_agent`를 선택하세요.

### 텍스트로 체험하기

UI에 다음 프롬프트를 입력하여 테스트해 보세요.

* What is the weather in New York? (뉴욕의 날씨는 어때?)
* What is the time in New York? (뉴욕은 지금 몇 시야?)
* What is the weather in Paris? (파리의 날씨는 어때?)
* What is the time in Paris? (파리는 지금 몇 시야?)

에이전트는 google_search 도구를 사용하여 최신 정보를 가져와 질문에 답변할 것입니다.

### 음성 및 비디오로 체험하기

음성을 시도하려면 웹 브라우저를 새로고침하고, 마이크 버튼을 클릭하여 음성 입력을 활성화한 뒤, 동일한 질문을 음성으로 물어보세요. 실시간으로 음성 답변을 들을 수 있습니다.

비디오를 시도하려면 웹 브라우저를 새로고침하고, 카메라 버튼을 클릭하여 비디오 입력을 활성화한 뒤, "What do you see?(무엇이 보이나요?)"와 같은 질문을 해보세요. 에이전트는 비디오 입력에 보이는 내용에 대해 답변할 것입니다.

(마이크나 카메라 버튼은 한 번만 클릭하면 충분합니다. 음성이나 비디오가 모델로 스트리밍되고 모델의 응답이 지속적으로 다시 스트리밍됩니다. 마이크나 카메라 버튼을 여러 번 클릭하는 것은 지원되지 않습니다.)

### 도구 중지

콘솔에서 `Ctrl-C`를 눌러 `adk web`을 중지합니다.

### ADK Streaming 관련 참고 사항

다음 기능들은 ADK Streaming의 향후 버전에서 지원될 예정입니다: Callback, LongRunningTool, ExampleTool, Shell agent (예: SequentialAgent).

축하합니다! ADK를 사용하여 첫 번째 스트리밍 에이전트를 성공적으로 생성하고 상호작용했습니다!

## 다음 단계: 커스텀 스트리밍 앱 구축

[커스텀 오디오 스트리밍 앱](../../streaming/custom-streaming.md) 튜토리얼에서는 ADK Streaming과 [FastAPI](https://fastapi.tiangolo.com/)로 구축된 커스텀 비동기 웹 앱의 서버 및 클라이언트 코드를 개괄적으로 설명하며, 이를 통해 실시간 양방향 오디오 및 텍스트 통신을 구현하는 방법을 안내합니다.