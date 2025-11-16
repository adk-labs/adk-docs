# ADKのインストール

=== "Python"

    ## 仮想環境の作成と有効化

    [venv](https://docs.python.org/3/library/venv.html)を使用してPythonの仮想環境を作成することをお勧めします:

    ```shell
    python -m venv .venv
    ```

    次に、お使いのオペレーティングシステムと環境に応じた適切なコマンドで仮想環境を有効化します:

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

    (任意) インストールを確認:

    ```bash
    pip show google-adk
    ```

=== "Go"

    ## 新規Goモジュールの作成

    新しいプロジェクトを開始する場合は、新しいGoモジュールを作成します:

    ```shell
    go mod init example.com/my-agent
    ```

    ## ADKのインストール

    プロジェクトにADKを追加するには、次のコマンドを実行します:

    ```shell
    go get google.golang.org/adk
    ```

    これにより、ADKが依存関係として`go.mod`ファイルに追加されます。

    (任意) `go.mod`ファイルに`google.golang.org/adk`のエントリがあることを確認し、インストールを検証します。

=== "Java"

    mavenまたはgradleのいずれかを使用して、`google-adk`および`google-adk-dev`パッケージを追加できます。

    `google-adk`は、Java ADKのコアライブラリです。Java ADKには、エージェントをシームレスに実行するための、プラグイン可能なサンプルSpringBootサーバーも付属しています。このオプションの
    パッケージは、`google-adk-dev`の一部として含まれています。

    mavenを使用している場合は、以下を`pom.xml`に追加します:

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
            <!-- ADKのコア依存関係 -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk</artifactId>
                <version>0.3.0</version>
            </dependency>
            <!-- エージェントをデバッグするためのADK開発用Web UI -->
            <dependency>
                <groupId>com.google.adk</groupId>
                <artifactId>google-adk-dev</artifactId>
                <version>0.3.0</version>
            </dependency>
        </dependencies>

    </project>
    ```

    参考用の[完全なpom.xml](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run/pom.xml)ファイルはこちらです。

    gradleを使用している場合は、依存関係をbuild.gradleに追加します:

    ```title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.2.0'
        implementation 'com.google.adk:google-adk-dev:0.2.0'
    }
    ```

    また、Gradleが`javac`に`-parameters`を渡すように設定する必要があります。（または、`@Schema(name = "...")`を使用します）。


## 次のステップ

* [**クイックスタート**](quickstart.md)で最初のエージェントを作成してみましょう。