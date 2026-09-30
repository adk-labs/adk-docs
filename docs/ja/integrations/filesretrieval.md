---
catalog_title: Files Retrieval Tool
catalog_description: ベクトル類似度検索を使用してローカルドキュメントのインデックス作成と検索を行います
catalog_icon: /integrations/assets/filesretrieval.png
catalog_tags: ["google", "data"]
---

# ADK 向け Files Retrieval ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

`FilesRetrieval` ツールを使用すると、ADK エージェントは検索拡張生成（RAG）を使用してローカルドキュメントのインデックス作成とクエリ実行を行えます。Google の Gemini エンベディングモデルを使用して、指定したディレクトリに対して LlamaIndex の `VectorStoreIndex` を構築します。エージェントは、ローカルのテキストファイル、Markdown ドキュメント、ソースファイルから関連する抜粋を取得し、プロジェクト固有のコンテキストに基づいて回答をグラウンディングできます。

## ユースケース

- **コードベースとドキュメントの検索**: ローカルリポジトリから関連する関数、設計メモ、ドキュメントを取得して技術的な質問に回答します。
- **ローカルナレッジベースのグラウンディング**: ホストされたドキュメントストアに最初にロードすることなく、自身のファイルシステムから内部の Markdown ファイル、技術仕様、ガイドを直接インデックス作成します。ドキュメントの内容はインデックス作成のために設定されたエンベディングモデルに送信されるため、機密情報をインデックス作成する前に Google AI Studio または Agent Platform のデータ処理規約を確認してください。
- **コンテキスト拡張アシスタント**: レポート、ログ、テキストファイルからドメイン固有の関連データを取得し、検証済みのソース資料に基づいてエージェントのレスポンスをグラウンディングします。

## 前提条件

`FilesRetrieval` ツールは LlamaIndex を使用してドキュメントのインデックスを作成しますが、ADK はデフォルトではこれをインストールしません。これを提供するエクストラをインストールしてください。

```bash
pip install "google-adk[extensions]"
```

次に、Google AI Studio または Agent Platform の認証情報を設定します。

=== "Google AI Studio"

    [Google AI Studio](https://aistudio.google.com/) で API キーを生成し、環境変数を設定します。

    ```bash
    export GOOGLE_API_KEY="your-api-key"
    ```

=== "Agent Platform"

    Google Cloud の認証情報を使用して Agent Platform へのアクセスを設定します。

    ```bash
    export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
    export GOOGLE_CLOUD_PROJECT="your-project-id"
    export GOOGLE_CLOUD_LOCATION="<global | us | eu>"
    ```

!!! note
    
    本番環境では、`embedding_model=GoogleGenAIEmbedding(model_name="gemini-embedding-2", embed_batch_size=1)` を使用して GA モデルを明示的に渡してください。詳細については、[Gemini Embedding](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/embedding-2) を参照してください。ADK エージェントを Google Cloud リソースおよびサービスに接続する方法の詳細については、Google Cloud [接続ガイド](/ja/get-started/google-cloud/) を参照してください。

## エージェントでの使用

この例では、ローカルデータディレクトリに対して `FilesRetrieval` を構成し、それを ADK エージェントにアタッチします。実行する前に、エージェントモジュールの隣に `data/` ディレクトリを作成し、インデックスを作成する `.txt` または `.md` ファイルを追加してください。`FilesRetrieval` は構築時にディレクトリ全体をロードして埋め込みを生成するため、ディレクトリがすでに存在している必要があり、エージェントモジュールがインポートされるたびにコンテンツが再インデックスされます。

```python
import os
from google.adk.agents import Agent
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval

# ソースドキュメントを含むディレクトリへのパス
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# FilesRetrieval ツールの初期化
files_retrieval = FilesRetrieval(
    name="search_documents",
    description=(
        "Search through local documentation files to find relevant"
        " information. Use this tool when the user asks questions about"
        " architecture, project structure, or tools."
    ),
    input_dir=DATA_DIR,
)

# 検索ツールを備えたエージェントを作成
root_agent = Agent(
    model="gemini-flash-latest",
    name="files_retrieval_agent",
    instruction=(
        "You are a helpful assistant that answers questions based on local"
        " documentation files. Always use the search_documents tool to retrieve"
        " relevant context before generating your answer."
    ),
    tools=[files_retrieval],
)
```

## 利用可能なツール

`FilesRetrieval` クラスはツールです。`tools=[...]` でアタッチされると、エージェントには単一の `query` 文字列パラメータを受け取る1つの関数が表示されます。

ツール | 説明
---- | -----------
`search_documents` | インデックス作成されたディレクトリ内のドキュメントに対してセマンティックベクトル検索を実行し、指定された自然言語クエリに対して最も関連性の高いコンテンツチャンクを返します。`name` パラメータで名前を変更できます。

## 設定

`FilesRetrieval` コンストラクタは次のパラメータを受け入れます。

パラメータ | 型 | 必須 | デフォルト | 説明
--------- | ---- | -------- | ------- | -----------
`name` | `str` | **はい** | — | 関数呼び出しのためにモデルが使用するツールの固有識別子。
`description` | `str` | **はい** | — | エージェントが検索ツールをいつどのように呼び出すべきかの説明。
`input_dir` | `str` | **はい** | — | ロードおよびインデックス作成を行うドキュメントを含むローカルファイルシステムのディレクトリパス。
`embedding_model` | `Optional[BaseEmbedding]` | いいえ | `None` | カスタムの LlamaIndex `BaseEmbedding` インスタンス。省略した場合は、デフォルトで `GoogleGenAIEmbedding(model_name="gemini-embedding-2-preview", embed_batch_size=1)` になります。

### カスタムエンベディングモデル

LlamaIndex の `BaseEmbedding` インターフェースに準拠するインスタンスを渡すことで、エンベディングモデルをカスタマイズできます。

```python
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

custom_embedding = GoogleGenAIEmbedding(
    model_name="gemini-embedding-2",
    embed_batch_size=1,
)

files_retrieval = FilesRetrieval(
    name="search_documents",
    description="Search local knowledge base files.",
    input_dir=os.path.join(os.path.dirname(__file__), "data"),
    embedding_model=custom_embedding,
)
```

## 関連リソース

- [VectorStoreIndex の使用（LlamaIndex）](https://docs.llamaindex.ai/en/stable/module_guides/indexing/vector_store_index/)
- [PyPI の llama-index-embeddings-google-genai](https://pypi.org/project/llama-index-embeddings-google-genai/)
