# ADK 에이전트를 위한 스킬

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.25.0</span><span class="lst-preview">실험적</span>
</div>

에이전트 ***스킬(Skill)*** 은 ADK 에이전트가 특정 작업을 수행할 때 사용할 수 있는
독립적인 기능 단위입니다. 에이전트 스킬은
[Agent Skill specification](https://agentskills.io/specification)을 기반으로,
작업 수행에 필요한 지침, 리소스, 도구를 하나로 캡슐화합니다.
스킬 구조는 에이전트의 운영 컨텍스트 윈도우에 미치는 영향을 최소화하기 위해
점진적으로 로드할 수 있도록 설계되어 있습니다.

!!! example "실험적 기능"
    Skills 기능은 실험적 기능이며
    [알려진 제한 사항](#known-limitations)이 있습니다.
    [피드백](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=skills)을 환영합니다.

## 시작하기

`SkillToolset` 클래스를 사용하면 하나 이상의 스킬을 에이전트 정의에 포함한 뒤
에이전트의 도구 목록에 추가할 수 있습니다.
[코드 안에서 스킬을 정의](#inline-skills)할 수도 있고,
아래와 같이 파일 정의에서 스킬을 불러올 수도 있습니다.

```python
import pathlib

from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

weather_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "weather_skill"
)

my_skill_toolset = skill_toolset.SkillToolset(
    skills=[weather_skill]
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="skill_user_agent",
    description="An agent that can use specialized skills.",
    instruction=(
        "You are a helpful assistant that can leverage skills to perform tasks."
    ),
    tools=[
        my_skill_toolset,
    ],
)
```

파일 기반 스킬 정의와 인라인 스킬 정의를 모두 포함한 ADK 에이전트의 전체 예제는
코드 샘플
[skills_agent](https://github.com/google/adk-python/tree/main/contributing/samples/skills_agent)를 참조하세요.

## 스킬 정의하기

Skills 기능을 사용하면 에이전트가 필요할 때 로드할 수 있는
스킬 지침과 리소스를 모듈형 패키지로 만들 수 있습니다.
이 접근 방식은 에이전트의 기능을 체계적으로 구성하고,
필요할 때만 지침을 로드함으로써 컨텍스트 윈도우를 최적화하는 데 도움이 됩니다.
스킬 구조는 세 단계로 구성됩니다.

-   **L1 (메타데이터):** 스킬 검색을 위한 메타데이터를 제공합니다.
    이 정보는 `SKILL.md` 파일의 frontmatter 섹션에 정의되며,
    스킬 이름과 설명 같은 속성을 포함합니다.
-   **L2 (지침):** 에이전트가 스킬을 트리거할 때 로드되는
    스킬의 기본 지침을 포함합니다.
    이 정보는 `SKILL.md` 파일 본문에 정의됩니다.
-   **L3 (리소스):** 필요에 따라 로드할 수 있는 참조 자료,
    에셋, 스크립트 같은 추가 리소스를 포함합니다.
    이러한 리소스는 다음 디렉터리에 정리됩니다.
    -   `references/`: 확장 지침, 워크플로, 가이드를 담은 추가 Markdown 파일
    -   `assets/`: 데이터베이스 스키마, API 문서, 템플릿, 예제 같은 리소스 자료
    -   `scripts/`: 에이전트 런타임이 지원하는 실행 가능한 스크립트

### 파일로 스킬 정의하기

다음 디렉터리 구조는 ADK 에이전트 프로젝트에 스킬을 포함하는 권장 방식입니다.
아래에 보이는 `example_skill/` 디렉터리와 다른 병렬 스킬 디렉터리는
[Agent Skill specification](https://agentskills.io/specification)의
파일 구조를 따라야 합니다.
`SKILL.md` 파일만 필수입니다.

```
my_agent/
    agent.py
    .env
    skills/
        example_skill/        # Skill
            SKILL.md          # main instructions (required)
            references/
                REFERENCE.md  # detailed API reference
                FORMS.md      # form-filling guide
                *.md          # domain-specific information
            assets/
                *.*           # templates, images, data
            scripts/
                *.py          # utility scripts
```

!!! warning "스크립트 실행은 아직 지원되지 않음"
    스크립트 실행은 아직 지원되지 않으며
    [알려진 제한 사항](#known-limitations)에 포함되어 있습니다.

### 코드로 스킬 정의하기 {#inline-skills}

ADK 에이전트에서는 아래 예시처럼 `Skill` 모델 클래스를 사용해
에이전트 코드 안에서 스킬을 정의할 수도 있습니다.
이 방식은 ADK 에이전트 코드에서 스킬을 동적으로 수정할 수 있게 해줍니다.

```python
from google.adk.skills import models

greeting_skill = models.Skill(
    frontmatter=models.Frontmatter(
        name="greeting-skill",
        description=(
            "A friendly greeting skill that can say hello to a specific person."
        ),
    ),
    instructions=(
        "Step 1: Read the 'references/hello_world.txt' file to understand how"
        " to greet the user. Step 2: Return a greeting based on the reference."
    ),
    resources=models.Resources(
        references={
            "hello_world.txt": "Hello! So glad to have you here!",
            "example.md": "This is an example reference.",
        },
    ),
)
```

## 알려진 제한 사항 {#known-limitations}

Skills 기능은 실험적이며 현재 다음 제한 사항이 있습니다.

-   **스크립트 실행:** Skills 기능은 현재
    스크립트 실행(`scripts/` 디렉터리)을 지원하지 않습니다.

## 다음 단계

스킬을 사용하는 에이전트를 빌드할 때 다음 자료를 참고하세요.

*   ADK Skills 에이전트 코드 샘플:
    [skills_agent](https://github.com/google/adk-python/tree/main/contributing/samples/skills_agent)
*   Agent Skills
    [specification documentation](https://agentskills.io/)
