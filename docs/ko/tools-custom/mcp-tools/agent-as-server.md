# ADK 에이전트를 MCP 서버로 구성

ADK 에이전트의 기능을 MCP 서버 내에서 호스팅하여 Antigravity, Claude Code 또는 커스텀 에이전트와 같은 외부 MCP 클라이언트에서 접근할 수 있도록 만들 수 있습니다.
이를 달성하는 두 가지 주요 방법이 있습니다:

* **전체 에이전트 노출:** 간단한 한 줄 변환을 통해 전체 멀티턴 에이전트 추론 및 내부 툴 실행을 서버로 래핑합니다.

* **개별 툴 노출:** 에이전트의 추론 루프 없이 특정 독립형 ADK 툴(예: `FunctionTool`)을 래핑하기 위해 경량 MCP 서버를 수동으로 빌드합니다.

## 시작하기
가장 강력한 접근 방식은 전체 `LlmAgent`를 노출하는 것입니다. `to_mcp_server()` 유틸리티를 사용하면 에이전트를 표준 FastMCP 서버로 변환할 수 있습니다. 이를 통해 외부 클라이언트는 에이전트의 전체 인지 기능 및 내부 툴킷과 상호작용할 수 있습니다.

```python
from google.adk.agents import LlmAgent
from google.adk.tools.load_web_page import load_web_page
from google.adk.tools.mcp_tool import to_mcp_server

# 1. ADK 에이전트 정의
agent = LlmAgent(
    model="gemini-flash-latest", 
    name="web_reader_agent", 
    instruction="Fetch and summarize web content for the user.", 
    tools=[load_web_page], 
)

# 2. 에이전트를 MCP 서버로 변환
app = to_mcp_server(agent)

if __name__ == "__main__":
    # 에이전트를 표준 stdio MCP 서버로 실행
    app.run()
```

## 개별 ADK 툴 노출
전체 에이전트 추론 루프 없이 개별 기능(예: 특정 `FunctionTool`)만 노출하려는 경우 MCP 서버를 직접 빌드해야 합니다.

**사전 준비 사항:**
ADK 환경에 MCP Server 라이브러리를 설치해야 합니다:
```bash
pip install mcp
```

**구현 단계:**

1. **툴 초기화:** 노출하려는 ADK 툴(예: `FunctionTool(load_web_page)`)을 인스턴스화합니다.
2. **툴 목록 핸들러:** 툴을 알리기 위해 MCP 서버의 `@app.list_tools()` 핸들러를 구현합니다. `google.adk.tools.mcp_tool.conversion_utils`의 `adk_to_mcp_tool_type` 유틸리티를 사용하여 ADK 툴 정의를 MCP 스키마 형식으로 변환합니다.
3. **툴 호출 핸들러:** 클라이언트 요청을 수신하기 위해 `@app.call_tool()` 핸들러를 구현합니다. 이 핸들러는 요청이 래핑된 툴과 일치하는지 확인하고, ADK 툴의 `.run_async()` 메서드(`tool_context=None` 전달)를 실행하며, 응답을 `mcp.types.TextContent`와 같은 MCP 호환 구조로 포맷해야 합니다.

## ADK 툴을 사용한 MCP 서버 빌드

1. MCP 서버를 위한 새 Python 파일(예: `my_adk_mcp_server.py`)을 생성합니다.
2. 새 파일에 다음 코드를 추가하여 서버 로직을 구현합니다. 이 스크립트는 ADK `load_web_page` 툴을 노출하는 MCP 서버를 설정합니다.

```python
import asyncio
import json
import os
from dotenv import load_dotenv

# MCP Server 임포트
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio 

# ADK Tool 임포트
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.load_web_page import load_web_page 
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

load_dotenv()

# 1. ADK 툴 준비
adk_tool_to_expose = FunctionTool(load_web_page)

# 2. MCP Server 인스턴스 생성
app = Server("adk-tool-exposing-mcp-server")

# 3. list_tools 핸들러 구현
@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    mcp_tool_schema = adk_to_mcp_tool_type(adk_tool_to_expose)
    return [mcp_tool_schema]

# 4. call_tool 핸들러 구현
@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    if name == adk_tool_to_expose.name:
        try:
            # ADK 툴 실행
            adk_tool_response = await adk_tool_to_expose.run_async(
                args=arguments, 
                tool_context=None,
            )
            # MCP TextContent로 포맷
            response_text = json.dumps(adk_tool_response, indent=2)
            return [mcp_types.TextContent(type="text", text=response_text)]
        except Exception as e:
            error_text = json.dumps({"error": str(e)})
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        error_text = json.dumps({"error": f"Tool '{name}' not found."})
        return [mcp_types.TextContent(type="text", text=error_text)]

# 5. MCP Server 실행기 (Stdio)
async def run_mcp_stdio_server():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(run_mcp_stdio_server())
```

## 연결 및 전송 모드
이러한 MCP 서버를 통해 ADK 기능을 노출할 때 일반적으로 표준 입력/출력 연결(`mcp.server.stdio`)을 사용하여 실행합니다. 이 연결을 통해 부모 프로세스로 실행되는 외부 클라이언트 애플리케이션이 스크립트를 생성하고 stdio 스트림을 통해 직접 통신할 수 있으므로 연결이 자체 완결적이고 격리된 상태로 유지됩니다.

## ADK 에이전트로 커스텀 MCP 서버 테스트

커스텀 서버를 테스트하려면 클라이언트 역할을 하는 ADK 에이전트를 빌드해야 합니다. 이 에이전트는 `McpToolset`을 사용하여 방금 생성한 서버 스크립트에 대한 연결을 설정합니다.

1. `./adk_agent_samples/mcp_client_agent/`와 같은 새 디렉터리에 에이전트를 설정합니다. `agent.py` 파일을 생성하고 검색 가능하도록 `__init__.py`를 함께 포함합니다.

```python
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 중요: 이전에 빌드한 서버 스크립트의 절대 경로를 제공하십시오.
MCP_SERVER_SCRIPT = "/path/to/your/my_adk_mcp_server.py"

root_agent = LlmAgent(
    model='gemini-flash-latest',
    name='web_reader_mcp_client_agent',
    instruction="Use the 'load_web_page' tool to fetch content from a URL provided by the user.",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='python3', 
                    args=[MCP_SERVER_SCRIPT], 
                )
            )
        )
    ],
)
```

2. 터미널에서 에이전트의 상위 디렉터리로 이동합니다:

```bash
cd ./adk_agent_samples
adk web
```

3. ADK 웹 UI를 열고 web_reader_mcp_client_agent를 선택합니다.
4. *Load the content from "https://example.com"* 과 같은 프롬프트로 연결을 테스트합니다.

## Google Cloud Genmedia용 MCP 서버

[Genmedia 서비스용 MCP 툴](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia)은 Imagen, Veo, Chirp 3 HD 음성, Lyria와 같은 Google Cloud 생성형 미디어 서비스를 AI 애플리케이션에 통합할 수 있는 오픈소스 MCP 서버 세트입니다.

Agent Development Kit (ADK) 및 [Genkit](https://genkit.dev/)은 이러한 MCP 툴에 대한 기본 지원을 제공하여 AI 에이전트가 생성형 미디어 워크플로를 효과적으로 오케스트레이션할 수 있도록 지원합니다. 구현 지침은 [ADK 예제 에이전트](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/adk) 및 [Genkit 예제](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/genkit)를 참조하십시오.
