---
catalog_title: ADK Connector
catalog_description: 기기 간 세션 동기화를 지원하여 인기 있는 메시징 채널에 ADK 에이전트를 챗봇으로 노출하세요
catalog_icon: /integrations/assets/adk-connector.png
catalog_tags: ["connectors"]
---

# ADK Connector

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[ADK Connector](https://github.com/Harshk133/adk-connector)는 플러그 앤 플레이 방식의 툴킷으로, 모든 ADK 에이전트를 래핑하여 텔레그램(Telegram) 및 디스코드(Discord)와 같은 인기 메시징 채널에 챗봇으로 노출할 수 있도록 지원합니다. 현재 지원되는 채널의 전체 목록은 프로젝트 저장소(Repository)를 참조하세요.

몇 줄의 코드만 추가하면 로컬 개발, 테스트 단계와 실제 프로덕션 메시징 플랫폼 간의 격차를 메울 수 있으며, 데이터베이스 기반의 기기 간 세션 동기화(cross-device session synchronization)를 기본적으로 지원합니다.

## 주요 사용 사례

- **다중 채널 배포 (Multi-Channel Deployment)**: 지원되는 메시징 채널(예: 텔레그램, 디스코드)에 Python 또는 JavaScript/TypeScript로 작성된 ADK 에이전트를 즉시 챗봇으로 배포할 수 있습니다.
- **기기 간 세션 동기화 (Cross-Device Session Synchronization)**: 대화를 원활하게 전환할 수 있습니다. 텔레그램이나 디스코드에서 나눈 채팅을 로컬 ADK Web UI(`adk web`) 내에서 그대로 확인하고, 디버깅하며, 대화를 이어갈 수 있습니다.
- **탄력적인 상태 관리 (Resilient State Management)**: 세션 상태, 도구 호출, 사용자 상호작용을 기록하기 위한 비동기 SQLite 백엔드를 자동으로 구성합니다.
- **견고한 멀티 에이전트 워크플로 (Robust Multi-Agent Workflows)**: 중복 임포트(double-import) 방지 안전망과 상위 및 하위 에이전트 간의 프롬프트 컨텍스트 변수 자동 해석을 제공합니다.

## 사전 요구사항

- Python 3.10+ 또는 Node.js 18+
- Gemini API 키 (`GOOGLE_API_KEY` 환경 변수로 설정)
- 메시징 채널 인증 정보:
    - **텔레그램(Telegram)**: 텔레그램 계정 및 BotFather로부터 발급받은 봇 토큰(Bot Token)
    - **디스코드(Discord)**: 디스코드 개발자 계정, 디스코드 봇 토큰(Bot Token) 및 클라이언트 ID(Client ID)

## 설치

사용 중인 ADK 프로젝트에 따라 Python 또는 JavaScript/TypeScript용 커넥터를 설치할 수 있습니다.

=== "Python"

    ```bash
    pip install adk-connector
    ```

    데이터베이스 기반의 기기 간 세션 동기화(예: `adk web` UI)를 활성화하려면 ADK DB 컴포넌트도 함께 설치해야 합니다:

    ```bash
    pip install "google-adk[db]"
    ```

=== "JavaScript / TypeScript"

    ```bash
    npm install adk-connector-js
    ```

## 에이전트와 함께 사용하기

기존 Google ADK 에이전트를 래핑하여 메시징 채널에 실행하는 방법은 다음과 같습니다.

=== "Python (텔레그램)"

    ```python
    import os
    from dotenv import load_dotenv
    from google.adk.agents.llm_agent import Agent
    from adk_connectors.telegram import TelegramConnector

    # 환경 변수 로드
    load_dotenv()

    # 1. 표준 Google ADK 에이전트 정의
    assistant = Agent(
        model='gemini-flash-latest',
        name='my_assistant',
        instruction='You are a helpful assistant.'
    )

    if __name__ == "__main__":
        # 2. 텔레그램 봇 토큰 가져오기
        token = os.getenv("TELEGRAM_BOT_TOKEN")

        # 3. 커넥터 바인딩
        connector = TelegramConnector(
            token=token,
            agent=assistant
        )

        # 4. 폴링 시작
        connector.start()
    ```

=== "Python (디스코드)"

    ```python
    import os
    from dotenv import load_dotenv
    from google.adk.agents.llm_agent import Agent
    from adk_connectors.discord import DiscordConnector

    # 환경 변수 로드
    load_dotenv()

    # 1. 표준 Google ADK 에이전트 정의
    assistant = Agent(
        model='gemini-flash-latest',
        name='my_assistant',
        instruction='You are a helpful assistant.'
    )

    if __name__ == "__main__":
        # 2. 디스코드 봇 토큰 가져오기
        token = os.getenv("DISCORD_BOT_TOKEN")

        # 3. 커넥터 바인딩
        connector = DiscordConnector(
            token=token,
            agent=assistant
        )

        # 4. 봇 시작!
        connector.start()
    ```

=== "JavaScript / TypeScript (텔레그램)"

    ```typescript
    import { LlmAgent } from '@google/adk';
    import { TelegramConnector } from 'adk-connector-js';
    import dotenv from 'dotenv';

    dotenv.config();

    // 1. 표준 Google ADK 에이전트 정의
    export const rootAgent = new LlmAgent({
      name: 'my_assistant',
      model: 'gemini-flash-latest',
      instruction: 'You are a helpful assistant.'
    });

    // 2. 스크립트 진입점 하위에서 텔레그램 커넥터 실행
    if (import.meta.url === `file://${process.argv[1]}` || process.argv[1]?.endsWith('agent.ts')) {
      const connector = new TelegramConnector({
        token: process.env.TELEGRAM_BOT_TOKEN!,
        agent: rootAgent
      });

      connector.start();
    }
    ```

## adk web과 세션 동기화

Python 환경의 경우, 공급자별 사용자 ID를 로컬 개발 환경에 매핑하여 텔레그램 또는 디스코드 채팅 기록을 로컬 ADK Web UI와 직접 동기화할 수 있습니다.

1. 코드에서 `session_management_across_device=True`로 설정하고 사용자 ID를 전달합니다:

    === "텔레그램"

        ```python
        connector = TelegramConnector(
            token=token,
            agent=assistant,
            session_management_across_device=True,  # DB 구동 및 매핑 영속성 설정
            dev_user_id=os.getenv("TELEGRAM_USER_ID") # 이 ID를 Web UI의 "user" 네임스페이스에 동기화
        )
        ```

    === "디스코드"

        ```python
        connector = DiscordConnector(
            token=token,
            agent=assistant,
            session_management_across_device=True,  # DB 구동 및 매핑 영속성 설정
            dev_user_id=os.getenv("DISCORD_USER_ID")  # 이 ID를 Web UI의 "user" 네임스페이스에 동기화
        )
        ```

2. 봇 스크립트를 실행합니다:
   ```bash
   python agent.py
   ```
3. 별도의 터미널에서 ADK Web UI를 실행합니다:
   ```bash
   adk web .
   ```
4. `http://127.0.0.1:8000`에 접속하여 활성 대화 및 도구 실행 로그를 브라우저에서 직접 확인합니다.

## 추가 자료

- [ADK Connector GitHub 저장소](https://github.com/Harshk133/adk-connector)
- [ADK Connector Python 패키지 (PyPI)](https://pypi.org/project/adk-connector/)
- [ADK Connector JS/TS 패키지 (NPM)](https://www.npmjs.com/package/adk-connector-js)
