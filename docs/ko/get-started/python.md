# ADK용 Python 빠른 시작

이 가이드는 ADK(Agent Development Kit) for Python을 사용하여 시작하는 방법을 보여줍니다. 시작하기 전에 다음이 설치되어 있는지 확인하십시오.

*   Python 3.10 이상
*   패키지 설치를 위한 `pip`

## 설치

다음 명령어를 실행하여 ADK를 설치합니다.

```shell
pip install google-adk
```

??? tip "권장: Python 가상 환경 생성 및 활성화"

    Python 가상 환경을 생성합니다.

    ```shell
    python -m venv .venv
    ```

    Python 가상 환경을 활성화합니다.

    === "Windows CMD"

        ```console
        .venv\Scripts\activate.bat
        ```

    === "Windows Powershell"

        ```console
        .venv\Scripts\Activate.ps1
        ```

    === "MacOS / Linux"

        ```bash
        source .venv/bin/activate
        ```

## 에이전트 프로젝트 생성

`adk create` 명령을 실행하여 새 에이전트 프로젝트를 시작합니다.

```shell
adk create my_agent
```

### 에이전트 프로젝트 탐색

생성된 에이전트 프로젝트는 다음과 같은 구조를 가지며, `agent.py` 파일에는 에이전트의 주요 제어 코드가 포함되어 있습니다.

```none
my_agent/
    agent.py      # 메인 에이전트 코드
    .env          # API 키 또는 프로젝트 ID
    __init__.py
```

## 에이전트 프로젝트 업데이트

`agent.py` 파일에는 `root_agent` 정의가 포함되어 있으며, 이는 ADK 에이전트의 유일한 필수 요소입니다. 에이전트가 사용할 도구를 정의할 수도 있습니다. 생성된 `agent.py` 코드를 다음 코드에 표시된 대로 에이전트가 사용할 `get_current_time` 도구를 포함하도록 업데이트합니다.

```python
from google.adk.agents.llm_agent import Agent

# 모의 도구 구현
def get_current_time(city: str) -> dict:
    """지정된 도시의 현재 시간을 반환합니다."""
    return {"status": "success", "city": city, "time": "오전 10:30"}

root_agent = Agent(
    model='gemini-3-pro-preview',
    name='root_agent',
    description="지정된 도시의 현재 시간을 알려줍니다.",
    instruction="당신은 도시의 현재 시간을 알려주는 유용한 도우미입니다. 이를 위해 'get_current_time' 도구를 사용하십시오.",
    tools=[get_current_time],
)
```

### API 키 설정

이 프로젝트는 API 키가 필요한 Gemini API를 사용합니다. Gemini API 키가 아직 없는 경우 Google AI Studio의 [API 키](https://aistudio.google.com/app/apikey) 페이지에서 키를 생성합니다.

터미널 창에서 `.env` 파일에 API 키를 환경 변수로 작성합니다.

```console title="업데이트: my_agent/.env"
echo 'GOOGLE_API_KEY="YOUR_API_KEY"' > .env
```

??? tip "ADK에서 다른 AI 모델 사용"
    ADK는 다양한 생성형 AI 모델 사용을 지원합니다. ADK 에이전트에서 다른 모델을 구성하는 방법에 대한 자세한 내용은 [모델 및 인증](/adk-docs/ko/agents/models)을 참조하세요.

## 에이전트 실행

`adk run` 명령을 사용하여 대화형 명령줄 인터페이스로 ADK 에이전트를 실행하거나 `adk web` 명령을 사용하여 ADK에서 제공하는 ADK 웹 사용자 인터페이스를 사용하여 실행할 수 있습니다. 이 두 가지 옵션을 통해 에이전트를 테스트하고 상호 작용할 수 있습니다.

### 명령줄 인터페이스로 실행

`adk run` 명령줄 도구를 사용하여 에이전트를 실행합니다.

```console
adk run my_agent
```

![adk-run.png](/adk-docs/ko/assets/adk-run.png)

### 웹 인터페이스로 실행

ADK 프레임워크는 에이전트를 테스트하고 상호 작용하는 데 사용할 수 있는 웹 인터페이스를 제공합니다. 다음 명령을 사용하여 웹 인터페이스를 시작할 수 있습니다.

```console
adk web --port 8000
```

!!! note

    `my_agent/` 폴더가 포함된 **상위 디렉토리**에서 이 명령을 실행하십시오. 예를 들어 에이전트가 `agents/my_agent/` 안에 있는 경우 `agents/` 디렉토리에서 `adk web`을 실행하십시오.

이 명령은 에이전트용 채팅 인터페이스가 있는 웹 서버를 시작합니다. 웹 인터페이스는 (http://localhost:8000)에서 액세스할 수 있습니다. 왼쪽 상단 모서리에서 에이전트를 선택하고 요청을 입력합니다.

![adk-web-dev-ui-chat.png](/adk-docs/ko/assets/adk-web-dev-ui-chat.png)

## 다음: 에이전트 빌드

이제 ADK가 설치되었고 첫 번째 에이전트가 실행 중이므로 이제 빌드 가이드를 사용하여 자신만의 에이전트를 빌드해 보세요.

*  [에이전트 빌드](/adk-docs/ko/tutorials/)