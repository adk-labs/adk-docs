# 명령줄 사용

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK는 에이전트를 테스트하기 위한 대화형 터미널 인터페이스를 제공합니다. 이는 빠른 테스트, 스크립트 기반 상호작용, CI/CD 파이프라인에 유용합니다.

![ADK Run](../assets/adk-run.png)

## 에이전트 실행

다음 명령으로 ADK 명령줄 인터페이스에서 에이전트를 실행합니다:

=== "Python"

    ```shell
    adk run my_agent
    ```

=== "TypeScript"

    ```shell
    npx @google/adk-devtools run agent.ts
    ```

=== "Go"

    Go에서 명령줄 인터페이스는 독립형 `adk` 도구가 아닙니다. 대신 에이전트의 `main.go`에 론처를 직접 포함합니다. `full.NewLauncher()` 헬퍼는 콘솔, 웹 서버 및 기타 모드를 단일 바이너리로 묶으며, 하위 명령 키워드가 제공되지 않는 경우 **콘솔이 기본값**으로 설정됩니다:

    ```go title="main.go"
    import (
        "google.golang.org/adk/v2/cmd/launcher"
        "google.golang.org/adk/v2/cmd/launcher/full"
    )

    func main() {
        // ... 에이전트 및 구성 빌드 ...
        l := full.NewLauncher()
        if err := l.Execute(ctx, config, os.Args[1:]); err != nil {
            log.Fatalf("Run failed: %v\n\n%s", err, l.CommandLineSyntax())
        }
    }
    ```

    다음 명령 중 하나를 사용하여 콘솔 모드로 에이전트를 실행합니다:

    ```shell
    go run agent.go           # 콘솔이 기본 하위 론처입니다
    go run agent.go console   # 또는 console 하위 명령을 명시적으로 지정합니다
    ```

=== "Java"

    `AgentCliRunner` 클래스를 만들고([Java 빠른 시작](../get-started/java.md) 참고) 다음을 실행합니다:

    ```shell
    mvn compile exec:java -Dexec.mainClass="com.example.agent.AgentCliRunner"
    ```

그러면 질의를 입력하고 터미널에서 에이전트 응답을 직접 확인할 수 있는 대화형 세션이 시작됩니다:

=== "Python"

    ```shell
    Running agent my_agent, type exit to exit.
    [user]: What's the weather in New York?
    [my_agent]: The weather in New York is sunny with a temperature of 25°C.
    [user]: exit
    ```

=== "TypeScript"

    ```shell
    Running agent my_agent, type exit to exit.
    [user]: What's the weather in New York?
    [my_agent]: The weather in New York is sunny with a temperature of 25°C.
    [user]: exit
    ```

=== "Go"

    ```shell
    User -> What's the weather in New York?

    Agent -> The weather in New York is sunny with a temperature of 25°C.

    User ->
    ```

    종료하려면 **Ctrl+C**를 누르거나 EOF(**Ctrl+D**)를 전송합니다.

=== "Java"

    ```shell
    Running agent my_agent, type exit to exit.
    [user]: What's the weather in New York?
    [my_agent]: The weather in New York is sunny with a temperature of 25°C.
    [user]: exit
    ```

## 세션 옵션

!!! note "Python 전용"

    `--save_session`, `--resume`, `--replay`, `--session_id` 옵션은 Python ADK CLI에서만 사용할 수 있습니다. Go 콘솔 론처는 명령줄 플래그를 통한 세션 저장/재개/재생을 지원하지 않습니다. Go에서는 `launcher.Config`에 영구적인 `session.Service` 구현(예: `session/database`)을 제공하여 코드 내에서 세션 지속성을 구성합니다.

`adk run` 명령에는 세션 저장, 재개, 재생을 위한 옵션이 있습니다.

### 세션 저장

종료 시 세션을 저장하려면:

```shell
adk run --save_session path/to/my_agent
```

세션 ID 입력을 요청받으며, 세션은 `path/to/my_agent/<session_id>.session.json`에 저장됩니다.

세션 ID를 미리 지정할 수도 있습니다:

```shell
adk run --save_session --session_id my_session path/to/my_agent
```

### 세션 재개

이전에 저장한 세션을 이어서 진행하려면:

```shell
adk run --resume path/to/my_agent/my_session.session.json path/to/my_agent
```

이 명령은 이전 세션 상태와 이벤트 히스토리를 불러와 표시한 뒤, 대화를 계속할 수 있게 합니다.

### 세션 재생

대화형 입력 없이 세션 파일을 재생하려면:

```shell
adk run --replay path/to/input.json path/to/my_agent
```

입력 파일에는 초기 상태와 질의가 포함되어야 합니다:

```json
{
  "state": {"key": "value"},
  "queries": ["What is 2 + 2?", "What is the capital of France?"]
}
```

## 스토리지 옵션

!!! note "Python 전용"

    `--session_service_uri` 및 `--artifact_service_uri` 명령줄 플래그는 Python ADK CLI에서만 사용할 수 있습니다. Go에서는 `launcher.Config`를 구성할 때 코드 내에서 세션 및 아티팩트 서비스를 구성합니다(예: 영구 데이터베이스 지원 세션 저장소의 경우 `session/database`, Cloud Storage 지원 아티팩트의 경우 `artifact/gcsartifact`).

