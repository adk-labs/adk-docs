---
catalog_title: Computer Use
catalog_description: Gemini 모델로 컴퓨터 사용자 인터페이스를 조작합니다
catalog_icon: /integrations/assets/gemini-spark.svg
catalog_tags: ["google"]
---
# ADK용 Gemini API Computer Use 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.17.0</span><span class="lst-preview">미리보기</span>
</div>

Computer Use 도구 세트(`ComputerUseToolset`)를 사용하면 에이전트가 브라우저와 같은 컴퓨터의 사용자 인터페이스를 직접 조작하여 작업을 완료할 수 있습니다. 이 도구는 전용 Gemini 모델과 [Playwright](https://playwright.dev/) 테스트 도구를 사용하여 Chromium 브라우저를 제어하며, 스크린샷 캡처, 클릭, 텍스트 입력, 페이지 이동을 통해 웹 페이지와 상호작용할 수 있습니다.

Computer Use 모델에 대한 자세한 내용은 Gemini API [Computer Use](https://ai.google.dev/gemini-api/docs/computer-use) 또는 Google Cloud Vertex AI API [Computer Use](https://cloud.google.com/vertex-ai/generative-ai/docs/computer-use) 문서를 참고하세요.

!!! example "Preview 릴리스"
    Computer Use 모델 및 도구는 Preview 릴리스입니다. 자세한 내용은 [출시 단계 설명](https://cloud.google.com/products#product-launch-stages)을 참고하세요.

## 설정

Computer Use 도구 세트를 사용하려면 Playwright와 Chromium을 포함한 관련 종속 항목을 설치해야 합니다.

??? tip "권장: Python 가상 환경 생성 및 활성화"

    Python 가상 환경 생성:

    ```shell
    python3 -m venv .venv
    ```

    Python 가상 환경 활성화:

    === "Windows CMD"

        ```console
        .venv\Scripts\activate.bat
        ```

    === "Windows PowerShell"

        ```console
        .venv\Scripts\Activate.ps1
        ```

    === "MacOS / Linux"

        ```bash
        source .venv/bin/activate
        ```

Computer Use 도구 세트에 필요한 소프트웨어 라이브러리를 설정하려면 다음 단계를 따르세요.

1.  Python 종속 항목 설치:
    ```console
    pip install termcolor==3.1.0
    pip install playwright==1.52.0
    pip install browserbase==1.3.0
    pip install rich
    ```
2.  Chromium 브라우저를 포함한 Playwright 종속 항목 설치:
    ```console
    playwright install-deps chromium
    playwright install chromium
    ```

## 도구 사용

Computer Use 도구 세트를 에이전트에 도구로 추가하여 사용합니다. 도구를 구성할 때는 에이전트가 컴퓨터를 조작하는 인터페이스를 정의하는 `BaseComputer` 클래스의 구현체를 제공해야 합니다. 다음 예제에서는 이를 위해 `PlaywrightComputer` 클래스를 정의하여 사용합니다. 이 구현체의 전체 코드는 [computer_use](https://github.com/google/adk-python/blob/main/contributing/samples/computer_use/playwright.py) 에이전트 샘플 프로젝트의 `playwright.py` 파일에서 확인할 수 있습니다.

```python
from google.adk import Agent
from google.adk.tools.computer_use.computer_use_toolset import ComputerUseToolset

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

전체 코드 예제는 [computer_use](https://github.com/google/adk-python/tree/main/contributing/samples/computer_use) 에이전트 샘플 프로젝트를 참고하세요.
