Agent Development Kit（ADK）へのご貢献に関心をお寄せいただき、ありがとうございます。以下に挙げるコアフレームワーク、ドキュメント、および関連コンポーネントへの貢献を歓迎します。

このガイドでは、参加方法をご案内します。

## コミュニティに参加する

* ADK について議論したり、質問したり、エージェント全般について話したい場合は、Reddit の **[r/agentdevelopmentkit](https://www.reddit.com/r/agentdevelopmentkit/)** に参加してください。
* 月次コミュニティコールの更新を受け取りたい場合は、**[ADK Community Google Group](https://groups.google.com/g/adk-community)** に参加してください。
* バグを報告したり ADK フレームワークに貢献したりしたい場合は、以下のセクションで適切なリポジトリの見つけ方と始め方を確認してください。

## 貢献の準備

### 適切なリポジトリを選ぶ

ADK プロジェクトはいくつかのリポジトリに分かれています。あなたの貢献に適したものを見つけてください。

リポジトリ | 説明 | 詳細ガイド
--- | --- | ---
[`google/adk-python`](https://github.com/google/adk-python) | コア Python ライブラリのソースコードが含まれています。 | [`CONTRIBUTING.md`](https://github.com/google/adk-python/blob/main/CONTRIBUTING.md)
[`google/adk-python-community`](https://github.com/google/adk-python-community) | コミュニティ提供のツール、インテグレーション、スクリプトが含まれています。 | [`CONTRIBUTING.md`](https://github.com/google/adk-python-community/blob/main/CONTRIBUTING.md)
[`google/adk-js`](https://github.com/google/adk-js) | コア JavaScript ライブラリのソースコードが含まれています。 | [`CONTRIBUTING.md`](https://github.com/google/adk-js/blob/main/CONTRIBUTING.md)
[`google/adk-go`](https://github.com/google/adk-go) | コア Go ライブラリのソースコードが含まれています。 | [`CONTRIBUTING.md`](https://github.com/google/adk-go/blob/main/CONTRIBUTING.md)
[`google/adk-java`](https://github.com/google/adk-java) | コア Java ライブラリのソースコードが含まれています。 | [`CONTRIBUTING.md`](https://github.com/google/adk-java/blob/main/CONTRIBUTING.md)
[`google/adk-docs`](https://github.com/google/adk-docs) | 現在ご覧になっているドキュメントサイトのソースが含まれています。 | [`CONTRIBUTING.md`](https://github.com/google/adk-docs/blob/main/CONTRIBUTING.md)
[`google/adk-samples`](https://github.com/google/adk-samples) | ADK のサンプルエージェントが含まれています。 | [`CONTRIBUTING.md`](https://github.com/google/adk-samples/blob/main/CONTRIBUTING.md)
[`google/adk-web`](https://github.com/google/adk-web) | `adk web` 開発 UI のソースが含まれています。 |

これらのリポジトリには通常、ルートに `CONTRIBUTING.md` ファイルがあり、要件、テスト、コードレビューの流れなど、各コンポーネントの詳細情報が記載されています。

### CLA に署名する

このプロジェクトへの貢献には、[Contributor License Agreement](https://cla.developers.google.com/about)（CLA）への同意が必要です。あなた（またはあなたの雇用主）は貢献物の著作権を保持し、この契約によって、プロジェクトの一部としてあなたの貢献を使用および再配布する許可が私たちに与えられます。

あなたまたは現在の雇用主がすでに Google CLA に署名している場合（別のプロジェクト向けであっても）、再度署名する必要はないかもしれません。

<https://cla.developers.google.com/> で現在の契約状況を確認するか、新しい契約に署名してください。

### コミュニティガイドラインを確認する

このプロジェクトは [Google のオープンソースコミュニティガイドライン](https://opensource.google/conduct/) に従います。

## 貢献方法

ADK にはいくつかの方法で貢献できます。

### Issue を報告する { #reporting-issues-bugs-errors }

フレームワークのバグやドキュメントの誤りを見つけた場合は:

* **フレームワークのバグ:** [`google/adk-python`](https://github.com/google/adk-python/issues/new)、[`google/adk-js`](https://github.com/google/adk-js/issues/new)、[`google/adk-go`](https://github.com/google/adk-go/issues/new)、または [`google/adk-java`](https://github.com/google/adk-java/issues/new) に Issue を作成してください。
* **ドキュメントの誤り:** [バグテンプレートを使って `google/adk-docs` に Issue を作成](https://github.com/google/adk-docs/issues/new?template=bug_report.md)

### 改善提案をする { #suggesting-enhancements }

新機能や既存機能の改善アイデアがありますか。

* **フレームワークの改善:** [`google/adk-python`](https://github.com/google/adk-python/issues/new)、[`google/adk-js`](https://github.com/google/adk-js/issues/new)、[`google/adk-go`](https://github.com/google/adk-go/issues/new)、または [`google/adk-java`](https://github.com/google/adk-java/issues/new) に Issue を作成してください。
* **ドキュメントの改善:** [`google/adk-docs`](https://github.com/google/adk-docs/issues/new) に Issue を作成してください。

### ドキュメントを改善する { #improving-documentation }

タイポ、不明瞭な説明、情報の不足を見つけましたか。変更を直接提出してください。

* **方法:** 提案する改善を含む Pull Request（PR）を送信してください。
* **場所:** [`google/adk-docs` で Pull Request を作成](https://github.com/google/adk-docs/pulls)

### コードを書く { #writing-code }

バグ修正、新機能の実装、またはドキュメント用のコードサンプル提供にご協力ください。

**方法:** コード変更を含む Pull Request（PR）を送信してください。

* **Python フレームワーク:** [`google/adk-python` で Pull Request を作成](https://github.com/google/adk-python/pulls)
* **TypeScript フレームワーク:** [`google/adk-js` で Pull Request を作成](https://github.com/google/adk-js/pulls)
* **Go フレームワーク:** [`google/adk-go` で Pull Request を作成](https://github.com/google/adk-go/pulls)
* **Java フレームワーク:** [`google/adk-java` で Pull Request を作成](https://github.com/google/adk-java/pulls)
* **ドキュメント:** [`google/adk-docs` で Pull Request を作成](https://github.com/google/adk-docs/pulls)

### コードレビュー

* プロジェクトメンバーを含むすべての貢献はレビューを受けます。

* コードの提出とレビューには GitHub Pull Request（PR）を使用します。PR には変更内容を明確に記述してください。

## ライセンス

貢献することで、あなたの貢献がプロジェクトの [Apache 2.0 License](https://github.com/google/adk-docs/blob/main/LICENSE) の下でライセンスされることに同意したものとみなされます。

## ご質問はありますか?

行き詰まったり質問がある場合は、関連リポジトリの Issue トラッカーに遠慮なく Issue を作成してください。
