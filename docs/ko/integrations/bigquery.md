---
catalog_title: BigQuery 도구
catalog_description: BigQuery에 연결하여 데이터를 조회하고 분석을 수행합니다
catalog_icon: /integrations/assets/bigquery.png
catalog_tags: ["data", "google"]
---

# ADK용 BigQuery 도구

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-python">Python v1.1.0</span>
</div>

BigQuery 연동을 제공하는 도구 모음은 다음과 같습니다:

* **`list_dataset_ids`**: GCP 프로젝트에 존재하는 BigQuery 데이터셋 ID 목록을 가져옵니다.
* **`get_dataset_info`**: BigQuery 데이터셋에 대한 메타데이터를 가져옵니다.
* **`list_table_ids`**: BigQuery 데이터셋에 존재하는 테이블 ID 목록을 가져옵니다.
* **`get_table_info`**: BigQuery 테이블에 대한 메타데이터를 가져옵니다.
* **`get_job_info`**: BigQuery 작업에 대한 메타데이터 정보(슬롯 사용량, 구성, 통계, 상태 등)를 가져옵니다.
* **`execute_sql`**: BigQuery에서 SQL 쿼리를 실행하고 결과를 가져옵니다.
* **`forecast`**: `AI.FORECAST` 함수를 사용하여 BigQuery AI 시계열 예측을 실행합니다.
* **`analyze_contribution`**: 메트릭의 변화를 이끄는 요인을 파악하기 위해 BigQuery ML 기여도 분석을 수행합니다.
* **`detect_anomalies`**: ARIMA_PLUS 모델을 학습시키고 시계열 데이터의 이상을 감지합니다.
* **`ask_data_insights`**: 자연어를 사용하여 BigQuery 테이블의 데이터에 대한 질문에 답변합니다.
* **`search_catalog`**: Dataplex를 통한 자연어 시맨틱 검색으로 BigQuery 데이터셋과 테이블을 찾습니다.

이 도구들은 `BigQueryToolset`으로 패키징되어 있습니다.

## 인증 (Authentication)

`BigQueryToolset`은 `BigQueryCredentialsConfig`를 통해 여러 인증 방식을 지원합니다.

### 애플리케이션 기본 사용자 인증 정보 (Application Default Credentials)

로컬 개발 환경 및 Cloud Run, GKE와 같은 Google Cloud 서비스에서 실행할 때 이 방식을 사용해야 합니다.

```python
import google.auth
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# 애플리케이션 기본 사용자 인증 정보 로드
credentials, project_id = google.auth.default()

# 툴셋 구성
credentials_config = BigQueryCredentialsConfig(credentials=credentials)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

### 서비스 계정 (Service Account)

서비스 계정 파일 또는 정보를 명시적으로 제공할 수 있습니다.

```python
from google.oauth2 import service_account
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# 서비스 계정 인증 정보 로드
credentials = service_account.Credentials.from_service_account_file('path/to/key.json')

# 툴셋 구성
credentials_config = BigQueryCredentialsConfig(credentials=credentials)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

### 외부 액세스 토큰 (External Access Token)

최종 사용자를 대신하여 작동해야 하는 애플리케이션의 경우, OAuth2 흐름이나 외부 IDP 등에서 얻은 액세스 토큰으로 직접 인스턴스화된 사용자 인증 정보를 전달할 수 있습니다.

```python
from google.oauth2.credentials import Credentials
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# 'user_token'이 외부 OAuth 흐름을 통해 획득되었다고 가정
credentials = Credentials(token=user_token)

# 툴셋 구성
credentials_config = BigQueryCredentialsConfig(credentials=credentials)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

### 외부 인증 제공업체 (External Auth Providers)

Gemini Enterprise와 같이 토큰이 플랫폼에 의해 관리되는 외부 인증 제공업체와 통합하는 경우 `external_access_token_key`를 사용합니다.

```python
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# 세션 상태에서 액세스 토큰을 조회하는 데 사용되는 키
credentials_config = BigQueryCredentialsConfig(
    external_access_token_key="YOUR_AUTH_ID"
)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

### 대화형 인증 (Interactive Auth - ADK Web)

대화형 세션을 위해 `adk web` 인터페이스를 사용할 때 OAuth 2.0 클라이언트 인증 정보를 제공하여 로그인 흐름을 트리거할 수 있습니다. 이 메커니즘은 로컬 개발 환경과 Cloud Run과 같은 환경에 배포된 ADK 에이전트 모두에서 작동합니다.

```python
from google.adk.tools.bigquery import BigQueryToolset, BigQueryCredentialsConfig

# OAuth 2.0 클라이언트 ID 및 보안 비밀 제공
credentials_config = BigQueryCredentialsConfig(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)
bigquery_toolset = BigQueryToolset(credentials_config=credentials_config)
```

## 샘플 코드

다음 샘플 코드는 애플리케이션 기본 사용자 인증 정보(ADC)를 사용하여 ADK 에이전트에서 `BigQueryToolset`을 사용하는 방법을 보여줍니다.

```py
--8<-- "examples/python/snippets/tools/built-in-tools/bigquery.py"
```

## 샘플 에이전트

상세한 인증 예제가 포함된 BigQuery 기반 에이전트의 완전한 실행 가능한 샘플은 GitHub의 [BigQuery Sample Agent](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/bigquery)를 참조하세요.

참고: BigQuery 데이터 에이전트를 도구로 사용하려면 [ADK용 Data Agents 도구](data-agent.md)를 참조하세요.
