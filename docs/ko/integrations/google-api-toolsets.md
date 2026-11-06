---
catalog_title: Google Apps 도구 세트
catalog_description: Calendar, Gmail, Docs, Sheets, Slides 및 YouTube 작업
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["google", "connectors"]
---

# ADK용 Google Apps 도구 세트

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원됨</span><span class="lst-python">Python v1.0.0</span><span class="lst-typescript">TypeScript v2.4.0</span>
</div>

Google Apps 도구 세트(toolsets)를 사용하면 Agent Development Kit(ADK) 에이전트가 Google Calendar, Gmail, Google Docs, Google Sheets, Google Slides 및 YouTube에 액세스할 수 있습니다. ADK는 API의 [Google API Discovery](https://developers.google.com/discovery) 문서에서 각 도구 세트를 생성합니다. API의 모든 메서드는 에이전트가 호출할 수 있는 하나의 도구가 되며, 도구 세트는 이러한 호출에 대한 OAuth 2.0 인증을 처리합니다.
이 도구 세트들은 `GoogleApiToolset`을 확장하며, 디스커버리 문서를 게시하는 다른 Google API에 에이전트를 연결하기 위해 `GoogleApiToolset`을 직접 사용할 수도 있습니다.

!!! example "TypeScript에서 실험적 기능"
    ADK TypeScript에서 `GoogleApiToolset` 및 이를 기반으로 구축된 도구 세트는 실험적 기능이며 각 도구 세트를 처음 생성할 때 경고를 로깅합니다. TypeScript 도구 세트는 Python 도구 세트보다 적은 옵션을 지원하며 OAuth 스코프를 선택하는 방식이 다릅니다. 자세한 내용은 [TypeScript에서의 차이점](#differences-in-typescript)을 참고하세요.

## 사용 사례

- **일정 관리 어시스턴트**: 사용자를 대신하여 빈 시간을 찾고, 예정된 일정을 나열하고, Calendar 일정을 생성하거나 업데이트합니다.
- **이메일 분류**: Gmail 메시지를 검색, 읽기, 라벨 지정 및 초안 작성하거나, 사용자가 확인한 후 답장을 보냅니다.
- **문서 생성**: Google Docs 및 Slides 프레젠테이션을 생성하고 에이전트가 생성한 콘텐츠로 채웁니다.
- **스프레드시트 자동화**: 워크플로우의 일부로 Google Sheet에서 범위를 읽고, 행을 추가하고, 셀 값을 업데이트합니다.
- **채널 관리**: YouTube를 검색하고, 채널의 동영상과 재생목록을 나열하고, 댓글을 관리합니다.

## 사전 요구사항

- [Google Cloud 프로젝트](https://developers.google.com/workspace/guides/create-project).
- 해당 프로젝트에서 사용할 각 도구 세트의 API(예: Google Calendar API 또는 Gmail API)가 활성화되어 있어야 합니다. 자세한 내용은 [Google Workspace API 사용 설정](https://developers.google.com/workspace/guides/enable-apis)을 참고하세요.
- **웹 애플리케이션** 유형의 OAuth 2.0 클라이언트 ID 및 클라이언트 시크릿. 자세한 내용은 [OAuth 2.0 사용자 인증 정보 얻기](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred)를 참고하세요.
- [ADK 웹 인터페이스](/ko/runtime/web-interface/)로 테스트하는 경우, OAuth 클라이언트의 **승인된 리디렉션 URI(Authorized redirect URIs)**에 웹 인터페이스 URL(예: `http://localhost:8000/dev-ui/`)을 추가하세요.

## 설치

=== "Python"

    이 도구 세트는 `tools` 엑스트라(extra)의 일부인 Google API Python 클라이언트에 의존합니다.

    ```bash
    pip install "google-adk[tools]"
    ```

=== "TypeScript"

    이 도구 세트는 코어 패키지의 일부이며 ADK TypeScript v2.4.0 이상이 필요합니다.

    ```bash
    npm install @google/adk
    ```

## 에이전트와 함께 사용하기

OAuth 클라이언트 사용자 인증 정보로 도구 세트를 생성하고 에이전트의 `tools` 목록에 추가합니다. 도구 필터(tool filter)를 사용하여 에이전트에 필요한 도구만 노출하세요. 대부분의 API에는 수십 개의 메서드가 있으므로, 도구 목록을 짧게 유지하면 모델의 컨텍스트를 작게 유지하고 도구 선택의 정확도를 높일 수 있습니다.

=== "Python"

    ```python
    import os

    from google.adk.agents import Agent
    from google.adk.tools.google_api_tool import CalendarToolset

    calendar_toolset = CalendarToolset(
        client_id=os.environ["OAUTH_CLIENT_ID"],
        client_secret=os.environ["OAUTH_CLIENT_SECRET"],
        tool_filter=[
            "calendar_events_list",
            "calendar_events_get",
            "calendar_events_insert",
            "calendar_freebusy_query",
        ],
    )

    root_agent = Agent(
        model="gemini-flash-latest",
        name="calendar_agent",
        instruction=(
            "Help the user manage their Google Calendar. Use 'primary' as the "
            "calendar_id unless the user names another calendar."
        ),
        tools=[calendar_toolset],
    )
    ```

=== "TypeScript"

    ```typescript
    import { CalendarToolset, LlmAgent } from "@google/adk";

    const calendarToolset = new CalendarToolset({
        clientId: process.env.OAUTH_CLIENT_ID!,
        clientSecret: process.env.OAUTH_CLIENT_SECRET,
        toolFilter: [
            "calendar_events_list",
            "calendar_events_get",
            "calendar_events_insert",
            "calendar_freebusy_query",
        ],
    });

    const rootAgent = new LlmAgent({
        model: "gemini-flash-latest",
        name: "calendar_agent",
        instruction:
            "Help the user manage their Google Calendar. Use 'primary' as the " +
            "calendar_id unless the user names another calendar.",
        tools: [calendarToolset],
    });

    export { rootAgent };
    ```

에이전트가 이러한 도구 중 하나를 처음 호출할 때 ADK는 사용자에게 Google 계정으로 로그인하고 액세스 권한을 부여하도록 요청합니다. ADK 웹 인터페이스에서는 동의 화면이 팝업 창으로 열립니다. 자체 클라이언트 애플리케이션을 빌드하는 경우 애플리케이션에서 이 요청을 처리해야 합니다. 자세한 내용은 [도구로 인증](/ko/tools-custom/authentication/)을 참고하세요.

도구 이름은 디스커버리 문서의 메서드 ID를 기반으로 스네이크 케이스(snake_case) 형식의 `<api>_<resource>_<method>` 패턴을 따릅니다. 예를 들어 Calendar API 메서드 `calendar.events.quickAdd`는 `calendar_events_quick_add` 도구가 됩니다. 도구 이름은 Python과 TypeScript에서 동일합니다.

## 사용 가능한 도구 세트

Python에서는 `google.adk.tools.google_api_tool`에서 도구 세트를 가져옵니다. TypeScript에서는 `@google/adk`에서 가져옵니다.

도구 세트 | API | 도구 수
------- | --- | -----
`CalendarToolset` | [Google Calendar API v3](https://developers.google.com/workspace/calendar/api/v3/reference) | 38
`DocsToolset` | [Google Docs API v1](https://developers.google.com/workspace/docs/api/reference/rest) | 3
`GmailToolset` | [Gmail API v1](https://developers.google.com/workspace/gmail/api/reference/rest) | 79
`SheetsToolset` | [Google Sheets API v4](https://developers.google.com/workspace/sheets/api/reference/rest) | 17
`SlidesToolset` | [Google Slides API v1](https://developers.google.com/workspace/slides/api/reference/rest) | 5
`YoutubeToolset` | [YouTube Data API v3](https://developers.google.com/youtube/v3/docs) | 83

도구 수는 `google-api-python-client` 2.x를 사용하는 ADK Python v2.13.0 및 ADK TypeScript v2.4.0 기준입니다. Python은 `google-api-python-client`에 번들로 포함된 디스커버리 문서를 읽습니다. TypeScript는 에이전트가 도구 세트의 도구를 처음 로드할 때 Google API Discovery Service에서 디스커버리 문서를 다운로드합니다. 두 언어 모두 기본 API에서 메서드가 추가되거나 제거되면 도구 수가 변경됩니다.

각 도구 세트는 동일한 생성자 인수를 받습니다. Python은 이를 키워드 인수로 받고, TypeScript는 단일 옵션 객체의 속성으로 받습니다.

Python | TypeScript | 설명
------ | ---------- | -----------
`client_id` | `clientId` | 사용자 로그인 흐름에 사용되는 OAuth 2.0 클라이언트 ID입니다.
`client_secret` | `clientSecret` | 사용자 로그인 흐름에 사용되는 OAuth 2.0 클라이언트 시크릿입니다.
`tool_filter` | `toolFilter` | 노출할 도구 이름 목록, 또는 각 도구를 전달받아 노출할지 여부를 Python에서는 `True`, TypeScript에서는 `true`로 반환하는 조건자(predicate) 함수입니다.
`service_account` | 지원되지 않음 | 사용자 대신 서비스 계정으로 인증하기 위한 `ServiceAccount`입니다. [서비스 계정으로 인증하기](#authenticate-with-a-service-account)를 참고하세요.
`tool_name_prefix` | 지원되지 않음 | 모든 도구 이름 앞에 밑줄(`_`)과 함께 추가되는 접두사입니다.

### Calendar

`CalendarToolset`은 캘린더, 일정, 액세스 제어 목록(ACL) 및 한가함/바쁨(free/busy) 쿼리를 관리합니다.

=== "Python"

    ```python
    calendar_toolset = CalendarToolset(
        client_id=os.environ["OAUTH_CLIENT_ID"],
        client_secret=os.environ["OAUTH_CLIENT_SECRET"],
        tool_filter=[
            "calendar_events_list",
            "calendar_events_quick_add",
            "calendar_events_patch",
            "calendar_events_delete",
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    const calendarToolset = new CalendarToolset({
        clientId: process.env.OAUTH_CLIENT_ID,
        clientSecret: process.env.OAUTH_CLIENT_SECRET,
        toolFilter: [
            "calendar_events_list",
            "calendar_events_quick_add",
            "calendar_events_patch",
            "calendar_events_delete",
        ],
    });
    ```

도구 | 설명
---- | -----------
`calendar_events_list` | 선택적 시간 범위 및 검색 쿼리를 사용하여 캘린더의 일정을 나열합니다.
`calendar_events_get` | 단일 일정을 반환합니다.
`calendar_events_insert` | 일정을 생성합니다.
`calendar_events_quick_add` | "내일 정오 점심 식사"와 같은 텍스트 문자열에서 일정을 생성합니다.
`calendar_events_patch` | 일정의 필드를 업데이트합니다.
`calendar_events_delete` | 일정을 삭제합니다.
`calendar_freebusy_query` | 캘린더 세트에 대한 한가함/바쁨 정보를 반환합니다.
`calendar_calendar_list_list` | 사용자의 캘린더 목록에 있는 캘린더를 나열합니다.

기타 도구는 `acl`, `calendars`, `calendar_list`, `colors`, `settings` 및 알림 채널을 다룹니다.

### Docs

`DocsToolset`은 Google Docs 문서를 생성, 읽기 및 편집합니다.

=== "Python"

    ```python
    docs_toolset = DocsToolset(
        client_id=os.environ["OAUTH_CLIENT_ID"],
        client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    )
    ```

=== "TypeScript"

    ```typescript
    const docsToolset = new DocsToolset({
        clientId: process.env.OAUTH_CLIENT_ID,
        clientSecret: process.env.OAUTH_CLIENT_SECRET,
    });
    ```

도구 | 설명
---- | -----------
`docs_documents_create` | 지정된 제목으로 빈 문서를 생성합니다.
`docs_documents_get` | 문서의 콘텐츠와 구조를 반환합니다.
`docs_documents_batch_update` | 텍스트 삽입, 텍스트 바꾸기 또는 표 추가와 같은 편집 내용을 문서에 적용합니다.

### Gmail

`GmailToolset`은 메시지, 스레드, 초안, 라벨 및 사서함 설정을 읽고 관리합니다.

=== "Python"

    ```python
    gmail_toolset = GmailToolset(
        client_id=os.environ["OAUTH_CLIENT_ID"],
        client_secret=os.environ["OAUTH_CLIENT_SECRET"],
        tool_filter=[
            "gmail_users_messages_list",
            "gmail_users_messages_get",
            "gmail_users_drafts_create",
            "gmail_users_labels_list",
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    const gmailToolset = new GmailToolset({
        clientId: process.env.OAUTH_CLIENT_ID,
        clientSecret: process.env.OAUTH_CLIENT_SECRET,
        toolFilter: [
            "gmail_users_messages_list",
            "gmail_users_messages_get",
            "gmail_users_drafts_create",
            "gmail_users_labels_list",
        ],
    });
    ```

도구 | 설명
---- | -----------
`gmail_users_messages_list` | `is:unread`와 같은 선택적 Gmail 검색 쿼리를 사용하여 메시지를 나열합니다.
`gmail_users_messages_get` | 단일 메시지를 반환합니다.
`gmail_users_messages_send` | 메시지를 보냅니다.
`gmail_users_messages_modify` | 메시지에서 라벨을 추가하거나 제거합니다.
`gmail_users_threads_list` | 대화 스레드를 나열합니다.
`gmail_users_threads_get` | 스레드의 모든 메시지를 반환합니다.
`gmail_users_drafts_create` | 초안을 생성합니다.
`gmail_users_labels_list` | 사서함의 라벨을 나열합니다.

Gmail 도구는 `user_id` 매개변수를 받습니다. 로그인한 사용자의 경우 `me`를 사용하도록 에이전트에 지시하세요. 기타 도구는 기록, 첨부파일, 그리고 필터, 전달, 부재중 자동 응답과 같은 사서함 설정을 다룹니다.

### Sheets

`SheetsToolset`은 스프레드시트 값을 읽고 쓰며 스프레드시트 구조를 변경합니다.

=== "Python"

    ```python
    sheets_toolset = SheetsToolset(
        client_id=os.environ["OAUTH_CLIENT_ID"],
        client_secret=os.environ["OAUTH_CLIENT_SECRET"],
        tool_filter=[
            "sheets_spreadsheets_get",
            "sheets_spreadsheets_values_get",
            "sheets_spreadsheets_values_append",
            "sheets_spreadsheets_values_update",
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    const sheetsToolset = new SheetsToolset({
        clientId: process.env.OAUTH_CLIENT_ID,
        clientSecret: process.env.OAUTH_CLIENT_SECRET,
        toolFilter: [
            "sheets_spreadsheets_get",
            "sheets_spreadsheets_values_get",
            "sheets_spreadsheets_values_append",
            "sheets_spreadsheets_values_update",
        ],
    });
    ```

도구 | 설명
---- | -----------
`sheets_spreadsheets_create` | 스프레드시트를 생성합니다.
`sheets_spreadsheets_get` | 시트 이름 및 속성과 같은 스프레드시트 메타데이터를 반환합니다.
`sheets_spreadsheets_batch_update` | 시트 추가 또는 셀 서식 지정과 같은 구조적 변경 사항을 적용합니다.
`sheets_spreadsheets_values_get` | `Sheet1!A1:D10`과 같은 범위의 값을 반환합니다.
`sheets_spreadsheets_values_batch_get` | 여러 범위의 값을 반환합니다.
`sheets_spreadsheets_values_append` | 범위 내 데이터의 마지막 행 뒤에 행을 추가합니다.
`sheets_spreadsheets_values_update` | 범위에 값을 씁니다.
`sheets_spreadsheets_values_clear` | 범위의 값을 지웁니다.

### Slides

`SlidesToolset`은 Google Slides 프레젠테이션을 생성, 읽기 및 편집합니다.

=== "Python"

    ```python
    slides_toolset = SlidesToolset(
        client_id=os.environ["OAUTH_CLIENT_ID"],
        client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    )
    ```

=== "TypeScript"

    ```typescript
    const slidesToolset = new SlidesToolset({
        clientId: process.env.OAUTH_CLIENT_ID,
        clientSecret: process.env.OAUTH_CLIENT_SECRET,
    });
    ```

도구 | 설명
---- | -----------
`slides_presentations_create` | 빈 프레젠테이션을 생성합니다.
`slides_presentations_get` | 프레젠테이션의 콘텐츠를 반환합니다.
`slides_presentations_batch_update` | 슬라이드, 도형, 텍스트 또는 이미지 추가와 같은 편집 내용을 적용합니다.
`slides_presentations_pages_get` | 단일 슬라이드를 반환합니다.
`slides_presentations_pages_get_thumbnail` | 단일 슬라이드의 썸네일 이미지 URL을 반환합니다.

### YouTube

`YoutubeToolset`은 YouTube를 검색하고 채널의 동영상, 재생목록, 댓글 및 실시간 방송을 관리합니다.

=== "Python"

    ```python
    youtube_toolset = YoutubeToolset(
        client_id=os.environ["OAUTH_CLIENT_ID"],
        client_secret=os.environ["OAUTH_CLIENT_SECRET"],
        tool_filter=[
            "youtube_search_list",
            "youtube_videos_list",
            "youtube_playlists_list",
            "youtube_playlist_items_list",
        ],
    )
    ```

=== "TypeScript"

    ```typescript
    const youtubeToolset = new YoutubeToolset({
        clientId: process.env.OAUTH_CLIENT_ID,
        clientSecret: process.env.OAUTH_CLIENT_SECRET,
        toolFilter: [
            "youtube_search_list",
            "youtube_videos_list",
            "youtube_playlists_list",
            "youtube_playlist_items_list",
        ],
    });
    ```

도구 | 설명
---- | -----------
`youtube_search_list` | 동영상, 채널 및 재생목록을 검색합니다.
`youtube_videos_list` | 동영상의 세부정보 및 통계를 반환합니다.
`youtube_channels_list` | 채널의 세부정보를 반환합니다.
`youtube_playlists_list` | 재생목록을 나열합니다.
`youtube_playlist_items_list` | 재생목록의 동영상을 나열합니다.
`youtube_comment_threads_list` | 동영상 또는 채널의 댓글 스레드를 나열합니다.
`youtube_comments_set_moderation_status` | 댓글을 승인, 거부 또는 검토 대기 상태로 설정합니다.
`youtube_subscriptions_list` | 구독 목록을 나열합니다.

기타 도구는 자막, 채널 섹션, 실시간 방송 및 스트림, 실시간 채팅, 썸네일을 다룹니다.

## 인증

도구 세트는 OAuth 2.0을 사용하여 로그인한 사용자로서 Google API를 호출합니다. Python에서는 도구 세트가 서비스 계정으로 인증할 수도 있습니다. 다음 섹션에서는 각 방법을 설정하는 방법과 도구 세트가 요청하는 OAuth 스코프를 설명합니다.

### OAuth 2.0으로 사용자 인증하기

클라이언트 ID와 클라이언트 시크릿을 전달하면 각 도구 호출은 로그인한 사용자로서 실행됩니다. ADK는 도구에 토큰이 처음 필요할 때 OAuth 2.0 승인 코드 흐름을 시작하고, 결과 사용자 인증 정보를 저장한 뒤 세션의 이후 호출에서 이를 재사용합니다.

도구 세트를 생성한 후에 클라이언트 사용자 인증 정보를 설정할 수도 있습니다.

=== "Python"

    ```python
    calendar_toolset = CalendarToolset()
    calendar_toolset.configure_auth(
        client_id=os.environ["OAUTH_CLIENT_ID"],
        client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    )
    ```

=== "TypeScript"

    ```typescript
    const calendarToolset = new CalendarToolset();
    calendarToolset.configureAuth(
        process.env.OAUTH_CLIENT_ID,
        process.env.OAUTH_CLIENT_SECRET,
    );
    ```

### OAuth 스코프 {#oauth-scopes}

도구 세트는 API의 디스커버리 문서에 나열된 첫 번째 스코프 하나를 OAuth 스코프로 요청합니다.

Python에서 `google-api-python-client` 2.x의 디스커버리 문서는 다음과 같은 전체 액세스 스코프를 첫 번째로 나열합니다.

도구 세트 | 기본 스코프
------- | -------------
`CalendarToolset` | `https://www.googleapis.com/auth/calendar`
`DocsToolset` | `https://www.googleapis.com/auth/documents`
`GmailToolset` | `https://mail.google.com/`
`SheetsToolset` | `https://www.googleapis.com/auth/drive`
`SlidesToolset` | `https://www.googleapis.com/auth/drive`
`YoutubeToolset` | `https://www.googleapis.com/auth/youtube`

도구 필터는 에이전트가 호출할 수 있는 도구를 제한하지만, 사용자가 부여하는 스코프를 줄이지는 않습니다. 사용자에게 표시되는 동의 화면을 검토하고, 도구 필터와 에이전트 지침을 사용하여 파괴적인(destructive) 도구를 제한하세요.

!!! warning "TypeScript에서의 스코프 선택"
    TypeScript에서 도구 세트는 런타임에 다운로드하는 디스커버리 문서에서 첫 번째 스코프를 가져옵니다. Google API Discovery Service는 스코프를 고정된 순서로 반환하지 않으므로, 요청되는 스코프가 실행할 때마다 달라질 수 있으며 사용하는 도구를 포괄하지 못하는 읽기 전용이거나 좁은 범위의 스코프가 선택될 수 있습니다. 예를 들어 `CalendarToolset`은 `calendar_events_list`를 허용하지 않는 `https://www.googleapis.com/auth/calendar.acls.readonly`를 요청할 수 있습니다. 스코프가 도구를 포괄하지 못하면 API는 스코프 부족(insufficient-scope) 오류로 호출을 거부합니다. ADK TypeScript v2.4.0에는 스코프를 설정하거나 추가하는 옵션이 없습니다.

Python에서 더 많은 스코프를 요청하려면 `GoogleApiToolset`을 직접 생성하고 `additional_scopes`를 전달하세요. 도구 세트는 이를 기본 스코프에 추가합니다.

```python
from google.adk.tools.google_api_tool import GoogleApiToolset

gmail_toolset = GoogleApiToolset(
    "gmail",
    "v1",
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    additional_scopes=["https://www.googleapis.com/auth/gmail.settings.basic"],
)
```

### 서비스 계정으로 인증하기 {#authenticate-with-a-service-account}

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원됨</span><span class="lst-python">Python v1.0.0</span>
</div>

사용자 대신 서비스 계정으로 API를 호출하려면 `ServiceAccount`를 전달하세요. 서비스 계정은 서비스 계정의 이메일 주소와 공유된 스프레드시트나 문서 등 해당 계정과 공유된 데이터에만 액세스할 수 있습니다. `scopes`를 API 호출에 필요한 스코프로 설정하세요.

```python
import json

from google.adk.auth.auth_credential import ServiceAccount
from google.adk.auth.auth_credential import ServiceAccountCredential
from google.adk.tools.google_api_tool import SheetsToolset

with open("path/to/key.json") as f:
  key = ServiceAccountCredential.model_validate(json.load(f))

sheets_toolset = SheetsToolset(
    service_account=ServiceAccount(
        service_account_credential=key,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    ),
    tool_filter=[
        "sheets_spreadsheets_values_get",
        "sheets_spreadsheets_values_append",
    ],
)
```

키 파일 대신 애플리케이션 기본 사용자 인증 정보(Application Default Credentials)를 사용하려면 `ServiceAccount(use_default_credential=True, scopes=[...])`를 전달하세요.

## 구성

도구 세트가 노출하는 도구와 모델에 표시되는 도구 이름을 변경할 수 있습니다. 조건자 함수를 사용하여 규칙에 따라 도구를 선택하거나, Python에서 도구 이름에 접두사를 추가하여 다른 소스의 도구와 이름이 충돌하는 것을 방지하세요.

### 도구 이름에 접두사 추가하기

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원됨</span><span class="lst-python">Python v1.0.0</span>
</div>

에이전트가 여러 소스의 도구를 사용할 때 이름 충돌을 피하려면 `tool_name_prefix`를 설정하세요. 도구 세트는 모델에 표시되는 모든 도구 이름 앞에 접두사와 밑줄(`_`)을 추가합니다. `tool_filter`의 값에는 접두사가 없는 원래 이름을 사용합니다.

```python
calendar_toolset = CalendarToolset(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    tool_filter=["calendar_events_list"],
    tool_name_prefix="google",
)
# 모델에는 도구가 "google_calendar_events_list"로 표시됩니다.
```

### 조건자(predicate)로 도구 필터링하기

이름 대신 규칙에 따라 도구를 선택하려면 함수를 도구 필터로 전달하세요. 이 함수는 각 도구와 선택적인 읽기 전용 컨텍스트를 인수로 받습니다. 예를 들어 읽기 작업만 노출하려면 다음과 같이 작성합니다.

=== "Python"

    ```python
    def is_read_only(tool, readonly_context=None) -> bool:
      return tool.name.endswith(("_get", "_list"))

    gmail_toolset = GmailToolset(
        client_id=os.environ["OAUTH_CLIENT_ID"],
        client_secret=os.environ["OAUTH_CLIENT_SECRET"],
        tool_filter=is_read_only,
    )
    ```

=== "TypeScript"

    ```typescript
    import { BaseTool, GmailToolset } from "@google/adk";

    function isReadOnly(tool: BaseTool): boolean {
        return tool.name.endsWith("_get") || tool.name.endsWith("_list");
    }

    const gmailToolset = new GmailToolset({
        clientId: process.env.OAUTH_CLIENT_ID,
        clientSecret: process.env.OAUTH_CLIENT_SECRET,
        toolFilter: isReadOnly,
    });
    ```

도구 세트를 생성한 후에도 Python의 `set_tool_filter()` 또는 TypeScript의 `setToolFilter()`를 사용하여 필터를 교체할 수 있습니다.

## 다른 Google API 사용하기

`GoogleApiToolset`은 디스커버리 문서가 있는 모든 Google API에 대한 도구를 생성합니다. [APIs Explorer](https://developers.google.com/apis-explorer)에 나열된 API 이름과 버전을 전달하세요. 예를 들어 Google Drive API를 사용하려면 다음과 같이 작성합니다.

=== "Python"

    ```python
    from google.adk.tools.google_api_tool import GoogleApiToolset

    drive_toolset = GoogleApiToolset(
        "drive",
        "v3",
        client_id=os.environ["OAUTH_CLIENT_ID"],
        client_secret=os.environ["OAUTH_CLIENT_SECRET"],
        tool_filter=["drive_files_list", "drive_files_get"],
    )
    ```

=== "TypeScript"

    ```typescript
    import { GoogleApiToolset } from "@google/adk";

    const driveToolset = new GoogleApiToolset({
        apiName: "drive",
        apiVersion: "v3",
        clientId: process.env.OAUTH_CLIENT_ID,
        clientSecret: process.env.OAUTH_CLIENT_SECRET,
        toolFilter: ["drive_files_list", "drive_files_get"],
    });
    ```

Python에서 `GoogleApiToolset`은 다음과 같은 키워드 전용 인수도 받습니다.

인수 | 설명
-------- | -----------
`additional_scopes` | 기본 스코프와 함께 요청할 추가 OAuth 스코프입니다.
`additional_headers` | 도구 세트가 보내는 모든 요청에 추가되는 HTTP 헤더입니다.
`discovery_url` | Google API 클라이언트의 `build()` 함수에 `discoveryServiceUrl`로 전달되는 커스텀 디스커버리 서비스 URL입니다.

## TypeScript에서의 차이점 {#differences-in-typescript}

ADK TypeScript v2.4.0의 TypeScript 도구 세트는 Python 도구 세트와 다음과 같은 차이점이 있습니다.

- **실험적 기능**: 해당 클래스들은 실험적 기능이며 각 클래스를 처음 생성할 때 경고를 로깅합니다.
- **디스커버리 문서**: 에이전트가 도구를 처음 로드할 때 도구 세트가 `https://www.googleapis.com/discovery/v1/apis`에서 디스커버리 문서를 다운로드하므로 에이전트에서 해당 엔드포인트에 대한 네트워크 액세스가 필요합니다.
- **스코프**: 기본 스코프는 다운로드한 디스커버리 문서의 첫 번째 스코프이며 실행 간에 변경될 수 있습니다. 자세한 내용은 [OAuth 스코프](#oauth-scopes)를 참고하세요.
- **지원되지 않는 기능**: 서비스 계정 인증, 도구 이름 접두사, `additional_scopes`, `additional_headers` 및 `discovery_url`.

## 추가 리소스

- [도구로 인증](/ko/tools-custom/authentication/)
- [Google API 도구용 ADK Python 샘플 에이전트](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/google_api)
- [ADK Python `GoogleApiToolset` 소스 코드](https://github.com/google/adk-python/blob/main/src/google/adk/tools/google_api_tool/google_api_toolset.py)
- [Google API 도구 세트용 ADK TypeScript 오프라인 샘플](https://github.com/google/adk-js/blob/adk-v2.4.0/samples/tools/google_api_tool/agent.ts)
- [ADK TypeScript `GoogleApiToolset` 소스 코드](https://github.com/google/adk-js/blob/adk-v2.4.0/core/src/tools/google_api_tool/google_api_toolset.ts)
- [Google API Discovery Service](https://developers.google.com/discovery)
