import json
import urllib.request
import urllib.error

API_URL = "https://0154-35-247-40-115.ngrok-free.app/generate"

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # Lambda に送られてきた JSON ボディを読み取る
        body = json.loads(event['body'])
        prompt = body['message']  # 単純に message を prompt として使用

        # API 用リクエストペイロード（Swagger 仕様準拠）
        request_data = {
            "prompt": prompt,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }

        # POST リクエスト送信
        req = urllib.request.Request(
            API_URL,
            data=json.dumps(request_data).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        print("Sending request to:", API_URL)
        with urllib.request.urlopen(req, timeout=90) as response:
            response_body = response.read()
            response_json = json.loads(response_body)

        print("Received response:", json.dumps(response_json))

        # 応答から生成テキストを取り出す
        generated_text = response_json.get("generated_text", "")

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
                "response_time": response_json.get("response_time", None)
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
