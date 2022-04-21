import traceback
import pymysql

from selenium.webdriver import ChromeOptions
# 这里注意一下 selenium 4.0.0版本后 需要额外导入一个包
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome, ChromeOptions

import time
import traceback
import requests
import json



def get_hot_search() -> list:
    ts = time.strftime("%Y-%m-%d %X")
    option = ChromeOptions()
    s = Service('C:/Users/86132/AppData/Local/Google/Chrome/Application/chrome.exe')
    driver = webdriver.Chrome(service=s)
    chrome_driver_binary = '../chromedriver.exe'
    option.add_argument("--headless")  # 开启无头模式
    option.add_argument("--no-sandbox")  # 关闭沙盒模式
    data = []
    # 这里的参数是浏览器驱动的路径，若在驱动在当前文件目录下，可以忽略不写
    # browser = Chrome(chrome_driver_binary, options=option)
    url = 'https://top.baidu.com/board?tab=realtime'
    driver.get(url)
    # 这里注意一下 selenium 4.0.0版本后 需要使用find_elements/find_element
    # elements = browser.find_elements_by_css_selector( '.c-single-text-ellipsis')
    elements = driver.find_elements(By.XPATH, '//*[@id="sanRoot"]/main/div[2]/div/div[2]/div/div[2]/a/div[1]')
    # 这里只收录了热词，没有收录热力值，优化：收录热力值作为词云的value
    elements_value = driver.find_elements(By.XPATH, '//*[@id="sanRoot"]/main/div[2]/div/div[2]/div/div[1]/div[2]')
    for i in range(len(elements)):
        ele = elements[i]
        ele_v = elements_value[i]
        data.append([ele.text, ele_v.text, ts])
    driver.close()
    return data


def get_conn():
    """
    :return: 连接，游标l
    """
    # 创建连接
    db = pymysql.connect(host="47.100.91.211",
                           user="ali9yun_xyz",
                           password="hjl",
                           db="cov",
                           charset="utf8")
    # 创建游标
    cursor = db.cursor()  # 执行完毕返回的结果集默认以元组显示
    return db, cursor


def close_conn(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def updateHotSearch():
    cursor = None
    try:
        db, cursor = get_conn()
        content = get_hot_search()
        print(f'{time.asctime()} 开始更新热搜数据')
        cursor = db.cursor()
        sql = 'insert into hotsearch (dt,content) values(%s,%s)'
        ts = time.strftime('%Y-%m-%d %X')
        for line in content:
            cursor.execute(sql, (ts, line))
        db.commit()
        print(f'{time.asctime()} 热搜数据更新完毕')
    except:
        traceback.print_exc()
    finally:
        if cursor:
            cursor.close()



def get_tencent_data():
    header = {'User-Agent':
                  r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62'}
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5'
    url2 = 'https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=chinaDayList,chinaDayAddList,diseaseh5Shelf,provinceCompare'
    res = requests.get(url, headers=header).json()
    res2 = requests.get(url2, headers=header).json()

    data = json.loads(res['data'])
    data2 = res2['data']

    history = {}

    for i in data2['chinaDayList']:
        ds = i['y'] + '.' + i['date']
        tup = time.strptime(ds, '%Y.%m.%d')
        ds = time.strftime('%Y-%m-%d', tup)
        history[ds] = {'confirm': i['confirm'],
                       'suspect': i['suspect'],
                       'heal': i['heal'], 'dead': i['dead']}

    for i in data2['chinaDayAddList']:
        ds = i['y'] + '.' + i['date']
        tup = time.strptime(ds, '%Y.%m.%d')
        ds = time.strftime('%Y-%m-%d', tup)
        if ds not in history.keys():
            continue
        history[ds].update({'confirm_add': i['confirm'],
                            'suspect_add': i['suspect'],
                            'heal_add': i['heal'], 'dead_add': i['dead']})

    details = []
    update_time = data['lastUpdateTime']
    data_province = data['areaTree'][0]['children']
    for pro_infos in data_province:
        province = pro_infos['name']
        for city_infos in pro_infos['children']:
            city = city_infos['name']
            confirm = city_infos['total']['confirm']
            confirm_add = city_infos['today']['confirm']
            heal = city_infos['total']['heal']
            dead = city_infos['total']['dead']
            details.append([update_time, province, city, confirm,
                            confirm_add, heal, dead])
    return {'history':history, 'details':details}


def insert_history(data:dict):
    try:
        print(f'{time.asctime()} 开始插入数据')
        cursor = db.cursor()
        for k, v in data.items():
            sql_query = f"insert into history values('{k}',{v['confirm']},{v['confirm_add']}," \
                        f"{v['suspect']},{v['suspect_add']},{v['heal']},{v['heal_add']}," \
                        f"{v['dead']},{v['dead_add']})"
            print(sql_query)
            cursor.execute(sql_query)
        db.commit()
        print(f'{time.asctime()} 完成插入数据')
    except:
        traceback.print_exc()
    finally:
        cursor.close()


def update_history(data:dict):
    try:
        print(f'{time.asctime()} 开始更新历史数据')
        cursor = db.cursor()
        sql = 'select confirm from history where ds=%s'
        for k, v in data.items():
            if len(v.keys()) != 8:
                continue
            if not cursor.execute(sql, k):
                sql_query = f"insert into history values('{k}',{v['confirm']},{v['confirm_add']}," \
                            f"{v['suspect']},{v['suspect_add']},{v['heal']},{v['heal_add']}," \
                            f"{v['dead']},{v['dead_add']})"
                cursor.execute(sql_query)
        db.commit()
        print(f'{time.asctime()} 完成更新历史数据')
    except:
        traceback.print_exc()
    finally:
        if 'cursor' in locals().keys():
            cursor.close()


def update_details(data:list):
    cursor = None
    try:
        cursor = db.cursor()
        # 子查询，选中update_time字段，按照id字段的降序排列顺序，选出update_time字段第一个
        # 将返回的时间与我们传入的时间比较，相同返回1
        sql = 'select %s=(select update_time from details order by id desc limit 1)'
        # 指定插入顺序
        sql_query = f"insert into details (update_time,province,city,confirm,confirm_add," \
                    f"heal,dead) values(%s,%s,%s,%s,%s,%s,%s)"
        # print(data[0][0])
        cursor.execute(sql, data[0][0]) #对比最大时间戳
        result = cursor.fetchone()[0]
        if not result:
            print(f'{time.asctime()} 开始更新数据')
            for item in data:
                cursor.execute(sql_query, item)
            db.commit()
            print(f'{time.asctime()} 完成更新数据')
        else:
            print(f'{time.asctime()} 已是最新数据')
    except:
        traceback.print_exc()
    finally:
        if cursor:
            cursor.close()


def getBaiduData():
    option = ChromeOptions()
    option.add_argument('--headless')  # 隐藏浏览器
    option.add_argument('--no-sandbox')  # linux下需要添加

    browser = Chrome(options=option)
    url = 'https://top.baidu.com/board?tab=realtime'
    browser.get(url)

    xpath = '//*[@id="sanRoot"]/main/div[2]/div/div[2]/div/div[2]/a/div[1]'
    elements = browser.find_elements(by='xpath', value=xpath)
    content = [element.text for element in elements]
    browser.close()
    return content


db = pymysql.connect(host="localhost", user="root", passwd="root", database="cov")
data = get_tencent_data()
# insert_history(data['history'])
update_history(data['history'])
update_details(data['details'])
# updateHotSearch()
db.close()


if __name__ == '__main__':
    get_hot_search()
    updateHotSearch()