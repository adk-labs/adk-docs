エージェント開発キット（ADK）へのご協力に関心をお寄せいただき、ありがとうございます。私たちは、以下にリストされているコアフレームワーク、ドキュメント、および関連コンポーネントへの貢献を歓迎します。

このガイドでは、参加方法について説明します。

## コントリビューションの準備

### 適切なリポジトリの選択

ADKプロジェクトは、いくつかのリポジトリに分かれています。コントリビューションに適したリポジトリを見つけてください。

リポジトリ | 説明 | 詳細ガイド
--- | --- | ---
[`google/adk-python`](https://github.com/google/adk-python) | コアPythonライブラリのソースコードが含まれています。 | [`CONTRIBUTING.md`](https://github.com/google/adk-python/blob/main/CONTRIBUTING.md)
[`google/adk-python-community`](https://github.com/google/adk-python-community) | コミュニティから提供されたツール、インテグレーション、スクリプトが含まれています。 | [`CONTRIBUTING.md`](https://github.com/google/adk-python-community/blob/main/CONTRIBUTING.md)
[`google/adk-go`](https://github.com/google/adk-go) | コアGoライブラリのソースコードが含まれています。 | 
[`google/adk-java`](https://github.com/google/adk-java) | コアJavaライブラリのソースコードが含まれています。 | [`CONTRIBUTING.md`](https://github.com/google/adk-java/blob/main/CONTRIBUTING.md)
[`google/adk-docs`](https://github.com/google/adk-docs) | 現在ご覧になっているドキュメントサイトのソースが含まれています。 | [`CONTRIBUTING.md`](https://github.com/google/adk-docs/blob/main/CONTRIBUTING.md)
[`google/adk-web`](https://github.com/google/adk-web) | `adk web` 開発UIのソースが含まれています。 |

これらのリポジトリのルートには、通常`CONTRIBUTING.md`ファイルがあり、各コンポーネントの要件、テスト、コードレビュープロセスなどに関する詳細情報が記載されています。

### CLAへの署名

このプロジェクトへの貢献には、[貢献者ライセンス契約（Contributor License Agreement, CLA）](https://cla.developers.google.com/about)への同意が必要です。貢献内容の著作権は貢献者（またはその雇用主）に帰属しますが、この契約により、プロジェクトの一部としてあなたの貢献を使用および再配布する許可が私たちに与えられます。

あなたまたは現在の雇用主がすでにGoogle CLAに署名している場合（たとえそれが別のプロジェクトのためであっても）、再度署名する必要はないかもしれません。

<https://cla.developers.google.com/>にアクセスして、現在の契約状況を確認するか、新しい契約に署名してください。

### コミュニティガイドラインの確認

このプロジェクトは、[Googleのオープンソースコミュニティガイドライン](https://opensource.google/conduct/)に従います。

## ディスカッションへの参加

質問がありますか？アイデアを共有したいですか？あるいはADKをどのように使っているかについて話したいですか？ぜひ**[Python](https://github.com/google/adk-python/discussions)**または**[Java](https://github.com/google/adk-java/discussions)**のDiscussionsにお越しください！

ここは、主に以下のための場所です：

* 質問をしたり、コミュニティやメンテナーから助けを得る
* あなたのプロジェクトやユースケースを共有する（`Show and Tell`）
* 正式なIssueを作成する前に、潜在的な機能や改善点について議論する
* ADKに関する一般的な会話

## 貢献の方法

ADKに貢献するには、いくつかの方法があります：

### 問題の報告 { #reporting-issues-bugs-errors }

フレームワークのバグやドキュメントのエラーを見つけた場合：

* **フレームワークのバグ：** [`google/adk-python`](https://github.com/google/adk-python/issues/new)または[`google/adk-java`](https://github.com/google/adk-java/issues/new)でIssueを作成してください。
* **ドキュメントのエラー：** [`google/adk-docs`でIssueを作成（バグテンプレートを使用）](https://github.com/google/adk-docs/issues/new?template=bug_report.md)

### 機能強化の提案 { #suggesting-enhancements }

新機能や既存機能の改善に関するアイデアがありますか？

* **フレームワークの機能強化：** [`google/adk-python`](https://github.com/google/adk-python/issues/new)または[`google/adk-java`](https://github.com/google/adk-java/issues/new)でIssueを作成してください。
* **ドキュメントの機能強化：** [`google/adk-docs`でIssueを作成](https://github.com/google/adk-docs/issues/new)

### ドキュメントの改善 { #improving-documentation }

タイプミス、不明瞭な説明、情報の欠落を見つけましたか？変更を直接提案してください：

* **方法：** 提案する改善点を含むプルリクエスト（PR）を送信してください。
* **場所：** [`google/adk-docs`でプルリクエストを作成](https://github.com/google/adk-docs/pulls)

### コードの作成 { #writing-code }

バグの修正、新機能の実装、またはドキュメント用のコードサンプルの提供にご協力ください：

**方法：** コードの変更を含むプルリクエスト（PR）を送信してください。

* **Pythonフレームワーク：** [`google/adk-python`でプルリクエストを作成](https://github.com/google/adk-python/pulls)
* **Javaフレームワーク：** [`google/adk-java`でプルリクエストを作成](https://github.com/google/adk-java/pulls)
* **ドキュメント：** [`google/adk-docs`でプルリクエストを作成](https://github.com/google/adk-docs/pulls)

### コードレビュー

* プロジェクトメンバーからのものを含め、すべての貢献はレビュープロセスを経ます。

* コードの提出とレビューには、GitHubのプルリクエスト（PR）を使用します。PRには、行っている変更を明確に記述してください。

## ライセンス

貢献することにより、あなたの貢献がプロジェクトの[Apache 2.0 ライセンス](https://github.com/google/adk-docs/blob/main/LICENSE)の下でライセンスされることに同意したことになります。

## ご質問はありますか？

行き詰まったり質問がある場合は、関連するリポジトリのIssueトラッカーでお気軽にIssueを作成してください。