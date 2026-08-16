---
catalog_title: Spanner 도구
catalog_description: Spanner와 상호작용하여 데이터를 조회하고 검색 및 SQL 실행을 수행합니다
catalog_icon: /integrations/assets/spanner.png
catalog_tags: ["data","google"]
---

# ADK용 Google Cloud Spanner 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.11.0</span><span class="lst-preview">실험적</span>
</div>

[Google Cloud Spanner](https://cloud.google.com/spanner)는 SQL 및 벡터 검색을 지원하는 완전 관리형 분산 데이터베이스입니다. ADK Spanner 도구를 사용하면 에이전트가 데이터베이스 스키마를 탐색하고, SQL 쿼리를 실행하며, Spanner 데이터에 대해 벡터 유사도 검색을 수행할 수 있습니다.

!!! example "실험적 기능"
    이 기능은 실험적이며 향후 릴리스에서 업데이트될 수 있습니다.

## 사용 가능한 도구

`SpannerToolset`은 다음 도구를 제공합니다:

- **`list_table_names`**: GCP Spanner 데이터베이스에 존재하는 테이블 이름 목록을 가져옵니다.
- **`list_table_indexes`**: GCP Spanner 데이터베이스에 존재하는 테이블 인덱스 목록을 가져옵니다.
- **`list_table_index_columns`**: GCP Spanner 데이터베이스에 존재하는 테이블 인덱스 컬럼 목록을 가져옵니다.
- **`list_named_schemas`**: Spanner 데이터베이스의 명명된 스키마(named schema)를 가져옵니다.
- **`get_table_schema`**: Spanner 데이터베이스 테이블 스키마 및 메타데이터 정보를 가져옵니다.
- **`execute_sql`**: Spanner 데이터베이스에서 SQL 쿼리를 실행하고 결과를 가져옵니다.
- **`similarity_search`**: 텍스트 쿼리를 사용하여 Spanner에서 유사도 검색을 수행합니다.

## 에이전트와 함께 사용

```py
--8<-- "examples/python/snippets/tools/built-in-tools/spanner.py"
```

## 벡터 유사도 검색 (Vector similarity search)

`vector_store_similarity_search` 도구를 사용하면 에이전트가 벡터 저장소로 구성된 Spanner 테이블에 대해 시맨틱 검색을 수행할 수 있습니다. 이 기능은 컨텍스트를 인식하는 RAG 애플리케이션을 구축하는 데 필수적이며, AI 모델이 정확한 키워드 일치 대신 의미론적 의미를 기반으로 데이터베이스 컨텍스트를 검색할 수 있도록 합니다. `SpannerVectorStoreSettings`를 구성하면 에이전트가 사용자 질의의 의도를 더 잘 이해하고 가장 관련성이 높은 Spanner 데이터를 기반으로 응답을 접지(Grounding)할 수 있습니다.

다음 예시는 Spanner 테이블을 벡터 저장소로 구성하고 `vector_store_similarity_search` 도구를 RAG 에이전트에 연결하는 방법을 보여줍니다:

```py
from google.adk.agents import LlmAgent
from google.adk.tools.spanner import SpannerCredentialsConfig, SpannerToolset
from google.adk.tools.spanner.settings import (
    Capabilities,
    SpannerToolSettings,
    SpannerVectorStoreSettings,
)

# 1. 벡터 저장소 설정으로 Spanner 도구 구성 정의
my_vector_store_settings = SpannerVectorStoreSettings(
    project_id="your-gcp-project",
    instance_id="your-spanner-instance",
    database_id="your-database",
    table_name="my_products",
    content_column="productDescription",
    embedding_column="productDescriptionEmbedding",
    vector_length=768,
    vertex_ai_embedding_model_name="text-embedding-005",
    selected_columns=["productId", "productName", "productDescription"],
    nearest_neighbors_algorithm="EXACT_NEAREST_NEIGHBORS",
    top_k=3,
    distance_type="COSINE",
    additional_filter="inventoryCount > 0",
)

my_tool_settings = SpannerToolSettings(
    capabilities=[Capabilities.DATA_READ],
    vector_store_settings=my_vector_store_settings,
)

# 2. Spanner 툴셋 초기화
credentials_config = SpannerCredentialsConfig()
my_spanner_toolset = SpannerToolset(
    credentials_config=credentials_config,
    spanner_tool_settings=my_tool_settings,
    tool_filter=["vector_store_similarity_search"],
)

# 3. RAG 에이전트에서 툴셋 사용
my_rag_agent = LlmAgent(
    model="gemini-flash-latest",
    name="product_search_agent",
    instruction="""
    You are a helpful assistant that answers user questions by finding similar products.
    1. Always use the `vector_store_similarity_search` tool to find relevant product information.
    2. If no relevant information is found, state that no matching products were found.
    3. Present the relevant product details clearly in your response.
    """,
    tools=[my_spanner_toolset],
)
```

### 구성

위에서 사용된 `SpannerVectorStoreSettings` 클래스는 `vector_store_similarity_search`가 작동하는 방식을 정의합니다. 다음 매개변수를 허용합니다:

#### 필수 매개변수

- **`project_id`**: 인증 컨텍스트에 필요한 Google Cloud 프로젝트 ID입니다.
- **`instance_id`**: Spanner 인스턴스 ID입니다.
- **`database_id`**: Spanner 데이터베이스 ID입니다.
- **`table_name`**: 벡터 임베딩이 포함된 Spanner 테이블입니다.
- **`embedding_column`**: 벡터 임베딩이 저장된 `ARRAY<FLOAT>` 또는 `ARRAY<DOUBLE>` 컬럼입니다.
- **`content_column`**: 검색할 원본 텍스트 또는 콘텐츠가 포함된 컬럼입니다.
- **`vector_length`**: 모델과 일치해야 하는 임베딩 벡터의 차원 수입니다.
- **`vertex_ai_embedding_model_name`**: 임베딩을 생성하는 데 사용된 모델입니다(예: "text-embedding-005").

#### 선택 매개변수

- **`selected_columns`**: 메타데이터나 식별자 등 검색 결과에 포함할 컬럼 목록입니다.
- **`nearest_neighbors_algorithm`**: 검색에 사용할 알고리즘입니다(`EXACT_NEAREST_NEIGHBORS`, `APPROXIMATE_NEAREST_NEIGHBORS` 등).
    - **`num_leaves_to_search`**: 검색할 인덱스 리프 노드 수입니다. `APPROXIMATE_NEAREST_NEIGHBORS`와 함께 사용할 때만 사용됩니다.
    - **`vector_search_index_settings`**: 벡터 인덱스 설정입니다. `APPROXIMATE_NEAREST_NEIGHBORS`와 함께 사용할 때만 필요합니다.
- **`top_k`**: 질의당 검색할 가장 가까운 이웃의 수입니다.
- **`distance_type`**: 유사도 계산에 사용되는 거리 메트릭입니다(`COSINE` 또는 `EUCLIDEAN`).
- **`additional_filter`**: 검색 중 적용할 선택적 SQL 필터 문자열입니다(예: "inventoryCount > 0").

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
