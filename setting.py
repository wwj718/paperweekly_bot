#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals
import os
import logging

logger = logging.getLogger(__name__)

USE_LEANCLOUD_FOR_LOG = False  # 默认不使用消息云存储 但是头像一直在用它
USE_LEANCLOUD_FOR_IMAGE = False  # 默认不使用消息云存储 但是头像一直在用它
DEBUG = False  # 使用环境变量，不必修改文件

# env DEBUG=True python wechat_group_bot.py(fish)  DEBUG=True python
# wechat_group_bot.py(bash/zsh)
is_debug = os.getenv("DEBUG", None)
if is_debug:
    DEBUG = is_debug


FORCED_IN_ACTION = False  # 是够是活动期间

# feature action
# 管理员名字
if DEBUG:
    ACTION_ADMIN = ["种瓜", ]
else:
    ACTION_ADMIN = ["张俊", ]
ACTION_KEYWORD = "提问开始"
ACTION_TIME = 60 * 60 * 2  # 2 hour
