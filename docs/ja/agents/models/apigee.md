# ADK エージェントのための Apigee AI Gateway

<div class="language-support-tag">
   <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.18.0</span><span class="lst-java">Java v0.4.0</span>
</div>

[Apigee](https://docs.cloud.google.com/apigee/docs/api-platform/get-started/what-apigee) は
強力な [AI Gateway](https://cloud.google.com/solutions/apigee-ai) を提供し、
生成 AI モデルのトラフィック管理とガバナンスの方法を根本的に変えます。
Vertex AI や Gemini API などの AI モデルエンドポイントを Apigee プロキシ経由で公開すると、
すぐに次のエンタープライズグレード機能を利用できます。

- **モデルセキュリティ:** Model Armor のようなセキュリティポリシーで脅威を保護できます。
- **トラフィックガバナンス:** Rate Limiting と Token Limiting を適用して、コスト管理と不正利用防止を行えます。
- **パフォーマンス:** セマンティックキャッシュと高度なモデルルーティングで応答時間と効率を向上できます。
- **監視と可視化:** すべての AI リクエストに対して詳細な監視、分析、監査を取得できます。

!!! note

    `ApigeeLLM` ラッパーは現在、Vertex AI と Gemini API (generateContent) での使用を前提として設計されています。
    他のモデルやインターフェースのサポートは引き続き拡張しています。

## 実装例

`ApigeeLlm` ラッパーオブジェクトをインスタンス化し、`LlmAgent` やその他の
エージェントタイプに渡すことで、Apigee ガバナンスをワークフローへ統合します。

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

この設定を使うと、エージェントからの API 呼び出しはすべてまず Apigee を経由し、
必要なポリシー（セキュリティ、レート制御、ロギング）が実行された後に、
安全に基盤の AI モデルエンドポイントへ転送されます。
Apigee プロキシを使った完全なコード例は
[Hello World Apigee LLM](https://github.com/google/adk-python/tree/main/contributing/samples/hello_world_apigeellm) を参照してください。
