# 에이전트 워크플로용 그래프 경로 구축

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v2.0.0</span><span class="lst-preview">Alpha</span>
</div>

ADK의 그래프 기반 워크플로는 에이전트 로직을 실행 노드와 엣지의 그래프로
정의하여, 인공지능(AI) 추론과 코드 로직을 결합한 더 신뢰성 높은 프로세스를
구축할 수 있게 합니다. 이러한 워크플로를 사용하면 코드 함수, AI 기반 에이전트,
도구, 인간 입력을 캡슐화하는 실행 노드의 논리적 경로를 만들 수 있습니다.
라우팅 로직을 명시적으로 설계함으로써, 이 접근 방식은 코드 안에서 구체적이고
단계적인 프로세스 워크플로를 정의할 수 있게 하며, 프롬프트 기반 에이전트만
사용하는 방식보다 더 높은 정밀도와 신뢰성을 제공합니다.

![Graph-based flight upgrade agent](/adk-docs/assets/graph-workflow-router.svg)

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

**그림 1.** 작업 그래프의 시각화와 이를 구현하는 ***Workflow*** 코드입니다.

그래프 기반 에이전트 워크플로를 사용할 때의 장점은 프롬프트 기반 에이전트보다
제어성, 예측 가능성, 신뢰성이 크게 높아진다는 점입니다. 전체 프로세스
워크플로를 코드로 정의함으로써, 작업이 어떻게 라우팅되고 실행되는지를 더 많이
제어할 수 있습니다. 이러한 구조화된 노드 정의는 에이전트의 예측 가능성을 높이고,
정의된 단계와 프로세스 관리가 필요한 복잡한 작업의 신뢰성을 강화합니다.

!!! example "Alpha 릴리스"

    ADK 2.0은 Alpha 릴리스이며, 이전 버전의 ADK와 함께 사용할 때 호환성이
    깨지는 변경이 발생할 수 있습니다. 프로덕션 환경처럼 하위 호환성이 필요한
    경우에는 ADK 2.0을 사용하지 마세요. 이 릴리스를 테스트해 보시고
    [피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)을
    보내주시기 바랍니다.

[그래프 기반 에이전트 워크플로](/adk-docs/ko/workflows/)를 확인하여 ADK의
그래프 기반 워크플로를 시작해 보세요.

## 노드

그래프는 실행 노드로 구성됩니다. 이러한 *노드*는 ***Agents***, ADK
***Tools***, 인간 입력 작업, 또는 직접 작성한 코드 함수가 될 수 있습니다.
노드는 이전에 실행된 노드로부터 입력을 받을 수 있고, ***Event*** 객체를 통해
데이터를 내보낼 수 있습니다. 다음 예시는 텍스트 입력을 처리하고 텍스트 출력을
보내는 간단한 ***FunctionNode*** 를 보여줍니다.

```python
from google.adk import Event

def my_function_node(node_input: str):
    input_text_modified = node_input.upper()
    return Event(output=input_text_modified)
```

노드 사이에서 데이터를 전달하는 방법에 대한 자세한 내용은
[에이전트 워크플로의 데이터 처리](/adk-docs/ko/workflows/data-handling/)를
참조하세요.

## 워크플로 그래프 구문

그래프는 논리적 실행 경로와 따라야 할 *노드* 및 조건을 정의하는 ***edges***
배열을 만들어 정의합니다. 이 섹션은 ***edges*** 배열에서 사용하는 그래프 구문의
개요를 제공합니다. 다음 코드 예시는 순서대로 실행되는 두 개의 노드를 가진
기본 워크플로를 보여줍니다.

```python
from google.adk import Workflow

root_agent = Workflow(
    name="sequential_workflow",
    edges=[("START", task_A_node, task_B_node)],
)
```

