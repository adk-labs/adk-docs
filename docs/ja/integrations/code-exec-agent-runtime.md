---
catalog_title: Code Execution Tool with Agent Runtime
catalog_description: 安全でスケーラブルな環境で AI 生成コードを実行する
catalog_icon: /integrations/assets/agent-platform.svg
catalog_tags: ["code", "google"]
---


# ADK 向け Agent Runtime コード実行ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.17.0</span>
</div>

Agent Runtime コード実行 ADK ツールは、[Google Cloud Agent Runtime](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview) サービスを使用して、AI が生成したコードを低レイテンシかつ高効率に実行する手段を提供します。このツールはエージェントワークフロー向けに高速実行できるよう設計されており、セキュリティを高めるためにサンドボックス環境を使用します。また、複数のリクエストにわたってコードとデータを永続化できるため、次のような複雑な複数ステップのコーディングタスクを実現できます。

- **コード開発とデバッグ:** 複数のリクエストにわたってコードをテスト・デバッグし、改善を繰り返すエージェントタスクを作成できます。
- **データ分析を伴うコード実行:** 最大 100 MB のデータファイルをアップロードし、実行のたびにデータを再読み込みすることなく、コードベースのデータ分析を複数回実行できます。

このコード実行ツールは Agent Runtime スイートの一部ですが、使用するためにエージェントを Agent Runtime にデプロイする必要はありません。ローカル環境や他のサービス上でエージェントを実行しながら、このツールを利用できます。Agent Runtime のコード実行機能の詳細については、[Agent Runtime Code Execution](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/overview) のドキュメントを参照してください。


## ツールの使用

Agent Runtime コード実行ツールを ADK エージェントで使用するには、事前に Google Cloud Agent Runtime でサンドボックス環境を作成しておく必要があります。

ADK エージェントでコード実行ツールを使用する手順は次のとおりです。

1. Agent Runtime の [Code Execution quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart) の手順に従って、コード実行用のサンドボックス環境を作成します。
1. サンドボックス環境を作成した Google Cloud プロジェクトにアクセスできるよう設定した ADK エージェントを作成します。
1. 次のコード例は、コード実行ツールを使用するように構成されたエージェントを示しています。`SANDBOX_RESOURCE_NAME` は、作成したサンドボックス環境のリソース名に置き換えてください。

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

`sandbox_resource_name` に指定する形式の詳細や、代替パラメータである `agent_engine_resource_name` については、[設定パラメータ](#config-parameters)を参照してください。このツールで推奨されるシステム指示（system instruction）を含むより高度な例については、[高度な例](#advanced-example)または完全版の [agent code example](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution) を参照してください。

## 仕組み

`AgentEngineSandboxCodeExecutor` ツールは、エージェントのタスク全体を通じて単一のサンドボックスを維持します。つまり、ADK ワークフローセッション内のすべての操作にわたってサンドボックスの状態が永続化されます。

1. **サンドボックスの作成:** コード実行を必要とする複数ステップのタスクでは、Agent Runtime が指定された言語およびマシン構成でサンドボックスを作成し、コード実行環境を分離します。サンドボックスが事前に作成されていない場合、コード実行ツールはデフォルト設定で自動的にサンドボックスを作成します。
1. **状態を永続化したコード実行:** ツール呼び出しで AI が生成したコードはサンドボックスにストリーミングされ、分離された環境内で実行されます。実行後もサンドボックスは同じセッション内の後続のツール呼び出しのために*アクティブなまま*維持され、変数、インポート済みモジュール、およびファイル状態が同じエージェントからの次のツール呼び出しに引き継がれます。
1. **結果の取得:** 標準出力とキャプチャされたエラーストリームが収集され、呼び出し元のエージェントに返されます。
1. **サンドボックスのクリーンアップ:** エージェントのタスクまたは会話が終了すると、エージェントがサンドボックスを明示的に削除するか、作成時に指定したサンドボックスの TTL 機能によって自動的に削除させることができます。

## 主な利点

- **状態の永続化:** データ操作や変数のコンテキストを複数のツール呼び出し間で引き継ぐ必要がある複雑なタスクを解決できます。
- **的確な分離:** 軽量性を保ちながら堅牢なプロセスレベルの分離を提供し、ツールコードの安全な実行を保証します。
- **Agent Runtime との統合:** Agent Runtime のツール使用レイヤーおよびオーケストレーションレイヤーと緊密に統合されています。
- **低レイテンシのパフォーマンス:** 高速動作を重視して設計されており、大きなオーバーヘッドを発生させることなく、複雑なツール使用ワークフローを効率的に実行できます。
- **柔軟なコンピューティング構成:** プログラミング言語、CPU 性能、メモリ構成を指定してサンドボックスを作成できます。

## システム要件

ADK エージェントで Agent Runtime コード実行ツールを使用するには、次の要件を満たす必要があります。

- Agent Platform API が有効になっている Google Cloud プロジェクト
- エージェントのサービスアカウントに **roles/aiplatform.user** ロールが付与されていること（以下の操作に必要です）:
    - コード実行サンドボックスの作成、取得、一覧表示、および削除
    - コード実行サンドボックスでのコード実行

## 設定パラメータ {#config-parameters}

Agent Runtime コード実行ツールには次のパラメータがあります。以下のリソースパラメータのいずれかを設定する必要があります。

- **`sandbox_resource_name`**: 各ツール呼び出しで使用する既存のサンドボックス環境へのリソースパスです。指定する文字列の形式は次のとおりです。
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}/sandboxEnvironments/{$SANDBOX_ENVIRONMENT_ID}

    # Example:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172/sandboxEnvironments/6545148888889161728
    ```
- **`agent_engine_resource_name`**: ツールがサンドボックス環境を作成する先の Agent Runtime リソース名です。指定する文字列の形式は次のとおりです。
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}

    # Example:
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172
    ```

Google Cloud クライアント接続を介して Google Cloud Agent Runtime API を使用し、次の設定を含む Agent Runtime サンドボックス環境を個別に構成することもできます。

- **プログラミング言語**（Python や JavaScript など）
- **コンピューティング環境**（CPU やメモリサイズなど）

Google Cloud Agent Runtime への接続およびサンドボックス環境の構成の詳細については、Agent Runtime の [Code Execution quickstart](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart#create_a_sandbox) を参照してください。

## 高度な例 {#advanced-example}

次のコード例は、ADK エージェントでコード実行ツールを実装する方法を示しています。この例には、コード実行の動作ガイドラインを設定する `base_system_instruction` 関数が含まれています。このシステム指示の指定は任意ですが、このツールから最良の結果を得るために強く推奨されます。

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
      ```tool_output
      (49, 7)

      ```
    - To display the result of a numerical computation:
      ```tool_code
      x = 10 ** 9 - 12 ** 5
      print(f'{{x=}}')
      ```
      The output will be presented to you as:
      ```tool_output
      x=999751168

      ```
    - You **never** generate ```tool_output yourself.
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

このコード例を使用した ADK エージェントの完全なバージョンについては、[agent_engine_code_execution sample](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution) を参照してください。
