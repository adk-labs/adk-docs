---
catalog_title: Chroma
catalog_description: 시맨틱 벡터 검색으로 정보를 저장하고 조회합니다
catalog_icon: /adk-docs/integrations/assets/chroma.png
catalog_tags: ["data","mcp"]
---

# ADK용 Chroma MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Chroma MCP Server](https://github.com/chroma-core/chroma-mcp)는
ADK 에이전트를 오픈소스 임베딩 데이터베이스인
[Chroma](https://www.trychroma.com/)와 연결합니다.
이 통합을 통해 에이전트는 컬렉션 생성, 문서 저장,
시맨틱 검색/전문 검색(full text search)/메타데이터 필터링 기반 조회를 수행할 수 있습니다.

## 사용 사례

- **에이전트용 시맨틱 메모리**: 대화 컨텍스트, 사실, 학습 정보를 저장하고
  에이전트가 나중에 자연어 질의로 검색할 수 있습니다.

- **지식 베이스 조회**: 문서를 저장하고 관련 컨텍스트를 검색해 응답하는
  RAG 시스템을 구축합니다.

- **세션 간 영구 컨텍스트**: 대화 간 장기 메모리를 유지해,
  에이전트가 과거 상호작용과 축적 지식을 참조할 수 있습니다.

## 사전 준비 사항

- **로컬 저장소 사용 시**: 데이터 영구 저장용 디렉터리 경로
- **Chroma Cloud 사용 시**: tenant ID, database name, API key를 가진
  [Chroma Cloud](https://www.trychroma.com/) 계정

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        # For local storage, use:
        DATA_DIR = "/path/to/your/data/directory"

        # For Chroma Cloud, use:
        # CHROMA_TENANT = "your-tenant-id"
        # CHROMA_DATABASE = "your-database-name"
        # CHROMA_API_KEY = "your-api-key"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="chroma_agent",
            instruction="Help users store and retrieve information using semantic search",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=[
                                "chroma-mcp",
                                # For local storage, use:
                                "--client-type",
                                "persistent",
                                "--data-dir",
                                DATA_DIR,
                                # For Chroma Cloud, use:
                                # "--client-type",
                                # "cloud",
                                # "--tenant",
                                # CHROMA_TENANT,
                                # "--database",
                                # CHROMA_DATABASE,
                                # "--api-key",
                                # CHROMA_API_KEY,
                            ],
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

        // For local storage, use:
        const DATA_DIR = "/path/to/your/data/directory";

        // For Chroma Cloud, use:
        // const CHROMA_TENANT = "your-tenant-id";
        // const CHROMA_DATABASE = "your-database-name";
        // const CHROMA_API_KEY = "your-api-key";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "chroma_agent",
            instruction: "Help users store and retrieve information using semantic search",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: [
                            "chroma-mcp",
                            // For local storage, use:
                            "--client-type",
                            "persistent",
                            "--data-dir",
                            DATA_DIR,
                            // For Chroma Cloud, use:
                            // "--client-type",
                            // "cloud",
                            // "--tenant",
                            // CHROMA_TENANT,
                            // "--database",
                            // CHROMA_DATABASE,
                            // "--api-key",
                            // CHROMA_API_KEY,
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

### 컬렉션 관리

Tool | Description
---- | -----------
`chroma_list_collections` | 페이지네이션 지원 포함 모든 컬렉션 나열
`chroma_create_collection` | 선택적 HNSW 구성으로 새 컬렉션 생성
`chroma_get_collection_info` | 컬렉션 상세 정보 조회
`chroma_get_collection_count` | 컬렉션 문서 수 조회
`chroma_modify_collection` | 컬렉션 이름 또는 메타데이터 업데이트
`chroma_delete_collection` | 컬렉션 삭제
`chroma_peek_collection` | 컬렉션 문서 샘플 조회

### 문서 작업

Tool | Description
---- | -----------
`chroma_add_documents` | 선택적 메타데이터/커스텀 ID와 함께 문서 추가
`chroma_query_documents` | 고급 필터링이 가능한 시맨틱 검색 질의
`chroma_get_documents` | ID 또는 필터로 문서 조회(페이지네이션 지원)
`chroma_update_documents` | 기존 문서의 내용/메타데이터/임베딩 업데이트
`chroma_delete_documents` | 컬렉션에서 특정 문서 삭제

## 구성

Chroma MCP 서버는 요구 사항에 맞는 여러 client type을 지원합니다:

### Client type

Client Type | Description | Key Arguments
----------- | ----------- | -------------
`ephemeral` | 인메모리 저장소(재시작 시 초기화). 테스트에 유용. | None (default)
`persistent` | 로컬 머신의 파일 기반 저장소 | `--data-dir`
`http` | 셀프호스팅 Chroma 서버 연결 | `--host`, `--port`, `--ssl`, `--custom-auth-credentials`
`cloud` | Chroma Cloud(api.trychroma.com) 연결 | `--tenant`, `--database`, `--api-key`

### 환경 변수

환경 변수로도 클라이언트를 구성할 수 있습니다.
명령줄 인수가 환경 변수보다 우선합니다.

Variable | Description
-------- | -----------
`CHROMA_CLIENT_TYPE` | 클라이언트 유형: `ephemeral`, `persistent`, `http`, `cloud`
`CHROMA_DATA_DIR` | 영구 로컬 저장 경로
`CHROMA_TENANT` | Chroma Cloud tenant ID
`CHROMA_DATABASE` | Chroma Cloud database name
`CHROMA_API_KEY` | Chroma Cloud API key
`CHROMA_HOST` | 셀프호스팅 HTTP client host
`CHROMA_PORT` | 셀프호스팅 HTTP client port
`CHROMA_SSL` | HTTP client SSL 활성화 (`true` 또는 `false`)
`CHROMA_DOTENV_PATH` | `.env` 파일 경로(기본값 `.chroma_env`)

## 추가 리소스

- [Chroma MCP Server Repository](https://github.com/chroma-core/chroma-mcp)
- [Chroma Documentation](https://docs.trychroma.com/)
- [Chroma Cloud](https://www.trychroma.com/)
