# 에이전트 워크플로를 위한 인간 입력

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v2.0.0</span><span class="lst-preview">Alpha</span>
</div>

데이터 입력, 의사결정 검증, 또는 작업 허가를 위해 인간 입력을 요청할 수 있는
능력은 많은 에이전트 기반 워크플로에서 중요한 요소입니다. ADK의 그래프 기반
워크플로에는 워크플로의 일부로 인간의 입력을 얻기 위해 특별히 만들어진
human-in-the-loop(HITL) 노드가 포함될 수 있습니다. 이러한 노드는 실행에
인공지능(AI) 모델이 필요하지 않으므로 입력 프로세스를 더 예측 가능하고
신뢰성 있게 만들 수 있습니다.

!!! example "Alpha 릴리스"

    ADK 2.0은 Alpha 릴리스이며, 이전 버전의 ADK와 함께 사용할 때 호환성이
    깨지는 변경이 발생할 수 있습니다. 프로덕션 환경처럼 하위 호환성이 필요한
    경우에는 ADK 2.0을 사용하지 마세요. 이 릴리스를 테스트해 보시고
    [피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)을
    보내주시기 바랍니다.

## 시작하기

***RequestInput*** 클래스와 사용자에게 보여줄 텍스트 프롬프트를 사용하면
그래프 안에 인간 입력 노드를 구현할 수 있습니다. 다음 코드 예시는 Workflow
그래프에 인간 입력 노드를 추가하는 방법을 보여줍니다.

```python
from google.adk.events import RequestInput
from google.adk import Workflow

def step1(): # Human input step
  yield RequestInput(message="Enter a number:")

def step2(node_input):
  return node_input * 2

root_agent = Workflow(
    name="root_agent",
    edges=[('START', step1, step2)],
)
```

이 코드 예시에서 `step1`은 시스템이 사용자로부터 입력을 받을 때까지 에이전트
실행을 일시 중지합니다. 시스템이 사용자 입력을 받으면 그 입력이 다음 노드로
전달됩니다.

## 구성 옵션

인간 입력 노드는 ***RequestInput*** 클래스와 함께 다음 구성 옵션을 사용할 수
있습니다.

- **`message`:** 인간 입력 요청을 설명하기 위해 사용자에게 제공되는 텍스트입니다.
- **`payload`:** 인간 입력 요청의 일부로 사용할 구조화된 데이터입니다.
- **`response_schema`:** 인간 응답이 따라야 하는 데이터 구조입니다.

!!! note "참고: response_schema 입력 제한"

    **response_schema** 설정의 경우, ***RequestInput*** 클래스는 인간의 응답을
    지정된 데이터 구조에 맞게 자동으로 재구성하지 않습니다. 인간 응답은 지정된
    형식으로 직접 제공되어야 합니다. 더 나은 사용자 경험을 위해 구조화된 데이터를
    수집하는 사용자 인터페이스를 제공하거나, 비정형 데이터를 필요한 형식에 맞추는
    Agent 노드를 사용하는 것을 고려하세요.

## 인간 입력 예시

다음 코드 예시는 ***message***, ***payload***, ***response schema*** 매개변수를
사용한 더 자세한 인간 입력 요청을 보여줍니다.

### response schema와 함께 입력 요청하기

다음 코드 샘플은 워크플로 노드에서 ***response schema*** 를 포함한
***RequestInput*** 객체를 구성하는 방법을 보여줍니다.

```python
async def initial_prompt(ctx: Context):
   """Ask the user for itinerary information"""
   input_message = """
       This is an interactive concierge workflow tasked with making you a great
       itinerary for you in your city of choice. If you give some details about
       yourself or what you are generally looking for I can better personalize
       your itinerary.
       For example, input your:
           City (Required),
           Age,
           Hobby,
           Example of attraction you liked
   """
   resp = {"user_response": str}

   yield RequestInput(message=input_message, response_schema=resp)
```

### 데이터 payload와 함께 입력 요청하기

다음 코드 샘플은 워크플로 노드에서 ***payload*** 와 ***response schema*** 를
포함한 ***RequestInput*** 객체를 구성하는 방법을 보여줍니다. 이 예시에서
`ActivitiesList`는 활동 목록을 구성하는 에이전트 노드가 채운다고 가정하며,
`get_user_feedback()` 노드는 사용자에게 피드백을 요청합니다.

```python
class ActivitiesList(BaseModel):
   """Itinerary should be a list of dictionaries for each activity. Each
   activity has a name and a description"""
   itinerary: List[Dict[str, str]]

async def get_user_feedback(node_input: ActivitiesList):
   """
   Retrieves the user's thoughts on the agents initial itinerary in order to
   either expand on, change the list, or exit the loop
   """
   message = (
       f"""
       Here is your recommended base itinerary:\n{node_input}\n\n
       Which of these items appeal to you (if any)?
       """
   )

   yield RequestInput(
       message=message,
       payload=node_input,
       response_schema={"user":"response"}
   )
```
