# ADK 도구의 제한 사항

일부 ADK 도구에는 에이전트 워크플로 안에서 구현 방식에 영향을 줄 수 있는 제한이 있습니다.
이 페이지에서는 이러한 도구 제한 사항과, 가능한 경우 우회 방법을 설명합니다.

## 에이전트당 도구 1개 제한 {#one-tool-one-agent}

!!! note "ADK Python: 내장 Search 우회 방법은 옵트인(opt-in) 방식입니다"

    ADK Python v1.16.0 이상에서는 Google Search 및 Agent Search 도구에 대해
    이 제한을 우회할 수 있지만 기본적으로 활성화되어 있지는 않습니다.
    `bypass_multi_tools_limit=True`를 지정하여 도구를 직접 생성해야 하며,
    `google.adk.tools`에서 내보내는 공유 `google_search` 인스턴스는 이 플래그가
    꺼진 상태로 제공됩니다. 아래 우회 방법 #2를 참고하세요.

일반적으로 하나의 에이전트에 여러 도구를 사용할 수 있지만,
특정 도구를 에이전트 안에서 사용하면 같은 에이전트에서 다른 도구를
함께 사용할 수 없습니다. 다음 ADK 도구는 하나의 에이전트 객체에서
다른 도구 없이 단독으로만 사용할 수 있습니다.

*   Gemini API의 [Code Execution](/tools/gemini-api/code-execution/)
*   Gemini API의 [Google Search](/tools/gemini-api/google-search/)
*   [Vertex AI Search](/integrations/agent-search/)

예를 들어, 아래와 같이 이들 도구 중 하나를 다른 도구와 함께
하나의 에이전트에서 사용하는 방식은 ***지원되지 않습니다***.

=== "Python"

    ```py
    root_agent = Agent(
        name="RootAgent",
        model="gemini-flash-latest",
        description="Code Agent",
        tools=[custom_function],
        code_executor=BuiltInCodeExecutor() # <-- 도구와 함께 사용 시 지원되지 않음
    )
    ```

=== "Java"

    ```java
     LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("You're a specialist in Google Search")
                .tools(new GoogleSearchTool(), new YourCustomTool()) // <-- 지원되지 않음
                .build();
    ```

### 우회 방법 #1: 에이전트를 AgentTool로 감싸기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript (v0.6.1+)</span><span class="lst-java">Java</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

아래 코드는 여러 내장 도구를 함께 사용하거나,
내장 도구와 기타 도구를 여러 에이전트를 통해 조합하는 방법을 보여줍니다.

=== "Python"

    ```py
    from google.adk.tools.agent_tool import AgentTool
    from google.adk.agents import Agent
    from google.adk.tools import google_search
    from google.adk.code_executors import BuiltInCodeExecutor

    search_agent = Agent(
        model='gemini-flash-latest',
        name='SearchAgent',
        instruction="""
        You're a specialist in Google Search
        """,
        tools=[google_search],
    )
    coding_agent = Agent(
        model='gemini-flash-latest',
        name='CodeAgent',
        instruction="""
        You're a specialist in Code Execution
        """,
        code_executor=BuiltInCodeExecutor(),
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-flash-latest",
        description="Root Agent",
        tools=[AgentTool(agent=search_agent), AgentTool(agent=coding_agent)],
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.BaseAgent;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.tools.AgentTool;
    import com.google.adk.tools.BuiltInCodeExecutionTool;
    import com.google.adk.tools.GoogleSearchTool;
    import com.google.common.collect.ImmutableList;

    public class NestedAgentApp {

      private static final String MODEL_ID = "gemini-flash-latest";

      public static void main(String[] args) {

        // SearchAgent 정의
        LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("You're a specialist in Google Search")
                .tools(new GoogleSearchTool()) // GoogleSearchTool 인스턴스화
                .build();


        // CodingAgent 정의
        LlmAgent codingAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("CodeAgent")
                .instruction("You're a specialist in Code Execution")
                .tools(new BuiltInCodeExecutionTool()) // BuiltInCodeExecutionTool 인스턴스화
                .build();

        // AgentTool.create()로 SearchAgent와 CodingAgent를 감싼 RootAgent 정의
        BaseAgent rootAgent =
            LlmAgent.builder()
                .name("RootAgent")
                .model(MODEL_ID)
                .description("Root Agent")
                .tools(
                    AgentTool.create(searchAgent), // create 메서드 사용
                    AgentTool.create(codingAgent)   // create 메서드 사용
                 )
                .build();

        // 참고: 이 샘플은 에이전트 정의만 보여줍니다.
        // 실제 실행하려면 이전 예시와 유사하게 Runner, SessionService와 통합해야 합니다.
        System.out.println("Agents defined successfully:");
        System.out.println("  Root Agent: " + rootAgent.name());
        System.out.println("  Search Agent (nested): " + searchAgent.name());
        System.out.println("  Code Agent (nested): " + codingAgent.name());
      }
    }
    ```

