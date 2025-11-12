# Google検索グラウンディングについて

[Google検索グラウンディングツール](../tools/built-in-tools.md#google-search)は、Agent Development Kit（ADK）の強力な機能であり、AIエージェントがウェブからリアルタイムで信頼できる情報にアクセスできるようにします。エージェントをGoogle検索に接続することで、信頼できる情報源に裏付けられた最新の回答をユーザーに提供できます。

この機能は、天気予報、ニュースイベント、株価、またはモデルのトレーニングデータカットオフ以降に変更された可能性のある事実など、最新情報を必要とするクエリに特に役立ちます。エージェントが外部情報が必要であると判断すると、自動的にウェブ検索を実行し、適切な帰属表示とともに結果を応答に組み込みます。

## 学習内容

このガイドでは、次のことを学びます。

- **クイックセットアップ**: Google検索対応エージェントをゼロから作成して実行する方法
- **グラウンディングアーキテクチャ**: ウェブグラウンディングの背後にあるデータフローと技術的なプロセス
- **応答構造**: グラウンディングされた応答とそのメタデータを解釈する方法
- **ベストプラクティス**: 検索結果と引用をユーザーに表示するためのガイドライン

### 追加リソース

追加リソースとして、[Geminiフルスタックエージェント開発キット（ADK）クイックスタート](https://github.com/google/adk-samples/tree/main/python/agents/gemini-fullstack)には、フルスタックアプリケーションの例として[Google検索グラウンディングの優れた実用例](https://github.com/google/adk-samples/blob/main/python/agents/gemini-fullstack/app/agent.py)があります。

## Google検索グラウンディングクイックスタート

このクイックスタートでは、Google検索グラウンディング機能を備えたADKエージェントの作成について説明します。このクイックスタートでは、Python 3.9以降とターミナルアクセスを備えたローカルIDE（VS CodeまたはPyCharmなど）を想定しています。

### 1. 環境のセットアップとADKのインストール { #set-up-environment-install-adk }

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
pip install google-adk==1.4.2
```

### 2. エージェントプロジェクトの作成 { #create-agent-project }

プロジェクトディレクトリで、次のコマンドを実行します。

=== "OS X &amp; Linux"
    ```bash
    # ステップ1：エージェント用の新しいディレクトリを作成する
    mkdir google_search_agent

    # ステップ2：エージェント用の__init__.pyを作成する
    echo "from . import agent" > google_search_agent/__init__.py

    # ステップ3：agent.py（エージェント定義）と.env（Gemini認証構成）を作成する
    touch google_search_agent/agent.py .env
    ```

=== "Windows"
    ```shell
    # ステップ1：エージェント用の新しいディレクトリを作成する
    mkdir google_search_agent

    # ステップ2：エージェント用の__init__.pyを作成する
    echo "from . import agent" > google_search_agent/__init__.py

    # ステップ3：agent.py（エージェント定義）と.env（Gemini認証構成）を作成する
    type nul > google_search_agent\agent.py 
    type nul > google_search_agent\.env
    ```



#### `agent.py`の編集

次のコードをコピーして`agent.py`に貼り付けます。

```python title="google_search_agent/agent.py"
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="google_search_agent",
    model="gemini-2.5-flash",
    instruction="必要に応じてGoogle検索を使用して質問に答えます。常に情報源を引用してください。",
    description="Google検索機能を備えたプロフェッショナルな検索アシスタント",
    tools=[google_search]
)
```

これで、次のディレクトリ構造になります。

```console
my_project/
    google_search_agent/
        __init__.py
        agent.py
    .env
```

### 3. プラットフォームの選択 { #choose-a-platform }

エージェントを実行するには、エージェントがGeminiモデルを呼び出すために使用するプラットフォームを選択する必要があります。Google AI StudioまたはVertex AIから1つ選択します。

=== "Gemini - Google AI Studio"
    1. [Google AI Studio](https://aistudio.google.com/apikey)からAPIキーを取得します。
    2. Pythonを使用している場合は、**`.env`**ファイルを開き、次のコードをコピーして貼り付けます。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3. `PASTE_YOUR_ACTUAL_API_KEY_HERE`を実際の`APIキー`に置き換えます。

=== "Gemini - Google Cloud Vertex AI"
    1. 既存の[Google Cloud](https://cloud.google.com/?e=48754805&hl=en)アカウントとプロジェクトが必要です。
        * [Google Cloudプロジェクト](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)をセットアップする
        * [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)をセットアップする
        * ターミナルから`gcloud auth login`を実行してGoogle Cloudに認証する。
        * [Vertex AI APIを有効にする](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)。
    2. Pythonを使用している場合は、**`.env`**ファイルを開き、次のコードをコピーして貼り付け、プロジェクトIDと場所を更新します。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=LOCATION
        ```

### 4. エージェントの実行 { #run-your-agent }

エージェントと対話するには、いくつかの方法があります。

=== "開発UI（adk web）"
    次のコマンドを実行して、**開発UI**を起動します。

    ```shell
    adk web
    ```
    
    !!!info "Windowsユーザーへの注意"

        `_make_subprocess_transport NotImplementedError`が発生した場合は、代わりに`adk web --no-reload`を使用することを検討してください。


    **ステップ1：**提供されたURL（通常は`http://localhost:8000`または`http://127.0.0.1:8000`）をブラウザで直接開きます。

    **ステップ2.** UIの左上隅にあるドロップダウンでエージェントを選択できます。「google_search_agent」を選択します。

    !!!note "トラブルシューティング"

        ドロップダウンメニューに「google_search_agent」が表示されない場合は、エージェントフォルダの**親フォルダ**（つまり、google_search_agentの親フォルダ）で`adk web`を実行していることを確認してください。

    **ステップ3.** これで、テキストボックスを使用してエージェントとチャットできます。

=== "ターミナル（adk run）"

    次のコマンドを実行して、Weatherエージェントとチャットします。

    ```
    adk run google_search_agent
    ```
    終了するには、Cmd/Ctrl+Cを使用します。

### 📝 試してみるプロンプトの例

これらの質問で、エージェントが実際にGoogle検索を呼び出して最新の天気と時刻を取得していることを確認できます。

* ニューヨークの天気は？
* ニューヨークの今の時刻は？
* パリの天気は？
* パリの今の時刻は？

![adk webでエージェントを試す](../assets/google_search_grd_adk_web.png)

ADKを使用してGoogle検索エージェントを正常に作成し、対話しました！

## Google検索によるグラウンディングの仕組み

グラウンディングは、エージェントをウェブ上のリアルタイム情報に接続し、より正確で最新の応答を生成できるようにするプロセスです。ユーザーのプロンプトに、モデルがトレーニングされていない情報や時間的制約のある情報が必要な場合、エージェントの基盤となる大規模言語モデルは、関連する事実を見つけるためにgoogle_searchツールをインテリジェントに呼び出すことを決定します。

### **データフロー図**

この図は、ユーザーのクエリがグラウンディングされた応答になるまでのステップバイステップのプロセスを示しています。

![](../assets/google_search_grd_dataflow.png)

### **詳細な説明**

グラウンディングエージェントは、図に記載されているデータフローを使用して、外部情報を取得、処理し、ユーザーに提示される最終的な回答に組み込みます。

1. **ユーザークエリ**: エンドユーザーは、質問をしたりコマンドを与えたりしてエージェントと対話します。
2. **ADKオーケストレーション**: Agent Development Kitは、エージェントの動作をオーケストレーションし、ユーザーのメッセージをエージェントのコアに渡します。
3. **LLM分析とツール呼び出し**: エージェントのLLM（Geminiモデルなど）がプロンプトを分析します。外部の最新情報が必要であると判断した場合、google_searchツールを呼び出してグラウンディングメカニズムをトリガーします。これは、最近のニュース、天気、またはモデルのトレーニングデータに存在しない事実に関するクエリに答えるのに最適です。
4. **グラウンディングサービスとの対話**: google_searchツールは、1つ以上のクエリを作成してGoogle検索インデックスに送信する内部グラウンディングサービスと対話します。
5. **コンテキストインジェクション**: グラウンディングサービスは、関連するウェブページとスニペットを取得します。次に、最終的な応答が生成される前に、これらの検索結果をモデルのコンテキストに統合します。この重要なステップにより、モデルは事実に基づいたリアルタイムのデータを「推論」できます。
6. **グラウンディングされた応答の生成**: 新鮮な検索結果によって情報が得られたLLMは、取得した情報を組み込んだ応答を生成します。
7. **ソース付きの応答の提示**: ADKは、必要なソースURLとgroundingMetadataを含む最終的なグラウンディングされた応答を受け取り、帰属表示とともにユーザーに提示します。これにより、エンドユーザーは情報を検証し、エージェントの回答に対する信頼を築くことができます。

### Google検索応答によるグラウンディングの理解

エージェントがGoogle検索を使用して応答をグラウンディングする場合、最終的なテキストの回答だけでなく、その回答を生成するために使用したソースも含む詳細な情報セットを返します。このメタデータは、応答を検証し、元のソースに帰属表示を提供するために重要です。

#### **グラウンディングされた応答の例**

以下は、グラウンディングされたクエリの後にモデルによって返されたコンテンツオブジェクトの例です。

**最終回答テキスト：**

```
「はい、インテルマイアミはFIFAクラブワールドカップの最後の試合に勝ちました。彼らは2番目のグループステージの試合でFCポルトに2-1で勝利しました。トーナメントでの最初の試合は、アルアハリFCとの0-0の引き分けでした。インテルマイアミは、2025年6月23日月曜日にパルメイラスとの3番目のグループステージの試合を予定しています。」
```

**グラウンディングメタデータスニペット：**

```json
"groundingMetadata": {
  "groundingChunks": [
    { "web": { "title": "mlssoccer.com", "uri": "..." } },
    { "web": { "title": "intermiamicf.com", "uri": "..." } },
    { "web": { "title": "mlssoccer.com", "uri": "..." } }
  ],
  "groundingSupports": [
    {
      "groundingChunkIndices": [0, 1],
      "segment": {
        "startIndex": 65,
        "endIndex": 126,
        "text": "彼らは2番目のグループステージの試合でFCポルトに2-1で勝利しました。"
      }
    },
    {
      "groundingChunkIndices": [1],
      "segment": {
        "startIndex": 127,
        "endIndex": 196,
        "text": "トーナメントでの最初の試合は、アルアハリFCとの0-0の引き分けでした。"
      }
    },
    {
      "groundingChunkIndices": [0, 2],
      "segment": {
        "startIndex": 197,
        "endIndex": 303,
        "text": "インテルマイアミは、2025年6月23日月曜日にパルメイラスとの3番目のグループステージの試合を予定しています。"
      }
    }
  ],
  "searchEntryPoint": { ... }
}

```

#### **応答の解釈方法**

メタデータは、モデルによって生成されたテキストとそれを裏付けるソースとの間のリンクを提供します。以下にステップバイステップの内訳を示します。

1. **groundingChunks**: これは、モデルが参照したウェブページのリストです。各チャンクには、ウェブページのタイトルとソースにリンクするURIが含まれています。
2. **groundingSupports**: このリストは、最終的な回答の特定の文をgroundingChunksにリンクします。
   * **segment**: このオブジェクトは、startIndex、endIndex、およびテキスト自体によって定義される、最終的なテキスト回答の特定の部分を識別します。
   * **groundingChunkIndices**: この配列には、groundingChunksにリストされているソースに対応するインデックス番号が含まれています。たとえば、「彼らは2番目のグループステージの試合でFCポルトに2-1で勝利しました...」という文は、インデックス0と1のgroundingChunks（mlssoccer.comとintermiamicf.comの両方）の情報によって裏付けられています。

### Google検索でグラウンディングされた応答を表示する方法

グラウンディングを使用する上で重要な部分は、引用や検索候補を含む情報をエンドユーザーに正しく表示することです。これにより、信頼が構築され、ユーザーは情報を検証できます。

![Google検索からの応答](../assets/google_search_grd_resp.png)

#### **検索候補の表示**

`groundingMetadata`の`searchEntryPoint`オブジェクトには、検索クエリ候補を表示するための事前にフォーマットされたHTMLが含まれています。サンプル画像に見られるように、これらは通常、ユーザーが関連トピックを探索できるクリック可能なチップとしてレンダリングされます。

**searchEntryPointからレンダリングされたHTML：**メタデータは、Googleロゴと「次のFIFAクラブワールドカップはいつですか」や「インテルマイアミFIFAクラブワールドカップの歴史」などの関連クエリのチップを含む検索候補バーをレンダリングするために必要なHTMLとCSSを提供します。このHTMLをアプリケーションのフロントエンドに直接統合すると、候補が意図したとおりに表示されます。

詳細については、Vertex AIドキュメントの[Google検索候補の使用](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions)を参照してください。

## まとめ

Google検索グラウンディングは、AIエージェントを静的な知識リポジトリから、リアルタイムで正確な情報を提供できる動的なウェブ接続アシスタントに変革します。この機能をADKエージェントに統合することで、次のことが可能になります。

- トレーニングデータを超えた最新情報へのアクセス
- 透明性と信頼のためのソース帰属の提供
- 検証可能な事実を含む包括的な回答の提供
- 関連する検索候補によるユーザーエクスペリエンスの向上

グラウンディングプロセスは、ユーザーのクエリをGoogleの広大な検索インデックスにシームレスに接続し、会話の流れを維持しながら最新のコンテキストで応答を充実させます。グラウンディングされた応答を適切に実装して表示することで、エージェントは情報発見と意思決定のための強力なツールになります。
