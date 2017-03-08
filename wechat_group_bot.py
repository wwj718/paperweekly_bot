#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals
import time
import os
import yaml
import random
import re
import datetime
import thread
import db_store
import hashlib
from localuser import LocalUserTool, UserImgCache
import itchat
# ,ATTACHMENT,VIDEO, RECORDING #语音
from itchat.content import TEXT, PICTURE, SHARING
import plugin
from utils import  broadcast,timestamp2time

from threading import Timer

# log
import logging.config


def setup_logging(
    default_path='logging.yaml',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
setup_logging()
logger = logging.getLogger(__name__)
chat_message_recorder_logger = logging.getLogger("chat_message_recorder")

# setting
import setting
# 把头像改为可选
USE_LEANCLOUD_FOR_LOG = setting.USE_LEANCLOUD_FOR_LOG
USE_LEANCLOUD_FOR_IMAGE = setting.USE_LEANCLOUD_FOR_IMAGE
DEBUG = setting.DEBUG
if USE_LEANCLOUD_FOR_LOG:
    from leancloud_store import push_message


# action
IN_ACTION = False


def end_action():
    # todo 通知所有群
    global IN_ACTION
    global groups
    message="@all 提问时间结束:)"
    active_target_groups = [group for group in groups if group._group_id]
    IN_ACTION = False
    broadcast(itchat,message,active_target_groups)


def begin_action():
    global IN_ACTION
    IN_ACTION = True
    t = Timer(setting.ACTION_TIME, end_action)
    t.start()


class GroupBot(object):  # 没必要多线程

    def __init__(self, group_name):
        self._group_name = group_name
        self._group_id = None

    def __str__(self):
        return self._group_name

    def set_id(self, group_id):
        self._group_id = group_id

    def __repr__(self):
        return self._group_name

    def simple_reply(msg):
        print("reply message!")

def forward_message(msg, src_group, target_groups):
    '''按类型发消息'''
    msg["UserImg"] = '' #成为一个开关 只有开启采用
    if msg["Type"] == 'Text':
        '''
        #print(itchat.get_friends())
        # 消息入口
        username = msg["ActualUserName"] # 发言用户id 群id:FromUserName
        user = itchat.search_friends(userName=username)
        '''
        logger.info("forward_message begin")  # log for debug
        logger.info(("forward message : ", msg)) #这里有所有的信息

        # 多给msg一个属性 at_id
        message2push = {}
        message2push["group_name"] = src_group._group_name
        message2push["content"] = msg["Text"]
        message2push["group_user_name"] = msg["ActualNickName"]
        message2push["CreateTime"] = timestamp2time(int(msg["CreateTime"]))
        try:
            # todo 这个那个包装为一个函数 减少副作用 传入什么 ，输出什么
            # 部分用户无法获取头像  chatroomid 错误 原因在itchat username
            # user_head_img = itchat.get_head_img(userName=msg["ActualUserName"],chatroomUserName=src_group._group_id,picDir="/tmp/wechat_user/{}".format(img_id)) #存储到本地
            # 第一层缓存，获取头像之前，先检查本轮对话中 msg["ActualUserName"]
          if USE_LEANCLOUD_FOR_IMAGE:
            #from localuser import LocalUserTool, UserImgCache
            user_img = UserImgCache()
            group_user_id = msg["ActualUserName"]
            url_get_with_user_id = user_img.get_user_img_with_user_id(group_user_id)  # 第一层缓存 , 掉线后，group_user_id变化
            if url_get_with_user_id:
                message2push["user_img"] = url_get_with_user_id #return
                #logger.info("url_get_with_user_id: %s" ,message2push["user_img"])
            else:
                # 重新登录user id 变了，但是img md5还有效
                #logging.debug("ActualUserName :%s, src_group _group_id: %s", msg["ActualUserName"], src_group._group_id)
                img_data = itchat.get_head_img(userName=msg["ActualUserName"], chatroomUserName=src_group._group_id)  # .getvalue()#前头是str #有时候错误
                # logging.debug(img_data)
                img_md5 = hashlib.md5(buffer(img_data)).hexdigest()
                url_get_with_img_md5 = user_img.get_user_img_with_img_md5(img_md5)
                if url_get_with_img_md5:
                    message2push["user_img"] = url_get_with_img_md5
                    #logger.info("url_get_with_img_md5: %s", message2push["user_img"])
                else:
                    # 如果两级缓存都没有命中,再上传头像
                    url_with_uploading_img = user_img.set_user_img(group_user_id, buffer(img_data))

                    message2push["user_img"] = url_with_uploading_img
                    #logger.info("url_with_uploading_img: %s",message2push["user_img"])
            msg["UserImg"] = message2push["user_img"] #.get("user_img")
        except Exception as e:
            logger.error("can not get user head img")
            logger.error('Failed to open file', exc_info=True)

        try:
            # 日志系统
            if USE_LEANCLOUD_FOR_LOG:
                logger.info("ready to push message to cloud")
                push_message(message2push)
            logger.info("ready to push message to local file")
            #logger.info(message2push)
            logger.info("ready to push message to local db(sqlite)")
            db_store.push_message(message2push)
        except Exception as e:
            logger.error("log error")
            logger.info(str(e))
            # todo 有空优化

        chat_message_recorder_logger.info(message2push) #记录所有待推送到云端的信息 时间
        actual_user_name = msg["ActualNickName"]
        # for at id
        localuser_tool = LocalUserTool()

        # feature ： at_id todo:插件化
        at_id = localuser_tool.get_at_id(actual_user_name)
        if not at_id:
            at_id = localuser_tool.set_at_id(actual_user_name)
        # 改造消息对象，使其多一个at_id
        msg["at_id"] = at_id
        match_at_message = re.match(
            r'at *(?P<message_at_id>\d+) *(?P<message_text>.*)', msg["Text"])
        if match_at_message:
            # 如果是at意图的消息
            groupdict = match_at_message.groupdict()
            message_at_id = groupdict.get("message_at_id")
            message_text = groupdict.get("message_text")
            actual_user_name = localuser_tool.get_actual_user_name(
                int(message_at_id))

            for group in target_groups:
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info((now, group._group_name, msg[
                            'ActualNickName'], msg["Text"]))
                # 加入群名 group._group_name 做一个映射
                message = u'@{} \n{}-at_id:{} 发言 ：\n{}'.format(
                    actual_user_name, msg['ActualNickName'], msg['at_id'], message_text)
                #message = u'@{}\u2005\n : {}'.format(actual_user_name,message_text)
                itchat.send(message, group._group_id)
        else:
            # 如果不是at消息：即普通文本消息
            # bot回复论坛消息
            # handle_text_msg对消息做个分类，只做分析，handle_text_msg不主动发送消息，此处可嵌入插件
            response = handle_text_msg(msg).get("response")
            if response:
                # 只回复本群
                itchat.send(response, src_group._group_id)
            else:
                # 推送到其他群
                for group in target_groups:
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    logger.info((now, group._group_name, msg[
                                'ActualNickName'], msg["Text"]))
                    # if group._group_id:
                    message = '{}-at_id:{} 发言 ：\n{}'.format(
                        msg['ActualNickName'], msg['at_id'], msg['Text'])
                    itchat.send(message, group._group_id)  # 采用异步
    # 之后的消息统一转发
    if msg["Type"] == 'Picture':
            # todo：上传到云端
        msg['Text'](msg['FileName'])  # 下载 其他大文件 异步使用另一个线程
        for group in target_groups:
            itchat.send_image(msg['FileName'], group._group_id)

    if msg['Type'] == 'Sharing':
        # todo: 同样作为普通消息存入log
        share_message = "@{}分享\n{} {}".format(
            msg['ActualNickName'], msg["Url"].replace("amp;", ""), msg["Text"])
        for group in target_groups:
            itchat.send_msg(share_message, group._group_id)


def get_target_groups(src_group, groups):
    '''
    src_group 是 对象
    groups: 所有的微信组，全集
    todo 写为内部函数
    '''
    list_groups = list(groups)
    list_groups.remove(src_group)  # target groups
    return list_groups
    #print("from {} to {}".format(src_group._group_name,",".join([group._group_name for group in list_groups])))


def handle_text_msg(msg):
    global IN_ACTION
    # todo 改变调度机制 目前非常不自然
    username = msg['ActualNickName']  # 发言者,昵称
    content = msg['Text']
    userlogo = msg["UserImg"]
    # 触发
    if username in setting.ACTION_ADMIN and setting.ACTION_KEYWORD in content:
        begin_action()
        response = "活动开始! 2小时后结束:)"
        return {'type': 'b', 'response': response}  # 活动开始 群发
    if '[咖啡]' in content and IN_ACTION:
        # 发帖 正则匹配
        clean_content = re.split(r'\[咖啡\]', content)[-1]
        if clean_content:
            # todo :之后重构到插件里 目前本末倒置了
            clean_content = "<span class='api_icon'>![](" + userlogo + \
                ")</span><span class='api_nickname'>" + username + "</span>" + clean_content
            try:
                # 丢到线程里 timeout
                plugin.msg_input(msg=clean_content)
            except Exception as e:
                logger.error(str(e))

            # 此处对接论坛的webhook
            # 类似 forum_client.post_thread(username,clean_content)
            # 其中username为微信用户昵称，clean_content为发帖内容
            response = "@{} 提问成功：）".format(username)
            return {'type': 'q', 'response': response}
    # if '/bot/t' in content:
    '''
    if content.startswith('[得意]'):
        #回帖
        #判断下正则是够合格
        thread_id,clean_content = re.split(r'\[得意\].*?(?P<id>\d+)', content)[-2:]
        response = "回帖成功:)"
        return {'type':'t','response':response}
    '''
    # if '/bot/h' in content:
    if '[疑问]' in content:
        # help
        #response='Hi @{} 使用说明如下：\n帮助:[闭嘴]\n发帖:[疑问] 帖子内容\n回帖:[得意](id) 回复内容\n搜索:[惊讶] 问题内容'.format(msg['ActualNickName'])
        response = 'Hi @{} 使用说明如下：\n帮助:[疑问]\n提问:[咖啡] 问题内容'.format(
            msg['ActualNickName'])
        return {'type': 'h', 'response': response}
    return {'type': None, 'response': None}  # 无标记


# 全局设置
if DEBUG:
    group1_name = 'paper测试1'
    group2_name = 'paper测试2'
    group3_name = '测试m'
    group1 = GroupBot(group_name=group1_name)
    group2 = GroupBot(group_name=group2_name)
    group3 = GroupBot(group_name=group3_name)
    groups = (group1, group2, group3)  # ,group4)  #list原有结构会被改变 ,内部元素是够会不可变
    #topic groups pw
    # 主题群消息定期发往大群
    topic_groups=()
    #other group ai100
    other_group_map= {} #用于存储id->name 映射
else:
    # 注意 ai100使用过程发现群名字符串不能有包含关系，否则可能造成错误
    # 量子位今天的异常也是这个原因
    group1_name = 'PaperWeekly交流群'
    group2_name = 'PaperWeekly交流二群'
    group3_name = 'PaperWeekly交流三群'
    group4_name = 'PaperWeekly交流四群'
    group5_name = 'PaperWeekly交流五群'
    group1 = GroupBot(group_name=group1_name)
    group2 = GroupBot(group_name=group2_name)
    group3 = GroupBot(group_name=group3_name)
    group4 = GroupBot(group_name=group4_name)
    group5 = GroupBot(group_name=group5_name)
    # list原有结构会被改变 ,内部元素是够会不可变
    groups = (group1, group2, group3, group4, group5)

    #topic groups pw
    # 主题群消息定期发往大群
    topic_groups=()
    #other group ai100
    other_group_map= {} #用于存储id->name 映射


# 全局入口
def main():
    # 群聊，TEXT(filter)
    @itchat.msg_register([TEXT, SHARING, PICTURE], isGroupChat=True)
    def simple_reply(msg):
        global groups
        global other_group_map
        print("group message input from wechat(begin)")
        # 互相转发的群
        for group in groups:
            #logger.info(("local_group", group._group_id, group._group_name))
            #logger.info("msg from group:{}".format(msg['FromUserName']))
            if msg['FromUserName'] == group._group_id:
                # 一条消息只能匹配一次
                src_group = group  # 消息来源群组
                target_groups = get_target_groups(src_group, tuple(groups))  # 消息发往的目标群
                # 筛选出已激活的
                active_target_groups = [group for group in target_groups if group._group_id]
                forward_message(msg, src_group, active_target_groups)  # !!内部逻辑入口
            if not group._group_id:
                # 如果群未被激活，则开始搜索群id
                # 每条消息都找一下，维护一个全局群id列表
                group_instance = itchat.search_chatrooms(name=group._group_name)
                if group_instance:
                    group.set_id(group_instance[0]['UserName'])
                    print("{}激活,group_id:{}".format(group._group_name, group._group_id))
                    if DEBUG:
                        itchat.send_msg('机器人已激活: )', group._group_id)

        # todo 都需要头像 拆分出来

        # topic groups 只定期发送到大群
        # forward_message(msg, src_group, active_target_groups)
        # 也是只存储，只是定期看一下数据，然后转让，定时任务
        # 定时任务 不影响主线程 https://github.com/mrhwick/schedule/blob/master/schedule/__init__.py 仅仅把schedule.run_pending()改为run_continuously()
        # 使用本地数据库查询 时间用timestamp arrow
        #db_store.push_message(message2push)
        #然后写查询 每2小时查询一下 pillow生成图片 使用jupyter来做
        # 大体上的布局 [xx]:xxx
        # 需求 摘要+链接(网页)
        ##############################################
        # log other groups  记录群消息
        # 作为群的一种类型 如果是这种类型的消息则不转发 只存储
        # 获取群名，获取头像 独立函数 缓存

        is_other_groups_msg = msg['FromUserName'] not in [group._group_id for group in groups]
        if setting.PUSH_ALL_GROUP_MESSAGE_TO_LEANCLOUD and is_other_groups_msg:
            # 没有头像
            from leancloud_store import push_message
            other_group_FromUserName = msg['FromUserName']
            other_group_NickName =  other_group_map.get(other_group_FromUserName)
            # 建立缓存 维护一个字典即可，不需要永久化 todo 头像也这样做
            if not other_group_NickName:
                other_group = itchat.search_chatrooms(userName=other_group_FromUserName)
                other_group_NickName = other_group["NickName"]
                logger.debug("store other_group_NickName to other_group_map")
                other_group_map[other_group_FromUserName] = other_group_NickName
            message2push={}
            message2push["content"] = msg["Text"]
            message2push["group_user_name"] = msg["ActualNickName"]
            message2push["CreateTime"] = timestamp2time(int(msg["CreateTime"]))
            message2push["group_name"] = other_group_NickName
            logger.info("ready to push other group message to cloud")
            push_message(message2push)

            #import IPython;IPython.embed()

    # print "End Main function"

itchat.auto_login(enableCmdQR=2, hotReload=True)  # 调整宽度：enableCmdQR=2
thread.start_new_thread(itchat.run, ())

while True:
    main()
    time.sleep(1)
