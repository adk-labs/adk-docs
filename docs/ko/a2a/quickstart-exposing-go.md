# 빠른 시작: A2A를 통해 원격 에이전트 노출하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-go">Go</span><span class="lst-preview">실험적 기능</span>
</div>

이 빠른 시작은 모든 개발자에게 가장 일반적인 시작 지점인 **"에이전트가 있습니다. 다른 에이전트가 A2A를 통해 내 에이전트를 사용할 수 있도록 노출하려면 어떻게 해야 하나요?"**에 대해 다룹니다. 이는 서로 다른 에이전트가 협력하고 상호 작용해야 하는 복잡한 다중 에이전트 시스템을 구축하는 데 중요합니다.

## 개요

이 샘플은 ADK 에이전트를 쉽게 노출하여 A2A 프로토콜을 사용하여 다른 에이전트에서 사용할 수 있도록 하는 방법을 보여줍니다.

Go에서는 A2A 시작 프로그램을 사용하여 에이전트를 노출하며, 이 프로그램은 에이전트 카드를 동적으로 생성합니다.

```text
┌─────────────────┐                             ┌───────────────────────────────┐
│   루트 에이전트 │       A2A 프로토콜          │ A2A 노출된 소수 확인 에이전트 │
│                 │────────────────────────────▶│      (localhost: 8001)        │
└─────────────────┘                             └───────────────────────────────┘
```

이 샘플은 다음으로 구성됩니다.

- **원격 프라임 에이전트** (`remote_a2a/check_prime_agent/main.go`): 다른 에이전트가 A2A를 통해 사용할 수 있도록 노출하려는 에이전트입니다. 소수 확인을 처리하는 에이전트입니다. A2A 시작 프로그램을 사용하여 노출됩니다.
- **루트 에이전트** (`main.go`): 원격 프라임 에이전트를 호출하는 간단한 에이전트입니다.

## A2A 시작 프로그램으로 원격 에이전트 노출

Go ADK를 사용하여 빌드된 기존 에이전트를 가져와 A2A 시작 프로그램을 사용하여 A2A와 호환되도록 만들 수 있습니다.

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
│       └── main.go    # 원격 프라임 에이전트
├── go.mod
├── go.sum
└── main.go            # 루트 에이전트
```

#### 루트 에이전트 (`a2a_basic/main.go`)

- **`newRootAgent`**: 원격 A2A 서비스에 연결하는 로컬 에이전트입니다.

#### 원격 프라임 에이전트 (`a2a_basic/remote_a2a/check_prime_agent/main.go`)

- **`checkPrimeTool`**: 소수 확인을 위한 함수입니다.
- **`main`**: 에이전트를 생성하고 A2A 서버를 시작하는 기본 함수입니다.

### 2. 원격 A2A 에이전트 서버 시작 { #start-the-remote-a2a-agent-server }

이제 `check_prime_agent`를 호스팅할 원격 에이전트 서버를 시작할 수 있습니다.

```bash
# 원격 에이전트 시작
go run remote_a2a/check_prime_agent/main.go
```

실행되면 다음과 같은 내용이 표시됩니다.

```shell
2025/11/06 11:00:19 Starting A2A prime checker server on port 8001
2025/11/06 11:00:19 Starting the web server: &{port:8001}
2025/11/06 11:00:19 
2025/11/06 11:00:19 Web servers starts on http://localhost:8001
2025/11/06 11:00:19        a2a:  you can access A2A using jsonrpc protocol: http://localhost:8001
```

### 3. 원격 에이전트가 실행 중인지 확인 { #check-that-your-remote-agent-is-running }

A2A 시작 프로그램에서 자동으로 생성된 에이전트 카드를 방문하여 에이전트가 실행 중인지 확인할 수 있습니다.

[http://localhost:8001/.well-known/agent-card.json](http://localhost:8001/.well-known/agent-card.json)

에이전트 카드의 내용을 볼 수 있습니다.

### 4. 기본(소비) 에이전트 실행 { #run-the-main-consuming-agent }

이제 원격 에이전트가 실행 중이므로 기본 에이전트를 실행할 수 있습니다.

```bash
# 별도의 터미널에서 기본 에이전트 실행
go run main.go
```

#### 작동 방식

원격 에이전트는 `main` 함수의 A2A 시작 프로그램을 사용하여 노출됩니다. 시작 프로그램은 서버를 시작하고 에이전트 카드를 생성하는 작업을 처리합니다.

```go title="remote_a2a/check_prime_agent/main.go"
--8<-- "examples/go/a2a_basic/remote_a2a/check_prime_agent/main.go:a2a-launcher"
```

## 상호 작용 예

두 서비스가 모두 실행되면 루트 에이전트와 상호 작용하여 A2A를 통해 원격 에이전트를 호출하는 방법을 확인할 수 있습니다.

**소수 확인:**

이 상호 작용은 A2A를 통해 원격 에이전트인 프라임 에이전트를 사용합니다.

```text
사용자: 주사위를 굴려서 소수인지 확인해주세요
봇: 알겠습니다. 먼저 주사위를 굴린 다음 결과가 소수인지 확인하겠습니다.

봇이 도구 호출: transfer_to_agent, 인수: map[agent_name:roll_agent]
봇이 도구 호출: roll_die, 인수: map[sides:6]
봇이 도구 호출: transfer_to_agent, 인수: map[agent_name:prime_agent]
봇이 도구 호출: prime_checking, 인수: map[nums:[3]]
봇: 3은 소수입니다.
...
```

## 다음 단계

이제 A2A 서버를 통해 원격 에이전트를 노출하는 에이전트를 만들었으므로 다음 단계는 다른 에이전트에서 이를 사용하는 방법을 배우는 것입니다.

- [**A2A 빠른 시작(소비)**](./quickstart-consuming-go.md): 에이전트가 A2A 프로토콜을 사용하여 다른 에이전트를 사용하는 방법을 배웁니다.
