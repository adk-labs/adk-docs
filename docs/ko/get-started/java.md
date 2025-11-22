# ADK용 Java 빠른 시작

이 가이드는 ADK(Agent Development Kit) for Java를 사용하여 시작하는 방법을 보여줍니다. 시작하기 전에 다음이 설치되어 있는지 확인하십시오.

*   Java 17 이상
*   Maven 3.9 이상

## 에이전트 프로젝트 생성

다음 파일 및 디렉토리 구조로 에이전트 프로젝트를 생성합니다.

```none
my_agent/
    src/main/java/com/example/agent/
                        HelloTimeAgent.java # 메인 에이전트 코드
                        AgentCliRunner.java # 명령줄 인터페이스
    pom.xml                                 # 프로젝트 구성
    .env                                    # API 키 또는 프로젝트 ID
```

??? tip "명령줄을 사용하여 이 프로젝트 구조 생성"

    === "Windows"

        ```console
        mkdir my_agent\src\main\java\com\example\agent
        type nul > my_agent\src\main\java\com\example\agent\HelloTimeAgent.java
        type nul > my_agent\src\main\java\com\example\agent\AgentCliRunner.java
        type nul > my_agent\pom.xml
        type nul > my_agent\.env
        ```

    === "MacOS / Linux"

        ```bash
        mkdir -p my_agent/src/main/java/com/example/agent && \
            touch my_agent/src/main/java/com/example/agent/HelloTimeAgent.java && \
            touch my_agent/src/main/java/com/example/agent/AgentCliRunner.java && \
            touch my_agent/pom.xml my_agent/.env
        ```

### 에이전트 코드 정의

ADK [함수 도구](/adk-docs/ko/tools-custom/function-tools/)의 간단한 구현인 `getCurrentTime()`을 포함하여 기본 에이전트 코드를 생성합니다. 프로젝트 디렉토리의 `HelloTimeAgent.java` 파일에 다음 코드를 추가합니다.

```java title="my_agent/src/main/java/com/example/agent/HelloTimeAgent.java"
package com.example.agent;

import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;

import java.util.Map;

public class HelloTimeAgent {

    public static BaseAgent ROOT_AGENT = initAgent();

    private static BaseAgent initAgent() {
        return LlmAgent.builder()
            .name("hello-time-agent")
            .description("지정된 도시의 현재 시간을 알려줍니다.")
            .instruction("""
                당신은 지정된 도시의 현재 시간을 알려주는 유용한 도우미입니다.
                이를 위해 'getCurrentTime' 도구를 사용하십시오.
                """)
            .model("gemini-2.5-flash")
            .tools(FunctionTool.create(HelloTimeAgent.class, "getCurrentTime"))
            .build();
    }

    /** Mock 도구 구현 */
    @Schema(description = "주어진 도시에 대한 현재 시간을 가져옵니다.")
    public static Map<String, String> getCurrentTime(
        @Schema(name = "city", description = "시간을 가져올 도시 이름") String city) {
        return Map.of(
            "city", city,
            "forecast", "시간은 오전 10시 30분입니다."
        );
    }
}
```

