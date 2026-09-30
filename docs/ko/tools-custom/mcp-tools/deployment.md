# MCP 툴을 사용하는 에이전트 배포

MCP 툴을 사용하는 ADK 에이전트를 Cloud Run, GKE, Agent Runtime과 같은 프로덕션 환경에 배포할 때는 컨테이너화 및 분산 환경에서 MCP 연결이 어떻게 작동할지 고려해야 합니다.

## 핵심 배포 요구사항: 동기식 에이전트 정의

!!! warning

    MCP 툴을 사용하는 에이전트를 배포할 때 에이전트와 해당 `McpToolset`은 `agent.py` 파일에서 **동기식**으로 정의되어야 합니다. `adk web`은 비동기식 에이전트 생성을 허용하지만 배포 환경에서는 동기식 인스턴스화가 필요합니다.

```python
# 올바른 방법: 배포를 위한 동기식 에이전트 정의
import os
from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

_allowed_path = os.path.dirname(os.path.abspath(__file__))

root_agent = LlmAgent(
    model='gemini-flash-latest',
    name='enterprise_assistant',
    instruction=f'Help user accessing their file systems. Allowed directory: {_allowed_path}',
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=['-y', '@modelcontextprotocol/server-filesystem', _allowed_path],
                ),
                timeout=5,  # 적절한 타임아웃 구성
            ),
            # 프로덕션 환경에서의 보안을 위해 툴 필터링
            tool_filter=[
                'read_file', 'read_multiple_files', 'list_directory',
                'directory_tree', 'search_files', 'get_file_info',
                'list_allowed_directories',
            ],
        )
    ],
)
```

```python
# 잘못된 방법: 비동기 패턴은 배포 환경에서 작동하지 않음
async def get_agent():  # 배포 환경에서는 작동하지 않습니다
    toolset = await create_mcp_toolset_async()
    return LlmAgent(tools=[toolset])
```

## 빠른 배포 명령어

### Agent Runtime
```bash
uv run adk deploy agent_engine \
  --project=<your-gcp-project-id> \
  --region=<your-gcp-region> \
  --display_name="My MCP Agent" \
  ./path/to/your/agent_directory
```

### Cloud Run
```bash
uv run adk deploy cloud_run \
  --project=<your-gcp-project-id> \
  --region=<your-gcp-region> \
  --service_name=<your-service-name> \
  ./path/to/your/agent_directory
```

## 배포 패턴

### 패턴 1: 자체 완결형 Stdio MCP 서버

npm 패키지나 Python 모듈(예: `@modelcontextprotocol/server-filesystem`)로 패키징할 수 있는 MCP 서버의 경우 에이전트 컨테이너에 직접 포함할 수 있습니다:

**컨테이너 요구사항:**
```dockerfile
# npm 기반 MCP 서버 예시
FROM python:3.13-slim

# MCP 서버를 위한 Node.js 및 npm 설치
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 에이전트 코드 복사
COPY . .

# 에이전트가 이제 'npx' 명령어로 StdioConnectionParams를 사용할 수 있습니다
CMD ["python", "main.py"]
```

**에이전트 구성:**
```python
# npx와 MCP 서버가 동일한 환경에서 실행되므로 컨테이너에서 정상 작동합니다
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-filesystem", "/app/data"],
        ),
    ),
)
```

### 패턴 2: 원격 MCP 서버 (Streamable HTTP)

확장성이 필요한 프로덕션 배포의 경우 MCP 서버를 별도의 서비스로 배포하고 Streamable HTTP를 통해 연결합니다:

**MCP 서버 배포 (Cloud Run):**
```python
# deploy_mcp_server.py - Streamable HTTP를 사용하는 별도의 Cloud Run 서비스
import contextlib
import logging
from collections.abc import AsyncIterator
from typing import Any

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

logger = logging.getLogger(__name__)

def create_mcp_server():
    """MCP 서버를 생성하고 구성합니다."""
    app = Server("adk-mcp-streamable-server")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
        """MCP 클라이언트의 툴 호출을 처리합니다."""
        # 툴 구현 예시 - 실제 ADK 툴로 교체하십시오
        if name == "example_tool":
            result = arguments.get("input", "No input provided")
            return [
                types.TextContent(
                    type="text",
                    text=f"Processed: {result}"
                )
            ]
        else:
            raise ValueError(f"Unknown tool: {name}")

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """사용 가능한 툴 목록을 반환합니다."""
        return [
            types.Tool(
                name="example_tool",
                description="Example tool for demonstration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Input text to process"
                        }
                    },
                    "required": ["input"]
                }
            )
        ]

    return app

def main(port: int = 8080, json_response: bool = False):
    """메인 서버 함수."""
    logging.basicConfig(level=logging.INFO)

    app = create_mcp_server()

    # 확장성을 위해 stateless 모드로 세션 매니저 생성
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=json_response,
        stateless=True,  # Cloud Run 확장성에 중요
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """세션 매니저 수명 주기 관리."""
        async with session_manager.run():
            logger.info("MCP Streamable HTTP server started!")
            try:
                yield
            finally:
                logger.info("MCP server shutting down...")

    # ASGI 애플리케이션 생성
    starlette_app = Starlette(
        debug=False,  # 프로덕션에서는 False로 설정
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    import uvicorn
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
```

