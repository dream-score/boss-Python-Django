import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv
import pandas as pd
import os
import django
from webdriver_manager.chrome import ChromeDriverManager

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boss直聘数据可视化分析.settings')
django.setup()
# 但是还是需要在文件开头添加两行配置环境变量的配置语句，让程序知道该去哪儿寻找 models 中的文件。
from myApp.models import *


class spider(object):
    def __init__(self, type, page):
        self.type = type
        # 岗位关键字
        self.page = page
        # 页码数
        self.spiderUrl = "https://www.zhipin.com/web/geek/job?query=%s&city=100010000&page=%s"


    def startBrower(self):
        option = webdriver.ChromeOptions()
        # option.add_experimental_option("debuggerAddress", "localhost:9222")
        option.add_experimental_option("excludeSwitches", ['enable-automation'])
        # s = Service("./chromedriver.exe")
        # selenium 驱动的位置
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
        # browser = webdriver.Chrome(service=s, options=option)
        return browser

    def main(self, **info):
        if info['page'] < self.page:
            return
        brower = self.startBrower()
        print('列表页面URL:' + self.spiderUrl % (self.type, self.page))
        brower.get(self.spiderUrl % (self.type, self.page))
        time.sleep(20)  # 网络或硬件设备原因，页面加载较慢，所以设置睡眠时间等待加载完成，彩开始下面的数据解析。否则解析会报错
        job_list = brower.find_elements(by=By.XPATH, value="//ul[@class='job-list-box']/li")
        self.init()
        print("正在爬取第 %d 页...." % (self.page))
        for index, job in enumerate(job_list):
            try:

                jobData = []
                # title  工作名字
                title = job.find_element(by=By.XPATH,
                                         value="./div[1]/a/div[1]/span[1]").text
                # address  地址
                addresses = job.find_element(by=By.XPATH,
                                             value="./div[1]/a/div[1]/span[2]/span[1]").text.split(
                    '·')
                address = addresses[0]
                # dist 行政区
                if len(addresses) != 1:
                    dist = addresses[1]
                else:
                    dist = ''
                # type  工作类型
                type = self.type

                tag_list = job.find_elements(by=By.XPATH,
                                             value="./div[1]/a/div[2]/ul/li")
                if len(tag_list) == 2:
                    educational = job.find_element(by=By.XPATH,
                                                   value="./div[1]/a/div[2]/ul/li[2]").text
                    workExperience = job.find_element(by=By.XPATH,
                                                      value="./div[1]/a/div[2]/ul/li[1]").text
                else:
                    educational = job.find_element(by=By.XPATH,
                                                   value="./div[1]/a/div[2]/ul/li[3]").text
                    workExperience = job.find_element(by=By.XPATH,
                                                      value="./div[1]/a/div[2]/ul/li[2]").text
                # hr
                hrWork = job.find_element(by=By.XPATH,
                                          value="//div[contains(@class,'job-info')]/div[@class='info-public']/em").text
                hrName = job.find_element(by=By.XPATH,
                                          value="//div[contains(@class,'job-info')]/div[@class='info-public']").text

                # workTag 工作标签
                workTag = job.find_elements(by=By.XPATH,
                                            value="//div[contains(@class,'job-card-footer')]/ul[@class='tag-list']/li")
                workTag = json.dumps(list(map(lambda x: x.text, workTag)))

                # salary 薪资
                salaries = job.find_element(by=By.XPATH,
                                            value="//div[contains(@class,'job-info')]/span[@class='salary']").text
                # 是否为实习单位
                pratice = 0
                if salaries.find('K') != -1:
                    salaries = salaries.split('·')
                    if len(salaries) == 1:
                        salary = list(map(lambda x: int(x) * 1000, salaries[0].replace('K', '').split('-')))
                        salaryMonth = '0薪'
                    else:
                        # salaryMonth 年底多薪
                        salary = list(map(lambda x: int(x) * 1000, salaries[0].replace('K', '').split('-')))
                        salaryMonth = salaries[1]
                else:
                    salary = list(map(lambda x: int(x), salaries.replace('元/天', '').split('-')))
                    salaryMonth = '0薪'
                    pratice = 1

                # companyTitle 公司名称
                companyTitle = job.find_element(by=By.XPATH, value="//h3[@class='company-name']/a").text
                # companyAvatar 公司头像
                companyAvatar = job.find_element(by=By.XPATH,
                                                 value="//div[contains(@class,'job-card-right')]//img").get_attribute(
                    "src")
                companyInfoList = job.find_elements(by=By.XPATH,
                                                    value="//div[contains(@class,'job-card-right')]//ul[@class='company-tag-list']/li")
                if len(companyInfoList) == 3:
                    companyNature = job.find_element(by=By.XPATH,
                                                     value="//div[contains(@class,'job-card-right')]//ul[@class='company-tag-list']/li[1]").text
                    companyStatus = job.find_element(by=By.XPATH,
                                                     value="//div[contains(@class,'job-card-right')]//ul[@class='company-tag-list']/li[2]").text
                    try:
                        companyPeople = list(map(lambda x: int(x), job.find_element(by=By.XPATH,
                                                                                    value="//div[contains(@class,'job-card-right')]//ul[@class='company-tag-list']/li[3]").text.replace(
                            '人', '').split('-')))
                    except:
                        companyPeople = [0, 10000]
                else:
                    companyNature = job.find_element(by=By.XPATH,
                                                     value="//div[contains(@class,'job-card-right')]//ul[@class='company-tag-list']/li[1]").text
                    companyStatus = "未融资"
                    try:
                        companyPeople = list(map(lambda x: int(x), job.find_element(by=By.XPATH,
                                                                                    value="//div[contains(@class,'job-card-right')]//ul[@class='company-tag-list']/li[2]").text.replace(
                            '人', '').split('-')))
                    except:
                        companyPeople = [0, 10000]
                # companyTag 公司标签
                companyTag = job.find_element(by=By.XPATH,
                                              value="//div[contains(@class,'job-card-footer')]/div[@class='info-desc']").text
                if companyTag:
                    companyTag = json.dumps(companyTag.split('，'))
                else:
                    companyTag = '无'

                # 详情地址
                detailUrl = job.find_element(by=By.XPATH,
                                             value="//div[@class='job-card-body clearfix']/a").get_attribute('href')
                # 公司详情
                companyUrl = job.find_element(by=By.XPATH, value="//h3[@class='company-name']/a").get_attribute('href')

                jobData.append(title)
                jobData.append(address)
                jobData.append(type)
                jobData.append(educational)
                jobData.append(workExperience)
                jobData.append(workTag)
                jobData.append(salary)
                jobData.append(salaryMonth)
                jobData.append(companyTag)
                jobData.append(hrWork)
                jobData.append(hrName)
                jobData.append(pratice)
                jobData.append(companyTitle)
                jobData.append(companyAvatar)
                jobData.append(companyNature)
                jobData.append(companyStatus)
                jobData.append(companyPeople)
                jobData.append(detailUrl)
                jobData.append(companyUrl)
                jobData.append(dist)
                print(jobData)
                self.save_to_csv(jobData)
            except:
                pass
        self.save_to_sql()  # 每一页数据及时入库
        self.page += 1 # 下一页
        self.main(page=info['page']) # 递归调用进行逐页爬取，你刚刚删除文件的时候，这一步没做，意思是我没有彻底删除？使得挂了一个进程在哪阻塞着

    def save_to_csv(self, rowData):
        with open('./temp.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(rowData)

    def clear_numTemp(self):
        with open('./numTemp.txt', 'w', encoding='utf-8') as f:
            f.write('')

    def init(self):
        if os.path.exists('./temp.csv'):
            os.remove("./temp.csv")
        with open('./temp.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                ["title", "address", "type", "educational", "workExperience", "workTag", "salary", "salaryMonth",
                 "companyTags", "hrWork", "hrName", "pratice", "companyTitle", "companyAvatar", "companyNature",
                 "companyStatus", "companyPeople", "detailUrl", "companyUrl", "dist"])

    def save_to_sql(self):
        data = self.clearData()
        for job in data:
            JobInfo.objects.create(
                title=job[0],
                address=job[1],
                type=job[2],
                educational=job[3],
                workExperience=job[4],
                workTag=job[5],
                salary=job[6],
                salaryMonth=job[7],
                companyTags=job[8],
                hrWork=job[9],
                hrName=job[10],
                pratice=job[11],
                companyTitle=job[12],
                companyAvatar=job[13],
                companyNature=job[14],
                companyStatus=job[15],
                companyPeople=job[16],
                detailUrl=job[17],
                companyUrl=job[18],
                dist=job[19]
            )
        print("导入数据库成功")

    def clearData(self):
        df = pd.read_csv('./temp.csv')
        print("数据清洗中......")
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)
        df['salaryMonth'] = df['salaryMonth'].map(lambda x: x.replace('薪', ''))
        print("数据清洗已完成......")
        print("有效总条数为%d" % df.shape[0])
        return df.values



if __name__ == '__main__':
    spiderObj = spider("python", 1);# 这里是指定你要爬取的内容，目前是python，
    spiderObj.startBrower()
    spiderObj.main(page=2) # 这里控制爬取的页面数量

