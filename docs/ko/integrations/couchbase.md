---
catalog_title: Couchbase
catalog_description: 컬렉션을 조회하고, 스키마를 탐색하며, SQL++ 쿼리를 실행합니다
catalog_icon: /integrations/assets/couchbase.png
catalog_tags: ["data", "mcp"]
---

# ADK용 Couchbase MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Couchbase MCP Server](https://github.com/Couchbase-Ecosystem/mcp-server-couchbase)는
ADK 에이전트를 [Couchbase](https://www.couchbase.com/) 클러스터와 연결합니다.
이 통합을 사용하면 에이전트가 자연어로 Couchbase 데이터를 탐색하고,
쿼리를 실행하며, 성능 문제를 분석할 수 있습니다.

## 사용 사례

- **데이터 탐색**: 버킷, 스코프, 컬렉션, 문서 스키마를 찾아보고 자연어 쿼리로 데이터를 조회합니다.

- **데이터베이스 관리**: 대화형 명령으로 클러스터 상태를 모니터링하고, 실행 중인 서비스와 버킷, 스코프, 컬렉션 구조를 관리합니다.

- **쿼리 성능 분석**: 인덱스 추천을 받고, 쿼리 플랜을 분석하고, 느리거나 선택성이 낮은 쿼리를 조사해 성능을 최적화합니다.

## 사전 요구 사항

- 실행 중인 Couchbase 클러스터가 필요합니다. 다음 중 하나를 사용할 수 있습니다.
    - [Couchbase Capella](https://cloud.couchbase.com/) 사용(관리형 클라우드 서비스)
    - Couchbase Server 7.x 이상을 로컬 또는 자체 호스팅으로 실행
- 클러스터용 연결 문자열과 자격 증명(사용자 이름/비밀번호 또는 mTLS용 클라이언트 인증서)
- [`uv`](https://docs.astral.sh/uv/) 패키지 관리자 설치(`uvx` 명령 사용용)

## 에이전트에서 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        CB_CONNECTION_STRING = "couchbase://localhost"
        CB_USERNAME = "Administrator"
        CB_PASSWORD = "password"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="couchbase_agent",
            instruction="Help users explore and query Couchbase databases",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["couchbase-mcp-server"],
                            env={
                                "CB_CONNECTION_STRING": CB_CONNECTION_STRING,
                                "CB_USERNAME": CB_USERNAME,
                                "CB_PASSWORD": CB_PASSWORD,
                                "CB_MCP_READ_ONLY_MODE": "true",  # 쓰기 작업 방지
                            },
                        ),
                        timeout=60,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const CB_CONNECTION_STRING = "couchbase://localhost";
        const CB_USERNAME = "Administrator";
        const CB_PASSWORD = "password";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "couchbase_agent",
            instruction: "Help users explore and query Couchbase databases",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["couchbase-mcp-server"],
                        env: {
                            CB_CONNECTION_STRING: CB_CONNECTION_STRING,
                            CB_USERNAME: CB_USERNAME,
                            CB_PASSWORD: CB_PASSWORD,
                            CB_MCP_READ_ONLY_MODE: "true", // 쓰기 작업 방지
                        },
                    },
                })
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

### 클러스터 설정 및 상태 도구

도구 | 설명
---- | -----------
`get_server_configuration_status` | MCP 서버 상태를 가져옵니다
`test_cluster_connection` | 클러스터에 연결해 클러스터 자격 증명을 확인합니다
`get_cluster_health_and_services` | 클러스터 상태와 실행 중인 모든 서비스 목록을 가져옵니다

### 데이터 모델 및 스키마 탐색 도구

도구 | 설명
---- | -----------
`get_buckets_in_cluster` | 클러스터의 모든 버킷 목록을 가져옵니다
`get_scopes_in_bucket` | 지정한 버킷의 모든 스코프 목록을 가져옵니다
`get_collections_in_scope` | 지정한 버킷과 스코프의 모든 컬렉션 목록을 가져옵니다
`get_scopes_and_collections_in_bucket` | 지정한 버킷의 모든 스코프와 컬렉션 목록을 가져옵니다
`get_schema_for_collection` | 컬렉션의 구조를 가져옵니다

### 문서 KV 작업 도구

