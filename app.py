import json
import os

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (ButtonsTemplate, MessageEvent, PostbackAction,
                            TemplateSendMessage, TextMessage)

app = Flask(__name__)

#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
ALLOWED_USERS = os.environ['ALLOWED_USER'].split(';')

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# Herokuログイン接続確認のためのメソッド
# Herokuにログインすると「hello world」とブラウザに表示される
@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    body_dict = json.loads(body)
    print(f"Request body: {body}")
    print(f"params: {request.args}")

    send_user = body_dict['events'][0]['source']['userId']
    if send_user not in ALLOWED_USERS:
        print("Invalid access from the user {send_user}.")
        abort(400)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    buttons_template_message = TemplateSendMessage(
        alt_text='勤務を開始します！',
        template=ButtonsTemplate(
            title='出勤',
            text='選択してください！',
            actions=[
                PostbackAction(
                    label='出勤',
                    display_text='出勤',
                    data='action=attend&manual=false'
                ),
                PostbackAction(
                    label='出勤（手入力）',
                    display_text='出勤（手入力）',
                    data='action=buy&manual=true'
                )
            ]
        )
    )
    line_bot_api.reply_message(
        event.reply_token,
        buttons_template_message)

if __name__ == "__main__":
    app.run()
