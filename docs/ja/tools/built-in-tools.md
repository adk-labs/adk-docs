# 組み込みツール

これらの組み込みツールは、Google検索やコード実行などのすぐに使える機能を提供し、エージェントに共通の能力を付与します。例えば、ウェブから情報を取得する必要があるエージェントは、追加の設定なしで直接**google\_search**ツールを使用できます。

## 使用方法

1.  **インポート:** ツールモジュールから目的のツールをインポートします。これはPythonでは`agents.tools`、Goでは`google.golang.org/adk/tool/geminitool`、Javaでは`com.google.adk.tools`です。
2.  **設定:** ツールを初期化し、必要であれば必須パラメータを提供します。
3.  **登録:** 初期化されたツールをエージェントの**tools**リストに追加します。

エージェントに追加されると、エージェントは**ユーザープロンプト**と自身の**指示**に基づいてツールを使用するかどうかを決定できます。エージェントがツールを呼び出すと、フレームワークがその実行を処理します。重要：このページの***制限事項***セクションを確認してください。

## 利用可能な組み込みツール

注：GoはGoogle検索ツールと`geminitool`パッケージを介した他の組み込みツールをサポートしています。
注：現在、JavaはGoogle検索とコード実行ツールのみをサポートしています。

### Google検索

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`google_search`ツールを使用すると、エージェントはGoogle検索を使用してウェブ検索を実行できます。`google_search`ツールはGemini 2モデルとのみ互換性があります。ツールの詳細については、[Google検索グラウンディングについて](../grounding/google_search_grounding.md)を参照してください。

!!! warning "`google_search`ツール使用時の追加要件"
    Google検索によるグラウンディングを使用し、レスポンスで検索候補を受け取った場合、本番環境およびアプリケーションで検索候補を表示する必要があります。
    Google検索によるグラウンディングの詳細については、[Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions)または[Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions)のGoogle検索によるグラウンディングのドキュメントを参照してください。UIコード（HTML）はGeminiレスポンスの`renderedContent`として返されるため、ポリシーに従ってアプリにHTMLを表示する必要があります。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/google_search.py"
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools/built-in-tools/google_search.go"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/GoogleSearchAgentApp.java:full_code"
    ```

### コード実行

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`built_in_code_execution`ツールは、特にGemini 2モデルを使用する場合に、エージェントがコードを実行できるようにします。これにより、モデルは計算、データ操作、小さなスクリプトの実行などのタスクを実行できます。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CodeExecutionAgentApp.java:full_code"
    ```

### GKEコードエグゼキュータ

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.14.0</span>
</div>

GKEコードエグゼキュータ（`GkeCodeExecutor`）は、gVisorを使用してワークロードを分離するGKE（Google Kubernetes Engine）サンドボックス環境を活用して、LLMが生成したコードを実行するための安全でスケーラブルな方法を提供します。コード実行リクエストごとに、強化されたPod構成を持つエフェメラルなサンドボックス化されたKubernetesジョブを動的に作成します。セキュリティと分離が重要なGKE上の本番環境では、このエグゼキュータを使用する必要があります。

#### 仕組み

コード実行のリクエストが行われると、`GkeCodeExecutor`は次の手順を実行します。

1.  **ConfigMapの作成:** 実行する必要のあるPythonコードを保存するためにKubernetes ConfigMapが作成されます。
2.  **サンドボックス化されたPodの作成:** 新しいKubernetesジョブが作成され、これにより、強化されたセキュリティコンテキストとgVisorランタイムが有効になったPodが作成されます。ConfigMapのコードがこのPodにマウントされます。
3.  **コードの実行:** コードは、基盤となるノードや他のワークロードから分離されたサンドボックス化されたPod内で実行されます。
4.  **結果の取得:** 実行からの標準出力とエラーストリームがPodのログからキャプチャされます。
5.  **リソースのクリーンアップ:** 実行が完了すると、ジョブと関連するConfigMapが自動的に削除され、アーティファクトが残らないようになります。

#### 主な利点

