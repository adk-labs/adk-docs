---
catalog_title: Grafana Cloud
catalog_description: Grafana Cloud에서 metric, log, trace를 query하고 dashboard, alert, incident를 관리합니다
catalog_icon: /integrations/assets/grafana-cloud.png
catalog_tags: ["observability", "mcp"]
---

# ADK용 Grafana Cloud MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Grafana Cloud MCP server](https://grafana.com/docs/grafana-cloud/machine-learning/assistant/configure/cloud-mcp/)는
ADK 에이전트를 Grafana Cloud observability stack에 직접 연결합니다. 에이전트는
Prometheus metric query, Loki log search, Tempo request trace, dashboard 탐색,
alert 및 incident 관리 등을 수행할 수 있으며 60개 이상의 도구를 사용할 수 있습니다.

이 서버는 완전히 hosted 방식으로 제공되며 로컬 설치, Docker container, service account token이
필요하지 않습니다. 인증은 Grafana RBAC를 통한 user-scoped permission과 OAuth 2.1을
사용합니다.

## 사용 사례

- **Incident 조사**: metric, log, trace를 query하여 production issue를 진단합니다.
  Prometheus alert, Loki log pattern, Tempo trace를 하나의 대화에서 연결합니다.
- **Dashboard 관리**: Grafana dashboard를 programmatically 검색, 검사, 업데이트합니다.
  panel query를 추출하고 deep link를 생성하며 panel을 image로 render합니다.
- **Infrastructure monitoring**: data source를 나열하고, 사용 가능한 metric을 발견하고,
  label value를 탐색하며 PromQL 또는 LogQL query를 대화식으로 만듭니다.
- **Alert 대응**: firing alert rule 확인, on-call schedule 확인, incident 생성 또는 업데이트,
  incident timeline에 activity note 추가를 수행합니다.

## 전제 조건

