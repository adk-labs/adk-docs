---
catalog_title: Atlan
catalog_description: Atlan 카탈로그에서 데이터 자산을 검색, 탐색, 거버넌스합니다
catalog_icon: /integrations/assets/atlan.png
catalog_tags: ["mcp"]
---

# ADK용 Atlan MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Atlan MCP Server](https://github.com/atlanhq/agent-toolkit)는 ADK 에이전트를
[Atlan](https://www.atlan.com/) 데이터 카탈로그에 연결하여, 자연어로 warehouse,
lake, BI 도구, pipeline 전반의 데이터 자산을 발견, 탐색, 거버넌스, 관리할 수
있게 합니다.

## 사용 사례

- **자산 발견:** semantic search를 사용해 table, column, dashboard, pipeline
  전반을 검색하고 분석 또는 기능 개발에 적합한 데이터를 찾습니다.

- **Lineage 및 영향 분석:** 스키마 변경 전에 자산의 upstream source 또는
  downstream consumer를 추적해 의존성을 파악합니다.

- **거버넌스 및 stewardship:** 에이전트에서 설명을 업데이트하고, 자산을 인증하고,
  glossary와 data domain을 관리하며, data quality rule을 만들거나 예약합니다.

## 전제 조건

- [Atlan](https://atlan.com/) tenant
- 조회하려는 자산에 접근할 수 있는 권한이 있는 Atlan 계정
- 로컬에 설치된 Node.js(hosted MCP server로 bridge하는 `mcp-remote`에서 사용)

## 에이전트와 함께 사용

=== "Python"

    === "로컬 MCP 서버"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters


        root_agent = Agent(
            model="gemini-flash-latest",
            name="atlan_agent",
            instruction="Help users search, explore, and govern data assets in Atlan",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.atlan.com/mcp",
                            ]
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "로컬 MCP 서버"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "atlan_agent",
            instruction: "Help users search, explore, and govern data assets in Atlan",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.atlan.com/mcp",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    이 에이전트를 처음 실행하면 OAuth로 접근 권한을 요청하기 위해 브라우저 창이
    자동으로 열립니다. 또는 콘솔에 출력되는 승인 URL을 사용할 수도 있습니다. 에이전트가
    Atlan tenant에 접근할 수 있도록 이 요청을 승인해야 합니다.

## 사용 가능한 도구

### 발견 및 검색

Tool | Description
---- | -----------
`semantic_search_tool` | AI 기반 semantic understanding을 사용해 모든 데이터 자산을 자연어로 검색합니다
`search_assets_tool` | 구조화된 필터와 조건으로 자산을 검색합니다
`traverse_lineage_tool` | 자산의 data flow를 upstream(source) 또는 downstream(consumer)으로 추적합니다
`query_assets_tool` | 연결된 데이터 소스에 대해 SQL 쿼리를 실행합니다
`get_asset_tool` | GUID 또는 qualified name으로 단일 자산의 상세 정보(custom metadata, data quality check, README 포함)를 가져옵니다
`resolve_metadata_tool` | 이름 또는 설명으로 metadata entity(user, classification, custom metadata set, glossary, domain, data product)를 찾습니다
`get_groups_tool` | workspace group과 구성원을 나열합니다
`search_atlan_docs_tool` | Atlan 제품 문서를 검색하고 source citation이 포함된 LLM 생성 답변을 반환합니다

### 자산 업데이트

Tool | Description
---- | -----------
`update_assets_tool` | 자산 설명, certificate 상태, README 또는 term을 업데이트합니다
`manage_announcements_tool` | 자산에 announcement(information, warning, issue)를 추가하거나 제거합니다
`manage_asset_lifecycle_tool` | 자산을 archive, restore 또는 영구 purge합니다

### Glossary 및 domain

Tool | Description
---- | -----------
`create_glossaries` | 새 glossary를 만듭니다
`create_glossary_terms` | glossary 안에 term을 만듭니다
`create_glossary_categories` | glossary 안에 category를 만듭니다
`create_domains` | data domain과 subdomain을 만듭니다
`create_data_products` | domain 및 asset에 연결된 data product를 만듭니다

### Data quality rule

Tool | Description
---- | -----------
`create_dq_rules_tool` | data quality rule(null check, uniqueness, regex, custom SQL 등)을 만듭니다
`update_dq_rules_tool` | 기존 data quality rule을 업데이트합니다
`schedule_dq_rules_tool` | cron expression으로 data quality rule 실행을 예약합니다
`delete_dq_rules_tool` | data quality rule을 삭제합니다

### Custom metadata

Tool | Description
---- | -----------
`create_custom_metadata_set_tool` | typed attribute가 있는 custom metadata set을 만듭니다
`add_attributes_to_cm_set_tool` | 기존 custom metadata set에 새 attribute를 추가합니다
`remove_attributes_from_cm_set_tool` | custom metadata set에서 attribute를 archive(soft-delete)합니다
`delete_custom_metadata_set_tool` | custom metadata set을 영구 삭제하고 모든 자산에서 해당 값을 지웁니다
`update_custom_metadata_tool` | 하나 이상의 자산에서 custom metadata 값을 업데이트합니다
`remove_custom_metadata_tool` | 자산에서 custom metadata set의 값을 제거합니다

### Atlan tag

Tool | Description
---- | -----------
`add_atlan_tags_tool` | 하나 이상의 자산에 Atlan tag를 추가합니다
`remove_atlan_tag_tool` | 하나 이상의 자산에서 Atlan tag를 제거합니다

## 추가 리소스

- [Atlan MCP Server Repository](https://github.com/atlanhq/agent-toolkit)
- [Atlan MCP Overview](https://docs.atlan.com/product/capabilities/atlan-ai/how-tos/atlan-mcp-overview)
