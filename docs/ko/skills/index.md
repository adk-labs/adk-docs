# ADK 에이전트용 스킬 (Skills)

<div class="language-support-tag">
    <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.25.0</span><span class="lst-typescript">TypeScript v0.6.1</span><span class="lst-go">Go v1.2.0</span><span class="lst-preview">실험적</span>
</div>

에이전트 ***스킬(Skill)***은 ADK 에이전트가 특정 작업을 수행하는 데 사용할 수 있는 독립적인 기능 단위입니다. 에이전트 스킬은 [Agent Skill 사양](https://agentskills.io/specification)을 기반으로 작업에 필요한 지침, 리소스 및 도구를 캡슐화합니다. 스킬의 구조를 통해 점진적으로 로드하여 에이전트의 작동 컨텍스트 윈도우에 미치는 영향을 최소화할 수 있습니다.

!!! example "실험적 기능"
    스킬 기능은 실험적입니다. 각 ADK GitHub 리포지토리를 통한 여러분의 피드백을 환영합니다:
    [ADK Python](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=skills),
    [ADK TypeScript](https://github.com/google/adk-js/issues/new?template=feature_request.md&labels=skills),
    [ADK Go](https://github.com/google/adk-go/issues/new?template=feature_request.md&labels=skills).

## 시작하기

`SkillToolset` 클래스를 사용하여 에이전트에서 하나 이상의 스킬을 사용할 수 있도록 설정합니다. [코드에서 스킬을 정의](#inline-skills)하거나 [파일 시스템에서 스킬을 로드](#filesystem-skills)할 수 있습니다.

=== "Python"

    ```python
    import pathlib

    from google.adk import Agent
    from google.adk.skills import load_skill_from_dir
    from google.adk.tools import skill_toolset

    weather_skill = load_skill_from_dir(
        pathlib.Path(__file__).parent / "skills" / "weather_skill"
    )

    my_skill_toolset = skill_toolset.SkillToolset(
        skills=[weather_skill],
        additional_tools=[get_weather_tool],
    )

    root_agent = Agent(
        model="gemini-flash-latest",
        name="skill_user_agent",
        description="특수 스킬을 사용할 수 있는 에이전트입니다.",
        instruction=(
            "You are a helpful assistant that can leverage skills to perform tasks."
        ),
        tools=[
            my_skill_toolset,
        ],
    )
    ```

    파일 기반 및 인라인 스킬 정의가 모두 포함된 ADK 에이전트의 완전한 코드 예제는 [skills_agent](https://github.com/google/adk-python/tree/main/contributing/samples/environment_and_skills/skills_agent) 샘플을 참조하세요.

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/skills/get_started.ts:full_example"
    ```

=== "Go"

    ```go
    import (
        "context"
        "os"

        "google.golang.org/adk/v2/agent/llmagent"
        "google.golang.org/adk/v2/tool/skilltoolset/skill"
        "google.golang.org/adk/v2/tool/skilltoolset"
        "google.golang.org/adk/v2/tool"
    )

    mySkillToolset, err := skilltoolset.New(ctx, skilltoolset.Config{
        Source: skill.NewFileSystemSource(os.DirFS("./skills")),
    })
    if err != nil {
        // handle error
    }

    rootAgent, err := llmagent.New(llmagent.Config{
        Name:        "skill_user_agent",
        Model:       model,
        Description: "An agent that can use specialized skills.",
        Instruction: "You are a helpful assistant that can leverage skills to perform tasks.",
        Toolsets:    []tool.Toolset{mySkillToolset},
    })
    if err != nil {
        // handle error
    }
    ```

    완전한 예제는 [skills](https://github.com/google/adk-go/tree/main/examples/skills)의 코드 샘플을 참조하세요.

!!! note "작업 디렉터리 확인"

    현재 작업 디렉터리에 `skills/` 디렉터리가 존재하고 에이전트에서 사용할 스킬의 하위 디렉터리가 포함되어 있는지 확인하세요.

## 스킬 구조

스킬 기능을 사용하면 에이전트가 온디맨드로 로드할 수 있는 스킬 지침 및 리소스의 모듈식 패키지를 만들 수 있습니다. 이 접근 방식은 에이전트의 기능을 구성하고 지침이 필요할 때만 로드하여 컨텍스트 윈도우를 최적화하는 데 도움이 됩니다. 스킬 구조는 3개 레벨로 구성됩니다:

-   **L1 (메타데이터):** 스킬 검색을 위한 메타데이터를 제공합니다. 이 정보는 `SKILL.md` 파일의 frontmatter 섹션에 정의되며 스킬 이름 및 설명과 같은 속성을 포함합니다.
-   **L2 (지침):** 에이전트에 의해 스킬이 트리거될 때 로드되는 스킬의 기본 지침을 포함합니다. 이 정보는 `SKILL.md` 파일의 본문에 정의됩니다.
-   **L3 (리소스):** 필요에 따라 로드할 수 있는 참조 자료, 에셋, 스크립트와 같은 추가 리소스를 포함합니다. 이러한 리소스는 다음 디렉터리로 구성됩니다:
    -   `references/`: 확장된 지침, 워크플로 또는 가이드가 포함된 추가 Markdown 파일.
    -   `assets/`: 데이터베이스 스키마, API 문서, 템플릿, 예제와 같은 리소스 자료.
    -   `scripts/`: 에이전트 런타임에서 지원하는 실행 가능한 스크립트.

### 스킬 사용을 위한 시스템 지침

`SkillToolset`은 에이전트가 스킬과 상호작용하는 방법을 설명하는 기본 시스템 지침을 제공합니다:

*   스킬을 사용하기 전에 `load_skill` 도구를 사용하여 스킬의 지침을 읽어야 합니다.
*   스킬 정의의 지침을 정확하게 따라야 합니다.
*   스킬 디렉터리 내의 파일을 보려면 `load_skill_resource` 도구를 사용해야 합니다.
*   스킬의 `scripts/` 디렉터리에서 스크립트를 실행하려면 `run_skill_script`를 사용해야 합니다.

### 스킬 유효성 검사

스킬의 `SKILL.md` 파일의 frontmatter는 다음 요구사항을 충족하는지 검증됩니다:

*   **name**:
    *   64자 이하여야 합니다.
    *   소문자 케밥 케이스(a-z, 0-9 및 하이픈)여야 합니다.
    *   앞이나 뒤에 하이픈이 오거나 연속된 하이픈을 사용할 수 없습니다.
*   **description**:
    *   비어 있어서는 안 됩니다.
    *   1024자 이하여야 합니다.

### 스킬 디렉터리 구조

권장되는 스킬 디렉터리 구조는 다음과 같습니다. 아래에 표시된 `example-skill/` 디렉터리와 병렬 스킬 디렉터리는 [Agent Skill 사양](https://agentskills.io/specification) 파일 구조를 따라야 합니다. `SKILL.md` 파일만 필수입니다.

```
my_agent/
    agent.py (또는 agent.ts / main.go)
    .env
    skills/
        example-skill/        # Skill
            SKILL.md          # 메인 지침 (필수)
            references/
                REFERENCE.md  # 상세 API 레퍼런스
                FORMS.md      # 양식 작성 가이드
                *.md          # 도메인별 정보
            assets/
                *.*           # 템플릿, 이미지, 데이터
            scripts/
                *.py          # 유틸리티 스크립트 (Python)
                *.js          # 유틸리티 스크립트 (JavaScript)
                *.ts          # 유틸리티 스크립트 (TypeScript)
```

## 스킬 소스

[코드 내에서 스킬을 정의](#inline-skills)하거나 [파일 시스템에서 스킬을 읽을](#filesystem-skills) 수 있습니다.

### 코드에서 스킬 정의 {#inline-skills}

아래와 같이 에이전트 코드 내에서 직접 스킬을 정의할 수 있습니다.

=== "Python"

    ```python
    from google.adk.skills import models

    greeting_skill = models.Skill(
        frontmatter=models.Frontmatter(
            name="greeting-skill",
            description=(
                "특정 사람에게 인사를 전할 수 있는 친절한 인사 스킬입니다."
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

=== "TypeScript"

    ```typescript
    --8<-- "examples/typescript/snippets/skills/inline_skill.ts:full_example"
    ```

=== "Go"

    !!! note
        ADK Go는 현재 인라인 스킬을 위한 표준 Source를 제공하지 않지만 향후 추가될 수 있습니다.
        코드에서 직접 스킬을 정의하려면 아래와 같이 `skill.Source` 인터페이스를 직접 구현해야 합니다.

    ```go
    import (
        "context"
        "io"
        "slices"
        "strings"

        "google.golang.org/adk/v2/tool/skilltoolset/skill"
    )

    type StaticSource struct{}

    func (s *StaticSource) ListFrontmatters(ctx context.Context) ([]*skill.Frontmatter, error) {
        return []*skill.Frontmatter{
            {Name: "greeting-skill", Description: "A friendly greeting skill that can say hello to a specific person."},
        }, nil
    }

    func (s *StaticSource) LoadFrontmatter(ctx context.Context, name string) (*skill.Frontmatter, error) {
        if name != "greeting-skill" {
            return nil, skill.ErrSkillNotFound
        }
        return &skill.Frontmatter{Name: "greeting-skill", Description: "A friendly greeting skill that can say hello to a specific person."}, nil
    }

    func (s *StaticSource) LoadInstructions(ctx context.Context, name string) (string, error) {
        if name != "greeting-skill" {
            return "", skill.ErrSkillNotFound
        }
        return "Step 1: Read the 'references/hello_world.txt' file to understand how to greet the user. Step 2: Return a greeting based on the reference.", nil
    }

    func (s *StaticSource) ListResources(ctx context.Context, name, subpath string) ([]string, error) {
        if name != "greeting-skill" {
            return nil, skill.ErrSkillNotFound
        }
        if !slices.Contains([]string{"", ".", "references", "references/"}, subpath) {
            return nil, skill.ErrResourceNotFound
        }
        return []string{"references/hello_world.txt", "references/example.md"}, nil
    }

    func (s *StaticSource) LoadResource(ctx context.Context, name, resourcePath string) (io.ReadCloser, error) {
        if name != "greeting-skill" {
            return nil, skill.ErrSkillNotFound
        }
        switch resourcePath {
        case "references/hello_world.txt":
            return io.NopCloser(strings.NewReader("Hello! So glad to have you here!")), nil
        case "references/example.md":
            return io.NopCloser(strings.NewReader("This is an example reference.")), nil
        default:
            return nil, skill.ErrResourceNotFound
        }
    }
    ```

!!! note
    `Source` 인터페이스는 라이브 업데이트 및 개인화와 같은 동적 사용 사례를 지원하기 위해 모든 데이터 저장소(예: 데이터베이스)로 지원될 수 있습니다.

### 파일 시스템에서 스킬 읽기 {#filesystem-skills}

=== "Python"

    ```python
    import pathlib

    from google.adk.skills import load_skill_from_dir
    from google.adk.tools import skill_toolset

    greeting_skill = load_skill_from_dir(
        pathlib.Path(__file__).parent / "skills" / "greeting-skill"
    )
    weather_skill = load_skill_from_dir(
        pathlib.Path(__file__).parent / "skills" / "weather-skill"
    )

    my_skill_toolset = skill_toolset.SkillToolset(
        skills=[weather_skill, greeting_skill],
    )
    ```

=== "Go"

    ```go
    import (
        "os"

        "google.golang.org/adk/v2/tool/skilltoolset/skill"
        "google.golang.org/adk/v2/tool/skilltoolset"
    )

    // ...

    source := skill.NewFileSystemSource(os.DirFS("./skills"))

    skillToolset, err := skilltoolset.New(ctx, skilltoolset.Config{
        Source: source,
    })
    if err != nil {
        // handle error
    }
    ```

## 스킬 처리 및 유효성 검사

에이전트에 스킬을 포함하면 에이전트는 표준화된 프로세스를 사용하여 스킬과 상호작용합니다. 이 프로세스에는 스킬 사용 방법에 대한 시스템 수준 지침, 스킬 표현 방식에 대한 정의된 형식, 스킬 정의에 대한 일련의 유효성 검사 규칙이 포함됩니다.

## 다음 단계

스킬을 사용하여 에이전트를 빌드하기 위한 다음 리소스를 확인하세요:

- [Python 스킬 코드 샘플](https://github.com/google/adk-python/tree/main/contributing/samples/environment_and_skills/skills_agent)
- [Go 스킬 코드 샘플](https://github.com/google/adk-go/tree/main/examples/skills)
- Agent Skills [사양 문서](https://agentskills.io/)
