# API 서버 사용하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

에이전트를 배포하기 전에 의도한 대로 작동하는지 테스트해야 합니다. 개발 환경에서 에이전트를 테스트하는 가장 쉬운 방법은 ADK API 서버를 사용하는 것입니다.

=== "Python"

    ```py
    adk api_server
    ```

=== "Go"

    ```go
    go run agent.go web api
    ```

=== "Java"

    포트 번호를 업데이트해야 합니다.
    === "Maven"
        Maven으로 ADK 웹 서버를 컴파일하고 실행합니다.
        ```console
        mvn compile exec:java \
         -Dexec.args="--adk.agents.source-dir=src/main/java/agents --server.port=8080"
        ```
    === "Gradle"
        Gradle의 경우, `build.gradle` 또는 `build.gradle.kts` 빌드 파일의 플러그인 섹션에 다음 Java 플러그인이 있어야 합니다.

        ```groovy
        plugins {
            id('java')
            // 다른 플러그인들
        }
        ```
        그런 다음, 빌드 파일의 다른 곳, 최상위 레벨에 새 태스크를 생성합니다.

        ```groovy
        tasks.register('runADKWebServer', JavaExec) {
            dependsOn classes
            classpath = sourceSets.main.runtimeClasspath
            mainClass = 'com.google.adk.web.AdkWebServer'
            args '--adk.agents.source-dir=src/main/java/agents', '--server.port=8080'
        }
        ```

        마지막으로, 명령줄에서 다음 명령을 실행합니다.
        ```console
        gradle runADKWebServer
        ```


    Java에서는 Dev UI와 API 서버가 함께 번들로 제공됩니다.

이 명령어는 로컬 웹 서버를 시작하며, 여기서 cURL 명령을 실행하거나 API 요청을 보내 에이전트를 테스트할 수 있습니다.

!!! tip "고급 사용법 및 디버깅"

    사용 가능한 모든 엔드포인트, 요청/응답 형식, 디버깅 팁(대화형 API 문서 사용 방법 포함)에 대한 전체 참조는 아래 **ADK API 서버 가이드**를 참조하세요.

## 로컬 테스트

로컬 테스트는 로컬 웹 서버를 시작하고, 세션을 생성하고, 에이전트에 쿼리를 보내는 과정을 포함합니다. 먼저, 올바른 작업 디렉터리에 있는지 확인하세요.

```console
parent_folder/
└── my_sample_agent/
    └── agent.py (또는 Agent.java)
```

**로컬 서버 시작**

다음으로, 위에 나열된 명령을 사용하여 로컬 서버를 시작합니다.

출력은 다음과 유사하게 나타나야 합니다.

=== "Python"

    ```shell
    INFO:     Started server process [12345]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
    ```

=== "Java"

    ```shell
    2025-05-13T23:32:08.972-06:00  INFO 37864 --- [ebServer.main()] o.s.b.w.embedded.tomcat.TomcatWebServer  : Tomcat started on port 8080 (http) with context path '/'
    2025-05-13T23:32:08.980-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : Started AdkWebServer in 1.15 seconds (process running for 2.877)
    2025-05-13T23:32:08.981-06:00  INFO 37864 --- [ebServer.main()] com.google.adk.web.AdkWebServer          : AdkWebServer application started successfully.
    ```

이제 서버가 로컬에서 실행 중입니다. 이후의 모든 명령어에서 올바른 **_포트 번호_**를 사용해야 합니다.

**새 세션 생성**

API 서버가 계속 실행 중인 상태에서 새 터미널 창이나 탭을 열고 다음을 사용하여 에이전트와 새 세션을 생성합니다.

```shell
curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"key1": "value1", "key2": 42}'
```

무슨 일이 일어나는지 분석해 보겠습니다.

* `http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_123`: 이 주소는 에이전트 폴더 이름인 `my_sample_agent` 에이전트에 대해 사용자 ID(`u_123`)와 세션 ID(`s_123`)로 새 세션을 생성합니다. `my_sample_agent`를 여러분의 에이전트 폴더 이름으로 바꿀 수 있습니다. `u_123`은 특정 사용자 ID로, `s_123`은 특정 세션 ID로 바꿀 수 있습니다.
* `{"key1": "value1", "key2": 42}`: 이 부분은 선택 사항입니다. 세션을 생성할 때 에이전트의 기존 상태(dict)를 사용자 정의하는 데 사용할 수 있습니다.

