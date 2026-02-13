---
catalog_title: Freeplay
catalog_description: Freeplay を使ってエンドツーエンドの可観測性とともに AI エージェントを構築・最適化・評価します
catalog_icon: /adk-docs/integrations/assets/freeplay.png
catalog_tags: ["observability"]
---
# Freeplay を使用したエージェントのオブザーバビリティと評価

[Freeplay](https://freeplay.ai/) は、AI エージェントを構築および最適化するためのエンドツーエンドのワークフローを提供し、ADK と統合できます。Freeplay を使用すると、チーム全体が簡単に共同作業して、エージェントの指示 (プロンプト) を繰り返し、さまざまなモデルとエージェントの変更を試して比較し、オフラインとオンラインの両方で評価を実行して品質を測定し、本番環境を監視し、手動でデータを確認できます。

Freeplay の主な利点:

* **シンプルなオブザーバビリティ** - 人間によるレビューを容易にするために、エージェント、LLM コール、ツールコールに焦点を当てています。
* **オンライン評価/自動スコアラー** - 本番環境でのエラー検出用。
* **オフライン評価と実験の比較** - デプロイ前に変更をテストします。
* **プロンプト管理** - Freeplay プレイグラウンドからコードに直接変更をプッシュすることをサポートします。
* **人間によるレビューワークフロー** - エラー分析とデータ注釈に関するコラボレーション用。
* **強力な UI** - ドメインの専門家がエンジニアと緊密に連携できるようにします。

Freeplay と ADK は互いに補完し合っています。ADK は強力で表現力豊かなエージェントオーケストレーションフレームワークを提供し、Freeplay はオブザーバビリティ、プロンプト管理、評価、テストのためにプラグインします。Freeplay と統合すると、Freeplay UI またはコードからプロンプトと評価を更新できるため、チームの誰もが貢献できます。

デモを見るには、[ここをクリック](https://www.loom.com/share/82f41ffde94949beb941cb191f53c3ec?sid=997aff3c-daa3-40ab-93a9-fdaf87ea2ea1)してください。

## はじめに

以下は、Freeplay と ADK を使い始めるためのガイドです。完全なサンプル ADK エージェントリポジトリは[こちら](https://github.com/228Labs/freeplay-google-demo)にあります。

### Freeplay アカウントの作成

無料の [Freeplay アカウント](https://freeplay.ai/signup)にサインアップしてください。

アカウントを作成したら、次の環境変数を定義できます。

```
FREEPLAY_PROJECT_ID=
FREEPLAY_API_KEY=
FREEPLAY_API_URL=
```

### Freeplay ADK ライブラリの使用

Freeplay ADK ライブラリをインストールします。

```
pip install freeplay-python-adk
```

Freeplay は、オブザーバビリティを初期化すると、ADK アプリケーションから OTel ログを自動的にキャプチャします。

```python
from freeplay_python_adk.client import FreeplayADK
FreeplayADK.initialize_observability()
```

また、Freeplay プラグインをアプリに渡す必要もあります。

```python
from app.agent import root_agent
from freeplay_python_adk.freeplay_observability_plugin import FreeplayObservabilityPlugin
from google.adk.runners import App

app = App(
    name="app",
    root_agent=root_agent,
    plugins=[FreeplayObservabilityPlugin()],
)

__all__ = ["app"]
```

これで、通常どおり ADK を使用でき、[オブザーバビリティ] セクションで Freeplay にログが流れているのがわかります。

## オブザーバビリティ

Freeplay のオブザーバビリティ機能を使用すると、エージェントが本番環境でどのように動作しているかを明確に把握できます。個々のエージェントトレースを掘り下げて、各ステップを理解し、問題を診断できます。

![トレースの詳細](https://228labs.com/freeplay-google-demo/images/trace_detail.png)

Freeplay のフィルタリング機能を使用して、関心のあるセグメント全体でデータを検索およびフィルタリングすることもできます。

![フィルター](https://228labs.com/freeplay-google-demo/images/filter.png)

## プロンプト管理 (オプション)

Freeplay は、さまざまなプロンプトバージョンのバージョン管理とテストのプロセスを簡素化する[ネイティブプロンプト管理](https://docs.freeplay.ai/docs/managing-prompts)を提供します。Freeplay UI で ADK エージェントの指示の変更を試し、さまざまなモデルをテストし、機能フラグと同様に更新をコードに直接プッシュできます。

ADK とともに Freeplay のプロンプト管理機能を利用するには、Freeplay ADK エージェントラッパーを使用する必要があります。`FreeplayLLMAgent` は ADK のベース `LlmAgent` クラスを拡張するため、プロンプトをエージェントの指示としてハードコーディングする代わりに、Freeplay アプリケーションでプロンプトをバージョン管理できます。

まず、[プロンプト] -> [プロンプトテンプレートの作成] に移動して、Freeplay でプロンプトを定義します。

![プロンプト](https://228labs.com/freeplay-google-demo/images/prompt.png)

プロンプトテンプレートを作成するときは、次のセクションで説明するように、3 つの要素を追加する必要があります。

### システムメッセージ

これは、コードの「指示」セクションに対応します。

### エージェントコンテキスト変数

システムメッセージの下部に以下を追加すると、進行中のエージェントコンテキストが渡される変数が作成されます。

```python
{{agent_context}}
```

### 履歴ブロック

[新しいメッセージ] をクリックし、役割を [履歴] に変更します。これにより、過去のメッセージが存在する場合に渡されるようになります。

![プロンプトエディター](https://228labs.com/freeplay-google-demo/images/prompt_editor.png)

これで、コードで ```FreeplayLLMAgent``` を使用できます。

```python
from freeplay_python_adk.client import FreeplayADK
from freeplay_python_adk.freeplay_llm_agent import (
    FreeplayLLMAgent,
)

FreeplayADK.initialize_observability()

root_agent = FreeplayLLMAgent(
    name="social_product_researcher",
    tools=[tavily_search],
)
```

```social_product_researcher``` が呼び出されると、プロンプトが Freeplay から取得され、適切な入力変数でフォーマットされます。

## 評価

Freeplay を使用すると、Freeplay Web アプリケーションから[評価](https://docs.freeplay.ai/docs/evaluations)を定義、バージョン管理、実行できます。[評価] -> [新しい評価] に移動して、プロンプトまたはエージェントの評価を定義できます。

![Freeplay での新しい評価の作成](https://228labs.com/freeplay-google-demo/images/eval_create.png)

これらの評価は、オンライン監視とオフライン評価の両方で実行するように構成できます。オフライン評価用のデータセットは、Freeplay にアップロードするか、ログの例から保存できます。

## データセット管理

Freeplay にデータが流れ始めたら、これらのログを使用して、繰り返しテストする[データセット](https://docs.freeplay.ai/docs/datasets)の構築を開始できます。本番ログを使用して、ゴールデンデータセットまたは変更を加えるときにテストするために使用できる障害ケースのコレクションを作成します。

![テストケースの保存](https://228labs.com/freeplay-google-demo/images/save_test_case.png)

## バッチテスト

エージェントを反復処理する際に、[プロンプト](https://docs.freeplay.ai/docs/component-level-test-runs)レベルと[エンドツーエンド](https://docs.freeplay.ai/docs/end-to-end-test-runs)エージェントレベルの両方でバッチテスト (つまり、オフライン実験) を実行できます。これにより、複数の異なるモデルまたはプロンプトの変更を比較し、エージェントの実行全体で変更を直接比較して定量化できます。

ADK を使用して Freeplay でバッチテストを実行するためのコード例は[こちら](https://github.com/228Labs/freeplay-google-demo/blob/main/examples/example_test_run.py)です。Google ADK を使用して Freeplay でバッチテストを実行するためのコード例は[こちら](https://github.com/228Labs/freeplay-google-demo/blob/main/examples/example_test_run.py)です。

## 今すぐサインアップ

[Freeplay](https://freeplay.ai/) にアクセスしてアカウントにサインアップし、[こちら](https://github.com/228Labs/freeplay-google-demo)で完全な Freeplay <> ADK 統合を確認してください。
