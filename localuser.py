#!/usr/bin/env python
# encoding: utf-8

# 构建一个用户模型
# 消息来得时候构建用户
from tinydb import TinyDB, where, Query
import time
import hashlib
#from leancloud_store import push_message, save_file
import uuid


class LocalUserTool(object):
    '''
    数据库作为类属性
    是一个工具类
    实质上是数据存储/检索类

    todo 重构为peewee 使用model更直观

    为用户的群昵称和at_id建立关系
    '''
    DB = TinyDB("localuser" + ".json")
    # 删掉旧的
    # TABLE= DB.table("localuser"+str(int(time.time()))) # 加上时间戳
    DB.purge_tables()  # 移除所有表格
    TABLE = DB.table("localuser")  # 加上时间戳

    def __init__(self):
        """TODO: to be defined1.
        :userid: TODO
        """
        pass

    def get_actual_user_name(self, at_id):
        '''
        根据at_id获取用户昵称 ， 用于at
        '''
        # userid = msg["ActualUserName"] # 用户在群里的名字 , 可at
        Record = Query()
        localuser = self.TABLE.get(Record.at_id == at_id)  # dict
        if localuser:
            return localuser.get("actual_user_name")

    def get_at_id(self, actual_user_name):
        Record = Query()
        localuser = self.TABLE.get(
            Record.actual_user_name == actual_user_name)  # dict
        if localuser:
            return localuser.get("at_id")

    def set_at_id(self, actual_user_name, groupid=None):
        '''
        设置用户at_id
        '''
        # 检验msg["ActualUserName"]是够已分配at_id，如果没有则分配，如果有则
        #new_record["actual_user_name"] = userid
        localuser = {}
        localuser["actual_user_name"] = actual_user_name
        localuser["groupid"] = groupid
        localuser["at_id"] = len(self.TABLE.all()) + 1  # 自增,从1开始
        self.TABLE.insert(localuser)
        return localuser["at_id"]
        # 获取用户信息，如果存在则获取，不存在则添加


class UserImgCache(object):
    '''
    缓存用户头像
    首先通过user_id看看是否存在，如果不存在else if img_md5  如果都不存在，就上传
    test it
    '''
    DB = TinyDB("user_img_cache" + ".json")
    TABLE = DB.table("user_img_cache")  # 加上时间戳 这个表不应该每次清空

    def __init__(self):
        pass

    def get_user_img_with_user_id(self, group_user_id):
        # 使用昵称还是id  id每次会变 昵称可能不唯一
        Record = Query()
        localuser = self.TABLE.get(
            Record.group_user_id == group_user_id)  # dict
        if localuser:
            return localuser.get("img_url")

    def get_user_img_with_img_md5(self, img_md5):
        Record = Query()
        localuser = self.TABLE.get(Record.img_md5 == img_md5)  # dict
        if localuser:
            return localuser.get("img_url")

    def set_user_img(self, group_user_id, img_data):
        # 一次设置好，用户的信息 类比at id
        # 只在确认用户头像没有上传的情况下才调用此函数
        '''
        img_data 是 buffer
        '''
        from leancloud_store import save_file
        localuser = {}
        localuser["group_user_id"] = group_user_id
        # 一致 26771cad667b860261090a8d52f3299c wwj
        img_md5 = hashlib.md5(img_data).hexdigest()
        localuser["img_md5"] = img_md5
        #cloud_file = leancloud.File(filename, data)
        # cloud_file.save()
        fime_name = uuid.uuid4().get_hex()[:10] + ".png"
        url = save_file(fime_name, img_data)
        localuser["img_url"] = url
        self.TABLE.insert(localuser)
        return localuser["img_url"]


def main():
    pass
    '''
    localuser_tool = LocalUserTool()
    print(localuser_tool.get_actual_user_name(10))
    at_id = localuser_tool.get_at_id("@abc")
    if not at_id:
        localuser_tool.set_at_id("@abc")
    at_id = localuser_tool.get_at_id("@abc")
    print(localuser_tool.get_actual_user_name(at_id))
    '''


if __name__ == '__main__':
    main()
