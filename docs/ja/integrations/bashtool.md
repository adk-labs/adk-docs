---
catalog_title: Bash Tool
catalog_description: セキュアでリソースが制限されたローカルサンドボックス内でBashコマンドを実行する
catalog_icon: /integrations/assets/bash.png
catalog_tags: ["code", "google"]
---

# ADK用 Bash ツール

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.27.0</span>
</div>

`ExecuteBashTool` を使用すると、ADK エージェントがローカル ワークスペース ディレクトリ内で Bash コマンドを実行できるようになります。このツールは、ファイル システムの操作、スクリプトの実行、またはエージェントを通じてローカル環境と直接相互作用するのに役立ちます。
このツールは Python ADK でのみ利用可能です。

## インストール

Bash ツールは、コアの Agent Development Kit (ADK) にデフォルトで含まれています。個別の統合パッケージをインストールする必要はなく、メイン ライブラリをインストールするだけです。

```bash
pip install google-adk
```

## エージェントでの使用

!!! warning "POSIX 専用"

    `ExecuteBashTool` は現在、Linux や macOS などの **POSIX システムでのみサポート** されています。Windows システムでこのツールを実行するとハードエラーが発生します。

Bash ツールを使用するには、`ExecuteBashTool` をインスタンス化し、エージェントの `tools` リストに含めます。スニペットを実行する前に `my_workspace_path` が有効なディレクトリ パス文字列として定義されていることを確認してください。

```python
from google.adk.tools.bash_tool import ExecuteBashTool, BashToolPolicy

policy = BashToolPolicy(
    allowed_command_prefixes=("ls", "cat", "grep"),
    timeout_seconds=30,
    max_memory_bytes=1024 * 1024 * 512,   # 512MB
    max_file_size_bytes=1024 * 1024 * 10, # 10MB
    max_child_processes=5
)

tool = ExecuteBashTool(workspace=my_workspace_path, policy=policy)
```

## セキュリティと実行保護機能

任意のコードを実行することには固有のリスクが伴うため、`ExecuteBashTool` には生成されたサブプロセスに適用されるいくつかの必須およびオプションのセキュリティ機能が含まれています。

### デフォルトポリシーはすべてのコマンドを許可

デフォルトでは、`BashToolPolicy` は `allowed_command_prefixes=("*",)` で初期化されます。これは、**デフォルトですべてのコマンドが許可されている** ことを意味します。アプリケーションを保護するには、ポリシーを初期化するときに許可されるコマンドを明示的に制限する必要があります。

```python
# セキュアな実装例
from google.adk.tools.bash_tool import BashToolPolicy

strict_policy = BashToolPolicy(
    allowed_command_prefixes=("ls ", "cat ", "pwd")
)
```

### 組み込みの保護

1. **ユーザー確認:** ツールはコマンドを実行する前に **常に** ユーザー確認を要求します。フレームワークは実行を一時停止し、`adk_request_confirmation` フローを通じてユーザーまたはクライアント アプリケーションがコマンドを承認するまで待機します。
2. **コマンド検証:** `allowed_command_prefixes` を使用して特定のコマンドを許可リストに追加し、`blocked_operators` を使用して特定の文字列パターンを厳格に禁止できます。
3. **リソース制限:** フォークボムやメモリ枯渇を防ぐため、OS レベルの制限である `setrlimit` が適用され、メモリ消費量、ファイルサイズ、および子プロセスの数が制限されます。
4. **コアダンプの無効化:** 機密性の高いメモリリークを防ぐため、実行サブプロセスに対してコアダンプが厳格に無効化（`RLIMIT_CORE` が `0` に設定）されます。
5. **プロセスグループの終了:** コマンドが `timeout_seconds` を超えた場合、ツールはプロセスグループ全体に `SIGKILL` を発行し、孤立したバックグラウンドプロセスが残らないようにします。

## 利用可能なツール

| ツール名 | クラス名 | 説明 |
| :--- | :--- | :--- |
| `execute_bash` | `ExecuteBashTool` | ワークスペース内で Bash コマンドを実行します。POSIX 専用 |