*   **強化されたセキュリティ:** コードは、カーネルレベルの分離を備えたgVisorサンドボックス環境で実行されます。
*   **エフェメラル環境:** 各コード実行は独自のエフェメラルPodで実行され、実行間の状態転送を防ぎます。
*   **リソース制御:** 実行PodのCPUとメモリの制限を構成して、リソースの乱用を防ぐことができます。
*   **スケーラビリティ:** GKEが基盤となるノードのスケジューリングとスケーリングを処理するため、多数のコード実行を並行して実行できます。

#### システム要件

GKEコードエグゼキュータツールを使用してADKプロジェクトを正常にデプロイするには、次の要件を満たす必要があります。

- **gVisor対応ノードプール**を備えたGKEクラスタ。
- エージェントのサービスアカウントには、次のことを許可する特定の**RBAC権限**が必要です。
    - 各実行リクエストの**ジョブ**の作成、監視、削除。
    - ジョブのPodにコードを挿入するための**ConfigMap**の管理。
    - 実行結果を取得するための**Pod**のリスト表示と**ログ**の読み取り。
- GKEエクストラを使用してクライアントライブラリをインストールします：`pip install google-adk[gke]`

すぐに使える完全な構成については、
[deployment_rbac.yaml](https://github.com/google/adk-python/blob/main/contributing/samples/gke_agent_sandbox/deployment_rbac.yaml)
サンプルを参照してください。ADKワークフローをGKEにデプロイする方法の詳細については、
[Google Kubernetes Engine（GKE）へのデプロイ](/adk-docs/ja/deploy/gke/)を参照してください。

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.code_executors import GkeCodeExecutor

    # サービスアカウントが必要なRBAC権限を持つ名前空間を対象としてエグゼキュータを初期化します。
    # この例では、カスタムタイムアウトとリソース制限も設定します。
    gke_executor = GkeCodeExecutor(
        namespace="agent-sandbox",
        timeout_seconds=600,
        cpu_limit="1000m",  # 1 CPUコア
        mem_limit="1Gi",
    )

    # エージェントは、生成するすべてのコードにこのエグゼキュータを使用するようになりました。
    gke_agent = LlmAgent(
        name="gke_coding_agent",
        model="gemini-2.0-flash",
        instruction="あなたはPythonコードを記述して実行する便利なAIエージェントです。",
        code_executor=gke_executor,
    )
    ```

#### 構成パラメータ

`GkeCodeExecutor`は、次のパラメータで構成できます。

| パラメータ            | 型   | 説明                                                                             |
| -------------------- | ------ | --------------------------------------------------------------------------------------- |
| `namespace`          | `str`  | 実行ジョブが作成されるKubernetes名前空間。デフォルトは`"default"`です。 |
| `image`              | `str`  | 実行Podに使用するコンテナイメージ。デフォルトは`"python:3.11-slim"`です。         |
| `timeout_seconds`    | `int`  | コード実行のタイムアウト（秒）。デフォルトは`300`です。                           |
| `cpu_requested`      | `str`  | 実行Podに要求するCPUの量。デフォルトは`"200m"`です。                   |
| `mem_requested`      | `str`  | 実行Podに要求するメモリの量。デフォルトは`"256Mi"`です。               |
| `cpu_limit`          | `str`  | 実行Podが使用できるCPUの最大量。デフォルトは`"500m"`です。                  |
| `mem_limit`          | `str`  | 実行Podが使用できるメモリの最大量。デフォルトは`"512Mi"`です。              |
| `kubeconfig_path`    | `str`  | 認証に使用するkubeconfigファイルへのパス。クラスタ内構成またはデフォルトのローカルkubeconfigにフォールバックします。 |
| `kubeconfig_context` | `str`  | 使用する`kubeconfig`コンテキスト。  |

### Vertex AI RAGエンジン

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`vertex_ai_rag_retrieval`ツールを使用すると、エージェントはVertex
AI RAGエンジンを使用してプライベートデータ検索を実行できます。

Vertex AI RAGエンジンでグラウンディングを使用する場合は、事前にRAGコーパスを準備する必要があります。
セットアップについては、[RAG ADKエージェントサンプル](https://github.com/google/adk-samples/blob/main/python/agents/RAG/rag/shared_libraries/prepare_corpus_and_data.py)または[Vertex AI RAGエンジンページ](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-quickstart)を参照してください。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/vertexai_rag_engine.py"
    ```

### Vertex AI Search

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

`vertex_ai_search_tool`はGoogle CloudのVertex AI Searchを使用し、エージェントがプライベートに設定されたデータストア（例: 社内ドキュメント、企業ポリシー、ナレッジベース）を検索できるようにします。この組み込みツールでは、設定時に特定のデータストアIDを提供する必要があります。ツールの詳細については、[Vertex AI Searchグラウンディングについて](../grounding/vertex_ai_search_grounding.md)を参照してください。


```py
--8<-- "examples/python/snippets/tools/built-in-tools/vertexai_search.py"
```


### BigQuery

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.1.0</span>
</div>

以下は、BigQueryとの連携を提供するためのツール群です。

* **`list_dataset_ids`**: GCPプロジェクト内に存在するBigQueryデータセットIDを取得します。
* **`get_dataset_info`**: BigQueryデータセットに関するメタデータを取得します。
* **`list_table_ids`**: BigQueryデータセット内に存在するテーブルIDを取得します。
* **`get_table_info`**: BigQueryテーブルに関するメタデータを取得します。
* **`execute_sql`**: BigQueryでSQLクエリを実行し、その結果を取得します。
* **`forecast`**: `AI.FORECAST`関数を使用してBigQuery AI時系列予測を実行します。
* **`ask_data_insights`**: 自然言語を使用してBigQueryテーブルのデータに関する質問に答えます。

これらは`BigQueryToolset`というツールセットにパッケージ化されています。



```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigquery.py"
```


### Spanner

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.11.0</span>
</div>

以下は、Spannerとの連携を提供するためのツール群です。

* **`list_table_names`**: GCP Spannerデータベースに存在するテーブル名を取得します。
* **`list_table_indexes`**: GCP Spannerデータベースに存在するテーブルインデックスを取得します。
* **`list_table_index_columns`**: GCP Spannerデータベースに存在するテーブルインデックス列を取得します。
* **`list_named_schemas`**: Spannerデータベースの名前付きスキーマを取得します。
* **`get_table_schema`**: Spannerデータベースのテーブルスキーマとメタデータ情報を取得します。
* **`execute_sql`**: SpannerデータベースでSQLクエリを実行し、その結果を取得します。
* **`similarity_search`**: テキストクエリを使用してSpannerで類似性検索を実行します。

これらは`SpannerToolset`というツールセットにパッケージ化されています。



```py
--8<-- "examples/python/snippets/tools/built-in-tools/spanner.py"
```


### Bigtable

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.12.0</span>
</div>

以下は、Bigtableとの連携を提供するためのツール群です。

* **`list_instances`**: Google CloudプロジェクトのBigtableインスタンスを取得します。
* **`get_instance_info`**: Google Cloudプロジェクトのメタデータインスタンス情報を取得します。
* **`list_tables`**: GCP Bigtableインスタンスのテーブルを取得します。
* **`get_table_info`**: GCP Bigtableのメタデータテーブル情報を取得します。
* **`execute_sql`**: BigtableテーブルでSQLクエリを実行し、その結果を取得します。

これらは`BigtableToolset`というツールセットにパッケージ化されています。



```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigtable.py"
```

## 組み込みツールを他のツールと使用する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-java">Java</span>
</div>

以下のコードサンプルは、複数の組み込みツールを使用する方法、または複数のエージェントを使用して組み込みツールを他のツールと組み合わせる方法を示しています。

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
        あなたはGoogle検索のスペシャリストです
        """,
        tools=[google_search],
    )
    coding_agent = Agent(
        model='gemini-2.0-flash',
        name='CodeAgent',
        instruction="""
        あなたはコード実行のスペシャリストです
        """,
        code_executor=BuiltInCodeExecutor(),
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="ルートエージェント",
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

        // SearchAgentを定義
        LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("あなたはGoogle検索のスペシャリストです")
                .tools(new GoogleSearchTool()) // GoogleSearchToolをインスタンス化
                .build();


        // CodingAgentを定義
        LlmAgent codingAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("CodeAgent")
                .instruction("あなたはコード実行のスペシャリストです")
                .tools(new BuiltInCodeExecutionTool()) // BuiltInCodeExecutionToolをインスタンス化
                .build();

        // RootAgentを定義。AgentTool.create()を使用してSearchAgentとCodingAgentをラップ
        BaseAgent rootAgent =
            LlmAgent.builder()
                .name("RootAgent")
                .model(MODEL_ID)
                .description("ルートエージェント")
                .tools(
                    AgentTool.create(searchAgent), // createメソッドを使用
                    AgentTool.create(codingAgent)   // createメソッドを使用
                 )
                .build();

        // 注：このサンプルはエージェントの定義のみを示しています。
        // これらのエージェントを実行するには、前の例と同様に、
        // RunnerとSessionServiceに統合する必要があります。
        System.out.println("エージェントが正常に定義されました:");
        System.out.println("  ルートエージェント: " + rootAgent.name());
        System.out.println("  検索エージェント（ネスト）: " + searchAgent.name());
        System.out.println("  コードエージェント（ネスト）: " + codingAgent.name());
      }
    }
    ```


### 制限事項

!!! warning

    現在、各ルートエージェントまたは単一のエージェントに対して、サポートされている組み込みツールは1つだけです。同じエージェント内で他のどのタイプのツールも使用することはできません。

 例えば、単一のエージェント内で***組み込みツールを他のツールと一緒に***使用する以下のアプローチは、現在サポートされて**いません**。

=== "Python"

    ```py
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="ルートエージェント",
        tools=[custom_function],
        code_executor=BuiltInCodeExecutor() # <-- toolsと併用する場合はサポートされていません
    )
    ```

=== "Java"

    ```java
     LlmAgent searchAgent =
            LlmAgent.builder()
                .model(MODEL_ID)
                .name("SearchAgent")
                .instruction("あなたはGoogle検索のスペシャリストです")
                .tools(new GoogleSearchTool(), new YourCustomTool()) // <-- サポートされていません
                .build();
    ```

ADK Pythonには、この制限を回避するための組み込みの回避策があります。
`GoogleSearchTool`および`VertexAiSearchTool`の場合（`bypass_multi_tools_limit=True`を使用して有効にします）、例：
[サンプルエージェント](https://github.com/google/adk-python/tree/main/contributing/samples/built_in_multi_tools)。

!!! warning

    組み込みツールはサブエージェント内では使用できません。ただし、
    上記の回避策のため、ADK Pythonの`GoogleSearchTool`および`VertexAiSearchTool`は例外です。

例えば、サブエージェント内で組み込みツールを使用する以下のアプローチは、現在サポートされて**いません**。

=== "Python"

    ```py
    url_context_agent = Agent(
        model='gemini-2.0-flash',
        name='UrlContextAgent',
        instruction="""
        あなたはURLコンテキストのスペシャリストです
        """,
        tools=[url_context],
    )
    coding_agent = Agent(
        model='gemini-2.0-flash',
        name='CodeAgent',
        instruction="""
        あなたはコード実行のスペシャリストです
        """,
        code_executor=BuiltInCodeExecutor(),
    )
    root_agent = Agent(
        name="RootAgent",
        model="gemini-2.0-flash",
        description="ルートエージェント",
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
            .model("gemini-2.0-flash")
            .name("SearchAgent")
            .instruction("あなたはGoogle検索のスペシャリストです")
            .tools(new GoogleSearchTool())
            .build();

    LlmAgent codingAgent =
        LlmAgent.builder()
            .model("gemini-2.0-flash")
            .name("CodeAgent")
            .instruction("あなたはコード実行のスペシャリストです")
            .tools(new BuiltInCodeExecutionTool())
            .build();


    LlmAgent rootAgent =
        LlmAgent.builder()
            .name("RootAgent")
            .model("gemini-2.0-flash")
            .description("ルートエージェント")
            .subAgents(searchAgent, codingAgent) // サポートされていません、サブエージェントが組み込みツールを使用しているため。
            .build();
    ```