---
catalog_title: Synap
catalog_description: ADK 에이전트에 세션 간 지속되는 장기 메모리를 추가하세요
catalog_icon: /integrations/assets/synap.png
catalog_tags: ["data"]
---

# ADK를 위한 Synap 연동

<div class="language-support-tag">
  <span class="lst-supported">ADK 지원</span><span class="lst-python">Python</span>
</div>

[`maximem-synap-google-adk`](https://pypi.org/project/maximem-synap-google-adk/) 플러그인은 AI 에이전트를 위한 관리형 장기 메모리 레이어인 [Synap](https://www.maximem.ai/synap)에 ADK 에이전트를 연결해 줍니다. Synap은 대화 내용에서 정보(사실, 선호도, 에피소드, 감정 및 시간적 사건)를 자동으로 추출하여 구조화하고, 현재 질의와 의미론적으로 관련된 부분만 조회하여 가져옵니다.

## 주요 사용 사례

- **세션 간 지속되는 메모리 (Persistent cross-session memory)**: 수동으로 기록하지 않고도 여러 세션과 배포 환경에 걸쳐 유지되는 장기 메모리를 ADK 에이전트에 부여합니다.
- **다중 테넌트 격리 (Multi-tenant isolation)**: 메모리 범위가 `user_id` 및 `customer_id`로 제한되므로 다중 사용자 배포 환경에서 엄격한 격리를 보장합니다.
- **의미론적 호출 (Semantic recall)**: 서버 측 추출 기능을 통해 현재 질의와 관련된 정보만 추출하여 프롬프트를 짧게 유지하고 토큰 사용을 효율화합니다.

## 사전 요구사항

- [Synap](https://synap.maximem.ai) 계정 및 API 키
- [Gemini API 키](https://aistudio.google.com/app/api-keys) (또는 ADK와 연동하도록 구성된 기타 모델 제공업체 키)

## 설치

```bash
pip install maximem-synap-google-adk maximem-synap
```

다음 환경 변수를 설정합니다:

```bash
export SYNAP_API_KEY="your-synap-api-key"
```

## 에이전트와 함께 사용하기

`create_synap_tools(...)`는 에이전트가 필요에 따라 메모리를 호출하고 보존하기 위해 부를 수 있는 두 개의 `FunctionTool` 인스턴스인 `search_memory`와 `store_memory`를 반환합니다.

```python
import os

from google.adk.agents.llm_agent import Agent
from maximem_synap import MaximemSynapSDK
from synap_google_adk import create_synap_tools

sdk = MaximemSynapSDK(api_key=os.environ["SYNAP_API_KEY"])

synap_tools = create_synap_tools(
    sdk=sdk,
    user_id="alice",
    customer_id="acme_corp",
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="memory_assistant",
    instruction=(
        "당신은 장기 메모리를 가진 유용한 에이전트 도우미입니다. "
        "search_memory를 사용하여 사용자에 대해 알고 있는 것을 기억해 내세요. "
        "store_memory를 사용하여 사용자가 언급한 새로운 중요한 사실을 저장하세요."
    ),
    tools=synap_tools,
)
```

실행:

```bash
adk run path/to/your_agent
```

첫 번째 턴에서 에이전트에게 정보(예: *"땅콩 알레르기가 있어요"*)를 전달한 뒤, 나중 턴에서 이에 대해 질문해 보세요. Synap은 개별 `adk run` 호출 사이에서도 관련 메모리를 자동으로 조회하여 가져옵니다.

## 사용 가능한 도구

| 도구 | 설명 |
|------|-------------|
| `search_memory` | 사용자의 저장된 메모리에 대한 의미론적 검색을 수행합니다. 자연어 질의를 입력받아 가장 관련성 높은 사실, 선호도, 에피소드를 반환합니다. |
| `store_memory` | 사용자의 장기 메모리에 구체적인 사실을 영속화하여 저장합니다. 사용자가 기억할 만한 내용을 공유할 때 에이전트가 이 도구를 호출합니다. |

## 리소스

- [Synap 공식 문서](https://docs.maximem.ai)
- [ADK 연동 가이드](https://docs.maximem.ai/integrations/google-adk)
- [PyPI의 `maximem-synap-google-adk`](https://pypi.org/project/maximem-synap-google-adk/)
- [오픈 소스 연동 패키지](https://github.com/maximem-ai/maximem_synap_sdk/tree/main/packages/integrations/synap-google-adk)
- [Synap 대시보드](https://synap.maximem.ai)
