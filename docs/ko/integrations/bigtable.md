---
catalog_title: Bigtable 도구
catalog_description: Bigtable과 상호작용하여 데이터를 조회하고 SQL을 실행합니다
catalog_icon: /adk-docs/integrations/assets/bigtable.png
catalog_tags: ["data", "google"]
---

# ADK용 Bigtable 도구

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.12.0</span>
</div>

다음은 Bigtable 통합을 제공하기 위한 도구 모음입니다:

* **`list_instances`**: Google Cloud 프로젝트의 Bigtable 인스턴스를 조회합니다.
* **`get_instance_info`**: Google Cloud 프로젝트의 인스턴스 메타데이터 정보를 조회합니다.
* **`list_tables`**: GCP Bigtable 인스턴스의 테이블을 조회합니다.
* **`get_table_info`**: GCP Bigtable의 테이블 메타데이터 정보를 조회합니다.
* **`execute_sql`**: Bigtable 테이블에서 SQL 쿼리를 실행하고 결과를 조회합니다.

이 도구들은 `BigtableToolset` 툴셋으로 패키징되어 있습니다.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigtable.py"
```
