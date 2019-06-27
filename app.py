import sqlite3
import csv
import requests
import json
import threading
import time



def execute_db(fname, sql_cmd):
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    c.execute(sql_cmd)
    conn.commit()
    conn.close()


def select_db(fname, sql_cmd):
    conn = sqlite3.connect(fname)
    c = conn.cursor()
    c.execute(sql_cmd)
    rows = c.fetchall()
    conn.close()
    return rows


def create_table(db_name):
    print('狀態：建立資料庫及資料表')
    table_name = input('creat new table:')  #地名,最低溫,最高溫,降雨機率
    # cmd = 'CREATE TABLE jack (id INTEGER PRIMARY KEY AUTOINCREMENT, item TEXT, price INTEGER, shop TEXT)'
    cmd = 'CREATE TABLE %s (id TEXT PRIMARY KEY , low TEXT, high TEXT, rain TEXT)' % (table_name)
    execute_db(db_name, cmd)


def into_data(db_name):
    print('狀態：插入測試資料')
    table_name = input('table name:')
    id = input('id:')
    item = input('item:')
    price = input('price:')
    shop = input('shop:')
    # cmd = 'INSERT INTO %s (id, item, price, shop) VALUES (%d,"%s", %d, "%s")' % (int(id), item, int(price), shop)
    cmd = 'INSERT INTO %s (id, item, price, shop) VALUES (%d, "%s", %d, "%s")' % (table_name, int(id), item, int(price), shop)
    # cmd = 'INSERT INTO %s (item, price, shop) VALUES ("%s", %d, "%s")' % (table_name, item, int(price), shop)
    execute_db(db_name, cmd)


def into_many_data(db_name):
    print('狀態：插入多筆資料')

    with open('ezprice.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:                                                          #地名,最低溫,最高溫,降雨機率
            cmd = 'INSERT INTO w (id, low, high, rain) VALUES ("%s" ,"%s", "%s", "%s")' % (row['地名'], row['最低溫'], row['最高溫'],row['降雨機率'])
            execute_db(db_name, cmd)


def select_data(db_name):
    #print('狀態：選擇資料')
    cmd = 'SELECT * FROM w WHERE id="高雄市"'
    #cmd = 'SELECT id FROM w'
    for row in select_db(db_name, cmd):
        if row != None:
            if int(row[3].replace('%','')) > 10 :
                return int(row[3].replace('%',''))
        else:
            break

def select_data1(id,db_name):
    #print('狀態：選擇資料')
    cmd = 'SELECT * FROM w WHERE id="%s"' %(id)
    #cmd = 'SELECT id FROM w'
    for row in select_db(db_name, cmd):
        if row[0] != None:
            return row[0]+">>最低溫："+row[1].replace(' C','')+'度Ｃ'+"。最高溫："+row[2].replace(' C','')+'度Ｃ。'+"降雨機率："+row[3]

def delete_data(db_name):
    print('狀態：刪除資料')
    table_name = input('table name:')
    id = input('id:')
    cmd = 'delete from %s where id = %d' % (table_name, int(id))
    execute_db(db_name, cmd)


def updata(db_name):
    print('狀態：更新資料')
    #table_name = input('table name:')
    #id = input('id:')
    #item = input('item:')
    with open('ezprice.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:                                                          #地名,最低溫,最高溫,降雨機率
            cmd = 'update w set low="%s",high="%s",rain="%s" where ID="%s"' % (row['最低溫'], row['最高溫'],row['降雨機率'],row['地名'])

            #cmd = 'update w set (low, high, rain) VALUES ("%s" ,"%s", "%s") where id="%s"' % (row['最低溫'], row['最高溫'],row['降雨機率'],row['地名'])
            execute_db(db_name, cmd)



def weather():
    url='https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization=CWB-7FBEE53D-7439-4C27-9BE7-5414679AAD4A&format=JSON'
    data = requests.get(url)
    jsondata=json.loads(data.text)
    #print(jsondata)
    item=[]
    items=[]
    for i in range(len(jsondata['cwbopendata']['dataset']['location'])):
        location = jsondata['cwbopendata']['dataset']['location'][i]['locationName']
        #print(location)
        item.append(location)
        maxT = jsondata['cwbopendata']['dataset']['location'][i]['weatherElement'][1]['time'][0]['parameter']['parameterName']
        #print(minT + ' C')
        item.append(maxT + ' C')
        minT = jsondata['cwbopendata']['dataset']['location'][i]['weatherElement'][2]['time'][0]['parameter']['parameterName']
        #print(maxT + ' C')
        item.append(minT + ' C')
        PoP = jsondata['cwbopendata']['dataset']['location'][i]['weatherElement'][4]['time'][0]['parameter']['parameterName']
        #print(PoP + '%')
        item.append(PoP + '%')
        items.append(item)
        item = []
    with open('ezprice.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('地名', '最高溫', '最低溫', '降雨機率'))
        for item in items:
            writer.writerow((column for column in item))







from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('your LineBotApi')
# Channel Secret
handler = WebhookHandler('your WebhookHandler')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    db_name = 'db.sqlite'
    weather()
    updata(db_name)
    id=event.message.text
    message=TextSendMessage(text=select_data1(id,db_name))
    line_bot_api.reply_message(event.reply_token, message)


import os


if __name__ == '__main__':
    #db_name = 'db.sqlite'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    #weather()


