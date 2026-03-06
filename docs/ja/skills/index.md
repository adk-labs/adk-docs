# ADK エージェント向けスキル

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.25.0</span><span class="lst-preview">実験的</span>
</div>

エージェント ***Skill*** は、ADK エージェントが特定のタスクを実行するために
利用できる自己完結型の機能単位です。エージェント Skill は
[Agent Skill specification](https://agentskills.io/specification) に基づき、
タスクに必要な指示、リソース、ツールをまとめてカプセル化します。
Skill の構造は、エージェントのコンテキストウィンドウへの影響を最小限に抑えるため、
段階的に読み込めるようになっています。

!!! example "実験的"
    Skills 機能は実験的であり、
    [既知の制限事項](#known-limitations)があります。
    [フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=skills)を歓迎します。

## はじめに

`SkillToolset` クラスを使うと、1 つ以上の Skill をエージェント定義に含め、
その後エージェントの tools リストへ追加できます。
[コード内で Skill を定義](#inline-skills)することも、
以下のようにファイル定義から Skill を読み込むこともできます。

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
    model="gemini-2.5-flash",
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

ファイルベースとインラインの Skill 定義の両方を含む ADK エージェントの完全な例については、
コードサンプル
[skills_agent](https://github.com/google/adk-python/tree/main/contributing/samples/skills_agent) を参照してください。

## Skill を定義する

Skills 機能を使うと、エージェントが必要に応じて読み込める
Skill の指示やリソースをモジュール化パッケージとして作成できます。
この方式により、エージェントの能力を整理しやすくなり、
必要なときだけ指示を読み込むことでコンテキストウィンドウを最適化できます。
Skill の構造は 3 つのレベルで構成されます。

-   **L1 (メタデータ):** Skill 発見のためのメタデータを提供します。
    この情報は `SKILL.md` ファイルの frontmatter セクションに定義され、
    Skill 名や説明などのプロパティを含みます。
-   **L2 (指示):** エージェントが Skill をトリガーしたときに読み込まれる
    Skill の主たる指示を含みます。
    この情報は `SKILL.md` ファイル本文に定義されます。
-   **L3 (リソース):** 必要に応じて読み込める参照資料、
    アセット、スクリプトなどの追加リソースを含みます。
    これらのリソースは次のディレクトリに整理されます。
    -   `references/`: 拡張指示、ワークフロー、ガイダンスを含む追加 Markdown ファイル
    -   `assets/`: データベーススキーマ、API ドキュメント、テンプレート、例などの資料
    -   `scripts/`: エージェントランタイムがサポートする実行可能スクリプト

### ファイルで Skill を定義する

次のディレクトリ構造は、ADK エージェントプロジェクトに Skill を含める推奨方法を示しています。
以下に示す `example_skill/` ディレクトリと、それと並列に置く Skill ディレクトリは
[Agent Skill specification](https://agentskills.io/specification) の
ファイル構造に従う必要があります。
必須なのは `SKILL.md` ファイルだけです。

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

!!! warning "スクリプト実行は未対応"
    スクリプト実行はまだサポートされておらず、
    [既知の制限事項](#known-limitations)に含まれます。

### コードで Skill を定義する {#inline-skills}

ADK エージェントでは、以下の例のように `Skill` モデルクラスを使って
エージェントコード内で Skill を定義することもできます。
この定義方法により、ADK エージェントコードから Skill を動的に変更できます。

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

## 既知の制限事項 {#known-limitations}

Skills 機能は実験的であり、現在は次の制限があります。

-   **スクリプト実行:** Skills 機能は現在、
    スクリプト実行 (`scripts/` ディレクトリ) をサポートしていません。

## 次のステップ

Skills を使うエージェントを構築する際は、次の資料を参照してください。

*   ADK Skills エージェントのコードサンプル:
    [skills_agent](https://github.com/google/adk-python/tree/main/contributing/samples/skills_agent)
*   Agent Skills
    [specification documentation](https://agentskills.io/)
