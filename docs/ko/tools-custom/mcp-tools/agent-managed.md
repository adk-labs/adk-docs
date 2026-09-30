# 하위 에이전트를 통한 MCP 관리

이미 **직접 MCP 툴 연동**을 통해 에이전트를 외부 리소스에 연결하는 방법과 **에이전트 노출 MCP 서버**를 통해 외부 클라이언트에 에이전트를 서빙하는 방법을 확인했습니다. 그러나 ADK 멀티 에이전트 역량이 확장됨에 따라 단일 모델의 컨텍스트 창에 과부하를 주지 않으면서 복잡한 다단계 추론을 격리하는 방법이 필요할 수 있습니다.

## 시작하기

```python
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 1단계: MCP 연결 초기화
mcp_connection = StdioConnectionParams(
    server_params=StdioServerParameters(
        command='npx',
        args=['-y', '@modelcontextprotocol/server-postgres', 'postgres://user:pass@localhost:5432/db'],
    )
)

# 2단계: 자식 하위 에이전트 생성 및 McpToolset 연결
database_sub_agent = LlmAgent(
    name="database_sub_agent",
    model="gemini-flash-latest",
    description="Delegates tasks to a database specialist...",
    instruction="You are a SQL expert...",
    tools=[McpToolset(connection_params=mcp_connection, tool_filter=['query_db', 'list_tables'])]
)
database_tool = AgentTool(agent=database_sub_agent)


# 3단계: 기본 루트 에이전트에 AgentTool 제공
root_agent = LlmAgent(
    name="primary_orchestrator",
    model="gemini-pro-latest",
    instruction="You are the main assistant. You have access to specialized agents. Delegate data retrieval tasks to your database tool.",
    tools=[database_tool]
)
```

## 아키텍처 역할 및 툴 어댑테이션
ADK 프레임워크에서 `AgentTool`은 상위 오케스트레이터에 네이티브 툴로 노출하기 위해 `LlmAgent`를 래핑합니다. 자식 에이전트는 기본 MCP 서버에 연결(`list_tools` 사용)하고 외부 MCP 툴 정의를 ADK 호환 `BaseTool` 인스턴스로 변환하며 모든 실행 호출(`call_tool`)을 비동기적으로 프록시하는 `McpToolset`을 통해 툴을 사용합니다.

## 툴 범위 지정 및 인지 필터링 (`tool_filter`)
특화된 하위 에이전트에 `McpToolset`을 할당할 때 `tool_filter` 매개변수를 사용하여 해당 에이전트에서 사용할 수 있는 구체적인 툴을 제한할 수 있습니다:
* **인지적 집중:** 'read_file', 'list_directory'와 같이 하위 에이전트의 역할과 관련된 특정 작업만 노출합니다.
* **보안 및 샌드박싱:** MCP 서버에 의해 노출된 위험한 툴에 대한 의도치 않은 접근을 방지하여 예측할 수 없는 입력으로부터 실행 표면을 격리합니다.

## 연결 전송 모드
하위 에이전트의 `McpToolset`은 배포 아키텍처에 따라 다음 두 가지 기본 연결 모드 중 하나로 구성해야 합니다:
* **로컬 하위 프로세스 (`StdioConnectionParams`):** 표준 입력/출력을 통해 통신하는 로컬 실행 파일 또는 프로세스(예: `npx` 또는 `python`을 통해)를 생성합니다. 독립형 단일 컨테이너 환경에 가장 적합합니다.
* **원격 네트워크 (`StreamableHTTPConnectionParams` / `SseConnectionParams`):** `X-Goog-Api-Key` 또는 `Authorization`과 같은 헤더를 사용하여 HTTP/SSE를 통해 연결합니다. 확장 가능하고 멀티 테넌트이거나 독립적으로 관리되는 MCP 백엔드에 가장 적합합니다.

## 정의 및 수명 주기 규칙
* **프로덕션을 위한 동기식 인스턴스화:** Cloud Run, GKE, Agent Engine 등 멀티 에이전트 설정을 배포할 때 하위 에이전트와 해당 `McpToolset`은 비동기 팩토리 함수 내부가 아니라 `agent.py`에서 동기식으로 인스턴스화되어야 합니다.
* **세션 지속성 및 복원:** `McpToolset`은 `getstate` 및 `setstate`를 통한 직렬화를 지원합니다. 세션 상태는 수명 주기 이벤트 전반에 걸쳐 보존되지만, 에이전트 프로세스가 복원될 때 MCP 소켓/stdio 연결은 동적으로 다시 초기화됩니다.
* **정리 관리:** 커스텀 런타임에서 `adk web` 외부로 실행할 때 `toolset.close()` 또는 exit stack을 통한 명시적 정리를 사용하면 백그라운드 서버 하위 프로세스 및 네트워크 연결이 깔끔하게 종료됩니다.
