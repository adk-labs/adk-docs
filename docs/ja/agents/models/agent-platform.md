# ADK エージェント向けの Agent Platform ホスティングモデル

Google Cloud の MLOps エコシステムとの統合や、エンタープライズグレードのスケーラビリティと信頼性を実現するために、Agent Platform エンドポイントにデプロイされたモデルを使用できます。
これには、Model Garden のモデルや独自にファインチューニングしたモデルが含まれます。

**統合方法:** Agent Platform エンドポイントの完全なリソース文字列（`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`）を `LlmAgent` の `model` パラメータに直接渡します。

## Agent Platform のセットアップ

環境が Agent Platform 用に構成されていることを確認します。

1. **認証:** アプリケーションのデフォルト認証情報（ADC）を使用します:

    ```shell
    gcloud auth application-default login
    ```

2. **環境変数:** プロジェクトとロケーションを設定します:

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
    ```

3. **Agent Platform バックエンドを有効にする:** `google-genai` ライブラリが Agent Platform をターゲットにするよう環境変数を設定します:

    ```shell
    export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
    ```

## Model Garden のデプロイ

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

[Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) のさまざまなオープンモデルやプロプライエタリモデルをエンドポイントにデプロイできます。

**例:**

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

## ファインチューニング済みモデルのエンドポイント

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

ファインチューニング済みモデル（Gemini ベースか、Agent Platform でサポートされている他のアーキテクチャかを問わず）をデプロイすると、直接使用可能なエンドポイントが作成されます。

**例:**

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

## Agent Platform 上の Anthropic Claude {#anthropic-claude}

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.2.0</span><span class="lst-typescript">TypeScript v2.4.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v1.4.0</span>
</div>

Anthropic などの一部のプロバイダーは、Agent Platform を通じてモデルを直接提供しています。拡張思考（extended thinking）やプロンプト キャッシングを含め、Agent Platform 上で Claude モデルをセットアップして使用する方法については、Claude モデルガイドの [Agent Platform 経由で接続する](/ja/agents/models/anthropic/#connect-through-agent-platform)を参照してください。

## Agent Platform 上のオープンモデル {#open-models}

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Agent Platform は、Model-as-a-Service (MaaS) を通じて、Meta Llama などの厳選されたオープンソース モデルを提供します。これらのモデルはマネージド API 経由でアクセスできるため、基盤となるインフラストラクチャを管理せずにデプロイおよび拡張できます。利用可能なオプションの完全なリストについては、[Agent Platform open models for MaaS](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/maas/use-open-models#open-models) のドキュメントを参照してください。

=== "Python"

    [LiteLLM](https://docs.litellm.ai/) ライブラリを使用して、Agent Platform MaaS 上の Meta Llama などのオープンモデルにアクセスできます。

    **統合方法:** `LiteLlm` ラッパークラスを使用し、`LlmAgent` の `model` パラメータとして設定します。ADK で LiteLLM を使用する方法については、[LiteLLM model connector for ADK agents](/agents/models/litellm/#litellm-model-connector-for-adk-agents) のドキュメントを参照してください。

    **セットアップ:**

    1. **Agent Platform 環境:** Agent Platform の共通セットアップ（ADC、環境変数、`GOOGLE_GENAI_USE_ENTERPRISE=TRUE`）が完了していることを確認します。

    2. **LiteLLM のインストール:**
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
