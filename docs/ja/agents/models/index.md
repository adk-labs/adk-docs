# ADK エージェント向けの AI モデル

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">Typescript</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

Agent Development Kit (ADK) は柔軟な設計により、様々な大規模言語モデル（LLM）を
エージェントに統合できます。このセクションでは、Gemini を中心に、外部でホストされるモデルや
ローカル実行される一般的なモデルの統合方法を説明します。

ADK はモデル統合のために複数の仕組みを提供します。

1. **直接文字列/レジストリ:** Google AI Studio または Agent Platform 経由で
   アクセスする Gemini モデル、Agent Platform エンドポイントでホストされる
   モデルなど、Google Cloud と密接に統合されたモデルに使用します。モデル名または
   エンドポイントリソース文字列を渡すと、ADK の内部レジストリが適切なバックエンド
   クライアントに解決します。

      *  [Gemini モデル](/agents/models/google-gemini/)
      *  [Claude モデル](/agents/models/anthropic/)
      *  [Agent Platform ホスティングモデル](/agents/models/agent-platform/)

2. **モデルコネクター:** Google エコシステム外のモデルや、特定のクライアント設定を要するモデルに対しては、
   `ApigeeLlm` や `LiteLlm` のようなラッパークラスをインスタンス化し、`LlmAgent` の
   `model` パラメータに渡します。

      *  [Apigee モデル](/agents/models/apigee/)
      *  [LiteLLM モデル](/agents/models/litellm/)
      *  [Ollama モデルホスティング](/agents/models/ollama/)
      *  [vLLM モデルホスティング](/agents/models/vllm/)
      *  [LiteRT-LM モデルホスティング](/ja/agents/models/litert-lm/)

3. **[モデルルーティング](/ja/agents/models/routing/):** ルーター関数を使って
   実行時に複数のモデルから動的に選択し、エラー時には自動的に別のモデルへ
   フェイルオーバーできます。
