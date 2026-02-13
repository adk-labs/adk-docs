# AI 모델 for ADK 에이전트

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">Typescript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

Agent Development Kit (ADK)는 유연한 설계를 갖추고 있어, 다양한 대규모 언어 모델(LLM)을
에이전트에 통합할 수 있습니다. 이 섹션에서는 Gemini를 중심으로 하여,
외부에서 호스팅되거나 로컬에서 실행되는 인기 모델들을 효과적으로 통합하는 방법을 설명합니다.

ADK는 모델 통합을 위해 주로 두 가지 메커니즘을 사용합니다.

1. **직접 문자열/레지스트리:** Google Cloud 및 Vertex AI에서 직접 접근하는 Gemini 모델,
   또는 Vertex AI 엔드포인트에 호스팅된 모델처럼 Google 생태계와 밀접하게 통합된 모델의 경우,
   모델 이름 또는 엔드포인트 리소스 문자열을 전달하면 ADK 내부 레지스트리가
   이를 적절한 백엔드 클라이언트로 변환합니다.

      *  [Gemini 모델](/adk-docs/agents/models/google-gemini/)
      *  [Claude 모델](/adk-docs/agents/models/anthropic/)
      *  [Vertex AI 호스팅 모델](/adk-docs/agents/models/vertex/)

2. **모델 커넥터:** Google 생태계 외부 모델이나 특정 클라이언트 설정이 필요한 모델의 경우,
   `ApigeeLlm` 또는 `LiteLlm` 같은 특정 래퍼 클래스를 인스턴스화해
   이를 `LlmAgent`의 `model` 매개변수로 전달합니다.

      *  [Apigee 모델](/adk-docs/agents/models/apigee/)
      *  [LiteLLM 모델](/adk-docs/agents/models/litellm/)
      *  [Ollama 모델 호스팅](/adk-docs/agents/models/ollama/)
      *  [vLLM 모델 호스팅](/adk-docs/agents/models/vllm/)
