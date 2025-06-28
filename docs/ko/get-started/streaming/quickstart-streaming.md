# 빠른 시작 (스트리밍 / Python) {#adk-streaming-quickstart}

이 빠른 시작 가이드를 통해 간단한 에이전트를 만들고 ADK 스트리밍을 사용하여 저지연 양방향 음성 및 영상 통신을 활성화하는 방법을 배웁니다. ADK를 설치하고, 기본적인 "Google 검색" 에이전트를 설정한 후, `adk web` 툴로 스트리밍 에이전트를 실행해 보고, 이어서 ADK 스트리밍과 [FastAPI](https://fastapi.tiangolo.com/)를 사용하여 직접 간단한 비동기 웹 앱을 구축하는 방법을 설명합니다.

**참고:** 이 가이드는 Windows, Mac, Linux 환경에서 터미널 사용 경험이 있다고 가정합니다.

## 음성/영상 스트리밍을 지원하는 모델 {#supported-models}

ADK에서 음성/영상 스트리밍을 사용하려면 Live API를 지원하는 Gemini 모델을 사용해야 합니다. Gemini Live API를 지원하는 **모델 ID**는 아래 문서에서 찾을 수 있습니다.

-   [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
-   [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## 1. 환경 설정 및 ADK 설치 {#1.-setup-installation}

가상 환경 생성 및 활성화 (권장):

```bash
# 생성
python -m venv .venv
# 활성화 (새 터미널마다)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

ADK 설치:

```bash
pip install google-adk
```

## 2. 프로젝트 구조 {#2.-project-structure}

다음과 같이 빈 파일들로 폴더 구조를 만듭니다.

```console
adk-streaming/  # 프로젝트 폴더
└── app/ # 웹 앱 폴더
    ├── .env # Gemini API 키
    └── google_search_agent/ # 에이전트 폴더
        ├── __init__.py # 파이썬 패키지
        └── agent.py # 에이전트 정의
```

### agent.py

다음 코드 블록을 복사하여 `agent.py` 파일에 붙여넣습니다.

`model`의 경우, 앞서 [모델 섹션](#supported-models)에서 설명한 대로 모델 ID를 다시 한번 확인해 주세요.

```py
from google.adk.agents import Agent
from google.adk.tools import google_search  # 툴 import

root_agent = Agent(
   # 에이전트를 위한 고유한 이름
   name="basic_search_agent",
   # 에이전트가 사용할 대규모 언어 모델 (LLM)
   # 아래 링크에서 live를 지원하는 최신 모델 ID를 입력해주세요.
   # https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/#supported-models
   model="...",  # 예: model="gemini-2.0-flash-live-001" 또는 model="gemini-2.0-flash-live-preview-04-09"
   # 에이전트의 목적에 대한 짧은 설명
   description="Google 검색을 사용하여 질문에 답변하는 에이전트.",
   # 에이전트의 행동을 설정하기 위한 지침
   instruction="당신은 전문 연구원입니다. 항상 사실에 입각하여 답변합니다.",
   # Google 검색으로 그라운딩을 수행하기 위해 google_search 툴을 추가
   tools=[google_search]
)
```

`agent.py`는 모든 에이전트의 로직이 저장될 곳이며, 반드시 `root_agent`가 정의되어 있어야 합니다.

[Google 검색을 이용한 그라운딩](https://ai.google.dev/gemini-api/docs/grounding?lang=ko#configure-search) 기능이 얼마나 쉽게 통합되었는지 확인해 보세요. `Agent` 클래스와 `google_search` 툴이 LLM 및 검색 API와의 복잡한 상호작용을 처리하므로, 여러분은 에이전트의 *목적*과 *행동*에만 집중할 수 있습니다.

![intro_components.png](../../assets/quickstart-streaming-tool.png)

다음 코드 블록을 복사하여 `__init__.py` 파일에 붙여넣습니다.

```py title="__init__.py"
from . import agent
```

## 3. 플랫폼 설정 {#3.-set-up-the-platform}

에이전트를 실행하려면 Google AI Studio 또는 Google Cloud Vertex AI 중에서 플랫폼을 선택하세요.

=== "Gemini - Google AI Studio"
    1.  [Google AI Studio](https://aistudio.google.com/apikey)에서 API 키를 받습니다.
    2.  `app/` 폴더 안에 있는 **`.env`** 파일을 열고 다음 코드를 복사하여 붙여넣습니다.

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3.  `PASTE_YOUR_ACTUAL_API_KEY_HERE`를 실제 `API KEY`로 교체합니다.

=== "Gemini - Google Cloud Vertex AI"
    1.  기존 [Google Cloud](https://cloud.google.com/?e=48754805&hl=ko) 계정과 프로젝트가 필요합니다.
        *   [Google Cloud 프로젝트 설정](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
        *   [gcloud CLI 설정](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
        *   터미널에서 `gcloud auth login`을 실행하여 Google Cloud에 인증합니다.
        *   [Vertex AI API를 활성화](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)합니다.
    2.  `app/` 폴더 안에 있는 **`.env`** 파일을 엽니다. 다음 코드를 복사하여 붙여넣고 프로젝트 ID와 위치를 업데이트합니다.

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=PASTE_YOUR_ACTUAL_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

## 4. `adk web`으로 에이전트 테스트하기 {#4.-try-it-adk-web}

이제 에이전트를 테스트할 준비가 되었습니다. 다음 명령을 실행하여 **개발 UI**를 시작합니다. 먼저, 현재 디렉토리를 `app`으로 설정해야 합니다.

```shell
cd app
```

또한, 다음 명령으로 `SSL_CERT_FILE` 변수를 설정합니다. 이는 나중에 있을 음성 및 영상 테스트에 필요합니다.

```shell
export SSL_CERT_FILE=$(python -m certifi)
```

그런 다음, 개발 UI를 실행합니다.

```shell
adk web
```

!!!info "Windows 사용자를 위한 참고"

    `_make_subprocess_transport NotImplementedError` 오류가 발생하면, 대신 `adk web --no-reload`를 사용해 보세요.

제공된 URL(보통 `http://localhost:8000` 또는 `http://127.0.0.1:8000`)을 **브라우저에서 직접** 엽니다. 이 연결은 전적으로 로컬 컴퓨터 내에서 유지됩니다. `google_search_agent`를 선택하세요.

### 텍스트로 테스트하기

UI에 다음 프롬프트를 입력하여 테스트해 보세요.

*   뉴욕 날씨 어때?
*   뉴욕은 지금 몇 시야?
*   파리 날씨 어때?
*   파리는 지금 몇 시야?

에이전트는 이 질문들에 답하기 위해 google_search 툴을 사용하여 최신 정보를 가져올 것입니다.

### 음성 및 영상으로 테스트하기

음성으로 테스트하려면 웹 브라우저를 새로고침하고, 마이크 버튼을 클릭하여 음성 입력을 활성화한 후, 같은 질문을 음성으로 해보세요. 실시간으로 음성 답변을 들을 수 있습니다.

영상으로 테스트하려면 웹 브라우저를 새로고침하고, 카메라 버튼을 클릭하여 영상 입력을 활성화한 후, "뭐가 보여?"와 같은 질문을 해보세요. 에이전트는 영상 입력에서 보이는 것에 대해 답변할 것입니다.

(마이크나 카메라 버튼을 한 번만 클릭하는 것으로 충분합니다. 여러분의 음성이나 영상은 모델로 계속 스트리밍되고, 모델의 응답도 계속해서 스트리밍되어 돌아옵니다. 마이크나 카메라 버튼을 여러 번 클릭하는 것은 지원되지 않습니다.)

### 툴 중지하기

콘솔에서 `Ctrl-C`를 눌러 `adk web`을 중지합니다.

### ADK 스트리밍에 대한 참고

콜백(Callback), LongRunningTool, ExampleTool, 셸 에이전트(예: SequentialAgent)와 같은 기능들은 ADK 스트리밍의 향후 버전에서 지원될 예정입니다.

축하합니다! ADK를 사용하여 첫 번째 스트리밍 에이전트를 성공적으로 만들고 상호작용했습니다!

## 다음 단계: 커스텀 스트리밍 앱 만들기

[커스텀 오디오 스트리밍 앱](../../streaming/custom-streaming.md) 튜토리얼에서는 ADK 스트리밍과 [FastAPI](https://fastapi.tiangolo.com/)로 구축된 커스텀 비동기 웹 앱의 서버 및 클라이언트 코드를 개괄적으로 설명하여, 실시간 양방향 오디오 및 텍스트 통신을 가능하게 합니다.