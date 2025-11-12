# 빠른 시작: A2A를 통해 원격 에이전트 사용하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-go">Go</span><span class="lst-preview">실험적 기능</span>
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

`a2a_basic` 예제에서는 먼저 로컬 루트 에이전트가 사용할 수 있도록 A2A 서버를 통해 `check_prime_agent`를 노출해야 합니다.

### 1. 샘플 코드 가져오기 { #getting-the-sample-code }

먼저 Go가 설치되어 있고 환경이 설정되어 있는지 확인하십시오.

여기에서 [**`a2a_basic`** 샘플](https://github.com/google/adk-docs/tree/main/examples/go/a2a_basic)로 복제하고 이동할 수 있습니다.

```bash
cd examples/go/a2a_basic
```

보시다시피 폴더 구조는 다음과 같습니다.

```text
a2a_basic/
├── remote_a2a/
│   └── check_prime_agent/
│       └── main.go
├── go.mod
├── go.sum
└── main.go # 로컬 루트 에이전트
```

#### 기본 에이전트 (`a2a_basic/main.go`)

- **`rollDieTool`**: 주사위 굴리기를 위한 함수 도구
- **`newRollAgent`**: 주사위 굴리기에 특화된 로컬 에이전트
- **`newPrimeAgent`**: 원격 A2A 에이전트 구성
- **`newRootAgent`**: 위임 로직이 있는 기본 오케스트레이터

#### 원격 프라임 에이전트 (`a2a_basic/remote_a2a/check_prime_agent/main.go`)

- **`checkPrimeTool`**: 소수 확인 알고리즘
- **`main`**: 소수 확인 서비스 및 A2A 서버 구현

### 2. 원격 프라임 에이전트 서버 시작 { #start-the-remote-prime-agent-server }

ADK 에이전트가 A2A를 통해 원격 에이전트를 사용하는 방법을 보여주려면 먼저 프라임 에이전트(`check_prime_agent` 아래)를 호스팅할 원격 에이전트 서버를 시작해야 합니다.

```bash
# 포트 8001에서 check_prime_agent를 제공하는 원격 a2a 서버 시작
go run remote_a2a/check_prime_agent/main.go
```

실행되면 다음과 같은 내용이 표시됩니다.

``` shell
2025/11/06 11:00:19 Starting A2A prime checker server on port 8001
2025/11/06 11:00:19 Starting the web server: &{port:8001}
2025/11/06 11:00:19 
2025/11/06 11:00:19 Web servers starts on http://localhost:8001
2025/11/06 11:00:19        a2a:  you can access A2A using jsonrpc protocol: http://localhost:8001
```
  
### 3. 원격 에이전트의 필수 에이전트 카드 확인 { #look-out-for-the-required-agent-card-of-the-remote-agent }

A2A 프로토콜에서는 각 에이전트가 수행하는 작업을 설명하는 에이전트 카드를 가지고 있어야 합니다.

Go ADK에서는 A2A 시작 프로그램을 사용하여 에이전트를 노출할 때 에이전트 카드가 동적으로 생성됩니다. `http://localhost:8001/.well-known/agent-card.json`을 방문하여 생성된 카드를 볼 수 있습니다.

### 4. 기본(소비) 에이전트 실행 { #run-the-main-consuming-agent }

  ```bash
  # 별도의 터미널에서 기본 에이전트 실행
  go run main.go
  ```

#### 작동 방식

기본 에이전트는 `remoteagent.New`를 사용하여 원격 에이전트(이 예에서는 `prime_agent`)를 사용합니다. 아래에서 볼 수 있듯이 `Name`, `Description` 및 `AgentCardSource` URL이 필요합니다.

```go title="a2a_basic/main.go"
--8<-- "examples/go/a2a_basic/main.go:new-prime-agent"
```

그런 다음 루트 에이전트에서 원격 에이전트를 간단히 사용할 수 있습니다. 이 경우 `primeAgent`는 아래 `root_agent`의 하위 에이전트 중 하나로 사용됩니다.

```go title="a2a_basic/main.go"
--8<-- "examples/go/a2a_basic/main.go:new-root-agent"
```

## 상호 작용 예

기본 에이전트와 원격 에이전트가 모두 실행되면 루트 에이전트와 상호 작용하여 A2A를 통해 원격 에이전트를 호출하는 방법을 확인할 수 있습니다.

**간단한 주사위 굴리기:**
이 상호 작용은 로컬 에이전트인 롤 에이전트를 사용합니다.

```text
사용자: 6면체 주사위를 굴려주세요
봇이 도구 호출: transfer_to_agent, 인수: map[agent_name:roll_agent]
봇이 도구 호출: roll_die, 인수: map[sides:6]
봇: 6면체 주사위를 굴렸고 결과는 6입니다.
```

**소수 확인:**

이 상호 작용은 A2A를 통해 원격 에이전트인 프라임 에이전트를 사용합니다.

```text
사용자: 7은 소수인가요?
봇이 도구 호출: transfer_to_agent, 인수: map[agent_name:prime_agent]
봇이 도구 호출: prime_checking, 인수: map[nums:[7]]
봇: 예, 7은 소수입니다.
```

**결합된 작업:**

이 상호 작용은 로컬 롤 에이전트와 원격 프라임 에이전트를 모두 사용합니다.

```text
사용자: 주사위를 굴려서 소수인지 확인해주세요
봇: 알겠습니다. 먼저 주사위를 굴린 다음 결과가 소수인지 확인하겠습니다.

봇이 도구 호출: transfer_to_agent, 인수: map[agent_name:roll_agent]
봇이 도구 호출: roll_die, 인수: map[sides:6]
봇이 도구 호출: transfer_to_agent, 인수: map[agent_name:prime_agent]
봇이 도구 호출: prime_checking, 인수: map[nums:[3]]
봇: 3은 소수입니다.
```

## 다음 단계

이제 A2A 서버를 통해 원격 에이전트를 사용하는 에이전트를 만들었으므로 다음 단계는 자신의 에이전트를 노출하는 방법을 배우는 것입니다.

- [**A2A 빠른 시작(노출)**](./quickstart-exposing-go.md): 다른 에이전트가 A2A 프로토콜을 통해 기존 에이전트를 사용할 수 있도록 노출하는 방법을 배웁니다.
