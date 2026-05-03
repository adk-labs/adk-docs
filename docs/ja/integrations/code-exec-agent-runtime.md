---
catalog_title: Code Execution Tool with Agent Runtime
catalog_description: AI が生成したコードを安全でスケーラブルな GKE 環境で実行する
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["code", "google"]
---


# ADK 用エージェント ランタイム コード実行ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.17.0</span>
</div>

エージェント ランタイム コード実行 ADK ツールは、低遅延、高
AI で生成されたコードを実行するための効率的な方法
[Google Cloud Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
サービス。このツールは、エージェントのワークフローに合わせて高速に実行できるように設計されており、
セキュリティを向上させるためにサンドボックス環境を使用します。コード実行ツール
コードとデータを複数のリクエストにわたって永続化できるため、複雑なリクエストを可能にし、
次のような複数ステップのコーディング タスク。

- **コード開発とデバッグ:** テストとデバッグを行うエージェント タスクを作成します。
    複数のリクエストにわたってコードのバージョンを反復処理します。
- **データ分析を伴うコード:** 最大 100MB のデータ ファイルをアップロードし、実行します
    コードを実行するたびにデータを再ロードする必要がなく、複数のコードベースの分析が可能です。

このコード実行ツールはエージェント ランタイム スイートの一部ですが、
エージェントを使用するには、エージェント ランタイムにエージェントをデプロイする必要があります。エージェントを実行できます
ローカルで、または他のサービスでこのツールを使用してください。詳細については、
エージェント ランタイムのコード実行機能については、「
[Agent Runtime Code Execution](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/overview)
ドキュメント。


## ツールを使用する

エージェント ランタイム コード実行ツールを使用するには、サンドボックスを作成する必要があります
ADK でツールを使用する前に、Google Cloud Agent Runtime を使用した環境を構築する
エージェント。

ADK エージェントでコード実行ツールを使用するには:

1. エージェント ランタイムの指示に従います。
    [Code Execution quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart)
    コード実行サンドボックス環境を作成します。
1. Google Cloud プロジェクトにアクセスするための設定を含む ADK エージェントを作成します
    サンドボックス環境を作成した場所。
1. 次のコード例は、コードを使用するように構成されたエージェントを示しています。
    エグゼキュータツール。 `SANDBOX_RESOURCE_NAME` をサンドボックス環境に置き換えます
    作成したリソース名。

```python
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

root_agent = Agent(
    model="gemini-flash-latest",
    name="agent_engine_code_execution_agent",
    instruction="You are a helpful agent that can write and execute code to answer questions and solve problems.",
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name="SANDBOX_RESOURCE_NAME",
    ),
)
```

`sandbox_resource_name` 値の予期される形式の詳細と、
代替の `agent_engine_resource_name` パラメータについては、[Configuration
parameters](#config-parameters) を参照してください。より高度な例としては、
ツールの推奨システム手順については、[Advanced
example](#advanced-example) または完全版を参照してください。
[agent code example](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution)。

## 仕組み

`AgentEngineCodeExecutor` ツールは、システム全体にわたって単一のサンドボックスを維持します。
エージェントのタスク。つまり、サンドボックスの状態はエージェント内のすべての操作にわたって持続します。
ADK ワークフロー セッション。

1. **サンドボックスの作成:** コードの実行が必要な複数ステップのタスクの場合、
    エージェント ランタイムは、指定された言語とマシンでサンドボックスを作成します
    構成、コード実行環境を分離します。サンドボックスがない場合
    事前に作成されている場合、コード実行ツールは次を使用して自動的に作成します。
    デフォルト設定。
1. **永続性を伴うコード実行:** ツール呼び出し用の AI 生成コード
    サンドボックスにストリーミングされ、分離された環境内で実行されます。
    環境。実行後、サンドボックスは後続のために *アクティブなまま*になります。
    同じセッション内でのツール呼び出し、変数、インポートされたモジュール、
    同じエージェントからの次のツール呼び出しのファイル状態。
1. **結果の取得:** 標準出力およびキャプチャされたエラー
    ストリームが収集され、呼び出し側エージェントに返されます。
1. **サンドボックスのクリーンアップ:** エージェントのタスクまたは会話が終了すると、
    エージェントはサンドボックスを明示的に削除することも、サンドボックスの TTL 機能に依存することもできます。
    サンドボックスの作成時に指定したサンドボックス。

## 主な利点

- **永続状態:** データ操作または
    変数コンテキストは、複数のツール呼び出し間で引き継がれる必要があります。
- **対象を絞った分離:** 堅牢なプロセスレベルの分離を提供します。
    軽量性を維持しながら、ツール コードの実行が安全であることを保証します。
- **エージェント ランタイムの統合:** エージェント ランタイムに緊密に統合
    ツール使用層とオーケストレーション層。
- **低遅延パフォーマンス:** スピードを重視して設計されており、エージェントは
    大きなオーバーヘッドを発生させることなく、複雑なツール使用ワークフローを効率的に実行します。
- **柔軟なコンピューティング構成:** 特定のサンドボックスを作成します。
    プログラミング言語、処理能力、メモリ構成。

## システム要件¶

エージェント ランタイムを正常に使用するには、次の要件を満たす必要があります。
ADK エージェントを使用したコード実行ツール:

- Agent Platform API が有効になっている Google Cloud プロジェクト
- エージェントのサービス アカウントには **roles/aiplatform.user** ロールが必要です。
    次のことを許可します。
    - コード実行サンドボックスの作成、取得、一覧表示、および削除
    - コード実行サンドボックスの実行

## 設定パラメータ {#config-parameters}

エージェント ランタイム コード実行ツールには次のパラメータがあります。設定する必要があります
次のリソース パラメータのいずれか:

- **`sandbox_resource_name`** : へのサンドボックス リソース パス
    各ツール呼び出しに使用される既存のサンドボックス環境。期待される
文字列の形式は次のとおりです。
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}/sandboxEnvironments/{$SANDBOX_ENVIRONMENT_ID}

    # Example:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172/sandboxEnvironments/6545148888889161728
    ```
- **`agent_engine_resource_name`**: ツールが存在するエージェント ランタイム リソース名
サンドボックス環境を作成します。予期される文字列形式は次のとおりです。
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}

    # Example:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172
    ```

Google Cloud エージェント ランタイムの API を使用してエージェント ランタイム サンドボックスを構成できます
Google Cloud クライアント接続を使用して個別に環境を構築します。
次の設定:

- **プログラミング言語** (Python および JavaScript を含む)
- **コンピューティング環境** (CPU とメモリのサイズを含む)

Google Cloud Agent Runtimeへの接続と構成の詳細については、
サンドボックス環境については、「エージェント ランタイム」を参照してください。
[Code Execution quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart#create_a_sandbox)。

## 高度な例 {#advanced-example}

次のコード例は、Code Executor ツールの使用を実装する方法を示しています。
ADK エージェント内。この例には、設定する `base_system_instruction` 句が含まれています
コード実行の操作ガイドライン。この指示条項は、
オプションですが、このツールから最良の結果を得るために強く推奨されます。

```python
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

def base_system_instruction():
  """Returns: data science agent system instruction."""

  return """
  # Guidelines

  **Objective:** Assist the user in achieving their data analysis goals, **with emphasis on avoiding assumptions and ensuring accuracy.** Reaching that goal can involve multiple steps. When you need to generate code, you **don't** need to solve the goal in one go. Only generate the next step at a time.

  **Code Execution:** All code snippets provided will be executed within the sandbox environment.

  **Statefulness:** All code snippets are executed and the variables stays in the environment. You NEVER need to re-initialize variables. You NEVER need to reload files. You NEVER need to re-import libraries.

  **Output Visibility:** Always print the output of code execution to visualize results, especially for data exploration and analysis. For example:
    - To look a the shape of a pandas.DataFrame do:
      ```tool_code
      print(df.shape)
      ```
      The output will be presented to you as:
      ```tool_outputs
      (49, 7)

      ```
    - To display the result of a numerical computation:
      ```tool_code
      x = 10 ** 9 - 12 ** 5
      print(f'{{x=}}')
      ```
      The output will be presented to you as:
      ```tool_outputs
      x=999751168

      ```
    - You **never** generate ```tool_outputs yourself.
    - You can then use this output to decide on next steps.
    - Print just variables (e.g., `print(f'{{variable=}}')`.

  **No Assumptions:** **Crucially, avoid making assumptions about the nature of the data or column names.** Base findings solely on the data itself. Always use the information obtained from `explore_df` to guide your analysis.

  **Available files:** Only use the files that are available as specified in the list of available files.

  **Data in prompt:** Some queries contain the input data directly in the prompt. You have to parse that data into a pandas DataFrame. ALWAYS parse all the data. NEVER edit the data that are given to you.

  **Answerability:** Some queries may not be answerable with the available data. In those cases, inform the user why you cannot process their query and suggest what type of data would be needed to fulfill their request.

  """

root_agent = Agent(
    model="gemini-flash-latest",
    name="agent_engine_code_execution_agent",
    instruction=base_system_instruction() + """


You need to assist the user with their queries by looking at the data and the context in the conversation.
You final answer should summarize the code and code execution relevant to the user query.

You should include all pieces of data to answer the user query, such as the table from code execution results.
If you cannot answer the question directly, you should follow the guidelines above to generate the next step.
If the question can be answered directly with writing any code, you should do that.
If you doesn't have enough data to answer the question, you should ask for clarification from the user.

You should NEVER install any package on your own like `pip install ...`.
When plotting trends, you should make sure to sort and order the data by the x-axis.


""",
    code_executor=AgentEngineSandboxCodeExecutor(
        # Replace with your sandbox resource name if you already have one.
        sandbox_resource_name="SANDBOX_RESOURCE_NAME",
        # Replace with agent engine resource name used for creating sandbox if
        # sandbox_resource_name is not set:
        # agent_engine_resource_name="AGENT_ENGINE_RESOURCE_NAME",
    ),
)
```

このコード例を使用した ADK エージェントの完全なバージョンについては、
[agent_engine_code_execution sample](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution)。
