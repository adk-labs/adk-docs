# ADK エージェント向けの vLLM モデルホスト

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

[vLLM](https://github.com/vllm-project/vllm) などのツールを使用すると、
モデルを効率的にホストし、OpenAI 互換の API エンドポイントとして提供できます。
ADK は Python 用の [LiteLLM](/adk-docs/agents/models/litellm/) ライブラリ経由で
vLLM モデルを利用できます。

## セットアップ

1. **モデルのデプロイ:** 選択したモデルを vLLM（または同様のツール）でデプロイします。
   API ベース URL（例: `https://your-vllm-endpoint.run.app/v1`）を控えておきます。
    * *ADK ツール向けに重要:* デプロイ時に、サービングツールが OpenAI 互換の
      ツール/関数呼び出しをサポートし、有効化していることを確認してください。
      vLLM ではモデルにより `--enable-auto-tool-choice` や特定の
      `--tool-call-parser` フラグが必要になる場合があります。vLLM の Tool Use
      ドキュメントを参照してください。
2. **認証:** エンドポイントがどのような認証方式（API キー、ベアラートークンなど）を使うか確認します。

## 統合例

次の例は、vLLM エンドポイントを ADK エージェントで使用する方法を示します。

```python
import subprocess
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# --- Example Agent using a model hosted on a vLLM endpoint ---

# Endpoint URL provided by your vLLM deployment
api_base_url = "https://your-vllm-endpoint.run.app/v1"

# Model name as recognized by *your* vLLM endpoint configuration
model_name_at_endpoint = "hosted_vllm/google/gemma-3-4b-it" # Example from vllm_test.py

# Authentication (Example: using gcloud identity token for a Cloud Run deployment)
# Adapt this based on your endpoint's security
try:
    gcloud_token = subprocess.check_output(
        ["gcloud", "auth", "print-identity-token", "-q"]
    ).decode().strip()
    auth_headers = {"Authorization": f"Bearer {gcloud_token}"}
except Exception as e:
    print(f"Warning: Could not get gcloud token - {e}. Endpoint might be unsecured or require different auth.")
    auth_headers = None # Or handle error appropriately

agent_vllm = LlmAgent(
    model=LiteLlm(
        model=model_name_at_endpoint,
        api_base=api_base_url,
        # Pass authentication headers if needed
        extra_headers=auth_headers
        # Alternatively, if endpoint uses an API key:
        # api_key="YOUR_ENDPOINT_API_KEY"
    ),
    name="vllm_agent",
    instruction="You are a helpful assistant running on a self-hosted vLLM endpoint.",
    # ... other agent parameters
)
```