!!! warning "주의: Gemini 3 호환성"

    ADK Java v0.3.0 이하는 함수 호출에 대한 사고 서명 변경으로 인해
    [Gemini 3 Pro Preview](https://ai.google.dev/gemini-api/docs/models#gemini-3-pro)와 호환되지 않습니다.
    대신 Gemini 2.5 이하 모델을 사용하십시오.

### 프로젝트 및 종속성 구성

ADK 에이전트 프로젝트는 `pom.xml` 프로젝트 파일에 다음 종속성이 필요합니다.

```xml title="my_agent/pom.xml (일부)"
<dependencies>
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>adk-core</artifactId>
        <version>0.3.0</version>
    </dependency>
</dependencies>
```

`pom.xml` 프로젝트 파일을 업데이트하여 이 종속성과 추가 설정을 다음 구성 코드를 포함하도록 합니다.

??? info "프로젝트에 대한 완전한 `pom.xml` 구성"
    다음 코드는 이 프로젝트에 대한 완전한 `pom.xml` 구성을 보여줍니다.

    ```xml title="my_agent/pom.xml"
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion>

        <groupId>com.example.agent</groupId>
        <artifactId>adk-agents</artifactId>
        <version>1.0-SNAPSHOT</version>

        <!-- 사용할 Java 버전 지정 -->
        <properties>
            <maven.compiler.source>17</maven.compiler.source>
            <maven.compiler.target>17</maven.compiler.target>
            <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        </properties>

        <dependencies>
            <!-- ADK 코어 종속성 -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk</artifactId>
                <version>0.3.0</version>
            </dependency>
            <!-- 에이전트를 디버그하기 위한 ADK 개발 웹 UI -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk-dev</artifactId>
                <version>0.3.0</version>
            </dependency>
        </dependencies>

    </project>
    ```

### API 키 설정

이 프로젝트는 API 키가 필요한 Gemini API를 사용합니다. Gemini API 키가 아직 없는 경우 Google AI Studio의 [API 키](https://aistudio.google.com/app/apikey) 페이지에서 키를 생성합니다.

터미널 창에서 프로젝트의 `.env` 파일에 API 키를 작성하여 환경 변수를 설정합니다.

=== "MacOS / Linux"

    ```bash title="업데이트: my_agent/.env"
    echo 'export GOOGLE_API_KEY="YOUR_API_KEY"' > .env
    ```

=== "Windows"

    ```console title="업데이트: my_agent/env.bat"
    echo 'set GOOGLE_API_KEY="YOUR_API_KEY"' > env.bat
    ```

??? tip "ADK에서 다른 AI 모델 사용"
    ADK는 다양한 생성형 AI 모델 사용을 지원합니다. ADK 에이전트에서 다른 모델을 구성하는 방법에 대한 자세한 내용은 [모델 및 인증](/adk-docs/ko/agents/models)을 참조하세요.

### 에이전트 명령줄 인터페이스 생성

`AgentCliRunner.java` 클래스를 생성하여 명령줄에서 `HelloTimeAgent`를 실행하고 상호 작용할 수 있도록 합니다. 이 코드는 에이전트를 실행하기 위한 `RunConfig` 객체와 실행 중인 에이전트와 상호 작용하기 위한 `Session` 객체를 생성하는 방법을 보여줍니다.

```java title="my_agent/src/main/java/com/example/agent/AgentCliRunner.java"
package com.example.agent;

import com.google.adk.agents.RunConfig;
import com.google.adk.events.Event;
import com.google.adk.runner.InMemoryRunner;
import com.google.adk.sessions.Session;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Scanner;

import static java.nio.charset.StandardCharsets.UTF_8;

public class AgentCliRunner {

    public static void main(String[] args) {
        RunConfig runConfig = RunConfig.builder().build();
        InMemoryRunner runner = new InMemoryRunner(HelloTimeAgent.ROOT_AGENT);

        Session session = runner
                .sessionService()
                .createSession(runner.appName(), "user1234")
                .blockingGet();

        try (Scanner scanner = new Scanner(System.in, UTF_8)) {
            while (true) {
                System.out.print("\nYou > ");
                String userInput = scanner.nextLine();
                if ("quit".equalsIgnoreCase(userInput)) {
                    break;
                }

                Content userMsg = Content.fromParts(Part.fromText(userInput));
                Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg, runConfig);

                System.out.print("\nAgent > ");
                events.blockingForEach(event -> {
                    if (event.finalResponse()) {
                        System.out.println(event.stringifyContent());
                    }
                });
            }
        }
    }
}
```

## 에이전트 실행

정의한 대화형 명령줄 인터페이스 `AgentCliRunner` 클래스 또는 `AdkWebServer` 클래스를 사용하여 ADK에서 제공하는 ADK 웹 사용자 인터페이스를 사용하여 ADK 에이전트를 실행할 수 있습니다. 이 두 가지 옵션을 통해 에이전트를 테스트하고 상호 작용할 수 있습니다.

### 명령줄 인터페이스로 실행

다음 Maven 명령을 사용하여 명령줄 인터페이스 `AgentCliRunner` 클래스로 에이전트를 실행합니다.

```console
# 키 및 설정 로드: source .env 또는 env.bat
mvn compile exec:java -Dexec.mainClass="com.example.agent.AgentCliRunner"
```

![adk-run.png](/adk-docs/ko/assets/adk-run.png)

### 웹 인터페이스로 실행

다음 Maven 명령을 사용하여 ADK 웹 인터페이스로 에이전트를 실행합니다.

```console
# 키 및 설정 로드: source .env 또는 env.bat
mvn compile exec:java \
    -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
    -Dexec.args="--adk.agents.source-dir=target --server.port=8000"
```

이 명령은 에이전트용 채팅 인터페이스가 있는 웹 서버를 시작합니다. 웹 인터페이스는 (http://localhost:8000)에서 액세스할 수 있습니다. 왼쪽 상단 모서리에서 에이전트를 선택하고 요청을 입력합니다.

![adk-web-dev-ui-chat.png](/adk-docs/ko/assets/adk-web-dev-ui-chat.png)

## 다음: 에이전트 빌드

이제 ADK가 설치되었고 첫 번째 에이전트가 실행 중이므로 이제 빌드 가이드를 사용하여 자신만의 에이전트를 빌드해 보세요.

*  [에이전트 빌드](/adk-docs/ko/tutorials/)

```