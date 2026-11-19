---
catalog_title: Atlan
catalog_description: 메타데이터, 데이터 계보(lineage), 비즈니스 지식을 검색·탐색하고 거버넌스를 관리합니다
catalog_icon: /integrations/assets/atlan.png
catalog_tags: ["mcp"]
---

# ADK용 Atlan MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Atlan MCP Server](https://github.com/atlanhq/agent-toolkit)는 ADK 에이전트를
엔터프라이즈 AI를 위한 컨텍스트 계층인 [Atlan](https://www.atlan.com/)에
연결합니다. 이를 통해 에이전트는 조직의 컨텍스트 저장소(context repo), 즉 AI 에이전트가 효과적으로
동작하는 데 필요한 지식, 데이터, 시맨틱 정보에 접근할 수 있습니다. 이 통합을 사용하면
에이전트가 엔터프라이즈 컨텍스트를 검색·탐색하고, 엔드투엔드 데이터 계보(lineage)를
추적하며, 거버넌스가 적용된 데이터 정의와 용어집(glossary)에 접근하고, SQL을 실행하며, 메타데이터
그래프를 관리하고 데이터 품질을 보장하여 모든 에이전트 작업이 신뢰할 수
있는 조직 컨텍스트에 그라운딩(Grounding)되도록 할 수 있습니다.

## 사용 사례

- **엔터프라이즈 컨텍스트 검색 및 탐색:** 자연어로 전체 기술 스택의 테이블, 컬럼,
  대시보드, 용어집 항목, 데이터 프로덕트를 찾습니다.

- **엔드투엔드 계보(lineage) 탐색:** 시스템 전반에서 데이터 흐름을 업스트림(upstream)과 다운스트림(downstream)으로
  추적해 스키마 변경 전에 의존성을 파악합니다.

- **거버넌스가 적용된 데이터 정의 접근:** 용어집, 데이터 도메인, 인증된 메타데이터를 사용해
  에이전트 출력을 신뢰할 수 있는 조직 컨텍스트에 그라운딩(Grounding)합니다.

- **메타데이터 그래프 관리:** 에이전트에서 설명 업데이트, 자산 인증, 용어집 관리,
  데이터 품질 규칙과 스케줄 정의, SQL 실행까지 수행합니다.

## 사전 요구사항

- [Atlan](https://atlan.com/) 테넌트(tenant)
- 조회하려는 자산에 접근할 수 있는 권한이 있는 Atlan 계정
- 로컬에 설치된 Node.js (호스팅된 MCP 서버로 연결하는 `mcp-remote`에서 사용)

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
            instruction="Help users search, discover, and manage enterprise data assets using Atlan",
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
            instruction: "Help users search, discover, and manage enterprise data assets using Atlan",
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

### 탐색 및 검색

도구 | 설명
---- | -----------
`semantic_search_tool` | AI 기반 시맨틱 이해를 사용해 모든 데이터 자산을 자연어로 검색합니다
`search_assets_tool` | 구조화된 필터와 조건으로 자산을 검색합니다
`traverse_lineage_tool` | 자산의 데이터 흐름을 업스트림(소스) 또는 다운스트림(컨슈머)으로 추적합니다
`query_assets_tool` | 연결된 데이터 소스에 대해 SQL 쿼리를 실행합니다
`get_asset_tool` | GUID 또는 정규화된 이름(qualified name)으로 단일 자산의 상세 정보(커스텀 메타데이터, 데이터 품질 검사, README 포함)를 가져옵니다
`resolve_metadata_tool` | 이름 또는 설명으로 메타데이터 엔티티(사용자, 분류, 커스텀 메타데이터 세트, 용어집, 도메인, 데이터 프로덕트)를 찾습니다
`get_groups_tool` | 워크스페이스 그룹과 구성원을 나열합니다
`search_atlan_docs_tool` | Atlan 제품 문서를 검색하고 출처 인용이 포함된 LLM 생성 답변을 반환합니다

### 자산 업데이트

도구 | 설명
---- | -----------
`update_assets_tool` | 자산 설명, 인증(certificate) 상태, README 또는 용어를 업데이트합니다
`manage_announcements_tool` | 자산에 공지(정보, 경고, 이슈)를 추가하거나 제거합니다
`manage_asset_lifecycle_tool` | 자산을 보관(archive), 복원(restore) 또는 영구 삭제(purge)합니다

### 용어집 및 도메인

도구 | 설명
---- | -----------
`create_glossaries` | 새 용어집(glossary)을 만듭니다
`create_glossary_terms` | 용어집 안에 용어(term)를 만듭니다
`create_glossary_categories` | 용어집 안에 카테고리를 만듭니다
`create_domains` | 데이터 도메인과 하위 도메인을 만듭니다
`create_data_products` | 도메인 및 자산에 연결된 데이터 프로덕트를 만듭니다

### 데이터 품질 규칙

도구 | 설명
---- | -----------
`create_dq_rules_tool` | 데이터 품질 규칙(null 검사, 고유성, 정규식, 커스텀 SQL 등)을 만듭니다
`update_dq_rules_tool` | 기존 데이터 품질 규칙을 업데이트합니다
`schedule_dq_rules_tool` | cron 표현식으로 데이터 품질 규칙 실행을 예약합니다
`delete_dq_rules_tool` | 데이터 품질 규칙을 삭제합니다

### 커스텀 메타데이터

도구 | 설명
---- | -----------
`create_custom_metadata_set_tool` | 타입이 지정된 속성을 가진 커스텀 메타데이터 세트를 만듭니다
`add_attributes_to_cm_set_tool` | 기존 커스텀 메타데이터 세트에 새 속성을 추가합니다
`remove_attributes_from_cm_set_tool` | 커스텀 메타데이터 세트에서 속성을 보관(소프트 삭제)합니다
`delete_custom_metadata_set_tool` | 커스텀 메타데이터 세트를 영구 삭제하고 모든 자산에서 해당 값을 지웁니다
`update_custom_metadata_tool` | 하나 이상의 자산에서 커스텀 메타데이터 값을 업데이트합니다
`remove_custom_metadata_tool` | 자산에서 커스텀 메타데이터 세트의 값을 제거합니다

### Atlan 태그

도구 | 설명
---- | -----------
`add_atlan_tags_tool` | 하나 이상의 자산에 Atlan 태그를 추가합니다
`remove_atlan_tag_tool` | 하나 이상의 자산에서 Atlan 태그를 제거합니다

## 추가 리소스

- [Atlan MCP 서버 저장소](https://github.com/atlanhq/agent-toolkit)
- [Atlan MCP 개요](https://docs.atlan.com/product/capabilities/atlan-ai/how-tos/atlan-mcp-overview)
