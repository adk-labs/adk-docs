---
catalog_title: ElevenLabs
catalog_description: 音声生成、音声クローン、音声文字起こし、効果音生成を行います
catalog_icon: /adk-docs/integrations/assets/elevenlabs.png
catalog_tags: ["mcp"]
---

# ADK 向け ElevenLabs MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[ElevenLabs MCP Server](https://github.com/elevenlabs/elevenlabs-mcp) は
ADK エージェントを [ElevenLabs](https://elevenlabs.io/) AI オーディオプラットフォームへ接続します。
この連携により、エージェントは自然言語で音声生成、
音声クローン、音声文字起こし、効果音生成、
会話型 AI 体験の構築を行えます。


## ユースケース

- **テキスト読み上げ (TTS) 生成**: 多様な音声を使ってテキストを自然音声へ変換し、
  stability、style、similarity を細かく制御できます。

- **音声クローンと設計**: 音声サンプルから声を複製したり、
  年齢/性別/アクセント/トーンなど希望特性をテキスト記述して新しい声を生成できます。

- **音声処理**: 背景ノイズから音声を分離し、
  別の声に変換したり、話者識別付きで音声をテキスト化できます。

- **効果音とサウンドスケープ**: テキスト記述から効果音や環境音を生成できます。
  例: 「動物が天候に反応する、密林の雷雨」。

## 前提条件

- [ElevenLabs account](https://elevenlabs.io/app/sign-up) の作成
- アカウント設定で [API key](https://elevenlabs.io/app/settings/api-keys) を生成

## エージェントで使う

=== "Python"

    === "Local MCP Server"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="elevenlabs_agent",
            instruction="Help users generate speech, clone voices, and process audio",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="uvx",
                            args=["elevenlabs-mcp"],
                            env={
                                "ELEVENLABS_API_KEY": ELEVENLABS_API_KEY,
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

        const ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "elevenlabs_agent",
            instruction: "Help users generate speech, clone voices, and process audio",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "uvx",
                        args: ["elevenlabs-mcp"],
                        env: {
                            ELEVENLABS_API_KEY: ELEVENLABS_API_KEY,
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 利用可能なツール

### テキスト読み上げと音声

Tool | Description
---- | -----------
`text_to_speech` | 指定音声でテキストから音声を生成
`speech_to_speech` | 音声を別の声に変換
`text_to_voice` | テキスト説明から音声プレビュー生成
`create_voice_from_preview` | 生成した音声プレビューをライブラリへ保存
`voice_clone` | 音声サンプルから声を複製
`get_voice` | 特定音声の詳細取得
`search_voices` | ライブラリ内音声検索
`search_voice_library` | 公開音声ライブラリ検索
`list_models` | 利用可能 TTS モデル一覧

### 音声処理

Tool | Description
---- | -----------
`speech_to_text` | 話者識別付き音声文字起こし
`text_to_sound_effects` | テキスト説明から効果音生成
`isolate_audio` | 背景ノイズ/音楽から音声を分離
`play_audio` | ローカルで音声ファイル再生
`compose_music` | 説明から音楽生成
`create_composition_plan` | 作曲プラン作成

### 会話型 AI

Tool | Description
---- | -----------
`create_agent` | 会話型 AI エージェント作成
`get_agent` | 特定エージェント詳細取得
`list_agents` | 会話型 AI エージェント一覧
`add_knowledge_base_to_agent` | エージェントへナレッジベース追加
`make_outbound_call` | エージェントで発信通話を開始
`list_phone_numbers` | 利用可能電話番号一覧
`get_conversation` | 特定会話の詳細取得
`list_conversations` | 会話一覧

### アカウント

Tool | Description
---- | -----------
`check_subscription` | サブスクリプションとクレジット利用状況を確認

## 設定

ElevenLabs MCP サーバーは環境変数で設定できます:

Variable | Description | Default
-------- | ----------- | -------
`ELEVENLABS_API_KEY` | ElevenLabs API キー | Required
`ELEVENLABS_MCP_BASE_PATH` | ファイル操作のベースパス | `~/Desktop`
`ELEVENLABS_MCP_OUTPUT_MODE` | 生成ファイルの返却方法 | `files`
`ELEVENLABS_API_RESIDENCY` | データ居住リージョン (enterprise のみ) | `us`

### 出力モード

`ELEVENLABS_MCP_OUTPUT_MODE` は 3 モードをサポートします:

- **`files`** (デフォルト): ファイルをディスク保存しパスを返す
- **`resources`**: MCP リソース (base64 バイナリ) として返す
- **`both`**: ディスク保存と MCP リソース返却の両方

## 追加リソース

- [ElevenLabs MCP Server Repository](https://github.com/elevenlabs/elevenlabs-mcp)
- [Introducing ElevenLabs MCP](https://elevenlabs.io/blog/introducing-elevenlabs-mcp)
- [ElevenLabs Documentation](https://elevenlabs.io/docs)
