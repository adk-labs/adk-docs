---
catalog_title: Bash Tool
catalog_description: 보안 및 리소스가 제한된 로컬 샌드박스 내에서 Bash 명령 실행
catalog_icon: /integrations/assets/bash.png
catalog_tags: ["code", "google"]
---

# ADK용 Bash 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.27.0</span>
</div>

`ExecuteBashTool`을 사용하면 ADK 에이전트가 로컬 작업 공간 디렉토리 내에서 Bash 명령을 실행할 수 있습니다. 이 도구는 파일 시스템 작업, 스크립트 실행 또는 에이전트를 통해 로컬 환경과 직접 상호작용하는 데 유용합니다.
이 도구는 Python ADK에서만 사용할 수 있습니다.

## 설치

Bash 도구는 핵심 에이전트 개발 키트(ADK)에 기본으로 포함되어 있습니다. 별도의 통합 패키지를 설치할 필요 없이 메인 라이브러리를 설치하기만 하면 됩니다.

```bash
pip install google-adk
```

## 에이전트와 함께 사용

!!! warning "POSIX 전용"

    `ExecuteBashTool`은 현재 Linux 또는 macOS와 같은 **POSIX 시스템에서만 지원**됩니다. Windows 시스템에서 이 도구를 실행하면 심각한 오류가 발생합니다.

Bash 도구를 사용하려면 `ExecuteBashTool`을 인스턴스화하고 에이전트의 `tools` 목록에 포함합니다. 코드 스니펫을 실행하기 전에 `my_workspace_path`가 유효한 디렉토리 경로 문자열로 정의되어 있는지 확인하세요.

```python
from google.adk.tools.bash_tool import ExecuteBashTool, BashToolPolicy

policy = BashToolPolicy(
    allowed_command_prefixes=("ls", "cat", "grep"),
    timeout_seconds=30,
    max_memory_bytes=1024 * 1024 * 512,   # 512MB
    max_file_size_bytes=1024 * 1024 * 10, # 10MB
    max_child_processes=5
)

tool = ExecuteBashTool(workspace=my_workspace_path, policy=policy)
```

## 보안 및 실행 보호 조치

임의의 코드를 실행하는 것은 본질적인 위험을 동반하므로, `ExecuteBashTool`에는 생성된 하위 프로세스에 적용되는 여러 필수 및 선택적 보안 기능이 포함되어 있습니다.

### 기본 정책은 모든 명령 허용

기본적으로 `BashToolPolicy`는 `allowed_command_prefixes=("*",)`로 초기화됩니다. 즉, **기본적으로 모든 명령이 허용**됩니다. 애플리케이션을 보호하려면 정책을 초기화할 때 허용되는 명령을 명시적으로 제한해야 합니다.

```python
# 보안 구현 예시
from google.adk.tools.bash_tool import BashToolPolicy

strict_policy = BashToolPolicy(
    allowed_command_prefixes=("ls ", "cat ", "pwd")
)
```

### 내장 보호 기능

1. **사용자 확인:** 도구는 명령을 실행하기 전에 **항상** 사용자 확인을 요청합니다. 프레임워크는 실행을 일시 중지하고 `adk_request_confirmation` 흐름을 통해 사용자 또는 클라이언트 애플리케이션이 명령을 승인할 때까지 대기합니다.
2. **명령 검증:** `allowed_command_prefixes`를 사용하여 특정 명령을 허용 목록에 추가하고 `blocked_operators`를 사용하여 특정 문자열 패턴을 엄격하게 금지할 수 있습니다.
3. **리소스 제한:** 포크 봄(fork bomb)이나 메모리 고갈을 방지하기 위해 OS 수준의 제한인 `setrlimit`이 적용되어 메모리 소비, 파일 크기 및 하위 프로세스 수를 제한합니다.
4. **코어 덤프 비활성화:** 민감한 메모리 유출을 방지하기 위해 실행 하위 프로세스에 대해 코어 덤프가 엄격하게 비활성화(`RLIMIT_CORE`가 `0`으로 설정)됩니다.
5. **프로세스 그룹 종료:** 명령이 `timeout_seconds`를 초과하면 도구는 전체 프로세스 그룹에 `SIGKILL`을 발송하여 고아 백그라운드 프로세스가 남지 않도록 합니다.

## 사용 가능한 도구

| 도구 이름 | 클래스 이름 | 설명 |
| :--- | :--- | :--- |
| `execute_bash` | `ExecuteBashTool` | 작업 공간 내에서 Bash 명령을 실행합니다. POSIX 전용 |
