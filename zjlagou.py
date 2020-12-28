#  _*_ coding:utf-8 _*_
"""
拉勾网职位查询分析
write the code, change the words
"""
import json
import sys
import time
import os

import numpy as np
import pandas as pd
import requests

__author = "open_china"
__time__ = "2018.12.25"


# 网络爬虫
class Spider(object):
    def __init__(self):
        self.city = "成都"
        self.work_type = "python"
        self.max_index = 20
        # Cookie，Referer，User-Agent
        self.headers = {
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com/',
            'Referer': 'https://www.lagou.com/jobs/list_golang?labelWords=&fromSearch=true&suginput=',
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie':"JSESSIONID=ABAAABAAADEAAFIC485EAD4A087F3E3F9A8E2F54188D74F; WEBTJ-ID=20191002114529-16d8a92a6b68d5-0c6a2b42679b38-1d3d6b55-1296000-16d8a92a6b7375; _ga=GA1.2.1502959086.1569987930; _gid=GA1.2.795525759.1569987930; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1569987930; user_trace_token=20191002114529-1431f998-e4c7-11e9-97a2-525400f775ce; LGSID=20191002114529-1431fb48-e4c7-11e9-97a2-525400f775ce; LGUID=20191002114529-1431fcdb-e4c7-11e9-97a2-525400f775ce; gate_login_token=d580c481b29cd714e057a400f6ba350e192c304741678bda; LG_LOGIN_USER_ID=850442ddf49abacc9f4f420e3b32c80ed758ee9c258afefc; LG_HAS_LOGIN=1; _putrc=9F1804B9DF6EA72C; login=true; unick=%E5%88%98%E7%A5%96%E5%86%9B; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=120; privacyPolicyPopup=false; index_location_city=%E6%88%90%E9%83%BD; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216d8a9302437af-00cf9e5b0e50cc-1d3d6b55-1296000-16d8a930244b7f%22%2C%22%24device_id%22%3A%2216d8a9302437af-00cf9e5b0e50cc-1d3d6b55-1296000-16d8a930244b7f%22%7D; sajssdk_2015_cross_new_user=1; TG-TRACK-CODE=index_search; _gat=1; X_HTTP_TOKEN=23d63e1f4096458f54309996517d075c275ebf5eee; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1569990346; LGRID=20191002122545-b42f9aa4-e4cc-11e9-a53a-5254005c3644; SEARCH_ID=80134a8a044d46cbaac0974527afcf1f"

        }
        self.base_url = "https://www.lagou.com/jobs/positionAjax.json?px=default&city=" + \
                        self.city + "&needAddtionalResult=false"
        self.record = []
        self.record_path = './saveData/'
        self.session = requests.Session()
        if not os.path.exists(self.record_path):
            os.makedirs(self.record_path)
        else:
            print("pass it")

    def save_record(self):
        df = pd.DataFrame(self.record)
        df.to_excel(
            self.record_path + "itwork-" + self.work_type + "-" + self.city + "-" + time.strftime('%Y%m%d') + ".xls",
            index=False)
        print("保存成功:",
              self.record_path + "itwork-" + self.work_type + "-" + self.city + "-" + time.strftime('%Y%m%d') + ".xls")
        print(df.shape[0], df.shape[1])
        print("len:", len(self.record))

    def start(self):
        data = {
            'first': 'true',
            'pn': 1,
            'kd': self.work_type,
        }
        print("url: ", self.base_url)
        req = self.session.post(self.base_url, data=data, headers=self.headers)
        data = req.text
        data = json.loads(data)

        print("data: ", data)
        if "status" in data and data["status"] == False:
            print("错误信息:", data["msg"])
            return
        city_name = data["content"]["positionResult"]["locationInfo"]["city"]
        total_num = data["content"]["positionResult"]["totalCount"]
        page_num = data["content"]["positionResult"]["resultSize"]
        total_index = int(np.floor(total_num / page_num))
        print(">>>>>>>>>  ", total_index, page_num, total_index, city_name)
        spider_index = min(total_index + 1, self.max_index)
        for i in range(1, spider_index):
            a = np.random.randint(100, 300)
            time.sleep(a / 1000)
            data = {
                'first': 'true',
                'pn': i,
                'kd': self.work_type,
            }
            try:
                req = self.session.post(self.base_url, data=data, headers=self.headers, timeout=5)
                data = req.text
                print(data)
                data = json.loads(data)
            except Exception as e:
                print(sys._getframe().f_lineno, "error: ", e)
                print("False----, sleep 2", data)
                time.sleep(2)  # sleep  for a wihile
                continue

            statue = data["success"]
            if statue:
                pass
            else:
                time.sleep(2)  # sleep  for a wihile
                continue
            result = data["content"]["positionResult"]["result"]
            for a in result:
                record_d = {
                    "公司ID": a["companyId"],
                    "职位": a["positionName"],
                    "工作经验": a["workYear"],
                    "学历要求": a["education"],
                    "岗位性质": a["jobNature"],
                    "城市": a["city"],
                    "发布时间": a["createTime"],
                    "所属行业": a["industryField"],
                    "职位类别一": a["firstType"],
                    "职位类别二": a["secondType"]
                }

                skill = a["skillLables"]
                skill = "无" if len(skill) == 0 else ",".join(skill)
                record_d["技能"] = skill
                record_d["薪资"] = a["salary"]
                record_d["所属区域"] = a["district"]
                record_d["公司全称"] = a["companyFullName"]
                self.record.append(record_d)
            print("完成数据:", i, "/", page_num, spider_index, total_num)
        self.save_record()


if __name__ == "__main__":
    start_time = time.time()
    print("开始网络爬虫")
    spider = Spider()
    spider.start()
    end_time = time.time()
    print("耗时：", end_time - start_time)
    pass
