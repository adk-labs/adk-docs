---
catalog_title: Spanner ツール
catalog_description: Spanner と対話してデータを取得、検索、SQL 実行を行います
catalog_icon: /integrations/assets/spanner.png
catalog_tags: ["data","google"]
---

# ADK用 Google Cloud Spanner ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.11.0</span><span class="lst-preview">プレビュー</span>
</div>

[Google Cloud Spanner](https://cloud.google.com/spanner) は、SQL とベクトル検索をサポートするフルマネージドの分散型データベースです。ADK Spanner ツールを使用すると、エージェントはデータベース スキーマを探索し、SQL クエリを実行し、Spanner データに対してベクトル類似性検索を実行できます。

!!! example "プレビュー"
    この機能はプレビュー段階であり、将来のリリースで更新される可能性があります。

## 利用可能なツール

`SpannerToolset` は次のツールを提供します。

- **`list_table_names`**: GCP Spanner データベースに存在するテーブル名を取得します。
- **`list_table_indexes`**: GCP Spanner データベースに存在するテーブル インデックスを取得します。
- **`list_table_index_columns`**: GCP Spanner データベースに存在するテーブル インデックス列を取得します。
- **`list_named_schemas`**: Spanner データベースの名前付きスキーマを取得します。
- **`get_table_schema`**: Spanner データベースのテーブル スキーマとメタデータ情報を取得します。
- **`execute_sql`**: Spanner データベースで SQL クエリを実行し、結果を取得します。
- **`similarity_search`**: テキスト クエリを使用して Spanner で類似性検索を実行します。

## エージェントでの使用

```py
--8<-- "examples/python/snippets/tools/built-in-tools/spanner.py"
```

## ベクトル類似性検索 (Vector similarity search)

`vector_store_similarity_search` ツールを使用すると、エージェントはベクトル ストアとして構成された Spanner テーブルに対してセマンティック検索を実行できます。この機能は、コンテキスト対応の RAG アプリケーションを構築するために不可欠です。AI モデルは、正確なキーワードの一致ではなく、意味的な意味に基づいてデータベースのコンテキストを取得できます。`SpannerVectorStoreSettings` を構成することで、エージェントはユーザー クエリの背後にある意図をよりよく理解し、最も関連性の高い Spanner データに基づいて応答をグラウンディングできます。

次の例では、Spanner テーブルをベクトル ストアとして構成し、`vector_store_similarity_search` ツールを RAG エージェントに接続します。

```py
from google.adk.agents import LlmAgent
from google.adk.tools.spanner import SpannerCredentialsConfig, SpannerToolset
from google.adk.tools.spanner.settings import (
    Capabilities,
    SpannerToolSettings,
    SpannerVectorStoreSettings,
)

# 1. ベクトル ストア設定で Spanner ツール構成を定義
my_vector_store_settings = SpannerVectorStoreSettings(
    project_id="your-gcp-project",
    instance_id="your-spanner-instance",
    database_id="your-database",
    table_name="my_products",
    content_column="productDescription",
    embedding_column="productDescriptionEmbedding",
    vector_length=768,
    vertex_ai_embedding_model_name="text-embedding-005",
    selected_columns=["productId", "productName", "productDescription"],
    nearest_neighbors_algorithm="EXACT_NEAREST_NEIGHBORS",
    top_k=3,
    distance_type="COSINE",
    additional_filter="inventoryCount > 0",
)

my_tool_settings = SpannerToolSettings(
    capabilities=[Capabilities.DATA_READ],
    vector_store_settings=my_vector_store_settings,
)

# 2. Spanner ツールセットを初期化
credentials_config = SpannerCredentialsConfig()
my_spanner_toolset = SpannerToolset(
    credentials_config=credentials_config,
    spanner_tool_settings=my_tool_settings,
    tool_filter=["vector_store_similarity_search"],
)

# 3. RAG エージェントでツールセットを使用
my_rag_agent = LlmAgent(
    model="gemini-flash-latest",
    name="product_search_agent",
    instruction="""
    You are a helpful assistant that answers user questions by finding similar products.
    1. Always use the `vector_store_similarity_search` tool to find relevant product information.
    2. If no relevant information is found, state that no matching products were found.
    3. Present the relevant product details clearly in your response.
    """,
    tools=[my_spanner_toolset],
)
```

### 構成

上記で使用した `SpannerVectorStoreSettings` クラスは、`vector_store_similarity_search` の動作方法を定義します。次のパラメータを受け入れます。

#### 必須パラメータ

- **`project_id`**: 認証コンテキストに必要な Google Cloud プロジェクト ID。
- **`instance_id`**: Spanner インスタンス ID。
- **`database_id`**: Spanner データベース ID。
- **`table_name`**: ベクトル埋め込みを含む Spanner テーブル。
- **`embedding_column`**: ベクトル埋め込みが格納されている `ARRAY<FLOAT>` または `ARRAY<DOUBLE>` 列。
- **`content_column`**: 取得する元のテキストまたはコンテンツを含む列。
- **`vector_length`**: モデルと一致する必要がある埋め込みベクトルの次元数。
- **`vertex_ai_embedding_model_name`**: 埋め込みの生成に使用されるモデル (例: "text-embedding-005")。

#### オプション パラメータ

- **`selected_columns`**: メタデータや識別子など、検索結果に含める列のリスト。
- **`nearest_neighbors_algorithm`**: 検索に使用するアルゴリズム (`EXACT_NEAREST_NEIGHBORS` や `APPROXIMATE_NEAREST_NEIGHBORS` など)。
    - **`num_leaves_to_search`**: 検索するインデックス リーフ ノードの数。`APPROXIMATE_NEAREST_NEIGHBORS` でのみ使用されます。
    - **`vector_search_index_settings`**: ベクトル インデックス設定。`APPROXIMATE_NEAREST_NEIGHBORS` でのみ必要です。
- **`top_k`**: クエリごとに取得する最も近い近傍の数。
- **`distance_type`**: 類似度の計算に使用される距離メトリック (`COSINE` または `EUCLIDEAN`)。
- **`additional_filter`**: 検索中に適用するオプションの SQL フィルタ文字列 (例: "inventoryCount > 0")。

## Spanner Admin Toolset

`SpannerAdminToolset` を使用すると、Spanner インスタンスとデータベースに対する管理操作が可能になります。これには別のライブラリのインポートが必要です。

!!! warning "注意して使用"

    このツールセットは Spanner インスタンスとデータベースを作成、検査、変更できるため、アクセス権は慎重に付与してください。実行環境 (Application Default Credentials またはサービス アカウント キーなど) が承認されたプロジェクトのみに制限され、`roles/spanner.admin` などの必要最小限の IAM 権限を使用していることを確認してください。

### 利用可能なツール

* **`list_instances`**: プロジェクト内の Spanner インスタンスを一覧表示します。
* **`get_instance`**: Spanner インスタンスの詳細を取得します。
* **`create_database`**: 新しい Spanner データベースを作成します。
* **`list_databases`**: インスタンス内の Spanner データベースを一覧表示します。
* **`create_instance`**: 新しい Spanner インスタンスを作成します。
* **`list_instance_configs`**: 利用可能な Spanner インスタンス構成を一覧表示します。
* **`get_instance_config`**: Spanner インスタンス構成の詳細を取得します。

### 構成

このツールセットを使用する前に、必要な環境変数を設定してください。

- `SPANNER_PROJECT`: 操作対象の GCP プロジェクト ID。
- `SPANNER_INSTANCE` (オプション): デフォルトの Spanner インスタンス ID。
- `SPANNER_DATABASE` (オプション): デフォルトのデータベース ID。

### エージェントでの使用

`SpannerAdminToolset` を初期化して、Google Cloud Spanner 管理機能にアクセスします。次に、`LlmAgent` の `tools` リストに渡して、エージェントが Spanner リソースを管理できるようにします。

```python
from google.adk.agents import LlmAgent
from google.adk.tools.spanner import SpannerAdminToolset

# Spanner 管理ツールセットを初期化
spanner_admin_tools = SpannerAdminToolset()

# エージェントにツールセットを登録 (モデルと指示が提供されていることを確認)
agent = LlmAgent(
    name="SpannerAdminAgent",
    model="gemini-flash-latest",
    instruction=(
        "You are a helpful database administrator. Use the SpannerAdminToolset "
        "to manage and query Spanner instances and databases in the project."
    ),
    tools=[spanner_admin_tools]
)
```
