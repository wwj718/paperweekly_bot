# paperweekly bot
paperweekly_bot 拆分自paper weekly，组件之一，当时为paperweek设计，多数需求也来自群友的讨论，具体设计可以参考我的这篇文章：

这部分似乎挺多人都需要（我的两个朋友的创业公司都用到它，最近infoq和ai100也打算采用）

所以我将它单独拆分出来，独立维护

# 准备增加的特性
*  消息云端存储、持久化（建议来自@MT）
*  消息管理界面
     *  es6/ webpack/react
*  维持心跳
     *  两个机器人 ping pong
*  大群模式（需求来自@蒋涛）
     *  由管理员开启开关
*  支持任意群互通
*   支持web页面扫码
     *  websocket
*  掉线消息提醒
     *  email

# todo
*  模块化，打包发布
*  文档

# 使用
```
# git clone 
pip install -r requirements.txt
set -x  LEANCLOUD_APP_ID xxx
set -x LEANCLOUD_APP_KEY xxx
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
