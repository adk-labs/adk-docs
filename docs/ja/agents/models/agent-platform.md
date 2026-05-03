# ADK エージェントのエージェント プラットフォームでホストされるモデル

エンタープライズ グレードの拡張性、信頼性、Google との統合を実現
クラウドの MLOps エコシステムでは、エージェント プラットフォーム エンドポイントにデプロイされたモデルを使用できます。
これには、Model Garden のモデルまたは独自に微調整したモデルが含まれます。

**統合方法:** 完全なエージェント プラットフォーム エンドポイント リソース文字列を渡します。
(`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`) に直接送信します。
`LlmAgent` の `model` パラメータ。

## エージェント プラットフォームのセットアップ

環境がエージェント プラットフォーム用に構成されていることを確認します。

1. **認証:** アプリケーションのデフォルト認証情報 (ADC) を使用します:

    ```shell
    gcloud auth application-default login
    ```

2. **環境変数:** プロジェクトと場所を設定します。

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
    ```

3. **エージェント プラットフォーム バックエンドを有効にする:** 重要なのは、`google-genai` ライブラリを確認することです。
   ターゲット エージェント プラットフォーム:

    ```shell
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    ```

## モデル ガーデン デプロイメント

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

さまざまなオープンな独自モデルをデプロイできます。
[Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
エンドポイントに。

**例：**

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.genai import types # For config objects

    # --- Example Agent using a Llama 3 model deployed from Model Garden ---

    # Replace with your actual Agent Platform Endpoint resource name
    llama3_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID"

    agent_llama3_vertex = LlmAgent(
        model=llama3_endpoint,
        name="llama3_vertex_agent",
        instruction="You are a helpful assistant based on Llama 3, hosted on Agent Platform.",
        generate_content_config=types.GenerateContentConfig(max_output_tokens=2048),
        # ... other agent parameters
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Gemini;
    import com.google.genai.types.GenerateContentConfig;

    // ...

    // Replace with your actual Agent Platform Endpoint resource name
    String llama3Endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_LLAMA3_ENDPOINT_ID";

    LlmAgent agentLlama3Vertex = LlmAgent.builder()
        .model(Gemini.builder()
            .modelName(llama3Endpoint)
            .build())
        .name("llama3_vertex_agent")
        .instruction("You are a helpful assistant based on Llama 3, hosted on Agent Platform.")
        .generateContentConfig(GenerateContentConfig.builder()
            .maxOutputTokens(2048)
            .build())
        // ... other agent parameters
        .build();
    ```

## 微調整されたモデルのエンドポイント

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

微調整されたモデルのデプロイ (Gemini または他のアーキテクチャに基づくかどうか)
エージェント プラットフォームでサポートされている) を使用すると、エンドポイントが直接使用できるようになります。

**例：**

=== "Python"

    ```python
    from google.adk.agents import LlmAgent

    # --- Example Agent using a fine-tuned Gemini model endpoint ---

    # Replace with your fine-tuned model's endpoint resource name
    finetuned_gemini_endpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID"

    agent_finetuned_gemini = LlmAgent(
        model=finetuned_gemini_endpoint,
        name="finetuned_gemini_agent",
        instruction="You are a specialized assistant trained on specific data.",
        # ... other agent parameters
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.Gemini;

    // ...

    // Replace with your fine-tuned model's endpoint resource name
    String finetunedGeminiEndpoint = "projects/YOUR_PROJECT_ID/locations/us-central1/endpoints/YOUR_FINETUNED_ENDPOINT_ID";

    LlmAgent agentFinetunedGemini = LlmAgent.builder()
        .model(Gemini.builder()
            .modelName(finetunedGeminiEndpoint)
            .build())
        .name("finetuned_gemini_agent")
        .instruction("You are a specialized assistant trained on specific data.")
        // ... other agent parameters
        .build();
    ```

## エージェント プラットフォーム上の Anthropic Claude {#anthropic-claude}

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Anthropic などの一部のプロバイダーは、自社のモデルを次のサイトから直接利用できるようにしています。
エージェントプラットフォーム。

**例：**

=== "Python"

    **統合方法:** 直接モデル文字列を使用します (例:
    `"claude-3-sonnet@20240229"`)、*ただし、ADK 内で手動登録が必要*です。

    **登録する理由** ADK のレジストリは、`gemini-*` 文字列を自動的に認識します。
    標準のエージェント プラットフォーム エンドポイント文字列 (`projects/.../endpoints/...`) と
    `google-genai` ライブラリを介してそれらをルーティングします。他のモデルタイプを直接使用する場合
    エージェント プラットフォーム (クロードなど) を介して、ADK レジストリに明示的に指示する必要があります。
    特定のラッパー クラス (この場合は `Claude`) はそのモデルの処理方法を知っています
    エージェント プラットフォーム バックエンドの識別子文字列。

    **セットアップ:**

    1. **エージェント プラットフォーム環境:** 統合されたエージェント プラットフォームのセットアップ (ADC、環境) を確認します。
       Vars、`GOOGLE_GENAI_USE_VERTEXAI=TRUE`) が完了しました。

    2. **プロバイダー ライブラリのインストール:** 構成された必要なクライアント ライブラリをインストールします。
       エージェントプラットフォーム用。

        ```shell
        pip install "anthropic[vertex]"
        ```

    3. **モデル クラスの登録:** このコードをアプリケーションの先頭近くに追加します。
       Claude モデル文字列を使用してエージェントを作成する *前*:

        ```python
        # Required for using Claude model strings directly via Agent Platform with LlmAgent
        from google.adk.models.anthropic_llm import Claude
        from google.adk.models.registry import LLMRegistry

        LLMRegistry.register(Claude)
        ```

       ```python
       from google.adk.agents import LlmAgent
       from google.adk.models.anthropic_llm import Claude # Import needed for registration
       from google.adk.models.registry import LLMRegistry # Import needed for registration
       from google.genai import types

       # --- Register Claude class (do this once at startup) ---
       LLMRegistry.register(Claude)

       # --- Example Agent using Claude 3 Sonnet on Agent Platform ---

       # Standard model name for Claude 3 Sonnet on Agent Platform
       claude_model_vertexai = "claude-3-sonnet@20240229"

       agent_claude_vertexai = LlmAgent(
           model=claude_model_vertexai, # Pass the direct string after registration
           name="claude_vertexai_agent",
           instruction="You are an assistant powered by Claude 3 Sonnet on Agent Platform.",
           generate_content_config=types.GenerateContentConfig(max_output_tokens=4096),
           # ... other agent parameters
       )
       ```

