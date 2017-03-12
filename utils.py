#!/usr/bin/env python
# encoding: utf-8
import arrow
import hashlib


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

def get_user_img(itchat,msg,user_img,group_id):
            '''
            user_img = UserImgCache()
            '''
            group_user_id = msg["ActualUserName"]
            url_get_with_user_id = user_img.get_user_img_with_user_id(group_user_id)  # 第一层缓存 , 掉线后，group_user_id变化
            if url_get_with_user_id:
                #message2push["user_img"] = url_get_with_user_id #return
                return url_get_with_user_id
                #logger.info("url_get_with_user_id: %s" ,message2push["user_img"])
            else:
                # 重新登录user id 变了，但是img md5还有效
                #logging.debug("ActualUserName :%s, src_group _group_id: %s", msg["ActualUserName"], src_group._group_id)
                img_data = itchat.get_head_img(userName=group_user_id, chatroomUserName=group_id)  # .getvalue()#前头是str #有时候错误
                # logging.debug(img_data)
                img_md5 = hashlib.md5(buffer(img_data)).hexdigest()
                url_get_with_img_md5 = user_img.get_user_img_with_img_md5(img_md5)
                if url_get_with_img_md5:
                    #message2push["user_img"] = url_get_with_img_md5
                    return url_get_with_img_md5
                    #logger.info("url_get_with_img_md5: %s", message2push["user_img"])
                else:
                    # 如果两级缓存都没有命中,再上传头像
                    url_with_uploading_img = user_img.set_user_img(group_user_id, buffer(img_data))

                    #message2push["user_img"] = url_with_uploading_img
                    return url_with_uploading_img
                    #logger.info("url_with_uploading_img: %s",message2push["user_img"])


if __name__ == '__main__':
    print(timestamp2time(get_now_timestamp()))  # ok
