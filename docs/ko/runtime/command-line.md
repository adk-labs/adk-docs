# 명령줄 사용

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK는 에이전트를 테스트하기 위한 대화형 터미널 인터페이스를 제공합니다. 이는
빠른 테스트, 스크립트 기반 상호작용, CI/CD 파이프라인에 유용합니다.

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

    ```shell
    go run agent.go
    ```

=== "Java"

    `AgentCliRunner` 클래스를 만들고([Java 빠른 시작](../get-started/java.md) 참고) 다음을 실행합니다:

    ```shell
    mvn compile exec:java -Dexec.mainClass="com.example.agent.AgentCliRunner"
    ```

그러면 질의를 입력하고 터미널에서 에이전트 응답을 직접 확인할 수 있는
대화형 세션이 시작됩니다:

```shell
Running agent my_agent, type exit to exit.
[user]: What's the weather in New York?
[my_agent]: The weather in New York is sunny with a temperature of 25°C.
[user]: exit
```

## 세션 옵션

`adk run` 명령에는 세션 저장, 재개, 재생을 위한 옵션이 있습니다.

### 세션 저장

종료 시 세션을 저장하려면:

```shell
adk run --save_session path/to/my_agent
```

세션 ID 입력을 요청받으며, 세션은
`path/to/my_agent/<session_id>.session.json`에 저장됩니다.

세션 ID를 미리 지정할 수도 있습니다:

```shell
adk run --save_session --session_id my_session path/to/my_agent
```

### 세션 재개

이전에 저장한 세션을 이어서 진행하려면:

```shell
adk run --resume path/to/my_agent/my_session.session.json path/to/my_agent
```

이 명령은 이전 세션 상태와 이벤트 히스토리를 불러와 표시한 뒤,
대화를 계속할 수 있게 합니다.

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

## 저장소 옵션

| Option | Description | Default |
|--------|-------------|---------|
| `--session_service_uri` | 사용자 지정 세션 저장소 URI | `.adk/session.db` 아래 SQLite |
| `--artifact_service_uri` | 사용자 지정 아티팩트 저장소 URI | 로컬 `.adk/artifacts` |

### 저장소 옵션 예시

```shell
adk run --session_service_uri "sqlite:///my_sessions.db" path/to/my_agent
```

## 전체 옵션

| Option | Description |
|--------|-------------|
| `--save_session` | 종료 시 세션을 JSON 파일로 저장 |
| `--session_id` | 저장 시 사용할 세션 ID |
| `--resume` | 재개할 저장 세션 파일 경로 |
| `--replay` | 비대화형 재생용 입력 파일 경로 |
| `--session_service_uri` | 사용자 지정 세션 저장소 URI |
| `--artifact_service_uri` | 사용자 지정 아티팩트 저장소 URI |
