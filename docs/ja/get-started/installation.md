# ADKのインストール

=== "Python"

    ## 仮想環境の作成とアクティブ化

    [venv](https://docs.python.org/3/library/venv.html)を使用して仮想Python環境を作成することをお勧めします。

    ```shell
    python -m venv .venv
    ```

    次に、オペレーティングシステムと環境に適したコマンドを使用して仮想環境をアクティブ化できます。

    ```
    # Mac / Linux
    source .venv/bin/activate

    # Windows CMD:
    .venv\Scripts\activate.bat

    # Windows PowerShell:
    .venv\Scripts\Activate.ps1
    ```

    ### ADKのインストール

    ```bash
    pip install google-adk
    ```

    （オプション）インストールを確認します。

    ```bash
    pip show google-adk
    ```

=== "Go"

    ## 新しいGoモジュールの作成

    新しいプロジェクトを開始する場合は、新しいGoモジュールを作成できます。

    ```shell
    go mod init example.com/my-agent
    ```

    ## ADKのインストール

    プロジェクトにADKを追加するには、次のコマンドを実行します。

    ```shell
    go get google.golang.org/adk
    ```

    これにより、ADKが`go.mod`ファイルに依存関係として追加されます。

    （オプション）`go.mod`ファイルで`google.golang.org/adk`エントリを確認して、インストールを確認します。

=== "Java"

    mavenまたはgradleを使用して、`google-adk`および`google-adk-dev`パッケージを追加できます。

    `google-adk`は、コアのJava ADKライブラリです。Java ADKには、エージェントをシームレスに実行するためのプラグ可能なサンプルSpringBootサーバーも付属しています。このオプションのパッケージは、`google-adk-dev`の一部として存在します。

    mavenを使用している場合は、`pom.xml`に次を追加します。

    ```xml title="pom.xml"
    <?xml version="1.0" encoding="UTF-8"?>
    <project xmlns="http://maven.apache.org/POM/4.0.0"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
        <modelVersion>4.0.0</modelVersion>

        <groupId>com.example.agent</groupId>
        <artifactId>adk-agents</artifactId>
        <version>1.0-SNAPSHOT</version>

        <!-- 使用するJavaのバージョンを指定します -->
        <properties>
            <maven.compiler.source>17</maven.compiler.source>
            <maven.compiler.target>17</maven.compiler.target>
            <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        </properties>

        <dependencies>
            <!-- ADKコアの依存関係 -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk</artifactId>
                <version>0.3.0</version>
            </dependency>
            <!-- エージェントをデバッグするためのADK開発Web UI -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk-dev</artifactId>
                <version>0.3.0</version>
            </dependency>
        </dependencies>

    </project>
    ```

    参照用の[完全なpom.xml](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run/pom.xml)ファイルは次のとおりです。

    gradleを使用している場合は、build.gradleに依存関係を追加します。

    ```title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.2.0'
        implementation 'com.google.adk:google-adk-dev:0.2.0'
    }
    ```

    また、Gradleが`-parameters`を`javac`に渡すように構成する必要があります。（または、`@Schema(name = "...")`を使用します）。


## 次のステップ

* [**クイックスタート**](quickstart.md)で最初のエージェントを作成してみてください
