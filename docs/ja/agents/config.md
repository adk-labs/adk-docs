# エージェント構成でエージェントを構築する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.11.0</span><span class="lst-preview">実験的</span>
</div>

ADKエージェント構成機能を使用すると、コードを記述せずにADKワークフローを構築できます。エージェント構成は、エージェントの簡単な説明を含むYAML形式のテキストファイルを使用するため、誰でもADKエージェントを組み立てて実行できます。以下は、基本的なエージェント構成定義の簡単な例です。

```
name: assistant_agent
model: gemini-2.5-flash
description: ユーザーの質問に答えることができるヘルパーエージェント。
instruction: あなたは、ユーザーのさまざまな質問に答えるのに役立つエージェントです。
```

エージェント構成ファイルを使用して、関数、ツール、サブエージェントなどを組み込むことができる、より複雑なエージェントを構築できます。このページでは、エージェント構成機能を使用してADKワークフローを構築および実行する方法について説明します。エージェント構成形式でサポートされている構文と設定の詳細については、[エージェント構成構文リファレンス](/adk-docs/api-reference/agentconfig/)を参照してください。

!!! example "実験的"
    エージェント構成機能は実験的なものであり、いくつかの[既知の制限](#known-limitations)があります。[フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=agent%20config)をお待ちしております。

## はじめに

このセクションでは、インストール設定、エージェントの構築、エージェントの実行など、ADKとエージェント構成機能を使用してエージェントの構築を開始および設定する方法について説明します。

### セットアップ

Google Agent Development Kitライブラリをインストールし、Gemini APIなどの生成AIモデルのアクセスキーを提供する必要があります。このセクションでは、エージェント構成ファイルを使用してエージェントを実行する前にインストールおよび構成する必要があるものについて詳しく説明します。

!!! note
    エージェント構成機能は現在、Geminiモデルのみをサポートしています。追加の機能制限の詳細については、[既知の制限](#known-limitations)を参照してください。

エージェント構成で使用するためにADKをセットアップするには：

1.  [インストール](/adk-docs/get-started/installation/#python)の指示に従って、ADK Pythonライブラリをインストールします。*現在、Pythonが必要です。*詳細については、[既知の制限](?tab=t.0#heading=h.xefmlyt7zh0i)を参照してください。
2.  ターミナルで次のコマンドを実行して、ADKがインストールされていることを確認します。

        adk --version

    このコマンドは、インストールしたADKのバージョンを表示するはずです。

!!! Tip
    ステップ2で`adk`コマンドの実行に失敗し、バージョンが表示されない場合は、Python環境がアクティブであることを確認してください。MacおよびLinuxのターミナルで`source .venv/bin/activate`を実行します。その他のプラットフォームコマンドについては、[インストール](/adk-docs/get-started/installation/#python)ページを参照してください。

### エージェントを構築する

エージェント構成でエージェントを構築するには、`adk create`コマンドを使用してエージェントのプロジェクトファイルを作成し、生成された`root_agent.yaml`ファイルを編集します。

エージェント構成で使用するADKプロジェクトを作成するには：

1.  ターミナルウィンドウで、次のコマンドを実行して構成ベースのエージェントを作成します。

        adk create --type=config my_agent

    このコマンドは、`root_agent.yaml`ファイルと`.env`ファイルを含む`my_agent/`フォルダーを生成します。

2.  `my_agent/.env`ファイルで、エージェントが生成AIモデルやその他のサービスにアクセスするための環境変数を設定します。

    1.  Google APIを介したGeminiモデルへのアクセスについては、APIキーを含む行をファイルに追加します。

            GOOGLE_GENAI_USE_VERTEXAI=0
            GOOGLE_API_KEY=<your-Google-Gemini-API-key>

        Google AI Studioの[APIキー](https://aistudio.google.com/app/apikey)ページからAPIキーを取得できます。

    2.  Google Cloudを介したGeminiモデルへのアクセスについては、これらの行をファイルに追加します。

            GOOGLE_GENAI_USE_VERTEXAI=1
            GOOGLE_CLOUD_PROJECT=<your_gcp_project>
            GOOGLE_CLOUD_LOCATION=us-central1

        Cloudプロジェクトの作成の詳細については、[プロジェクトの作成と管理](https://cloud.google.com/resource-manager/docs/creating-managing-projects)に関するGoogle Cloudのドキュメントを参照してください。

3.  テキストエディタを使用して、以下に示すようにエージェント構成ファイル`my_agent/root_agent.yaml`を編集します。

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
name: assistant_agent
model: gemini-2.5-flash
description: ユーザーの質問に答えることができるヘルパーエージェント。
instruction: あなたは、ユーザーのさまざまな質問に答えるのに役立つエージェントです。
```

ADK[サンプルリポジトリ](https://github.com/search?q=repo%3Agoogle%2Fadk-python+path%3A%2F%5Econtributing%5C%2Fsamples%5C%2F%2F+.yaml&type=code)または[エージェント構成構文](/adk-docs/api-reference/agentconfig/)リファレンスを参照して、`root_agent.yaml`エージェント構成ファイルのその他の構成オプションを見つけることができます。

### エージェントを実行する

エージェント構成の編集が完了したら、Webインターフェイス、コマンドラインターミナル実行、またはAPIサーバーモードを使用してエージェントを実行できます。

エージェント構成で定義されたエージェントを実行するには：

1.  ターミナルで、`root_agent.yaml`ファイルを含む`my_agent/`ディレクトリに移動します。
2.  次のいずれかのコマンドを入力して、エージェントを実行します。
    -   `adk web` - エージェントのWeb UIインターフェイスを実行します。
    -   `adk run` - ユーザーインターフェイスなしでターミナルでエージェントを実行します。
    -   `adk api_server` - 他のアプリケーションで使用できるサービスとしてエージェントを実行します。

エージェントの実行方法の詳細については、[クイックスタート](/adk-docs/get-started/quickstart/#run-your-agent)の*エージェントの実行*トピックを参照してください。ADKコマンドラインオプションの詳細については、[ADK CLIリファレンス](/adk-docs/api-reference/cli/)を参照してください。

## 構成例

このセクションでは、エージェントの構築を開始するためのエージェント構成ファイルの例を示します。追加のより完全な例については、ADK[サンプルリポジトリ](https://github.com/search?q=repo%3Agoogle%2Fadk-python+path%3A%2F%5Econtributing%5C%2Fsamples%5C%2F%2F+root_agent.yaml&type=code)を参照してください。

### 組み込みツールの例

次の例では、Google検索を使用してエージェントに機能を提供する組み込みのADKツール関数を使用します。このエージェントは、検索ツールを自動的に使用してユーザーの要求に応答します。

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
name: search_agent
model: gemini-2.0-flash
description: 'Google検索クエリを実行し、結果に関する質問に答えることを仕事とするエージェント。'
instruction: あなたは、Google検索クエリを実行し、結果に関する質問に答えることを仕事とするエージェントです。
tools:
  - name: google_search
```

詳細については、[ADKサンプルリポジトリ](https://github.com/google/adk-python/blob/main/contributing/samples/tool_builtin_config/root_agent.yaml)でこのサンプルの完全なコードを参照してください。

### カスタムツールの例

次の例では、Pythonコードで構築され、構成ファイルの`tools:`セクションにリストされているカスタムツールを使用します。エージェントはこのツールを使用して、ユーザーが提供した数値のリストが素数であるかどうかを確認します。

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
model: gemini-2.5-flash
name: prime_agent
description: 数値が素数であるかどうかを確認する処理を行います。
instruction: |
  あなたは、数値が素数であるかどうかを確認する責任があります。
  素数を確認するように求められた場合は、整数のリストを使用してcheck_primeツールを呼び出す必要があります。
  素数を手動で判断しようとしないでください。
  素数の結果をルートエージェントに返します。
tools:
  - name: ma_llm.check_prime
```

詳細については、[ADKサンプルリポジトリ](https://github.com/google/adk-python/blob/main/contributing/samples/multi_agent_llm_config/prime_agent.yaml)でこのサンプルの完全なコードを参照してください。

### サブエージェントの例

次の例は、`sub_agents:`セクションで2つのサブエージェントが定義され、構成ファイルの`tools:`セクションでサンプルツールが定義されているエージェントを示しています。このエージェントは、ユーザーが何を望んでいるかを判断し、要求を解決するためにサブエージェントの1つに委任します。サブエージェントは、エージェント構成YAMLファイルを使用して定義されます。

```
# yaml-language-server: $schema=https://raw.githubusercontent.com/google/adk-python/refs/heads/main/src/google/adk/agents/config_schemas/AgentConfig.json
agent_class: LlmAgent
model: gemini-2.5-flash
name: root_agent
description: コーディングと数学の個別指導を提供する学習アシスタント。
instruction: |
  あなたは、学生がコーディングと数学の質問をするのを手伝う学習アシスタントです。

  コーディングの質問はcode_tutor_agentに、数学の質問はmath_tutor_agentに委任します。

  次の手順に従ってください。
  1. ユーザーがプログラミングまたはコーディングについて質問した場合は、code_tutor_agentに委任します。
  2. ユーザーが数学の概念または問題について質問した場合は、math_tutor_agentに委任します。
  3. 常に明確な説明を提供し、学習を奨励してください。
sub_agents:
  - config_path: code_tutor_agent.yaml
  - config_path: math_tutor_agent.yaml
```

詳細については、[ADKサンプルリポジトリ](https://github.com/google/adk-python/blob/main/contributing/samples/multi_agent_basic_config/root_agent.yaml)でこのサンプルの完全なコードを参照してください。

## エージェント構成のデプロイ

コードベースのエージェントと同じ手順を使用して、[Cloud Run](/adk-docs/deploy/cloud-run/)および[エージェントエンジン](/adk-docs/deploy/agent-engine/)でエージェント構成エージェントをデプロイできます。エージェント構成ベースのエージェントを準備してデプロイする方法の詳細については、[Cloud Run](/adk-docs/deploy/cloud-run/)および[エージェントエンジン](/adk-docs/deploy/agent-engine/)のデプロイガイドを参照してください。

## 既知の制限 {#known-limitations}

エージェント構成機能は実験的なものであり、次の制限があります。

-   **モデルのサポート:** 現在、Geminiモデルのみがサポートされています。サードパーティモデルとの統合は進行中です。
-   **プログラミング言語:** エージェント構成機能は現在、プログラミングコードを必要とするツールやその他の機能に対してPythonコードのみをサポートしています。
-   **ADKツールのサポート:** 次のADKツールはエージェント構成機能でサポートされていますが、*すべてのツールが完全にサポートされているわけではありません*。
    -   `google_search`
    -   `load_artifacts`
    -   `url_context`
    -   `exit_loop`
    -   `preload_memory`
    -   `get_user_choice`
    -   `enterprise_web_search`
    -   `load_web_page`: Webページにアクセスするには、完全修飾パスが必要です。
-   **エージェントタイプのサポート:** `LangGraphAgent`および`A2aAgent`タイプはまだサポートされていません。
    -   `AgentTool`
    -   `LongRunningFunctionTool`
    -   `VertexAiSearchTool`
    -   `MCPToolset`
    -   `ExampleTool`

## 次のステップ

ADKエージェント構成で何をどのように構築するかについてのアイデアについては、ADK[adk-samples](https://github.com/search?q=repo:google/adk-python+path:/%5Econtributing%5C/samples%5C//+root_agent.yaml&type=code)リポジトリのyamlベースのエージェント定義を参照してください。エージェント構成形式でサポートされている構文と設定の詳細については、[エージェント構成構文リファレンス](/adk-docs/api-reference/agentconfig/)を参照してください。
