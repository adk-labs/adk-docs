# 빠른 시작: A2A를 통해 원격 에이전트 노출하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-preview">실험적 기능</span>
</div>

이 빠른 시작 가이드는 모든 개발자의 가장 일반적인 출발점인 **"에이전트가 있는데, 다른 에이전트들이 A2A를 통해 내 에이전트를 사용할 수 있도록 어떻게 노출하나요?"**에 대해 다룹니다. 이는 서로 다른 에이전트들이 협력하고 상호 작용해야 하는 복잡한 다중 에이전트 시스템을 구축하는 데 매우 중요합니다.

## 개요

이 샘플은 ADK 에이전트를 쉽게 노출하여 다른 에이전트가 A2A 프로토콜을 사용하여 이를 소비(consume)할 수 있는 방법을 보여줍니다.

ADK 에이전트를 A2A를 통해 노출하는 두 가지 주요 방법이 있습니다.

*   **`to_a2a(root_agent)` 함수 사용:** 기존 에이전트를 A2A와 연동되도록 변환하고, `adk deploy api_server` 대신 `uvicorn`을 통해 서버로 노출하고 싶을 때 이 함수를 사용하세요. 이는 에이전트를 프로덕션 환경에 배포할 때 `uvicorn`을 통해 노출할 대상을 더 세밀하게 제어할 수 있음을 의미합니다. 또한, `to_a2a()` 함수는 에이전트 코드를 기반으로 에이전트 카드(agent card)를 자동으로 생성합니다.
*   **자신만의 에이전트 카드(`agent.json`)를 생성하고 `adk api_server --a2a`를 사용하여 호스팅:** 이 접근 방식에는 두 가지 주요 이점이 있습니다. 첫째, `adk api_server --a2a`는 `adk web`과 함께 작동하여 에이전트를 쉽게 사용, 디버깅 및 테스트할 수 있습니다. 둘째, `adk api_server`를 사용하면 여러 개의 개별 에이전트가 있는 상위 폴더를 지정할 수 있습니다. 에이전트 카드(`agent.json`)가 있는 에이전트들은 동일한 서버를 통해 다른 에이전트들이 A2A를 통해 자동으로 사용할 수 있게 됩니다. 하지만, 자신만의 에이전트 카드를 만들어야 합니다. 에이전트 카드를 만드는 방법은 [A2A Python 튜토리얼](https://a2a-protocol.org/latest/tutorials/python/1-introduction/)을 따를 수 있습니다.

이 빠른 시작 가이드는 `to_a2a()`에 초점을 맞춥니다. 이 방법이 에이전트를 노출하는 가장 쉬운 방법이며, 에이전트 카드도 배후에서 자동으로 생성하기 때문입니다. `adk api_server` 접근 방식을 사용하고 싶다면, [A2A 빠른 시작 (소비편) 문서](quickstart-consuming.md)에서 사용 예시를 볼 수 있습니다.

```text
전:
                                                ┌────────────────────┐
                                                │ 헬로 월드 에이전트      │
                                                │ (Python 객체)        │
                                                │ (에이전트 카드 없음)    │
                                                └────────────────────┘

                                                          │
                                                          │ to_a2a()
                                                          ▼

후:
┌────────────────┐                             ┌───────────────────────────────┐
│   루트 에이전트   │       A2A 프로토콜              │ A2A로 노출된 헬로 월드 에이전트    │
│(RemoteA2aAgent)│────────────────────────────▶│      (localhost: 8001)        │
│(localhost:8000)│                             └───────────────────────────────┘
└────────────────┘
```

이 샘플은 다음으로 구성됩니다:

-   **원격 헬로 월드 에이전트** (`remote_a2a/hello_world/agent.py`): 다른 에이전트들이 A2A를 통해 사용할 수 있도록 노출하고자 하는 에이전트입니다. 주사위 굴리기와 소수 확인을 처리하는 에이전트입니다. `to_a2a()` 함수를 사용하여 노출되고 `uvicorn`을 통해 제공됩니다.
-   **루트 에이전트** (`agent.py`): 원격 헬로 월드 에이전트를 호출하기만 하는 간단한 에이전트입니다.

## `to_a2a(root_agent)` 함수로 원격 에이전트 노출하기

ADK를 사용하여 구축된 기존 에이전트를 `to_a2a()` 함수로 간단히 감싸서 A2A와 호환되도록 만들 수 있습니다. 예를 들어, `root_agent`에 다음과 같이 정의된 에이전트가 있다면:

```python
# 여기에 에이전트 코드
root_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world_agent',
    
    <...에이전트 코드...>
)
```

`to_a2a(root_agent)`를 사용하여 간단히 A2A 호환으로 만들 수 있습니다:

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# 에이전트를 A2A 호환으로 만들기
a2a_app = to_a2a(root_agent, port=8001)
```

`to_a2a()` 함수는 [ADK 에이전트에서 기술, 기능 및 메타데이터를 추출](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/utils/agent_card_builder.py)하여 배후에서 에이전트 카드를 인메모리(in-memory)로 자동 생성하기까지 합니다. 덕분에 에이전트 엔드포인트가 `uvicorn`으로 제공될 때 잘 알려진(well-known) 에이전트 카드를 사용할 수 있습니다.

`agent_card` 매개변수를 사용하여 자신만의 에이전트 카드를 제공할 수도 있습니다. 값은 `AgentCard` 객체이거나 에이전트 카드 JSON 파일의 경로일 수 있습니다.

**`AgentCard` 객체 예시:**
```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard

# A2A 에이전트 카드 정의
my_agent_card = AgentCard(
    name="file_agent",
    url="http://example.com",
    description="Test agent from file",
    version="1.0.0",
    capabilities={},
    skills=[],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    supportsAuthenticatedExtendedCard=False,
)
a2a_app = to_a2a(root_agent, port=8001, agent_card=my_agent_card)
```

**JSON 파일 경로 예시:**
```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# 파일에서 A2A 에이전트 카드 로드
a2a_app = to_a2a(root_agent, port=8001, agent_card="/path/to/your/agent-card.json")
```

이제 샘플 코드를 자세히 살펴보겠습니다.

### 1. 샘플 코드 받기 { #getting-the-sample-code }

먼저, 필요한 종속성이 설치되어 있는지 확인하세요:

```bash
pip install google-adk[a2a]
```

여기서 [**a2a_root** 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/a2a_root)을 복제하고 해당 디렉토리로 이동할 수 있습니다:

```bash
git clone https://github.com/google/adk-python.git
```

보시다시피, 폴더 구조는 다음과 같습니다:

```text
a2a_root/
├── remote_a2a/
│   └── hello_world/    
│       ├── __init__.py
│       └── agent.py    # 원격 헬로 월드 에이전트
├── README.md
└── agent.py            # 루트 에이전트
```

#### 루트 에이전트 (`a2a_root/agent.py`)

-   **`root_agent`**: 원격 A2A 서비스에 연결하는 `RemoteA2aAgent`
-   **에이전트 카드 URL**: 원격 서버의 잘 알려진(well-known) 에이전트 카드 엔드포인트를 가리킵니다.

#### 원격 헬로 월드 에이전트 (`a2a_root/remote_a2a/hello_world/agent.py`)

-   **`roll_die(sides: int)`**: 상태 관리가 포함된 주사위 굴리기용 함수 도구
-   **`check_prime(nums: list[int])`**: 소수 확인을 위한 비동기 함수
-   **`root_agent`**: 포괄적인 지침이 포함된 메인 에이전트
-   **`a2a_app`**: `to_a2a()` 유틸리티를 사용하여 생성된 A2A 애플리케이션

### 2. 원격 A2A 에이전트 서버 시작하기 { #start-the-remote-a2a-agent-server }

이제 원격 에이전트 서버를 시작할 수 있습니다. 이 서버는 hello_world 에이전트 내의 `a2a_app`을 호스팅합니다:

```bash
# 현재 작업 디렉토리가 adk-python/인지 확인
# uvicorn을 사용하여 원격 에이전트 시작
uvicorn contributing.samples.a2a_root.remote_a2a.hello_world.agent:a2a_app --host localhost --port 8001
```

??? note "왜 포트 8001을 사용하나요?"
    이 빠른 시작 가이드에서는 로컬에서 테스트할 때 에이전트들이 localhost를 사용하므로, 노출된 에이전트(원격 소수 에이전트)를 위한 A2A 서버의 `port`는 소비하는 에이전트의 포트와 달라야 합니다. 소비하는 에이전트와 상호 작용할 `adk web`의 기본 포트는 `8000`이므로, A2A 서버는 별도의 포트인 `8001`을 사용하여 생성됩니다.

실행되면 다음과 같은 메시지가 표시됩니다:

```shell
INFO:     Started server process [10615]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8001 (Press CTRL+C to quit)
```

### 3. 원격 에이전트가 실행 중인지 확인하기 { #check-that-your-remote-agent-is-running }

`a2a_root/remote_a2a/hello_world/agent.py`의 `to_a2a()` 함수 일부로 이전에 자동 생성된 에이전트 카드를 방문하여 에이전트가 실행 중인지 확인할 수 있습니다:

[http://localhost:8001/.well-known/agent-card.json](http://localhost:8001/.well-known/agent-card.json)

다음과 같은 에이전트 카드 내용을 볼 수 있어야 합니다:

```json
{"capabilities":{},"defaultInputModes":["text/plain"],"defaultOutputModes":["text/plain"],"description":"8면 주사위를 굴리고 소수를 확인할 수 있는 헬로 월드 에이전트.","name":"hello_world_agent","protocolVersion":"0.2.6","skills":[...],"supportsAuthenticatedExtendedCard":false,"url":"http://localhost:8001","version":"0.0.1"}
```

### 4. 메인 (소비) 에이전트 실행하기 { #run-the-main-consuming-agent }

이제 원격 에이전트가 실행 중이므로, 개발 UI를 시작하고 "a2a_root"를 에이전트로 선택할 수 있습니다.

```bash
# 별도의 터미널에서 adk 웹 서버 실행
adk web contributing/samples/
```

adk 웹 서버를 열려면 [http://localhost:8000](http://localhost:8000)으로 이동하세요.

## 상호 작용 예시

두 서비스가 모두 실행되면, 루트 에이전트와 상호 작용하여 A2A를 통해 원격 에이전트를 어떻게 호출하는지 확인할 수 있습니다:

**간단한 주사위 굴리기:**
이 상호 작용은 로컬 에이전트인 Roll Agent를 사용합니다:

```text
사용자: 6면 주사위를 굴려줘
봇: 4가 나왔습니다.
```

**소수 확인:**

이 상호 작용은 A2A를 통해 원격 에이전트인 Prime Agent를 사용합니다:

```text
사용자: 7은 소수야?
봇: 네, 7은 소수입니다.
```

**결합된 작업:**

이 상호 작용은 로컬 Roll Agent와 원격 Prime Agent를 모두 사용합니다:

```text
사용자: 10면 주사위를 굴리고 소수인지 확인해줘
봇: 8이 나왔습니다.
봇: 8은 소수가 아닙니다.
```

## 다음 단계

이제 A2A 서버를 통해 원격 에이전트를 노출하는 에이전트를 만들었으므로, 다음 단계는 다른 에이전트에서 이를 소비하는 방법을 배우는 것입니다.

-   [**A2A 빠른 시작 (소비편)**](./quickstart-consuming.md): A2A 프로토콜을 사용하여 에이전트가 다른 에이전트를 사용하는 방법을 배우세요.
