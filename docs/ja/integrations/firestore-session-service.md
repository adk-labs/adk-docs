---
catalog_title: Firestore Session Service
catalog_description: Firestore を使った ADK エージェントのセッション状態管理
catalog_icon: /integrations/assets/firestore-session.jpg
catalog_tags: ["data", "google"]
---

# Firestore を使ったセッション状態管理

<div class="language-support-tag">
  <span class="lst-supported">ADK でサポート</span><span class="lst-java">Java</span>
</div>

[Google Cloud Firestore](https://cloud.google.com/firestore) は、クライアントサイドおよびサーバーサイド開発向けにデータを保存・同期できる、柔軟でスケーラブルな NoSQL クラウドデータベースです。
ADK は Firestore を使って永続的なエージェントセッション状態を管理するネイティブ統合を提供し、会話履歴を失うことなく連続したマルチターン会話を実現します。

## ユースケース

- **カスタマーサポートエージェント**: 長時間続くサポートチケット全体でコンテキストを保持し、複数セッションにまたがって過去のトラブルシュート手順や好みを記憶させます。
- **パーソナライズドアシスタント**: ユーザーについての知識を時間とともに蓄積し、過去の会話に基づいて将来のやり取りを個別化します。
- **マルチモーダルワークフロー**: 組み込みの GCS アーティファクトストレージを活用し、画像・動画・音声をテキスト会話と一緒にシームレスに扱います。
- **エンタープライズチャットボット**: 大規模な企業環境に適した本番レベルの永続化を備えた、高信頼な対話型 AI アプリケーションを展開します。

## 前提条件

- Firestore が有効な [Google Cloud プロジェクト](https://cloud.google.com/)
- Google Cloud プロジェクト内の [Firestore データベース](https://cloud.google.com/firestore/docs/setup)
- 環境で設定済みの適切な [Google Cloud 認証情報](https://cloud.google.com/docs/authentication/provide-credentials-adc)

## 依存関係のインストール

!!! note

    互換性を確保するため、`google-adk` と `google-adk-firestore-session-service` には同じバージョンを使用してください。

次の依存関係を `pom.xml` (Maven) または `build.gradle` (Gradle) に追加し、`1.0.0` は対象の ADK バージョンに置き換えてください。

### Maven

```xml
<dependencies>
    <!-- ADK Core -->
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>1.0.0</version>
    </dependency>
    <!-- Firestore Session Service -->
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk-firestore-session-service</artifactId>
        <version>1.0.0</version>
    </dependency>
</dependencies>
```

### Gradle

```gradle
dependencies {
    // ADK Core
    implementation 'com.google.adk:google-adk:1.0.0'
    // Firestore Session Service
    implementation 'com.google.adk:google-adk-firestore-session-service:1.0.0'
}
```

## 例: Firestore セッション管理付きエージェント

`FirestoreDatabaseRunner` を使って、エージェントと Firestore バックのセッション管理をカプセル化します。
次の例は、カスタムセッション ID を使ってターン間の会話コンテキストを記憶するシンプルなアシスタントエージェントの完全なセットアップです。

```java
import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.RunConfig;
import com.google.adk.runner.FirestoreDatabaseRunner;
import com.google.cloud.firestore.Firestore;
import com.google.cloud.firestore.FirestoreOptions;
import io.reactivex.rxjava3.core.Flowable;
import java.util.Map;
import com.google.adk.sessions.FirestoreSessionService;
import com.google.adk.sessions.Session;
import com.google.adk.tools.Annotations.Schema;
import com.google.adk.tools.FunctionTool;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import com.google.adk.events.Event;
import java.util.Scanner;
import static java.nio.charset.StandardCharsets.UTF_8;

public class YourAgentApplication {

    public static void main(String[] args) {
        System.out.println("Starting YourAgentApplication...");

        RunConfig runConfig = RunConfig.builder().build();
        String appName = "hello-time-agent";

        BaseAgent timeAgent = initAgent();

        // Firestore の初期化
        FirestoreOptions firestoreOptions = FirestoreOptions.getDefaultInstance();
        Firestore firestore = firestoreOptions.getService();

        // FirestoreDatabaseRunner を使ってセッション状態を保持
        FirestoreDatabaseRunner runner = new FirestoreDatabaseRunner(
                timeAgent,
                appName,
                firestore
        );

        // 新しいセッションを作成するか、既存のセッションを読み込む
        Session session = new FirestoreSessionService(firestore)
                .createSession(appName, "user1234", null, "12345")
                .blockingGet();

        // 対話型 CLI を開始
        try (Scanner scanner = new Scanner(System.in, UTF_8)) {
            while (true) {
                System.out.print("\\nYou > ");
                String userInput = scanner.nextLine();
                if ("quit".equalsIgnoreCase(userInput)) {
                    break;
                }

                Content userMsg = Content.fromParts(Part.fromText(userInput));
                Flowable<Event> events = runner.runAsync(session.userId(), session.id(), userMsg, runConfig);

                System.out.print("\\nAgent > ");
                events.blockingForEach(event -> {
                    if (event.finalResponse()) {
                        System.out.println(event.stringifyContent());
                    }
                });
            }
        }
    }

    /** Mock tool implementation */
    @Schema(description = "指定した都市の現在時刻を取得します")
    public static Map<String, String> getCurrentTime(
        @Schema(name = "city", description = "時刻を取得する都市名") String city) {
        return Map.of(
            "city", city,
            "time", "The time is 10:30am."
        );
    }

    private static BaseAgent initAgent() {
        return LlmAgent.builder()
            .name("hello-time-agent")
            .description("指定した都市の現在時刻を伝えます")
            .instruction("""
                あなたは都市の現在時刻を伝える便利なアシスタントです。
                この目的には 'getCurrentTime' ツールを使用してください。
                """)
            .model("gemini-3.1-pro-preview")
            .tools(FunctionTool.create(YourAgentApplication.class, "getCurrentTime"))
            .build();
    }
}
```

## 構成

!!! note

    Firestore Session Service は properties ファイルによる設定をサポートします。これにより、専用の Firestore
    データベースを簡単に対象にし、エージェントのセッションデータを保存するカスタムコレクション名を定義できます。

独自の Firestore property 設定を提供して ADK アプリケーションを Firestore session service に合わせて構成できます。
そうしない場合、ライブラリはデフォルト設定を使用します。

### 環境別構成

ライブラリはデフォルト設定よりも環境別の property ファイルを優先します。解決順序は次のとおりです。

1. **環境変数オーバーライド**: まず `env` という環境変数を確認します。これが設定されている場合 (例: `env=dev`)、`adk-firestore-{env}.properties`
   に一致する property ファイルを読み込みます (例: `adk-firestore-dev.properties`)。
2. **デフォルトへのフォールバック**: `env` 変数が設定されていない、または環境別ファイルが見つからない場合は、
   `adk-firestore.properties` を読み込みます。

サンプル property 設定:

```properties
# セッションデータ保存用 Firestore コレクション名
firebase.root.collection.name=adk-session
# アーティファクト保存用 Google Cloud Storage バケット名
gcs.adk.bucket.name=your-gcs-bucket-name
# キーワード抽出の stop words
keyword.extraction.stopwords=a,about,above,after,again,against,all,am,an,and,any,are,aren't,as,at,be,because,been,before,being,below,between,both,but,by,can't,cannot,could,couldn't,did,didn't,do,does,doesn't,doing,don't,down,during,each,few,for,from,further,had,hadn't,has,hasn't,have,haven't,having,he,he'd,he'll,he's,her,here,here's,hers,herself,him,himself,his,how,i,i'd,i'll,i'm,i've,if,in,into,is
```

!!! important

    `FirestoreDatabaseRunner` には `gcs.adk.bucket.name` プロパティの定義が必要です。
    これは runner が内部で `GcsArtifactService` を初期化し、マルチモーダルアーティファクト保存を処理するためです。
    このプロパティがないか空の場合、アプリケーションは起動時に `RuntimeException` を送出します。
    これは、エージェントが生成または処理する画像、動画、音声ファイルなどのアーティファクトを保存するために使用されます。

## リソース

- [Firestore Session Service](https://github.com/google/adk-java/tree/main/contrib/firestore-session-service):
  Firestore Session Service のソースコードです。
- [Spring Boot Google ADK + Firestore Example](https://github.com/mohan-ganesh/spring-boot-google-adk-firestore):
  Cloud Firestore を使った Java ベースの Google ADK エージェントアプリケーション構築の例です。
- [Firestore Session Service - DeepWiki](https://deepwiki.com/google/adk-java/4.3-firestore-session-service):
  Google ADK for Java における Firestore 統合の詳細な説明です。
