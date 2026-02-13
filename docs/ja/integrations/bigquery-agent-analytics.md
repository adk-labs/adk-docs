# BigQuery Agent Analytics プラグイン

<div class="language-support-tag">
  <span class="lst-supported">ADK でサポート</span><span class="lst-python">Python v1.18.0</span><span class="lst-preview">プレビュー</span>
</div>

!!! note "可用性"

    このプラグインを試すには、ツリーのトップから ADK をビルドするか、バージョン 1.19 の公式リリースを待つことをお勧めします。バージョン 1.19 がリリースされると、このメモは削除されます。

BigQuery Agent Analytics プラグインは、詳細なエージェントの動作分析のための堅牢なソリューションを提供することで、Agent Development Kit (ADK) を大幅に強化します。ADK プラグイン アーキテクチャと BigQuery Storage Write API を使用して、重要な運用イベントを Google BigQuery テーブルに直接キャプチャしてログに記録し、デバッグ、リアルタイム監視、および包括的なオフライン パフォーマンス評価のための高度な機能を提供します。

!!! example "プレビュー リリース"

    BigQuery Agent Analytics プラグインはプレビュー リリースです。詳細については、[リリース段階の説明](https://cloud.google.com/products#product-launch-stages) を参照してください。

!!! warning "BigQuery Storage Write API"

    この機能は、有料サービスである **BigQuery Storage Write API** を使用します。
    料金については、[BigQuery のドキュメント](https://cloud.google.com/bigquery/pricing?e=48754805&hl=en#data-ingestion-pricing) を参照してください。

## ユースケース

-   **エージェント ワークフローのデバッグと分析:** 幅広い *プラグイン ライフサイクル イベント* (LLM 呼び出し、ツール使用) と *エージェントが生成したイベント* (ユーザー入力、モデル応答) を、明確に定義されたスキーマにキャプチャします。
-   **大量の分析とデバッグ:** ログ記録操作は、メインのエージェントの実行をブロックしないように、別のスレッドで非同期に実行されます。大量のイベントを処理するように設計されたこのプラグインは、タイムスタンプを介してイベントの順序を保持します。

記録されるエージェント イベント データは、ADK イベント タイプによって異なります。詳細については、[イベント タイプとペイロード](#event-types) を参照してください。

## 前提条件

-   **BigQuery API** が有効になっている **Google Cloud プロジェクト**。
-   **BigQuery データセット:** プラグインを使用する前に、ログ テーブルを格納するデータセットを作成します。テーブルが存在しない場合、プラグインはデータセット内に必要なイベント テーブルを自動的に作成します。デフォルトでは、このテーブルの名前は agent_events ですが、プラグイン構成の table_id パラメータでこれをカスタマイズできます。
-   **認証:**
    -   **ローカル:** `gcloud auth application-default login` を実行します。
    -   **クラウド:** サービス アカウントに必要な権限があることを確認します。

### IAM 権限

エージェントが正しく機能するには、エージェントが実行されているプリンシパル (サービス アカウント、ユーザー アカウントなど) に、次の Google Cloud ロールが必要です。
*   プロジェクトで BigQuery クエリを実行するためのプロジェクト レベルの `roles/bigquery.jobUser`。このロールだけでは、どのデータにもアクセスできません。
*   選択した BigQuery テーブルにログ/イベント データを書き込むためのテーブル レベルの `roles/bigquery.dataEditor`。
エージェントにこのテーブルを作成させる必要がある場合は、テーブルを作成する BigQuery データセットに `roles/bigquery.dataEditor` を付与する必要があります。

## エージェントでの使用

BigQuery Analytics プラグインは、ADK エージェントの App オブジェクトで構成および登録することで使用します。次の例は、このプラグインと BigQuery ツールが有効になっているエージェントの実装を示しています。

```python title="my_bq_agent/agent.py"
# my_bq_agent/agent.py
import os
import google.auth
from google.adk.apps import App
from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# --- 構成 ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
DATASET_ID = os.environ.get("BIG_QUERY_DATASET_ID", "your-big-query-dataset-id")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "your-gcp-project-location") # Google Cloud プロジェクトの場所を使用

if PROJECT_ID == "your-gcp-project-id":
    raise ValueError("GOOGLE_CLOUD_PROJECT を設定するか、コードを更新してください。")
if DATASET_ID == "your-big-query-dataset-id":
    raise ValueError("BIG_QUERY_DATASET_ID を設定するか、コードを更新してください。")
if LOCATION == "your-gcp-project-location":
    raise ValueError("GOOGLE_CLOUD_LOCATION を設定するか、コードを更新してください。")

# --- 重要: Gemini インスタンス化の前に環境変数を設定 ---
os.environ['GOOGLE_CLOUD_PROJECT'] = PROJECT_ID
os.environ['GOOGLE_CLOUD_LOCATION'] = LOCATION
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'True' # Vertex AI API が有効になっていることを確認

# --- プラグインの初期化 ---
bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=PROJECT_ID, # project_id はユーザーからの必須入力
    dataset_id=DATASET_ID, # dataset_id はユーザーからの必須入力
    table_id="agent_events" # オプション: デフォルトは "agent_events"。テーブルが存在しない場合、プラグインは自動的にこのテーブルを作成します。
)

# --- ツールとモデルの初期化 ---
credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials)
)

llm = Gemini(
    model="gemini-1.5-flash",
)

root_agent = Agent(
    model=llm,
    name='my_bq_agent',
    instruction="あなたは BigQuery ツールにアクセスできる便利なアシスタントです。",
    tools=[bigquery_toolset]
)

# --- アプリの作成 ---
app = App(
    name="my_bq_agent",
    root_agent=root_agent,
    plugins=[bq_logging_plugin], # ここでプラグインを登録
)
```

### エージェントの実行とテスト

エージェントを実行し、「何ができるか教えて」や「クラウド プロジェクト <your-gcp-project-id> のデータセットを一覧表示して」などのチャット インターフェイスを介していくつかのリクエストを行うことで、プラグインをテストします。これらのアクションは、Google Cloud プロジェクトの BigQuery インスタンスに記録されるイベントを作成します。これらのイベントが処理されると、このクエリを使用して [BigQuery コンソール](https://console.cloud.google.com/bigquery) でそのデータを表示できます。

```sql
SELECT timestamp, event_type, content
FROM `your-gcp-project-id.your-big-query-dataset-id.agent_events`
ORDER BY timestamp DESC
LIMIT 20;
```

## 構成オプション

`BigQueryLoggerConfig` を使用してプラグインをカスタマイズできます。

-   **`enabled`** (`bool`, デフォルト: `True`): プラグインがエージェント データを BigQuery テーブルにログ記録しないようにするには、このパラメータを False に設定します。
-   **`event_allowlist`** (`Optional[List[str]]`, デフォルト: `None`): ログに記録するイベント タイプのリスト。`None` の場合、`event_denylist` にあるイベントを除くすべてのイベントがログに記録されます。サポートされているイベント タイプの包括的なリストについては、[イベント タイプとペイロード](#event-types) セクションを参照してください。
-   **`event_denylist`** (`Optional[List[str]]`, デフォルト: `None`): ログ記録をスキップするイベント タイプのリスト。サポートされているイベント タイプの包括的なリストについては、[イベント タイプとペイロード](#event-types) セクションを参照してください。
-   **`content_formatter`** (`Optional[Callable[[Any], str]]`, デフォルト: `None`): ログ記録の前にイベント コンテンツをフォーマットするオプションの関数。次のコードは、コンテンツ フォーマッタを実装する方法を示しています。
-   **`shutdown_timeout`** (`float`, デフォルト: `5.0`): シャットダウン中にログがフラッシュされるのを待つ秒数。
-   **`client_close_timeout`** (`float`, デフォルト: `2.0`): BigQuery クライアントが閉じるのを待つ秒数。
-   **`max_content_length`** (`int`, デフォルト: `500`): 切り捨て前のコンテンツ部分の最大長。

次のコード サンプルは、BigQuery Agent Analytics プラグインの構成を定義する方法を示しています。

```python
import json
import re

from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryLoggerConfig

def redact_dollar_amounts(event_content: Any) -> str:
    """
    ドル額 (例: $600, $12.50) を編集し、
    入力が dict の場合は JSON 出力を保証するカスタム フォーマッタ。
    """
    text_content = ""
    if isinstance(event_content, dict):
        text_content = json.dumps(event_content)
    else:
        text_content = str(event_content)

    # ドル額を見つける正規表現: $ の後に数字が続き、オプションでカンマまたは小数点が付きます。
    # 例: $600, $1,200.50, $0.99
    redacted_content = re.sub(r'\$\d+(?:,\d{3})*(?:\.\d+)?', 'xxx', text_content)

    return redacted_content

config = BigQueryLoggerConfig(
    enabled=True,
    event_allowlist=["LLM_REQUEST", "LLM_RESPONSE"], # これらのイベントのみをログに記録
    # event_denylist=["TOOL_STARTING"], # これらのイベントをスキップ
    shutdown_timeout=10.0, # 終了時にログがフラッシュされるまで最大 10 秒待機
    client_close_timeout=2.0, # BQ クライアントが閉じるまで最大 2 秒待機
    max_content_length=500, # コンテンツを 500 文字に切り捨て (デフォルト)
    content_formatter=redact_dollar_amounts, # ログ コンテンツのドル額を編集

)

plugin = BigQueryAgentAnalyticsPlugin(..., config=config)
```

## スキーマと本番環境のセットアップ

テーブルが存在しない場合、プラグインは自動的にテーブルを作成します。ただし、本番環境では、パフォーマンスとコストを最適化するために、**パーティショニング**と**クラスタリング**を使用してテーブルを手動で作成することをお勧めします。

**推奨 DDL:**

```sql
CREATE TABLE `your-gcp-project-id.adk_agent_logs.agent_events`
(
  timestamp TIMESTAMP NOT NULL OPTIONS(description="イベントがログに記録された UTC 時刻。"),
  event_type STRING OPTIONS(description="ログに記録されるイベントのタイプを示します (例: 'LLM_REQUEST', 'TOOL_COMPLETED')。"),
  agent STRING OPTIONS(description="イベントに関連付けられている ADK エージェントまたは作成者の名前。"),
  session_id STRING OPTIONS(description="単一の会話またはユーザー セッション内のイベントをグループ化するための一意の識別子。"),
  invocation_id STRING OPTIONS(description="セッション内の個々のエージェントの実行またはターンの一意の識別子。"),
  user_id STRING OPTIONS(description="現在のセッションに関連付けられているユーザーの識別子。"),
  content STRING OPTIONS(description="イベント固有のデータ (ペイロード)。形式は event_type によって異なります。"),
  error_message STRING OPTIONS(description="イベントの処理中にエラーが発生した場合に入力されます。"),
  is_truncated STRING OPTIONS(description="コンテンツ フィールドがサイズ制限のために切り捨てられたかどうかを示します。")
)
PARTITION BY DATE(timestamp)
CLUSTER BY event_type, agent, user_id;
```
### イベント タイプとペイロード {#event-types}

`content` 列には、`event_type` に固有のフォーマットされた文字列が含まれています。次の表に、これらのイベントと対応するコンテンツを示します。

!!! note

    - すべての可変コンテンツ フィールド (ユーザー入力、モデル応答、ツール引数、システム プロンプトなど)
    - は、ログ サイズを管理するために `max_content_length` 文字に切り捨てられます。
    - (`BigQueryLoggerConfig` で構成、デフォルト 500)

#### LLM インタラクション (プラグイン ライフサイクル)

これらのイベントは、LLM に送信され、LLM から受信された生のリクエストを追跡します。

<table>
  <thead>
    <tr>
      <th><strong>イベント タイプ</strong></th>
      <th><strong>トリガー条件</strong></th>
      <th><strong>コンテンツ形式ロジック</strong></th>
      <th><strong>コンテンツ例</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>
LLM_REQUEST
</pre></p></td>
      <td><p><pre>
before_model_callback
</pre></p></td>
      <td><p><pre>
Model: {model} | Prompt: {prompt} | System Prompt: Model: {model} | Prompt: {formatted_contents} | System Prompt: {system_prompt} | Params: {params} | Available Tools: {tool_names}
</pre></p></td>
      <td><p><pre>
Model: gemini-1.5-flash | Prompt: user: Model: gemini-flash-1.5| Prompt: user: text: 'Hello'| System Prompt: You are a helpful assistant. | Params: {temperature=1.0} | Available Tools: ['bigquery_tool']
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
LLM_RESPONSE
</pre></p></td>
      <td><p><pre>
after_model_callback
</pre></p></td>
      <td><strong>ツール呼び出しの場合:</strong> <code>Tool Name: {func_names} | Token Usage: {usage}</code><br>
<br>
**テキストの場合:** `Tool Name: text_response, text: '{text}' | Token Usage:
{usage}`</td>
      <td><p><pre>
Tool Name: text_response, text: 'Here is the data.' | Token Usage: {prompt: 10, candidates: 5, total: 15}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
LLM_ERROR
</pre></p></td>
      <td><p><pre>
on_model_error_callback
</pre></p></td>
      <td><code>None</code> (エラーの詳細は <code>error_message</code>
列にあります)</td>
      <td><p><pre>
None
</pre></p></td>
    </tr>
  </tbody>
</table>

#### ツールの使用 (プラグイン ライフサイクル)

これらのイベントは、エージェントによるツールの実行を追跡します。

<table>
  <thead>
    <tr>
      <th><strong>イベント タイプ</strong></th>
      <th><strong>トリガー条件</strong></th>
      <th><strong>コンテンツ形式ロジック</strong></th>
      <th><strong>コンテンツ例</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>
TOOL_STARTING
</pre></p></td>
      <td><p><pre>
before_tool_callback
</pre></p></td>
      <td><p><pre>
Tool Name: {name}, Description: {desc}, Arguments: {args}
</pre></p></td>
      <td><p><pre>
Tool Name: list_datasets, Description: Lists datasets..., Arguments: {'project_id': 'my-project'}
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
TOOL_COMPLETED
</pre></p></td>
      <td><p><pre>
after_tool_callback
</pre></p></td>
      <td><p><pre>
Tool Name: {name}, Result: {result}
</pre></p></td>
      <td><p><pre>
Tool Name: list_datasets, Result: ['dataset_1', 'dataset_2']
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
TOOL_ERROR
</pre></p></td>
      <td><p><pre>
on_tool_error_callback
</pre></p></td>
      <td><code>Tool Name: {name}, Arguments: {args}</code> (エラーの詳細は
<code>error_message</code> にあります)</td>
      <td><p><pre>
Tool Name: list_datasets, Arguments: {}
</pre></p></td>
    </tr>
  </tbody>
</table>

#### エージェント ライフサイクル (プラグイン ライフサイクル)

これらのイベントは、サブエージェントを含むエージェントの実行の開始と終了を追跡します。

<table>
  <thead>
    <tr>
      <th><strong>イベント タイプ</strong></th>
      <th><strong>トリガー条件</strong></th>
      <th><strong>コンテンツ形式ロジック</strong></th>
      <th><strong>コンテンツ例</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>
INVOCATION_STARTING
</pre></p></td>
      <td><p><pre>
before_run_callback
</pre></p></td>
      <td><p><pre>
None
</pre></p></td>
      <td><p><pre>
None
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
INVOCATION_COMPLETED
</pre></p></td>
      <td><p><pre>
after_run_callback
</pre></p></td>
      <td><p><pre>
None
</pre></p></td>
      <td><p><pre>
None
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
AGENT_STARTING
</pre></p></td>
      <td><p><pre>
before_agent_callback
</pre></p></td>
      <td><p><pre>
Agent Name: {agent_name}
</pre></p></td>
      <td><p><pre>
Agent Name: sub_agent_researcher
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
AGENT_COMPLETED
</pre></p></td>
      <td><p><pre>
after_agent_callback
</pre></p></td>
      <td><p><pre>
Agent Name: {agent_name}
</pre></p></td>
      <td><p><pre>
Agent Name: sub_agent_researcher
</pre></p></td>
    </tr>
  </tbody>
</table>

#### ユーザーおよび一般イベント (イベント ストリーム)

これらのイベントは、エージェントまたはランナーによって生成された `Event` オブジェクトから派生します。

<table>
  <thead>
    <tr>
      <th><strong>イベント タイプ</strong></th>
      <th><strong>トリガー条件</strong></th>
      <th><strong>コンテンツ形式ロジック</strong></th>
      <th><strong>コンテンツ例</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p><pre>
USER_MESSAGE_RECEIVED
</pre></p></td>
      <td><p><pre>
on_user_message_callback
</pre></p></td>
      <td><p><pre>
User Content: {formatted_message}
</pre></p></td>
      <td><p><pre>
User Content: text: 'Show me the sales data.'
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
TOOL_CALL
</pre></p></td>
      <td><code>event.get_function_calls()</code> が true</td>
      <td><p><pre>
call: {func_name}
</pre></p></td>
      <td><p><pre>
call: list_datasets
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
TOOL_RESULT
</pre></p></td>
      <td><code>event.get_function_responses()</code> が true</td>
      <td><p><pre>
resp: {func_name}
</pre></p></td>
      <td><p><pre>
resp: list_datasets
</pre></p></td>
    </tr>
    <tr>
      <td><p><pre>
MODEL_RESPONSE
</pre></p></td>
      <td><code>event.content</code> にパーツがある</td>
      <td><p><pre>
text: '{text}'
</pre></p></td>
      <td><p><pre>
text: 'I found 2 datasets.'
</pre></p></td>
    </tr>
  </tbody>
</table>

## 高度な分析クエリ

次のクエリ例は、BigQuery に記録された ADK エージェント イベント分析データから情報を抽出する方法を示しています。これらのクエリは、[BigQuery コンソール](https://console.cloud.google.com/bigquery) を使用して実行できます。

これらのクエリを実行する前に、提供されている SQL 内で GCP プロジェクト ID、BigQuery データセット ID、およびテーブル ID (指定されていない場合はデフォルトで "agent_events") を更新してください。

**特定の会話のターンをトレースする**

```sql
SELECT timestamp, event_type, agent, content
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE invocation_id = 'your-invocation-id'
ORDER BY timestamp ASC;
```

**1 日あたりの呼び出し量**

```sql
SELECT DATE(timestamp) as log_date, COUNT(DISTINCT invocation_id) as count
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'INVOCATION_STARTING'
GROUP BY log_date ORDER BY log_date DESC;
```

**トークン使用量の分析**

```sql
SELECT
  AVG(CAST(REGEXP_EXTRACT(content, r"Token Usage:.*total: ([0-9]+)") AS INT64)) as avg_tokens
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE event_type = 'LLM_RESPONSE';
```

**エラー監視**

```sql
SELECT timestamp, event_type, error_message
FROM `your-gcp-project-id.your-dataset-id.agent_events`
WHERE error_message IS NOT NULL
ORDER BY timestamp DESC LIMIT 50;
```

## 追加リソース

-   [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
-   [BigQuery 製品ドキュメント](https://cloud.google.com/bigquery/docs)
