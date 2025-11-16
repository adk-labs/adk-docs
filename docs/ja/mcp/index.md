# モデルコンテキストプロトコル（MCP）

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-go">Go</span><span class="lst-java">Java</span>
</div>

[モデルコンテキストプロトコル（MCP）](https://modelcontextprotocol.io/introduction)は、GeminiやClaudeのような大規模言語モデル（LLM）が、外部のアプリケーション、データソース、ツールとどのように通信するかを標準化するために設計されたオープンスタンダードです。LLMがコンテキストを取得し、アクションを実行し、様々なシステムと対話する方法を簡素化する、普遍的な接続メカニズムだとお考えください。

## MCPの仕組み

MCPはクライアント/サーバーアーキテクチャに従い、データ（リソース）、インタラクティブなテンプレート（プロンプト）、実行可能な関数（ツール）がMCPサーバーによってどのように公開され、MCPクライアント（LLMホストアプリケーションまたはAIエージェント）によってどのように利用されるかを定義します。

## ADKにおけるMCPツール

ADKは、MCPサービスを呼び出すツールを構築しようとしている場合でも、他の開発者やエージェントがあなたのツールと対話できるようにMCPサーバーを公開しようとしている場合でも、エージェントでMCPツールを使用および利用するのに役立ちます。

ADKをMCPサーバーと一緒に使用するのに役立つコードサンプルと設計パターンについては、[MCPツールドキュメント](../tools/mcp-tools.md)を参照してください。これには以下が含まれます：

- **ADK内での既存MCPサーバーの利用**：ADKエージェントはMCPクライアントとして機能し、外部のMCPサーバーから提供されるツールを使用できます。
- **MCPサーバーを介したADKツールの公開**：ADKツールをラップし、任意のMCPクライアントからアクセスできるようにするMCPサーバーの構築方法。

## データベース向けMCP Toolbox

[データベース向けMCP Toolbox](https://github.com/googleapis/genai-toolbox)は、バックエンドのデータソースを、事前構築済みですぐに本番環境で利用できるツールセットとして安全に公開する、オープンソースのMCPサーバーです。これは普遍的な抽象化レイヤーとして機能し、ADKエージェントが組み込みのサポートにより、多種多様なデータベースから安全に情報をクエリ、分析、取得できるようにします。

MCP Toolboxサーバーには包括的なコネクタライブラリが含まれており、エージェントが複雑なデータ資産と安全に対話できることを保証します。

### 対応データソース

MCP Toolboxは、以下のデータベースおよびデータプラットフォーム向けに、すぐに使えるツールセットを提供します。

#### Google Cloud

*   [BigQuery](https://googleapis.github.io/genai-toolbox/resources/sources/bigquery/)（SQL実行、スキーマ検出、AIによる時系列予測などのツールを含む）
*   [AlloyDB](https://googleapis.github.io/genai-toolbox/resources/sources/alloydb-pg/)（PostgreSQL互換。標準クエリと自然言語クエリの両方のツールを含む）
*   [AlloyDB Admin](https://googleapis.github.io/genai-toolbox/resources/sources/alloydb-admin/)
*   [Spanner](https://googleapis.github.io/genai-toolbox/resources/sources/spanner/)（GoogleSQLとPostgreSQLの両方の言語をサポート）
*   Cloud SQL（[Cloud SQL for PostgreSQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-pg/)、[Cloud SQL for MySQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-mysql/)、[Cloud SQL for SQL Server](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-mssql/)の専用サポートを含む）
*   [Cloud SQL Admin](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-admin/)
*   [Firestore](https://googleapis.github.io/genai-toolbox/resources/sources/firestore/)
*   [Bigtable](https://googleapis.github.io/genai-toolbox/resources/sources/bigtable/)
*   [Dataplex](https://googleapis.github.io/genai-toolbox/resources/sources/dataplex/)（データ検出とメタデータ検索用）
*   [Cloud Monitoring](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-monitoring/)

#### リレーショナル & SQLデータベース

*   [PostgreSQL](https://googleapis.github.io/genai-toolbox/resources/sources/postgres/)（汎用）
*   [MySQL](https://googleapis.github.io/genai-toolbox/resources/sources/mysql/)（汎用）
*   [Microsoft SQL Server](https://googleapis.github.io/genai-toolbox/resources/sources/mssql/)（汎用）
*   [ClickHouse](https://googleapis.github.io/genai-toolbox/resources/sources/clickhouse/)
*   [TiDB](https://googleapis.github.io/genai-toolbox/resources/sources/tidb/)
*   [OceanBase](https://googleapis.github.io/genai-toolbox/resources/sources/oceanbase/)
*   [Firebird](https://googleapis.github.io/genai-toolbox/resources/sources/firebird/)
*   [SQLite](https://googleapis.github.io/genai-toolbox/resources/sources/sqlite/)
*   [YugabyteDB](https://googleapis.github.io/genai-toolbox/resources/sources/yugabytedb/)

#### NoSQL & キーバリューストア

*   [MongoDB](https://googleapis.github.io/genai-toolbox/resources/sources/mongodb/)
*   [Couchbase](https://googleapis.github.io/genai-toolbox/resources/sources/couchbase/)
*   [Redis](https://googleapis.github.io/genai-toolbox/resources/sources/redis/)
*   [Valkey](https://googleapis.github.io/genai-toolbox/resources/sources/valkey/)
*   [Cassandra](https://googleapis.github.io/genai-toolbox/resources/sources/cassandra/)

#### グラフデータベース

*   [Neo4j](https://googleapis.github.io/genai-toolbox/resources/sources/neo4j/)（Cypherクエリとスキーマ検査ツールを含む）
*   [Dgraph](https://googleapis.github.io/genai-toolbox/resources/sources/dgraph/)

#### データプラットフォーム & フェデレーション

*   [Looker](https://googleapis.github.io/genai-toolbox/resources/sources/looker/)（Looker API経由でのLookの実行、クエリ、ダッシュボード構築用）
*   [Trino](https://googleapis.github.io/genai-toolbox/resources/sources/trino/)（複数ソースにまたがるフェデレーションクエリ実行用）

#### その他

*   [HTTP](https://googleapis.github.io/genai-toolbox/resources/sources/http/)

### ドキュメント

ADKとデータベース向けMCP Toolboxを連携して使用する方法については、[データベース向けMCP Toolbox](/adk-docs/tools/google-cloud/mcp-toolbox-for-databases/)のドキュメントを参照してください。データベース向けMCP Toolboxの開始にあたり、ブログ投稿[チュートリアル：データベース向けMCP Toolbox - BigQueryデータセットの公開](https://medium.com/google-cloud/tutorial-mcp-toolbox-for-databases-exposing-big-query-datasets-9321f0064f4e)とCodelab[データベース向けMCP Toolbox：BigQueryデータセットをMCPクライアントで利用可能にする](https://codelabs.developers.google.com/mcp-toolbox-bigquery-dataset?hl=en#0)も利用できます。

![GenAI Toolbox](../assets/mcp_db_toolbox.png)

## ADKエージェントとFastMCPサーバー
[FastMCP](https://github.com/jlowin/fastmcp)は、複雑なMCPプロトコルの詳細やサーバー管理をすべて処理するため、あなたは優れたツールの構築に集中できます。これは高レベルでPythonらしい（Pythonic）設計になっており、ほとんどの場合、関数にデコレーターを付けるだけで済みます。

Cloud Run上で実行されるFastMCPサーバーとADKを連携させる方法については、[MCPツールドキュメント](../tools/mcp-tools.md)を参照してください。

## Google Cloud Genmedia向けMCPサーバー

[Genmediaサービス向けMCPツール](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia)は、Imagen、Veo、Chirp 3 HDボイス、LyriaといったGoogle Cloudの生成メディアサービスをAIアプリケーションに統合できるようにする、オープンソースのMCPサーバーセットです。

Agent Development Kit（ADK）と[Genkit](https://genkit.dev/)は、これらのMCPツールに対する組み込みサポートを提供し、AIエージェントが生成メディアのワークフローを効果的にオーケストレーションできるようにします。実装ガイダンスについては、[ADKサンプルエージェント](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/adk)および[Genkitサンプル](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/tree/main/experiments/mcp-genmedia/sample-agents/genkit)を参照してください。