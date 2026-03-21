---
catalog_title: GoodMem
catalog_description: Add persistent semantic memory to agents across conversations
catalog_icon: /adk-docs/integrations/assets/goodmem.svg
catalog_tags: ["data"]
---

# ADK 向け GoodMem プラグイン

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[GoodMem ADK プラグイン](https://github.com/PAIR-Systems-Inc/goodmem-adk) は、
[GoodMem](https://goodmem.ai) に ADK エージェントを接続します。GoodMem は
ベクトルベースのセマンティックメモリサービスです。この統合により、エージェントは
会話をまたいで永続的かつ検索可能なメモリを持ち、過去のやり取り、ユーザーの
好み、アップロード済みドキュメントを想起できるようになります。

統合方法は 2 つあります。

| 方法 | 説明 |
|----------|-------------|
| **Plugin** (`GoodmemPlugin`) | ADK のコールバックを通じて、各ターンで暗黙的かつ決定論的にメモリを管理します。会話ターンとファイル添付を自動的に保存します。 |
| **Tools** (`GoodmemSaveTool`, `GoodmemFetchTool`) | 明示的でエージェント主導のメモリ管理です。保存と取得のタイミングをエージェントが決定します。 |

## ユースケース

- **エージェント向けの永続メモリ**: 会話をまたいで頼れる長期記憶を
  エージェントに与えます。
- **ハンズフリーなマルチモーダルメモリ管理**: ユーザーメッセージ、エージェント
  応答、ファイル添付（PDF、DOCX など）を含む会話情報を自動的に保存し、取得します。
- **毎回ゼロから始めない**: エージェントは、誰なのか、何を話したのか、すでに
  どんな解決策を試したのかを覚えており、トークンを節約し、重複作業を避けられます。

## 前提条件

- [GoodMem](https://goodmem.ai/quick-start) のインスタンス（セルフホストまたはクラウド）
- GoodMem API キー
- [Gemini API キー](https://aistudio.google.com/app/api-keys)（Gemini による埋め込みの自動生成用）

## インストール

```bash
pip install goodmem-adk
```

## エージェントでの利用

=== "Plugin (Automatic memory)"

    ```python
    import os
    from google.adk.agents import LlmAgent
    from google.adk.apps import App
    from goodmem_adk import GoodmemPlugin

    plugin = GoodmemPlugin(
        base_url=os.getenv("GOODMEM_BASE_URL"),  # e.g. "http://localhost:8080"
        api_key=os.getenv("GOODMEM_API_KEY"),
        top_k=5,  # Number of memories to retrieve per turn
    )

    agent = LlmAgent(
        name="memory_agent",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant with persistent memory.",
    )

    app = App(name="GoodmemPluginDemo", root_agent=agent, plugins=[plugin])
    ```

=== "Tools (Agent-controlled memory)"

    ```python
    import os
    from google.adk.agents import LlmAgent
    from google.adk.apps import App
    from goodmem_adk import GoodmemSaveTool, GoodmemFetchTool

    save_tool = GoodmemSaveTool(
        base_url=os.getenv("GOODMEM_BASE_URL"),  # e.g. "http://localhost:8080"
        api_key=os.getenv("GOODMEM_API_KEY"),
    )
    fetch_tool = GoodmemFetchTool(
        base_url=os.getenv("GOODMEM_BASE_URL"),
        api_key=os.getenv("GOODMEM_API_KEY"),
        top_k=5,
    )

    agent = LlmAgent(
        name="memory_agent",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant with persistent memory.",
        tools=[save_tool, fetch_tool],
    )

    app = App(name="GoodmemToolsDemo", root_agent=agent)
    ```

## 利用可能なツール

### プラグインコールバック

`GoodmemPlugin` は ADK コールバックを使用してメモリを自動的に管理します。

Callback | 説明
-------- | -----------
`on_user_message_callback` | ユーザーメッセージとファイル添付をメモリに保存する
`before_model_callback` | 関連するメモリを取得し、プロンプトに注入する
`after_model_callback` | エージェント応答をメモリに保存する

これらのコールバックは決定論的で、各エージェント対話中に実行され、エージェントを
通過するすべての情報をメモリに保存します。何を保存または取得するかを、エージェントが
決定する必要はありません。

### ツール

ツール方式を使う場合、エージェントは次のツールを利用できます。

Tool | 説明
---- | -----------
`goodmem_save` | テキスト内容とファイル添付を永続メモリに保存する
`goodmem_fetch` | セマンティック類似度クエリを使ってメモリを検索する

これらのツールは必要に応じてエージェントから呼び出され、会話コンテキストに応じて
保存（必要なら書き換え付き）や取得のタイミングをエージェントが選択できます。

## 設定

### 環境変数

Variable | 必須 | 説明
-------- | -------- | -----------
`GOODMEM_BASE_URL` | Yes | GoodMem サーバーの URL (`/v1` サフィックスなし)
`GOODMEM_API_KEY` | Yes | GoodMem の API キー
`GOOGLE_API_KEY` | Yes | Gemini 埋め込みを自動作成するための Gemini API キー
`GOODMEM_EMBEDDER_ID` | No | 特定の embedder を固定する（存在している必要があります）
`GOODMEM_SPACE_ID` | No | 特定の memory space を固定する（存在している必要があります）
`GOODMEM_SPACE_NAME` | No | デフォルトの space 名を上書きする（存在しない場合は自動作成）

### Space resolution

If no space is configured, one is auto-created per user:

- Plugin: `adk_chat_{user_id}`
- Tools: `adk_tool_{user_id}`

## Additional resources

- [GoodMem ADK on GitHub](https://github.com/PAIR-Systems-Inc/goodmem-adk)
- [GoodMem Documentation](https://goodmem.ai)
- [GoodMem ADK on PyPI](https://pypi.org/project/goodmem-adk/)