도구 | 설명
---- | -----------
`get_document_by_id` | 지정한 스코프와 컬렉션에서 ID로 문서를 가져옵니다
`upsert_document_by_id` | 지정한 스코프와 컬렉션에 ID로 문서를 upsert합니다. **`CB_MCP_READ_ONLY_MODE=true`일 때 비활성화됩니다.**
`insert_document_by_id` | 새 문서를 ID로 삽입합니다(문서가 이미 있으면 실패). **`CB_MCP_READ_ONLY_MODE=true`일 때 비활성화됩니다.**
`replace_document_by_id` | 기존 문서를 ID로 교체합니다(문서가 없으면 실패). **`CB_MCP_READ_ONLY_MODE=true`일 때 비활성화됩니다.**
`delete_document_by_id` | 지정한 스코프와 컬렉션에서 ID로 문서를 삭제합니다. **`CB_MCP_READ_ONLY_MODE=true`일 때 비활성화됩니다.**

### 쿼리 및 인덱싱 도구

도구 | 설명
---- | -----------
`run_sql_plus_plus_query` | 지정한 스코프에서 [SQL++ 쿼리](https://www.couchbase.com/sqlplusplus/)를 실행합니다
`list_indexes` | 버킷, 스코프, 컬렉션, 인덱스 이름으로 선택적으로 필터링하면서 클러스터의 모든 인덱스와 정의를 나열합니다
`get_index_advisor_recommendations` | 주어진 SQL++ 쿼리에 대해 Couchbase Index Advisor의 인덱스 추천을 받아 쿼리 성능을 최적화합니다

### 쿼리 성능 분석 도구

도구 | 설명
---- | -----------
`get_longest_running_queries` | 평균 서비스 시간이 가장 긴 쿼리를 가져옵니다
`get_most_frequent_queries` | 가장 자주 실행된 쿼리를 가져옵니다
`get_queries_with_largest_response_sizes` | 응답 크기가 가장 큰 쿼리를 가져옵니다
`get_queries_with_large_result_count` | 결과 수가 가장 많은 쿼리를 가져옵니다
`get_queries_using_primary_index` | 기본 인덱스를 사용하는 쿼리를 가져옵니다(잠재적인 성능 문제)
`get_queries_not_using_covering_index` | 커버링 인덱스를 사용하지 않는 쿼리를 가져옵니다
`get_queries_not_selective` | 선택성이 낮은 쿼리를 가져옵니다(인덱스 스캔이 최종 결과보다 훨씬 많은 문서를 반환함)

## 구성

### 환경 변수

변수 | 설명 | 기본값
-------- | ----------- | -------
`CB_CONNECTION_STRING` | Couchbase 클러스터에 대한 연결 문자열 | 필수
`CB_USERNAME` | 기본 인증용 사용자 이름 | 필수(mTLS용 클라이언트 인증서도 가능)
`CB_PASSWORD` | 기본 인증용 비밀번호 | 필수(mTLS용 클라이언트 인증서도 가능)
`CB_CLIENT_CERT_PATH` | mTLS 인증용 클라이언트 인증서 파일 경로 | 없음
`CB_CLIENT_KEY_PATH` | mTLS 인증용 클라이언트 키 파일 경로 | 없음
`CB_CA_CERT_PATH` | TLS용 서버 루트 인증서 경로(Capella에는 필요하지 않음) | 없음
`CB_MCP_READ_ONLY_MODE` | 모든 데이터 변경(KV 및 쿼리)을 방지합니다 | `true`
`CB_MCP_DISABLED_TOOLS` | 비활성화할 도구를 쉼표로 구분한 목록 | 없음

### 읽기 전용 모드

`CB_MCP_READ_ONLY_MODE` 설정(기본적으로 활성화됨)은 서버를 읽기 전용 작업으로 제한합니다.
이 옵션을 활성화하면 KV 쓰기 도구(`upsert_document_by_id`, `insert_document_by_id`,
`replace_document_by_id`, `delete_document_by_id`)가 로드되지 않으며, 데이터를 수정하는 SQL++ 쿼리는 차단됩니다.
이렇게 하면 실수로 변경할 위험 없이 안전하게 데이터를 탐색할 수 있습니다.

### 도구 비활성화

`CB_MCP_DISABLED_TOOLS`를 사용해 특정 도구를 비활성화할 수 있습니다:

```python
env={
    "CB_CONNECTION_STRING": "couchbase://localhost",
    "CB_USERNAME": "Administrator",
    "CB_PASSWORD": "password",
    "CB_MCP_DISABLED_TOOLS": "get_index_advisor_recommendations,get_queries_not_selective",
}
```

## 추가 자료

- [Couchbase MCP Server 저장소](https://github.com/Couchbase-Ecosystem/mcp-server-couchbase)
- [Couchbase 문서](https://docs.couchbase.com/)
- [Couchbase Capella](https://cloud.couchbase.com/)
