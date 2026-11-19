# App ワークフロー管理クラス

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.14.0</span><span class="lst-typescript">TypeScript v1.4.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v0.4.0</span>
</div>

***App*** クラスは、Agent Development Kit（ADK）のエージェントワークフロー全体を管理する最上位コンテナです。*ルートエージェント*によってグループ化されたエージェント群のライフサイクル、構成、および状態を管理するように設計されています。**App** クラスは、エージェントワークフロー全体の運用インフラストラクチャと、個々のエージェントのタスク指向の推論との間で関心の分離を実現します。

ADK ワークフローでの ***App*** オブジェクトの定義は任意ですが、定義するとエージェントコードの構成方法や実行方法が変わります。実務上は、***App*** クラスを使用してエージェントワークフローの以下の機能を構成します。

*   [**コンテキストキャッシュ**](/ja/context/caching/)
*   [**コンテキスト圧縮**](/ja/context/compaction/)
*   [**エージェントの再開**](/ja/runtime/resume/)
*   [**プラグイン**](/ja/plugins/)

このガイドでは、ADK エージェントワークフローの構成と管理に `App` クラスを使用する方法について説明します。

## App クラスの目的

***App*** クラスは、複雑なエージェントシステムを構築する際に発生するいくつかのアーキテクチャ上の課題に対処します。

*   **一元化された構成:** API キーやデータベースクライアントなどの共有リソースを管理するための一元的な場所を提供し、すべてのエージェントに構成を引き回す必要がなくなります。
*   **ライフサイクル管理:** ***App*** クラスには起動時（on startup）およびシャットダウン時（on shutdown）のフックが含まれており、複数の呼び出しにわたって維持する必要があるデータベース接続プールやインメモリキャッシュなどの永続的なリソースを確実に管理できます。
*   **状態スコープ:** `app:*` プレフィックスを使用してアプリケーションレベルの状態に明示的な境界を定義し、この状態のスコープとライフタイムを開発者に明確にします。
*   **デプロイ単位:** ***App*** の概念は正式な*デプロイ可能単位*を確立し、エージェントアプリケーションのバージョン管理、テスト、およびサービングを簡素化します。

## App オブジェクトを定義する

***App*** クラスはエージェントワークフローのプライマリコンテナとして使用され、プロジェクトのルートエージェントを保持します。*ルートエージェント*は、プライマリコントローラエージェントおよび追加のサブエージェントのコンテナです。

### ルートエージェントを使って App を定義する

***Agent*** クラスのインスタンスを作成して、ワークフローの*ルートエージェント*を作成します。次に、以下のサンプルコードに示すように ***App*** オブジェクトを定義し、ルートエージェントオブジェクトとオプション機能を設定します。

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
        # オプションで App レベル機能を含める:
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
      // オプションで App レベル機能を含める:
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
        // オプションで App レベル機能を含める:
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

!!! tip "推奨：`app` 変数名を使用する"

    エージェントプロジェクトのコードでは、ADK コマンドラインインターフェース（CLI）のランナーツールと互換性を持たせるため、***App*** オブジェクトの変数名を `app` に設定してください。

### App エージェントを実行する

以下のコードサンプルに示すように、***Runner*** クラスの `app` パラメータを指定してエージェントワークフローを実行できます。

=== "Python"

    ```python title="main.py"
    import asyncio
    from dotenv import load_dotenv
    from google.adk.runners import InMemoryRunner
    from agent import app # agent.pyからコードをインポート

    load_dotenv() # APIキーと設定を読み込む
    # インポートされたアプリケーションオブジェクトを使用してランナーを設定する
    runner = InMemoryRunner(app=app)

    async def main():
        try:  # run_debug()にはADK Python 1.18以降が必要です。
            response = await runner.run_debug("Hello there!")

        except Exception as e:
            print(f"An error occurred during agent execution: {e}")

    if __name__ == "__main__":
        asyncio.run(main())

    ```

=== "TypeScript"

    ```typescript title="main.ts"
    import {InMemoryRunner, isFinalResponse, stringifyContent} from '@google/adk';
    import {app} from './agent.js'; // agent.tsからコードをインポート

    // インポートされたアプリケーションオブジェクトを使用してランナーを設定する
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
        // アプリケーションオブジェクトを使って Runner を設定する

        App app = ...;

        Runner runner = Runner.builder()
            .app(app) // 先ほど定義した 'app' オブジェクトを使用
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

!!! note "`Runner.run_debug()` のバージョン要件"

    `Runner.run_debug()` メソッドには、ADK Python v1.18.0 以降が必要です。より多くのセットアップコードが必要になる `Runner.run()` を使用することもできます。詳細については、[エージェントランタイム](/ja/runtime/)ガイドを参照してください。

=== "Python"

    次のコマンドを使用して、`main.py`コードでAppエージェントを実行します。

    ```console
    python3 main.py
    ```

=== "TypeScript"

    次のコマンドを使用して、`main.ts`コードでAppエージェントを実行します。

    ```console
    npx tsx main.ts
    ```

=== "Java"

    `AppMain.java` コードで App エージェントを実行するには、ビルドツール（例: Gradle `application` プラグイン）を使用します。

    ```console
    ./gradlew run
    ```

=== "Kotlin"

    `Main.kt` コードで App エージェントを実行するには、ビルドツール（例: Gradle `application` プラグイン）を使用します。

    ```console
    ./gradlew run
    ```

## 次のステップ

より完全なサンプルコードの実装については、[Hello Worldアプリ](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_app)のコード例を参照してください。