ADK Python에서 `AgentTool`은 래핑된 에이전트의 그라운딩 메타데이터를 호출하는 에이전트로 다시 전달하지 않습니다. 해당 메타데이터를 세션 상태의 `temp:_adk_grounding_metadata` 키 아래에 저장하려면 `AgentTool`에 `propagate_grounding_metadata=True`를 설정하세요. ADK는 상위 에이전트에 `google_search_agent`라는 이름의 도구가 있을 때만 이를 상위 에이전트 자체 응답에 첨부하며, 이 도구는 아래 우회 방법 #2가 자동으로 생성해 주는 도구입니다.

### 우회 방법 #2: bypass_multi_tools_limit

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-java">Java</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

ADK Python은 `GoogleSearchTool` 및 `VertexAiSearchTool`에 대해
이 제한을 우회하는 내장 방법을 제공합니다
(`bypass_multi_tools_limit=True`로 활성화).
자세한 내용은
[built_in_multi_tools](https://github.com/google/adk-python/tree/main/contributing/samples/tools/built_in_multi_tools)
샘플 에이전트를 참고하세요.

예를 들어 `google.adk.tools.google_search_tool`에서 가져온 `GoogleSearchTool(bypass_multi_tools_limit=True)`처럼 직접 생성한 도구 인스턴스에 플래그를 설정하세요. `google.adk.tools`에서 내보내는 공유 `google_search` 인스턴스는 이 플래그가 꺼진 상태로 유지됩니다. 이 우회 기능은 에이전트의 `tools` 목록에 항목이 두 개 이상 있거나 다른 에이전트로 제어권을 이전할 수 있을 때 적용됩니다.

!!! warning

    내장 도구는 하위 에이전트 내에서 사용할 수 없습니다. ADK Python에서는
    하위 에이전트가 `bypass_multi_tools_limit=True`로 도구를 생성한 경우에만
    `GoogleSearchTool` 및 `VertexAiSearchTool`이 예외적으로 허용됩니다.

예를 들어, 아래와 같이 하위 에이전트에서 내장 도구를 사용하는 방식은
**지원되지 않습니다**.

=== "Python"

    ```py
    url_context_agent = Agent(
        model='gemini-flash-latest',
        name='UrlContextAgent',
        instruction="""
        You're a specialist in URL Context
        """,
        tools=[url_context],
    )
    coding_agent = Agent(
        model='gemini-flash-latest',
        name='CodeAgent',
        instruction="""
        You're a specialist in Code Execution
        """,
        code_executor=BuiltInCodeExecutor(),
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-flash-latest",
        description="Root Agent",
        sub_agents=[
            url_context_agent,
            coding_agent
        ],
    )
    ```

=== "Java"

    ```java
    LlmAgent searchAgent =
        LlmAgent.builder()
            .model("gemini-flash-latest")
            .name("SearchAgent")
            .instruction("You're a specialist in Google Search")
            .tools(new GoogleSearchTool())
            .build();

    LlmAgent codingAgent =
        LlmAgent.builder()
            .model("gemini-flash-latest")
            .name("CodeAgent")
            .instruction("You're a specialist in Code Execution")
            .tools(new BuiltInCodeExecutionTool())
            .build();


    LlmAgent rootAgent =
        LlmAgent.builder()
            .name("RootAgent")
            .model("gemini-flash-latest")
            .description("Root Agent")
            .subAgents(searchAgent, codingAgent) // 하위 에이전트가 내장 도구를 사용하므로 지원되지 않음
            .build();
    ```

## Kotlin 해결 방법 예제

영어 원문에 추가된 Kotlin 예제는 내장 도구 제한을 피하기 위해 루트 에이전트에서만 내장 도구를 직접 구성하는 패턴을 보여줍니다.

```kotlin
--8<-- "examples/kotlin/snippets/tools/LimitationsWorkaround.kt:workaround_1"
```
