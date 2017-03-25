#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals
import os
import logging

logger = logging.getLogger(__name__)

##########leancloud
USE_LEANCLOUD_FOR_LOG =  True# 默认不使用消息云存储 # pw False / ai100 True
USE_LEANCLOUD_FOR_IMAGE = True  # 默认不使用消息云存储 但是头像一直在用它
PUSH_ALL_GROUP_MESSAGE_TO_LEANCLOUD = True # pw False / ai100 True
###########

############# debug
# env DEBUG=True python wechat_group_bot.py(fish)  DEBUG=True python
# wechat_group_bot.py(bash/zsh)
#有东西就是true ，都是字符串
DEBUG = False  # 使用环境变量，不必修改文件
is_debug = os.getenv("DEBUG", None)
if is_debug:
    DEBUG = is_debug
#print(DEBUG)
############

############ action
FORCED_IN_ACTION = False  # 是够是活动期间

# feature action
# 管理员名字
if DEBUG:
    ACTION_ADMIN = ["种瓜", ]
else:
    ACTION_ADMIN = ["张俊", ]
ACTION_KEYWORD = "提问开始"
ACTION_TIME = 60 * 60 * 2  # 2 hour
##############


### 分组功能(ai100)
# 机器学习日报 计算机视觉日报  独立转发
#group_family
