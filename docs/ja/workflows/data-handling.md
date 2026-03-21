# エージェントワークフローのデータ処理

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.0.0</span><span class="lst-preview">Alpha</span>
</div>

エージェントとグラフベースのノード間でデータを構造化し管理することは、
ADK で信頼性の高いプロセスを構築するうえで重要です。このガイドでは、
グラフベースワークフローと協調エージェントにおけるデータ処理を説明し、
グラフノード間で ***Events*** を使って情報がどのように送受信されるかを
扱います。events、data、content、state の主要パラメータを説明し、
データ形式のスキーマと特定の instruction 構文を使って、関数ノードと
エージェントノードの両方で構造化データ転送を実装する方法を説明します。

!!! example "Alpha リリース"

    ADK 2.0 は Alpha リリースであり、以前の ADK バージョンと併用する際に
    互換性を壊す変更が発生する可能性があります。プロダクション環境のように
    後方互換性が必要な場合は ADK 2.0 を使用しないでください。このリリースを
    ぜひ試していただき、
    [フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)
    をお寄せください。

!!! danger "警告: ADK 2.0 と ADK 1.0 のデータ保存システムを混在させないでください"

    ADK 2.0 プロジェクトで永続ストレージを使用する場合は、**セッション
    ストレージ、メモリシステム、評価データなどを含む、ただしそれらに限らない
    すべてのストレージを ADK 1.0 プロジェクトと ADK 2.0 プロジェクトで共有
    しないでください。** そうするとデータが失われたり、ADK 1.0 プロジェクトで
    使用できなくなったりする可能性があります。

## ワークフローグラフの Events

グラフベースワークフローの中では、***Events*** を使ってデータを渡します。
ワークフローグラフ内のすべての実行 *nodes* は Events を消費し、発行します。
このセクションでは、***Workflow*** 内のノード間でデータを送受信する基本を
説明します。Events には、ノード間で異なる種類のデータを伝送するための
固有パラメータがあります。ノードデータ処理の主なパラメータは次のとおりです。

- **`output`**: *nodes* 間で情報を渡すためのパラメータ
- **`message`**: ユーザーへの応答として意図されたデータ
- **`state`**: ADK セッション全体を通じて ***Events*** によりノード間で
  自動的に永続化されるデータ

Events には、Event のソースノードなど、ワークフローに関する追加情報も
含まれます。

### Events によるノードの入出力

グラフ内の各ノードは、***Event*** クラスを通じてデータを受信し送信します。
次のコードスニペットのように、***yield*** 構文を使ってデータを次のノードへ
引き渡します。

```python
from google.adk import Event

def my_function_node(node_input: str):
    output_value = node_input.upper()
    return Event(output=output_value) # "THE RESULT"
```

追加処理が不要な ***Event*** データを出力する場合は、***return*** 構文を
使います。追加処理が必要なデータを発行する場合や、2 件以上のデータ項目を
生成する場合は、複数の ***yield*** コマンドを使えます。各 ***yield***
呼び出しは、グラフの次のノードへ渡される Event 上のデータオブジェクトの
リストに追加されます。パラメータなしの ***return*** または ***yield*** は、
次のノードへ `None` 値を渡します。

### Event `output` パラメータ

***Event*** の ***output*** パラメータは、グラフの次のノードへデータを渡す
標準的な方法です。次のノードは、以下のコードサンプルのように、そのデータを
含む ***node input*** オブジェクトを受け取ります。

```python
def my_function_node_1():
    return Event(output="The Result")

def my_function_node_2(node_input: Content):
    output_value = node_input.parts[0].text.lower()
    return Event(output=output_value) # "the result"
```

次のコードサンプルのように、シリアライズ可能な形式の、より長く構造化された
データを渡すこともできます。

```python
def my_function_node_3():
    yield Event(
        output={
            "city_name": "Paris",
            "city_time": "10:10 AM",
        },
    )
```

!!! warning "注意: Event.output の制限"

    ノードは 1 回の実行につき、***Event.output*** データペイロードを 1 つしか
    発行できません。この制限により、ノード内で複数回 ***yield*** することは
    可能ですが、***Event.output*** を含む ***yield*** を 2 回以上行うと
    ランタイムエラーになります。

### Event `message` パラメータ

***Event*** の ***message*** パラメータは、ユーザー応答として意図された
データを渡すために使用します。一般に、ユーザーへ情報を提供したり、ユーザー
から情報を求めたりする場合を除いて、エージェントコードで ***message***
パラメータを使うべきではありません。次のコード例は、ワークフロー実行中に
ユーザーへ情報を提供する方法を示します。

