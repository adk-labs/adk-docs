---
catalog_title: Daytona
catalog_description: 安全なサンドボックスでコード実行、シェル実行、ファイル管理を行います
catalog_icon: /adk-docs/integrations/assets/daytona.png
catalog_tags: ["code"]
---

# ADK 向け Daytona プラグイン

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python</span>
</div>

[Daytona ADK plugin](https://github.com/daytonaio/daytona-adk-plugin) は ADK
エージェントを [Daytona](https://www.daytona.io/) サンドボックスへ接続します。
この連携により、エージェントは隔離環境でコード実行、シェルコマンド実行、
ファイル管理を行え、AI 生成コードを安全に実行できます。

## ユースケース

- **安全なコード実行**: ローカル環境へリスクを与えず、隔離サンドボックスで
  Python、JavaScript、TypeScript コードを実行します。

- **シェルコマンド自動化**: ビルド、インストール、システム操作のために
  タイムアウトや作業ディレクトリを設定してシェルコマンドを実行します。

- **ファイル管理**: スクリプトやデータセットをサンドボックスへアップロードし、
  生成物や結果を取得します。

## 前提条件

- [Daytona](https://www.daytona.io/) アカウント
- Daytona API キー

## インストール

```bash
pip install daytona-adk
```

## エージェントで使う

```python
from daytona_adk import DaytonaPlugin
from google.adk.agents import Agent

plugin = DaytonaPlugin(
  api_key="your-daytona-api-key" # Or set DAYTONA_API_KEY environment variable
)

root_agent = Agent(
    model="gemini-2.5-pro",
    name="sandbox_agent",
    instruction="Help users execute code and commands in a secure sandbox",
    tools=plugin.get_tools(),
)
```

## 利用可能なツール

Tool | Description
---- | -----------
`execute_code_in_daytona` | Python、JavaScript、TypeScript コードを実行
`execute_command_in_daytona` | シェルコマンドを実行
`upload_file_to_daytona` | スクリプト/データファイルをサンドボックスへアップロード
`read_file_from_daytona` | スクリプト出力や生成ファイルを読み取り
`start_long_running_command_daytona` | バックグラウンドプロセス (サーバー、watcher) を開始

## Learn more

安全なサンドボックスでコードを作成・テスト・検証するコード生成エージェントの詳細は
[このガイド](https://www.daytona.io/docs/en/google-adk-code-generator) を参照してください。

## 追加リソース

- [Code Generator Agent Guide](https://www.daytona.io/docs/en/google-adk-code-generator)
- [Daytona ADK on PyPI](https://pypi.org/project/daytona-adk/)
- [Daytona ADK on GitHub](https://github.com/daytonaio/daytona-adk-plugin)
- [Daytona Documentation](https://www.daytona.io/docs)
