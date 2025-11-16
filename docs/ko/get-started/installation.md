# ADK 설치

=== "Python"

    ## 가상 환경 생성 및 활성화

    [venv](https://docs.python.org/3/library/venv.html)를 사용하여 가상 Python 환경을 만드는 것이 좋습니다.

    ```shell
    python -m venv .venv
    ```

    이제 운영 체제 및 환경에 적합한 명령을 사용하여 가상 환경을 활성화할 수 있습니다.

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

    ## 새 Go 모듈 만들기

    새 프로젝트를 시작하는 경우 새 Go 모듈을 만들 수 있습니다.

    ```shell
    go mod init example.com/my-agent
    ```

    ## ADK 설치

    프로젝트에 ADK를 추가하려면 다음 명령을 실행합니다.

    ```shell
    go get google.golang.org/adk
    ```

    이렇게 하면 ADK가 `go.mod` 파일에 종속성으로 추가됩니다.

    (선택 사항) `go.mod` 파일에서 `google.golang.org/adk` 항목을 확인하여 설치를 확인합니다.

=== "Java"

    maven 또는 gradle을 사용하여 `google-adk` 및 `google-adk-dev` 패키지를 추가할 수 있습니다.

    `google-adk`는 핵심 Java ADK 라이브러리입니다. Java ADK에는 에이전트를 원활하게 실행할 수 있는 플러그형 예제 SpringBoot 서버도 함께 제공됩니다. 이 선택적 패키지는 `google-adk-dev`의 일부로 제공됩니다.

    maven을 사용하는 경우 `pom.xml`에 다음을 추가합니다.

    ```xml title="pom.xml"
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion>

        <groupId>com.example.agent</groupId>
        <artifactId>adk-agents</artifactId>
        <version>1.0-SNAPSHOT</version>

        <!-- 사용할 Java 버전을 지정합니다. -->
        <properties>
            <maven.compiler.source>17</maven.compiler.source>
            <maven.compiler.target>17</maven.compiler.target>
            <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        </properties>

        <dependencies>
            <!-- ADK 핵심 종속성 -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk</artifactId>
                <version>0.3.0</version>
            </dependency>
            <!-- 에이전트를 디버그하기 위한 ADK 개발 웹 UI -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk-dev</artifactId>
                <version>0.3.0</version>
            </dependency>
        </dependencies>

    </project>
    ```

    참조용 [전체 pom.xml](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run/pom.xml) 파일은 다음과 같습니다.

    gradle을 사용하는 경우 build.gradle에 종속성을 추가합니다.

    ```title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.2.0'
        implementation 'com.google.adk:google-adk-dev:0.2.0'
    }
    ```

    Gradle이 `-parameters`를 `javac`에 전달하도록 구성해야 합니다. (또는 `@Schema(name = "...")`를 사용하십시오.)


## 다음 단계

* [**빠른 시작**](quickstart.md)으로 첫 번째 에이전트 만들기를 시도해 보십시오.
