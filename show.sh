echo '===== port: 5005'
lsof -ti:5005|wc -l
echo '=====  port: 5055'
lsof -ti:5055|wc -l

echo "启动前请检查：1.源码、后端、api接口版本 2.预训练语言模型路径 3.python虚拟环境 5.api接口环境 6.redis集群环境 7.日志级别"
