---
description: Agents CLI와 코딩 어시스턴트를 사용하여 기존 AI 에이전트, 커스텀 에이전트 루프, 워크플로우를 Google Agent Development Kit (ADK)로 마이그레이션하는 방법을 알아봅니다.
---

# 기존 에이전트를 ADK로 마이그레이션

이 가이드에서는 Agents CLI와 코딩 에이전트를 사용하여 기존 에이전트 코드베이스를 Agent Development Kit (ADK)로 마이그레이션하는 방법을 안내합니다. ADK로 마이그레이션하면 여러 언어에 걸쳐 에이전트 아키텍처를 표준화하고, 내장된 평가 도구를 사용하며, Google Cloud에 직접 배포할 수 있습니다.

## Agents CLI로 마이그레이션

상태 객체, 노드 그래프, 실행 루프를 한 줄씩 수동으로 다시 작성하는 대신, Agents CLI를 사용하여 코딩 에이전트와 함께 마이그레이션을 계획하고 실행할 수 있습니다.

Agents CLI는 Antigravity, Claude Code, Cursor, Codex와 같은 코딩 에이전트에 ADK 개발 스킬을 설치합니다. 기존 프로젝트에서 코딩 에이전트를 열면 다음과 같은 작업을 수행할 수 있습니다:

* 현재 에이전트 구조, 도구, 상태, 라우팅 규칙 분석.
* 기존 컴포넌트를 네이티브 ADK 클래스 및 그래프 워크플로우로 매핑.
* 장단점이 포함된 아키텍처 옵션 제안.
* 도구, 에이전트 정의, 세션 처리를 점진적으로 변환.
* 마이그레이션 전후 동작을 검증하기 위한 평가 데이터셋 생성.

