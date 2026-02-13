---
catalog_title: Mailgun
catalog_description: 이메일 전송, 전달 지표 추적, 메일링 리스트 관리를 수행합니다
catalog_icon: /adk-docs/integrations/assets/mailgun.png
catalog_tags: ["mcp"]
---

# ADK용 Mailgun MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Mailgun MCP Server](https://github.com/mailgun/mailgun-mcp-server)는
ADK 에이전트를 트랜잭션 이메일 서비스인 [Mailgun](https://www.mailgun.com/)과 연결합니다.
이 통합을 통해 에이전트는 자연어로 이메일 전송,
전달 지표 추적, 도메인/템플릿 관리, 메일링 리스트 처리를 수행할 수 있습니다.

## 사용 사례

- **이메일 전송/관리**: 트랜잭션 이메일 및 마케팅 이메일을 작성/전송하고,
  저장 메시지를 조회하며, 기존 메시지를 재전송합니다.

- **전달 성능 모니터링**: 전달 통계를 조회하고,
  반송 분류를 분석하며, 발신자 평판 유지를 위해 suppression 리스트를 검토합니다.

- **이메일 인프라 관리**: 도메인 DNS 구성 검증, 추적 설정 구성,
  이메일 템플릿 생성, 인바운드 라우팅 규칙 설정을 수행합니다.

## 사전 준비 사항

- [Mailgun 계정](https://www.mailgun.com/) 생성
- [Mailgun Dashboard](https://app.mailgun.com/settings/api_security)에서 API 키 생성

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        MAILGUN_API_KEY = "YOUR_MAILGUN_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="mailgun_agent",
            instruction="Help users send emails and manage their Mailgun account",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@mailgun/mcp-server",
                            ],
                            env={
                                "MAILGUN_API_KEY": MAILGUN_API_KEY,
                                # "MAILGUN_API_REGION": "eu",  # Optional: defaults to "us"
                            }
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const MAILGUN_API_KEY = "YOUR_MAILGUN_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "mailgun_agent",
            instruction: "Help users send emails and manage their Mailgun account",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@mailgun/mcp-server"],
                        env: {
                            MAILGUN_API_KEY: MAILGUN_API_KEY,
                            // MAILGUN_API_REGION: "eu",  // Optional: defaults to "us"
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

### 메시징

Tool | Description
---- | -----------
`send_email` | HTML 콘텐츠 및 첨부파일을 지원하는 이메일 전송
`get_stored_message` | 저장된 이메일 메시지 조회
`resend_message` | 이전에 보낸 메시지 재전송

### 도메인

Tool | Description
---- | -----------
`get_domain` | 특정 도메인 상세 정보 조회
`verify_domain` | 도메인 DNS 구성 검증
`get_tracking_settings` | 추적 설정(클릭, 오픈, 수신거부) 조회
`update_tracking_settings` | 도메인 추적 설정 업데이트

### 웹훅

Tool | Description
---- | -----------
`list_webhooks` | 도메인의 이벤트 웹훅 목록 조회
`create_webhook` | 새 이벤트 웹훅 생성
`update_webhook` | 기존 웹훅 업데이트
`delete_webhook` | 웹훅 삭제

### 라우트

Tool | Description
---- | -----------
`list_routes` | 인바운드 이메일 라우팅 규칙 조회
`update_route` | 인바운드 라우팅 규칙 업데이트

### 메일링 리스트

Tool | Description
---- | -----------
`create_mailing_list` | 새 메일링 리스트 생성
`manage_list_members` | 메일링 리스트 멤버 추가/삭제/업데이트

### 템플릿

Tool | Description
---- | -----------
`create_template` | 새 이메일 템플릿 생성
`manage_template_versions` | 템플릿 버전 생성/관리

### 분석 및 통계

Tool | Description
---- | -----------
`query_metrics` | 날짜 범위별 발송/사용 지표 조회
`get_logs` | 이메일 이벤트 로그 조회
`get_stats` | 도메인, 태그, 제공자, 기기, 국가별 집계 통계 조회

### Suppressions

Tool | Description
---- | -----------
`get_bounces` | 반송 이메일 주소 조회
`get_unsubscribes` | 수신 거부 이메일 주소 조회
`get_complaints` | 클레임(불만) 기록 조회
`get_allowlist` | allowlist 항목 조회

### IP

Tool | Description
---- | -----------
`list_ips` | IP 할당 정보 조회
`get_ip_pools` | 전용 IP 풀 구성 조회

### 반송 분류

Tool | Description
---- | -----------
`get_bounce_classification` | 반송 유형 및 전달 이슈 분석

## 구성

Variable | Required | Default | Description
-------- | -------- | ------- | -----------
`MAILGUN_API_KEY` | Yes | — | Mailgun API 키
`MAILGUN_API_REGION` | No | `us` | API 리전: `us` 또는 `eu`

## 추가 리소스

- [Mailgun MCP Server Repository](https://github.com/mailgun/mailgun-mcp-server)
- [Mailgun MCP Integration Guide](https://www.mailgun.com/resources/integrations/mcp-server/)
- [Mailgun Documentation](https://documentation.mailgun.com/)
