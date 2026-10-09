# ADK 에이전트를 위한 OpenAI 모델

<div class="language-support-tag">
   <span class="lst-supported">ADK에서 지원</span><span class="lst-go">Go v2.1.0</span><span class="lst-preview">실험적 기능</span>
</div>

!!! example "실험적 기능"

    `openaimodel` 패키지는 실험적 기능이며 향후 동작이 변경되거나 제거될 수 있습니다. 여러분의 [피드백](https://github.com/google/adk-go/issues/new?template=feature_request.md)을 환영합니다!

ADK에서 OpenAI 모델을 사용할 수 있습니다. 연결하는 방법은 사용하는 언어에 따라 다릅니다.

- **Go — 기본 지원:** ADK Go는 OpenAI Responses API 또는 [Chat Completions API](#chat-completions-api)를 타겟팅하여 `model.LLM` 인터페이스를 구현하는 `openaimodel` 패키지를 직접 제공합니다. [시작하기](#get-started)를 참고하세요.
- **Python — LiteLLM 경유:** ADK Python은 LiteLLM 커넥터를 통해 OpenAI 모델(및 기타 다양한 제공업체)에 액세스합니다. [LiteLLM](/ko/agents/models/litellm/)을 참고하세요.

## 시작하기 {#get-started}

`openaimodel` 패키지는 OpenAI API와 상호작용하기 위한 클라이언트를 제공합니다. 이 패키지는 `model.LLM` 인터페이스를 구현하며 기본적으로 OpenAI Responses API를 사용하거나, `ClientConfig.API`에서 선택한 경우 [Chat Completions API](#chat-completions-api)를 사용합니다.
다음 코드 예시는 에이전트에서 OpenAI 모델을 사용하는 기본 구현을 보여줍니다.

=== "Go"

    === "Responses API"

        ```go
        import (
        	"context"
        	"log"

        	"github.com/openai/openai-go/v3"
        	"google.golang.org/adk/v2/agent/llmagent"
        	"google.golang.org/adk/v2/model/openaimodel"
        )

        // Instantiate the model
        llm, err := openaimodel.NewModel(context.Background(), openai.ChatModelGPT4oMini, &openaimodel.ClientConfig{})
        if err != nil {
          log.Fatal(err)
        }

        // Create the agent
        agent, err := llmagent.New(llmagent.Config{
          Name:        "openai_agent",
          Model:       llm,
          Instruction: "You are a helpful AI assistant.",
        })
        if err != nil {
          log.Fatal(err)
        }
        ```

        실행 가능한 전체 샘플은 ADK Go 저장소의 [examples/openai/responses/](https://github.com/google/adk-go/tree/main/examples/openai/responses)를 참고하세요.

    === "Chat Completions API"

        ADK Go v2.5.0 이상이 필요합니다.

        ```go
        import (
        	"context"
        	"log"
        	"os"

        	"github.com/openai/openai-go/v3"
        	"google.golang.org/adk/v2/agent/llmagent"
        	"google.golang.org/adk/v2/model/openaimodel"
        )

        // Instantiate the model on the Chat Completions API
        llm, err := openaimodel.NewModel(context.Background(), openai.ChatModelGPT4oMini, &openaimodel.ClientConfig{
          APIKey: os.Getenv("OPENAI_API_KEY"),
          API:    openaimodel.APIChatCompletions,
        })
        if err != nil {
          log.Fatal(err)
        }

        // Create the agent
        agent, err := llmagent.New(llmagent.Config{
          Name:        "openai_agent",
          Model:       llm,
          Instruction: "You are a helpful AI assistant.",
        })
        if err != nil {
          log.Fatal(err)
        }
        ```

        실행 가능한 전체 샘플은 ADK Go 저장소의 [examples/openai/completions/](https://github.com/google/adk-go/tree/main/examples/openai/completions)를 참고하세요.

## Chat Completions API {#chat-completions-api}

<div class="language-support-tag">
   <span class="lst-supported">ADK에서 지원</span><span class="lst-go">Go v2.5.0</span><span class="lst-preview">실험적 기능</span>
</div>

기본적으로 `openaimodel`은 OpenAI [Responses API](https://platform.openai.com/docs/api-reference/responses)(`POST /v1/responses`)로 요청을 보냅니다. 거의 모든 OpenAI 호환 제공업체는 [Chat Completions API](https://platform.openai.com/docs/api-reference/chat)(`POST /v1/chat/completions`)를 구현하며, 일부는 이 API만 구현합니다. 이를 사용하려면 [시작하기](#get-started) 아래의 Chat Completions API 탭에 표시된 대로 `ClientConfig`의 `API` 필드를 `openaimodel.APIChatCompletions`로 설정하세요. 에이전트, 도구 및 러너는 두 API 모두에서 동일한 방식으로 작동합니다.

!!! warning "다른 제공업체를 위한 API 키 설정"

    다른 OpenAI 호환 제공업체에 연결하려면 `BaseURL`을 해당 엔드포인트로 설정하고 `APIKey`를 해당 키로 설정하세요. `APIKey`가 비어 있으면 `openai-go` SDK는 `OPENAI_API_KEY` 환경 변수로 폴백하여 해당 키를 `BaseURL`로 전송합니다.

두 API는 동일한 기능을 지원하지만 다음과 같은 차이점이 있습니다.

- **생성 설정:** `StopSequences`, `FrequencyPenalty`, `PresencePenalty`, `Seed`는 Chat Completions API로 전송됩니다. Responses API에는 이에 상응하는 필드가 없으므로 오류를 반환합니다.
- **추론 출력:** Chat Completions API는 추론 텍스트를 반환하지 않으므로 응답에 사고(thought) 파트가 포함되지 않으며 `ThinkingConfig.IncludeThoughts`는 무시됩니다. 추론 노력(effort)과 추론 토큰 수 계산은 두 API 모두에서 작동합니다.
- **출력 토큰 제한:** `MaxOutputTokens`는 `max_completion_tokens`로 전송됩니다. 일부 호환 서버는 이전의 `max_tokens` 필드만 인식하므로 해당 서버에서는 제한이 적용되지 않습니다.

## 지원되는 기능

- 텍스트 생성 (스트리밍 및 비스트리밍)
- 함수(도구) 호출 (Function tool calling)
- `OutputSchema`(JSON 스키마)를 통한 정형 출력
- 추론 토큰 계산을 포함한 추론 모델 (예: o-시리즈)
- 토큰 Logprob

## 제한 사항

- **텍스트 전용** — 멀티모달 입력(이미지, 오디오, 파일)은 지원되지 않습니다.
- **함수 도구 전용** — 기본 내장 도구(Google Search, 코드 실행 등)는 지원되지 않습니다.
- **정형 출력은 OpenAI 엄격 모드(Strict mode) 사용** — `OutputSchema`에 선언된 모든 필드는 필수(required)로 취급됩니다.
- 일부 `GenerateContentConfig` 옵션은 자동으로 무시되지 않고 오류를 반환합니다: `TopK`, 다중 후보(multiple candidates), 요청 라벨 및 보안 설정. 또한 Responses API는 중단 시퀀스(stop sequences), 빈도/존재 패널티 및 시드(seed)도 거부하지만, 이는 [Chat Completions API](#chat-completions-api)에서 지원됩니다.

## 구성 옵션

`ClientConfig`는 클라이언트를 구성하기 위한 여러 옵션을 제공합니다.

- `APIKey`: OpenAI API 키.
- `BaseURL`: 사용자 지정 엔드포인트 URL (OpenAI 호환 엔드포인트에 유용함).
- `HTTPClient`: 사용자 지정 `*http.Client`.
- `Options`: 고급 `openai-go` 요청 옵션 (`[]option.RequestOption`).
- `API`: 호출할 OpenAI API: `openaimodel.APIResponses`(기본값) 또는 `openaimodel.APIChatCompletions`. [Chat Completions API](#chat-completions-api)를 참고하세요.

`APIKey` 또는 `BaseURL`을 비워 두면 기본 `openai-go` SDK의 기본 동작에 의해 `OPENAI_API_KEY` 및 `OPENAI_BASE_URL` 환경 변수로 자동으로 폴백됩니다.

## OpenAI 모델 인증

OpenAI 모델을 사용할 때 OpenAI API로 인증하려면 API 키를 제공해야 합니다. 이 정보를 제공하는 가장 직접적인 방법은 환경 변수 또는 `.env` 파일을 사용하는 것입니다.

`openaimodel` 패키지는 기본 URL을 구성하여 OpenAI 호환 엔드포인트(예: Ollama, LM Studio 또는 vLLM을 통해 제공되는 로컬 모델)도 지원합니다. 엔드포인트가 Responses API를 제공하지 않는 경우 [Chat Completions API](#chat-completions-api)에 설명된 대로 `API`도 `openaimodel.APIChatCompletions`로 설정하세요.

=== "OpenAI API"

    ```bash
    # .env 구성 파일
    OPENAI_API_KEY="PASTE_YOUR_OPENAI_API_KEY_HERE"
    ```

=== "OpenAI 호환 엔드포인트"

    ```bash
    # .env 구성 파일
    OPENAI_API_KEY="api-key-if-required"
    OPENAI_BASE_URL="http://localhost:11434/v1" # 예시: 로컬 Ollama 엔드포인트
    ```
