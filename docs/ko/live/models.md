# 라이브 에이전트를 위한 지원 모델

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span>
</div>

라이브 에이전트는 `run_live()` 아래에서 두 가지 [음성 아키텍처](architectures/index.md) 중 하나로 실행됩니다:

- **[음성 대 음성 (Speech-to-speech)](architectures/speech-to-speech.md)**: 단일 네이티브 오디오 Live 모델이 양방향 연결을 통해 오디오 입력과 오디오 출력을 직접 처리합니다.
- **[캐스케이드 (Cascade)](architectures/cascade.md)**: 음성-텍스트 변환(STT), 임의의 텍스트 LLM, 텍스트-음성 변환(TTS)을 순차적으로 연결합니다.

## 네이티브 오디오 모델 { #live-models }

네이티브 오디오 모델은 중간의 텍스트-음성 변환(TTS) 단계 없이 오디오 입력을 받아 오디오 출력을 엔드투엔드로 직접 생성합니다. 이를 통해 단일 양방향 연결 위에서 자연스러운 운율(prosody)을 제공합니다.

| 모델 | AI Studio | Agent Platform |
|---|---|---|
| Gemini 2.5 Flash Live | `gemini-2.5-flash-native-audio-preview-12-2025` (Preview) | `gemini-live-2.5-flash-native-audio` (GA) |
| Gemini 3.1 Flash Live | `gemini-3.1-flash-live-preview` (Preview) | 사용 불가 |
| Gemini 3.8 Live | `gemini-3.8-live` (GA) | `gemini-3.8-live` (GA) |
| Gemini 3.8 Live Extended Thinking | `gemini-3.8-live-extended-thinking` (GA) | 사용 불가 |

Gemini 2.5 Flash Live는 백엔드마다 ID가 다를 뿐 하나의 모델이며, 제공되는 기능은 어느 쪽이든 동일합니다. ADK의 `LlmAgent.DEFAULT_LIVE_MODEL`은 `gemini-live-2.5-flash-native-audio`이며, 이 섹션의 예제에서 사용되는 모델이기도 합니다.

