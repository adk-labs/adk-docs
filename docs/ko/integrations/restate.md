---
catalog_title: Restate
catalog_description: 내구성 세션과 사람 승인 기반의 복원력 있는 에이전트 실행/오케스트레이션
catalog_icon: /adk-docs/integrations/assets/restate.svg
---

# ADK용 Restate 플러그인

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Restate](https://restate.dev)는 ADK 에이전트를 본질적으로 복원력 있고 견고한
시스템으로 만들어주는 durable execution 엔진입니다. 지속 세션,
사람 승인용 pause/resume, 복원력 있는 멀티 에이전트 오케스트레이션,
안전한 버저닝, 전체 실행에 대한 관측/제어 기능을 제공합니다.
모든 LLM 호출과 도구 실행이 저널링되므로 실패가 발생해도
에이전트는 정확히 중단 지점부터 복구합니다.

## 사용 사례

Restate 플러그인은 에이전트에 다음 기능을 제공합니다:

- **Durable execution**: 진행 상태를 잃지 않습니다. 에이전트가 크래시 나도
  자동 재시도/복구로 정확히 중단 지점부터 이어집니다.
- **사람 개입(Human-in-the-loop) pause/resume**: 사람 승인 전까지
  며칠/몇 주 동안 실행을 중지하고, 같은 지점에서 다시 시작할 수 있습니다.
- **Durable state**: 내장 세션 관리로 에이전트 메모리와 대화 히스토리가
  재시작 후에도 유지됩니다.
- **관측성과 작업 제어**: 에이전트가 수행한 작업을 정확히 확인하고,
  언제든 실행을 중지/일시정지/재개할 수 있습니다.
- **복원력 있는 멀티 에이전트 오케스트레이션**: 여러 에이전트 간 워크플로를
  병렬 실행으로 복원력 있게 운영할 수 있습니다.
- **안전한 버저닝**: immutable deployment 기반으로
  진행 중 실행을 깨지 않고 새 버전을 배포할 수 있습니다.

## 사전 준비 사항

- Python 3.12+
- [Gemini API key](https://aistudio.google.com/app/api-keys)

아래 예시를 실행하려면 추가로 다음이 필요합니다:

- [uv](https://docs.astral.sh/uv/) (Python 패키지 관리자)
- [Docker](https://docs.docker.com/get-docker/) (또는
  Restate 서버용 [Brew/npm/binary](https://docs.restate.dev/develop/local_dev#running-restate-server--cli-locally))

## 설치

Restate Python SDK 설치:

```bash
pip install "restate-sdk[serde]"
```

## 에이전트와 함께 사용

다음 단계에 따라 durable agent를 실행하고 Restate UI에서 실행 저널을 확인하세요:

1. **[restate-google-adk-example repository](https://github.com/restatedev/restate-google-adk-example)를 clone하고 예시 디렉터리로 이동**

    ```bash
    git clone https://github.com/restatedev/restate-google-adk-example.git
    cd restate-google-adk-example/examples/hello-world
    ```

2. **Gemini API 키 export**

    ```bash
    export GOOGLE_API_KEY=your-api-key
    ```

3. **weather agent 시작**

    ```bash
    uv run .
    ```

4. **다른 터미널에서 Restate 시작**

    ```bash
    docker run --name restate --rm -p 8080:8080 -p 9070:9070 -d \
      --add-host host.docker.internal:host-gateway \
      docker.restate.dev/restatedev/restate:latest
    ```

    다른 설치 방법: [Brew, npm, binary
    downloads](https://docs.restate.dev/develop/local_dev#running-restate-server--cli-locally)

5. **에이전트 등록**

    `localhost:9070`에서 Restate UI를 열고 에이전트 deployment를 등록합니다
    (예: `http://host.docker.internal:9080`):

    ![Restate registration](./assets/restate-registration.png)

    !!! tip "안전한 버저닝"

        Restate는 각 deployment를 immutable snapshot으로 등록합니다.
        새 버전을 배포하면, 진행 중인 실행은 원래 deployment에서 완료되고
        새 요청은 최신 버전으로 라우팅됩니다.
        자세한 내용은
        [version-aware routing](https://docs.restate.dev/services/versioning)을 참조하세요.

6. **에이전트에 요청 전송**

    Restate UI에서 **WeatherAgent**를 선택하고 **Playground**에서
    요청을 전송합니다:

    ![Send request in the UI](./assets/restate-request.png)

    !!! tip "Durable 세션과 재시도"

        이 요청은 Restate를 거치며 에이전트로 전달되기 전에 영속화됩니다.
        각 세션(여기서는 `session-1`)은 격리되고 상태를 가지며 durable합니다.
        실행 중 에이전트가 크래시 나면 Restate가 자동으로 재시도하고,
        마지막 저널링 단계부터 진행을 잃지 않고 재개합니다.

7. **실행 저널 점검**

    **Invocations** 탭을 클릭한 뒤 invocation을 선택하면
    실행 저널을 볼 수 있습니다:

    ![Restate journal in the UI](./assets/restate-journal.png)

    !!! tip "에이전트 실행 전체 제어"

        모든 LLM 호출과 도구 실행이 저널에 기록됩니다.
        UI에서 실행을 일시정지, 재개, 임의 중간 단계에서 재시작,
        또는 종료할 수 있습니다. **State** 탭에서 현재 세션 데이터를 확인하세요.

## 기능

Restate 플러그인은 ADK 에이전트에 다음 기능을 제공합니다:

| Capability | Description |
| --- | --- |
| Durable tool execution | `restate_object_context().run_typed()`로 도구 로직을 감싸 자동 재시도/복구 |
| Human-in-the-loop | 외부 신호(예: 사람 승인)까지 `restate_object_context().awakeable()`로 실행 일시정지 |
| Persistent sessions | `RestateSessionService()`가 에이전트 메모리/대화 상태를 durable하게 저장 |
| Durable LLM calls | `RestatePlugin()`이 LLM 호출을 저널링하고 자동 재시도 |
| Multi-agent communication | `restate_object_context().service_call()`로 durable cross-agent HTTP 호출 |
| Parallel execution | `restate.gather()`로 도구/에이전트를 동시 실행하고 결정론적으로 복구 |

## 추가 리소스

- [Restate ADK example repository](https://github.com/restatedev/restate-google-adk-example) - 사람 승인 포함 claims processing 등 실행 가능한 예제
- [Restate ADK tutorial](https://docs.restate.dev/tour/google-adk) - Restate와 ADK로 에이전트 개발 워크스루
- [Restate AI documentation](https://docs.restate.dev/ai) - durable AI agent 패턴 전체 레퍼런스
- [Restate SDK on PyPI](https://pypi.org/project/restate-sdk/) - Python 패키지
