---
catalog_title: Atlan
catalog_description: メタデータ、リネージ、ビジネスナレッジを検索、探索、ガバナンス管理します
catalog_icon: /integrations/assets/atlan.png
catalog_tags: ["mcp"]
---

# ADK 向け Atlan MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Atlan MCP Server](https://github.com/atlanhq/agent-toolkit) は ADK エージェントを、
エンタープライズ AI 向けのコンテキストレイヤーである
[Atlan](https://www.atlan.com/) に接続します。これによりエージェントは、AI
エージェントが効果的に処理を行うために必要な知識、データ、セマンティクスを備えた
組織のコンテキストリポジトリにアクセスできます。この統合により、エージェントは
エンタープライズコンテキストの検索と検出、エンドツーエンドのリネージ探索、ガバナンス管理された
データ定義や用語集（グロッサリー）へのアクセス、SQL の実行、メタデータグラフの整備、
データ品質の確保を行えるようになり、すべてのエージェントタスクを信頼できる組織コンテキストに
グラウンディング（Grounding）できます。

## ユースケース

- **エンタープライズコンテキストの検索と検出**: 自然言語を使って、技術スタック全体の
  テーブル、カラム、ダッシュボード、用語集の用語、データプロダクトを見つけます。

- **エンドツーエンドのリネージ探索**: システム全体でデータフローを上流（upstream）および
  下流（downstream）に追跡し、スキーマ変更の前に依存関係を把握します。

- **ガバナンス管理されたデータ定義へのアクセス**: 用語集、データドメイン、認定済み
  メタデータを使って、エージェントの出力を信頼できる組織コンテキストにグラウンディングします。

- **メタデータグラフの整備**: 説明の更新、アセットの認定、用語集の管理、
  データ品質ルールとスケジュールの定義、SQL の実行までをすべてエージェントから行います。

## 前提条件

- [Atlan](https://atlan.com/) テナント
- クエリ対象のアセットへアクセスする権限を持つ Atlan アカウント
- ローカルにインストールされた Node.js（ホスト型 MCP サーバーへブリッジ接続する
  `mcp-remote` で使用）

## エージェントでの使用

=== "Python"

    === "ローカル MCP サーバー"

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters


        root_agent = Agent(
            model="gemini-flash-latest",
            name="atlan_agent",
            instruction="Help users search, discover, and manage enterprise data assets using Atlan",
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.atlan.com/mcp",
                            ]
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "ローカル MCP サーバー"

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-flash-latest",
            name: "atlan_agent",
            instruction: "Help users search, discover, and manage enterprise data assets using Atlan",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.atlan.com/mcp",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

!!! note

    このエージェントを初めて実行すると、OAuth でアクセスを要求するために
    ブラウザーウィンドウが自動的に開きます。代わりに、コンソールに表示される
    認可 URL を使用することもできます。エージェントが Atlan テナントにアクセス
    できるよう、この要求を承認する必要があります。

## 利用可能なツール

### 検出と検索

ツール | 説明
---- | -----------
`semantic_search_tool` | AI によるセマンティック理解を使って、すべてのデータアセットを自然言語で検索します
`search_assets_tool` | 構造化されたフィルタと条件でアセットを検索します
`traverse_lineage_tool` | アセットのデータフローを上流（ソース）または下流（コンシューマー）へ追跡します
`query_assets_tool` | 接続済みデータソースに対して SQL クエリを実行します
`get_asset_tool` | GUID または完全修飾名（qualified name）を指定して、単一アセットの詳細情報（カスタムメタデータ、データ品質チェック、README を含む）を取得します
`resolve_metadata_tool` | 名前または説明からメタデータエンティティ（ユーザー、分類、カスタムメタデータセット、用語集、ドメイン、データプロダクト）を検出します
`get_groups_tool` | ワークスペースグループとそのメンバーを一覧表示します
`search_atlan_docs_tool` | Atlan の製品ドキュメントを検索し、出典の引用付きで LLM 生成の回答を返します

### アセット更新

ツール | 説明
---- | -----------
`update_assets_tool` | アセットの説明、認定ステータス、README、または用語を更新します
`manage_announcements_tool` | アセットにアナウンス（情報、警告、問題）を追加または削除します
`manage_asset_lifecycle_tool` | アセットをアーカイブ、復元、または完全削除（パージ）します

### 用語集とドメイン

ツール | 説明
---- | -----------
`create_glossaries` | 新しい用語集を作成します
`create_glossary_terms` | 用語集内に用語を作成します
`create_glossary_categories` | 用語集内にカテゴリを作成します
`create_domains` | データドメインとサブドメインを作成します
`create_data_products` | ドメインやアセットに紐づくデータプロダクトを作成します

### データ品質ルール

ツール | 説明
---- | -----------
`create_dq_rules_tool` | データ品質ルール（NULL チェック、一意性、正規表現、カスタム SQL など）を作成します
`update_dq_rules_tool` | 既存のデータ品質ルールを更新します
`schedule_dq_rules_tool` | cron 式を使ってデータ品質ルールの実行をスケジュールします
`delete_dq_rules_tool` | データ品質ルールを削除します

### カスタムメタデータ

ツール | 説明
---- | -----------
`create_custom_metadata_set_tool` | 型付き属性を持つカスタムメタデータセットを作成します
`add_attributes_to_cm_set_tool` | 既存のカスタムメタデータセットに新しい属性を追加します
`remove_attributes_from_cm_set_tool` | カスタムメタデータセットから属性をアーカイブ（論理削除）します
`delete_custom_metadata_set_tool` | カスタムメタデータセットを完全削除し、すべてのアセットからその値を消去します
`update_custom_metadata_tool` | 1 つ以上のアセットでカスタムメタデータ値を更新します
`remove_custom_metadata_tool` | アセットからカスタムメタデータセットの値を削除します

### Atlan タグ

ツール | 説明
---- | -----------
`add_atlan_tags_tool` | 1 つ以上のアセットに Atlan タグを追加します
`remove_atlan_tag_tool` | 1 つ以上のアセットから Atlan タグを削除します

## 追加リソース

- [Atlan MCP Server Repository](https://github.com/atlanhq/agent-toolkit)
- [Atlan MCP Overview](https://docs.atlan.com/product/capabilities/atlan-ai/how-tos/atlan-mcp-overview)
