#  _*_ coding:utf-8  _*_

"""
拉勾网IT薪资分析报表
write the code, change the worls
"""
__author__ = "open_china"
__time__ = "2018.12.27"

import pandas as pd
import numpy as np
from pyecharts import Funnel, Pie
import os


def draw_pie(path, title, attr, value):
    pie = Pie(title)
    pie.add("", attr=attr, value=value, radius=[30, 50],
            is_label_show=True, rosetype="radius")
    pie.render(path)
    print("create ok:", path)


class LagouAnay(object):
    def __init__(self):
        self.html_path = "./html"
        self.file_path = './saveData'
        if not os.path.exists(self.html_path):
            os.makedirs(self.html_path)

    def get_df_data(self):
        lis = os.listdir(self.file_path)
        data_xls = pd.read_excel(self.file_path + "\\" + lis[0])  # 只解析第一个文件
        df = pd.DataFrame(data_xls)
        return df

    # 薪资分布图
    def get_salary(self, df):
        money = df["薪资"].apply(lambda x: np.array(x.replace("k", "").replace("K", "").split("-")).tolist())
        money = money.apply(lambda x: (int(x[0]) + int(x[1])) / 2)
        # 重新分类薪资区间范围
        df["薪资"] = pd.cut(money,
                          bins=[0, 10, 20, 25, 30, 100],
                          right=False,
                          labels=np.array(["0-10k", "10k-20k", "20k-25k", "25k-30k", "30K+"]))
        data = df["薪资"].value_counts()
        funnel = Funnel("工程师薪资分布图", title_pos="center")
        funnel.add(
            name="薪资分布",
            attr=data.index,
            value=data.values,
            is_label_show=True,
            label_formatter='{b}  {d}%',
            label_pos='inside',
            legend_orient='vertical',
            legend_pos='right',
        )
        funnel.render(self.html_path + "salary.html")
        draw_pie(self.html_path + "salaryPie.html", "薪资分布", data.index, data.values)

    #  区域分布
    def get_location(self, df):
        data = df["所属区域"]
        location = data.value_counts()
        draw_pie(self.html_path + "location.html", "IT区域分布", location.index, location.values)

    # 学历绘图
    def get_education(self, df):
        data = df["学历要求"]
        data = data[data != "不限"]
        edu = data.value_counts()
        draw_pie(self.html_path + "edu.html", "学历要求", edu.index, edu.values)

    def start(self):
        df = self.get_df_data()
        self.get_salary(df)
        self.get_education(df)
        self.get_location(df)


if __name__ == "__main__":
    LagouAnay().start()
