# Managed agents (관리형 에이전트)

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.4.0</span><span class="lst-preview">Preview</span>
</div>

Managed agents(관리형 에이전트)를 사용하면 ADK 흐름 내에서 Managed Agents API를 지원하는 Google의 퍼스트 파티 기본 제공 에이전트를 사용할 수 있습니다. Managed agents는 [Gemini API](https://ai.google.dev/gemini-api/docs/agents) 및 [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents)을 통해 제공됩니다. `ManagedAgent` 클래스는 특수한 서버 사이드 실행 환경에서 실행되는 관리형 에이전트(예: Antigravity 에이전트)에 연결하므로, 샌드박스를 관리하거나 클라이언트 사이드 함수 선언을 작성하지 않고도 강력한 기본 제공 기능을 사용할 수 있습니다.

`ManagedAgent`는 다른 ADK 에이전트와 동일한 `BaseAgent` 계약을 구현하므로 독립 실행형으로 사용하거나 ADK 흐름에 직접 추가할 수 있습니다. 해당 환경을 직접 빌드하고 운영하기보다 특수한 내장 도구가 있는 견고한 서버 호스팅 에이전트를 원하는 경우에 유용합니다.

## Managed agents 란 무엇인가요?

*Managed agent (관리형 에이전트)*는 자체 ADK 프로세스에 의해 실행되는 것이 아니라, Managed Agents API를 통해 Google에서 추론, 도구 및 실행 환경을 호스팅하고 운영하는 에이전트입니다. `ManagedAgent`는 표준 `generate_content` 호출을 발행하는 대신 서버 사이드 *상호작용(interaction)*을 생성하고 결과를 ADK 흐름으로 다시 스트리밍합니다. Managed agents는 다음과 같은 여러 가지 내장된 이점을 제공합니다.

- **퍼스트 파티 기본 제공 에이전트:** ready-made 에이전트(예: Antigravity 에이전트)의 `agent_id`를 참조하여 연결합니다.
- **내장된 서버 사이드 실행:** 웹 검색 및 코드 실행과 같은 기능이 서버의 관리형 샌드박스에서 실행되므로 로컬 샌드박스를 프로비저닝하거나 보호할 필요가 없습니다.
- **클라이언트 사이드 함수 선언 없음:** 서버 사이드 도구가 관리형 에이전트에서 구성되므로 로컬에서 선언하거나 실행하지 않습니다.

## 직접 빌드하는 것과 Managed agents를 사용하는 것의 비교

Managed agents와 ADK 에이전트는 서로 다른 문제를 해결합니다. 둘 사이의 선택은 주로 기본 제공 기능의 유용함과 미세 제어 기능 간의 절충안입니다.

- **Managed agents**는 강력한 에이전트를 즉시 사용할 수 있도록 제공하지만 유연성이 제한됩니다. 도구 세트가 미리 정의된 서버 사이드 방식이고 에이전트는 관리형 환경에서만 실행되며 클라이언트 사이드 도구 또는 MCP 도구는 지원되지 않습니다.
- **ADK 에이전트**(예: [`LlmAgent`](/ko/agents/llm-agents/))는 모델, 지침, 도구(커스텀 함수 도구 및 MCP 도구 포함) 및 실행 위치에 대한 미세 제어 기능을 제공합니다.

## 사전 준비 사항

`ManagedAgent`는 두 가지 백엔드를 지원합니다. 사용하려는 백엔드에 대한 사전 준비 사항을 완료하여 자격 증명(credentials)과 `agent_id`를 획득하세요.

### Gemini API 백엔드

- **인증:** Gemini API 키를 획득하고 `GEMINI_API_KEY` 환경 변수로 설정합니다.
- **에이전트 ID:** 연결할 `agent_id`가 필요합니다. 다음 중 하나를 수행할 수 있습니다.
    - [Gemini API Agents 설명서](https://ai.google.dev/gemini-api/docs/agents)를 따라 새 에이전트를 만듭니다.
    - 아래 예에서 사용되는 `antigravity-preview-05-2026`과 같은 기본 제공 에이전트 ID를 사용합니다.

### Agent Platform 백엔드

- **인증:** Agent Platform은 Google Cloud 자격 증명이 필요합니다. 로컬 환경을 인증하려면 [Agent Platform 설정 지침](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents/create-manage#before-you-begin)을 따르세요. (예: `gcloud auth application-default login` 사용)
- **위치(Location):** Managed Agents API는 `global` 위치에서만 제공됩니다. `ManagedAgent`는 Agent Platform 백엔드에서 `global` 연결을 강제합니다.
- **에이전트 ID:** Gemini API와 마찬가지로 `agent_id`가 필요합니다. [Agent Platform Managed Agents 가이드](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents)를 통해 하나를 생성하거나 프로젝트에서 사용 가능한 기본 제공 에이전트 ID를 사용합니다.

## 시작하기

다음 예에서는 웹 검색을 사용하여 질문에 답하는 에이전트와 서버 사이드에서 코드를 실행하여 연산 질문을 해결하는 에이전트 등 두 개의 관리형 에이전트를 생성합니다. 둘 다 관리형 환경(`environment={'type': 'remote'}`)에서 도구를 실행합니다.

=== "Python"

    ```python
    import os
    from google.adk.agents import ManagedAgent
    from google.adk.tools import google_search
    from google.genai import types

    # MANAGED_AGENT_ID 및 적절한 환경 구성이 있는지 확인하십시오.
    _AGENT_ID = os.environ.get('MANAGED_AGENT_ID', 'antigravity-preview-05-2026')

    managed_search_agent = ManagedAgent(
        name='managed_search_agent',
        description='Answers questions that need fresh, grounded information from the web.',
        agent_id=_AGENT_ID,
        environment={'type': 'remote'},
        tools=[google_search],
    )

    # raw types.Tool을 사용하는 관리형 코드 실행 에이전트
    managed_code_execution_agent = ManagedAgent(
        name='managed_code_execution_agent',
        description='Solves computational questions by running code server-side.',
        agent_id=_AGENT_ID,
        environment={'type': 'remote'},
        tools=[types.Tool(code_execution=types.ToolCodeExecution())],
    )
    ```

## 작동 원리

`ManagedAgent`를 호출하면 ADK는 [Interactions API](https://ai.google.dev/gemini-api/docs/interactions-overview)를 통해 관리형 에이전트에 요청을 전송하고, 부분 및 최종 결과를 실시간으로 ADK 흐름에 스트리밍합니다. 추론, 도구 및 실행은 모두 ADK 프로세스가 아닌 Google의 관리형 환경에서 실행됩니다.

!!! note "`ManagedAgent`가 Managed Agents API에 매핑되는 방식"

    ADK `ManagedAgent`는 새로운 관리형 에이전트 리소스를 생성하거나 등록하지 않습니다. 백엔드에 이미 존재하는 에이전트(`agent_id`로 명명됨)에 연결하고 런타임에 상호작용별 재정의(override)로 해당 구성(`tools` 및 `environment` 등)을 적용합니다. Managed Agents API의 관점에서 ADK는 데이터 평면(Interactions API)에서만 작동하며 제어 평면(에이전트 리소스를 생성하고 관리하는 Agents API)은 그대로 유지합니다. 이 두 평면의 차이점에 대한 자세한 내용은 [Managed Agents API 시스템 아키텍처](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents)를 참고하세요.

### 로컬 세션 vs 원격 상태

`ManagedAgent`는 로컬에 거의 상태를 유지하지 않습니다. ADK 세션은 생성하는 이벤트에서 오직 두 가지 값, 즉 `previous_interaction_id`와 샌드박스 `environment_id`만을 유지합니다. 각 새 턴에서 에이전트는 이전 세션 이벤트를 스캔하여 두 값을 모두 복구한 다음 재사용하므로 대화와 샌드박스가 계속 유지됩니다.

그 외 모든 것은 서버 사이드에 상주합니다. Managed Agents API는 샌드박스 환경과 전체 상호작용 기록을 소유하며, 로컬 세션이 아닌 해당 원격 상호작용이 대화를 계속하기 위한 정보의 소스(source of truth)가 됩니다. 응답 텍스트는 로컬 ADK 이벤트와 원격 상호작용 기록 모두에 나타나지만, ADK는 원격 상태를 복구하고 재사용하는 데 필요한 ID만 저장하며 이전 턴을 다시 전송하지는 않습니다.

## 제한 사항

- **위치 고정 (Agent Platform만 해당):** Agent Platform 백엔드의 경우, Managed Agents API는 현재 `global` 위치에서만 제공됩니다. 리전 엔드포인트는 오류를 발생시킵니다.
- **서버 사이드 도구 전용:** 클라이언트 실행 도구(Python 함수, 호출 가능 객체) 및 MCP 도구는 지원되지 않으며 `NotImplementedError`를 발생시킵니다.
- **스트리밍 전용:** 에이전트는 스트리밍 상호작용(`stream=True`)을 사용합니다. 백그라운드 폴링 실행 및 엄격한 비스트리밍 연결은 아직 완전하게 지원되지 않습니다.
- **백엔드 차이:** Gemini API와 Agent Platform 백엔드는 현재 약간 다른 동작 패턴을 보입니다. 사용하려는 특정 백엔드를 대상으로 테스트하세요.

## 다음 단계

- **샘플:** [Managed Agent Basic](https://github.com/google/adk-python/tree/main/contributing/samples/managed_agent/basic) 및 [Managed Agent Code Execution](https://github.com/google/adk-python/tree/main/contributing/samples/managed_agent/code_execution).
- **백엔드 설명서:** [Gemini API Agents](https://ai.google.dev/gemini-api/docs/agents) 및 [Agent Platform Managed Agents](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents).
- **관련 ADK 주제:** [에이전트용 모델](/ko/agents/models/), [다중 에이전트 워크플로](/ko/workflows/), 및 [커스텀 도구](/ko/tools-custom/).
