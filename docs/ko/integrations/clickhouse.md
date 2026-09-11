---
catalog_title: ClickHouse Cloud
catalog_description: 데이터 쿼리, 스키마 탐색, 서비스 및 비용 모니터링
catalog_tags: ["data", "mcp"]
---

# ADK용 ClickHouse Cloud MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[ClickHouse Cloud 원격 MCP 서버](https://clickhouse.com/docs/cloud/features/ai-ml/remote-mcp)는 ADK 에이전트를 사용자의 ClickHouse Cloud 서비스에 직접 연결합니다. 에이전트는 데이터베이스 및 테이블 목록 조회, 스키마 검사, 읽기 전용 SQL 쿼리 실행, 서비스·백업·ClickPipes·청구 현황 파악, 그리고 다양한 추가 도구에 접근할 수 있습니다.

이 서버는 완전 관리형(fully hosted)으로 제공되므로 로컬 설치, Docker 컨테이너, API 키 설정이 필요하지 않습니다. 인증에는 OAuth 2.0을 사용하며, 접근 권한은 인증된 사용자가 접근 권한을 가진 조직 및 서비스로 범위가 지정됩니다.

## 주요 사용 사례

- **데이터 탐색 및 분석**: 데이터베이스 및 테이블을 탐색하고, 컬럼 정의를 검사하며, 자연어로 분석용 SELECT 쿼리를 실행합니다. "최근 7일간 국가별 평균 세션 시간은 얼마인가요?"라고 질문하면 에이전트가 이를 SQL로 변환하여 실행합니다.
- **인사이트 및 보고서 생성**: 별도의 데이터 파이프라인을 구축하지 않고도 분석 결과를 요약, 시각화 또는 다운스트림 워크플로우로 가져옵니다.
- **인프라 모니터링**: 조직 내 서비스 목록 조회, 서비스 상태 및 세부정보 확인, 백업 일정 및 최근 백업 검토, 구성된 ClickPipes 확인.
- **비용 추적**: 특정 날짜 범위에 걸친 일별 엔터티별 비용 기록을 포함하여 조직의 청구 및 사용량 데이터를 조회합니다.

## 사전 요구사항

