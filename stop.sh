#!/bin/bash

# 查找并杀死指定端口的进程
kill -9 $(lsof -i:5005 -t)
kill -9 $(lsof -i:5055 -t)

