#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals
import time
import random
import re
import datetime
import thread
from localuser import LocalUserTool,UserImgCache
import db_store
import hashlib
import itchat
from itchat.content import TEXT, PICTURE, SHARING #  ,ATTACHMENT,VIDEO, RECORDING #语音

##########log
import logging
LOG_FILE = "/tmp/wechat_4group.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler(LOG_FILE)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

#######setting
USE_LEANCLOUD = False #默认不使用消息云存储
if USE_LEANCLOUD:
    from leancloud_store import push_message


#########


#class GroupBot(threading.Thread): # 作为threading类
class GroupBot(object):  # 没必要多线程
    """Docstring for GroupBot. """

    def __init__(self, group_name):
        """TODO: to be defined1.

        :group_name: TODO

        """
        #threading.Thread.__init__(self)
        self._group_name = group_name
        self._group_id = None

    def __str__(self):
        return self._group_name
    def set_id(self,group_id):
        self._group_id = group_id


    def __repr__(self):
        return self._group_name
    #@itchat.msg_register([TEXT,SHARING,PICTURE], isGroupChat=True)  # 群聊，TEXT ， 可视为已经完成的filter
    def simple_reply(msg):
        print("reply message!")  # 消息接受在主进程中接受一次即可,没必要多线程,需要一个只能的send_message

    def run(self):
        wait_time = random.randrange(1, 3)
        print("thread {}(group_name:{}) will wait {}s".format(
            self.name, self._group_name, wait_time))  # 默认的名字:Thread-1
        time.sleep(wait_time)
        print("thread {} finished".format(self.name))


def forward_message(msg,src_group,target_groups):
    '''按类型发消息'''
    if msg["Type"] == 'Text':
        '''
        print(itchat.get_friends())
        # 消息入口
        logger.info(msg)
        username = msg["ActualUserName"] # 发言用户id 群id:FromUserName
        user = itchat.search_friends(userName=username)
        '''
        logger.info("forward_message begin") # log
        logger.info(("forward message : ",msg)) # log
        # 跨群@ , 至于私聊 可以截图发微信号
        #把用户都存下,多给msg一个属性 at_id
        # logger.info((now, group._group_name, msg['ActualNickName'], msg["Text"]))
        # 存入云端
        message2push = {}
        message2push["group_name"] = src_group._group_name
        message2push["content"] = msg["Text"]
        message2push["group_user_name"] = msg["ActualNickName"]
        try:
            # 头像
            #user_head_img = itchat.get_head_img(userName=msg["ActualUserName"],chatroomUserName=src_group._group_id,picDir="/tmp/wechat_user/{}".format(img_id)) #存储到本地
            # todo:第一层缓存，获取头像之前，先检查本轮对话中 msg["ActualUserName"] 是否被记录在本地数据库,免去向微信请求
            user_img = UserImgCache()
            group_user_id = msg["ActualUserName"]
            url_get_with_user_id = user_img.get_user_img_with_user_id(group_user_id) #第一层缓存
            if url_get_with_user_id:
                message2push["user_img"] = url_get_with_user_id
                logger.info(("url_get_with_user_id: "+message2push["user_img"]))
            else:
                #重新登录user id 变了，但是img md5还有效
                img_data = itchat.get_head_img(userName=msg["ActualUserName"],chatroomUserName=src_group._group_id)#.getvalue()#前头是str
                img_md5= hashlib.md5(buffer(img_data)).hexdigest()
                url_get_with_img_md5 = user_img.get_user_img_with_img_md5(img_md5)
                if url_get_with_img_md5:
                    message2push["user_img"] = url_get_with_img_md5
                    logger.info(("url_get_with_img_md5: "+message2push["user_img"]))
                else:
                    # 如果两级缓存都没有命中
                    url_with_uploading_img = user_img.set_user_img(group_user_id,buffer(img_data))
                    message2push["user_img"] = url_with_uploading_img
                    logger.info(("url_with_uploading_img: "+message2push["user_img"]))
        except Exception as e:
            logger.info("can not get user head img")
            logger.info(str(e))

        try:
            logger.info("ready to push message to cloud")
            if USE_LEANCLOUD:
                push_message(message2push)
            logger.info("ready to push message to local db(sqlite)")
            logger.info(message2push)
            db_store.push_message(message2push)
        #except e:
        except Exception as e:
            logger.info("can not push message")
            logger.info(str(e))
            # 这样不好 ，有空优化

        actual_user_name = msg["ActualNickName"]
        # for at id
        localuser_tool = LocalUserTool()
        at_id = localuser_tool.get_at_id(actual_user_name)
        if not at_id:
            at_id = localuser_tool.set_at_id(actual_user_name)
        # 改造消息属性，使其多一个at_id
        msg["at_id"] = at_id
        match_at_message = re.match(r'at *(?P<message_at_id>\d+) *(?P<message_text>.*)', msg["Text"])
        if match_at_message:
            # at 的消息
            groupdict = match_at_message.groupdict()
            message_at_id = groupdict.get("message_at_id")
            message_text = groupdict.get("message_text")
            actual_user_name = localuser_tool.get_actual_user_name(int(message_at_id))

            for group in target_groups:
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info((now, group._group_name, msg['ActualNickName'], msg["Text"]))
                message = u'@{} \n{}-at_id:{} 发言 ：\n{}'.format(actual_user_name,msg['ActualNickName'],msg['at_id'],message_text)
                #message = u'@{}\u2005\n : {}'.format(actual_user_name,message_text)
                itchat.send(message,group._group_id)
        else:
            #普通文本消息
            # bot回复论坛消息
            response = handle_text_msg(msg).get("response") #来源小组不一样，回复
            if response:
                itchat.send(response,src_group._group_id)
            # 推送到其他群
            else:
              #如果是网往论坛的则不转发
              for group in target_groups:
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info((now, group._group_name, msg['ActualNickName'], msg["Text"]))
                #if group._group_id:
                message = '{}-at_id:{} 发言 ：\n{}'.format(msg['ActualNickName'],msg['at_id'],msg['Text'])
                itchat.send(message,group._group_id) # 采用异步

    if msg["Type"] == 'Picture':
            # todo：上传到云端
            msg['Text'](msg['FileName'])  #下载
            for group in target_groups:
                itchat.send_image(msg['FileName'], group._group_id)

    if msg['Type'] == 'Sharing':
        # 同样作为普通消息存入云端
        share_message = "@{}分享\n{} {}".format(
            msg['ActualNickName'], msg["Url"].replace("amp;", ""), msg["Text"])
        for group in target_groups:
            itchat.send_msg(share_message, group._group_id)


