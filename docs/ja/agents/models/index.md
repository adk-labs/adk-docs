# ADK エージェント向けの AI モデル

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">Typescript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

Agent Development Kit (ADK) は柔軟な設計により、様々な大規模言語モデル（LLM）を
エージェントに統合できます。このセクションでは、Gemini を中心に、外部でホストされるモデルや
ローカル実行される一般的なモデルの統合方法を説明します。

ADK はモデル統合のために主に2種類の仕組みを使用します。

1. **直接文字列/レジストリ:** Google Cloud や Vertex AI 経由で Gemini モデルを
   使用する場合、または Vertex AI エンドポイントでホストされるモデルのように
   Google エコシステムと密接に統合されたモデルの場合、モデル名またはエンドポイント
   リソース文字列を渡すことで、ADK の内部レジストリが適切なバックエンドクライアントへ変換します。

      *  [Gemini モデル](/adk-docs/agents/models/google-gemini/)
      *  [Claude モデル](/adk-docs/agents/models/anthropic/)
      *  [Vertex AI ホスティングモデル](/adk-docs/agents/models/vertex/)

2. **モデルコネクター:** Google エコシステム外のモデルや、特定のクライアント設定を要するモデルに対しては、
   `ApigeeLlm` や `LiteLlm` のようなラッパークラスをインスタンス化し、`LlmAgent` の
   `model` パラメータに渡します。

      *  [Apigee モデル](/adk-docs/agents/models/apigee/)
      *  [LiteLLM モデル](/adk-docs/agents/models/litellm/)
      *  [Ollama モデルホスティング](/adk-docs/agents/models/ollama/)
      *  [vLLM モデルホスティング](/adk-docs/agents/models/vllm/)