**원격 MCP용 에이전트 구성:**

=== "Python"

    ```python
    # ADK 에이전트가 Streamable HTTP를 통해 원격 MCP 서비스에 연결합니다
    McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://your-mcp-server-url.run.app/mcp",
            headers={"Authorization": "Bearer your-auth-token"}
        ),
    )
    ```

=== "Java"

    ```java
    import java.util.Map;
    import com.google.adk.tools.mcp.StreamableHttpServerParameters;
    import com.google.adk.tools.mcp.McpToolset;

    // ADK 에이전트가 Streamable HTTP를 통해 원격 MCP 서비스에 연결합니다
    StreamableHttpServerParameters streamableParams = StreamableHttpServerParameters.builder()
            .url("https://your-mcp-server-url.run.app/mcp")
            .headers(Map.of("Authorization", "Bearer your-auth-token"))
            .build();

    McpToolset toolset = new McpToolset(streamableParams);
    ```

=== "Kotlin"

    ```kotlin
    import com.google.adk.kt.tools.mcp.McpConnectionParameters
    import com.google.adk.kt.tools.mcp.McpToolset

    // ADK 에이전트가 Streamable HTTP를 통해 원격 MCP 서비스에 연결합니다
    // headerProvider는 suspend 함수이므로 fetchToken()이 요청당 최신 토큰을 기다릴 수 있습니다;
    // 또한 세션 재사용을 비활성화하므로 고정된 토큰의 경우 StreamableHttp(headers = ...)를 사용하십시오.
    val toolset =
        McpToolset.McpToolsetConfig(
            streamableHttpConnectionParams =
                McpConnectionParameters.StreamableHttp(
                    url = "https://your-mcp-server-url.run.app/mcp",
                ),
        ).toToolset(headerProvider = { mapOf("Authorization" to "Bearer ${fetchToken()}") })
    ```

### 패턴 3: 사이드카 MCP 서버 (GKE)

Kubernetes 환경에서는 MCP 서버를 사이드카 컨테이너로 배포할 수 있습니다:

```yaml
# deployment.yaml - MCP 사이드카가 포함된 GKE
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent-with-mcp
spec:
  template:
    spec:
      containers:
      # 메인 ADK 에이전트 컨테이너
      - name: adk-agent
        image: your-adk-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: MCP_SERVER_URL
          value: "http://localhost:8081"

      # MCP 서버 사이드카
      - name: mcp-server
        image: your-mcp-server:latest
        ports:
        - containerPort: 8081
```

## 연결 관리 고려사항

확장성 및 인프라 요구에 따라 연결 유형을 선택하십시오.

### Stdio 연결
*   **장점:** 간단한 설정, 프로세스 격리, 컨테이너에서 원활하게 작동.
*   **단점:** 프로세스 오버헤드, 대규모 배포에는 부적합.
*   **적합한 환경:** 개발, 단일 테넌트 배포 및 단순한 MCP 서버.

### SSE/HTTP 연결
*   **장점:** 네트워크 기반, 확장 가능, 여러 클라이언트 처리 가능.
*   **단점:** 네트워크 인프라 및 인증 복잡성 필요.
*   **적합한 환경:** 프로덕션 배포, 멀티 테넌트 시스템, 외부 MCP 서비스 및 대용량 트래픽.

## 프로덕션 배포 가이드라인

MCP 툴이 포함된 에이전트를 프로덕션 환경에 배포할 때는 다음과 같은 핵심 가이드라인을 따르십시오.

### 연결 수명 주기
*   표준 exit stack 패턴을 사용하여 MCP 연결을 올바르게 정리합니다.
*   연결 설정 및 요청에 대해 적절한 타임아웃을 구성합니다.
*   일시적인 연결 실패를 원활하게 처리할 수 있도록 재시도 로직을 구현합니다.

### 리소스 관리
*   각 연결이 새 프로세스를 생성하므로 stdio MCP 서버의 메모리 사용량을 면밀히 모니터링합니다.
*   MCP 서버 프로세스에 적절한 CPU 및 메모리 제한을 구성합니다.
*   리소스 소비를 최적화하기 위해 원격 MCP 서버에 대한 연결 풀링을 구현합니다.

### 보안
!!! important "보안 모범 사례"
    *   모든 원격 MCP 연결에 엄격한 인증 헤더를 사용하십시오.
    *   ADK 에이전트와 MCP 서버 간의 네트워크 접근을 엄격하게 제한하십시오.
    *   `tool_filter`를 사용하여 노출되는 기능을 엄격하게 제한하십시오.
    *   프롬프트 또는 커맨드 인젝션 공격을 방지하기 위해 모든 MCP 툴 입력을 검증하십시오.
    *   파일시스템 MCP 서버에는 제한적인 절대 파일 경로를 사용하십시오(예: `os.path.dirname(os.path.abspath(__file__))`).
    *   가능하면 프로덕션 환경에서 읽기 전용 툴 필터를 적용하십시오.

### 모니터링 및 관찰 가능성
*   모든 MCP 연결 설정 및 해제 이벤트를 로깅합니다.
*   MCP 툴 실행 시간과 전반적인 성공률을 모니터링합니다.
*   반복되는 MCP 연결 실패에 대해 자동 알림을 설정합니다.
