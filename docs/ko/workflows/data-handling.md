# 에이전트 워크플로의 데이터 처리

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v2.0.0</span><span class="lst-preview">Alpha</span>
</div>

에이전트와 그래프 기반 노트 사이에서 데이터를 구조화하고 관리하는 일은 ADK로
신뢰성 높은 프로세스를 구축하는 데 매우 중요합니다. 이 가이드는 그래프 기반
워크플로와 협업 에이전트에서의 데이터 처리를 설명하며, 그래프 노드 사이에서
***Events*** 를 사용해 정보가 어떻게 전달되고 수신되는지를 다룹니다. 이벤트,
데이터, 콘텐츠, 상태에 대한 핵심 매개변수를 설명하고, 데이터 형식 스키마와
특정 instruction 구문을 사용해 함수 노드와 에이전트 노드 모두에서 구조화된
데이터 전송을 구현하는 방법을 설명합니다.

!!! example "Alpha 릴리스"

    ADK 2.0은 Alpha 릴리스이며, 이전 버전의 ADK와 함께 사용할 때 호환성이
    깨지는 변경이 발생할 수 있습니다. 프로덕션 환경처럼 하위 호환성이 필요한
    경우에는 ADK 2.0을 사용하지 마세요. 이 릴리스를 테스트해 보시고
    [피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)을
    보내주시기 바랍니다.

!!! danger "경고: ADK 2.0과 ADK 1.0 데이터 저장 시스템을 혼용하지 마세요"

    ADK 2.0 프로젝트에 영구 저장소를 사용하는 경우, **세션 저장소, 메모리 시스템,
    평가 데이터 등을 포함하되 이에 한정되지 않는 모든 저장소를 ADK 1.0
    프로젝트와 ADK 2.0 프로젝트가 공유하지 않도록 하세요.** 그렇게 하면 데이터가
    손실되거나, ADK 1.0 프로젝트에서 사용할 수 없게 될 수 있습니다.

## 워크플로 그래프 Events

그래프 기반 워크플로 내부에서는 ***Events*** 를 사용해 데이터를 전달합니다.
워크플로 그래프의 모든 실행 *노드*는 Events 를 소비하고 방출합니다. 이 섹션은
***Workflow*** 안에서 노드 사이에 데이터를 전송하고 수신하는 기본 사항을
다룹니다. Events 는 노드 사이에서 서로 다른 종류의 데이터를 전송하기 위한
특정 매개변수를 가집니다. 노드 데이터 처리의 핵심 매개변수는 다음과 같습니다.

- **`output`**: *노드* 사이에 정보를 전달하기 위한 매개변수
- **`message`**: 사용자에게 응답으로 전달할 데이터
- **`state`**: ADK 세션 전체에서 ***Events*** 를 통해 노드 사이에 자동으로
  영속화되는 데이터

Events 는 이 외에도 Event 의 소스 노드 등 워크플로에 대한 추가 정보를 함께
전달합니다.

### Events 를 통한 노드 입력과 출력

그래프의 각 노드는 ***Event*** 클래스를 통해 데이터를 수신하고 전송합니다.
다음 코드 스니펫처럼 ***yield*** 구문을 사용해 데이터를 다음 노드로 넘길 수
있습니다.

```python
from google.adk import Event

def my_function_node(node_input: str):
    output_value = node_input.upper()
    return Event(output=output_value) # "THE RESULT"
```

추가 처리가 필요하지 않은 ***Event*** 데이터를 출력할 때는 ***return*** 구문을
사용합니다. 추가 처리가 필요한 데이터를 내보내거나, 두 개 이상의 데이터 항목을
생성하는 경우에는 둘 이상의 ***yield*** 명령을 사용할 수 있습니다. 각
***yield*** 호출은 그래프의 다음 노드로 전달되는 Event 의 데이터 객체 목록에
추가됩니다. 매개변수 없이 사용하는 ***return*** 또는 ***yield*** 는 다음
노드로 `None` 값을 전달합니다.

### Event `output` 매개변수

***Event*** 의 ***output*** 매개변수는 그래프의 다음 노드로 데이터를 전달하는
표준 방식입니다. 다음 노드는 다음 코드 샘플처럼 해당 데이터를 담은 ***node input***
객체를 받게 됩니다.

