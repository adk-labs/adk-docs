# ADK 2.0 Alpha에 오신 것을 환영합니다

!!! example "Alpha 릴리스"

    ADK 2.0은 Alpha 릴리스이며, 이전 버전의 ADK와 함께 사용할 때 호환성이
    깨지는 변경이 발생할 수 있습니다. 프로덕션 환경처럼 하위 호환성이 필요한
    경우에는 ADK 2.0을 사용하지 마세요. 이 릴리스를 테스트해 보시고
    [피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)을
    보내주시기 바랍니다.

ADK 2.0은 정교한 AI 에이전트를 구축하기 위한 강력한 도구를 도입하며,
에이전트를 더 높은 제어력, 예측 가능성, 신뢰성으로 까다로운 작업을
수행하도록 구조화할 수 있게 해줍니다. ADK 2.0은 Python용 Alpha 릴리스로
제공되며 다음 핵심 기능을 포함합니다.

- [**그래프 기반 워크플로**](/ko/workflows/): 작업이 라우팅되고
  실행되는 방식을 더 세밀하게 제어할 수 있는 결정론적 에이전트 워크플로를
  구축합니다.
- [**협업 에이전트**](/ko/workflows/collaboration/): 조정 역할의
  에이전트와 함께 여러 서브에이전트가 협력하는 복잡한 에이전트 아키텍처를
  구축합니다.
- [**동적 워크플로**](/ko/workflows/dynamic/): 반복 루프와 복잡한
  의사결정 기반 분기를 포함하는 더 복잡한 워크플로를 코드 기반 로직으로
  구현합니다.

자세한 내용은 위의 연결된 주제를 확인하고, ADK 2.0으로 에이전트를 구축하는
새로운 방식을 직접 시도해 보세요.

## ADK 1.0 호환성

ADK 2.0은 ADK 1.x 릴리스로 개발한 에이전트와 호환되도록 설계되었습니다.
하지만 ADK 1.x로 구축된 에이전트의 수와 다양성을 고려할 때, 일부 에이전트
구현, 특히 고급 기능이 많은 에이전트는 ADK 2.0에서 호환성 문제를 드러낼 수
있다고 예상합니다. 현재 GA 이전 릴리스 기간 동안 이러한 문제를 식별할 수
있도록 도움을 부탁드립니다. ADK 1.0에서 ADK 2.0으로 전환할 때 발견한
비호환성은 [이슈 트래커](https://github.com/google/adk-python/issues/new?template=bug_report.md&labels=v2)를
통해 보고해 주세요.

!!! danger "경고: ADK 2.0과 ADK 1.0 데이터 저장 시스템을 혼용하지 마세요"

    ADK 2.0 프로젝트에 영속 저장소를 사용하는 경우, **세션 저장소, 메모리
    시스템, 평가 데이터 등을 포함해 ADK 2.0 프로젝트가 ADK 1.0 프로젝트와
    저장소를 공유하도록 두지 마세요.** 이렇게 하면 데이터가 손실되거나 ADK
    1.0 프로젝트에서 데이터를 사용할 수 없게 될 수 있습니다.

## ADK 2.0 설치 {#install}

ADK 2.0은 pre-GA 릴리스로 제공되므로 자동으로 설치되지 않습니다. 설치 시 이
버전을 명시적으로 선택해야 합니다. 이 버전의 시스템 요구 사항은 다음과
같습니다.

* **Python 3.11** 이상
* 패키지 설치를 위한 `pip`

ADK 2.0을 설치하려면 다음 단계를 따르세요.

1. Python 가상 환경을 활성화합니다. 아래 지침을 참고하세요.
1. 현재 pre-GA 버전의 ADK 2.0을 선택하기 위해 `--pre` 옵션과 함께 `pip`로
   패키지를 설치합니다.

   ```bash
   pip install google-adk --pre
   ```

??? tip "권장: Python 가상 환경을 생성하고 활성화하기"

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

!!! note "참고: 기존 ADK 1.0 프로젝트 업데이트"

    Python 환경에 이미 ADK 1.0 라이브러리가 설치되어 있는 경우, `--pre`
    옵션만으로는 ADK 2.0 라이브러리가 설치되지 않습니다. 위 설치 명령에
    `--force` 옵션을 추가하면 ADK 2.0 라이브러리를 강제로 설치할 수
    있습니다. ADK 2.0에는 Python 가상 환경을 사용하고, **ADK 1.0 프로젝트를
    ADK 2.0 라이브러리로 업데이트하기 전에 반드시 백업을 확보하세요.**

## 다음 단계

ADK 2.0 기능으로 에이전트를 구축하는 개발자 가이드를 확인하세요.

- [**그래프 기반 워크플로**](/ko/workflows/)
- [**협업 에이전트**](/ko/workflows/collaboration/)
- [**동적 워크플로**](/ko/workflows/dynamic/)

테스트와 영감을 위해 다음 ADK 2.0 코드 샘플도 확인해 보세요.

- [**워크플로 샘플**](https://github.com/google/adk-python/tree/v2/contributing/workflow_samples)
- [**협업 작업 샘플**](https://github.com/google/adk-python/tree/v2/contributing/task_samples)

ADK 2.0을 확인해 주셔서 감사합니다. 여러분의
[피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)을
기다리겠습니다.
