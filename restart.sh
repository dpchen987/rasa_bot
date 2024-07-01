#!/usr/bin/sh
# cd utils && python3 corpus_accurate_hit.py && cd ..
# 查找并杀死指定端口的进程
kill -9 $(lsof -i:5006 -t)
kill -9 $(lsof -i:5056 -t)
rm run_action.out run_rasa.out
# 重新启动
# LOG_LEVEL=WARNING ACTION_SERVER_SANIC_WORKERS=4 nohup rasa run actions -p 5056 > /dev/null 2> run_action.out &
# LOG_LEVEL=WARNING SANIC_WORKERS=4 nohup rasa run -p 5006 -v --enable-api --cors "*" > /dev/null 2> run_rasa.out &
ACTION_SERVER_SANIC_WORKERS=4 nohup rasa run actions -p 5056 --quiet > /dev/null 2> run_action.out &
SANIC_WORKERS=4 nohup rasa run -p 5006 -v --enable-api --cors "*" --quiet > /dev/null 2> run_rasa.out &

