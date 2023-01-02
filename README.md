# slack_dialog_bots
Slackで対話するボット

# 事前準備
.envファイルを作成し、SLACK_BOT_TOKENとSLACK_API_TOKENを設定する。

# 起動方法
master, facilitator, timekeeperのそれぞれのフォルダでbot.pyを起動する。
```
cd master
python bot.py
```
```
cd facilitator
python bot.py
```
```
cd timekeeper
python bot.py
```

# 仕組み
- masterがボットの対話の内容が記述された`scenario.json`を読み込む。- `scenario.json`に従って、facilitatorとtimekeeperに発話の命令を送る(pyzmqを使って命令を送信する)。
- facilitatorとtimekeeperは自分宛の命令であれば、Slackに発話を投稿する。
- ユーザの入力はいつでも可能。ただし、シナリオ進行に影響するのは`scenario.json`でtypeがwaitの時のみ。