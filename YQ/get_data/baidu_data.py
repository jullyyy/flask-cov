import traceback

import pymysql
from selenium.webdriver import ChromeOptions
# 这里注意一下 selenium 4.0.0版本后 需要额外导入一个包
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time


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
    db = pymysql.connect(host="localhost",
                           user="root",
                           password="root",
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


if __name__ == '__main__':
    get_hot_search()
    updateHotSearch()