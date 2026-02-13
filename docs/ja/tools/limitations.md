# ADK ツールの制限事項

一部の ADK ツールには、エージェントのワークフロー内での実装方法に
影響する制限があります。このページでは、それらの制限事項と、
可能な場合の回避策を説明します。

## エージェントごとのツール 1 個制限 {#one-tool-one-agent}

!!! note "ADK Python v1.15.0 以下の Search のみ"

    この制限は、ADK Python v1.15.0 以下で Google Search と Vertex AI Search
    ツールを使う場合にのみ適用されます。ADK Python v1.16.0 以降では、
    この制限を解消する組み込みの回避策が提供されています。

一般に、1 つのエージェントで複数ツールを使用できますが、
特定のツールをエージェント内で使う場合、そのエージェントでは他ツールを
併用できません。次の ADK ツールは、1 つのエージェントオブジェクト内で
他ツールなしに単独でのみ使用できます。

*   Gemini API の [Code Execution](/adk-docs/tools/gemini-api/code-execution/)
*   Gemini API の [Google Search](/adk-docs/tools/gemini-api/google-search/)
*   [Vertex AI Search](/adk-docs/tools/google-cloud/vertex-ai-search/)

たとえば、次のようにこれらのツールのいずれかを他ツールと一緒に
単一エージェントで使う方法は ***サポートされていません***。

=== "Python"

    ```py
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.5-flash",
        description="Code Agent",
        tools=[custom_function],
        code_executor=BuiltInCodeExecutor() # <-- ツール併用時は非サポート
    )
    ```

=== "Java"

    ```java
     LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("You're a specialist in Google Search")
                .tools(new GoogleSearchTool(), new YourCustomTool()) // <-- 非サポート
                .build();
    ```

### 回避策 #1: AgentTool.create() メソッド

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-java">Java</span>
</div>

次のコードサンプルは、複数の組み込みツールを使う方法、
または組み込みツールと他ツールを複数エージェントで組み合わせる方法を示します。

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

        // SearchAgent の定義
        LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("You're a specialist in Google Search")
                .tools(new GoogleSearchTool()) // GoogleSearchTool をインスタンス化
                .build();


        // CodingAgent の定義
        LlmAgent codingAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("CodeAgent")
                .instruction("You're a specialist in Code Execution")
                .tools(new BuiltInCodeExecutionTool()) // BuiltInCodeExecutionTool をインスタンス化
                .build();

        // AgentTool.create() で SearchAgent と CodingAgent をラップする RootAgent の定義
        BaseAgent rootAgent =
            LlmAgent.builder()
                .name("RootAgent")
                .model(MODEL_ID)
                .description("Root Agent")
                .tools(
                    AgentTool.create(searchAgent), // create メソッドを使用
                    AgentTool.create(codingAgent)   // create メソッドを使用
                 )
                .build();

        // 注: このサンプルはエージェント定義のみを示します。
        // 実行するには、前の例と同様に Runner と SessionService への統合が必要です。
        System.out.println("Agents defined successfully:");
        System.out.println("  Root Agent: " + rootAgent.name());
        System.out.println("  Search Agent (nested): " + searchAgent.name());
        System.out.println("  Code Agent (nested): " + codingAgent.name());
      }
    }
    ```

### 回避策 #2: bypass_multi_tools_limit

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-java">Java</span>
</div>

ADK Python には `GoogleSearchTool` と `VertexAiSearchTool` について
この制限を回避する組み込み機能があります
（`bypass_multi_tools_limit=True` で有効化）。
詳細は
[built_in_multi_tools](https://github.com/google/adk-python/tree/main/contributing/samples/built_in_multi_tools)
サンプルエージェントを参照してください。

!!! warning

    組み込みツールはサブエージェント内では使用できません。
    ただし、上記回避策がある ADK Python の
    `GoogleSearchTool` と `VertexAiSearchTool` は例外です。

たとえば、次のようにサブエージェント内で組み込みツールを使う方法は
**サポートされていません**。

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
            .subAgents(searchAgent, codingAgent) // サブエージェントが組み込みツールを使うため非サポート
            .build();
    ```
