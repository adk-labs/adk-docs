# ADK 2.0 Alpha へようこそ

!!! example "Alpha リリース"

    ADK 2.0 は Alpha リリースであり、以前の ADK バージョンと併用する際に
    互換性を壊す変更が発生する可能性があります。プロダクション環境のように
    後方互換性が必要な場合は ADK 2.0 を使用しないでください。このリリースを
    ぜひ試していただき、
    [フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)
    をお寄せください。

ADK 2.0 は高度な AI エージェントを構築するための強力なツールを導入し、
より高い制御性、予測可能性、信頼性をもって難しいタスクを実行できるように
エージェントを構造化するのに役立ちます。ADK 2.0 は Python 向け Alpha
リリースとして提供され、次の主要機能を含みます。

- [**グラフベースのワークフロー**](/ja/workflows/): タスクの
  ルーティングと実行方法をより細かく制御できる、決定論的なエージェント
  ワークフローを構築します。
- [**協調エージェント**](/ja/workflows/collaboration/):
  コーディネーターエージェントと複数のサブエージェントが連携する複雑な
  エージェントアーキテクチャを構築します。
- [**動的ワークフロー**](/ja/workflows/dynamic/): 反復ループや
  複雑な意思決定分岐を含む、より高度なワークフローをコードベースのロジックで
  構築します。

詳しくは上記のリンク先を確認し、ADK 2.0 による新しいエージェント構築方法を
試してみてください。

## ADK 1.0 との互換性

ADK 2.0 は ADK 1.x リリースで開発されたエージェントとの互換性を保つように
設計されています。しかし、ADK 1.x で構築されたエージェントの数と多様性を
考えると、特に高度で機能豊富なエージェント実装では、ADK 2.0 上で
非互換性が見つかる可能性があります。現在の pre-GA 期間中にこうした問題を
特定できるよう、ご協力をお願いします。ADK 1.0 から ADK 2.0 への移行で
見つけた非互換性は
[issue tracker](https://github.com/google/adk-python/issues/new?template=bug_report.md&labels=v2)
を通じて報告してください。

!!! danger "警告: ADK 2.0 と ADK 1.0 のデータ保存システムを混在させないでください"

    ADK 2.0 プロジェクトで永続ストレージを使用する場合は、**セッション
    ストレージ、メモリシステム、評価データなどを含め、ADK 2.0 プロジェクトが
    ADK 1.0 プロジェクトとストレージを共有しないようにしてください。**
    共有するとデータが失われたり、ADK 1.0 プロジェクトで利用できなくなったり
    する可能性があります。

## ADK 2.0 をインストールする {#install}

ADK 2.0 は pre-GA リリースとして提供されているため、自動ではインストール
されません。インストール時に明示的に選択する必要があります。このバージョンの
システム要件は次のとおりです。

* **Python 3.11** 以上
* パッケージのインストールに必要な `pip`

ADK 2.0 をインストールするには、次の手順に従ってください。

1. Python 仮想環境を有効にします。以下の手順を参照してください。
1. 現在の pre-GA バージョンの ADK 2.0 を選択するため、`--pre` を付けて
   `pip` でパッケージをインストールします。

   ```bash
   pip install google-adk --pre
   ```

??? tip "推奨: Python 仮想環境を作成して有効化する"

    Python 仮想環境を作成します。

    ```shell
    python -m venv .venv
    ```

    Python 仮想環境を有効化します。

    === "Windows CMD"

        ```console
        .venv\Scripts\activate.bat
        ```

    === "Windows Powershell"

        ```console
        .venv\Scripts\Activate.ps1
        ```

    === "MacOS / Linux"

        ```bash
        source .venv/bin/activate
        ```

!!! note "注: 既存の ADK 1.0 プロジェクトを更新する場合"

    Python 環境にすでに ADK 1.0 ライブラリがインストールされている場合、
    `--pre` オプションだけでは ADK 2.0 ライブラリはインストールされません。
    上記のインストールコマンドに `--force` オプションを追加すると、ADK 2.0
    ライブラリを強制インストールできます。ADK 2.0 では Python 仮想環境を
    使用し、**ADK 1.0 プロジェクトを ADK 2.0 ライブラリへ更新する前に必ず
    バックアップを取得してください。**

## 次のステップ

ADK 2.0 の機能でエージェントを構築するための開発者ガイドを読んでください。

- [**グラフベースのワークフロー**](/ja/workflows/)
- [**協調エージェント**](/ja/workflows/collaboration/)
- [**動的ワークフロー**](/ja/workflows/dynamic/)

テストや着想のために、次の ADK 2.0 コードサンプルも確認してください。

- [**ワークフローサンプル**](https://github.com/google/adk-python/tree/v2/contributing/workflow_samples)
- [**協調タスクサンプル**](https://github.com/google/adk-python/tree/v2/contributing/task_samples)

ADK 2.0 をご確認いただきありがとうございます。皆さまからの
[フィードバック](https://github.com/google/adk-python/issues/new?template=feature_request.md&labels=v2)
をお待ちしています。
