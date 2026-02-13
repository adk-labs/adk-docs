---
catalog_title: MCP Toolbox for Databases
catalog_description: Connect over 30 different data sources to your agents
catalog_icon: /adk-docs/integrations/assets/mcp-toolbox-for-databases.png
catalog_tags: ["mcp","data","google"]
---
# 데이터베이스용 MCP 도구 상자

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python</span><span class="lst-go">Go</span>
</div>

[데이터베이스용 MCP 도구 상자](https://github.com/googleapis/genai-toolbox)는 데이터베이스용 오픈 소스 MCP 서버입니다. 엔터프라이즈급 및 프로덕션 품질을 염두에 두고 설계되었습니다. 연결 풀링, 인증 등과 같은 복잡성을 처리하여 도구를 더 쉽고 빠르고 안전하게 개발할 수 있습니다.

Google의 에이전트 개발 키트(ADK)는 도구 상자를 기본적으로 지원합니다. 도구 상자 [시작하기](https://googleapis.github.io/genai-toolbox/getting-started/) 또는 [구성하기](https://googleapis.github.io/genai-toolbox/getting-started/configure/)에 대한 자세한 내용은 [설명서](https://googleapis.github.io/genai-toolbox/getting-started/introduction/)를 참조하세요.

![GenAI 도구 상자](../../assets/mcp_db_toolbox.png)

## 지원되는 데이터 소스

MCP 도구 상자는 다음 데이터베이스 및 데이터 플랫폼에 대한 즉시 사용 가능한 도구 세트를 제공합니다.

### Google Cloud

*   [BigQuery](https://googleapis.github.io/genai-toolbox/resources/sources/bigquery/) (SQL 실행, 스키마 검색 및 AI 기반 시계열 예측용 도구 포함)
*   [AlloyDB](https://googleapis.github.io/genai-toolbox/resources/sources/alloydb-pg/) (PostgreSQL 호환, 표준 쿼리 및 자연어 쿼리용 도구 포함)
*   [AlloyDB 관리자](https://googleapis.github.io/genai-toolbox/resources/sources/alloydb-admin/)
*   [Spanner](https://googleapis.github.io/genai-toolbox/resources/sources/spanner/) (GoogleSQL 및 PostgreSQL 방언 모두 지원)
*   Cloud SQL ([PostgreSQL용 Cloud SQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-pg/), [MySQL용 Cloud SQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-mysql/) 및 [SQL Server용 Cloud SQL](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-mssql/)에 대한 전용 지원 포함)
*   [Cloud SQL 관리자](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-sql-admin/)
*   [Firestore](https://googleapis.github.io/genai-toolbox/resources/sources/firestore/)
*   [Bigtable](https://googleapis.github.io/genai-toolbox/resources/sources/bigtable/)
*   [Dataplex](https://googleapis.github.io/genai-toolbox/resources/sources/dataplex/) (데이터 검색 및 메타데이터 검색용)
*   [Cloud Monitoring](https://googleapis.github.io/genai-toolbox/resources/sources/cloud-monitoring/)

### 관계형 및 SQL 데이터베이스

*   [PostgreSQL](https://googleapis.github.io/genai-toolbox/resources/sources/postgres/) (일반)
*   [MySQL](https://googleapis.github.io/genai-toolbox/resources/sources/mysql/) (일반)
*   [Microsoft SQL Server](https://googleapis.github.io/genai-toolbox/resources/sources/mssql/) (일반)
*   [ClickHouse](https://googleapis.github.io/genai-toolbox/resources/sources/clickhouse/)
*   [TiDB](https://googleapis.github.io/genai-toolbox/resources/sources/tidb/)
*   [OceanBase](https://googleapis.github.io/genai-toolbox/resources/sources/oceanbase/)
*   [Firebird](https://googleapis.github.io/genai-toolbox/resources/sources/firebird/)
*   [SQLite](https://googleapis.github.io/genai-toolbox/resources/sources/sqlite/)
*   [YugabyteDB](https://googleapis.github.io/genai-toolbox/resources/sources/yugabytedb/)

### NoSQL 및 키-값 저장소

*   [MongoDB](https://googleapis.github.io/genai-toolbox/resources/sources/mongodb/)
*   [Couchbase](https://googleapis.github.io/genai-toolbox/resources/sources/couchbase/)
*   [Redis](https://googleapis.github.io/genai-toolbox/resources/sources/redis/)
*   [Valkey](https://googleapis.github.io/genai-toolbox/resources/sources/valkey/)
*   [Cassandra](https://googleapis.github.io/genai-toolbox/resources/sources/cassandra/)

### 그래프 데이터베이스

*   [Neo4j](https://googleapis.github.io/genai-toolbox/resources/sources/neo4j/) (Cypher 쿼리 및 스키마 검사용 도구 포함)
*   [Dgraph](https://googleapis.github.io/genai-toolbox/resources/sources/dgraph/)

### 데이터 플랫폼 및 연합

*   [Looker](https://googleapis.github.io/genai-toolbox/resources/sources/looker/) (Looker API를 통해 Look, 쿼리 및 대시보드 빌드 실행용)
*   [Trino](https://googleapis.github.io/genai-toolbox/resources/sources/trino/) (여러 소스에서 연합 쿼리 실행용)

### 기타

*   [HTTP](https://googleapis.github.io/genai-toolbox/resources/sources/http/)

## 구성 및 배포

도구 상자는 직접 배포하고 관리하는 오픈 소스 서버입니다. 배포 및 구성에 대한 자세한 내용은 공식 도구 상자 설명서를 참조하세요.

* [서버 설치](https://googleapis.github.io/genai-toolbox/getting-started/introduction/#installing-the-server)
* [도구 상자 구성](https://googleapis.github.io/genai-toolbox/getting-started/configure/)

## ADK용 클라이언트 SDK 설치

=== "Python"

    ADK는 도구 상자를 사용하기 위해 `toolbox-core` python 패키지에 의존합니다. 시작하기 전에 패키지를 설치하세요.

    ```shell
    pip install toolbox-core
    ```

    ### 도구 상자 도구 로드

    도구 상자 서버가 구성되고 실행되면 ADK를 사용하여 서버에서 도구를 로드할 수 있습니다.

    ```python
    from google.adk.agents import Agent
    from toolbox_core import ToolboxSyncClient

    toolbox = ToolboxSyncClient("https://127.0.0.1:5000")

    # 특정 도구 세트 로드
    tools = toolbox.load_toolset('my-toolset-name'),
    # 단일 도구 로드
    tools = toolbox.load_tool('my-tool-name'),

    root_agent = Agent(
        ...,
        tools=tools # 에이전트에 도구 목록 제공

    )
    ```

=== "Go"

    ADK는 도구 상자를 사용하기 위해 `mcp-toolbox-sdk-go` go 모듈에 의존합니다. 시작하기 전에 모듈을 설치하세요.

    ```shell
    go get github.com/googleapis/mcp-toolbox-sdk-go
    ```

    ### 도구 상자 도구 로드

    도구 상자 서버가 구성되고 실행되면 ADK를 사용하여 서버에서 도구를 로드할 수 있습니다.

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
    		log.Fatalf("MCP 도구 상자 클라이언트를 만드는 데 실패했습니다: %v", err)
    	}

      // 특정 도구 세트 로드
      toolboxtools, err := toolboxClient.LoadToolset("my-toolset-name", ctx)
      if err != nil {
        return fmt.Sprintln("도구 상자 도구 세트를 로드할 수 없습니다", err)
      }

      toolsList := make([]tool.Tool, len(toolboxtools))
        for i := range toolboxtools {
          toolsList[i] = &toolboxtools[i]
        }

      llmagent, err := llmagent.New(llmagent.Config{
        ...,
        Tools:       toolsList,
      })

      // 단일 도구 로드
      tool, err := client.LoadTool("my-tool-name", ctx)
      if err != nil {
        return fmt.Sprintln("도구 상자 도구를 로드할 수 없습니다", err)
      }

      llmagent, err := llmagent.New(llmagent.Config{
        ...,
        Tools:       []tool.Tool{&toolboxtool},
      })
    }
    ```

## 고급 도구 상자 기능

도구 상자에는 데이터베이스용 Gen AI 도구를 개발하기 위한 다양한 기능이 있습니다. 자세한 내용은 다음 기능에 대해 자세히 알아보세요.

* [인증된 매개변수](https://googleapis.github.io/genai-toolbox/resources/tools/#authenticated-parameters): 도구 입력을 OIDC 토큰의 값에 자동으로 바인딩하여 잠재적으로 데이터 유출 없이 민감한 쿼리를 쉽게 실행할 수 있습니다.
* [승인된 호출:](https://googleapis.github.io/genai-toolbox/resources/tools/#authorized-invocations)  사용자 인증 토큰을 기반으로 도구 사용에 대한 액세스를 제한합니다.
* [OpenTelemetry](https://googleapis.github.io/genai-toolbox/how-to/export_telemetry/): OpenTelemetry를 사용하여 도구 상자에서 메트릭 및 추적을 가져옵니다.
