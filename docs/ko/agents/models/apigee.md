# ADK 에이전트를 위한 Apigee AI Gateway

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.18.0</span><span class="lst-java">Java v0.4.0</span>
</div>

[Apigee](https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee)는
강력한 [AI Gateway](https://cloud.google.com/solutions/apigee-ai)를 제공하여
생성형 AI 모델 트래픽을 관리하고 거버넌스 하는 방식 자체를 바꿉니다. AI 모델 엔드포인트(예: Vertex AI 또는 Gemini API)를
Apigee 프록시를 통해 노출하면 다음과 같은 엔터프라이즈급 기능을 즉시 사용할 수 있습니다.

- **모델 보안:** Model Armor와 같은 보안 정책으로 위협을 차단합니다.
- **트래픽 거버넌스:** Rate Limiting 및 Token Limiting을 적용해 비용을 관리하고 남용을 방지합니다.
- **성능:** 시맨틱 캐싱과 고급 모델 라우팅을 사용하여 응답 시간과 효율성을 개선합니다.
- **모니터링 및 가시성:** 모든 AI 요청에 대해 세부 모니터링, 분석, 감사 로그를 확보할 수 있습니다.

!!! note

    `ApigeeLLM` 래퍼는 현재 Vertex AI 및 Gemini API(generateContent)에서 사용하도록 설계되어 있습니다.
    다른 모델 및 인터페이스에 대한 지원은 계속 확장하고 있습니다.

## 구현 예시

`ApigeeLlm` 래퍼 객체를 생성해 에이전트 워크플로우에 통합하고,
이를 `LlmAgent` 또는 다른 에이전트 유형에 전달하세요.

=== "Python"

    ```python

    from google.adk.agents import LlmAgent
    from google.adk.models.apigee_llm import ApigeeLlm

    # Instantiate the ApigeeLlm wrapper
    model = ApigeeLlm(
        # Specify the Apigee route to your model. For more info, check out the ApigeeLlm documentation (https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm).
        model="apigee/gemini-2.5-flash",
        # The proxy URL of your deployed Apigee proxy including the base path
        proxy_url=f"https://{APIGEE_PROXY_URL}",
        # Pass necessary authentication/authorization headers (like an API key)
        custom_headers={"foo": "bar"}
    )

    # Pass the configured model wrapper to your LlmAgent
    agent = LlmAgent(
        model=model,
        name="my_governed_agent",
        instruction="You are a helpful assistant powered by Gemini and governed by Apigee.",
        # ... other agent parameters
    )

    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.ApigeeLlm;
    import com.google.common.collect.ImmutableMap;

    ApigeeLlm apigeeLlm =
            ApigeeLlm.builder()
                .modelName("apigee/gemini-2.5-flash") // Specify the Apigee route to your model. For more info, check out the ApigeeLlm documentation
                .proxyUrl(APIGEE_PROXY_URL) //The proxy URL of your deployed Apigee proxy including the base path
                .customHeaders(ImmutableMap.of("foo", "bar")) //Pass necessary authentication/authorization headers (like an API key)
                .build();
    LlmAgent agent =
        LlmAgent.builder()
            .model(apigeeLlm)
            .name("my_governed_agent")
            .description("my_governed_agent")
            .instruction("You are a helpful assistant powered by Gemini and governed by Apigee.")
            // tools will be added next
            .build();
    ```

이 설정을 사용하면 에이전트의 모든 API 호출이 먼저 Apigee로 라우팅되며,
보안, 속도 제한, 로깅 같은 필수 정책이 모두 실행된 뒤 요청이
기본 AI 모델 엔드포인트로 안전하게 전달됩니다.
전체 Apigee 프록시 사용 예제는
[Hello World Apigee LLM](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm)에서 확인할 수 있습니다.
