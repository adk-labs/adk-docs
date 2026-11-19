# ADK 에이전트를 위한 Agent Platform 호스팅 모델

엔터프라이즈급 확장성, 안정성 및 Google Cloud의 MLOps 생태계와의 통합을 위해 Agent Platform 엔드포인트에 배포된 모델을 사용할 수 있습니다. 여기에는 Model Garden의 모델이나 직접 파인튜닝(미세 조정)한 모델이 포함됩니다.

**통합 방법:** 전체 Agent Platform 엔드포인트 리소스 문자열(`projects/PROJECT_ID/locations/LOCATION/endpoints/ENDPOINT_ID`)을 `LlmAgent`의 `model` 매개변수에 직접 전달합니다.

## Agent Platform 설정

Agent Platform에 맞게 환경이 구성되어 있는지 확인하세요.

1. **인증:** ADC(애플리케이션 기본 사용자 인증 정보)를 사용합니다.

    ```shell
    gcloud auth application-default login
    ```

2. **환경 변수:** 프로젝트와 리전을 설정합니다.

    ```shell
    export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    export GOOGLE_CLOUD_LOCATION="YOUR_VERTEX_AI_LOCATION" # e.g., us-central1
    ```

3. **Agent Platform 백엔드 활성화:** `google-genai` 라이브러리가 Agent Platform을 대상으로 동작하도록 다음 환경 변수를 설정합니다.

    ```shell
    export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
    ```

## Model Garden 배포

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

[Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)에서 다양한 오픈 모델과 독점 모델을 엔드포인트에 배포할 수 있습니다.

**예시:**

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

## 파인튜닝된 모델 엔드포인트

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.2.0</span><span class="lst-java">Java v0.1.0</span>
</div>

파인튜닝(미세 조정)된 모델(Gemini 또는 Agent Platform에서 지원하는 기타 아키텍처 기반)을 배포하면 바로 사용할 수 있는 엔드포인트가 생성됩니다.

**예시:**

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

## Agent Platform의 Anthropic Claude {#anthropic-claude}

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.2.0</span><span class="lst-typescript">TypeScript v2.4.0</span><span class="lst-go">Go v2.7.0</span><span class="lst-java">Java v0.1.0</span><span class="lst-kotlin">Kotlin v1.4.0</span>
</div>

Anthropic과 같은 일부 제공업체는 Agent Platform을 통해 모델을 직접 제공합니다. 확장 추론(extended thinking) 및 프롬프트 캐싱을 포함하여 Agent Platform에서 Claude 모델을 설정하고 사용하려면 Claude 모델 가이드의 [Agent Platform을 통해 연결](/ko/agents/models/anthropic/#connect-through-agent-platform)을 참고하세요.

## Agent Platform의 오픈 모델 {#open-models}

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

Agent Platform은 MaaS(Model-as-a-Service)를 통해 Meta Llama와 같은 엄선된 오픈 소스 모델을 제공합니다. 이러한 모델은 관리형 API를 통해 액세스할 수 있으므로 기본 인프라를 관리하지 않고도 배포하고 확장할 수 있습니다. 사용 가능한 옵션의 전체 목록은 [Agent Platform open models for MaaS](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/maas/use-open-models#open-models) 설명서를 참고하세요.

=== "Python"

    [LiteLLM](https://docs.litellm.ai/) 라이브러리를 사용하여 Agent Platform MaaS에서 Meta의 Llama와 같은 오픈 모델에 액세스할 수 있습니다.

    **통합 방법:** `LiteLlm` 래퍼 클래스를 인스턴스화하여 `LlmAgent`의 `model` 매개변수로 설정합니다. ADK에서 LiteLLM을 사용하는 방법은 [LiteLLM model connector for ADK agents](/agents/models/litellm/#litellm-model-connector-for-adk-agents) 문서를 참고하세요.

    **설정:**

    1. **Agent Platform 환경:** 통합 Agent Platform 설정(ADC, 환경 변수, `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`)이 완료되었는지 확인합니다.

    2. **LiteLLM 설치:**
            ```shell
            pip install litellm
            ```

    **예시:**

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
