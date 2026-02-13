---
catalog_title: Cartesia
catalog_description: 音声生成、音声ローカライズ、オーディオコンテンツ作成を行います
catalog_icon: /adk-docs/integrations/assets/cartesia.png
catalog_tags: ["mcp"]
---

# ADK 向け Cartesia MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Cartesia MCP Server](https://github.com/cartesia-ai/cartesia-mcp) は
ADK エージェントを [Cartesia](https://cartesia.ai/) の AI オーディオプラットフォームへ接続します。
この連携により、エージェントは自然言語で音声生成、
言語間の音声ローカライズ、オーディオコンテンツ作成を行えます。

## ユースケース

- **テキスト読み上げ (TTS) 生成**: Cartesia の多様な音声ライブラリを使って
  テキストを自然な音声に変換し、音声選択や出力形式を細かく制御します。

- **音声ローカライズ**: 既存の音声を別言語へ変換しつつ、
  元話者の特徴を保持します。多言語コンテンツ制作に最適です。

- **オーディオインフィル**: オーディオセグメント間の空白を埋めて
  滑らかな遷移を作成します。ポッドキャスト編集やオーディオブック制作に有用です。

- **音声変換**: オーディオクリップを Cartesia ライブラリ内の別の声に変換します。

## 前提条件

- [Cartesia アカウント](https://play.cartesia.ai/sign-in) の作成
- Cartesia playground で [API キー](https://play.cartesia.ai/keys) を生成

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        CARTESIA_API_KEY = "YOUR_CARTESIA_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="cartesia_agent",
            instruction="Help users generate speech and work with audio content",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["cartesia-mcp"],
                            env={
                                "CARTESIA_API_KEY": CARTESIA_API_KEY,
                                # "OUTPUT_DIRECTORY": "/path/to/output",  # Optional
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

        const CARTESIA_API_KEY = "YOUR_CARTESIA_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "cartesia_agent",
            instruction: "Help users generate speech and work with audio content",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["cartesia-mcp"],
                        env: {
                            CARTESIA_API_KEY: CARTESIA_API_KEY,
                            // OUTPUT_DIRECTORY: "/path/to/output",  // Optional
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

Tool | Description
---- | -----------
`text_to_speech` | 指定した音声でテキストを音声へ変換
`list_voices` | 利用可能な Cartesia 音声一覧を取得
`get_voice` | 特定音声の詳細取得
`clone_voice` | 音声サンプルから音声クローン作成
`update_voice` | 既存音声を更新
`delete_voice` | ライブラリから音声を削除
`localize_voice` | 音声を別言語へ変換
`voice_change` | 音声ファイルを別音声へ変換
`infill` | 音声セグメント間の空白を補完

## 設定

Cartesia MCP サーバーは環境変数で設定できます:

Variable | Description | Required
-------- | ----------- | --------
`CARTESIA_API_KEY` | Cartesia API キー | Yes
`OUTPUT_DIRECTORY` | 生成オーディオを保存するディレクトリ | No

## 追加リソース

- [Cartesia MCP Server Repository](https://github.com/cartesia-ai/cartesia-mcp)
- [Cartesia MCP Documentation](https://docs.cartesia.ai/integrations/mcp)
- [Cartesia Playground](https://play.cartesia.ai/)
