#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals
import sys;reload(sys);sys.setdefaultencoding('utf8') #中文编码问题
from os.path import dirname, join
import pandas as pd
import sqlite3
#import re
#import sys
#import datetime
import pandas
import arrow # pip install

try:
    from StringIO import StringIO
except:
    #python3有问题
    from io import StringIO
import os
import uuid
#import shlex
#import csv
import codecs
from collections import namedtuple
# 变为flask
from flask import Flask, send_file
from flask import render_template
#upload pdf
from flask import Flask, request, redirect, url_for,flash
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = '/home/ubuntu/www_paperweekly/uploads'
ALLOWED_EXTENSIONS = set(['pdf'])

##CSV_UPLOAD_FOLDER = '/home/ubuntu/www_paperweekly/upload_csv'
CSV_UPLOAD_FOLDER = '/home/ubuntu/paperweekly_bot/bokeh_app/upload_csv'
#CSV_UPLOAD_FOLDER = '/tmp/upload_csv'
CSV_ALLOWED_EXTENSIONS = set(['csv'])

def update(begin=0):
    conn = sqlite3.connect(join(dirname(__file__), '../group_chat_message.db'))
    query = "SELECT * FROM message ORDER BY createdAt"  # 排序 时间
    df = pd.read_sql_query(query, conn)
    df['createdAt'] = pandas.to_datetime(df['createdAt'], unit='s',utc=True)#.tz_localize('UTC').tz_convert('Asia/Shanghai')
    df.index=df['createdAt']
    df['createdAt'] = pd.to_datetime(df['createdAt']).dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
    #embed()
    arw = arrow.utcnow()
    utc = arw.to('Asia/Shanghai')
    button_group_value_date = utc.replace(days=-begin)#几天
    #begin_date = button_group_value_date[begin]#utc.replace(days=-1)
    begin_date_string=button_group_value_date.format(fmt='YYYY-MM-DD')
    print(begin_date_string)
    #df = df[(df['createdAt']>"2017-6-7") & (df['createdAt']<"2017-6-9")]#.tail()
    df = df[(df['createdAt']>begin_date_string)]#.tail()
    df.index=df['createdAt']
    df["createdAt"]= df.createdAt.apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
    csv_df = df[['content','group_name', 'group_user_name','user_img','createdAt']]
    # 只取几个属性
    '''
    source.data = {
        'group_name': current.group_name,
        'group_user_name': current.group_user_name,
        'content': current.content,
        #'user_img': current.user_img,
        #df['datetime'].apply(lambda x: x.strftime('%d%m%Y'))
        'createdAt': current.createdAt.apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S')),#pd.to_datetime(current.createdAt,format="%Y%m%d-%H%M%S"), #展示为字符
    }
    '''
    buffer = StringIO()
    csv_df.to_csv(buffer,index=False,header=False,sep=str("|"),encoding='utf-8')#,quoting=csv.QUOTE_NONNUMERIC) #content加上双引号
    buffer.seek(0)
    return send_file(buffer,
                 attachment_filename="test.csv",
                 mimetype='text/csv')


#button_group = RadioButtonGroup(labels=["1day(today)", "1week", "1month","0.5year","1year"], active=0)
#@app.route('/')

@app.route('/date/<int:page_id>')
def begin_date(page_id):
    # 作为参数传递 begin=[0,1,2,3,4]
    # 传入数字
    # <input type="number" name="quantity" min="1" max="5">
    begin = page_id#request.args.get('begin',)
    return update(begin) #'Hello World!'

@app.route('/admin2358')
def hello_world():
    # 作为参数传递 begin=[0,1,2,3,4]
    # 传入数字
    #
    return  render_template("hello.html")



#@app.route('/upload_pdf')
#def upload_pdf():
#    return  render_template("upload_pdf.html")