def get_target_groups(src_group, groups):
    '''
    src_group 是 对象
    groups: 所有的微信组，全集
    '''
    list_groups = list(groups)
    list_groups.remove(src_group)  # target groups
    return list_groups
    #print("from {} to {}".format(src_group._group_name,",".join([group._group_name for group in list_groups])))

def handle_text_msg(msg):
    #username = msg['ActualNickName'] # 发言者
    content = msg['Text']

    if '[疑问]' in content:
        #发帖
        clean_content = re.split(r'\[疑问\]', content)[-1]
        # 此处对接论坛的webhook
        #forum_client.post_thread(username,clean_content)
        response = "发帖成功：）"
        return {'type':'q','response':response}
    #if '/bot/t' in content:
    if content.startswith('[得意]'):
        #回帖
        #判断下正则是够合格
        thread_id,clean_content = re.split(r'\[得意\].*?(?P<id>\d+)', content)[-2:]
        response = "回帖成功:)"#forum_client.post_reply(username,thread_id,clean_content)
        return {'type':'t','response':response}
    #if '/bot/h' in content:
    if '[闭嘴]' in content:
        #help
        #response='Hi @{} 使用说明如下：\n帮助:[闭嘴]\n发帖:[疑问] 帖子内容\n回帖:[得意](id) 回复内容\n搜索:[惊讶] 问题内容'.format(msg['ActualNickName'])
        response='Hi @{} 使用说明如下：\n帮助:[闭嘴]\n发帖:[疑问] 帖子内容\n回帖:[得意](id) 回复内容'.format(msg['ActualNickName'])
        return {'type':'h','response':response}
    return {'type':None,'response':None}




# 全局设置
group1_name = 'paper测试1'
group2_name = 'paper测试2'
group3_name = '测试m'
#group1_name = 'PaperWeekly交流群'
#group2_name = 'PaperWeekly交流二群'
#group3_name = 'PaperWeekly交流三群'
#group4_name = 'PaperWeekly交流四群'
group1 = GroupBot(group_name=group1_name)
group2 = GroupBot(group_name=group2_name)
group3 = GroupBot(group_name=group3_name)
#group4 = GroupBot(group_name=group4_name)
groups = (group1, group2, group3)#,group4)  #list原有结构会被改变 ,内部元素是够会不可变



def main():

    @itchat.msg_register([TEXT,SHARING,PICTURE], isGroupChat=True)  # 群聊，TEXT ， 可视为已经完成的filter
    def simple_reply(msg):
        #设置为nolocal
        global groups
        print("group message input") #itchat 1.2.18 每次信息确实来这里了
        for group in groups:
            logger.info(("local_group",group._group_id,group._group_name))
            logger.info("meg from group:{}".format(msg['FromUserName']))
            if msg['FromUserName'] == group._group_id: # 一条消息只能匹配一次
                src_group = group
                target_groups = get_target_groups(src_group, tuple(groups))
                # 筛选出已激活的
                active_target_groups = [group for group in target_groups if group._group_id]
                forward_message(msg,src_group,active_target_groups)
            if not group._group_id:
                print(group._group_id) #None
                # 不存在的时候
                #如果找到群id就不找，否则每条消息来都找一下,维护一个群列表,全局
                group_instance = itchat.search_chatrooms(name=group._group_name
                                                         )  #本地测试群
                if group_instance:
                    group.set_id(group_instance[0]['UserName']) #没有设置成功？
                    print("{}激活,group_id:{}".format(group._group_name,group._group_id))
                    itchat.send_msg('机器人已激活: )', group._group_id)

    #print "End Main function"

itchat.auto_login(enableCmdQR=2,hotReload=True) #调整宽度：enableCmdQR=2
thread.start_new_thread(itchat.run, ())

while 1:
    main()
    time.sleep(1)

