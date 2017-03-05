#!/usr/bin/env python
# encoding: utf-8
import arrow


def get_now_timestamp():
    utc = arrow.utcnow()
    # 使用utc的，最后要表现的时候才加上local
    #local = utc.to('Asia/Shanghai')
    return utc.timestamp
    # return local.format('YYYY-MM-DD HH:mm:ss')


def timestamp2time(timestamp):
    utc = arrow.get(timestamp)
    local = utc.to('Asia/Shanghai')
    return local.format('YYYY-MM-DD HH:mm:ss')

def totimestamp(time_string):
    a=arrow.get(time_string, 'YYYY-MM-DD HH:mm:ss')
    return a.timestamp #之后使用timestamp2time 试试

def broadcast(itchat,message,target_groups):
    # 给所有群广播消息
    for group in target_groups:
        itchat.send(message, group._group_id)

if __name__ == '__main__':
    print(timestamp2time(get_now_timestamp()))  # ok
