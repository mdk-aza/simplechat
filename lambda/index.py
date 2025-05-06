import json
import urllib.request
import urllib.error

API_URL = "https://0154-35-247-40-115.ngrok-free.app/generate"

def build_prompt(history, user_message):
    prompt_parts = []
    for msg in history:
        if msg["role"] == "user":
            prompt_parts.append(f"ユーザー: {msg['content']}")
        elif msg["role"] == "assistant":
            prompt_parts.append(f"アシスタント: {msg['content']}")
    prompt_parts.append(f"ユーザー: {user_message}")
    return "\n".join(prompt_parts)

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # Cognito で認証されたユーザー情報を取得
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            user_id = user_info.get('email') or user_info.get('cognito:username')
            print(f"Authenticated user: {user_id}")
        else:
            user_id = "anonymous"
            print("No authenticated user found.")

        # リクエストからメッセージと会話履歴を取得
        body = json.loads(event['body'])
        user_message = body['message']
        conversation_history = body.get("conversationHistory", [])

        # プロンプト作成
        prompt = build_prompt(conversation_history, user_message)

        # 推論API呼び出し用のリクエストペイロード
        request_data = {
            "prompt": prompt,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }

        req = urllib.request.Request(
            API_URL,
            data=json.dumps(request_data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        print(f"[{user_id}] Sending request to:", API_URL)
        with urllib.request.urlopen(req, timeout=60) as response:
            response_body = response.read()
            response_json = json.loads(response_body)

        generated_text = response_json.get("generated_text", "")
        print(f"[{user_id}] Generated response:", generated_text)

        # 会話履歴に追加
        updated_history = conversation_history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": generated_text}
        ]

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": generated_text,
                "response_time": response_json.get("response_time", None),
                "conversationHistory": updated_history
            })
        }

    except urllib.error.HTTPError as e:
        error_message = e.read().decode()
        print("HTTPError:", error_message)
        return {
            "statusCode": e.code,
            "body": json.dumps({"success": False, "error": error_message})
        }

    except Exception as error:
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
