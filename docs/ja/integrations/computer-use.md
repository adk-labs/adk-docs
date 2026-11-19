---
catalog_title: Computer Use
catalog_description: Gemini モデルを使ってコンピュータのユーザーインターフェースを操作します
catalog_icon: /integrations/assets/gemini-spark.svg
catalog_tags: ["google"]
---
# Gemini を使用した Computer Use ツールセット

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.17.0</span><span class="lst-preview">プレビュー</span>
</div>

Computer Use（コンピュータ操作）ツールセットを使用すると、エージェントはブラウザーなどのコンピュータのユーザーインターフェースを操作してタスクを完了できます。このツールは、対応する Gemini モデルと [Playwright](https://playwright.dev/) テストツールを使用して Chromium ブラウザーを制御し、スクリーンショットの撮影、クリック、入力、ナビゲーションによって Web ページを操作できます。

Computer Use モデルの詳細については、Gemini API の [Computer Use](https://ai.google.dev/gemini-api/docs/computer-use) または Google Cloud Vertex AI API の [Computer Use](https://cloud.google.com/vertex-ai/generative-ai/docs/computer-use) を参照してください。

!!! example "プレビューリリース"
    Computer Use モデルとツールはプレビューリリースです。詳細については、[リリースステージの説明](https://cloud.google.com/products#product-launch-stages)を参照してください。

## セットアップ

Computer Use ツールセットを使用するには、Playwright とその依存関係（Chromium を含む）をインストールする必要があります。

??? tip "推奨：Python仮想環境の作成とアクティブ化"

    Python仮想環境を作成します。

    ```shell
    python3 -m venv .venv
    ```

    Python仮想環境をアクティブ化します。

    === "Windows CMD"

        ```console
        .venv\Scripts\activate.bat
        ```

    === "Windows PowerShell"

        ```console
        .venv\Scripts\Activate.ps1
        ```

    === "MacOS / Linux"

        ```bash
        source .venv/bin/activate
        ```

Computer Use ツールセットに必要なソフトウェアライブラリをセットアップするには：

1.  Pythonの依存関係をインストールします。
    ```console
    pip install termcolor==3.1.0
    pip install playwright==1.52.0
    pip install browserbase==1.3.0
    pip install rich
    ```
2.  Chromiumブラウザーを含むPlaywrightの依存関係をインストールします。
    ```console
    playwright install-deps chromium
    playwright install chromium
    ```

## ツールの使用

エージェントにツールとして追加して、Computer Use ツールセットを使用します。ツールを設定するときは、エージェントがコンピュータを操作するためのインターフェースを定義する `BaseComputer` クラスの実装を提供する必要があります。次の例では、この目的のために `PlaywrightComputer` クラスが定義されています。この実装のコードは、[computer_use](https://github.com/google/adk-python/blob/main/contributing/samples/computer_use/playwright.py) エージェントサンプルプロジェクトの `playwright.py` ファイルにあります。

```python
from google.adk import Agent
from google.adk.tools.computer_use.computer_use_toolset import ComputerUseToolset

from .playwright import PlaywrightComputer

root_agent = Agent(
    model='gemini-2.5-computer-use-preview-10-2025',
    name='hello_world_agent',
    description=(
        'コンピュータ上のブラウザを操作してユーザーのタスクを完了できるコンピュータ使用エージェント'
    ),
    instruction='あなたはコンピュータ使用エージェントです',
    tools=[
        ComputerUseToolset(computer=PlaywrightComputer(screen_size=(1280, 936)))
    ],
)
```

完全なコード例については、[computer_use](https://github.com/google/adk-python/tree/main/contributing/samples/computer_use)エージェントサンプルプロジェクトを参照してください。
