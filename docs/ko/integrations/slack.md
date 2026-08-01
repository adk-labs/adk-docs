---
catalog_title: Slack
catalog_description: 멘션, DM 및 스레드 답글에 응답하는 봇으로 에이전트를 실행합니다.
catalog_icon: /integrations/assets/slack.png
catalog_tags: ["connectors", "google"]
---

# ADK용 Slack 런너

<div class="language-support-tag"><span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span></div>

ADK는 [Socket Mode](https://api.slack.com/apis/connections/socket)를 사용하여 Slack에 에이전트를 직접 배포할 수 있는 `SlackRunner` 클래스를 제공합니다. 이 통합은 이벤트 수신, 응답 전송 및 대화 스레드 자동 관리를 처리하는 어댑터 역할을 합니다.

## 사용 사례

- **Socket Mode 배포**: 공개 HTTP 엔드포인트를 노출하지 않고 워크스페이스 이벤트를 에이전트로 라우팅합니다.
- **스레드 관리**: 다이렉트 메시지(DM) 및 중첩된 스레드 답글에서 지속적인 대화 맥락을 유지합니다.
- **이벤트 기반 트리거**: 다이렉트 메시지 또는 앱 멘션을 사용하여 에이전트 워크플로를 자동으로 활성화합니다.

## 사전 준비 사항

- [Slack API 대시보드](https://api.slack.com/apps)에서 구성된 Slack 앱. 먼저 Slack 계정에 로그인해야 합니다.
- `app_mentions:read`, `chat:write`, `im:history` 봇 토큰 범위를 가진 봇 사용자 OAuth 토큰(`xoxb-...`).
- `connections:write` 범위를 가진 웹소켓 앱 수준 토큰(`xapp-...`).

## 설치

터미널에서 다음 명령어를 실행하여 필수 Slack Socket Mode 종속 항목과 함께 ADK를 설치합니다.

```bash
pip install "google-adk[slack]"
```

## 에이전트와 함께 사용

이 예시는 에이전트를 Slack에 배포하기 위한 엔드투엔드 설정을 보여줍니다. 코어 에이전트를 구성하고 대화 기록을 관리하기 위한 인메모리 세션을 설정하며, Socket Mode와 함께 SlackRunner를 사용하여 워크스페이스에 연결하고 들어오는 이벤트를 처리합니다.

```python
import asyncio
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.integrations.slack import SlackRunner
from slack_bolt.app.async_app import AsyncApp

# 코어 에이전트 정의
root_agent = Agent(
    model="gemini-flash-latest",
    name="slack_agent",
    instruction="You are a helpful team assistant running on Slack.",
)

# Socket Mode를 통해 Slack에 연결
runner = Runner(
    app_name="slack_agent",
    agent=root_agent,
    session_service=InMemorySessionService(),
    auto_create_session=True,
)
slack_app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])
slack_runner = SlackRunner(runner, slack_app)

asyncio.run(slack_runner.start(os.environ["SLACK_APP_TOKEN"]))
```

## 추가 리소스

- [Slack API 문서](https://api.slack.com/docs)
- [PyPI의 google-adk](https://pypi.org/project/google-adk/)
