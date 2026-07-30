---
catalog_title: e2a
catalog_description: 사람이 검토하는 승인 절차를 갖춘 AI 에이전트용 인증 이메일 게이트웨이
catalog_icon: /integrations/assets/e2a.png
catalog_tags: ["mcp"]
---

# ADK용 e2a MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[e2a MCP Server](https://github.com/tokencanopy/e2a/tree/main/mcp)는 ADK 에이전트를 AI 에이전트 전용으로 구축된 인증 이메일 게이트웨이인 [e2a](https://e2a.dev)에 연결합니다. 이 통합을 통해 에이전트는 동료처럼 자연어를 사용하여 메시지를 전송, 수신 및 회신할 수 있는 고유한 이메일 수신함을 갖게 되며, 수신 메일의 SPF/DKIM/DMARC 검증 및 발신 메시지에 대한 선택적 사람 검토 보류 기능을 제공합니다.

서버는 `https://api.e2a.dev/mcp`에 호스팅되어 있으며 Streamable HTTP로 통신하므로 로컬에 설치하거나 실행할 필요가 없습니다.

## 사용 사례

- **에이전트에 고유한 수신함 부여**: 전용 이메일 주소(예: `support-bot@your-domain.com`)를 프로비저닝하여 에이전트가 팀원처럼 메일을 보내고 받을 수 있도록 합니다.

- **인증된 수신 메일**: 모든 수신 메시지에는 SPF, DKIM 및 DMARC 증거가 전달되므로 에이전트는 콘텐츠에 대해 조치를 취하기전에 발신자가 주장하는 사람인지 확인할 수 있습니다.

- **사람 참여(Human-in-the-loop) 검토**: 검토 보류 기능을 켜면 사람이 승인할 때까지 발신 메시지가 `pending_review` 상태로 보류됩니다. 필요한 경우 전송 전에 제목, 본문 또는 수신자를 직접 수정할 수 있습니다.

- **스레드 대화 자동화**: `In-Reply-To` 및 `References` 헤더가 보존된 상태로 답장하므로 수신자의 메일 클라이언트에서 여러 턴에 걸쳐 대화 스레드가 유지됩니다.

## 전제 조건

