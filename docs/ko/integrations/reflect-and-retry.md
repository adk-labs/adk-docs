---
catalog_title: Reflect and Retry Plugin
catalog_description: 실패한 도구 호출을 자동으로 재시도합니다
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["google"]
---
# ADK용 Reflect and Retry 플러그인

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.16.0</span><span class="lst-go">Go v0.5.0</span>
</div>

Reflect and Retry 플러그인을 사용하면 에이전트가 ADK [도구](/ko/tools-custom/)의 오류 응답에서 복구하고 도구 요청을 자동으로 재시도할 수 있습니다. 이 플러그인은 도구 오류를 가로채고, 원인 분석(reflection) 및 수정을 위한 구조화된 가이드를 AI 모델에 제공한 뒤, 설정 가능한 한도까지 작업을 재시도합니다. 다음과 같은 기능을 통해 에이전트 워크플로의 복원력을 높일 수 있습니다.

*   **동시성 안전**: 락(lock)을 사용하여 병렬 도구 실행을 안전하게 처리합니다.
*   **구성 가능한 범위**: 호출(invocation) 단위(기본값) 또는 전역 단위로 오류를 추적합니다.
*   **세분화된 추적**: 오류 횟수를 도구별로 개별 추적합니다.
*   **커스텀 오류 추출**: 일반 도구 응답 내부의 오류 상태 감지를 지원합니다.

## Reflect and Retry 플러그인 추가

아래와 같이 ADK 프로젝트의 `App` 객체 내 `plugins` 설정에 플러그인을 등록하여 ADK 워크플로에 추가합니다.

```python
from google.adk.apps.app import App
from google.adk.plugins import ReflectAndRetryToolPlugin

app = App(
    name="my_app",
    root_agent=root_agent,
    plugins=[
        ReflectAndRetryToolPlugin(max_retries=3),
    ],
)
```

이 구성을 사용하면 에이전트가 호출한 도구가 오류를 반환하는 경우 요청이 업데이트되고 도구당 최대 3번까지 다시 시도됩니다.

## 구성 설정

Reflect and Retry 플러그인은 다음과 같은 구성 옵션을 제공합니다.

*   **`max_retries`**: (선택 사항) 오류가 아닌 정상 응답을 받기 위해 시스템이 추가로 재시도하는 최대 횟수입니다. 기본값은 `3`입니다.
*   **`throw_exception_if_retry_exceeded`**: (선택 사항) `False`로 설정하면 마지막 재시도까지 실패하더라도 예외를 발생시키지 않습니다. 기본값은 `True`입니다.
*   **`tracking_scope`**: (선택 사항)
    *   **`TrackingScope.INVOCATION`**: 단일 호출(invocation) 및 사용자 범위 내에서 도구 오류를 추적합니다. 기본값입니다.
    *   **`TrackingScope.GLOBAL`**: 모든 호출 및 모든 사용자에 걸쳐 도구 오류를 추적합니다.

### 고급 구성

`ReflectAndRetryToolPlugin` 클래스를 상속하여 플러그인 동작을 세밀하게 확장할 수 있습니다. 다음 코드 샘플은 응답 내용에서 오류 상태를 감지하도록 확장하는 방법을 보여줍니다.

```python
class CustomRetryPlugin(ReflectAndRetryToolPlugin):
  async def extract_error_from_result(self, *, tool, tool_args,tool_context,
  result):
    # 응답 내용을 기반으로 오류 감지
    if result.get('status') == 'error':
        return result
    return None  # 오류 감지되지 않음

# 이 수정된 플러그인을 앱 객체에 추가합니다.
error_handling_plugin = CustomRetryPlugin(max_retries=5)
```

## 다음 단계

Reflect and Retry 플러그인을 사용하는 전체 코드 샘플은 다음을 참고하세요.

*   [기본](https://github.com/google/adk-python/tree/main/contributing/samples/plugins/plugin_reflect_tool_retry/basic)
    코드 샘플
*   [할루시네이션(환각)으로 생성된 함수 이름](https://github.com/google/adk-python/tree/main/contributing/samples/plugins/plugin_reflect_tool_retry/hallucinating_func_name)
    코드 샘플
