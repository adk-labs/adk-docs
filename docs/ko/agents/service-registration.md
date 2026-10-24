# 서비스 등록

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.34.0</span>
</div>

세션, 아티팩트, 메모리 및 Agent2Agent(A2A) 태스크 저장소를 위한 커스텀 서비스를 등록하여 ADK 런타임 기능을 확장할 수 있습니다. 커스텀 서비스를 등록하면 자체 백엔드 시스템과 스토리지 제공업체를 에이전트에 통합할 수 있습니다.

다음 두 가지 방법 중 하나를 사용하여 커스텀 서비스를 등록하세요.

*   **`services.yaml`**: 간단한 생성자로 인스턴스화되는 서비스를 위한 YAML 구성 파일입니다.
*   **`services.py`**: 커스텀 초기화나 복잡한 로직이 필요한 서비스를 위한 Python 스크립트입니다.

## `services.yaml`로 서비스 등록

간단한 생성자(예: `MyService(uri="...")`)로 인스턴스화되는 서비스를 등록하려면 `services.yaml` 또는 `services.yml` 파일을 사용하세요. 이 파일을 에이전트 디렉터리(`adk run` 사용 시) 또는 에이전트 루트 디렉터리(`adk web` 및 `adk api_server` 사용 시)에 배치합니다.

`services.yaml`에서 커스텀 서비스를 정의합니다:

```yaml
services:
  - scheme: mysession
    type: session
    class: my_custom_package.modules.MyCustomSessionService
  - scheme: myartifact
    type: artifact
    class: my_custom_package.storage.MyCustomArtifactService
  - scheme: mymemory
    type: memory
    class: my_custom_package.modules.MyCustomMemoryService
  - scheme: mytaskstore
    type: task_store
    class: my_custom_package.tasks.MyCustomTaskStore
```

`services.yaml` 파일은 다음 속성을 지원합니다:

*   `scheme`: 커스텀 서비스를 트리거하는 URI 스킴입니다(예: `mysession://`).
*   `type`: 서비스 유형으로, `session`, `artifact`, `memory` 또는 `task_store`가 될 수 있습니다.
*   `class`: 서비스 구현체의 정규화된(fully qualified) 클래스 이름입니다.

## `services.py`로 서비스 등록

복잡한 초기화가 필요하거나 서비스 생성 프로세스를 더 세밀하게 제어해야 하는 경우, `services.yaml`과 동일한 위치에 `services.py` 파일을 배치하여 사용하세요.

`services.py`에서 커스텀 `session`, `artifact`, `memory` 서비스를 등록합니다:

```python
from google.adk.cli.service_registry import get_service_registry
from my_custom_package.modules import MyCustomSessionService
from my_custom_package.storage import MyCustomArtifactService
from my_custom_package.memory import MyCustomMemoryService

def my_session_factory(uri: str, **kwargs):
    # 여기에 커스텀 로직을 추가합니다.
    return MyCustomSessionService(uri=uri, **kwargs)

def my_artifact_factory(uri: str, **kwargs):
    """커스텀 아티팩트 서비스를 인스턴스화하는 팩토리 함수입니다."""
    return MyCustomArtifactService(uri=uri, **kwargs)

def my_memory_factory(uri: str, **kwargs):
    """커스텀 메모리 서비스를 인스턴스화하는 팩토리 함수입니다."""
    return MyCustomMemoryService(uri=uri, **kwargs)

# 레지스트리를 가져옵니다.
registry = get_service_registry()

# 세션, 아티팩트, 메모리 서비스를 등록합니다.
registry.register_session_service("mysession", my_session_factory)
registry.register_artifact_service("myartifact", my_artifact_factory)
registry.register_memory_service("mymemory", my_memory_factory)
```

예제 스크립트는 다음 작업을 수행합니다:

1.  `get_service_registry`를 임포트하여 서비스 레지스트리 인스턴스를 가져옵니다.
2.  URI와 키워드 인수를 받아 커스텀 서비스의 인스턴스를 반환하는 팩토리 함수(예: `my_session_factory`)를 정의합니다.
3.  `register_session_service`, `register_artifact_service`, `register_memory_service`를 사용하여 원하는 스킴(예: `mysession`)으로 팩토리 함수를 등록합니다.

## 서비스 로드

ADK 명령줄 도구(`adk run`, `adk web` 또는 `adk api_server`)로 에이전트를 실행하면 ADK는 `services.yaml`(또는 `services.yml`) 및 `services.py`에서 커스텀 서비스를 자동으로 검색하고 로드합니다.

### 검색 위치

ADK는 실행하는 명령어에 따라 구성 파일의 위치를 찾습니다:

*   **`adk run`**: 에이전트 디렉터리에서 서비스 파일을 검색합니다.
*   **`adk web` 및 `adk api_server`**: 명령어에 전달된 에이전트 루트 디렉터리에서 서비스 파일을 검색합니다.

### 로드 순서 및 우선순위

대상 디렉터리에 `services.yaml`과 `services.py`가 모두 있는 경우:

1.  **로드 순서**: ADK는 `services.yaml`을 먼저 로드한 다음 `services.py`를 로드합니다.
2.  **우선순위**: 동일한 스킴을 가진 서비스가 두 파일 모두에 정의된 경우, `services.py`의 정의가 우선 적용됩니다.
