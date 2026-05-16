---
catalog_title: Atlan
catalog_description: metadata、lineage、business knowledge を検索、探索、ガバナンスします
catalog_icon: /integrations/assets/atlan.png
catalog_tags: ["mcp"]
---

# ADK 向け Atlan MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Atlan MCP Server](https://github.com/atlanhq/agent-toolkit) は ADK エージェントを、
エンタープライズ AI のためのコンテキストレイヤーである
[Atlan](https://www.atlan.com/) に接続します。これによりエージェントは、AI
エージェントが効果的に作業するために必要な知識、データ、セマンティクスを含む
組織の context repo にアクセスできます。この統合により、エージェントは
エンタープライズコンテキストの検索と発見、end-to-end lineage の探索、ガバナンス
されたデータ定義と glossary へのアクセス、SQL の実行、metadata graph の整理、
data quality の確保を行い、すべてのエージェントタスクを信頼できる組織コンテキスト
に基づかせることができます。

## ユースケース

- **エンタープライズコンテキストの検索と発見:** 自然言語でスタック全体の
  table、column、dashboard、glossary term、data product を見つけます。

- **End-to-end lineage の探索:** システム全体でデータフローを upstream と
  downstream に追跡し、スキーマ変更前に依存関係を把握します。

- **ガバナンスされたデータ定義へのアクセス:** glossary、data domain、認証済み
  metadata を使って、エージェントの出力を信頼できる組織コンテキストに基づかせます。

- **Metadata graph の整理:** エージェントから説明の更新、アセットの認証、
  glossary の管理、data quality rule と schedule の定義、SQL の実行まで行います。

## 前提条件

- [Atlan](https://atlan.com/) tenant
- クエリしたいアセットへアクセスする権限を持つ Atlan アカウント
- ローカルにインストールされた Node.js（hosted MCP server へ bridge する
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
    ブラウザウィンドウが自動的に開きます。代わりに、コンソールに表示される
    認可 URL を使用することもできます。エージェントが Atlan tenant にアクセス
    できるよう、この要求を承認する必要があります。

## 利用可能なツール

### 発見と検索

Tool | Description
---- | -----------
`semantic_search_tool` | AI による semantic understanding を使って、すべてのデータアセットを自然言語で検索します
`search_assets_tool` | 構造化されたフィルタと条件でアセットを検索します
`traverse_lineage_tool` | アセットの data flow を upstream（source）または downstream（consumer）へ追跡します
`query_assets_tool` | 接続済みデータソースに対して SQL クエリを実行します
`get_asset_tool` | GUID または qualified name で単一アセットの詳細情報（custom metadata、data quality check、README を含む）を取得します
`resolve_metadata_tool` | 名前または説明で metadata entity（user、classification、custom metadata set、glossary、domain、data product）を見つけます
`get_groups_tool` | workspace group とそのメンバーを一覧表示します
`search_atlan_docs_tool` | Atlan 製品ドキュメントを検索し、source citation を含む LLM 生成回答を返します

### アセット更新

Tool | Description
---- | -----------
`update_assets_tool` | アセット説明、certificate ステータス、README、term を更新します
`manage_announcements_tool` | アセットに announcement（information、warning、issue）を追加または削除します
`manage_asset_lifecycle_tool` | アセットを archive、restore、または完全 purge します

### Glossary と domain

Tool | Description
---- | -----------
`create_glossaries` | 新しい glossary を作成します
`create_glossary_terms` | glossary 内に term を作成します
`create_glossary_categories` | glossary 内に category を作成します
`create_domains` | data domain と subdomain を作成します
`create_data_products` | domain と asset に紐づく data product を作成します

### Data quality rule

Tool | Description
---- | -----------
`create_dq_rules_tool` | data quality rule（null check、uniqueness、regex、custom SQL など）を作成します
`update_dq_rules_tool` | 既存の data quality rule を更新します
`schedule_dq_rules_tool` | cron expression で data quality rule の実行をスケジュールします
`delete_dq_rules_tool` | data quality rule を削除します

### Custom metadata

Tool | Description
---- | -----------
`create_custom_metadata_set_tool` | typed attribute を持つ custom metadata set を作成します
`add_attributes_to_cm_set_tool` | 既存の custom metadata set に新しい attribute を追加します
`remove_attributes_from_cm_set_tool` | custom metadata set から attribute を archive（soft-delete）します
`delete_custom_metadata_set_tool` | custom metadata set を完全削除し、すべてのアセットからその値を消去します
`update_custom_metadata_tool` | 1 つ以上のアセットで custom metadata 値を更新します
`remove_custom_metadata_tool` | アセットから custom metadata set の値を削除します

### Atlan tag

Tool | Description
---- | -----------
`add_atlan_tags_tool` | 1 つ以上のアセットに Atlan tag を追加します
`remove_atlan_tag_tool` | 1 つ以上のアセットから Atlan tag を削除します

## 追加リソース

- [Atlan MCP Server Repository](https://github.com/atlanhq/agent-toolkit)
- [Atlan MCP Overview](https://docs.atlan.com/product/capabilities/atlan-ai/how-tos/atlan-mcp-overview)
