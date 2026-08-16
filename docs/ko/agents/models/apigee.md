# ADK 에이전트용 Apigee AI Gateway

<div class="language-support-tag">
   <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.18.0</span><span class="lst-java">Java v0.4.0</span>
</div>

[Apigee](https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee)는 강력한 [AI Gateway](https://cloud.google.com/solutions/apigee-ai)를 제공하여 생성형 AI 모델 트래픽을 관리하고 제어하는 방식을 혁신합니다. Apigee 프록시를 통해 AI 모델 엔드포인트(예: Agent Platform 또는 Gemini API)를 노출하면 다음과 같은 엔터프라이즈급 기능을 즉시 활용할 수 있습니다:

- **모델 보안 (Model Safety):** 위협 보호를 위해 Model Armor와 같은 보안 정책을 구현합니다.
- **트래픽 제어 (Traffic Governance):** 비용을 관리하고 남용을 방지하기 위해 Rate Limiting(요청 제한) 및 Token Limiting(토큰 제한)을 적용합니다.
- **성능 향상 (Performance):** 시맨틱 캐싱(Semantic Caching) 및 고급 모델 라우팅을 사용하여 응답 시간과 효율성을 향상합니다.
- **모니터링 및 가시성 (Monitoring & Visibility):** 모든 AI 요청에 대한 세분화된 모니터링, 분석 및 감사를 제공합니다.

   `ApigeeLlm` 래퍼는 Agent Platform 및 Gemini API(generateContent)와 함께 사용하도록 설계되었습니다. 다른 모델 및 인터페이스에 대한 지원도 지속적으로 확장하고 있습니다. 자체 호스팅 또는 타사 제공업체를 포함한 OpenAI 호환 모델의 경우 `CompletionsHTTPClient`를 사용하여 Apigee 프록시를 통해 트래픽을 라우팅하세요.

## 구현 예시

`ApigeeLlm` 래퍼 객체를 인스턴스화하고 이를 `LlmAgent` 또는 다른 에이전트 유형에 전달하여 Apigee의 거버넌스를 에이전트 워크플로우에 통합합니다.

=== "Python"

    ```python
    from google.adk.agents import LlmAgent
    from google.adk.models.apigee_llm import ApigeeLlm

    # ApigeeLlm 래퍼 인스턴스화
    model = ApigeeLlm(
        # 모델의 Apigee 경로 지정. 자세한 정보는 ApigeeLlm 문서를 참조하세요 (https://github.com/google/adk-python/tree/main/contributing/samples/models/hello_world_apigeellm).
        model="apigee/gemini-flash-latest",
        # 기본 경로를 포함한 배포된 Apigee 프록시의 프록시 URL
        proxy_url=f"https://{APIGEE_PROXY_URL}",
        # 필요한 인증/인가 헤더 전달 (예: API 키)
        custom_headers={"foo": "bar"}
    )

    # 구성된 모델 래퍼를 LlmAgent에 전달
    agent = LlmAgent(
        model=model,
        name="my_governed_agent",
        instruction="You are a helpful assistant powered by Gemini and governed by Apigee.",
        # ... 기타 에이전트 매개변수
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.models.ApigeeLlm;
    import com.google.common.collect.ImmutableMap;

    ApigeeLlm apigeeLlm =
            ApigeeLlm.builder()
                .modelName("apigee/gemini-flash-latest") // 모델의 Apigee 경로 지정
                .proxyUrl(APIGEE_PROXY_URL) // 기본 경로를 포함한 배포된 Apigee 프록시 URL
                .customHeaders(ImmutableMap.of("foo", "bar")) // 필요한 인증/인가 헤더 전달 (예: API 키)
                .build();
    LlmAgent agent =
        LlmAgent.builder()
            .model(apigeeLlm)
            .name("my_governed_agent")
            .description("my_governed_agent")
            .instruction("You are a helpful assistant powered by Gemini and governed by Apigee.")
            // 도구가 다음에 추가됨
            .build();
    ```

이 구성을 사용하면 에이전트의 모든 API 호출이 먼저 Apigee를 통해 라우팅되며, 요청이 기본 AI 모델 엔드포인트로 안전하게 전달되기 전에 필요한 모든 정책(보안, 요청 제한, 로깅)이 실행됩니다. 전체 Apigee 프록시 사용 예제는 [Hello World Apigee LLM](https://github.com/google/adk-python/tree/main/contributing/samples/models/hello_world_apigeellm)에서 확인할 수 있습니다.

## OpenAI 호환성

`CompletionsHTTPClient`는 OpenAI API 형식과의 호환성을 위해 설계된 일반 HTTP 클라이언트입니다. 네이티브 Gemini 또는 Vertex AI 프로토콜 대신 표준 OpenAI 호환 `/chat/completions` 엔드포인트를 기대하는 프록시(예: Apigee)를 통해 요청을 라우팅할 수 있습니다. 이 클라이언트는 다음을 처리합니다:

- **페이로드 구성**: `LlmRequest` 객체를 OpenAI 호환 API에 필요한 형식으로 변환합니다.
- **응답 처리**: 프록시의 스트리밍 및 비스트리밍 응답을 관리합니다.
- **안정성**: `tenacity`를 사용하여 비스트리밍 요청을 재시도하지만, 생성자에 `retry_options=types.HttpRetryOptions(...)`를 전달한 경우에만 적용됩니다. 기본적으로 각 요청은 한 번만 시도되며 스트리밍 요청은 재시도되지 않습니다.
- **정규화**: 응답 및 스트리밍 청크를 ADK 프레임워크의 나머지 부분에서 기대하는 표준 형식으로 파싱합니다.

### 구현 예시

```python
import asyncio
from google.adk.models.apigee_llm import CompletionsHTTPClient
from google.adk.models.llm_request import LlmRequest
from google.genai import types

async def test_client():
    # 1. 클라이언트 초기화
    client = CompletionsHTTPClient(
        base_url="https://your-apigee-proxy-url.com/v1",
        headers={"Authorization": "Bearer YOUR_API_KEY"}
    )

    # 2. 최소 요청 구성
    request = LlmRequest(
        model="gpt-4o",  # 대상 모델 ID로 대체
        contents=[types.Content(role="user", parts=[types.Part.from_text(text="Hello!")])]
    )

    # 3. 비스트리밍 생성 실행
    async for response in client.generate_content_async(request, stream=False):
        if response.content and response.content.parts:
            print(f"Response: {response.content.parts[0].text}")

if __name__ == "__main__":
    asyncio.run(test_client())
```
