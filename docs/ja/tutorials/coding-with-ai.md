# AI と一緒にコーディングする

AI コーディングアシスタントを使って Agent Development Kit（ADK）で
エージェントを構築できます。プロジェクトに開発スキルをインストールするか、
MCP サーバー経由で ADK ドキュメントを接続することで、コーディング
エージェントに ADK の専門知識を与えられます。

- [**Agent Platform の Agents CLI**](#agents-cli): ADK 開発用のコマンドラインツールとコーディングスキル。
- [**ADK Docs MCP Server**](#adk-docs-mcp-server): MCP サーバー経由で
  コーディングツールを ADK ドキュメントへ接続します。
- [**ADK Docs Index**](#adk-docs-index): `llms.txt` 標準に従う機械可読な
  ドキュメントファイルです。

## Agents CLI {#agents-cli}

[Agents CLI](https://google.github.io/agents-cli/) ツールセットを使用すると、Antigravity、Claude Code、Cursor などの好みの AI コーディング環境やその他の AI コーディングツールに ADK エージェントの専門知識を組み込むことができます。現在の AI 搭載の開発環境に Agents CLI をインストールし、ADK エージェントの テンプレート作成（スキャフォールディング）、構築、テスト、評価、デプロイを行ってください。開発環境で以下の Agents CLI スキルを有効化できます。
*   開発ライフサイクルとコーディングガイドライン
*   プロジェクトのテンプレート作成（スキャフォールディング）
*   評価手法とスコアリング
*   Agent Runtime、Cloud Run、GKE へのデプロイ
*   Gemini Enterprise へのエージェント公開
*   トレース、ロギング、統合
*   Python API クイックリファレンスとドキュメントインデックス

Agents CLI をインストールして ADK 開発スキルをセットアップするには、次を実行します。

```bash
uvx google-agents-cli setup
```

開発環境での Agents CLI のインストールと使用方法の詳細については、[Agents CLI ドキュメント](https://google.github.io/agents-cli/)を参照してください。

## ADK Docs MCP Server

MCP サーバーを使うようにコーディングツールを設定すれば、ADK ドキュメントを
検索して読み込めます。以下は一般的なツール向けの設定手順です。

### Antigravity

[Antigravity](https://antigravity.google/) に ADK ドキュメント MCP サーバーを
追加するには（[`uv`](https://docs.astral.sh/uv/) が必要です）:

1. エディタ上部のエージェントパネルにある **...**（more）メニューから
   MCP ストアを開きます。
2. **Manage MCP Servers** をクリックし、**View raw config** を
   選択します。
3. `mcp_config.json` に次を追加します。

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

[Claude Code](https://code.claude.com/docs/en/overview) に ADK ドキュメント
MCP サーバーを追加するには、次を実行します。

```bash
claude mcp add adk-docs --transport stdio -- uvx --from mcpdoc mcpdoc --urls AgentDevelopmentKit:https://adk.dev/llms.txt --transport stdio
```

### Cursor

[Cursor](https://cursor.com/) に ADK ドキュメント MCP サーバーを追加するには
（[`uv`](https://docs.astral.sh/uv/) が必要です）:

1. **Cursor Settings** を開き、**Tools & MCP** タブに移動します。
2. **New MCP Server** をクリックして `mcp.json` を開きます。
3. `mcp.json` に次を追加します。

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

MCP サーバーをサポートする任意のコーディングツールでも、上記と同じ
サーバー設定を使えます。利用するツールの MCP 設定に合わせて、
Antigravity または Cursor セクションの JSON 例を調整してください。

## ADK Docs Index

ADK ドキュメントは [`llms.txt` 標準](https://llmstxt.org/) に従う
機械可読ファイルとして提供されます。これらのファイルはドキュメント更新の
たびに生成され、常に最新状態に保たれます。

| File | Description | URL |
|------|-------------|-----|
| `llms.txt` | リンク付きのドキュメントインデックス | [`adk.dev/llms.txt`](https://adk.dev/llms.txt) |
| `llms-full.txt` | ドキュメント全体を 1 ファイルで提供 | [`adk.dev/llms-full.txt`](https://adk.dev/llms-full.txt) |
