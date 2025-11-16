# ADK 설치하기

=== "Python"

    ## 가상 환경 생성 및 활성화

    [venv](https://docs.python.org/3/library/venv.html)를 사용하여 Python 가상 환경을 만드는 것을 권장합니다:

    ```shell
    python -m venv .venv
    ```

    이제 운영체제와 환경에 맞는 명령어를 사용하여 가상 환경을 활성화할 수 있습니다:

    ```
    # Mac / Linux
    source .venv/bin/activate

    # Windows CMD:
    .venv\Scripts\activate.bat

    # Windows PowerShell:
    .venv\Scripts\Activate.ps1
    ```

    ### ADK 설치

    ```bash
    pip install google-adk
    ```

    (선택 사항) 설치 확인:

    ```bash
    pip show google-adk
    ```

=== "Go"

    ## 새로운 Go 모듈 생성하기

    새 프로젝트를 시작하는 경우, 다음과 같이 새로운 Go 모듈을 생성할 수 있습니다:

    ```shell
    go mod init example.com/my-agent
    ```

    ## ADK 설치

    프로젝트에 ADK를 추가하려면 다음 명령어를 실행하세요:

    ```shell
    go get google.golang.org/adk
    ```

    이 명령어는 `go.mod` 파일에 ADK를 의존성(dependency)으로 추가합니다.

    (선택 사항) `go.mod` 파일에 `google.golang.org/adk` 항목이 있는지 확인하여 설치를 검증할 수 있습니다.

=== "Java"

    maven 또는 gradle을 사용하여 `google-adk`와 `google-adk-dev` 패키지를 추가할 수 있습니다.

    `google-adk`는 핵심 Java ADK 라이브러리입니다. 또한 Java ADK는 에이전트를 원활하게 실행할 수 있도록 플러그인 방식(pluggable)의 예제 SpringBoot 서버와 함께 제공됩니다. 이 선택적
    패키지는 `google-adk-dev`의 일부로 포함되어 있습니다.

    maven을 사용하는 경우, 다음 내용을 `pom.xml`에 추가하세요:

    ```xml title="pom.xml"
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion>

        <groupId>com.example.agent</groupId>
        <artifactId>adk-agents</artifactId>
        <version>1.0-SNAPSHOT</version>

        <!-- 사용할 Java 버전을 명시합니다 -->
        <properties>
            <maven.compiler.source>17</maven.compiler.source>
            <maven.compiler.target>17</maven.compiler.target>
            <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        </properties>

        <dependencies>
            <!-- ADK 핵심 의존성 -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk</artifactId>
                <version>0.3.0</version>
            </dependency>
            <!-- 에이전트 디버깅을 위한 ADK 개발용 웹 UI -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk-dev</artifactId>
                <version>0.3.0</version>
            </dependency>
        </dependencies>

    </project>
    ```

    참고용 [전체 pom.xml](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run/pom.xml) 파일은 여기 있습니다.

    gradle을 사용하는 경우, build.gradle에 다음 의존성을 추가하세요:

    ```title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.2.0'
        implementation 'com.google.adk:google-adk-dev:0.2.0'
    }
    ```

    또한 Gradle이 `javac`에 `-parameters`를 전달하도록 설정해야 합니다. (또는 `@Schema(name = "...")`를 사용하세요).


## 다음 단계

* [**빠른 시작**](quickstart.md) 가이드를 따라 첫 에이전트를 만들어 보세요.