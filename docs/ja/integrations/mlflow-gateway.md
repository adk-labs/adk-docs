---
catalog_title: MLflow AI Gateway
catalog_description: 組み込みのガバナンスを使用して、マルチプロバイダー アクセスのための LLM リクエストをルーティングします。
catalog_icon: /integrations/assets/mlflow.png
catalog_tags: ["connectors"]
---


# ADK エージェント用の MLflow AI ゲートウェイ

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[MLflow AI Gateway](https://mlflow.org/docs/latest/genai/governance/ai-gateway/)
MLflow 追跡サーバーに組み込まれたデータベースを利用した LLM プロキシです (MLflow ≥
3.0）。数十のプロバイダーにわたって統合された OpenAI 互換 API を提供します。
Gemini、Anthropic、Mistral、Bedrock、Ollama などが含まれます。
シークレット管理、フォールバック/再試行、トラフィック分割、予算追跡、すべて
MLflow UI を通じて設定されます。

MLflow AI Gateway は OpenAI 互換のエンドポイントを公開しているため、
ADK エージェントは、[LiteLLM](/agents/models/litellm/) モデル コネクタを使用してそれに接続します。

## 使用例

- **マルチプロバイダー ルーティング**: エージェント コードを変更せずに LLM プロバイダーを切り替えます
- **秘密管理**: プロバイダー API キーは暗号化されてサーバーに保存されます。あなたの
  アプリケーションはプロバイダーキーを送信しません
- **フォールバックと再試行**: 障害発生時にモデルをバックアップする自動フェイルオーバー
- **予算追跡**: エンドポイントごとまたはユーザーごとのトークン予算
- **トラフィック分割**: リクエストの割合を別のモデルにルーティングします。
  A/B テスト
- **使用状況トレース**: すべての呼び出しが MLflow トレースとして自動的に記録されます。

## 前提条件

- MLflow バージョン 3.0 以降
- 環境にインストールされている Google ADK と LiteLLM

## セットアップ

依存関係をインストールします。

```bash
pip install mlflow[genai] google-adk litellm
```

MLflow サーバーを起動します。

```bash
mlflow server --host 127.0.0.1 --port 5000
```

MLflow UI は、`http://localhost:5000` で入手可能になります。

次の MLflow UI に移動して、ゲートウェイ エンドポイントを作成します。
`http://localhost:5000` に移動し、**AI ゲートウェイ → エンドポイントの作成** に移動します。を選択してください
プロバイダー (例: Google Gemini) とモデル (例: `gemini-flash-latest`)、および
プロバイダー API キーを入力します。このキーはサーバー上に暗号化されて保存されます。

![MLflow AI Gateway - Create Endpoint](assets/mlflow-gateway-create-endpoint.png)

[MLflow AI Gateway
documentation](https://mlflow.org/docs/latest/genai/governance/ai-gateway/endpoints/) を参照してください。
エンドポイント構成の詳細については、

## エージェントと一緒に使用する

MLflow ゲートウェイを指す `api_base` とともに `LiteLlm` ラッパーを使用します。
エンドポイント。 `model` パラメータには、`openai/` プレフィックスとそれに続く名前を使用する必要があります。
ゲートウェイエンドポイント名。

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Point to MLflow AI Gateway endpoint.
# "my-chat-endpoint" is the endpoint name you created in the MLflow UI.
agent = LlmAgent(
    model=LiteLlm(
        model="openai/my-chat-endpoint",
        api_base="http://localhost:5000/gateway/openai/v1",
        api_key="unused",  # provider keys are managed by the MLflow server
    ),
    name="gateway_agent",
    instruction="You are a helpful assistant powered by MLflow AI Gateway.",
)
```

基盤となる LLM プロバイダーは、
MLflow UI のゲートウェイ エンドポイント。ADK でコードを変更する必要はありません。
エージェント。

## ヒント

- `api_key` パラメータは LiteLLM に必要ですが、
  ゲートウェイ。空ではない文字列に設定します。
- プロキシの背後またはリモート ホスト上で、`localhost:5000` を実際のサーバーに置き換えます。
  住所。
- エンドツーエンドで[MLflow Tracing](/integrations/mlflow-tracing/)と組み合わせる
  ADK エージェントの可観測性。

## リソース

- [MLflow AI Gateway
  Documentation](https://mlflow.org/docs/latest/genai/governance/ai-gateway/):
  エンドポイント管理をカバーする MLflow AI Gateway の公式ドキュメント。
  クエリ API とゲートウェイ機能。
- [MLflow Tracing for ADK](/integrations/mlflow-tracing/): 可観測性のセットアップ
  MLflow トレースを使用した ADK エージェント向け。
- [LiteLLM model connector](/agents/models/litellm/): のドキュメント
  ADK エージェントを互換性のあるエンドポイントに接続するために使用される LiteLLM ラッパー。
