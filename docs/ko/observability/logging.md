# 에이전트 개발 키트(ADK)의 로깅

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v0.1.0</span><span class="lst-typescript">TypeScript v0.2.0</span><span class="lst-go">Go v0.1.0</span><span class="lst-java">Java v0.1.0</span>
</div>

에이전트 개발 키트(ADK)는 Python의 표준 `logging` 모듈을 사용하여 유연하고 강력한 로깅 기능을 제공합니다. 이 로그를 설정하고 해석하는 방법을 이해하는 것은 에이전트의 동작을 모니터링하고 문제를 효과적으로 디버깅하는 데 매우 중요합니다.

## 로깅 철학

ADK의 로깅 접근 방식은 기본적으로 지나치게 장황하지 않으면서도 상세한 진단 정보를 제공하는 것입니다. 애플리케이션 개발자가 직접 설정할 수 있도록 설계되어, 개발 환경이든 프로덕션 환경이든 특정 요구에 맞게 로그 출력을 조정할 수 있습니다.

- **표준 라이브러리:** 표준 `logging` 라이브러리를 사용하므로, 이와 호환되는 모든 설정이나 핸들러는 ADK에서도 작동합니다.
- **계층적 로거:** 로거는 모듈 경로에 따라 계층적으로 이름이 지정됩니다(예: `google_adk.google.adk.agents.llm_agent`). 이를 통해 프레임워크의 어느 부분에서 로그를 생성할지 세밀하게 제어할 수 있습니다.
- **사용자 설정:** 프레임워크 자체는 로깅을 설정하지 않습니다. 애플리케이션의 진입점에서 원하는 로깅 설정을 구성하는 것은 프레임워크를 사용하는 개발자의 책임입니다.

## 로깅 설정 방법

메인 애플리케이션 스크립트(예: `main.py`)에서 에이전트를 초기화하고 실행하기 전에 로깅을 설정할 수 있습니다. 가장 간단한 방법은 `logging.basicConfig`를 사용하는 것입니다.

### 설정 예시

