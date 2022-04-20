# # python 爬取百度疫情数据
# from operator import rshift
# import requests
# import re 
# import json
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36"
# }
# # url = 'https://voice.baidu.com/act/newpneumonia/newpneumonia/?from=osari_aladin_banner'
# url = 'https://www.ali9yun.xyz/home-master/'
# # 1.发送请求
# response = requests.get(url,headers=headers)
# # 2.获取数据
# # print(response)
# data_html = response.text
# # print(response.text)

# # 字符串
# json_str = re.findall('"component":\[(.*)\],',data_html)
# print(json_str)

# # 类型转变 由json字符串转变为python字典
# # json_dict = json.loads(json_str)
# # print(json_dict)

# # updateDate = json_dict['updateDate']
# # for item in updateDate:
# #     print(item)


from http.cookiejar import Cookie
from urllib import response
import requests
import re
import json
# 解析html格式数据
# from lxml import etree
import time

if __name__ == '__main__':
    # 获取当前的时间
    print("当前的时间是：", time.strftime("%Y-%m-%d %H:%M:%S"))
    url = "https://s.weibo.com/top/summary/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'
        # 'Cookie', 'SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WhC0voZv8R8vQEf4pJRpp2a; SUB=_2AkMVAdZjf8NxqwFRmPsQzW3ha4h1yg3EieKjXSe4JRMxHRl-yj8XqkoTtRB6PoH4jB73cofp-9l_Ljh5jUzDmAQv-OOW; login_sid_t=e726be04a0e0402fb980d933c239fe59; cross_origin_proto=SSL; _s_tentry=passport.weibo.com; Apache=8955051417030.646.1650284892921; SINAGLOBAL=8955051417030.646.1650284892921; ULV=1650284892926:1:1:1:8955051417030.646.1650284892921:'
        #           'referer':'https://s.weibo.com/?topnav=1&wvr=6'

    }
    response = requests.get(url, headers=headers)
    data = response.text
    print(data)
