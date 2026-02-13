---
catalog_title: 코드 실행
catalog_description: Gemini 모델을 사용해 코드를 실행하고 디버깅합니다
catalog_icon: /adk-docs/integrations/assets/gemini-spark.svg
catalog_tags: ["code", "google"]
---

# ADK용 Gemini API 코드 실행 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`built_in_code_execution` 도구를 사용하면 에이전트가 코드를 실행할 수 있습니다.
특히 Gemini 2 이상 모델을 사용할 때 동작합니다. 이를 통해 모델이
계산, 데이터 조작, 소규모 스크립트 실행 같은 작업을 수행할 수 있습니다.

!!! warning "경고: 에이전트당 단일 도구 제한"

    이 도구는 하나의 에이전트 인스턴스 내에서 ***단독으로만*** 사용할 수 있습니다.
    이 제한과 우회 방법에 대한 자세한 내용은
    [ADK 도구 제한 사항](/adk-docs/tools/limitations/#one-tool-one-agent)을 참조하세요.

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CodeExecutionAgentApp.java:full_code"
    ```
