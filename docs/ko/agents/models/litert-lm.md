# ADK 에이전트를 위한 LiteRT-LM 모델 호스트

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span>
</div>

[LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM)은 엣지 플랫폼 전반에서
언어 모델을 효율적으로 실행하기 위한 C++ 라이브러리입니다. 데스크톱(Linux,
macOS, Windows)에서는 ADK가 LiteRT-LM CLI `lit`으로 실행한 LiteRT-LM 서버를
통해 LiteRT-LM 호스팅 모델과 통합됩니다.

## 시작하기

LiteRT-LM은 `Gemini` 클래스와 함께 사용합니다. `base_url`과 `model`
매개변수만 설정하면 됩니다.

1. `base_url`을 LiteRT-LM 서버 URL로 설정합니다. 예: `localhost:8001`
2. `model`을 LiteRT-LM 모델 이름으로 설정합니다. 예: `gemma3n-e2b`

```py
from google.adk.agents import Agent
from google.adk.models import Gemini

root_agent = Agent(
    model=Gemini(
        model="gemma3n-e2b",
        base_url="http://localhost:8001",
    ),
    name="dice_agent",
    description=(
        "hello world agent that can roll a die of 8 sides and check prime"
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

그다음 평소처럼 에이전트를 실행합니다.

```bash
adk web
```

## LiteRT-LM 서버 실행하기

LiteRT-LM 서버는 LiteRT-LM 모델을 제공하는 별도 프로세스입니다. 이 서버는
LiteRT-LM CLI 도구 `lit`이 시작합니다.

### `lit` CLI 도구 다운로드

LiteRT-LM GitHub 저장소의
[안내](https://github.com/google-ai-edge/LiteRT-LM?tab=readme-ov-file#desktop-cli-lit)를
따라 `lit` CLI 도구를 다운로드하세요.

### 모델 다운로드

서버를 시작하기 전에 먼저 모델을 다운로드해야 합니다. `lit`으로 LiteRT-LM 모델을
다운로드하려면 *Hugging Face* 사용자 액세스 토큰이 필요합니다. 토큰은
[여기](https://huggingface.co/settings/tokens)에서 발급받을 수 있습니다.

다운로드 가능한 모델 목록을 보려면 `lit list` 명령을 사용하세요.

```bash
lit list --show_all
```

`lit pull` 명령으로 모델을 다운로드합니다.

```bash
export HUGGING_FACE_HUB_TOKEN="**your Hugging Face token**"
lit pull gemma3n-e2b
```

### 서버 실행

모델을 다운로드한 후 다음 명령으로 로컬에서 LiteRT-LM 서버를 시작합니다.

```bash
lit serve --port 8001
```

!!! tip "로컬 서버 포트 번호"

    LiteRT-LM 서버의 포트 번호는 자유롭게 선택할 수 있지만, 에이전트 코드의
    `Gemini` 클래스에서 설정한 `base_url`과 반드시 일치해야 합니다.

### 디버깅

LiteRT-LM 서버로 들어오는 요청과 모델에 전달되는 정확한 입력을 확인하려면
`--verbose` 플래그를 사용하세요.

```bash
lit serve --port 8001 --verbose
```
