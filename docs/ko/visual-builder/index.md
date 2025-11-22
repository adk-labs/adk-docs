# 에이전트용 Visual Builder

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python v1.18.0</span><span class="lst-preview">실험적 기능</span>
</div>

ADK Visual Builder는 ADK 에이전트를 생성하고 관리하기 위한 시각적 워크플로 설계 환경을 제공하는 웹 기반 도구입니다. 이 도구를 사용하면 초보자에게 친숙한 그래픽 인터페이스에서 에이전트를 설계, 구축 및 테스트할 수 있으며, 에이전트 구축을 돕는 AI 기반 어시스턴트가 포함되어 있습니다.

![Visual Agent Builder](../assets/visual-builder.png)

!!! example "실험적 기능 (Experimental)"
    Visual Builder 기능은 실험적 릴리스입니다. 여러분의 [피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md)을 환영합니다!

## 시작하기 (Get started)

Visual Builder 인터페이스는 ADK 웹 도구 사용자 인터페이스(UI)의 일부입니다. ADK 라이브러리가 [설치](/adk-docs/get-started/installation/#python)되어 있는지 확인한 후 ADK 웹 사용자 인터페이스를 실행하세요.

```console
adk web --port 8000
```

??? tip "팁: 코드 개발 디렉터리에서 실행하세요"

    Visual Builder 도구는 ADK 웹 도구를 실행한 디렉터리 내의 새로운 하위 디렉터리에 프로젝트 파일을 기록합니다. 쓰기 권한이 있는 개발자 디렉터리 위치에서 이 명령을 실행해야 합니다.

![Visual Agent Builder start](../assets/visual-builder-start.png)
**그림 1:** Visual Builder 도구를 시작하기 위한 ADK 웹 컨트롤.

Visual Builder로 에이전트를 생성하려면:

1.  *그림 1*과 같이 페이지 왼쪽 상단에서 **+** (더하기 기호)를 선택하여 에이전트 생성을 시작합니다.
1.  에이전트 애플리케이션의 이름을 입력하고 **Create(생성)**를 선택합니다.
1.  다음 중 하나를 수행하여 에이전트를 편집합니다:
    *   왼쪽 패널에서 에이전트 구성 요소 값을 편집합니다.
    *   중앙 패널에서 새 에이전트 구성 요소를 추가합니다.
    *   오른쪽 패널에서 프롬프트를 사용하여 에이전트를 수정하거나 도움말을 얻습니다.
1.  왼쪽 하단 모서리에 있는 **Save(저장)**를 선택하여 에이전트를 저장합니다.
1.  새 에이전트와 상호 작용하여 테스트합니다.
1.  *그림 1*과 같이 페이지 왼쪽 상단에서 연필 아이콘을 선택하여 에이전트 편집을 계속합니다.

Visual Builder 사용 시 참고할 몇 가지 사항은 다음과 같습니다:

*   **에이전트 생성 및 저장:** 에이전트를 생성할 때 편집 인터페이스를 종료하기 전에 반드시 **Save(저장)**를 선택해야 합니다. 그렇지 않으면 새 에이전트를 편집할 수 없게 될 수 있습니다.
*   **에이전트 편집:** 에이전트 편집(연필 아이콘)은 Visual Builder로 생성된 에이전트에 대해서만 *사용 가능*합니다.
*   **도구 추가:** 기존 사용자 정의 도구(Custom Tools)를 Visual Builder 에이전트에 추가할 때, 완전한(fully-qualified) Python 함수 이름을 지정해야 합니다.

## 워크플로 구성 요소 지원 (Workflow component support)

Visual Builder 도구는 에이전트를 구축하기 위한 드래그 앤 드롭 사용자 인터페이스뿐만 아니라, 질문에 답변하고 에이전트 워크플로를 편집할 수 있는 AI 기반 개발 어시스턴트를 제공합니다. 이 도구는 다음을 포함하여 ADK 에이전트 워크플로를 구축하는 데 필요한 모든 필수 구성 요소를 지원합니다:

*   **에이전트 (Agents)**
    *   **루트 에이전트 (Root Agent)**: 워크플로의 주 제어 에이전트입니다. ADK 에이전트 워크플로의 다른 모든 에이전트는 서브 에이전트로 간주됩니다.
    *   [**LLM 에이전트:**](/adk-docs/agents/llm-agents/) 생성형 AI 모델로 구동되는 에이전트입니다.
    *   [**순차 에이전트 (Sequential Agent):**](/adk-docs/agents/workflow-agents/sequential-agents/) 일련의 서브 에이전트를 순서대로 실행하는 워크플로 에이전트입니다.
    *   [**루프 에이전트 (Loop Agent):**](/adk-docs/agents/workflow-agents/loop-agents/) 특정 조건이 충족될 때까지 서브 에이전트를 반복적으로 실행하는 워크플로 에이전트입니다.
    *   [**병렬 에이전트 (Parallel Agent):**](/adk-docs/agents/workflow-agents/parallel-agents/) 여러 서브 에이전트를 동시에 실행하는 워크플로 에이전트입니다.
*   **도구 (Tools)**
    *   [**사전 구축 도구 (Prebuilt tools):**](/adk-docs/tools/built-in-tools/) ADK에서 제공하는 제한된 도구 세트를 에이전트에 추가할 수 있습니다.
    *   [**사용자 정의 도구 (Custom tools):**](/adk-docs/tools-custom/) 사용자 정의 도구를 직접 구축하여 워크플로에 추가할 수 있습니다.
*   **구성 요소 (Components)**
    *   [**콜백 (Callbacks)**](/adk-docs/callbacks/) 에이전트 워크플로 이벤트의 시작과 끝에서 에이전트의 동작을 수정할 수 있는 흐름 제어 구성 요소입니다.

일부 고급 ADK 기능은 에이전트 구성(Agent Config) 기능의 제한으로 인해 Visual Builder에서 지원되지 않습니다. 자세한 내용은 에이전트 구성 [알려진 제한 사항](/adk-docs/agents/config/#known-limitations)을 참조하세요.

## 프로젝트 코드 출력 (Project code output)

Visual Builder 도구는 [에이전트 구성 (Agent Config)](/adk-docs/agents/config/) 형식을 사용하여 코드를 생성합니다. 에이전트에는 `.yaml` 구성 파일을, 사용자 정의 도구에는 Python 코드를 사용합니다. 이 파일들은 ADK 웹 인터페이스를 실행한 디렉터리의 하위 폴더에 생성됩니다. 다음 목록은 `DiceAgent` 프로젝트의 예시 레이아웃을 보여줍니다:

```none
DiceAgent/
    root_agent.yaml    # 메인 에이전트 코드
    sub_agent_1.yaml   # 서브 에이전트 (있는 경우)
    tools/             # 도구 디렉터리
        __init__.py
        dice_tool.py   # 도구 코드
```

!!! note "생성된 에이전트 편집"

    개발 환경에서 생성된 파일을 편집할 수 있습니다. 하지만 일부 변경 사항은 Visual Builder와 호환되지 않을 수 있습니다.

## 다음 단계 (Next steps)

Visual Builder 개발 어시스턴트를 사용하여 다음 프롬프트로 새 에이전트를 구축해 보세요:

```none
Help me add a dice roll tool to my current agent.
Use the default model if you need to configure that.
```

(내 현재 에이전트에 주사위 굴리기 도구를 추가하도록 도와줘. 구성이 필요한 경우 기본 모델을 사용해.)

Visual Builder에서 사용하는 에이전트 구성 코드 형식과 사용 가능한 옵션에 대한 자세한 정보를 확인해 보세요:

*   [에이전트 구성 (Agent Config)](/adk-docs/agents/config/)
*   [에이전트 구성 YAML 스키마](/adk-docs/api-reference/agentconfig/)