# プラグイン

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.7.0</span>
</div>

Agent Development Kit（ADK）のプラグインは、コールバックフックを使用してエージェントワークフローライフサイクルのさまざまな段階で実行できるカスタムコードモジュールです。エージェントワークフロー全体に適用できる機能にプラグインを使用します。プラグインの一般的なアプリケーションは次のとおりです。

-   **ロギングとトレース**: デバッグとパフォーマンス分析のために、エージェント、ツール、および生成AIモデルのアクティビティの詳細なログを作成します。
-   **ポリシーの適用**: ユーザーが特定のツールを使用する権限があるかどうかを確認し、権限がない場合はその実行を防ぐ関数など、セキュリティガードレールを実装します。
-   **監視とメトリック**: トークンの使用状況、実行時間、呼び出し回数に関するメトリックを収集し、Prometheusや[Google Cloud Observability](https://cloud.google.com/stackdriver/docs)（旧Stackdriver）などの監視システムにエクスポートします。
-   **応答のキャッシュ**: 以前にリクエストが行われたかどうかを確認して、高価または時間のかかるAIモデルまたはツールの呼び出しをスキップして、キャッシュされた応答を返すことができます。
-   **リクエストまたは応答の変更**: AIモデルのプロンプトに情報を動的に追加したり、ツールの出力応答を標準化したりします。

!!! tip
    セキュリティガードレールとポリシーを実装する場合は、コールバックよりもモジュール性と柔軟性に優れたADKプラグインを使用してください。詳細については、[セキュリティガードレールのためのコールバックとプラグイン](/adk-docs/ja/safety/#callbacks-and-plugins-for-security-guardrails)を参照してください。

!!! warning "注意"
    プラグインは[ADK Webインターフェイス](../evaluate/#1-adk-web-run-evaluations-via-the-web-ui)ではサポートされていません。ADKワークフローでプラグインを使用する場合は、Webインターフェイスなしでワークフローを実行する必要があります。

## プラグインの仕組み

ADKプラグインは`BasePlugin`クラスを拡張し、プラグインを実行する必要があるエージェントライフサイクルの場所を示す1つ以上の`callback`メソッドを含みます。エージェントの`Runner`クラスに登録することで、プラグインをエージェントに統合します。エージェントアプリケーションでプラグインをトリガーする方法と場所の詳細については、[プラグインコールバックフック](#plugin-callback-hooks)を参照してください。

プラグイン機能は、ADKの拡張可能なアーキテクチャの重要な設計要素である[コールバック](../callbacks/)に基づいています。一般的なエージェントコールバックは*特定のタスク*に対して*単一のエージェント、単一のツール*で構成されますが、プラグインは`Runner`に*一度*登録され、そのコールバックはそのランナーによって管理されるすべてのエージェント、ツール、LLM呼び出しに*グローバル*に適用されます。プラグインを使用すると、関連するコールバック関数をまとめてパッケージ化し、ワークフロー全体で使用できます。これにより、プラグインはエージェントアプリケーション全体にまたがる機能を実装するための理想的なソリューションになります。

## 事前構築済みプラグイン

ADKには、エージェントワークフローにすぐに追加できるいくつかのプラグインが含まれています。

*   [**ツールの反映と再試行**](/adk-docs/ja/plugins/reflect-and-retry/): ツールの障害を追跡し、ツールリクエストをインテリジェントに再試行します。
*   [**BigQuery分析**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/bigquery_agent_analytics_plugin.py): BigQueryによるエージェントのロギングと分析を有効にします。
*   [**コンテキストフィルター**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/context_filter_plugin.py): 生成AIコンテキストをフィルタリングしてサイズを縮小します。
*   [**グローバル命令**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/global_instruction_plugin.py): アプリレベルでグローバル命令機能を提供するプラグイン。
*   [**ファイルをアーティファクトとして保存**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/save_files_as_artifacts_plugin.py): ユーザーメッセージに含まれるファイルをアーティファクトとして保存します。
*   [**ロギング**](https://github.com/google/adk-python/blame/main/src/google/adk/plugins/logging_plugin.py): 各エージェントワークフローのコールバックポイントで重要な情報をログに記録します。

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
  """エージェントとツールの呼び出しをカウントするカスタムプラグイン。"""

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
    print(f"[プラグイン] エージェントの実行回数：{self.agent_count}")

  async def before_model_callback(
      self, *, callback_context: CallbackContext, llm_request: LlmRequest
  ) -> None:
    """LLMリクエストの回数をカウントします。"""
    self.llm_request_count += 1
    print(f"[プラグイン] LLMリクエストの回数：{self.llm_request_count}")
```

このコード例では、エージェントのライフサイクル中にこれらのタスクの実行をカウントするために、`before_agent_callback`と`before_model_callback`のコールバックを実装しています。

### プラグインクラスの登録

`plugins`パラメータを使用して、`Runner`クラスの一部としてエージェントの初期化中に登録することで、プラグインクラスを統合します。このパラメータで複数のプラグインを指定できます。次のコード例は、前のセクションで定義した`CountInvocationPlugin`プラグインを単純なADKエージェントに登録する方法を示しています。

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
    model='gemini-1.5-flash',
    name='hello_world',
    description='ユーザーのクエリでhello worldを出力します。',
    instruction="""hello_worldツールを使用して、hello worldとユーザーのクエリを出力します。
    """,
    tools=[hello_world],
)

async def main():
  """エージェントのメインエントリポイント。"""
  prompt = 'hello world'
  runner = InMemoryRunner(
      agent=root_agent,
      app_name='test_app_with_plugin',

      # ここにプラグインを追加します。複数のプラグインを追加できます。
      plugins=[CountInvocationPlugin()],
  )

  # 残りは通常のADKランナーの起動と同じです。
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
    print(f'** {event.author}からイベントを取得しました')

if __name__ == "__main__":
  asyncio.run(main())
```

### プラグインを使用してエージェントを実行する

通常どおりにプラグインを実行します。以下に、コマンドラインを実行する方法を示します。

```sh
python3 -m path.to.main
```

プラグインは[ADK Webインターフェイス](../evaluate/#1-adk-web-run-evaluations-via-the-web-ui)ではサポートされていません。ADKワークフローでプラグインを使用する場合は、Webインターフェイスなしでワークフローを実行する必要があります。

前述のエージェントの出力は次のようになります。

```log
[プラグイン] エージェントの実行回数：1
[プラグイン] LLMリクエストの回数：1
** hello_worldからイベントを取得しました
Hello world: query is [hello world]
** hello_worldからイベントを取得しました
[プラグイン] LLMリクエストの回数：2
** hello_worldからイベントを取得しました
```


ADKエージェントの実行の詳細については、[クイックスタート](/adk-docs/ja/get-started/quickstart/#run-your-agent)ガイドを参照してください。

## プラグインを使用したワークフローの構築

プラグインコールバックフックは、エージェントの実行ライフサイクルを傍受、変更、さらには制御するロジックを実装するためのメカニズムです。各フックは、プラグインクラス内の特定のメソッドであり、重要な瞬間にコードを実行するように実装できます。フックの戻り値に基づいて、2つの動作モードから選択できます。

-   **監視するには：** 戻り値のない（`None`）フックを実装します。このアプローチは、ロギングやメトリックの収集などのタスクに使用され、エージェントのワークフローが中断されることなく次のステップに進むことができます。たとえば、プラグインで`after_tool_callback`を使用して、デバッグのためにすべてのツールの結果をログに記録できます。
-   **介入するには：** フックを実装して値を返します。このアプローチは、ワークフローを短絡させます。`Runner`は処理を停止し、後続のプラグインとモデル呼び出しなどの元々意図されていたアクションをスキップし、プラグインコールバックの戻り値を結果として使用します。一般的な使用例は、`before_model_callback`を実装してキャッシュされた`LlmResponse`を返し、冗長でコストのかかるAPI呼び出しを防ぐことです。
-   **修正するには：** フックを実装してコンテキストオブジェクトを変更します。このアプローチでは、モジュールの実行を中断することなく、実行するモジュールのコンテキストデータを変更できます。たとえば、モデルオブジェクトの実行に追加の標準化されたプロンプトテキストを追加します。

**注意：** プラグインコールバック関数は、オブジェクトレベルで実装されたコールバックよりも優先されます。この動作は、エージェント、モデル、またはツールオブジェクトのコールバックが実行される*前*に、Anyプラグインコールバックコードが実行されることを意味します。さらに、プラグインレベルのエージェントコールバックが空の（`None`）応答ではなく値を返した場合、エージェント、モデル、またはツールレベルのコールバックは*実行されません*（スキップされます）。

プラグインの設計は、コード実行の階層を確立し、グローバルな懸念事項をローカルのエージェントロジックから分離します。プラグインは、`PerformanceMonitoringPlugin`などの構築するステートフルな*モジュール*であり、コールバックフックは、そのモジュール内で実行される特定の*関数*です。このアーキテクチャは、次の重要な点で標準のエージェントコールバックとは根本的に異なります。

-   **スコープ：** プラグインフックは*グローバル*です。`Runner`にプラグインを一度登録すると、そのフックは管理するすべてのエージェント、モデル、ツールに普遍的に適用されます。対照的に、エージェントコールバックは*ローカル*であり、特定のエージェントインスタンスで個別に構成されます。
-   **実行順序：** プラグインが*優先*されます。特定のイベントに対して、プラグインフックは常に対応するエージェントコールバックの前に実行されます。このシステム動作により、プラグインは、セキュリティポリシー、ユニバーサルキャッシング、アプリケーション全体での一貫したロギングなどの横断的な機能を実装するための正しいアーキテクチャ上の選択肢になります。

### エージェントコールバックとプラグイン

前のセクションで述べたように、プラグインとエージェントコールバックにはいくつかの機能的な類似点があります。次の表は、プラグインとエージェントコールバックの違いをより詳細に比較したものです。

<table>
  <thead>
    <tr>
      <th></th>
      <th><strong>プラグイン</strong></th>
      <th><strong>エージェントコールバック</strong></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>スコープ</strong></td>
      <td><strong>グローバル</strong>：`Runner`内のすべてのエージェント/ツール/LLMに適用されます。</td>
      <td><strong>ローカル</strong>：構成されている特定のエージェントインスタンスにのみ適用されます。</td>
    </tr>
    <tr>
      <td><strong>主な使用例</strong></td>
      <td><strong>水平機能</strong>：ロギング、ポリシー、監視、グローバルキャッシング。</td>
      <td><strong>特定のエージェントロジック</strong>：単一のエージェントの動作または状態の変更。</td>
    </tr>
    <tr>
      <td><strong>構成</strong></td>
      <td>`Runner`で一度構成します。</td>
      <td>各`BaseAgent`インスタンスで個別に構成します。</td>
    </tr>
    <tr>
      <td><strong>実行順序</strong></td>
      <td>プラグインコールバックはエージェントコールバックの<strong>前</strong>に実行されます。</td>
      <td>エージェントコールバックはプラグインコールバックの<strong>後</strong>に実行されます。</td>
    </tr>
  </tbody>
</table>

## プラグインコールバックフック

プラグインクラスで定義するコールバック関数を使用して、プラグインがいつ呼び出されるかを定義します。コールバックは、ユーザーメッセージが受信されたとき、`Runner`、`Agent`、`Model`、または`Tool`が呼び出される前後、`Events`に対して、および`Model`または`Tool`のエラーが発生したときに使用できます。これらのコールバックには、エージェント、モデル、およびツールクラス内で定義されたコールバックが含まれ、優先されます。

次の図は、エージェントワークフロー中にプラグイン機能をアタッチして実行できるコールバックポイントを示しています。

![ADKプラグインコールバックフック](../assets/workflow-plugin-hooks.svg)
**図1.** プラグインコールバックフックの場所を含むADKエージェントワークフローの図。

次のセクションでは、プラグインで使用できるコールバックフックについて詳しく説明します。

-   [ユーザーメッセージコールバック](#user-message-callbacks)
-   [ランナースタートコールバック](#runner-start-callbacks)
-   [エージェント実行コールバック](#agent-execution-callbacks)
-   [モデルコールバック](#model-callbacks)
-   [ツールコールバック](#tool-callbacks)
-   [ランナーエンドコールバック](#runner-end-callbacks)

### ユーザーメッセージコールバック

*ユーザーメッセージc*allback（`on_user_message_callback`）は、ユーザーがメッセージを送信したときに発生します。`on_user_message_callback`は最初に実行されるフックであり、最初の入力を検査または変更する機会を与えます。

-   **実行タイミング：** このコールバックは、`runner.run()`の直後、他の処理の前に発生します。
-   **目的：** ユーザーの生の入力を検査または変更する最初の機会。
-   **フロー制御：** `types.Content`オブジェクトを返して、ユーザーの元のメッセージを**置き換え**ます。

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def on_user_message_callback(
    self,
    *,
    invocation_context: InvocationContext,
    user_message: types.Content,
) -> Optional[types.Content]:
```

### ランナースタートコールバック

*ランナースタート*コールバック（`before_run_callback`）は、`Runner`オブジェクトが潜在的に変更されたユーザーメッセージを受け取り、実行の準備をするときに発生します。`before_run_callback`はここで起動し、エージェントロジックが開始される前にグローバルなセットアップを可能にします。

-   **実行タイミング：** `runner.run()`が呼び出された直後、他の処理の前に発生します。
-   **目的：** ユーザーの生の入力を検査または変更する最初の機会。
-   **フロー制御：** `types.Content`オブジェクトを返して、ユーザーの元のメッセージを**置き換え**ます。

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def before_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[types.Content]:
```

### エージェント実行コールバック

*エージェント実行*コールバック（`before_agent`、`after_agent`）は、`Runner`オブジェクトがエージェントを呼び出すときに発生します。`before_agent_callback`は、エージェントの主要な作業が始まる直前に実行されます。主要な作業には、モデルやツールの呼び出しを含む、リクエストを処理するためのエージェントのプロセス全体が含まれます。エージェントがすべてのステップを完了し、結果を準備した後、`after_agent_callback`が実行されます。

**注意：**これらのコールバックを実装するプラグインは、エージェントレベルのコールバックが実行される*前*に実行されます。さらに、プラグインレベルのエージェントコールバックが`None`またはnull応答以外のものを返した場合、エージェントレベルのコールバックは*実行されません*（スキップされます）。

エージェントオブジェクトの一部として定義されたエージェントコールバックの詳細については、[コールバックの種類](../callbacks/types-of-callbacks/#agent-lifecycle-callbacks)を参照してください。

### モデルコールバック

モデルコールバック**（`before_model`、`after_model`、`on_model_error`）**は、モデルオブジェクトが実行される前後に行われます。プラグイン機能は、以下で詳しく説明するように、エラーが発生した場合のコールバックもサポートしています。

-   エージェントがAIモデルを呼び出す必要がある場合、`before_model_callback`が最初に実行されます。
-   モデルの呼び出しが成功した場合、`after_model_callback`が次に実行されます。
-   モデルの呼び出しが例外で失敗した場合、代わりに`on_model_error_callback`がトリガーされ、正常な回復が可能になります。

**注意：** **`before_model`**および`**after_model`**コールバックメソッドを実装するプラグインは、モデルレベルのコールバックが実行される*前*に実行されます。さらに、プラグインレベルのモデルコールバックが`None`またはnull応答以外のものを返した場合、モデルレベルのコールバックは*実行されません*（スキップされます）。

#### モデルのエラーコールバックの詳細

モデルオブジェクトのエラーコールバックは、次のように機能するプラグイン機能でのみサポートされています。

-   **実行タイミング：** モデルの呼び出し中に例外が発生した場合。
-   **一般的な使用例：** 正常なエラー処理、特定のエラーのログ記録、または「AIサービスは現在利用できません」などのフォールバック応答の返却。
-   **フロー制御：**
    -   `LlmResponse`オブジェクトを返して**例外を抑制**し、フォールバック結果を提供します。
    -   `None`を返して、元の例外が発生するようにします。

**注**：モデルオブジェクトの実行が`LlmResponse`を返した場合、システムは実行フローを再開し、`after_model_callback`が通常どおりトリガーされます。****

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

プラグインのツールコールバック**（`before_tool`、`after_tool`、`on_tool_error`）**は、ツールの実行前後、またはエラーが発生したときに発生します。プラグイン機能は、以下で詳しく説明するように、エラーが発生した場合のコールバックもサポートしています。

-   エージェントがツールを実行すると、`before_tool_callback`が最初に実行されます。
-   ツールが正常に実行されると、`after_tool_callback`が次に実行されます。
-   ツールが例外を発生させた場合、代わりに`on_tool_error_callback`がトリガーされ、障害を処理する機会が与えられます。`on_tool_error_callback`がdictを返した場合、`after_tool_callback`が通常どおりトリガーされます。

**注意：**これらのコールバックを実装するプラグインは、ツールレベルのコールバックが実行される*前*に実行されます。さらに、プラグインレベルのツールコールバックが`None`またはnull応答以外のものを返した場合、ツールレベルのコールバックは*実行されません*（スキップされます）。

#### ツールのエラーコールバックの詳細

ツールオブジェクトのエラーコールバックは、次のように機能するプラグイン機能でのみサポートされています。

-   **実行タイミング：** ツールの`run`メソッドの実行中に例外が発生した場合。
-   **目的：** 特定のツール例外（`APIError`など）のキャッチ、障害のログ記録、およびLLMへのユーザーフレンドリーなエラーメッセージの提供。
-   **フロー制御：** `dict`を返して**例外を抑制**し、フォールバック結果を提供します。`None`を返して、元の例外が発生するようにします。

**注**：`dict`を返すことにより、実行フローが再開され、`after_tool_callback`が通常どおりトリガーされます。

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

*イベントコールバック*（`on_event_callback`）は、エージェントがテキスト応答やツール呼び出し結果などの出力を生成するときに発生し、それらを`Event`オブジェクトとして生成します。`on_event_callback`は各イベントに対して起動し、クライアントにストリーミングされる前に変更できます。

-   **実行タイミング：** エージェントが`Event`を生成した後、ユーザーに送信される前。エージェントの実行で複数のイベントが生成される場合があります。
-   **目的：** イベントの変更やエンリッチ（メタデータの追加など）、または特定のイベントに基づく副作用のトリガーに役立ちます。
-   **フロー制御：** `Event`オブジェクトを返して、元のイベントを**置き換え**ます。

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def on_event_callback(
    self, *, invocation_context: InvocationContext, event: Event
) -> Optional[Event]:
```

### ランナーエンドコールバック

*ランナーエンド*コールバック**（`after_run_callback`）**は、エージェントがプロセス全体を完了し、すべてのイベントが処理されると、`Runner`が実行を完了するときに発生します。`after_run_callback`は最後のフックであり、クリーンアップと最終レポートに最適です。

-   **実行タイミング：** `Runner`がリクエストの実行を完全に完了した後。
-   **目的：** 接続のクローズやログとメトリックデータの最終処理など、グローバルなクリーンアップタスクに最適です。
-   **フロー制御：** このコールバックはティアダウン専用であり、最終結果を変更することはできません。

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def after_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[None]:
```

## 次のステップ

ADKプロジェクトにプラグインを開発して適用するための次のリソースを確認してください。

-   その他のADKプラグインのコード例については、[ADK Pythonリポジトリ](https://github.com/google/adk-python/tree/main/src/google/adk/plugins)を参照してください。
-   セキュリティ目的でプラグインを適用する方法については、[セキュリティガードレールのためのコールバックとプラグイン](/adk-docs/ja/safety/#callbacks-and-plugins-for-security-guardrails)を参照してください。