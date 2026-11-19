# 병렬 실행으로 도구 성능 향상

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.10.0</span>
</div>

Python용 Agent Development Kit(ADK) 버전 1.10.0부터 프레임워크는 에이전트가 요청한 모든 [함수 도구](/ko/tools-custom/function-tools/)를 병렬로 실행하려고 시도합니다. 이 동작은 특히 여러 외부 API나 장기 실행 작업에 의존하는 에이전트의 성능과 응답성을 크게 높여 줍니다. 예를 들어 각각 2초가 걸리는 3개의 도구가 있을 때 이를 병렬로 실행하면 총 실행 시간은 6초 대신 약 2초로 단축됩니다. 도구 함수의 병렬 실행은 특히 다음과 같은 시나리오에서 에이전트 성능을 크게 개선합니다.

-   **리서치 작업:** 워크플로의 다음 단계로 넘어가기 전에 에이전트가 여러 소스에서 정보를 수집하는 경우.
-   **API 호출:** 여러 항공사의 API로 예약 가능한 항공편을 동시에 조회하는 등 에이전트가 여러 API에 독립적으로 접근하는 경우.
-   **발행 및 커뮤니케이션 작업:** 에이전트가 여러 독립적인 채널이나 다수의 수신자에게 동시에 메시지를 발행하거나 전송해야 하는 경우.

단, 이 성능 개선 효과를 얻으려면 커스텀 도구가 비동기 실행을 지원하도록 빌드되어야 합니다. 이 가이드에서는 ADK에서 병렬 도구 실행이 작동하는 방식과 이를 최대한 활용하도록 도구를 작성하는 방법을 설명합니다.

!!! warning
    함께 호출된 도구 함수 중 동기 방식으로 동작하는 ADK 도구가 하나라도 있으면, 다른 도구가 병렬 실행을 지원하더라도 전체 병렬 실행이 차단됩니다.

## 병렬 처리를 지원하는 도구 빌드

도구 함수를 비동기 함수로 정의하면 병렬 실행이 활성화됩니다. Python 코드에서는 `async def`와 `await` 구문을 사용하여 ADK가 `asyncio` 이벤트 루프에서 함수들을 동시에 실행할 수 있도록 작성합니다. 다음 섹션에서는 병렬 처리 및 비동기 작업을 지원하도록 작성된 에이전트 도구 예시를 보여줍니다.

### HTTP 웹 호출 예시

다음 코드 예시는 비동기로 동작하여 병렬 실행이 가능하도록 `get_weather()` 함수를 작성하는 방법을 보여줍니다.

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

### 긴 루프에서의 제어권 양보(Yield) 예시

도구가 다수의 요청이나 장기 실행 요청을 반복 처리하는 경우 다음 코드 샘플과 같이 다른 도구가 실행될 수 있도록 제어권을 양보(yield)하는 코드를 추가하는 것이 좋습니다.

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
    다른 함수의 실행을 차단하지 않으려면 일시 대기 시 `asyncio.sleep()` 함수를 사용하세요.

### 연산 집약적 작업을 위한 스레드 풀 예시

CPU 연산 집약적인 작업을 수행할 때는 다음 예시와 같이 가용 컴퓨팅 리소스를 효율적으로 관리하기 위해 스레드 풀을 활용하는 것이 좋습니다.

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

### 청크 단위 처리(Chunking) 예시

긴 리스트나 대용량 데이터를 처리할 때는 다음 예시와 같이 스레드 풀 기법과 함께 데이터를 청크(chunk) 단위로 나누고 청크 사이에 제어권을 양보하는 방식을 결합해 보세요.

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

          # 청크 간 제어 양보
          await asyncio.sleep(0)

      return {"total_processed": len(results), "results": results}
```

## 병렬 실행을 유도하는 프롬프트 및 도구 설명 작성

AI 모델용 프롬프트를 작성할 때는 함수 호출을 병렬로 수행하도록 명시적으로 지시하거나 힌트를 포함하는 것이 좋습니다. 다음 프롬프트 예시는 모델이 도구를 병렬로 호출하도록 안내합니다.

```none
사용자가 여러 정보를 요청할 때 항상 함수를 병렬로 호출하십시오.

  예:
  - "런던 날씨와 USD에서 EUR로의 환율 가져오기" → 두 함수를 동시에 호출
  - "도시 A와 B 비교" → get_weather, get_population, get_distance를 병렬로 호출
  - "여러 주식 분석" → 각 주식에 대해 get_stock_price를 병렬로 호출

  항상 단일 복잡한 호출보다 여러 특정 함수 호출을 선호하십시오.
```

다음 예는 병렬 실행을 통해 보다 효율적인 사용을 암시하는 도구 함수 설명을 보여줍니다.

```python
 async def get_weather(city: str) -> dict:
      """단일 도시에 대한 현재 날씨를 가져옵니다.

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

에이전트 및 함수 호출용 도구 빌드에 대한 자세한 내용은 [함수 도구](/ko/tools-custom/function-tools/)를 참고하세요. 병렬 처리를 활용하는 도구의 자세한 예는 [adk-python](https://github.com/google/adk-python/tree/main/contributing/samples/parallel_functions) 리포지토리의 샘플을 참고하세요.