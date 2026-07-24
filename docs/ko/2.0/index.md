---
hide:
  - navigation
---

# ADK 2.0에 오신 것을 환영합니다

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v2.0.0</span><span class="lst-go">Go v2.0.0</span>
</div>

ADK 2.0은 정교한 AI 에이전트를 구축하기 위한 강력한 도구를 도입하여 에이전트를 더 뛰어난 제어력, 예측 가능성 및 신뢰성으로 까다로운 작업을 수행하도록 구조화할 수 있게 해줍니다. ADK 2.0은 Python 및 Go에서 사용 가능하며 다음 핵심 기능을 포함합니다.

-   [**그래프 기반 워크플로**](/ko/graphs/): 작업이 라우팅되고 실행되는 방식을 더 세밀하게 제어할 수 있는 결정론적 에이전트 워크플로를 구축합니다.

-   [**동적 워크플로**](/ko/graphs/dynamic/): 반복 루프 및 복잡한 의사결정 기반 분기를 포함한 더 복잡한 워크플로를 코드 기반 로직으로 구축합니다.

-   [**협업 워크플로**](/ko/workflows/collaboration/): 코디네이터 에이전트와 여러 서브에이전트가 함께 작동하는 복잡한 에이전트 아키텍처를 구축합니다.

위에 링크된 항목을 확인하고 ADK 2.0으로 에이전트를 구축하는 새로운 방법을 경험해 보세요!

!!! tip "ADK Python v2.0.0 정식 릴리스 (GA)"

    ADK Python 2.0은 2026년 5월 19일 자로 정식 버전(GA)이 릴리스되었습니다.

!!! tip "ADK Go v2.0.0 정식 릴리스 (GA)"

    ADK Go 2.0은 2026년 6월 30일 자로 정식 버전(GA)이 릴리스되었습니다.

## ADK Python 1.x 호환성

ADK 2.0은 ADK 1.x 릴리스로 개발된 에이전트와 호환되도록 설계되었습니다. 하지만 ADK 1.x 프로젝트를 ADK 2.0으로 업그레이드하기 전에 알아두어야 할 하위 호환성을 깨뜨리는 변경 사항(breaking changes)이 몇 가지 있습니다.

!!! warning "주요 변경 사항: ADK Python 1.x에서 2.0으로의 비호환성"

    ADK Python v2.0.0에서 도입된 여러 비호환성 및 호환성 파괴 변경 사항이 있습니다. 업그레이드하기 전에 이러한 변경 사항을 검토하고 필요한 경우 조치를 취하세요.

ADK 2.0 릴리스는 워크플로 런타임(Workflow Runtime)을 도입하여 ADK를 계층적 에이전트 실행기에서 그래프 기반 실행 엔진으로 전환합니다. 이 새로운 아키텍처에서 에이전트, 도구 및 함수는 워크플로 그래프 내의 개별 *노드(nodes)*로 평가됩니다. ADK 1.x에서 업그레이드하는 경우 프로덕션 애플리케이션의 원활한 전환을 위해 다음 주요 변경 사항 및 마이그레이션 단계를 검토하세요.

### 이벤트 스키마 및 사용자 지정 세션 스토리지

ADK 2.0은 그래프 상태 및 워크플로 출력을 추적하기 위해 핵심 ***Event*** 스키마에 `node_info` 및 `output` 신규 필드를 도입합니다.

*   **사용자 지정 세션 스토리지:** 엄격한 열 구조(rigid columns)를 사용하여 고유한 SQL 또는 NoSQL 데이터베이스에 세션을 저장하는 등 자체 `BaseSessionService`를 구현한 경우, 데이터베이스 스키마를 새 필드에 맞게 업데이트해야 합니다. 2.0 ***Event***를 1.x 고정 테이블에 삽입하려고 하면 삽입 또는 ORM 역직렬화 오류가 발생합니다. *단, 사용자 지정 세션 서비스가 이벤트를 명시적 열에 매핑하지 않고 직렬화된 JSON 블롭(blob)으로 저장하는 경우에는 스키마를 업데이트할 필요가 없습니다.*
*   **엄격한 JSON 검증:** 배포 환경에 `additionalProperties: false` 설정을 포함하여 엄격한 JSON 스키마 검증을 수행하는 다운스트림 API 게이트웨이, 모바일 클라이언트 또는 웹 프론트엔드가 포함되어 있는 경우 예상 스키마가 업데이트될 때까지 2.0 이벤트를 거부합니다.

**마이그레이션 조치:** 모든 Event 페이로드에서 `node_info` 및 `output` 필드를 수신하고 저장하도록 데이터베이스 스키마와 다운스트림 클라이언트 검증기를 업데이트하세요. 2.0 세션을 공유 데이터베이스에 쓰기 전에 모든 리더 애플리케이션이 2.0 형식을 처리할 수 있도록 업데이트되었는지 확인하세요.

