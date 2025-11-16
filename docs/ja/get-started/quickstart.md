# マルチツールエージェントの構築

このクイックスタートでは、Agent Development Kit (ADK)のインストール、複数のツールを持つ基本的なエージェントのセットアップ、そしてターミナルまたはインタラクティブなブラウザベースの開発UIでローカルに実行するまでをガイドします。

<!-- <img src="../../assets/quickstart.png" alt="Quickstart setup"> -->

このクイックスタートは、Python 3.9以上またはJava 17以上がインストールされたローカルIDE（VS Code、PyCharm、IntelliJ IDEAなど）とターミナルアクセスが利用できることを前提としています。この方法は、アプリケーションを完全にあなたのマシン上で実行するもので、内部開発に推奨されます。

## 1. 環境のセットアップとADKのインストール { #set-up-environment-install-adk }

=== "Python"

    仮想環境の作成と有効化 (推奨):

    ```bash
    # 作成
    python -m venv .venv
    # 有効化 (新しいターミナルごと)
    # macOS/Linux: source .venv/bin/activate
    # Windows CMD: .venv\Scripts\activate.bat
    # Windows PowerShell: .venv\Scripts\Activate.ps1
    ```

    ADKのインストール:

    ```bash
    pip install google-adk
    ```

=== "Java"

    ADKをインストールして環境をセットアップするには、次の手順に進んでください。

## 2. エージェントプロジェクトの作成 { #create-agent-project }

### プロジェクト構造

