# 동적 워크플로

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v2.0.0</span><span class="lst-preview">Alpha</span>
</div>

ADK 프레임워크는 [그래프 기반 워크플로](/adk-docs/ko/workflows/)의 더 유연하고
강력한 대안으로, 워크플로를 프로그래밍 방식으로 정의할 수 있는 방법을 제공합니다.
그래프 기반 접근법은 워크플로 노드로 다단계의 정적 프로세스 구조를 조합하는 데
편리합니다. 하지만 워크플로의 논리 경로가 반복 루프나 복잡한 분기 로직을 포함해
더 복잡해지면, 그래프 기반 접근법은 요구에 맞지 않거나 관리하기 너무 번거로워질
수 있습니다.

ADK의 동적 워크플로를 사용하면 그래프 기반 경로 구조를 내려놓고, 선택한
프로그래밍 언어의 모든 기능을 사용해 워크플로를 구축할 수 있습니다. 동적
워크플로에서는 간단한 데코레이터로 워크플로를 만들고, 워크플로 노드를 함수처럼
호출하며, 복잡한 라우팅 로직을 구현할 수 있습니다. ADK 동적 워크플로의 장점은
다음과 같습니다.

- **유연한 제어 흐름:** 정적 그래프로 표현하기 어렵거나 불가능한 루프,
  조건문, 재귀를 사용해 실행 순서를 동적으로 정의할 수 있습니다.
- **프로그래밍 중심 경험:** 그래프 기반 라우팅 대신 `while` 루프와
  `async/await` 같은 익숙한 구문을 사용할 수 있습니다.
- **자동 체크포인팅:** 동적 워크플로는 각 노드 실행을 추적합니다. 워크플로를
  재개할 때 성공한 하위 노드는 자동으로 건너뛰므로, 복잡한 로직도 기본적으로
  내구성과 재개 가능성을 갖습니다.
- **캡슐화:** 비즈니스 로직을 내부적으로 더 낮은 수준의 노드로 조합하는
  *부모* 노드 안에 감싸서, 전체 워크플로 그래프를 깔끔하고 관리 가능하게
  유지할 수 있습니다.

!!! example "Alpha 릴리스"

    ADK 2.0은 Alpha 릴리스이며, 이전 버전의 ADK와 함께 사용할 때 호환성이
    깨지는 변경이 발생할 수 있습니다. 프로덕션 환경처럼 하위 호환성이 필요한
    경우에는 ADK 2.0을 사용하지 마세요. 이 릴리스를 테스트해 보시고
    [피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)을
    보내주시기 바랍니다.

이 기능을 시험하기 위해 ADK 2.0을 설치하는 방법은
[ADK 2.0에 오신 것을 환영합니다](/adk-docs/ko/2.0/)를 참조하세요.

## 시작하기

다음 동적 워크플로 코드 예시는 함수 하나를 가진 기본 워크플로를 정의하는 방법을
보여줍니다.

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

