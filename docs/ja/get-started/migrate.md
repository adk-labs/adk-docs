---
description: Agents CLI とコーディング アシスタントを使用して、既存の AI エージェント、カスタム エージェント ループ、ワークフローを Google Agent Development Kit (ADK) に移行する方法について説明します。
---

# 既存のエージェントを ADK に移行する

このガイドでは、Agents CLI とコーディング エージェントを使用して、既存のエージェント コードベースを Agent Development Kit (ADK) に移行する方法を説明します。ADK に移行することで、複数のプログラミング言語にわたってエージェント アーキテクチャを標準化し、組み込みの評価ツールを活用し、Google Cloud に直接デプロイできるようになります。

## Agents CLI を使用した移行

状態オブジェクト、ノードグラフ、実行ループを 1 行ずつ手動で書き直す代わりに、Agents CLI を使用してコーディング エージェントとともに移行の計画と実行を行うことができます。

Agents CLI は、Antigravity、Claude Code、Cursor、Codex などのコーディング エージェントに ADK 開発スキルをインストールします。既存のプロジェクトでコーディング エージェントを開くと、次のことが可能になります:

* 現在のエージェント構造、ツール、状態、ルーティング ルールの分析。
* 既存のコンポーネントをネイティブの ADK クラスやグラフ ワークフローにマッピング。
* トレードオフを含むアーキテクチャ オプションの提案。
* ツール、エージェント定義、セッション処理の段階的な変換。
* 移行前後の動作を検証するための評価データセットの生成。

