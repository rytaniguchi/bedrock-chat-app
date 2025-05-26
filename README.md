# AWS Bedrock Chat App

このアプリはAWS Bedrock Claudeとチャット形式でやり取りできるPython CLIツールです。

---

## セットアップ

1. AWS認証情報は`.env`ファイルに記載してください（例: `.env` ファイルをプロジェクト直下に作成し、以下のように記載）。
   ```env
   AWS_ACCESS_KEY_ID=your-access-key-id
   AWS_SECRET_ACCESS_KEY=your-secret-access-key
   AWS_REGION=ap-northeast-1
   MODEL_ID=apac.anthropic.claude-sonnet-4-20250514-v1:0
   ```
   ※ `.env`はgit管理対象外にしてください。
   ※ `python-dotenv`で自動的に読み込まれます。
2. 依存パッケージをインストール:
   ```sh
   pip install -r requirements.txt
   ```
   - Macで音声入力を使う場合は、事前に`brew install portaudio`を実行してください。
3. `main.py`を実行:
   - キーボード入力モード（デフォルト）
     ```sh
     python main.py
     ```
   - マイク入力モード（音声認識）
     ```sh
     python main.py mic
     ```

- 質問を入力または話しかけると、Bedrock Claudeが返答します。
- 終了するには`exit`と入力または発話してください。
- `history`と入力または発話すると、これまでの会話履歴が表示されます。

---

## 主な機能
- AWS Bedrock Claudeと対話できるPython CLIチャットアプリ
- **ブース展示リスト**をシステムプロンプトに埋め込み、AIがこのリストから最適な展示のみを選んで提案
- Macの場合、AIの返答を音声で読み上げる機能も追加可能（`say`コマンド利用、デフォルト無効）
- **音声認識入力（micモード）**に対応（Google Speech APIを利用）
- `history`コマンドで会話履歴をいつでも確認可能
- 会話履歴はAIへのコンテキストとして毎回送信され、自然な対話が可能

---

## ブース展示リスト連携について
- Python側でブース展示リスト（おすすめユーザー・事例ポイント付き）を定義
- Claudeのsystem promptにリスト内容をテキストで埋め込み、AIがこのリストからのみ選定・提案
- ブース情報の追加・修正は`main.py`のリストを編集するだけで簡単

---

## 使い方例
- `python main.py` で通常のCLIチャット
- `python main.py mic` でマイク入力チャット
- `history` で会話履歴を表示
- `exit` で終了

---

## 依存パッケージ
- `boto3`（AWS Bedrock API呼び出し）
- `python-dotenv`（.envファイル読込）
- `speechrecognition`（音声認識）
- `pyaudio`（マイク入力用、Macはbrewでportaudio必須）

---

## ファイル構成
- `main.py` （Python CLIアプリ本体）
- `requirements.txt` （依存パッケージ定義）
- `.env` （AWS認証情報・モデルIDなど、git管理外）

---

## 備考
- ブース選定ロジックを今後Python側で自動化する拡張も可能です。
- ご要望に応じて履歴のファイル保存やWeb化も対応できます。

## 注意事項
- `.env`ファイルやAWS秘密情報は絶対に公開リポジトリに含めないでください
- フロントエンドのソースコードは含まれていません


## ディレクトリ構成例

- main.py (Python CLI/バックエンド)
- requirements.txt

---