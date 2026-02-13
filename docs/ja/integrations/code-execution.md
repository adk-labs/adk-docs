---
catalog_title: コード実行
catalog_description: Gemini モデルを使ってコード実行とデバッグを行います
catalog_icon: /adk-docs/integrations/assets/gemini-spark.svg
catalog_tags: ["code", "google"]
---

# ADK 向け Gemini API コード実行ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span><span class="lst-java">Java v0.2.0</span>
</div>

`built_in_code_execution` ツールを使うと、エージェントがコードを実行できます。
特に Gemini 2 以降のモデル利用時に有効です。これによりモデルは
計算、データ操作、小規模スクリプト実行などのタスクを実行できます。

!!! warning "警告: 1 エージェント 1 ツール制限"

    このツールは、1 つのエージェントインスタンス内で ***単独でのみ*** 使用できます。
    この制限と回避策の詳細は
    [ADK ツールの制限事項](/adk-docs/tools/limitations/#one-tool-one-agent)を参照してください。

=== "Python"

    ```py
    --8<-- "examples/python/snippets/tools/built-in-tools/code_execution.py"
    ```

=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/tools/CodeExecutionAgentApp.java:full_code"
    ```