Agents CLI の使用方法の詳細については、[Agents CLI](https://google.github.io/agents-cli/) のドキュメントをご覧ください。

## 前提条件

移行を開始する前に、以下がインストールされていることを確認してください:

* Python 3.11 以降
* [`uv`](https://docs.astral.sh/uv/getting-started/installation/) パッケージ マネージャー
* サポートされているコーディング エージェント

コーディング エージェントに Agents CLI とその ADK スキルをインストールします:

```bash
uvx google-agents-cli setup
```

インストールを確認するには、次を実行します:

```bash
agents-cli info
```

## 移行ワークフロー

既存のエージェントを ADK に移行するには、次の手順に従います:

1. [既存プロジェクトでコーディング エージェントを開く](#既存プロジェクトでコーディング-エージェントを開く)
2. [移行計画をブレインストーミングする](#移行計画をブレインストーミングする)
3. [エージェント パターンを ADK にマッピングする](#エージェント-パターンを-adk-にマッピングする)
4. [評価を伴うコード変換](#評価を伴うコード変換)
5. [検証と評価](#検証と評価)

### 既存プロジェクトでコーディング エージェントを開く

既存のエージェント プロジェクトのルート ディレクトリでターミナルまたは IDE を開き、コーディング エージェントを起動します。エージェントが Agents CLI によってインストールされた ADK スキルを検出していることを確認します。

### 移行計画をブレインストーミングする

コーディング エージェントに現在のコードベースを検査し、ターゲットとなる ADK アーキテクチャをブレインストーミングするよう依頼します。エージェントには Agents CLI を介して ADK スキルが読み込まれているため、ADK の状態管理、グラフ ワークフロー、オーケストレーション パターンを理解しています。コーディング エージェントで次のようなプロンプトを使用します:

```text title="コード エージェント プロンプト"
I want to migrate this existing agent codebase to Google Agent Development Kit (ADK).
Please inspect our current files, state schema, tools, and control flow.
Propose 2-3 target ADK architecture options with trade-offs, and recommend the cleanest approach.
Include an evaluation plan to verify behavior using agents-cli eval.
```

コーディング エージェントは次の項目を分析します:

* **実行フロー (Execution flow):** 単一のツール呼び出しループ、決定論的グラフ ワークフロー、動的ルーター、またはマルチエージェント チーム。
* **ツール (Tools):** 関数、パラメータ シグネチャ、docstring、外部 API 呼び出し。
* **メモリと検索 (Memory and retrieval):** ナレッジ ストア、ベクトル検索の統合、または会話メモリ。
* **状態 (State):** ターン間で追跡される変数、スクラッチパッド キー、セッション ストレージ。
* **ターゲット クラス (Target classes):** `Agent` や `Workflow` など、どの ADK クラスが最も適しているか。
* **評価戦略 (Evaluation strategy):** 移行したエージェントをベンチマークするために、既存のテストケースを評価データセットに変換する方法。

提案されたアプローチを確認したら、要件に合ったアーキテクチャを承認します。

### エージェント パターンを ADK にマッピングする

ADK は、カスタム ディスパッチ ループや状態ハンドラーを、宣言型クラスとグラフ ワークフローに置き換えます。移行中は、次のマッピングをガイドとして使用してください:

| 既存のパターン | ADK の同等機能 | 説明 |
| :--- | :--- | :--- |
| カスタム ツール スキーマまたはラッパー | ネイティブ Python 関数または `FunctionTool` | 型ヒントと docstring を持つ通常の Python 関数。ADK がツール宣言を自動的に導出します。 |
| カスタム エージェント ループまたはランナー | `Agent` | モデル、指示、ツール、サブエージェントを指定する宣言型エージェント定義。 |
| メモリと検索 | `BaseMemoryService` 実装と検索ツール | 組み込みメモリ サービス（`InMemoryMemoryService`、`VertexAiMemoryBankService`、`VertexAiRagMemoryService`）およびセッションやドキュメントのグラウンディング用検索ツール。 |
| 状態辞書またはスクラッチパッド | `ToolContext` を介した `session.state` | ツール、コールバック、エージェントの指示内からアクセス可能な共有ミュータブル セッション状態。 |
| マルチエージェント ワークフローとパイプライン | `google.adk.workflow.Workflow` | 条件付きルート、ループ、並列分岐を備えた明示的なグラフ ノード。 |
| マルチエージェント ハンドオフ | `Agent(sub_agents=[...])` | コーディネーター エージェントが特化したサブエージェントに委任する階層的委任。 |
| リモート エージェント間通信 | A2A プロトコル | Agent-to-Agent 標準を使用した HTTP 経由のエージェント間通信。 |

### 評価を伴うコード変換

信頼性の高い移行はテスト駆動型です。コーディング エージェントは、移行されたエージェントが元の実装と同じ結果を生成することを検証するために、新しい ADK コードとともに評価データセットとテスト スイートをセットアップできます。

1. **評価テストケースの設定:** コーディング エージェントに、既存のテストケースや記録された会話を `eval/` 配下の評価ケースに変換させます。
2. **ツールとエージェント ロジックの移植:** カスタム ディスパッチ ループとツール ラッパーを、型付けされた Python 関数および ADK の `Agent` または `Workflow` に置き換えます。

```python
# agent.py
from google.adk.agents import Agent
from google.adk.tools import ToolContext

def lookup_customer(customer_id: str) -> str:
    """Retrieve account tier and status for a customer."""
    return "Tier: Premium, Status: Active"

def calculate_discount(amount: float, rate: float = 0.1) -> float:
    """Calculate discounted total for a transaction."""
    return amount * (1.0 - rate)

root_agent = Agent(
    name="customer_support_agent",
    model="gemini-flash-latest",
    instruction="Assist customers with account inquiries and discounts using your tools.",
    tools=[lookup_customer, calculate_discount],
)
```

### 検証と評価

評価スイートを実行して、移行されたエージェントをベースライン テストケースと比較します:

```bash
agents-cli eval run
```

クエリを直接テストしたり、対話形式でテストしたりすることもできます:

```bash
# 単一のプロンプトをテスト
agents-cli run "Look up customer cust_101 and apply a 10% discount on $100."

# インタラクティブ Web UI を起動
agents-cli playground
```

## 次のステップ

* ADK のツール パターンの詳細については、[マルチツール エージェント チュートリアル](/tutorials/multi-tool-agent/)をご覧ください。
* マルチエージェントのルーティングと状態調整については、[グラフ ワークフロー](/graphs/)をご覧ください。
* [デプロイ ガイド](/deploy/)を使用してエージェントをデプロイします。
