# ADK 에이전트를 위한 Ollama 모델 호스트

<div class="language-support-tag">
    <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v0.1.0</span>
</div>

[Ollama](https://ollama.com/)는 오픈 소스 모델을 로컬에서 호스팅하고 실행할 수 있게 해주는 도구입니다.
ADK는 [LiteLLM](/adk-docs/agents/models/litellm/) 모델 커넥터 라이브러리를 통해
Ollama에서 호스팅되는 모델과 통합됩니다.

## 시작하기

Ollama에서 호스팅되는 모델로 에이전트를 만들 때는 LiteLLM 래퍼를 사용합니다.
다음 예시는 Gemma 오픈 모델을 에이전트에서 사용하는 기본 구현을 보여줍니다.

```py
root_agent = Agent(
    model=LiteLlm(model="ollama_chat/gemma3:latest"),
    name="dice_agent",
    description=(
        "hello world agent that can roll a dice of 8 sides and check prime"
        " numbers."
    ),
    instruction="""
      You roll dice and answer questions about the outcome of the dice rolls.
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

!!! warning "경고: `ollama_chat` 인터페이스 사용"

    `ollama` 대신 반드시 `ollama_chat` 프로바이더를 설정해야 합니다.
    `ollama`를 사용하면 도구 호출 무한 루프 또는 이전 컨텍스트 무시 같은 예기치 않은 동작이 발생할 수 있습니다.

!!! tip "`OLLAMA_API_BASE` 환경 변수 사용"

    생성 요청에서 `api_base` 파라미터를 지정할 수 있지만,
    v1.65.5에서는 라이브러리가 다른 API 호출에 환경 변수를 사용합니다.
    모든 요청이 올바른 경로로 라우팅되도록 Ollama 서버 URL에 대한
    `OLLAMA_API_BASE`를 설정해야 합니다.

```bash
export OLLAMA_API_BASE="http://localhost:11434"
adk web
```

## 모델 선택

에이전트에서 도구를 사용하는 경우 [Ollama 웹사이트](https://ollama.com/search?c=tools)에서
도구 지원 모델을 선택해야 합니다.
안정적인 결과를 위해서는 도구가 지원되는 모델을 사용하세요.
다음 명령으로 모델의 도구 지원 여부를 확인할 수 있습니다.

```bash
ollama show mistral-small3.1
  Model
    architecture        mistral3
    parameters          24.0B
    context length      131072
    embedding length    5120
    quantization        Q4_K_M

  Capabilities
    completion
    vision
    tools
```

`Capabilities` 항목에 **tools**가 표시되어야 합니다.
모델이 사용하는 템플릿을 확인해 필요에 맞게 조정할 수도 있습니다.

```bash
ollama show --modelfile llama3.2 > model_file_to_modify
```

예를 들어 위 모델의 기본 템플릿은 기본적으로 모델이 항상 함수를 호출하도록 지시합니다.
이로 인해 무한 함수 호출 루프가 발생할 수 있습니다.

```
Given the following functions, please respond with a JSON for a function call
with its proper arguments that best answers the given prompt.

Respond in the format {"name": function name, "parameters": dictionary of
argument name and its value}. Do not use variables.
```

다음과 같이 더 설명적인 프롬프트로 교체하면 무한 호출을 줄일 수 있습니다.

```
Review the user's prompt and the available functions listed below.

First, determine if calling one of these functions is the most appropriate way
to respond. A function call is likely needed if the prompt asks for a specific
action, requires external data lookup, or involves calculations handled by the
functions. If the prompt is a general question or can be answered directly, a
function call is likely NOT needed.

If you determine a function call IS required: Respond ONLY with a JSON object in
the format {"name": "function_name", "parameters": {"argument_name": "value"}}.
Ensure parameter values are concrete, not variables.

If you determine a function call IS NOT required: Respond directly to the user's
prompt in plain text, providing the answer or information requested. Do not
output any JSON.
```

그런 다음 아래 명령으로 새 모델을 생성할 수 있습니다.

```bash
ollama create llama3.2-modified -f model_file_to_modify
```

## OpenAI 프로바이더 사용

대신 `openai`를 프로바이더 이름으로 사용할 수도 있습니다. 이 방식은
`OLLAMA_API_BASE` 대신 다음 환경변수를 설정합니다.
- `OPENAI_API_BASE=http://localhost:11434/v1`
- `OPENAI_API_KEY=anything`

참고: `API_BASE` 값 뒤에 `"/v1"`이 붙습니다.

```py
root_agent = Agent(
    model=LiteLlm(model="openai/mistral-small3.1"),
    name="dice_agent",
    description=(
        "hello world agent that can roll a dice of 8 sides and check prime"
        " numbers."
    ),
    instruction="""
      You roll dice and answer questions about the outcome of the dice rolls.
    """,
    tools=[
        roll_die,
        check_prime,
    ],
)
```

```bash
export OPENAI_API_BASE=http://localhost:11434/v1
export OPENAI_API_KEY=anything
adk web
```

### 디버깅

다음 코드를 임포트 직후에 추가하면 Ollama 서버로 전송되는 요청을 확인할 수 있습니다.

```py
import litellm
litellm._turn_on_debug()
```

다음과 같은 형식의 라인을 확인하세요.

```bash
Request Sent from LiteLLM:
curl -X POST \
http://localhost:11434/api/chat \
-d '{'model': 'mistral-small3.1', 'messages': [{'role': 'system', 'content': ...
```
