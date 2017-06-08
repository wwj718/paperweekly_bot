from __future__ import unicode_literals
from os.path import dirname, join
import pandas as pd
import sqlite3
import sys
import datetime
import pandas
import arrow # pip install 
#from pprint import pprint
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource, CustomJS,DatePicker
from bokeh.models.widgets import Slider, Button, DataTable, TableColumn, NumberFormatter, TextInput,RadioButtonGroup
from bokeh.io import curdoc
from IPython import embed
# https://pythonspot.com/sqlite-database-with-pandas/
'''
conn = sqlite3.connect(join(dirname(__file__), '../group_chat_message.db'))
query = "SELECT * FROM message ORDER BY createdAt"  # 排序 时间
df = pd.read_sql_query(query, conn)
'''
# print(df[:10]) #ok
# sys.exit(0)

source = ColumnDataSource(data=dict()) #变为全局



def update():
    #实时更新
    conn = sqlite3.connect(join(dirname(__file__), '../group_chat_message.db'))
    query = "SELECT * FROM message ORDER BY createdAt"  # 排序 时间
    df = pd.read_sql_query(query, conn)
    df['createdAt'] = pandas.to_datetime(df['createdAt'], unit='s',utc=True)#.tz_localize('UTC').tz_convert('Asia/Shanghai')
    df.index=df['createdAt']
    df['createdAt'] = pd.to_datetime(df['createdAt']).dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')
    # range
    #embed()
    #df[(df['createdAt']>datetime.date(2017,6,1)) & (df['createdAt']<datetime.date(2017,6,7))]
    #begin_time = 
    #end_time =
    #今天,昨天,过期一周,过去一个月,过去半年,过去1年 0,1,2,3,4
    arw = arrow.utcnow()
    utc = arw.to('Asia/Shanghai')
    #begin_date = utc.replace(months=-1)
    #YYYY-MM-DD HH:mm:ssZZ
    print(button_group.active)
    button_group_value_date = {0:utc.replace(days=-1),1:utc.replace(weeks=-1),2:utc.replace(months=-1),3:utc.replace(months=-6),4:utc.replace(years=-1)}
    begin_date = button_group_value_date[button_group.active]#utc.replace(days=-1)
    begin_date_string=begin_date.format(fmt='YYYY-MM-DD')
    print(begin_date_string)
    #df = df[(df['createdAt']>"2017-6-7") & (df['createdAt']<"2017-6-9")]#.tail()
    df = df[(df['createdAt']>begin_date_string)]#.tail()

    current = df[df.content.str.contains(
        search_text.value.strip()) == True]  # df[""]

    source.data = {
        'group_name': current.group_name,
        'group_user_name': current.group_user_name,
        'content': current.content,
        #'user_img': current.user_img,
        #df['datetime'].apply(lambda x: x.strftime('%d%m%Y'))
        'createdAt': current.createdAt.apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S')),#pd.to_datetime(current.createdAt,format="%Y%m%d-%H%M%S"), #展示为字符
    }

search_text = TextInput(title="search")
'''
beginning = DatePicker(title="Begin Date", min_date=datetime(2014,11,1),
                       max_date=datetime.now(),
                       value=datetime(datetime.now().year,1,1))
'''
button = Button(label="Download", button_type="success")

button_group = RadioButtonGroup(labels=["1day(today)", "1week", "1month","0.5year","1year"], active=0)

button.callback = CustomJS(args=dict(source=source),
                           code=open(join(dirname(__file__), "download.js")).read())
#search_text_val = search_text.value.strip()
#slider = Slider(title="开始时间", start=10000, end=250000, value=150000, step=1000)
#slider.on_change('value', lambda attr, old, new: update())
search_text.on_change('value', lambda attr, old, new: update())
button_group.on_change('active', lambda attr, old, new: update())

#export csv https://demo.bokehplots.com/apps/export_csv


columns = [
    TableColumn(field="group_name", title="Group Name"),
    TableColumn(field="group_user_name", title="Group User Name"),
    TableColumn(field="content", title="Content"),
    #TableColumn(field="user_img", title="User Img"),
    TableColumn(field="createdAt", title="createdAt"),
    #TableColumn(field="salary", title="Income", formatter=NumberFormatter(format="$0,0.00")),
]

data_table = DataTable(source=source, columns=columns, width=800)

controls = widgetbox(search_text,button_group,button)  # , button)
table = widgetbox(data_table)

curdoc().add_root(row(controls, table))
#curdoc().add_root(HBox(children=[beginning]))
curdoc().title = "Explore message"

update()
