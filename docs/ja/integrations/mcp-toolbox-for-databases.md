---
hide:
  - toc
---
# データベース向けMCPツールボックス

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-go">Go</span>
</div>

[データベース向けMCPツールボックス](https://github.com/googleapis/genai-toolbox)は、データベース向けのオープンソースMCPサーバーです。エンタープライズグレードと本番品質を念頭に置いて設計されています。接続プーリング、認証などの複雑さを処理することで、ツールをより簡単、迅速、安全に開発できます。

GoogleのAgent Development Kit（ADK）は、ツールボックスを組み込みでサポートしています。ツールボックスの[はじめに](https://googleapis.github.io/genai-toolbox/getting-started/)または[構成](https://googleapis.github.io/genai-toolbox/getting-started/configure/)の詳細については、[ドキュメント](https://googleapis.github.io/genai-toolbox/getting-started/introduction/)を参照してください。

![GenAIツールボックス](../../assets/mcp_db_toolbox.png)

## サポートされているデータソース

MCPツールボックスは、次のデータベースとデータプラットフォーム向けにすぐに使えるツールセットを提供します。

### Google Cloud

*   [BigQuery](https://googleapis.github.io/genai-toolbox/resources/sources/bigquery/)（SQL実行、スキーマ検出、AIを活用した時系列予測用のツールを含む）
*   [AlloyDB](https://googleapis.github.io/genai-toolbox/resources/sources/alloydb-pg/)（PostgreSQL互換、標準クエリと自然言語クエリの両方のツールを含む）
*   [AlloyDB Admin](https://googleapis.github.io/genai-toolbox/resources/sources/alloydb-admin/)
*   [Spanner](https://googleapis.github.io/genai-toolbox/resources/sources/spanner/)（GoogleSQLとPostgreSQLの両方のダイアлектをサポート）
*   Cloud SQL（[Cloud SQL for PostgreSQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-pg/)、[Cloud SQL for MySQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-mysql/)、[Cloud SQL for SQL Server](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-mssql/)の専用サポートを含む）
*   [Cloud SQL Admin](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-admin/)
*   [Firestore](https://googleapis.github.io/genai-toolbox/resources/sources/firestore/)
*   [Bigtable](https://googleapis.github.io/genai-toolbox/resources/sources/bigtable/)
*   [Dataplex](https://googleapis.github.io/genai-toolbox/resources/sources/dataplex/)（データ検出とメタデータ検索用）
*   [Cloud Monitoring](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-monitoring/)

### リレーショナルおよびSQLデータベース

*   [PostgreSQL](https://googleapis.github.io/genai-toolbox/resources/sources/postgres/)（汎用）
*   [MySQL](https://googleapis.github.io/genai-toolbox/resources/sources/mysql/)（汎用）
*   [Microsoft SQL Server](https://googleapis.github.io/genai-toolbox/resources/sources/mssql/)（汎用）
*   [ClickHouse](https://googleapis.github.io/genai-toolbox/resources/sources/clickhouse/)
*   [TiDB](https://googleapis.github.io/genai-toolbox/resources/sources/tidb/)
*   [OceanBase](https://googleapis.github.io/genai-toolbox/resources/sources/oceanbase/)
*   [Firebird](https://googleapis.github.io/genai-toolbox/resources/sources/firebird/)
*   [SQLite](https://googleapis.github.io/genai-toolbox/resources/sources/sqlite/)
*   [YugabyteDB](https://googleapis.github.io/genai-toolbox/resources/sources/yugabytedb/)

### NoSQLおよびキー値ストア

*   [MongoDB](https://googleapis.github.io/genai-toolbox/resources/sources/mongodb/)
*   [Couchbase](https://googleapis.github.io/genai-toolbox/resources/sources/couchbase/)
*   [Redis](https://googleapis.github.io/genai-toolbox/resources/sources/redis/)
*   [Valkey](https://googleapis.github.io/genai-toolbox/resources/sources/valkey/)
*   [Cassandra](https://googleapis.github.io/genai-toolbox/resources/sources/cassandra/)

### グラフデータベース

*   [Neo4j](https://googleapis.github.io/genai-toolbox/resources/sources/neo4j/)（Cypherクエリとスキーマ検査用のツールを含む）
*   [Dgraph](https://googleapis.github.io/genai-toolbox/resources/sources/dgraph/)

### データプラットフォームとフェデレーション

*   [Looker](https://googleapis.github.io/genai-toolbox/resources/sources/looker/)（Looker APIを介したLook、クエリ、ダッシュボードの構築の実行用）
*   [Trino](https://googleapis.github.io/genai-toolbox/resources/sources/trino/)（複数のソースにまたがるフェデレーションクエリの実行用）

### その他

*   [HTTP](https://googleapis.github.io/genai-toolbox/resources/sources/http/)

## 構成と展開

ツールボックスは、自分で展開および管理するオープンソースサーバーです。展開と構成の詳細については、公式のツールボックスドキュメントを参照してください。

* [サーバーのインストール](https://googleapis.github.io/genai-toolbox/getting-started/introduction/#installing-the-server)
* [ツールボックスの構成](https://googleapis.github.io/genai-toolbox/getting-started/configure/)

## ADK用クライアントSDKのインストール

=== "Python"

    ADKは、ツールボックスを使用するために`toolbox-core` pythonパッケージに依存しています。開始する前にパッケージをインストールしてください。

    ```shell
    pip install toolbox-core
    ```

    ### ツールボックスツールの読み込み

    ツールボックスサーバーが構成されて実行されたら、ADKを使用してサーバーからツールを読み込むことができます。

    ```python
    from google.adk.agents import Agent
    from toolbox_core import ToolboxSyncClient

    toolbox = ToolboxSyncClient("https://127.0.0.1:5000")

    # 特定のツールセットを読み込む
    tools = toolbox.load_toolset('my-toolset-name'),
    # 単一のツールを読み込む
    tools = toolbox.load_tool('my-tool-name'),

    root_agent = Agent(
        ...,
        tools=tools # エージェントにツールのリストを提供する

    )
    ```

=== "Go"

    ADKは、ツールボックスを使用するために`mcp-toolbox-sdk-go` goモジュールに依存しています。開始する前にモジュールをインストールしてください。

    ```shell
    go get github.com/googleapis/mcp-toolbox-sdk-go
    ```

    ### ツールボックスツールの読み込み

    ツールボックスサーバーが構成されて実行されたら、ADKを使用してサーバーからツールを読み込むことができます。

    ```go
    package main

    import (
    	"context"
    	"fmt"

    	"github.com/googleapis/mcp-toolbox-sdk-go/tbadk"
    	"google.golang.org/adk/agent/llmagent"
    )

    func main() {

      toolboxClient, err := tbadk.NewToolboxClient("https://127.0.0.1:5000")
    	if err != nil {
    		log.Fatalf("MCPツールボックスクライアントの作成に失敗しました: %v", err)
    	}

      // 特定のツールセットを読み込む
      toolboxtools, err := toolboxClient.LoadToolset("my-toolset-name", ctx)
      if err != nil {
        return fmt.Sprintln("ツールボックスツールセットを読み込めませんでした", err)
      }

      toolsList := make([]tool.Tool, len(toolboxtools))
        for i := range toolboxtools {
          toolsList[i] = &toolboxtools[i]
        }

      llmagent, err := llmagent.New(llmagent.Config{
        ...,
        Tools:       toolsList,
      })

      // 単一のツールを読み込む
      tool, err := client.LoadTool("my-tool-name", ctx)
      if err != nil {
        return fmt.Sprintln("ツールボックスツールを読み込めませんでした", err)
      }

      llmagent, err := llmagent.New(llmagent.Config{
        ...,
        Tools:       []tool.Tool{&toolboxtool},
      })
    }
    ```

## 高度なツールボックス機能

ツールボックスには、データベース向けのGen AIツールを開発するためのさまざまな機能があります。詳細については、次の機能について詳しくお読みください。

* [認証済みパラメータ](https://googleapis.github.io/genai-toolbox/resources/tools/#authenticated-parameters): ツール入力をOIDCトークンの値に自動的にバインドし、機密性の高いクエリをデータ漏洩の可能性なく簡単に実行できるようにします
* [承認済み呼び出し:](https://googleapis.github.io/genai-toolbox/resources/tools/#authorized-invocations)  ユーザーの認証トークンに基づいてツールを使用するためのアクセスを制限します
* [OpenTelemetry](https://googleapis.github.io/genai-toolbox/how-to/export_telemetry/): OpenTelemetryを使用してツールボックスからメトリックとトレースを取得します
