# import requests
# # from selenium.webdriver import Chrome, ChromeOptions
# import urllib.request as rq
# import pymysql
# # from bs4 import BeautifulSoup
# import json
# import time
# import traceback
#
#
# """
# return: 返回历史数据和当日详细数据
# # """
#
# url_today = 'https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=diseaseh5Shelf'
# url_last = "https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=chinaDayList,chinaDayAddList,nowConfirmStatis,provinceCompare"
#
#
# def get_history(url_last,url_today):
#     headers = {
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
#     }
#     r_det = requests.get(url_today, headers)
#     r_his = requests.get(url_last, headers)
#     res_det = json.loads(r_det.text)  # json字符串转字典
#     res_his = json.loads(r_his.text)
#     data_det = res_det['data']['diseaseh5Shelf']
#     data_his = res_his['data']
#
#     history = {}  # 历史数据
#     for i in data_his["chinaDayList"]:
#         if (i["date"] > "04.01"):
#             ds = i["y"] + "." + i["date"]
#             tup = time.strptime(ds, "%Y.%m.%d")
#             ds = time.strftime("%Y-%m-%d", tup)  # 改变时间格式,不然插入数据库会报错，数据库是datetime类型
#             confirm = i["confirm"]
#             confirm_now = i["nowConfirm"]
#             suspect = i["suspect"]
#             heal = i["heal"]
#             dead = i["dead"]
#             history[ds] = {"confirm": confirm, "confirm_now": confirm_now, "suspect": suspect, "heal": heal,
#                            "dead": dead}
#         else:
#             continue
#     for i in data_his["chinaDayAddList"]:
#         if (i["date"] > "04.01"):
#             ds = i["y"] + "." + i["date"]
#             tup = time.strptime(ds, "%Y.%m.%d")
#             ds = time.strftime("%Y-%m-%d", tup)
#             confirm_add = i["confirm"]
#             suspect_add = i["suspect"]
#             heal_add = i["heal"]
#             dead_add = i["dead"]
#             history[ds].update(
#                 {"confirm_add": confirm_add, "suspect_add": suspect_add, "heal_add": heal_add, "dead_add": dead_add})
#         else:
#             continue
#     ''' areaTree ：name 中国数据
#                    today
#                    total
#                    children :-name 省级数据
#                             -today
#                             -total
#                             -children:-name 市级数据
#                                       -today
#                                       -total
#                             '''
#     details = []  # 当日详细数据
#     update_time = data_det["lastUpdateTime"]
#     data_country = data_det["areaTree"]  # list 之前有25个国家,现在只有中国
#     data_province = data_country[0]["children"]  # 中国各省
#     for pro_infos in data_province:
#         province = pro_infos["name"]  # 省名
#         for city_infos in pro_infos["children"]:
#             city = city_infos["name"]  # 城市名
#             confirm = city_infos["total"]["confirm"]  # l累计确诊
#             confirm_add = city_infos["today"]["confirm"]  # 新增确诊
#             confirm_now = city_infos["total"]["nowConfirm"]  # 现有确诊
#             heal = city_infos["total"]["heal"]  # 累计治愈
#             dead = city_infos["total"]["dead"]  # 累计死亡
#             details.append([update_time, province, city, confirm, confirm_add, confirm_now, heal, dead])
#     return history, details
#
#
# def gethtml(url):
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}
#     req = rq.Request(url, headers=headers)
#     res = rq.urlopen(req)
#
#     html = res.read().decode("utf-8")
#     return html
#
#
# # 连接数据库
# def get_conn():
#     conn = pymysql.connect(
#         host="localhost",
#         user="root",
#         password="root",
#         db="cov",
#         charset="utf8",
#         # port=3306,
#     )
#     # 创建游标：
#     cursor = conn.cursor()
#     return conn, cursor
#
#
# def close_conn(conn, cursor):
#     if cursor:
#         cursor.close()
#     if conn:
#         conn.close()
#
#
# def update_details(url_last, url_today):
#     cursor = None
#     conn = None
#     try:
#         # [['2020-07-01 15:20:46', '北京', '丰台', 266, 0, 43, 0],....]
#         detail_data = get_history(url_last, url_today)[1]  # 0是字典数据 1是列表数据
#         conn, cursor = get_conn()
#         sql = "insert into details(update_time,province,city,confirm,confirm_add,heal,dead) values(%s,%s,%s,%s,%s,%s,%s)"
#         sql_query = 'select %s=(select update_time from details order by id desc limit 1)'  # 对比当前最大时间戳,拿到最后一条数据
#         cursor.execute(sql_query, detail_data[0][0])
#         if not cursor.fetchone()[0]:
#             print(f"{time.asctime()}开始更新最新数据")
#             for item in detail_data:
#                 cursor.execute(sql, item)
#             conn.commit()  # 提交事务 update delete insert操作
#             print(f"{time.asctime()}更新最新数据完毕")
#         else:
#             print(f"{time.asctime()}已是最新数据！")
#     except:
#         traceback.print_exc()
#     finally:
#         close_conn(conn, cursor)
#
#
# def insert_history(url_last, url_today):
#     cursor = None
#     conn = None
#     try:
#         dic = get_history(url_last, url_today)[0]
#
#         print(f"{time.asctime()}开始插入历史数据")
#         conn, cursor = get_conn()
#         sql = "insert into history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#         for key, value in dic.items():
#             # item 格式 {'2020-01-13': {'confirm': 41, 'suspect': 0, 'heal': 0, 'dead': 1}
#             cursor.execute(sql, [key, value.get("confirm"), value.get("confirm_add"), value.get("suspect"),
#                                  value.get("suspect_add"), value.get("heal"), value.get("heal_add"),
#                                  value.get("dead"), value.get("dead_add")])
#         conn.commit()  # 提交事务 update delete insert操作
#         print(f"{time.asctime()}插入历史数据完毕")
#     except:
#         traceback.print_exc()
#     finally:
#         close_conn(conn, cursor)
#
#
# def update_history(url_last, url_today):
#     cursor = None
#     conn = None
#     try:
#         dic = get_history(url_last, url_today)[0]
#         print(f"{time.asctime()}开始更新历史数据")
#         conn, cursor = get_conn()
#         sql = "insert into history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#         sql_query = "select confirm from history where ds=%s"
#         for key, value in dic.items():
#             # item 格式 {'2020-01-13': {'confirm': 41, 'suspect': 0, 'heal': 0, 'dead': 1}
#             if not cursor.execute(sql_query, key):
#                 cursor.execute(sql, [key, value.get("confirm"), value.get("confirm_add"), value.get("suspect"),
#                                      value.get("suspect_add"), value.get("heal"), value.get("heal_add"),
#                                      value.get("dead"), value.get("dead_add")])
#         conn.commit()
#         print(f"{time.asctime()}历史数据更新完毕")
#     except:
#         traceback.print_exc()
#     finally:
#         close_conn(conn, cursor)
#
# # def getBaiduData():
# #     option = ChromeOptions()
# #     option.add_argument('--headless')  # 隐藏浏览器
# #     option.add_argument('--no-sandbox')  # linux下需要添加
# #
# #     browser = Chrome(options=option)
# #     url = 'https://top.baidu.com/board?tab=realtime'
# #     browser.get(url)
# #
# #     xpath = '//*[@id="sanRoot"]/main/div[2]/div/div[2]/div/div[2]/a/div[1]'
# #     elements = browser.find_elements(by='xpath', value=xpath)
# #     content = [element.text for element in elements]
# #     browser.close()
# #
# #     return content
#
# # def updateHotSearch():
# #     cursor = None
# #     try:
# #         conn, cursor = get_conn()
# #         content = getBaiduData()
# #         print(f'{time.asctime()} 开始更新热搜数据')
# #         cursor = conn.cursor()
# #         sql = 'insert into hotsearch (dt,content) values(%s,%s)'
# #         ts = time.strftime('%Y-%m-%d %X')
# #         for line in content:
# #             cursor.execute(sql, (ts, line))
# #         conn.commit()
# #         print(f'{time.asctime()} 热搜数据更新完毕')
# #     except:
# #         traceback.print_exc()
# #     finally:
# #         if cursor:
# #             cursor.close()
#
# if __name__ == '__main__':
#     # insert_history(url_last, url_today)
#     update_details(url_last, url_today)
#     update_history(url_last, url_today)
#     # getBaiduData()

import pymysql
import time
import traceback
import requests
import json

from selenium.webdriver import Chrome, ChromeOptions



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

# def updateHotSearch():
#     cursor = None
#     try:
#         content = getBaiduData()
#         print(f'{time.asctime()} 开始更新热搜数据')
#         cursor = db.cursor()
#         sql = 'insert into hotsearch (dt,content) values(%s,%s)'
#         ts = time.strftime('%Y-%m-%d %X')
#         for line in content:
#             cursor.execute(sql, (ts, line))
#         db.commit()
#         print(f'{time.asctime()} 热搜数据更新完毕')
#     except:
#         traceback.print_exc()
#     finally:
#         if cursor:
#             cursor.close()


db = pymysql.connect(host="localhost", user="root", passwd="root", database="cov")
data = get_tencent_data()
# insert_history(data['history'])
update_history(data['history'])
update_details(data['details'])
# updateHotSearch()
db.close()

