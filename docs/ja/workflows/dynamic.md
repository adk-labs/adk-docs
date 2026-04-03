# 動的ワークフロー

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.0.0</span><span class="lst-preview">Alpha</span>
</div>

ADK フレームワークは、[グラフベースワークフロー](/ja/workflows/)の
より柔軟で強力な代替手段として、ワークフローをプログラム的に定義する方法を
提供します。グラフベースのアプローチは、ワークフローノードを使って複数
ステップの静的なプロセス構造を組み立てるのに便利です。しかし、ワークフローの
ロジックパスが反復ループや複雑な分岐ロジックを含むようになると、グラフ
ベースのアプローチは要件に適さなくなったり、管理が煩雑になりすぎたりする
ことがあります。

ADK の動的ワークフローでは、グラフベースのパス構造を脇に置き、選択した
プログラミング言語の力を全面的に使ってワークフローを構築できます。動的
ワークフローでは、シンプルなデコレータでワークフローを作り、ワークフロー
ノードを関数として呼び出し、複雑なルーティングロジックを構築できます。
ADK の動的ワークフローには次の利点があります。

- **柔軟な制御フロー:** 静的グラフでは表現が難しい、または不可能なループ、
  条件分岐、再帰を使って実行順序を動的に定義できます。
- **プログラミング中心の体験:** グラフベースのルーティングの代わりに、
  `while` ループや `async/await` のような馴染み深い構文を使えます。
- **自動チェックポイント:** 動的ワークフローは各ノード実行を追跡します。
  ワークフロー再開時には成功済みのサブノードを自動的にスキップするため、
  複雑なロジックでも既定で耐障害性と再開可能性を持ちます。
- **カプセル化:** 低レベルノードを内部で組み合わせる *parent* ノードに
  ビジネスロジックを包み込み、ワークフロー全体のグラフをきれいで管理しやすい
  状態に保てます。

!!! example "Alpha リリース"

    ADK 2.0 は Alpha リリースであり、以前の ADK バージョンと併用する際に
    互換性を壊す変更が発生する可能性があります。プロダクション環境のように
    後方互換性が必要な場合は ADK 2.0 を使用しないでください。このリリースを
    ぜひ試していただき、
    [フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)
    をお寄せください。

この機能を試すための ADK 2.0 のインストール方法については、
[ADK 2.0 Alpha へようこそ](/ja/2.0/) を参照してください。

## はじめに

次の動的ワークフローのコード例は、1 つの関数ノードを含む基本的なワークフロー
の定義方法を示します。

```python
from google.adk import Workflow
from google.adk import Event
from google.adk import Context
from typing import Any

@node(name="hello_node")
def my_node(node_input: Any):
    return "Hello World"

# define a dynamic workflow node
@node(rerun_on_resume=True)
async def my_workflow(ctx: Context, node_input: str) -> str:
    # run_node executes a node and returns its output
    result = await ctx.run_node(my_node, input_data="hello")
    return result

# Run the workflow
root_agent = Workflow(
    name="root_agent",
    edges=[("START", my_workflow)],
)
```

