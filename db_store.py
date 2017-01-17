#!/usr/bin/env python
# encoding: utf-8
'''
将聊天消息存入数据库
    使用peewee驱动sqlite
    使用bokeh提供可视化,使用pandas检索数据
    和leancloud一样，对外暴露功能函数

时间字段使用arrow,存入统一使用unix时间戳,数字

永远使用UTC 或者UNIX 时间戳 http://pycoders-weekly-chinese.readthedocs.io/en/latest/issue5/what-you-need-to-know-about-datetimes.html

todo:
    *  使用正则提取log,归档纳入数据库

# 开发的时候用gui工具查看数据库 方便调试 sandman sqlitebrower
'''

from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import datetime
from utils import  get_now_timestamp
import datetime
db = SqliteExtDatabase('group_chat_message.db')

import logging
logging.basicConfig(level=logging.INFO)

################ data class

class BaseModel(Model):
    class Meta:
        database = db



class Message(BaseModel):
    # 字段和存入一样
    group_name = CharField()
    content = CharField()
    group_user_name = CharField()
    user_img = CharField(null = True) #url 可空
    createdAt = IntegerField(default=get_now_timestamp) #默认自创建(使用函数) , 使用arrow
    updatedAt = IntegerField(default=get_now_timestamp) #命名与leancloud默认的一致,time 使用unix时间戳 使用数字 posixTimestamp
    # 使用默认的世界有更多工具方便管理 pandas/boken默认处理的时间是什么，还是用默认的好，需要处理在用arrow
    '''
    createdAt = DateTimeField(default=datetime.datetime.now) #注意utc 和local 存储的时候使用utc  使用时间戳似乎更容易
    updatedAt = DateTimeField(default=datetime.datetime.now)
    '''

def push_message(message):
    # message is dict
    message_model = Message()
    for key in message:
        message_model.__setattr__(key,message.get(key))
    try:
        message_model.save()
        logging.info("success to store message!")
    except Exception as e:
        logging.info(str(e))

#####
def create_table():
    db.connect()
    #db.create_tables([Message])
    # 重建table，或者删除
    # http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#sqlite-ext migrate
    # db.drop_tables([User, Tweet, Something], safe=True)
    db.create_tables([Message])


def manage_table():
    db.connect()
    #db.create_tables([UserFinishTrack,])
    #db.create_tables([UserFinishTrack,UserStatus])
    #db.drop_tables([UserFinishTrack,UserStatus], safe=True)

#####

if __name__ == '__main__':
       create_table()
          #manage_table()
