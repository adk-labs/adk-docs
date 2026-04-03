---
catalog_title: Google Developer Knowledge
catalog_description: Google의 공식 개발자 문서를 검색해 코드와 가이드를 찾습니다
catalog_icon: /integrations/assets/google-developer-knowledge.png
catalog_tags: ["mcp"]
---

# ADK용 Google Developer Knowledge MCP 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Google Developer Knowledge MCP 서버](https://developers.google.com/knowledge/mcp)는
Google의 공개 개발자 문서에 프로그래밍 방식으로 접근할 수 있게 해주며,
이 지식 베이스를 자신의 애플리케이션과 워크플로에 통합할 수 있도록 합니다.
ADK 에이전트를 Google의 공식 문서 라이브러리에 연결하면, 받는 코드와 가이드가 최신이고
권위 있는 문맥을 바탕으로 한다는 점을 보장할 수 있습니다.

## 사용 사례

- **구현 가이드**: 특정 기능을 구현하는 가장 좋은 방법을 질문합니다(예: Firebase Cloud Messaging을 사용한 푸시 알림).
- **코드 생성 및 설명**: Python으로 Cloud Storage 프로젝트의 모든 버킷을 나열하는 예제처럼, 문서에서 코드 예제를 검색합니다.
- **문제 해결 및 디버깅**: 오류 메시지나 API 키 워터마크를 질의해 문제를 빠르게 해결합니다.
- **비교 분석 및 요약**: Cloud Run과 Cloud Functions 같은 서비스 간 비교를 만듭니다.

## 사전 요구 사항

- [Google Cloud 프로젝트](https://developers.google.com/workspace/guides/create-project)
- [Developer Knowledge API 활성화](https://console.cloud.google.com/start/api?id=developerknowledge.googleapis.com)
- [인증 구성](https://developers.google.com/knowledge/mcp#authentication) 완료(OAuth 또는 API Key)

## 설치

Google Cloud 프로젝트에서 Developer Knowledge MCP 서버를 사용하도록 활성화해야 합니다.
정확한 `gcloud` 명령과 절차는 공식 [설치 가이드](https://developers.google.com/knowledge/mcp#installation)를 참고하세요.

## 에이전트에서 사용

=== "Python"

    === "Remote MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

        DEVELOPER_KNOWLEDGE_API_KEY = "YOUR_DEVELOPER_KNOWLEDGE_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="google_knowledge_agent",
            instruction="Search Google developer documentation for implementation guidance.",
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://developerknowledge.googleapis.com/mcp",
                        headers={"X-Goog-Api-Key": DEVELOPER_KNOWLEDGE_API_KEY},
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Remote MCP Server"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const DEVELOPER_KNOWLEDGE_API_KEY = "YOUR_DEVELOPER_KNOWLEDGE_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "google_knowledge_agent",
            instruction: "Search Google developer documentation for implementation guidance.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://developerknowledge.googleapis.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                "X-Goog-Api-Key": DEVELOPER_KNOWLEDGE_API_KEY,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 사용 가능한 도구

| 도구 이름 | 설명 |
|---|---|
| `search_documents` | Google의 개발자 문서를 검색해 질의와 관련된 페이지와 발췌를 찾습니다 |
| `get_documents` | 검색 결과의 상위 참조를 사용해 여러 문서의 전체 페이지 내용을 가져옵니다 |

## 추가 자료

- [Developer Knowledge MCP 문서](https://developers.google.com/knowledge/mcp)
- [Developer Knowledge API 참조](https://developers.google.com/knowledge/api)
- [Corpus 참조](https://developers.google.com/knowledge/reference/corpus-reference)