def allowed_file(filename,EXTENSIONS=ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in EXTENSIONS

@app.route('/upload_pdf', methods=['GET', 'POST'])
def upload_file():
    #新的域名manage
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #中文问题
            file.save(os.path.join(UPLOAD_FOLDER, filename)) # 加上uuid 原本就没问题
            #url = #str(filename)
            url = "http://admin.paperweekly.site/uploads/{}".format(str(filename))
            return url
            #ok
            #return redirect(url_for('uploaded_file',
            #                        filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>上传pdf文件(文件名不能包含中文，后缀为pdf，如hello.pdf)</h1>
    <form method=post enctype=multipart/form-data>
         <input type=file name=file>
         <input type=submit value=上传>
    </form>
    '''

@app.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv_file():
    #新的域名manage
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename,CSV_ALLOWED_EXTENSIONS):
            #filename = secure_filename(file.filename) # uuid
            #now = arrow.utcnow().to('Asia/Shanghai').format('YYYY_MM_DD__HH_mm_ss')
            now = arrow.utcnow().to('Asia/Shanghai').format('YYYY_MM_DD')
            #中文问题
            #filename = "{}__{}".format(now,str(uuid.uuid4())[:6])
            filename = "{}__{}".format(now,str(uuid.uuid4())[:6])
            file.save(os.path.join(CSV_UPLOAD_FOLDER, filename)) # 加上uuid 原本就没问题

            #import IPython;IPython.embed()
            # 用这个内容去创建一个页面 处理这个csv 空行 分割csv
            #url = "http://admin.paperweekly.site/upload_csv/{}".format(str(filename))
            '''
            content = file.read().decode("utf-8");# 渲染为html
            content_list =  content.split("\n\n");
            content_context = [i.split("\n") for i in content_list]
            '''
            return redirect(url_for('message',
                                    csv_filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>上传csv文件(后缀为csv，如hello.csv)</h1>
    <form method=post enctype=multipart/form-data>
         <input type=file name=file>
         <input type=submit value=上传>
    </form>
    '''

# 展示 保存文件，传递文件名，渲染
def split_message(content):
    #strin=shlex.shlex(message.encode("utf-8"))
    #strin.whitespace=','
    #strin.whitesapce_split=True
    #b=list(strin)
    #return b
    #print(b)
    #csv.reader(message)
    #return  message.split(",")
    #return csv.reader(content,skipinitialspace=True) #unicode
    #r= re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', message) #re.split(r', (?=(?:"[^"]*?(?: [^"]*)*))|, (?=[^",]+(?:,|$))', message)
    #print r
    result = content.split("|")
    #print result
    if len(result)==5:
        return result
    else:
        print(content) #被过滤的


@app.route('/message/<csv_filename>')
def message(csv_filename):
    # 作为参数传递 begin=[0,1,2,3,4]
    # 传入数字
    # <input type="number" name="quantity" min="1" max="5">
    f = codecs.open(os.path.join(CSV_UPLOAD_FOLDER, csv_filename), 'r', 'UTF-8')
    #with open(os.path.join(CSV_UPLOAD_FOLDER, csv_filename)) as f:
    content = f.read()#.decode("utf-8");# 渲染为html
    content_list =  content.split("\n\n"); #把每个视为csv
    message_obj = namedtuple('Message', ["content","group_name","group_user_name","user_img","createdAt"])
    content_context = [[message_obj._make(split_message(message)) for message in message_group.split("\n") if split_message(message)]  for message_group in content_list]
    #content_context = [shlex.split(j) for i in content_list for j in i.split("\n") ] #[["xx","aa"]]
    # 三层list
    #content_context = [line for line in content_list_lines]
    # 图片还是文字
    #print content_context
    return render_template("test.html",content_context=content_context)
    #return str(content_context)

    # 展示 放到数据库里，peewee 增删改 高级views
    # 仅仅是展示 直接渲染为jinja html 返回链接 uuid
    # ui bootstrap chat

@app.route('/list/message')
def list_message():
    # 作为参数传递 begin=[0,1,2,3,4]
    # 传入数字
    # <input type="number" name="quantity" min="1" max="5">
    # todo 打开这个目录 CSV_UPLOAD_FOLDER 列出文件
    files = os.listdir(CSV_UPLOAD_FOLDER)
    #print files
    return render_template("list.html",files=files)
    #return str(content_context)

    # 展示 放到数据库里，peewee 增删改 高级views
    # 仅仅是展示 直接渲染为jinja html 返回链接 uuid
    # ui bootstrap chat


if __name__ == '__main__':
    #app.debug = True
    app.run()


