---
catalog_title: BigQuery 도구
catalog_description: BigQuery에 연결해 데이터를 조회하고 분석을 수행합니다
catalog_icon: /adk-docs/integrations/assets/bigquery.png
catalog_tags: ["data", "google"]
---

# ADK용 BigQuery 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.1.0</span>
</div>

다음은 BigQuery 통합을 제공하기 위한 도구 모음입니다:

* **`list_dataset_ids`**: GCP 프로젝트에 존재하는 BigQuery 데이터셋 ID를 조회합니다.
* **`get_dataset_info`**: BigQuery 데이터셋의 메타데이터를 조회합니다.
* **`list_table_ids`**: BigQuery 데이터셋에 존재하는 테이블 ID를 조회합니다.
* **`get_table_info`**: BigQuery 테이블의 메타데이터를 조회합니다.
* **`execute_sql`**: BigQuery에서 SQL 쿼리를 실행하고 결과를 조회합니다.
* **`forecast`**: `AI.FORECAST` 함수를 사용해 BigQuery AI 시계열 예측을 수행합니다.
* **`ask_data_insights`**: 자연어로 BigQuery 테이블의 데이터에 대해 질의응답합니다.

이 도구들은 `BigQueryToolset` 툴셋으로 패키징되어 있습니다.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigquery.py"
```

참고: BigQuery 데이터 에이전트를 도구로 사용하려면 [ADK용 Data Agents 도구](data-agent.md)를 참조하세요.
