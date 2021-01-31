import justpy as jp

import json
import datetime
import time
import pandas as pd
from pandas import json_normalize
import decimal
import numpy as np
from requests_html import HTMLSession
session = HTMLSession()

input_classes = "m-2 bg-gray-200 border-2 border-gray-200 rounded w-64 py-2 px-4 text-gray-700 focus:outline-none focus:bg-white focus:border-purple-500"
p_classes = 'm-2 p-2 h-32 text-xl border-2'
button_classes = 'w-32 m-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'

async def read(self, msg):
    print(msg.page.data['symbols'])
    uri = f'quotes?symbols={symbols}'
    print(uri)
    r = session.get(host + uri)
    data = json.loads(r.html.text)
    print(data)

symbols = ['COMEX:GC', 'COMEX:HG', 'NYMEX:US30', 'NYMEX:US500', 'NYMEX:USTEC', 'NYMEX:DX', 
        '서울:KS11', '서울:KS100', '도쿄:JP225', 
        '서울:005930', '서울:035420', '서울:001040', 'KOSDAQ:035760', '서울:009540']

async def index(request):
    wp = jp.WebPage(data={
        'symbols': ','.join(symbols), 
        'q': None
        })
    in1 = jp.Input(a=wp, classes=input_classes, placeholder='Please type here', model=[wp, 'symbols'])
    b = jp.Button(text='Read', click=read, a=wp, classes=button_classes)
    return wp

jp.justpy(index)



def str_to_timestamp(date):
    obj_datetime = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return datetime_to_timestamp(obj_datetime)

def datetime_to_timestamp(dt):
    return int(time.mktime(dt.timetuple()))

def transform_ohlc(data):
    result = {}
    if 't' in data.keys():
        result['Date'] = data.pop('t')
        for i, v in enumerate(result['Date']):
            result['Date'][i] = datetime.datetime.fromtimestamp(v)
    if 'o' in data.keys():
        result['Open'] = data.pop('o')
    if 'h' in data.keys():
        result['High'] = data.pop('h')
    if 'l' in data.keys():
        result['Low'] = data.pop('l')
    if 'c' in data.keys():
        result['Close'] = data.pop('c')
    if 'v' in data.keys():
        result['Volume'] = data.pop('v')
        
    df = pd.DataFrame.from_dict(result)
    return df.set_index('Date')


host = 'https://tvc4.forexpros.com/bf9b0cf35ce6ca91b1bba8dd1d70c0c2/1601606035/18/18/88/'

def history(symbol, resolution, from_date, to_date=None):
    from_timestamp = str_to_timestamp(from_date + ' 00:00:00' if len(from_date) == 10 else from_date)
    if not to_date:
        to_timestamp = datetime_to_timestamp(datetime.datetime.now())
    else:     
        to_timestamp = str_to_timestamp(to_date + ' 23:59:59' if len(to_date) == 10 else to_date)
 
    data = history_raw(symbol, resolution, from_timestamp, to_timestamp)
    if len(data['t']) >= 5000:
        while True:
            data2 = history_raw(symbol, resolution, data['t'][-1] + 1, to_timestamp)
            data['t'] = data['t'] + data2['t']
            data['o'] = data['o'] + data2['o']
            data['h'] = data['h'] + data2['h']
            data['l'] = data['l'] + data2['l']
            data['c'] = data['c'] + data2['c']
            data['v'] = data['v'] + data2['v']
            if len(data2['t']) < 5000: break
                
    return transform_ohlc(data)

def history_raw(symbol, resolution, from_timestamp, to_timestamp):
    uri = f'history?symbol={symbol}&resolution={resolution}&from={from_timestamp}&to={to_timestamp}'
    r = session.get(host + uri)
    return json.loads(r.html.text)    

async def quotes(symbols):
    uri = f'quotes?symbols={symbols}'
    print(uri)
    r = session.get(host + uri)
    data = json.loads(r.html.text)
    d = [row['v'] for row in data['d']]
    return pd.DataFrame(d)

def candle(symbol, resolution, from_date, to_date=None, digit=0):
    return candle_df(history(symbol, resolution, from_date, to_date), digit)

def candle_df(df, digit=0):
    df['Open'] = round(df['Open'], digit)
    df['High'] = round(df['High'], digit)
    df['Low'] = round(df['Low'], digit)
    df['Close'] = round(df['Close'], digit)
    df['Pre_Close'] = df['Close'].shift()
    df['Gap'] = df['Open']-df['Pre_Close']
    df['Change'] = df['Close']-df['Pre_Close']
    df['Change_Rate'] = round((df['Close']/df['Pre_Close']-1)*100, 2)
    df['Body'] = df['Close']-df['Open']
    df['Height'] = df['High']-df['Low']
    return df
