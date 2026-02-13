# ADK エージェント用の LiteLLM モデルコネクター

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

[LiteLLM](https://docs.litellm.ai/) は、モデルとモデルホスティングサービスのための
変換レイヤーとして機能する Python ライブラリで、100 以上の LLM に対して
標準化された OpenAI 互換インターフェースを提供します。
ADK は LiteLLM を介して、OpenAI、Anthropic（非 Vertex AI）、Cohere など多数の
プロバイダーの幅広い LLM にアクセスできます。
Open-source モデルをローカルで実行したり、セルフホストして運用制御・コスト最適化・
プライバシー保護・オフライン利用へ活用できます。

LiteLLM ライブラリを使うことで、リモートまたはローカルでホストされた AI モデルに接続できます。

*   **リモートモデルホスト:** `LiteLlm` ラッパークラスを使用し、`LlmAgent` の `model` パラメータとして設定します。
*   **ローカルモデルホスト:** ローカルモデルサーバーを参照するように設定された
    `LiteLlm` ラッパークラスを使用します。ローカルホスティング例は
    [Ollama](/adk-docs/agents/models/ollama/) や
    [vLLM](/adk-docs/agents/models/vllm/) のドキュメントを参照してください。

??? warning "LiteLLM の Windows 文字エンコーディング"

    ADK エージェントを Windows で LiteLLM と一緒に使う場合、`UnicodeDecodeError` が発生する可能性があります。
    これは LiteLLM が `cp1252` など既定の Windows エンコーディングで
    キャッシュファイルを読み込もうとすることが原因です。`PYTHONUTF8` 環境変数を `1` に設定すると、
    Python のすべてのファイル I/O が UTF-8 で処理され、エラーを防げます。

    **例（PowerShell）:**
    ```powershell
    # 現在のセッションのみ
    $env:PYTHONUTF8 = "1"

    # ユーザー環境に永続化
    [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.EnvironmentVariableTarget]::User)
    ```

## セットアップ

1. **LiteLLM のインストール:**
        ```shell
        pip install litellm
        ```
2. **プロバイダー API キーの設定:** 使用するプロバイダーの API キーを環境変数として設定します。

    * *OpenAI の例:*

        ```shell
        export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
        ```

    * *Anthropic（非 Vertex AI）の例:*

        ```shell
        export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
        ```

    * *その他のプロバイダーについては* [LiteLLM Providers ドキュメント](https://docs.litellm.ai/docs/providers)
      に従って適切な環境変数名を確認してください。*

## 実装例

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# --- Example Agent using OpenAI's GPT-4o ---
# (Requires OPENAI_API_KEY)
agent_openai = LlmAgent(
    model=LiteLlm(model="openai/gpt-4o"), # LiteLLM model string format
    name="openai_agent",
    instruction="You are a helpful assistant powered by GPT-4o.",
    # ... other agent parameters
)

# --- Example Agent using Anthropic's Claude Haiku (non-Vertex) ---
# (Requires ANTHROPIC_API_KEY)
agent_claude_direct = LlmAgent(
    model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
    name="claude_direct_agent",
    instruction="You are an assistant powered by Claude Haiku.",
    # ... other agent parameters
)
```