Agents CLI 사용에 대한 자세한 내용은 [Agents CLI](https://google.github.io/agents-cli/) 문서를 참조하세요.

## 사전 요구사항

마이그레이션을 시작하기 전에 다음이 설치되어 있는지 확인하세요:

* Python 3.11 이상
* [`uv`](https://docs.astral.sh/uv/getting-started/installation/) 패키지 관리자
* 지원되는 코딩 에이전트

코딩 에이전트에 Agents CLI와 해당 ADK 스킬을 설치합니다:

```bash
uvx google-agents-cli setup
```

설치를 확인하려면 다음을 실행하세요:

```bash
agents-cli info
```

## 마이그레이션 워크플로우

다음 절차에 따라 기존 에이전트를 ADK로 마이그레이션합니다:

1. [기존 프로젝트에서 코딩 에이전트 열기](#기존-프로젝트에서-코딩-에이전트-열기)
2. [마이그레이션 계획 브레인스토밍](#마이그레이션-계획-브레인스토밍)
3. [에이전트 패턴을 ADK로 매핑](#에이전트-패턴을-adk로-매핑)
4. [평가를 동반한 코드 변환](#평가를-동반한-코드-변환)
5. [검증 및 평가](#검증-및-평가)

### 기존 프로젝트에서 코딩 에이전트 열기

기존 에이전트 프로젝트의 루트 디렉터리에서 터미널 또는 IDE를 열고 코딩 에이전트를 시작합니다. 에이전트가 Agents CLI에 의해 설치된 ADK 스킬을 감지하는지 확인합니다.

### 마이그레이션 계획 브레인스토밍

코딩 에이전트에 현재 코드베이스를 검사하고 목표 ADK 아키텍처를 브레인스토밍하도록 요청합니다. 에이전트에는 Agents CLI를 통해 ADK 스킬이 로드되어 있으므로 ADK 상태 관리, 그래프 워크플로우, 오케스트레이션 패턴을 이해하고 있습니다. 코딩 에이전트에서 다음과 유사한 프롬프트를 사용합니다:

```text title="코드 에이전트 프롬프트"
I want to migrate this existing agent codebase to Google Agent Development Kit (ADK).
Please inspect our current files, state schema, tools, and control flow.
Propose 2-3 target ADK architecture options with trade-offs, and recommend the cleanest approach.
Include an evaluation plan to verify behavior using agents-cli eval.
```

코딩 에이전트는 다음 항목들을 분석합니다:

* **실행 흐름(Execution flow):** 단일 도구 호출 루프, 결정론적 그래프 워크플로우, 동적 라우터 또는 다중 에이전트 팀.
* **도구(Tools):** 함수, 매개변수 시그니처, docstring, 외부 API 호출.
* **메모리 및 검색(Memory and retrieval):** 지식 저장소, 벡터 검색 통합 또는 대화 메모리.
* **상태(State):** 턴 간 추적되는 변수, 스크래치패드 키, 세션 스토리지.
* **대상 클래스(Target classes):** `Agent` 또는 `Workflow` 등 가장 적합한 ADK 클래스.
* **평가 전략(Evaluation strategy):** 마이그레이션된 에이전트를 벤치마크하기 위해 기존 테스트 케이스를 평가 데이터셋으로 변환하는 방법.

제안된 접근 방식을 검토한 후 요구사항에 맞는 아키텍처를 승인합니다.

### 에이전트 패턴을 ADK로 매핑

ADK는 커스텀 디스패치 루프 및 상태 핸들러를 선언적 클래스와 그래프 워크플로우로 대체합니다. 마이그레이션 중 다음 매핑을 가이드로 사용하세요:

| 기존 패턴 | ADK 해당 기능 | 설명 |
| :--- | :--- | :--- |
| 커스텀 도구 스키마 또는 래퍼 | 네이티브 Python 함수 또는 `FunctionTool` | 타입 힌트와 docstring이 있는 일반 Python 함수. ADK가 도구 선언을 자동으로 파생합니다. |
| 커스텀 에이전트 루프 또는 러너 | `Agent` | 모델, 지침, 도구, 서브 에이전트를 지정하는 선언적 에이전트 정의. |
| 메모리 및 검색 | `BaseMemoryService` 구현체 및 검색 도구 | 내장 메모리 서비스(`InMemoryMemoryService`, `VertexAiMemoryBankService`, `VertexAiRagMemoryService`) 및 세션과 문서 그라운딩을 위한 검색 도구. |
| 상태 딕셔너리 또는 스크래치패드 | `ToolContext`를 통한 `session.state` | 도구, 콜백, 에이전트 지침 내부에서 접근 가능한 공유 가변 세션 상태. |
| 다중 에이전트 워크플로우 및 파이프라인 | `google.adk.workflow.Workflow` | 조건부 라우팅, 루프, 병렬 분기를 갖춘 명시적 그래프 노드. |
| 다중 에이전트 핸드오프 | `Agent(sub_agents=[...])` | 코디네이터 에이전트가 전문 서브 에이전트에 위임하는 계층적 위임. |
| 원격 에이전트 통신 | A2A 프로토콜 | Agent-to-Agent 표준을 사용하는 HTTP 기반 에이전트 간 통신. |

### 평가를 동반한 코드 변환

안정적인 마이그레이션은 테스트 주도적(test-driven)이어야 합니다. 코딩 에이전트는 마이그레이션된 에이전트가 원래 구현과 동일한 결과를 생성하는지 검증하기 위해 새로운 ADK 코드와 함께 평가 데이터셋 및 테스트 모음을 구성할 수 있습니다.

1. **평가 테스트 케이스 설정:** 코딩 에이전트가 기존 테스트 케이스 또는 기록된 대화를 `eval/` 아래의 평가 케이스로 변환하도록 합니다.
2. **도구 및 에이전트 로직 이식:** 커스텀 디스패치 루프 및 도구 래퍼를 타입이 지정된 Python 함수 및 ADK `Agent` 또는 `Workflow`로 대체합니다.

```python
# agent.py
from google.adk.agents import Agent
from google.adk.tools import ToolContext

def lookup_customer(customer_id: str) -> str:
    """Retrieve account tier and status for a customer."""
    return "Tier: Premium, Status: Active"

def calculate_discount(amount: float, rate: float = 0.1) -> float:
    """Calculate discounted total for a transaction."""
    return amount * (1.0 - rate)

root_agent = Agent(
    name="customer_support_agent",
    model="gemini-flash-latest",
    instruction="Assist customers with account inquiries and discounts using your tools.",
    tools=[lookup_customer, calculate_discount],
)
```

### 검증 및 평가

평가 스위트를 실행하여 마이그레이션된 에이전트를 기준 테스트 케이스와 비교합니다:

```bash
agents-cli eval run
```

쿼리를 직접 또는 대화형으로 테스트할 수도 있습니다:

```bash
# 단일 프롬프트 테스트
agents-cli run "Look up customer cust_101 and apply a 10% discount on $100."

# 대화형 웹 UI 시작
agents-cli playground
```

## 다음 단계

* ADK 도구 패턴에 대해 자세히 알아보려면 [다중 도구 에이전트 튜토리얼](/tutorials/multi-tool-agent/)을 읽어보세요.
* 다중 에이전트 라우팅 및 상태 조정을 위해 [그래프 워크플로우](/graphs/)를 살펴보세요.
* [배포 가이드](/deploy/)를 사용하여 에이전트를 배포하세요.