### 에이전트 실행: BaseAgent에서 BaseNode로

ADK 1.x에서 에이전트는 독립형 실행기였습니다. ADK 2.0에서 ***BaseAgent*** 클래스는 이제 ***BaseNode***를 상속받습니다. 에이전트는 이제 새로운 워크플로 그래프 엔진 내에서 개별 *노드*로 평가됩니다.

*   **실행 드라이버 사용자 지정 오버라이드:** ABC 계약이 변경되었습니다. `_run_async_impl()` 또는 `generate_content()`와 같은 1.x 추상 메서드의 사용자 지정 오버라이드는 더 이상 올바른 실행 방법이 아닙니다. 워크플로 그래프 엔진은 이러한 레거시 오버라이드를 완전히 우회합니다. 이러한 메서드를 오버라이드하여 사용자 지정 텔레메트리나 상태 관리를 주입한 경우 해당 호출은 무시됩니다.

**마이그레이션 조치:** 사용자 지정 실행 로직을 `run()` 오버라이드 외부로 이동하세요. 대신 표준화된 `BeforeAgentCallback` 및 `AfterAgentCallback` 인터페이스를 활용하여 실행 수명 주기에 사용자 지정 로직을 안전하게 주입하세요.

### 컨텍스트 및 콜백: 자체 변이(In-Place Mutation)

프레임워크를 우회하여 이벤트를 수동으로 추가하는 것은 더 이상 안전하지 않습니다.

*   **이벤트 직접 추가:** ADK 1.x에서는 일부 개발자가 `context.session.events.append(custom_event)`를 통해 세션에 이벤트를 강제로 추가했습니다. ADK 2.0에서 워크플로 러너는 상태, 그래프 라우팅 및 스트리밍을 관리하기 위해 이벤트 방출을 엄격히 제어해야 합니다. 세션 목록에 수동으로 추가하면 그래프 엔진을 우회하여 결정론을 깨뜨립니다.

**마이그레이션 조치:** 이벤트를 세션에 직접 추가하지 마시고 `enqueue_event`를 직접 사용하지 마세요. 이제 프레임워크가 자체적으로 영속성, 라우팅 및 스트리밍을 관리할 수 있도록 노드 또는 에이전트 내에서 이벤트를 명시적으로 `yield`해야 합니다.

### 오류 처리 및 자동 재시도

ADK 2.0 프레임워크는 이제 자동 재시도, 텔레메트리 및 HITL(Human-in-the-Loop) 일시 중지를 활성화하기 위해 예외를 자동으로 캡처합니다.

*   **`Try...except` 및 `BaseException`:** ADK 1.x에서는 프레임워크에 자동 재시도 기능이 내장되어 있지 않아 개발자가 도구 내부에서 수동으로 `try...except` 루프를 작성하는 경우가 많았습니다. ADK 2.0에서 도구를 마이그레이션할 때 넓은 범위의 `except Exception:` 블록을 그대로 두면 프레임워크에서 오류를 감지하지 못해 해당 단계에 대한 새로운 2.0 자동 재시도 메커니즘이 비활성화됩니다. 또한 `BaseException`을 캡처하면 `NodeInterruptedError`를 의도치 않게 트랩하여 HITL 입력을 위해 워크플로를 일시 중지하는 기능이 중단됩니다.

**마이그레이션 조치:** 프레임워크가 구성된 ***RetryConfig***(예: `RetryConfig(max_attempts=3)`)에 대해 평가할 수 있도록 도구에서 표준 예외가 전파되도록 허용하세요. 예외를 명시적으로 다시 발생시키지 않는 한 ***BaseException***을 캡처하지 마세요.