- 무료 [e2a 계정](https://e2a.dev) 및 대시보드의 API 키

## 에이전트와 함께 사용

=== "Python"

    === "원격 MCP 서버"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import (
            StreamableHTTPConnectionParams,
        )

        E2A_API_KEY = "YOUR_E2A_API_KEY"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="e2a_agent",
            instruction=(
                "You manage email through the e2a tools. Call whoami once to "
                "learn your identity and inbox address. Use list_messages and "
                "get_message to read; use reply_to_message when replying to an "
                "existing thread (it preserves In-Reply-To and References), and "
                "send_message only to start a new thread. Both 'accepted' and "
                "'pending_review' are successful outcomes — never re-send after "
                "either one."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://api.e2a.dev/mcp",
                        headers={"Authorization": f"Bearer {E2A_API_KEY}"},
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "원격 MCP 서버"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const E2A_API_KEY = "YOUR_E2A_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "e2a_agent",
            instruction:
                "You manage email through the e2a tools. Call whoami once to " +
                "learn your identity and inbox address. Use list_messages and " +
                "get_message to read; use reply_to_message when replying to an " +
                "existing thread (it preserves In-Reply-To and References), and " +
                "send_message only to start a new thread. Both 'accepted' and " +
                "'pending_review' are successful outcomes — never re-send after " +
                "either one.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://api.e2a.dev/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${E2A_API_KEY}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! tip "프로덕션 환경에서는 툴셋을 e2a SDK와 함께 사용하세요"

    MCP 툴셋은 수신함을 모델에 전달합니다. 웹훅 서명 검증, 최소 한 번 이상 전달(at-least-once delivery) 처리, 멱등성 있는 전송 등 결정론적 부분은 [Python](https://pypi.org/project/e2a/) 또는 [TypeScript](https://www.npmjs.com/package/@e2a/sdk) SDK를 사용하여 애플리케이션 코드에 유지하세요. 아래의 ADK 웹훅 예시는 이러한 형태의 작동하는 완전한 예시입니다.

## 사용 가능한 도구

호스팅된 서버는 60개 이상의 도구를 노출합니다. 최종 권한 집합을 확인하려면 엔드포인트에 대해 `tools/list`를 호출하세요. 표시되는 도구는 키에 따라 다릅니다. 배포된 에이전트에 권장되는 **에이전트 범주 키**(`e2a_agt_…`)는 런타임 도구만 볼 수 있으며, **계정 범주 키**(`e2a_acct_…`)는 아래의 관리 도구도 함께 볼 수 있습니다.

### 런타임 — 수신함 도구

도구 | 설명
---- | -----------
`whoami` | 인증된 식별 정보(사용자, 자격 증명 범위, 요금제 및 사용 한도, 에이전트 범주 자격 증명의 경우 `agent_email`)를 반환합니다.
`get_agent` | 단일 에이전트의 전체 레코드를 가져옵니다.
`list_messages` | `direction`, `read_status`, 검색 필터 및 커서 페이지네이션을 사용하여 수신함 또는 발신함 메일을 나열합니다.
`get_message` | 단일 메시지의 전체 본문, 헤더, 첨부파일 메타데이터 및 SPF/DKIM/DMARC 검증 결과를 가져옵니다.
`get_message_lifecycle` | 단일 메시지의 재구성된 배달 히스토리를 가져옵니다.
`get_attachment` | 첨부파일 메타데이터 또는 `inline: true`인 바이트 데이터를 가져옵니다.
`send_message` | 새 이메일을 전송합니다. 검토 보류에 걸리면 `accepted` 또는 `pending_review`를 반환합니다. 둘 다 성공이므로 재전송해서는 안 됩니다.
`reply_to_message` | 스레드 내에서 답장합니다. `In-Reply-To` 및 `References`를 보존합니다.
`forward_message` | 메시지를 새 수신자에게 전달합니다.
`list_conversations` / `get_conversation` | 개별 메시지 대신 대화 스레드를 찾아봅니다.
`update_message_labels` | 메시지에 라벨을 추가하거나 제거합니다.
`delete_message` / `restore_message` | 휴지통으로 소프트 삭제하고 복원합니다.

### 관리 — 프로비저닝 및 설정

도구 | 설명
---- | -----------
`list_agents`, `create_agent`, `update_agent`, `delete_agent`, `restore_agent` | 에이전트 수신함을 관리합니다.
`get_protection`, `update_protection` | 에이전트별 스크리닝 및 검토 보류 구성을 관리합니다.
`list_domains`, `register_domain`, `get_domain`, `verify_domain`, `delete_domain` | 사용자 지정 도메인 등록 및 DNS 검증을 수행합니다.
`list_reviews`, `get_review`, `approve_review`, `reject_review` | 사람의 검토 대기열을 작업합니다.
`list_webhooks`, `create_webhook`, `update_webhook`, `delete_webhook`, `rotate_webhook_secret`, `test_webhook`, `list_webhook_deliveries` | 웹훅 구독 및 배달 히스토리를 관리합니다.
`list_events`, `get_event`, `redeliver_event` | 이벤트 로그 및 재생을 관리합니다.
`list_templates`, `create_template`, `update_template`, `delete_template`, `validate_template` | 서버 측 이메일 템플릿을 관리합니다 (베타).
`list_api_keys`, `create_api_key`, `delete_api_key` | API 키를 관리합니다.

## 구성

호스팅된 엔드포인트는 위의 `Authorization` 헤더에 전달되는 API 키 외에 별도의 환경 변수가 필요하지 않습니다. 자체 호스팅된 e2a 배포를 사용하려면 `url`을 해당 배포의 `/mcp` 엔드포인트로 변경하세요.

대화형 MCP 클라이언트는 키를 붙여넣는 대신 `https://api.e2a.dev/mcp`를 OAuth 2.1 커넥터로 추가할 수 있습니다. 메일을 수신하려면 `list_messages`를 폴링하거나 SDK의 `listen()`으로 웹소켓을 열거나(공개 URL 필요 없음), `create_webhook`으로 HTTPS 엔드포인트를 구독하세요.

## 추가 리소스

- [e2a MCP Server 소스 코드](https://github.com/tokencanopy/e2a/tree/main/mcp)
- [실행 가능한 ADK 예시](https://github.com/tokencanopy/e2a/tree/main/mcp/examples/adk)
- [ADK 웹훅 예시](https://github.com/tokencanopy/e2a/tree/main/examples/adk-cloud-webhook)
- [e2a 설명서](https://e2a.dev)
