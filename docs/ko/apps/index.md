# App 워크플로 관리 클래스

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.14.0</span><span class="lst-typescript">TypeScript v1.4.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.4.0</span>
</div>

***App*** 클래스는 전체 에이전트 개발 키트(ADK) 에이전트 워크플로의 최상위 컨테이너입니다. ***루트 에이전트(root agent)***를 중심으로 그룹화된 에이전트 모음의 라이프사이클, 구성 및 상태를 관리하도록 설계되었습니다. **App** 클래스는 에이전트 워크플로의 전반적인 운영 인프라와 개별 에이전트의 작업 중심 추론을 분리하여 관심사 분리(separation of concerns)를 실현합니다.

ADK 워크플로에서 ***App*** 객체를 정의하는 것은 선택 사항이며, 에이전트 코드를 구성하고 에이전트를 실행하는 방식에 영향을 줍니다. 실무적으로는 ***App*** 클래스를 사용하여 에이전트 워크플로에 다음 기능을 구성합니다.

*   [**컨텍스트 캐싱**](/ko/context/caching/)
*   [**컨텍스트 압축**](/ko/context/compaction/)
*   [**에이전트 재개**](/ko/runtime/resume/)
*   [**플러그인**](/ko/plugins/)

이 가이드에서는 `App` 클래스를 사용하여 ADK 에이전트 워크플로를 구성하고 관리하는 방법을 설명합니다.

## App 클래스의 목적

***App*** 클래스는 복잡한 에이전트 시스템을 구축할 때 발생하는 여러 아키텍처 과제를 해결합니다.

*   **중앙 집중식 구성:** API 키 및 데이터베이스 클라이언트와 같은 공유 리소스를 단일 위치에서 중앙 집중식으로 관리하므로 모든 에이전트에 구성을 일일이 전달할 필요가 없습니다.
*   **라이프사이클 관리:** ***App*** 클래스에는 시작 시(`on_startup`) 및 종료 시(`on_shutdown`) 훅(hook)이 포함되어 있어 여러 호출에 걸쳐 유지되어야 하는 데이터베이스 연결 풀이나 인메모리 캐시와 같은 영구 리소스를 안정적으로 관리할 수 있습니다.
*   **상태 범위:** `app:*` 접두사로 애플리케이션 수준 상태에 대한 명시적인 경계를 정의하여 이 상태의 범위와 수명을 개발자에게 명확하게 드러냅니다.
*   **배포 단위:** ***App*** 개념은 공식적인 *배포 가능 단위*를 확립하여 에이전트 애플리케이션의 버전 관리, 테스트 및 서빙을 단순화합니다.

## App 객체 정의

***App*** 클래스는 에이전트 워크플로의 기본 컨테이너로 사용되며 프로젝트의 루트 에이전트를 포함합니다. ***루트 에이전트***는 기본 컨트롤러 에이전트와 추가 서브 에이전트들을 담는 컨테이너입니다.

### 루트 에이전트로 App 정의

***Agent*** 클래스의 인스턴스를 생성하여 워크플로의 ***루트 에이전트***를 만듭니다. 그런 다음 아래 샘플 코드와 같이 ***App*** 객체를 정의하고 ***루트 에이전트*** 객체와 선택적 기능을 구성합니다.

=== "Python"

    ```python title="agent.py"
    from google.adk.agents.llm_agent import Agent
    from google.adk.apps import App

    root_agent = Agent(
        model='gemini-flash-latest',
        name='greeter_agent',
        description='An agent that provides a friendly greeting.',
        instruction='Reply with Hello, World!',
    )

    app = App(
        name="agents",
        root_agent=root_agent,
        # 선택적으로 App 수준 기능 포함:
        # plugins, context_cache_config, events_compaction_config,
        # resumability_config
    )
    ```

=== "TypeScript"

    ```typescript title="agent.ts"
    import {App, LlmAgent} from '@google/adk';

    export const rootAgent = new LlmAgent({
      model: 'gemini-flash-latest',
      name: 'greeter_agent',
      description: 'An agent that provides a friendly greeting.',
      instruction: 'Reply with Hello, World!',
    });

    export const app = new App({
      name: 'agents',
      rootAgent: rootAgent,
      // 선택적으로 App 수준 기능 포함:
      // plugins, resumabilityConfig
    });
    ```

=== "Java"

    ```java title="AgentConfiguration.java"
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.apps.App;

    LlmAgent rootAgent = LlmAgent.builder()
        .model("gemini-flash-latest")
        .name("greeter_agent")
        .description("An agent that provides a friendly greeting.")
        .instruction("Reply with Hello, World!")
        .build();

    App app = App.builder()
        .name("agents")
        .rootAgent(rootAgent)
        // 선택적으로 App 수준 기능 포함:
        // .plugins(plugins)
        // .contextCacheConfig(contextCacheConfig)
        // .eventsCompactionConfig(eventsCompactionConfig)
        .build();
    ```

