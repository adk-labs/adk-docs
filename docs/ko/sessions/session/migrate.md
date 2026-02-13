# 세션 데이터베이스 스키마 마이그레이션

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.22.1</span>
</div>

`DatabaseSessionService`를 사용 중이고 ADK Python 릴리스 v1.22.0 이상으로
업그레이드하는 경우, 데이터베이스를 새로운 세션 데이터베이스 스키마로
마이그레이션해야 합니다. ADK Python 릴리스 v1.22.0부터
`DatabaseSessionService`의 데이터베이스 스키마는 pickle 기반 직렬화인 `v0`에서
JSON 기반 직렬화를 사용하는 `v1`로 업데이트되었습니다. 기존 `v0` 세션
스키마 데이터베이스도 ADK Python v1.22.0 이상에서 계속 동작하지만,
향후 릴리스에서는 `v1` 스키마가 필요할 수 있습니다.


## 세션 데이터베이스 마이그레이션

마이그레이션을 돕기 위한 스크립트가 제공됩니다. 이 스크립트는
기존 데이터베이스에서 데이터를 읽어 새 포맷으로 변환한 뒤,
새 데이터베이스에 기록합니다. 아래 예시처럼 ADK 명령줄 인터페이스(CLI)의
`migrate session` 명령으로 마이그레이션을 실행할 수 있습니다:

!!! warning "필수: ADK Python v1.22.1 이상"

    이 절차에는 ADK Python v1.22.1 이상이 필요합니다. 해당 버전에
    세션 데이터베이스 스키마 변경을 지원하는 마이그레이션 CLI 기능과
    버그 수정이 포함되어 있기 때문입니다.

=== "SQLite"

    ```bash
    adk migrate session \
      --source_db_url=sqlite:///source.db \
      --dest_db_url=sqlite:///dest.db
    ```

=== "PostgreSQL"

    ```bash
    adk migrate session \
      --source_db_url=postgresql://localhost:5432/v0 \
      --dest_db_url=postgresql://localhost:5432/v1
    ```

마이그레이션 후에는 `DatabaseSessionService` 설정을 업데이트하여
`dest_db_url`에 지정한 새 데이터베이스 URL을 사용하세요.
