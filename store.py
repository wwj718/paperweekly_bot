#!/usr/bin/env python
# encoding: utf-8

import leancloud
from leancloud import Object
from leancloud import Query
import os

# 设置环境变量
# set -x  LEANCLOUD_APP_ID xxx
APP_ID = os.environ.get("LEANCLOUD_APP_ID")
APP_KEY  = os.environ.get("LEANCLOUD_APP_KEY")

leancloud.init(APP_ID, APP_KEY)

class MessageModel(Object):
    pass
'''
messageModel = leancloud.Object.extend('messageModel')
message_model = messageModel()

message_model.set('init_message', 'go!')
message_model.save()
# self.set('content', value)


'''

def push_message(message):
    # todo:使用魔法参数
    # message is dict
    message_model = MessageModel()
    for key in message:
        message_model.set(key,message.get(key))
    message_model.save()

if __name__ == '__main__':
    message_init = {}
    message_init["init"]='go!'
    push_message(message_init)

