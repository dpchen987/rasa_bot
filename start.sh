#!/bin/bash

# 为精准命中生成数据文件
cd utils && python3 corpus_accurate_hit.py && cd ..

# 重新启动
ACTION_SERVER_SANIC_WORKERS=64  nohup rasa run actions &
SANIC_WORKERS=64 nohup rasa run -v --enable-api  --cors "*" &
