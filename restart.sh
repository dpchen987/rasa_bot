#!/usr/bin/sh

# 为精准命中生成数据文件
#!/usr/bin/sh
# 查找并杀死指定端口的进程
kill -9 $(lsof -i:5006 -t)
kill -9 $(lsof -i:5056 -t)
rm nohup.out
# 重新启动
ACTION_SERVER_SANIC_WORKERS=6  nohup rasa run actions  -p 5056 &
SANIC_WORKERS=6 nohup rasa run -p 5006 -v --enable-api  --cors "*" &

tail -f nohup.out