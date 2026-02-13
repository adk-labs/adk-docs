---
catalog_title: Code Execution Tool with Agent Engine
catalog_description: 安全でスケーラブルな GKE 環境で AI 生成コードを実行します
catalog_icon: /adk-docs/integrations/assets/vertex-ai.png
catalog_tags: ["code", "google"]
---
# Agent Engineを使用したコード実行ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.17.0</span><span class="lst-preview">プレビュー</span>
</div>

Agent Engineコード実行ADKツールは、[Google Cloud Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)サービスを使用してAI生成コードを実行するための低レイテンシで高効率な方法を提供します。このツールは、エージェントワークフローに合わせて高速実行できるように設計されており、セキュリティを向上させるためにサンドボックス環境を使用します。コード実行ツールを使用すると、複数のリクエストにわたってコードとデータを永続化できるため、次のような複雑なマルチステップのコーディングタスクが可能になります。

-   **コード開発とデバッグ:** 複数のリクエストにわたってコードのバージョンをテストおよび反復するエージェントタスクを作成します。
-   **データ分析によるコード:** 最大100MBのデータファイルをアップロードし、各コード実行でデータを再ロードすることなく、複数のコードベースの分析を実行します。

このコード実行ツールはAgent Engineスイートの一部ですが、エージェントをAgent Engineにデプロイして使用する必要はありません。エージェントをローカルまたは他のサービスで実行し、このツールを使用できます。Agent Engineのコード実行機能の詳細については、[Agent Engineコード実行](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/overview)のドキュメントを参照してください。