추가적인 ADK Python 1.0 -> 2.0 비호환성을 발견하면 [이슈 트래커](https://github.com/google/adk-python/issues/new?template=bug_report.md&labels=v2)를 통해 제보해 주세요.

### ADK Python 1.x 설치 {#install}

ADK를 업데이트하고 싶지만 아직 ADK 2.0으로 업그레이드할 준비가 되지 않은 경우 아래와 같이 설치 시 ADK 버전을 지정하거나 호환 릴리스 `~=` 연산자를 사용하세요. ADK 1.0의 시스템 요구 사항은 다음과 같습니다.

*   **Python 3.10** 이상
*   패키지 설치용 `pip`

최신 버전의 ADK 1.x를 설치하려면 다음 단계를 따르세요.

1.  Python 가상 환경을 활성화합니다.

2.  ADK 1.x용 호환 릴리스 `~=` 연산자를 사용하여 pip로 패키지를 설치합니다.

    ```bash
    pip install "google-adk~=1.0"
    ```

## ADK Go 1.x 호환성

ADK Go 2.0은 ADK Go 1.x 릴리스로 개발된 에이전트와 호환되도록 설계되었습니다. 그러나 ADK Go 1.x 프로젝트를 ADK Go 2.0으로 업그레이드하기 전에 알아두어야 할 호환성 파괴 변경 사항이 몇 가지 있습니다.

!!! warning "주요 변경 사항: ADK Go 1.x에서 2.0으로의 비호환성"

    ADK Go v2.0.0에서 도입된 알려진 비호환성 및 변경 사항이 있습니다. 업그레이드하기 전에 이러한 변경 사항을 검토하세요.

ADK Go 2.0 릴리스는 워크플로 런타임을 도입하여 ADK Go를 계층적 에이전트 실행기에서 그래프 기반 실행 엔진으로 전환합니다. 이 새 아키텍처에서 에이전트, 도구 및 함수는 워크플로 그래프 내의 개별 *노드*로 평가됩니다.

### 모듈 임포트 경로

ADK Go 2.0은 새로운 메이저 버전 모듈 경로를 사용합니다. Go 소스 파일 및 `go.mod` 파일의 모든 임포트 경로를 업데이트해야 합니다.

*   **1.x 임포트 경로:** `google.golang.org/adk`
*   **2.0 임포트 경로:** `google.golang.org/adk/v2`

**마이그레이션 조치:** `go get google.golang.org/adk/v2`를 실행하고 소스 파일의 모든 임포트 문을 `google.golang.org/adk/...`에서 `google.golang.org/adk/v2/...`로 업데이트하세요.

### 에이전트 실행: Agent 인터페이스 변경 사항

ADK Go 1.x에서 에이전트는 `Run` 메서드를 제공하여 `agent.Agent` 인터페이스를 구현했습니다. ADK Go 2.0에서 에이전트는 새 워크플로 그래프 엔진 내의 개별 *노드*로 평가됩니다.

**마이그레이션 조치:** 사용자 지정 실행 로직을 표준화된 `BeforeAgentCallback` 및 `AfterAgentCallback` 훅으로 이동하여 실행 수명 주기에 안전하게 주입하세요.

### 이벤트 생성: `session.NewEvent` 시그니처 변경

`session.NewEvent`는 이제 첫 번째 인자로 `context.Context`를 필요로 합니다.

```go
// 이전 (ADK Go 1.x)
ev := session.NewEvent(ctx.InvocationID())
// 또는
ev := session.NewEventWithContext(ctx, ctx.InvocationID())

// 이후 (ADK Go 2.0)
ev := session.NewEvent(ctx, ctx.InvocationID())
```

**마이그레이션 조치:** 이미 범위 내에 있는 컨텍스트를 `session.NewEvent`의 첫 번째 인자로 전달하세요.

### 이벤트 스키마 및 사용자 지정 세션 스토리지

ADK Go 2.0은 그래프 라우팅, 워크플로 상태 및 HITL 일시 중지를 지원하기 위해 핵심 ***Event*** 구조체에 5개의 새 필드를 추가합니다.

| Go 필드 | 직렬화된 이름 | 목적 |
|---|---|---|
| `IsolationScope string` | `isolationScope` | LLM 프롬프트 히스토리에서 이 이벤트를 볼 수 있는 에이전트 컨텍스트를 제한합니다. |
| `Routes []string` | `Routes` | 조건부 엣지 디스패치를 구동하기 위해 노드에서 방출하는 라우팅 키입니다. |
| `RequestedInput *RequestInput` | `RequestedInput` | 워크플로 노드가 사람의 입력을 위해 일시 중지됨을 나타냅니다. |
| `Output any` | `Output` | 워크플로 노드의 일반 데이터 출력입니다. |
| `NodeInfo *NodeInfo` | `nodeInfo` | 이벤트를 방출한 노드를 식별하는 워크플로 노드 메타데이터입니다. |

**마이그레이션 조치:** 모든 Event 페이로드에서 5개의 새 필드를 수신하고 저장하도록 데이터베이스 스키마 및 다운스트림 클라이언트 검증기를 업데이트하세요.

추가적인 ADK Go 1.0 -> 2.0 비호환성을 발견하면 [이슈 트래커](https://github.com/google/adk-go/issues/new?template=bug_report.md&labels=v2)를 통해 제보해 주세요.

### ADK Go 1.x 설치 {#install-go}

ADK Go 1.x를 계속 사용하고 싶다면 1.x 릴리스 라인으로 종속성을 고정하세요.

```shell
go get google.golang.org/adk@v1
```

## 다음 단계

ADK 2.0 기능으로 에이전트를 구축하기 위한 개발자 가이드를 읽어보세요.

-   [**그래프 기반 워크플로**](/ko/graphs/)
-   [**협업 에이전트**](/ko/workflows/collaboration/)
-   [**동적 워크플로**](/ko/graphs/dynamic/)

ADK 2.0에 관심을 가져주셔서 감사합니다! [ADK Go](https://github.com/google/adk-go/issues/new) 또는 [ADK Python](https://github.com/google/adk-python/issues/new)에서 의견을 나눠주세요.
