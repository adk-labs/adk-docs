---
catalog_title: Firestore Session Service
catalog_description: Firestore를 사용한 ADK 에이전트용 세션 상태 관리
catalog_icon: /integrations/assets/firestore-session.jpg
catalog_tags: ["data", "google"]
---

# Firestore를 사용한 세션 상태 관리

<div class="language-support-tag">
  <span class="lst-supported">ADK에서 지원</span><span class="lst-java">Java</span>
</div>

[Google Cloud Firestore](https://cloud.google.com/firestore)는 클라이언트 및 서버 측 개발을 위해 데이터를 저장하고 동기화하는 유연하고 확장 가능한 NoSQL 클라우드 데이터베이스입니다.
ADK는 Firestore를 사용해 지속적인 에이전트 세션 상태를 관리하는 기본 통합을 제공하며, 대화 기록을 잃지 않고도 연속적인 다중 턴 대화를 지원합니다.

## 사용 사례

- **고객 지원 에이전트**: 긴 지원 티켓 전반에서 컨텍스트를 유지하여, 여러 세션에 걸쳐 이전 문제 해결 단계와 선호도를 기억하도록 합니다.
- **개인화된 어시스턴트**: 사용자에 대한 지식을 시간이 지나며 축적해, 과거 대화를 기반으로 이후 상호작용을 개인화합니다.
- **멀티모달 워크플로**: 내장된 GCS 아티팩트 저장소를 활용해 이미지, 비디오, 오디오를 텍스트 대화와 함께 매끄럽게 처리합니다.
- **엔터프라이즈 챗봇**: 대규모 엔터프라이즈 환경에 적합한 프로덕션급 지속성을 갖춘 매우 신뢰할 수 있는 대화형 AI 애플리케이션을 배포합니다.

## 사전 준비 사항

- Firestore가 활성화된 [Google Cloud 프로젝트](https://cloud.google.com/)
- Google Cloud 프로젝트에 [Firestore 데이터베이스](https://cloud.google.com/firestore/docs/setup)
- 환경에 구성된 적절한 [Google Cloud 자격 증명](https://cloud.google.com/docs/authentication/provide-credentials-adc)

## 의존성 설치

!!! note

    호환성을 보장하려면 `google-adk`와 `google-adk-firestore-session-service`에 같은 버전을 사용해야 합니다.

다음 의존성을 `pom.xml`(Maven) 또는 `build.gradle`(Gradle)에 추가하되, `1.0.0`은 대상 ADK 버전으로 바꿔 주세요.

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

## 예제: Firestore 세션 관리가 있는 에이전트

`FirestoreDatabaseRunner`를 사용해 에이전트와 Firestore 기반 세션 관리를 캡슐화합니다.
다음은 사용자 지정 세션 ID를 사용해 턴 사이의 대화 컨텍스트를 기억하는 간단한 어시스턴트 에이전트를 설정하는 전체 예제입니다.

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

        // Firestore 초기화
        FirestoreOptions firestoreOptions = FirestoreOptions.getDefaultInstance();
        Firestore firestore = firestoreOptions.getService();

        // FirestoreDatabaseRunner로 세션 상태를 유지
        FirestoreDatabaseRunner runner = new FirestoreDatabaseRunner(
                timeAgent,
                appName,
                firestore
        );

        // 새 세션을 만들거나 기존 세션을 불러오기
        Session session = new FirestoreSessionService(firestore)
                .createSession(appName, "user1234", null, "12345")
                .blockingGet();

        // 대화형 CLI 시작
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
    @Schema(description = "주어진 도시의 현재 시간을 가져옵니다")
    public static Map<String, String> getCurrentTime(
        @Schema(name = "city", description = "시간을 가져올 도시 이름") String city) {
        return Map.of(
            "city", city,
            "time", "The time is 10:30am."
        );
    }

    private static BaseAgent initAgent() {
        return LlmAgent.builder()
            .name("hello-time-agent")
            .description("지정한 도시의 현재 시간을 알려 줍니다")
            .instruction("""
                당신은 도시의 현재 시간을 알려 주는 유용한 어시스턴트입니다.
                이 목적에는 'getCurrentTime' 도구를 사용하세요.
                """)
            .model("gemini-3.1-pro-preview")
            .tools(FunctionTool.create(YourAgentApplication.class, "getCurrentTime"))
            .build();
    }
}
```

## 구성

!!! note

    Firestore Session Service는 properties 파일 구성을 지원합니다. 이를 통해 전용 Firestore
    데이터베이스를 쉽게 대상으로 지정하고, 에이전트 세션 데이터를 저장할 사용자 지정 컬렉션 이름을 정의할 수 있습니다.

자체 Firestore 속성 설정을 제공해 ADK 애플리케이션을 Firestore 세션 서비스에 맞게 구성할 수 있습니다.
그렇지 않으면 라이브러리는 기본 설정을 사용합니다.

### 환경별 구성

라이브러리는 기본 설정보다 환경별 속성 파일을 우선합니다. 해석 순서는 다음과 같습니다.

1. **환경 변수 재정의**: 먼저 `env`라는 환경 변수를 확인합니다. 이 변수가 설정되어 있으면(예: `env=dev`)
   `adk-firestore-{env}.properties` 템플릿과 일치하는 속성 파일을 로드합니다(예: `adk-firestore-dev.properties`).
2. **기본 대체값**: `env` 변수가 설정되지 않았거나 환경별 파일을 찾을 수 없으면
   `adk-firestore.properties`를 로드합니다.

샘플 속성 설정:

```properties
# 세션 데이터 저장용 Firestore 컬렉션 이름
firebase.root.collection.name=adk-session
# 아티팩트 저장용 Google Cloud Storage 버킷 이름
gcs.adk.bucket.name=your-gcs-bucket-name
# 키워드 추출용 stop words
keyword.extraction.stopwords=a,about,above,after,again,against,all,am,an,and,any,are,aren't,as,at,be,because,been,before,being,below,between,both,but,by,can't,cannot,could,couldn't,did,didn't,do,does,doesn't,doing,don't,down,during,each,few,for,from,further,had,hadn't,has,hasn't,have,haven't,having,he,he'd,he'll,he's,her,here,here's,hers,herself,him,himself,his,how,i,i'd,i'll,i'm,i've,if,in,into,is
```

!!! important

    `FirestoreDatabaseRunner`는 `gcs.adk.bucket.name` 속성이 정의되어 있어야 합니다.
    이는 runner가 내부적으로 `GcsArtifactService`를 초기화해 멀티모달 아티팩트 저장을 처리하기 때문입니다.
    이 속성이 없거나 비어 있으면 애플리케이션은 시작 시 `RuntimeException`을 발생시킵니다.
    이 저장소는 에이전트가 생성하거나 처리하는 이미지, 비디오, 오디오 파일 같은 아티팩트를 저장하는 데 사용됩니다.

## 리소스

- [Firestore Session Service](https://github.com/google/adk-java/tree/main/contrib/firestore-session-service):
  Firestore Session Service 소스 코드입니다.
- [Spring Boot Google ADK + Firestore Example](https://github.com/mohan-ganesh/spring-boot-google-adk-firestore):
  Cloud Firestore를 사용한 Java 기반 Google ADK 에이전트 애플리케이션 구축 예제입니다.
- [Firestore Session Service - DeepWiki](https://deepwiki.com/google/adk-java/4.3-firestore-session-service):
  Google ADK for Java의 Firestore 통합에 대한 자세한 설명입니다.
