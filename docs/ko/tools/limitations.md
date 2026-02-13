# ADK 도구의 제한 사항

일부 ADK 도구에는 에이전트 워크플로 안에서 구현 방식에 영향을 줄 수 있는 제한이 있습니다.
이 페이지에서는 이러한 도구 제한 사항과, 가능한 경우 우회 방법을 설명합니다.

## 에이전트당 도구 1개 제한 {#one-tool-one-agent}

!!! note "ADK Python v1.15.0 이하의 Search에만 해당"

    이 제한은 ADK Python v1.15.0 이하에서 Google Search 및 Vertex AI Search
    도구를 사용할 때만 적용됩니다. ADK Python v1.16.0 이상에서는
    이 제한을 제거하는 내장 우회 방법이 제공됩니다.

일반적으로 하나의 에이전트에 여러 도구를 사용할 수 있지만,
특정 도구를 에이전트 안에서 사용하면 같은 에이전트에서 다른 도구를
함께 사용할 수 없습니다. 다음 ADK 도구는 하나의 에이전트 객체에서
다른 도구 없이 단독으로만 사용할 수 있습니다.

*   Gemini API의 [Code Execution](/adk-docs/tools/gemini-api/code-execution/)
*   Gemini API의 [Google Search](/adk-docs/tools/gemini-api/google-search/)
*   [Vertex AI Search](/adk-docs/tools/google-cloud/vertex-ai-search/)

예를 들어, 아래와 같이 이들 도구 중 하나를 다른 도구와 함께
하나의 에이전트에서 사용하는 방식은 ***지원되지 않습니다***.

=== "Python"

    ```py
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.5-flash",
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

### 우회 방법 #1: AgentTool.create() 메서드

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-java">Java</span>
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
        model='gemini-2.0-flash',
        name='SearchAgent',
        instruction="""
        You're a specialist in Google Search
        """,
        tools=[google_search],
    )
    coding_agent = Agent(
        model='gemini-2.0-flash',
        name='CodeAgent',
        instruction="""
        You're a specialist in Code Execution
        """,
        code_executor=BuiltInCodeExecutor(),
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
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

      private static final String MODEL_ID = "gemini-2.0-flash";

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

### 우회 방법 #2: bypass_multi_tools_limit

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-java">Java</span>
</div>

ADK Python은 `GoogleSearchTool` 및 `VertexAiSearchTool`에 대해
이 제한을 우회하는 내장 방법을 제공합니다
(`bypass_multi_tools_limit=True`로 활성화).
자세한 내용은
[built_in_multi_tools](https://github.com/google/adk-python/tree/main/contributing/samples/built_in_multi_tools)
샘플 에이전트를 참고하세요.

!!! warning

    내장 도구는 하위 에이전트에서 사용할 수 없습니다.
    단, ADK Python에서는 위 우회 방법이 적용되는
    `GoogleSearchTool` 및 `VertexAiSearchTool`은 예외입니다.

예를 들어, 아래와 같이 하위 에이전트에서 내장 도구를 사용하는 방식은
**지원되지 않습니다**.

=== "Python"

    ```py
    url_context_agent = Agent(
        model='gemini-2.5-flash',
        name='UrlContextAgent',
        instruction="""
        You're a specialist in URL Context
        """,
        tools=[url_context],
    )
    coding_agent = Agent(
        model='gemini-2.5-flash',
        name='CodeAgent',
        instruction="""
        You're a specialist in Code Execution
        """,
        code_executor=BuiltInCodeExecutor(),
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.5-flash",
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
            .model("gemini-2.5-flash")
            .name("SearchAgent")
            .instruction("You're a specialist in Google Search")
            .tools(new GoogleSearchTool())
            .build();

    LlmAgent codingAgent =
        LlmAgent.builder()
            .model("gemini-2.5-flash")
            .name("CodeAgent")
            .instruction("You're a specialist in Code Execution")
            .tools(new BuiltInCodeExecutionTool())
            .build();


    LlmAgent rootAgent =
        LlmAgent.builder()
            .name("RootAgent")
            .model("gemini-2.5-flash")
            .description("Root Agent")
            .subAgents(searchAgent, codingAgent) // 하위 에이전트가 내장 도구를 사용하므로 지원되지 않음
            .build();
    ```
