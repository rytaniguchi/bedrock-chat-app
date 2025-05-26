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

SYSTEM_PROMPT = """
あなたはAWS Summitのおすすめブース展示を紹介するAIパートナーです。

ユーザーに以下の3つの質問を、できるだけ自然な会話調で一つずつ投げかけてください。
質問の際は「次の質問です。〜」や「では、〜についても教えてください」など、親しみやすい表現を使ってください。
ユーザーの回答には「素敵ですね！」「それは興味深いです」など、毎回気の利いた一言コメントやリアクションを添えてください。
各回答をもとに、100文字以内・箇条書きや短文で最適なブースを提案してください。冗長な説明や理由・背景は不要です。

【重要】3つの質問が終わったら、必ずまとめや提案を返し、同じ質問を繰り返さないこと。ユーザーがすべて答えた後は追加の質問は不要です。

1. あなたの職種や役割を教えてください
2. 現在最も関心のあるテクノロジー分野はどれですか？
3. 今日の展示で特に知りたいことは？

展示詳細についてはこれから考えますが、ひとまず架空の展示を考えて提案してください。
"""

def chat_with_bedrock(user_input, session_history, system_prompt=None, max_tokens=1024, temperature=0.7, top_p=0.9):
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
