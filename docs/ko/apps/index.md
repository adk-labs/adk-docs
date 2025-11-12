# 앱: 워크플로 관리 클래스

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.14.0</span>
</div>

***앱*** 클래스는 전체 에이전트 개발 키트(ADK) 에이전트 워크플로의 최상위 컨테이너입니다. ***루트 에이전트***별로 그룹화된 에이전트 모음의 수명 주기, 구성 및 상태를 관리하도록 설계되었습니다. **앱** 클래스는 에이전트 워크플로의 전체 운영 인프라에 대한 우려 사항을 개별 에이전트의 작업 지향적 추론과 분리합니다.

ADK 워크플로에서 ***앱*** 객체를 정의하는 것은 선택 사항이며 에이전트 코드를 구성하고 에이전트를 실행하는 방법을 변경합니다. 실용적인 관점에서 ***앱*** 클래스를 사용하여 에이전트 워크플로에 대한 다음 기능을 구성합니다.

*   [**컨텍스트 캐싱**](/adk-docs/context/caching/)
*   [**컨텍스트 압축**](/adk-docs/context/compaction/)
*   [**에이전트 재개**](/adk-docs/runtime/resume/)
*   [**플러그인**](/adk-docs/plugins/)

이 가이드에서는 ADK 에이전트 워크플로를 구성하고 관리하기 위해 앱 클래스를 사용하는 방법을 설명합니다.

## 앱 클래스의 목적

***앱*** 클래스는 복잡한 에이전트 시스템을 구축할 때 발생하는 몇 가지 아키텍처 문제를 해결합니다.

*   **중앙 집중식 구성:** API 키 및 데이터베이스 클라이언트와 같은 공유 리소스를 관리하기 위한 단일 중앙 집중식 위치를 제공하여 모든 에이전트를 통해 구성을 전달할 필요가 없습니다.
*   **수명 주기 관리:** ***앱*** 클래스에는 ***시작 시*** 및 ***종료 시*** 후크가 포함되어 있어 여러 호출에 걸쳐 존재해야 하는 데이터베이스 연결 풀 또는 인메모리 캐시와 같은 영구 리소스를 안정적으로 관리할 수 있습니다.
*   **상태 범위:** `app:*` 접두사로 애플리케이션 수준 상태에 대한 명시적인 경계를 정의하여 이 상태의 범위와 수명을 개발자에게 명확하게 합니다.
*   **배포 단위:** ***앱*** 개념은 공식적인 *배포 가능 단위*를 설정하여 에이전트 애플리케이션의 버전 관리, 테스트 및 서비스를 단순화합니다.

## 앱 객체 정의

***앱*** 클래스는 에이전트 워크플로의 기본 컨테이너로 사용되며 프로젝트의 루트 에이전트를 포함합니다. ***루트 에이전트***는 기본 컨트롤러 에이전트 및 추가 하위 에이전트의 컨테이너입니다.

### 루트 에이전트로 앱 정의

***에이전트*** 기본 클래스에서 서브클래스를 만들어 워크플로에 대한 ***루트 에이전트***를 만듭니다. 그런 다음 다음 샘플 코드와 같이 ***앱*** 객체를 정의하고 ***루트 에이전트*** 객체 및 선택적 기능으로 구성합니다.

```python title="agent.py"
from google.adk.agents.llm_agent import Agent
from google.adk.apps import App

root_agent = Agent(
    model='gemini-2.5-flash',
    name='greeter_agent',
    description='An agent that provides a friendly greeting.',
    instruction='Reply with Hello, World!',
)

app = App(
    name="agents",
    root_agent=root_agent,
    # Optionally include App-level features:
    # plugins, context_cache_config, resumability_config
)
```

!!! tip "권장: `app` 변수 이름 사용"

    에이전트 프로젝트 코드에서 ***앱*** 객체를 변수 이름 `app`으로 설정하여 ADK 명령줄 인터페이스 실행기 도구와 호환되도록 합니다.

### 앱 에이전트 실행

다음 코드 샘플과 같이 `app` 매개변수를 사용하여 ***실행기*** 클래스를 사용하여 에이전트 워크플로를 실행할 수 있습니다.

```python title="main.py"
import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from agent import app # agent.py에서 코드 가져오기

load_dotenv() # API 키 및 설정 로드
# 가져온 애플리케이션 객체를 사용하여 실행기 설정
runner = InMemoryRunner(app=app)

async def main():
    try:  # run_debug()에는 ADK Python 1.18 이상이 필요합니다.
        response = await runner.run_debug("Hello there!")
        
    except Exception as e:
        print(f"An error occurred during agent execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())

```

!!! note "`Runner.run_debug()`에 대한 버전 요구 사항"

    `Runner.run_debug()` 명령에는 ADK Python v1.18.0 이상이 필요합니다. 더 많은 설정 코드가 필요한 `Runner.run()`을 사용할 수도 있습니다. 자세한 내용은 다음을 참조하십시오.

다음 명령을 사용하여 `main.py` 코드로 앱 에이전트를 실행합니다.

```console
python main.py
```

## 다음 단계

더 완전한 샘플 코드 구현은 [Hello World 앱](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_app) 코드 예제를 참조하십시오.
