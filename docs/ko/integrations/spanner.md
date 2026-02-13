---
catalog_title: Spanner 도구
catalog_description: Spanner와 상호작용하여 데이터를 조회하고 검색 및 SQL 실행을 수행합니다
catalog_icon: /adk-docs/integrations/assets/spanner.png
catalog_tags: ["data","google"]
---

# ADK용 Google Cloud Spanner 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.11.0</span>
</div>

다음은 Spanner 통합을 제공하기 위한 도구 모음입니다:

* **`list_table_names`**: GCP Spanner 데이터베이스에 존재하는 테이블 이름을 조회합니다.
* **`list_table_indexes`**: GCP Spanner 데이터베이스에 존재하는 테이블 인덱스를 조회합니다.
* **`list_table_index_columns`**: GCP Spanner 데이터베이스에 존재하는 테이블 인덱스 컬럼을 조회합니다.
* **`list_named_schemas`**: Spanner 데이터베이스의 named schema를 조회합니다.
* **`get_table_schema`**: Spanner 데이터베이스 테이블 스키마와 메타데이터 정보를 조회합니다.
* **`execute_sql`**: Spanner 데이터베이스에서 SQL 쿼리를 실행하고 결과를 조회합니다.
* **`similarity_search`**: 텍스트 쿼리를 사용해 Spanner에서 유사도 검색을 수행합니다.

이 도구들은 `SpannerToolset` 툴셋으로 패키징되어 있습니다.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/spanner.py"
```