```python
async def user_message(node_input: str):
  """Tell user research process is starting."""
  yield Event(message="Beginning research process...")
```

### Event `state` パラメータ

***Event*** の ***state*** パラメータは、ADK セッション全体を通して保持する
少量のデータ値を維持するために使います。state パラメータの値は Nodes 間で
自動的に永続化され、より複雑なワークフローの実行を導くために使われます。
Nodes は state 値を変更でき、変更された state 値は downstream Nodes で利用
できます。次のコード例は、state がノード間でどのように永続化されるかを
示します。

```python
async def init_state_node(attempts: int = 0):
  yield Event(
      state={
          "attempts": attempts,
      },
  )

async def task_attempt_node(node_input: Content, attempts: int):
  yield Event(
      state={
          "attempts": attempts + 1,
      },
  )

async def read_state_node(ctx: WorkflowContext):
  print(f"attempts state: {ctx.state}") # attempts state: attempts: 1

root_agent = Workflow(
    name="root_agent",
    edges=[("START", init_state_node, task_attempt_node, read_state_node)],
)
```

!!! warning "注意: `state` プロパティのデータ制限"

    state パラメータは、ノード間で *大量のデータを永続化する用途* に使うべき
    ではありません。大量データの永続化には、Workflow のライフサイクル中に
    artifacts やデータベース Tools など、他のデータ永続化メカニズムを使用
    してください。

## スキーマでノードの入出力データを制約する

入力および出力データのスキーマを設定することで、***FunctionNodes*** や
**Agents** を含む任意のノードの入出力データ形式を制約できます。次の
パラメータは、任意のノードで任意に設定できるオプションです。エージェント
プロジェクトの要件に応じて、これらのパラメータの両方、またはいずれか一方を
設定できます。

- **`input_schema`**: ***BaseModel*** を拡張するクラスを使って期待する入力
  スキーマを設定します。
- **`output_schema`**: ***BaseModel*** を拡張するクラスを使って必要な出力
  スキーマを設定します。

以下のコード例は、サブエージェントに入力スキーマと出力スキーマの両方を
設定する方法を示します。

```python
from google.adk import Agent
from pydantic import BaseModel

class FlightSearchInput(BaseModel):
    origin: str           # Airport code "SFO"
    destination: str      # Airport code "CDG"
    departure_date: date  # date(2026, 3, 15)
    passengers: int = 1   # Number of passengers

class FlightSearchOutput(BaseModel):
    flights: list[Flight]
    cheapest_price: float

flight_searcher = Agent(
    name="flight_searcher",
    instruction="Search for available flights.",
    input_schema=FlightSearchInput,
    output_schema=FlightSearchOutput,
    tools=[search_flights_api],
    mode="single-turn",
    ...
)

assistant = Agent(
    name="assistant",
    instruction="You help users plan trips.",
    sub_agents=[flight_searcher],
    ...
)
```

## エージェントで構造化データにアクセスする

サブエージェントや関数ノードのようなワークフローノードから、構造化データを
エージェントへ渡す場合、そのデータをエージェントの instructions に
組み込むための特定の構文を使えます。具体的には、中括弧 `{ }` を使って入力
スキーマのプロパティを選択するか、`< >` を使って入力スキーマのプロパティ、
`from` キーワード、およびデータを提供するノード名を指定できます。次の
コードスニペットは、エージェントの ***input schema*** を通じて渡された
データを取り込む 2 つの方法を示します。

```python
class CityTime(BaseModel):
    time_info: str  # time information
    city: str       # city name

def lookup_time_function(city: str):
    """Simulate returning the current time in the specified city."""
    return Event(output=CityTime(time_info='10:10 AM', city=city))

city_report_agent = Agent(
    name="city_report_agent",
    model="gemini-2.5-flash",
    input_schema=CityTime,

    # data selection based on class and parameter
    # instruction="""
    #     Return a sentence in the following format:
    #     It is {CityTime.time_info} in {CityTime.city} right now.
    # """,

    # more restrictive data selection based on source node name
    instruction="""
        Return a sentence in the following format:
        It is <CityTime.time_info from lookup_time_function> in
        <CityTime.city from lookup_time_function> right now.
    """,
)

root_agent = Workflow(
    name="root_agent",
    edges=[
        (START, city_generator_agent, lookup_time_function, city_report_agent)
    ],
)
```

このワークフローの完全版ではありませんが、単純化したバージョンについては
[グラフベースのエージェントワークフロー](/adk-docs/ja/workflows/#はじめに)
を参照してください。
