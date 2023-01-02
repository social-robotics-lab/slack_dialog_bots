#環境変数を扱うためのライブラリ
import os
import time
import re
import zmq
import json
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from scenario_manager import ScenarioManager

# 定数
load_dotenv()
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN_1"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN_1"]

# ZeroMQの設定
context = zmq.Context()
pub = context.socket(zmq.PUB)
pub.bind('tcp://*:5556')

# シナリオマネージャの初期化
f = open("scenario.json", "r", encoding="utf-8")
scenario = json.load(f)
f.close()
sm = ScenarioManager(scenario)

# アプリの初期化
app = App(token=SLACK_BOT_TOKEN)

# グローバル変数
last_res = {}
is_first = True

@app.event("message")
def message_handle(message):
    if "bot_id" in message:
        # botからのメッセージの場合の処理
        res = sm.next()
        # 前回と同じレスポンスならば何もしない
        if res == last_res: return
        # レスポンスがwaitなら何もしない
        if res["type"] == "wait": return
        # botたちにテキストを送信
        data = dict(speaker=res["speaker"], text=res["text"])
        print(data)
        pub.send_string(json.dumps(data))
        return

    # ユーザからのメッセージの場合の処理
    res = sm.next(message["text"]) 
    # 前回と同じレスポンスならば何もしない
    if res == last_res: return
    # レスポンスがwaitなら何もしない
    if res["type"] == "wait": return
    # botたちにテキストを送信
    data = dict(speaker=res["speaker"], text=res["text"])
    print(data)
    pub.send_string(json.dumps(data))
    return


if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()