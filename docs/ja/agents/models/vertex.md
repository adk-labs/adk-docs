# ADK エージェント向けの Vertex AI ホスティングモデル

エンタープライズ向けの拡張性、信頼性、および Google Cloud の MLOps エコシステムとの統合のために、
Vertex AI エンドポイントにデプロイされたモデルを使用できます。これには Model Garden のモデルや
独自のファインチューニングモデルが含まれます。

**統合方法:** 完全な Vertex AI エンドポイントリソース文字列
(`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`) を `LlmAgent` の
`model` パラメータへ直接渡します。

## Vertex AI 設定

Vertex AI が利用可能な環境にしていることを確認します。

1. **認証:** Application Default Credentials (ADC) を使用します。

    ```shell
    gcloud auth application-default login
    ```

2. **環境変数の設定:** プロジェクトとロケーションを設定します。

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
    ```

3. **Vertex バックエンドを有効化:** `google-genai` ライブラリが Vertex AI を
   対象とするようにします。

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

## Model Garden デプロイメント

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span>
</div>

[Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
からさまざまなオープンモデルおよびプロプライエタリモデルをエンドポイントへデプロイできます。

**例:**

```python
from google.adk.agents import LlmAgent
from google.genai import types # For config objects

# --- Example Agent using a Llama 3 model deployed from Model Garden ---

# 実際の Vertex AI エンドポイントリソース名に置き換えてください
llama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

agent_llama3_vertex = LlmAgent(
    model=llama3_endpoint,
    name="llama3_vertex_agent",
    instruction="You are a helpful assistant based on Llama 3, hosted on Vertex AI.",
    generate_content_config=types.GenerateContentConfig(max_output_tokens=2048),
    # ... other agent parameters
)
```

## ファインチューニングモデルエンドポイント

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span>
</div>

Gemini または Vertex AI がサポートする他のアーキテクチャのファインチューニングモデルを
デプロイすると、そのエンドポイントを直接使用できるようになります。

**例:**

```python
from google.adk.agents import LlmAgent

# --- Example Agent using a fine-tuned Gemini model endpoint ---

# 実際のファインチューニング済みモデルエンドポイントリソース名に置き換えてください
finetuned_gemini_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID"

