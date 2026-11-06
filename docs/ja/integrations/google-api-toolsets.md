---
catalog_title: Google Apps ツールセット
catalog_description: Calendar、Gmail、Docs、Sheets、Slides、YouTube の操作
catalog_icon: /integrations/assets/adk.png
catalog_tags: ["google", "connectors"]
---

# ADK 用 Google Apps ツールセット

<div class="language-support-tag">
  <span class="lst-supported">ADK でのサポート</span><span class="lst-python">Python v1.0.0</span><span class="lst-typescript">TypeScript v2.4.0</span>
</div>

Google Apps ツールセット（toolsets）を使用すると、Agent Development Kit（ADK）エージェントから Google カレンダー、Gmail、Google ドキュメント、Google スプレッドシート、Google スライド、および YouTube にアクセスできるようになります。ADK は、各 API の [Google API Discovery](https://developers.google.com/discovery) ドキュメントから各ツールセットを生成します。API 内のすべてのメソッドがエージェントから呼び出し可能な 1 つのツールになり、ツールセットがそれらの呼び出しに対する OAuth 2.0 認証を処理します。
これらのツールセットは `GoogleApiToolset` を拡張したものであり、`GoogleApiToolset` を直接使用して、ディスカバリドキュメントを公開している他の任意の Google API にエージェントを接続することもできます。

!!! example "TypeScript では実験的機能"
    ADK TypeScript では、`GoogleApiToolset` およびそれに基づいて構築されたツールセットは実験的機能であり、各ツールセットを最初に作成した際に警告がログに記録されます。TypeScript のツールセットは Python のツールセットよりもサポートされているオプションが少なく、OAuth スコープの選択方法も異なります。詳細については、[TypeScript での違い](#differences-in-typescript)をご覧ください。

## ユースケース

- **スケジュール管理アシスタント**: ユーザーに代わって空き時間を検索し、今後の予定を一覧表示し、カレンダーの予定を作成または更新します。
- **メールのトリアージ**: Gmail メッセージの検索、読み取り、ラベル付け、下書きの作成を行ったり、ユーザーの確認後に返信を送信したりします。
- **ドキュメント生成**: Google ドキュメントやスライドのプレゼンテーションを作成し、エージェントが生成したコンテンツを入力します。
- **スプレッドシートの自動化**: ワークフローの一部として、Google スプレッドシートから範囲を読み取り、行を追加し、セルの値を更新します。
- **チャンネル管理**: YouTube の検索、チャンネルの動画や再生リストの一覧表示、コメントのモデレーションを行います。

## 前提条件

- [Google Cloud プロジェクト](https://developers.google.com/workspace/guides/create-project)。
- 使用する各ツールセットに対応する API（Google Calendar API や Gmail API など）がそのプロジェクトで有効になっていること。詳細については、[Google Workspace API を有効にする](https://developers.google.com/workspace/guides/enable-apis)をご覧ください。
- **ウェブ アプリケーション** タイプの OAuth 2.0 クライアント ID とクライアント シークレット。詳細については、[OAuth 2.0 認証情報を取得する](https://developers.google.com/identity/protocols/oauth2/web-server#creatingcred)をご覧ください。
- [ADK ウェブインターフェース](/ja/runtime/web-interface/)でテストする場合は、OAuth クライアントの **承認済みのリダイレクト URI（Authorized redirect URIs）** にウェブインターフェースの URL（例: `http://localhost:8000/dev-ui/`）を追加してください。

## インストール

=== "Python"

    ツールセットは、`tools` extra に含まれる Google API Python クライアントに依存しています。

    ```bash
    pip install "google-adk[tools]"
    ```

=== "TypeScript"

    ツールセットはコアパッケージの一部であり、ADK TypeScript v2.4.0 以降が必要です。

    ```bash
    npm install @google/adk
    ```

## エージェントでの使用

OAuth クライアント認証情報を使用してツールセットを作成し、エージェントの `tools` リストに追加します。ツールフィルタ（tool filter）を使用して、エージェントが必要とするツールのみを公開してください。これらの API のほとんどには数十個のメソッドがあり、ツールリストを短く保つことでモデルのコンテキストを小さく抑え、ツール選択の精度を高めることができます。

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

エージェントがこれらのツールのいずれかを初めて呼び出すと、ADK はユーザーに Google でログインしてアクセス権を付与するよう求めます。ADK ウェブインターフェースでは、同意画面がポップアップウィンドウで開きます。独自のクライアントアプリケーションを構築する場合は、アプリケーション側でこのリクエストを処理する必要があります。詳細については、[ツールによる認証](/ja/tools-custom/authentication/)をご覧ください。

ツール名は、ディスカバリドキュメント内のメソッド ID に基づき、スネークケース（snake_case）の `<api>_<resource>_<method>` パターンに従います。たとえば、Calendar API のメソッド `calendar.events.quickAdd` は `calendar_events_quick_add` ツールになります。名前は Python と TypeScript で共通です。

## 利用可能なツールセット

Python では、`google.adk.tools.google_api_tool` からツールセットをインポートします。TypeScript では、`@google/adk` からインポートします。

ツールセット | API | ツール数
------- | --- | -----
`CalendarToolset` | [Google Calendar API v3](https://developers.google.com/workspace/calendar/api/v3/reference) | 38
`DocsToolset` | [Google Docs API v1](https://developers.google.com/workspace/docs/api/reference/rest) | 3
`GmailToolset` | [Gmail API v1](https://developers.google.com/workspace/gmail/api/reference/rest) | 79
`SheetsToolset` | [Google Sheets API v4](https://developers.google.com/workspace/sheets/api/reference/rest) | 17
`SlidesToolset` | [Google Slides API v1](https://developers.google.com/workspace/slides/api/reference/rest) | 5
`YoutubeToolset` | [YouTube Data API v3](https://developers.google.com/youtube/v3/docs) | 83

ツール数は、`google-api-python-client` 2.x を使用した ADK Python v2.13.0、および ADK TypeScript v2.4.0 時点のものです。Python は `google-api-python-client` に同梱されているディスカバリドキュメントを読み取ります。TypeScript は、エージェントがツールセットのツールを初めてロードする際に、Google API Discovery Service からディスカバリドキュメントをダウンロードします。どちらの言語でも、基盤となる API でメソッドが追加または削除されるとツール数は変化します。

各ツールセットは同じコンストラクタ引数を受け取ります。Python はキーワード引数として受け取り、TypeScript は 1 つのオプションオブジェクトのプロパティとして受け取ります。

Python | TypeScript | 説明
------ | ---------- | -----------
`client_id` | `clientId` | ユーザーのログインフローに使用される OAuth 2.0 クライアント ID。
`client_secret` | `clientSecret` | ユーザーのログインフローに使用される OAuth 2.0 クライアント シークレット。
`tool_filter` | `toolFilter` | 公開するツール名のリスト、または各ツールを受け取って公開する場合に Python では `True`、TypeScript では `true` を返す述語（predicate）関数。
`service_account` | サポート対象外 | ユーザーの代わりにサービスアカウントとして認証するための `ServiceAccount`。[サービスアカウントで認証する](#authenticate-with-a-service-account)をご覧ください。
`tool_name_prefix` | サポート対象外 | すべてのツール名の先頭にアンダースコア（`_`）付きで追加されるプレフィックス。

### Calendar

`CalendarToolset` は、カレンダー、予定、アクセス制御リスト（ACL）、および空き 시간（free/busy）クエリを管理します。

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

ツール | 説明
---- | -----------
`calendar_events_list` | カレンダー上の予定を一覧表示します（オプションで時間範囲や検索クエリを指定可能）。
`calendar_events_get` | 1 件の予定を返します。
`calendar_events_insert` | 予定を作成します。
`calendar_events_quick_add` | 「明日の正午にランチ」のようなテキスト文字列から予定を作成します。
`calendar_events_patch` | 予定のフィールドを更新します。
`calendar_events_delete` | 予定を削除します。
`calendar_freebusy_query` | カレンダーのセットに対する空き時間情報を返します。
`calendar_calendar_list_list` | ユーザーのカレンダーリストにあるカレンダーを一覧表示します。

その他のツールは、`acl`、`calendars`、`calendar_list`、`colors`、`settings`、および通知チャンネルを扱います。

### Docs

`DocsToolset` は、Google ドキュメントの作成、読み取り、および編集を行います。

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

ツール | 説明
---- | -----------
`docs_documents_create` | 指定されたタイトルで空白のドキュメントを作成します。
`docs_documents_get` | ドキュメントのコンテンツと構造を返します。
`docs_documents_batch_update` | テキストの挿入、テキストの置換、表の追加などの編集をドキュメントに適用します。

### Gmail

`GmailToolset` は、メッセージ、スレッド、下書き、ラベル、およびメールボックス設定の読み取りと管理を行います。

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

ツール | 説明
---- | -----------
`gmail_users_messages_list` | メッセージを一覧表示します（`is:unread` などのオプションの Gmail 検索クエリを指定可能）。
`gmail_users_messages_get` | 1 件のメッセージを返します。
`gmail_users_messages_send` | メッセージを送信します。
`gmail_users_messages_modify` | メッセージのラベルを追加または削除します。
`gmail_users_threads_list` | 会話スレッドを一覧表示します。
`gmail_users_threads_get` | スレッド内のすべてのメッセージを返します。
`gmail_users_drafts_create` | 下書きを作成します。
`gmail_users_labels_list` | メールボックス内のラベルを一覧表示します。

Gmail ツールは `user_id` パラメータを受け取ります。ログイン中のユーザーには `me` を使用するようエージェントに指示してください。その他のツールは、履歴、添付ファイル、およびフィルタ、転送、不在時自動返信などのメールボックス設定を扱います。

### Sheets

`SheetsToolset` は、スプレッドシートの値の読み書きやスプレッドシートの構造の変更を行います。

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

ツール | 説明
---- | -----------
`sheets_spreadsheets_create` | スプレッドシートを作成します。
`sheets_spreadsheets_get` | シート名やプロパティなどのスプレッドシートのメタデータを返します。
`sheets_spreadsheets_batch_update` | シートの追加やセルの書式設定など、構造の変更を適用します。
`sheets_spreadsheets_values_get` | `Sheet1!A1:D10` などの範囲内の値を返します。
`sheets_spreadsheets_values_batch_get` | 複数の範囲内の値を返します。
`sheets_spreadsheets_values_append` | 範囲内のデータの最終行の後に新しい行を追加します。
`sheets_spreadsheets_values_update` | 範囲に値を書き込みます。
`sheets_spreadsheets_values_clear` | 範囲内の値を消去します。

### Slides

`SlidesToolset` は、Google スライドのプレゼンテーションの作成、読み取り、および編集を行います。

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

ツール | 説明
---- | -----------
`slides_presentations_create` | 空白のプレゼンテーションを作成します。
`slides_presentations_get` | プレゼンテーションのコンテンツを返します。
`slides_presentations_batch_update` | スライド、図形、テキスト、画像の追加などの編集を適用します。
`slides_presentations_pages_get` | 1 枚のスライドを返します。
`slides_presentations_pages_get_thumbnail` | 1 枚のスライドのサムネイル画像 URL を返します。

### YouTube

`YoutubeToolset` は、YouTube の検索や、チャンネルの動画、再生リスト、コメント、ライブ配信の管理を行います。

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

ツール | 説明
---- | -----------
`youtube_search_list` | 動画、チャンネル、再生リストを検索します。
`youtube_videos_list` | 動画の詳細と統計情報を返します。
`youtube_channels_list` | チャンネルの詳細を返します。
`youtube_playlists_list` | 再生リストを一覧表示します。
`youtube_playlist_items_list` | 再生リスト内の動画を一覧表示します。
`youtube_comment_threads_list` | 動画またはチャンネルのコメントスレッドを一覧表示します。
`youtube_comments_set_moderation_status` | コメントを承認、拒否、または確認待ちとして保留します。
`youtube_subscriptions_list` | 登録チャンネルを一覧表示します。

その他のツールは、字幕、チャンネルセクション、ライブ配信とストリーム、ライブチャット、およびサムネイルを扱います。

## 認証

ツールセットは OAuth 2.0 を使用し、ログイン中のユーザーとして Google API を呼び出します。Python では、ツールセットはサービスアカウントとして認証することもできます。次のセクションでは、各方法の設定手順と、ツールセットがリクエストする OAuth スコープについて説明します。

### OAuth 2.0 でユーザーを認証する

クライアント ID とクライアント シークレットを渡すと、各ツール呼び出しはログイン中のユーザーとして実行されます。ADK は、ツールが初めてトークンを必要としたときに OAuth 2.0 認可コードフローを開始し、取得した認証情報を保存して、セッション内の以降の呼び出しで再利用します。

ツールセットの作成後にクライアント認証情報を設定することもできます。

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

### OAuth スコープ {#oauth-scopes}

ツールセットは 1 つの OAuth スコープ（API のディスカバリドキュメントで最初にリストされているスコープ）をリクエストします。

Python では、`google-api-python-client` 2.x のディスカバリドキュメントにおいて、次のフルアクセススコープが最初にリストされています。

ツールセット | デフォルトスコープ
------- | -------------
`CalendarToolset` | `https://www.googleapis.com/auth/calendar`
`DocsToolset` | `https://www.googleapis.com/auth/documents`
`GmailToolset` | `https://mail.google.com/`
`SheetsToolset` | `https://www.googleapis.com/auth/drive`
`SlidesToolset` | `https://www.googleapis.com/auth/drive`
`YoutubeToolset` | `https://www.googleapis.com/auth/youtube`

ツールフィルタはエージェントが呼び出せるツールを制限しますが、ユーザーが付与するスコープを縮小するものではありません。ユーザーに表示される同意画面を確認し、ツールフィルタとエージェントの指示（instruction）によって破壊的なツールを制限してください。

!!! warning "TypeScript でのスコープ選択"
    TypeScript では、ツールセットは実行時にダウンロードしたディスカバリドキュメントから最初のスコープを取得します。Google API Discovery Service はスコープを固定された順序で返さないため、リクエストされるスコープは実行ごとに変わる可能性があり、使用するツールをカバーしない読み取り専用または狭いスコープになる場合があります。たとえば、`CalendarToolset` が `calendar_events_list` を許可しない `https://www.googleapis.com/auth/calendar.acls.readonly` をリクエストすることがあります。スコープがツールをカバーしていない場合、API はスコープ不足（insufficient-scope）エラーで呼び出しを拒否します。ADK TypeScript v2.4.0 には、スコープを設定または追加するオプションはありません。

Python で追加のスコープをリクエストするには、`GoogleApiToolset` を直接作成して `additional_scopes` を渡します。ツールセットはこれらをデフォルトスコープに追加します。

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

### サービスアカウントで認証する {#authenticate-with-a-service-account}

<div class="language-support-tag">
  <span class="lst-supported">ADK でのサポート</span><span class="lst-python">Python v1.0.0</span>
</div>

ユーザーの代わりにサービスアカウントとして API を呼び出すには、`ServiceAccount` を渡します。サービスアカウントは、サービスアカウントのメールアドレスと共有されたスプレッドシートやドキュメントなど、そのアカウントと共有されたデータにのみアクセスできます。`scopes` には API 呼び出しに必要なスコープを設定してください。

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

キーファイルの代わりにアプリケーションのデフォルト認証情報（Application Default Credentials）を使用するには、`ServiceAccount(use_default_credential=True, scopes=[...])` を渡します。

## 構成

ツールセットが公開するツールや、モデルから見えるツール名を変更できます。述語関数を使用してルールベースでツールを選択したり、Python ではツール名にプレフィックスを追加して他のソースのツールとの名前の衝突を回避したりできます。

### ツール名にプレフィックスを追加する

<div class="language-support-tag">
  <span class="lst-supported">ADK でのサポート</span><span class="lst-python">Python v1.0.0</span>
</div>

エージェントが複数のソースからのツールを使用する際に名前の衝突を避けるには、`tool_name_prefix` を設定します。ツールセットは、モデルから見えるすべてのツール名の先頭にプレフィックスとアンダースコア（`_`）を追加します。`tool_filter` の値にはプレフィックスなしの名前を使用します。

```python
calendar_toolset = CalendarToolset(
    client_id=os.environ["OAUTH_CLIENT_ID"],
    client_secret=os.environ["OAUTH_CLIENT_SECRET"],
    tool_filter=["calendar_events_list"],
    tool_name_prefix="google",
)
# モデルからはツールが "google_calendar_events_list" として見えます。
```

### 述語（predicate）でツールをフィルタリングする

名前ではなくルールでツールを選択するには、ツールフィルタとして関数を渡します。関数は各ツールとオプションの読み取り専用コンテキストを受け取ります。たとえば、読み取り操作のみを公開するには次のようにします。

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

ツールセットの作成後に、Python の `set_tool_filter()` または TypeScript の `setToolFilter()` を使用してフィルタを置き換えることもできます。

## 他の Google API を使用する

`GoogleApiToolset` は、ディスカバリドキュメントを持つ任意の Google API のツールを生成します。[APIs Explorer](https://developers.google.com/apis-explorer) に記載されている API 名とバージョンを渡してください。たとえば、Google Drive API を使用する場合は次のようにします。

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

Python では、`GoogleApiToolset` は次のキーワード専用引数も受け取ります。

引数 | 説明
-------- | -----------
`additional_scopes` | デフォルトスコープと合わせてリクエストする追加の OAuth スコープ。
`additional_headers` | ツールセットが送信するすべてのリクエストに追加される HTTP ヘッダー。
`discovery_url` | Google API クライアントの `build()` 関数に `discoveryServiceUrl` として渡されるカスタムディスカバリサービス URL。

## TypeScript での違い {#differences-in-typescript}

ADK TypeScript v2.4.0 の TypeScript ツールセットは、Python ツールセットと次の点で異なります。

- **実験的機能**: クラスは実験的機能であり、各クラスを最初に作成した際に警告がログに記録されます。
- **ディスカバリドキュメント**: エージェントがツールを初めてロードする際に、ツールセットが `https://www.googleapis.com/discovery/v1/apis` からディスカバリドキュメントをダウンロードするため、エージェントからそのエンドポイントへのネットワークアクセスが必要です。
- **スコープ**: デフォルトスコープはダウンロードされたディスカバリドキュメント内の最初のスコープであり、実行ごとに変わる可能性があります。詳細については、[OAuth スコープ](#oauth-scopes)をご覧ください。
- **サポート対象外**: サービスアカウント認証、ツール名のプレフィックス、`additional_scopes`、`additional_headers`、および `discovery_url`。

## 追加リソース

- [ツールによる認証](/ja/tools-custom/authentication/)
- [Google API ツール用 ADK Python サンプルエージェント](https://github.com/google/adk-python/tree/main/contributing/samples/integrations/google_api)
- [ADK Python `GoogleApiToolset` ソースコード](https://github.com/google/adk-python/blob/main/src/google/adk/tools/google_api_tool/google_api_toolset.py)
- [Google API ツールセット用 ADK TypeScript オフラインサンプル](https://github.com/google/adk-js/blob/adk-v2.4.0/samples/tools/google_api_tool/agent.ts)
- [ADK TypeScript `GoogleApiToolset` ソースコード](https://github.com/google/adk-js/blob/adk-v2.4.0/core/src/tools/google_api_tool/google_api_toolset.ts)
- [Google API Discovery Service](https://developers.google.com/discovery)
