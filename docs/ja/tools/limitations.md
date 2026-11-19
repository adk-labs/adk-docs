# ADK ツールの制限事項

一部の ADK ツールには、エージェントのワークフロー内での実装方法に
影響する制限があります。このページでは、それらの制限事項と、
可能な場合の回避策を説明します。

## エージェントごとのツール 1 個制限 {#one-tool-one-agent}

!!! note "ADK Python: 組み込みの Search 回避策はオプトイン方式です"

    ADK Python v1.16.0 以降では、Google Search および Agent Search ツールに対して
    この制限を回避できますが、デフォルトでは有効になっていません。
    `bypass_multi_tools_limit=True` を指定してツールを自分で構築する必要があります。
    `google.adk.tools` からエクスポートされている共有の `google_search` インスタンスでは、
    このフラグはオフのままです。以下の回避策 #2 を参照してください。

一般に、1 つのエージェントで複数のツールを使用できますが、
特定のツールをエージェント内で使う場合、そのエージェントでは他のツールを
併用できません。次の ADK ツールは、1 つのエージェントオブジェクト内で
**単独でのみ（他のツールと併用不可）**使用できます。

*   Gemini API の [Code Execution](/tools/gemini-api/code-execution/)
*   Gemini API の [Google Search](/tools/gemini-api/google-search/)
*   [Vertex AI Search](/integrations/agent-search/)

たとえば、次のようにこれらのツールのいずれかを他ツールと一緒に
単一エージェントで使う方法は ***サポートされていません***。

=== "Python"

    ```py
    root_agent = Agent(
        name="RootAgent",
        model="gemini-flash-latest",
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

### 回避策 #1: エージェントを AgentTool でラップする

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript (v0.6.1+)</span><span class="lst-java">Java</span><span class="lst-kotlin">Kotlin v0.1.0</span>
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

ADK Python では、`AgentTool` はラップされたエージェントのグラウンディング メタデータを呼び出し元のエージェントに返しません。そのメタデータをセッション ステートの `temp:_adk_grounding_metadata` キーの下に保存するには、`AgentTool` に `propagate_grounding_metadata=True` を設定してください。ADK は、親エージェントが `google_search_agent` という名前のツール（以下の回避策 #2 が自動的に作成するツール）を持っている場合にのみ、親エージェント自身の応答にそのメタデータを添付します。

### 回避策 #2: bypass_multi_tools_limit

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-java">Java</span><span class="lst-kotlin">Kotlin v0.1.0</span>
</div>

ADK Python には `GoogleSearchTool` と `VertexAiSearchTool` について
この制限を回避する組み込み機能があります
（`bypass_multi_tools_limit=True` で有効化）。
詳細は
[built_in_multi_tools](https://github.com/google/adk-python/tree/main/contributing/samples/tools/built_in_multi_tools)
サンプルエージェントを参照してください。

たとえば、`google.adk.tools.google_search_tool` からインポートした `GoogleSearchTool(bypass_multi_tools_limit=True)` のように、自分で構築するツール インスタンスにフラグを設定してください。`google.adk.tools` からエクスポートされている共有の `google_search` インスタンスではフラグはオフのままです。このバイパスは、エージェントの `tools` リストに複数のエントリがある場合、または別のエージェントに制御を転送できる場合に有効になります。

!!! warning

    組み込みツールはサブエージェント内では使用できません。ADK Python では、
    サブエージェントが `bypass_multi_tools_limit=True` を指定してツールを構築した場合に限り、
    `GoogleSearchTool` と `VertexAiSearchTool` が例外となります。

たとえば、次のようにサブエージェント内で組み込みツールを使う方法は
**サポートされていません**。

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
            .subAgents(searchAgent, codingAgent) // サブエージェントが組み込みツールを使うため非サポート
            .build();
    ```

## Kotlin の回避策例

Kotlin では、組み込みツールの制限を回避するため、ルートエージェントでのみ組み込みツールを直接構成するパターンを使用できます。

```kotlin
--8<-- "examples/kotlin/snippets/tools/LimitationsWorkaround.kt:workaround_1"
```
