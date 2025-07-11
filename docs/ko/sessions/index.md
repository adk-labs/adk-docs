# 대화형 컨텍스트 소개: 세션, 상태, 그리고 메모리

## 컨텍스트가 중요한 이유

의미 있는 다중 턴 대화를 위해서는 에이전트가 컨텍스트를 이해해야 합니다. 인간과 마찬가지로, 연속성을 유지하고 반복을 피하기 위해 대화 기록, 즉 무엇을 말하고 무엇을 했는지 기억해야 합니다. Agent Development Kit(ADK)는 `세션`, `상태`, `메모리`를 통해 이 컨텍스트를 관리하는 구조화된 방법을 제공합니다.

## 핵심 개념

에이전트와의 다양한 대화 인스턴스를 별개의 **대화 스레드**로 생각하고, 잠재적으로 **장기적인 지식**을 활용한다고 상상해 보세요.

1.  **`세션(Session)`**: 현재 대화 스레드

    *   사용자와 에이전트 시스템 간의 *단일하고 진행 중인 상호작용*을 나타냅니다.
    *   *해당 특정 상호작용* 동안 에이전트가 취한 메시지와 조치의 시간순 시퀀스(이를 `이벤트`라고 함)를 포함합니다.
    *   `세션`은 *이 대화 중에만* 관련된 임시 데이터(`상태`)를 보유할 수도 있습니다.

2.  **`상태(State)` (`session.state`)**: 현재 대화 내의 데이터

    *   특정 `세션` 내에 저장된 데이터입니다.
    *   *현재 활성* 대화 스레드에만 관련된 정보를 관리하는 데 사용됩니다(예: *이 채팅 중* 장바구니에 담긴 항목, *이 세션에서* 언급된 사용자 선호도).

3.  **`메모리(Memory)`**: 검색 가능한, 세션 간 정보

    *   *여러 과거 세션*에 걸쳐 있거나 외부 데이터 소스를 포함할 수 있는 정보 저장소를 나타냅니다.
    *   에이전트가 즉각적인 대화를 넘어 정보나 컨텍스트를 회상하기 위해 *검색*할 수 있는 지식 기반 역할을 합니다.

## 컨텍스트 관리: 서비스

ADK는 이러한 개념을 관리하기 위한 서비스를 제공합니다:

1.  **`SessionService`**: 다양한 대화 스레드(`세션` 객체)를 관리합니다.

    *   생명주기를 처리합니다: 개별 `세션` 생성, 검색, 업데이트(`이벤트` 추가, `상태` 수정), 삭제.

2.  **`MemoryService`**: 장기 지식 저장소(`메모리`)를 관리합니다.

    *   완료된 `세션`의 정보를 장기 저장소에 수집하는 것을 처리합니다.
    *   쿼리를 기반으로 이 저장된 지식을 검색하는 메서드를 제공합니다.

**구현**: ADK는 `SessionService`와 `MemoryService` 모두에 대해 다양한 구현을 제공하여 애플리케이션의 요구에 가장 적합한 스토리지 백엔드를 선택할 수 있도록 합니다. 특히, 두 서비스 모두 **인메모리 구현**이 제공됩니다. 이는 **로컬 테스트 및 빠른 개발**을 위해 특별히 설계되었습니다. 이러한 인메모리 옵션을 사용하여 저장된 모든 데이터(세션, 상태 또는 장기 지식)는 애플리케이션이 다시 시작될 때 **손실된다는 점**을 기억하는 것이 중요합니다. 로컬 테스트를 넘어선 지속성과 확장성을 위해 ADK는 클라우드 기반 및 데이터베이스 서비스 옵션도 제공합니다.

**요약:**

*   **`세션` & `상태`**: **현재 상호작용**에 초점을 맞춥니다 – *단일하고 활성인 대화*의 기록과 데이터입니다. 주로 `SessionService`에 의해 관리됩니다.
*   **메모리**: **과거 및 외부 정보**에 초점을 맞춥니다 – 잠재적으로 대화 전반에 걸친 *검색 가능한 아카이브*입니다. `MemoryService`에 의해 관리됩니다.

## 다음 단계는?

다음 섹션에서는 이러한 각 구성 요소에 대해 더 자세히 알아볼 것입니다:

*   **`세션`**: 구조와 `이벤트` 이해하기.
*   **`상태`**: 세션별 데이터를 효과적으로 읽고, 쓰고, 관리하는 방법.
*   **`SessionService`**: 세션에 적합한 스토리지 백엔드 선택하기.
*   **`MemoryService`**: 더 넓은 컨텍스트를 저장하고 검색하기 위한 옵션 탐색하기.

이러한 개념을 이해하는 것은 복잡하고, 상태를 유지하며, 컨텍스트를 인식하는 대화에 참여할 수 있는 에이전트를 구축하는 데 기본이 됩니다.