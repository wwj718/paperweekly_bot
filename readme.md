# paperweekly bot
paperweekly_bot 拆分自[paperweekly_forum](https://github.com/wwj718/paperweekly_forum)，是其组件之一，当时为paperweek设计，多数需求也来自群友的讨论，具体设计可以参考我的这篇文章：[论坛机器人的技术实现](http://blog.just4fun.site/paperweekly-forum-bot.html)

这部分似乎挺多人都需要（我的两个朋友的创业公司都用到它，最近infoq和ai100也打算采用）

所以我将它单独拆分出来，独立维护

# 准备增加的特性
*  消息云端存储、持久化（建议来自@MT）
*  消息管理界面
     *  es6/webpack/react
*  维持心跳
     *  两个机器人 互相ping pong
*  大群模式（需求来自@蒋涛）
     *  由管理员开启开关
*  支持任意群互通
*  支持web页面扫码
     *  websocket
*  掉线消息提醒
     *  email

# todo

- [ ]  模块化，打包发布
- [ ]  文档
- [x]  增加用户头像 
- [x]  升级itchat到1.2.18
- [x]  将用户头像upload到云端，同时做好本地缓存，避免每个用户都存储(使用md5) 
    - [x] 在本地存下hash和url （有一次img data网络请求）
    - [x] 单次优化，存下3元组（data_hash,userName,url） 只要有任意一个就不做网络请求
- [x] 使用py.test写测试：py.test test_localuser.py (vim  !py.test -s %)
- [ ] 构建本地存储（peewee），和云端存储继承自同一个类，通过设置文件设置
- [ ] 使用bokeh可视化数据 

# 使用
```
# git clone 
pip install -r requirements.txt
set -x  LEANCLOUD_APP_ID xxx  # or export LEANCLOUD_APP_ID=xxx
set -x LEANCLOUD_APP_KEY xxx
python db_store # 创建本地数据库（默认是sqlite，也可自行替换为mysql、PostgreSQL
python wechat_group_bot.py
```

# 新增特性文档
### 云端存储
使用leancloud,每条消息对象包括以下属性:

*  group_name
*  group_user_name
*  content
*  created time


详情参考leancloud管理台

![](http://oav6fgfj1.bkt.clouddn.com/lean5c45948b.png)
