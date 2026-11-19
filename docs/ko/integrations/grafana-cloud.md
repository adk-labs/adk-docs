---
catalog_title: Grafana Cloud
catalog_description: Grafana Cloud에서 메트릭, 로그, 트레이스를 쿼리하고 대시보드, 알림, 인시던트를 관리합니다
catalog_icon: /integrations/assets/grafana-cloud.png
catalog_tags: ["observability", "mcp"]
---

# ADK용 Grafana Cloud MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Grafana Cloud MCP 서버](https://grafana.com/docs/grafana-cloud/machine-learning/assistant/configure/cloud-mcp/)는
ADK 에이전트를 Grafana Cloud 관측 가능성(observability) 스택에 직접 연결합니다. 에이전트는
Prometheus 메트릭 쿼리, Loki 로그 검색, Tempo 요청 추적, 대시보드 탐색,
알림(alert) 및 인시던트(incident) 관리 등을 수행할 수 있으며 60개 이상의 도구를 사용할 수 있습니다.

이 서버는 완전 관리형(hosted)으로 제공되므로 로컬 설치, Docker 컨테이너, 서비스 계정 토큰이
필요하지 않습니다. 인증은 Grafana RBAC를 통한 사용자 범위 권한과 OAuth 2.1을
사용합니다.

## 사용 사례

- **인시던트 조사**: 메트릭, 로그, 트레이스를 쿼리하여 프로덕션 이슈를 진단합니다.
  Prometheus 알림, Loki 로그 패턴, Tempo 트레이스를 하나의 대화에서 연관 분석합니다.
- **대시보드 관리**: Grafana 대시보드를 프로그래밍 방식으로 검색, 검사, 업데이트합니다.
  패널 쿼리를 추출하고 딥 링크를 생성하며 패널을 이미지로 렌더링합니다.
- **인프라 모니터링**: 데이터 소스를 나열하고, 사용 가능한 메트릭을 탐색하며,
  레이블 값을 살펴보고 PromQL 또는 LogQL 쿼리를 대화식으로 작성합니다.
- **알림 대응**: 발생 중인 알림 규칙 확인, 온콜(on-call) 일정 확인, 인시던트 생성 또는 업데이트,
  인시던트 타임라인에 활동 메모 추가를 수행합니다.

## 사전 요구사항

