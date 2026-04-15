---
catalog_title: Adspirer
catalog_description: Google、Meta、LinkedIn、TikTok Ads 全体で広告キャンペーンを作成、管理、最適化
catalog_icon: /integrations/assets/adspirer.png
catalog_tags: ["mcp", "connectors"]
---

# ADK 向け Adspirer MCP ツール

<div class="language-support-tag">
  <span class="lst-supported">ADK でサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[Adspirer MCP Server](https://github.com/amekala/ads-mcp) は ADK エージェントを
[Adspirer](https://www.adspirer.com/) に接続します。Adspirer は Google Ads、
Meta Ads、LinkedIn Ads、TikTok Ads にまたがる 100 以上のツールを備えた
AI 広告プラットフォームです。この統合により、キーワード調査やオーディエンス設計から
キャンペーンの立ち上げ、パフォーマンス分析まで、自然言語で広告キャンペーンを
作成、管理、最適化できるようになります。

## 仕組み

Adspirer は ADK エージェントと広告プラットフォームの間を橋渡しするリモート MCP サーバーです。
エージェントは Adspirer の MCP エンドポイントに接続し、OAuth 2.1 で認証したうえで、
広告プラットフォーム API に直接対応する 100 以上のツールへアクセスします。

一般的なワークフローは次のとおりです。

1. **接続**: ADK エージェントが `https://mcp.adspirer.com/mcp` に接続し、OAuth 2.1 で認証します。初回実行時にはブラウザが開き、ログインして広告アカウントへのアクセスを承認します。
2. **発見**: 接続済みの広告プラットフォーム (Google Ads、Meta Ads、LinkedIn Ads、TikTok Ads) に応じて、利用可能なツールをエージェントが検出します。
3. **実行**: これでエージェントは、キーワード調査、オーディエンス設計、キャンペーン作成、成果分析、予算最適化、広告管理まで、キャンペーンのライフサイクル全体を自然言語で実行できます。

Adspirer は OAuth トークン管理、広告プラットフォーム API 呼び出し、安全ガードレール
(たとえばキャンペーン削除の禁止や既存予算の変更制限) を担うため、組み込みの保護付きで
エージェントを自律的に動かせます。

## ユースケース

- **キャンペーン作成**: 自然言語で Google、Meta、LinkedIn、TikTok にまたがる複雑な広告キャンペーンを立ち上げられます。ダッシュボードを直接操作せずに、Search、Performance Max、YouTube、Demand Gen、画像、動画、カルーセルの各キャンペーンを作成できます。
- **パフォーマンス分析**: 接続済みのすべての広告プラットフォームのキャンペーン指標を分析できます。"どのキャンペーンの ROAS が最も高いか"、"どこで予算を無駄にしているか" といった質問に対し、最適化提案付きで答えられます。
- **キーワード調査と計画**: Google Keyword Planner の実 CPC、検索ボリューム、競合データを使ってキーワード調査ができます。キーワード戦略を作成し、そのままキャンペーンへ追加できます。
- **予算最適化**: 成果の低いキャンペーンを特定し、予算の非効率を検知し、チャネル横断・キャンペーン横断での支出配分に関する AI ベースの提案を得られます。
- **広告管理**: 既存キャンペーンに新しい広告グループ、広告セット、広告を追加できます。クリエイティブの A/B テスト、広告文の更新、キーワード管理、キャンペーンの一時停止や再開もエージェント経由で行えます。

## 前提条件

- [Adspirer](https://www.adspirer.com/) アカウントが必要です (無料プランあり)
- 少なくとも 1 つの広告プラットフォーム (Google Ads、Meta Ads、LinkedIn Ads、TikTok Ads) が接続されている必要があります。登録後に Adspirer ダッシュボードから接続できます
- 手順の詳細は [Quickstart guide](https://www.adspirer.com/docs/quickstart) を参照してください

## エージェントと一緒に使う

=== "Python"

    === "Local MCP Server"

        エージェントを初めて実行すると、OAuth アクセスを求めるブラウザウィンドウが自動的に開きます。ブラウザで承認すると、接続済みの広告アカウントにエージェントがアクセスできるようになります。

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="advertising_agent",
            instruction=(
                "You are an advertising agent that helps users create, manage, "
                "and optimize ad campaigns across Google Ads, Meta Ads, "
                "LinkedIn Ads, and TikTok Ads."
            ),
            tools=[
                McpToolset(
                    connection_params=StdioConnectionParams(
                        server_params=StdioServerParameters(
                            command="npx",
                            args=[
                                "-y",
                                "mcp-remote",
                                "https://mcp.adspirer.com/mcp",
                            ],
                        ),
                        timeout=30,
                    ),
                )
            ],
        )
        ```

    === "Remote MCP Server"

        すでに Adspirer のアクセストークンがある場合は、OAuth のブラウザフローなしで Streamable HTTP を使って直接接続できます。

        ```python
        from google.adk.agents import Agent
        from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

        ADSPIRER_ACCESS_TOKEN = "YOUR_ADSPIRER_ACCESS_TOKEN"

        root_agent = Agent(
            model="gemini-2.5-pro",
            name="advertising_agent",
            instruction=(
                "You are an advertising agent that helps users create, manage, "
                "and optimize ad campaigns across Google Ads, Meta Ads, "
                "LinkedIn Ads, and TikTok Ads."
            ),
            tools=[
                McpToolset(
                    connection_params=StreamableHTTPConnectionParams(
                        url="https://mcp.adspirer.com/mcp",
                        headers={
                            "Authorization": f"Bearer {ADSPIRER_ACCESS_TOKEN}",
                        },
                    ),
                )
            ],
        )
        ```

=== "TypeScript"

    === "Local MCP Server"

        エージェントを初めて実行すると、OAuth アクセスを求めるブラウザウィンドウが自動的に開きます。ブラウザで承認すると、接続済みの広告アカウントにエージェントがアクセスできるようになります。

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "advertising_agent",
            instruction:
                "You are an advertising agent that helps users create, manage, " +
                "and optimize ad campaigns across Google Ads, Meta Ads, " +
                "LinkedIn Ads, and TikTok Ads.",
            tools: [
                new MCPToolset({
                    type: "StdioConnectionParams",
                    serverParams: {
                        command: "npx",
                        args: [
                            "-y",
                            "mcp-remote",
                            "https://mcp.adspirer.com/mcp",
                        ],
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

    === "Remote MCP Server"

        すでに Adspirer のアクセストークンがある場合は、OAuth のブラウザフローなしで Streamable HTTP を使って直接接続できます。

        ```typescript
        import { LlmAgent, MCPToolset } from "@google/adk";

        const ADSPIRER_ACCESS_TOKEN = "YOUR_ADSPIRER_ACCESS_TOKEN";

        const rootAgent = new LlmAgent({
            model: "gemini-2.5-pro",
            name: "advertising_agent",
            instruction:
                "You are an advertising agent that helps users create, manage, " +
                "and optimize ad campaigns across Google Ads, Meta Ads, " +
                "LinkedIn Ads, and TikTok Ads.",
            tools: [
                new MCPToolset({
                    type: "StreamableHTTPConnectionParams",
                    url: "https://mcp.adspirer.com/mcp",
                    transportOptions: {
                        requestInit: {
                            headers: {
                                Authorization: `Bearer ${ADSPIRER_ACCESS_TOKEN}`,
                            },
                        },
                    },
                }),
            ],
        });

        export { rootAgent };
        ```

## 機能

Adspirer は、4 つの主要な広告プラットフォーム全体で広告キャンペーンのライフサイクル全体を管理するための 100 以上の MCP ツールを提供します。

機能 | 説明
---------- | -----------
キャンペーン作成 | Search、PMax、YouTube、Demand Gen、画像、動画、カルーセルの各キャンペーンを開始
パフォーマンス分析 | 指標分析、異常検知、最適化提案の取得
キーワード調査 | 実 CPC、検索ボリューム、競合データを使ったキーワード調査
予算最適化 | AI ベースの予算配分と無駄な支出の検知
広告管理 | 広告、広告グループ、広告セット、見出し、説明文の作成と更新
オーディエンスターゲティング | 興味関心、行動、役職、カスタムオーディエンスの検索
アセット管理 | 既存クリエイティブアセットの検証、アップロード、検索
キャンペーン制御 | 一時停止、再開、入札、予算、ターゲティング設定の更新

## 対応プラットフォーム

プラットフォーム | ツール数 | 機能
-------- | ----- | ------------
Google Ads | 49 | Search、PMax、YouTube、Demand Gen キャンペーン、キーワード調査、広告表示オプション、オーディエンスシグナル
Meta Ads | 30+ | 画像、動画、カルーセル、DCO キャンペーン、ピクセルトラッキング、リードフォーム、オーディエンスインサイト
LinkedIn Ads | 28 | スポンサードコンテンツ、リード獲得、会話型広告、デモグラフィックターゲティング、エンゲージメント分析
TikTok Ads | 4 | キャンペーン管理とパフォーマンス分析

## 追加リソース

- [Adspirer Website](https://www.adspirer.com/)
- [Adspirer MCP Server on GitHub](https://github.com/amekala/ads-mcp)
- [Quickstart Guide](https://www.adspirer.com/docs/quickstart)
- [Tool Catalog](https://www.adspirer.com/docs/agent-skills/tools)
- [Core Workflows](https://www.adspirer.com/docs/agent-skills/workflows)
- [Ad Platform Guides](https://www.adspirer.com/docs)
