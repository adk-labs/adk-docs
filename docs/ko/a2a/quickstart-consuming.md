# 빠른 시작: A2A를 통해 원격 에이전트 사용하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-preview">실험적 기능</span>
</div>

이 빠른 시작은 모든 개발자에게 가장 일반적인 시작 지점인 **"원격 에이전트가 있는데, 내 ADK 에이전트가 A2A를 통해 이를 사용하게 하려면 어떻게 해야 하나요?"**에 대해 다룹니다. 이는 서로 다른 에이전트가 협력하고 상호 작용해야 하는 복잡한 다중 에이전트 시스템을 구축하는 데 중요합니다.

## 개요

이 샘플은 에이전트 개발 키트(ADK)의 **에이전트 대 에이전트(A2A)** 아키텍처를 시연하며, 여러 에이전트가 함께 작동하여 복잡한 작업을 처리하는 방법을 보여줍니다. 이 샘플은 주사위를 굴리고 숫자가 소수인지 확인할 수 있는 에이전트를 구현합니다.

```text
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   루트 에이전트 │───▶│   롤 에이전트    │    │   원격 프라임      │
│  (로컬)         │    │   (로컬)         │    │   에이전트         │
│                 │    │                  │    │  (localhost:8001)  │
│                 │───▶│                  │◀───│                    │
└─────────────────┘    └──────────────────┘    └────────────────────┘
```

A2A 기본 샘플은 다음으로 구성됩니다.

- **루트 에이전트** (`root_agent`): 전문화된 하위 에이전트에 작업을 위임하는 기본 오케스트레이터
- **롤 에이전트** (`roll_agent`): 주사위 굴리기 작업을 처리하는 로컬 하위 에이전트
- **프라임 에이전트** (`prime_agent`): 숫자가 소수인지 확인하는 원격 A2A 에이전트, 이 에이전트는 별도의 A2A 서버에서 실행됩니다.

## ADK 서버로 에이전트 노출

ADK에는 에이전트를 A2A 프로토콜을 사용하여 노출하는 내장 CLI 명령인 `adk api_server --a2a`가 함께 제공됩니다.

`a2a_basic` 예제에서는 먼저 로컬 루트 에이전트가 사용할 수 있도록 A2A 서버를 통해 `check_prime_agent`를 노출해야 합니다.

### 1. 샘플 코드 가져오기 { #getting-the-sample-code }

먼저 필요한 종속성이 설치되어 있는지 확인하십시오.

```bash
pip install google-adk[a2a]
```

여기에서 [**`a2a_basic`** 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/a2a_basic)로 복제하고 이동할 수 있습니다.

```bash
git clone https://github.com/google/adk-python.git
```

보시다시피 폴더 구조는 다음과 같습니다.

```text
a2a_basic/
├── remote_a2a/
│   └── check_prime_agent/
│       ├── __init__.py
│       ├── agent.json
│       └── agent.py
├── README.md
├── __init__.py
└── agent.py # 로컬 루트 에이전트
```

#### 기본 에이전트 (`a2a_basic/agent.py`)

- **`roll_die(sides: int)`**: 주사위 굴리기를 위한 함수 도구
- **`roll_agent`**: 주사위 굴리기에 특화된 로컬 에이전트
- **`prime_agent`**: 원격 A2A 에이전트 구성
- **`root_agent`**: 위임 로직이 있는 기본 오케스트레이터

#### 원격 프라임 에이전트 (`a2a_basic/remote_a2a/check_prime_agent/`)

- **`agent.py`**: 소수 확인 서비스 구현
- **`agent.json`**: A2A 에이전트의 에이전트 카드
- **`check_prime(nums: list[int])`**: 소수 확인 알고리즘

### 2. 원격 프라임 에이전트 서버 시작 { #start-the-remote-prime-agent-server }

ADK 에이전트가 A2A를 통해 원격 에이전트를 사용하는 방법을 보여주려면 먼저 프라임 에이전트(`check_prime_agent` 아래)를 호스팅할 원격 에이전트 서버를 시작해야 합니다.

```bash
# 포트 8001에서 check_prime_agent를 제공하는 원격 a2a 서버 시작
adk api_server --a2a --port 8001 contributing/samples/a2a_basic/remote_a2a
```

??? note "디버깅을 위한 로깅 추가 `--log_level debug`"
    디버그 수준 로깅을 활성화하려면 `adk api_server`에 `--log_level debug`를 추가하면 됩니다.
    ```bash
    adk api_server --a2a --port 8001 contributing/samples/a2a_basic/remote_a2a --log_level debug
    ```
    이렇게 하면 에이전트를 테스트할 때 검사할 수 있는 더 풍부한 로그가 제공됩니다.

