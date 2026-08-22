# ADK エージェント向け LiteRT-LM モデル ホスト

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-kotlin">Kotlin v0.4.0</span>
</div>

[LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM) ライブラリを使用すると、GPU (グラフィックス プロセッシング ユニット) や TPU (テンソル プロセッシング ユニット) などの専用プロセッサを必要とせずに、さまざまなコンピューティング デバイス上で言語モデルをローカルで効率的に実行できます。LiteRT-LM は Google Gemma モデルやサードパーティ モデルを含む多くのモデルをサポートしています。このガイドでは、次の言語で ADK と LiteRT-LM を設定する手順について説明します。

- [Python](#python) 
- [Kotlin](#kotlin)

## Python

これらの手順では、LiteRT-LM のローカル ホスティング モデル サーバーである `lit` の使用を含め、Python で Gemma オープン ウェイト モデルとともに ADK で LiteRT-LM サーバーを使用する方法について説明します。

### リソースのインストール

LiteRT-LM で使用するモデルをダウンロードし、モデルの検索とダウンロードを支援する `lit` CLI ツールが必要です。

#### `lit` CLI ツールのインストール

LiteRT-LM GitHub リポジトリの [手順](https://github.com/google-ai-edge/LiteRT-LM?tab=readme-ov-file#desktop-cli-lit) に従って、`lit` CLI ツールをダウンロードしてインストールします。

#### モデルのダウンロード

サーバーを起動する前に、モデルをダウンロードする必要があります。`lit` を使用して LiteRT-LM モデルをダウンロードするには、_Hugging Face_ ユーザー アクセス トークンが必要です。_Hugging Face_ アカウント トークンは [こちら](https://huggingface.co/settings/tokens) から取得できます。

ダウンロード可能なモデルのリストを表示するには、`lit list` コマンドを使用します。

```bash
lit list --show_all
```

`lit pull` コマンドを使用してモデルをダウンロードします。

```bash
export HUGGING_FACE_HUB_TOKEN="**your Hugging Face token**"
lit pull gemma3n-e2b
```

### エージェントの構成

LiteRT-LM およびホストされたモデルに接続するようにエージェントを構成します。LiteRT-LM で Gemma モデルを実行する場合は、モデル識別子とローカル ネットワーク アドレスを使用して `Gemini` モデル クラスを構成します。

ADK および Gemma モデルで LiteRT-LM を使用するには:

1.  `base_url` をスキームを含む LiteRT-LM サーバー URL（例: `http://localhost:8001`）に設定します。
2.  `model` を LiteRT-LM モデル名（例: `gemma3n-e2b`）に設定します。

以下のコード例は、前述の Gemma モデル構成を提供するローカルにホストされた LiteRT-LM インスタンスに接続するようにエージェントを構成する方法を示しています。

```py
from google.adk.agents import Agent
from google.adk.models import Gemini

root_agent = Agent(
    model=Gemini(
        model="gemma3n-e2b",
        base_url="http://localhost:8001",
    ),
    name="dice_agent",
    description=(
        "hello world agent that can roll a die of 8 sides and check prime"
        " numbers."
    ),
    instruction="""
      You roll dice and answer questions about the outcome of the dice rolls.
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

次に、通常どおりエージェントを実行します。

```bash
adk web
```

### LiteRT-LM サーバーの実行

LiteRT-LM サーバーは、LiteRT-LM モデルを提供する独立したプロセスです。LiteRT-LM CLI ツール `lit` によって起動されます。

#### サーバーの実行

モデルをダウンロードした後、次のコマンドを実行してローカルで LiteRT-LM サーバーを起動します。

```bash
lit serve --port 8001
```

!!! tip "ローカル サーバーのポート番号"

    エージェント コードの `Gemini` クラスに設定した `base_url` と一致する限り、LiteRT-LM サーバーのポート番号は自由に選択できます。

#### デバッグ

LiteRT-LM サーバーへの受信リクエストとモデルに送信された正確な入力を確認するには、`--verbose` フラグを使用します。

```bash
lit serve --port 8001 --verbose
```

## Kotlin

これらの手順では、`com.google.adk.kt.litertlm` パッケージを使用して Kotlin で ADK と LiteRT-LM を使用する方法について説明します。

### リソースのインストール

LiteRT-LM で使用するモデルをダウンロードし、モデルの検索とダウンロードを支援する `litert-lm` CLI ツールが必要です。

#### LiteRT-LM CLI のインストール

前提条件: Python 3.10 以降

CLI をインストールするには、次を実行します。

```bash
pip install --upgrade litert-lm
```

uv の使用など、その他のインストール方法については、[LiteRT-LM CLI インストール ガイド](https://developers.google.com/edge/litert-lm/cli/installation) を参照してください。

#### モデルのダウンロード

`litert-lm` CLI ツールを使用するには、LiteRT-LM と互換性のあるモデルをダウンロードします。`litert-lm` を使用して Hugging Face から直接モデルをダウンロードします。

```bash
litert-lm import \
  --from-huggingface-repo litert-community/gemma-4-E2B-it-litert-lm \
  gemma-4-E2B-it.litertlm
```

ダウンロード後、モデルはローカルの次の場所に保存されます。

```
~/.litert-lm/models/gemma-4-E2B-it.litertlm/model.litertlm
```

`litert-lm` の詳細については、[LiteRT-LM CLI 使用ガイド](https://developers.google.com/edge/litert-lm/cli/usage) を参照してください。

### 依存関係の追加

ADK Kotlin はアダプター パッケージ `com.google.adk:google-adk-kotlin-litertlm` を介して LiteRT-LM と連携します。

`build.gradle.kts` で、依存関係に `com.google.adk:google-adk-kotlin-litertlm` および `com.google.ai.edge.litertlm:litertlm-jvm` を追加します。

```kt
repositories {
    mavenCentral()
    google()
}

dependencies {
    implementation("com.google.adk:google-adk-kotlin-core:0.8.0")
    implementation("com.google.adk:google-adk-kotlin-litertlm:0.8.0")
    implementation("com.google.ai.edge.litertlm:litertlm-jvm:0.13.1")
    // その他の依存関係...
}
```

### エージェント モデルの構成

`LlmAgent` オブジェクトの一部として `LiteRtLmModel` オブジェクトを構成することにより、LiteRT-LM を使用してエージェント用のローカル モデルを実行します。まだ ADK Kotlin プロジェクトがない場合は、[ADK 向け Kotlin クイックスタート](/ja/get-started/kotlin/) 入門ガイドに従ってください。以下のコード例は、`LlmAgent` を構成し、`model` パラメータを `LiteRtLmModel` に設定する方法を示しています。

```kt
 object HelloTimeAgent {

    // 環境変数からモデルのパスを取得します。
    private val modelPath: String by lazy {
        System.getenv("LITERT_LM_MODEL_PATH")
            ?: throw IllegalStateException(
                "LITERT_LM_MODEL_PATH environment variable must be set pointing to a .litertlm file."
            )
    }

    @JvmField
    val rootAgent =
        LlmAgent(
            name = "hello_time_agent",
            description = "Tells the current time in a specified city.",
            model =
                LiteRtLmModel.create(
                    EngineConfig(modelPath = modelPath, backend = Backend.CPU())
                ),
            instruction =
                Instruction(
                    "You are a helpful assistant that tells the current time in a city. " +
                        "Use the 'getCurrentTime' tool for this purpose."
                ),
            tools = TimeService().generatedTools(),
        )
}
```

この例では、LiteRT-LM モデル ファイルへのパスが環境変数 `LITERT_LM_MODEL_PATH` から読み取られます。モデルは CPU 上で実行されます。`backend = Backend.GPU()` を設定して GPU 上でモデルを実行することもできます。

エージェントを実行するときは、`LITERT_LM_MODEL_PATH` をモデル ファイルの場所（例: `~/.litert-lm/models/gemma-4-E2B-it.litertlm/model.litertlm`）に設定します。

### エージェントの実行

上記の変更を加えて [ADK 向け Kotlin クイックスタート](/ja/get-started/kotlin/) に従った場合、環境変数 `LITERT_LM_MODEL_PATH` をモデル ファイルのパスに設定してコマンドライン REPL を使用し、ADK エージェントを実行できます。

```bash
LITERT_LM_MODEL_PATH=~/.litert-lm/models/gemma-4-E2B-it.litertlm/model.litertlm ./gradlew run
```

対話の例:

```
Agent hello_time_agent is ready. Type 'exit' to quit.

You > what's your name?

hello_time_agent > I am Gemma 4, a Large Language Model developed by Google DeepMind.

You > what time is it in paris?

hello_time_agent > calls tool: getCurrentTime

hello_time_agent > The time in Paris is 10:30 am.
```
