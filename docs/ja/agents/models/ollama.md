# ADK エージェント向けの Ollama モデルホスト

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

[Ollama](https://ollama.com/)はオープンソースモデルをローカルでホストして実行できるツールです。
ADKは[LiteLLM](/adk-docs/agents/models/litellm/)モデルコネクターライブラリを通じて
Ollamaでホストされたモデルを統合します。

## はじめに

Ollamaでホストされたモデルを使ってエージェントを作成するには、LiteLLMラッパーを使用します。
以下の例は、Gemmaオープンモデルをエージェントで使う基本実装です。

```py
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/gemma3:latest"),
    name="dice_agent",
    description=(
        "hello world agent that can roll a dice of 8 sides and check prime"
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

!!! warning "警告: `ollama_chat` インターフェースを使用"

    `ollama`ではなくプロバイダーとして`ollama_chat`を設定してください。
    `ollama`を使うと、無限ループの関数呼び出しや、前のコンテキスト無視などの予期しない動作になることがあります。

!!! tip "`OLLAMA_API_BASE` 環境変数の使用"

    LiteLLMでは生成時に`api_base`パラメータを指定できますが、
    v1.65.5ではその他の API 呼び出しで環境変数を参照します。
    すべてのリクエストを適切にルーティングするには、Ollama サーバー URL に対して
    `OLLAMA_API_BASE` を設定してください。

```bash
export OLLAMA_API_BASE="http://localhost:11434"
adk web
```

## モデルの選択

エージェントがツールを利用する場合は、[Ollama ウェブサイト](https://ollama.com/search?c=tools)で
ツールサポート付きモデルを選択してください。安定した結果を得るには、
ツール対応のモデルを使用します。
以下のコマンドでモデルのツールサポートを確認できます。

```bash
ollama show mistral-small3.1
  Model
    architecture        mistral3
    parameters          24.0B
    context length      131072
    embedding length    5120
    quantization        Q4_K_M

  Capabilities
    completion
    vision
    tools
```

`Capabilities` に **tools** が含まれていることを確認します。
必要に応じてテンプレートを確認し調整できます。

```bash
ollama show --modelfile llama3.2 > model_file_to_modify
```

たとえば上記モデルのデフォルトテンプレートは、モデルに常時関数呼び出しを
要求する傾向があります。これにより無限関数呼び出しループが発生する可能性があります。

```
Given the following functions, please respond with a JSON for a function call
with its proper arguments that best answers the given prompt.

Respond in the format {"name": function name, "parameters": dictionary of
argument name and its value}. Do not use variables.
```

たとえば以下のように、より説明的なプロンプトに置き換えることで無限ループを防げます。

```
Review the user's prompt and the available functions listed below.

First, determine if calling one of these functions is the most appropriate way
to respond. A function call is likely needed if the prompt asks for a specific
action, requires external data lookup, or involves calculations handled by the
functions. If the prompt is a general question or can be answered directly, a
function call is likely NOT needed.

If you determine a function call IS required: Respond ONLY with a JSON object in
the format {"name": "function_name", "parameters": {"argument_name": "value"}}.
Ensure parameter values are concrete, not variables.

If you determine a function call IS NOT required: Respond directly to the user's
prompt in plain text, providing the answer or information requested. Do not
output any JSON.
```

その後、以下のコマンドで新しいモデルを作成できます。

```bash
ollama create llama3.2-modified -f model_file_to_modify
```

## OpenAI プロバイダーの使用

代わりに `openai` をプロバイダー名として使用できます。この場合は
`OLLAMA_API_BASE` ではなく次を設定します。
- `OPENAI_API_BASE=http://localhost:11434/v1`
- `OPENAI_API_KEY=anything`

`API_BASE` の値の末尾に `"/v1"` が必要です。

```py
root_agent = Agent(
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description=(
        "hello world agent that can roll a dice of 8 sides and check prime"
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

```bash
export OPENAI_API_BASE=http://localhost:11434/v1
export OPENAI_API_KEY=anything
adk web
```

### デバッグ

インポート直後に次を追加すると、Ollama サーバーへ送信されるリクエストを確認できます。

```py
import litellm
litellm._turn_on_debug()
```

以下のような行を探します。

```bash
Request Sent from LiteLLM:
curl -X POST \
http://localhost:11434/api/chat \
-d '{'model': 'mistral-small3.1', 'messages': [{'role': 'system', 'content': ...
```
