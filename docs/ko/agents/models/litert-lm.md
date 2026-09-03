# ADK 에이전트를 위한 LiteRT-LM 모델 호스트

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-kotlin">Kotlin v0.4.0</span>
</div>

[LiteRT-LM](https://github.com/google-ai-edge/LiteRT-LM) 라이브러리를 사용하면 GPU(그래픽 처리 장치) 또는 TPU(텐서 처리 장치)와 같은 전용 프로세서 없이도 다양한 컴퓨팅 장치에서 로컬로 언어 모델을 효율적으로 실행할 수 있습니다. LiteRT-LM은 Google Gemma 모델과 서드파티 모델을 포함한 다양한 모델을 지원합니다. 이 가이드는 다음 언어에서 ADK와 함께 LiteRT-LM을 설정하는 지침을 제공합니다.

- [Python](#python) 
- [Kotlin](#kotlin)

## Python

이 지침은 LiteRT-LM의 로컬 호스팅 모델 서버인 `lit`을 사용하는 것을 포함하여, Python에서 Gemma 오픈 가중치 모델과 함께 ADK에서 LiteRT-LM 서버를 사용하는 방법을 설명합니다.

### 리소스 설치

LiteRT-LM과 함께 사용할 모델을 다운로드하고 모델을 찾고 다운로드하는 데 도움이 되는 `lit` CLI 도구가 필요합니다.

#### `lit` CLI 도구 설치

LiteRT-LM GitHub 저장소의 [지침](https://github.com/google-ai-edge/LiteRT-LM?tab=readme-ov-file#desktop-cli-lit)에 따라 `lit` CLI 도구를 다운로드하고 설치합니다.

#### 모델 다운로드

서버를 시작하기 전에 모델을 다운로드해야 합니다. `lit`을 사용하여 LiteRT-LM 모델을 다운로드하려면 _Hugging Face_ 사용자 액세스 토큰이 필요합니다. _Hugging Face_ 계정 토큰은 [여기](https://huggingface.co/settings/tokens)에서 얻을 수 있습니다.

다운로드 가능한 모델 목록을 보려면 `lit list` 명령을 사용합니다.

```bash
lit list --show_all
```

`lit pull` 명령을 사용하여 모델을 다운로드합니다.

```bash
export HUGGING_FACE_HUB_TOKEN="**your Hugging Face token**"
lit pull gemma3n-e2b
```

### 에이전트 구성

LiteRT-LM 및 호스팅된 모델에 연결하도록 에이전트를 구성합니다. LiteRT-LM으로 Gemma 모델을 실행할 때 모델 식별자 및 로컬 네트워크 주소로 `Gemini` 모델 클래스를 구성합니다.

ADK 및 Gemma 모델과 함께 LiteRT-LM을 사용하려면 다음을 수행합니다.

1.  `base_url`을 스키마를 포함한 LiteRT-LM 서버 URL로 설정합니다(예: `http://localhost:8001`).
2.  `model`을 LiteRT-LM 모델 이름으로 설정합니다(예: `gemma3n-e2b`).

다음 예시 코드는 위에 설명된 Gemma 모델 구성을 제공하는 로컬 호스팅 LiteRT-LM 인스턴스에 연결하도록 에이전트를 구성하는 방법을 보여줍니다.

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

그런 다음 평소와 같이 에이전트를 실행합니다.

```bash
adk web
```

### LiteRT-LM 서버 실행

LiteRT-LM 서버는 LiteRT-LM 모델을 제공하는 별도의 프로세스입니다. LiteRT-LM CLI 도구인 `lit`에 의해 시작됩니다.

#### 서버 실행

모델을 다운로드한 후 다음 명령을 실행하여 로컬에서 LiteRT-LM 서버를 시작합니다.

```bash
lit serve --port 8001
```

!!! tip "로컬 서버 포트 번호"

    에이전트 코드의 `Gemini` 클래스에 설정한 `base_url`과 일치하는 한 LiteRT-LM 서버의 포트 번호를 자유롭게 선택할 수 있습니다.

#### 디버깅

LiteRT-LM 서버로 들어오는 요청과 모델에 전송된 정확한 입력을 보려면 `--verbose` 플래그를 사용합니다.

```bash
lit serve --port 8001 --verbose
```

## Kotlin

이 지침은 `com.google.adk.kt.litertlm` 패키지를 사용하여 Kotlin에서 ADK와 함께 LiteRT-LM을 사용하는 방법을 설명합니다.

### 리소스 설치

LiteRT-LM과 함께 사용할 모델을 다운로드하고 모델을 찾고 다운로드하는 데 도움이 되는 `litert-lm` CLI 도구가 필요합니다.

#### LiteRT-LM CLI 설치

사전 요구 사항: Python 3.10 이상

CLI를 설치하려면 다음을 실행합니다.

```bash
pip install --upgrade litert-lm
```

uv 사용과 같은 추가 설치 방법은 [LiteRT-LM CLI 설치 가이드](https://developers.google.com/edge/litert-lm/cli/installation)를 참고하세요.

#### 모델 다운로드

`litert-lm` CLI 도구를 사용하려면 LiteRT-LM과 호환되는 모델을 다운로드합니다. `litert-lm`을 사용하여 Hugging Face에서 직접 모델을 다운로드합니다.

```bash
litert-lm import \
  --from-huggingface-repo litert-community/gemma-4-E2B-it-litert-lm \
  gemma-4-E2B-it.litertlm
```

다운로드된 모델은 로컬의 다음 위치에 저장됩니다.

```
~/.litert-lm/models/gemma-4-E2B-it.litertlm/model.litertlm
```

`litert-lm`에 대한 자세한 내용은 [LiteRT-LM CLI 사용 가이드](https://developers.google.com/edge/litert-lm/cli/usage)를 참고하세요.

### 종속 항목 추가

ADK Kotlin은 어댑터 패키지인 `com.google.adk:google-adk-kotlin-litertlm`을 통해 LiteRT-LM과 함께 작동합니다.

`build.gradle.kts`에서 종속 항목에 `com.google.adk:google-adk-kotlin-litertlm` 및 `com.google.ai.edge.litertlm:litertlm-jvm`을 추가합니다.

```kt
repositories {
    mavenCentral()
    google()
}

dependencies {
    implementation("com.google.adk:google-adk-kotlin-core:0.9.0")
    implementation("com.google.adk:google-adk-kotlin-litertlm:0.9.0")
    implementation("com.google.ai.edge.litertlm:litertlm-jvm:0.13.1")
    // 기타 종속 항목...
}
```

### 에이전트 모델 구성

`LlmAgent` 객체의 일부로 `LiteRtLmModel` 객체를 구성하여 LiteRT-LM으로 에이전트의 로컬 모델을 실행합니다. 아직 ADK Kotlin 프로젝트가 없다면 [ADK용 Kotlin 빠른 시작](/ko/get-started/kotlin/) 시작 가이드를 따르세요. 다음 코드 예시는 `LlmAgent`를 구성하고 `model` 매개변수를 `LiteRtLmModel`로 설정하는 방법을 보여줍니다.

```kt
 object HelloTimeAgent {

    // 환경 변수에서 모델 경로를 가져옵니다.
    private val modelPath: String by lazy {
        System.getenv("LITERT_LM_MODEL_PATH")
            ?: throw IllegalStateException(
                "LITERT_LM_MODEL_PATH environment variable must be set pointing to a .litertlm file."
            )
    }

    @JvmField
    val rootAgent =
        LlmAgent(
            name = "hello_time_agent",
            description = "Tells the current time in a specified city.",
            model =
                LiteRtLmModel.create(
                    EngineConfig(modelPath = modelPath, backend = Backend.CPU())
                ),
            instruction =
                Instruction(
                    "You are a helpful assistant that tells the current time in a city. " +
                        "Use the 'getCurrentTime' tool for this purpose."
                ),
            tools = TimeService().generatedTools(),
        )
}
```

이 예제에서 LiteRT-LM 모델 파일의 경로는 환경 변수 `LITERT_LM_MODEL_PATH`에서 읽습니다. 모델은 CPU에서 실행됩니다. `backend = Backend.GPU()`를 설정하여 GPU에서 모델을 실행할 수도 있습니다.

에이전트를 실행할 때 `LITERT_LM_MODEL_PATH`를 모델 파일의 위치(예: `~/.litert-lm/models/gemma-4-E2B-it.litertlm/model.litertlm`)로 설정합니다.

### 에이전트 실행

위의 수정 사항을 적용하여 [ADK용 Kotlin 빠른 시작](/ko/get-started/kotlin/)을 완료했다면 모델 파일 경로로 환경 변수 `LITERT_LM_MODEL_PATH`를 설정하고 명령줄 REPL을 사용하여 ADK 에이전트를 실행할 수 있습니다.

```bash
LITERT_LM_MODEL_PATH=~/.litert-lm/models/gemma-4-E2B-it.litertlm/model.litertlm ./gradlew run
```

상호작용 예시:

```
Agent hello_time_agent is ready. Type 'exit' to quit.

You > what's your name?

hello_time_agent > I am Gemma 4, a Large Language Model developed by Google DeepMind.

You > what time is it in paris?

hello_time_agent > calls tool: getCurrentTime

hello_time_agent > The time in Paris is 10:30 am.
```