- [Grafana Cloud](https://grafana.com/products/cloud/) instance 접근 권한
- administrator가 Grafana Assistant terms and conditions를 수락해야 함
- **Assistant Cloud MCP User** role 또는
  `grafana-assistant-app.cloud-mcp:access` permission. **Editor** role 이상 사용자는
  기본적으로 이 권한을 가집니다.

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

`<your-stack>`을 Grafana Cloud stack name으로 바꿉니다. `X-Grafana-URL` header는
선택 사항이지만 OAuth authorization 중 URL 입력 단계를 건너뛰고 consent page로 바로
redirect하므로 사용하는 것이 좋습니다.

!!! note

    에이전트가 처음 연결되면 브라우저에서 connection authorization을 요청받습니다.
    OAuth token은 1시간 동안 유효하며 30일 동안 자동으로 refresh됩니다.

## 구성

Grafana Cloud MCP server는 read 및 write access scope를 지원합니다.

- **Read access**: dashboard, alert, incident를 보고 data source를 query합니다. 항상
  사용할 수 있습니다.
- **Write access**: dashboard, alert, incident를 생성하고 수정합니다. OAuth consent
  단계에서 write access를 부여하거나 보류할 수 있습니다.

에이전트가 data query만 필요로 한다면 least-privilege 구성을 위해 authorization 중
write access를 거부하세요.

## 사용 가능한 도구

### Search and navigation

Tool | Description
---- | -----------
`search_dashboards` | query string으로 dashboard를 검색합니다
`search_folders` | query string으로 folder를 검색합니다
`generate_deeplink` | dashboard, panel, Explore query를 위한 deep link URL을 생성합니다

### Dashboards

Tool | Description | Access
---- | ----------- | ------
`get_dashboard_by_uid` | UID로 complete dashboard JSON을 가져옵니다 | Read
`get_dashboard_summary` | dashboard의 compact summary를 가져옵니다 | Read
`get_dashboard_property` | JSONPath를 사용해 dashboard의 특정 부분을 추출합니다 | Read
`get_dashboard_panel_queries` | template variable substitution이 적용된 panel query를 가져옵니다 | Read
`update_dashboard` | dashboard를 생성하거나 업데이트합니다 | Write
`create_folder` | Grafana folder를 생성합니다 | Write

### Data sources

Tool | Description
---- | -----------
`list_datasources` | optional type filtering과 함께 구성된 모든 data source를 나열합니다
`get_datasource` | UID 또는 name으로 data source의 상세 정보를 가져옵니다

### Prometheus

Tool | Description
---- | -----------
`list_prometheus_metric_names` | regex filtering과 pagination으로 사용 가능한 metric을 발견합니다
`list_prometheus_metric_metadata` | 현재 scrape된 metric의 metadata를 나열합니다
`list_prometheus_label_names` | optional series selector와 time range로 label name을 나열합니다
`list_prometheus_label_values` | 특정 label의 값을 가져옵니다
`query_prometheus` | PromQL instant 또는 range query를 실행합니다
`query_prometheus_histogram` | histogram percentile을 query합니다

### Loki

Tool | Description
---- | -----------
`list_loki_label_names` | log에서 사용 가능한 label name을 나열합니다
`list_loki_label_values` | 특정 label의 unique value를 가져옵니다
`query_loki_logs` | log entry 또는 metric value에 대한 LogQL query를 실행합니다
`query_loki_stats` | log stream 통계를 가져옵니다
`query_loki_patterns` | 일반적인 log pattern을 감지하고 분석합니다

### Tempo

Tool | Description
---- | -----------
`tempo_traceql-search` | TraceQL로 trace를 검색합니다
`tempo_get-trace` | ID로 trace를 가져옵니다
`tempo_get-attribute-names` | 사용 가능한 trace attribute를 발견합니다
`tempo_get-attribute-values` | trace attribute 값을 가져옵니다
`tempo_traceql-metrics-instant` | instant TraceQL metrics query를 실행합니다
`tempo_traceql-metrics-range` | range TraceQL metrics query를 실행합니다

### Pyroscope

Tool | Description
---- | -----------
`list_pyroscope_label_names` | profile에서 사용 가능한 label name을 나열합니다
`list_pyroscope_label_values` | 특정 label의 값을 나열합니다
`list_pyroscope_profile_types` | 사용 가능한 profile type을 나열합니다
`query_pyroscope` | Pyroscope의 profile 또는 metric을 query합니다

### Alerting

Tool | Description | Access
---- | ----------- | ------
`alerting_manage_rules` | alert rule을 list, filter, create, update합니다 | Read / Write
`alerting_manage_routing` | notification policy, contact point, time interval을 확인합니다 | Read

### Incidents

Tool | Description | Access
---- | ----------- | ------
`list_incidents` | optional status filtering으로 incident를 나열합니다 | Read
`get_incident` | ID로 full incident detail을 가져옵니다 | Read
`create_incident` | 새 incident를 생성합니다 | Write
`add_activity_to_incident` | incident timeline에 note를 추가합니다 | Write

### OnCall

Tool | Description
---- | -----------
`list_oncall_schedules` | optional team filtering으로 on-call schedule을 나열합니다
`get_oncall_shift` | 상세 shift 정보를 가져옵니다
`get_current_oncall_users` | schedule에서 현재 on-call인 사용자를 가져옵니다
`list_oncall_teams` | OnCall team을 나열합니다
`list_oncall_users` | optional filtering으로 OnCall user를 나열합니다
`list_alert_groups` | state, team, time range, label로 filtering하여 alert group을 나열합니다

### Additional tools

Tool | Description | Access
---- | ----------- | ------
`get_panel_image` | dashboard panel을 PNG image로 render합니다 | Read
`describe_infrastructure` | topology와 dependency를 포함한 service group summary를 가져옵니다 | Read
`get_annotations` | dashboard, time range, tag로 filtering한 annotation을 가져옵니다 | Read
`create_annotation` | dashboard 또는 panel에 새 annotation을 생성합니다 | Write
`query_clickhouse` | ClickHouse data source에 SQL query를 실행합니다 | Read
`query_cloudwatch` | AWS CloudWatch metric을 query합니다 | Read
`query_elasticsearch` | Elasticsearch data source에 search를 실행합니다 | Read

## Self-hosted Grafana

Self-hosted Grafana instance에는 open source
[Grafana MCP server](https://github.com/grafana/mcp-grafana)를 대신 사용하세요. 이
서버는 로컬에서 실행되며 service account token을 사용해 모든 Grafana instance에 연결합니다.

## 추가 리소스

- [Grafana Cloud MCP Server Documentation](https://grafana.com/docs/grafana-cloud/machine-learning/assistant/configure/cloud-mcp/)
- [Grafana Cloud](https://grafana.com/products/cloud/)