agent_finetuned_gemini = LlmAgent(
    model=finetuned_gemini_endpoint,
    name="finetuned_gemini_agent",
    instruction="You are a specialized assistant trained on specific data.",
    # ... other agent parameters
)
```

## Vertex AI 上の Anthropic Claude {#third-party-models-on-vertex-ai-eg-anthropic-claude}

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Anthropic のような一部のプロバイダーは、モデルを Vertex AI 経由で直接提供します。

=== "Python"

    **統合方法:** 直接モデル文字列（例: `"claude-3-sonnet@20240229"`）を使用しますが、ADK での
    **手動登録**が必要です。

    **登録が必要な理由:** ADK のレジストリは、`gemini-*` 文字列と標準
    Vertex AI エンドポイント文字列（`projects/.../endpoints/...`）を自動的に認識して
    `google-genai` ライブラリへルーティングします。Claude のような他のモデルを
    Vertex AI 経由で直接使う場合は、ADK レジストリに当該モデルを扱える
    ラッパークラス（この例では `Claude`）を明示的に登録する必要があります。

    **セットアップ:**

    1. **Vertex AI 環境:** 統合された Vertex AI の設定（ADC、環境変数、
       `GOOGLE_GENAI_USE_VERTEXAI=TRUE`）が完了していることを確認します。

    2. **プロバイダーライブラリのインストール:** Vertex AI 用に設定された
       必要なクライアントライブラリをインストールします。

        ```shell
        pip install "anthropic[vertex]"
        ```

    3. **モデルクラスの登録:** エージェント作成前に、アプリケーション開始時点で
       次のコードを追加します。

        ```python
        # Required for using Claude model strings directly via Vertex AI with LlmAgent
        from google.adk.models.anthropic_llm import Claude
        from google.adk.models.registry import LLMRegistry

        LLMRegistry.register(Claude)
        ```

       **例:**

       ```python
       from google.adk.agents import LlmAgent
       from google.adk.models.anthropic_llm import Claude # Import needed for registration
       from google.adk.models.registry import LLMRegistry # Import needed for registration
       from google.genai import types

       # --- Register Claude class (do this once at startup) ---
       LLMRegistry.register(Claude)

       # --- Example Agent using Claude 3 Sonnet on Vertex AI ---

       # Standard model name for Claude 3 Sonnet on Vertex AI
       claude_model_vertexai = "claude-3-sonnet@20240229"

       agent_claude_vertexai = LlmAgent(
           model=claude_model_vertexai, # Pass the direct string after registration
           name="claude_vertexai_agent",
           instruction="You are an assistant powered by Claude 3 Sonnet on Vertex AI.",
           generate_content_config=types.GenerateContentConfig(max_output_tokens=4096),
           # ... other agent parameters
       )
       ```

=== "Java"

    **統合方法:** プロバイダー固有のモデルクラスを直接インスタンス化し（例: `com.google.adk.models.Claude`）、Vertex AI バックエンドを指定します。

    **直接インスタンス化が必要な理由:** Java ADK の `LlmRegistry` は主に Gemini モデルを扱うためです。Vertex AI の Claude のようなサードパーティモデルでは、ADK のラッパークラス（例: `Claude`）インスタンスを `LlmAgent` に直接渡します。 このラッパークラスは、特定クライアントライブラリ経由でモデルとやり取りし、そのライブラリは Vertex AI 用に設定されます。

    **セットアップ:**

    1.  **Vertex AI 環境:**
        *   Google Cloud プロジェクトとリージョンが正しく設定されていることを確認します。
        *   **Application Default Credentials (ADC):** 環境で ADC が正しく設定されていることを確認します。
            通常は `gcloud auth application-default login` 実行で設定します。
            Java クライアントライブラリは Vertex AI 認証のためこのクレデンシャルを使用します。
            詳細は [Google Cloud Java の ADC ドキュメント](https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault_) を参照してください。

    2.  **プロバイダライブラリ依存関係:**
        *   **サードパーティクライアントライブラリ（多くはトランジティブ）:** ADK コアライブラリには
            Vertex AI でよく使われるサードパーティモデル（Anthropic 必須クラスなど）の
            必要なクライアントライブラリが **トランジティブ依存関係**として含まれることが多く、
            その場合 `pom.xml` や `build.gradle` に Anthropic Vertex SDK を明示追加する必要がないことがあります。

    3.  **モデルのインスタンス化と構成:**
        `LlmAgent` 作成時に `Claude` クラス（または同等のプロバイダー用クラス）をインスタンス化し、
        `VertexBackend` を構成します。

    **例:**

    ```java
    import com.anthropic.client.AnthropicClient;
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.vertex.backends.VertexBackend;
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Claude; // ADK's wrapper for Claude
    import com.google.auth.oauth2.GoogleCredentials;
    import java.io.IOException;

    // ... other imports

    public class ClaudeVertexAiAgent {

        public static LlmAgent createAgent() throws IOException {
            // Model name for Claude 3 Sonnet on Vertex AI (or any other Claude model)
            String claudeModelVertexAi = "claude-3-7-sonnet"; // Or any other Claude model

            // Configure the AnthropicOkHttpClient with the VertexBackend
            AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
                .backend(
                    VertexBackend.builder()
                        .region("us-east5") // Specify your Vertex AI region
                        .project("your-gcp-project-id") // Specify your GCP Project ID
                        .googleCredentials(GoogleCredentials.getApplicationDefault())
                        .build())
                .build();

            // Instantiate LlmAgent with the ADK Claude wrapper
            LlmAgent agentClaudeVertexAi = LlmAgent.builder()
                .model(new Claude(claudeModelVertexAi, anthropicClient)) // Pass the Claude instance
                .name("claude_vertexai_agent")
                .instruction("You are an assistant powered by Claude 3 Sonnet on Vertex AI.")
                // .generateContentConfig(...) // Optional: Add generation config if needed
                // ... other agent parameters
                .build();

            return agentClaudeVertexAi;
        }

        public static void main(String[] args) {
            try {
                LlmAgent agent = createAgent();
                System.out.println("Successfully created agent: " + agent.name());
                // Here you would typically set up a Runner and Session to interact with the agent
            } catch (IOException e) {
                System.err.println("Failed to create agent: " + e.getMessage());
                e.printStackTrace();
            }
        }
    }
    ```

## Vertex AI のオープンモデル {#open-models}

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

Vertex AI は、Meta Llama などのオープンソースモデルを Model-as-a-Service（MaaS）
として厳選して提供します。これらのモデルは管理型 API 経由でアクセスできるため、
基盤インフラを管理せずにデプロイとスケールが可能です。利用可能なモデルの一覧は
[Vertex AI open models for MaaS](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/maas/use-open-models#open-models) を参照してください。

=== "Python"

    [LiteLLM](https://docs.litellm.ai/) ライブラリを使って、Vertex AI MaaS の Meta Llama などのオープンモデルを利用できます。

    **統合方法:** `LiteLlm` ラッパークラスを使用し、`LlmAgent` の `model` パラメータに設定します。
    ADK で LiteLLM を使用する方法は [ADK エージェント向け LiteLLM モデルコネクタ](/adk-docs/agents/models/litellm/#litellm-model-connector-for-adk-agents) を参照してください。

    **セットアップ:**

    1. **Vertex AI 環境:** 統合された Vertex AI の設定（ADC、環境変数、
       `GOOGLE_GENAI_USE_VERTEXAI=TRUE`）が完了していることを確認します。

    2. **LiteLLM インストール:**
            ```shell
            pip install litellm
            ```

    **例:**

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm

    # --- Example Agent using Meta's Llama 4 Scout ---
    agent_llama_vertexai = LlmAgent(
        model=LiteLlm(model="vertex_ai/meta/llama-4-scout-17b-16e-instruct-maas"), # LiteLLM model string format
        name="llama4_agent",
        instruction="You are a helpful assistant powered by Llama 4 Scout.",
        # ... other agent parameters
    )

    ```
