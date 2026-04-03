---
catalog_title: StackOne
catalog_description: エージェントを 200 以上の SaaS プロバイダに接続します
catalog_icon: /integrations/assets/stackone.png
catalog_tags: ["connectors"]
---

# ADK 向け StackOne プラグイン

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[StackOne ADK Plugin](https://github.com/StackOneHQ/stackone-adk-plugin) は、
ADK エージェントを [StackOne](https://stackone.com) の統合 AI 連携ゲートウェイを
通じて数百のプロバイダに接続します。各 API ごとにツール関数を手作業で定義する
代わりに、このプラグインは接続済みプロバイダから利用可能なツールを動的に検出し、
ADK のネイティブツールとして公開します。HRIS、ATS、CRM、生産性ツール、
スケジューリングツールなど、さらに多くの
[統合](https://www.stackone.com/connectors) をサポートします。

## ユースケース

- **営業・レベニューオペレーション:** CRM（例: HubSpot、Salesforce）で
  リードを探し、連絡先データを補強し、パーソナライズされたアウトリーチを
  下書きし、その活動を記録に戻すエージェントを 1 つの会話内で構築できます。

- **People Operations:** ATS（例: Greenhouse、Ashby）で候補者をスクリーニングし、
  カレンダーツール（例: Google Calendar、Calendly）で空き時間を確認し、
  面接評価を収集し、応募者をパイプラインの各段階に進め、HRIS（例: BambooHR、
  Workday）へのオンボーディングを自動化するエージェントを作成できます。
  従業員ライフサイクル全体を手作業なしでカバーできます。

- **マーケティング自動化:** CRM のオーディエンスセグメントをメールプラットフォーム
  （例: Mailchimp、Klaviyo）へ同期し、メールシーケンスをトリガーし、
  チャネル横断でエンゲージメント指標を報告するキャンペーンエージェントを
  構築できます。

- **プロダクトデリバリー:** サポートツール（例: Intercom、Zendesk、Slack）からの
  フィードバックをトリアージし、プロジェクト管理ツール（例: Linear、Jira）に
  Issue を作成して優先順位付けし、オブザーバビリティプラットフォーム
  （例: PagerDuty、Datadog）の知見を使ってインシデントを解決するエージェントを
  作れます。プロダクトリサーチ、デリバリー、信頼性を 1 つのワークフローに
  まとめられます。

## 前提条件

- 少なくとも 1 つのプロバイダが接続された [StackOne アカウント](https://app.stackone.com)
- [StackOne Dashboard](https://app.stackone.com) で取得した StackOne API キー
- [Gemini API キー](https://aistudio.google.com/apikey)

## インストール

```bash
pip install stackone-adk
```

または `uv` を使う場合:

```bash
uv add stackone-adk
```

## エージェントでの使用

!!! tip "環境変数"

    以下の例を実行する前に API キーを環境変数として設定してください。

    ```bash
    export STACKONE_API_KEY="your-stackone-api-key"
    export GOOGLE_API_KEY="your-google-api-key"
    ```

    `STACKONE_API_KEY` が設定されると、プラグインはそれを自動的に読み取り、
    接続済みアカウントを検出します。

=== "Python"

    === "App と一緒に使う（推奨）"

        ```python
        import asyncio

        from google.adk.agents import Agent
        from google.adk.apps import App
        from google.adk.runners import InMemoryRunner
        from stackone_adk import StackOnePlugin


        async def main():
            plugin = StackOnePlugin()
            # 特定のアカウントに絞ることもできます:
            # plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")

            tools = plugin.get_tools()
            print(f"Discovered {len(tools)} tools")

            agent = Agent(
                model="gemini-2.5-flash",
                name="scheduling_agent",
                description="Manages scheduling, HR, and CRM through StackOne.",
                instruction=(
                    "You are a helpful assistant powered by StackOne. "
                    "You help users manage their scheduling, HR, and CRM tasks "
                    "by using the available tools.\n\n"
                    "Always be helpful and provide clear, organized responses."
                ),
                tools=tools,
            )

            app = App(
                name="scheduling_app",
                root_agent=agent,
                plugins=[plugin],
            )

            async with InMemoryRunner(app=app) as runner:
                events = await runner.run_debug(
                    "Get my most recent scheduled meeting from Calendly.",
                    quiet=True,
                )
                # エージェントの最終テキスト応答を抽出
                for event in reversed(events):
                    if event.content and event.content.parts:
                        text_parts = [p.text for p in event.content.parts if p.text]
                        if text_parts:
                            print("".join(text_parts))
                            break


        asyncio.run(main())
        ```

    === "Runner を直接使う"

        ```python
        import asyncio

        from google.adk.agents import Agent
        from google.adk.runners import InMemoryRunner
        from stackone_adk import StackOnePlugin


        async def main():
            plugin = StackOnePlugin()
            # 特定のアカウントに絞ることもできます:
            # plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID")

            tools = plugin.get_tools()
            print(f"Discovered {len(tools)} tools")

            agent = Agent(
                model="gemini-2.5-flash",
                name="scheduling_agent",
                description="Manages scheduling, HR, and CRM through StackOne.",
                instruction=(
                    "You are a helpful assistant powered by StackOne. "
                    "You help users manage their scheduling, HR, and CRM tasks "
                    "by using the available tools.\n\n"
                    "Always be helpful and provide clear, organized responses."
                ),
                tools=tools,
            )

            async with InMemoryRunner(
                app_name="scheduling_app", agent=agent
            ) as runner:
                events = await runner.run_debug(
                    "Get my most recent scheduled meeting from Calendly.",
                    quiet=True,
                )
                # エージェントの最終テキスト応答を抽出
                for event in reversed(events):
                    if event.content and event.content.parts:
                        text_parts = [p.text for p in event.content.parts if p.text]
                        if text_parts:
                            print("".join(text_parts))
                            break


        asyncio.run(main())
        ```

## 利用可能なツール

固定のツールセットを持つ統合とは異なり、StackOne のツールは StackOne API を通じて
接続済みプロバイダから **動的に検出** されます。利用できるツールは
[StackOne Dashboard](https://app.stackone.com) に接続した SaaS プロバイダに
応じて変わります。

検出されたツールを一覧表示するには:

```python
plugin = StackOnePlugin(account_id="YOUR_ACCOUNT_ID") # 任意: 省略すると接続済みの全アカウントを使用
for tool in plugin.get_tools():
    print(f"{tool.name}: {tool.description}")
```

### サポートされる統合カテゴリ

Category | Example providers
-------- | -----------------
HRIS | HiBob, BambooHR, Workday, SAP SuccessFactors, Personio, Gusto
ATS | Greenhouse, Ashby, Lever, Bullhorn, SmartRecruiters, Teamtailor
CRM & Sales | Salesforce, HubSpot, Pipedrive, Zoho CRM, Close, Copper
Marketing | Mailchimp, Klaviyo, ActiveCampaign, Brevo, GetResponse
Ticketing & Support | Zendesk, Freshdesk, Jira, ServiceNow, PagerDuty, Linear
Productivity | Asana, ClickUp, Slack, Microsoft Teams, Notion, Confluence
Scheduling | Calendly, Cal.com
LMS & Learning | 360Learning, Docebo, Go1, Cornerstone, LinkedIn Learning
Commerce | Shopify, BigCommerce, WooCommerce, Etsy
Developer Tools | GitHub, GitLab, Twilio

200 以上のサポート対象プロバイダの完全な一覧は
[StackOne integrations page](https://www.stackone.com/connectors) を参照してください。

## 構成

### プラグインパラメータ

Parameter | Type | Default | Description
--------- | ---- | ------- | -----------
`api_key` | `str | None` | `None` | StackOne API キーです。`STACKONE_API_KEY` 環境変数にフォールバックします。
`account_id` | `str | None` | `None` | すべてのツールに適用する既定のアカウント ID です。
`base_url` | `str | None` | `None` | API URL を上書きします（デフォルト: `https://api.stackone.com`）。
`plugin_name` | `str` | `"stackone_plugin"` | ADK 用のプラグイン識別子です。
`providers` | `list[str] | None` | `None` | プロバイダ名でフィルタリングします（例: `["calendly", "hibob"]`）。
`actions` | `list[str] | None` | `None` | glob 構文を使ったアクションパターンでフィルタリングします。
`account_ids` | `list[str] | None` | `None` | 特定の接続済みアカウント ID にツールを限定します。

### ツールフィルタリング

プロバイダ、アクションパターン、アカウント ID、またはその組み合わせで
ツールをフィルタリングできます。

```python
# アカウントを指定
plugin = StackOnePlugin(account_ids=["acct-hibob-1", "acct-bamboohr-1"])

# 読み取り専用操作
plugin = StackOnePlugin(actions=["*_list_*", "*_get_*"])

# glob パターンを使った特定アクション
plugin = StackOnePlugin(actions=["calendly_list_events", "calendly_get_event_*"])

# 複合フィルタ
plugin = StackOnePlugin(
    actions=["*_list_*", "*_get_*"],
    account_ids=["acct-hibob-1"],
)
```

## 追加リソース

- [StackOne ADK Plugin Repository](https://github.com/StackOneHQ/stackone-adk-plugin)
- [StackOne Documentation](https://docs.stackone.com/)
- [StackOne Dashboard](https://app.stackone.com)
- [StackOne Python AI SDK](https://github.com/StackOneHQ/stackone-ai-python)
