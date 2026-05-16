---
catalog_title: Grafana Cloud
catalog_description: Grafana Cloud で metric、log、trace を query し、dashboard、alert、incident を管理します
catalog_icon: /integrations/assets/grafana-cloud.png
catalog_tags: ["observability", "mcp"]
---

# ADK 向け Grafana Cloud MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Grafana Cloud MCP server](https://grafana.com/docs/grafana-cloud/machine-learning/assistant/configure/cloud-mcp/)は、
ADK エージェントを Grafana Cloud observability stack に直接接続します。エージェントは
Prometheus metric query、Loki log search、Tempo request trace、dashboard の閲覧、
alert と incident の管理などを実行でき、60 を超えるツールを利用できます。

このサーバーは完全に hosted されており、ローカルインストール、Docker container、
service account token は不要です。認証には Grafana RBAC による user-scoped permission と
OAuth 2.1 を使用します。

## ユースケース

- **Incident の調査**: metric、log、trace を query して production issue を診断します。
  Prometheus alert、Loki log pattern、Tempo trace を 1 つの会話で関連付けます。
- **Dashboard の管理**: Grafana dashboard を programmatically に検索、検査、更新します。
  panel query を抽出し、deep link を生成し、panel を image として render します。
- **Infrastructure monitoring**: data source を一覧表示し、利用可能な metric を発見し、
  label value を探索しながら PromQL または LogQL query を対話的に構築します。
- **Alert への対応**: firing alert rule の確認、on-call schedule の確認、incident の作成または更新、
  incident timeline への activity note 追加を行います。

## 前提条件

- [Grafana Cloud](https://grafana.com/products/cloud/) instance へのアクセス
- administrator が Grafana Assistant terms and conditions に同意していること
- **Assistant Cloud MCP User** role、または
  `grafana-assistant-app.cloud-mcp:access` permission。**Editor** role 以上のユーザーは
  デフォルトでこの権限を持ちます。

## エージェントでの使用

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

`<your-stack>` を Grafana Cloud stack name に置き換えます。`X-Grafana-URL` header は
任意ですが、OAuth authorization 中の URL 入力ステップを省略し、consent page に直接
redirect できるため推奨されます。

!!! note

    エージェントが初めて接続すると、ブラウザで connection authorization を求められます。
    OAuth token は 1 時間有効で、30 日間自動的に refresh されます。

## 設定

Grafana Cloud MCP server は read と write access scope をサポートします。

- **Read access**: dashboard、alert、incident を表示し、data source を query します。
  常に利用できます。
- **Write access**: dashboard、alert、incident を作成、変更します。OAuth consent
  ステップで write access を許可または拒否できます。

エージェントが data query だけを必要とする場合は、least-privilege 構成のために
authorization 時に write access を拒否してください。

## 利用可能なツール

### Search and navigation

Tool | Description
---- | -----------
`search_dashboards` | query string で dashboard を検索します
`search_folders` | query string で folder を検索します
`generate_deeplink` | dashboard、panel、Explore query の deep link URL を生成します

### Dashboards

Tool | Description | Access
---- | ----------- | ------
`get_dashboard_by_uid` | UID で complete dashboard JSON を取得します | Read
`get_dashboard_summary` | dashboard の compact summary を取得します | Read
`get_dashboard_property` | JSONPath で dashboard の特定部分を抽出します | Read
`get_dashboard_panel_queries` | template variable substitution を適用した panel query を取得します | Read
`update_dashboard` | dashboard を作成または更新します | Write
`create_folder` | Grafana folder を作成します | Write

### Data sources

Tool | Description
---- | -----------
`list_datasources` | optional type filtering とともに、構成済みのすべての data source を一覧表示します
`get_datasource` | UID または name で data source の詳細情報を取得します

### Prometheus

Tool | Description
---- | -----------
`list_prometheus_metric_names` | regex filtering と pagination で利用可能な metric を発見します
`list_prometheus_metric_metadata` | 現在 scrape されている metric の metadata を一覧表示します
`list_prometheus_label_names` | optional series selector と time range で label name を一覧表示します
`list_prometheus_label_values` | 特定 label の値を取得します
`query_prometheus` | PromQL instant または range query を実行します
`query_prometheus_histogram` | histogram percentile を query します

### Loki

Tool | Description
---- | -----------
`list_loki_label_names` | log で利用可能な label name を一覧表示します
`list_loki_label_values` | 特定 label の unique value を取得します
`query_loki_logs` | log entry または metric value に対する LogQL query を実行します
`query_loki_stats` | log stream の統計を取得します
`query_loki_patterns` | 一般的な log pattern を検出、分析します

### Tempo

Tool | Description
---- | -----------
`tempo_traceql-search` | TraceQL で trace を検索します
`tempo_get-trace` | ID で trace を取得します
`tempo_get-attribute-names` | 利用可能な trace attribute を発見します
`tempo_get-attribute-values` | trace attribute の値を取得します
`tempo_traceql-metrics-instant` | instant TraceQL metrics query を実行します
`tempo_traceql-metrics-range` | range TraceQL metrics query を実行します

### Pyroscope

Tool | Description
---- | -----------
`list_pyroscope_label_names` | profile で利用可能な label name を一覧表示します
`list_pyroscope_label_values` | 特定 label の値を一覧表示します
`list_pyroscope_profile_types` | 利用可能な profile type を一覧表示します
`query_pyroscope` | Pyroscope の profile または metric を query します

### Alerting

Tool | Description | Access
---- | ----------- | ------
`alerting_manage_rules` | alert rule を list、filter、create、update します | Read / Write
`alerting_manage_routing` | notification policy、contact point、time interval を確認します | Read

### Incidents

Tool | Description | Access
---- | ----------- | ------
`list_incidents` | optional status filtering で incident を一覧表示します | Read
`get_incident` | ID で full incident detail を取得します | Read
`create_incident` | 新しい incident を作成します | Write
`add_activity_to_incident` | incident timeline に note を追加します | Write

### OnCall

Tool | Description
---- | -----------
`list_oncall_schedules` | optional team filtering で on-call schedule を一覧表示します
`get_oncall_shift` | 詳細な shift 情報を取得します
`get_current_oncall_users` | schedule で現在 on-call のユーザーを取得します
`list_oncall_teams` | OnCall team を一覧表示します
`list_oncall_users` | optional filtering で OnCall user を一覧表示します
`list_alert_groups` | state、team、time range、label で filtering して alert group を一覧表示します

### Additional tools

Tool | Description | Access
---- | ----------- | ------
`get_panel_image` | dashboard panel を PNG image として render します | Read
`describe_infrastructure` | topology と dependency を含む service group summary を取得します | Read
`get_annotations` | dashboard、time range、tag で filtering した annotation を取得します | Read
`create_annotation` | dashboard または panel に新しい annotation を作成します | Write
`query_clickhouse` | ClickHouse data source に SQL query を実行します | Read
`query_cloudwatch` | AWS CloudWatch metric を query します | Read
`query_elasticsearch` | Elasticsearch data source に search を実行します | Read

## Self-hosted Grafana

Self-hosted Grafana instance では、代わりに open source の
[Grafana MCP server](https://github.com/grafana/mcp-grafana) を使用してください。この
サーバーはローカルで実行され、service account token を使って任意の Grafana instance に
接続します。

## 追加リソース

- [Grafana Cloud MCP Server Documentation](https://grafana.com/docs/grafana-cloud/machine-learning/assistant/configure/cloud-mcp/)
- [Grafana Cloud](https://grafana.com/products/cloud/)