| 옵션 | 설명 | 기본값 |
|--------|-------------|---------|
| `--session_service_uri` | 사용자 지정 세션 스토리지 URI | `<agents_dir>/<agent>/.adk/session.db`에 위치한 에이전트별 SQLite |
| `--artifact_service_uri` | 사용자 지정 아티팩트 스토리지 URI | `<agents_dir>/<agent>/.adk/artifacts`에 위치한 에이전트별 디렉토리 |
| `--memory_service_uri` | 사용자 지정 메모리 서비스 URI | 인메모리 |

### 스토리지 옵션 예시

```shell
adk run --session_service_uri "sqlite:///my_sessions.db" path/to/my_agent
```

## 모든 옵션

=== "Python"

    대화형 세션을 시작하는 대신 단일 메시지를 보내고 종료하려면 질의를 인수로 전달합니다:

    ```shell
    adk run path/to/my_agent "hello"
    ```

    | 옵션 | 설명 |
    |--------|-------------|
    | `--save_session` | 종료 시 세션을 JSON 파일에 저장 |
    | `--session_id` | 저장할 때 사용할 세션 ID |
    | `--resume` | 재개할 저장된 세션 파일의 경로 |
    | `--replay` | 비대화형 재생을 위한 입력 파일 경로 |
    | `--session_service_uri` | 사용자 지정 세션 스토리지 URI |
    | `--artifact_service_uri` | 사용자 지정 아티팩트 스토리지 URI |
    | `--memory_service_uri` | 사용자 지정 메모리 서비스 URI |
    | `--use_local_storage/--no_use_local_storage` | 서비스 URI가 설정되지 않은 경우 로컬 `.adk` 폴더 사용 여부 |
    | `--state` | 실행을 위한 초기 상태 (JSON 문자열) |
    | `--timeout` | 단일 턴 또는 질의에 대한 타임아웃 (예: `30s`, `5m`) |
    | `--in_memory` | 세션 데이터를 영구 저장하지 않음 |
    | `--jsonl` | 사람이 읽을 수 있는 텍스트 대신 구조화된 JSONL 출력 |
    | `--default_llm_model` | 에이전트가 설정하지 않은 경우 사용할 기본 모델 |

=== "Go"

    !!! note "Go 플래그는 Python과 다릅니다"

        Go 콘솔 론처는 `--save_session`, `--resume`, `--replay`, `--session_id`, `--session_service_uri`, `--artifact_service_uri`를 지원하지 않습니다. 이는 Python CLI 기능입니다. 세션 및 아티팩트 서비스는 `launcher.Config`를 통해 Go 코드에서 구성됩니다.

    플래그는 `console` 키워드 뒤에 전달됩니다 (또는 `console`이 기본값인 경우 직접 전달):

    | 플래그 | 설명 | 기본값 |
    |------|-------------|---------|
    | `-streaming_mode` | 에이전트 응답을 위한 스트리밍 모드 (`none`\|`sse`) | 자동 감지 (TTY → `sse`, 파이프 → `none`) |
    | `-shutdown-timeout` | 정상 종료 대기 시간 | `2s` |
    | `-otel_to_cloud` | OpenTelemetry 데이터를 GCP로 내보내기 | `false` |

    예를 들어 비스트리밍 출력을 강제하려면:

    ```shell
    go run agent.go console -streaming_mode none
    ```

    또는 SSE 스트리밍(토큰별 출력)을 강제하려면:

    ```shell
    go run agent.go -streaming_mode sse
    ```

## 사용량 텔레메트리 (Usage telemetry)

ADK CLI는 기능 채택을 이해하고 개발 우선순위를 안내하며 도구 성능을 향상하기 위해 익명의 사용량 텔레메트리를 수집합니다. 데이터 수집은 명시적으로 활성화할 때까지 기본적으로 비활성화(OFF)되어 있습니다.

텔레메트리 환경설정은 로컬 컴퓨터의 `~/.adk/config.json`에 저장됩니다. 터미널을 통해 언제든지 텔레메트리 데이터 수집을 관리할 수 있습니다:

- **활성화**: `adk telemetry enable`
- **비활성화**: `adk telemetry disable`
- **상태 확인**: `adk telemetry status`

`~/.adk/config.json`을 열고 `telemetry` 속성을 `false`로 설정하여 언제든지 수동으로 텔레메트리 데이터 수집을 비활성화할 수도 있습니다:

```json
{
  "telemetry": false
}
```

**수집되는 데이터**

- **환경 속성**: 운영체제 정보, 런타임 언어 및 버전, 설치된 ADK CLI 버전.
- **명령 실행 이벤트**: 일반적인 명령 및 하위 명령 이름, 전달된 플래그, 실행 시간, 종료 코드 및 오류 발생 시 예외 유형. 또한 시퀀스 번호와 명령 실행 후 삭제되는 임시 세션 ID를 로깅합니다.

**수집되지 않는 데이터**

CLI는 다음과 같은 민감하거나 비공개 또는 개인 데이터를 일체 수집하지 않습니다:

- 에이전트 이름, 프롬프트 문자열, 파일 경로 등 명령이나 플래그에 전달된 인수 또는 매개변수 값.
- 사용자 자격증명, 사용자 이름, API 키, OAuth 토큰 또는 비밀(secrets).
- Google Cloud 프로젝트 ID 또는 Cloud 계정 세부정보.
- 소스 코드 파일, 파일 내용 또는 디렉토리 경로.
- 개인 식별 정보(PII).