この例では、便宜上 [***@node***](#node) アノテーションを使用し、記述コードを
できるだけシンプルに保っています。このアノテーションは、コードを ADK
動的ワークフローのコンテキストで実行できるようにするラッパーを生成します。

## 構成要素: ノードとワークフロー

ノードとワークフローは、ADK の動的ワークフローを構成する基本要素です。
これらのクラスは、ADK のコードベースワークフローへ統合できるように、コードを
ラップするために必要な機能を提供します。

### ノードと @node {#node}

ADK の動的ワークフローは、***BaseNode*** から派生したクラスである *nodes* で
構成されます。利用しやすいワークフローノードの単純な形として
***FunctionNode*** があり、***Workflow*** の中で実行するために必要な機能で
コードをラップできます。利便性のため、ADK フレームワークは ***@node***
アノテーションを提供しており、ノードラッパーを生成して、ボイラープレート
となるラッパーコードを最小限に抑えます。

```python
@node(name="hello_node")
def my_function_node(node_input: Any):
    return "Hello World"
```

次のコードスニペットは、***@node*** アノテーションを *使わない* 場合の
等価なコードを示します。

```python
# base function
def my_function_node(node_input: Any):
    return "Hello World"

# FunctionNode wrapper with options
success_node = FunctionNode(
    my_function_node,
    name="hello",
    rerun_on_resume=True,
)
```

外部ライブラリの関数をラップする必要がある場合、同じ関数から異なる設定で
複数のノードを作成する必要がある場合、または高度なオーケストレーションのために
レジストリでノード参照を管理している場合には、自分でノードラッパーコードを
作成すると便利です。

### ワークフロー

ADK の動的ワークフローでは、***Workflow*** クラスをノードの
オーケストレーションを担う主要コンテナとして使います。ノードを使って、
ノードの実行と、そのノード群の実行ロジック（順序やパス）を管理するコードで
動的ワークフローを定義します。次のコードサンプルを参照してください。

```python
@node(rerun_on_resume=True)
async def my_workflow(ctx):
    # run_node executes a node and returns its output
    result = await ctx.run_node(my_function_node, input_data="Hello")
    result_formatted = await ctx.run_node(my_formatting_node, input_data=result)
    return result_formatted

# Run the workflow
root_agent = Workflow(
    name="root_agent",
    edges=[("START", my_workflow)],
)
```

## データ処理

ADK で動的ワークフローを使う場合、
[グラフベースワークフロー](/ja/workflows/)よりもデータ受け渡しは
簡単です。ワークフローでは ***Context*** クラスの ***run_node()*** メソッドが
ノードの出力を直接返すためです。これにより、データ転送のためにセッション
状態や複雑なルーティング出力を直接扱う必要がなくなります。次のコード例は、
エージェントノードと関数ノードの間で文字列データを受け渡す方法を示します。

```python
from google.adk import Context

@node(rerun_on_resume=True)
async def editorial_workflow(ctx: Context, user_request: str):
    # Agent Node generates output
    raw_draft = await ctx.run_node(draft_agent, user_request)

    # Function Node formats text
    formatted_text = await ctx.run_node(format_function_node, raw_draft)

    return formatted_text
```

定義済みクラスを使って特定のデータスキーマを受け渡し、グラフベース
ワークフローノードと同様に入力および出力スキーマを構成することもできます。
次のコード例を参照してください。

```python
from google.adk import Agent
from google.adk import Context
from pydantic import BaseModel

class CityTime(BaseModel):
    time_info: str  # time information
    city: str       # city name

@node
def city_time_function(city: str):
    """Simulate returning the current time in a specified city."""
    return CityTime(time_info="10:10 AM", city=city)

city_report_agent = Agent(
    name="city_report_agent",
    model="gemini-2.5-flash",
    input_schema=CityTime,
    instruction="""output the data provided by the previous node.""",
)

@node # workflow node
async def city_workflow(ctx: Context):
    city_time = await ctx.run_node(city_time_function, "Paris")
    report_text = await ctx.run_node(city_report_agent, city_time)

    return report_text
```

ワークフローノード間のデータ処理の詳細は、
[エージェントワークフローのデータ処理](/ja/workflows/data-handling/)
を参照してください。

## ワークフロールート

ADK の動的ワークフローは、
[グラフベースワークフロー](/ja/workflows/)と比べてルーティング
ロジックの柔軟性が高く、反復ループやより複雑な分岐ロジックも扱えます。
このセクションでは、ルーティングに使えるいくつかのテクニックを説明します。

### シーケンスルート

ADK の動的ワークフローでは、グラフベースワークフローと同様に、順次的な
タスク処理を構築できます。次のコードスニペットは、エージェント、関数ノード、
2 つ目のエージェントで構成される動的ワークフローを示します。

```python
@node # workflow node
async def city_workflow(ctx: Context):
    city = await ctx.run_node(city_generator_agent)
    city_time = await ctx.run_node(city_time_function, city)
    report_text = await ctx.run_node(city_report_agent, city_time)

    return report_text
```

### ループルート

タスクに反復ループを使いたいワークフローでは、動的ワークフローのほうが必要な
ルーティングロジックをはるかに柔軟に定義できます。次のコード例は、コードの
生成、レビュー、更新を行うワークフローループを、動的ワークフローで構成する
方法を示します。

```python
coder_agent = LlmAgent(
    name="generator_agent",
    model="gemini-2.5-flash",
    instruction="Write python code for user request.",
    output_schema=str,
)

@node(name="lint_reviewer")
compile_lint_check = ApiNode()

fixer_agent = LlmAgent(
    name="generator_agent",
    model="gemini-2.5-flash",
    instruction="""Refactor current code {code}.
        Based on compile & lint review: {findings}""",
    output_schema=str,
)

@node # workflow node
async def code_workflow(ctx):
  code = await ctx.run_node(coder_agent)
  check_resp = await ctx.run_node(compile_lint_check, code)

  while check_resp.findings:
    yield Event(state={"code": code, "findings": check_resp.findings})
    code = await ctx.run_node(fixer_agent)

    check_resp = await ctx.run_node(compile_lint_check, code)

  return code
```

### 並列実行ルート

ADK の動的ワークフローは並列実行もサポートでき、その実現には `asyncio`
などの標準的な非同期ライブラリを使用できます。次のコード例は、並列実行を
サポートするワークフローノードの構築方法と、それをより大きなワークフローへ
統合する方法を示します。

```python
from google.adk.workflow import BaseNode
from google.adk import Context
from typing import Any
import asyncio

class ParallelNode(BaseNode):
    """A supervisor node that runs a worker node in parallel."""
    real_node: BaseNode

    async def run(self, ctx: Context, node_input: list[Any]):
        tasks = []

        # Dynamically schedule worker nodes for each item in the input list
        for item in node_input:
            # ctx.run_node returns an awaitable future for the ephemeral node
            tasks.append(ctx.run_node(self.real_node, item))

        # Use asyncio to gather results in parallel
        results = await asyncio.gather(*tasks)

        return results
```

!!! tip "ヒント: 並列ノードの再開"

    ワークフローフレームワークは、動的ワークフローが再開された場合、並列
    ワーカーノードを含め、失敗した、または中断されたワーカーノードのみが
    再実行されることを保証します。

## 人間入力

ADK の動的ワークフローには、Human in the Loop (HITL) ステップを含めることも
できます。ワークフローに人間入力を組み込むには、ワークフローを中断する
***BaseNode*** サブクラスを作成し、ユーザーへのリクエストと応答取得に使う
***RequestInput*** インスタンスを組み合わせます。次のコード例は、人間入力
ノードを構築してワークフローに含める方法を示します。

```python
from google.adk.workflow import BaseNode
from google.adk import Context
from google.adk.events import RequestInput
from typing import Any, AsyncGenerator

class GetInput(BaseNode):
    """A node that pauses execution and waits for human input."""
    rerun_on_resume = False  # Ensure the response is yielded as output on resume

    def __init__(self, request: RequestInput, name: str):
        self.request = request
        self.name = name

    def get_name(self) -> str:
        return self.name

    async def run(self) -> AsyncGenerator[Any, None]:
        # Yielding the request tells the workflow to pause and wait for input
        yield self.request

async def approval_process_node(ctx: Context, node_input: Any):
    """A parent node that coordinates a human approval step."""

    # Define the request for the user
    request = RequestInput(message="Please approve this request (Yes/No)")

    # Invoke the HITL node dynamically. The workflow pauses here.
    user_response = await ctx.run_node(GetInput(request, name="approval_step"))

    if user_response.lower() == "yes":
        return "Request Approved"
    else:
        return "Request Denied"
```

## 高度な機能

動的ワークフローには、より複雑な開発シナリオを扱うための高度な機能が
いくつか用意されています。これらの機能により、実行に対するより細かな制御と、
既存の技術インフラとのより良い統合が可能になります。

### 実行 ID

ADK フレームワークは、親 ID とカウンタに基づいて、子ノード実行の決定論的な
識別子 (ID) を生成します。ADK ワークフローは、各スケジュール済みノードの
以前の結果を識別するために、決定論的 ID を使用します。これらの ID は動的
ノードのスケジュール順序に基づいて生成され、チェックポイントや、ワークフロー
再開時または再実行時に正しい順序でタスクを再実行するために使われます。

#### カスタム実行 ID

並べ替え可能なリストを処理する場合など、ごく稀に安定した識別子が必要になる
ことがあり、その場合はノード実行時にカスタム ID を指定できます。一般には、
ワークフロータスクのリトライやプロセス再開への影響があるため、これを避ける
べきです。具体的には、これらの ID はノード状態を確認し、すでに実行済みの
ノードをスキップするために使われます。カスタム ID を与える場合は、
ワークフロー再実行時にも決定論的であり、入力に対して論理的に同一であり続ける
必要があります。次のコード例は、ワークフローでノードを実行する際にこのような
識別子を追加する方法を示します。

!!! warning "警告: カスタム実行 ID"

    カスタム実行 ID は作成しないでください。実行 ID はノードの実行順序を
    決定するために使われるため、カスタム実行 ID はワークフロー内のノードを
    再実行しようとするときに問題を引き起こす可能性があります。

```python
class Order(BaseModel):
  order_id: str
  cart_items: list[Product]

def shorten_link(ctx, node_input: str):

  orders = await get_orders()

  process_tasks = []
  for i, order in enumerate(orders):
    task = ctx.run_node(process_order, order, name=order.order_id))

    process_tasks.append(task)

  result = asyncio.gather(*process_tasks)

  yield result
```
