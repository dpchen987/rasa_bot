#!/usr/bin/sh

# 为精准命中生成数据文件
#!/usr/bin/sh
# 查找并杀死指定端口的进程
kill -9 $(lsof -i:5005 -t)
kill -9 $(lsof -i:5055 -t)
rm nohup5005.out
# 重新启动
ACTION_SERVER_SANIC_WORKERS=1  nohup rasa run actions  -p 5055 &
SANIC_WORKERS=1 nohup rasa run -p 5005 -v --enable-api  --cors "*" &> ./nohup5005.out &

tail -f nohup5005.out
