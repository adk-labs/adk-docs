---
catalog_title: Synap
catalog_description: ADK エージェントにセッション間をまたぐ長期永続メモリを追加します
catalog_icon: /integrations/assets/synap.png
catalog_tags: ["data"]
---

# ADK向けの Synap 連携

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python</span>
</div>

[`maximem-synap-google-adk`](https://pypi.org/project/maximem-synap-google-adk/) プラグインは、AI エージェント向けに管理された長期メモリレイヤーである [Synap](https://www.maximem.ai/synap) に ADK エージェントを接続します。Synap は会話から知識（事実、好み、エピソード、感情、および時間的イベント）を自動的に抽出して構造化し、現在のクエリに意味的に関連するもののみを取得します。

## 主なユースケース

- **セッションをまたぐ長期永続メモリ (Persistent cross-session memory)**: 手動で記録を保持することなく、セッションやデプロイを超えて維持される長期メモリを ADK エージェントに提供します。
- **マルチテナント分離 (Multi-tenant isolation)**: メモリのスコープは `user_id` と `customer_id` に設定されるため、マルチユーザー環境での厳密な分離を保証します。
- **セマンティックリコール (Semantic recall)**: サーバー側での抽出により、現在のクエリに関連するもののみが引き出され、プロンプトを短くし、トークン効率を高く保ちます。

## 前提条件

- [Synap](https://synap.maximem.ai) アカウントと API キー
- [Gemini API キー](https://aistudio.google.com/app/api-keys)（または ADK で構成されている他のモデルプロバイダ）

## インストール

```bash
pip install maximem-synap-google-adk maximem-synap
```

以下の環境変数を設定します:

```bash
export SYNAP_API_KEY="your-synap-api-key"
```

## エージェントでの使用

`create_synap_tools(...)` は、エージェントが必要に応じてメモリを呼び出したり保存したりするために呼び出すことができる、 `search_memory` と `store_memory` の 2 つ of `FunctionTool` インスタンスを返します。

```python
import os

from google.adk.agents.llm_agent import Agent
from maximem_synap import MaximemSynapSDK
from synap_google_adk import create_synap_tools

sdk = MaximemSynapSDK(api_key=os.environ["SYNAP_API_KEY"])

synap_tools = create_synap_tools(
    sdk=sdk,
    user_id="alice",
    customer_id="acme_corp",
)

root_agent = Agent(
    model="gemini-flash-latest",
    name="memory_assistant",
    instruction=(
        "あなたは長期メモリを持つ便利なアシスタントです。 "
        "search_memory を使用して、ユーザーについて知っていることを思い出します。 "
        "store_memory を使用して、ユーザーが言及した新しい重要な事実を保存します。"
    ),
    tools=synap_tools,
)
```

起動:

```bash
adk run path/to/your_agent
```

最初のターンでエージェントに何か（例： *「ピーナッツアレルギーがあります」*）を教え、後のターンでそれについて尋ねてみてください。別々の `adk run` 呼び出しの間であっても、Synap は関連するメモリを自動的に取得します。

## 利用可能なツール

| ツール | 説明 |
|------|-------------|
| `search_memory` | ユーザーの保存されたメモリに対するセマンティック検索。自然言語のクエリを受け取り、最も関連性の高い事実、好み、およびエピソードを返します。 |
| `store_memory` | ユーザーの長期メモリに明示的な事実を保存します。ユーザーが記憶する価値のあることを共有したときに、エージェントはこれを呼び出します。 |

## リソース

- [Synap ドキュメント](https://docs.maximem.ai)
- [ADK 連携ガイド](https://docs.maximem.ai/integrations/google-adk)
- [PyPI の `maximem-synap-google-adk`](https://pypi.org/project/maximem-synap-google-adk/)
- [オープンソース統合パッケージ](https://github.com/maximem-ai/maximem_synap_sdk/tree/main/packages/integrations/synap-google-adk)
- [Synap ダッシュボード](https://synap.maximem.ai)