성공적으로 생성되면 세션 정보가 반환되어야 합니다. 출력은 다음과 유사하게 나타나야 합니다.

```json
{"id":"s_123","appName":"my_sample_agent","userId":"u_123","state":{"key1":"value1","key2":42},"events":[],"lastUpdateTime":1743711430.022186}
```

!!! info

    정확히 동일한 사용자 ID와 세션 ID로 여러 세션을 생성할 수 없습니다. 시도하면 다음과 같은 응답을 볼 수 있습니다. `{"detail":"Session already exists: s_123"}`. 이 문제를 해결하려면 해당 세션(예: `s_123`)을 삭제하거나 다른 세션 ID를 선택하면 됩니다.

**쿼리 전송**

POST를 통해 에이전트에 쿼리를 보내는 방법에는 `/run` 또는 `/run_sse` 경로를 사용하는 두 가지가 있습니다.

* `POST http://localhost:8000/run`: 모든 이벤트를 리스트로 수집하여 한 번에 반환합니다. 대부분의 사용자에게 적합합니다 (확실하지 않다면 이 방법을 사용하는 것을 권장합니다).
* `POST http://localhost:8000/run_sse`: 서버-전송 이벤트(Server-Sent-Events)로 반환하며, 이는 이벤트 객체의 스트림입니다. 이벤트가 사용 가능해지는 즉시 알림을 받고 싶은 사용자에게 적합합니다. `/run_sse`를 사용하면 `streaming`을 `true`로 설정하여 토큰 수준 스트리밍을 활성화할 수도 있습니다.

**`/run` 사용하기**

```shell
curl -X POST http://localhost:8000/run \
-H "Content-Type: application/json" \
-d '{
"app_name": "my_sample_agent",
"user_id": "u_123",
"session_id": "s_123",
"new_message": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
}
}'
```

`/run`을 사용하면 전체 이벤트 출력이 동시에 리스트 형태로 표시되며, 다음과 유사하게 나타나야 합니다.

```json
[{"content":{"parts":[{"functionCall":{"id":"af-e75e946d-c02a-4aad-931e-49e4ab859838","args":{"city":"new york"},"name":"get_weather"}}],"role":"model"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"longRunningToolIds":[],"id":"2Btee6zW","timestamp":1743712220.385936},{"content":{"parts":[{"functionResponse":{"id":"af-e75e946d-c02a-4aad-931e-49e4ab859838","name":"get_weather","response":{"status":"success","report":"The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}}}],"role":"user"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"PmWibL2m","timestamp":1743712221.895042},{"content":{"parts":[{"text":"OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"}],"role":"model"},"invocationId":"e-71353f1e-aea1-4821-aa4b-46874a766853","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"sYT42eVC","timestamp":1743712221.899018}]
```

**`/run_sse` 사용하기**

```shell
curl -X POST http://localhost:8000/run_sse \
-H "Content-Type: application/json" \
-d '{
"app_name": "my_sample_agent",
"user_id": "u_123",
"session_id": "s_123",
"new_message": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
},
"streaming": false
}'
```

`streaming`을 `true`로 설정하여 토큰 수준 스트리밍을 활성화할 수 있습니다. 이는 응답이 여러 청크로 반환됨을 의미하며, 출력은 다음과 유사하게 나타나야 합니다.

```shell
data: {"content":{"parts":[{"functionCall":{"id":"af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d","args":{"city":"new york"},"name":"get_weather"}}],"role":"model"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"longRunningToolIds":[],"id":"ptcjaZBa","timestamp":1743712255.313043}

data: {"content":{"parts":[{"functionResponse":{"id":"af-f83f8af9-f732-46b6-8cb5-7b5b73bbf13d","name":"get_weather","response":{"status":"success","report":"The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit)."}}}],"role":"user"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"5aocxjaq","timestamp":1743712257.387306}

data: {"content":{"parts":[{"text":"OK. The weather in New York is sunny with a temperature of 25 degrees Celsius (41 degrees Fahrenheit).\n"}],"role":"model"},"invocationId":"e-3f6d7765-5287-419e-9991-5fffa1a75565","author":"weather_time_agent","actions":{"stateDelta":{},"artifactDelta":{},"requestedAuthConfigs":{}},"id":"rAnWGSiV","timestamp":1743712257.391317}
```
**`/run` 또는 `/run_sse`를 사용하여 base64로 인코딩된 파일과 함께 쿼리 전송**

