import time
import pymysql
import string
from jieba.analyse import extract_tags


def get_time():
    time_str = time.strftime("%Y{}%m{}%d{} %X")
    return time_str.format("年", "月", "日")


# 封装 连接 和 关闭 两个方法
def get_conn():
    """
    :return: 连接，游标l
    """
    # 创建连接
    conn = pymysql.connect(host="localhost",
                           user="root",
                           password="root",
                           db="cov",
                           charset="utf8")
    # 创建游标
    cursor = conn.cursor()  # 执行完毕返回的结果集默认以元组显示
    return conn, cursor


def close_conn(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()


def query(sql, *args):
    '''
    :param sql:
    :param args:
    :return:返回结果，((),())形式
    '''
    conn, cursor = get_conn()
    cursor.execute(sql, args)
    res = cursor.fetchall()  # 获取结果
    close_conn(conn, cursor)
    return res


def get_c1_data():
    sql = "select sum(confirm)," \
          "(select suspect from history order by ds desc limit 1)," \
          "sum(heal)," \
          "sum(dead) " \
          "from details " \
          "where update_time=(select update_time from details order by update_time desc limit 1) "

    res = query(sql)
    print(res, 88)
    return res[0]

# def get_c1_data():
#     """
#     :return: 返回大屏div id=c1 的数据
#     """
#     # 因为会更新多次数据，取时间戳最新的那组数据
#     sql = """
#     SELECT total,total-heal-dead,heal,dead from (
#     select sum(confirm) total,
#     (SELECT heal from history ORDER BY ds desc LIMIT 1) heal ,
#       sum(dead) dead
#     from details where update_time=(
#       select update_time from details order by update_time desc limit 1)
#     ) d;
#     """
#     res = query(sql)
#     return res[0]


def get_c2_data():
    sql = "select province,sum(confirm) from details " \
          "where update_time=(select update_time from details " \
          "order by update_time desc limit 1) " \
          "group by province"

    res = query(sql)
    return res


def get_l1_data():
    sql = "select ds,confirm,suspect,heal,dead from history"

    res = query(sql)
    return res


def get_l2_data():
    sql = "select ds,confirm_add,suspect_add,heal_add,dead_add from history"

    res = query(sql)
    return res


def get_r1_data():
    # union_all 两块相加
    sql = 'SELECT city,confirm FROM ' \
 \
          '(select city,confirm from details  ' \
 \
          'where update_time=(select update_time from details order by update_time desc limit 1) ' \
 \
          'and province not in ("湖北","北京","上海","天津","重庆") ' \
 \
          'union all ' \
 \
          'select province as city,sum(confirm) as confirm from details  ' \
 \
          'where update_time=(select update_time from details order by update_time desc limit 1) ' \
 \
          'and province in ("北京","上海","天津","重庆") group by province) as a ' \
 \
          'ORDER BY confirm DESC limit 100'

    res = query(sql)
    return res


def get_r2_data():
    sql = "select content from jinri_hot order by id"

    res = query(sql)
    return res


from flask import jsonify

if __name__ == '__main__':
    # get_l1_data()
    # get_r1_data()
    # get_r2_data()
    print(get_c1_data())
    # pass