Gemini 3.1 Flash Live는 AI Studio에서만 사용할 수 있으며 비차단(non-blocking) 도구를 지원하지 않습니다. 자세한 내용은 [모델별 기능 지원](#per-model-feature-support) 및 [Gemini 3.1 Flash Live 모델 페이지](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview)를 참고하세요.

Gemini 3.8 Live는 두 백엔드 모두에서 실행됩니다. Gemini 3.8 Live Extended Thinking은 백그라운드 추론(background reasoning)을 추가하며 AI Studio에서만 사용할 수 있고, [모델별 기능 지원](#per-model-feature-support)에 나열된 에이전트 변경 사항이 필요합니다. 두 모델을 비교하려면 [AI Studio](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live) 또는 [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-live)의 Gemini 3.8 Live 모델 페이지와 [Gemini 3.8 Live Extended Thinking 모델 페이지](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live-extended-thinking)를 참고하세요.

이들 모델은 **오디오 전용**으로 출력하며 대화 언어를 자동으로 감지합니다. `TEXT` 응답 모달리티를 지원하지 않으므로, 음성과 함께 텍스트를 얻으려면 [오디오 전사](configuration.md#audio-transcription)를 사용해야 합니다. 음성 선택, 전사, 턴 감지는 [구성](configuration.md)에서 다룹니다.

### 모델별 기능 지원 { #per-model-feature-support }

몇 가지 ADK 설정은 실행 중인 모델에 따라 다르게 동작합니다:

| 기능 | Gemini 2.5 Flash Live | Gemini 3.1 Flash Live | Gemini 3.8 Live | Gemini 3.8 Live Extended Thinking |
|---|---|---|---|---|
| [능동적 및 감정적 대화](configuration.md#proactivity-and-affective-dialog) | `RunConfig`를 통한 옵트인(Opt-in) | `RunConfig` 설정 무시됨 | `RunConfig` 설정 무시됨 | `RunConfig` 설정 무시됨 |
| [비차단(Non-blocking) 도구](tools.md#non-blocking-tools) | 지원됨 | 지원 안 됨 | 지원됨 | 모든 도구에 필수 (아래 설명 참조) |
| 도구의 [`response_scheduling`](tools.md#non-blocking-tools) | 지원됨 | 지원 안 됨 | 지원됨 | 지원 안 됨 |
| [모델 응답의 종료](events.md#interaction-status) | `turn_complete` | `turn_complete` | `turn_complete` | `interaction_status`가 `IDLE` (아래 설명 참조) |

2.5에서 더 최신 모델로 전환할 때는 단일 서버 이벤트에 여러 파트가 포함될 수 있으므로 `parts[0]`을 읽는 대신 `event.content.parts`를 순회하세요. 또한 턴 커버리지에 감지된 모든 오디오 활동과 비디오 프레임이 포함될 수 있어 비디오를 지속적으로 스트리밍할 경우 토큰 비용이 달라집니다. 업스트림 [마이그레이션 안내](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview#migrating-from-gemini-25-flash-live)를 참조하세요.

[AI Studio](https://ai.google.dev/gemini-api/docs/models) 및 [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models) 문서의 각 모델 페이지에서는 지원되는 사고 수준(thinking level)과 같은 모델 수준 동작을 설명합니다. ADK에서는 에이전트의 `generate_content_config.thinking_config`를 통해 사고(thinking)를 설정합니다.

Gemini 3.8 Live Extended Thinking을 사용하려면 ADK Python 2.10 이상이 필요하며 에이전트에 두 가지 변경을 적용해야 합니다:

- **비차단(Non-blocking) 도구**: 모든 도구에 `behavior = types.Behavior.NON_BLOCKING`을 설정하고 `response_scheduling`은 설정하지 않은 채로 두세요. [비차단 도구](tools.md#non-blocking-tools)를 참고하세요.
- **상호작용 상태(Interaction status)**: 요청당 `turn_complete`가 여러 번 도착할 수 있으므로 `event.interaction_status`(`run_live`에서는 `interactionStatus`)를 읽으세요. 이 값은 모델이 아직 요청을 처리하는 동안에는 `IN_PROGRESS`이고 작업이 완료되면 `IDLE`이 됩니다. [상호작용 상태](events.md#interaction-status)를 참고하세요.

## 캐스케이드 모델

[캐스케이드 아키텍처](architectures/cascade.md)에서 추론 단계는 [에이전트용 모델](../agents/models/index.md)에 있는 모든 텍스트 모델을 허용합니다. 음성 단계의 경우 ADK는 다음 Gemini 음성 모델을 지원합니다:

| 단계 | 모델 |
|---|---|
| **음성-텍스트 변환 (`GeminiSTT`)** | `gemini-3.5-transcribe-live` |
| **텍스트-음성 변환 (`GeminiTTS`)** | `gemini-3.8-flash-lite-tts`, `gemini-3.8-flash-tts` |

또한 `CascadeLive`에는 [ElevenLabs 모델](https://elevenlabs.io/docs/overview/models)(`ElevenLabsSTT`, `ElevenLabsTTS`)을 위한 내장 어댑터가 포함되어 있으며, [커스텀 변환](architectures/cascade.md#custom-speech-transforms)을 통해 다른 모든 음성 제공업체를 지원합니다.

## 백엔드 선택하기

Gemini 모델은 두 백엔드 중 하나를 통해 접근합니다. ADK는 동일한 코드로 두 백엔드와 통신하며, 환경 변수로 전환할 수 있으므로 한 곳에서 개발하고 다른 곳에 배포할 수 있습니다.

| | AI Studio | Agent Platform |
|---|---|---|
| **정식 명칭** | Google AI Studio | Gemini Enterprise Agent Platform |
| **적합한 용도** | 프로토타이핑, 개발 | 프로덕션, 엔터프라이즈 |
| **인증** | API 키 (`GOOGLE_API_KEY`) | Cloud 자격 증명 (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`) |
| **설정** | API 키만 필요 | Cloud 프로젝트 설정 필요 |
| **한도** | [세션 지속 시간 및 동시성](#platform-limits-and-quotas) | [세션 지속 시간 및 동시성](#platform-limits-and-quotas) |

코드 변경 없이 `GOOGLE_GENAI_USE_ENTERPRISE` 환경 변수(`FALSE`는 AI Studio, `TRUE`는 Agent Platform)로 전환합니다. 설정 방법은 [빠른 시작](get-started/streaming-python.md)을 참고하세요.

!!! note "Agent Platform: Live API 모델에는 `global` 위치가 지원되지 않음"

    Live API 모델은 `GOOGLE_CLOUD_LOCATION=global`에서는 사용할 수 없습니다. `us-central1`, `us-east1` 또는 `asia-northeast1`과 같은 리전 엔드포인트를 사용하고, 배포하기 전에 [Agent Platform 위치](https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations)의 엔드포인트 위치 표를 확인하세요.

## 플랫폼 한도 및 할당량 { #platform-limits-and-quotas }

두 백엔드 모두 연결 및 세션 실행 시간과 동시 실행 가능한 세션 수를 제한합니다. 이러한 수치는 변경될 수 있으므로 업스트림 공식 문서를 신뢰할 수 있는 정보원으로 취급하고 프로덕션 한도를 사전에 확인하세요.

| 한도 | AI Studio | Agent Platform |
|---|---|---|
| 세션 지속 시간 (오디오 전용) | 15분 | 15분 |
| 세션 지속 시간 (오디오 + 비디오) | 2분 | 2분 |
| 연결 수명 | 약 10분 | 약 10분 |
| 동시 세션 수 | [속도 제한](https://ai.google.dev/gemini-api/docs/rate-limits) 참고 | 종량제 기준 프로젝트당 최대 1,000개, Provisioned Throughput 사용 시 무제한 |

Agent Platform은 위의 오디오 전용 한도와 별개로 대화 세션을 기본적으로 10분으로 추가 제한합니다.

[컨텍스트 윈도우 압축](sessions.md#context-window-compression)을 활성화하면 세션을 지속 시간 한도 이상으로 연장할 수 있습니다. Agent Platform에서는 [Cloud Console 할당량 페이지](https://console.cloud.google.com/iam-admin/quotas)의 **"Bidi generate content concurrent requests"** 항목에서 동시 세션 수 증가를 요청할 수 있습니다. 최신 수치는 [AI Studio](https://ai.google.dev/gemini-api/docs/live-api/capabilities), [Gemini API 속도 제한](https://ai.google.dev/gemini-api/docs/rate-limits), [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api/start-manage-session) 문서를 확인하세요.

## 모델 이름 처리 방법

모델 이름을 하드코딩하기보다 환경 변수에서 읽어오세요. 동일한 모델이라도 AI Studio와 Agent Platform에서 ID가 다르므로, `.env` 변수를 사용하면 하나의 코드베이스로 두 백엔드를 모두 지원할 수 있으며 모델 사용 중단(deprecation)에 유연하게 대처할 수 있습니다.

**권장 패턴:**

```python
import os
from google.adk.agents import Agent

# 합리적인 기본값을 폴백으로 사용하여 환경 변수 사용
agent = Agent(
    name="my_agent",
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-live-2.5-flash-native-audio"),
    tools=[...],
    instruction="..."
)
```

**환경 변수를 사용해야 하는 이유:**

- **백엔드별 ID**: 동일한 모델이라도 AI Studio와 Agent Platform에서 이름이 다르므로 둘 사이를 전환하려면 모델 ID를 변경해야 합니다. 환경 변수를 사용하면 이를 코드에서 분리할 수 있습니다.
- **모델 가용성 변경**: 모델은 정기적으로 출시되고 지원이 중단됩니다. 1년 전에 작성된 라이브 에이전트가 더 이상 존재하지 않는 모델에 고정되어서는 안 됩니다.
- **환경별 구성**: 개발, 스테이징, 프로덕션 환경에 서로 다른 모델을 사용합니다.

**`.env` 파일 구성:**

```bash
# AI Studio
DEMO_AGENT_MODEL=gemini-2.5-flash-native-audio-preview-12-2025

# AI Studio 또는 Agent Platform
# DEMO_AGENT_MODEL=gemini-3.8-live

# AI Studio (다단계 추론 및 느린 도구용)
# DEMO_AGENT_MODEL=gemini-3.8-live-extended-thinking

# Agent Platform
# DEMO_AGENT_MODEL=gemini-live-2.5-flash-native-audio
```

!!! note "환경 변수 로딩 순서"

    `python-dotenv`로 `.env` 파일을 사용할 때 환경 변수를 읽는 모듈을 가져오기 **전**에 `load_dotenv()`를 호출해야 합니다. 그렇지 않으면 `os.getenv()`가 `None`을 반환하고 기본값으로 대체되어 `.env` 구성을 무시하게 됩니다.

    **`main.py`의 올바른 순서:**

    ```python
    from dotenv import load_dotenv
    from pathlib import Path

    # 에이전트를 import하기 전에 .env 파일을 로드합니다
    load_dotenv(Path(__file__).parent / ".env")

    # 이제 환경 변수를 사용하는 모듈을 안전하게 import할 수 있습니다
    from google_search_agent.agent import agent
    ```

    **잘못된 순서 (작동하지 않음):**

    ```python
    from dotenv import load_dotenv
    from google_search_agent.agent import agent  # 에이전트가 여기서 환경 변수를 읽음

    # 너무 늦었습니다! 에이전트는 이미 기본 모델로 초기화되었습니다
    load_dotenv(Path(__file__).parent / ".env")
    ```

    이는 Python의 import 동작 방식 때문입니다. 모듈을 import할 때 최상위 코드가 즉시 실행됩니다. 에이전트 모듈이 import 시점에 `os.getenv("DEMO_AGENT_MODEL")`을 호출하는 경우 `.env` 파일이 이미 로드되어 있어야 합니다.

**적합한 모델 선택:**

1. **백엔드 선택**: 프로토타이핑은 AI Studio, 프로덕션은 Agent Platform을 선택합니다. 이에 따라 위의 표에서 ID 열이 결정되며, Agent Platform에서는 선택지가 Gemini 2.5 Flash Live와 Gemini 3.8 Live로 좁혀집니다.
2. **현재 가용성 확인**: 위의 모델 표와 공식 문서를 참조하세요.
3. **환경 변수 구성**: `.env` 파일에 모델 이름을 설정하고 에이전트를 생성할 때 해당 값을 읽어옵니다.

## 모델 호환성 및 가용성

모델 호환성과 가용성에 대한 최신 정보는 다음을 참조하세요:

- **AI Studio**: [Gemini 모델 문서](https://ai.google.dev/gemini-api/docs/models) 및 [Live API 기능 가이드](https://ai.google.dev/gemini-api/docs/live-api/capabilities)
- **Agent Platform**: [Live API 개요](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api) 및 [Agent Platform 모델 문서](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models)

프로덕션에 배포하기 전에 항상 공식 문서에서 모델 가용성과 기능 지원 여부를 확인하세요.
