# AI と一緒にコーディングする

AI コーディングアシスタントを使って Agent Development Kit（ADK）で
エージェントを構築できます。プロジェクトに開発スキルをインストールするか、
MCP サーバー経由で ADK ドキュメントを接続することで、コーディング
エージェントに ADK の専門知識を与えられます。

- [**ADK Skills**](#adk-skills): ADK 開発スキルをプロジェクトへ直接
  インストールします。
- [**ADK Docs MCP Server**](#adk-docs-mcp-server): MCP サーバー経由で
  コーディングツールを ADK ドキュメントへ接続します。
- [**ADK Docs Index**](#adk-docs-index): `llms.txt` 標準に従う機械可読な
  ドキュメントファイルです。

## ADK Skills

ADK は、API、コーディングパターン、デプロイ、評価をカバーする開発用
[skills](https://agentskills.io/) セットを提供します。これらのスキルは
Gemini CLI、Antigravity、Claude Code、Cursor を含む互換ツールで
利用できます。

ADK 開発スキルをインストールするには、プロジェクトディレクトリで次を
実行します。

```bash
npx skills add google/adk-docs/skills -y
```

次を含む [GitHub 上の ADK
skills](https://github.com/google/adk-docs/tree/main/skills) を参照して
ください。

| Skill | 説明 |
|-------|------|
| `adk-cheatsheet` | Python API クイックリファレンスとドキュメントインデックス |
| `adk-deploy-guide` | Agent Engine と Cloud Run のデプロイ |
| `adk-dev-guide` | 開発ライフサイクルとコーディングガイドライン |
| `adk-eval-guide` | 評価手法とスコアリング |
| `adk-observability-guide` | トレーシング、ロギング、統合 |
| `adk-scaffold` | プロジェクトスキャフォールディング |

## ADK Docs MCP Server

MCP サーバーを使うようにコーディングツールを設定すれば、ADK ドキュメントを
検索して読み込めます。以下は一般的なツール向けの設定手順です。

### Gemini CLI

[Gemini CLI](https://geminicli.com/) に ADK ドキュメント MCP サーバーを
追加するには、[ADK Docs
Extension](https://github.com/derailed-dash/adk-docs-ext) をインストール
します。

```bash
gemini extensions install https://github.com/derailed-dash/adk-docs-ext
```

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
            "AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt",
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
claude mcp add adk-docs --transport stdio -- uvx --from mcpdoc mcpdoc --urls AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt --transport stdio
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
            "AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt",
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
| `llms.txt` | リンク付きのドキュメントインデックス | [`google.github.io/adk-docs/llms.txt`](https://google.github.io/adk-docs/llms.txt) |
| `llms-full.txt` | ドキュメント全体を 1 ファイルで提供 | [`google.github.io/adk-docs/llms-full.txt`](https://google.github.io/adk-docs/llms-full.txt) |
