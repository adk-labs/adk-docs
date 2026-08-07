---
catalog_title: Enterprise Web Search
catalog_description: 기업 정책을 준수하는 웹 검색 결과로 ADK 에이전트에 근거(grounding) 데이터 제공
catalog_icon: /integrations/assets/enterprise-web-search.png
catalog_tags: ["google", "search"]
---

# ADK용 Enterprise Web Search 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.9.0</span><span class="lst-typescript">TypeScript v1.5.0</span>
</div>

Google Cloud [Enterprise Web Search](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest/Shared.Types/EnterpriseWebSearch)는 웹의 정보를 바탕으로 ADK 에이전트에 근거(grounding) 데이터를 제공하면서도 기업 컴플라이언스 및 소스 제어를 유지합니다. 엔터프라이즈급 워크로드를 위해 설계된 이 도구는 근거 데이터가 조직의 보안 및 컴플라이언스 정책에 부합하도록 보장합니다.

!!! note "Enterprise Web Search vs. Agent Search"

    Enterprise Web Search는 [Agent Search](https://adk.dev/ko/integrations/agent-search/)와 다릅니다. Agent Search가 색인된 비공개 데이터 저장소를 쿼리하는 반면, Enterprise Web Search는 규정을 준수하는 공개 웹 데이터를 검색합니다.

!!! warning "서비스 전용 약관"

    Enterprise Web Search 도구를 사용할 때 UI에 검색 추천 및 필수 Google 로고를 올바르게 표시하는 것을 포함하여 Google의 서비스 전용 약관을 준수할 의무가 있습니다.

## 사용 사례 (Use cases)

- **엔터프라이즈 그래운딩(Enterprise Grounding)**: 조직의 컴플라이언스 표준을 유지하면서 최신 웹 정보를 에이전트에 제공합니다.
- **제어된 웹 액세스(Controlled Web Access)**: 조사, 시장 인텔리전스 또는 고객 지원 작업을 위해 에이전트가 신뢰할 수 있는 웹 소스를 쿼리하도록 보장합니다.
- **규제 대상 워크플로(Regulated Workflows)**: 엄격한 감사 가능성 및 데이터 거버넌스가 필요한 환경에 그래운딩 기능을 배포합니다.

## 사전 요구 사항 (Prerequisites)

- Agent Search가 활성화된 Google Cloud Platform에 대한 액세스 권한.
- Gemini 모델에 필요한 권한이 구성된 GCP 프로젝트.
- 환경 변수 `GOOGLE_GENAI_USE_ENTERPRISE=TRUE`가 설정되어 있어야 합니다.
- `google-adk` 패키지(Python) 또는 `@google/adk` 패키지(TypeScript) 설치:

=== "Python"

    ```bash
    pip install google-adk
    ```

=== "TypeScript"

    ```bash
    npm install @google/adk
    ```

## 에이전트와 함께 사용

다음 예제는 사전 인스턴스화된 `enterprise_web_search` 도구로 ADK 에이전트를 구성하는 방법을 보여줍니다.

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools import enterprise_web_search

    root_agent = Agent(
        model="gemini-flash-latest",
        name="enterprise_search_agent",
        instruction="Answer user questions accurately using enterprise-compliant web search results.",
        tools=[enterprise_web_search],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, ENTERPRISE_WEB_SEARCH } from "@google/adk";

    const rootAgent = new LlmAgent({
      model: "gemini-flash-latest",
      name: "enterprise_search_agent",
      instruction: "Answer user questions accurately using enterprise-compliant web search results.",
      tools: [ENTERPRISE_WEB_SEARCH],
    });

    export { rootAgent };
    ```

## 선택 가이드라인 (Selection guidance)

- 모든 Gemini 모델에서 광범위한 웹 커버리지가 필요한 일반 목적의 애플리케이션에는 표준 Google Search를 사용하세요.
- 컴플라이언스 제어, 소스 감사, Gemini 2+ 모델 배포가 필수적인 엔터프라이즈 에이전트를 구축할 때는 Enterprise Web Search를 사용하세요.

## 추가 리소스

- [Agent Search Web Grounding Overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/grounding/web-grounding-enterprise)
