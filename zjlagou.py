#  _*_ coding:utf-8 _*_
"""
拉勾网职位查询分析
write the code, change the worls
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
        self.city = "北京"
        self.worktype = "python"
        self.maxindex = 20
        # Cookie，Referer，User-Agent
        self.headers = {
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/jobs/list_python?labelWords=&fromSearch=true&suginput=',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': "user_trace_token=20181224221417-14f12a99-306e-4271-b1ae-ea8181048de5; _ga=GA1.2.495178308.1545660858; LGUID=20181224221419-340dd7c0-0786-11e9-a954-5254005c3644; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22167e2527ce71e1-06b5de01b08e72-b781636-1049088-167e2527ce9859%22%2C%22%24device_id%22%3A%22167e2527ce71e1-06b5de01b08e72-b781636-1049088-167e2527ce9859%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; JSESSIONID=ABAAABAAAIAACBI533E5D5C9B7929F6CE9069706B9DE992; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1546951443,1547301394,1547630032,1547724764; _gat=1; _gid=GA1.2.973674907.1547724764; LGSID=20190117193243-9af5ed35-1a4b-11e9-b681-5254005c3644; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%8C%97%E4%BA%AC; TG-TRACK-CODE=index_search; SEARCH_ID=ebeb56a526e645acbeec9d8008cb220a; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1547724858; LGRID=20190117193417-d2b58b23-1a4b-11e9-b681-5254005c3644"
        }
        self.baseurl = "https://www.lagou.com/jobs/positionAjax.json?px=default&city=" + \
                       self.city + "&needAddtionalResult=false"
        self.Record = []
        self.Recordpath = '.\\saveData\\'
        self.session = requests.Session()
        if not os.path.exists(self.Recordpath):
            os.makedirs(self.Recordpath)

    def saveRecord(self):
        df = pd.DataFrame(self.Record)
        df.to_excel(
            self.Recordpath + "itwork-" + self.worktype + "-" + self.city + "-" + time.strftime('%Y%m%d') + ".xls",
            index=False)
        print("保存成功:",
              self.Recordpath + "itwork-" + self.worktype + "-" + self.city + "-" + time.strftime('%Y%m%d') + ".xls")
        print(df.shape[0], df.shape[1])
        print("len:", len(self.Record))

    def start(self):
        data = {
            'first': 'true',
            'pn': 1,
            'kd': self.worktype,
        }
        print("url: ", self.baseurl)
        req = self.session.post(self.baseurl, data=data, headers=self.headers)
        data = req.text
        data = json.loads(data)

        print("data: ", data)
        if "status" in data and data["status"] == False:
            print("错误信息:", data["msg"])
            return
        cityname = data["content"]["positionResult"]["locationInfo"]["city"]
        totalnum = data["content"]["positionResult"]["totalCount"]
        pagenum = data["content"]["positionResult"]["resultSize"]
        total_index = int(np.floor(totalnum / pagenum))
        print(">>>>>>>>>  ", total_index, pagenum, total_index, cityname)
        spider_index = min(total_index + 1, self.maxindex)
        for i in range(1, spider_index):
            a = np.random.randint(100, 300)
            time.sleep(a / 1000)
            data = {
                'first': 'true',
                'pn': i,
                'kd': self.worktype,
            }
            try:
                req = self.session.post(self.baseurl, data=data, headers=self.headers, timeout=5)
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
                print("False----, sleep 2", data)
                time.sleep(2)  # sleep  for a wihile
                continue
            result = data["content"]["positionResult"]["result"]
            for a in result:
                record_d = {}
                record_d["公司ID"] = a["companyId"]
                record_d["职位"] = a["positionName"]
                record_d["工作经验"] = a["workYear"]
                record_d["学历要求"] = a["education"]
                record_d["岗位性质"] = a["jobNature"]
                record_d["城市"] = a["city"]
                record_d["发布时间"] = a["createTime"]
                record_d["所属行业"] = a["industryField"]
                record_d["职位类别一"] = a["firstType"]
                record_d["职位类别二"] = a["secondType"]
                skill = a["skillLables"]
                skill = "无" if len(skill) == 0 else  ",".join(skill)
                record_d["技能"] = skill
                record_d["薪资"] = a["salary"]
                record_d["所属区域"] = a["district"]
                record_d["公司全称"] = a["companyFullName"]
                self.Record.append(record_d)
            print("完成数据:", i, "/", pagenum, spider_index, totalnum)
        self.saveRecord()


if __name__ == "__main__":
    stime = time.time()
    print("开始网络爬虫")
    spider = Spider()
    spider.start()
    etime = time.time()
    print("耗时：", etime - stime)
    pass
