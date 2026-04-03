# エージェントワークフローのグラフルートを構築する

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.0.0</span><span class="lst-preview">Alpha</span>
</div>

ADK のグラフベースワークフローは、エージェントロジックを実行ノードと
エッジのグラフとして定義し、人工知能 (AI) の推論とコードロジックを
組み合わせた、より信頼性の高いプロセスを構築できるようにします。これらの
ワークフローでは、コード関数、AI 搭載エージェント、Tools、人間入力を
カプセル化する実行ノードの論理ルートを作成できます。ルーティングロジックを
明示的に設計することで、このアプローチはコード内で具体的かつ段階的な
プロセスワークフローを定義でき、純粋にプロンプトベースのエージェントより
高い精度と信頼性を提供します。

![Graph-based flight upgrade agent](/assets/graph-workflow-router.svg)

```python
root_agent = Workflow(
  name="routing_workflow",
  edges=[
    ("START", process_message, router),
    (router,
      {
        "output-1": response_1,
        "output-2": response_2,
        "output-3": response_3,
      },
    ),
  ],
)
```

**図 1.** タスクグラフの可視化と、それを実装する ***Workflow*** コードです。

グラフベースのエージェントワークフローを使う利点は、プロンプトベース
エージェントと比べて、制御性、予測可能性、信頼性が大幅に向上することです。
全体のプロセスワークフローをコードで定義することで、タスクがどのように
ルーティングされ、実行されるかをより細かく制御できます。この構造化された
ノード定義は、エージェントの予測可能性を向上させ、定義済みの手順と
プロセス管理を必要とする複雑なタスクに対する信頼性を高めます。

!!! example "Alpha リリース"

    ADK 2.0 は Alpha リリースであり、以前の ADK バージョンと併用する際に
    互換性を壊す変更が発生する可能性があります。プロダクション環境のように
    後方互換性が必要な場合は ADK 2.0 を使用しないでください。このリリースを
    ぜひ試していただき、
    [フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)
    をお寄せください。

[グラフベースのエージェントワークフロー](/ja/workflows/) を確認して、
ADK のグラフベースワークフローを始めてください。

## ノード

グラフは実行ノードで構成されます。これらの *nodes* は ***Agents***、ADK
***Tools***、人間入力タスク、または自分で書いたコード関数にできます。
ノードは先に実行されたノードから入力を受け取り、***Event*** オブジェクトを
通じてデータを出力できます。次の例は、テキスト入力を処理してテキスト出力を
送る単純な ***FunctionNode*** を示します。

```python
from google.adk import Event

def my_function_node(node_input: str):
    input_text_modified = node_input.upper()
    return Event(output=input_text_modified)
```

ノード間でデータを転送する方法の詳細は、
[エージェントワークフローのデータ処理](/ja/workflows/data-handling/)
を参照してください。

## ワークフローグラフの構文

グラフは、従うべき論理的な実行パス、*nodes*、条件を定義する ***edges***
配列を作成して定義します。このセクションでは、***edges*** 配列における
グラフ構文の概要を説明します。次のコード例は、順番に実行される 2 つの
ノードを持つ基本ワークフローを示します。

```python
from google.adk import Workflow

root_agent = Workflow(
    name="sequential_workflow",
    edges=[("START", task_A_node, task_B_node)],
)
```

