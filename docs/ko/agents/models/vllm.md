# ADK 에이전트를 위한 vLLM 모델 호스트

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

[vLLM](https://github.com/vllm-project/vllm) 같은 도구를 사용하면
모델을 효율적으로 호스팅하고 OpenAI 호환 API 엔드포인트로 제공할 수 있습니다.
ADK는 Python에서 [LiteLLM](/adk-docs/agents/models/litellm/) 라이브러리를 통해
vLLM 모델을 사용할 수 있습니다.

## 설정

1. **모델 배포:** 원하는 모델을 vLLM(또는 유사 도구)로 배포합니다.
   API 베이스 URL(예: `https://your-vllm-endpoint.run.app/v1`)을 기록합니다.
    * *ADK 도구에 중요:* 배포 시 서빙 도구가 OpenAI 호환 도구/함수 호출을 지원하고 활성화했는지 확인합니다.
      vLLM의 경우 모델에 따라 `--enable-auto-tool-choice` 또는 특정 `--tool-call-parser` 플래그가 필요할 수 있습니다.
      자세한 내용은 vLLM 문서의 Tool Use 섹션을 확인하세요.
2. **인증:** 엔드포인트의 인증 방식(예: API 키, bearer 토큰)을 확인합니다.

## 통합 예시

다음 예시는 vLLM 엔드포인트를 ADK 에이전트와 함께 사용하는 방법을 보여줍니다.

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
