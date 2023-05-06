from flask import Flask
import requests
import time
import json
from flask_cors import CORS

HEPTABASE_WHITEBOARD_ID = 'b898d7ffec62e9e9bdab80daa06e705061a1b83740acba02f9345a1a8d0f4aae'

# 存储 heptabase base 数据
HEPTABASE_DATA = {'result':'erro','data':{},'time':''}

def get_hepta_data():
    '''
    获取 heptabase 数据
    '''
    req = requests.get(
        'https://app.heptabase.com/api/whiteboard/?secret='+HEPTABASE_WHITEBOARD_ID)
    req_json = json.loads(req.text)
    return req_json

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.route('/')
def home():
    global HEPTABASE_DATA
    
    if(HEPTABASE_DATA['result']!='success'):
        # 如果全局变量中没有存储数据
        req_json = get_hepta_data()
        HEPTABASE_DATA = {'result':'success','data':req_json,'time':int(time.time())}
        return HEPTABASE_DATA
    else:
        # 全局变量有存储数据则直接返回，以提升数据获取速度。
        return HEPTABASE_DATA

@app.route('/update')
def update():
    '''
    获取 hepta 数据存储到全局变量中
    '''
    global HEPTABASE_DATA
    req_json = get_hepta_data()
    HEPTABASE_DATA = {'result':'success','data':req_json,'time':int(time.time())}
    return HEPTABASE_DATA

@app.route('/about')
def about():
    return 'About Page Route'


@app.route('/portfolio')
def portfolio():
    return 'Portfolio Page Route'


@app.route('/contact')
def contact():
    return 'Contact Page Route'


@app.route('/api')
def api():
    with open('data.json', mode='r') as my_file:
        text = my_file.read()
        return text

if __name__ == '__main__':
    app.run(debug=True)
