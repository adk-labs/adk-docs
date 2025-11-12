# ADK용 Python 빠른 시작

이 가이드에서는 Python용 에이전트 개발 키트(ADK)를 시작하고 실행하는 방법을 보여줍니다. 시작하기 전에 다음이 설치되어 있는지 확인하십시오.

*   Python 3.9 이상
*   패키지 설치용 `pip`

## 설치

다음 명령을 실행하여 ADK를 설치합니다.

```shell
pip install google-adk
```

??? tip "권장: Python 가상 환경 생성 및 활성화"

    Python 가상 환경을 만듭니다.

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

## 에이전트 프로젝트 만들기

`adk create` 명령을 실행하여 새 에이전트 프로젝트를 시작합니다.

```shell
adk create my_agent
```

### 에이전트 프로젝트 살펴보기

생성된 에이전트 프로젝트는 다음과 같은 구조를 가지며 `agent.py` 파일에는 에이전트의 기본 제어 코드가 포함되어 있습니다.

```none
my_agent/
    agent.py      # 기본 에이전트 코드
    .env          # API 키 또는 프로젝트 ID
    __init__.py
```

## 에이전트 프로젝트 업데이트

`agent.py` 파일에는 ADK 에이전트의 유일한 필수 요소인 `root_agent` 정의가 포함되어 있습니다. 에이전트가 사용할 도구를 정의할 수도 있습니다. 다음 코드와 같이 에이전트가 사용할 `get_current_time` 도구를 포함하도록 생성된 `agent.py` 코드를 업데이트합니다.

```python
from google.adk.agents.llm_agent import Agent

# 모의 도구 구현
def get_current_time(city: str) -> dict:
    """지정된 도시의 현재 시간을 반환합니다."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="지정된 도시의 현재 시간을 알려줍니다.",
    instruction="당신은 도시의 현재 시간을 알려주는 유용한 도우미입니다. 이 용도로 'get_current_time' 도구를 사용하십시오.",
    tools=[get_current_time],
)
```

### API 키 설정

이 프로젝트는 API 키가 필요한 Gemini API를 사용합니다. 아직 Gemini API 키가 없는 경우 Google AI Studio의 [API 키](https://aistudio.google.com/app/apikey) 페이지에서 키를 만듭니다.

터미널 창에서 API 키를 환경 변수로 `.env` 파일에 작성합니다.

```console title="Update: my_agent/.env"
echo 'GOOGLE_API_KEY="YOUR_API_KEY"' > .env
```

??? tip "ADK에서 다른 AI 모델 사용"
    ADK는 많은 생성 AI 모델의 사용을 지원합니다. ADK 에이전트에서 다른 모델을 구성하는 방법에 대한 자세한 내용은 [모델 및 인증](/adk-docs/agents/models)을 참조하십시오.

## 에이전트 실행

`adk run` 명령을 사용하는 대화형 명령줄 인터페이스 또는 `adk web` 명령을 사용하여 ADK에서 제공하는 ADK 웹 사용자 인터페이스로 ADK 에이전트를 실행할 수 있습니다. 이 두 가지 옵션 모두 에이전트를 테스트하고 상호 작용할 수 있습니다.

### 명령줄 인터페이스로 실행

`adk run` 명령줄 도구를 사용하여 에이전트를 실행합니다.

```console
adk run my_agent
```

![adk-run.png](/adk-docs/assets/adk-run.png)

### 웹 인터페이스로 실행

ADK 프레임워크는 에이전트를 테스트하고 상호 작용하는 데 사용할 수 있는 웹 인터페이스를 제공합니다. 다음 명령을 사용하여 웹 인터페이스를 시작할 수 있습니다.

```console
adk web --port 8000
```

!!! note

    `my_agent/` 폴더가 포함된 **상위 디렉터리**에서 이 명령을 실행합니다. 예를 들어 에이전트가 `agents/my_agent/` 내에 있는 경우 `agents/` 디렉터리에서 `adk web`을 실행합니다.

이 명령은 에이전트용 채팅 인터페이스가 있는 웹 서버를 시작합니다. (http://localhost:8000)에서 웹 인터페이스에 액세스할 수 있습니다. 왼쪽 상단에서 에이전트를 선택하고 요청을 입력합니다.

![adk-web-dev-ui-chat.png](/adk-docs/assets/adk-web-dev-ui-chat.png)

## 다음: 에이전트 빌드

이제 ADK를 설치하고 첫 번째 에이전트를 실행했으므로 빌드 가이드를 사용하여 자신만의 에이전트를 빌드해 보세요.

*  [에이전트 빌드](/adk-docs/tutorials/)
