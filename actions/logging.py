#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging, os
import multiprocessing
# 模式
DEBUG_MOD = False
DEBUG_MOD = True
# 运行目录
WORK_PATH = os.path.dirname(__file__)
log_queue = multiprocessing.Queue(-1)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'standard': {'format': "%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s",
                    'datefmt': "%Y-%m-%d %H:%M:%S" #default: "%Y-%m-%d %H:%M:%S"
        },
        'asr_fmt': {'format': "%(asctime)s %(message)s", 'datefmt': "%Y-%m-%d %H:%M:%S"},
        'simple': {'format': '%(levelname)s %(module)s %(lineno)d %(message)s'},
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'DEBUG' if DEBUG_MOD else 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
#            'encoding': 'utf8'
        },
    #    'file': {  # 向文件中输出日志
    #        'level': 'DEBUG' if DEBUG_MOD else 'INFO',
    #        'class': 'logging.handlers.TimedRotatingFileHandler', 
    #        'filename': os.path.join(WORK_PATH, '../logs', log_filename), #os.path.join(os.path.dirname(BASE_DIR), "logs/XXXXX.log"),  # 日志文件的位置
    #        'formatter': 'standard',
    #        'encoding': 'utf-8',
    #        'when': 'midnight',
    #        'backupCount': 10
    #    },
        # 'file': {  # 向文件中输出日志
        #     'level': 'DEBUG' if DEBUG_MOD else 'INFO',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename': os.path.join(WORK_PATH, '../logs', f'action{os.getpid()}.log'), #os.path.join(os.path.dirname(BASE_DIR), "logs/XXXXX.log"),  # 日志文件的位置
        #     'formatter': 'standard',
        #     'encoding': 'utf8',
        #     'maxBytes': 1024 * 1024 *2,
        #     'backupCount': 5
        # },
    #    'queue': {  # 向文件中输出日志
    #        'level': 'INFO',
    #        'class': 'logging.handlers.QueueHandler', 
    #        'formatter': 'standard',
    #        'args': (log_queue,)
    #    },
        # 'asr_file': {  # 向文件中输出日志
        #     'level': 'DEBUG' if DEBUG_MOD else 'WARNING',
        #     'class': 'logging.handlers.RotatingFileHandler', 
        #     'filename': os.path.join(os.path.dirname(WORK_PATH), "logs/actions.log"), #os.path.join(os.path.dirname(BASE_DIR), "logs/XXXXX.log"),  # 日志文件的位置
        #     'formatter': 'asr_fmt',
        #     'encoding': 'utf8',
        #     'maxBytes': 1024 * 1024,
        #     'backupCount': 10
        # },
        # 20200512新增
    #    'file': {  # 向文件中输出日志
    #        'level': 'INFO',
    #        'class': 'logging.FileHandler', 
    #        'filename': os.path.join(WORK_PATH, '../logs', 'action_0.log'), #os.path.join(os.path.dirname(BASE_DIR), "logs/XXXXX.log"),  # 日志文件的位置
    #        'formatter': 'standard',
    #        'encoding': 'utf8',
    #    },
    },
    'loggers': {  # 日志器
        'action_logger': {  # 定义了一个名为logger的日志器
            # 'handlers': ['console'],  # ['console', 'file']可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'DEBUG',  # 日志器接收的最低日志级别
        },
        # 'ASR': {  # 定义了一个名为logger的日志器
        #     'handlers': ['asr_file'],  # 可以同时向终端与文件中输出日志
        #     'propagate': True,  # 是否继续传递日志信息
        #     'level': 'DEBUG',  # 日志器接收的最低日志级别
        # },
    }
}
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
queue_handler = logging.handlers.QueueHandler(log_queue)
queue_handler.setFormatter(formatter)
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('action_logger')
logger.addHandler(queue_handler)

# log_queue = multiprocessing.Queue(-1)
# def setup_logging():
#     # 创建一个日志队列
#     # log_queue = multiprocessing.Queue()
#     # 创建一个队列处理程序，用于将日志消息推送到队列中
#     queue_handler = logging.handlers.QueueHandler(log_queue)
#     # 创建一个日志记录器并设置其级别
#     logger = logging.getLogger('action_logger')
#     logger.setLevel(logging.INFO)
#     # 创建一个日志文件处理程序，用于将日志消息写入文件
#     file_handler = logging.FileHandler('app.log')
#     # 创建一个格式化程序，用于定义日志消息的格式
#     formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
#     # 将格式化程序添加到处理程序
#     queue_handler.setFormatter(formatter)
#     file_handler.setFormatter(formatter)
#     # 将处理程序添加到记录器
#     logger.addHandler(queue_handler)
#     logger.addHandler(file_handler)

#     # 返回日志队列和队列处理程序
#     return queue_handler

def listener_process(queue):
    formatter = logging.Formatter("%(message)s")
    handler = logging.handlers.RotatingFileHandler(filename=os.path.join(WORK_PATH, '../logs', 'action.log'), maxBytes=1024 * 1024 * 100, backupCount=9)
    handler.setFormatter(formatter)
    listener = logging.handlers.QueueListener(queue, handler)
    return listener

listener = listener_process(log_queue)
listener.start()