- 실행 중인 ClickHouse 인스턴스 ([ClickHouse Cloud](https://clickhouse.com/cloud) 또는 자체 호스팅)
- **로컬 MCP 서버**: [uv](https://docs.astral.sh/uv/) 설치됨 ([mcp-clickhouse](https://github.com/ClickHouse/mcp-clickhouse) 실행에 `uvx` 사용) 및 에이전트에 필요한 최소 권한을 가진 ClickHouse 사용자
- **원격 MCP 서버** (ClickHouse Cloud 전용): 서비스에 대해 원격 MCP 서버가 활성화되어 있어야 합니다. ClickHouse Cloud 콘솔에서 서비스를 열고 **Connect**를 클릭한 후, **Connect with MCP**를 선택하고 활성화(toggle on)합니다.

## 에이전트와 함께 사용

=== "Python"

    === "로컬 MCP 서버"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        clickhouse_tools = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=["mcp-clickhouse"],
                    env={
                        "CLICKHOUSE_HOST": "<your-instance>.clickhouse.cloud",
                        "CLICKHOUSE_USER": "<clickhouse-user>",
                        "CLICKHOUSE_PASSWORD": "<clickhouse-password>",
                        "CLICKHOUSE_PORT": "8443",
                    },
                ),
                timeout=60,
            )
        )

        root_agent = Agent(
            model="gemini-flash-latest",
            name="clickhouse_agent",
            instruction="Help users explore and analyze data in ClickHouse. "
            "Use the ClickHouse tools to query the data before answering. "
            "Always ground your answer in actual query results, not assumptions.",
            tools=[clickhouse_tools],
        )
        ```

        `CLICKHOUSE_HOST`를 사용자의 인스턴스 호스트 이름으로 변경합니다(ClickHouse Cloud 또는 자체 호스팅 모두 작동). 에이전트에 필요한 권한만 가진 전용 데이터베이스 사용자를 사용하세요. `default` 또는 관리자 계정 사용은 지양해야 합니다. 쿼리는 기본적으로 읽기 전용으로 실행됩니다.

    === "원격 MCP 서버"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        root_agent = Agent(
            model="gemini-flash-latest",
            name="clickhouse_agent",
            instruction="Help users explore and analyze data in ClickHouse Cloud",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.clickhouse.cloud/mcp",
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "원격 MCP 서버"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "clickhouse_agent",
            instruction: "Help users explore and analyze data in ClickHouse Cloud",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.clickhouse.cloud/mcp",
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    원격 MCP 서버를 사용하는 경우, 에이전트가 처음 연결될 때 브라우저에서 ClickHouse Cloud 자격 증명으로 로그인하여 연결을 승인하라는 메시지가 표시됩니다. 접근 권한은 사용자가 접근 권한을 가진 조직 및 서비스로 범위가 지정됩니다. 반면 로컬 MCP 서버는 OAuth 흐름 없이 환경 변수에 지정된 데이터베이스 자격 증명으로 인증합니다.

## 보안 (Safety)

원격 MCP 서버가 노출하는 모든 도구는 **읽기 전용(read-only)**입니다. 각 도구의 MCP 메타데이터에는 `readOnlyHint: true`가 표시되어 있습니다. 어떤 도구도 데이터를 수정하거나, 서비스 구성을 변경하거나, 파괴적인 작업을 수행할 수 없습니다. `run_select_query` 도구는 오직 `SELECT` 문만 허용합니다.

로컬 MCP 서버 또한 기본적으로 읽기 전용입니다. 쓰기 접근 권한을 부여하려면 명시적으로 `CLICKHOUSE_ALLOW_WRITE_ACCESS=true`를 설정해야 하며, 파괴적인 작업(DROP, TRUNCATE)에는 추가로 `CLICKHOUSE_ALLOW_DROP=true`가 필요합니다.

## 사용 가능한 도구

### 로컬 MCP 서버

도구 | 설명
---- | -----------
`run_query` | SQL 쿼리 실행 (기본적으로 읽기 전용)
`list_databases` | ClickHouse 인스턴스의 모든 데이터베이스 목록 조회
`list_tables` | 페이지네이션 및 선택적 `like`/`not_like` 필터를 사용하여 데이터베이스 내 테이블 목록 조회

### 원격 MCP 서버 (ClickHouse Cloud)

원격 서버는 아래 카테고리의 읽기 전용 도구를 제공합니다.

### 쿼리 및 스키마 탐색

도구 | 설명
---- | -----------
`run_select_query` | ClickHouse 서비스에 대해 읽기 전용 SELECT 쿼리 실행
`list_databases` | ClickHouse 서비스에서 사용 가능한 모든 데이터베이스 목록 조회
`list_tables` | 선택적 `like`/`notLike` 필터를 사용하여 컬럼 정의를 포함한 데이터베이스 내 모든 테이블 목록 조회

### 조직 (Organizations)

도구 | 설명
---- | -----------
`get_organizations` | 인증된 사용자가 접근할 수 있는 모든 ClickHouse Cloud 조직 조회
`get_organization_details` | 단일 조직의 세부정보 반환

### 서비스 (Services)

도구 | 설명
---- | -----------
`get_services_list` | ClickHouse Cloud 조직 내 모든 서비스 목록 조회
`get_service_details` | 특정 서비스의 세부정보 반환

### 백업 (Backups)

도구 | 설명
---- | -----------
`list_service_backups` | 최신순으로 서비스의 모든 백업 목록 조회
`get_service_backup_details` | 단일 백업의 세부정보 반환
`get_service_backup_configuration` | 서비스의 백업 구성(일정 및 보존 설정) 반환

### ClickPipes

도구 | 설명
---- | -----------
`list_clickpipes` | 서비스에 구성된 모든 ClickPipes 목록 조회
`get_clickpipe` | 특정 ClickPipe의 세부정보 반환

### 청구 (Billing)

도구 | 설명
---- | -----------
`get_organization_cost` | 선택적 `from_date`/`to_date` (최대 31일 범위)를 사용하여 조직의 청구 및 사용량 비용 데이터 검색

## 로컬 서버와 원격 서버 비교

|                    | 로컬 MCP 서버                                                             | 원격 MCP 서버                                                                        |
| ------------------ | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **소스**           | [mcp-clickhouse](https://github.com/ClickHouse/mcp-clickhouse) (오픈 소스) | ClickHouse Cloud 완전 관리형                                                               |
| **전송 방식**      | `uvx`를 통한 로컬 stdio                                                    | 스트리밍 가능한 HTTP (`https://mcp.clickhouse.cloud/mcp`)                                  |
| **호환성**         | 모든 ClickHouse 인스턴스 (자체 호스팅 또는 Cloud)                          | ClickHouse Cloud 서비스 전용                                                               |
| **인증**           | 환경 변수 (데이터베이스 사용자)                                            | Cloud 자격 증명을 사용하는 OAuth 2.0                                                       |
| **제공 도구**      | 3개 도구: 쿼리 및 스키마 탐색                                              | 쿼리, 스키마 탐색, 서비스 관리, 백업, ClickPipes, 청구 관련 도구                           |

## 추가 리소스

- [GitHub의 mcp-clickhouse](https://github.com/ClickHouse/mcp-clickhouse)
- [ClickHouse Cloud 원격 MCP 문서](https://clickhouse.com/docs/cloud/features/ai-ml/remote-mcp)
- [원격 MCP 설정 가이드](https://clickhouse.com/docs/products/cloud/features/ai-ml/mcp/remote-mcp)
- [ClickHouse Cloud](https://clickhouse.com/cloud)
