# -*- coding: utf-8 -*- 
'''
Created on 16/10/31

@author: leng

'''

# 程序所需要的依赖包导入

from pymongo import MongoClient
from lxml import etree
from bs4 import BeautifulSoup
import requests
import math
import xlrd
import time


class Spapply_IDer:
    def __init__(self):  # 初始化全局变量
        self.param = {
            "showType": "1",
            "strSources": "",
            "strWhere": "PA='%%'",
            "numSortMethod": "2",
            "strLicenseCode": "",
            "numIp": "",
            "numIpc": "",
            "numIg": "",
            "numIgc": "",
            "numIgd": "",
            "numUg": "",
            "numUgc": "",
            "numUgd": "",
            "numDg": "",
            "numDgc": "",
            "pageSize": "10",
            "pageNow": "1"
        }
        self.header = {
            "Host": "epub.sipo.gov.cn",
            "Origin": "http://epub.sipo.gov.cn",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://epub.sipo.gov.cn/gjcx.jsp",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.10 Safari/537.36"
        }
        self.patentType = {
            u"发明公布": ["china_invent", "pip", 0],
            u"发明授权": ["china_authorize", "pig", 0],
            u"实用新型": ["china_use", "pug", 0],
            u"外观设计": ["china_appearance", "pdg", 0]
        }

    def get_company(self):  # 从excel中读取公司信息
        xlsx = xlrd.open_workbook("patent_for_RA.xlsx")
        with open('finishedCompany.txt', 'rb') as f:  # 这个txt存储的是已完成公司的名单
            content = f.read()
            f.close()
        for i in range(1, 2440):
            self.__init__()
            infos = xlsx.sheet_by_index(0).row_values(i)
            alliance_ID = str(infos[0])[:3]
            member_ID = infos[1]
            company = infos[2].strip()
            if company in content.decode('utf-8'):  # 如果发现已爬取过，跳下一个公司
                continue
            self.get_count(alliance_ID, member_ID, company)

    def get_unfinish(self):  # 补漏企业
        param = {
            "pip": ["china_invent", u"发明公布", 0],
            "pig": ["china_authorize", u"发明授权", 0],
            "pug": ["china_use", u"实用新型", 0],
            "pdg": ["china_appearance", u"外观设计", 0]
        }
        with open('unfinish1125.txt', 'rb') as f:
            unfinish = f.read()
            f.close()
        for info in unfinish.split('\r'):
            print info
            # self.__init__()
            # company = info.split('-')[0].decode('utf-8')
            # patentType = info.split('-')[1]
            # page = info.split('-')[2].replace('\r', '')
            # client = MongoClient('localhost', 27017)
            # db = client["patentCong"]
            # try:
            #     mongo = db.patent.find({'company': company})[0]
            #     alliance_ID = mongo['alliance_ID']
            #     member_ID = mongo['member_ID']
            #     self.param["strWhere"] = "PA='%" + company + "%'"
            #     self.param["strSources"] = patentType
            #     self.param["pageNow"] = page
            #     classify = param[patentType][1]
            #     key = param[patentType][0]
            #     try:
            #         contenting = requests.post("http://epub.sipo.gov.cn/patentoutline.action",data=self.param,headers=self.header, timeout=120).text
            #         self.get_data(classify, key, alliance_ID, member_ID, company, contenting)
            #         time.sleep(1)
            #     # 异常处理
            #     except Exception as e:
            #         print e
            #         self.log(company + u'爬取数据发生错误：' + str(e))
            #         self.file('', 'unFinish1126.txt',
            #                   company + '-' + self.param["strSources"] + '-' + self.param["pageNow"])
            #         continue
            # except Exception as er:
            #     continue

    def get_count(self, alliance_ID, member_ID, company):  # 获取公司需要爬取的专利总数
        self.log(u'正在爬取：' + company)
        try:
            self.param["strWhere"] = "PA='%" + company + "%'"
            # 通过post请求在网站上获取专利数
            try:
                content = requests.post("http://epub.sipo.gov.cn/patentoutline.action", data=self.param,
                                        headers=self.header, timeout=120).text
            except:
                self.file('', 'unFinish.txt', company)
                return
            # 对没有专利的公司进行处理
            if u'没有您要查询的结果' in content:
                self.file('', 'data/' + alliance_ID + member_ID + '.txt', company + u'没有查询到专利')
                self.file('', 'finishedCompany.txt', company)
                return None
            # 获取页数
            try:
                self.patentType[u"发明公布"][2] = int(content.split('pato.numIp.value = "')[1].split('"')[0])
                self.patentType[u"发明授权"][2] = int(content.split('pato.numIg.value = "')[1].split('"')[0])
                self.patentType[u"实用新型"][2] = int(content.split('pato.numUg.value = "')[1].split('"')[0])
                self.patentType[u"外观设计"][2] = int(content.split('pato.numDg.value = "')[1].split('"')[0])
            except:
                return
            self.log(
                u'一共有' + str(self.patentType[u"发明公布"][2] + self.patentType[u"发明授权"][2] + self.patentType[u"实用新型"][2] +
                             self.patentType[u"外观设计"][2]) + u'条专利')
            self.file('', 'finishedCompany.txt', company)
            for classify in self.patentType:
                key = self.patentType[classify][0]
                count = self.patentType[classify][2]
                pagenum = int(math.ceil(float(count) / 10))
                self.log(classify + u'一共有' + str(count) + u'条专利，共' + str(pagenum) + u'页')
                # 开始根据页数爬取
                for i in range(1, pagenum + 1):
                    self.log(u'正在爬取第' + str(i) + u'页')
                    self.param["pageNow"] = str(i)
                    self.param["strSources"] = self.patentType[classify][1]
                    try:
                        contenting = requests.post("http://epub.sipo.gov.cn/patentoutline.action",
                                                   data=self.param,
                                                   headers=self.header, timeout=120).text
                        self.get_data(classify, key, alliance_ID, member_ID, company, contenting)
                        time.sleep(1)
                    # 异常处理
                    except Exception as e:
                        self.log(company + u'爬取数据发生错误：' + str(e))
                        self.file('', 'unFinish.txt',
                                  company + '-' + self.param["strSources"] + '-' + self.param["pageNow"])
                        continue
        # 异常处理
        except Exception as e:
            self.file('', 'errorCompany.txt', company + u'发生错误：' + str(e))
            self.log(company + u'发生错误：' + str(e))
            return

    def get_data(self, typeC, typeE, alliance_ID, member_ID, company, content):
        # 对获取的专利数据进行处理，整合
        content_soup = BeautifulSoup(content, 'lxml')
        length = len(content_soup.find_all('div', attrs={'class': 'cp_box'}))
        announce_ID = '-'
        announce_time = '-'
        apply_ID = '-'
        apply_time = '-'
        patent_owner = '-'
        patent_index = '-'
        address = '-'
        for i in range(0, length):
            content_list = content_soup.find_all('div', attrs={'class': 'cp_box'})[i].find('div', attrs={
                'class': 'cp_linr'}).get_text('|', strip=True).encode('utf-8')
            for info in content_list.split('|'):
                if '申请公布号' in info:
                    try:
                        announce_ID = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        announce_ID = '-'
                elif '审定号' in info:
                    try:
                        announce_ID = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        announce_ID = '-'
                elif '授权公告号' in info:
                    try:
                        announce_ID = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        announce_ID = '-'
                elif '公告号' in info:
                    try:
                        announce_ID = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        announce_ID = '-'
                elif '申请公布日' in info:
                    try:
                        announce_time = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        announce_time = '-'
                elif '授权公告日' in info:
                    try:
                        announce_time = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        announce_time = '-'
                elif '公告日' in info:
                    try:
                        announce_time = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        announce_time = '-'
                elif '申请号' in info:
                    try:
                        apply_ID = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        apply_ID = '-'
                elif '申请日' in info:
                    try:
                        apply_time = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        apply_time = '-'
                elif '申请人' in info:
                    try:
                        patent_owner = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        patent_owner = '-'
                elif '专利权人' in info:
                    try:
                        patent_owner = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        patent_owner = '-'
                elif '分类号' in info:
                    try:
                        patent_index = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        patent_index = '-'
                elif '地址' in info:
                    try:
                        address = unicode(info.split('：')[1].strip(), 'utf-8')
                    except:
                        address = '-'
            data = company + ',' + alliance_ID + ',' + member_ID + ',' + typeE + ',' + announce_ID + ',' + announce_time \
                   + ',' + apply_ID + ',' + apply_time + ',' + patent_owner + ',' + patent_index + ',' + address
            self.file('', 'data/' + alliance_ID + member_ID + '.txt', data)
            self.mongo(alliance_ID, member_ID, typeC,
                       apply_time.replace('.', ''), company)

    def mongo(self, alliance_ID, member_ID, typeC, apply_time, company):
        # firm专利数据进行处理，存入数据库
        key = alliance_ID + member_ID + apply_time[:6]
        data = {
            "key": key,
            "company": company,
            "alliance_ID": alliance_ID,
            "member_ID": member_ID,
            "apply_time": apply_time[:6],
            "china_invent": 0,
            "china_authorize": 0,
            "china_appearance": 0,
            "china_use": 0
        }
        # 连接本地数据库
        client = MongoClient('localhost', 27017)
        db = client["patentCong"]
        try:
            # 判断数据库中是否有改月份信息，如有，在数目后加1
            content = db.patent.find({"key": key})[0]
            count = content[self.patentType[typeC][0]]
            db.patent.update({"key": key}, {"$set": {self.patentType[typeC][0]: count + 1}})
            self.log(u'正在更新专利月份数据')
        except:
            # 如无，插入新数据
            data[self.patentType[typeC][0]] = 1
            db.patent.insert(data)
            self.log(u'正在添加专利月份数据')

    def file(self, flag, filename, data):
        # 将部分写文件的操作函数化
        with open(filename, 'a+') as f:
            if flag == 'empty':  # 如传入标志带有empty,清空文件，重新写入数据
                f.truncate()
            elif flag == 'repeat':  # 如传入标志带有repeat,检查文件中是否有该公司，如有，不再重复写入
                content = f.read()
                if data in content:
                    f.close()
                    return 'Repeat'
            f.write(data.encode('utf-8') + '\n')
            f.close()
            return 'Success'

    def log(self, data):
        # 日志函数，将日志打印出来并写入log.txt
        print data
        nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open('log.txt', 'a+') as f:
            f.write(str(nowtime) + '->' + data.encode('utf-8') + '\n')
            f.close()


# 主函数
if __name__ == '__main__':
    l = Spapply_IDer()
    # l.get_company()
    l.get_unfinish()
