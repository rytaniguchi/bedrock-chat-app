import os
import json
import boto3
from dotenv import load_dotenv
import re
import subprocess

# .envの読み込み
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
MODEL_ID = os.getenv("MODEL_ID", "apac.anthropic.claude-sonnet-4-20250514-v1:0")

# --- ブース展示リスト定義 ---
booth_list = [
    {
        "name": "生成AI活用最前線ブース",
        "description": "最新の生成AIサービスや導入事例を体験できるデモ。業務効率化やアイデア創出に役立つソリューションを紹介。",
        "tags": [
            "おすすめユーザー: DX推進担当者・企画職・AI導入を検討中の方",
            "事例ポイント: 社内ナレッジ自動要約、チャットボット活用、AI議事録"
        ]
    },
    {
        "name": "IoT × AWS 実践ブース",
        "description": "IoTデバイスとAWSクラウド連携のハンズオン。現場データの可視化や自動化事例を体験。",
        "tags": [
            "おすすめユーザー: 製造業エンジニア・現場管理者・IoT導入検討者",
            "事例ポイント: 設備予知保全、遠隔監視、工場データ分析"
        ]
    },
    {
        "name": "セキュリティ＆ガバナンス相談ブース",
        "description": "AWS環境のセキュリティ設計や運用ガバナンスのベストプラクティスを専門家が解説。実際の運用課題も相談可能。",
        "tags": [
            "おすすめユーザー: 情シス・セキュリティ担当・経営層",
            "事例ポイント: 権限管理自動化、監査ログ活用、ゼロトラスト導入"
        ]
    }
]

def booth_list_to_text(booth_list):
    lines = []
    for booth in booth_list:
        lines.append(f"■ {booth['name']}")
        lines.append(f"  説明: {booth['description']}")
        for tag in booth['tags']:
            lines.append(f"  - {tag}")
        lines.append("")
    return "\n".join(lines)

BOOTH_LIST_TEXT = booth_list_to_text(booth_list)

SYSTEM_PROMPT = f"""
あなたは体験者との会話を元にして、自社が用意したAWS Summitのブース展示からおすすめの体験をピックアップして紹介するAIパートナーです。

下記の「ブース展示リスト」から、ユーザーの回答に最も合致するものを1つ以上選び、紹介してください。このリストにない展示は提案しないこと。

【ブース展示リスト】
{BOOTH_LIST_TEXT}

ユーザーに以下の3つの質問を、できるだけ自然な会話調で一つずつ投げかけてください。
質問の際は「次の質問です。〜」や「では、〜についても教えてください」など、親しみやすい表現を使ってください。
ユーザーの回答には「素敵ですね！」「それは興味深いです」など、毎回気の利いた一言コメントやリアクションを添えてください。
各回答をもとに、100文字以内・箇条書きや短文で最適なブースを提案してください。冗長な説明や理由・背景は不要です。

【重要】3つの質問が終わったら、必ずまとめや提案を返し、同じ質問を繰り返さないこと。ユーザーがすべて答えた後は追加の質問は不要です。

1. あなたの職種や役割を教えてください
2. 現在最も関心のあるテクノロジー分野はどれですか？
3. 今日の展示で特に知りたいことは？
"""


def chat_with_bedrock(user_input, session_history, system_prompt=None, max_tokens=1024, temperature=0.9, top_p=0.9):
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    messages = []
    # 直近のやり取り履歴を組み立て
    for user_msg, ai_msg in session_history:
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if ai_msg:
            messages.append({"role": "assistant", "content": ai_msg})
    if user_input:
        messages.append({"role": "user", "content": user_input})
    body = {
        "max_tokens": max_tokens,
        "messages": messages,
        "anthropic_version": "bedrock-2023-05-31",
        "temperature": temperature,
        "top_p": top_p
    }
    if system_prompt:
        body["system"] = system_prompt
    body = json.dumps(body)

    response = client.invoke_model_with_response_stream(
        modelId=MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json"
    )


    text = ""
    for event in response["body"]:
        try:
            if isinstance(event, dict) and "chunk" in event and "bytes" in event["chunk"]:
                chunk = json.loads(event["chunk"]["bytes"])
                if chunk.get("type") == "content_block_delta":
                    delta = chunk.get("delta", {})
                    if delta.get("type") == "text_delta":
                        token = delta.get("text", "")
                        text += token
                        print(token, end="", flush=True)
            elif isinstance(event, bytes):
                event = event.decode("utf-8")
                text += event
                print(event, end="", flush=True)
        except Exception:
            continue
    # if text:
        # print(text, end="", flush=True)
    print()
    return text.strip()

def main():
    session_history = []
    ai_init_prompt = "質問を始めてください。"
    try:
        ai_first_message = chat_with_bedrock(ai_init_prompt, session_history, system_prompt=SYSTEM_PROMPT)
        if ai_first_message is None:
            ai_first_message = ""
        # print(f"Bedrock: {ai_first_message}")
        # if os.uname().sysname == "Darwin":
        #     subprocess.run(["say", ai_first_message])
        if ai_init_prompt and ai_first_message:
            session_history.append((ai_init_prompt, ai_first_message))
    except Exception as e:
        print(f"[初回AIメッセージ取得エラー] {e}")
        ai_first_message = "(AIからの初回メッセージ取得に失敗しました)"

    while True:
        user_input = input("あなたの質問 > ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        if user_input.lower() == "history":
            print("\n--- 会話履歴 ---")
            for i, (user_msg, ai_msg) in enumerate(session_history, 1):
                print(f"{i}. [あなた] {user_msg}")
                print(f"   [AI] {ai_msg}")
            print("---\n")
            continue
        try:
            answer = chat_with_bedrock(user_input, session_history, system_prompt=SYSTEM_PROMPT)
            # print(f"Bedrock: {answer}")
            # if os.uname().sysname == "Darwin":
            #     subprocess.run(["say", answer])
            if user_input is not None and answer is not None:
                session_history.append((user_input, answer))
        except Exception as e:
            print(f"[Error] {e}")

if __name__ == "__main__":
    main()
