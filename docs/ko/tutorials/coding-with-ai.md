# AI와 함께 코딩하기

AI 코딩 어시스턴트를 사용해 Agent Development Kit(ADK)로 에이전트를
구축할 수 있습니다. 프로젝트에 개발 스킬을 설치하거나 MCP 서버를 통해
ADK 문서를 연결해 코딩 에이전트에 ADK 전문성을 제공하세요.

- [**Agent Platform의 Agents CLI**](#agents-cli): ADK 개발을 위한 명령줄 도구 및 코딩 스킬.
- [**ADK Docs MCP Server**](#adk-docs-mcp-server): MCP 서버를 통해 코딩
  도구를 ADK 문서에 연결합니다.
- [**ADK Docs Index**](#adk-docs-index): `llms.txt` 표준을 따르는
  머신 리더블 문서 파일입니다.

## Agents CLI {#agents-cli}

[Agents CLI](https://google.github.io/agents-cli/) 도구 세트를 사용하면 Antigravity, Gemini CLI, Claude Code, Cursor를 포함하여 즐겨 사용하는 AI 코딩 환경에 ADK 에이전트 전문성을 연결할 수 있습니다. 현재 사용 중인 AI 기반 개발 환경에 Agents CLI를 설치하여 ADK 에이전트를 스캐폴딩, 빌드, 테스트, 평가 및 배포하세요. 다음과 같은 Agents CLI 스킬로 개발 환경을 보완할 수 있습니다.

*   개발 수명 주기 및 코딩 가이드라인
*   프로젝트 스캐폴딩
*   평가 방법론 및 점수화
*   Agent Runtime, Cloud Run 및 GKE 배포
*   Gemini Enterprise 에이전트 게시
*   트레이싱, 로깅 및 통합
*   Python API 빠른 참조 및 문서 인덱스

Agents CLI를 설치하고 ADK 개발 스킬을 설정하려면 다음을 실행하세요.

```bash
uvx google-agents-cli setup
```

개발 환경에서 Agents CLI를 설치하고 사용하는 방법에 대한 자세한 내용은 [Agents CLI 문서](https://google.github.io/agents-cli/)를 참고하세요.

## ADK Docs MCP Server

MCP 서버를 사용하도록 코딩 도구를 구성하면 ADK 문서를 검색하고 읽을 수
있습니다. 아래에는 널리 쓰이는 도구의 설정 방법이 나와 있습니다.

### Gemini CLI

[Gemini CLI](https://geminicli.com/)에 ADK 문서 MCP 서버를 추가하려면
[ADK Docs Extension](https://github.com/derailed-dash/adk-docs-ext)을
설치하세요.

```bash
gemini extensions install https://github.com/derailed-dash/adk-docs-ext
```

### Antigravity

[Antigravity](https://antigravity.google/)에 ADK 문서 MCP 서버를
추가하려면([`uv`](https://docs.astral.sh/uv/) 필요):

1. 에디터 상단 에이전트 패널의 **...**(더보기) 메뉴에서 MCP 스토어를
   엽니다.
2. **Manage MCP Servers**를 클릭한 다음 **View raw config**를
   클릭합니다.
3. `mcp_config.json`에 다음 내용을 추가합니다.

    ```json
    {
      "mcpServers": {
        "adk-docs-mcp": {
          "command": "uvx",
          "args": [
            "--from",
            "mcpdoc",
            "mcpdoc",
            "--urls",
            "AgentDevelopmentKit:https://adk.dev/llms.txt",
            "--transport",
            "stdio"
          ]
        }
      }
    }
    ```

### Claude Code

[Claude Code](https://code.claude.com/docs/en/overview)에 ADK 문서 MCP
서버를 추가하려면 다음을 실행하세요.

```bash
claude mcp add adk-docs --transport stdio -- uvx --from mcpdoc mcpdoc --urls AgentDevelopmentKit:https://adk.dev/llms.txt --transport stdio
```

### Cursor

[Cursor](https://cursor.com/)에 ADK 문서 MCP 서버를 추가하려면
([`uv`](https://docs.astral.sh/uv/) 필요):

1. **Cursor Settings**를 열고 **Tools & MCP** 탭으로 이동합니다.
2. **New MCP Server**를 클릭하면 `mcp.json` 편집기가 열립니다.
3. `mcp.json`에 다음 내용을 추가합니다.

    ```json
    {
      "mcpServers": {
        "adk-docs-mcp": {
          "command": "uvx",
          "args": [
            "--from",
            "mcpdoc",
            "mcpdoc",
            "--urls",
            "AgentDevelopmentKit:https://adk.dev/llms.txt",
            "--transport",
            "stdio"
          ]
        }
      }
    }
    ```

### Other Tools

MCP 서버를 지원하는 모든 코딩 도구는 위와 같은 서버 구성을 사용할 수
있습니다. 사용하는 도구의 MCP 설정에 맞게 Antigravity 또는 Cursor
섹션의 JSON 예시를 조정하세요.

## ADK Docs Index

ADK 문서는 [`llms.txt` 표준](https://llmstxt.org/)을 따르는 머신
리더블 파일로 제공됩니다. 이 파일은 문서가 업데이트될 때마다 생성되며
항상 최신 상태를 유지합니다.

| 파일 | 설명 | URL |
|------|------|-----|
| `llms.txt` | 링크가 포함된 문서 인덱스 | [`adk.dev/llms.txt`](https://adk.dev/llms.txt) |
| `llms-full.txt` | 전체 문서를 하나의 파일로 제공 | [`adk.dev/llms-full.txt`](https://adk.dev/llms-full.txt) |
