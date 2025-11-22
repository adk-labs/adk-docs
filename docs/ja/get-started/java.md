# ADK用Javaクイックスタート

このガイドでは、Agent Development Kit for Javaを使用して開始する方法について説明します。開始する前に、次のものがインストールされていることを確認してください。

*   Java 17以降
*   Maven 3.9以降

## エージェントプロジェクトを作成する

次のファイルとディレクトリ構造でエージェントプロジェクトを作成します。

```none
my_agent/
    src/main/java/com/example/agent/
                        HelloTimeAgent.java # メインエージェントコード
                        AgentCliRunner.java # コマンドラインインターフェース
    pom.xml                                 # プロジェクト構成
    .env                                    # APIキーまたはプロジェクトID
```

??? tip "コマンドラインを使用してこのプロジェクト構造を作成する"

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

### エージェントコードを定義する

ADK [関数ツール](/adk-docs/ja/tools-custom/function-tools/)のシンプルな実装である`getCurrentTime()`を含む基本的なエージェントのコードを作成します。プロジェクトディレクトリの`HelloTimeAgent.java`ファイルに次のコードを追加します。

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
            .description("指定された都市の現在時刻を伝えます")
            .instruction("""
                あなたは指定された都市の現在時刻を伝えるのに役立つアシスタントです。
                この目的のために'getCurrentTime'ツールを使用してください。
                """)
            .model("gemini-2.5-flash")
            .tools(FunctionTool.create(HelloTimeAgent.class, "getCurrentTime"))
            .build();
    }

    /** モックツールの実装 */
    @Schema(description = "指定された都市の現在時刻を取得します")
    public static Map<String, String> getCurrentTime(
        @Schema(name = "city", description = "時刻を取得する都市の名前") String city) {
        return Map.of(
            "city", city,
            "forecast", "時刻は午前10時30分です。"
        );
    }
}
```

!!! warning "注意: Gemini 3の互換性"

    ADK Java v0.3.0以前は、関数呼び出しの思考署名変更により、
    [Gemini 3 Pro Preview](https://ai.google.dev/gemini-api/docs/models#gemini-3-pro)と互換性がありません。
    代わりにGemini 2.5以下のモデルを使用してください。

### プロジェクトと依存関係を構成する

ADKエージェントプロジェクトには、`pom.xml`プロジェクトファイルに次の依存関係が必要です。

```xml title="my_agent/pom.xml (一部)"
<dependencies>
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>adk-core</artifactId>
        <version>0.3.0</version>
    </dependency>
</dependencies>
```

`pom.xml`プロジェクトファイルを更新して、この依存関係と追加の設定を次の構成コードで含めます。

??? info "プロジェクトの完全な`pom.xml`構成"
    次のコードは、このプロジェクトの完全な`pom.xml`構成を示しています。

    ```xml title="my_agent/pom.xml"
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion>

        <groupId>com.example.agent</groupId>
        <artifactId>adk-agents</artifactId>
        <version>1.0-SNAPSHOT</version>

        <!-- 使用するJavaのバージョンを指定 -->
        <properties>
            <maven.compiler.source>17</maven.compiler.source>
            <maven.compiler.target>17</maven.compiler.target>
            <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        </properties>

        <dependencies>
            <!-- ADKコア依存関係 -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk</artifactId>
                <version>0.3.0</version>
            </dependency>
            <!-- エージェントをデバッグするためのADK開発Web UI -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk-dev</artifactId>
                <version>0.3.0</version>
            </dependency>
        </dependencies>

    </project>
    ```

### APIキーを設定する

このプロジェクトはAPIキーを必要とするGemini APIを使用します。まだGemini APIキーをお持ちでない場合は、Google AI Studioの[APIキー](https://aistudio.google.com/app/apikey)ページでキーを作成してください。

ターミナルウィンドウで、APIキーをプロジェクトの`.env`ファイルに書き込み、環境変数を設定します。

=== "MacOS / Linux"

    ```bash title="更新: my_agent/.env"
    echo 'export GOOGLE_API_KEY="YOUR_API_KEY"' > .env
    ```

=== "Windows"

    ```console title="更新: my_agent/env.bat"
    echo 'set GOOGLE_API_KEY="YOUR_API_KEY"' > env.bat
    ```

??? tip "ADKで他のAIモデルを使用する"
    ADKは多くの生成AIモデルの使用をサポートしています。ADKエージェントで他のモデルを構成する方法の詳細については、[モデルと認証](/adk-docs/ja/agents/models)を参照してください。

### エージェントコマンドラインインターフェースを作成する

`AgentCliRunner.java`クラスを作成して、コマンドラインから`HelloTimeAgent`を実行し、対話できるようにします。このコードは、エージェントを実行するための`RunConfig`オブジェクトと、実行中のエージェントと対話するための`Session`オブジェクトを作成する方法を示しています。

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

## エージェントを実行する

定義した対話型コマンドラインインターフェース`AgentCliRunner`クラス、または`AdkWebServer`クラスを使用してADKが提供するADKウェブユーザーインターフェースを使用して、ADKエージェントを実行できます。これらのオプションの両方で、エージェントをテストして対話できます。

### コマンドラインインターフェースで実行する

次のMavenコマンドを使用して、コマンドラインインターフェース`AgentCliRunner`クラスでエージェントを実行します。

```console
# キーと設定をロードする: source .env または env.bat
mvn compile exec:java -Dexec.mainClass="com.example.agent.AgentCliRunner"
```

![adk-run.png](/adk-docs/ja/assets/adk-run.png)

### ウェブインターフェースで実行する

次のMavenコマンドを使用して、ADKウェブインターフェースでエージェントを実行します。

```console
# キーと設定をロードする: source .env または env.bat
mvn compile exec:java \
    -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
    -Dexec.args="--adk.agents.source-dir=target --server.port=8000"
```

このコマンドは、エージェント用のチャットインターフェースを備えたウェブサーバーを起動します。ウェブインターフェースは(http://localhost:8000)でアクセスできます。左上隅でエージェントを選択し、リクエストを入力します。

![adk-web-dev-ui-chat.png](/adk-docs/ja/assets/adk-web-dev-ui-chat.png)

## 次へ: エージェントを構築する

ADKがインストールされ、最初のエージェントが実行中になったので、ビルドガイドを使用して独自のエージェントを構築してみてください。

*  [エージェントを構築する](/adk-docs/ja/tutorials/)

```