=== "Python"

    以下のプロジェクト構造を作成する必要があります:

    ```console
    parent_folder/
        multi_tool_agent/
            __init__.py
            agent.py
            .env
    ```

    `multi_tool_agent` フォルダを作成します:

    ```bash
    mkdir multi_tool_agent/
    ```

    !!! info "Windowsユーザー向けの注意"

        次のいくつかのステップでWindows上でADKを使用する際、`mkdir`や`echo`のようなコマンドはヌルバイトや不正なエンコーディングでファイルを生成することがあるため、ファイルエクスプローラーまたはIDEを使用してPythonファイルを作成することをお勧めします。

    ### `__init__.py`

    次に、フォルダ内に `__init__.py` ファイルを作成します:

    ```shell
    echo "from . import agent" > multi_tool_agent/__init__.py
    ```

    これで、`__init__.py` は以下のようになります:

    ```python title="multi_tool_agent/__init__.py"
    --8<-- "examples/python/snippets/get-started/multi_tool_agent/__init__.py"
    ```

    ### `agent.py`

    同じフォルダに `agent.py` ファイルを作成します:

    === "OS X &amp; Linux"
        ```shell
        touch multi_tool_agent/agent.py
        ```

    === "Windows"
        ```shell
        type nul > multi_tool_agent/agent.py
        ```

    以下のコードをコピーして `agent.py` に貼り付けます:

    ```python title="multi_tool_agent/agent.py"
    --8<-- "examples/python/snippets/get-started/multi_tool_agent/agent.py"
    ```

    ### `.env`

    同じフォルダに `.env` ファイルを作成します:

    === "OS X &amp; Linux"
        ```shell
        touch multi_tool_agent/.env
        ```

    === "Windows"
        ```shell
        type nul > multi_tool_agent\.env
        ```

    このファイルに関する詳細は、次のセクション [モデルのセットアップ](#set-up-the-model) で説明します。

=== "Java"

    Javaプロジェクトは一般的に以下のプロジェクト構造を持ちます:

    ```console
    project_folder/
    ├── pom.xml (or build.gradle)
    ├── src/
    ├── └── main/
    │       └── java/
    │           └── agents/
    │               └── multitool/
    └── test/
    ```

    ### `MultiToolAgent.java`の作成

    `src/main/java/agents/multitool/` ディレクトリ内の `agents.multitool` パッケージに `MultiToolAgent.java` ソースファイルを作成します。

    以下のコードをコピーして `MultiToolAgent.java` に貼り付けます:

    ```java title="agents/multitool/MultiToolAgent.java"
    --8<-- "examples/java/cloud-run/src/main/java/agents/multitool/MultiToolAgent.java:full_code"
    ```

![intro_components.png](../assets/quickstart-flow-tool.png)

## 3. モデルのセットアップ { #set-up-the-model }

エージェントがユーザーの要求を理解し、応答を生成する能力は、大規模言語モデル（LLM）によって実現されています。エージェントはこの外部LLMサービスに安全な呼び出しを行う必要があり、そのためには**認証情報**が必要です。有効な認証情報がない場合、LLMサービスはエージェントの要求を拒否し、エージェントは機能できなくなります。

!!!tip "モデル認証ガイド"
    様々なモデルへの認証に関する詳細なガイドは、[認証ガイド](../agents/models.md#google-ai-studio) を参照してください。
    これは、エージェントがLLMサービスへの呼び出しを行えるようにするための重要なステップです。

=== "Gemini - Google AI Studio"
    1. [Google AI Studio](https://aistudio.google.com/apikey) から API キーを取得します。
    2. Pythonを使用する場合、(`multi_tool_agent/` 内にある) **`.env`** ファイルを開き、以下のコードをコピー＆ペーストします。

        ```env title="multi_tool_agent/.env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

        Javaを使用する場合、環境変数を定義します:

        ```console title="terminal"
        export GOOGLE_GENAI_USE_VERTEXAI=FALSE
        export GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3. `PASTE_YOUR_ACTUAL_API_KEY_HERE` を実際の `APIキー` に置き換えてください。

=== "Gemini - Google Cloud Vertex AI"
    1. [Google Cloud プロジェクトをセットアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)し、[Vertex AI API を有効化](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)します。
    2. [gcloud CLI をセットアップ](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)します。
    3. ターミナルから `gcloud auth application-default login` を実行してGoogle Cloudに認証します。
    4. Pythonを使用する場合、(`multi_tool_agent/` 内にある) **`.env`** ファイルを開き、以下のコードをコピー＆ペーストし、プロジェクトIDとロケーションを更新します。

        ```env title="multi_tool_agent/.env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=LOCATION
        ```

        Javaを使用する場合、環境変数を定義します:

        ```console title="terminal"
        export GOOGLE_GENAI_USE_VERTEXAI=TRUE
        export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
        export GOOGLE_CLOUD_LOCATION=LOCATION
        ```

=== "Gemini - Google Cloud Vertex AI (Express モード)"
    1. 無料のGoogle Cloudプロジェクトにサインアップし、対象アカウントでGeminiを無料で使用できます！
        * [Vertex AI Express モードでGoogle Cloudプロジェクトをセットアップする](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)
        * Express モードのプロジェクトからAPIキーを取得します。このキーをADKで使用すると、Geminiモデルを無料で使用できるほか、Agent Engineサービスにもアクセスできます。
    2. Pythonを使用する場合、(`multi_tool_agent/` 内にある) **`.env`** ファイルを開き、以下のコードをコピー＆ペーストし、プロジェクトIDとロケーションを更新します。

        ```env title="multi_tool_agent/.env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
        ```

        Javaを使用する場合、環境変数を定義します:

        ```console title="terminal"
        export GOOGLE_GENAI_USE_VERTEXAI=TRUE
        export GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_EXPRESS_MODE_API_KEY_HERE
        ```

## 4. エージェントの実行 { #run-your-agent }

=== "Python"

    ターミナルを使い、エージェントプロジェクトの親ディレクトリに移動します（例: `cd ..`を使用）:

    ```console
    parent_folder/      <-- このディレクトリに移動
        multi_tool_agent/
            __init__.py
            agent.py
            .env
    ```

    エージェントと対話するには複数の方法があります:

    === "開発UI (adk web)"

        !!! success "Vertex AIユーザー向けの認証設定"
            前のステップで **"Gemini - Google Cloud Vertex AI"** を選択した場合は、開発UIを起動する前にGoogle Cloudで認証する必要があります。

            このコマンドを実行し、プロンプトに従ってください:
            ```bash
            gcloud auth application-default login
            ```

            **注意:** "Gemini - Google AI Studio" を使用している場合は、このステップをスキップしてください。

        以下のコマンドを実行して **開発UI** を起動します。

        ```shell
        adk web
        ```

        !!!info "Windowsユーザー向けの注意"

            `_make_subprocess_transport NotImplementedError` が発生した場合は、代わりに `adk web --no-reload` の使用を検討してください。


        **ステップ1:** 提供されたURL（通常は `http://localhost:8000` または `http://127.0.0.1:8000`）をブラウザで直接開きます。

        **ステップ2:** UIの左上にあるドロップダウンでエージェントを選択できます。「multi_tool_agent」を選択します。

        !!!note "トラブルシューティング"

            ドロップダウンメニューに「multi_tool_agent」が表示されない場合は、`adk web` をエージェントフォルダの**親フォルダ**（つまり、multi_tool_agent の親フォルダ）で実行していることを確認してください。

        **ステップ3:** テキストボックスを使ってエージェントとチャットできます:

        ![adk-web-dev-ui-chat.png](../assets/adk-web-dev-ui-chat.png)


        **ステップ4:** 左側の `Events` タブを使い、アクションをクリックすることで、個々の関数呼び出し、応答、モデルの応答を検査できます:

        ![adk-web-dev-ui-function-call.png](../assets/adk-web-dev-ui-function-call.png)

        `Events` タブでは、`Trace` ボタンをクリックして各イベントのトレースログを確認することもでき、各関数呼び出しのレイテンシーが表示されます:

        ![adk-web-dev-ui-trace.png](../assets/adk-web-dev-ui-trace.png)

        **ステップ5:** マイクを有効にしてエージェントと話すこともできます:

        !!!note "音声/動画ストリーミングのモデルサポート"

            ADKで音声/動画ストリーミングを使用するには、Live APIをサポートするGeminiモデルを使用する必要があります。Gemini Live APIをサポートする**モデルID**は、ドキュメントで確認できます:

            - [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
            - [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

            その後、先に作成した`agent.py`ファイル内の`root_agent`にある`model`文字列を置き換えることができます ([セクションにジャンプ](#agentpy))。コードは次のようになります:

            ```py
            root_agent = Agent(
                name="weather_time_agent",
                model="モデルIDに置き換えてください", #例: gemini-2.0-flash-live-001
                ...
            ```

        ![adk-web-dev-ui-audio.png](../assets/adk-web-dev-ui-audio.png)

    === "ターミナル (adk run)"

        !!! tip

            `adk run` を使用する際、次のようにテキストをコマンドにパイプすることで、エージェントにプロンプトを注入して開始できます:

            ```shell
            echo "Please start by listing files" | adk run file_listing_agent
            ```

        以下のコマンドを実行して、Weatherエージェントとチャットします。

        ```
        adk run multi_tool_agent
        ```

        ![adk-run.png](../assets/adk-run.png)

        終了するには、Cmd/Ctrl+C を使用します。

    === "APIサーバー (adk api_server)"

        `adk api_server` を使用すると、単一のコマンドでローカルのFastAPIサーバーを作成でき、エージェントをデプロイする前にローカルのcURLリクエストをテストできます。

        ![adk-api-server.png](../assets/adk-api-server.png)

        テストのために `adk api_server` を使用する方法については、[APIサーバーの使用に関するドキュメント](/adk-docs/runtime/api-server/) を参照してください。

=== "Java"

    ターミナルを使い、エージェントプロジェクトの親ディレクトリに移動します（例: `cd ..`を使用）:

    ```console
    project_folder/                <-- このディレクトリに移動
    ├── pom.xml (or build.gradle)
    ├── src/
    ├── └── main/
    │       └── java/
    │           └── agents/
    │               └── multitool/
    │                   └── MultiToolAgent.java
    └── test/
    ```

    === "開発UI"

        ターミナルから以下のコマンドを実行して開発UIを起動します。

        **開発UIサーバーのメインクラス名は変更しないでください。**

        ```console title="terminal"
        mvn exec:java \
            -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
            -Dexec.args="--adk.agents.source-dir=src/main/java" \
            -Dexec.classpathScope="compile"
        ```

        **ステップ1:** 提供されたURL（通常は `http://localhost:8080` または `http://127.0.0.1:8080`）をブラウザで直接開きます。

        **ステップ2:** UIの左上にあるドロップダウンでエージェントを選択できます。「multi_tool_agent」を選択します。

        !!!note "トラブルシューティング"

            ドロップダウンメニューに「multi_tool_agent」が表示されない場合は、`mvn` コマンドをJavaソースコードがある場所（通常は `src/main/java`）で実行していることを確認してください。

        **ステップ3:** テキストボックスを使ってエージェントとチャットできます:

        ![adk-web-dev-ui-chat.png](../assets/adk-web-dev-ui-chat.png)

        **ステップ4:** アクションをクリックすることで、個々の関数呼び出し、応答、モデルの応答を検査することもできます:

        ![adk-web-dev-ui-function-call.png](../assets/adk-web-dev-ui-function-call.png)

    === "Maven"

        Mavenでは、以下のコマンドでJavaクラスの `main()` メソッドを実行します:

        ```console title="terminal"
        mvn compile exec:java -Dexec.mainClass="agents.multitool.MultiToolAgent"
        ```

    === "Gradle"

        Gradleでは、`build.gradle` または `build.gradle.kts` ビルドファイルの `plugins` セクションに以下のJavaプラグインが必要です:

        ```groovy
        plugins {
            id('java')
            // other plugins
        }
        ```

        次に、ビルドファイルの別の場所（トップレベル）で、エージェントの `main()` メソッドを実行するための新しいタスクを作成します:

        ```groovy
        tasks.register('runAgent', JavaExec) {
            classpath = sourceSets.main.runtimeClasspath
            mainClass = 'agents.multitool.MultiToolAgent'
        }
        ```

        最後に、コマンドラインで以下のコマンドを実行します:

        ```console
        gradle runAgent
        ```

### 📝 試してみるプロンプトの例

* ニューヨークの天気は？
* ニューヨークの今の時間は？
* パリの天気は？
* パリの今の時間は？

## 🎉 おめでとうございます！

ADKを使用して、最初のエージェントの作成と対話に成功しました！

---

## 🛣️ 次のステップ

* **チュートリアルに進む**: エージェントにメモリ、セッション、状態を追加する方法を学びます:
  [チュートリアル](../tutorials/index.md)。
* **高度な設定を掘り下げる:** プロジェクト構造、設定、その他のインターフェースについて深く知るには、[セットアップ](installation.md)セクションを参照してください。
* **コアコンセプトを理解する:** [エージェントの概念](../agents/index.md)について学びます。