!!! example "プレビューリリース"
    Agent Engineコード実行機能はプレビューリリースです。詳細については、[リリース段階の説明](https://cloud.google.com/products#product-launch-stages)を参照してください。

## ツールの使用

Agent Engineコード実行ツールを使用するには、ADKエージェントでツールを使用する前に、Google Cloud Agent Engineでサンドボックス環境を作成する必要があります。

ADKエージェントでコード実行ツールを使用するには：

1.  Agent Engineの[コード実行クイックスタート](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart)の手順に従って、コード実行サンドボックス環境を作成します。
1.  サンドボックス環境を作成したGoogle Cloudプロジェクトにアクセスするための設定でADKエージェントを作成します。
1.  次のコード例は、コード実行ツールを使用するように構成されたエージェントを示しています。`SANDBOX_RESOURCE_NAME`を、作成したサンドボックス環境リソース名に置き換えます。

```python
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

root_agent = Agent(
    model="gemini-2.5-flash",
    name="agent_engine_code_execution_agent",
    instruction="あなたは、質問に答えたり問題を解決したりするためにコードを記述して実行できる便利なエージェントです。",
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name="SANDBOX_RESOURCE_NAME",
    ),
)
```

`sandbox_resource_name`値の期待される形式、および代替の`agent_engine_resource_name`パラメータの詳細については、[構成パラメータ](#config-parameters)を参照してください。ツールの推奨されるシステム指示を含む高度な例については、[高度な例](#advanced-example)または完全な[エージェントコードの例](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution)を参照してください。

## 仕組み

`AgentEngineCodeExecutor`ツールは、エージェントのタスク全体で単一のサンドボックスを維持します。つまり、サンドボックスの状態はADKワークフローセッション内のすべての操作で永続化されます。

1.  **サンドボックスの作成:** コード実行が必要なマルチステップタスクの場合、Agent Engineは指定された言語とマシン構成でサンドボックスを作成し、コード実行環境を分離します。事前に作成されたサンドボックスがない場合、コード実行ツールはデフォルト設定を使用して自動的にサンドボックスを作成します。
1.  **永続性のあるコード実行:** ツール呼び出し用にAIが生成したコードはサンドボックスにストリーミングされ、分離された環境内で実行されます。実行後、サンドボックスは同じセッション内の後続のツール呼び出しに対して*アクティブなまま*になり、同じエージェントからの次のツール呼び出しのために変数、インポートされたモジュール、およびファイルの状態を保持します。
1.  **結果の取得:** 標準出力、およびキャプチャされたエラーストリームが収集され、呼び出し元のエージェントに返されます。
1.  **サンドボックスのクリーンアップ:** エージェントタスクまたは会話が終了すると、エージェントはサンドボックスを明示的に削除するか、サンドボックスの作成時に指定されたサンドボックスのTTL機能に依存できます。

## 主な利点

-   **永続的な状態:** 複数のツール呼び出し間でデータ操作または変数コンテキストを引き継ぐ必要がある複雑なタスクを解決します。
-   **対象を絞った分離:** 堅牢なプロセスレベルの分離を提供し、ツールコードの実行が安全でありながら軽量であることを保証します。
-   **Agent Engineの統合:** Agent Engineのツール使用およびオーケストレーションレイヤーに緊密に統合されています。
-   **低レイテンシのパフォーマンス:** 速度を重視して設計されており、エージェントは大きなオーバーヘッドなしで複雑なツール使用ワークフローを効率的に実行できます。
-   **柔軟なコンピューティング構成:** 特定のプログラミング言語、処理能力、およびメモリ構成でサンドボックスを作成します。

## システム要件¶

ADKエージェントでAgent Engineコード実行ツールを正常に使用するには、次の要件を満たす必要があります。

-   Vertex APIが有効になっているGoogle Cloudプロジェクト
-   エージェントのサービスアカウントには、次のことを許可する**roles/aiplatform.user**ロールが必要です。
    -   コード実行サンドボックスの作成、取得、一覧表示、削除
    -   コード実行サンドボックスの実行

## 構成パラメータ {#config-parameters}

Agent Engineコード実行ツールには次のパラメータがあります。次のリソースパラメータのいずれかを設定する必要があります。

-   **`sandbox_resource_name`**: 各ツール呼び出しに使用する既存のサンドボックス環境へのサンドボックスリソースパス。期待される文字列形式は次のとおりです。
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}/sandboxEnvironments/{$SANDBOX_ENVIRONMENT_ID}
    
    # 例：
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172/sandboxEnvironments/6545148888889161728
    ```
-   **`agent_engine_resource_name`**: ツールがサンドボックス環境を作成するAgent Engineリソース名。期待される文字列形式は次のとおりです。
    ```
    projects/{$PROJECT_ID}/locations/{$LOCATION_ID}/reasoningEngines/{$REASONING_ENGINE_ID}
    
    # 例：
    projects/my-vertex-agent-project/locations/us-central1/reasoningEngines/6842888880301111172
    ```

Google Cloud Agent EngineのAPIを使用して、次の設定を含むGoogle Cloudクライアント接続を使用してAgent Engineサンドボックス環境を個別に構成できます。

-   PythonやJavaScriptなどの**プログラミング言語**
-   CPUやメモリサイズなどの**コンピューティング環境**

Google Cloud Agent Engineへの接続とサンドボックス環境の構成の詳細については、Agent Engineの[コード実行クイックスタート](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/code-execution/quickstart#create_a_sandbox)を参照してください。

## 高度な例 {#advanced-example}

次のコード例は、ADKエージェントでコード実行ツールの使用を実装する方法を示しています。この例には、コード実行の操作ガイドラインを設定するための`base_system_instruction`句が含まれています。この指示句はオプションですが、このツールから最良の結果を得るために強くお勧めします。

```python
from google.adk.agents.llm_agent import Agent
from google.adk.code_executors.agent_engine_sandbox_code_executor import AgentEngineSandboxCodeExecutor

def base_system_instruction():
  """戻り値：データサイエンスエージェントのシステム指示。"""

  return """
  # ガイドライン

  **目的:** ユーザーがデータ分析の目標を達成するのを支援し、**仮定を避け、正確性を確保することに重点を置きます。**その目標を達成するには、複数のステップが必要になる場合があります。コードを生成する必要がある場合、一度に目標を解決する必要はありません。一度に次のステップのみを生成してください。

  **コード実行:** 提供されるすべてのコードスニペットは、サンドボックス環境内で実行されます。

  **ステートフル性:** すべてのコードスニペットが実行され、変数は環境に残ります。変数を再初期化する必要は**ありません**。ファイルを再ロードする必要は**ありません**。ライブラリを再インポートする必要は**ありません**。

  **出力の可視性:** データ探索や分析のために結果を視覚化するために、常にコード実行の出力を印刷してください。例：
    - pandas.DataFrameの形状を確認するには、次のようにします。
      ```tool_code
      print(df.shape)
      ```
      出力は次のように表示されます。
      ```tool_outputs
      (49, 7)

      ```
    - 数値計算の結果を表示するには：
      ```tool_code
      x = 10 ** 9 - 12 ** 5
      print(f'{{x=}}')
      ```
      出力は次のように表示されます。
      ```tool_outputs
      x=999751168

      ```
    - ```tool_outputsを自分で生成することは**ありません**。
    - この出力を使用して、次のステップを決定できます。
    - 変数のみを印刷します（例：`print(f'{{variable=}}')`）。

  **仮定なし:** **重要なこととして、データの性質や列名について仮定を立てないでください。**調査結果はデータ自体にのみ基づいてください。常に`explore_df`から取得した情報を使用して分析をガイドしてください。

  **利用可能なファイル:** 利用可能なファイルのリストで指定されている利用可能なファイルのみを使用してください。

  **プロンプト内のデータ:** 一部のクエリには、プロンプトに直接入力データが含まれています。そのデータをpandas DataFrameに解析する必要があります。常にすべてのデータを解析してください。与えられたデータを編集しないでください。

  **回答可能性:** 一部のクエリは、利用可能なデータでは回答できない場合があります。その場合は、クエリを処理できない理由をユーザーに伝え、リクエストを満たすためにどのような種類のデータが必要になるかを提案してください。

  """

root_agent = Agent(
    model="gemini-2.5-flash",
    name="agent_engine_code_execution_agent",
    instruction=base_system_instruction() + """


会話のデータとコンテキストを見て、ユーザーのクエリを支援する必要があります。
最終的な回答は、ユーザーのクエリに関連するコードとコード実行を要約する必要があります。

コード実行結果のテーブルなど、ユーザーのクエリに回答するためのすべてのデータを含める必要があります。
質問に直接回答できない場合は、上記の手順に従って次のステップを生成する必要があります。
コードを記述して直接回答できる質問の場合は、そうする必要があります。
質問に回答するのに十分なデータがない場合は、ユーザーに明確化を求める必要があります。

`pip install ...`のように、自分でパッケージをインストールすることは**ありません**。
トレンドをプロットするときは、x軸でデータを並べ替えて順序付けする必要があります。


""",
    code_executor=AgentEngineSandboxCodeExecutor(
        # すでに持っている場合は、サンドボックスリソース名に置き換えます。
        sandbox_resource_name="SANDBOX_RESOURCE_NAME",
        # sandbox_resource_nameが設定されていない場合は、サンドボックスの作成に使用されるエージェントエンジンリソース名に置き換えます。
        # agent_engine_resource_name="AGENT_ENGINE_RESOURCE_NAME",
    ),
)
```

このコード例を使用するADKエージェントの完全なバージョンについては、[agent_engine_code_executionサンプル](https://github.com/google/adk-python/tree/main/contributing/samples/agent_engine_code_execution)を参照してください。
