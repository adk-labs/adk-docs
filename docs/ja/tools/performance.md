---
hide:
  - toc
---
# 並列実行によるツールパフォーマンスの向上

<div class="language-support-tag">
  <span class="lst-supported">ADKでサポート</span><span class="lst-python">Python v1.10.0</span>
</div>

Python向けAgent Development Kit（ADK）バージョン1.10.0以降、フレームワークはエージェントが要求した[関数ツール](/adk-docs/tools/function-tools/)を並列で実行しようとします。この動作により、特に複数の外部APIや長時間実行タスクに依存するエージェントのパフォーマンスと応答性が大幅に向上します。たとえば、それぞれ2秒かかる3つのツールがある場合、それらを並列で実行すると、合計実行時間は6秒ではなく2秒に近くなります。ツール関数を並列で実行する機能は、特に次のシナリオでエージェントのパフォーマンスを向上させることができます。

-   **調査タスク:** エージェントがワークフローの次の段階に進む前に、複数のソースから情報を収集する場合。
-   **API呼び出し:** エージェントが複数の航空会社のAPIを使用して利用可能なフライトを検索するなど、複数のAPIに個別にアクセスする場合。
-   **公開および通信タスク:** エージェントが複数の独立したチャネルまたは複数の受信者を介して公開または通信する必要がある場合。

ただし、このパフォーマンス向上を有効にするには、カスタムツールが非同期実行をサポートして構築されている必要があります。このガイドでは、ADKで並列ツール実行がどのように機能するか、およびこの処理機能を最大限に活用するためにツールを構築する方法について説明します。

!!! warning
    ツール関数呼び出しのセットで同期処理を使用するADKツールは、他のツールが並列実行を許可している場合でも、他のツールが並列で実行されるのをブロックします。

## 並列対応ツールの構築

ツール関数を非同期関数として定義することで、並列実行を有効にします。Pythonコードでは、これは`async def`および`await`構文を使用することを意味し、これによりADKは`asyncio`イベントループでそれらを同時に実行できます。次のセクションでは、並列処理および非同期操作用に構築されたエージェントツールの例を示します。

### http Web呼び出しの例

次のコード例は、`get_weather()`関数を非同期で動作させ、並列実行を可能にするように変更する方法を示しています。

```python
 async def get_weather(city: str) -> dict:
      async with aiohttp.ClientSession() as session:
          async with session.get(f"http://api.weather.com/{city}") as response:
              return await response.json()
```

### データベース呼び出しの例

次のコード例は、データベース呼び出し関数を非同期で動作するように記述する方法を示しています。

```python
async def query_database(query: str) -> list:
      async with asyncpg.connect("postgresql://...") as conn:
          return await conn.fetch(query)
```

### 長いループの譲歩動作の例

ツールが複数のリクエストまたは多数の長時間実行リクエストを処理している場合は、次のコードサンプルに示すように、他のツールが実行できるように譲歩コードを追加することを検討してください。

```python
async def process_data(data: list) -> dict:
      results = []
      for i, item in enumerate(data):
          processed = await process_item(item)  # 譲歩ポイント
          results.append(processed)

          # 長いループの定期的な譲歩ポイントを追加
          if i % 100 == 0:
              await asyncio.sleep(0)  # 制御を譲る
      return {"results": results}
```

!!! tip "重要"
    他の関数の実行をブロックしないように、一時停止には`asyncio.sleep()`関数を使用してください。

### 集中的な操作のためのスレッドプールの例

処理集約的な関数を実行する場合は、次の例に示すように、利用可能なコンピューティングリソースをより適切に管理するためにスレッドプールを作成することを検討してください。

```python
async def cpu_intensive_tool(data: list) -> dict:
      loop = asyncio.get_event_loop()

      # CPUバウンド作業にスレッドプールを使用
      with ThreadPoolExecutor() as executor:
          result = await loop.run_in_executor(
              executor,
              expensive_computation,
              data
          )
      return {"result": result}
```

### プロセスチャンキングの例

長いリストまたは大量のデータに対してプロセスを実行する場合は、次の例に示すように、スレッドプール手法とデータチャンクへの処理の分割を組み合わせ、チャンク間で処理時間を譲ることを検討してください。

```python
 async def process_large_dataset(dataset: list) -> dict:
      results = []
      chunk_size = 1000

      for i in range(0, len(dataset), chunk_size):
          chunk = dataset[i:i + chunk_size]

          # スレッドプールでチャンクを処理
          loop = asyncio.get_event_loop()
          with ThreadPoolExecutor() as executor:
              chunk_result = await loop.run_in_executor(
                  executor, process_chunk, chunk
              )

          results.extend(chunk_result)

          # チャンク間で制御を譲る
          await asyncio.sleep(0)

      return {"total_processed": len(results), "results": results}
```

## 並列対応のプロンプトとツールの説明の作成

AIモデルのプロンプトを作成する場合は、関数呼び出しを並列で実行するように明示的に指定またはヒントを与えることを検討してください。次のAIプロンプトの例では、モデルにツールを並列で使用するように指示しています。

```none
ユーザーが複数の情報を要求した場合は、常に関数を並列で呼び出します。

  例：
  - 「ロンドンの天気とUSDからEURへの為替レートを取得」→両方の関数を同時に呼び出す
  - 「都市AとBを比較」→get_weather、get_population、get_distanceを並列で呼び出す
  - 「複数の株式を分析」→各株式のget_stock_priceを並列で呼び出す

  常に単一の複雑な呼び出しよりも複数の特定の関数呼び出しを優先します。
```

次の例は、並列実行によるより効率的な使用を示唆するツール関数の説明を示しています。

```python
 async def get_weather(city: str) -> dict:
      """単一の都市の現在の天気を取得します。

      この関数は並列実行に最適化されています - 異なる都市に対して複数回呼び出します。

      引数：
          city：都市名、例：「ロンドン」、「ニューヨーク」

      戻り値：
          気温、状態、湿度を含む気象データ
      """
      await asyncio.sleep(2)  # API呼び出しをシミュレート
      return {"city": city, "temp": 72, "condition": "sunny"}
```

## 次のステップ

エージェントおよび関数呼び出し用のツールの構築の詳細については、[関数ツール](https://google.github.io/adk-docs/tools/function-tools/)を参照してください。並列処理を活用するツールのより詳細な例については、[adk-python](https://github.com/google/adk-python/tree/main/contributing/samples/parallel_functions)リポジトリのサンプルを参照してください。
