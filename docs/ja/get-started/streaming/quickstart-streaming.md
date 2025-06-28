# クイックスタート (ストリーミング / Python) {#adk-streaming-quickstart}

このクイックスタートでは、シンプルなエージェントを作成し、ADKストリーミングを使用して低遅延かつ双方向の音声・映像コミュニケーションを有効にする方法を学びます。ADKをインストールし、基本的な「Google検索」エージェントをセットアップし、`adk web`ツールでストリーミングエージェントを実行してみます。その後、ADKストリーミングと[FastAPI](https://fastapi.tiangolo.com/)を使用して、自分で簡単な非同期Webアプリを構築する方法を説明します。

**注:** このガイドは、Windows、Mac、Linux環境でのターミナル使用経験があることを前提としています。

## 音声/映像ストリーミングでサポートされているモデル {#supported-models}

ADKで音声/映像ストリーミングを使用するには、Live APIをサポートするGeminiモデルを使用する必要があります。Gemini Live APIをサポートする**モデルID**は、以下のドキュメントで確認できます。

-   [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
-   [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## 1. 環境のセットアップとADKのインストール {#1.-setup-installation}

仮想環境の作成と有効化（推奨）:

```bash
# 作成
python -m venv .venv
# 有効化（新しいターミナルごと）
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

ADKのインストール:

```bash
pip install google-adk
```

## 2. プロジェクト構造 {#2.-project-structure}

空のファイルで以下のフォルダ構造を作成します。

```console
adk-streaming/  # プロジェクトフォルダ
└── app/ # Webアプリのフォルダ
    ├── .env # Gemini APIキー
    └── google_search_agent/ # エージェントのフォルダ
        ├── __init__.py # Pythonパッケージ
        └── agent.py # エージェントの定義
```

### agent.py

以下のコードブロックをコピーして、`agent.py`ファイルに貼り付けます。

`model`については、前述の[モデルセクション](#supported-models)で説明したように、モデルIDを再確認してください。

```py
from google.adk.agents import Agent
from google.adk.tools import google_search  # ツールをインポート

root_agent = Agent(
   # エージェントの一意な名前。
   name="basic_search_agent",
   # エージェントが使用する大規模言語モデル（LLM）。
   # 以下のリンクからliveをサポートする最新のモデルIDを入力してください。
   # https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/#supported-models
   model="...",  # 例: model="gemini-2.0-flash-live-001" または model="gemini-2.0-flash-live-preview-04-09"
   # エージェントの目的の簡単な説明。
   description="Google検索を使用して質問に答えるエージェント。",
   # エージェントの振る舞いを設定するための指示。
   instruction="あなたは熟練した研究者です。常に事実に忠実に行動します。",
   # Google検索でグラウンディングを実行するためにgoogle_searchツールを追加します。
   tools=[google_search]
)
```

`agent.py`には、すべてのエージェントのロジックが保存され、`root_agent`が定義されている必要があります。

[Google検索によるグラウンディング](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search)機能がどれほど簡単に統合されたかに注目してください。`Agent`クラスと`google_search`ツールが、LLMや検索APIとの複雑な相互作用を処理するため、あなたはエージェントの*目的*と*振る舞い*に集中できます。

![intro_components.png](../../assets/quickstart-streaming-tool.png)

以下のコードブロックを`__init__.py`ファイルにコピーして貼り付けます。

```py title="__init__.py"
from . import agent
```

## 3. プラットフォームのセットアップ {#3.-set-up-the-platform}

エージェントを実行するには、Google AI StudioまたはGoogle Cloud Vertex AIからプラットフォームを選択します。

=== "Gemini - Google AI Studio"
    1.  [Google AI Studio](https://aistudio.google.com/apikey)からAPIキーを取得します。
    2.  `app/`内にある**`.env`**ファイルを開き、以下のコードをコピーして貼り付けます。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3.  `PASTE_YOUR_ACTUAL_API_KEY_HERE`を実際の`API KEY`に置き換えてください。

=== "Gemini - Google Cloud Vertex AI"
    1.  既存の[Google Cloud](https://cloud.google.com/?e=48754805&hl=ja)アカウントとプロジェクトが必要です。
        *   [Google Cloudプロジェクトをセットアップする](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)
        *   [gcloud CLIをセットアップする](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local)
        *   ターミナルから`gcloud auth login`を実行してGoogle Cloudに認証します。
        *   [Vertex AI APIを有効にする](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)。
    2.  `app/`内にある**`.env`**ファイルを開きます。以下のコードをコピーして貼り付け、プロジェクトIDとロケーションを更新してください。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=PASTE_YOUR_ACTUAL_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

## 4. `adk web`でエージェントを試す {#4.-try-it-adk-web}

これでエージェントを試す準備ができました。次のコマンドを実行して**開発UI**を起動します。まず、現在のディレクトリを`app`に設定してください。

```shell
cd app
```

また、次のコマンドで`SSL_CERT_FILE`変数を設定します。これは後の音声および映像テストで必要になります。

```shell
export SSL_CERT_FILE=$(python -m certifi)
```

次に、開発UIを実行します。

```shell
adk web
```

!!!info "Windowsユーザーへの注意"

    `_make_subprocess_transport NotImplementedError`が発生した場合は、代わりに`adk web --no-reload`の使用を検討してください。

提供されたURL（通常は `http://localhost:8000` または `http://127.0.0.1:8000`）を**直接ブラウザで**開きます。この接続は、完全にローカルマシン上に留まります。`google_search_agent`を選択します。

### テキストで試す

UIに以下のプロンプトを入力して試してみてください。

*   ニューヨークの天気は？
*   ニューヨークの今の時間は？
*   パリの天気は？
*   パリの今の時間は？

エージェントはgoogle_searchツールを使用して、これらの質問に答えるための最新情報を取得します。

### 音声と映像で試す

音声で試すには、Webブラウザをリロードし、マイクボタンをクリックして音声入力を有効にし、同じ質問を音声で行います。リアルタイムで音声の回答が聞こえます。

映像で試すには、Webブラウザをリロードし、カメラボタンをクリックして映像入力を有効にし、「何が見えますか？」のような質問をします。エージェントは映像入力で見えるものについて回答します。

（マイクまたはカメラボタンを一度クリックするだけで十分です。音声や映像はモデルに継続的にストリーミングされ、モデルの応答も継続的にストリーミングで返されます。マイクまたはカメラボタンを複数回クリックすることはサポートされていません。）

### ツールを停止する

コンソールで`Ctrl-C`を押して`adk web`を停止します。

### ADKストリーミングに関する注意

以下の機能は、ADKストリーミングの将来のバージョンでサポートされる予定です：Callback、LongRunningTool、ExampleTool、およびシェルエージェント（例：SequentialAgent）。

おめでとうございます！ADKを使用して、最初のストリーミングエージェントの作成と対話に成功しました！

## 次のステップ：カスタムストリーミングアプリの構築

[カスタム音声ストリーミングアプリ](../../streaming/custom-streaming.md)のチュートリアルでは、ADKストリーミングと[FastAPI](https://fastapi.tiangolo.com/)で構築されたカスタム非同期Webアプリのサーバーとクライアントのコードの概要を説明し、リアルタイムの双方向音声およびテキスト通信を可能にします。