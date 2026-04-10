---
catalog_title: Environment Toolset
catalog_description: 파일, 스크립트, 코드 실행을 위한 로컬 및 사용자 지정 컴퓨팅 환경을 만듭니다
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["code", "google"]
---

# ADK용 Environment Toolset

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.29.0</span><span class="lst-preview">실험적 기능</span>
</div>

특히 코딩과 파일 작업처럼 여러 에이전트 요청에 걸쳐 유지되는
컴퓨팅 환경에서 코드 실행과 파일 조작이 필요한 작업이 있습니다.
ADK의 ***EnvironmentToolset*** 클래스는 에이전트가 환경과 상호작용하여
파일 작업을 수행하고 셸 명령을 실행할 수 있게 해 줍니다.
Environment Toolset은 ADK 에이전트와 함께 사용할 로컬 또는 원격 실행 환경을
구성하고 활용하기 위한 일반 프레임워크로 설계되었습니다.
ADK는 [***LocalEnvironment***](#local-environment) 구현을 이 프레임워크용으로 제공합니다.

!!! example "실험적 기능"
    Environment Toolset 기능은 실험적이며 변경될 수 있습니다.
    의견이 있다면
    [피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md)을 보내 주세요.

## 시작하기

***EnvironmentToolset***에 ***LocalEnvironment*** 인스턴스를 추가해
에이전트가 로컬 환경과 상호작용하도록 활성화합니다.

```python
from google.adk import Agent
from google.adk.environment import LocalEnvironment
from google.adk.tools.environment import EnvironmentToolset

root_agent = Agent(
    model="gemini-flash-latest",
    name="my_agent",
    instruction="""
    당신은 로컬 환경을 사용해 명령 실행과 파일 I/O를 수행할 수 있는
    유용한 AI 어시스턴트입니다. 환경의 규칙과 사용자의 지시를 따르세요.
    """,
    tools=[
        EnvironmentToolset(
            environment=LocalEnvironment(),
        ),
    ],
)
```

전체 구현 예시는
[Local environment sample](https://github.com/google/adk-python/tree/main/contributing/samples/local_environment)을 참고하세요.

### 에이전트와 함께 사용해 보기

대화형 세션에서 파일 작업과 명령 실행이 필요한 프롬프트를 입력해,
Environment Toolset이 구성된 에이전트와 상호작용할 수 있습니다.
다음 프롬프트를 시도해 보세요.

```none
Write a Python file named hello.py to the working directory
that prints 'Hello from ADK!'. Then read the file to verify
its contents, and finally execute it using a command.
```

이 지침에 따라 에이전트는 다음 작업을 수행합니다.

-   파일 쓰기: `hello.py` 파일을 만들고 "Hello from ADK!" 내용을 저장합니다.
-   파일 읽기: `hello.py` 파일을 읽어 내용을 확인합니다.
-   실행: `hello.py` 파일을 실행하고 출력을 반환합니다.

## LocalEnvironment {#local-environment}

***LocalEnvironment*** 클래스는 ADK가 제공하는 환경 구현으로,
***Environment Toolset***과 함께 사용됩니다. 이 환경은 다음 기능을 제공합니다.

-   **로컬 실행:** Python asyncio subprocess를 사용해 로컬 머신에서
    셸 명령과 스크립트를 직접 실행합니다.
-   **파일 작업:** 지정한 작업 디렉터리 내에서 파일을 만들고, 읽고, 수정합니다.
-   **사용자 지정:** 에이전트 작업 공간에 사용할 환경 변수와 작업 디렉터리를 구성합니다.
-   **프레임워크 호환성:** 그래프 기반 워크플로를 포함해 ADK 1.0과 ADK 2.0
    모두와 호환됩니다.

### 구성 옵션

***LocalEnvironment*** 클래스는 다음 매개변수를 지원합니다.

-   **working_dir**: (선택 사항) 에이전트가 파일 작업과 명령 실행을 수행할 디렉터리입니다.
    작업 디렉터리를 지정하면 생성된 파일을 에이전트 실행 후에도 계속 사용할 수 있습니다.
    자세한 내용은 [파일 유지](#file-persistence)를 참고하세요.
-   **env_vars**: (선택 사항) 실행 컨텍스트에 설정할 환경 변수 딕셔너리입니다.

다음 코드 샘플은 ***LocalEnvironment*** 객체에 이러한 옵션을 설정하는 방법을 보여 줍니다.

```python
local_environment=LocalEnvironment(
    working_dir="/tmp/my_agent_workspace",
    env_vars={"PORT": "8080", "LOG_LEVEL": "DEBUG"},
)
```

### 파일 작업

***LocalEnvironment*** 구현에는 로컬 컴퓨팅 환경에서 에이전트가 실행할 수 있는 다음 도구가 포함됩니다.

-   ***ReadFile***: 에이전트 지시에 따라 기존 텍스트 파일을 읽습니다.
-   ***EditFile***: 에이전트 지시에 따라 기존 텍스트 파일을 수정합니다.
-   ***WriteFile***: 에이전트 지시에 따라 새 텍스트 파일을 만듭니다.
-   ***Execute***: 설치 프로그램, 셸 스크립트, 프로그램 코드 실행을 포함한 터미널 명령을
    에이전트 지시에 따라 실행합니다.

!!! danger "경고: 데이터 손실 및 코드 실행 가능성"

    로컬 환경에서 터미널 명령을 실행하면 해당 환경의 데이터가 손실되거나
    코드와 애플리케이션 실행에 영향을 줄 수 있습니다. 파일 변경과 명령 실행을
    허용하기 전에 사람의 승인 절차를 도입하는 것을 고려하세요.

***LocalEnvironment***에서 실행되는 명령은 `asyncio.create_subprocess_shell`을 사용하므로
장시간 실행 작업 중에도 에이전트가 계속 반응할 수 있습니다.

### 파일 유지 {#file-persistence}

***LocalEnvironment***로 생성한 파일과 파일 출력은 기본적으로 임시 디렉터리에 저장됩니다.
그 디렉터리는 ADK Web 세션 종료와 같이 에이전트가 종료될 때 삭제됩니다. 하지만 환경에
***working directory***를 설정하면, 그 위치에 작성된 파일은 에이전트 종료 후에도 *삭제되지 않습니다*.

**팁:** 에이전트 세션 간 파일 보존을 더 세밀하게 제어하려면 [***Artifacts***](/ko/artifacts/)와
Artifact Service를 사용해 파일을 환경으로 업로드하고 다운로드하세요.

## 사용자 지정 환경

***EnvironmentToolset*** 아키텍처는 확장 가능하도록 설계되어 있어,
원격 환경을 포함한 자체 사용자 지정 환경을 만들 수 있습니다.
이 기능에 사용할 실행 환경은
[BaseEnvironment](https://github.com/google/adk-python/blob/main/src/google/adk/environment/_base_environment.py)
클래스를 기반으로 만드는 것을 권장합니다.
시작하는 데 도움이 되도록 [LocalEnvironment](https://github.com/google/adk-python/blob/main/src/google/adk/environment/_local_environment.py)
구현 코드를 참고할 수 있습니다.
