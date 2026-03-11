# ADK エージェント向け LiteRT-LM モデルホスト

<div class="language-support-tag">
    <span class="lst-supported">ADK でサポート</span><span class="lst-python">Python v0.1.0</span>
</div>

[LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM) は、エッジプラットフォーム全体で言語モデルを効率的に実行するための C++ ライブラリです。
デスクトップ環境（Linux、macOS、Windows）では、ADK は LiteRT-LM の CLI `lit` が起動する LiteRT-LM サーバーを介して、LiteRT-LM でホストされたモデルと統合します。

## はじめに

LiteRT-LM は `Gemini` クラスで動作します。設定するのは `base_url` と `model` パラメータだけです。

1. `base_url` を LiteRT-LM サーバーの URL に設定します。例: `localhost:8001`
2. `model` を LiteRT-LM のモデル名に設定します。例: `gemma3n-e2b`

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

その後、通常どおりエージェントを実行します。

```bash
adk web
```

## LiteRT-LM サーバーの実行

LiteRT-LM サーバーは、LiteRT-LM モデルを提供する別プロセスです。LiteRT-LM CLI ツール `lit` によって起動されます。

### `lit` CLI ツールをダウンロードする

LiteRT-LM GitHub リポジトリの
[手順](https://github.com/google-ai-edge/LiteRT-LM?tab=readme-ov-file#desktop-cli-lit)
に従って `lit` CLI ツールをダウンロードしてください。

### モデルをダウンロードする

サーバーを起動する前に、まずモデルをダウンロードする必要があります。`lit` を使って LiteRT-LM モデルをダウンロードするには、*Hugging Face* のユーザーアクセストークンが必要です。*Hugging Face* アカウント用トークンは
[こちら](https://huggingface.co/settings/tokens)
から取得できます。

ダウンロード可能なモデル一覧を確認するには、`lit list` コマンドを使用します。

```bash
lit list --show_all
```

`lit pull` コマンドでモデルをダウンロードします。

```bash
export HUGGING_FACE_HUB_TOKEN="**your Hugging Face token**"
lit pull gemma3n-e2b
```

### サーバーを実行する

モデルをダウンロードしたら、次のコマンドを実行して LiteRT-LM サーバーをローカルで起動します。

```bash
lit serve --port 8001
```

!!! tip "ローカルサーバーのポート番号"

    LiteRT-LM サーバーのポート番号は任意に選べますが、エージェントコード内の `Gemini` クラスで設定した `base_url` と一致している必要があります。

### デバッグ

LiteRT-LM サーバーに到着するリクエストや、モデルに送信される正確な入力を確認するには、`--verbose` フラグを使用します。

```bash
lit serve --port 8001 --verbose
```
