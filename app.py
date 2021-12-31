import copy
import json
import os
from datetime import datetime
from urllib.parse import parse_qs

import redis
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent, PostbackEvent, TextMessage,
                            TextSendMessage)
from rq import Queue

from templates import (ATTEND_TEMPLATE, ATTEND_TIME_TEMPLATE,
                       CHECKOUT_TEMPLATE, CHECKOUT_TIME_TEMPLATE,
                       LOCATION_TEMPLATE, NOTE_TEMPLATE)
from utils import attend, checkout
from worker import conn

app = Flask(__name__)
r = redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)
q = Queue(connection=conn)

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
    user_id = event.source.user_id
    key_checkout = f'{user_id}_checkout'
    text = event.message.text
    print(text)
    if text == "出勤":
        message = ATTEND_TEMPLATE
    elif text == "退勤":
        message = copy.deepcopy(CHECKOUT_TEMPLATE)
        message.text = "退勤します！"
    else:
        if r.exists(key_checkout) and r.hexists(key_checkout, 'manual') and r.hexists(key_checkout, 'time'):
            r.hset(key_checkout, 'note', text)
            r.hset(key_checkout, 'user_id', user_id)
            hash = r.hgetall(key_checkout)
            q.enqueue(checkout, hash)
            message = TextSendMessage(text='ただいま打刻中です！このまましばらくお待ち下さい！')
            r.delete(key_checkout)
        else:
            message = TextSendMessage(text='打刻を開始する場合は「出勤」または「退勤」と入力してください！')
    line_bot_api.reply_message(
        event.reply_token,
        message)

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    user_id = event.source.user_id
    key_attend = f'{user_id}_attend'
    key_checkout = f'{user_id}_checkout'
    params = parse_qs(data)
    action = params['action'][0]
    if action == "attend":
        if params['manual'][0] == "false":
            r.hset(key_attend, 'manual', 'false')
            message = LOCATION_TEMPLATE
        else:
            r.hset(key_attend, 'manual', 'true')
            message = TextSendMessage(
                text='出勤時刻を入力してください！',
                quick_reply=ATTEND_TIME_TEMPLATE
            )
    elif action == "checkout":
        if params['manual'][0] == "false":
            r.hset(key_checkout, 'manual', 'false')
            # 手入力でなくても備考がある場合はtimeが必要になる
            current_time = datetime.now().strftime('%H:%M')
            r.hset(key_attend, 'time', current_time)
            message = NOTE_TEMPLATE
        else:
            r.hset(key_checkout, 'manual', 'true')
            message = TextSendMessage(
                text='出勤時刻を入力してください！',
                quick_reply=CHECKOUT_TIME_TEMPLATE
            )
    elif action == "time":
        time = event.postback.params['time']
        if params['type'][0] == "attend":
            # 出勤の場合は勤務地確認
            r.hset(key_attend, 'time', time)
            message = LOCATION_TEMPLATE
        else:
            # 退勤の場合は備考確認
            r.hset(key_checkout, 'time', time)
            message = NOTE_TEMPLATE
    elif action == "locate":
        location = params['location'][0]
        r.hset(key_attend, 'location', location)
        r.hset(key_attend, 'user_id', user_id)
        hash = r.hgetall(key_attend)
        print(f"hash: {hash}")
        q.enqueue(attend, hash)
        r.delete(key_attend)
        message = TextSendMessage(text='ただいま打刻中です！このまましばらくお待ち下さい！')
    elif action == "note":
        reply = params['reply'][0]
        if reply == 'yes':
            message = TextSendMessage(text='備考を入力して送信してください！')
        else:
            # 備考がなければ打刻処理へ
            r.hset(key_checkout, 'user_id', user_id)
            hash = r.hgetall(key_checkout)
            q.enqueue(checkout, hash)
            message = TextSendMessage(text='ただいま打刻中です！このまましばらくお待ち下さい！')
            r.delete(key_checkout)

    line_bot_api.reply_message(
        event.reply_token,
        message)

if __name__ == "__main__":
    app.run()
