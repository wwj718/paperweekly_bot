#!/usr/bin/env python
# encoding: utf-8
import sys
import json
import Queue
'''
Queue
#python2 ,熟悉一下 与list的区别线程安全？
put()方法在队尾插入一个项目
get()方法从队头删除并返回一个项目
先进先出 Queue.Queue(maxsize)

可能itchat需要加锁
'''
import time
import threading
sys.path.append("bot_plugin/plugins")
queue    = Queue.Queue()
# 插件目录作为搜索路径
def get_plugin():
    plugins = json.loads(open("./bot_plugin/plugins.json").read())
    for plugin in plugins["module"]:
        if plugin not in sys.modules:
            pass
            #globals()[plugin] = __import__(plugin)
            ##print(plugin) #plugin1
            exec("import %s" % plugin)
    return plugins["module"] # plugins list ,plugin filename

def plugin_runner(plugin,**kwargs):
    #print kwargs
    #print("plugin_runner begin")
    queue.put(1)
    result = sys.modules[plugin].run(**kwargs) #实现run方法
    queue.get()
    #print("plugin_runner end")

def msg_input(**kwargs):
    #对外暴露的插件入口,msg流过各个插件
    # todo 层层传递魔法参数，直到需要时到出 msg itchat
    #queue没有东西才运行，使用queue来协调，生产者消费者模型
    #print("msg_input begin")
    #print(kwargs)
    plugins = get_plugin() #耗时
    #print("plugin load ok")
    for plugin in plugins:
        #msg={"msg":"hello world"}
        #plugin_runner(plugin,**kwargs) #每次调用是key value **本身是dict
        t = threading.Thread(target=plugin_runner,args=(plugin,),kwargs=kwargs) #记得args加 , !
        t.start()
    #print("msg_input end")

if __name__ == '__main__':
    #print("main begin")
    msg={"msg":"hello world"}
    # try保护起来 不要在插件里出错
    msg_input(msg=msg)
    #print("main end")
