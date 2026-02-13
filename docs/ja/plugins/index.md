# プラグイン

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.7.0</span>
</div>

Agent Development Kit (ADK) のプラグインは、コールバックフックを使用してエージェントワークフローのライフサイクルのさまざまな段階で実行できるカスタムコードモジュールです。プラグインは、エージェントワークフロー全体に適用される機能に使用します。プラグインの一般的な用途は次のとおりです。

-   **ロギングとトレース**: デバッグとパフォーマンス分析のために、エージェント、ツール、生成AIモデルのアクティビティの詳細なログを作成します。
-   **ポリシーの適用**: ユーザーが特定のツールを使用する権限があるかどうかを確認し、権限がない場合はその実行を防止する関数など、セキュリティガードレールを実装します。
-   **監視とメトリクス**: Prometheusや[Google Cloud Observability](https://cloud.google.com/stackdriver/docs) (旧Stackdriver) などの監視システムに、トークン使用量、実行時間、呼び出し回数に関するメトリクスを収集してエクスポートします。
-   **応答キャッシング**: リクエストが以前に行われたかどうかを確認して、コストがかかる、または時間がかかるAIモデルやツール呼び出しをスキップし、キャッシュされた応答を返すことができます。
-   **リクエストまたは応答の変更**: AIモデルのプロンプトに情報を動的に追加したり、ツールの出力応答を標準化したりします。

!!! tip "ヒント: セキュリティ機能にはプラグインを使用"
    セキュリティガードレールやポリシーの実装では、コールバックよりもモジュール性と柔軟性に優れたADKプラグインの利用を推奨します。詳細は[セキュリティガードレールのためのコールバックとプラグイン](/adk-docs/ja/safety/#callbacks-and-plugins-for-security-guardrails)を参照してください。

!!! tip "ヒント: ADK 統合"
    ADK向けの事前構築プラグインおよびその他の統合一覧は、[ツールと統合](/adk-docs/ja/integrations/)を参照してください。

## プラグインの仕組み

ADKプラグインは`BasePlugin`クラスを拡張し、プラグインがエージェントライフサイクルのどこで実行されるべきかを示す1つ以上の`callback`メソッドを含みます。プラグインは、エージェントの`Runner`クラスに登録することでエージェントに統合します。エージェントアプリケーションでプラグインをトリガーする方法と場所の詳細については、[プラグインコールバックフック](#plugin-callback-hooks)を参照してください。

プラグイン機能は、ADKの拡張可能なアーキテクチャの主要な設計要素である[コールバック](../callbacks/index.md)に基づいて構築されています。一般的なエージェントコールバックが*特定のタスク*のために*単一のエージェント、単一のツール*に構成されるのに対し、プラグインは`Runner`に*一度*登録され、そのコールバックは当該ランナーが管理するすべてのエージェント、ツール、LLM呼び出しに*グローバルに*適用されます。プラグインを使用すると、関連するコールバック関数をまとめてパッケージ化し、ワークフロー全体で使用できます。これにより、プラグインはエージェントアプリケーション全体にわたる機能を実装するための理想的なソリューションとなります。

## 事前構築済みプラグイン

ADKには、エージェントワークフローにすぐに追加できるいくつかのプラグインが含まれています。

*   [**リフレクトとリトライツール**](/adk-docs/ja/plugins/reflect-and-retry/):
    ツールの失敗を追跡し、ツールリクエストをインテリジェントに再試行します。
*   [**BigQueryアナリティクス**](/adk-docs/ja/observability/bigquery-agent-analytics/):
    BigQueryによるエージェントのロギングと分析を可能にします。
*   [**コンテキストフィルター**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/context_filter_plugin.py):
    生成AIのコンテキストをフィルタリングしてサイズを削減します。
*   [**グローバルインストラクション**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/global_instruction_plugin.py):
    Appレベルでグローバルインストラクション機能を提供するプラグインです。
*   [**ファイルをアーティファクトとして保存**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/save_files_as_artifacts_plugin.py):
    ユーザーメッセージに含まれるファイルをアーティファクトとして保存します。
*   [**ロギング**](https://github.com/google/adk-python/blame/main/src/google/adk/plugins/logging_plugin.py):
    各エージェントワークフローのコールバックポイントで重要な情報をログに記録します。

## プラグインの定義と登録

このセクションでは、プラグインクラスを定義し、エージェントワークフローの一部として登録する方法について説明します。完全なコード例については、リポジトリの[プラグインの基本](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_basic)を参照してください。

### プラグインクラスの作成

`BasePlugin`クラスを拡張し、次のコード例に示すように1つ以上の`callback`メソッドを追加することから始めます。

```py title="count_plugin.py"
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin

class CountInvocationPlugin(BasePlugin):
  """エージェントとツールの呼び出し回数をカウントするカスタムプラグインです。"""

  def __init__(self) -> None:
    """カウンターでプラグインを初期化します。"""
    super().__init__(name="count_invocation")
    self.agent_count: int = 0
    self.tool_count: int = 0
    self.llm_request_count: int = 0

  async def before_agent_callback(
      self, *, agent: BaseAgent, callback_context: CallbackContext
  ) -> None:
    """エージェントの実行回数をカウントします。"""
    self.agent_count += 1
    print(f"[Plugin] エージェントの実行回数: {self.agent_count}")

  async def before_model_callback(
      self, *, callback_context: CallbackContext, llm_request: LlmRequest
  ) -> None:
    """LLMリクエストの数をカウントします。"""
    self.llm_request_count += 1
    print(f"[Plugin] LLMリクエストの数: {self.llm_request_count}")
```

このコード例は、エージェントのライフサイクル中にこれらのタスクの実行をカウントするために、`before_agent_callback`と`before_model_callback`のコールバックを実装しています。

### プラグインクラスの登録

`plugins`パラメータを使用して、エージェントの初期化時に`Runner`クラスの一部としてプラグインクラスを登録して統合します。このパラメータで複数のプラグインを指定できます。次のコード例は、前のセクションで定義した`CountInvocationPlugin`プラグインをシンプルなADKエージェントに登録する方法を示しています。

```py
from google.adk.runners import InMemoryRunner
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import asyncio

# プラグインをインポートします。
from .count_plugin import CountInvocationPlugin

async def hello_world(tool_context: ToolContext, query: str):
  print(f'Hello world: query is [{query}]')

root_agent = Agent(
    model='gemini-2.0-flash',
    name='hello_world',
    description='ユーザーのクエリでハローワールドを出力します。',
    instruction="""
    ハローワールドツールを使用してハローワールドとユーザーのクエリを出力してください。
    """,
    tools=[hello_world],
)

async def main():
  """エージェントのメインエントリポイントです。"""
  prompt = 'hello world'
  runner = InMemoryRunner(
      agent=root_agent,
      app_name='test_app_with_plugin',

      # ここにプラグインを追加します。複数のプラグインを追加できます。
      plugins=[CountInvocationPlugin()],
  )

  # 残りは通常のADKランナーを起動するのと同じです。
  session = await runner.session_service.create_session(
      user_id='user',
      app_name='test_app_with_plugin',
  )

  async for event in runner.run_async(
      user_id='user',
      session_id=session.id,
      new_message=types.Content(
        role='user', parts=[types.Part.from_text(text=prompt)]
      )
  ):
    print(f'** {event.author}からのイベントを受け取りました')

if __name__ == "__main__":
  asyncio.run(main())
```

### プラグインでエージェントを実行する

通常通りプラグインを実行します。以下はコマンドラインの実行方法を示しています。

```sh
python3 -m path.to.main
```

プラグインは[ADKウェブインターフェース](../evaluate/#1-adk-web-run-evaluations-via-the-web-ui)ではサポートされていません。ADKワークフローでプラグインを使用する場合は、ウェブインターフェースなしでワークフローを実行する必要があります。

この以前に説明したエージェントの出力は、次のようになります。

```log
[Plugin] エージェントの実行回数: 1
[Plugin] LLMリクエストの数: 1
** hello_worldからのイベントを受け取りました
Hello world: query is [hello world]
** hello_worldからのイベントを受け取りました
[Plugin] LLMリクエストの数: 2
** hello_worldからのイベントを受け取りました
```


ADKエージェントの実行に関する詳細については、[クイックスタート](/adk-docs/ja/get-started/quickstart/#run-your-agent)ガイドを参照してください。

## プラグインでワークフローを構築する

プラグインコールバックフックは、エージェントの実行ライフサイクルをインターセプト、変更、さらには制御するロジックを実装するためのメカニズムです。各フックは、プラグインクラス内の特定のメソッドであり、重要な瞬間にコードを実行するように実装できます。フックの戻り値に基づいて、2つの操作モードを選択できます。

-   **監視する場合:** 戻り値のないフック (`None`) を実装します。このアプローチは、ロギングやメトリクス収集などのタスクに使用され、エージェントのワークフローが中断することなく次のステップに進むことができます。たとえば、プラグインの`after_tool_callback`を使用して、デバッグのためにすべてのツールの結果をログに記録できます。
-   **介入する場合:** フックを実装し、値を返します。このアプローチは、ワークフローをショートサーキットします。`Runner`は処理を停止し、後続のプラグインと、モデル呼び出しなどの本来意図されたアクションをスキップし、プラグインコールバックの戻り値を結果として使用します。一般的な使用例は、キャッシュされた`LlmResponse`を返すように`before_model_callback`を実装し、冗長でコストのかかるAPI呼び出しを防ぐことです。
-   **修正する場合:** フックを実装し、Contextオブジェクトを変更します。このアプローチにより、モジュールの実行を中断することなく、実行されるモジュールのコンテキストデータを変更できます。たとえば、Modelオブジェクトの実行のための追加の標準化されたプロンプトテキストを追加するなどです。

**注意:** プラグインコールバック関数は、オブジェクトレベルで実装されたコールバックよりも優先されます。この動作は、プラグインレベルのコールバックコードが、エージェント、モデル、またはツールオブジェクトのコールバックが実行される*前に*実行されることを意味します。さらに、プラグインレベルのエージェントコールバックが空でない (`None`ではない) 応答を返す場合、エージェント、モデル、またはツールレベルのコールバックは*実行されません* (スキップされます)。

プラグイン設計は、コード実行の階層を確立し、グローバルな関心事をローカルエージェントロジックから分離します。プラグインは、`PerformanceMonitoringPlugin`などの構築するステートフルな*モジュール*であり、コールバックフックは、そのモジュール内で実行される特定の*関数*です。このアーキテクチャは、次の重要な点で標準のエージェントコールバックとは根本的に異なります。

-   **スコープ:** プラグインフックは*グローバル*です。プラグインは`Runner`に一度登録され、そのフックは管理するすべてのAgent、Model、およびToolに普遍的に適用されます。対照的に、エージェントコールバックは*ローカル*であり、特定のAgentインスタンスで個別に構成されます。
-   **実行順序:** プラグインが*優先*します。任意のイベントに対して、プラグインフックは常に、対応するエージェントコールバックよりも先に実行されます。このシステム動作により、プラグインはセキュリティポリシー、ユニバーサルキャッシング、アプリケーション全体の一貫したロギングなどの横断的な機能を実装するための正しいアーキテクチャの選択となります。

### エージェントのコールバックとプラグイン

前のセクションで述べたように、プラグインとエージェントのコールバックには機能的な類似点がいくつかあります。次の表は、プラグインとエージェントのコールバックの違いをより詳細に比較しています。

<table>
  <thead>
    <tr>
      <th></th>
      <th><strong>プラグイン</strong></th>
      <th><strong>エージェントのコールバック</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>スコープ</strong></td>
      <td><strong>グローバル</strong>: <code>Runner</code>内のすべてのエージェント/ツール/LLMに適用されます。</td>
      <td><strong>ローカル</strong>: 構成されている特定のエージェントインスタンスにのみ適用されます。</td>
    </tr>
    <tr>
      <td><strong>主なユースケース</strong></td>
      <td><strong>横断的機能</strong>: ロギング、ポリシー、監視、グローバルキャッシング。</td>
      <td><strong>特定のエージェントロジック</strong>: 単一のエージェントの動作または状態の変更。</td>
    </tr>
    <tr>
      <td><strong>構成</strong></td>
      <td><code>Runner</code>で一度構成します。</td>
      <td>各<code>BaseAgent</code>インスタンスで個別に構成します。</td>
    </tr>
    <tr>
      <td><strong>実行順序</strong></td>
      <td>プラグインのコールバックはエージェントのコールバック<strong>の前に</strong>実行されます。</td>
      <td>エージェントのコールバックはプラグインのコールバック<strong>の後に</strong>実行されます。</td>
    </tr>
  </tbody>
</table>

## プラグインコールバックフック

プラグインクラスで定義するコールバック関数を使用して、プラグインが呼び出されるタイミングを定義します。コールバックは、ユーザーメッセージが受信されたとき、`Runner`、`Agent`、`Model`、または`Tool`が呼び出される前と後、`Events`に対して、および`Model`または`Tool`エラーが発生したときに利用できます。これらのコールバックには、Agent、Model、およびToolクラス内で定義されたすべてのコールバックが含まれ、それらよりも優先されます。

次の図は、エージェントワークフロー中にプラグイン機能をアタッチして実行できるコールバックポイントを示しています。

![ADKプラグインコールバックフック](../assets/workflow-plugin-hooks.svg)
**図1.** プラグインコールバックフックの場所を含むADKエージェントワークフロー図。

次のセクションでは、プラグインで利用可能なコールバックフックについて詳しく説明します。

-   [ユーザーメッセージコールバック](#user-message-callbacks)
-   [ランナー開始コールバック](#runner-start-callbacks)
-   [エージェント実行コールバック](#agent-execution-callbacks)
-   [モデルコールバック](#model-callbacks)
-   [ツールコールバック](#tool-callbacks)
-   [ランナー終了コールバック](#runner-end-callbacks)

### ユーザーメッセージコールバック

*ユーザーメッセージ*コールバック (`on_user_message_callback`) は、ユーザーがメッセージを送信したときに発生します。`on_user_message_callback`は最初に実行されるフックであり、初期入力を検査または変更する機会を提供します。

-   **実行タイミング:** `runner.run()`の直後、他の処理の前に発生します。
-   **目的:** ユーザーの生入力を検査または変更する最初の機会です。
-   **フロー制御:** ユーザーの元のメッセージを**置き換える**`types.Content`オブジェクトを返します。

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def on_user_message_callback(
    self,
    *,
    invocation_context: InvocationContext,
    user_message: types.Content,
) -> Optional[types.Content]:
```

### ランナー開始コールバック

*ランナー開始*コールバック (`before_run_callback`) は、`Runner`オブジェクトが変更された可能性のあるユーザーメッセージを受け取り、実行を準備するときに発生します。`before_run_callback`はここで発火し、エージェントロジックが開始される前にグローバルなセットアップを可能にします。

-   **実行タイミング:** `runner.run()`が呼び出された直後、他の処理の前に発生します。
-   **目的:** ユーザーの生入力を検査または変更する最初の機会です。
-   **フロー制御:** ユーザーの元のメッセージを**置き換える**`types.Content`オブジェクトを返します。

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def before_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[types.Content]:
```

### エージェント実行コールバック

*エージェント実行*コールバック (`before_agent`、`after_agent`) は、`Runner`オブジェクトがエージェントを呼び出したときに発生します。`before_agent_callback`はエージェントの主要な作業が開始される直前に実行されます。主要な作業には、モデルやツールの呼び出しを含む、リクエストを処理するためのエージェントのプロセス全体が含まれます。エージェントがすべてのステップを完了し、結果を準備した後、`after_agent_callback`が実行されます。

**注意:** これらのコールバックを実装するプラグインは、エージェントレベルのコールバックが実行される*前に*実行されます。さらに、プラグインレベルのエージェントコールバックが`None`またはnull応答以外の何かを返す場合、エージェントレベルのコールバックは*実行されません* (スキップされます)。

Agentオブジェクトの一部として定義されたAgentコールバックの詳細については、[コールバックの種類](../callbacks/types-of-callbacks.md#agent-lifecycle-callbacks)を参照してください。

### モデルコールバック

モデルコールバック **(`before_model`、`after_model`、`on_model_error`)** は、Modelオブジェクトが実行される前後に発生します。プラグイン機能は、以下に詳述するように、エラー発生時のコールバックもサポートしています。

-   エージェントがAIモデルを呼び出す必要がある場合、`before_model_callback`が最初に実行されます。
-   モデル呼び出しが成功した場合、次に`after_model_callback`が実行されます。
-   モデル呼び出しが例外で失敗した場合、代わりに`on_model_error_callback`がトリガーされ、正常な回復が可能になります。

**注意:** **`before_model`** および **`after_model`** コールバックメソッドを実装するプラグインは、モデルレベルのコールバックが実行される*前に*実行されます。さらに、プラグインレベルのモデルコールバックが`None`またはnull応答以外の何かを返す場合、モデルレベルのコールバックは*実行されません* (スキップされます)。

#### モデルエラー時コールバックの詳細

Modelオブジェクトのエラー時コールバックは、プラグイン機能によってのみサポートされており、次のように機能します。

-   **実行タイミング:** モデル呼び出し中に例外が発生した場合。
-   **一般的なユースケース:** 正常なエラー処理、特定のエラーのロギング、または「AIサービスは現在利用できません」のようなフォールバック応答の返却。
-   **フロー制御:** 
    -   `LlmResponse`オブジェクトを返して**例外を抑制**し、フォールバック結果を提供します。
    -   `None`を返して、元の例外が発生することを許可します。

**注**: Modelオブジェクトの実行が`LlmResponse`を返す場合、システムは実行フローを再開し、`after_model_callback`が通常どおりトリガーされます。****

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def on_model_error_callback(
    self,
    *,
    callback_context: CallbackContext,
    llm_request: LlmRequest,
    error: Exception,
) -> Optional[LlmResponse]:
```

### ツールコールバック

プラグインのツールコールバック **(`before_tool`、`after_tool`、`on_tool_error`)** は、ツールの実行前または実行後、あるいはエラーが発生したときに発生します。プラグイン機能は、以下に詳述するように、エラー発生時のコールバックもサポートしています。

-   エージェントがツールを実行する場合、最初に`before_tool_callback`が実行されます。
-   ツールが正常に実行されると、次に`after_tool_callback`が実行されます。
-   ツールが例外を発生させた場合、代わりに`on_tool_error_callback`がトリガーされ、失敗を処理する機会が与えられます。`on_tool_error_callback`が辞書を返す場合、`after_tool_callback`が通常どおりトリガーされます。

**注意:** これらのコールバックを実装するプラグインは、ツールレベルのコールバックが実行される*前に*実行されます。さらに、プラグインレベルのツールコールバックが`None`またはnull応答以外の何かを返す場合、ツールレベルのコールバックは*実行されません* (スキップされます)。

#### ツールエラー時コールバックの詳細

ツールオブジェクトのエラー時コールバックは、プラグイン機能によってのみサポートされており、次のように機能します。

-   **実行タイミング:** ツールの`run`メソッドの実行中に例外が発生した場合。
-   **目的:** 特定のツール例外 (`APIError`など) を捕捉し、失敗をログに記録し、LLMにユーザーフレンドリーなエラーメッセージを提供します。
-   **フロー制御:** `dict`を返して**例外を抑制**し、フォールバック結果を提供します。`None`を返して、元の例外が発生することを許可します。

**注**: `dict`を返すことで、実行フローが再開され、`after_tool_callback`が通常どおりトリガーされます。

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def on_tool_error_callback(
    self,
    *,
    tool: BaseTool,
    tool_args: dict[str, Any],
    tool_context: ToolContext,
    error: Exception,
) -> Optional[dict]:
```

### イベントコールバック

*イベントコールバック* (`on_event_callback`) は、エージェントがテキスト応答やツール呼び出しの結果などの出力を生成し、それらを`Event`オブジェクトとして生成するときに発生します。`on_event_callback`は各イベントに対して発火し、クライアントにストリーミングされる前にイベントを変更できるようにします。

-   **実行タイミング:** エージェントが`Event`を生成した後、ユーザーに送信される前。エージェントの実行は複数のイベントを生成する可能性があります。
-   **目的:** イベントの変更またはエンリッチメント (例: メタデータの追加)、または特定のイベントに基づいた副作用のトリガーに役立ちます。
-   **フロー制御:** 元のイベントを**置き換える**`Event`オブジェクトを返します。

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def on_event_callback(
    self, *, invocation_context: InvocationContext, event: Event
) -> Optional[Event]:
```

### ランナー終了コールバック

*ランナー終了*コールバック **(`after_run_callback`)** は、エージェントがプロセス全体を完了し、すべてのイベントが処理された後、`Runner`が実行を完了したときに発生します。`after_run_callback`は最後のフックであり、クリーンアップと最終レポートに最適です。

-   **実行タイミング:** `Runner`がリクエストの実行を完全に完了した後。
-   **目的:** 接続のクローズやログとメトリクスデータの最終化など、グローバルなクリーンアップタスクに最適です。
-   **フロー制御:** このコールバックはティアダウン専用であり、最終結果を変更することはできません。

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def after_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[None]:
```

## 次のステップ

ADKプロジェクトにプラグインを開発して適用するためのこれらのリソースを確認してください。

-   より多くのADKプラグインコードの例については、[ADK Pythonリポジトリ](https://github.com/google/adk-python/tree/main/src/google/adk/plugins)を参照してください。
-   セキュリティ目的でプラグインを適用する方法については、[セキュリティガードレールのためのコールバックとプラグイン](/adk-docs/ja/safety/#callbacks-and-plugins-for-security-guardrails)を参照してください。
