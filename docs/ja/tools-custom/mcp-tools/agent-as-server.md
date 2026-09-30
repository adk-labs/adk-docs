# ADK エージェントを MCP サーバーとして構成

ADK エージェントの機能を MCP サーバー内でホストすることにより、Antigravity、Claude Code、カスタム エージェントなどの外部 MCP クライアントから利用できるようにすることができます。
これを実現するには、主に 2 つの方法があります。

* **エージェント全体を公開:** シンプルな 1 行の変換を使用して、マルチターンのエージェント推論全体と内部ツール実行をサーバーにラップします。

* **個々のツールを公開:** エージェントの推論ループなしで、特定のスタンドアロン ADK ツール（`FunctionTool` など）をラップする軽量の MCP サーバーを手動で構築します。

## はじめに
最も強力なアプローチは、`LlmAgent` 全体を公開することです。`to_mcp_server()` ユーティリティを使用すると、エージェントを標準の FastMCP サーバーに変換できます。これにより、外部クライアントはエージェントの完全な認知的機能および内部ツールキットと対話できるようになります。

```python
from google.adk.agents import LlmAgent
from google.adk.tools.load_web_page import load_web_page
from google.adk.tools.mcp_tool import to_mcp_server

# 1. ADK エージェントを定義する
agent = LlmAgent(
    model="gemini-flash-latest", 
    name="web_reader_agent", 
    instruction="Fetch and summarize web content for the user.", 
    tools=[load_web_page], 
)

# 2. エージェントを MCP サーバーに変換する
app = to_mcp_server(agent)

if __name__ == "__main__":
    # エージェントを標準の stdio MCP サーバーとして実行する
    app.run()
```

## 個々の ADK ツールを公開
エージェントの推論ループ全体を使用せずに、個別の機能（特定の `FunctionTool` など）のみを公開したい場合は、手動で MCP サーバーを構築する必要があります。

**前提条件:**
ADK 環境に MCP Server ライブラリをインストールする必要があります。
```bash
pip install mcp
```

**実装手順:**

1. **ツールの初期化:** 公開したい ADK ツールをインスタンス化します（例: `FunctionTool(load_web_page)`）。
2. **ツール一覧ハンドラー:** ツールを通知するために、MCP サーバーの `@app.list_tools()` ハンドラーを実装します。`google.adk.tools.mcp_tool.conversion_utils` の `adk_to_mcp_tool_type` ユーティリティを使用して、ADK ツール定義を MCP スキーマ形式に変換します。
3. **ツール呼び出しハンドラー:** クライアントのリクエストを受信するために、`@app.call_tool()` ハンドラーを実装します。このハンドラーは、リクエストがラップされたツールと一致するかどうかを特定し、ADK ツールの `.run_async()` メソッドを実行し（`tool_context=None` を渡す）、レスポンスを `mcp.types.TextContent` などの MCP 準拠の構造にフォーマットする必要があります。

## ADK ツールを使用した MCP サーバーの構築

1. MCP サーバー用の新しい Python ファイルを作成します（例: `my_adk_mcp_server.py`）。
2. 新しいファイルに次のコードを追加して、サーバー ロジックを実装します。このスクリプトは、ADK の `load_web_page` ツールを公開する MCP サーバーをセットアップします。

```python
import asyncio
import json
import os
from dotenv import load_dotenv

# MCP Server のインポート
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio 

# ADK Tool のインポート
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.load_web_page import load_web_page 
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

load_dotenv()

# 1. ADK ツールを準備する
adk_tool_to_expose = FunctionTool(load_web_page)

# 2. MCP サーバー インスタンスを作成する
app = Server("adk-tool-exposing-mcp-server")

# 3. list_tools ハンドラーを実装する
@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    mcp_tool_schema = adk_to_mcp_tool_type(adk_tool_to_expose)
    return [mcp_tool_schema]

# 4. call_tool ハンドラーを実装する
@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    if name == adk_tool_to_expose.name:
        try:
            # ADK ツールを実行する
            adk_tool_response = await adk_tool_to_expose.run_async(
                args=arguments, 
                tool_context=None,
            )
            # MCP TextContent にフォーマットする
            response_text = json.dumps(adk_tool_response, indent=2)
            return [mcp_types.TextContent(type="text", text=response_text)]
        except Exception as e:
            error_text = json.dumps({"error": str(e)})
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        error_text = json.dumps({"error": f"Tool '{name}' not found."})
        return [mcp_types.TextContent(type="text", text=error_text)]

# 5. MCP サーバー ランナー (Stdio)
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

## 接続と転送モード
これらの MCP サーバーを介して ADK 機能を公開する場合、通常は標準入出力接続（`mcp.server.stdio`）を使用して実行します。この接続により、親プロセスとして実行されている外部クライアント アプリケーションがスクリプトを生成し、stdio ストリーム経由で直接通信できるため、接続の自己完結性と分離性が維持されます。

## ADK エージェントでカスタム MCP サーバーをテストする

カスタム サーバーをテストするには、クライアントとして機能する ADK エージェントを構築する必要があります。このエージェントは `McpToolset` を使用して、作成したサーバー スクリプトへの接続を確立します。

1. `./adk_agent_samples/mcp_client_agent/` などの新しいディレクトリにエージェントをセットアップします。`agent.py` ファイルを作成し、検出可能にするためにその隣に `__init__.py` を含めます。

```python
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 重要: 前の手順で構築したサーバースクリプトへの絶対パスを指定してください
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

2. ターミナルでエージェントの親ディレクトリに移動します。

```bash
cd ./adk_agent_samples
adk web
```

3. ADK Web UI を開き、web_reader_mcp_client_agent を選択します。
4. *Load the content from "https://example.com"* などのプロンプトを使用して接続をテストします。

## Google Cloud Genmedia 向け MCP サーバー

[Genmedia サービス向け MCP ツール](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia) は、Imagen、Veo、Chirp 3 HD 音声、Lyria などの Google Cloud 生成メディア サービスを AI アプリケーションに統合できるようにするオープンソース MCP サーバーのセットです。

Agent Development Kit (ADK) と [Genkit](https://genkit.dev/) はこれらの MCP ツールの組み込みサポートを提供しており、AI エージェントが生成メディア ワークフローを効果的にオーケストレーションできるようにします。実装のガイダンスについては、[ADK サンプル エージェント](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/adk) および [Genkit サンプル](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/genkit) を参照してください。
