import os
import json
import threading
import time
import zmq
from dotenv import load_dotenv
from slack_sdk import WebClient

#-----------------------------------------------------------------------------------
# sub.recv_strint()はCtrl-cで終了できないため、クライアントの処理をデーモンスレッド化し、
# メインスレッドをCtrl-cで終了すると同時に、クライアントスレッドを終了できるようにしている。
#-----------------------------------------------------------------------------------

# 定数
SPEAKER = "タイムキーパー"
CHANNEL = "#グループディスカッション"
load_dotenv()
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN_5"]

# ZeroMQの設定
context = zmq.Context()
sub = context.socket(zmq.SUB)
sub.connect("tcp://localhost:5556")
sub.setsockopt(zmq.SUBSCRIBE, b"")

# Slackへのポスト用のクライアント
client = WebClient(SLACK_BOT_TOKEN)

# 【サブスレッド用】masterからデータを受信し、自分宛てのデータをポストする関数
def run_client():
    while True:
        data_str = sub.recv_string()
        data = json.loads(data_str)
        if data["speaker"] == SPEAKER:
            client.chat_postMessage(channel=CHANNEL, text=data["text"])
            print(f"{SPEAKER}: {data['text']}")

# Threadの起動
threading.Thread(target=run_client, daemon=True).start()
# メインスレッドはCtrl-cを受け付けられるsleepで待つようにする。
try:
    while True: time.sleep(10)
except KeyboardInterrupt:
    sub.close()
    