=== "Kotlin"

    ```kotlin title="Agent.kt"
    import com.google.adk.kt.agents.Instruction
    import com.google.adk.kt.agents.LlmAgent
    import com.google.adk.kt.apps.App
    import com.google.adk.kt.models.Gemini

    val rootAgent =
        LlmAgent(
            model = Gemini(name = "gemini-flash-latest"),
            name = "greeter_agent",
            description = "An agent that provides a friendly greeting.",
            instruction = Instruction("Reply with Hello, World!"),
        )

    val app =
        App(
            appName = "agents",
            rootAgent = rootAgent,
            // Optionally include App-level features:
            // plugins, resumabilityConfig, eventsCompactionConfig,
            // contextCacheConfig
        )
    ```

!!! tip "권장: `app` 변수 이름 사용"

    에이전트 프로젝트 코드에서 ***App*** 객체를 변수 이름 `app`에 할당하여 ADK 명령줄 인터페이스(CLI) 러너 도구와 호환되도록 하세요.

### App 에이전트 실행

다음 코드 샘플과 같이 `app` 매개변수를 통해 ***Runner*** 클래스로 에이전트 워크플로를 실행할 수 있습니다.

=== "Python"

    ```python title="main.py"
    import asyncio
    from dotenv import load_dotenv
    from google.adk.runners import InMemoryRunner
    from agent import app # agent.py에서 코드 가져오기

    load_dotenv() # API 키 및 설정 로드
    # 가져온 애플리케이션 객체를 사용하여 실행기 설정
    runner = InMemoryRunner(app=app)

    async def main():
        try:  # run_debug()에는 ADK Python 1.18 이상이 필요합니다.
            response = await runner.run_debug("Hello there!")

        except Exception as e:
            print(f"An error occurred during agent execution: {e}")

    if __name__ == "__main__":
        asyncio.run(main())

    ```

=== "TypeScript"

    ```typescript title="main.ts"
    import {InMemoryRunner, isFinalResponse, stringifyContent} from '@google/adk';
    import {app} from './agent.js'; // agent.ts에서 코드 가져오기

    // 가져온 애플리케이션 객체를 사용하여 Runner 설정
    const runner = new InMemoryRunner({app});

    async function main() {
      try {
        for await (const event of runner.runEphemeral({
          userId: 'user',
          newMessage: {role: 'user', parts: [{text: 'Hello there!'}]},
        })) {
          if (isFinalResponse(event) && event.content) {
            console.log(`Response: ${stringifyContent(event)}`);
          }
        }
      } catch (e) {
        console.error(`An error occurred during agent execution: ${e}`);
      }
    }

    main();
    ```

=== "Java"

    ```java title="AppMain.java"
    import com.google.genai.types.Content;
    import com.google.adk.runner.Runner;

    public class AppMain {

      public static void main(String[] args) throws Exception {
        // 애플리케이션 객체를 사용해 Runner 설정

        App app = ...;

        Runner runner = Runner.builder()
            .app(app) // 앞에서 정의한 'app' 객체 사용
            .build();

        runner.runAsync("user", "session-1", Content.fromParts(Part.fromText("Hello there!")))
            .filter(event -> event.finalResponse() && event.content().isPresent())
            .blockingSubscribe(event -> System.out.println("Response: " + event.stringifyContent()));
      }
    }
    ```

=== "Kotlin"

    ```kotlin title="Main.kt"
    import com.google.adk.kt.runners.InMemoryRunner
    import com.google.adk.kt.types.Content
    import com.google.adk.kt.types.Role
    import kotlinx.coroutines.runBlocking

    // Set a Runner using the application object defined in Agent.kt
    val runner = InMemoryRunner(app = app)

    fun main() =
        runBlocking {
            try {
                runner
                    .runAsync(
                        userId = "user",
                        sessionId = "session-1",
                        newMessage = Content.fromText(Role.USER, "Hello there!"),
                    ).collect { event ->
                        if (event.isFinalResponse && event.content != null) {
                            println("Response: ${event.contentText()}")
                        }
                    }
            } catch (e: Exception) {
                println("An error occurred during agent execution: $e")
            }
        }
    ```

!!! note "`Runner.run_debug()`에 대한 버전 요구 사항"

    `Runner.run_debug()` 명령에는 ADK Python v1.18.0 이상이 필요합니다. 더 많은 설정 코드가 필요한 `Runner.run()`을 사용할 수도 있습니다. 자세한 내용은 [에이전트 런타임](/ko/runtime/) 가이드를 참고하세요.

=== "Python"

    다음 명령을 사용하여 `main.py` 코드로 App 에이전트를 실행합니다.

    ```console
    python3 main.py
    ```

=== "TypeScript"

    다음 명령을 사용하여 `main.ts` 코드로 App 에이전트를 실행합니다.

    ```console
    npx tsx main.ts
    ```

=== "Java"

    `AppMain.java` 코드로 App 에이전트를 실행하려면 빌드 도구(예: Gradle `application` 플러그인)를 사용하세요.

    ```console
    ./gradlew run
    ```

=== "Kotlin"

    `Main.kt` 코드로 App 에이전트를 실행하려면 빌드 도구(예: Gradle `application` 플러그인)를 사용하세요.

    ```console
    ./gradlew run
    ```

## 다음 단계

더 완전한 샘플 코드 구현은 [Hello World 앱](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_app) 코드 예제를 참고하세요.
