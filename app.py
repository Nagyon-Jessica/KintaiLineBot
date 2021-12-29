import json
import os
from urllib.parse import parse_qs

import redis
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent, PostbackEvent, TextMessage,
                            TextSendMessage)

from templates import (ATTEND_TEMPLATE, ATTEND_TIME_TEMPLATE,
                       CHECKOUT_TEMPLATE, LOCATION_TEMPLATE)

app = Flask(__name__)
r = redis.from_url(os.environ.get("REDIS_URL"))

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
    message = ATTEND_TEMPLATE
    line_bot_api.reply_message(
        event.reply_token,
        message)

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    user_id = event.source.user_id
    key = f'{user_id}_attend'
    params = parse_qs(data)
    action = params['action'][0]
    if action == "attend":
        if params['manual'][0] == "false":
            r.hset(key, 'manual', 'false')
            message = LOCATION_TEMPLATE
        else:
            r.hset(key, 'manual', 'true')
            message = TextSendMessage(
                text='出勤時刻を入力してください！',
                quick_reply=ATTEND_TIME_TEMPLATE
            )
    elif action == "time":
        time = event.postback.params['time']
        if params['type'][0] == "attend":
            r.hset(key, 'time', time)
            message = LOCATION_TEMPLATE
    elif action == "locate":
        location = params['location'][0]
        r.hset(key, 'location', location)
        print(f"hash: {r.hgetall(key)}")
        message = CHECKOUT_TEMPLATE

    line_bot_api.reply_message(
        event.reply_token,
        message)

if __name__ == "__main__":
    app.run()
