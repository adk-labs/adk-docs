# セッションデータベーススキーマの移行

<div class="language-support-tag">
  <span class="lst-supported">Supported in ADK</span><span class="lst-python">Python v1.22.1</span>
</div>

`DatabaseSessionService` を利用していて、ADK Python リリース
v1.22.0 以上へアップグレードする場合は、データベースを新しいセッションデータベース
スキーマへ移行する必要があります。ADK Python リリース v1.22.0 以降、
`DatabaseSessionService` のデータベーススキーマは、pickle ベースの
シリアライズである `v0` から、JSON ベースのシリアライズを使う `v1` へ
更新されました。従来の `v0` セッションスキーマ DB は ADK Python v1.22.0 以上でも
引き続き動作しますが、将来のリリースでは `v1` スキーマが必要になる可能性があります。


## セッションデータベースを移行する

移行プロセスを支援するスクリプトが用意されています。このスクリプトは
既存データベースからデータを読み取り、新しい形式へ変換して、
新しいデータベースへ書き込みます。次の例のように、ADK コマンドライン
インターフェース (CLI) の `migrate session` コマンドで移行を実行できます:

!!! warning "必須: ADK Python v1.22.1 以上"

    この手順には ADK Python v1.22.1 以上が必要です。これは、
    セッションデータベーススキーマ変更をサポートする移行 CLI 機能と
    バグ修正が含まれているためです。

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

移行後は、`DatabaseSessionService` の設定を更新し、
`dest_db_url` で指定した新しい DB URL を使用してください。
