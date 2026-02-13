---
catalog_title: Reflect and Retry Plugin
catalog_description: Automatically retry tool calls that fail
catalog_icon: /adk-docs/integrations/assets/adk.png
catalog_tags: ["google"]
---
# 반영 및 재시도 도구 플러그인

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.16.0</span>
</div>

반영 및 재시도 도구 플러그인은 에이전트가 ADK [도구](/adk-docs/ko/tools-custom/)의 오류 응답에서 복구하고 도구 요청을 자동으로 재시도하는 데 도움이 될 수 있습니다. 이 플러그인은 도구 오류를 가로채고, 반영 및 수정을 위해 AI 모델에 구조화된 지침을 제공하며, 구성 가능한 한도까지 작업을 재시도합니다. 이 플러그인은 다음 기능을 포함하여 에이전트 워크플로에 더 많은 복원력을 구축하는 데 도움이 될 수 있습니다.

*   **동시성 안전**: 잠금을 사용하여 병렬 도구 실행을 안전하게 처리합니다.
*   **구성 가능한 범위**: 호출당(기본값) 또는 전역적으로 오류를 추적합니다.
*   **세분화된 추적**: 오류 횟수는 도구별로 추적됩니다.
*   **사용자 지정 오류 추출**: 일반 도구 응답에서 오류 감지를 지원합니다.

## 반영 및 재시도 플러그인 추가

아래와 같이 ADK 프로젝트의 앱 객체의 플러그인 설정에 이 플러그인을 추가하여 ADK 워크플로에 추가합니다.

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

반영 및 재시도 플러그인에는 다음과 같은 구성 옵션이 있습니다.

*   **`max_retries`**: (선택 사항) 시스템이 오류가 아닌 응답을 받기 위해 시도하는 총 추가 시도 횟수입니다. 기본값은 3입니다.
*   **`throw_exception_if_retry_exceeded`**: (선택 사항) `False`로 설정하면 최종 재시도 시도가 실패하더라도 시스템에서 오류를 발생시키지 않습니다. 기본값은 `True`입니다.
*   **`tracking_scope`**: (선택 사항)
    *   **`TrackingScope.INVOCATION`**: 단일 호출 및 사용자에 대한 도구 오류를 추적합니다. 이 값은 기본값입니다.
    *   **`TrackingScope.GLOBAL`**: 모든 호출 및 모든 사용자에 대한 도구 오류를 추적합니다.

### 고급 구성

`ReflectAndRetryToolPlugin` 클래스를 확장하여 이 플러그인의 동작을 추가로 수정할 수 있습니다. 다음 코드 샘플은 오류 상태의 응답을 선택하여 동작을 간단하게 확장하는 방법을 보여줍니다.

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

반영 및 재시도 플러그인을 사용하는 전체 코드 샘플은 다음을 참조하십시오.

*   [기본](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_reflect_tool_retry/basic) 코드 샘플
*   [환각 함수 이름](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_reflect_tool_retry/hallucinating_func_name) 코드 샘플
