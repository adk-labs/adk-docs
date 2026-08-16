# ADK エージェント用スキル (Skills)

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.25.0</span><span class="lst-typescript">TypeScript v0.6.1</span><span class="lst-go">Go v1.2.0</span><span class="lst-preview">プレビュー</span>
</div>

エージェント ***スキル (Skill)*** は、ADK エージェントが特定のタスクを実行するために使用できる自己完結型の機能単位です。エージェント スキルは、[Agent Skill 仕様](https://agentskills.io/specification) に基づいて、タスクに必要な指示、リソース、ツールをカプセル化します。スキルの構造により、段階的にロードしてエージェントの動作コンテキスト ウィンドウへの影響を最小限に抑えることができます。

!!! example "プレビュー"
    スキル機能はプレビュー段階です。各 ADK GitHub リポジトリからのフィードバックをお待ちしております。
    [ADK Python](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=skills)、
    [ADK TypeScript](https://github.com/google/adk-js/issues/new?template=feature_request.md&labels=skills)、
    [ADK Go](https://github.com/google/adk-go/issues/new?template=feature_request.md&labels=skills)。

## はじめに

`SkillToolset` クラスを使用して、エージェントで 1 つ以上のスキルを使用できるようにします。[コード内でスキルを定義](#inline-skills) するか、[ファイルシステムからスキルをロード](#filesystem-skills) できます。

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
        description="特殊なスキルを使用できるエージェント。",
        instruction=(
            "You are a helpful assistant that can leverage skills to perform tasks."
        ),
        tools=[
            my_skill_toolset,
        ],
    )
    ```

    ファイルベースおよびインラインのスキル定義を含む ADK エージェントの完全なコード例については、[skills_agent](https://github.com/google/adk-python/tree/main/contributing/samples/environment_and_skills/skills_agent) サンプルを参照してください。

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
        // エラー処理
    }

    rootAgent, err := llmagent.New(llmagent.Config{
        Name:        "skill_user_agent",
        Model:       model,
        Description: "特殊なスキルを使用できるエージェント。",
        Instruction: "You are a helpful assistant that can leverage skills to perform tasks.",
        Toolsets:    []tool.Toolset{mySkillToolset},
    })
    if err != nil {
        // エラー処理
    }
    ```

    完全な例については、[skills](https://github.com/google/adk-go/tree/main/examples/skills) のコード サンプルを参照してください。

!!! note "作業ディレクトリの確認"

    現在の作業ディレクトリに `skills/` ディレクトリが存在し、エージェントで使用するスキルのサブディレクトリが含まれていることを確認してください。

## スキルの構造

スキル機能を使用すると、エージェントが必要に応じてロードできるスキル指示とリソースのモジュール式パッケージを作成できます。このアプローチは、エージェントの機能を整理し、必要な場合にのみ指示をロードすることでコンテキスト ウィンドウを最適化するのに役立ちます。スキルの構造は 3 つのレベルに編成されています。

-   **L1 (メタデータ):** スキル検出用のメタデータを提供します。この情報は `SKILL.md` ファイルの frontmatter セクションで定義され、スキル名や説明などのプロパティが含まれます。
-   **L2 (指示):** エージェントによってスキルがトリガーされたときにロードされるスキルのプライマリ指示が含まれます。この情報は `SKILL.md` ファイルの本文で定義されます。
-   **L3 (リソース):** 必要に応じてロードできる参考資料、アセット、スクリプトなどの追加リソースが含まれます。これらのリソースは次のディレクトリに編成されています。
    -   `references/`: 拡張された指示、ワークフロー、またはガイダンスを含む追加の Markdown ファイル。
    -   `assets/`: データベース スキーマ、API ドキュメント、テンプレート、例などのリソース資料。
    -   `scripts/`: エージェント ランタイムでサポートされている実行可能スクリプト。

### スキルを使用するためのシステム指示

`SkillToolset` は、スキルとの対話方法の概要を示すデフォルトのシステム指示をエージェントに提供します。

*   スキルを使用する前に、`load_skill` ツールを使用してスキルの指示を読む必要があります。
*   スキル定義の指示に正確に従う必要があります。
*   スキル ディレクトリ内のファイルを表示するには、`load_skill_resource` ツールを使用する必要があります。
*   スキルの `scripts/` ディレクトリからスクリプトを実行するには、`run_skill_script` を使用する必要があります。

### スキルの検証

スキルの `SKILL.md` ファイルの frontmatter は、次の要件を満たしていることが検証されます。

*   **name**:
    *   64 文字以下である必要があります。
    *   小文字のケバブケース (a-z、0-9、およびハイフン) である必要があります。
    *   先頭、末尾、または連続したハイフンを含めることはできません。
*   **description**:
    *   空であってはなりません。
    *   1024 文字以下である必要があります。

### スキル ディレクトリ構造

推奨されるスキル ディレクトリ構造は次のとおりです。以下に示す `example-skill/` ディレクトリおよび並列のスキル ディレクトリは、[Agent Skill 仕様](https://agentskills.io/specification) のファイル構造に従う必要があります。`SKILL.md` ファイルのみが必須です。

```
my_agent/
    agent.py (または agent.ts / main.go)
    .env
    skills/
        example-skill/        # Skill
            SKILL.md          # メイン指示 (必須)
            references/
                REFERENCE.md  # 詳細な API リファレンス
                FORMS.md      # フォーム入力ガイド
                *.md          # ドメイン固有の情報
            assets/
                *.*           # テンプレート、画像、データ
            scripts/
                *.py          # ユーティリティ スクリプト (Python)
                *.js          # ユーティリティ スクリプト (JavaScript)
                *.ts          # ユーティリティ スクリプト (TypeScript)
```

## スキル ソース

[コード内でスキルを定義](#inline-skills) するか、[ファイルシステムからスキルを読み取る](#filesystem-skills) ことができます。

### コードでのスキル定義 {#inline-skills}

以下に示すように、エージェントのコード内で直接スキルを定義できます。

=== "Python"

    ```python
    from google.adk.skills import models

    greeting_skill = models.Skill(
        frontmatter=models.Frontmatter(
            name="greeting-skill",
            description=(
                "特定の人に挨拶できる親しみやすい挨拶スキル。"
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
        ADK Go は現在インライン スキル用の標準 Source を提供していませんが、将来追加される可能性があります。
        コード内で直接スキルを定義するには、以下に示すように `skill.Source` インターフェースを自分で実装する必要があります。

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
    `Source` インターフェースは、ライブ更新やパーソナライゼーションなどの動的なユースケースをサポートするために、任意のデータ ストア (データベースなど) によって支援されます。

### ファイルシステムからのスキルの読み取り {#filesystem-skills}

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
        // エラー処理
    }
    ```

## スキルの処理と検証

エージェントにスキルを含めると、エージェントは標準化されたプロセスを使用してスキルと対話します。このプロセスには、スキルの使用方法に関するシステム レベルの指示、スキルの表現方法に関する定義された形式、およびスキル定義の一連の検証ルールが含まれます。

## 次のステップ

スキルを使用してエージェントを構築するための次のリソースを確認してください。

- [Python でのスキル - コード サンプル](https://github.com/google/adk-python/tree/main/contributing/samples/environment_and_skills/skills_agent)
- [Go でのスキル - コード サンプル](https://github.com/google/adk-go/tree/main/examples/skills)
- Agent Skills [仕様ドキュメント](https://agentskills.io/)