=== "Java"

    **統合方法:** プロバイダー固有のモデル クラス (`com.google.adk.models.Claude` など) を直接インスタンス化し、エージェント プラットフォーム バックエンドで構成します。

    **直接インスタンス化を行う理由** Java ADK の `LlmRegistry` は、デフォルトで主に Gemini モデルを処理します。 Agent Platform 上の Claude などのサードパーティ モデルの場合、ADK のラッパー クラス (`Claude` など) のインスタンスを `LlmAgent` に直接提供します。このラッパー クラスは、エージェント プラットフォーム用に構成された特定のクライアント ライブラリを介してモデルと対話する役割を果たします。

    **セットアップ:**

    1. **エージェント プラットフォーム環境:**
        * Google Cloud プロジェクトとリージョンが正しく設定されていることを確認してください。
        * **アプリケーションのデフォルト認証情報 (ADC):** ADC が環境で正しく構成されていることを確認してください。これは通常、`gcloud auth application-default login` を実行することによって行われます。 Java クライアント ライブラリは、これらの資格情報を使用してエージェント プラットフォームで認証します。詳細な設定については、[Google Cloud Java documentation on ADC](https://cloud.google.com/java/docs/reference/google-auth-library/latest/com.google.auth.oauth2.GoogleCredentials#com_google_auth_oauth2_GoogleCredentials_getApplicationDefault__) に従ってください。

    2. **プロバイダー ライブラリの依存関係:**
        * **サードパーティ クライアント ライブラリ (多くの場合推移的):** ADK コア ライブラリには、多くの場合、エージェント プラットフォーム上の一般的なサードパーティ モデルに必要なクライアント ライブラリ (Anthropic の必須クラスなど) が **推移的な依存関係**として含まれています。これは、`pom.xml` または `build.gradle` に Anthropic Vertex SDK の別の依存関係を明示的に追加する必要がない可能性があることを意味します。

    3. **モデルのインスタンス化と構成:**
        `LlmAgent` を作成するときは、`Claude` クラス (または別のプロバイダーの同等のもの) をインスタンス化し、その `VertexBackend` を構成します。

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
            // Model name for Claude 3 Sonnet on Agent Platform (or other versions)
            String claudeModelVertexAi = "claude-3-7-sonnet"; // Or any other Claude model

            // Configure the AnthropicOkHttpClient with the VertexBackend
            AnthropicClient anthropicClient = AnthropicOkHttpClient.builder()
                .backend(
                    VertexBackend.builder()
                        .region("us-east5") // Specify your Agent Platform region
                        .project("your-gcp-project-id") // Specify your GCP Project ID
                        .googleCredentials(GoogleCredentials.getApplicationDefault())
                        .build())
                .build();

            // Instantiate LlmAgent with the ADK Claude wrapper
            LlmAgent agentClaudeVertexAi = LlmAgent.builder()
                .model(new Claude(claudeModelVertexAi, anthropicClient)) // Pass the Claude instance
                .name("claude_vertexai_agent")
                .instruction("You are an assistant powered by Claude 3 Sonnet on Agent Platform.")
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

## エージェント プラットフォーム上のオープン モデル {#open-models}

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Agent Platform は、Model-as-a-Service (MaaS) を通じて、Meta Llama などの厳選されたオープンソース モデルを提供します。これらのモデルはマネージド API 経由でアクセスできるため、基盤となるインフラストラクチャを管理せずにデプロイおよび拡張できます。利用可能なオプションの完全なリストについては、[Agent Platform open models for MaaS](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/maas/use-open-models#open-models) のドキュメントを参照してください。

=== "Python"

    [LiteLLM](https://docs.litellm.ai/) ライブラリを使用して、エージェント プラットフォーム MaaS 上の Meta の Llama などのオープン モデルにアクセスできます。

    **統合方法:** `LiteLlm` ラッパー クラスを使用して設定します
    `LlmAgent` の `model` パラメータとして。 ADK で LiteLLM を使用する方法については、[LiteLLM model connector for ADK agents](/agents/models/litellm/#litellm-model-connector-for-adk-agents) ドキュメントを必ず読んでください。

    **セットアップ:**

    1. **エージェント プラットフォーム環境:** 統合されたエージェント プラットフォームのセットアップ (ADC、環境) を確認します。
       Vars、`GOOGLE_GENAI_USE_VERTEXAI=TRUE`) が完了しました。

    2. **LiteLLM をインストールします:**
            ```shell
            pip install litellm
            ```

    **例：**

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