??? note "왜 포트 8001을 사용하나요?"
    이 빠른 시작에서는 로컬에서 테스트할 때 에이전트가 localhost를 사용하므로 노출된 에이전트(원격 프라임 에이전트)의 A2A 서버 포트는 소비 에이전트의 포트와 달라야 합니다. 소비 에이전트와 상호 작용할 `adk web`의 기본 포트는 `8000`이므로 A2A 서버는 별도의 포트인 `8001`을 사용하여 생성됩니다.

실행되면 다음과 같은 내용이 표시됩니다.

``` shell
INFO:     Started server process [56558]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
```
  
### 3. 원격 에이전트의 필수 에이전트 카드(`agent-card.json`) 확인 { #look-out-for-the-required-agent-card-agent-json-of-the-remote-agent }

A2A 프로토콜에서는 각 에이전트가 수행하는 작업을 설명하는 에이전트 카드를 가지고 있어야 합니다.

다른 사람이 이미 에이전트에서 사용하려는 원격 A2A 에이전트를 빌드했다면 해당 에이전트 카드(`agent-card.json`)가 있는지 확인해야 합니다.

샘플에서 `check_prime_agent`에는 이미 제공된 에이전트 카드가 있습니다.

```json title="a2a_basic/remote_a2a/check_prime_agent/agent-card.json"

{
  "capabilities": {},
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["application/json"],
  "description": "An agent specialized in checking whether numbers are prime. It can efficiently determine the primality of individual numbers or lists of numbers.",
  "name": "check_prime_agent",
  "skills": [
    {
      "id": "prime_checking",
      "name": "Prime Number Checking",
      "description": "Check if numbers in a list are prime using efficient mathematical algorithms",
      "tags": ["mathematical", "computation", "prime", "numbers"]
    }
  ],
  "url": "http://localhost:8001/a2a/check_prime_agent",
  "version": "1.0.0"
}
```

??? note "ADK의 에이전트 카드에 대한 추가 정보"

    ADK에서는 `to_a2a(root_agent)` 래퍼를 사용하여 에이전트 카드를 자동으로 생성할 수 있습니다. 다른 사람이 사용할 수 있도록 기존 에이전트를 노출하는 방법에 대해 자세히 알아보려면 [A2A 빠른 시작(노출)](quickstart-exposing.md) 자습서를 참조하십시오.

### 4. 기본(소비) 에이전트 실행 { #run-the-main-consuming-agent }

  ```bash
  # 별도의 터미널에서 adk 웹 서버 실행
  adk web contributing/samples/
  ```

#### 작동 방식

기본 에이전트는 `RemoteA2aAgent()` 함수를 사용하여 원격 에이전트(이 예에서는 `prime_agent`)를 사용합니다. 아래에서 볼 수 있듯이 `RemoteA2aAgent()`에는 `name`, `description` 및 `agent_card`의 URL이 필요합니다.

```python title="a2a_basic/agent.py"
<...code truncated...>

from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

prime_agent = RemoteA2aAgent(
    name="prime_agent",
    description="Agent that handles checking if numbers are prime.",
    agent_card=(
        f"http://localhost:8001/a2a/check_prime_agent{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)

<...code truncated>
```

그런 다음 에이전트에서 `RemoteA2aAgent`를 간단히 사용할 수 있습니다. 이 경우 `prime_agent`는 아래 `root_agent`의 하위 에이전트 중 하나로 사용됩니다.

```python title="a2a_basic/agent.py"
from google.adk.agents.llm_agent import Agent
from google.genai import types

root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    instruction="""
      <You are a helpful assistant that can roll dice and check if numbers are prime.
      You delegate rolling dice tasks to the roll_agent and prime checking tasks to the prime_agent.
      Follow these steps:
      1. If the user asks to roll a die, delegate to the roll_agent.
      2. If the user asks to check primes, delegate to the prime_agent.
      3. If the user asks to roll a die and then check if the result is prime, call roll_agent first, then pass the result to prime_agent.
      Always clarify the results before proceeding.>
    """,
    global_instruction=(
        "You are DicePrimeBot, ready to roll dice and check prime numbers."
    ),
    sub_agents=[roll_agent, prime_agent],
    tools=[example_tool],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # avoid false alarm about rolling dice.
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
```

## 상호 작용 예

기본 에이전트와 원격 에이전트가 모두 실행되면 루트 에이전트와 상호 작용하여 A2A를 통해 원격 에이전트를 호출하는 방법을 확인할 수 있습니다.

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

이제 A2A 서버를 통해 원격 에이전트를 사용하는 에이전트를 만들었으므로 다음 단계는 다른 에이전트에서 연결하는 방법을 배우는 것입니다.

- [**A2A 빠른 시작(노출)**](./quickstart-exposing.md): 다른 에이전트가 A2A 프로토콜을 통해 기존 에이전트를 사용할 수 있도록 노출하는 방법을 배웁니다.
