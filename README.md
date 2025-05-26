<<<<<<< HEAD
# bedrock-chat-app
Bedrock Claudeを使ったPython CLIチャットアプリ（Mac対応、音声読み上げも可）
=======
# AWS Bedrock Chat App

このアプリはAWS Bedrockとチャット形式でやり取りできるPython CLIツールです。

---

## セットアップ

1. AWS認証情報は`.env`ファイルに記載してください（例: `.env` ファイルをプロジェクト直下に作成し、以下のように記載）。
   ```env
   AWS_ACCESS_KEY_ID=your-access-key-id
   AWS_SECRET_ACCESS_KEY=your-secret-access-key
   AWS_REGION=us-east-1
   ```
   ※ `.env`はgit管理対象外にしてください。
   ※ `python-dotenv`で自動的に読み込まれます。
2. 依存パッケージをインストール:
   ```sh
   pip install -r requirements.txt
   ```
3. `main.py`を実行:
   ```sh
   python main.py
   ```

- 質問を入力すると、Bedrockのモデルが返答します。
- 終了するには`exit`と入力してください。

---

## 機能
- AWS Bedrock Claudeと対話できるPython CLIチャットアプリ
- Macの場合、AIの返答を音声で読み上げる機能も追加可能

---

## 注意事項
- `.env`ファイルやAWS秘密情報は絶対に公開リポジトリに含めないでください
- フロントエンドのソースコードは含まれていません

   npm run dev
   ```
   ブラウザで http://localhost:5173 を開いてください。

### バックエンドAPIの用意
- `src/App.tsx`のAPI_URL（デフォルト: `/api/chat`）にリクエストが送信されます。
- Python側でFlaskやFastAPI等で `/api/chat` エンドポイントを用意し、main.pyのロジックをラップしてください。
- 例: Flask
   ```python
   from flask import Flask, request, jsonify
   from main import chat_with_bedrock

   app = Flask(__name__)

   @app.route('/api/chat', methods=['POST'])
   def chat():
       data = request.json
       prompt = data.get('prompt')
       history = data.get('history', [])
       reply = chat_with_bedrock(prompt, [(m['content'],"") for m in history if m['role']=="user"])
       return jsonify({"reply": reply})

   if __name__ == '__main__':
       app.run(port=5000)
   ```
- ViteのdevサーバーとバックエンドAPIをCORSまたはプロキシでつなぐと便利です。

---

## ディレクトリ構成例

- main.py (Python CLI/バックエンド)
- requirements.txt
- package.json, tsconfig.json, vite.config.ts
- src/ (Reactフロントエンド)
- public/

---

ご不明点やカスタマイズ要望があればご相談ください。
>>>>>>> d6c85c2 (READMEをPython CLIチャットアプリ専用に整理（フロントエンド説明削除）)
