---
catalog_title: Reflect and Retry Plugin
catalog_description: 失敗したツール呼び出しを自動で再試行します
catalog_icon: /adk-docs/integrations/assets/adk.png
catalog_tags: ["google"]
---
# リフレクトおよび再試行ツールプラグイン

<div class="language-support-tag">
    <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.16.0</span>
</div>

リフレクトおよび再試行ツールプラグインは、エージェントがADK[ツール](/adk-docs/ja/tools-custom/)からのエラー応答から回復し、ツールリクエストを自動的に再試行するのに役立ちます。このプラグインは、ツールの障害を傍受し、リフレクションと修正のためにAIモデルに構造化されたガイダンスを提供し、構成可能な制限まで操作を再試行します。このプラグインは、次の機能を含む、エージェントワークフローに回復性を高めるのに役立ちます。

*   **同時実行セーフ**: ロックを使用して、並列ツール実行を安全に処理します。
*   **構成可能なスコープ**: 呼び出しごと（デフォルト）またはグローバルに障害を追跡します。
*   **詳細な追跡**: 障害数はツールごとに追跡されます。
*   **カスタムエラー抽出**: 通常のツール応答でのエラー検出をサポートします。

## リフレクトおよび再試行プラグインの追加

以下に示すように、ADKプロジェクトのAppオブジェクトのプラグイン設定にこのプラグインを追加して、ADKワークフローに追加します。

```python
from google.adk.apps.app import App
from google.adk.plugins import ReflectAndRetryToolPlugin

app = App(
    name="my_app",
    root_agent=root_agent,
    plugins=[
        ReflectAndRetryToolPlugin(max_retries=3),
    ],
)
```

この構成では、エージェントによって呼び出されたツールがエラーを返した場合、リクエストが更新され、ツールごとに最大3回まで再試行されます。

## 構成設定

リフレクトおよび再試行プラグインには、次の構成オプションがあります。

*   **`max_retries`**: （オプション）システムがエラー以外の応答を受信するために行う追加の試行の合計数。デフォルト値は3です。
*   **`throw_exception_if_retry_exceeded`**: （オプション）`False`に設定すると、最後の再試行が失敗してもシステムはエラーを発生させません。デフォルト値は`True`です。
*   **`tracking_scope`**: （オプション）
    *   **`TrackingScope.INVOCATION`**: 単一の呼び出しとユーザー全体のツールの障害を追跡します。この値はデフォルトです。
    *   **`TrackingScope.GLOBAL`**: すべての呼び出しとすべてのユーザー全体のツールの障害を追跡します。

### 高度な構成

`ReflectAndRetryToolPlugin`クラスを拡張することで、このプラグインの動作をさらに変更できます。次のコードサンプルは、エラーステータスの応答を選択することによる動作の単純な拡張を示しています。

```python
class CustomRetryPlugin(ReflectAndRetryToolPlugin):
  async def extract_error_from_result(self, *, tool, tool_args,tool_context,
  result):
    # 応答コンテンツに基づいてエラーを検出する
    if result.get('status') == 'error':
        return result
    return None  # エラーは検出されませんでした

# この変更されたプラグインをAppオブジェクトに追加します。
error_handling_plugin = CustomRetryPlugin(max_retries=5)
```

## 次のステップ

リフレクトおよび再試行プラグインを使用した完全なコードサンプルについては、以下を参照してください。

*   [基本](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_reflect_tool_retry/basic)コードサンプル
*   [幻覚関数名](https://github.com/google/adk-python/tree/main/contributing/samples/plugin_reflect_tool_retry/hallucinating_func_name)コードサンプル
