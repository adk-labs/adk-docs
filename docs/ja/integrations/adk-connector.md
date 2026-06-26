---
catalog_title: ADK Connector
catalog_description: デバイス間のセッション同期をサポートし、一般的なメッセージングチャネルに ADK エージェントをチャットボットとして公開します
catalog_icon: /integrations/assets/adk-connector.png
catalog_tags: ["connectors"]
---

# ADK Connector

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span><span class="lst-typescript">TypeScript</span>
</div>

[ADK Connector](https://github.com/Harshk133/adk-connector)は、任意の ADK エージェントをラッピングし、Telegram や Discord などの一般的なメッセージングチャネルにチャットボットとして公開できるプラグアンドプレイ의 ツールキットです。現在サポートされているチャネルの完全なリストについては、プロジェクトリポジトリを参照してください。

数行のコードを追加するだけで、ローカル開発、テスト環境と実際のプロダクションメッセージングプラットフォームの間のギャップを埋めることができ、データベースベースのデバイス間セッション同期をネイティブにサポートします。

## 主なユースケース

- **マルチチャネルデプロイ (Multi-Channel Deployment)**: サポートされているメッセージングチャネル（Telegram、Discord など）に、Python または JavaScript/TypeScript で記述された ADK エージェントをチャットボットとして即座にデプロイできます。
- **デバイス間のセッション同期 (Cross-Device Session Synchronization)**: 会話をシームレスに切り替えることができます。Telegram や Discord でのチャット履歴を、ローカルの ADK Web UI (`adk web`) 内でそのまま確認、デバッグし、会話を継続できます。
- **弾力的な状態管理 (Resilient State Management)**: セッション状態、ツール呼び出し、ユーザーのインタラクションを記録するための非同期 SQLite バックエンドを自動的に構成します。
- **堅牢なマルチエージェントワークフロー (Robust Multi-Agent Workflows)**: 二重インポート（double-import）防止セーフティと、親およびサブエージェント間でのプロンプトコンテキスト変数の自動解決を提供します。

## 前提条件

- Python 3.10+ または Node.js 18+
- Gemini API キー（`GOOGLE_API_KEY` として設定）
- メッセージングチャネルの認証情報:
    - **Telegram**: Telegram アカウントと BotFather からの Bot トークン
    - **Discord**: Discord 開発者アカウント、Discord Bot トークン、およびクライアント ID

## インストール

ADK プロジェクトに応じて、Python または JavaScript / TypeScript 用のコネクタをインストールできます。

=== "Python"

    ```bash
    pip install adk-connector
    ```

    データベースベースのデバイス間セッション同期（例: `adk web` UI）を有効にするには、ADK DB コンポーネントもインストールします:

    ```bash
    pip install "google-adk[db]"
    ```

=== "JavaScript / TypeScript"

    ```bash
    npm install adk-connector-js
    ```

## エージェントでの使用

既存の Google ADK エージェントをラップしてメッセージングチャネルで起動する方法は次のとおりです。

=== "Python (Telegram)"

    ```python
    import os
    from dotenv import load_dotenv
    from google.adk.agents.llm_agent import Agent
    from adk_connectors.telegram import TelegramConnector

    # 環境変数をロード
    load_dotenv()

    # 1. 標準の Google ADK エージェントを定義
    assistant = Agent(
        model='gemini-flash-latest',
        name='my_assistant',
        instruction='You are a helpful assistant.'
    )

    if __name__ == "__main__":
        # 2. Telegram Bot トークンを取得
        token = os.getenv("TELEGRAM_BOT_TOKEN")

        # 3. コネクタをバインド
        connector = TelegramConnector(
            token=token,
            agent=assistant
        )

        # 4. ポーリングを開始
        connector.start()
    ```

=== "Python (Discord)"

    ```python
    import os
    from dotenv import load_dotenv
    from google.adk.agents.llm_agent import Agent
    from adk_connectors.discord import DiscordConnector

    # 환경변수 로드
    load_dotenv()

    # 1. 標準の Google ADK エージェントを定義
    assistant = Agent(
        model='gemini-flash-latest',
        name='my_assistant',
        instruction='You are a helpful assistant.'
    )

    if __name__ == "__main__":
        # 2. Discord Bot トークンを取得
        token = os.getenv("DISCORD_BOT_TOKEN")

        # 3. コネクタをバインド
        connector = DiscordConnector(
            token=token,
            agent=assistant
        )

        # 4. ボットを起動します！
        connector.start()
    ```

=== "JavaScript / TypeScript (Telegram)"

    ```typescript
    import { LlmAgent } from '@google/adk';
    import { TelegramConnector } from 'adk-connector-js';
    import dotenv from 'dotenv';

    dotenv.config();

    // 1. 標準の Google ADK エージェントを定義
    export const rootAgent = new LlmAgent({
      name: 'my_assistant',
      model: 'gemini-flash-latest',
      instruction: 'You are a helpful assistant.'
    });

    // 2. スクリプトのエントリーポイントで Telegram コネクタを起動
    if (import.meta.url === `file://${process.argv[1]}` || process.argv[1]?.endsWith('agent.ts')) {
      const connector = new TelegramConnector({
        token: process.env.TELEGRAM_BOT_TOKEN!,
        agent: rootAgent
      });

      connector.start();
    }
    ```

## adk webとのセッション同期

Python セットアップの場合、プロバイダー固有のユーザー ID をローカル開発環境にマッピングすることで、Telegram または Discord のチャット履歴をローカルの ADK Web UI と直接同期できます。

1. コード内で `session_management_across_device=True` を設定し、ユーザー ID を渡します。

    === "Telegram"

        ```python
        connector = TelegramConnector(
            token=token,
            agent=assistant,
            session_management_across_device=True,  # DBの起動とマッピングの永続化
            dev_user_id=os.getenv("TELEGRAM_USER_ID") # このIDをWeb UIの "user" ネームスペースに同期します
        )
        ```

    === "Discord"

        ```python
        connector = DiscordConnector(
            token=token,
            agent=assistant,
            session_management_across_device=True,  # DBの起動とマッピングの永続化
            dev_user_id=os.getenv("DISCORD_USER_ID")  # このIDをWeb UIの "user" ネームスペースに同期します
        )
        ```

2. ボットスクリプトを実行します:
   ```bash
   python agent.py
   ```
3. 別のターミナルで ADK Web UI を実行します:
   ```bash
   adk web .
   ```
4. `http://127.0.0.1:8000` にアクセスして、アクティブな会話とツール実行ログをブラウザで直接確認します。

## 追加のリソース

- [ADK Connector GitHub リポジトリ](https://github.com/Harshk133/adk-connector)
- [ADK Connector Python パッケージ (PyPI)](https://pypi.org/project/adk-connector/)
- [ADK Connector JS/TS パッケージ (NPM)](https://www.npmjs.com/package/adk-connector-js)
