# プラグイン

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.7.0</span>
</div>

Agent Development Kit（ADK）のプラグインは、コールバックフックを使用してエージェントワークフローライフサイクルのさまざまな段階で実行できるカスタムコードモジュールです。エージェントワークフロー全体に適用できる機能にプラグインを使用します。プラグインの一般的なアプリケーションは次のとおりです。

-   **ロギングとトレース**: デバッグとパフォーマンス分析のために、エージェント、ツール、および生成AIモデルのアクティビティの詳細なログを作成します。
-   **ポリシーの適用**: ユーザーが特定のツールを使用する権限があるかどうかを確認し、権限がない場合はその実行を防ぐ関数など、セキュリティガードレールを実装します。
-   **監視とメトリック**: トークンの使用状況、実行時間、呼び出し回数に関するメトリックを収集し、Prometheusや[Google Cloud Observability](https://cloud.google.com/stackdriver/docs)（旧Stackdriver）などの監視システムにエクスポートします。
-   **応答のキャッシュ**: 以前にリクエストが行われたかどうかを確認し、コストのかかる、または時間のかかるAIモデルやツールの呼び出しをスキップして、キャッシュされた応答を返すことができます。
-   **リクエストまたは応答の変更**: AIモデルのプロンプトに情報を動的に追加したり、ツールの出力応答を標準化したりします。

!!! tip
    セキュリティガードレールとポリシーを実装する場合は、コールバックよりもモジュール性と柔軟性に優れたADKプラグインを使用してください。詳細については、[セキュリティガードレールのためのコールバックとプラグイン](/adk-docs/safety/#callbacks-and-plugins-for-security-guardrails)を参照してください。

!!! warning "注意"
    プラグインは[ADK Webインターフェイス](../evaluate/#1-adk-web-run-evaluations-via-the-web-ui)ではサポートされていません。ADKワークフローでプラグインを使用する場合は、Webインターフェイスなしでワークフローを実行する必要があります。

## プラグインの仕組み

ADKプラグインは`BasePlugin`クラスを拡張し、エージェントライフサイクルのどこでプラグインを実行する必要があるかを示す1つ以上の`callback`メソッドを含みます。エージェントの`Runner`クラスにプラグインを登録することで、エージェントにプラグインを統合します。エージェントアプリケーションでプラグインをトリガーできる場所と方法の詳細については、[プラグインコールバックフック](#plugin-callback-hooks)を参照してください。

プラグイン機能は、ADKの拡張可能なアーキテクチャの重要な設計要素である[コールバック](../callbacks/)に基づいています。一般的なエージェントコールバックは*特定のタスク*に対して*単一のエージェント、単一のツール*に構成されますが、プラグインは`Runner`に*一度*登録され、そのコールバックは、そのランナーによって管理されるすべてのエージェント、ツール、およびLLM呼び出しに*グローバルに*適用されます。プラグインを使用すると、関連するコールバック関数をまとめてパッケージ化し、ワークフロー全体で使用できます。これにより、プラグインはエージェントアプリケーション全体にまたがる機能を実装するための理想的なソリューションになります。

## 事前構築済みプラグイン

ADKには、エージェントワークフローにすぐに追加できるいくつかのプラグインが含まれています。

*   [**リフレクトと再試行ツール**](/adk-docs/plugins/reflect-and-retry/)：ツールの障害を追跡し、ツールリクエストをインテリジェントに再試行します。
*   [**BigQueryロギング**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/bigquery_logging_plugin.py)：BigQueryを使用してエージェントのロギングと分析を有効にします。
*   [**コンテキストフィルター**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/context_filter_plugin.py)：生成AIコンテキストをフィルタリングしてサイズを縮小します。
*   [**グローバルインストラクション**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/global_instruction_plugin.py)：アプリレベルでグローバルインストラクション機能を提供するプラグイン。
*   [**ファイルをアーティファクトとして保存**](https://github.com/google/adk-python/blob/main/src/google/adk/plugins/save_files_as_artifacts_plugin.py)：ユーザーメッセージに含まれるファイルをアーティファクトとして保存します。
*   [**ロギング**](https://github.com/google/adk-python/blame/main/src/google/adk/plugins/logging_plugin.py)：各エージェントワークフローのコールバックポイントで重要な情報をログに記録します。

## プラグインの定義と登録

このセクションでは、プラグインクラスを定義し、エージェントワークフローの一部として登録する方法について説明します。完全なコード例については、リポジトリの[プラグインの基本](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_basic)を参照してください。

### プラグインクラスの作成

次のコード例に示すように、`BasePlugin`クラスを拡張し、1つ以上の`callback`メソッドを追加することから始めます。

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
    print(f"[プラグイン] エージェントの実行回数: {self.agent_count}")

  async def before_model_callback(
      self, *, callback_context: CallbackContext, llm_request: LlmRequest
  ) -> None:
    """LLMリクエストの回数をカウントします。"""
    self.llm_request_count += 1
    print(f"[プラグイン] LLMリクエストの回数: {self.llm_request_count}")
```

このコード例では、エージェントのライフサイクル中にこれらのタスクの実行をカウントするために、`before_agent_callback`と`before_model_callback`のコールバックを実装しています。

### プラグインクラスの登録

`plugins`パラメータを使用して、`Runner`クラスの一部としてエージェントの初期化中にプラグインクラスを登録して統合します。このパラメータを使用して複数のプラグインを指定できます。次のコード例は、前のセクションで定義した`CountInvocationPlugin`プラグインを単純なADKエージェントに登録する方法を示しています。

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

### プラグインを使用したエージェントの実行

通常どおりプラグインを実行します。以下に、コマンドラインの実行方法を示します。

```sh
python3 -m path.to.main
```

プラグインは[ADK Webインターフェイス](../evaluate/#1-adk-web-run-evaluations-via-the-web-ui)ではサポートされていません。ADKワークフローでプラグインを使用する場合は、Webインターフェイスなしでワークフローを実行する必要があります。

前述のエージェントの出力は、次のようになります。

```log
[プラグイン] エージェントの実行回数: 1
[プラグイン] LLMリクエストの回数: 1
** hello_worldからイベントを取得しました
Hello world: query is [hello world]
** hello_worldからイベントを取得しました
[プラグイン] LLMリクエストの回数: 2
** hello_worldからイベントを取得しました
```


ADKエージェントの実行の詳細については、[クイックスタート](/adk-docs/get-started/quickstart/#run-your-agent)ガイドを参照してください。

## プラグインを使用したワークフローの構築

プラグインコールバックフックは、エージェントの実行ライフサイクルを傍受、変更、さらには制御するロジックを実装するためのメカニズムです。各フックは、プラグインクラス内の特定のメソッドであり、重要な瞬間にコードを実行するように実装できます。フックの戻り値に基づいて、2つの動作モードから選択できます。

-   **監視するには：**戻り値のない（`None`）フックを実装します。このアプローチは、ロギングやメトリックの収集などのタスクに使用され、エージェントのワークフローが中断されることなく次のステップに進むことができます。たとえば、プラグインで`after_tool_callback`を使用して、デバッグのためにすべてのツールの結果をログに記録できます。
-   **介入するには：**フックを実装して値を返します。このアプローチは、ワークフローを短絡させます。`Runner`は処理を停止し、後続のプラグインと、モデル呼び出しなどの元々意図されていたアクションをスキップし、プラグインコールバックの戻り値を結果として使用します。一般的な使用例は、`before_model_callback`を実装してキャッシュされた`LlmResponse`を返し、冗長でコストのかかるAPI呼び出しを防ぐことです。
-   **修正するには：**フックを実装してコンテキストオブジェクトを変更します。このアプローチでは、そのモジュールの実行を妨げることなく、実行されるモジュールのコンテキストデータを変更できます。たとえば、モデルオブジェクトの実行のために、追加の標準化されたプロンプトテキストを追加します。

**注意：**プラグインコールバック関数は、オブジェクトレベルで実装されたコールバックよりも優先されます。この動作は、エージェント、モデル、またはツールオブジェクトのコールバックが実行される*前に*、プラグインコールバックコードが実行されることを意味します。さらに、プラグインレベルのエージェントコールバックが空の（`None`）応答ではなく値を返す場合、エージェント、モデル、またはツールレベルのコールバックは*実行されません*（スキップされます）。

プラグインの設計は、コード実行の階層を確立し、グローバルな懸念事項をローカルのエージェントロジックから分離します。プラグインは、`PerformanceMonitoringPlugin`などの構築するステートフルな*モジュール*であり、コールバックフックは、そのモジュール内で実行される特定の*関数*です。このアーキテクチャは、次の重要な点で標準のエージェントコールバックとは根本的に異なります。

-   **スコープ：**プラグインフックは*グローバル*です。`Runner`にプラグインを一度登録すると、そのフックは、管理するすべてのエージェント、モデル、およびツールに普遍的に適用されます。対照的に、エージェントコールバックは*ローカル*であり、特定のエージェントインスタンスで個別に構成されます。
-   **実行順序：**プラグインには*優先順位*があります。特定のイベントに対して、プラグインフックは常に対応するエージェントコールバックの前に実行されます。このシステム動作により、プラグインは、セキュリティポリシー、ユニバーサルキャッシング、アプリケーション全体にわたる一貫したロギングなどの横断的な機能を実装するための正しいアーキテクチャ上の選択肢となります。

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
      <td><strong>グローバル</strong>：<code>Runner</code>内のすべてのエージェント/ツール/LLMに適用されます。</td>
      <td><strong>ローカル</strong>：構成されている特定のエージェントインスタンスにのみ適用されます。</td>
    </tr>
    <tr>
      <td><strong>主な使用例</strong></td>
      <td><strong>水平機能</strong>：ロギング、ポリシー、監視、グローバルキャッシング。</td>
      <td><strong>特定のエージェントロジック</strong>：単一のエージェントの動作または状態の変更。</td>
    </tr>
    <tr>
      <td><strong>構成</strong></td>
      <td><code>Runner</code>で一度構成します。</td>
      <td>各<code>BaseAgent</code>インスタンスで個別に構成します。</td>
    </tr>
    <tr>
      <td><strong>実行順序</strong></td>
      <td>プラグインコールバックはエージェントコールバックの<strong>前</strong>に実行されます。</td>
      <td>エージェントコールバックはプラグインコールバックの<strong>後</strong>に実行されます。</td>
    </tr>
  </tbody>
</table>

## プラグインコールバックフック

プラグインクラスで定義するコールバック関数を使用して、プラグインがいつ呼び出されるかを定義します。コールバックは、ユーザーメッセージが受信されたとき、`Runner`、`Agent`、`Model`、または`Tool`が呼び出される前後、`Events`に対して、および`Model`または`Tool`エラーが発生したときに使用できます。これらのコールバックには、エージェント、モデル、およびツールクラス内で定義されたコールバックが含まれ、優先されます。

次の図は、エージェントワークフロー中にプラグイン機能をアタッチして実行できるコールバックポイントを示しています。

![ADKプラグインコールバックフック](../assets/workflow-plugin-hooks.svg)
**図1.** プラグインコールバックフックの場所を含むADKエージェントワークフローの図。

次のセクションでは、プラグインで使用できるコールバックフックについて詳しく説明します。

-   [ユーザーメッセージコールバック](#user-message-callbacks)
-   [ランナー開始コールバック](#runner-start-callbacks)
-   [エージェント実行コールバック](#agent-execution-callbacks)
-   [モデルコールバック](#model-callbacks)
-   [ツールコールバック](#tool-callbacks)
-   [ランナー終了コールバック](#runner-end-callbacks)

### ユーザーメッセージコールバック

*ユーザーメッセージ*コールバック（`on_user_message_callback`）は、ユーザーがメッセージを送信したときに発生します。`on_user_message_callback`は、最初に実行されるフックであり、初期入力を検査または変更する機会を提供します。

-   **実行タイミング：**このコールバックは、他の処理の前に`runner.run()`の直後に発生します。
-   **目的：**ユーザーの生の入力を検査または変更する最初の機会。
-   **フロー制御：**ユーザーの元のメッセージを**置き換える**ために`types.Content`オブジェクトを返します。

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

*ランナー開始*コールバック（`before_run_callback`）は、`Runner`オブジェクトが潜在的に変更されたユーザーメッセージを受け取り、実行の準備をするときに発生します。`before_run_callback`はここで起動し、エージェントロジックが開始される前にグローバルなセットアップを可能にします。

-   **実行タイミング：**他の処理の前に`runner.run()`が呼び出された直後に発生します。
-   **目的：**ユーザーの生の入力を検査または変更する最初の機会。
-   **フロー制御：**ユーザーの元のメッセージを**置き換える**ために`types.Content`オブジェクトを返します。

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def before_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[types.Content]:
```

### エージェント実行コールバック

*エージェント実行*コールバック（`before_agent`、`after_agent`）は、`Runner`オブジェクトがエージェントを呼び出すときに発生します。`before_agent_callback`は、エージェントの主要な作業が開始される直前に実行されます。主要な作業には、モデルやツールの呼び出しを含む、リクエストを処理するためのエージェントのプロセス全体が含まれます。エージェントがすべてのステップを完了し、結果を準備した後、`after_agent_callback`が実行されます。

**注意：**これらのコールバックを実装するプラグインは、エージェントレベルのコールバックが実行される*前に*実行されます。さらに、プラグインレベルのエージェントコールバックが`None`またはnull応答以外のものを返す場合、エージェントレベルのコールバックは*実行されません*（スキップされます）。

エージェントオブジェクトの一部として定義されたエージェントコールバックの詳細については、[コールバックの種類](../callbacks/types-of-callbacks/#agent-lifecycle-callbacks)を参照してください。

### モデルコールバック

モデルコールバック**（`before_model`、`after_model`、`on_model_error`）**は、モデルオブジェクトが実行される前後に行われます。プラグイン機能は、以下に詳述するように、エラー発生時のコールバックもサポートしています。

-   エージェントがAIモデルを呼び出す必要がある場合、`before_model_callback`が最初に実行されます。
-   モデルの呼び出しが成功した場合、`after_model_callback`が次に実行されます。
-   モデルの呼び出しが例外で失敗した場合、代わりに`on_model_error_callback`がトリガーされ、正常な回復が可能になります。

**注意：** **`before_model`**および`**after_model`**コールバックメソッドを実装するプラグインは、モデルレベルのコールバックが実行される*前に*実行されます。さらに、プラグインレベルのモデルコールバックが`None`またはnull応答以外のものを返す場合、モデルレベルのコールバックは*実行されません*（スキップされます）。

#### モデルのエラーコールバックの詳細

モデルオブジェクトのエラーコールバックは、プラグイン機能でのみサポートされており、次のように機能します。

-   **実行タイミング：**モデルの呼び出し中に例外が発生した場合。
-   **一般的な使用例：**正常なエラー処理、特定のエラーのロギング、または「AIサービスは現在利用できません」などのフォールバック応答の返却。
-   **フロー制御：**
    -   **例外を抑制**し、フォールバック結果を提供するために`LlmResponse`オブジェクトを返します。
    -   元の例外を発生させるために`None`を返します。

**注**：モデルオブジェクトの実行が`LlmResponse`を返す場合、システムは実行フローを再開し、`after_model_callback`が通常どおりトリガーされます。****

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

プラグインのツールコールバック**（`before_tool`、`after_tool`、`on_tool_error`）**は、ツールの実行前後、またはエラー発生時に発生します。プラグイン機能は、以下に詳述するように、エラー発生時のコールバックもサポートしています。

-   エージェントがツールを実行すると、`before_tool_callback`が最初に実行されます。
-   ツールが正常に実行されると、`after_tool_callback`が次に実行されます。
-   ツールが例外を発生させた場合、代わりに`on_tool_error_callback`がトリガーされ、障害を処理する機会が与えられます。`on_tool_error_callback`がdictを返す場合、`after_tool_callback`は通常どおりトリガーされます。

**注意：**これらのコールバックを実装するプラグインは、ツールレベルのコールバックが実行される*前に*実行されます。さらに、プラグインレベルのツールコールバックが`None`またはnull応答以外のものを返す場合、ツールレベルのコールバックは*実行されません*（スキップされます）。

#### ツールのエラーコールバックの詳細

ツールオブジェクトのエラーコールバックは、プラグイン機能でのみサポートされており、次のように機能します。

-   **実行タイミング：**ツールの`run`メソッドの実行中に例外が発生した場合。
-   **目的：**特定のツール例外（`APIError`など）のキャッチ、障害のロギング、およびLLMへのユーザーフレンドリーなエラーメッセージの返却。
-   **フロー制御：** **例外を抑制**し、フォールバック結果を提供するために`dict`を返します。元の例外を発生させるために`None`を返します。

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

*イベントコールバック*（`on_event_callback`）は、エージェントがテキスト応答やツール呼び出し結果などの出力を生成すると、それらを`Event`オブジェクトとして生成するときに発生します。`on_event_callback`は各イベントに対して起動し、クライアントにストリーミングされる前に変更する機会を提供します。

-   **実行タイミング：**エージェントが`Event`を生成した後、ユーザーに送信される前。エージェントの実行は複数のイベントを生成する場合があります。
-   **目的：**イベントの変更または拡充（メタデータの追加など）、または特定のイベントに基づく副作用のトリガーに役立ちます。
-   **フロー制御：**元のイベントを**置き換える**ために`Event`オブジェクトを返します。

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def on_event_callback(
    self, *, invocation_context: InvocationContext, event: Event
) -> Optional[Event]:
```

### ランナー終了コールバック

*ランナー終了*コールバック**（`after_run_callback`）**は、エージェントがプロセス全体を完了し、すべてのイベントが処理されると、`Runner`が実行を完了するときに発生します。`after_run_callback`は、クリーンアップと最終レポートに最適な最後のフックです。

-   **実行タイミング：** `Runner`がリクエストの実行を完全に完了した後。
-   **目的：**接続のクローズやログとメトリックデータの最終処理など、グローバルなクリーンアップタスクに最適です。
-   **フロー制御：**このコールバックはティアダウン専用であり、最終結果を変更することはできません。

次のコード例は、このコールバックの基本的な構文を示しています。

```py
async def after_run_callback(
    self, *, invocation_context: InvocationContext
) -> Optional[None]:
```

## 次のステップ

ADKプロジェクトにプラグインを開発して適用するための次のリソースを確認してください。

-   その他のADKプラグインのコード例については、[ADK Pythonリポジトリ](https://github.com/google/adk-python/tree/main/src/google/adk/plugins)を参照してください。
-   セキュリティ目的でプラグインを適用する方法については、[セキュリティガードレールのためのコールバックとプラグイン](/adk-docs/safety/#callbacks-and-plugins-for-security-guardrails)を参照してください。