```python
def my_function_node_1():
    return Event(output="The Result")

def my_function_node_2(node_input: Content):
    output_value = node_input.parts[0].text.lower()
    return Event(output=output_value) # "the result"
```

다음 코드 샘플처럼, 직렬화 가능한 형식의 더 길고 구조화된 데이터도 전달할 수
있습니다.

```python
def my_function_node_3():
    yield Event(
        output={
            "city_name": "Paris",
            "city_time": "10:10 AM",
        },
    )
```

!!! warning "주의: Event.output 제한"

    노드는 한 번 실행될 때 ***Event.output*** 데이터 페이로드를 하나만 내보낼 수
    있습니다. 즉, 노드 안에서 ***yield*** 를 여러 번 사용할 수는 있지만,
    ***Event.output*** 을 가진 ***yield*** 를 두 번 이상 실행하면 런타임 오류가
    발생합니다.

### Event `message` 매개변수

***Event*** 의 ***message*** 매개변수는 사용자 응답용 데이터를 전달할 때
사용합니다. 일반적으로는 사용자에게 정보를 제공하거나 사용자로부터 정보를
요청하는 경우가 아니라면, 에이전트 코드에서 ***message*** 매개변수를 사용하지
않아야 합니다. 다음 코드는 워크플로 실행 도중 사용자에게 정보를 제공하는 예시를
보여줍니다.

```python
async def user_message(node_input: str):
  """Tell user research process is starting."""
  yield Event(message="Beginning research process...")
```

### Event `state` 매개변수

***Event*** 의 ***state*** 매개변수는 ADK 세션 전체 동안 유지해야 하는 소량의
데이터 값을 저장하는 데 사용합니다. state 매개변수의 값은 노드 사이에서 자동으로
영속화되며, 더 복잡한 워크플로의 실행을 안내하기 위한 용도로 설계되었습니다.
노드는 state 값을 수정할 수 있으며, 수정된 state 값은 다운스트림 노드에서
사용할 수 있습니다. 다음 코드 예시는 state 가 노드 사이에서 어떻게 유지되는지
보여줍니다.

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

!!! warning "주의: `state` 속성 데이터 제한"

    state 매개변수는 노드 간에 *대량의 데이터를 영속화하는 용도*로 사용하면 안
    됩니다. 대용량 데이터 리소스는 Workflow 수명 주기 동안 artifacts 나 데이터베이스
    Tool 같은 다른 데이터 영속화 메커니즘을 사용하세요.

## 스키마로 노드 입력과 출력 데이터 제한하기

입력 및 출력 데이터 스키마를 설정해 ***FunctionNodes*** 와 **Agents** 를
포함한 모든 노드의 입력 및 출력 데이터 형식을 제한할 수 있습니다. 다음
매개변수는 모든 노드에서 선택적으로 설정할 수 있습니다. 에이전트 프로젝트의
요구사항에 따라 이 매개변수들을 둘 다 또는 하나만 설정할 수 있습니다.

- **`input_schema`**: ***BaseModel*** 을 확장한 클래스를 사용해 기대하는 입력
  스키마를 설정합니다.
- **`output_schema`**: ***BaseModel*** 을 확장한 클래스를 사용해 필요한 출력
  스키마를 설정합니다.

아래 코드 예시는 서브에이전트에 입력 및 출력 스키마를 모두 설정하는 방법을
보여줍니다.

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

## 에이전트에서 구조화된 데이터 접근

서브에이전트나 함수 노드 같은 워크플로 노드로부터 구조화된 데이터를 에이전트에
전달할 때, 해당 데이터를 에이전트의 instructions 에 넣기 위한 특정 구문을
사용할 수 있습니다. 구체적으로는 중괄호 `{ }` 를 사용해 입력 스키마 속성을
선택하거나, `< >` 를 사용해 입력 스키마 속성, `from` 키워드, 그리고 해당
데이터를 제공하는 노드 이름을 지정할 수 있습니다. 다음 코드 스니펫은 에이전트
***input schema*** 를 통해 전달된 데이터를 포함하는 두 가지 방법을 보여줍니다.

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

이 워크플로의 완전하지만 단순화된 버전은
[그래프 기반 에이전트 워크플로](/ko/workflows/#시작하기)를
참조하세요.
