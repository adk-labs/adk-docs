# Google 검색 그라운딩 이해

[Google 검색 그라운딩 도구](../tools/built-in-tools.md#google-search)는 ADK(Agent Development Kit)의 강력한 기능으로, AI 에이전트가 웹에서 실시간의 권위 있는 정보에 액세스할 수 있도록 합니다. 에이전트를 Google 검색에 연결하여 신뢰할 수 있는 출처를 기반으로 사용자에게 최신 답변을 제공할 수 있습니다.

이 기능은 날씨 업데이트, 뉴스 이벤트, 주식 가격 또는 모델의 학습 데이터 마감일 이후 변경되었을 수 있는 모든 사실과 같이 현재 정보가 필요한 쿼리에 특히 유용합니다. 에이전트가 외부 정보가 필요하다고 판단하면 자동으로 웹 검색을 수행하고 적절한 출처 표시와 함께 결과를 응답에 통합합니다.

## 학습할 내용

이 가이드에서는 다음을 학습합니다.

- **빠른 설정**: Google 검색 지원 에이전트를 처음부터 생성하고 실행하는 방법
- **그라운딩 아키텍처**: 웹 그라운딩의 데이터 흐름 및 기술 프로세스
- **응답 구조**: 그라운딩된 응답 및 메타데이터를 해석하는 방법
- **모범 사례**: 사용자에게 검색 결과 및 출처를 표시하기 위한 지침

### 추가 자료

추가 자료로, [Gemini 풀스택 에이전트 개발 키트(ADK) 빠른 시작](https://github.com/google/adk-samples/tree/main/python/agents/gemini-fullstack)에는 풀스택 애플리케이션 예시로 [Google 검색 그라운딩을 훌륭하게 실용적으로 사용한 사례](https://github.com/google/adk-samples/blob/main/python/agents/gemini-fullstack/app/agent.py)가 있습니다.

## Google 검색 그라운딩 빠른 시작

이 빠른 시작은 Google 검색 그라운딩 기능이 있는 ADK 에이전트를 생성하는 과정을 안내합니다. 이 빠른 시작은 Python 3.10+ 및 터미널 액세스가 가능한 로컬 IDE(VS Code 또는 PyCharm 등)를 가정합니다.

### 1. 환경 설정 및 ADK 설치 { #set-up-environment-install-adk }

가상 환경 생성 및 활성화:

```bash
# 생성
python -m venv .venv

# 활성화(새 터미널마다)
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

ADK 설치:

```bash
pip install google-adk==1.4.2
```

### 2. 에이전트 프로젝트 생성 { #create-agent-project }

프로젝트 디렉토리에서 다음 명령을 실행합니다.

=== "OS X &amp; Linux"
    ```bash
    # 1단계: 에이전트용 새 디렉토리 생성
    mkdir google_search_agent

    # 2단계: 에이전트용 __init__.py 생성
    echo "from . import agent" > google_search_agent/__init__.py

    # 3단계: agent.py(에이전트 정의) 및 .env(Gemini 인증 구성) 생성
    touch google_search_agent/agent.py .env
    ```

=== "Windows"
    ```shell
    # 1단계: 에이전트용 새 디렉토리 생성
    mkdir google_search_agent

    # 2단계: 에이전트용 __init__.py 생성
    echo "from . import agent" > google_search_agent/__init__.py

    # 3단계: agent.py(에이전트 정의) 및 .env(Gemini 인증 구성) 생성
    type nul > google_search_agent\agent.py 
    type nul > google_search_agent\.env
    ```



#### `agent.py` 편집

다음 코드를 `agent.py`에 복사하여 붙여넣습니다.

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

이제 다음과 같은 디렉토리 구조가 됩니다.

```console
my_project/
    google_search_agent/
        __init__.py
        agent.py
    .env
```

### 3. 플랫폼 선택 { #choose-a-platform }

에이전트를 실행하려면 에이전트가 Gemini 모델을 호출하는 데 사용할 플랫폼을 선택해야 합니다. Google AI Studio 또는 Vertex AI 중 하나를 선택합니다.

=== "Gemini - Google AI Studio"
    1. [Google AI Studio](https://aistudio.google.com/apikey)에서 API 키를 가져옵니다.
    2. Python을 사용하는 경우 **`.env`** 파일을 열고 다음 코드를 복사하여 붙여넣습니다.

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3. `PASTE_YOUR_ACTUAL_API_KEY_HERE`를 실제 `API KEY`로 바꿉니다.

=== "Gemini - Google Cloud Vertex AI"
    1. 기존 [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) 계정 및 프로젝트가 필요합니다.
        * [Google Cloud 프로젝트](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)를 설정합니다.
        * [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)를 설정합니다.
        * 터미널에서 `gcloud auth login`을 실행하여 Google Cloud에 인증합니다.
        * [Vertex AI API를 활성화](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)합니다.
    2. Python을 사용하는 경우 **`.env`** 파일을 열고 다음 코드를 복사하여 붙여넣고 프로젝트 ID와 위치를 업데이트합니다.

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=LOCATION
        ```

### 4. 에이전트 실행 { #run-your-agent }

에이전트와 상호 작용하는 여러 가지 방법이 있습니다.

=== "개발 UI (adk web)"
    다음 명령을 실행하여 **개발 UI**를 시작합니다.

    ```shell
    adk web
    ```
    
    !!!info "Windows 사용자 참고 사항"

        `_make_subprocess_transport NotImplementedError`가 발생하는 경우 대신 `adk web --no-reload`를 사용하는 것을 고려하십시오.


    **1단계:** 제공된 URL(일반적으로 `http://localhost:8000` 또는 `http://127.0.0.1:8000`)을 브라우저에서 직접 엽니다.

    **2단계.** UI의 왼쪽 상단 모서리에서 드롭다운에서 에이전트를 선택할 수 있습니다. "google_search_agent"를 선택합니다.

    !!!note "문제 해결"

        드롭다운 메뉴에 "google_search_agent"가 표시되지 않으면 에이전트 폴더의 **상위 폴더**(즉, google_search_agent의 상위 폴더)에서 `adk web`을 실행하고 있는지 확인하십시오.

    **3단계.** 이제 텍스트 상자를 사용하여 에이전트와 대화할 수 있습니다.

=== "터미널 (adk run)"

    날씨 에이전트와 채팅하려면 다음 명령을 실행하십시오.

    ```
    adk run google_search_agent
    ```
    종료하려면 Cmd/Ctrl+C를 사용하십시오.

### 📝 시도할 예시 프롬프트

이 질문들을 통해 에이전트가 최신 날씨와 시간을 얻기 위해 실제로 Google 검색을 호출하는지 확인할 수 있습니다.

* 뉴욕의 날씨는 어떻습니까?
* 뉴욕의 시간은 몇 시입니까?
* 파리의 날씨는 어떻습니까?
* 파리의 시간은 몇 시입니까?

![adk 웹을 사용하여 에이전트 시도](../assets/google_search_grd_adk_web.png)

ADK를 사용하여 Google 검색 에이전트를 성공적으로 만들고 상호 작용했습니다!

## Google 검색 그라운딩 작동 방식

그라운딩은 에이전트를 웹에서 실시간 정보에 연결하여 AI 에이전트가 더 정확하고 최신 응답을 생성할 수 있도록 하는 프로세스입니다. 사용자 프롬프트가 모델이 학습하지 않은 정보 또는 시간에 민감한 정보를 요구할 때 에이전트의 기본 대규모 언어 모델은 관련 사실을 찾기 위해 google_search 도구를 호출할지 지능적으로 결정합니다.

### **데이터 흐름 다이어그램**

이 다이어그램은 사용자 쿼리가 그라운딩된 응답으로 이어지는 단계별 프로세스를 보여줍니다.

![](../assets/google_search_grd_dataflow.png)

### **상세 설명**

그라운딩 에이전트는 다이어그램에 설명된 데이터 흐름을 사용하여 외부 정보를 검색, 처리 및 사용자에게 제시되는 최종 답변에 통합합니다.

1. **사용자 쿼리**: 최종 사용자가 질문을 하거나 명령을 내려 에이전트와 상호 작용합니다.
2. **ADK 오케스트레이션**: Agent Development Kit는 에이전트의 동작을 오케스트레이션하고 사용자의 메시지를 에이전트의 핵심으로 전달합니다.
3. **LLM 분석 및 도구 호출**: 에이전트의 LLM(예: Gemini 모델)이 프롬프트를 분석합니다. 외부의 최신 정보가 필요하다고 판단하면 google_search 도구를 호출하여 그라운딩 메커니즘을 트리거합니다. 이는 최신 뉴스, 날씨 또는 모델의 학습 데이터에 없는 사실에 대한 쿼리에 답변하는 데 이상적입니다.
4. **그라운딩 서비스 상호 작용**: google_search 도구는 Google 검색 인덱스에 하나 이상의 쿼리를 구성하고 전송하는 내부 그라운딩 서비스와 상호 작용합니다.
5. **컨텍스트 주입**: 그라운딩 서비스는 관련 웹 페이지와 스니펫을 검색합니다. 그런 다음 최종 응답이 생성되기 전에 이러한 검색 결과를 모델의 컨텍스트에 통합합니다. 이 중요한 단계는 모델이 사실적이고 실시간 데이터에 대해 "추론"할 수 있도록 합니다.
6. **그라운딩된 응답 생성**: 이제 새로운 검색 결과에 의해 정보를 얻은 LLM은 검색된 정보를 통합하는 응답을 생성합니다.
7. **출처와 함께 응답 제시**: ADK는 필요한 출처 URL과 groundingMetadata를 포함하는 최종 그라운딩된 응답을 수신하고 출처 표시와 함께 사용자에게 제시합니다. 이를 통해 최종 사용자는 정보를 확인하고 에이전트 답변에 대한 신뢰를 구축할 수 있습니다.

### Google 검색 응답으로 그라운딩 이해

에이전트가 Google 검색을 사용하여 응답을 그라운딩할 때 최종 텍스트 답변뿐만 아니라 해당 답변을 생성하는 데 사용한 출처를 포함하는 상세한 정보 세트를 반환합니다. 이 메타데이터는 응답을 확인하고 원본 출처에 대한 출처 표시를 제공하는 데 중요합니다.

#### **그라운딩된 응답의 예시**

다음은 그라운딩된 쿼리 후 모델이 반환한 콘텐츠 객체의 예시입니다.

**최종 답변 텍스트:**

```
"네, 인터 마이애미는 FIFA 클럽 월드컵에서 마지막 경기에서 승리했습니다. 2차 조별 리그 경기에서 FC 포르투를 2-1로 이겼습니다. 토너먼트의 첫 경기는 알 아흘리 FC와 0-0 무승부였습니다. 인터 마이애미는 2025년 6월 23일 월요일에 팔메이라스를 상대로 3차 조별 리그 경기를 치를 예정입니다."
```

**그라운딩 메타데이터 스니펫:**

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
        "text": "2차 조별 리그 경기에서 FC 포르투를 2-1로 이겼습니다."
      }
    },
    {
      "groundingChunkIndices": [1],
      "segment": {
        "startIndex": 127,
        "endIndex": 196,
        "text": "토너먼트의 첫 경기는 알 아흘리 FC와 0-0 무승부였습니다."
      }
    },
    {
      "groundingChunkIndices": [0, 2],
      "segment": {
        "startIndex": 197,
        "endIndex": 303,
        "text": "인터 마이애미는 2025년 6월 23일 월요일에 팔메이라스를 상대로 3차 조별 리그 경기를 치를 예정입니다."
      }
    }
  ],
  "searchEntryPoint": { ... }
}

