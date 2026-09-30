# MCP ツールを使用するエージェントのデプロイ

MCP ツールを使用する ADK エージェントを Cloud Run、GKE、または Agent Runtime などの本番環境にデプロイする場合、コンテナ化された分散環境で MCP 接続がどのように機能するかを考慮する必要があります。

## 重要なデプロイ要件: 同期的なエージェント定義

!!! warning

    MCP ツールを使用するエージェントをデプロイする場合、エージェントとその `McpToolset` は `agent.py` ファイル内で**同期的**に定義する必要があります。`adk web` では非同期のエージェント作成が可能ですが、デプロイ環境では同期的なインスタンス化が必要です。

```python
# 正しい方法: デプロイ用の同期エージェント定義
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
                timeout=5,  # 適切なタイムアウトを構成する
            ),
            # 本番環境でのセキュリティのためにツールをフィルタリングする
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
# 誤った方法: 非同期パターンはデプロイ環境では機能しません
async def get_agent():  # これはデプロイ環境では機能しません
    toolset = await create_mcp_toolset_async()
    return LlmAgent(tools=[toolset])
```

## クイック デプロイ コマンド

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

## デプロイ パターン

### パターン 1: 自己完結型 Stdio MCP サーバー

npm パッケージや Python モジュール（`@modelcontextprotocol/server-filesystem` など）としてパッケージ化できる MCP サーバーの場合、エージェントのコンテナに直接含めることができます。

**コンテナ要件:**
```dockerfile
# npm ベースの MCP サーバーの例
FROM python:3.13-slim

# MCP サーバー用の Node.js と npm をインストール
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Python の依存関係をインストール
COPY requirements.txt .
RUN pip install -r requirements.txt

# エージェント コードをコピー
COPY . .

# エージェントは 'npx' コマンドで StdioConnectionParams を使用できるようになります
CMD ["python", "main.py"]
```

**エージェント構成:**
```python
# npx と MCP サーバーが同じ環境で実行されるため、コンテナ内で機能します
McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "@modelcontextprotocol/server-filesystem", "/app/data"],
        ),
    ),
)
```

### パターン 2: リモート MCP サーバー (Streamable HTTP)

スケーラビリティを必要とする本番環境へのデプロイでは、MCP サーバーを個別のサービスとしてデプロイし、Streamable HTTP 経由で接続します。

**MCP サーバーのデプロイ (Cloud Run):**
```python
# deploy_mcp_server.py - Streamable HTTP を使用する個別の Cloud Run サービス
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
    """MCP サーバーを作成して構成します。"""
    app = Server("adk-mcp-streamable-server")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
        """MCP クライアントからのツール呼び出しを処理します。"""
        # ツールの実装例 - 実際の ADK ツールに置き換えてください
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
        """使用可能なツールを一覧表示します。"""
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
    """メイン サーバー関数。"""
    logging.basicConfig(level=logging.INFO)

    app = create_mcp_server()

    # スケーラビリティのためにステートレス モードでセッション マネージャーを作成
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=None,
        json_response=json_response,
        stateless=True,  # Cloud Run のスケーラビリティに重要
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """セッション マネージャーのライフサイクルを管理します。"""
        async with session_manager.run():
            logger.info("MCP Streamable HTTP server started!")
            try:
                yield
            finally:
                logger.info("MCP server shutting down...")

    # ASGI アプリケーションの作成
    starlette_app = Starlette(
        debug=False,  # 本番環境では False に設定
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

**リモート MCP 用のエージェント構成:**

=== "Python"

    ```python
    # ADK エージェントは Streamable HTTP 経由でリモート MCP サービスに接続します
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

    // ADK エージェントは Streamable HTTP 経由でリモート MCP サービスに接続します
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

    // ADK エージェントは Streamable HTTP 経由でリモート MCP サービスに接続します
    // headerProvider は suspend 関数のため、fetchToken() はリクエストごとに新しいトークンを待機できます。
    // またセッションの再利用を無効化するため、固定トークンの場合は StreamableHttp(headers = ...) を使用してください。
    val toolset =
        McpToolset.McpToolsetConfig(
            streamableHttpConnectionParams =
                McpConnectionParameters.StreamableHttp(
                    url = "https://your-mcp-server-url.run.app/mcp",
                ),
        ).toToolset(headerProvider = { mapOf("Authorization" to "Bearer ${fetchToken()}") })
    ```

### パターン 3: サイドカー MCP サーバー (GKE)

Kubernetes 環境では、MCP サーバーをサイドカー コンテナとしてデプロイできます。

```yaml
# deployment.yaml - MCP サイドカーを含む GKE
apiVersion: apps/v1
kind: Deployment
metadata:
  name: adk-agent-with-mcp
spec:
  template:
    spec:
      containers:
      # メインの ADK エージェント コンテナ
      - name: adk-agent
        image: your-adk-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: MCP_SERVER_URL
          value: "http://localhost:8081"

      # MCP サーバー サイドカー
      - name: mcp-server
        image: your-mcp-server:latest
        ports:
        - containerPort: 8081
```

## 接続管理に関する考慮事項

スケーリングとインフラストラクチャのニーズに基づいて接続タイプを選択してください。

### Stdio 接続
*   **メリット:** セットアップが簡単、プロセス分離、コンテナ内で適切に動作。
*   **デメリット:** プロセス オーバーヘッド。大規模デプロイには不向き。
*   **最適な用途:** 開発環境、シングルテナント デプロイ、およびシンプルな MCP サーバー。

### SSE/HTTP 接続
*   **メリット:** ネットワーク ベース、スケーラブル、複数クライアントの処理が可能。
*   **デメリット:** ネットワーク インフラストラクチャと認証の複雑さが必要。
*   **最適な用途:** 本番環境デプロイ、マルチテナント システム、外部 MCP サービス、およびトラフィックの多い環境。

## 本番環境デプロイのガイドライン

MCP ツールを使用するエージェントを本番環境にデプロイする場合は、以下の主要なガイドラインに従ってください。

### 接続のライフサイクル
*   標準的な exit stack パターンを使用して MCP 接続を適切にクリーンアップします。
*   接続の確立とリクエストに対して適切なタイムアウトを構成します。
*   一時的な接続障害を適切に処理するために再試行ロジックを実装します。

### リソース管理
*   各接続が新しいプロセスを生成するため、stdio MCP サーバーのメモリ使用量を綿密に監視します。
*   MCP サーバー プロセスに対して適切な CPU およびメモリ制限を構成します。
*   リソース消費を最適化するために、リモート MCP サーバーの接続プーリングを実装します。

### セキュリティ
!!! important "セキュリティのベスト プラクティス"
    *   すべてのリモート MCP 接続に厳格な認証ヘッダーを使用してください。
    *   ADK エージェントと MCP サーバー間のネットワーク アクセスを厳密に制限してください。
    *   `tool_filter` を使用して、公開されるツール機能を厳格に制限してください。
    *   プロンプトやコマンドのインジェクション攻撃を防ぐために、すべての MCP ツール入力を検証してください。
    *   ファイルシステム MCP サーバーには、制限された絶対ファイル パスを使用してください（例: `os.path.dirname(os.path.abspath(__file__))`）。
    *   可能な限り、本番環境では読み取り専用ツール フィルターを適用してください。

### 監視と可観測性
*   すべての MCP 接続の確立および破棄イベントをログに記録します。
*   MCP ツールの実行時間と全体的な成功率を監視します。
*   再発する MCP 接続障害に対して自動アラートを設定します。
