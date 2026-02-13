---
catalog_title: Google Search
catalog_description: Gemini と Google Search を使って Web 検索を実行します
catalog_icon: /adk-docs/integrations/assets/google-search.png
catalog_tags: ["search","google"]
---

# ADK 向け Gemini API Google Search ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`google_search` ツールを使うと、エージェントは Google Search を利用して Web 検索を実行できます。`google_search` ツールは Gemini 2 モデルとのみ互換です。ツールの詳細は [Google Search グラウンディングの理解](/adk-docs/grounding/google_search_grounding/) を参照してください。

!!! warning "`google_search` ツール使用時の追加要件"
    Google Search によるグラウンディングを使用して、応答に Search 提案が含まれる場合、プロダクション環境およびアプリケーションで Search 提案を表示する必要があります。
    Google Search グラウンディングの詳細は、[Google AI Studio](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions) または [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/grounding-search-suggestions) のドキュメントを参照してください。UI コード (HTML) は Gemini 応答の `renderedContent` として返されるため、ポリシーに従ってアプリ内で HTML を表示する必要があります。

!!! warning "警告: 1 エージェント 1 ツール制限"

    このツールは、1 つのエージェントインスタンス内で ***単独でのみ*** 使用できます。
    この制限と回避策の詳細は
    [ADK ツールの制限事項](/adk-docs/tools/limitations/#one-tool-one-agent)を参照してください。

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
