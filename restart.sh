#!/usr/bin/sh
# 查找并杀死指定端口的进程
kill -9 $(lsof -i:5006 -t)
kill -9 $(lsof -i:5056 -t)
rm nohup.out
# 重新启动
ACTION_SERVER_SANIC_WORKERS=2  nohup rasa run actions  -p 5056 &
SANIC_WORKERS=4 nohup rasa run -p 5006 -v --enable-api  --cors "*" --logging-config-file logging_2.yml &