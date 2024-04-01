#!/usr/bin/sh
# 查找并杀死指定端口的进程
kill -9 $(lsof -i:5006 -t)
kill -9 $(lsof -i:5056 -t)