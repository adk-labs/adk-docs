# Google 검색 기반 이해

[Google 검색 기반 도구](../tools/built-in-tools.md#google-search)는 에이전트 개발 키트(ADK)의 강력한 기능으로, AI 에이전트가 웹에서 실시간으로 신뢰할 수 있는 정보에 액세스할 수 있도록 합니다. 에이전트를 Google 검색에 연결하면 신뢰할 수 있는 출처를 기반으로 한 최신 답변을 사용자에게 제공할 수 있습니다.

이 기능은 날씨 업데이트, 뉴스 이벤트, 주가 또는 모델의 학습 데이터 컷오프 이후 변경되었을 수 있는 모든 사실과 같은 최신 정보가 필요한 쿼리에 특히 유용합니다. 에이전트가 외부 정보가 필요하다고 판단하면 자동으로 웹 검색을 수행하고 적절한 출처와 함께 결과를 응답에 통합합니다.

## 학습 내용

이 가이드에서는 다음을 알아봅니다.

- **빠른 설정**: Google 검색 지원 에이전트를 처음부터 만들고 실행하는 방법
- **기반 아키텍처**: 웹 기반의 데이터 흐름 및 기술 프로세스
- **응답 구조**: 기반 응답 및 해당 메타데이터를 해석하는 방법
- **모범 사례**: 검색 결과 및 인용을 사용자에게 표시하기 위한 지침

### 추가 리소스

추가 리소스로, [Gemini 전체 스택 에이전트 개발 키트(ADK) 빠른 시작](https://github.com/google/adk-samples/tree/main/python/agents/gemini-fullstack)에는 전체 스택 애플리케이션 예제로 [Google 검색 기반의 훌륭한 실제 사용 사례](https://github.com/google/adk-samples/blob/main/python/agents/gemini-fullstack/app/agent.py)가 있습니다.

## Google 검색 기반 빠른 시작

이 빠른 시작에서는 Google 검색 기반 기능이 있는 ADK 에이전트를 만드는 과정을 안내합니다. 이 빠른 시작에서는 Python 3.9 이상 및 터미널 액세스가 가능한 로컬 IDE(VS Code 또는 PyCharm 등)를 가정합니다.

### 1. 환경 설정 및 ADK 설치 { #set-up-environment-install-adk }

가상 환경 생성 및 활성화:

```bash
# 생성
python -m venv .venv

# 활성화(각 새 터미널)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

ADK 설치:

```bash
pip install google-adk==1.4.2
```

### 2. 에이전트 프로젝트 만들기 { #create-agent-project }

프로젝트 디렉터리에서 다음 명령을 실행합니다.

=== "OS X 및 Linux"
    ```bash
    # 1단계: 에이전트에 대한 새 디렉터리 만들기
    mkdir google_search_agent

    # 2단계: 에이전트에 대한 __init__.py 만들기
    echo "from . import agent" > google_search_agent/__init__.py

    # 3단계: agent.py(에이전트 정의) 및 .env(Gemini 인증 구성) 만들기
    touch google_search_agent/agent.py .env
    ```

=== "Windows"
    ```shell
    # 1단계: 에이전트에 대한 새 디렉터리 만들기
    mkdir google_search_agent

    # 2단계: 에이전트에 대한 __init__.py 만들기
    echo "from . import agent" > google_search_agent/__init__.py

    # 3단계: agent.py(에이전트 정의) 및 .env(Gemini 인증 구성) 만들기
    type nul > google_search_agent\agent.py 
    type nul > google_search_agent\.env
    ```



#### `agent.py` 편집

다음 코드를 복사하여 `agent.py`에 붙여넣습니다.

```python title="google_search_agent/agent.py"
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="google_search_agent",
    model="gemini-2.5-flash",
    instruction="필요할 때 Google 검색을 사용하여 질문에 답변합니다. 항상 출처를 인용하십시오.",
    description="Google 검색 기능이 있는 전문 검색 도우미",
    tools=[google_search]
)
```

이제 다음과 같은 디렉터리 구조가 됩니다.

```console
my_project/
    google_search_agent/
        __init__.py
        agent.py
    .env
```

### 3. 플랫폼 선택 { #choose-a-platform }

에이전트를 실행하려면 에이전트가 Gemini 모델을 호출하는 데 사용할 플랫폼을 선택해야 합니다. Google AI Studio 또는 Vertex AI 중에서 하나를 선택합니다.

=== "Gemini - Google AI Studio"
    1. [Google AI Studio](https://aistudio.google.com/apikey)에서 API 키를 가져옵니다.
    2. Python을 사용하는 경우 **`.env`** 파일을 열고 다음 코드를 복사하여 붙여넣습니다.

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3. `PASTE_YOUR_ACTUAL_API_KEY_HERE`를 실제 `API 키`로 바꿉니다.

=== "Gemini - Google Cloud Vertex AI"
    1. 기존 [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) 계정과 프로젝트가 필요합니다.
        * [Google Cloud 프로젝트](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp) 설정
        * [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local) 설정
        * 터미널에서 `gcloud auth login`을 실행하여 Google Cloud에 인증합니다.
        * [Vertex AI API 사용 설정](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com).
    2. Python을 사용하는 경우 **`.env`** 파일을 열고 다음 코드를 복사하여 붙여넣고 프로젝트 ID와 위치를 업데이트합니다.

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=LOCATION
        ```

### 4. 에이전트 실행 { #run-your-agent }

에이전트와 상호 작용하는 방법에는 여러 가지가 있습니다.

=== "개발 UI (adk web)"
    다음 명령을 실행하여 **개발 UI**를 시작합니다.

    ```shell
    adk web
    ```
    
    !!!info "Windows 사용자 참고"

        `_make_subprocess_transport NotImplementedError`가 발생하면 대신 `adk web --no-reload`를 사용해 보세요.


    **1단계:** 제공된 URL(일반적으로 `http://localhost:8000` 또는 `http://127.0.0.1:8000`)을 브라우저에서 직접 엽니다.

    **2단계.** UI의 왼쪽 상단 모서리에서 드롭다운에서 에이전트를 선택할 수 있습니다. "google_search_agent"를 선택합니다.

    !!!note "문제 해결"

        드롭다운 메뉴에 "google_search_agent"가 표시되지 않으면 에이전트 폴더의 **상위 폴더**(즉, google_search_agent의 상위 폴더)에서 `adk web`을 실행하고 있는지 확인하십시오.

    **3단계.** 이제 텍스트 상자를 사용하여 에이전트와 채팅할 수 있습니다.

=== "터미널 (adk run)"

    다음 명령을 실행하여 날씨 에이전트와 채팅합니다.

    ```
    adk run google_search_agent
    ```
    종료하려면 Cmd/Ctrl+C를 사용합니다.

### 📝 시도해 볼 만한 예제 프롬프트

이러한 질문을 통해 에이전트가 실제로 Google 검색을 호출하여 최신 날씨와 시간을 가져오는지 확인할 수 있습니다.

* 뉴욕의 날씨는 어떻습니까?
* 뉴욕은 지금 몇 시입니까?
* 파리의 날씨는 어떻습니까?
* 파리는 지금 몇 시입니까?

![adk web으로 에이전트 시도](../assets/google_search_grd_adk_web.png)

ADK를 사용하여 Google 검색 에이전트를 성공적으로 만들고 상호 작용했습니다!

## Google 검색 기반 작동 방식

기반은 에이전트를 웹의 실시간 정보에 연결하여 더 정확하고 최신 응답을 생성할 수 있도록 하는 프로세스입니다. 사용자의 프롬프트에 모델이 학습하지 않았거나 시간에 민감한 정보가 필요한 경우 에이전트의 기본 대규모 언어 모델은 관련 사실을 찾기 위해 google_search 도구를 지능적으로 호출하기로 결정합니다.

### **데이터 흐름 다이어그램**

이 다이어그램은 사용자 쿼리가 기반 응답을 생성하는 단계별 프로세스를 보여줍니다.

![](../assets/google_search_grd_dataflow.png)

### **자세한 설명**

기반 에이전트는 다이어그램에 설명된 데이터 흐름을 사용하여 외부 정보를 검색, 처리 및 사용자에게 제공되는 최종 답변에 통합합니다.

1. **사용자 쿼리**: 최종 사용자는 질문을 하거나 명령을 내려 에이전트와 상호 작용합니다.
2. **ADK 오케스트레이션**: 에이전트 개발 키트는 에이전트의 동작을 오케스트레이션하고 사용자의 메시지를 에이전트의 핵심으로 전달합니다.
3. **LLM 분석 및 도구 호출**: 에이전트의 LLM(예: Gemini 모델)은 프롬프트를 분석합니다. 외부의 최신 정보가 필요하다고 판단되면 google_search 도구를 호출하여 기반 메커니즘을 트리거합니다. 이는 최신 뉴스, 날씨 또는 모델의 학습 데이터에 없는 사실에 대한 쿼리에 답변하는 데 이상적입니다.
4. **기반 서비스 상호 작용**: google_search 도구는 Google 검색 인덱스에 하나 이상의 쿼리를 공식화하고 보내는 내부 기반 서비스와 상호 작용합니다.
5. **컨텍스트 주입**: 기반 서비스는 관련 웹 페이지와 스니펫을 검색합니다. 그런 다음 최종 응답이 생성되기 전에 이러한 검색 결과를 모델의 컨텍스트에 통합합니다. 이 중요한 단계를 통해 모델은 사실적이고 실시간 데이터를 "추론"할 수 있습니다.
6. **기반 응답 생성**: 이제 새로운 검색 결과로 정보를 얻은 LLM은 검색된 정보를 통합하는 응답을 생성합니다.
7. **출처가 있는 응답 제시**: ADK는 필요한 소스 URL과 groundingMetadata를 포함하는 최종 기반 응답을 수신하고 출처와 함께 사용자에게 제시합니다. 이를 통해 최종 사용자는 정보를 확인하고 에이전트의 답변에 대한 신뢰를 구축할 수 있습니다.

### Google 검색 응답으로 기반 이해

에이전트가 Google 검색을 사용하여 응답을 기반으로 할 때 최종 텍스트 답변뿐만 아니라 해당 답변을 생성하는 데 사용한 출처를 포함하는 자세한 정보 세트를 반환합니다. 이 메타데이터는 응답을 확인하고 원본 출처에 대한 출처를 제공하는 데 중요합니다.

#### **기반 응답의 예**

다음은 기반 쿼리 후 모델에서 반환된 콘텐츠 객체의 예입니다.

**최종 답변 텍스트:**

```
"예, 인터 마이애미는 FIFA 클럽 월드컵 마지막 경기에서 승리했습니다. 그들은 두 번째 조별 예선 경기에서 FC 포르투를 2-1로 이겼습니다. 토너먼트 첫 경기는 알 아흘리 FC와 0-0 무승부였습니다. 인터 마이애미는 2025년 6월 23일 월요일에 팔메이라스와 세 번째 조별 예선 경기를 치를 예정입니다."
```

**기반 메타데이터 스니펫:**

```json
"groundingMetadata": {
  "groundingChunks": [
    { "web": { "title": "mlssoccer.com", "uri": "..." } },
    { "web": { "title": "intermiamicf.com", "uri": "..." } },
    { "web": { "title": "mlssoccer.com", "uri": "..." } }
  ],
  "groundingSupports": [
    {
      "groundingChunkIndices": [0, 1],
      "segment": {
        "startIndex": 65,
        "endIndex": 126,
        "text": "그들은 두 번째 조별 예선 경기에서 FC 포르투를 2-1로 이겼습니다."
      }
    },
    {
      "groundingChunkIndices": [1],
      "segment": {
        "startIndex": 127,
        "endIndex": 196,
        "text": "토너먼트 첫 경기는 알 아흘리 FC와 0-0 무승부였습니다."
      }
    },
    {
      "groundingChunkIndices": [0, 2],
      "segment": {
        "startIndex": 197,
        "endIndex": 303,
        "text": "인터 마이애미는 2025년 6월 23일 월요일에 팔메이라스와 세 번째 조별 예선 경기를 치를 예정입니다."
      }
    }
  ],
  "searchEntryPoint": { ... }
}

```

#### **응답 해석 방법**

메타데이터는 모델에서 생성된 텍스트와 이를 지원하는 출처 간의 연결을 제공합니다. 단계별 분석은 다음과 같습니다.

1. **groundingChunks**: 모델이 참조한 웹 페이지 목록입니다. 각 청크에는 웹 페이지 제목과 출처에 연결되는 URI가 포함되어 있습니다.
2. **groundingSupports**: 이 목록은 최종 답변의 특정 문장을 groundingChunks에 다시 연결합니다.
   * **segment**: 이 객체는 startIndex, endIndex 및 텍스트 자체로 정의된 최종 텍스트 답변의 특정 부분을 식별합니다.
   * **groundingChunkIndices**: 이 배열에는 groundingChunks에 나열된 출처에 해당하는 인덱스 번호가 포함되어 있습니다. 예를 들어 "그들은 두 번째 조별 예선 경기에서 FC 포르투를 2-1로 이겼습니다..."라는 문장은 인덱스 0과 1의 groundingChunks(mlssoccer.com 및 intermiamicf.com 모두)의 정보로 지원됩니다.

### Google 검색으로 기반 응답을 표시하는 방법

기반을 사용하는 중요한 부분은 인용 및 검색 제안을 포함하여 정보를 최종 사용자에게 올바르게 표시하는 것입니다. 이는 신뢰를 구축하고 사용자가 정보를 확인할 수 있도록 합니다.

![Google 검색의 응답](../assets/google_search_grd_resp.png)

#### **검색 제안 표시**

`groundingMetadata`의 `searchEntryPoint` 객체에는 검색 쿼리 제안을 표시하기 위한 미리 서식이 지정된 HTML이 포함되어 있습니다. 예제 이미지에서 볼 수 있듯이 일반적으로 사용자가 관련 항목을 탐색할 수 있는 클릭 가능한 칩으로 렌더링됩니다.

**searchEntryPoint에서 렌더링된 HTML:** 메타데이터는 Google 로고와 "다음 FIFA 클럽 월드컵은 언제입니까" 및 "인터 마이애미 FIFA 클럽 월드컵 역사"와 같은 관련 쿼리에 대한 칩을 포함하는 검색 제안 표시줄을 렌더링하는 데 필요한 HTML 및 CSS를 제공합니다. 이 HTML을 애플리케이션의 프런트엔드에 직접 통합하면 제안이 의도한 대로 표시됩니다.

자세한 내용은 Vertex AI 설명서의 [Google 검색 제안 사용](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions)을 참조하십시오.

## 요약

Google 검색 기반은 AI 에이전트를 정적 지식 저장소에서 실시간으로 정확한 정보를 제공할 수 있는 동적 웹 연결 도우미로 변환합니다. 이 기능을 ADK 에이전트에 통합하면 다음을 수행할 수 있습니다.

- 학습 데이터를 넘어 최신 정보에 액세스
- 투명성과 신뢰를 위한 출처 표시 제공
- 검증 가능한 사실로 포괄적인 답변 제공
- 관련 검색 제안으로 사용자 경험 향상

기반 프로세스는 사용자 쿼리를 Google의 방대한 검색 인덱스에 원활하게 연결하여 대화 흐름을 유지하면서 최신 컨텍스트로 응답을 풍부하게 합니다. 기반 응답을 올바르게 구현하고 표시하면 에이전트는 정보 검색 및 의사 결정을 위한 강력한 도구가 됩니다.
