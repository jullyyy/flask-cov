from traceback import print_tb
import requests
from flask import Flask
from flask import render_template
import utils
from flask import jsonify
from jieba.analyse import extract_tags
import string
import simplejson
import threading

from config import *

app = Flask(__name__)


@app.route('/ajaxtest',methods=["post"])
def hello_world4():
    name = requests.values.get("name")
    return f"你好 {name}，服务器收到了ajax请求"


@app.route('/')
def hello_world():
    return render_template("main.html")


@app.route('/login')
def login():
    return render_template("index.html")


@app.route('/time')
def get_time():
    return utils.get_time()


@app.route('/c1', methods=['get', 'post'])
def get_c1_data():
    data = utils.get_c1_data()
    # 这里是测试 不用管
    print(data, 999)
    return jsonify({
        "confirm": str(data[0]),
        "suspect": str(data[1]),
        "heal": str(data[2]),
        "dead": str(data[3])
    })


@app.route("/c2", methods=['get', 'post'])
def get_c2_data():
    res = []
    for tup in utils.get_c2_data():
        res.append({'name': tup[0], 'value': int(tup[1])})
    return jsonify({'data': res})


@app.route("/l1", methods=['get', 'post'])
def get_l1_data():
    data = utils.get_l1_data()
    day, confirm, suspect, heal, dead = [], [], [], [], []
    for a, b, c, d, e in data[7:]:
        day.append(a.strftime("%m-%d"))
        confirm.append(b)
        suspect.append(c)
        heal.append(d)
        dead.append(e)

    return jsonify({"day": day[-100:], "confirm": confirm[-100:], "suspect": suspect[-100:], "heal": heal[-100:],
                    "dead": dead[-100:]})


@app.route("/l2", methods=['get', 'post'])
def get_l2_data():
    data = utils.get_l2_data()
    day, confirm_add, suspect_add, heal_add, dead_add = [], [], [], [], []
    for a, b, c, d, e in data[7:]:
        day.append(a.strftime("%m-%d"))
        confirm_add.append(b)
        suspect_add.append(c)
        heal_add.append(d)
        dead_add.append(e)

    return jsonify({"day": day[-100:], "confirm_add": confirm_add[-100:], "suspect_add": suspect_add[-100:],
                    "heal_add": heal_add[-100:], "dead_add": dead_add[-100:]})


@app.route("/r1", methods=['get', 'post'])
def get_r1_data():
    data = utils.get_r1_data()
    city, confirm = [], []
    for a, b in data:
        if a != "地区待确认" and a != "境外输入":
            city.append(a)
            confirm.append(int(b))

    return jsonify({"city": city[0:5], "confirm": confirm[0:5]})


@app.route("/r2", methods=['get', 'post'])
def get_r2_data():
    data = utils.get_r2_data()
    d = []
    for i in data:
        k = i[0].rstrip(string.digits)  # 移除热搜数字,从右边
        v = i[0][len(k):]  # 获取关键字
        ks = extract_tags(k)  # 使用结巴提取关键字
        for j in ks:
            if not j.isdigit():
                d.append({"name": j, "value": v})

    return jsonify({"kws": d})

def cron_task():
    from datetime import datetime
    from time import sleep
    from os import popen
    print(f'定时任务开启，每{PAUSE}小时自动更新数据')
    while True:
        now = datetime.now()
        if (now.hour % PAUSE) == 0 and now.minute == 0 and now.second == 0:
            task = popen('python spider.py')
            sleep(10)
            result = task.read()
            print(result)
            task.close()
            sleep(60 * 60 * 6 - 100)
        sleep(0.8)


if __name__ == '__main__':
    # app.run()
    # app.run(port=5050,debug=True)
    # print(get_r2_data())
    threading.Thread(target=cron_task).start()
    # 服务器部署
    # app.run(host="0.0.0.0",port=PORT,debug=True)
    # 本地部署
    app.run(port=PORT,debug=True)
    
