---
catalog_title: Pinecone
catalog_description: 데이터를 저장하고 시맨틱 검색 및 결과 재정렬을 수행합니다
catalog_icon: /adk-docs/integrations/assets/pinecone.png
catalog_tags: ["data","mcp"]
---

# ADK용 Pinecone MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Pinecone MCP Server](https://github.com/pinecone-io/pinecone-mcp)는
ADK 에이전트를 AI 애플리케이션용 벡터 데이터베이스인
[Pinecone](https://www.pinecone.io/)과 연결합니다. 이 통합을 통해
에이전트는 인덱스를 관리하고, 메타데이터 필터링이 가능한 시맨틱 검색으로
데이터를 저장/검색하며, 여러 인덱스를 재정렬과 함께 검색할 수 있습니다.

## 사용 사례

- **시맨틱 검색 및 검색 기반 조회**: 자연어 질의와 메타데이터 필터링,
  재정렬을 사용해 저장된 데이터를 검색합니다.

- **지식 베이스 관리**: 데이터 저장/관리로
  RAG(retrieval-augmented generation) 시스템을 구축/운영합니다.

- **교차 인덱스 검색**: 여러 Pinecone 인덱스를 동시에 검색하고,
  결과를 자동 중복 제거 및 재정렬합니다.

## 사전 준비 사항

- [Pinecone](https://www.pinecone.io/) 계정
- [Pinecone Console](https://app.pinecone.io)에서 발급한 API 키

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="pinecone_agent",
            instruction="Help users manage and search their Pinecone vector indexes",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "@pinecone-database/mcp",
                            ],
                            env={
                                "PINECONE_API_KEY": PINECONE_API_KEY,
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

        const PINECONE_API_KEY = "YOUR_PINECONE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "pinecone_agent",
            instruction: "Help users manage and search their Pinecone vector indexes",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: ["-y", "@pinecone-database/mcp"],
                        env: {
                            PINECONE_API_KEY: PINECONE_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    [integrated inference](https://docs.pinecone.io/guides/inference/understanding-inference)
    가 활성화된 인덱스만 지원됩니다. 통합 임베딩 모델이 없는 인덱스는
    이 MCP 서버에서 지원되지 않습니다.

## 사용 가능한 도구

### 문서

Tool | Description
---- | -----------
`search-docs` | 공식 Pinecone 문서 검색

### 인덱스 관리

Tool | Description
---- | -----------
`list-indexes` | 모든 Pinecone 인덱스 나열
`describe-index` | 인덱스 구성 정보 조회
`describe-index-stats` | 레코드 수 및 네임스페이스 포함 인덱스 통계 조회
`create-index-for-model` | 임베딩용 통합 추론 모델이 포함된 새 인덱스 생성

### 데이터 작업

Tool | Description
---- | -----------
`upsert-records` | 통합 추론이 활성화된 인덱스에 레코드 삽입/업데이트
`search-records` | 메타데이터 필터링/재정렬 옵션으로 텍스트 질의 검색
`cascading-search` | 여러 인덱스 검색 후 결과 중복 제거 및 재정렬
`rerank-documents` | 특화된 재정렬 모델로 레코드/텍스트 문서 컬렉션 재정렬

## 추가 리소스

- [Pinecone MCP Server Repository](https://github.com/pinecone-io/pinecone-mcp)
- [Pinecone MCP Documentation](https://docs.pinecone.io/guides/operations/mcp-server)
- [Pinecone Documentation](https://docs.pinecone.io)
