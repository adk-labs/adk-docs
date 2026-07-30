---
catalog_title: Spanner 도구
catalog_description: Spanner와 상호작용하여 데이터를 조회하고 검색 및 SQL 실행을 수행합니다
catalog_icon: /integrations/assets/spanner.png
catalog_tags: ["data","google"]
---

# ADK용 Google Cloud Spanner 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.11.0</span>
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

## Spanner Admin Toolset

`SpannerAdminToolset`은 Spanner 인스턴스 및 데이터베이스에 대한 관리 작업을 지원합니다. 이 툴셋을 사용하려면 별도의 라이브러리 임포트가 필요합니다.

!!! warning "주의하여 사용"

    이 툴셋은 Spanner 인스턴스 및 데이터베이스를 생성, 검사 및 수정할 수 있으므로 신중하게 액세스 권한을 부여하세요. 실행 환경(Application Default Credentials 또는 서비스 계정 키 등)이 승인된 프로젝트로만 제한되어 있고 `roles/spanner.admin`과 같이 최소한의 필요한 IAM 권한만 사용하는지 확인하세요.

### 사용 가능한 도구

* **`list_instances`**: 프로젝트 내의 Spanner 인스턴스 목록을 조회합니다.
* **`get_instance`**: Spanner 인스턴스의 세부정보를 가져옵니다.
* **`create_database`**: 새로운 Spanner 데이터베이스를 생성합니다.
* **`list_databases`**: 인스턴스 내의 Spanner 데이터베이스 목록을 조회합니다.
* **`create_instance`**: 새로운 Spanner 인스턴스를 생성합니다.
* **`list_instance_configs`**: 사용 가능한 Spanner 인스턴스 구성 목록을 조회합니다.
* **`get_instance_config`**: Spanner 인스턴스 구성의 세부정보를 가져옵니다.

### 구성

이 툴셋을 사용하기 전에 필요한 환경 변수를 설정하세요:

- `SPANNER_PROJECT`: 작업을 수행할 GCP 프로젝트 ID입니다.
- `SPANNER_INSTANCE` (선택사항): 기본 Spanner 인스턴스 ID입니다.
- `SPANNER_DATABASE` (선택사항): 기본 데이터베이스 ID입니다.

### 에이전트와 함께 사용

Google Cloud Spanner 관리 기능에 액세스하려면 `SpannerAdminToolset`을 초기화하세요. 그런 다음 `LlmAgent`의 `tools` 목록에 전달하여 에이전트가 Spanner 리소스를 관리할 수 있도록 설정합니다.

```python
from google.adk.agents import LlmAgent
from google.adk.tools.spanner import SpannerAdminToolset

# Spanner 관리자 툴셋 초기화
spanner_admin_tools = SpannerAdminToolset()

# 에이전트에 툴셋 등록 (모델 및 지침 제공 확인)
agent = LlmAgent(
    name="SpannerAdminAgent",
    model="gemini-flash-latest",
    instruction=(
        "You are a helpful database administrator. Use the SpannerAdminToolset "
        "to manage and query Spanner instances and databases in the project."
    ),
    tools=[spanner_admin_tools]
)
```