```

#### **응답을 해석하는 방법**

메타데이터는 모델이 생성한 텍스트와 이를 뒷받침하는 출처 간의 링크를 제공합니다. 다음은 단계별 분석입니다.

1. **groundingChunks**: 모델이 참조한 웹 페이지 목록입니다. 각 청크에는 웹 페이지의 제목과 출처로 연결되는 uri가 포함되어 있습니다.
2. **groundingSupports**: 이 목록은 최종 답변의 특정 문장을 groundingChunks의 출처에 연결합니다.
   * **segment**: 이 객체는 startIndex, endIndex 및 텍스트 자체로 정의되는 최종 텍스트 답변의 특정 부분을 식별합니다.
   * **groundingChunkIndices**: 이 배열에는 groundingChunks에 나열된 출처에 해당하는 인덱스 번호가 포함되어 있습니다. 예를 들어, "FC 포르투를 2-1로 이겼습니다..."라는 문장은 인덱스 0과 1의 groundingChunks(mlssoccer.com 및 intermiamicf.com 모두)의 정보로 뒷받침됩니다.

### Google 검색으로 그라운딩 응답을 표시하는 방법

그라운딩을 사용하는 중요한 부분은 인용 및 검색 제안을 포함한 정보를 최종 사용자에게 올바르게 표시하는 것입니다. 이는 신뢰를 구축하고 사용자가 정보를 확인할 수 있도록 합니다.

![Google 검색 응답](../assets/google_search_grd_resp.png)

#### **검색 제안 표시**

`groundingMetadata`의 `searchEntryPoint` 객체에는 검색 쿼리 제안을 표시하기 위해 미리 서식 지정된 HTML이 포함되어 있습니다. 예시 이미지에서 볼 수 있듯이, 이들은 일반적으로 사용자가 관련 주제를 탐색할 수 있도록 클릭 가능한 칩으로 렌더링됩니다.

**searchEntryPoint에서 렌더링된 HTML:** 메타데이터는 Google 로고 및 "다음 FIFA 클럽 월드컵은 언제인가" 및 "인터 마이애미 FIFA 클럽 월드컵 역사"와 같은 관련 쿼리용 칩을 포함하는 검색 제안 바를 렌더링하는 데 필요한 HTML 및 CSS를 제공합니다. 이 HTML을 애플리케이션의 프런트 엔드에 직접 통합하면 제안이 의도한 대로 표시됩니다.

자세한 내용은 Vertex AI 문서의 [Google 검색 제안 사용](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions)을 참조하십시오.

## 요약

Google 검색 그라운딩은 AI 에이전트를 정적 지식 저장소에서 실시간으로 정확한 정보를 제공할 수 있는 동적 웹 연결 도우미로 변환합니다. 이 기능을 ADK 에이전트에 통합하면 다음을 수행할 수 있습니다.

- 학습 데이터를 넘어선 현재 정보에 액세스
- 투명성과 신뢰를 위한 출처 표시 제공
- 검증 가능한 사실을 포함한 포괄적인 답변 제공
- 관련 검색 제안으로 사용자 경험 향상

그라운딩 프로세스는 사용자 쿼리를 Google의 방대한 검색 인덱스에 원활하게 연결하여 대화 흐름을 유지하면서 최신 컨텍스트로 응답을 풍부하게 합니다. 그라운딩된 응답을 올바르게 구현하고 표시하면 에이전트가 정보 검색 및 의사 결정에 강력한 도구가 됩니다.