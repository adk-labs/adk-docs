# ADK 에이전트를 위한 LiteLLM 모델 커넥터

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

[LiteLLM](https://docs.litellm.ai/)은 모델과 모델 호스팅 서비스를 위한
번역 계층 역할을 수행하는 Python 라이브러리로, 100개 이상의 LLM을 위한
표준화된 OpenAI 호환 인터페이스를 제공합니다.
ADK는 LiteLLM을 통해 OpenAI, Anthropic(비-Vertex AI), Cohere 등 다양한 제공업체의
광범위한 LLM에 접근할 수 있게 해줍니다.
오픈 소스 모델을 로컬에서 실행하거나 자체 호스팅하고,
운영 제어, 비용 절감, 프라이버시, 오프라인 사용 사례에 맞게 LiteLLM으로 통합할 수 있습니다.

LiteLLM 라이브러리를 사용해 원격 또는 로컬로 호스팅된 AI 모델을 사용할 수 있습니다.

*   **원격 모델 호스트:** `LiteLlm` 래퍼 클래스를 사용해 `LlmAgent`의
    `model` 매개변수로 지정합니다.
*   **로컬 모델 호스트:** 로컬 모델 서버를 가리키도록 `LiteLlm` 래퍼를 설정합니다.
    로컬 모델 호스팅 예시는 [Ollama](/adk-docs/agents/models/ollama/) 또는
    [vLLM](/adk-docs/agents/models/vllm/) 문서를 참조하세요.

??? warning "Windows에서 LiteLLM 인코딩"

    ADK 에이전트를 Windows에서 LiteLLM과 함께 사용하면 `UnicodeDecodeError`가 발생할 수 있습니다.
    이는 LiteLLM이 기본 Windows 인코딩(`cp1252`)으로 캐시 파일을 읽으려 할 때 생길 수 있습니다.
    `PYTHONUTF8` 환경 변수를 `1`로 설정하면 이 문제를 방지할 수 있으며,
    Python이 모든 파일 I/O를 UTF-8로 처리하게 됩니다.

    **예시(PowerShell):**
    ```powershell
    # 현재 세션에만 설정
    $env:PYTHONUTF8 = "1"

    # 사용자 환경에 영구 설정
    [System.Environment]::SetEnvironmentVariable('PYTHONUTF8', '1', [System.EnvironmentVariableTarget]::User)
    ```

## 설정

1. **LiteLLM 설치:**
        ```shell
        pip install litellm
        ```
2. **공급자 API 키 설정:** 사용하려는 공급자별 API 키를 환경 변수로 구성합니다.

    * *OpenAI 예시:*

        ```shell
        export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
        ```

    * *Anthropic 예시(비-Vertex AI):*

        ```shell
        export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
        ```

    * *기타 공급자 키는* [LiteLLM Providers 문서](https://docs.litellm.ai/docs/providers)
      를 참고해 해당 환경 변수명을 확인하세요.*

## 구현 예시

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# --- Example Agent using OpenAI's GPT-4o ---
# (Requires OPENAI_API_KEY)
agent_openai = LlmAgent(
    model=LiteLlm(model="openai/gpt-4o"), # LiteLLM model string format
    name="openai_agent",
    instruction="You are a helpful assistant powered by GPT-4o.",
    # ... other agent parameters
)

# --- Example Agent using Anthropic's Claude Haiku (non-Vertex) ---
# (Requires ANTHROPIC_API_KEY)
agent_claude_direct = LlmAgent(
    model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
    name="claude_direct_agent",
    instruction="You are an assistant powered by Claude Haiku.",
    # ... other agent parameters
)
```
