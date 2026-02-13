# エージェント設定でエージェントを構築する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.11.0</span><span class="lst-preview">実験的</span>
</div>

ADKエージェント設定機能を使用すると、コードを記述することなくADKワークフローを構築できます。エージェント設定は、エージェントの簡単な説明を含むYAML形式のテキストファイルを使用するため、誰でもADKエージェントを組み立てて実行できます。以下は、基本的なエージェント設定定義の簡単な例です。

```
name: assistant_agent
model: gemini-2.5-flash
description: ユーザーの質問に回答できるヘルパーエージェント。
instruction: ユーザーのさまざまな質問に回答するエージェントです。
```

エージェント設定ファイルを使用して、関数、ツール、サブエージェントなどを組み込むことができる、より複雑なエージェントを構築できます。このページでは、エージェント設定機能を使用してADKワークフローを構築および実行する方法について説明します。エージェント設定形式でサポートされている構文と設定の詳細については、[エージェント設定構文リファレンス](/adk-docs/ja/api-reference/agentconfig/)を参照してください。

!!! example "実験的"
    エージェント設定機能は実験的なものであり、いくつかの[既知の制限](#known-limitations)があります。[フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=agent%20config)を歓迎します！

## はじめに

このセクションでは、インストール設定、エージェントの構築、エージェントの実行など、ADKとエージェント設定機能を使用してエージェントの構築を開始する方法について説明します。

### セットアップ

Google Agent Development Kitライブラリをインストールし、Gemini APIなどの生成AIモデルのアクセスキーを提供する必要があります。このセクションでは、エージェント設定ファイルでエージェントを実行する前にインストールおよび構成する必要があるものについて詳しく説明します。

!!! note
    エージェント設定機能は現在、Geminiモデルのみをサポートしています。追加の機能制限の詳細については、[既知の制限](#known-limitations)を参照してください。

エージェント設定で使用するためにADKをセットアップするには：

1.  [インストール](/adk-docs/ja/get-started/installation/#python)の手順に従ってADK Pythonライブラリをインストールします。 *現在Pythonが必要です。* 詳細については、[既知の制限](#known-limitations)を参照してください。
1.  ターミナルで次のコマンドを実行して、ADKがインストールされていることを確認します。

        adk --version

    このコマンドは、インストールされているADKのバージョンを表示します。

!!! Tip
    `adk`コマンドが実行されず、ステップ2でバージョンが一覧表示されない場合は、Python環境がアクティブであることを確認してください。MacおよびLinuxのターミナルで`source .venv/bin/activate`を実行します。他のプラットフォームコマンドについては、[インストール](/adk-docs/ja/get-started/installation/#python)ページを参照してください。

### エージェントを構築する

`adk create`コマンドを使用してエージェント設定でエージェントを構築し、エージェントのプロジェクトファイルを作成し、生成された`root_agent.yaml`ファイルを編集します。

エージェント設定で使用するためにADKプロジェクトを作成するには：

1.  ターミナルウィンドウで、次のコマンドを実行して設定ベースのエージェントを作成します。

        adk create --type=config my_agent

    このコマンドは、`root_agent.yaml`ファイルと`.env`ファイルを含む`my_agent/`フォルダを生成します。

1.  `my_agent/.env`ファイルで、エージェントが生成AIモデルやその他のサービスにアクセスできるように環境変数を設定します。

    1.  Google APIを介してGeminiモデルにアクセスするには、APIキーを含む行をファイルに追加します。

            GOOGLE_GENAI_USE_VERTEXAI=0
            GOOGLE_API_KEY=<your-Google-Gemini-API-key>

        Google AI Studioの[APIキー](https://aistudio.google.com/app/apikey)ページからAPIキーを取得できます。

    1.  Google Cloudを介してGeminiモデルにアクセスするには、次の行をファイルに追加します。

            GOOGLE_GENAI_USE_VERTEXAI=1
            GOOGLE_CLOUD_PROJECT=<your_gcp_project>
            GOOGLE_CLOUD_LOCATION=us-central1

        Cloudプロジェクトの作成の詳細については、Google Cloudドキュメントの[プロジェクトの作成と管理](https://cloud.google.com/resource-manager/docs/creating-managing-projects)を参照してください。

1.  テキストエディタを使用して、以下に示すようにエージェント設定ファイル`my_agent/root_agent.yaml`を編集します。

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
name: assistant_agent
model: gemini-2.5-flash
description: ユーザーの質問に回答できるヘルパーエージェント。
instruction: ユーザーのさまざまな質問に回答するエージェントです。
```

ADKの[サンプルリポジトリ](https://github.com/search?q=repo%3Agoogle%2Fadk-python+path%3A%2F%5Econtributing%5C%2Fsamples%5C%2F%2F+.yaml&type=code)または[エージェント設定構文](/adk-docs/ja/api-reference/agentconfig/)リファレンスを参照して、`root_agent.yaml`エージェント設定ファイルのより多くの設定オプションを見つけることができます。

### エージェントを実行する

エージェント設定の編集が完了したら、Webインターフェース、コマンドラインターミナル実行、またはAPIサーバーモードを使用してエージェントを実行できます。

エージェント設定で定義されたエージェントを実行するには：

1.  ターミナルで、`root_agent.yaml`ファイルを含む`my_agent/`ディレクトリに移動します。
1.  次のいずれかのコマンドを入力してエージェントを実行します。
    -   `adk web` - エージェントのWeb UIインターフェースを実行します。
    -   `adk run` - ユーザーインターフェースなしでターミナルでエージェントを実行します。
    -   `adk api_server` - 他のアプリケーションで使用できるサービスとしてエージェントを実行します。

エージェントの実行方法の詳細については、[クイックスタート](/adk-docs/ja/get-started/quickstart/#run-your-agent)の*エージェントを実行する*トピックを参照してください。ADKコマンドラインオプションの詳細については、[ADK CLIリファレンス](/adk-docs/ja/api-reference/cli/)を参照してください。

## サンプルの設定

このセクションでは、エージェントの構築を開始するためのエージェント設定ファイルの例を示します。追加のより完全な例については、ADKの[サンプルリポジトリ](https://github.com/search?q=repo%3Agoogle%2Fadk-python+path%3A%2F%5Econtributing%5C%2Fsamples%5C%2F%2F+root_agent.yaml&type=code)を参照してください。

### 組み込みツールの例

次の例では、Google検索を使用してエージェントに機能を提供する組み込みADKツール関数を使用します。このエージェントは、ユーザー要求に自動的に検索ツールを使用して応答します。

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
name: search_agent
model: gemini-2.0-flash
description: 'Google検索クエリを実行し、結果に関する質問に回答するエージェント。'
instruction: Google検索クエリを実行し、結果に関する質問に回答するエージェントです。
tools:
  - name: google_search
```

詳細については、[ADKサンプルリポジトリ](https://github.com/google/adk-python/blob/main/contributing/samples/tool_builtin_config/root_agent.yaml)でこのサンプルの完全なコードを参照してください。

### カスタムツールの例

次の例では、Pythonコードで構築され、設定ファイルの`tools:`セクションにリストされているカスタムツールを使用します。エージェントはこのツールを使用して、ユーザーが提供した数値のリストが素数であるかどうかを確認します。

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
model: gemini-2.5-flash
name: prime_agent
description: 数値が素数であるかどうかの確認を処理します。
instruction: |
  数値が素数であるかどうかの確認を担当します。
  素数であるかどうかの確認を求められた場合は、整数のリストでcheck_primeツールを呼び出す必要があります。
  手動で素数を判別しようとしないでください。
  素数の結果をルートエージェントに返します。
tools:
  - name: ma_llm.check_prime
```

詳細については、[ADKサンプルリポジトリ](https://github.com/google/adk-python/blob/main/contributing/samples/multi_agent_llm_config/prime_agent.yaml)でこのサンプルの完全なコードを参照してください。

### サブエージェントの例

次の例は、`sub_agents:`セクションに2つのサブエージェントと`tools:`セクションにサンプルツールが定義されたエージェントを示しています。このエージェントは、ユーザーが何を望んでいるかを判断し、サブエージェントの1つにリクエストを解決するように委任します。サブエージェントはエージェント設定YAMLファイルを使用して定義されます。

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
model: gemini-2.5-flash
name: root_agent
description: コードと数学の個別指導を提供する学習アシスタント。
instruction: |
  コードと数学の質問で生徒を助ける学習アシスタントです。

  プログラミングに関する質問はcode_tutor_agentに、数学に関する質問はmath_tutor_agentに委任します。

  次の手順に従ってください。
  1. ユーザーがプログラミングやコーディングについて質問した場合は、code_tutor_agentに委任します。
  2. ユーザーが数学の概念や問題について質問した場合は、math_tutor_agentに委任します。
  3. 常に明確な説明を提供し、学習を促します。
sub_agents:
  - config_path: code_tutor_agent.yaml
  - config_path: math_tutor_agent.yaml
```

詳細については、[ADKサンプルリポジトリ](https://github.com/google/adk-python/blob/main/contributing/samples/multi_agent_basic_config/root_agent.yaml)でこのサンプルの完全なコードを参照してください。

## エージェント設定のデプロイ

コードベースのエージェントと同じ手順で、[Cloud Run](/adk-docs/ja/deploy/cloud-run/)および[エージェントエンジン](/adk-docs/ja/deploy/agent-engine/)を使用してエージェント設定エージェントをデプロイできます。エージェント設定ベースのエージェントを準備およびデプロイする方法の詳細については、[Cloud Run](/adk-docs/ja/deploy/cloud-run/)および[エージェントエンジン](/adk-docs/ja/deploy/agent-engine/)のデプロイガイドを参照してください。

## 既知の制限 {#known-limitations}

エージェント設定機能は実験的なものであり、次の制限が含まれています。

-   **モデルのサポート:** 現在、Geminiモデルのみがサポートされています。サードパーティモデルとの統合は進行中です。
-   **プログラミング言語:** エージェント設定機能は現在、ツールやプログラミングコードを必要とするその他の機能に対してPythonコードのみをサポートしています。
-   **ADKツールのサポート:** 次のADKツールはエージェント設定機能でサポートされていますが、*すべてのツールが完全にサポートされているわけではありません*。
    -   `google_search`
    -   `load_artifacts`
    -   `url_context`
    -   `exit_loop`
    -   `preload_memory`
    -   `get_user_choice`
    -   `enterprise_web_search`
    -   `load_web_page`: ウェブページにアクセスするには完全修飾パスが必要です。
-   **エージェントタイプのサポート:** `LangGraphAgent`および`A2aAgent`タイプはまだサポートされていません。
    -   `AgentTool`
    -   `LongRunningFunctionTool`
    -   `VertexAiSearchTool`
    -   `McpToolset`
    -   `ExampleTool`

## 次のステップ

ADKエージェント設定で何をどのように構築するかについてのアイデアは、ADKの[adk-samples](https://github.com/search?q=repo:google/adk-python+path:/%5Econtributing%5C/samples%5C//+root_agent.yaml&type=code)リポジトリのYAMLベースのエージェント定義を参照してください。エージェント設定形式でサポートされている構文と設定の詳細については、[エージェント設定構文リファレンス](/adk-docs/ja/api-reference/agentconfig/)を参照してください。