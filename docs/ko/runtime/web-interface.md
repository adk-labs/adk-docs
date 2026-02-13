# 웹 인터페이스 사용

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ADK 웹 인터페이스를 사용하면 브라우저에서 에이전트를 직접 테스트할 수 있습니다. 이
도구는 에이전트를 대화형으로 개발하고 디버깅하는 간단한 방법을 제공합니다.

![ADK Web Interface](../assets/adk-web-dev-ui-chat.png)

!!! warning "주의: ADK Web은 개발 전용"

    ADK Web은 ***프로덕션 배포에서 사용하도록 설계되지 않았습니다***.
    ADK Web은 개발 및 디버깅 용도로만 사용해야 합니다.

## 웹 인터페이스 시작

다음 명령으로 ADK 웹 인터페이스에서 에이전트를 실행합니다:

=== "Python"

    ```shell
    adk web
    ```

=== "TypeScript"

    ```shell
    npx adk web
    ```

=== "Go"

    ```shell
    go run agent.go web api webui
    ```

=== "Java"

    포트 번호를 반드시 업데이트하세요.
    === "Maven"
        Maven을 사용해 ADK 웹 서버를 컴파일하고 실행합니다:
        ```console
        mvn compile exec:java \
         -Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"
        ```
    === "Gradle"
        Gradle을 사용할 경우 `build.gradle` 또는 `build.gradle.kts` 빌드 파일의 plugins 섹션에 다음 Java 플러그인이 있어야 합니다:

        ```groovy
        plugins {
            id('java')
            // other plugins
        }
        ```
        이후 빌드 파일의 top-level 영역에 새 태스크를 생성합니다:

        ```groovy
        tasks.register('runADKWebServer', JavaExec) {
            dependsOn classes
            classpath = sourceSets.main.runtimeClasspath
            mainClass = 'com.google.adk.web.AdkWebServer'
            args '--adk.agents.source-dir=src/main/java/agents', '--server.port=8080'
        }
        ```

        마지막으로 명령줄에서 다음 명령을 실행합니다:
        ```console
        gradle runADKWebServer
        ```


    Java에서는 웹 인터페이스와 API 서버가 함께 번들됩니다.

서버 기본 주소는 `http://localhost:8000`입니다:

```shell
+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://localhost:8000.                         |
+-----------------------------------------------------------------------------+
```

## 기능

ADK 웹 인터페이스의 주요 기능:

- **채팅 인터페이스**: 에이전트에 메시지를 보내고 실시간 응답 확인
- **세션 관리**: 세션 생성 및 전환
- **상태 점검**: 개발 중 세션 상태를 조회하고 수정
- **이벤트 히스토리**: 에이전트 실행 중 생성된 모든 이벤트 점검

## 일반 옵션

| Option | Description | Default |
|--------|-------------|---------|
| `--port` | 서버 실행 포트 | `8000` |
| `--host` | 호스트 바인딩 주소 | `127.0.0.1` |
| `--session_service_uri` | 사용자 지정 세션 저장소 URI | In-memory |
| `--artifact_service_uri` | 사용자 지정 아티팩트 저장소 URI | 로컬 `.adk/artifacts` |
| `--reload/--no-reload` | 코드 변경 시 자동 리로드 활성화 | `true` |

### 옵션 예시

```shell
adk web --port 3000 --session_service_uri "sqlite:///sessions.db"
```