`DEBUG` 수준 메시지를 포함한 상세 로깅을 활성화하려면 스크립트 상단에 다음 코드를 추가하세요.

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# 여기에 ADK 에이전트 코드 작성...
# from google.adk.agents import LlmAgent
# ...
```

### ADK CLI를 사용한 로깅 설정

ADK에 내장된 웹 서버나 API 서버를 사용하여 에이전트를 실행할 때, 명령줄에서 직접 로그 상세 수준을 쉽게 제어할 수 있습니다. `adk web`, `adk api_server`, `adk deploy cloud_run` 명령어 모두 `--log_level` 옵션을 지원합니다.

이를 통해 에이전트의 소스 코드를 수정하지 않고도 편리하게 로깅 수준을 설정할 수 있습니다.

> **참고:** 명령줄 설정은 ADK 로거에 대해 프로그래밍 방식의 설정(예: `logging.basicConfig`)보다 항상 우선합니다. 프로덕션 환경에서는 `INFO` 또는 `WARNING`을 사용하고, 문제 해결 시에만 `DEBUG`를 활성화하는 것이 좋습니다.

**`adk web` 사용 예시:**

`DEBUG` 수준 로깅으로 웹 서버를 시작하려면 다음을 실행하세요.

```bash
adk web --log_level DEBUG path/to/your/agents_dir
```

`--log_level` 옵션에서 사용할 수 있는 로그 수준은 다음과 같습니다.

- `DEBUG`
- `INFO` (기본값)
- `WARNING`
- `ERROR`
- `CRITICAL`

> `-v` 또는 `--verbose`를 `--log_level DEBUG`의 단축 명령어로 사용할 수도 있습니다.
>
> ```bash
> adk web -v path/to/your/agents_dir
> ```

### 로그 수준

ADK는 표준 로그 수준을 사용하여 메시지를 분류합니다. 설정된 수준에 따라 기록되는 정보가 결정됩니다.

| 수준 | 설명 | 기록되는 정보 유형 |
| :--- | :--- | :--- |
| **`DEBUG`** | **디버깅에 필수적입니다.** 세밀한 진단 정보를 위한 가장 상세한 수준입니다. | <ul><li>**전체 LLM 프롬프트:** 시스템 지침, 대화 기록, 도구를 포함하여 언어 모델에 전송된 전체 요청.</li><li>서비스로부터의 상세한 API 응답.</li><li>내부 상태 전환 및 변수 값.</li></ul> |
| **`INFO`** | 에이전트의 라이프사이클에 대한 일반 정보입니다. | <ul><li>에이전트 초기화 및 시작.</li><li>세션 생성 및 삭제 이벤트.</li><li>도구의 이름과 인자를 포함한 도구 실행.</li></ul> |
| **`WARNING`** | 잠재적인 문제나 사용 중단된(deprecated) 기능 사용을 나타냅니다. 에이전트는 계속 작동하지만 주의가 필요할 수 있습니다. | <ul><li>사용 중단된 메서드 또는 파라미터 사용.</li><li>시스템이 복구한 심각하지 않은 오류.</li></ul> |
| **`ERROR`** | 작업 완료를 막는 심각한 오류입니다. | <ul><li>외부 서비스(예: LLM, 세션 서비스)에 대한 API 호출 실패.</li><li>에이전트 실행 중 처리되지 않은 예외.</li><li>설정 오류.</li></ul> |

> **참고:** 프로덕션 환경에서는 `INFO` 또는 `WARNING`을 사용하는 것이 좋습니다. `DEBUG` 로그는 매우 장황하고 민감한 정보를 포함할 수 있으므로, 문제를 적극적으로 해결할 때만 `DEBUG`를 활성화하세요.

## 로그 읽기 및 이해하기

`basicConfig` 예제의 `format` 문자열은 각 로그 메시지의 구조를 결정합니다.

다음은 샘플 로그 항목입니다.

```text
2025-07-08 11:22:33,456 - DEBUG - google_adk.google.adk.models.google_llm - LLM Request: contents { ... }
```

| 로그 세그먼트                   | 포맷 지정자     | 의미                                           |
| ------------------------------- | ---------------- | ---------------------------------------------- |
| `2025-07-08 11:22:33,456`       | `%(asctime)s`    | 타임스탬프                                     |
| `DEBUG`                         | `%(levelname)s`  | 심각도 수준                                    |
| `google_adk.models.google_llm`  | `%(name)s`       | 로거 이름 (로그를 생성한 모듈)                 |
| `LLM Request: contents { ... }` | `%(message)s`    | 실제 로그 메시지                               |

로거 이름을 읽으면 즉시 로그의 출처를 파악하고 에이전트 아키텍처 내에서 해당 로그의 컨텍스트를 이해할 수 있습니다.

## 로그를 사용한 디버깅: 실용 예제

**시나리오:** 에이전트가 예상된 출력을 생성하지 않아 LLM으로 전송되는 프롬프트가 잘못되었거나 정보가 누락된 것으로 의심됩니다.

**단계:**

1.  **DEBUG 로깅 활성화:** `main.py`에서 설정 예제와 같이 로깅 수준을 `DEBUG`로 설정합니다.

    ```python
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    ```

2.  **에이전트 실행:** 평소처럼 에이전트의 작업을 실행합니다.

3.  **로그 검사:** 콘솔 출력에서 `google.adk.models.google_llm` 로거가 보낸 `LLM Request:`로 시작하는 메시지를 찾습니다.

    ```log
    ...
    2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm - Sending out request, model: gemini-2.0-flash, backend: GoogleLLMVariant.GEMINI_API, stream: False
    2025-07-10 15:26:13,778 - DEBUG - google_adk.google.adk.models.google_llm - 
    LLM Request:
    -----------------------------------------------------------
    System Instruction:

          You roll dice and answer questions about the outcome of the dice rolls.
          You can roll dice of different sizes.
          ...
        

    You are an agent. Your internal name is "hello_world_agent".

    The description about you is "hello world agent that can roll a dice of 8 sides and check prime numbers."
    -----------------------------------------------------------
    Contents:
    {"parts":[{"text":"Roll a 6 sided dice"}],"role":"user"}
    {"parts":[{"function_call":{"args":{"sides":6},"name":"roll_die"}}],"role":"model"}
    {"parts":[{"function_response":{"name":"roll_die","response":{"result":2}}}],"role":"user"}
    -----------------------------------------------------------
    Functions:
    roll_die: {'sides': {'type': <Type.INTEGER: 'INTEGER'>}} 
    check_prime: {'nums': {'items': {'type': <Type.INTEGER: 'INTEGER'>}, 'type': <Type.ARRAY: 'ARRAY'>}} 
    -----------------------------------------------------------

    2025-07-10 15:26:13,779 - INFO - google_genai.models - AFC is enabled with max remote calls: 10.
    2025-07-10 15:26:14,309 - INFO - google_adk.google.adk.models.google_llm - 
    LLM Response:
    -----------------------------------------------------------
    Text:
    I have rolled a 6 sided die, and the result is 2.
    ...
    ```

4.  **프롬프트 분석:** 기록된 요청의 `System Instruction`, `contents`, `functions` 섹션을 검토하여 다음을 확인할 수 있습니다.
    -   시스템 지침이 올바른가?
    -   대화 기록(`user` 및 `model` 턴)이 정확한가?
    -   가장 최근의 사용자 쿼리가 포함되어 있는가?
    -   올바른 도구가 모델에 제공되고 있는가?
    -   모델이 도구를 올바르게 호출하는가?
    -   모델이 응답하는 데 시간이 얼마나 걸리는가?

이 상세한 출력을 통해 잘못된 프롬프트 엔지니어링부터 도구 정의 문제에 이르기까지 광범위한 문제를 로그 파일에서 직접 진단할 수 있습니다.