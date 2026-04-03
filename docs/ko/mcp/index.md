# 모델 컨텍스트 프로토콜(MCP)

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

[모델 컨텍스트 프로토콜(MCP)](https://modelcontextprotocol.io/introduction)은 Gemini나 Claude 같은 대규모 언어 모델(LLM)이 외부 애플리케이션, 데이터 소스, 도구와 통신하는 방식을 표준화하기 위해 설계된 개방형 표준입니다. LLM이 컨텍스트를 얻고, 작업을 실행하며, 다양한 시스템과 상호작용하는 방식을 단순화하는 보편적인 연결 메커니즘이라고 생각하면 됩니다.

!!! tip "ADK용 MCP 도구"
    ADK에서 사용할 수 있는 사전 구축 MCP 도구 목록은
    [도구 및 통합](/ko/integrations/?topic=mcp)을 참조하세요.

## MCP는 어떻게 작동하나요?

MCP는 클라이언트-서버 아키텍처를 따르며, 데이터(리소스), 대화형 템플릿(프롬프트), 실행 가능한 함수(도구)가 MCP 서버에 의해 노출되고 MCP 클라이언트(LLM 호스트 애플리케이션 또는 AI 에이전트)에 의해 사용되는 방식을 정의합니다.

## ADK의 MCP 도구

ADK는 에이전트에서 MCP 도구를 사용하고 소비하는 데 도움을 줍니다. MCP 서비스를 호출하는 도구를 만들거나, 다른 개발자나 에이전트가 여러분의 도구와 상호작용할 수 있도록 MCP 서버를 노출하려는 경우 모두 지원합니다.

ADK에서 바로 사용할 수 있는 사전 구축 MCP 도구는 [도구 및 통합](/ko/integrations/)을 참조하세요. 또한 코드 샘플과 설계 패턴은 [MCP 도구 문서](/ko/tools-custom/mcp-tools/)를 참고하면, ADK를 MCP 서버와 함께 사용하는 방법을 확인할 수 있습니다. 여기에는 다음이 포함됩니다.

- **기존 MCP 서버를 ADK 안에서 사용하기**: ADK 에이전트가 MCP 클라이언트 역할을 하며 외부 MCP 서버가 제공하는 도구를 사용할 수 있습니다.
- **MCP 서버를 통해 ADK 도구 노출하기**: ADK 도구를 감싸는 MCP 서버를 구축하여 MCP 클라이언트가 사용할 수 있게 합니다.

## ADK 에이전트와 FastMCP 서버

ADK는 [FastMCP](https://github.com/jlowin/fastmcp)를 사용해 복잡한 MCP 프로토콜 세부 사항과 서버 관리를 처리하므로, 훌륭한 도구를 만드는 데 집중할 수 있습니다. FastMCP는 높은 수준의 Pythonic 추상화를 목표로 설계되었으며, 대부분의 경우 함수에 데코레이터를 붙이는 것만으로 충분합니다.

Cloud Run에서 실행되는 FastMCP 서버와 ADK를 함께 사용하는 방법은 [MCP 도구](/ko/tools-custom/mcp-tools/) 문서를 참조하세요.

## Google Cloud Genmedia용 MCP 서버

[Genmedia 서비스용 MCP 도구](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia)는 Imagen, Veo, Chirp 3 HD voices, Lyria 같은 Google Cloud 생성형 미디어 서비스를 AI 애플리케이션에 통합할 수 있게 해 주는 오픈소스 MCP 서버 세트입니다.

ADK와 [Genkit](https://genkit.dev/)은 이러한 MCP 도구를 기본적으로 지원하므로, AI 에이전트가 생성형 미디어 워크플로를 효과적으로 오케스트레이션할 수 있습니다. 구현 가이드는 [ADK 예제 에이전트](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/adk)와 [Genkit 예제](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/genkit)를 참조하세요.