!!! caution "주의: 워크플로와 에이전트 제한"

    그래프 기반 워크플로에 ***Agents*** 또는 ***LlmAgents*** 를 추가할 수
    있지만, 이들은 task 또는 single-turn 모드로 설정되어야 합니다. 에이전트
    모드에 대한 자세한 내용은
    [협업 에이전트 팀 구축하기](/adk-docs/ko/workflows/collaboration/#모드-구성과-동작)을
    참조하세요.

### 순차 경로

***edges*** 배열은 배열에 제시된 노드 순서에 따라 실행되며, 첫 번째 행에서
시작해 이후 행으로 진행하면서 실행을 완료합니다. ***edges*** 배열의 첫 번째
행은 ***START*** 키워드를 사용하여 그래프 실행의 시작을 나타내며, 나열된 각
노드가 순서대로 실행됩니다. 다음 코드 스니펫을 참고하세요.

```python
edges=[("START", task_A_node)]  # single node run
edges=[("START",
        task_A_node,
        task_B_node,
        task_C_node)]           # 3 nodes run in order
```

다음 코드 스니펫처럼, 워크플로 그래프 시작 시 병렬 작업을 시작하기 위해
***START*** 를 두 번 이상 사용할 수도 있습니다.

```python
edges=[
    ("START", parallel_task_A),
    ("START", parallel_task_B),
    ("START", parallel_task_C),
]
```

!!! warning "주의: 병렬 노드 제한"

    모든 워크플로 노드나 서브에이전트를 병렬로 실행할 수 있는 것은 아닙니다.
    특히 동일한 에이전트 세션 안에서 여러 개의 상호작용형 채팅 세션을 실행할 수는
    없습니다.

### 분기 경로

START 키워드 뒤에 오는 ***edges*** 배열의 이후 행은 노드를 위한 추가 실행
로직을 정의합니다. 분기 경로를 만들려면, 하나 이상의 경로 값을 출력하는 노드,
보통 ***FunctionNode*** 를 정의합니다. 엣지 그래프에서는 다음 코드 예시처럼
경로 값과 대상 노드를 사용해 실행 로직을 정의합니다.

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

## 병렬 작업: fan out 및 join 경로

여러 병렬 노드로 실행을 분기시키는 그래프를 만들 수 있으며, 일반적으로는 각
노드의 출력을 모아 후속 처리를 해야 합니다. 이를 위해 각 병렬 작업이 완료될
때까지 기다렸다가, 이 노드들의 출력 집합을 다음 노드로 전달하는
***JoinNode*** 객체를 사용합니다.

![Tasks connecting to a JoinNode](/adk-docs/assets/graph-joinnode.svg)

**그림 2.** 병렬 작업 노드의 출력은 JoinNode 객체를 사용해 합칠 수 있습니다.

다음 코드 스니펫은 기본적인 ***JoinNode*** 객체를 구현하고, 이를 사용해 모든
노드의 출력을 모으는 방법을 보여줍니다.

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

!!! warning "주의: 미완료 노드로 인해 멈추는 JoinNode"

    ***JoinNode*** 객체는 상류의 모든 노드가 Event 출력을 제공한 이후에만
    진행합니다. 상류 노드 중 하나라도 출력을 제공하지 못하면 JoinNode 는 멈추고
    워크플로 실행도 중단됩니다. ***JoinNode*** 로 출력을 보내는 모든 노드에는
    반드시 실패 대비용 출력 경로를 포함하세요.

## 중첩 워크플로

더 복잡한 워크플로를 구축할 때는 특정 작업의 기능을 재사용 가능한 워크플로로
캡슐화하고 싶을 수 있습니다. 이 목적을 위해 하나 이상의 ***Workflow*** 객체를
다른 워크플로 에이전트 그래프 내부의 노드로 사용할 수 있습니다.

![Nested Workflows inside a parent Workflow](/adk-docs/assets/graph-workflow-nodes.svg)

**그림 3.** 부모 ***Workflow*** 내부 노드로 사용되는 중첩 ***Workflows***.

다음 코드 스니펫은 두 개의 중첩 ***Workflow*** 객체(`workflow_B`,
`workflow_C`)를 그래프 노드로 사용하는 워크플로 에이전트를 구현하는 방법을
보여줍니다.

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

### 중첩 워크플로 데이터 출력

중첩된 Workflow 객체의 출력은 개별 노드와는 약간 다르게 동작합니다. 중첩
워크플로가 내부 노드 하나를 완료하면, 그 데이터는 중첩 워크플로 그래프의 다음
노드로 전달되는 동시에, 프로세스 추적성을 위해 해당 노드의 Event 가 부모
워크플로로 버블업됩니다. 중첩 워크플로가 마지막 노드를 완료하면, 부모 노드는
최종 리프 노드에서 데이터를 추출하여 이를 중첩 워크플로의 출력으로 내보냅니다.
