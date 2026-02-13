---
catalog_title: Qdrant
catalog_description: 시맨틱 벡터 검색으로 정보를 저장하고 조회합니다
catalog_icon: /adk-docs/integrations/assets/qdrant.png
catalog_tags: ["data","mcp"]
---

# ADK용 Qdrant MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Qdrant MCP Server](https://github.com/qdrant/mcp-server-qdrant)는
ADK 에이전트를 오픈소스 벡터 검색 엔진인 [Qdrant](https://qdrant.tech/)와 연결합니다.
이 통합을 통해 에이전트는 시맨틱 검색으로 정보를 저장하고 조회할 수 있습니다.

## 사용 사례

- **에이전트용 시맨틱 메모리**: 대화 컨텍스트, 사실, 학습된 정보를 저장하고
  에이전트가 나중에 자연어 질의로 검색할 수 있습니다.

- **코드 저장소 검색**: 코드 스니펫, 문서, 구현 패턴의 검색 인덱스를 구축하고
  시맨틱하게 질의할 수 있습니다.

- **지식 베이스 조회**: 문서를 저장하고 응답에 필요한 컨텍스트를 검색하는
  RAG 시스템을 구축합니다.

## 사전 준비 사항

- 실행 중인 Qdrant 인스턴스. 다음 중 하나를 사용할 수 있습니다:
    - [Qdrant Cloud](https://cloud.qdrant.io/) (관리형 서비스)
    - Docker 로컬 실행: `docker run -p 6333:6333 qdrant/qdrant`
- (선택 사항) 인증용 Qdrant API 키

## 에이전트와 함께 사용

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        QDRANT_URL = "http://localhost:6333"  # Or your Qdrant Cloud URL
        COLLECTION_NAME = "my_collection"
        # QDRANT_API_KEY = "YOUR_QDRANT_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="qdrant_agent",
            instruction="Help users store and retrieve information using semantic search",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["mcp-server-qdrant"],
                            env={
                                "QDRANT_URL": QDRANT_URL,
                                "COLLECTION_NAME": COLLECTION_NAME,
                                # "QDRANT_API_KEY": QDRANT_API_KEY,
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

        const QDRANT_URL = "http://localhost:6333"; // Or your Qdrant Cloud URL
        const COLLECTION_NAME = "my_collection";
        // const QDRANT_API_KEY = "YOUR_QDRANT_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "qdrant_agent",
            instruction: "Help users store and retrieve information using semantic search",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["mcp-server-qdrant"],
                        env: {
                            QDRANT_URL: QDRANT_URL,
                            COLLECTION_NAME: COLLECTION_NAME,
                            // QDRANT_API_KEY: QDRANT_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

Tool | Description
---- | -----------
`qdrant-store` | 선택적 메타데이터와 함께 정보를 Qdrant에 저장
`qdrant-find` | 자연어 질의로 관련 정보 검색

## 구성

Qdrant MCP 서버는 환경 변수로 구성할 수 있습니다:

Variable | Description | Default
-------- | ----------- | -------
`QDRANT_URL` | Qdrant 서버 URL | `None` (required)
`QDRANT_API_KEY` | Qdrant Cloud 인증용 API 키 | `None`
`COLLECTION_NAME` | 사용할 컬렉션 이름 | `None`
`QDRANT_LOCAL_PATH` | 로컬 영구 저장 경로(URL 대안) | `None`
`EMBEDDING_MODEL` | 사용할 임베딩 모델 | `sentence-transformers/all-MiniLM-L6-v2`
`EMBEDDING_PROVIDER` | 임베딩 제공자 (`fastembed` 또는 `ollama`) | `fastembed`
`TOOL_STORE_DESCRIPTION` | 저장 도구 사용자 설명 | 기본 설명
`TOOL_FIND_DESCRIPTION` | 검색 도구 사용자 설명 | 기본 설명

### 사용자 지정 도구 설명

도구 설명을 사용자 지정해 에이전트 동작을 유도할 수 있습니다:

```python
env={
    "QDRANT_URL": "http://localhost:6333",
    "COLLECTION_NAME": "code-snippets",
    "TOOL_STORE_DESCRIPTION": "Store code snippets with descriptions. The 'information' parameter should contain a description of what the code does, while the actual code should be in 'metadata.code'.",
    "TOOL_FIND_DESCRIPTION": "Search for relevant code snippets using natural language. Describe the functionality you're looking for.",
}
```

## 추가 리소스

- [Qdrant MCP Server Repository](https://github.com/qdrant/mcp-server-qdrant)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Cloud](https://cloud.qdrant.io/)
