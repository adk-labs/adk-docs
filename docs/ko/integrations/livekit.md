---
catalog_title: LiveKit
catalog_description: 라이브 음성 에이전트를 WebRTC 룸 또는 전화 통화에 연결합니다
catalog_icon: /integrations/assets/livekit.png
catalog_tags: ["connectors"]
---

# ADK용 LiveKit 러너

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.9.0</span><span class="lst-preview">실험적 기능</span>
</div>

ADK는 WebRTC 및 SIP 전화 통신을 위한 오픈 소스 플랫폼인 [LiveKit](https://livekit.io/)을 통해 라이브 에이전트를 제공할 수 있도록 `LiveKitRunner` 클래스를 제공합니다. 이 통합은 오디오 및 비디오 캡처, 재생, 끼어들기(barge-in), 자막, 통화 제어를 처리하는 전송 어댑터 역할을 하므로, 에이전트 코드를 변경하지 않고도 브라우저, 전화, 게임 클라이언트에서 ADK 에이전트에 접근할 수 있습니다.

## 사용 사례

LiveKit은 브라우저 앱, 모바일 앱, SIP 전화 통화, 게임 및 몰입형 클라이언트 등 다양한 사용 사례에 활용할 수 있습니다.

### 브라우저 및 모바일 앱

에이전트는 일반 참가자(participant)로 룸에 참여하므로 모든 LiveKit 클라이언트 SDK가 에이전트와 통신할 수 있습니다. 커넥터는 LiveKit 자체 컴포넌트가 바인딩되는 채널에 자막과 발화 상태를 게시하므로, 별도의 추가 연결 작업 없이도 해당 컴포넌트가 ADK 에이전트와 연동됩니다:

| LiveKit 리소스 | ADK 에이전트가 얻는 이점 |
| :--- | :--- |
| [클라이언트 SDK](https://docs.livekit.io/transport/) | Browser, Swift, Android, Flutter, React Native, Unity, C++, Rust, ESP32 |
| [UI 컴포넌트](https://github.com/orgs/livekit/repositories?q=components) | React, SwiftUI, Compose, Flutter용 사전 빌드된 음성 어시스턴트 위젯 |
| [스타터 앱](https://github.com/livekit-examples) | 플랫폼별 작동 가능한 샘플 앱 및 프론트엔드 없이 에이전트와 대화할 수 있는 Agents Playground |

### 전화 통화

SIP 발신자는 일반적인 LiveKit 참가자이므로, [인바운드 트렁크(inbound trunk)](https://docs.livekit.io/telephony/accepting-calls/inbound-trunk/) 및 [디스패치 규칙(dispatch rule)](https://docs.livekit.io/telephony/accepting-calls/dispatch-rule/)이 워커를 가리키도록 설정하면 전화 통화가 에이전트에 연결됩니다.

발신자 신원은 발신자가 말하기 전에 ADK 세션 상태에 저장되므로 함수 도구는 다른 상태 값과 마찬가지로 이를 읽을 수 있습니다:

```python
from google.adk.tools.tool_context import ToolContext

async def greet_by_account(tool_context: ToolContext) -> str:
  """발신자를 확인한 후 인사를 건넵니다."""
  number = tool_context.state.get("livekit_caller_phone_number")  # '+15105550100'
  if not number:
    return "I could not see the number you are calling from."
  return await crm.lookup(number)  # 자체 고객 조회 로직
```

커넥터는 키패드 입력을 단일 턴으로 버퍼링하므로, 6자리 계정 번호가 6번의 중단(interruption) 대신 하나의 입력으로 도착합니다.

### 게임 및 몰입형 클라이언트

LiveKit의 [Unity SDK](https://github.com/livekit/client-sdk-unity)는 LiveKit Cloud 또는 자체 호스팅 서버를 기반으로 Unity 앱에 실시간 오디오, 비디오, 데이터 채널을 추가합니다. ADK 에이전트를 룸에 배치하면 플레이어는 음성 기반 NPC 또는 게임 내 어시스턴트처럼 가상 세계에 영향을 미치는 캐릭터와 대화할 수 있습니다:

```python
from google.adk.integrations.livekit import current_call
from google.adk.tools.tool_context import ToolContext

async def open_the_door(door_id: str, tool_context: ToolContext) -> str:
  """게임 월드 내의 문을 엽니다."""
  call = current_call(tool_context)
  return await call.perform_rpc(method="open_door", payload=door_id)
```

클라이언트가 반환하는 모든 내용은 모델이 서술하는 도구 결과가 되므로, 에이전트는 실제로 발생한 상황을 설명할 수 있습니다. Unity 클라이언트에서는 하나의 RPC 메서드만 등록하면 되며, 대화, 도구 호출, 세션 관리는 ADK가 처리합니다.

## 시작하기

- `livekit` 엑스트라가 포함된 [ADK](https://adk.dev) >= 2.9.0.
- [라이브 모델](../live/models.md)을 위한 인증 정보.
- 자체 호스팅 또는 LiveKit Cloud 상의 LiveKit 서버. 둘 다 동일한 API를 제공하므로 동일한 워커 코드가 두 환경 모두에서 실행됩니다. 로컬 개발의 경우 `livekit-server --dev`를 실행합니다.
- 환경 변수로 설정된 `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`.

```bash
pip install "google-adk[livekit]" "livekit-agents>=1.4"
```

기존에 작성된 에이전트에서 시작합니다. `LiveKitToolset()`을 추가하면 발신자 통화 종료 또는 전달과 같은 통화 제어 기능이 제공됩니다. 이 툴셋은 통화가 있을 때만 활성화되므로 `adk web`에서도 에이전트가 그대로 실행됩니다:

```python
from google.adk.agents import Agent
from google.adk.integrations.livekit import LiveKitToolset
from google.adk.runners import InMemoryRunner

root_agent = Agent(
    model="gemini-live-2.5-flash-native-audio",
    name="support_agent",
    instruction="You help customers troubleshoot their home internet.",
    tools=[check_line_status, LiveKitToolset()],  # check_line_status는 자체 도구입니다
)
runner = InMemoryRunner(agent=root_agent, app_name="support")
```

에이전트를 연결하려면 러너에 연결된 룸을 전달합니다. 프로덕션 환경에서는 통화당 한 번 LiveKit이 디스패치하는 워커를 실행하며, 동일한 코드로 브라우저와 전화를 모두 지원합니다.

```python
from google.adk.integrations.livekit import LiveKitRunner
from livekit.agents import AgentServer
from livekit.agents import cli
from livekit.agents import JobContext

server = AgentServer()


@server.rtc_session(agent_name="support")
async def entrypoint(ctx: JobContext) -> None:
  """디스패치된 통화를 ADK 에이전트로 연결(브릿지)합니다."""
  await ctx.connect()
  # LiveKit에는 ADK 사용자 또는 세션 ID가 없습니다. 샘플에서는 작업 메타데이터에서 이를 읽습니다.
  await LiveKitRunner(
      runner=runner, room=ctx.room, user_id="live-user", session_id=ctx.room.name
  ).start()


if __name__ == "__main__":
  cli.run_app(server)
```

## 워커 배포

워커는 LiveKit 서버로 아웃바운드 연결을 설정하고 동일한 연결을 통해 디스패치된 작업을 수신하므로, 아웃바운드 네트워크 액세스만 필요하며 퍼블릭 주소나 부하 분산 장치(로드 밸런서)는 필요하지 않습니다. 그 외에는 일반적인 ADK 컨테이너와 동일하며 다른 ADK 에이전트와 같은 방식으로 배포됩니다. 엔트리포인트가 워커 모듈을 가리키도록 설정하세요:

```dockerfile
CMD ["python", "-m", "support_agent.livekit_worker", "start"]
```

[Agents CLI](../get-started/agents-cli.md)는 `pyproject.toml`의 `deployment_target`에 따라 이 컨테이너를 Agent Runtime, Cloud Run, GKE에 배포합니다. [Agents CLI로 배포](../deploy/agent-runtime/agents-cli.md)를 참조하거나, [Cloud Run](../deploy/cloud-run.md) 또는 [GKE](../deploy/gke.md)에 수동으로 배포하세요.

Cloud Run은 `$PORT`를 프로빙하는 반면 워커는 고정 포트에서 헬스 엔드포인트를 제공하므로 두 포트를 일치시켜야 합니다. 서버를 생성할 때 환경 변수에서 포트를 읽도록 구성합니다:

```python
import os

server = AgentServer(port=int(os.environ["PORT"]))
```

프로덕션에서 워커가 사용하는 포트가 8081이므로 `--port=8081`로 배포해도 동일하게 동작합니다. 또한 워커는 통화 사이에 유휴(idle) 상태를 유지하므로 디스패치를 계속 수락할 수 있도록 `--no-cpu-throttling` 및 `--min-instances=1` 옵션으로 실행하세요.

디스패치된 각 작업은 자체 프로세스에서 실행되므로 내구성 있는 [세션 서비스](../sessions/index.md)를 사용하세요. `InMemoryRunner` 클래스는 통화 간에 아무것도 유지하지 않습니다.

## 추가 리소스

- [LiveKit 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/livekit)
- [라이브 및 음성 에이전트](../live/index.md)
- [커스텀 서버 구축](../live/custom-server.md)
- [LiveKit 공식 문서](https://docs.livekit.io/)