- [Grafana Cloud](https://grafana.com/products/cloud/) 인스턴스 접근 권한
- 관리자가 Grafana Assistant 이용 약관에 동의해야 함
- **Assistant Cloud MCP User** 역할 또는
  `grafana-assistant-app.cloud-mcp:access` 권한 (**Editor** 역할 이상의 사용자는
  기본적으로 이 권한을 가집니다)

## 에이전트와 함께 사용

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        GRAFANA_URL = "https://<your-stack>.grafana.net"

        root_agent = Agent(
            model="gemini-flash-latest",
            name="observability_agent",
            instruction="Help users investigate issues using Grafana Cloud observability data",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.grafana.com/mcp",
                        headers={
                            "X-Grafana-URL": GRAFANA_URL,
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const GRAFANA_URL = "https://<your-stack>.grafana.net";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "observability_agent",
            instruction: "Help users investigate issues using Grafana Cloud observability data",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.grafana.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                "X-Grafana-URL": GRAFANA_URL,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

`<your-stack>`을 Grafana Cloud 스택 이름으로 바꿉니다. `X-Grafana-URL` 헤더는
선택 사항이지만, OAuth 승인 중 URL 입력 단계를 건너뛰고 동의 페이지로 바로
리디렉션하므로 사용하는 것이 좋습니다.

!!! note

    에이전트가 처음 연결되면 브라우저에서 연결 승인을 요청받습니다.
    OAuth 토큰은 1시간 동안 유효하며 30일 동안 자동으로 갱신됩니다.

## 구성

Grafana Cloud MCP 서버는 읽기 및 쓰기 접근 범위(scope)를 지원합니다.

- **읽기 권한 (Read access)**: 대시보드, 알림, 인시던트를 조회하고 데이터 소스를 쿼리합니다. 항상
  사용할 수 있습니다.
- **쓰기 권한 (Write access)**: 대시보드, 알림, 인시던트를 생성하고 수정합니다. OAuth 동의
  단계에서 쓰기 권한을 부여하거나 보류할 수 있습니다.

에이전트가 데이터 쿼리만 필요로 한다면 최소 권한(least-privilege) 구성을 위해 승인 과정에서
쓰기 권한을 거부하세요.

## 사용 가능한 도구

### 검색 및 탐색

도구 | 설명
---- | -----------
`search_dashboards` | 쿼리 문자열로 대시보드를 검색합니다
`search_folders` | 쿼리 문자열로 폴더를 검색합니다
`generate_deeplink` | 대시보드, 패널, Explore 쿼리를 위한 딥 링크 URL을 생성합니다

### 대시보드

도구 | 설명 | 권한
---- | ----------- | ------
`get_dashboard_by_uid` | UID로 전체 대시보드 JSON을 조회합니다 | 읽기
`get_dashboard_summary` | 대시보드의 간략한 요약을 가져옵니다 | 읽기
`get_dashboard_property` | JSONPath를 사용해 대시보드의 특정 부분을 추출합니다 | 읽기
`get_dashboard_panel_queries` | 템플릿 변수 치환이 적용된 패널 쿼리를 조회합니다 | 읽기
`update_dashboard` | 대시보드를 생성하거나 업데이트합니다 | 쓰기
`create_folder` | Grafana 폴더를 생성합니다 | 쓰기

### 데이터 소스

도구 | 설명
---- | -----------
`list_datasources` | 선택적 타입 필터링과 함께 구성된 모든 데이터 소스를 나열합니다
`get_datasource` | UID 또는 이름으로 데이터 소스의 상세 정보를 조회합니다

### Prometheus

도구 | 설명
---- | -----------
`list_prometheus_metric_names` | 정규식 필터링과 페이지네이션으로 사용 가능한 메트릭을 탐색합니다
`list_prometheus_metric_metadata` | 현재 스크레이핑된 메트릭의 메타데이터를 나열합니다
`list_prometheus_label_names` | 선택적 시리즈 셀렉터와 시간 범위로 레이블 이름을 나열합니다
`list_prometheus_label_values` | 특정 레이블의 값을 가져옵니다
`query_prometheus` | PromQL 즉시(instant) 또는 범위(range) 쿼리를 실행합니다
`query_prometheus_histogram` | 히스토그램 백분위수를 쿼리합니다

### Loki

도구 | 설명
---- | -----------
`list_loki_label_names` | 로그에서 사용 가능한 레이블 이름을 나열합니다
`list_loki_label_values` | 특정 레이블의 고유 값을 가져옵니다
`query_loki_logs` | 로그 항목 또는 메트릭 값에 대한 LogQL 쿼리를 실행합니다
`query_loki_stats` | 로그 스트림 통계를 가져옵니다
`query_loki_patterns` | 일반적인 로그 패턴을 감지하고 분석합니다

### Tempo

도구 | 설명
---- | -----------
`tempo_traceql-search` | TraceQL로 트레이스를 검색합니다
`tempo_get-trace` | ID로 트레이스를 조회합니다
`tempo_get-attribute-names` | 사용 가능한 트레이스 속성을 탐색합니다
`tempo_get-attribute-values` | 트레이스 속성 값을 가져옵니다
`tempo_traceql-metrics-instant` | 즉시(instant) TraceQL 메트릭 쿼리를 실행합니다
`tempo_traceql-metrics-range` | 범위(range) TraceQL 메트릭 쿼리를 실행합니다

### Pyroscope

도구 | 설명
---- | -----------
`list_pyroscope_label_names` | 프로파일에서 사용 가능한 레이블 이름을 나열합니다
`list_pyroscope_label_values` | 특정 레이블의 값을 나열합니다
`list_pyroscope_profile_types` | 사용 가능한 프로파일 타입을 나열합니다
`query_pyroscope` | Pyroscope의 프로파일 또는 메트릭을 쿼리합니다

### 알림 (Alerting)

도구 | 설명 | 권한
---- | ----------- | ------
`alerting_manage_rules` | 알림 규칙을 나열, 필터링, 생성, 업데이트합니다 | 읽기 / 쓰기
`alerting_manage_routing` | 알림 정책, 연락처(contact point), 시간 간격을 확인합니다 | 읽기

### 인시던트 (Incidents)

도구 | 설명 | 권한
---- | ----------- | ------
`list_incidents` | 선택적 상태 필터링으로 인시던트를 나열합니다 | 읽기
`get_incident` | ID로 전체 인시던트 상세 정보를 가져옵니다 | 읽기
`create_incident` | 새 인시던트를 생성합니다 | 쓰기
`add_activity_to_incident` | 인시던트 타임라인에 메모를 추가합니다 | 쓰기

### OnCall

도구 | 설명
---- | -----------
`list_oncall_schedules` | 선택적 팀 필터링으로 온콜 일정을 나열합니다
`get_oncall_shift` | 상세 근무 교대(shift) 정보를 가져옵니다
`get_current_oncall_users` | 일정에서 현재 온콜 담당 사용자를 가져옵니다
`list_oncall_teams` | OnCall 팀을 나열합니다
`list_oncall_users` | 선택적 필터링으로 OnCall 사용자를 나열합니다
`list_alert_groups` | 상태, 팀, 시간 범위, 레이블로 필터링하여 알림 그룹을 나열합니다

### 추가 도구

도구 | 설명 | 권한
---- | ----------- | ------
`get_panel_image` | 대시보드 패널을 PNG 이미지로 렌더링합니다 | 읽기
`describe_infrastructure` | 토폴로지와 의존성을 포함한 서비스 그룹 요약을 조회합니다 | 읽기
`get_annotations` | 대시보드, 시간 범위, 태그로 필터링한 어노테이션을 가져옵니다 | 읽기
`create_annotation` | 대시보드 또는 패널에 새 어노테이션을 생성합니다 | 쓰기
`query_clickhouse` | ClickHouse 데이터 소스에 SQL 쿼리를 실행합니다 | 읽기
`query_cloudwatch` | AWS CloudWatch 메트릭을 쿼리합니다 | 읽기
`query_elasticsearch` | Elasticsearch 데이터 소스에 검색을 실행합니다 | 읽기

## 셀프호스팅 Grafana

셀프호스팅 Grafana 인스턴스에는 오픈 소스
[Grafana MCP 서버](https://github.com/grafana/mcp-grafana)를 대신 사용하세요. 이
서버는 로컬에서 실행되며 서비스 계정 토큰을 사용해 모든 Grafana 인스턴스에 연결합니다.

## 추가 리소스

- [Grafana Cloud MCP 서버 문서](https://grafana.com/docs/grafana-cloud/machine-learning/assistant/configure/cloud-mcp/)
- [Grafana Cloud](https://grafana.com/products/cloud/)
