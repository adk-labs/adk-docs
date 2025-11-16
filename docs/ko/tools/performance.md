---
hide:
  - toc
---
# 병렬 실행으로 도구 성능 향상

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.10.0</span>
</div>

Python용 에이전트 개발 키트(ADK) 버전 1.10.0부터 프레임워크는 에이전트가 요청한 [함수 도구](/adk-docs/tools/function-tools/)를 병렬로 실행하려고 시도합니다. 이 동작은 에이전트의 성능과 응답성을 크게 향상시킬 수 있으며, 특히 여러 외부 API 또는 장기 실행 작업에 의존하는 에이전트의 경우 더욱 그렇습니다. 예를 들어 각각 2초가 걸리는 3개의 도구가 있는 경우 병렬로 실행하면 총 실행 시간이 6초 대신 2초에 가까워집니다. 도구 함수를 병렬로 실행하는 기능은 특히 다음과 같은 시나리오에서 에이전트의 성능을 향상시킬 수 있습니다.

-   **연구 작업:** 에이전트가 워크플로의 다음 단계로 진행하기 전에 여러 소스에서 정보를 수집하는 경우.
-   **API 호출:** 에이전트가 여러 항공사의 API를 사용하여 사용 가능한 항공편을 검색하는 등 여러 API에 독립적으로 액세스하는 경우.
-   **게시 및 통신 작업:** 에이전트가 여러 독립적인 채널 또는 여러 수신자를 통해 게시하거나 통신해야 하는 경우.

그러나 이 성능 향상을 사용하려면 사용자 지정 도구가 비동기 실행 지원으로 빌드되어야 합니다. 이 가이드에서는 ADK에서 병렬 도구 실행이 작동하는 방식과 이 처리 기능을 최대한 활용하기 위해 도구를 빌드하는 방법을 설명합니다.

!!! warning
    도구 함수 호출 집합에서 동기 처리를 사용하는 모든 ADK 도구는 다른 도구가 병렬 실행을 허용하더라도 다른 도구가 병렬로 실행되는 것을 차단합니다.

## 병렬 준비 도구 빌드

도구 함수를 비동기 함수로 정의하여 병렬 실행을 활성화합니다. Python 코드에서 이는 `async def` 및 `await` 구문을 사용하는 것을 의미하며, 이를 통해 ADK는 `asyncio` 이벤트 루프에서 동시에 실행할 수 있습니다. 다음 섹션에서는 병렬 처리 및 비동기 작업을 위해 빌드된 에이전트 도구의 예를 보여줍니다.

### http 웹 호출 예

다음 코드 예제는 비동기적으로 작동하고 병렬 실행을 허용하도록 `get_weather()` 함수를 수정하는 방법을 보여줍니다.

```python
 async def get_weather(city: str) -> dict:
      async with aiohttp.ClientSession() as session:
          async with session.get(f"http://api.weather.com/{city}") as response:
              return await response.json()
```

### 데이터베이스 호출 예

다음 코드 예제는 비동기적으로 작동하도록 데이터베이스 호출 함수를 작성하는 방법을 보여줍니다.

```python
async def query_database(query: str) -> list:
      async with asyncpg.connect("postgresql://...") as conn:
          return await conn.fetch(query)
```

### 긴 루프에 대한 양보 동작 예

도구가 여러 요청 또는 수많은 장기 실행 요청을 처리하는 경우 다음 코드 샘플과 같이 다른 도구가 실행되도록 허용하는 양보 코드를 추가하는 것을 고려하십시오.

```python
async def process_data(data: list) -> dict:
      results = []
      for i, item in enumerate(data):
          processed = await process_item(item)  # 양보 지점
          results.append(processed)

          # 긴 루프에 대한 주기적인 양보 지점 추가
          if i % 100 == 0:
              await asyncio.sleep(0)  # 제어 양보
      return {"results": results}
```

!!! tip "중요"
    다른 함수의 실행을 차단하지 않으려면 일시 중지에 `asyncio.sleep()` 함수를 사용하십시오.

### 집약적인 작업을 위한 스레드 풀 예

처리 집약적인 함수를 수행할 때 다음 예와 같이 사용 가능한 컴퓨팅 리소스를 더 잘 관리하기 위해 스레드 풀을 만드는 것을 고려하십시오.

```python
async def cpu_intensive_tool(data: list) -> dict:
      loop = asyncio.get_event_loop()

      # CPU 바운드 작업에 스레드 풀 사용
      with ThreadPoolExecutor() as executor:
          result = await loop.run_in_executor(
              executor,
              expensive_computation,
              data
          )
      return {"result": result}
```

### 프로세스 청킹 예

긴 목록 또는 대량의 데이터에 대한 프로세스를 수행할 때 다음 예와 같이 스레드 풀 기술을 데이터 청크로 처리 나누기와 결합하고 청크 간에 처리 시간을 양보하는 것을 고려하십시오.

```python
 async def process_large_dataset(dataset: list) -> dict:
      results = []
      chunk_size = 1000

      for i in range(0, len(dataset), chunk_size):
          chunk = dataset[i:i + chunk_size]

          # 스레드 풀에서 청크 처리
          loop = asyncio.get_event_loop()
          with ThreadPoolExecutor() as executor:
              chunk_result = await loop.run_in_executor(
                  executor, process_chunk, chunk
              )

          results.extend(chunk_result)

          # 청크 간에 제어 양보
          await asyncio.sleep(0)

      return {"total_processed": len(results), "results": results}
```

## 병렬 준비 프롬프트 및 도구 설명 작성

AI 모델용 프롬프트를 빌드할 때 함수 호출을 병렬로 수행하도록 명시적으로 지정하거나 힌트를 주는 것을 고려하십시오. 다음 AI 프롬프트 예는 모델에 도구를 병렬로 사용하도록 지시합니다.

```none
사용자가 여러 정보를 요청할 때 항상 함수를 병렬로 호출합니다.

  예:
  - "런던 날씨와 USD에서 EUR로의 환율 가져오기" → 두 함수를 동시에 호출
  - "도시 A와 B 비교" → get_weather, get_population, get_distance를 병렬로 호출
  - "여러 주식 분석" → 각 주식에 대해 get_stock_price를 병렬로 호출

  항상 단일 복잡한 호출보다 여러 특정 함수 호출을 선호합니다.
```

다음 예는 병렬 실행을 통해 더 효율적인 사용을 암시하는 도구 함수 설명을 보여줍니다.

```python
 async def get_weather(city: str) -> dict:
      """단일 도시의 현재 날씨를 가져옵니다.

      이 함수는 병렬 실행에 최적화되어 있습니다. 다른 도시에 대해 여러 번 호출하십시오.

      인수:
          city: 도시 이름, 예: '런던', '뉴욕'

      반환:
          온도, 조건, 습도를 포함한 날씨 데이터
      """
      await asyncio.sleep(2)  # API 호출 시뮬레이션
      return {"city": city, "temp": 72, "condition": "sunny"}
```

## 다음 단계

에이전트 및 함수 호출용 도구 빌드에 대한 자세한 내용은 [함수 도구](https://google.github.io/adk-docs/tools/function-tools/)를 참조하세요. 병렬 처리를 활용하는 도구의 더 자세한 예는 [adk-python](https://github.com/google/adk-python/tree/main/contributing/samples/parallel_functions) 리포지토리의 샘플을 참조하세요.