!!! caution "注意: ワークフローとエージェントの制限"

    グラフベースワークフローには ***Agents*** や ***LlmAgents*** を追加でき
    ますが、これらは task または single-turn モードに設定されていなければ
    なりません。エージェントモードの詳細は、
    [協調エージェントチームを構築する](/ja/workflows/collaboration/#モード設定と挙動)
    を参照してください。

### シーケンスルート

***edges*** 配列は、配列内に提示されたノードの順序に基づいて実行され、
最初の行から始まり、その後の行へ進みながら実行を完了します。***edges***
配列の最初の行は ***START*** キーワードを使ってグラフ実行の開始を示し、
列挙された各ノードが順番に実行されます。次のコードスニペットを参照して
ください。

```python
edges=[("START", task_A_node)]  # single node run
edges=[("START",
        task_A_node,
        task_B_node,
        task_C_node)]           # 3 nodes run in order
```

次のコードスニペットのように、ワークフローグラフの開始時に並列タスクを
開始するため、***START*** を複数回使うこともできます。

```python
edges=[
    ("START", parallel_task_A),
    ("START", parallel_task_B),
    ("START", parallel_task_C),
]
```

!!! warning "注意: 並列ノードの制限"

    すべてのワークフローノードやサブエージェントを並列実行できるわけでは
    ありません。特に、同一エージェントセッション内で複数の対話型チャット
    セッションを実行することはできません。

### 分岐ルート

START キーワードの後に続く ***edges*** 配列の行は、ノードの追加実行ロジックを
定義します。分岐パスでは、1 つ以上のルート値を出力するノード、通常は
***FunctionNode*** を定義します。エッジグラフでは、次のコード例のように、
ルート値とターゲットノードを使って実行ロジックを定義します。

```python
def router(node_input: str):
    """Simulate a routing decision"""
    return Event(route="RUN_TASK_C")

root_agent = Workflow(
    name="routing_workflow",
    edges=[
        ("START", task_A_node, router),
        (router,
          {
            # "route value": node_to_run
            "RUN_TASK_B": task_B_node,
            "RUN_TASK_C": task_C_node,
          },
        ),
    ],
)
```

## 並列タスク: fan out と join パス

複数の並列ノードへ実行を分岐させるグラフを作成でき、通常は各ノードの出力を
集約してさらに処理する必要があります。これは ***JoinNode*** オブジェクトを
使って実現します。JoinNode は各並列タスクの完了を待ち、それらのノードの
出力コレクションを次のノードへ渡します。

![Tasks connecting to a JoinNode](/assets/graph-joinnode.svg)

**図 2.** 並列タスクノードの出力は JoinNode オブジェクトを使って集約
できます。

次のコードスニペットは、基本的な ***JoinNode*** オブジェクトを実装し、
これを使ってすべてのノードの出力を集約する方法を示します。

```python
from google.adk.workflow import JoinNode

my_join_node = JoinNode(name="my_join_node")

edges=[
    ("START", parallel_task_A, my_join_node),
    ("START", parallel_task_B, my_join_node),
    ("START", parallel_task_C, my_join_node),
    (my_join_node, final_task_D),
]
```

!!! warning "注意: 未完了ノードによる JoinNode の停止"

    ***JoinNode*** オブジェクトは、上流のすべてのノードが Event 出力を提供
    して初めて進行します。上流ノードのいずれかが出力を提供しない場合、
    JoinNode は停止し、ワークフロー実行も止まります。***JoinNode*** に
    出力するすべてのノードには、必ずフェイルセーフの出力を含めてください。

## ネストされたワークフロー

より複雑なワークフローを構築する際には、特定のタスクの機能を再利用可能な
ワークフローへカプセル化したい場合があります。この目的のために、1 つ以上の
***Workflow*** オブジェクトを、別のワークフローエージェントグラフ内の
ノードとして使用できます。

![Nested Workflows inside a parent Workflow](/assets/graph-workflow-nodes.svg)

**図 3.** 親 ***Workflow*** 内のノードとして利用されるネストされた
***Workflows***。

次のコードスニペットは、2 つのネストされた ***Workflow*** オブジェクト
(`workflow_B`, `workflow_C`) をグラフノードとして使うワークフロー
エージェントの実装方法を示します。

```python
from google.adk import Workflow

root_agent = Workflow(
    name="parent_workflow",
    edges=[
       ("START", task_A1, router),
       (router, {
            "RUN_WORKFLOW_B": workflow_B,
            "RUN_WORKFLOW_C": workflow_C,
            },
       ),
    ],
)
```

### ネストされたワークフローのデータ出力

ネストされた Workflow オブジェクトの出力は、個別ノードとは少し異なる形で
機能します。ネストされたワークフローがその中のノードを 1 つ完了すると、
そのデータはネストされたワークフローグラフの次のノードへ伝えられると同時に、
プロセストレーサビリティのために、そのノードの Event が親ワークフローへ
バブルアップされます。ネストされたワークフローがプロセスの最後のノードを
完了すると、親ノードは最終リーフノードからデータを抽出し、それをネストされた
ワークフローの出力として送出します。