```shell
curl -X POST http://localhost:8000/run \
--H 'Content-Type: application/json' \
--d '{
   "appName":"my_sample_agent",
   "userId":"u_123",
   "sessionId":"s_123",
   "newMessage":{
      "role":"user",
      "parts":[
         {
            "text":"Describe this image"
         },
         {
            "inlineData":{
               "displayName":"my_image.png",
               "data":"iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAACXBIWXMAAAsTAAALEwEAmpw...",
               "mimeType":"image/png"
            }
         }
      ]
   },
   "streaming":false
}'
```

!!! info

    `/run_sse`를 사용하는 경우, 각 이벤트가 사용 가능해지는 즉시 볼 수 있습니다.

## 통합

ADK는 [콜백](../callbacks/index.md)을 사용하여 서드파티 관찰 가능성 도구와 통합됩니다. 이러한 통합은 에이전트 호출 및 상호 작용의 상세한 추적을 캡처하며, 이는 동작을 이해하고 문제를 디버깅하며 성능을 평가하는 데 중요합니다.

* [Comet Opik](https://github.com/comet-ml/opik)은 오픈소스 LLM 관찰 가능성 및 평가 플랫폼으로, [ADK를 기본적으로 지원](https://www.comet.com/docs/opik/tracing/integrations/adk)합니다.

## 에이전트 배포하기

이제 에이전트의 로컬 작동을 확인했으므로, 에이전트 배포 단계로 넘어갈 준비가 되었습니다! 에이전트를 배포할 수 있는 몇 가지 방법은 다음과 같습니다.

* [Agent Engine](../deploy/agent-engine/index.md)에 배포하기: ADK 에이전트를 Google Cloud의 Vertex AI 관리형 서비스에 배포하는 가장 쉬운 방법입니다.
* [Cloud Run](../deploy/cloud-run.md)에 배포하기: Google Cloud의 서버리스 아키텍처를 사용하여 에이전트를 확장하고 관리하는 방법을 완전히 제어할 수 있습니다.


## ADK API 서버

ADK API 서버는 에이전트를 RESTful API를 통해 노출하는 미리 패키징된 [FastAPI](https://fastapi.tiangolo.com/) 웹 서버입니다. 로컬 테스트 및 개발을 위한 주요 도구이며, 배포하기 전에 프로그래밍 방식으로 에이전트와 상호 작용할 수 있게 해줍니다.

## 서버 실행하기

서버를 시작하려면 프로젝트의 루트 디렉터리에서 다음 명령을 실행하세요.

```shell
adk api_server
```

기본적으로 서버는 `http://localhost:8000`에서 실행됩니다. 서버가 시작되었음을 확인하는 출력이 표시됩니다.

```shell
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

## 대화형 API 문서로 디버깅하기

API 서버는 Swagger UI를 사용하여 대화형 API 문서를 자동으로 생성합니다. 이는 엔드포인트를 탐색하고, 요청 형식을 이해하며, 브라우저에서 직접 에이전트를 테스트하는 데 매우 유용한 도구입니다.

대화형 문서에 액세스하려면 API 서버를 시작하고 웹 브라우저에서 [http://localhost:8000/docs](http://localhost:8000/docs)로 이동하세요.

사용 가능한 모든 API 엔드포인트의 완전하고 대화형인 목록이 표시되며, 이를 확장하여 파라미터, 요청 본문 및 응답 스키마에 대한 자세한 정보를 볼 수 있습니다. "Try it out"을 클릭하여 실행 중인 에이전트에 실시간 요청을 보낼 수도 있습니다.

## API 엔드포인트

다음 섹션에서는 에이전트와 상호 작용하기 위한 주요 엔드포인트에 대해 자세히 설명합니다.

!!! note "JSON 이름 규칙"
    - **요청 본문**은 필드 이름에 `snake_case`를 사용해야 합니다 (예: `"app_name"`).
    - **응답 본문**은 필드 이름에 `camelCase`를 사용합니다 (예: `"appName"`).

### 유틸리티 엔드포인트

#### 사용 가능한 에이전트 목록 조회

서버에서 발견한 모든 에이전트 애플리케이션 목록을 반환합니다.

*   **메서드:** `GET`
*   **경로:** `/list-apps`

**요청 예시**
```shell
curl -X GET http://localhost:8000/list-apps
```

**응답 예시**
```json
["my_sample_agent", "another_agent"]
```

---

### 세션 관리

세션은 특정 사용자가 에이전트와 상호 작용하는 동안의 상태와 이벤트 기록을 저장합니다.

#### 세션 생성 또는 업데이트

새 세션을 생성하거나 기존 세션을 업데이트합니다. 지정된 ID를 가진 세션이 이미 존재하는 경우, 해당 상태는 제공된 새 상태로 덮어쓰여집니다.

*   **메서드:** `POST`
*   **경로:** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**요청 본문**
```json
{
  "key1": "value1",
  "key2": 42
}
```

**요청 예시**
```shell
curl -X POST http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc \
  -H "Content-Type: application/json" \
  -d '{"visit_count": 5}'
```

**응답 예시**
```json
{"id":"s_abc","appName":"my_sample_agent","userId":"u_123","state":{"visit_count":5},"events":[],"lastUpdateTime":1743711430.022186}
```

#### 세션 조회

특정 세션의 세부 정보(현재 상태 및 모든 관련 이벤트 포함)를 검색합니다.

*   **메서드:** `GET`
*   **경로:** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**요청 예시**
```shell
curl -X GET http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
```

**응답 예시**
```json
{"id":"s_abc","appName":"my_sample_agent","userId":"u_123","state":{"visit_count":5},"events":[...],"lastUpdateTime":1743711430.022186}
```

#### 세션 삭제

세션 및 모든 관련 데이터를 삭제합니다.

*   **메서드:** `DELETE`
*   **경로:** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`

**요청 예시**
```shell
curl -X DELETE http://localhost:8000/apps/my_sample_agent/users/u_123/sessions/s_abc
```

**응답 예시**
성공적으로 삭제되면 `204 No Content` 상태 코드와 함께 빈 응답이 반환됩니다.

---

### 에이전트 실행

이 엔드포인트들은 에이전트에 새 메시지를 보내고 응답을 받는 데 사용됩니다.

#### 에이전트 실행 (단일 응답)

에이전트를 실행하고 실행이 완료된 후 생성된 모든 이벤트를 단일 JSON 배열로 반환합니다.

*   **메서드:** `POST`
*   **경로:** `/run`

**요청 본문**
```json
{
  "app_name": "my_sample_agent",
  "user_id": "u_123",
  "session_id": "s_abc",
  "new_message": {
    "role": "user",
    "parts": [
      { "text": "What is the capital of France?" }
    ]
  }
}
```

**요청 예시**
```shell
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my_sample_agent",
    "user_id": "u_123",
    "session_id": "s_abc",
    "new_message": {
      "role": "user",
      "parts": [{"text": "What is the capital of France?"}]
    }
  }'
```

#### 에이전트 실행 (스트리밍)

에이전트를 실행하고 이벤트가 생성될 때마다 [서버-전송 이벤트(SSE)](https://developer.mozilla.org/ko/docs/Web/API/Server-sent_events)를 사용하여 클라이언트로 스트리밍합니다.

*   **메서드:** `POST`
*   **경로:** `/run_sse`

**요청 본문**
요청 본문은 `/run`과 동일하며, 선택적 `streaming` 플래그가 추가됩니다.
```json
{
  "app_name": "my_sample_agent",
  "user_id": "u_123",
  "session_id": "s_abc",
  "new_message": {
    "role": "user",
    "parts": [
      { "text": "What is the weather in New York?" }
    ]
  },
  "streaming": true
}
```
- `streaming`: (선택 사항) `true`로 설정하면 모델 응답에 대해 토큰 수준 스트리밍을 활성화합니다. 기본값은 `false`입니다.

**요청 예시**
```shell
curl -X POST http://localhost:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "my_sample_agent",
    "user_id": "u_123",
    "session_id": "s_abc",
    "new_message": {
      "role": "user",
      "parts": [{"text": "What is the weather in New York?"}]
    },
    "streaming": false
  }'
```
