---
catalog_title: Enterprise Web Search
catalog_description: ポリシーに準拠した Web 検索結果で ADK エージェントをグラウンディング
catalog_icon: /integrations/assets/enterprise-web-search.png
catalog_tags: ["google", "search"]
---

# ADK 用 Enterprise Web Search ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.9.0</span><span class="lst-typescript">TypeScript v1.5.0</span>
</div>

Google Cloud [Enterprise Web Search](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest/Shared.Types/EnterpriseWebSearch) は、企業のコンプライアンスとソース制御を維持しながら、Web からの情報で ADK エージェントをグラウンディングします。エンタープライズグレードのワークロード向けに設計されたこのツールは、グラウンディングデータが組織のセキュリティおよびコンプライアンスポリシーに準拠していることを保証します。

!!! note "Enterprise Web Search と Agent Search の違い"

    Enterprise Web Search は [Agent Search](https://adk.dev/ja/integrations/agent-search/) とは異なります。Agent Search がインデックス付きのプライベートデータストアをクエリするのに対し、Enterprise Web Search は準拠した公開 Web データを取得します。

!!! warning "サービス固有の利用規約"

    Enterprise Web Search ツールを使用する場合、UI に検索候補および必要な Google ロゴを適切に表示することを含む、Google のサービス固有の利用規約を遵守する義務があります。

## ユースケース (Use cases)

- **エンタープライズグラウンディング (Enterprise Grounding)**: 組織のコンプライアンス基準を維持しながら、最新の Web 情報をエージェントに提供します。
- **制御された Web アクセス (Controlled Web Access)**: リサーチ、マーケットインテリジェンス、またはカスタマーサポートのタスクにおいて、エージェントが信頼できる Web ソースをクエリすることを保証します。
- **規制対象ワークフロー (Regulated Workflows)**: 厳格な監査可能性とデータガバナンスが必要な環境にグラウンディング機能をデプロイします。

## 前提条件 (Prerequisites)

- Agent Search が有効になっている Google Cloud Platform へのアクセス権。
- Gemini モデルに必要な権限が構成された GCP プロジェクト。
- 環境変数 `GOOGLE_GENAI_USE_ENTERPRISE=TRUE` が設定されている必要があります。
- `google-adk` パッケージ（Python）または `@google/adk` パッケージ（TypeScript）がインストールされていること：

=== "Python"

    ```bash
    pip install google-adk
    ```

=== "TypeScript"

    ```bash
    npm install @google/adk
    ```

## エージェントでの使用

次の例は、事前にインスタンス化された `enterprise_web_search` ツールを使用して ADK エージェントを構成する方法を示しています。

=== "Python"

    ```python
    from google.adk.agents import Agent
    from google.adk.tools import enterprise_web_search

    root_agent = Agent(
        model="gemini-flash-latest",
        name="enterprise_search_agent",
        instruction="Answer user questions accurately using enterprise-compliant web search results.",
        tools=[enterprise_web_search],
    )
    ```

=== "TypeScript"

    ```typescript
    import { LlmAgent, ENTERPRISE_WEB_SEARCH } from "@google/adk";

    const rootAgent = new LlmAgent({
      model: "gemini-flash-latest",
      name: "enterprise_search_agent",
      instruction: "Answer user questions accurately using enterprise-compliant web search results.",
      tools: [ENTERPRISE_WEB_SEARCH],
    });

    export { rootAgent };
    ```

## 選択ガイドライン (Selection guidance)

- 任意の Gemini モデルにおいて広範な Web カバーレージを必要とする汎用アプリケーションには、標準の Google Search を使用します。
- コンプライアンス制御、ソース監査、Gemini 2+ モデルへのデプロイが必須であるエンタープライズエージェントを構築する場合は、Enterprise Web Search を使用します。

## 追加リソース

- [Agent Search Web Grounding Overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/grounding/web-grounding-enterprise)
