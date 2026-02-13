---
catalog_title: Computer Use
catalog_description: Gemini 모델로 컴퓨터 사용자 인터페이스를 조작합니다
catalog_icon: /adk-docs/integrations/assets/gemini-spark.svg
catalog_tags: ["google"]
---
# Gemini와 함께하는 컴퓨터 사용 도구 세트

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.17.0</span><span class="lst-preview">미리보기</span>
</div>

컴퓨터 사용 도구 세트를 사용하면 에이전트가 브라우저와 같은 컴퓨터의 사용자 인터페이스를 조작하여 작업을 완료할 수 있습니다. 이 도구는 특정 Gemini 모델과 [Playwright](https://playwright.dev/) 테스트 도구를 사용하여 Chromium 브라우저를 제어하고 스크린샷 찍기, 클릭, 입력 및 탐색을 통해 웹 페이지와 상호 작용할 수 있습니다.

컴퓨터 사용 모델에 대한 자세한 내용은 Gemini API [컴퓨터 사용](https://ai.google.dev/gemini-api/docs/computer-use) 또는 Google Cloud Vertex AI API [컴퓨터 사용](https://cloud.google.com/vertex-ai/generative-ai/docs/computer-use)을 참조하세요.

!!! example "미리보기 출시"
    컴퓨터 사용 모델 및 도구는 미리보기 출시입니다. 자세한 내용은 [출시 단계 설명](https://cloud.google.com/products#product-launch-stages)을 참조하세요.

## 설정

컴퓨터 사용 도구 세트를 사용하려면 Playwright와 Chromium을 포함한 해당 종속성을 설치해야 합니다.

??? tip "권장: Python 가상 환경 생성 및 활성화"

    Python 가상 환경 생성:

    ```shell
    python -m venv .venv
    ```

    Python 가상 환경 활성화:

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

컴퓨터 사용 도구 세트에 필요한 소프트웨어 라이브러리를 설정하려면:

1.  Python 종속성 설치:
    ```console
    pip install termcolor==3.1.0
    pip install playwright==1.52.0
    pip install browserbase==1.3.0
    pip install rich
    ```
2.  Chromium 브라우저를 포함한 Playwright 종속성 설치:
    ```console
    playwright install-deps chromium
    playwright install chromium
    ```

## 도구 사용

에이전트에 도구로 추가하여 컴퓨터 사용 도구 세트를 사용합니다. 도구를 구성할 때 에이전트가 컴퓨터를 사용하는 인터페이스를 정의하는 `BaseComputer` 클래스의 구현을 제공해야 합니다. 다음 예에서는 이 목적을 위해 `PlaywrightComputer` 클래스가 정의됩니다. 이 구현에 대한 코드는 [computer_use](https://github.com/google/adk-python/blob/main/contributing/samples/computer_use/playwright.py) 에이전트 샘플 프로젝트의 `playwright.py` 파일에서 찾을 수 있습니다.

```python
from google.adk import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.computer_use.computer_use_toolset import ComputerUseToolset
from typing_extensions import override

from .playwright import PlaywrightComputer

root_agent = Agent(
    model='gemini-2.5-computer-use-preview-10-2025',
    name='hello_world_agent',
    description=(
        '컴퓨터에서 브라우저를 조작하여 사용자 작업을 완료할 수 있는 컴퓨터 사용 에이전트'
    ),
    instruction='당신은 컴퓨터 사용 에이전트입니다',
    tools=[
        ComputerUseToolset(computer=PlaywrightComputer(screen_size=(1280, 936)))
    ],
)
```

전체 코드 예제는 [computer_use](https://github.com/google/adk-python/tree/main/contributing/samples/computer_use) 에이전트 샘플 프로젝트를 참조하세요.
