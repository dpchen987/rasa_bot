#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging, os

# 模式
DEBUG_MOD = False
DEBUG_MOD = True
# 运行目录
WORK_PATH = os.path.dirname(__file__)

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
#        'file': {  # 向文件中输出日志
#            'level': 'DEBUG' if DEBUG_MOD else 'INFO',
#            'class': 'logging.handlers.TimedRotatingFileHandler', 
#            'filename': os.path.join(WORK_PATH, 'log', 'debug.log'), #os.path.join(os.path.dirname(BASE_DIR), "logs/XXXXX.log"),  # 日志文件的位置
#            'formatter': 'standard',
#            'encoding': 'utf8',
#            'when': 'midnight'
#        },
        'file': {  # 向文件中输出日志
            'level': 'DEBUG' if DEBUG_MOD else 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(WORK_PATH, '..\logs', 'actions.log'), #os.path.join(os.path.dirname(BASE_DIR), "logs/XXXXX.log"),  # 日志文件的位置
            'formatter': 'standard',
            'encoding': 'utf8',
            'maxBytes': 1024 * 1024,
            'backupCount': 10
        },
#        'asr_file': {  # 向文件中输出日志
#            'level': 'INFO',
#            'class': 'logging.handlers.TimedRotatingFileHandler', 
#            'filename': os.path.join(WORK_PATH, 'log', 'asr.log'), #os.path.join(os.path.dirname(BASE_DIR), "logs/XXXXX.log"),  # 日志文件的位置
#            'formatter': 'asr_fmt',
#            'encoding': 'utf8',
#            'when': 'midnight'
#        },
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
#        'asr_hd': {  # 向文件中输出日志
#            'level': 'INFO',
#            'class': 'logging.FileHandler', 
#            'filename': os.path.join(WORK_PATH, 'log', log_date + 'asr.log'), #os.path.join(os.path.dirname(BASE_DIR), "logs/XXXXX.log"),  # 日志文件的位置
#            'formatter': 'asr_fmt',
#            'encoding': 'utf8',
#        },
    },
    'loggers': {  # 日志器
        'action_logger': {  # 定义了一个名为logger的日志器
            'handlers': ['console', 'file'],  # ['console', 'file']可以同时向终端与文件中输出日志
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

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('action_logger')