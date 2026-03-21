# エージェントワークフローのための人間入力

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v2.0.0</span><span class="lst-preview">Alpha</span>
</div>

データ入力、意思決定の検証、またはアクション許可のために人間の入力を
要求できることは、多くのエージェント駆動ワークフローで重要な要素です。
ADK のグラフベースワークフローには、ワークフローの一部として人間から入力を
得るために特別に設計された Human in the Loop (HITL) ノードを含めることが
できます。これらのノードは実行に人工知能 (AI) モデルを必要としないため、
入力プロセスをより予測可能で信頼性の高いものにできます。

!!! example "Alpha リリース"

    ADK 2.0 は Alpha リリースであり、以前の ADK バージョンと併用する際に
    互換性を壊す変更が発生する可能性があります。プロダクション環境のように
    後方互換性が必要な場合は ADK 2.0 を使用しないでください。このリリースを
    ぜひ試していただき、
    [フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)
    をお寄せください。

## はじめに

***RequestInput*** クラスと、ユーザーに提示するテキストプロンプトを使うと、
グラフ内に人間入力ノードを実装できます。次のコード例は、Workflow グラフへ
人間入力ノードを追加する方法を示します。

```python
from google.adk.events import RequestInput
from google.adk import Workflow

def step1(): # Human input step
  yield RequestInput(message="Enter a number:")

def step2(node_input):
  return node_input * 2

root_agent = Workflow(
    name="root_agent",
    edges=[('START', step1, step2)],
)
```

このコード例では、`step1` がユーザーからの入力をシステムが受け取るまで
エージェントの実行を一時停止します。システムがユーザー入力を受け取ると、
その入力は次のノードへ渡されます。

## 設定オプション

人間入力ノードでは、***RequestInput*** クラスとともに次の設定オプションを
使用できます。

- **`message`:** 人間入力の要求内容を説明するためにユーザーへ提示される
  テキストです。
- **`payload`:** 人間入力リクエストの一部として利用する構造化データです。
- **`response_schema`:** 人間の応答が従う必要のあるデータ構造です。

!!! note "注: response schema 入力の制限"

    **response_schema** 設定について、***RequestInput*** クラスは人間の応答を
    指定されたデータ構造に自動で再整形しません。人間の応答は指定された形式で
    直接提供される必要があります。より良いユーザー体験のためには、構造化
    データを収集するユーザーインターフェースを提供するか、非構造化データを
    必要な形式へ整える Agent ノードの利用を検討してください。

## 人間入力の例

次のコード例は、***message***、***payload***、***response schema***
パラメータを含む、より詳細な人間入力リクエストを示します。

### response schema 付きで入力を要求する

次のコードサンプルは、ワークフローノード内で ***response schema*** を含む
***RequestInput*** オブジェクトを構築する方法を示します。

```python
async def initial_prompt(ctx: Context):
   """Ask the user for itinerary information"""
   input_message = """
       This is an interactive concierge workflow tasked with making you a great
       itinerary for you in your city of choice. If you give some details about
       yourself or what you are generally looking for I can better personalize
       your itinerary.
       For example, input your:
           City (Required),
           Age,
           Hobby,
           Example of attraction you liked
   """
   resp = {"user_response": str}

   yield RequestInput(message=input_message, response_schema=resp)
```

### データ payload 付きで入力を要求する

次のコードサンプルは、ワークフローノード内で ***payload*** と
***response schema*** を含む ***RequestInput*** オブジェクトを構築する方法を
示します。この例では、`ActivitiesList` はアクティビティの一覧を構成する
エージェントノードによって完成されることを想定しており、
`get_user_feedback()` ノードがユーザーにフィードバックを求めます。

```python
class ActivitiesList(BaseModel):
   """Itinerary should be a list of dictionaries for each activity. Each
   activity has a name and a description"""
   itinerary: List[Dict[str, str]]

async def get_user_feedback(node_input: ActivitiesList):
   """
   Retrieves the user's thoughts on the agents initial itinerary in order to
   either expand on, change the list, or exit the loop
   """
   message = (
       f"""
       Here is your recommended base itinerary:\n{node_input}\n\n
       Which of these items appeal to you (if any)?
       """
   )

   yield RequestInput(
       message=message,
       payload=node_input,
       response_schema={"user":"response"}
   )
```
