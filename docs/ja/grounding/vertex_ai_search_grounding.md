# Vertex AI Searchグラウンディングについて

[Vertex AI Searchグラウンディングツール](../tools/built-in-tools.md#vertex-ai-search)は、Agent Development Kit（ADK）の強力な機能であり、AIエージェントがプライベートなエンタープライズドキュメントやデータリポジトリから情報にアクセスできるようにします。エージェントをインデックス化されたエンタープライズコンテンツに接続することで、組織のナレッジベースに基づいた回答をユーザーに提供できます。

この機能は、内部ドキュメント、ポリシー、研究論文、または[Vertex AI Search](https://cloud.google.com/enterprise-search)データストアにインデックス化された独自のコンテンツからの情報を必要とするエンタープライズ固有のクエリに特に役立ちます。エージェントがナレッジベースからの情報が必要であると判断すると、自動的にインデックス化されたドキュメントを検索し、適切な帰属表示とともに結果を応答に組み込みます。

## 学習内容

このガイドでは、次のことを学びます。

- **クイックセットアップ**: Vertex AI Search対応エージェントをゼロから作成して実行する方法
- **グラウンディングアーキテクチャ**: エンタープライズドキュメントグラウンディングの背後にあるデータフローと技術的なプロセス
- **応答構造**: グラウンディングされた応答とそのメタデータを解釈する方法
- **ベストプラクティス**: 引用とドキュメント参照をユーザーに表示するためのガイドライン

## Vertex AI Searchグラウンディングクイックスタート

このクイックスタートでは、Vertex AI Searchグラウンディング機能を備えたADKエージェントの作成について説明します。このクイックスタートでは、Python 3.9以降とターミナルアクセスを備えたローカルIDE（VS CodeまたはPyCharmなど）を想定しています。

### 1. Vertex AI Searchの準備 { #prepare-vertex-ai-search }

すでにVertex AI SearchデータストアとそのデータストアIDをお持ちの場合は、このセクションをスキップできます。そうでない場合は、[カスタム検索の開始](https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search#unstructured-data)の指示に従って、`非構造化データ`タブを選択して[データストアの作成](https://cloud.google.com/generative-ai-app-builder/docs/try-enterprise-search#create_a_data_store)の最後まで進みます。この指示により、[Alphabet投資家サイト](https://abc.xyz/)の収益報告書PDFを含むサンプルデータストアを構築します。

データストアの作成セクションを完了したら、[データストア](https://console.cloud.google.com/gen-app-builder/data-stores/)を開き、作成したデータストアを選択して、`データストアID`を見つけます。

![Vertex AI Searchデータストア](../assets/vertex_ai_search_grd_data_store.png)

後で使用するため、この`データストアID`をメモしておきます。

### 2. 環境のセットアップとADKのインストール { #set-up-environment-install-adk }

仮想環境の作成とアクティブ化：

```bash
# 作成
python -m venv .venv

# アクティブ化（新しいターミナルごと）
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

ADKのインストール：

```bash
pip install google-adk==1.5.0
```

### 3. エージェントプロジェクトの作成 { #create-agent-project }

プロジェクトディレクトリで、次のコマンドを実行します。

=== "OS X &amp; Linux"
    ```bash
    # ステップ1：エージェント用の新しいディレクトリを作成する
    mkdir vertex_search_agent

    # ステップ2：エージェント用の__init__.pyを作成する
    echo "from . import agent" > vertex_search_agent/__init__.py

    # ステップ3：agent.py（エージェント定義）と.env（認証構成）を作成する
    touch vertex_search_agent/agent.py .env
    ```

=== "Windows"
    ```shell
    # ステップ1：エージェント用の新しいディレクトリを作成する
    mkdir vertex_search_agent

    # ステップ2：エージェント用の__init__.pyを作成する
    echo "from . import agent" > vertex_search_agent/__init__.py

    # ステップ3：agent.py（エージェント定義）と.env（認証構成）を作成する
    type nul > vertex_search_agent\agent.py 
    type nul > google_search_agent\.env
    ```

#### `agent.py`の編集

次のコードをコピーして`agent.py`に貼り付け、`構成`部分の`YOUR_PROJECT_ID`と`YOUR_DATASTORE_ID`をプロジェクトIDとデータストアIDにそれぞれ置き換えます。

```python title="vertex_search_agent/agent.py"
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool

# 構成
DATASTORE_ID = "projects/YOUR_PROJECT_ID/locations/global/collections/default_collection/dataStores/YOUR_DATASTORE_ID"

root_agent = Agent(
    name="vertex_search_agent",
    model="gemini-2.5-flash",
    instruction="Vertex AI Searchを使用して内部ドキュメントから情報を見つけて質問に答えます。可能な場合は常に情報源を引用してください。",
    description="Vertex AI Search機能を備えたエンタープライズドキュメント検索アシスタント",
    tools=[VertexAiSearchTool(data_store_id=DATASTORE_ID)]
)
```

これで、次のディレクトリ構造になります。

```console
my_project/
    vertex_search_agent/
        __init__.py
        agent.py
    .env
```

### 4. 認証設定 { #authentication-setup }

**注：Vertex AI SearchにはGoogle Cloud Platform（Vertex AI）認証が必要です。Google AI Studioはこのツールではサポートされていません。**

  * [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)をセットアップする
  * ターミナルから`gcloud auth login`を実行してGoogle Cloudに認証する。
  * **`.env`**ファイルを開き、次のコードをコピーして貼り付け、プロジェクトIDと場所を更新します。

    ```env title=".env"
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
    GOOGLE_CLOUD_LOCATION=LOCATION
    ```


### 5. エージェントの実行 { #run-your-agent }

エージェントと対話するには、いくつかの方法があります。

=== "開発UI（adk web）"
    次のコマンドを実行して、**開発UI**を起動します。

    ```shell
    adk web
    ```
    
    !!!info "Windowsユーザーへの注意"

        `_make_subprocess_transport NotImplementedError`が発生した場合は、代わりに`adk web --no-reload`を使用することを検討してください。


    **ステップ1：**提供されたURL（通常は`http://localhost:8000`または`http://127.0.0.1:8000`）をブラウザで直接開きます。

    **ステップ2.** UIの左上隅にあるドロップダウンでエージェントを選択できます。「vertex_search_agent」を選択します。

    !!!note "トラブルシューティング"

        ドロップダウンメニューに「vertex_search_agent」が表示されない場合は、エージェントフォルダの**親フォルダ**（つまり、vertex_search_agentの親フォルダ）で`adk web`を実行していることを確認してください。

    **ステップ3.** これで、テキストボックスを使用してエージェントとチャットできます。

=== "ターミナル（adk run）"

    次のコマンドを実行して、Vertex AI Searchエージェントとチャットします。

    ```
    adk run vertex_search_agent
    ```
    終了するには、Cmd/Ctrl+Cを使用します。

### 📝 試してみるプロンプトの例

これらの質問で、エージェントが実際にVertex AI Searchを呼び出してAlphabetレポートから情報を取得していることを確認できます。

* 2022年第1四半期のGoogle Cloudの収益は？
* YouTubeはどうですか？

![Vertex AI Searchグラウンディングデータフロー](../assets/vertex_ai_search_grd_adk_web.png)

ADKを使用してVertex AI Searchエージェントを正常に作成し、対話しました！

## Vertex AI Searchによるグラウンディングの仕組み

Vertex AI Searchによるグラウンディングは、エージェントを組織のインデックス化されたドキュメントとデータに接続し、プライベートなエンタープライズコンテンツに基づいて正確な応答を生成できるようにするプロセスです。ユーザーのプロンプトに内部ナレッジベースからの情報が必要な場合、エージェントの基盤となるLLMは、インデックス化されたドキュメントから関連する事実を見つけるために`VertexAiSearchTool`をインテリジェントに呼び出すことを決定します。

### **データフロー図**

この図は、ユーザーのクエリがグラウンディングされた応答になるまでのステップバイステップのプロセスを示しています。

![Vertex AI Searchグラウンディングデータフロー](../assets/vertex_ai_search_grd_dataflow.png)

### **詳細な説明**

グラウンディングエージェントは、図に記載されているデータフローを使用して、エンタープライズ情報を取得、処理し、ユーザーに提示される最終的な回答に組み込みます。

1. **ユーザークエリ**: エンドユーザーは、内部ドキュメントまたはエンタープライズデータに関する質問をしてエージェントと対話します。

2. **ADKオーケストレーション**: Agent Development Kitは、エージェントの動作をオーケストレーションし、ユーザーのメッセージをエージェントのコアに渡します。

3. **LLM分析とツール呼び出し**: エージェントのLLM（Geminiモデルなど）がプロンプトを分析します。インデックス化されたドキュメントからの情報が必要であると判断した場合、VertexAiSearchToolを呼び出してグラウンディングメカニズムをトリガーします。これは、会社のポリシー、技術文書、または独自の調査に関するクエリに答えるのに最適です。

4. **Vertex AI Searchサービスとの対話**: VertexAiSearchToolは、インデックス化されたエンタープライズドキュメントを含む、構成済みのVertex AI Searchデータストアと対話します。サービスは、プライベートコンテンツに対して検索クエリを作成して実行します。

5. **ドキュメントの取得とランク付け**: Vertex AI Searchは、意味的類似性と関連性スコアリングに基づいて、データストアから最も関連性の高いドキュメントチャンクを取得してランク付けします。

6. **コンテキストインジェクション**: 検索サービスは、最終的な応答が生成される前に、取得したドキュメントスニペットをモデルのコンテキストに統合します。この重要なステップにより、モデルは組織の事実に基づいたデータを「推論」できます。

7. **グラウンディングされた応答の生成**: 関連するエンタープライズコンテンツによって情報が得られたLLMは、ドキュメントから取得した情報を組み込んだ応答を生成します。

8. **ソース付きの応答の提示**: ADKは、必要なソースドキュメント参照とgroundingMetadataを含む最終的なグラウンディングされた応答を受け取り、帰属表示とともにユーザーに提示します。これにより、エンドユーザーはエンタープライズソースに対して情報を検証できます。

## Vertex AI Search応答によるグラウンディングの理解

エージェントがVertex AI Searchを使用して応答をグラウンディングする場合、最終的なテキストの回答と、その回答を生成するために使用されたドキュメントに関するメタデータを含む詳細な情報を返します。このメタデータは、応答を検証し、エンタープライズソースに帰属表示を提供するために重要です。

### グラウンディングされた応答の例

以下は、エンタープライズドキュメントに対するグラウンディングされたクエリの後にモデルによって返されたコンテンツオブジェクトの例です。

**最終回答テキスト：**

```
「医療書記官向けのモデル開発には、主に医療文書の複雑な性質、関連する機密データ、および臨床ワークフローの厳しい要件のために、いくつかの重大な課題があります。主な課題には、**精度と信頼性**があります。医療文書には非常に高いレベルの精度が求められます。エラーは誤診、誤った治療、および法的影響につながる可能性があるためです。AIモデルが微妙な医療言語を確実にキャプチャし、主観的な情報と客観的な情報を区別し、医師と患者の対話を正確に書き起こすことができるようにすることは、大きなハードルです。**自然言語理解（NLU）と音声認識**：医療会話はしばしば速く、高度に専門化された専門用語、頭字語、略語が含まれ、さまざまなアクセントや話し方を持つ個人によって話される可能性があります... [応答は、プライバシー、統合、および技術的な課題の詳細な分析で続きます]」
```

**グラウンディングメタデータスニペット：**

これは、受け取るグラウンディングメタデータです。`adk web`では、`Response`タブでこれを見つけることができます。

```json
{
  "groundingMetadata": {
    "groundingChunks": [
      {
        "document": {
          "title": "AI in Medical Scribing: Technical Challenges",
          "uri": "projects/your-project/locations/global/dataStores/your-datastore-id/documents/doc-medical-scribe-ai-tech-challenges",
          "id": "doc-medical-scribe-ai-tech-challenges"
        }
      },
      {
        "document": {
          "title": "Regulatory and Ethical Hurdles for AI in Healthcare",
          "uri": "projects/your-project/locations/global/dataStores/your-datastore-id/documents/doc-ai-healthcare-ethics",
          "id": "doc-ai-healthcare-ethics"
        }
      }
      // ... 追加のドキュメント
    ],
    "groundingSupports": [
      {
        "groundingChunkIndices": [0, 1],
        "segment": {
          "endIndex": 637,
          "startIndex": 433,
          "text": "Ensuring that AI models can reliably capture nuanced medical language..."
        }
      }
      // ... テキストセグメントをソースドキュメントにリンクする追加のサポート
    ],
    "retrievalQueries": [
      "challenges in natural language processing medical domain",
      "AI medical scribe challenges",
      "difficulties in developing AI for medical scribes"
      // ... 実行された追加の検索クエリ
    ]
  }
}
```

### 応答の解釈方法

メタデータは、モデルによって生成されたテキストとそれを裏付けるエンタープライズドキュメントとの間のリンクを提供します。以下にステップバイステップの内訳を示します。

- **groundingChunks**: これは、モデルが参照したエンタープライズドキュメントのリストです。各チャンクには、ドキュメントのタイトル、URI（ドキュメントパス）、およびIDが含まれています。

- **groundingSupports**: このリストは、最終的な回答の特定の文を`groundingChunks`にリンクします。

- **segment**: このオブジェクトは、`startIndex`、`endIndex`、および`text`自体によって定義される、最終的なテキスト回答の特定の部分を識別します。

- **groundingChunkIndices**: この配列には、`groundingChunks`にリストされているソースに対応するインデックス番号が含まれています。たとえば、「HIPAAコンプライアンス」に関するテキストは、インデックス1の`groundingChunks`（「規制および倫理的ハードル」ドキュメント）の情報によって裏付けられています。

- **retrievalQueries**: この配列は、関連情報を見つけるためにデータストアに対して実行された特定の検索クエリを示します。

## Vertex AI Searchでグラウンディングされた応答を表示する方法

Google検索グラウンディングとは異なり、Vertex AI Searchグラウンディングには特定の表示コンポーネントは必要ありません。ただし、引用とドキュメント参照を表示すると、信頼が構築され、ユーザーは組織の信頼できる情報源に対して情報を検証できます。

### オプションの引用表示

グラウンディングメタデータが提供されるため、アプリケーションのニーズに基づいて引用表示を実装することを選択できます。

**単純なテキスト表示（最小限の実装）：**

```python
for event in events:
    if event.is_final_response():
        print(event.content.parts[0].text)
        
        # オプション：ソース数を表示する
        if event.grounding_metadata:
            print(f"\n{len(event.grounding_metadata.grounding_chunks)}個のドキュメントに基づいています")
```

**拡張された引用表示（オプション）：**各ステートメントをどのドキュメントがサポートしているかを示すインタラクティブな引用を実装できます。グラウンディングメタデータは、テキストセグメントをソースドキュメントにマッピングするために必要なすべての情報を提供します。

### 実装に関する考慮事項

Vertex AI Searchグラウンディング表示を実装する場合：

1. **ドキュメントアクセス**: 参照されているドキュメントに対するユーザー権限を確認します
2. **単純な統合**: 基本的なテキスト出力には、追加の表示ロジックは必要ありません
3. **オプションの拡張機能**: ユースケースがソース帰属の恩恵を受ける場合にのみ引用を追加します
4. **ドキュメントリンク**: 必要に応じて、ドキュメントURIをアクセス可能な内部リンクに変換します
5. **検索クエリ**: retrievalQueries配列は、データストアに対して実行された検索を示します

## まとめ

Vertex AI Searchグラウンディングは、AIエージェントを汎用アシスタントから、組織のプライベートドキュメントから正確でソースが帰属表示された情報を提供できるエンタープライズ固有のナレッジシステムに変革します。この機能をADKエージェントに統合することで、次のことが可能になります。

- インデックス化されたドキュメントリポジトリから独自のコンテンツにアクセスする
- 透明性と信頼のためのソース帰属の提供
- 検証可能なエンタープライズファクトを含む包括的な回答の提供
- Google Cloud環境内でのデータプライバシーの維持

グラウンディングプロセスは、ユーザーのクエリを組織のナレッジベースにシームレスに接続し、会話の流れを維持しながらプライベートドキュメントからの関連コンテキストで応答を充実させます。適切に実装すると、エージェントはエンタープライズ情報の発見と意思決定のための強力なツールになります。
