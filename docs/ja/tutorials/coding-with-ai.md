# AI と一緒にコーディングする

Agent Development Kit（ADK）ドキュメントは
[`/llms.txt` 標準](https://llmstxt.org/) をサポートしており、
大規模言語モデル（LLM）向けに最適化された機械可読インデックスを提供します。
これにより、AI を活用する開発環境で ADK ドキュメントをコンテキストとして
簡単に利用できます。

## llms.txt とは？

`llms.txt` は、LLM 向けの地図として機能する標準テキストファイルで、
重要なドキュメントページとその説明を一覧化します。
これにより AI ツールは ADK ドキュメント構造を理解し、
質問に答えるための関連情報を取得しやすくなります。

ADK ドキュメントでは、更新のたびに自動生成される
次のファイルを提供しています。

File | Best For... | URL
---- | ----------- | ---
**`llms.txt`** | 動的にリンクを取得できるツール | [`https://google.github.io/adk-docs/llms.txt`](https://google.github.io/adk-docs/llms.txt)
**`llms-full.txt`** | サイト全体の静的テキストダンプを 1 ファイルで必要とするツール | [`https://google.github.io/adk-docs/llms-full.txt`](https://google.github.io/adk-docs/llms-full.txt)

## 開発ツールでの利用

これらのファイルを使うことで、AI コーディングアシスタントに ADK 知識を
与えることができます。これにより、エージェントはタスク計画やコード生成時に
ADK ドキュメントを自律的に検索・参照できます。

### Gemini CLI

[Gemini CLI](https://geminicli.com/) は
[ADK Docs Extension](https://github.com/derailed-dash/adk-docs-ext) を使うよう
設定できます。

**インストール:**

拡張をインストールするには、次のコマンドを実行します。

```bash
gemini extensions install https://github.com/derailed-dash/adk-docs-ext
```

**使い方:**

インストール後、拡張は自動で有効になります。
Gemini CLI で ADK について質問すると、`llms.txt` と ADK ドキュメントを使って
正確な回答やコード生成を行います。

たとえば Gemini CLI で次のように質問できます。

> Agent Development Kit を使って function tool を作るには？

---

### Antigravity

[Antigravity](https://antigravity.google/) IDE は、
ADK の `llms.txt` を参照するカスタム MCP サーバーを実行することで
ADK ドキュメントにアクセスできます。

**前提条件:**

この構成では、手動インストールなしでドキュメントサーバーを実行するため
`uvx` を使用します。[`uv`](https://docs.astral.sh/uv/) をインストールしてください。

**設定:**

1. エディタ上部のエージェントパネルにある **...**（more）メニューから MCP ストアを開きます。
2. **Manage MCP Servers** をクリックします。
3. **View raw config** をクリックします。
4. `mcp_config.json` に次のエントリを追加します。
   これが最初の MCP サーバーなら、コードブロック全体を貼り付けて構いません。

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

MCP サーバー管理の詳細は
[Antigravity MCP ドキュメント](https://antigravity.google/docs/mcp) を参照してください。

**使い方:**

設定後、コーディングエージェントに次のような指示を与えられます。

> ADK ドキュメントを使って、Gemini 2.5 Pro を使うマルチツールエージェントを作って。
> モックの天気検索ツールとカスタム計算ツールを含めて、
> `adk run` で検証して。

---

### Claude Code

[Claude Code](https://code.claude.com/docs/en/overview) は
[MCP サーバー](https://code.claude.com/docs/en/mcp) を追加することで、
ADK ドキュメントを参照できるようになります。

**インストール:**

Claude Code に ADK ドキュメント用 MCP サーバーを追加するには、次のコマンドを実行します。

```bash
claude mcp add adk-docs --transport stdio -- uvx --from mcpdoc mcpdoc --urls AgentDevelopmentKit:https://google.github.io/adk-docs/llms.txt --transport stdio
```

**使い方:**

インストール後、MCP サーバーは自動で有効になります。
Claude Code で ADK について質問すると、`llms.txt` と ADK ドキュメントを使って
正確な回答やコード生成を行います。

たとえば Claude Code で次のように質問できます。

> Agent Development Kit を使って function tool を作るには？

---

### Cursor

[Cursor](https://cursor.com/) IDE は、
ADK の `llms.txt` を参照するカスタム MCP サーバーを実行することで
ADK ドキュメントにアクセスできます。

**前提条件:**

この構成では、手動インストールなしでドキュメントサーバーを実行するため
`uvx` を使用します。[`uv`](https://docs.astral.sh/uv/) をインストールしてください。

**設定:**

1. **Cursor Settings** を開き、**Tools & MCP** タブへ移動します。
2. **New MCP Server** をクリックすると、`mcp.json` 編集画面が開きます。
3. `mcp.json` に次のエントリを追加します。
   これが最初の MCP サーバーなら、コードブロック全体を貼り付けて構いません。

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

MCP サーバー管理の詳細は
[Cursor MCP ドキュメント](https://cursor.com/docs/context/mcp) を参照してください。

**使い方:**

設定後、コーディングエージェントに次のような指示を与えられます。

> ADK ドキュメントを使って、Gemini 2.5 Pro を使うマルチツールエージェントを作って。
> モックの天気検索ツールとカスタム計算ツールを含めて、
> `adk run` で検証して。

---

### その他のツール

`llms.txt` 標準をサポートしている、または URL からドキュメントを取り込める
任意のツールで、これらのファイルを活用できます。
ツールのナレッジベース設定または MCP サーバー設定に
`https://google.github.io/adk-docs/llms.txt`（または `llms-full.txt`）を
指定してください。
