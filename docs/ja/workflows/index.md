# グラフベースのエージェントワークフロー

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.0.0</span><span class="lst-preview">Alpha</span>
</div>

ADK のグラフベースワークフローを使うと、コードロジックと AI の推論能力を
組み合わせた決定論的なプロセスを構築でき、より精密な制御を備えた
エージェントを作成できます。グラフベースワークフローでは、エージェントの
ロジックを実行ノードとエッジのグラフとして定義し、AI 搭載エージェントと
決定論的なツールやコードを組み合わせられます。

![Graph-based flight upgrade agent](/assets/workflow-design.svg)

**図 1.** 関数、Human in the Loop、ツール、LLM 機能など、異なる種類の
ワークフローノードを組み合わせた、フライトアップグレード向けの
グラフベースエージェント設計です。

事前構築済みの ADK
[ワークフローエージェント](/ja/agents/workflow-agents/) である
[Sequential Agents](/ja/agents/workflow-agents/sequential-agents/)
などは、エージェント群の間で定義済みのプロセスフロー制御のみを提供します。
長いプロンプトやツールを備えた標準的な ADK エージェントを引き続き構築し、
それらをグラフベースワークフローエージェントで利用することもできます。
より精密な制御が必要な場合、ワークフローエージェントのグラフは、タスクを
どのようにルーティングし実行するかに対して、より大きな柔軟性を与えます。
グラフベースワークフローには次の利点があります。

- **精密なロジックを定義:** さまざまなノード間の遷移を管理するルーティング
  ロジックを明示的に設計できます。
- **複雑な構造を実装:** 分岐や状態管理をサポートするエージェント
  ワークフローを構築できます。
- **AI なしで関数チェーンを実行:** 生成 AI モデルを呼び出さずに、
  エージェントツールや独自コードを実行できます。
- **信頼性を向上:** プロンプトだけに頼るのではなく、構造化されたノード定義を
  用いることで、エージェントの予測可能性を高められます。

!!! example "Alpha リリース"

    ADK 2.0 は Alpha リリースであり、以前の ADK バージョンと併用する際に
    互換性を壊す変更が発生する可能性があります。プロダクション環境のように
    後方互換性が必要な場合は ADK 2.0 を使用しないでください。このリリースを
    ぜひ試していただき、
    [フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)
    をお寄せください。

[ADK 2.0 のインストール](/ja/2.0/#install) の手順に従い、その後で
以下の説明を確認してグラフベースワークフローを始めてください。

## はじめに

このセクションでは、グラフベースエージェントの始め方を説明します。次の
例では、都市名を生成し、コード関数でその都市の現在時刻を調べ、最後の
エージェントがその情報を報告する順次的なグラフベースエージェント
ワークフローの作成方法を示します。

```python
from google.adk import Agent
from google.adk import Workflow
from google.adk import Event
from pydantic import BaseModel

city_generator_agent = Agent(
    name="city_generator_agent",
    model="gemini-2.5-flash",
    instruction="""Return the name of a random city.
      Return only the name, nothing else.""",
    output_schema=str,
)

class CityTime(BaseModel):
    time_info: str  # time information
    city: str       # city name

def lookup_time_function(node_input: str):
    """Simulate returning the current time in the specified city."""
    return CityTime(time_info="10:10 AM", city=node_input)

city_report_agent = Agent(
    name="city_report_agent",
    model="gemini-2.5-flash",
    input_schema=CityTime,
    instruction="""Output following line:
    It is {CityTime.time_info} in {CityTime.city} right now.""",
    output_schema=str,
)

def completed_message_function(node_input: str):
    return Event(
        message=f"{node_input}\n WORKFLOW COMPLETED.",
    )

root_agent = Workflow(
    name="root_agent",
    edges=[
        ("START", city_generator_agent, lookup_time_function,
          city_report_agent, completed_message_function)
    ],
)
```

このサンプルコードでは、***Workflow*** クラスを使って、シンプルな順次
ワークフローを組み立て、AI エージェント処理とコード実行を交互に行う方法を
示しています。長いプロンプトとツール呼び出しを持つ単一のエージェントでも
これらの手順は実行できますが、グラフベースのアプローチを使うと、タスクの
実行順序と各ステップのデータ出力を正確に制御できます。

グラフベースワークフローにおけるデータ処理の詳細は、
[ワークフローノードとエージェントでのデータ処理](/ja/workflows/data-handling/)
を参照してください。

## グラフでプロセスを構築する

プロンプトベースのエージェントでは、ADK エージェントの instructions
フィールドにタスクや手順の説明を書き込むことで、多段階のプロセスを定義
できます。しかし、手順や説明が長く複雑になるにつれて、エージェントが各
ステップやガイドラインに従っていることを保証するのは難しくなり、信頼性も
下がります。

グラフベースワークフローエージェントは、プロセス全体のワークフローを
コードで具体的に定義できるため、プロンプトベースエージェントに対して大きな
利点をもたらします。グラフベースエージェントワークフローでは、プロセスの
各ステップをグラフ内の実行 ***Node*** として定義でき、各ノードは AI
エージェント、Tool、または自分で書いたコードにできます。次の図は、単純な
プロンプトベースエージェントがどのようにワークフローエージェントグラフへ
変換されるかを示しています。

![Prompt-based agent to graph-based workflow](/assets/prompts-to-graphs.svg)

**図 2.** プロンプトベースエージェントの指示がグラフベースワークフローへ
変換された構造です。

プロンプトベースエージェントからグラフベースワークフローエージェントへ
移行すると、手順内のタスクを明示的に分解して、特定の実行フローを定義
できます。一度定義すれば、エージェントアプリケーションはグラフ内の
ステップに従って進行し、必要に応じて非決定的な AI 搭載エージェントと
決定論的なコードを切り替えます。

次のコードサンプルは、図 2 のワークフローグラフを ***Workflow***
クラスを使ったグラフベースエージェントへどのように変換できるかを示します。

```python
process_message = Agent(
    name="process_message",
    model="gemini-2.5-flash",
    instruction="""Classify user message into either "BUG", "CUSTOMER_SUPPORT",
      or "LOGISTICS". If you think a message applies to more than one category,
      reply with a comma separated list of categories.
   """,
    output_schema=str,
)

def router(node_input: str):
    routes = node_input.split(",")
    routes = [route.strip() for route in routes]
    return Event(route=routes)

def response_1_bug():
    return Event(message="Handling bug...")

def response_2_support():
    return Event(message="Handling customer support...")

def response_3_logistics():
    return Event(message="Handling logistics...")

root_agent = Workflow(
   name="routing_workflow",
   edges=[
       ("START", process_message, router),
       ( router,
           {
               "BUG": response_1_bug,
               "CUSTOMER_SUPPORT": response_2_support,
               "LOGISTICS": response_3_logistics,
           }
       )
   ],
)
```

このサンプルコードは、***edges*** 配列を使って、*nodes* の集合間にルートを
持つグラフを定義する方法を示しています。ノードは、エージェント、Tools、
独自コード、さらには追加の ***Workflows*** まで含められる離散的なタスク
です。ワークフロー向けの高度なグラフ構築については、
[ワークフローエージェントのグラフルートを構築する](/ja/workflows/graph-routes/)
を参照してください。

## 既知の制限事項 {#known-limitations}

グラフベースワークフローにはいくつかの既知の制限があります。次の ADK
機能とは *互換性がありません*。

- **Live Streaming** 機能は、グラフベースワークフローと互換性が
  ありません。
- **Integrations:** 一部のサードパーティ
  [Integrations](/ja/integrations/) は、グラフベースワークフローと
  互換性がない場合があります。
