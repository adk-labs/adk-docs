# ADK 에이전트를 위한 OpenAI 모델

<div class="language-support-tag">
   <span class="lst-supported">ADK에서 지원</span><span class="lst-go">Go v2.1.0</span><span class="lst-preview">실험적 기능</span>
</div>

!!! example "실험적 기능"

    `openaimodel` 패키지는 실험적 기능이며 향후 동작이 변경되거나 제거될 수 있습니다. 여러분의 [피드백](https://github.com/google/adk-go/issues/new?template=feature_request.md)을 환영합니다!

ADK에서 OpenAI 모델을 사용할 수 있습니다. 연결하는 방법은 사용하는 언어에 따라 다릅니다.

- **Go — 기본 지원:** ADK Go는 OpenAI Responses API를 타겟팅하여 `model.LLM` 인터페이스를 구현하는 `openaimodel` 패키지를 직접 제공합니다. [시작하기](#시작하기)를 참조하세요.
- **Python — LiteLLM 경유:** ADK Python은 LiteLLM 커넥터를 통해 OpenAI 모델(및 기타 다양한 제공업체)에 액세스합니다. [LiteLLM](/ko/agents/models/litellm/)을 참조하세요.

## 시작하기

`openaimodel` 패키지는 OpenAI API와 상호작용하기 위한 클라이언트를 제공합니다. 이 패키지는 `model.LLM` 인터페이스를 구현하여 OpenAI Responses API 표면을 노출하는 제공업체와 호환됩니다.
다음 코드 예시는 에이전트에서 OpenAI 모델을 사용하는 기본 구현을 보여줍니다.

=== "Go"

    ```go
    import (
    	"context"
    	"log"

    	"github.com/openai/openai-go/v3"
    	"google.golang.org/adk/v2/agent/llmagent"
    	"google.golang.org/adk/v2/model/openaimodel"
    )

    // 모델 인스턴스화
    llm, err := openaimodel.NewModel(context.Background(), openai.ChatModelGPT4oMini, &openaimodel.ClientConfig{})
    if err != nil {
      log.Fatal(err)
    }

    // 에이전트 생성
    agent, err := llmagent.New(llmagent.Config{
      Name:        "openai_agent",
      Model:       llm,
      Instruction: "You are a helpful AI assistant.",
    })
    if err != nil {
      log.Fatal(err)
    }
    ```

실행 가능한 전체 샘플은 ADK Go 저장소의 [examples/openai/](https://github.com/google/adk-go/tree/main/examples/openai)를 참조하세요.

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
- 일부 `GenerateContentConfig` 옵션은 자동으로 무시되지 않고 오류를 반환합니다: `TopK`, 중단 시퀀스(stop sequences), 다중 후보(multiple candidates), 빈도/존재 패널티, 요청 라벨 및 보안 설정.

## 구성 옵션

`ClientConfig`는 클라이언트를 구성하기 위한 여러 옵션을 제공합니다.

- `APIKey`: OpenAI API 키.
- `BaseURL`: 사용자 지정 엔드포인트 URL (OpenAI 호환 엔드포인트에 유용함).
- `HTTPClient`: 사용자 지정 `*http.Client`.
- `Options`: 고급 `openai-go` 요청 옵션 (`[]option.RequestOption`).

`APIKey` 또는 `BaseURL`을 비워 두면 기본 `openai-go` SDK의 기본 동작에 의해 `OPENAI_API_KEY` 및 `OPENAI_BASE_URL` 환경 변수로 자동으로 폴백됩니다.

## OpenAI 모델 인증

OpenAI 모델을 사용할 때 OpenAI API로 인증하려면 API 키를 제공해야 합니다. 이 정보를 제공하는 가장 직접적인 방법은 환경 변수 또는 `.env` 파일을 사용하는 것입니다.

`openaimodel` 패키지는 기본 URL을 구성하여 OpenAI 호환 엔드포인트(예: Ollama, LM Studio 또는 vLLM을 통해 제공되는 로컬 모델)도 지원합니다.

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
