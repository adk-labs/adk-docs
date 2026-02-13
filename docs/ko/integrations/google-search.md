---
catalog_title: Google Search
catalog_description: Gemini와 함께 Google Search를 사용해 웹 검색을 수행합니다
catalog_icon: /adk-docs/integrations/assets/google-search.png
catalog_tags: ["search","google"]
---

# ADK용 Gemini API Google Search 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`google_search` 도구를 사용하면 에이전트가 Google Search를 이용해 웹 검색을 수행할 수 있습니다. `google_search` 도구는 Gemini 2 모델과만 호환됩니다. 도구에 대한 자세한 내용은 [Google Search grounding 이해하기](/adk-docs/grounding/google_search_grounding/)를 참조하세요.

!!! warning "`google_search` 도구 사용 시 추가 요구 사항"
    Google Search로 그라운딩을 사용하고 응답에서 Search 제안을 받는 경우, 프로덕션 및 애플리케이션에서 해당 Search 제안을 반드시 표시해야 합니다.
    Google Search 그라운딩에 대한 자세한 내용은 [Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions) 또는 [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions) 문서를 참조하세요. UI 코드(HTML)는 Gemini 응답의 `renderedContent`로 반환되며, 정책에 따라 앱에서 해당 HTML을 표시해야 합니다.

!!! warning "경고: 에이전트당 단일 도구 제한"

    이 도구는 하나의 에이전트 인스턴스 내에서 ***단독으로만*** 사용할 수 있습니다.
    이 제한과 우회 방법에 대한 자세한 내용은
    [ADK 도구 제한 사항](/adk-docs/tools/limitations/#one-tool-one-agent)을 참조하세요.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/google_search.py"
    ```

=== "TypeScript"

    ```typescript
    import {GOOGLE_SEARCH, LlmAgent} from '@google/adk';

    export const rootAgent = new LlmAgent({
      model: 'gemini-2.5-flash',
      name: 'root_agent',
      description:
          'an agent whose job it is to perform Google search queries and answer questions about the results.',
      instruction:
          'You are an agent whose job is to perform Google search queries and answer questions about the results.',
      tools: [GOOGLE_SEARCH],
    });
    ```

=== "Go"

    ```go
    --8<-- "examples/go/snippets/tools/built-in-tools/google_search.go"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/GoogleSearchAgentApp.java:full_code"
    ```
