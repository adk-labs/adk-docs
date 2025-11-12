# 빠른 시작: A2A를 통해 원격 에이전트 노출하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-preview">실험적 기능</span>
</div>

이 빠른 시작은 모든 개발자에게 가장 일반적인 시작 지점인 **"에이전트가 있습니다. 다른 에이전트가 A2A를 통해 내 에이전트를 사용할 수 있도록 노출하려면 어떻게 해야 하나요?"**에 대해 다룹니다. 이는 서로 다른 에이전트가 협력하고 상호 작용해야 하는 복잡한 다중 에이전트 시스템을 구축하는 데 중요합니다.

## 개요

이 샘플은 ADK 에이전트를 쉽게 노출하여 A2A 프로토콜을 사용하여 다른 에이전트에서 사용할 수 있도록 하는 방법을 보여줍니다.

ADK 에이전트를 A2A를 통해 노출하는 두 가지 주요 방법이 있습니다.

* **`to_a2a(root_agent)` 함수 사용**: `adk deploy api_server` 대신 `uvicorn`을 통해 서버를 통해 노출할 수 있도록 기존 에이전트를 A2A와 함께 작동하도록 변환하려는 경우 이 함수를 사용합니다. 즉, 에이전트를 프로덕션화할 때 `uvicorn`을 통해 노출하려는 항목을 더 엄격하게 제어할 수 있습니다. 또한 `to_a2a()` 함수는 에이전트 코드를 기반으로 에이전트 카드를 자동으로 생성합니다.
* **자신만의 에이전트 카드(`agent.json`)를 만들고 `adk api_server --a2a`를 사용하여 호스팅**: 이 접근 방식에는 두 가지 주요 이점이 있습니다. 첫째, `adk api_server --a2a`는 `adk web`과 함께 작동하여 에이전트를 쉽게 사용, 디버그 및 테스트할 수 있습니다. 둘째, `adk api_server`를 사용하면 여러 개의 개별 에이전트가 있는 상위 폴더를 지정할 수 있습니다. 에이전트 카드(`agent.json`)가 있는 에이전트는 동일한 서버를 통해 다른 에이전트가 A2A를 통해 자동으로 사용할 수 있게 됩니다. 그러나 자신만의 에이전트 카드를 만들어야 합니다. 에이전트 카드를 만들려면 [A2A Python 자습서](https://a2a-protocol.org/latest/tutorials/python/1-introduction/)를 따를 수 있습니다.

이 빠른 시작은 에이전트를 노출하는 가장 쉬운 방법이며 백그라운드에서 에이전트 카드를 자동으로 생성하므로 `to_a2a()`에 중점을 둡니다. `adk api_server` 접근 방식을 사용하려면 [A2A 빠른 시작(소비) 설명서](quickstart-consuming.md)에서 사용되는 것을 볼 수 있습니다.

이전:
                                                ┌────────────────────┐
                                                │ Hello World 에이전트  │
                                                │  (Python 객체)   │
                                                | 에이전트 카드 없음 │
                                                └────────────────────┘

                                                          │
                                                          │ to_a2a()
                                                          ▼

이후:
┌────────────────┐                             ┌───────────────────────────────┐
│   루트 에이전트 │       A2A 프로토콜          │ A2A 노출된 Hello World 에이전트 │
│(RemoteA2aAgent)│────────────────────────────▶│      (localhost: 8001)         │
│(localhost:8000)│                             └───────────────────────────────┘
└────────────────┘

이 샘플은 다음으로 구성됩니다.

- **원격 Hello World 에이전트** (`remote_a2a/hello_world/agent.py`): 다른 에이전트가 A2A를 통해 사용할 수 있도록 노출하려는 에이전트입니다. 주사위 굴리기 및 소수 확인을 처리하는 에이전트입니다. `to_a2a()` 함수를 사용하여 노출되고 `uvicorn`을 사용하여 제공됩니다.
- **루트 에이전트** (`agent.py`): 원격 Hello World 에이전트를 호출하는 간단한 에이전트입니다.

## `to_a2a(root_agent)` 함수로 원격 에이전트 노출

ADK를 사용하여 빌드된 기존 에이전트를 가져와 `to_a2a()` 함수를 사용하여 래핑하기만 하면 A2A와 호환되도록 만들 수 있습니다. 예를 들어 `root_agent`에 다음과 같이 정의된 에이전트가 있는 경우:

```python
# 여기에 에이전트 코드
root_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world_agent',
    
    <...your agent code...>
)
```

그런 다음 `to_a2a(root_agent)`를 사용하여 간단하게 A2A와 호환되도록 만들 수 있습니다.

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# 에이전트를 A2A와 호환되도록 만들기
a2a_app = to_a2a(root_agent, port=8001)
```

`to_a2a()` 함수는 [ADK 에이전트에서 기술, 기능 및 메타데이터를 추출](https://github.com/google/adk-python/blob/main/src/google/adk/a2a/utils/agent_card_builder.py)하여 백그라운드에서 메모리 내 에이전트 카드를 자동으로 생성하므로 `uvicorn`을 사용하여 에이전트 엔드포인트가 제공될 때 잘 알려진 에이전트 카드를 사용할 수 있습니다.

`agent_card` 매개변수를 사용하여 자신만의 에이전트 카드를 제공할 수도 있습니다. 값은 `AgentCard` 객체 또는 에이전트 카드 JSON 파일의 경로일 수 있습니다.

**`AgentCard` 객체 예:**
```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard

# A2A 에이전트 카드 정의
my_agent_card = AgentCard(
    "name": "file_agent",
    "url": "http://example.com",
    "description": "Test agent from file",
    "version": "1.0.0",
    "capabilities": {},
    "skills": [],
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "supportsAuthenticatedExtendedCard": False,
)
a2a_app = to_a2a(root_agent, port=8001, agent_card=my_agent_card)
```

**JSON 파일 경로 예:**
```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# 파일에서 A2A 에이전트 카드 로드
a2a_app = to_a2a(root_agent, port=8001, agent_card="/path/to/your/agent-card.json")
```

이제 샘플 코드를 살펴보겠습니다.

### 1. 샘플 코드 가져오기 { #getting-the-sample-code }

먼저 필요한 종속성이 설치되어 있는지 확인하십시오.

```bash
pip install google-adk[a2a]
```

여기에서 [**a2a_root** 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/a2a_root)로 복제하고 이동할 수 있습니다.

```bash
git clone https://github.com/google/adk-python.git
```

보시다시피 폴더 구조는 다음과 같습니다.

```text
a2a_root/
├── remote_a2a/
│   └── hello_world/    
│       ├── __init__.py
│       └── agent.py    # 원격 Hello World 에이전트
├── README.md
└── agent.py            # 루트 에이전트
```

#### 루트 에이전트 (`a2a_root/agent.py`)

- **`root_agent`**: 원격 A2A 서비스에 연결하는 `RemoteA2aAgent`
- **에이전트 카드 URL**: 원격 서버의 잘 알려진 에이전트 카드 엔드포인트를 가리킵니다.

#### 원격 Hello World 에이전트 (`a2a_root/remote_a2a/hello_world/agent.py`)

- **`roll_die(sides: int)`**: 상태 관리를 통한 주사위 굴리기를 위한 함수 도구
- **`check_prime(nums: list[int])`**: 소수 확인을 위한 비동기 함수
- **`root_agent`**: 포괄적인 지침이 있는 기본 에이전트
- **`a2a_app`**: `to_a2a()` 유틸리티를 사용하여 만든 A2A 애플리케이션

### 2. 원격 A2A 에이전트 서버 시작 { #start-the-remote-a2a-agent-server }

이제 hello_world 에이전트 내에서 `a2a_app`을 호스팅할 원격 에이전트 서버를 시작할 수 있습니다.

```bash
# 현재 작업 디렉터리가 adk-python/인지 확인
# uvicorn을 사용하여 원격 에이전트 시작
uvicorn contributing.samples.a2a_root.remote_a2a.hello_world.agent:a2a_app --host localhost --port 8001
```

??? note "왜 포트 8001을 사용하나요?"
    이 빠른 시작에서는 로컬에서 테스트할 때 에이전트가 localhost를 사용하므로 노출된 에이전트(원격 프라임 에이전트)의 A2A 서버 포트는 소비 에이전트의 포트와 달라야 합니다. 소비 에이전트와 상호 작용할 `adk web`의 기본 포트는 `8000`이므로 A2A 서버는 별도의 포트인 `8001`을 사용하여 생성됩니다.

실행되면 다음과 같은 내용이 표시됩니다.

```shell
INFO:     Started server process [10615]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8001 (Press CTRL+C to quit)
```

### 3. 원격 에이전트가 실행 중인지 확인 { #check-that-your-remote-agent-is-running }

`a2a_root/remote_a2a/hello_world/agent.py`의 `to_a2a()` 함수의 일부로 이전에 자동 생성된 에이전트 카드를 방문하여 에이전트가 실행 중인지 확인할 수 있습니다.

[http://localhost:8001/.well-known/agent-card.json](http://localhost:8001/.well-known/agent-card.json)

에이전트 카드의 내용이 표시되어야 하며 다음과 같아야 합니다.

```json
{"capabilities":{},"defaultInputModes":["text/plain"],"defaultOutputModes":["text/plain"],"description":"hello world agent that can roll a dice of 8 sides and check prime numbers. ","name":"hello_world_agent","protocolVersion":"0.2.6","skills":[{"description":"hello world agent that can roll a dice of 8 sides and check prime numbers. 
      I roll dice and answer questions about the outcome of the dice rolls.
      I can roll dice of different sizes.
      I can use multiple tools in parallel by calling functions in parallel(in one request and in one round).
      It is ok to discuss previous dice roles, and comment on the dice rolls.
      When I are asked to roll a die, I must call the roll_die tool with the number of sides. Be sure to pass in an integer. Do not pass in a string.
      I should never roll a die on my own.
      When checking prime numbers, call the check_prime tool with a list of integers. Be sure to pass in a list of integers. I should never pass in a string.
      I should not check prime numbers before calling the tool.
      When I are asked to roll a die and check prime numbers, I should always make the following two function calls:
      1. I should first call the roll_die tool to get a roll. Wait for the function response before calling the check_prime tool.
      2. After I get the function response from roll_die tool, I should call the check_prime tool with the roll_die result.
        2.1 If user asks I to check primes based on previous rolls, make sure I include the previous rolls in the list.
      3. When I respond, I must include the roll_die result from step 1.
      I should always perform the previous 3 steps when asking for a roll and checking prime numbers.
      I should not rely on the previous history on prime results.
    ","id":"hello_world_agent","name":"model","tags":["llm"]},{"description":"Roll a die and return the rolled result.\n\nArgs:\n  sides: The integer number of sides the die has.\n  tool_context:... [truncated]
```

### 4. 기본(소비) 에이전트 실행 { #run-the-main-consuming-agent }

이제 원격 에이전트가 실행 중이므로 개발 UI를 시작하고 "a2a_root"를 에이전트로 선택할 수 있습니다.

```bash
# 별도의 터미널에서 adk 웹 서버 실행
adk web contributing/samples/
```

adk 웹 서버를 열려면 [http://localhost:8000](http://localhost:8000)으로 이동하십시오.

## 상호 작용 예

두 서비스가 모두 실행되면 루트 에이전트와 상호 작용하여 A2A를 통해 원격 에이전트를 호출하는 방법을 확인할 수 있습니다.

**간단한 주사위 굴리기:**
이 상호 작용은 로컬 에이전트인 롤 에이전트를 사용합니다.

```text
사용자: 6면체 주사위를 굴려주세요
봇: 4를 굴렸습니다.
```

**소수 확인:**

이 상호 작용은 A2A를 통해 원격 에이전트인 프라임 에이전트를 사용합니다.

```text
사용자: 7은 소수인가요?
봇: 예, 7은 소수입니다.
```

**결합된 작업:**

이 상호 작용은 로컬 롤 에이전트와 원격 프라임 에이전트를 모두 사용합니다.

```text
사용자: 10면체 주사위를 굴려서 소수인지 확인해주세요
봇: 8을 굴렸습니다.
봇: 8은 소수가 아닙니다.
```

## 다음 단계

이제 A2A 서버를 통해 원격 에이전트를 노출하는 에이전트를 만들었으므로 다음 단계는 다른 에이전트에서 이를 사용하는 방법을 배우는 것입니다.

- [**A2A 빠른 시작(소비)**](./quickstart-consuming.md): 에이전트가 A2A 프로토콜을 사용하여 다른 에이전트를 사용하는 방법을 배웁니다.
