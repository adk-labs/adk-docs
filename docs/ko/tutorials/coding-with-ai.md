# AI와 함께 코딩하기

Agent Development Kit(ADK) 문서는
[`/llms.txt` 표준](https://llmstxt.org/)을 지원하며,
대규모 언어 모델(LLM)에 최적화된 머신 리더블 문서 인덱스를 제공합니다.
이를 통해 AI 기반 개발 환경에서 ADK 문서를 컨텍스트로 쉽게 사용할 수 있습니다.

## llms.txt란?

`llms.txt`는 LLM을 위한 지도 역할을 하는 표준 텍스트 파일로,
가장 중요한 문서 페이지와 설명을 나열합니다.
이로써 AI 도구가 ADK 문서 구조를 이해하고,
질문에 답하는 데 필요한 정보를 더 정확히 찾아올 수 있습니다.

ADK 문서는 업데이트될 때마다 자동 생성되는
다음 파일을 제공합니다.

File | Best For... | URL
---- | ----------- | ---
**`llms.txt`** | 동적으로 링크를 가져올 수 있는 도구 | [`https://google.github.io/adk-docs/llms.txt`](https://google.github.io/adk-docs/llms.txt)
**`llms-full.txt`** | 사이트 전체를 하나의 고정 텍스트 덤프로 필요로 하는 도구 | [`https://google.github.io/adk-docs/llms-full.txt`](https://google.github.io/adk-docs/llms-full.txt)

## 개발 도구에서의 사용

이 파일들을 사용하면 AI 코딩 어시스턴트에 ADK 지식을 제공할 수 있습니다.
이 기능을 통해 에이전트가 작업 계획 및 코드 생성 과정에서
ADK 문서를 자율적으로 검색하고 읽을 수 있습니다.

### Gemini CLI

[Gemini CLI](https://geminicli.com/)는
[ADK Docs Extension](https://github.com/derailed-dash/adk-docs-ext)을 사용하도록
설정할 수 있습니다.

**설치:**

확장 프로그램을 설치하려면 다음 명령어를 실행하세요.

```bash
gemini extensions install https://github.com/derailed-dash/adk-docs-ext
```

**사용 방법:**

설치가 완료되면 확장 기능은 자동으로 활성화됩니다.
Gemini CLI에서 ADK에 대해 질문하면,
`llms.txt` 파일과 ADK 문서를 사용해 정확한 답변과 코드를 제공합니다.

예를 들어 Gemini CLI 안에서 다음과 같이 질문할 수 있습니다.

> Agent Development Kit으로 function tool을 만드는 방법은?

---

### Antigravity

[Antigravity](https://antigravity.google/) IDE는
ADK의 `llms.txt` 파일을 가리키는 사용자 정의 MCP 서버를 실행해
ADK 문서를 참조하도록 설정할 수 있습니다.

**사전 준비:**

이 설정은 수동 설치 없이 문서 서버를 실행하기 위해 `uvx`를 사용하므로,
[`uv`](https://docs.astral.sh/uv/) 도구가 설치되어 있어야 합니다.

**설정:**

1. 에디터 상단 에이전트 패널의 **...**(더보기) 메뉴에서 MCP 스토어를 엽니다.
2. **Manage MCP Servers**를 클릭합니다.
3. **View raw config**를 클릭합니다.
4. `mcp_config.json`에 아래 항목을 추가합니다.
   첫 MCP 서버라면 아래 코드 블록 전체를 붙여 넣어도 됩니다.

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
            "AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt",
            "--transport",
            "stdio"
          ]
        }
      }
    }
    ```

MCP 서버 관리에 대한 자세한 내용은
[Antigravity MCP 문서](https://antigravity.google/docs/mcp)를 참고하세요.

**사용 방법:**

설정 후에는 아래와 같은 지시를 코딩 에이전트에 프롬프트로 전달할 수 있습니다.

> ADK 문서를 사용해서 Gemini 2.5 Pro 기반 멀티툴 에이전트를 만들고,
> 모의 날씨 조회 도구와 사용자 정의 계산기 도구를 포함해줘.
> `adk run`으로 에이전트를 검증해줘.

---

### Claude Code

[Claude Code](https://code.claude.com/docs/en/overview)는
[MCP 서버](https://code.claude.com/docs/en/mcp)를 추가해
ADK 문서를 조회하도록 설정할 수 있습니다.

**설치:**

Claude Code에 ADK 문서용 MCP 서버를 추가하려면 다음 명령어를 실행하세요.

```bash
claude mcp add adk-docs --transport stdio -- uvx --from mcpdoc mcpdoc --urls AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt --transport stdio
```

**사용 방법:**

설치가 완료되면 MCP 서버가 자동으로 활성화됩니다.
Claude Code에서 ADK에 대해 질문하면,
`llms.txt` 파일과 ADK 문서를 사용해 정확한 답변과 코드를 제공합니다.

예를 들어 Claude Code 안에서 다음과 같이 질문할 수 있습니다.

> Agent Development Kit으로 function tool을 만드는 방법은?

---

### Cursor

[Cursor](https://cursor.com/) IDE는
ADK의 `llms.txt` 파일을 가리키는 사용자 정의 MCP 서버를 실행해
ADK 문서를 참조하도록 설정할 수 있습니다.

**사전 준비:**

이 설정은 수동 설치 없이 문서 서버를 실행하기 위해 `uvx`를 사용하므로,
[`uv`](https://docs.astral.sh/uv/) 도구가 설치되어 있어야 합니다.

**설정:**

1. **Cursor Settings**를 열고 **Tools & MCP** 탭으로 이동합니다.
2. **New MCP Server**를 클릭하면 `mcp.json` 편집이 열립니다.
3. `mcp.json`에 아래 항목을 추가합니다.
   첫 MCP 서버라면 아래 코드 블록 전체를 붙여 넣어도 됩니다.

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
            "AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt",
            "--transport",
            "stdio"
          ]
        }
      }
    }
    ```

MCP 서버 관리에 대한 자세한 내용은
[Cursor MCP 문서](https://cursor.com/docs/context/mcp)를 참고하세요.

**사용 방법:**

설정 후에는 아래와 같은 지시를 코딩 에이전트에 프롬프트로 전달할 수 있습니다.

> ADK 문서를 사용해서 Gemini 2.5 Pro 기반 멀티툴 에이전트를 만들고,
> 모의 날씨 조회 도구와 사용자 정의 계산기 도구를 포함해줘.
> `adk run`으로 에이전트를 검증해줘.

---

### 기타 도구

`llms.txt` 표준을 지원하거나 URL에서 문서를 가져올 수 있는 도구라면
모두 이 파일을 활용할 수 있습니다.
도구의 지식 베이스 설정 또는 MCP 서버 설정에
`https://google.github.io/adk-docs/llms.txt` (또는 `llms-full.txt`) URL을
제공하면 됩니다.
