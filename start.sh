#!/bin/bash

# 为精准命中生成数据文件
cd utils && python3 corpus_accurate_hit.py && cd ..

# 重新启动
ACTION_SERVER_SANIC_WORKERS=64  nohup rasa run actions -p 5056 &
SANIC_WORKERS=64 nohup rasa run -p 5006 -v --enable-api  --cors "*" &

ACTION_SERVER_SANIC_WORKERS=2  nohup rasa run actions -p 5056 &
SANIC_WORKERS=2 nohup rasa run -p 5006 -v --enable-api  --cors "*" &