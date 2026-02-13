# Pythonでストリーミングエージェントを構築する

このクイックスタートでは、シンプルなエージェントを作成し、ADK ストリーミングを活用して、低遅延（Low-latency）かつ双方向の音声およびビデオ通信を実現する方法を学びます。ADK をインストールし、基本的な「Google 検索」エージェントを設定して、`adk web` ツールでストリーミングエージェントを実行してみます。その後、ADK ストリーミングと [FastAPI](https://fastapi.tiangolo.com/) を使用して、シンプルな非同期 Web アプリを自作する方法について説明します。

**注:** このガイドは、Windows、Mac、Linux 環境でターミナルを使用した経験があることを前提としています。

## 音声/ビデオストリーミングでサポートされているモデル {#supported-models}

ADK で音声/ビデオストリーミングを使用するには、Live API をサポートする Gemini モデルを使用する必要があります。Gemini Live API をサポートする **モデル ID** は、以下のドキュメントで確認できます。

- [Google AI Studio: Gemini Live API](https://ai.google.dev/gemini-api/docs/models#live-api)
- [Vertex AI: Gemini Live API](https://cloud.google.com/vertex-ai/generative-ai/docs/live-api)

## 1. 環境設定と ADK のインストール { #setup-environment-install-adk }

仮想環境の作成とアクティブ化（推奨）:

```bash
# 作成
python -m venv .venv
# アクティブ化（新しいターミナルを開くたびに実行）
# macOS/Linux: source .venv/bin/activate
# Windows CMD: .venv\Scripts\activate.bat
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

ADK のインストール:

```bash
pip install google-adk
```

## 2. プロジェクト構造 { #project-structure }

空のファイルを含む以下のフォルダ構造を作成してください。

```console
adk-streaming/  # プロジェクトフォルダ
└── app/ # Web アプリフォルダ
    ├── .env # Gemini API キー
    └── google_search_agent/ # エージェントフォルダ
        ├── __init__.py # Python パッケージ
        └── agent.py # エージェント定義
```

### agent.py

以下のコードブロックを `agent.py` ファイルにコピー＆ペーストしてください。

`model` については、前述の [モデルセクション](#supported-models) で説明されているモデル ID を再確認してください。

```py
from google.adk.agents import Agent
from google.adk.tools import google_search  # ツール（Tool）のインポート

root_agent = Agent(
   # エージェントの一意の名前。
   name="basic_search_agent",
   # エージェントが使用する大規模言語モデル（LLM）。
   # https://google.github.io/adk-docs/get-started/streaming/quickstart-streaming/#supported-models から
   # Live をサポートする最新のモデル ID を入力してください。
   model="...",
   # エージェントの目的についての短い説明。
   description="Agent to answer questions using Google Search.",
   # エージェントの振る舞いを設定する指示（Instruction）。
   instruction="You are an expert researcher. You always stick to the facts.",
   # Google 検索によるグラウンディング（Grounding）を実行するために google_search ツールを追加。
   tools=[google_search]
)
```

`agent.py` は、すべてのエージェントロジックが保存される場所であり、`root_agent` が定義されている必要があります。

[Google 検索によるグラウンディング](https://ai.google.dev/gemini-api/docs/grounding?lang=python#configure-search)機能をいかに簡単に統合できたかに注目してください。`Agent` クラスと `google_search` ツールが LLM との複雑な相互作用や検索 API によるグラウンディングを処理するため、あなたはエージェントの「目的」と「振る舞い」に集中することができます。

![intro_components.png](../../assets/quickstart-streaming-tool.png)

以下のコードブロックを `__init__.py` ファイルにコピー＆ペーストしてください。

```py title="__init__.py"
from . import agent
```

## 3\. プラットフォームの設定 { #set-up-the-platform }

エージェントを実行するには、Google AI Studio または Google Cloud Vertex AI のいずれかのプラットフォームを選択してください。

=== "Gemini - Google AI Studio"
    1. [Google AI Studio](https://aistudio.google.com/apikey) から API キーを取得します。
    2. (`app/`) 内にある **`.env`** ファイルを開き、以下のコードをコピー＆ペーストします。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=FALSE
        GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
        ```

    3. `PASTE_YOUR_ACTUAL_API_KEY_HERE` の部分を実際の `API KEY` に置き換えてください。

=== "Gemini - Google Cloud Vertex AI"
    1. 既存の [Google Cloud](https://cloud.google.com/?e=48754805&hl=en) アカウントとプロジェクトが必要です。
        * [Google Cloud プロジェクト](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-gcp)を設定します。
        * [gcloud CLI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#setup-local) を設定します。
        * ターミナルから `gcloud auth login` を実行して、Google Cloud に認証します。
        * [Vertex AI API を有効化](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com)します。
    2. (`app/`) 内にある **`.env`** ファイルを開きます。以下のコードをコピー＆ペーストし、プロジェクト ID とロケーション（Region）を更新してください。

        ```env title=".env"
        GOOGLE_GENAI_USE_VERTEXAI=TRUE
        GOOGLE_CLOUD_PROJECT=PASTE_YOUR_ACTUAL_PROJECT_ID
        GOOGLE_CLOUD_LOCATION=us-central1
        ```

## 4. `adk web` でエージェントを試す { #try-the-agent-with-adk-web }

これでエージェントを試す準備が整いました。以下のコマンドを実行して **dev UI** を起動します。まず、カレントディレクトリが `app` に設定されていることを確認してください。

```shell
cd app
```

また、以下のコマンドを使用して `SSL_CERT_FILE` 変数を設定してください。これは、後で行う音声とビデオのテストに必要です。

=== "OS X &amp; Linux"
    ```bash
    export SSL_CERT_FILE=$(python -m certifi)
    ```

=== "Windows"
    ```powershell
    $env:SSL_CERT_FILE = (python -m certifi)
    ```

その後、dev UI を実行します。

```shell
adk web
```

!!!info "Windows ユーザーへの注意"

    `_make_subprocess_transport NotImplementedError` エラーが発生した場合は、代わりに `adk web --no-reload` を使用することを検討してください。

!!! warning "注意: ADK Web は開発用途限定"

    ADK Web は***本番デプロイでの利用を想定していません***。
    ADK Web は開発とデバッグ用途でのみ使用してください。

提供された URL（通常は `http://localhost:8000` または `http://127.0.0.1:8000`）を **ブラウザで直接** 開いてください。この接続は完全にローカルマシン内で維持されます。`google_search_agent` を選択してください。

### テキストで試す

UI に以下のプロンプトを入力して試してみてください。

* What is the weather in New York?（ニューヨークの天気はどうですか？）
* What is the time in New York?（ニューヨークは今何時ですか？）
* What is the weather in Paris?（パリの天気はどうですか？）
* What is the time in Paris?（パリは今何時ですか？）

エージェントは google_search ツールを使用して最新情報を取得し、質問に回答します。

### 音声とビデオで試す

音声を試すには、Web ブラウザをリロードし、マイクボタンをクリックして音声入力を有効にしてから、同じ質問を声で尋ねてください。リアルタイムで音声による回答が聞こえてきます。

ビデオを試すには、Web ブラウザをリロードし、カメラボタンをクリックしてビデオ入力を有効にし、「What do you see?（何が見えますか？）」といった質問をしてください。エージェントはビデオ入力で見えているものについて答えてくれます。

（マイクやカメラのボタンは一度クリックするだけで十分です。あなたの音声やビデオがモデルにストリーミングされ、モデルの応答が継続的にストリーミングされて戻ってきます。マイクやカメラのボタンを複数回クリックすることはサポートされていません。）

### ツールを停止する

コンソールで `Ctrl-C` を押して `adk web` を停止します。

### ADK ストリーミングに関する注記

以下の機能は、ADK ストリーミングの将来のバージョンでサポートされる予定です: Callback、LongRunningTool、ExampleTool、および Shell エージェント（例: SequentialAgent）。

おめでとうございます！ ADK を使用して最初のストリーミングエージェントを作成し、対話することに成功しました！

## 次のステップ: カスタムストリーミングアプリの構築

[カスタムオーディオストリーミングアプリ](../../streaming/custom-streaming.md)のチュートリアルでは、ADK ストリーミングと [FastAPI](https://fastapi.tiangolo.com/) で構築されたカスタム非同期 Web アプリのサーバーおよびクライアントコードの概要を説明し、リアルタイムの双方向オーディオおよびテキスト通信を実現する方法を案内しています。