이 예시는 편의를 위해 [***@node***](#node) 어노테이션을 사용하며, 작성 코드를
가능한 한 단순하게 유지합니다. 이 어노테이션은 ADK 동적 워크플로 컨텍스트에서
실행될 수 있도록 래퍼를 생성합니다.

## 구성 요소: 노드와 워크플로

노드와 워크플로는 ADK 동적 워크플로의 기본 구성 요소입니다. 이 클래스들은
코드가 ADK의 코드 기반 워크플로에 통합될 수 있도록 감싸는 데 필요한 기능을
제공합니다.

### 노드와 @node {#node}

ADK의 동적 워크플로는 ***BaseNode*** 에서 파생된 클래스인 *nodes* 로
구성됩니다. 사용 가능한 워크플로 노드의 단순한 형태로는 ***FunctionNode*** 가
있으며, 이는 ***Workflow*** 안에서 실행되기 위해 필요한 기능으로 코드를 감쌀 수
있게 합니다. 편의를 위해 ADK 프레임워크는 ***@node*** 어노테이션을 제공하며,
이 어노테이션은 노드 래퍼를 생성해 보일러플레이트 래퍼 코드를 최소화합니다.

```python
@node(name="hello_node")
def my_function_node(node_input: Any):
    return "Hello World"
```

다음 코드 스니펫은 ***@node*** 어노테이션을 *사용하지 않은* 동등한 코드를
보여줍니다.

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

외부 라이브러리의 함수를 감싸야 하거나, 동일한 함수를 다른 구성으로 여러 노드로
생성해야 하거나, 고급 오케스트레이션을 위해 레지스트리에서 노드 참조를 관리해야
하는 경우에는 래퍼 코드를 직접 작성하는 것이 유용할 수 있습니다.

### 워크플로

ADK 동적 워크플로에서 ***Workflow*** 클래스는 노드를 오케스트레이션하는 기본
컨테이너입니다. 노드를 사용해 동적 워크플로를 정의하고, 그 안의 코드로 노드
실행과 실행 로직(순서와 경로)을 관리합니다. 다음 코드 샘플을 참고하세요.

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

## 데이터 처리

ADK에서 동적 워크플로를 사용할 때는 [그래프 기반 워크플로](/adk-docs/ko/workflows/)
보다 데이터 전달이 더 단순합니다. 워크플로에서는 ***Context*** 클래스의
***run_node()*** 메서드가 노드의 출력을 직접 반환하기 때문입니다. 따라서
데이터 전송을 위해 세션 상태나 복잡한 라우팅 출력을 직접 다룰 필요가 없습니다.
다음 코드 예시는 에이전트 노드와 함수 노드 사이에서 문자열 데이터를 전달하는
방법을 보여줍니다.

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

또한 정의된 클래스를 사용해 특정 데이터 스키마를 전달하고, 그래프 기반 워크플로
노드와 유사하게 입력 및 출력 스키마를 구성할 수도 있습니다. 다음 코드 예시를
참고하세요.

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

워크플로 노드 사이의 데이터 처리에 대한 자세한 내용은
[에이전트 워크플로의 데이터 처리](/adk-docs/ko/workflows/data-handling/)를
참조하세요.

## 워크플로 경로

ADK의 동적 워크플로는 [그래프 기반 워크플로](/adk-docs/ko/workflows/)보다
라우팅 로직 측면에서 더 높은 유연성을 제공하며, 반복 루프나 더 복잡한 분기
로직도 표현할 수 있습니다. 이 섹션에서는 라우팅에 사용할 수 있는 몇 가지
기법을 설명합니다.

### 순차 경로

ADK의 동적 워크플로를 사용하면 그래프 기반 워크플로와 마찬가지로 순차적 작업
처리를 만들 수 있습니다. 다음 코드 스니펫은 에이전트, 함수 노드, 두 번째
에이전트로 구성된 동적 워크플로를 보여줍니다.

```python
@node # workflow node
async def city_workflow(ctx: Context):
    city = await ctx.run_node(city_generator_agent)
    city_time = await ctx.run_node(city_time_function, city)
    report_text = await ctx.run_node(city_report_agent, city_time)

    return report_text
```

### 루프 경로

작업에 반복 루프가 필요한 워크플로에서는, 동적 워크플로가 필요한 라우팅 로직을
훨씬 더 유연하게 정의할 수 있습니다. 다음 코드 예시는 동적 워크플로를 사용해
코드를 생성, 검토, 업데이트하는 워크플로 루프를 구성하는 방법을 보여줍니다.

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

### 병렬 실행 경로

ADK의 동적 워크플로는 병렬 실행도 지원할 수 있으며, 이를 구현하기 위해
`asyncio` 같은 표준 비동기 라이브러리를 사용할 수 있습니다. 다음 코드 예시는
병렬 실행을 지원하는 워크플로 노드를 만드는 방법과, 이를 더 큰 워크플로에
통합하는 방법을 보여줍니다.

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

!!! tip "팁: 병렬 노드 재개"

    워크플로 프레임워크는 동적 워크플로가 재개될 때, 병렬 작업자 노드를 포함해
    실패했거나 중단된 작업자 노드만 다시 실행되도록 보장합니다.

## 인간 입력

ADK의 동적 워크플로는 human in the loop(HITL) 단계도 포함할 수 있습니다.
인간 입력을 워크플로에 넣으려면, 워크플로를 중단하는 ***BaseNode*** 하위 클래스를
만들고, 사용자에게 요청을 전달하고 응답을 받기 위한 ***RequestInput*** 인스턴스를
함께 사용하면 됩니다. 다음 코드 예시는 인간 입력 노드를 만들고 이를 워크플로에
포함하는 방법을 보여줍니다.

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

## 고급 기능

동적 워크플로는 더 복잡한 개발 시나리오를 처리하기 위한 몇 가지 고급 기능을
제공합니다. 이러한 기능은 실행에 대한 더 세밀한 제어와, 기존 기술 인프라와의
더 나은 통합을 가능하게 합니다.

### 실행 ID

ADK 프레임워크는 부모 ID와 카운터를 기반으로 자식 노드 실행에 대한 결정론적
식별자(ID)를 생성합니다. ADK 워크플로는 각 예약된 노드에 대해 결정론적 ID를
사용해 이전 결과를 식별합니다. 이 ID는 동적 노드 예약 순서를 기준으로 생성되며,
체크포인팅과 워크플로 재개 또는 재실행 시 올바른 순서로 작업을 다시 실행하는 데
사용됩니다.

#### 사용자 지정 실행 ID

드문 경우이지만, 재정렬 가능한 목록을 처리하는 상황처럼 안정적인 식별자가
필요할 수 있으며, 이때는 노드를 실행할 때 사용자 지정 ID를 제공할 수 있습니다.
일반적으로는 워크플로 작업 재시도와 프로세스 재개에 미치는 영향 때문에 이를
피해야 합니다. 구체적으로, 이 ID는 노드 상태를 확인하고 이미 실행된 노드를
건너뛰는 데 사용됩니다. 사용자 지정 ID를 제공한다면, 워크플로 재실행 시에도
결정론적이어야 하고 입력에 대해 논리적으로 동일하게 유지되어야 합니다. 다음
코드는 워크플로에서 노드를 실행할 때 이런 식별자를 추가하는 방법을 보여줍니다.

!!! warning "경고: 사용자 지정 실행 ID"

    사용자 지정 실행 ID를 만들지 마세요. 실행 ID는 노드 실행 순서를 결정하는 데
    사용되므로, 사용자 지정 실행 ID는 워크플로에서 노드를 다시 실행하려 할 때
    문제를 일으킬 수 있습니다.

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
