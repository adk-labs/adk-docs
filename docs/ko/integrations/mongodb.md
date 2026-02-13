---
catalog_title: MongoDB
catalog_description: 컬렉션 질의, 데이터베이스 관리, 스키마 분석을 수행합니다
catalog_icon: /adk-docs/integrations/assets/mongodb.png
catalog_tags: ["data","mcp"]
---

# ADK용 MongoDB MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[MongoDB MCP Server](https://github.com/mongodb-js/mongodb-mcp-server)는
ADK 에이전트를 [MongoDB](https://www.mongodb.com/) 데이터베이스 및
MongoDB Atlas 클러스터와 연결합니다. 이 통합을 통해 에이전트는
자연어로 컬렉션 질의, 데이터베이스 관리, MongoDB Atlas 인프라 상호작용을 수행할 수 있습니다.

## 사용 사례

- **데이터 탐색 및 분석**: 자연어로 MongoDB 컬렉션을 질의하고,
  집계를 실행하며, 복잡한 쿼리를 수동 작성하지 않고 문서 스키마를 분석합니다.

- **데이터베이스 관리**: 데이터베이스/컬렉션 나열, 인덱스 생성,
  사용자 관리, 통계 모니터링을 대화형 명령으로 수행합니다.

- **Atlas 인프라 관리**: MongoDB Atlas 클러스터 생성/관리,
  접근 목록 구성, 성능 권장사항 조회를 에이전트에서 직접 수행합니다.

## 사전 준비 사항

- **데이터베이스 접근용**: MongoDB 연결 문자열(로컬/셀프호스팅/Atlas)
- **Atlas 관리용**: API 자격 증명(client ID, secret)을 가진
  [MongoDB Atlas](https://www.mongodb.com/atlas) 서비스 계정

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        # For database access, use a connection string:
        CONNECTION_STRING = "mongodb://localhost:27017/myDatabase"

        # For Atlas management, use API credentials:
        # ATLAS_CLIENT_ID = "YOUR_ATLAS_CLIENT_ID"
        # ATLAS_CLIENT_SECRET = "YOUR_ATLAS_CLIENT_SECRET"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="mongodb_agent",
            instruction="Help users query and manage MongoDB databases",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mongodb-mcp-server",
                                "--readOnly",  # Remove for write operations
                            ],
                            env={
                                # For database access, use:
                                "MDB_MCP_CONNECTION_STRING": CONNECTION_STRING,
                                # For Atlas management, use:
                                # "MDB_MCP_API_CLIENT_ID": ATLAS_CLIENT_ID,
                                # "MDB_MCP_API_CLIENT_SECRET": ATLAS_CLIENT_SECRET,
                            },
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

        // For database access, use a connection string:
        const CONNECTION_STRING = "mongodb://localhost:27017/myDatabase";

        // For Atlas management, use API credentials:
        // const ATLAS_CLIENT_ID = "YOUR_ATLAS_CLIENT_ID";
        // const ATLAS_CLIENT_SECRET = "YOUR_ATLAS_CLIENT_SECRET";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "mongodb_agent",
            instruction: "Help users query and manage MongoDB databases",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mongodb-mcp-server",
                            "--readOnly", // Remove for write operations
                        ],
                        env: {
                            // For database access, use:
                            MDB_MCP_CONNECTION_STRING: CONNECTION_STRING,
                            // For Atlas management, use:
                            // MDB_MCP_API_CLIENT_ID: ATLAS_CLIENT_ID,
                            // MDB_MCP_API_CLIENT_SECRET: ATLAS_CLIENT_SECRET,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

### MongoDB 데이터베이스 도구

Tool | Description
---- | -----------
`find` | MongoDB 컬렉션에 find 쿼리 실행
`aggregate` | MongoDB 컬렉션에 집계 실행
`count` | 컬렉션 문서 수 조회
`list-databases` | MongoDB 연결의 모든 데이터베이스 나열
`list-collections` | 특정 데이터베이스의 모든 컬렉션 나열
`collection-schema` | 컬렉션 스키마 설명
`collection-indexes` | 컬렉션 인덱스 설명
`insert-many` | 컬렉션에 문서 삽입
`update-many` | 필터에 일치하는 문서 업데이트
`delete-many` | 필터에 일치하는 문서 삭제
`create-collection` | 새 컬렉션 생성
`drop-collection` | 데이터베이스에서 컬렉션 제거
`drop-database` | 데이터베이스 제거
`create-index` | 컬렉션 인덱스 생성
`drop-index` | 컬렉션 인덱스 삭제
`rename-collection` | 컬렉션 이름 변경
`db-stats` | 데이터베이스 통계 조회
`explain` | 쿼리 실행 통계 조회
`export` | 쿼리 결과를 EJSON 형식으로 내보내기

### MongoDB Atlas 도구

!!! note

    Atlas 도구에는 API 자격 증명이 필요합니다. Atlas 도구를 활성화하려면
    `MDB_MCP_API_CLIENT_ID`와 `MDB_MCP_API_CLIENT_SECRET` 환경 변수를 설정하세요.

Tool | Description
---- | -----------
`atlas-list-orgs` | MongoDB Atlas 조직 목록 조회
`atlas-list-projects` | MongoDB Atlas 프로젝트 목록 조회
`atlas-list-clusters` | MongoDB Atlas 클러스터 목록 조회
`atlas-inspect-cluster` | 클러스터 메타데이터 점검
`atlas-list-db-users` | 데이터베이스 사용자 목록 조회
`atlas-create-free-cluster` | 무료 Atlas 클러스터 생성
`atlas-create-project` | Atlas 프로젝트 생성
`atlas-create-db-user` | 데이터베이스 사용자 생성
`atlas-create-access-list` | IP 접근 목록 구성
`atlas-inspect-access-list` | IP 접근 목록 항목 조회
`atlas-list-alerts` | Atlas 경보 목록 조회
`atlas-get-performance-advisor` | 성능 권장사항 조회

## 구성

### 환경 변수

Variable | Description
-------- | -----------
`MDB_MCP_CONNECTION_STRING` | 데이터베이스 접근용 MongoDB 연결 문자열
`MDB_MCP_API_CLIENT_ID` | Atlas 도구용 Atlas API client ID
`MDB_MCP_API_CLIENT_SECRET` | Atlas 도구용 Atlas API client secret
`MDB_MCP_READ_ONLY` | 읽기 전용 모드 활성화 (`true` 또는 `false`)
`MDB_MCP_DISABLED_TOOLS` | 비활성화할 도구의 쉼표 구분 목록
`MDB_MCP_LOG_PATH` | 로그 파일 디렉터리

### 읽기 전용 모드

`--readOnly` 플래그는 서버를 읽기, 연결, 메타데이터 작업으로만 제한합니다.
이렇게 하면 생성/수정/삭제 작업이 방지되어,
실수로 데이터를 변경할 위험 없이 안전한 데이터 탐색이 가능합니다.

### 도구 비활성화

`MDB_MCP_DISABLED_TOOLS`를 사용해 특정 도구 또는 카테고리를 비활성화할 수 있습니다:

- 도구 이름: `find`, `aggregate`, `insert-many` 등
- 카테고리: `atlas`(모든 Atlas 도구), `mongodb`(모든 데이터베이스 도구)
- 작업 유형: `create`, `update`, `delete`, `read`, `metadata`

## 추가 리소스

- [MongoDB MCP Server Repository](https://github.com/mongodb-js/mongodb-mcp-server)
- [MongoDB Documentation](https://www.mongodb.com/docs/)
- [MongoDB Atlas](https://www.mongodb.com/atlas)
